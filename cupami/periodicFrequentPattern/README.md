# Periodic-frequent patterns

These miners find itemsets that occur often enough and whose gaps between occurrences stay within a maximum period. The time gap is measured between timestamps, including the start and end of the observation window.

`minSup` sets the minimum support and `maxPer` sets the maximum allowed gap. Input rows contain a timestamp followed by items. See [temporal input details](../../docs/transaction-formats.md) and the [algorithm guides](../../docs/algorithms/README.md).

## Algorithms

### cuPFApriori

`cuPFApriori` uses level-wise candidate search.

---

### cuPFEclat

`cuPFEclat` uses depth-first search with vertical occurrence bitsets.

---

### cuPFGrowth

`cuPFGrowth` uses FP-tree search with periodicity checks.

---

### gPFMiner

`gPFMiner` uses a timestamp-indexed bitset representation.

## References

- S. Tarun, R. Uday Kiran, Y. Watanobe, and K. Goda, [“A Novel GPU-Accelerated Algorithm to Discover Periodic-Frequent Patterns in Temporal Databases”](https://doi.org/10.1109/BigData55660.2022.10020216), IEEE Big Data 2022. GPU timestamp-bitset mining.
- R. Uday Kiran, M. Kitsuregawa, and P. Krishna Reddy, [“Efficient Discovery of Periodic-Frequent Patterns in Very Large Databases”](https://doi.org/10.1016/j.jss.2015.10.035), Journal of Systems and Software 112, 2016. Periodic-frequent pattern model.

PAMI's CUDA bitset implementation and cuPAMI's row-based temporal representation are compared in [algorithm references](../../docs/algorithm-references.md#periodic-frequent-patterns). The `gPFMiner` timestamp layout is discussed separately in [its guide](../../docs/algorithms/gPFMiner.md).
