# METHODOLOGY — TETRA-SHIELD AI (scientific methods)

## 1. Intelligence chain
CONTAMINANT → ENVIRONMENTAL CONTEXT → BIOLOGICAL TRANSFORMATION OPPORTUNITIES →
ENZYME DISCOVERY → SEQUENCE → STRUCTURE → SUBSTRATE COMPATIBILITY → TRANSFORMATION →
PRODUCTS → PRODUCT SAFETY → RESIDUAL ANTIBACTERIAL ACTIVITY → AMR CONTEXT →
UNCERTAINTY → PRIORITY SCORE → VALIDATION RECOMMENDATION.

## 2. Contaminant intelligence
Tetracycline record retrieved live from PubChem PUG-REST (CID 54675776, 2026-09-17):
formula C22H24N2O8, MW 444.4, XLogP −2, TPSA 182 Å², HBD 6, HBA 9, RB 2,
InChIKey NWXMGUDVXFXRIG-WESIUVDSSA-N. No values invented; record in `data/raw/`.
2D depiction and descriptors re-derived with RDKit. Environmental chemistry narrative
sourced from review literature (L17) — labelled.

## 3. Candidate discovery
Resources: UniProtKB REST, RCSB PDB REST/files, AlphaFold DB, CARD (concept-level),
peer-reviewed literature incl. 2025 BSFL work. Evidence classes:
E1 experimental enzyme | E2 experimental system | E3 functional-genomics/family |
E4 structural/computational | E5 hypothesis. Six candidates:
Tet(X) Q01911 (E1), TetX2 Q93L51 (E1, PDB 2Y6R), Tet(X3) Q7X2A0 (E1 family),
Laccase-2 Q12718 (E2, PDB 1GYC), MnP1 Q02567 (E2, PDB 1MNP),
BSFL gut metatranscriptome candidate family (E3; sequence- and structure-unavailable — displayed as such).

## 4. Docking (real, validated)
- Receptor: 2Y6R chain A, co-crystallised 7-chlortetracycline removed, **FAD retained**
  (catalytically required), sulfates/waters removed; Gasteiger charges, protonated pH 7.4 (Open Babel).
- Ligands: PubChem 3D SDFs → PDBQT (Open Babel).
- Engine: **smina 2019-10-15 (AutoDock Vina 1.1.2 scoring), seed 42, exhaustiveness 16**,
  box 20 Å centred on the co-crystal ligand centroid.
- Validation: re-docking 7-CTC into its own pocket → heavy-atom RMSD **1.84 Å**
  (element-aware Hungarian assignment + Kabsch, because the PDB ligand lacks CONECT
  records — method documented in `src/docking/redock_rmsd.py`). Protocol = PASS.
- Result: tetracycline top affinity −9.7 kcal/mol; contacts ≤4 Å mapped (15 residues, FAD 2.36 Å).
- Laccase (1GYC, box on T1 Cu): all modes ≈ 0 kcal/mol → **honest negative result**;
  interpreted qualitatively (laccase = outer-sphere oxidation, rigid docking not mechanistically apt).
- MnP: docking not run — mechanism is diffusible Mn³⁺; using docking there would be
  pseudo-precision. Stated in the app.
- **DOCKING ≠ PROOF OF CATALYSIS** — docked score is one weight of 13 in the engine.

## 5. Sequence intelligence
Biopython PairwiseAligner global alignments (match 1 / mismatch 0 / gap −0.5,−0.1);
identity% = score / max length. TetX↔TetX2 99.5%; Tet(X3) ≈82%; fungal enzymes ≈18–21% —
two independent evolutionary solutions to the same contaminant.
Physicochemical stats per sequence (MW, pI, GRAVY, aromaticity).
Caveat enforced: similarity ≠ function (inactive Tet(X1) precedent).

## 6. Product intelligence & safety triage
Products tracked per pathway; structures only where verified (PubChem: 4-epitetracycline
CID 54682506, anhydrotetracycline CID 54675758); the enzymatic 11a-hydroxy product is
transient → labelled STRUCTURE UNCERTAIN. Deterministic triage: Morgan-FP Tanimoto to
parent + SMARTS pharmacophore alerts (β-diketone chelator, dimethylamino, carboxamide, enol).
Teaching case included: 4-epitetracycline returns Tanimoto 1.0 (achiral fingerprint
blindness) yet retains activity — the system defers to experimental activity labels.
Residual antibacterial activity classes: retained / reduced / loss demonstrated / predicted / unknown —
sourced from Yang 2004, Mitscher 1978, Jin 2021, Suda 2012, Wen 2010.

## 7. AMR SHIELD
Mechanism catalogue: enzymatic inactivation (tet(X) family), efflux (tetA/B/L/33/A60/tet34),
RPP (tetM/W/O/Q). Per-candidate screening categories LOW/MODERATE/HIGH/UNKNOWN CONCERN with
rationale; e.g., TetX family = HIGH (the biocatalyst is itself resistance machinery →
recommend cell-free enzyme form only). Categories are computational triage, not clinical/regulatory.

## 8. Environmental layer
Nigeria-focused, point-study-strict: Lagos surface waters (L11), Lagos hospital-WWTP
sludge — TC up to 310.2 ng/g (L12), Lagos marine isolates tetA/B/M context (L20).
No national extrapolation. One-Health frame computed from these records.

## 9. Cassava circular-bioremediation layer
Evidence-bounded: cassava ethanol-sludge biochar NaHCO₃-activated adsorbs TC
(Qmax 154.45 mg/g; 92.6% removal pH 3 — L14); cassava *peel* biochar evidence demonstrated
on ciprofloxacin, NOT tetracycline (L15) — the module states this explicitly.
ADS ORPTION (mass transfer) ≠ degradation ≠ detoxification; spent-adsorbent end-of-life
modelled as first-class output; recommended architecture = Option C (pre-concentration → enzymatic transformation).

## 10. Decision engine
score = 100 × (Σ w⁺·c⁺ normalised − 0.85·Σ w⁻·r⁻ normalised + 0.30), clipped [0,100].
13 inspectable components (8 positive, 5 risk). Presets: BALANCED, SAFETY_FIRST,
AMR_CONSERVATIVE, MAX_TRANSFORMATION, LOW_COST, HIGH_CONFIDENCE + fully custom weights.
Robustness: Monte-Carlo (400 sets, ±25%) → per-candidate rank distributions + Kendall's W = **0.955**;
ablation over 6 layer-sets; baselines (literature-only, docking-only, sequence-family-only) compared.

## 11. Why ML is deliberately not fitted
n=6 evidence-graded candidates cannot support a trustworthy fitted model
(leakage/overfit near-certain). See docs/MODEL_CARD.md for the full justification and
the rejected-alternative analysis.
