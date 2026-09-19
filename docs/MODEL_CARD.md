# MODEL CARD — TETRA-SHIELD PRIORITY ENGINE v1.0

## What the "model" is
A deterministic, fully inspectable **evidence-integration engine** (weighted additive
score with documented component formulas), *not* a fitted statistical/ML model.

## Why no supervised ML was fitted (deliberate, documented choice)
- Labelled data available: **6 candidates**, each graded on categorical evidence classes.
- Any fitted classifier/regressor (RF, XGBoost, logistic) on n=6 with 13 features would be
  textbook overfitting; cross-validation is undefined at this scale; sequence-cluster or
  scaffold splits would leave folds of size 1–2.
- The scientifically defensible alternative — used here — is a transparent weighted
  evidence score with **Monte-Carlo sensitivity analysis** (400 random weight sets) so the
  user sees exactly how fragile (or robust) rankings are: Kendall's W = 0.955.
- ML-similarity measures are used *deterministically* where they belong:
  RDKit Morgan-fingerprint Tanimoto (chemical similarity triage),
  Biopython sequence identity (family assignment context). These are labelled
  "deterministic similarity", never "predictions."

## Inputs
- Evidence classes E1–E5 from curated literature/databases (with DOIs/accessions).
- Computed artifacts: validated docking scores & contacts (smina/Vina, redock RMSD 1.84 Å),
  sequence identity %, cheminformatic descriptors, AlphaFold mean pLDDT.
- Risk components from curated AMR/product-safety/uncertainty records.

## Outputs
TETRA-SHIELD PRIORITY SCORE [0–100] per candidate + full component breakdown +
uncertainty flags + verdict. **NOT a risk score** (see disclaimer, enforced in reports).

## Intended use
Research/education triage: decide *which biocatalyst candidates to validate experimentally
first* for environmental tetracycline biotransformation, and *what hazards accompany them*.

## Out of scope / misuse
Clinical decisions, regulatory determinations, discharge compliance, tox classification.

## Validation (what was actually measured)
- Docking protocol: re-docking co-crystallised ligand, RMSD 1.84 Å (PASS).
- Score stability: Monte-Carlo W = 0.955; per-candidate P(top-3): TETX2 1.00, LAC 1.00, TETX 0.89.
- Ablation: layer removals produce interpretable, directionally-correct shifts (reported verbatim).
- Baselines: integrated ordering differs from every single-lens baseline (justifying integration).
- Software tests: 39 automated checks pass (`tests/test_core.py`).

## Known failure modes (honest)
- Component values for catalytic plausibility / transformation confidence are expert-set
  constants per candidate — defensible from literature, but NOT learned; changing them
  within reason is what sensitivity analysis is for.
- Laccase/MnP substrate compatibility relies on E2 literature; rigid docking cannot
  capture outer-sphere oxidation (recorded as a negative result, not hidden).
- Product tox data are sparse field-wide; we surface UNKNOWN rather than impute.

## Ethical considerations
No personal data; no API keys in source; all scientific claims traceable
(provenance.json). AMR labels framed to avoid stigmatising regions: Nigerian records are
point studies, explicitly not national characterisations.
