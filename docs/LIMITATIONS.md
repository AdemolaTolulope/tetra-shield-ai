# LIMITATIONS — read before citing results

1. **Scope**: one contaminant (tetracycline), six candidates. This is a first module of a
   platform architecture, not coverage of antibiotics generally.
2. **Priority Score is not truth**: a prioritisation heuristic tuned to literature; component
   constants are expert-set; weights are user-adjustable precisely because no unique
   objective weighting exists.
3. **Docking limits**: rigid receptor (no protein flexibility, no explicit water network,
   no induced fit). Validated by re-docking (RMSD 1.84 Å) but affinities remain
   *qualitative*; catalysis requires proximity of the bound substrate C11a to the FAD
   hydroperoxide, which docking alone cannot establish.
4. **Laccase/MnP**: rigid docking is mechanistically inappropriate (outer-sphere / diffusible
   oxidant). Their substrate compatibility rests on E2 literature, and the recorded
   all-zero laccase docking gives *no information* against catalysis.
5. **Transformation products**: the enzymatic 11a-hydroxy product is transient and
   partially characterised in the literature; we label it STRUCTURE UNCERTAIN. Predicted
   products are never drawn as structures.
6. **Product toxicity**: field-wide data sparsity. We never equate "no tox hit" with "safe";
   TP records carry LOW-EVIDENCE / UNKNOWN classes. EPA CompTox/Tox21 batch integration is
   marked future work (offline mode cannot guarantee availability).
7. **Nigeria data**: three point studies (Lagos 2016, Lagos/WWTP sludge 2022, Lagos marine
   2025). They do not characterise Nigeria nationally; the map is schematic.
8. **Cassava layer**: direct tetracycline evidence exists for cassava *ethanol sludge*
   biochar; cassava *peel* biochar evidence is demonstrated for ciprofloxacin, not
   tetracycline — we say so in the UI and count only the sludge record as TC-relevant.
   Adsorption ≠ destruction; spent-adsorbent plans are conceptual.
9. **BSFL candidate (E3)**: family-level, ORF-unvalidated. Its low score is a function of
   honest uncertainty flags, not a judgement against the biology.
10. **Sequence identity matrix** order-dependence: identities rounded; alignments are global
    and simplistic (no trimming of fungal signal peptides) — directionally correct,
    publication-grade phylogenetics deliberately out of scope.
11. **Report PDF** is an evidence summary, not a regulatory dossier.
12. **No clinical inference anywhere** — AMR categories are research triage.
