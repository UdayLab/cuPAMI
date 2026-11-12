# Partial-periodic patterns

Partial-periodic mining finds itemsets that appear in enough consecutive occurrence gaps no larger than a chosen period. Unlike periodic-frequent mining, it counts qualifying gaps between occurrences and does not include the gaps at the beginning or end of the observation window.

Input rows contain a timestamp followed by items. `period` is the largest gap counted, and `minPS` is the minimum number of qualifying gaps. See the [algorithm guides](../../docs/algorithms/README.md) and the [implementation references](../../docs/algorithm-references.md#partial-periodic-patterns).

## Algorithms

### cuPPPApriori

`cuPPPApriori` checks candidates level by level.

---

### cuPPPEclat

`cuPPPEclat` searches depth first using item occurrence bitsets.

## References

- R. Uday Kiran, J. N. Venkatesh, M. Toyoda, M. Kitsuregawa, and P. Krishna Reddy, [“Discovering Partial Periodic-Frequent Patterns in a Transactional Database”](https://doi.org/10.1016/j.jss.2016.11.035), Journal of Systems and Software 125, 2017. Partial-periodic pattern model.
- [PAMI `gPPMiner`](https://github.com/UdayLab/PAMI/blob/48d0c25fb5f1e4ff32e797fa00873033921f1aa7/PAMI/partialPeriodicPattern/cuda/gPPMiner.py) is the CUDA bitset implementation reference. cuPAMI follows its GPU intersection and temporal scanning approach while using the public `PPP_ECLAT` support semantics.
