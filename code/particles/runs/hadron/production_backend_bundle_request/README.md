# OPH Hadron Production Backend Bundle Request

This directory is the fillable production request for the current stable-channel
hadron lane. It is not a completed production bundle yet.

Files:

- `backend_run_manifest.json`: canonical production manifest, including the
  seeded `2+1`, QED-off ensemble/cfg/source schedule and all required HDF5
  dataset paths.
- `dataset_index.json`: flat checklist of every dataset that must be written.
- `correlators.h5`: absent by design in this manifest-only handoff. A real
  backend must create it.
- `arrays/`: optional no-HDF5 handoff directory. If the backend writes one
  whitespace-separated numeric text file per `array_file` listed in
  `dataset_index.json`, the repo can assemble an inline backend export.

Required backend output:

- `pi_iso`
- `N_iso_direct`
- `N_iso_exchange`

Each dataset must be little-endian float64, one-dimensional, finite, and have
the exact length listed in `dataset_index.json`. The arrays must come from real
production backend execution, not diagnostic, surrogate, fitted, or target-filled
values.

After `correlators.h5` is filled and the manifest provenance placeholders are
replaced, validate from `reverse-engineering-reality/code/particles` with:

```bash
python3 hadron/run_production_backend_writeback.py \
  --sequence-population runs/hadron/stable_channel_sequence_population.json \
  --receipt runs/hadron/runtime_schedule_receipt_N_therm_and_N_sep.json \
  --payload runs/hadron/stable_channel_cfg_source_measure_payload.json \
  --backend-bundle runs/hadron/production_backend_bundle_request \
  --n-therm 2048 \
  --n-sep 512 \
  --schedule-provenance "production_backend_bundle_request"
```

The readiness report must show `publication_bundle_ready=true` before any
source-side hadron row is promoted.

No-HDF5 array-file assembly path:

```bash
python3 hadron/assemble_backend_export_from_array_files.py \
  --manifest runs/hadron/production_backend_bundle_request/backend_run_manifest.json \
  --dataset-index runs/hadron/production_backend_bundle_request/dataset_index.json \
  --array-dir runs/hadron/production_backend_bundle_request \
  --output runs/hadron/production_backend_bundle_request/backend_export_inlined.json

python3 hadron/run_production_backend_writeback.py \
  --sequence-population runs/hadron/stable_channel_sequence_population.json \
  --receipt runs/hadron/runtime_schedule_receipt_N_therm_and_N_sep.json \
  --payload runs/hadron/stable_channel_cfg_source_measure_payload.json \
  --backend-bundle runs/hadron/production_backend_bundle_request/backend_export_inlined.json \
  --n-therm 2048 \
  --n-sep 512 \
  --schedule-provenance "production_backend_array_files"
```

External production backend runner:

```bash
OPH_HADRON_BACKEND_COMMAND="/path/to/real_backend_command --fill $OPH_HADRON_REQUEST_DIR" \
python3 hadron/run_external_production_backend.py \
  --request-dir runs/hadron/production_backend_bundle_request \
  --schedule-provenance "external_production_backend"
```

The runner exposes these environment variables to the backend command:

- `OPH_HADRON_REQUEST_DIR`
- `OPH_HADRON_MANIFEST`
- `OPH_HADRON_DATASET_INDEX`
- `OPH_HADRON_ARRAY_DIR`

If no backend command is supplied, or if any required array file is missing, the
runner exits without creating production values.
