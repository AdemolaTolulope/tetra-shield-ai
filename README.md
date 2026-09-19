# TETRA‑SHIELD AI — Environmental Biotransformation Decision Intelligence

**BioShield‑X platform · Module 1: Tetracycline · NSBS Innovation Challenge 2026 — "Step Out and Innovate" · Computational Biology & Bioinformatics · Working Prototype**

> Antibiotic *removal* is not *detoxification*. TETRA‑SHIELD is an explainable
> computational decision engine that evaluates whether a **biological** intervention
> against antibiotic pollution is plausible, what **transformation products** result,
> whether they remain **biologically active**, what the **AMR implications** are, and
> **what should be validated in the lab first**.

---

## What it actually computes (nothing is faked)

| Layer | Method | Artifact |
|---|---|---|
| Molecular docking | smina (AutoDock Vina 1.1.2), seed 42; receptor = PDB **2Y6R** chain A + FAD | top affinity **−9.7 kcal/mol** (tetracycline); **redock validation RMSD 1.84 Å** vs co‑crystallised 7‑chlortetracycline |
| Cheminformatics | RDKit descriptors, Morgan‑FP Tanimoto, SMARTS alerts | `results/product_cheminformatics.json` |
| Sequence intelligence | Biopython global alignments | identity matrix (TetX↔TetX2 **99.5%**) |
| Evidence engine | deterministic component scoring (no fitted ML — see `docs/MODEL_CARD.md`) | `results/decision_engine_validation.json` |
| Robustness | 400× Monte‑Carlo weight perturbation, Kendall's W, ablation, baselines | **W = 0.955** |
| Reports | reportlab PDF + JSON + CSV | `/api/report/{id}?format=pdf` |

## Run it (offline‑first)

```bash
cd tetra-shield-ai
pip install -r requirements.txt          # Open Babel CLI is needed only for re-docking
python3 app/main.py                       # or: uvicorn app.main:app --host 0.0.0.0 --port 8000
# open http://localhost:8000 — click "ANALYZE CONTAMINANT"
```

The app is fully functional **without internet** (cached, provenance‑stamped data).
Test suite: `python3 tests/test_core.py` → 39 tests.

## Repository map

```
app/            FastAPI server + static SPA (3Dmol.js bundled)
src/chemistry        cheminformatics (RDKit)
src/bioinformatics   sequence analysis
src/docking          receptor/ligand prep, smina runs, validation, contacts
src/scoring          TETRA-SHIELD decision engine + report generator
src/pipeline         knowledge-base builder + manifest generator
data/raw         fetched records (PubChem/UniProt/PDB/AlphaFold)
data/processed   kb/*.json + structures/ (provenance: data_manifest.csv, provenance.json)
results/         docking results, sequence analysis, validation JSON, demo PDF
tests/           test_core.py (39 tests)
docs/            METHODOLOGY, MODEL_CARD, VALIDATION_REPORT, LIMITATIONS, SCIENTIFIC_AUDIT,
                 DATA_SOURCES, USER_GUIDE, DEVELOPER_GUIDE, DEMO_GUIDE, NAMING,
                 COMPETITION_PACKAGE, PITCH_DECK, FINAL_REVIEW
```

## Core distinctions (product identity)

`REMOVAL ≠ DEGRADATION` · `DEGRADATION ≠ DETOXIFICATION` · `DOCKING ≠ CATALYSIS` ·
`SEQUENCE SIMILARITY ≠ FUNCTIONAL PROOF` · `PREDICTED STRUCTURE ≠ EXPERIMENTAL` ·
`NO AMR HIT ≠ AMR-FREE` · `NO TOXICITY DATA ≠ SAFE`

**TETRA‑SHIELD PRIORITY SCORE** is a computational prioritisation framework — *not* a
validated clinical, regulatory, toxicological or environmental risk score.
