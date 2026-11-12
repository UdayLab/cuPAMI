# Extra tools

This package contains data generators, format converters, and shared input/output helpers used by cuPAMI's miners.

## Synthetic data

`syntheticDataGenerator` creates transactional, binary transactional, quantitative transactional, and temporal databases. These are configurable local generators, not reproductions of an external synthetic workload model. See the [transaction format guide](../../docs/transaction-formats.md).

---

## Converters and file support

`fileConverter` and `datasetConverter` convert datasets among supported formats. Shared readers handle temporal and quantitative records. File schemas, optional dependencies, and GPU Direct Storage loading are described in [transaction formats](../../docs/transaction-formats.md).

The generators and converters do not implement pattern-mining algorithms. Their source and design notes are summarized in [algorithm references](../../docs/algorithm-references.md#shared-code-generation-and-formats).
