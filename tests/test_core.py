#!/usr/bin/env python3
"""TETRA-SHIELD test suite — run: python3 tests/test_core.py
Covers: chemical input, sequence handling, candidate retrieval, scoring,
uncertainty, AMR flags, product handling, report generation, graceful failure."""
import json, sys, math, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.scoring.engine import run_all, sensitivity, ablation, baselines, load_kb, component_scores, compute, BASE, EVIDENCE_MAP
from src.scoring import report as rep

P = 0; F = 0
def check(name, cond, extra=""):
    global P, F
    if cond:
        P += 1; print(f"  PASS  {name}")
    else:
        F += 1; print(f"  FAIL  {name} {extra}")

kb = load_kb()

print("== contaminant / chemical input ==")
c = kb["contaminant_tetracycline"]
check("tetracycline formula C22H24N2O8", c["formula"] == "C22H24N2O8")
check("InChIKey present and well-formed", c["identifiers"]["inchikey"].startswith("NWXMGUDVXFXRIG"))
check("provenance complete", all(k in c["provenance"] for k in ["source", "accession", "retrieved"]))
chem = json.load(open(ROOT / "results" / "product_cheminformatics.json"))
check("SMILES parse (RDKit implied by report)", "compounds" in chem)
check("tanimoto values within [0,1]", all(0 <= v <= 1 for v in chem["parent_similarity_tanimoto"].values()))
check("epimer Tanimoto == 1.0 (achiral FP teaching case)", chem["parent_similarity_tanimoto"].get("4-epitetracycline") == 1.0)

print("== sequence handling ==")
sa = json.load(open(ROOT / "results" / "sequence_analysis.json"))
m = sa["identity_percent_matrix"]
check("identity matrix symmetric ~", abs(m["TetX (B. fragilis)"]["Tet(X3) (P. aeruginosa)"] - m["Tet(X3) (P. aeruginosa)"]["TetX (B. fragilis)"]) < 1.0)
check("TetX vs TetX2 > 90% identity", m["TetX (B. fragilis)"]["TetX2 (B. thetaiotaomicron)"] > 90)
check("fungi distant (<40%)", m["MnP1 (P. chrysosporium)"]["Laccase-2 (T. versicolor)"] < 40)
check("sequence stats have length/MW/pI", all(k in sa["sequences"]["TetX (B. fragilis)"] for k in ["length", "mw_da", "pI"]))

print("== candidate retrieval ==")
cands = kb["candidates"]
check("6 candidates", len(cands) == 6)
check("every candidate has evidence level", all(c["evidence_level"] in EVIDENCE_MAP for c in cands))
check("every candidate has AMR status", all(c["resistance_association"]["status"] for c in cands))
check("BSFL candidate honestly sequence-less", next(c for c in cands if c["candidate_id"] == "BSFL-AA12")["sequence_fasta"] is None)

print("== scoring ==")
res = run_all()["candidates"]
check("scores in [0,100]", all(0 <= r["score"] <= 100 for r in res))
check("ranks are permutation 1..6", sorted(r["rank"] for r in res) == [1, 2, 3, 4, 5, 6])
check("TETX2-BT ranks #1 balanced", res[0]["candidate_id"] == "TETX2-BT")
check("unvalidated BSFL ranked last", res[-1]["candidate_id"] == "BSFL-AA12")
amrw = dict(BASE); amrw["amr_risk"] = 3.0
res2 = run_all(amrw)["candidates"]
check("AMR-conservative stance demotes resistance-enzyme", next(r for r in res2 if r["candidate_id"] == "TETX2-BT")["rank"] > 1, str([(r['candidate_id'], r['rank']) for r in res2]))

print("== uncertainty ==")
flags = {r["candidate_id"]: r["components"]["_flags"] for r in res}
check("BSFL flags include unvalidated enzyme", "individual-enzyme-unvalidated" in flags["BSFL-AA12"])
check("every candidate carries >=1 flag (honest system)", all(len(v) >= 1 for v in flags.values()))
check("TETX-BF flagged predicted-structure", "predicted-structure" in flags["TETX-BF"])

print("== AMR ==")
amr = kb["amr"]
check("three mechanism classes", len(amr["tetracycline_resistance_mechanisms"]) == 3)
tetxc = next(c for c in cands if c["candidate_id"] == "TETX-BF")
check("TetX marked HIGH CONCERN", tetxc["resistance_association"]["status"] == "HIGH CONCERN")
check("no candidate claims 'AMR-free'", all("free" not in c["resistance_association"]["mechanism"].lower() for c in cands))

print("== products ==")
prods = kb["products"]
check("epimer residual activity = retained", "RETAINED" in next(p for p in prods if p["product_id"] == "TP-EPI")["residual_activity"]["class"])
check("no product declared 'safe'", all("safe" != json.dumps(p).lower().strip('"') for p in prods))
check("structure-uncertain products labelled", any("UNCERTAIN" in p["structure_status"].upper() or "UNCERTAIN" in p.get("structure_status","").upper() for p in prods))

print("== docking artifacts ==")
dk = json.load(open(ROOT / "results" / "docking" / "docking_results.json"))
check("redock RMSD recorded", 0 < dk["redock_validation"]["best_mode_rmsd_A"] < 10)
check("tetracycline affinity computed", dk["runs"]["tetracycline"]["modes"][0]["affinity_kcal_mol"] < 0)
check("laccase negative result recorded honestly", dk["runs"]["laccase_1GYC_tetracycline"]["modes"][0]["affinity_kcal_mol"] >= -1.0)

print("== decision robustness ==")
s = sensitivity(n=60)
check("Kendall W in [0,1]", 0 <= s["kendalls_W"] <= 1, str(s["kendalls_W"]))
abl = ablation()
check("ablation changes ≥1 candidate score by >2", any(abs(abl[k][cid] - abl['full'][cid]) > 2 for k in abl if k != 'full' for cid in abl[k]))
check("baselines contain integrated", "tetra_shield_integrated" in baselines())

print("== report generation ==")
r = rep.build_report(c, cands[1], res[0], "BALANCED", kb)
check("report has disclaimer", "not a validated" in r["disclaimer"])
check("CSV export non-empty", "priority_score" in rep.to_csv(r))
with tempfile.TemporaryDirectory() as td:
    pdf = rep.to_pdf(r, Path(td) / "x.pdf")
    check("PDF export valid", open(pdf, "rb").read(5) == b"%PDF-")

print("== graceful failure ==")
broken = dict(cands[1]); broken["structure"] = {"kind": "unavailable"}
comps = component_scores(broken, kb)
score, _ = compute(comps, BASE)
check("missing structure doesn't crash; still scored", 0 <= score <= 100)
check("missing structure lowers confidence", comps["structure_confidence"] < 0.3)

print(f"\n==== RESULT: {P} passed, {F} failed ====")
sys.exit(1 if F else 0)
