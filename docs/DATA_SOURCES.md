# DATA SOURCES (summary — full table in data_manifest.csv)

| Source | Used for | Access |
|---|---|---|
| PubChem (CID 54675776, 54682506, 54675758) | contaminant + product identity, properties, 3D SDF | live PUG-REST at build; cached |
| UniProtKB (Q01911, Q93L51, Q7X2A0, Q02567, Q12718) | candidate identity, sequence | live REST at build; cached |
| RCSB PDB (2Y6R, 4A6N, 1MNP, 1GYC) | experimental structures + co-crystal ligand reference | live files at build; cached |
| AlphaFold DB (AF-Q01911-F1) | predicted structure, pLDDT (labelled PREDICTED) | live at build; cached |
| CARD (concept level) | AMR mechanism context | via literature |
| Peer-reviewed literature L01–L24 | degradation evidence, pathways, products, occurrence, AMR, cassava | citations+DOIs in kb/literature.json |
| smina/Vina, Open Babel, RDKit, Biopython, scipy, reportlab | computation | open tools; binaries/versions pinned |

Not used: DrugBank (license), BRENDA/KEGG bulk (license/access at build time) —
recorded as future integrations with access-compliant paths.
