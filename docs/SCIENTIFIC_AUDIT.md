# SCIENTIFIC AUDIT — claim-by-claim traceability

| # | Claim made by the system | Basis | Evidence class | Where verified |
|---|---|---|---|---|
| 1 | Tetracycline formula/MW/logP/TPSA/etc. | PubChem CID 54675776 (live fetch) | authoritative DB | `data/raw/pubchem_tetracycline.json` |
| 2 | TetX family = FAD monooxygenases, C11a hydroxylation, products decompose & lose activity | Yang 2004 JBC; Volkers 2011 JMB | E1 | L01, L02 |
| 3 | tet(X3)/tet(X4) = mobile high-level tigecycline resistance | He 2019 Nat Microbiol | E1 | L03 |
| 4 | Laccase eliminates tetracyclines (mediator-enhanced) | Suda 2012 Bioresour Technol | E2 | L06 |
| 5 | MnP degrades TC/OTC; multi-route products | Wen 2010 J Hazard Mater | E2 | L07 |
| 6 | BSFL gut: tet(X) absent; AA1/AA2/deacetylases proposed; 32.2% vs 11.5% degradation | Zhang 2023 Toxics 11(7):611 | E3 | L08 |
| 7 | 2025 BSFL enzyme discovery + tet34/UGT2B7 synergy | Pei 2025; Bioresour Technol 435:132887 | E1/E2 | L09, L10 |
| 8 | Lagos surface water pharma residues (incl. tetracycline class) | Olarinmoye 2016 JECE | E2(field) | L11 |
| 9 | Lagos hospital sludge TC ≤310.2 ng/g | Ajibola & Zwiener 2022 WASP 233:405 | E2(field) | L12 |
| 10 | Lagos marine tetA/B/M context | JKUMS 2025 | E2(field) | L20 |
| 11 | Cassava sludge biochar adsorbs TC (154.45 mg/g, pH 3 optimum) | Bioresour Technol 2021 | E2(batch) | L14 |
| 12 | Cassava PEEL biochar: demonstrated on ciprofloxacin, NOT TC | S259012302601563X study | E2(batch) | L15 |
| 13 | Anhydrotetracycline inhibits Tet(X) | Jin 2021 mSystems (reviewed) | E1(reviewed) | L04 |
| 14 | 4-epimer retains (partial) activity; acid→anhydro | Mitscher 1978 | review | L18 |
| 15 | Docking affinity −9.7 kcal/mol; redock RMSD 1.84 Å | computed (smina; validation script) | E4(computed) | `results/docking/` |
| 16 | Laccase docking ≈0 kcal/mol (negative) | computed | E4(computed) | `results/docking/` |
| 17 | Sequence identities (99.5% TetX–TetX2…) | computed (Biopython) | E4(computed) | `results/sequence_analysis.json` |
| 18 | Epimer Tanimoto 1.0; anhydro 0.534 | computed (RDKit) | E4(computed) | `results/product_cheminformatics.json` |
| 19 | Priority score & stability W=0.955 | computed (engine) | this work | `results/decision_engine_validation.json` |

## Statements the system deliberately does NOT make
- No "AMR-free" claims; no "safe" claims for products; no degradation claim for cassava
  adsorption; no national extrapolation from Lagos studies; no experimental-structure
  label for the AlphaFold model (AF-Q01911 shown as PREDICTED, mean pLDDT 95.3);
  no docking output for MnP (mechanistically inappropriate); no fabricated structures
  for the transient 11a-hydroxy product.

## Residual audit risks
- L09 (Pei 2025) journal metadata not fully resolved at build time → recorded with
  "verify" flag; the claim used in-app is conservative (enzyme candidates identified).
- L11 exact chlortetracycline bound taken from published abstract-level values.
- CARD entries used at concept level (no bulk download in offline mode).
