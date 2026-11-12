# Georeferenced frequent patterns

Georeferenced pattern mining finds frequent itemsets while enforcing spatial neighbourhood constraints. Items must meet the support threshold and satisfy the configured neighbour relationships.

## Algorithm

`cuSpatialEclat` reads an item transaction file and a neighbour file. It applies neighbour pruning on the CPU and counts support on the GPU using the shared CUDA Eclat bitset kernels.

See [spatial input details](../../docs/spatial-data.md) and the [cuSpatialEclat guide](../../docs/algorithms/cuSpatialEclat.md).

## References

- R. Uday Kiran, S. Shrivastava, P. Fournier-Viger, K. Zettsu, M. Toyoda, and M. Kitsuregawa, [“Discovering Frequent Spatial Patterns in Very Large Spatiotemporal Databases”](https://doi.org/10.1145/3397536.3422206), SIGSPATIAL 2020. Spatial pattern model.
- PAMI [`SpatialECLAT`](https://github.com/UdayLab/PAMI/blob/48d0c25fb5f1e4ff32e797fa00873033921f1aa7/PAMI/georeferencedFrequentPattern/basic/SpatialECLAT.py) is the CPU neighbour-pruning reference; PAMI [`cuEclatBit`](https://github.com/UdayLab/PAMI/blob/48d0c25fb5f1e4ff32e797fa00873033921f1aa7/PAMI/frequentPattern/cuda/cuEclatBit.py) is the GPU intersection reference.

The CPU/GPU division and local changes are detailed in [algorithm references](../../docs/algorithm-references.md#spatial-patterns).
