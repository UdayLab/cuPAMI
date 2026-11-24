# cuCMine

Mine coverage patterns with support-ordered prefix expansion and CUDA bitsets.
A pattern covers transactions containing **at least one** of its items.

```python
from cupami import cuCMine

rows = [["a", "b"], ["a"], ["a"], ["b"], ["c"]]
miner = cuCMine(rows, minRF=0.2, minCS=0.8, maxOR=0.5)
miner.mine()
assert miner.getPatterns() == {"a\tb": 4, "a\tb\tc": 5, "a\tc": 4}
miner.save("coverage-patterns.txt")
```

## Parameters and semantics

| Parameter | Meaning |
|---|---|
| `iFile` | Transaction iterable or CSV, BIN or Parquet path; HTTP(S) CSV is supported |
| `minRF` | Minimum singleton relative frequency, in `(0, 1]` |
| `minCS` | Minimum union coverage divided by transaction count, in `(0, 1]` |
| `maxOR` | Maximum extension overlap divided by the added item's support, in `[0, 1]` |
| `sep` | CSV delimiter; `None` detects comma or tab |
| `use_gpu_io` | `"auto"`, `True`, or `False`, as in cuApriori |
| `use_gds` | `"auto"`, `True`, or `False`; required GDS supports local BIN only |

Thresholds are ratios even when passed as integers: `1` means 100%, not one
transaction. Booleans, strings, nonfinite values and out-of-range values are
rejected. Empty transactions are omitted by the existing cuPAMI readers and
duplicate items count once. The denominator is the number of nonempty rows.

Items are ordered by descending singleton support with lexical ties. At each
extension, the candidate item's transaction set is intersected with the union
already covered. The overlap ratio must be at most `maxOR` at every ordered
prefix. Equality is accepted. Coverage is only an output condition: prefixes
below `minCS` continue growing if their overlap is valid. Singletons have no
overlap test but must meet both `minRF` and `minCS` to appear in the output.

`getPatterns()` returns tab-separated item names in mining order mapped to
integer union counts. `getPatternsAsDataFrame()` uses `Patterns` and `Coverage`
columns. `save()` writes `pattern : count` lines. `getLoadingTime()`,
`getMiningTime()` and `getTotalRuntime()` return seconds; `getRuntime()` is the
mining-time alias. Memory methods report process bytes.

## GPU implementation

Singleton bitsets are built using the shared cuPAMI kernels. An iterative
depth-first search evaluates later singleton extensions in bounded GPU batches.
A CUDA block per extension counts the intersection using word-parallel AND and
popcount. Coverage follows `|A ∪ B| = |A| + |B| - |A ∩ B|`, and accepted children
retain GPU union bitsets. The CPU schedules search and checks returned counts.
Candidate scratch buffers are bounded, but total search/output can still grow
exponentially with permissive overlap thresholds.

Mining requires CuPy and an NVIDIA CUDA GPU. Parquet input requires PyArrow.

```bash
python -m cupami.coveragePattern.cuCMine input.csv output.txt 0.2 0.8 0.5
```

## References and differences

Model: Sripada, Reddy and Kiran, *Coverage patterns for efficient banner
advertisement placement*, WWW Companion 2011,
[DOI: 10.1145/1963192.1963259](https://doi.org/10.1145/1963192.1963259).
The [SSDBM 2013 paper](https://www.tkl.iis.u-tokyo.ac.jp/new/uploads/publication_file/file/619/20-5-2013_ssdbm.pdf)
describes relative frequency, union coverage and ordered overlap.

Implementation reference:
[PAMI CMine](https://github.com/UdayLab/PAMI/blob/48d0c25fb5f1e4ff32e797fa00873033921f1aa7/PAMI/coveragePattern/basic/CMine.py)
and
[PAMI cuCMine](https://github.com/UdayLab/PAMI/blob/48d0c25fb5f1e4ff32e797fa00873033921f1aa7/PAMI/coveragePattern/cuda/cuCMine.py).
This implementation uses the same overlap-valid prefix growth with iterative
DFS rather than PAMI CUDA's breadth-first frontier. Local differences include
lexical tie-breaking, shared input readers, uint32 bitsets with uint64 counts,
validated ratio parameters, and applying `minCS` to singleton output. PAMI's
referenced implementations return all `minRF` singletons, even below `minCS`.
This is not an implementation of CMine++'s additional pruning rules.
