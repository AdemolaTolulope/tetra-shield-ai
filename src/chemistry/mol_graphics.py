#!/usr/bin/env python3
"""Chem intelligence: RDKit descriptors + 2D SVGs + pharmacophore alerts for products."""
import json
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem, Draw, Descriptors, Crippen, rdMolDescriptors

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "mol"
OUT.mkdir(parents=True, exist_ok=True)

COMPOUNDS = {
    "tetracycline": {"smiles": json.load(open(ROOT / "data" / "raw" / "pubchem_tetracycline.json"))["PropertyTable"]["Properties"][0]["SMILES"], "label": "Tetracycline (parent)"},
    "4-epitetracycline": {"smiles": json.load(open(ROOT / "data" / "raw" / "pubchem_4-epitetracycline.json"))["PropertyTable"]["Properties"][0]["SMILES"], "label": "4-Epitetracycline (abiotic product)"},
    "anhydrotetracycline": {"smiles": json.load(open(ROOT / "data" / "raw" / "pubchem_anhydrotetracycline.json"))["PropertyTable"]["Properties"][0]["SMILES"], "label": "Anhydrotetracycline (abiotic product)"},
}

ALERTS = {
    "alpha_diketone_C11_C12 chelator": "C(=O)C(=O)",
    "phenolic_OH (A-ring)": "cO",
    "dimethylamino_C4": "N(C)C",
    "carboxamide_C2": "C(=O)N",
    "enol_OH": "[OH][c,C]=[c,C]",
}

def main():
    ms, report = {}, {"method": "RDKit 2025.x Morgan FP r2/2048 Tanimoto; alert SMARTS matched where parseable",
                      "caveat": "Fingerprint similarity + structural alerts are deterministic triage, NOT a validated tox model."}
    for name, d in COMPOUNDS.items():
        m = Chem.MolFromSmiles(d["smiles"])
        ms[name] = m
        d["mw"] = round(Descriptors.MolWt(m), 2)
        d["logp_rdkit"] = round(Crippen.MolLogP(m), 2)
        d["tpsa"] = round(rdMolDescriptors.CalcTPSA(m), 1)
        d["rings"] = m.GetRingInfo().NumRings()
        alerts = {}
        for an, sm in ALERTS.items():
            p = Chem.MolFromSmarts(sm)
            alerts[an] = bool(m.HasSubstructMatch(p)) if p else "SMARTS-parse-error"
        d["alerts"] = alerts
        svg = Draw.MolsToGridImage([m], useSVG=True, subImgSize=(420, 340), legends=[d["label"]])
        with open(OUT / f"{name}.svg", "w") as f:
            f.write(svg.replace("svg:", "").replace('xmlns:xlink="http://www.w3.org/1999/xlink"', ""))
    tet = ms["tetracycline"]
    fp_t = AllChem.GetMorganFingerprintAsBitVect(tet, 2, 2048)
    sims = {}
    for name, m in ms.items():
        if name == "tetracycline":
            continue
        fp = AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048)
        sims[name] = round(__import__("rdkit").DataStructs.TanimotoSimilarity(fp_t, fp), 3)
    report["parent_similarity_tanimoto"] = sims
    report["compounds"] = COMPOUNDS
    report["interpretation"] = {
        "4-epitetracycline": f"Tanimoto {sims['4-epitetracycline']} — near-identical scaffold incl. chelation pharmacophore => residual antibacterial activity plausible (matches literature).",
        "anhydrotetracycline": f"Tanimoto {sims['anhydrotetracycline']} — ring system retained but C6 dehydration aromatises C-ring => altered activity + Tet(X)-inhibitor behaviour (literature)."}
    json.dump(report, open(ROOT / "results" / "product_cheminformatics.json", "w"), indent=2)
    print(json.dumps(sims, indent=1), "SVGs written")

if __name__ == "__main__":
    main()
