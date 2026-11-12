# Frequent patterns

This package finds item combinations that occur together in enough transactions. A pattern is frequent when its support meets `minSup`.

CUDA miners use CuPy and an NVIDIA GPU. `clApriori` uses OpenCL. Transactional input formats and support thresholds are described in the [algorithm guides](../../docs/algorithms/README.md).

## Algorithms

### Apriori

`cuApriori` grows candidate itemsets level by level and counts support on the GPU.

---

### Eclat

`cuEclat` searches itemsets depth first using transaction bitsets.

---

### FP-Growth

`cuFPGrowth` builds an FP-tree and mines conditional patterns.

---

### OpenCL Apriori

`clApriori` is an OpenCL implementation of Apriori for OpenCL GPUs.

## References

- R. Agrawal and R. Srikant, [“Fast Algorithms for Mining Association Rules in Large Databases”](https://www.vldb.org/conf/1994/P487.PDF), VLDB 1994. Apriori search and pruning.
- F. Zhang, Y. Zhang, and J. Bakos, [“GPApriori: GPU-Accelerated Frequent Itemset Mining”](https://doi.org/10.1109/CLUSTER.2011.61), CLUSTER 2011. GPU support counting for Apriori.
- M. J. Zaki, [“Scalable Algorithms for Association Mining”](https://doi.org/10.1109/69.846291), IEEE TKDE 2000. Eclat search.
- J. Han, J. Pei, and Y. Yin, [“Mining Frequent Patterns without Candidate Generation”](https://doi.org/10.1145/342009.335372), SIGMOD 2000. FP-tree and FP-Growth.

The CUDA implementation sources and local changes are documented in [algorithm references](../../docs/algorithm-references.md#frequent-patterns). See the individual guides for [cuApriori](../../docs/algorithms/cuApriori.md), [cuEclat](../../docs/algorithms/cuEclat.md), [cuFPGrowth](../../docs/algorithms/cuFPGrowth.md), and [clApriori](../../docs/algorithms/clApriori.md).
