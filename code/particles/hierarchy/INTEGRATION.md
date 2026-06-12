# Hierarchy Bundle Integration

This directory carries the frozen electroweak-hierarchy proof bundle supplied
for the OPH hierarchy audit. It is separate from the rounded `1.63094`
calibration carrier used by the older D10 particle-code path.

The bundle’s public endpoint branch uses

```text
P_C = 1.630968209403959324879279847782648941
alpha_U(P_C) = 0.041124336195630495
v/E_star = 2.0199803239725553e-17
```

The source-audit branch keeps the public Thomson endpoint out of the upstream
path and records

```text
P_cand = 1.63097209569432901817967892561191884270169
alpha_U(P_cand) = 0.04112424744557487
v(P_cand)/E_star = 2.0198114150099223e-17
```

The claim closed here is local electroweak hierarchy closure on the declared
source graph:

```text
P_star -> alpha_U(P_star) -> v/E_star
```

The `R_U` Krawczyk certificate proves a unique source zero inside the supplied
interval for the declared formula stack. The bundle also records its boundary:
source-only public Thomson transport, raw outward-rounded interval logs,
Higgs/top interval boxes, the Higgs RG defect bound, theorem-grade W/Z
promotion, the full no-G clock stack, and the local/global resonance theorem
are outside this certificate.

Run the local guard with:

```bash
python3 validators/validate_bundle.py
python3 computations/hierarchy_recompute.py
python3 -m pytest test_hierarchy_bundle.py
```
