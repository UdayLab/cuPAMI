# Coverage patterns

`cuCMine` finds itemsets whose combined transaction coverage is high and whose
items add transactions with limited overlap. It uses CUDA transaction bitsets.

```python
from cupami import cuCMine

rows = [["a"], ["a"], ["b"], ["b"], ["c"]]
miner = cuCMine(rows, minRF=0.2, minCS=1.0, maxOR=0.0)
miner.mine()
assert miner.getPatterns() == {"a\tb\tc": 5}
```

All thresholds are ratios: `minRF` and `minCS` are in `(0, 1]`; `maxOR`
is in `[0, 1]`. Every item must meet `minRF`. Items are ordered by decreasing
singleton support, breaking ties lexically. For each extension by item `i`,
`overlap = |covered_transactions ∩ transactions(i)| / |transactions(i)|`
must be at most `maxOR`. An overlap-valid prefix can continue growing even when
its coverage is below `minCS`. Output, including singletons, must meet `minCS`.
This is the support-ordered prefix search used by PAMI's CMine implementations.

Inputs: transaction iterables, CSV, BIN and Parquet. The shared readers remove
duplicate items and omit empty transactions; ratios use the remaining row count.
`sep`, `use_gpu_io` and `use_gds` follow cuApriori. Required GDS supports local
BIN input only. CUDA mining requires CuPy and an NVIDIA GPU; Parquet additionally
requires PyArrow. The default input mode selects an available loading backend.

`getPatterns()` maps tab-separated item names in mining order to **absolute
union coverage counts**. `getPatternsAsDataFrame()` returns `Patterns` and
`Coverage` columns. `save(path)` writes `pattern : count` lines. Timing, memory
and input-backend methods match other cuPAMI miners.

See the [algorithm guide](../../docs/algorithms/cuCMine.md) and
[notebook](../../notebooks/coveragePattern/cuCMine.ipynb).
