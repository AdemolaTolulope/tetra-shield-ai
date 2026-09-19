# DEVELOPER GUIDE

## Architecture
```
[fetchers: curl/pug-rest/uniprot/rcsb] -> data/raw
src/pipeline/build_kb.py                -> data/processed/kb/*.json
src/docking/prep_docking.py|analyze_docking.py|redock_rmsd.py -> results/docking/
src/chemistry/mol_graphics.py           -> results/product_cheminformatics.json + assets/mol/*.svg
src/bioinformatics/sequence_analysis.py -> results/sequence_analysis.json
src/scoring/engine.py                   -> run_all()/sensitivity()/ablation()/baselines()
src/scoring/report.py                   -> JSON/CSV/PDF
app/main.py (FastAPI)                   -> /api/* + static SPA
app/static (3Dmol.js local)             -> viewers, all offline
```

## Key invariants (do not break)
1. Real data only; every record carries provenance.
2. Missing data → "Data unavailable"/UNKNOWN, never fabricate.
3. Structure kind is displayed (experimental/predicted/unavailable) everywhere.
4. Docking is one component among 13; never displayed as catalytic proof.
5. Product safety UNKNOWN ≠ safe; AMR "no hit" ≠ AMR-free.
6. Weights adjustable; presets are entry points, not doctrine.

## Adding a candidate
Insert record in `candidates.json` (schema identical to existing), put FASTA in
`data/raw/`, optionally add structure to `STRUCT_MAP` (app/main.py) and components
in `engine::component_scores` (currently explicit per-candidate constants + computed
subscores). Re-run `tests/test_core.py`.

## Adding a contaminant (future module)
Mirror `contaminant_tetracycline.json` + products + pathways + occurrence records;
the SPA treats contaminant object generically (~70% reuse). Coverage claims remain
bound to actually-populated records.

## Performance
All heavy compute is at build time; runtime serves JSON. Sensitivity (400 iterations ×
6 candidates × 13 components) is sub-second. KB cached via `lru_cache`.

## Security
No credentials, no PII, no telemetry; smina binary included for x86_64 Linux.
