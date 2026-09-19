# NSBS COMPETITION PACKAGE — TETRA-SHIELD AI (all claims match the actual prototype)

## INNOVATION TITLE (≤15 words)
TETRA-SHIELD: Explainable decision engine for safe, AMR-aware enzymatic bioremediation of antibiotic pollution.

## ELEVATOR PITCH (≤35 words)
Antibiotics "removed" from water are not necessarily detoxified. TETRA-SHIELD computes — with real docking,
sequences and literature — whether an enzyme truly transforms tetracycline, what products result,
and which candidate to validate first.

## PROBLEM STATEMENT (150–200 words)
Nigeria's waterways receive antibiotics from hospitals, municipalities, aquaculture and
livestock. Tetracycline has been measured at up to 310 ng/g in Lagos hospital-WWTP sludge,
and resistance genes (tetA/B/M) circulate in Nigerian aquatic isolates. Standard monitoring
treats disappearance of the parent molecule as success — yet tetracycline epimerises into the
still-active 4-epitetracycline and dehydrates into anhydrotetracycline, while sub-MIC residues
keep selecting resistance. Biodegradation research, meanwhile, often stops at "percentage
removed," rarely asking what the transformation products do or whether the enzyme itself is
a resistance gene. Practitioners in low-resource settings lack a way to compare candidate
biocatalysts on *safety-adjusted* evidence before spending scarce laboratory funds.
TETRA-SHIELD addresses this gap: an offline-capable, explainable decision engine that links
contaminant identity, enzyme/structural/substrate evidence, transformation products,
residual antibacterial activity, AMR associations, uncertainty and locally feasible
cassava-waste pretreatment into one auditable prioritisation score — explicitly separating
removal, degradation and detoxification.

## TARGET BENEFICIARIES (100 words)
Environmental biotech and water-treatment researchers who must choose which enzymes to assay;
public-health and AMR teams (a One-Health view of residue-driven selection); Nigerian and
African wastewater operators and SMEs needing low-cost, locally sourced treatment options
(cassava agro-waste pre-concentration); regulators and NGOs who need evidence-graded rather
than anecdotal remediation claims; and academic labs seeking reproducible computational
triage. Ultimately, communities whose drinking-water sources sit downstream of hospital,
municipal and agro-industrial effluent benefit from remediation that is verified safe, not
just analytically invisible.

## BIOCHEMICAL MECHANISM (250–350 words)
TETRA-SHIELD's reference route is enzymatic inactivation by Tet(X)-family FAD-dependent
monooxygenases. The enzyme first reduces FAD with NADPH; the FADH2 reacts with O2 to form a
C4a-hydroperoxide, which regioselectively hydroxylates tetracycline at C11a. This addition
converts the C11a–C12 enol to a hemiketal, destroying the β-diketone Mg²⁺-chelation
pharmacophore required for ribosome binding; the product is unstable and decomposes
non-enzymatically to antibacterially inactive downstream products (Yang 2004; Volkers 2011).
The prototype verifies structural feasibility by docking tetracycline into the co-crystal
site of TetX2 (PDB 2Y6R, FAD retained): top affinity −9.7 kcal/mol with the protocol
validated by re-docking the crystallographic ligand (RMSD 1.84 Å); contacts include the
substrate-pocket His region and FAD-binding Arg/Asp region. Two fungal alternatives are
evaluated on their own mechanisms: laccase-2 (PDB 1GYC), a multicopper oxidase that
single-electron-oxidises phenolic substrates at the T1 copper (mediator-enhanced
tetracycline elimination, Suda 2012 — rigid docking gave no pose, recorded honestly), and
manganese peroxidase 1 (PDB 1MNP), which generates diffusible Mn³⁺ that oxidises
tetracycline through demethylation, dimethylamino oxidation, decarbonylation, hydroxylation
and oxidative dehydrogenation (Wen 2010). Safety is mechanism-aware: the engine tracks the
epimerisation equilibrium (active product) and acid dehydration to anhydrotetracycline
(altered activity, TetX inhibitor), and flags that resistant degraders must be deployed as
purified enzymes, never as genes or live organisms. Cassava-derived biochar is modelled only
as an adsorptive pre-concentration layer with explicit spent-material fate.

## MATERIALS / REAGENTS / DATASETS (≤150 words)
Computational prototype — no wet reagents consumed. Data: PubChem (CIDs 54675776, 54682506,
54675758); UniProtKB (Q01911, Q93L51, Q7X2A0, Q02567, Q12718); RCSB PDB (2Y6R, 4A6N, 1GYC,
1MNP); AlphaFold DB (AF-Q01911-F1); CARD (concept level); peer-reviewed literature incl.
Lagos field studies and 2025 BSF-gut work. Software: Python 3.13, FastAPI, smina/AutoDock
Vina 1.1.2, Open Babel, RDKit, Biopython, scipy, reportlab, 3Dmol.js. Future wet phase:
purified TetX/laccase, NADPH/FAD, tetracycline standards, LC-MS/MS, bioassay strains.

## SCALABILITY / COMMERCIAL / INDUSTRIAL VIABILITY (≤200 words)
The software is zero-marginal-cost and runs offline on commodity hardware — appropriate for
low-connectivity deployments. The treatment concept it prioritises is equally frugal: a
cassava-waste biochar pre-concentrator (feedstock is a free waste stream in the world's
largest cassava-producing country; lab literature shows up to 92.6% TC removal at pH 3 and
Qmax 154 mg/g for activated sludge-derived material) followed by a cell-free enzyme module,
avoiding GMO release and gene-transfer risk. Scale path: (1) computational triage (this
prototype) → (2) lab validation (enzyme assays, LC-MS/MS product ID, bioactivity and tox
assays) → (3) pilot cartridges at hospital/farm effluent points → (4) integration with
municipal polishing stages. Revenue models: licensing the decision engine to water-tech and
consulting firms; spin-off enzyme-cartridge product with local biochar manufacturing; grant
and climate/circular-economy funding. Costs are deliberately not quoted — they require the
wet-lab phase the roadmap defines. The architecture generalises to other contaminant classes
only where evidence modules exist, keeping every commercial claim evidence-scoped.

## NOVELTY / COMPETITIVE EDGE (≤150 words)
Existing tools answer single questions: BLAST finds similar enzymes; docking scores binding;
CARD flags resistance; occurrence maps show contamination. TETRA-SHIELD is, to our knowledge,
the first integrated, explainable engine that *jointly* evaluates (i) biological transformation
plausibility with validated real docking, (ii) transformation-product safety and residual
antibacterial activity, (iii) AMR implications of the biocatalyst itself, (iv) uncertainty,
and (v) locally feasible cassava-waste pretreatment — and makes the trade-offs adjustable and
provably stable (Kendall's W = 0.955). Its core doctrine — removal ≠ degradation ≠
detoxification — is enforced in the data model. Deliberate honesty (negative laccase docking
reported; unvalidated candidates scored low; no ML fitted on n=6) differentiates it from
dashboard-style "AI" claims. Novelty statement is integration-level and method-level, and we
do not claim field-wide uniqueness absent a full patent search.

## STRUCTURED ABSTRACT (250–300 words)
**Background.** Antibiotic residues in African waters sustain resistance selection, and
"removal" metrics can mask active transformation products. Decision tools that integrate
biodegradation, product safety and AMR for low-resource deployment are lacking.
**Methods.** We built TETRA-SHIELD, an offline-capable decision engine. Tetracycline identity
and descriptors were fetched from PubChem; six biocatalyst candidates (TetX, TetX2, Tet(X3),
laccase-2, MnP1, and a 2023–2025 black-soldier-fly gut metatranscriptome family) were curated
from UniProtKB, PDB, AlphaFold DB and literature with five-level evidence grading and full
provenance. Docking (smina/Vina) against TetX2 with FAD retained was validated by re-docking
(RMSD 1.84 Å); sequences were compared by global alignment; products were triaged with RDKit
similarity and pharmacophore alerts; AMR was screened per candidate. A 13-component
evidence-integrated priority score was stress-tested by 400-iteration Monte-Carlo sensitivity,
ablation and baseline comparisons. Nigerian occurrence (Lagos water, 310 ng/g sludge) and
cassava-biochar adsorption evidence (Qmax 154 mg/g) anchor local relevance.
**Results.** TetX2 leads balanced prioritisation (89.2/100) but ranks below laccase under an
AMR-conservative stance because TetX enzymes are themselves resistance determinants; rankings
are stable (W=0.955). The safety layer surfaced the activity-retaining epimer as the key
"removal ≠ detoxification" case; laccase docking was a genuine negative result and is
reported as such.
**Conclusions.** Safety-aware, AMR-aware, uncertainty-honest computational triage is feasible
and demonstrable end-to-end with public data, and yields concrete, falsifiable lab-validation
recommendations for environmental bioremediation in Nigeria.
