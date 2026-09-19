# DATA DICTIONARY

## kb/candidates.json (per record)
- candidate_id (str, unique), protein_name, gene_name, organism, source_environment
- accession {uniprot?, pdb?, dataset?}
- sequence_fasta (path|null)
- enzyme_family, cofactors[], annotation
- evidence_level ∈ {E1,E2,E3,E4,E5}
- degradation_evidence {status, refs[]}
- resistance_association {status ∈ {HIGH CONCERN, MODERATE CONCERN, LOW CONCERN, UNKNOWN}, mechanism, databases, refs[], note?}
- structure {kind ∈ {experimental,predicted,predicted-homology,unavailable}, source?, id?, resolution_A?, mean_plddt?, file?, label, related?}
- docking | null — {software, substrate, top_affinity_kcal_mol, redock_validation?, interactions?, note/interpretation, confidence?}
- transformation {pathway_id, type, known_vs_predicted}
- refs[] (literature ids)

## kb/products.json
- product_id, name, parent, route, structure_status, smiles|null, formula(_est)?, mw(_est)?
- known_vs_predicted, occurrence?
- residual_activity {class, evidence, refs[], detail?}
- safety_triage {class, toxicity_data?, ecotoxicity?, persistence?, refs[]}

## kb/environment.json
- occurrence_records[] {location, country, matrix, contaminant, concentration, year, study, ref, evidence, lat?, lon?}
- sources_pathways[], one_health {human, animal, environment}, persistence_summary

## results/docking/docking_results.json
- software, seed, exhaustiveness, box {center[], size[]}, receptor {pdb, chain, cofactor, note}
- runs {<ligand>: {modes[] {mode, affinity_kcal_mol}, receptor?, box?, note?}}
- redock_validation {ligand, best_mode_rmsd_A, method, interpretation}
- tetracycline_interactions {contact_cutoff_A, protein_contacts[] {residue, min_dist_A, atom}, fad_contacts[], min_fad_dist_A, note}

## Score components (engine)
POSITIVE (0–1): evidence_strength, degradation_demonstration, structure_confidence,
catalytic_plausibility, substrate_compatibility, transformation_confidence,
circular_feasibility, environmental_relevance
RISK (0–1): product_safety_risk, residual_activity_risk, amr_risk,
uncertainty_penalty, structural_uncertainty … plus _flags[] (strings).
