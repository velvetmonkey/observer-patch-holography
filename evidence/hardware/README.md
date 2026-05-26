# Hardware Evidence Bundles

This directory is the public evidence surface for OPH hardware-facing claims.
Paper text may cite hardware evidence only when the cited run has a public bundle
here, or when it points to a public pinned subrepository commit with equivalent
raw data and metadata.

Development notes, private runtime logs, and unpublished bench transcripts do
not carry paper evidence weight. They may motivate architecture, but they are
not cited as evidence until mirrored into an auditable public bundle.

## Allowed Claim Form

Use conservative claim language:

```text
Module set M produced candidate enrichment or a reproducible readout signature
on benchmark T, under controls C, and exact verifier V accepted the reported
hits.
```

Do not use this directory to claim that an optical chamber directly solved a
hard problem, proved OPH, proved a complexity-class collapse, or replaced a
mathematical theorem surface.

## Bundle Requirements

Each bundle should include:

- `manifest.json` with stable bundle ID, dates, operators, module IDs, body
  hashes, firmware hashes, wiring-map hashes, task IDs, verifier IDs, and claim
  status.
- Raw calibration data: dark scan, low-power sweep, coupling matrix, MDD or
  discharge trace when applicable, and recurrence or ring-diversity scans for
  toroidal bodies.
- Body/controller provenance: mesh/body hashes, board IDs, firmware hashes,
  wiring maps, and photos or photo hashes.
- Task evidence: task definition, scorebook, candidate records, verifier
  receipts, and exact-verifier source or hash.
- Controls: negative controls, shuffle/replay controls where applicable,
  duplicate-body checks, and symmetric-reference or Echosahedron shadow checks
  where applicable.
- `claim.md` stating the strongest allowed claim and explicit non-claims.

The `template/` directory gives a minimal shape for future bundles.

## License And Patent Policy

This hardware evidence surface is part of the OPH public repository. See the
main [LICENSE](../../LICENSE) and
[OPH Open Use And Anti-Patent Covenant](../../PATENTS.md). OPH-derived
hardware designs, devices, experimental procedures, verification methods,
software, and implementation patterns may be studied, tested, implemented,
modified, deployed, manufactured, and shared, but may not be used to create
patent claims that restrict others from practicing OPH-derived work.
