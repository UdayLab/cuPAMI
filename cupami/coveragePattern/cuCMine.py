"""CUDA coverage mining with support-ordered CMine prefix expansion.

Model: Sripada, Reddy and Kiran, Coverage patterns for efficient banner
advertisement placement, WWW Companion 2011, doi:10.1145/1963192.1963259.
Implementation reference: PAMI coveragePattern/{basic/CMine,cuda/cuCMine}.py,
revision 48d0c25fb5f1e4ff32e797fa00873033921f1aa7, GPL-3.0-or-later,
Copyright (C) 2021 Rage Uday Kiran. Local implementation uses iterative DFS,
bounded GPU extension batches and cuPAMI's shared uint32 transaction bitsets.
Unlike PAMI, singleton output must also satisfy minCS. See
docs/algorithm-references.md for the model and implementation differences.
"""

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Rage Uday Kiran (PAMI reference implementations).
# Copyright (C) 2026 Rage Uday Kiran (cuPAMI integration).

from __future__ import annotations

import math
from numbers import Real
from pathlib import Path
import sys
import time

if __name__ == "__main__" and not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = "cupami.coveragePattern"

from ..frequentPattern.cuApriori import cuApriori
from ..frequentPattern._bitsets import build_bitsets, count_supports, intersect_extensions


class cuCMine(cuApriori):
    """Mine high-coverage, low-overlap itemsets on a CUDA GPU.

    ``minRF`` and ``minCS`` are ratios in (0, 1]; ``maxOR`` is in [0, 1].
    Integers 0 and 1 mean ratios, not transaction counts. Items are ordered by
    descending singleton support, with lexical ties. Each extension must obey
    ``|covered & item| / |item| <= maxOR``; coverage only gates output.

    Input/loading options and output/timing/memory methods follow cuApriori.
    Duplicate items count once and empty transactions are omitted by the shared
    readers. getPatterns() maps tab-separated item names to union counts, not
    fractions or intersection supports. Mining requires CuPy and a CUDA device.
    """

    _EXTENSION_BATCH_SIZE = 4096
    _EXTENSION_BATCH_BYTES = 64 * 1024 * 1024

    def __init__(self, iFile, minRF, minCS, maxOR, sep=None,
                 use_gds="auto", use_gpu_io="auto"):
        self.minRF = self._ratio("minRF", minRF, allow_zero=False)
        self.minCS = self._ratio("minCS", minCS, allow_zero=False)
        self.maxOR = self._ratio("maxOR", maxOR, allow_zero=True)
        # Reuse input and reporting APIs; minSup is not used by this miner.
        super().__init__(iFile, 1, sep, use_gds=use_gds, use_gpu_io=use_gpu_io)

    @staticmethod
    def _ratio(name, value, allow_zero):
        if (isinstance(value, bool) or not isinstance(value, Real)
                or value > 1 or value < 0 or not math.isfinite(value)
                or (not allow_zero and value == 0)):
            interval = "[0, 1]" if allow_zero else "(0, 1]"
            raise ValueError(f"{name} must be a finite ratio in {interval}")
        return float(value)

    def _extensions(self, cp, pattern, covered, coverage, start, bits, supports):
        # Each active DFS frame retains only one batch, rather than a full level.
        words = bits.shape[1]
        batch_size = max(1, min(self._EXTENSION_BATCH_SIZE,
                               self._EXTENSION_BATCH_BYTES // max(1, words * 12)))
        for begin in range(start, len(supports), batch_size):
            end = min(begin + batch_size, len(supports))
            _, overlaps = intersect_extensions(cp, covered, bits[begin:end])
            for offset, overlap in enumerate(overlaps):
                item = begin + offset
                if overlap / supports[item] <= self.maxOR:
                    union_count = coverage + supports[item] - overlap
                    yield (pattern + (item,), covered | bits[item], union_count, item + 1)

    def mine(self):
        """Count singletons and expand overlap-valid prefixes on the GPU."""
        self._startTime = time.perf_counter()
        self._finalPatterns = {}
        cp = self._getCudaModule()
        items, rows, columns = self._getDevicePairs(cp)
        bits = build_bitsets(cp, rows, columns, self._transactionCount, len(items))
        supports = count_supports(cp, bits, [[i] for i in range(len(items))])
        order = sorted((i for i, count in enumerate(supports)
                        if count and count / self._transactionCount >= self.minRF),
                       key=lambda i: (-supports[i], items[i]))
        if order:
            bits = bits[cp.asarray(order)]
            names = [items[i] for i in order]
            supports = [supports[i] for i in order]
            roots = (((i,), bits[i], supports[i], i + 1) for i in range(len(order)))
            stack = [iter(roots)]
            while stack:
                node = next(stack[-1], None)
                if node is None:
                    stack.pop()
                    continue
                pattern, covered, coverage, start = node
                if coverage / self._transactionCount >= self.minCS:
                    self._finalPatterns[tuple(names[i] for i in pattern)] = coverage
                if start < len(order):
                    stack.append(self._extensions(
                        cp, pattern, covered, coverage, start, bits, supports))
        cp.cuda.get_current_stream().synchronize()
        self._endTime = time.perf_counter()

    def getPatternsAsDataFrame(self):
        """Return pattern names and absolute coverage counts."""
        frame = super().getPatternsAsDataFrame()
        return frame.rename(columns={"Support": "Coverage"})

    def printResults(self):
        print("Total number of Coverage Patterns:", len(self._finalPatterns))
        print("Total Memory in USS:", self.getMemoryUSS())
        print("Total Memory in RSS:", self.getMemoryRSS())
        print("Loading time (seconds):", self.getLoadingTime())
        print("Mining time (seconds):", self.getMiningTime())
        print("Total time (seconds):", self.getTotalRuntime())


if __name__ == "__main__":
    if len(sys.argv) not in (6, 7):
        sys.exit("Usage: python -m cupami.coveragePattern.cuCMine "
                 "<inputFile> <outputFile> <minRF> <minCS> <maxOR> [sep]")
    miner = cuCMine(sys.argv[1], *map(float, sys.argv[3:6]),
                    sep=sys.argv[6] if len(sys.argv) == 7 else None)
    miner.mine()
    miner.save(sys.argv[2])
    miner.printResults()
