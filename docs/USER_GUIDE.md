# USER GUIDE

## Start
`python3 app/main.py` → http://localhost:8000. No internet needed.

## Navigation
- **HOME** — what the system is; pipeline; live stats; "ANALYZE CONTAMINANT" (guided chain).
- **CONTAMINANT** — tetracycline identity, 2D/3D structure, provenance, Nigerian occurrence records, schematic map, One-Health frame.
- **DISCOVER** — six biocatalyst candidates with evidence class (E1–E3 here), AMR screening, priority bars; preset stances switch ranking.
- **CANDIDATE** — full dossier: annotation, sequence (FASTA), structure (3D viewer; EXPERIMENTAL vs PREDICTED labelling), docking metrics & contacts, 13-component score, "WHY?" breakdown, uncertainty flags, export/compare links.
- **SAFETY** — transformation pathways (KNOWN solid vs PREDICTED dashed), products with residual-activity classes, cheminformatics triage.
- **AMR SHIELD** — resistance classes, per-candidate screening, selection context.
- **CIRCULAR** — cassava flow chain; adsorption/degradation/detoxification distinctions; spent-adsorbent end-of-life; intervention options A–D table.
- **DECISION** — presets + 13 custom weight sliders; ranking; WHY panels; sensitivity; ablation; baselines.
- **COMPARE** — 2–4 candidates side-by-side.
- **REPORT** — export PDF/CSV/JSON; preview includes disclaimer and sources.
- **ABOUT** — methods, honesty contract, limitations.

## Reading the chips
`E1` experimental enzyme · `E2` experimental system · `E3` functional-genomics/family ·
`E4` structural/computational · `E5` hypothesis.
AMR colours: red HIGH, amber MODERATE, green LOW concern; grey UNKNOWN.
EXPERIMENTAL (green) vs PREDICTED (yellow) structure labels.

## If something says "Data unavailable"
That is the intended, honest behaviour — the system refuses to fabricate.
