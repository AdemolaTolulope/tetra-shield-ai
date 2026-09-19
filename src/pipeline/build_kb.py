#!/usr/bin/env python3
"""
TETRA-SHIELD AI — Knowledge base builder.
Assembles data/processed/kb/*.json from raw fetches + verified literature facts.
Every record carries provenance: source, accession, url, retrieval date, evidence class.
Evidence classes: E1 experimental enzyme | E2 experimental (microbe/system)
E3 strong sequence/functional-genomics | E4 structural/computational | E5 hypothesis
"""
import json, datetime, shutil, subprocess, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
KB = ROOT / "data" / "processed" / "kb"
STRUCT = ROOT / "data" / "processed" / "structures"
KB.mkdir(parents=True, exist_ok=True)
STRUCT.mkdir(parents=True, exist_ok=True)
TODAY = "2026-09-17"
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

def fasta_seq(p):
    seq = "".join(l.strip() for l in open(p) if not l.startswith(">"))
    return seq

# ---------------------------------------------------------------- CONTAMINANT
pc = json.load(open(RAW / "pubchem_tetracycline.json"))["PropertyTable"]["Properties"][0]
contaminant = {
 "contaminant_id": "CID54675776",
 "preferred_name": "Tetracycline",
 "title": pc["Title"],
 "class": "Tetracycline-class broad-spectrum antibiotic",
 "synonyms": ["Tetracycline", "Abricycline", "Achromycin", "Panmycin", "Tetracyclin",
              "(4S,4aS,5aS,6S,12aS)-4-(dimethylamino)-1,4,4a,5,5a,6,11,12a-octahydro-3,6,10,12,12a-pentahydroxy-6-methyl-1,11-dioxo-2-naphthacenecarboxamide"],
 "identifiers": {"pubchem_cid": 54675776, "inchikey": pc["InChIKey"],
                 "chebi": "CHEBI:27902 (tetracycline antibiotic class relation)", "cas": "60-54-8"},
 "formula": pc["MolecularFormula"],
 "molecular_weight": pc["MolecularWeight"],
 "canonical_smiles": pc["ConnectivitySMILES"],
 "isomeric_smiles": pc["SMILES"],
 "xlogp": pc["XLogP"], "hbd": pc["HBondDonorCount"], "hba": pc["HBondAcceptorCount"],
 "rotatable_bonds": pc["RotatableBondCount"], "tpsa": pc["TPSA"],
 "structural_features": [
   "Linear fused four-ring (naphthacene) scaffold",
   "C11–C12 beta-diketone + C1–C3 enolamide (Mg2+-chelating pharmacophore required for ribosome binding)",
   "C4 dimethylamino group (pH-dependent stereolabile/epimerisable centre)",
   "C6 tertiary alcohol (acid-labile; dehydration yields anhydrotetracycline)",
   "Ionisable at three pKa regions (~3.3, 7.7, 9.7): cation/zwitterion/anion speciation governs sorption & bioavailability"],
 "provenance": {"source": "PubChem PUG-REST", "accession": "CID 54675776",
                "url": "https://pubchem.ncbi.nlm.nih.gov/compound/54675776",
                "retrieved": TODAY, "license": "Public domain (US Gov)"},
 "environmental_chemistry": {
   "persistence": "Generally low–moderate aqueous persistence (photolysis, hydrolysis, epimerisation); persists when sorbed to sediments/sludge (strong sorption to clay/organic matter and multivalent cations).",
   "speciation_note": "Binds Mg2+/Ca2+ strongly — both fate (sorption) and antimicrobial mechanism depend on chelation.",
   "evidence": "literature-supported (review consensus)", "source": "reviewed in Daghrir & Drogui 2013, Environ Chem Lett 11:209"}
}
json.dump(contaminant, open(KB / "contaminant_tetracycline.json", "w"), indent=2)

# ---------------------------------------------------------------- LITERATURE BASE
lit = [
 {"id": "L01", "cite": "Yang W et al. 2004. TetX Is a Flavin-dependent Monooxygenase Conferring Resistance to Tetracycline Antibiotics. J Biol Chem 279(50):52346–52", "doi": "10.1074/jbc.M409573200", "evidence": "E1",
  "claim": "TetX/TetX2 are FAD-dependent monooxygenases requiring NADPH and O2; regiospecific C11a hydroxylation; product unstable, decomposes non-enzymatically; downstream products inactive."},
 {"id": "L02", "cite": "Volkers G et al. 2011. Structural basis for a new tetracycline resistance mechanism relying on the TetX monooxygenase. J Mol Biol 416(5):2212–25", "doi": "10.1016/j.jmb.2011.12.063", "evidence": "E1/E4",
  "claim": "Crystal structures of TetX (Bacteroides fragilis) and TetX2 (B. thetaiotaomicron) incl. tigecycline and 7-chlortetracycline complexes; FAD-binding and substrate-binding residues defined."},
 {"id": "L03", "cite": "He T et al. 2019. Emergence of plasmid-mediated high-level tigecycline resistance genes in animals and humans. Nat Microbiol 4:1450–6", "doi": "10.1038/s41564-019-0445-2", "evidence": "E1",
  "claim": "Mobile tet(X3)/tet(X4) on plasmids confer high-level tigecycline resistance; widespread dissemination; tet(X4) functionally validated."},
 {"id": "L04", "cite": "Jin L et al. 2021. Evolutionary Trajectory of the Tet(X) Family. mSystems 6(3):e00050-21", "doi": "10.1128/mSystems.00050-21", "evidence": "E2/E3",
  "claim": "Tet(X) family phylogeny; key residues H231, M372 (substrate region), E43, R114, D308 (FAD region); anhydrotetracycline inhibits Tet(X) enzymes."},
 {"id": "L05", "cite": "Markley JL, Wencewicz TA. 2018. Tetracycline-Inactivating Enzymes. Front Microbiol 9:1058", "doi": "10.3389/fmicb.2018.01058", "evidence": "review",
  "claim": "Tetracycline destructases (Tet(X) family) are environmental flavoenzymes; enzymatic inactivation is a growing resistance mechanism; products undergo non-enzymatic breakdown."},
 {"id": "L06", "cite": "Suda T et al. 2012. Treatment of tetracycline antibiotics by laccase in the presence of 1-hydroxybenzotriazole. Bioresour Technol 103(1):498–501", "doi": "10.1016/j.biortech.2011.10.041", "evidence": "E2",
  "claim": "Laccase (Trametes sp.) eliminates tetracycline antibiotics in vitro, strongly enhanced by redox mediator HBT."},
 {"id": "L07", "cite": "Wen X, Jia Y, Li J. 2010. Enzymatic degradation of tetracycline and oxytetracycline by crude manganese peroxidase prepared from Phanerochaete chrysosporium. J Hazard Mater 177(1–3):924–8", "doi": "10.1016/j.jhazmat.2010.01.005", "evidence": "E2",
  "claim": "MnP (white-rot fungus) degrades tetracycline/oxytetracycline; MnP identified TC transformation pathway (demethylation, oxidation of dimethylamino, decarbonylation, hydroxylation, oxidative dehydrogenation) and 7 possible products."},
 {"id": "L08", "cite": "Zhang Y et al. 2023. Comparative Metagenomic and Metatranscriptomic Analyses Reveal the Response of Black Soldier Fly Larvae Intestinal Microbes and Reduction Mechanisms to High Concentrations of Tetracycline. Toxics 11(7):611", "doi": "10.3390/toxics11070611", "evidence": "E3",
  "claim": "BSFL gut metatranscriptome under 1250 mg/kg TC: tet(X) family NOT detected; TC degradation rate 32.2% vs 11.5% germ-free; upregulated CAZyme families AA1 (laccase-like) and AA2 (MnP/lignin-peroxidase-like) and deacetylases proposed as degradation candidates; efflux (tet(33), tet(A), tet(B), tet(L), tetA(60)) and RPP (tetM, tetW) dominate resistance response."},
 {"id": "L09", "cite": "Pei Y et al. 2025. Novel Tetracycline-Degrading Enzymes from the Gut Microbiota of Black Soldier Fly: Discovery, Performance, Degradation Pathways, Mechanisms, and Application Potential. (Record: ResearchGate, May 2025; verify journal metadata)", "doi": "pending-verification", "evidence": "E1/E2",
  "claim": "2025 work identifying tetracycline-degrading enzyme candidates from BSFL gut microbiota; degradation pathways and application potential assessed."},
 {"id": "L10", "cite": "Bioresour Technol 2025;435:132887. Synergistic mechanism of tetracycline degradation by Serratia marcescens cooperated with black soldier fly larvae", "doi": "10.1016/j.biortech.2025.132887", "evidence": "E2",
  "claim": "tet34 and UGT2B7 identified as principal genes in S. marcescens BSFL-6/larvae synergistic tetracycline metabolism (genome + transcriptome + overexpression/RNAi)."},
 {"id": "L11", "cite": "Olarinmoye O, Bakare A, Ugwumba O, Hein A. 2016. Quantification of pharmaceutical residues in wastewater impacted surface waters and sewage sludge from Lagos, Nigeria. J Environ Chem Ecotoxicol 8(2):14–24", "doi": "10.5897/JECE2015.0355", "evidence": "E2(field)",
  "claim": "Pharmaceuticals incl. tetracycline-class detected in Lagos surface waters (up to 8.84 µg/L across compounds; chlortetracycline <0.05 µg/L) and sewage sludge."},
 {"id": "L12", "cite": "Ajibola AS, Zwiener C. 2022. Occurrence and risk assessment of antibiotic residues in sewage sludge of two Nigerian hospital wastewater treatment plants. Water Air Soil Pollut 233:405", "doi": "10.1007/s11270-022-05875-4", "evidence": "E2(field)",
  "claim": "Tetracycline up to 310.2 ng/g (Ijaiye sludge); oxytetracycline detected; 100% detection frequency in secondary sludge; risk assessment for land application."},
 {"id": "L13", "cite": "Liu C et al. 2021. Black Soldier Fly Larvae Can Effectively Degrade Oxytetracycline Bacterial Residue by Means of the Gut Bacterial Community. Frontiers/Animals (record via PMC8239407)", "doi": "10.3389/fanim.2021 (verify)", "evidence": "E2",
  "claim": "BSFL degrade oxytetracycline residue; hosts of enzymatic-modification tetracycline genes incl. Enterococcus, Ignatzschineria, Bordetella, Providencia, Proteus."},
 {"id": "L14", "cite": "Yang Q et al. 2021. Novel sodium bicarbonate activation of cassava ethanol sludge derived biochar for removing tetracycline from aqueous solution. Bioresour Technol (2021), S0960852421002881", "doi": "10.1016/j.biortech.2021.124557", "evidence": "E2",
  "claim": "Cassava ethanol-sludge biochar adsorbs tetracycline: 154.45 mg/g (NaHCO3-activated) vs 34.04 mg/g raw; max removal 92.6% at pH 3; mechanisms: electrostatic, H-bonding, pi–pi, pore-filling. ADSORPTION only."},
 {"id": "L15", "cite": "2026. Hierarchical factors governing the removal of ionizable pharmaceuticals by cassava peel–derived biochar: Bayesian modeling and DFT approaches. (ScienceDirect S259012302601563X)", "doi": "10.1016/j.jcou.2026 (verify)", "evidence": "E2",
  "claim": "Cassava PEEL biochar effectively adsorbs ciprofloxacin (ionizable pharmaceutical); circular-economy rationale stated. NOT tetracycline-specific."},
 {"id": "L16", "cite": "Hoslett J et al. 2021. The removal of tetracycline from water using biochar produced from agricultural discarded material. Sci Total Environ 751:141755", "doi": "10.1016/j.scitotenv.2020.141755", "evidence": "E2",
  "claim": "Agricultural-waste biochars remove tetracycline from water by adsorption."},
 {"id": "L17", "cite": "Daghrir R, Drogui P. 2013. Tetracycline antibiotics in the environment: a review. Environ Chem Lett 11:209–27", "doi": "10.1007/s10311-013-0404-8", "evidence": "review",
  "claim": "Environmental fate: sorption, hydrolysis, photolysis; epimerisation; complexation with cations."},
 {"id": "L18", "cite": "Mitscher LA. 1978. The Chemistry of the Tetracycline Antibiotics. Marcel Dekker, New York", "doi": "n/a (monograph)", "evidence": "review",
  "claim": "4-epitetracycline (C4 epimer) retains partial antibacterial activity and equilibrates with parent; anhydrotetracycline = acid-degradation product with altered activity/toxicity profile."},
 {"id": "L19", "cite": "Grenni P, Ancona V, Caracciolo AB. 2018. Ecological effects of antibiotics on natural ecosystems: a review. Microchem J 136:25–39", "doi": "10.1016/j.microc.2017.02.006", "evidence": "review",
  "claim": "Sub-inhibitory environmental antibiotic concentrations select for resistance and affect microbial communities — the AMR-environment link."},
 {"id": "L20", "cite": "Brieflands J Kermanshah Univ Med Sci 2025. Characterization and Antibiotic Sensitivity Profile of Two Bacteria Isolated from a Marine Environment in Lagos State, Nigeria", "doi": "10.5812/jkums-166173", "evidence": "E2(field)",
  "claim": "Lagos marine isolates resistant to tetracycline; transferable tetA/tetB/tetM reported in Nigerian aquatic E. coli/P. aeruginosa (and cited studies)."},
 {"id": "L21", "cite": "CARD — Comprehensive Antibiotic Resistance Database (accessed 2026)", "doi": "10.1093/nar/gkz935", "evidence": "database",
  "claim": "tet(X) family catalogued as tetracycline-inactivation resistance determinants; tet(34) efflux/other mechanisms documented; tetM/tetW RPP; tetA/B/L efflux."},
 {"id": "L22", "cite": "UniProtKB (accessed 2026-09-17): Q01911 (TETX_BACFG), Q93L51 (TETX_BACT4), Q7X2A0 (tetX3), Q02567 (MNP1_PHACH), Q12718 (LAC2_TRAVE)", "doi": "10.1093/nar/gkab1100", "evidence": "database",
  "claim": "Protein records: names, genes, organisms, lengths, EC numbers."},
 {"id": "L23", "cite": "RCSB PDB: 2Y6R (TetX2 + 7-chlortetracycline + FAD, 3.1 A), 4A6N (TetX + tigecycline, 2.3 A), 1MNP (MnP, 2.0 A), 1GYC (Trametes versicolor laccase, 1.9 A)", "doi": "10.2210/pdb2Y6R/pdb", "evidence": "E4",
  "claim": "Experimentally determined structures used in this prototype."},
 {"id": "L24", "cite": "AlphaFold DB: AF-Q01911-F1 (computed model of TetX, B. fragilis)", "doi": "10.1093/nar/gkab1061", "evidence": "E4(predicted)",
  "claim": "Predicted structure, mean pLDDT 95.3 — clearly labelled PREDICTED, not experimental."}
]
json.dump(lit, open(KB / "literature.json", "w"), indent=2)

# ---------------------------------------------------------------- CANDIDATES
dock = json.load(open(ROOT / "results" / "docking" / "docking_results.json"))
tet_aff = dock["runs"]["tetracycline"]["modes"][0]["affinity_kcal_mol"]
lac_aff = dock["runs"]["laccase_1GYC_tetracycline"]["modes"][0]["affinity_kcal_mol"]

def pl(path):
    v = [float(l[60:66]) for l in open(path) if l.startswith("ATOM")]
    return round(statistics.mean(v), 1)

candidates = [
 {
  "candidate_id": "TETX-BF",
  "protein_name": "TetX monooxygenase (tetracycline-inactivating enzyme)",
  "gene_name": "tetX", "organism": "Bacteroides fragilis", "source_environment": "human gut anaerobe; transposons Tn4351/Tn4400",
  "accession": {"uniprot": "Q01911", "gene_synonyms": "tetX; Tcr*"},
  "sequence_fasta": "data/raw/Q01911.fasta",
  "enzyme_family": "FAD-dependent monooxygenase (tetracycline destructase, EC 1.14.13.231); class A flavoprotein monooxygenase",
  "cofactors": ["FAD", "NADPH", "O2", "Mg2+ (assay)"],
  "annotation": "Catalyses regioselective C11a hydroxylation of tetracyclines; product unstable and decomposes non-enzymatically; downstream products lack antibacterial activity (functional loss demonstrated).",
  "evidence_level": "E1",
  "degradation_evidence": {"status": "experimentally-demonstrated", "refs": ["L01", "L02", "L05"]},
  "resistance_association": {"status": "HIGH CONCERN", "mechanism": "enzymatic inactivation (tetX is itself a tetracycline resistance gene; confers resistance incl. tigecycline in family members)",
     "databases": "CARD lists tet(X) as resistance determinant", "refs": ["L03", "L21"],
     "note": "Deploying purified enzyme avoids gene transfer; deploying the organism/gene biocatalytically carries HGT risk."},
  "structure": {"kind": "predicted", "source": "AlphaFold DB", "id": "AF-Q01911-F1", "mean_plddt": pl(RAW / "AF_Q01911.pdb"),
                "experimental_homolog": "4A6N (B. fragilis TetX + tigecycline, 2.3 A) exists; used as template context",
                "file": "structures/AF_Q01911.pdb",
                "label": "PREDICTED MODEL (AlphaFold) — not an experimentally solved structure"},
  "docking": None,
  "transformation": {"pathway_id": "P1", "type": "enzymatic hydroxylation (C11a) + non-enzymatic decomposition", "known_vs_predicted": "KNOWN (first step) / products partially characterised"},
  "refs": ["L01", "L02", "L04", "L05", "L22", "L24"]
 },
 {
  "candidate_id": "TETX2-BT",
  "protein_name": "TetX2 monooxygenase", "gene_name": "tetX2",
  "organism": "Bacteroides thetaiotaomicron", "source_environment": "human gut anaerobe",
  "accession": {"uniprot": "Q93L51", "pdb": "2Y6R"},
  "sequence_fasta": "data/raw/Q93L51.fasta",
  "enzyme_family": "FAD-dependent monooxygenase (tetracycline destructase)",
  "cofactors": ["FAD", "NADPH", "O2"],
  "annotation": "Functionally validated tetracycline-inactivating enzyme (confers resistance in aerobically grown E. coli); broad tetracycline substrate range.",
  "evidence_level": "E1",
  "degradation_evidence": {"status": "experimentally-demonstrated", "refs": ["L01", "L02"]},
  "resistance_association": {"status": "HIGH CONCERN", "mechanism": "enzymatic inactivation resistance gene (tetX2)", "databases": "CARD", "refs": ["L21", "L05"]},
  "structure": {"kind": "experimental", "source": "PDB", "id": "2Y6R", "resolution_A": 3.1,
                "cocrystal_ligand": "7-chlortetracycline", "method": "X-ray diffraction",
                "file": "structures/tetx2_2Y6R_chainA_FAD.pdb",
                "label": "EXPERIMENTAL (X-ray, 3.1 A) — moderate resolution; ligand complex present",
                "related": "4A6N TetX+tigecycline 2.3 A"},
  "docking": {"software": "smina/Vina 1.1.2", "substrate": "tetracycline",
              "top_affinity_kcal_mol": tet_aff,
              "redock_validation": dock["redock_validation"],
              "interactions": dock["tetracycline_interactions"],
              "note": "DOCKING != PROOF OF CATALYSIS. Computed with apo protein + FAD, box on co-crystal ligand site, seed 42."},
  "transformation": {"pathway_id": "P1", "type": "C11a hydroxylation + decomposition", "known_vs_predicted": "KNOWN (first step)"},
  "refs": ["L01", "L02", "L23"]
 },
 {
  "candidate_id": "TETX3-PA",
  "protein_name": "Tet(X3) monooxygenase", "gene_name": "tet(X3)",
  "organism": "Pseudomonas aeruginosa (record); disseminated on plasmids across Acinetobacter/Enterobacterales",
  "source_environment": "clinical & animal isolates; mobile genetic elements",
  "accession": {"uniprot": "Q7X2A0"},
  "sequence_fasta": "data/raw/Q7X2A0.fasta",
  "enzyme_family": "FAD-dependent monooxygenase (tetracycline destructase)",
  "cofactors": ["FAD", "NADPH", "O2"],
  "annotation": "Plasmid-borne family variant conferring high-level tigecycline resistance; enzymatically inactivates tetracyclines (validated for family; variant-level kinetics reported).",
  "evidence_level": "E1",
  "degradation_evidence": {"status": "experimentally-demonstrated (variant function shown; as biocatalyst it degrades tetracyclines)", "refs": ["L03", "L04"]},
  "resistance_association": {"status": "HIGH CONCERN", "mechanism": "mobile tigecycline resistance gene — among the most clinically alarming tetracycline-inactivation determinants",
     "databases": "CARD", "refs": ["L03", "L21"]},
  "structure": {"kind": "predicted-homology", "source": "no direct experimental structure; strong homology to TetX/TetX2 (family)",
                "file": None, "label": "STRUCTURE UNAVAILABLE in prototype build — homology context only"},
  "docking": None,
  "transformation": {"pathway_id": "P1", "type": "family-inferred C11a hydroxylation", "known_vs_predicted": "KNOWN (family) "},
  "refs": ["L03", "L04", "L22"]
 },
 {
  "candidate_id": "LAC-TV",
  "protein_name": "Laccase-2 (multicopper oxidase)", "gene_name": "LCC2",
  "organism": "Trametes versicolor (white-rot fungus)", "source_environment": "lignocellulose-degrading fungus; environmental biotechnology workhorse",
  "accession": {"uniprot": "Q12718", "pdb": "1GYC"},
  "sequence_fasta": "data/raw/Q12718.fasta",
  "enzyme_family": "Multicopper oxidase (AA1 family, CAZy)", "cofactors": ["4 Cu (T1, T2/T3 trinuclear)"],
  "annotation": "Oxidises broad phenolic/aromatic substrates via single-electron transfer at T1 Cu; eliminates tetracyclines in vitro, substantially enhanced by mediators (e.g. HBT).",
  "evidence_level": "E2",
  "degradation_evidence": {"status": "experimentally-demonstrated (in-vitro enzymatic elimination; mediator-enhanced)", "refs": ["L06"]},
  "resistance_association": {"status": "LOW CONCERN", "mechanism": "no ARG association detected in analysed reference databases (fungal ligninolytic enzyme, no mobility elements)", "databases": "CARD/NCBI AMRFinder: no hit", "refs": ["L21"]},
  "structure": {"kind": "experimental", "source": "PDB", "id": "1GYC", "resolution_A": 1.9, "method": "X-ray",
                "file": "structures/laccase_1GYC_chainA.pdb", "label": "EXPERIMENTAL (X-ray, 1.9 A)"},
  "docking": {"software": "smina/Vina 1.1.2", "substrate": "tetracycline (box on T1 Cu)",
              "top_affinity_kcal_mol": lac_aff,
              "interpretation": "No productive pose found at T1 copper channel under rigid docking (~0 kcal/mol across modes). Honest negative: rigid docking at this cavity does not capture laccase outer-sphere oxidation/mediator-assisted conversion. Docking absence of pose is NOT proof of non-catalysis; E2 evidence stands.",
              "confidence": "LOW (qualitative only)"},
  "transformation": {"pathway_id": "P2", "type": "oxidative (single-electron; mediator-assisted)", "known_vs_predicted": "KNOWN removal; products partially characterised"},
  "refs": ["L06", "L22", "L23"]
 },
 {
  "candidate_id": "MNP-PC",
  "protein_name": "Manganese peroxidase 1", "gene_name": "MNP1",
  "organism": "Phanerochaete (Phanerodontia) chrysosporium (white-rot fungus)", "source_environment": "lignocellulose-degrading fungus",
  "accession": {"uniprot": "Q02567", "pdb": "1MNP"},
  "sequence_fasta": "data/raw/Q02567.fasta",
  "enzyme_family": "Class II heme peroxidase (AA2 family, CAZy)", "cofactors": ["heme", "Mn2+", "H2O2"],
  "annotation": "Oxidises Mn2+ to diffusible Mn3+, which oxidises organics remotely; crude MnP degrades tetracycline & oxytetracycline; pathway products reported (demethylation, dimethylamino oxidation, decarbonylation, hydroxylation, oxidative dehydrogenation).",
  "evidence_level": "E2",
  "degradation_evidence": {"status": "experimentally-demonstrated (crude MnP; proccess/product analysis)", "refs": ["L07"]},
  "resistance_association": {"status": "LOW CONCERN", "mechanism": "no ARG association detected in analysed databases", "databases": "CARD/NCBI AMRFinder: no hit", "refs": ["L21"]},
  "structure": {"kind": "experimental", "source": "PDB", "id": "1MNP", "resolution_A": 2.0, "method": "X-ray",
                "file": "structures/mnp_1MNP_chainA.pdb", "label": "EXPERIMENTAL (X-ray, 2.0 A)"},
  "docking": {"note": "Docking not mechanistically appropriate: oxidation is mediated by diffusible Mn3+ generated at a small Mn-binding site, not by substrate binding in a pocket. Substrate compatibility assessed from E2 literature instead.",
              "top_affinity_kcal_mol": None},
  "transformation": {"pathway_id": "P3", "type": "Mn3+-mediated oxidation cascade", "known_vs_predicted": "KNOWN (multi-product pathway reported)"},
  "refs": ["L07", "L22", "L23"]
 },
 {
  "candidate_id": "BSFL-AA12",
  "protein_name": "BSFL gut metatranscriptome candidate family (laccase-like AA1 / peroxidase AA2 / deacetylase)",
  "gene_name": "unresolved (metatranscriptomic ORFs)", "organism": "Hermetia illucens gut microbiome",
  "source_environment": "black soldier fly larval gut under 1250 mg/kg tetracycline",
  "accession": {"dataset": "Toxics 2023;11:611 (metatranscriptomic annotations; CARD/eggNOG/CAZy based)"},
  "sequence_fasta": None,
  "enzyme_family": "AA1/AA2 auxiliary-activity enzymes + deacetylases (family-level only)",
  "cofactors": ["family-dependent"],
  "annotation": "Family-level candidates upregulated under TC pressure; tet(X) NOT detected in BSFL gut; gut flora increases TC degradation rate ~3x (32.2% vs 11.5% germ-free). No individual protein sequence/activity validated yet.",
  "evidence_level": "E3",
  "degradation_evidence": {"status": "strong functional-genomics evidence (community level); individual enzymes UNVALIDATED", "refs": ["L08", "L09", "L10"]},
  "resistance_association": {"status": "MODERATE CONCERN", "mechanism": "gut community simultaneously enriches efflux (tet(33), tetA, tetB, tetL, tetA(60)) and RPP (tetM, tetW) genes; selection-pressure context; the candidate ORFs themselves are not resistance genes", "databases": "CARD (community profile)", "refs": ["L08", "L10"]},
  "structure": {"kind": "unavailable", "label": "STRUCTURE UNAVAILABLE — no resolved ORF sequence in this prototype build"},
  "docking": None,
  "transformation": {"pathway_id": "P4", "type": "multi-route (proposed: oxidation, demethylation, deacetylation)", "known_vs_predicted": "PREDICTED family-level routes"},
  "refs": ["L08", "L09", "L10", "L13"]
 }
]
json.dump(candidates, open(KB / "candidates.json", "w"), indent=2)

# ---------------------------------------------------------------- PRODUCTS
products = [
 {"product_id": "TP-11OH", "name": "11a-hydroxytetracycline (enzymatic primary product; transient)",
  "parent": "tetracycline", "route": "TetX-family C11a hydroxylation (FAD/NADPH/O2)",
  "structure_status": "STRUCTURE UNCERTAIN — transient hemiketal; decomposes non-enzymatically to poorly characterized downstream products (L01, L05)",
  "smiles": None, "formula_est": "C22H24N2O9 (+O vs parent)", "mw_est": 460.4,
  "known_vs_predicted": "KNOWN reaction / characterisation incomplete",
  "residual_activity": {"class": "activity loss demonstrated (downstream products; functional resistance literature)", "evidence": "literature-supported", "refs": ["L01", "L05"],
     "detail": "Hydroxylation disrupts C11-C12 beta-diketone Mg-chelating pharmacophore required for ribosome binding; downstream products inactive (Yang 2004)."},
  "safety_triage": {"toxicity_data": "no dedicated tox dataset located", "ecotoxicity": "unknown", "persistence": "expected LOW (chemically unstable)",
     "class": "LOW-EVIDENCE — absence of tox data != safe; flagged for follow-up LC-MS product work", "refs": ["L01"]}
 },
 {"product_id": "TP-EPI", "name": "4-epitetracycline",
  "parent": "tetracycline", "route": "abiotic C4 epimerisation (equilibrium, weakly acidic pH) — environmental transformation product",
  "structure_status": "KNOWN (PubChem CID 54682506)",
  "smiles": json.load(open(RAW / "pubchem_4-epitetracycline.json"))["PropertyTable"]["Properties"][0]["SMILES"],
  "formula": "C22H24N2O8", "mw": 444.4,
  "known_vs_predicted": "KNOWN",
  "occurrence": "detected with parent in waters/manure matrices (epimer equilibrium)",
  "residual_activity": {"class": "RETAINED (reduced) — C4 epimer keeps full ring-chelation scaffold; equilibrates back to parent", "evidence": "literature-supported", "refs": ["L18"]},
  "safety_triage": {"class": "CONCERN for continued selective pressure: retains antibacterial activity hence drives AMR selection even after 'removal' of parent", "toxicity_data": "limited", "refs": ["L18", "L19"]}
 },
 {"product_id": "TP-ANHYDRO", "name": "Anhydrotetracycline",
  "parent": "tetracycline", "route": "acid-catalysed C6 dehydration (abiotic; sediments/acidic microsites)",
  "structure_status": "KNOWN (PubChem CID 54675758)",
  "smiles": json.load(open(RAW / "pubchem_anhydrotetracycline.json"))["PropertyTable"]["Properties"][0]["SMILES"],
  "formula": "C22H22N2O7", "mw": 426.4,
  "known_vs_predicted": "KNOWN",
  "residual_activity": {"class": "RETAINED but altered (weak antibacterial; acts as competitive inhibitor of Tet(X)-family destructases)", "evidence": "literature-supported", "refs": ["L04", "L18"]},
  "safety_triage": {"class": "MODERATE CONCERN — retains chelating chromophore; cytotoxicity reports in pharmacology literature; can suppress enzymatic detox (TetX inhibitor)", "refs": ["L04", "L18"]}
 },
 {"product_id": "TP-OX", "name": "Oxidation product group (laccase/MnP route)",
  "parent": "tetracycline", "route": "oxidative (laccase + mediator; MnP/Mn3+): demethylation, dimethylamino oxidation, decarbonylation, hydroxylation, oxidative dehydrogenation",
  "structure_status": "PARTIALLY CHARACTERISED — 7 possible products reported for MnP route (L07); laccase products partially described (L06)",
  "smiles": None,
  "known_vs_predicted": "KNOWN routes / individual structures partially resolved",
  "residual_activity": {"class": "reported antimicrobial-activity reduction for treatment effluents (assay-dependent)", "evidence": "literature-supported (limited)", "refs": ["L06", "L07"]},
  "safety_triage": {"class": "INSUFFICIENT EVIDENCE — product-specific tox data sparse; mandatory LC-MS + bioassay follow-up", "refs": ["L06", "L07"]}
 }
]
json.dump(products, open(KB / "products.json", "w"), indent=2)

# ---------------------------------------------------------------- ENVIRONMENT
environment = {
 "occurrence_records": [
  {"location": "Lagos (multiple sites incl. Amuwo-Odofin)", "country": "Nigeria", "matrix": "surface water (wastewater-impacted)",
   "contaminant": "tetracycline-class (chlortetracycline <0.05 ug/L; 12/37 pharmaceuticals detected, up to 8.84 ug/L for other compounds)",
   "concentration": "<0.05 ug/L (chlortetracycline); class-level signal", "year": 2016, "study": "Olarinmoye et al. 2016", "ref": "L11",
   "evidence": "E2(field)", "lat": 6.4654, "lon": 3.4064},
  {"location": "Ijaiye + second hospital WWTP, Lagos", "country": "Nigeria", "matrix": "sewage sludge",
   "contaminant": "tetracycline", "concentration": "up to 310.2 ng/g", "year": 2022,
   "study": "Ajibola & Zwiener 2022", "ref": "L12", "evidence": "E2(field)", "lat": 6.6164, "lon": 3.3460,
   "note": "100% detection frequency in secondary sludge; risk quotient assessed for land application"},
  {"location": "Lagos marine environment", "country": "Nigeria", "matrix": "marine water (microbiology)",
   "contaminant": "tetracycline resistance phenotype + tetA/tetB/tetM context", "concentration": "n/a (qualitative isolate study)",
   "year": 2025, "study": "Brieflands JKUMS 2025", "ref": "L20", "evidence": "E2(field)", "lat": 6.4310, "lon": 3.4200},
  {"location": "Kenya/Uganda surface waters (regional context)", "country": "East Africa (reference)", "matrix": "surface water",
   "contaminant": "tetracyclines", "concentration": "ng/L–ug/L ranges reported across African monitoring studies",
   "year": 2016, "study": "comparative datasets compiled in Olarinmoye 2016 discussion", "ref": "L11", "evidence": "review-sourced", "lat": None, "lon": None}
 ],
 "sources_pathways": ["hospital effluent", "municipal wastewater (limited treatment)", "pharmaceutical manufacturing discharge",
   "aquaculture & livestock runoff (veterinary TC/OTC use)", "sludge land application"],
 "one_health": {
   "human": "clinical use + hospital effluent; carbapenem-era pressure to preserve last-resort tetracyclines (tigecycline)",
   "animal": "veterinary tetracyclines among most-used livestock antibiotics; aquaculture use in Nigeria reported",
   "environment": "sub-inhibitory ng–ug/L levels maintain selection pressure; sludge application recycles residues to soils (L12, L19)"
 },
 "persistence_summary": contaminant["environmental_chemistry"]["persistence"]
}
json.dump(environment, open(KB / "environment.json", "w"), indent=2)

# ---------------------------------------------------------------- AMR SHIELD
amr = {
 "tetracycline_resistance_mechanisms": [
   {"class": "enzymatic inactivation", "genes": ["tet(X) family: tetX, tetX2, tet(X3), tet(X4), tet(X5)... tet(X14)"],
    "note": "FAD monooxygenases; environmental origin; mobilised variants (X3/X4) confer high-level tigecycline resistance (L03, L05)", "concern": "HIGH"},
   {"class": "efflux pumps", "genes": ["tet(A)", "tet(B)", "tet(L)", "tet(33)", "tetA(60)", "tet34 (efflux/other; implicated in BSFL-6 synergy, L10)"], "concern": "HIGH (mobile, common in wastewater)"},
   {"class": "ribosomal protection proteins", "genes": ["tet(M)", "tet(W)", "tet(O)", "tet(Q)"], "concern": "HIGH (very widespread)"}],
 "selection_context": "Sub-MIC antibiotic residues select resistant populations; aquatic systems act as resistance reservoirs and HGT arenas (L19). BSFL gut: degradation co-occurs with enrichment of tet efflux/RPP genes (L08, L10).",
 "database_note": "Screening categories (LOW/MODERATE/HIGH CONCERN) are computational triage — NOT clinical or regulatory determinations. 'No detected association' != 'AMR-free'."
}
json.dump(amr, open(KB / "amr.json", "w"), indent=2)

# ---------------------------------------------------------------- CASSAVA
cassava = {
 "role": "PRETREATMENT / ADSORPTION LAYER + support material — explicitly NOT degradation",
 "nigeria_context": "Nigeria is the world's largest cassava producer (~60 Mt/yr; FAO); peels and ethanol-processing sludge are abundant low-value waste streams.",
 "evidence": [
   {"material": "cassava ethanol-sludge biochar (NaHCO3-activated)",
    "contaminant": "tetracycline (DIRECT evidence)", "function": "ADSORPTION (mass transfer water->solid)",
    "performance": "Qmax 154.45 mg/g (activated) vs 34.04 mg/g (raw); ~92.6% removal at pH 3 in batch",
    "mechanisms": ["electrostatic attraction", "hydrogen bonding", "pi-pi interactions", "pore filling"],
    "ref": "L14", "evidence": "E2 (batch-scale, synthetic solution)"},
   {"material": "cassava peel-derived biochar (CP500/CP700)",
    "contaminant": "ciprofloxacin (NOT tetracycline)", "function": "ADSORPTION",
    "performance": "effective across pH 3–10 in lab conditions", "ref": "L15",
    "note": "Included to demonstrate the adsorbent principle for the PEEL stream; must not be represented as tetracycline degradation evidence."},
   {"material": "agricultural-waste biochars (general)", "contaminant": "tetracycline", "function": "ADSORPTION", "ref": "L16"}],
 "critical_distinctions": {
   "adsorption": "transfers/concentrates contaminant from water to solid; molecule NOT destroyed",
   "degradation": "chemical transformation of the molecule (enzymatic/abiotic)",
   "detoxification": "demonstrated loss of biological hazard (requires product + bioactivity evidence)"},
 "spent_adsorbent": {"issue": "TC-laden biochar is now hazardous solid waste / potential secondary source",
   "options": ["thermal regeneration/incineration (energy cost; destroys sorbent)",
               "coupling to enzymatic/microbial degradation of desorbed concentrate (TETRA-SHIELD architecture Option C)",
               "stabilisation in construction materials (mobilisation risk must be assessed)"],
   "design_principle": "Never claim 'treatment' for adsorption alone; the solid phase must have a managed end-of-life."},
 "circularity_score_inputs": {"feedstock_cost_class": "low (waste stream)", "activation_cost_class": "moderate (chemical activation) / low (pyrolysis only)",
   "local_availability": "high (Nigeria)", "evidence_class_for_TC": "adsorption-only (E2 batch)"}
}
json.dump(cassava, open(KB / "cassava.json", "w"), indent=2)

# ---------------------------------------------------------------- TRANSFORMATION PATHWAYS
pathways = [
 {"pathway_id": "P1", "name": "TetX-family C11a hydroxylation + non-enzymatic decomposition",
  "steps": [
    {"step": 1, "reaction": "tetracycline + O2 + NADPH -> 11a-hydroxytetracycline (hemiketal)", "enzyme": "TetX/TetX2/Tet(X3)",
     "cofactor": "FAD", "type": "monooxygenation", "known": True, "ref": "L01"},
    {"step": 2, "reaction": "11a-OH-tetracycline -> non-enzymatic decomposition products (multiple, incompletely characterised)",
     "enzyme": None, "type": "spontaneous", "known": "partially", "ref": "L01,L05"}],
  "product_ids": ["TP-11OH"], "residual_activity_summary": "downstream products: antibacterial activity lost (functional evidence)"},
 {"pathway_id": "P2", "name": "Laccase oxidative elimination (mediator-assisted)",
  "steps": [{"step": 1, "reaction": "tetracycline -> oxidised product group (radical-mediated)", "enzyme": "laccase-2", "cofactor": "Cu/O2 (+HBT mediator)", "type": "single-electron oxidation", "known": True, "ref": "L06"}],
  "product_ids": ["TP-OX"], "residual_activity_summary": "reported activity reduction; product-level data limited"},
 {"pathway_id": "P3", "name": "MnP / Mn3+ oxidative cascade",
  "steps": [
    {"step": 1, "reaction": "Mn2+ -> Mn3+ (heme peroxidase, H2O2)", "enzyme": "MnP1", "type": "peroxidation", "known": True, "ref": "L07"},
    {"step": 2, "reaction": "tetracycline -> demethylation; dimethylamino oxidation; decarbonylation; hydroxylation; oxidative dehydrogenation (7 products reported)", "enzyme": "Mn3+ (diffusible)", "type": "oxidation cascade", "known": True, "ref": "L07"}],
  "product_ids": ["TP-OX"], "residual_activity_summary": "reported antimicrobial reduction (assay-dependent)"},
 {"pathway_id": "P4", "name": "Abiotic transformation matrix (context for ANY 'removal' claim)",
  "steps": [
    {"step": 1, "reaction": "tetracycline <-> 4-epitetracycline", "type": "epimerisation (equilibrium)", "known": True, "ref": "L18"},
    {"step": 2, "reaction": "tetracycline -> anhydrotetracycline (acidic)", "type": "dehydration", "known": True, "ref": "L18"},
    {"step": 3, "reaction": "tetracycline -> photolysis/hydrolysis products", "type": "photochemical", "known": "partially", "ref": "L17"}],
  "product_ids": ["TP-EPI", "TP-ANHYDRO"],
  "residual_activity_summary": "KEY LESSON: 'disappearance' of parent via abiotic routes can yield ACTIVE (epimer) or CONCERNING (anhydro) products — removal != detoxification"}
]
json.dump(pathways, open(KB / "pathways.json", "w"), indent=2)

print("KB built:", [p.name for p in KB.glob('*.json')])
