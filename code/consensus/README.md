# Consensus Code

This directory contains OPH packet-net and consensus-protocol artifacts.

Canonical runners:

- `export_verified_tree_packet_net.py`: exports the verified tree packet-net repair domain.
- `reference_architecture_benchmark_suite.py`: runs the fixed-cutoff Z2/S3 reference-architecture benchmark suite for issue #237.

Run the benchmark suite from the repo root:

```bash
python3 code/consensus/reference_architecture_benchmark_suite.py
python3 -m pytest code/consensus/test_reference_architecture_benchmark_suite.py
```

The current emitted suite artifact is `code/consensus/runs/reference_architecture_benchmark_suite_current.json`.
It is a fixed-cutoff analytic benchmark surface only; it does not claim continuum/gravity closure or uniqueness of the microscopic UV completion.

## License And Patent Policy

This code surface is part of the OPH public repository. See the main
[LICENSE](../../LICENSE) and
[OPH Open Use And Anti-Patent Covenant](../../PATENTS.md).
