"""Coverage counts checked against independently enumerated transaction sets."""
import io
import random
import subprocess
import sys
import tempfile
import unittest
from itertools import combinations
from pathlib import Path
from unittest.mock import patch

from cupami import convertFile, cuCMine


def reference(rows, min_rf, min_cs, max_or):
    baskets = [{str(x).strip() for x in row if str(x).strip()} for row in rows]
    baskets = [row for row in baskets if row]
    if not baskets:
        return {}
    tids = {item: {i for i, row in enumerate(baskets) if item in row}
            for item in set().union(*baskets)}
    items = sorted((item for item in tids if len(tids[item]) / len(baskets) >= min_rf),
                   key=lambda item: (-len(tids[item]), item))
    result = {}
    for width in range(1, len(items) + 1):
        for pattern in combinations(items, width):
            # Enumerate independently, checking every ordered prefix.
            valid = all(len(set().union(*(tids[x] for x in pattern[:i])) & tids[pattern[i]])
                        / len(tids[pattern[i]]) <= max_or for i in range(1, width))
            count = len(set().union(*(tids[x] for x in pattern)))
            if valid and count / len(baskets) >= min_cs:
                result['\t'.join(pattern)] = count
    return result


class ParametersTest(unittest.TestCase):
    def test_invalid_ratios_before_loading(self):
        for name in ('minRF', 'minCS', 'maxOR'):
            for value in (-.1, 1.1, float('nan'), float('inf'), True, '0.5', None):
                args = dict(minRF=.1, minCS=.8, maxOR=.3)
                args[name] = value
                with self.subTest(name=name, value=value), self.assertRaisesRegex(ValueError, name):
                    cuCMine('missing.csv', **args)
        for name in ('minRF', 'minCS'):
            args = dict(minRF=.1, minCS=.8, maxOR=0)
            args[name] = 0
            with self.assertRaisesRegex(ValueError, name):
                cuCMine([], **args)


class CMineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cuCMine._getCudaModule()
        except (ImportError, RuntimeError) as error:
            raise unittest.SkipTest(str(error))

    def check(self, rows, rf, cs, overlap, **kwargs):
        miner = cuCMine(rows, rf, cs, overlap, **kwargs)
        miner.mine()
        self.assertEqual(miner.getPatterns(), reference(rows, rf, cs, overlap))
        return miner

    def test_low_coverage_prefixes_keep_growing(self):
        miner = self.check([['a'], ['a'], ['b'], ['b'], ['c']], .2, 1, 0)
        self.assertEqual(miner.getPatterns(), {'a\tb\tc': 5})

    def test_manual_overlap_boundary_and_singletons(self):
        rows = [['a', 'b'], ['a'], ['a'], ['b'], ['c']]
        self.assertEqual(self.check(rows, .2, .8, .5).getPatterns(),
                         {'a\tb': 4, 'a\tb\tc': 5, 'a\tc': 4})
        self.assertNotIn('a\tb', self.check(rows, .2, .8, .49).getPatterns())
        self.assertEqual(self.check([['a', 'b']] * 33, 1, 1, 1).getPatterns(),
                         {'a': 33, 'b': 33, 'a\tb': 33})
        self.assertEqual(self.check([['a', 'b']] * 33, 1, 1, 0).getPatterns(),
                         {'a': 33, 'b': 33})

    def test_randomized_against_exhaustive_reference(self):
        for seed in range(6):
            rng = random.Random(seed)
            rows = [rng.sample(range(7), rng.randrange(8)) for _ in range(31 + seed)]
            for rf, cs, overlap in ((.1, .7, .3), (.2, 1, .7), (.01, .1, 1), (1, 1, 0)):
                with self.subTest(seed=seed, rf=rf, cs=cs, overlap=overlap):
                    self.check(rows, rf, cs, overlap)

    def test_empty_duplicate_and_large_item_ids(self):
        for rows in ([], [[], []], [[0, 0, 1], [], [4294967295], [0, 1, 4294967295]]):
            self.check(rows, .1, .5, .5)

    def test_all_formats_and_loading_backends(self):
        rows = [[0, 1, 1], [], [0, 2], [1, 2], [3], [0, 1, 3]]
        expected = reference(rows, .2, .8, .5)
        with tempfile.TemporaryDirectory() as folder:
            for ext in ('csv', 'bin', 'parquet'):
                source = Path(folder) / ('transactions.' + ext)
                convertFile(rows, source)
                for gpu in (False, True):
                    with self.subTest(ext=ext, gpu=gpu):
                        miner = cuCMine(source, .2, .8, .5, use_gpu_io=gpu, use_gds=False)
                        miner.mine()
                        self.assertEqual(miner.getPatterns(), expected)

    def test_batch_limits_word_boundaries_and_repeat(self):
        rows = [[str(i % 5)] for i in range(65)]
        miner = cuCMine(rows, .1, .8, 0)
        miner._EXTENSION_BATCH_SIZE = 2
        miner._EXTENSION_BATCH_BYTES = 1
        for _ in range(2):
            miner.mine()
            self.assertEqual(miner.getPatterns(), reference(rows, .1, .8, 0))
        self.assertEqual(miner.getRuntime(), miner.getMiningTime())
        self.assertAlmostEqual(miner.getTotalRuntime(), miner.getLoadingTime() + miner.getMiningTime())
        self.assertGreaterEqual(miner.getMiningTime(), 0)
        self.assertGreaterEqual(miner.getMemoryRSS(), 0)
        self.assertGreaterEqual(miner.getMemoryUSS(), 0)
        frame = miner.getPatternsAsDataFrame()
        self.assertEqual(dict(zip(frame.Patterns, frame.Coverage)), miner.getPatterns())
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'patterns.txt'
            miner.save(path)
            self.assertEqual(dict((k, int(v)) for k, v in
                                  (line.rsplit(' : ', 1) for line in path.read_text().splitlines())),
                             miner.getPatterns())
        with patch('sys.stdout', new_callable=io.StringIO) as output:
            miner.printResults()
        self.assertIn('Coverage Patterns:', output.getvalue())

    def test_url_labels_and_separator(self):
        with patch('cupami.frequentPattern.cuApriori.urlopen',
                   return_value=io.BytesIO(b'"apple,pear"\tbanana\nbanana\tcherry\n')):
            miner = cuCMine('https://example.test/data.csv', .5, 1, 1, sep='\t')
        miner.mine()
        self.assertEqual(miner.getPatterns(), reference(
            [['apple,pear', 'banana'], ['banana', 'cherry']], .5, 1, 1))

    def test_cli(self):
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / 'data.csv', Path(folder) / 'patterns.txt'
            source.write_text('a\na\nb\nb\nc\n')
            result = subprocess.run([sys.executable, 'cupami/coveragePattern/cuCMine.py',
                                     str(source), str(output), '.2', '1', '0'],
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_text(), 'a\tb\tc : 5\n')


if __name__ == '__main__':
    unittest.main()
