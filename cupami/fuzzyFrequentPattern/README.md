# Fuzzy frequent patterns

Fuzzy frequent pattern mining finds combinations of items described by regions such as Low, Medium, and High. For example, the quantity of milk bought in a transaction can belong partly to `milk.Low` and partly to `milk.High`.

Each region has a membership value from 0 to 1. A value of 0 means no membership, and 1 means full membership. Membership functions convert quantities into these values before mining. The miners in this folder expect the transformed memberships as input.

## Example and fuzzy support

This example uses the memberships from [PAMI's MFFIMiner example](https://github.com/UdayLab/PAMI/blob/main/docs/fuzzyFrequentPatternMining.md#9-mining-multiple-fuzzy-frequent-itemsets-using-mffiminer).

| Transaction | milk.Low | milk.High | bread.High |
| --- | --- | --- | --- |
| 1 | 0.8 | 0.2 | 0.9 |
| 2 | 0.3 | 0.7 | 0.6 |
| 3 | 0.6 | 0.4 | 0.8 |
| 4 | 0.1 | 0.9 | 0.4 |

For a pattern, cuPAMI takes the minimum membership of its items in each transaction and adds these contributions. Missing items contribute zero. This total is the pattern's fuzzy support.

For `{milk.High, bread.High}`, the support is:

```text
min(0.2, 0.9) + min(0.7, 0.6) + min(0.4, 0.8) + min(0.9, 0.4)
= 0.2 + 0.6 + 0.4 + 0.4
= 1.6
```

A pattern is frequent when its support meets `minSup`. With an absolute threshold of `minSup=1`, this pattern is frequent.

---

## Fuzzy frequent patterns

`cuFFIMiner` keeps the strongest region for each base item, based on its total membership across the database. Here, `milk.High` totals 2.2 and `milk.Low` totals 1.8, so it keeps `milk.High`. Patterns involving `milk.Low` are not explored.

---

## Multiple fuzzy frequent patterns

Multiple fuzzy frequent itemset mining keeps every region that meets the support threshold. At `minSup=1`, both milk regions are kept. It can find `{milk.Low, bread.High}` with support 1.8 as well as `{milk.High, bread.High}` with support 1.6.

Each pattern still contains at most one region of a base item. `{milk.Low, milk.High}` is excluded because both labels describe milk.

### Algorithms

- `cuMFFIMiner` implements shared base-item traversal (SBT) from the paper “cuMFFP-Miner: GPU-Accelerated Multiple Fuzzy Frequent Pattern Mining via Shared Base-Item Traversal” by Mithun Thangaraj and Rage Uday Kiran. It reuses transaction matching across region combinations of a base item.
- `cuMultiFuzzyBaseline` is the flat GPU baseline from the same paper. It processes region combinations as separate traversal jobs.

See [fuzzy CSV format and support details](../../docs/fuzzy-data.md) and the guides for [cuFFIMiner](../../docs/algorithms/cuFFIMiner.md), [cuMFFIMiner](../../docs/algorithms/cuMFFIMiner.md), and [cuMultiFuzzyBaseline](../../docs/algorithms/cuMultiFuzzyBaseline.md).

## References

- J. C.-W. Lin, T. Li, P. Fournier-Viger, and T.-P. Hong, [“A Fast Algorithm for Mining Fuzzy Frequent Itemsets”](https://doi.org/10.3233/IFS-151936), Journal of Intelligent & Fuzzy Systems, 29(6), 2015. Fuzzy support and strongest-region model.
- J. C.-W. Lin et al., [“Efficient Mining of Multiple Fuzzy Frequent Itemsets”](https://doi.org/10.1007/s40815-016-0246-1), International Journal of Fuzzy Systems, 19(4), 2017. Multiple-region fuzzy itemset model.
- Mithun Thangaraj and Rage Uday Kiran, “cuMFFP-Miner: GPU-Accelerated Multiple Fuzzy Frequent Pattern Mining via Shared Base-Item Traversal,” The University of Aizu, Japan. Describes `cuMFFIMiner` and `cuMultiFuzzyBaseline`.

The CUDA source lineage and implementation differences are recorded in [algorithm references](../../docs/algorithm-references.md#fuzzy-patterns).
