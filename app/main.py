#!/usr/bin/env python3
"""
TETRA-SHIELD AI — application server (FastAPI).
Offline-first: all analysis is computed from cached, provenance-tracked data.
Live mode is optional and never required for the demonstration.
"""
import json, sys
from pathlib import Path
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles

from src.scoring.engine import run_all, sensitivity, ablation, baselines, load_kb, EVIDENCE_MAP, BASE
from src.scoring import report as rep

KB_DIR = ROOT / "data" / "processed" / "kb"
STRUCT_DIR = ROOT / "data" / "processed" / "structures"
STATIC = ROOT / "app" / "static"

app = FastAPI(title="TETRA-SHIELD AI", version="1.0.0",
              description="Environmental Biotransformation Decision Intelligence — offline cache mode")

STRUCT_MAP = {
    "TETX2-BT": "tetx2_2Y6R_chainA_FAD.pdb",
    "TETX-BF": "AF_Q01911.pdb",
    "LAC-TV": "laccase_1GYC_chainA.pdb",
    "MNP-PC": "mnp_1MNP_chainA.pdb",
}

@lru_cache()
def kb():
    return load_kb()

def get_candidate(cid):
    for c in kb()["candidates"]:
        if c["candidate_id"] == cid:
            return c
    raise HTTPException(404, f"candidate '{cid}' not found")

def fasta(acc):
    p = ROOT / "data" / "raw" / f"{acc}.fasta"
    if not p.exists():
        return None
    lines = p.read_text().splitlines()
    return {"header": lines[0], "sequence": "".join(l.strip() for l in lines[1:])}

@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "OFFLINE cache (verified reference data)",
            "n_candidates": len(kb()["candidates"]),
            "engine": "deterministic evidence-integration (ML deliberately not fitted — see MODEL_CARD)"}

# ------------------------------------------------ knowledge endpoints
@app.get("/api/contaminant")
def contaminant():
    c = kb()["contaminant_tetracycline"]
    extra = json.load(open(ROOT / "results" / "product_cheminformatics.json"))
    return {"contaminant": c, "cheminformatics": extra}

@app.get("/api/environment")
def environment():
    return kb()["environment"]

@app.get("/api/cassava")
def cassava():
    return kb()["cassava"]

@app.get("/api/amr")
def amr():
    return kb()["amr"]

@app.get("/api/products")
def products():
    return kb()["products"]

@app.get("/api/pathways")
def pathways():
    return kb()["pathways"]

@app.get("/api/literature")
def literature():
    return kb()["literature"]

@app.get("/api/sequence-analysis")
def sequence_analysis():
    return json.load(open(ROOT / "results" / "sequence_analysis.json"))

# ------------------------------------------------ candidates & scoring
@app.get("/api/candidates")
def candidates(preset: str = "BALANCED"):
    from src.scoring.engine import PRESETS
    w = PRESETS.get(preset, BASE)
    res = run_all(w)
    return {"preset": preset, "ranking": res["candidates"]}

@app.get("/api/candidate/{cid}")
def candidate(cid: str):
    c = get_candidate(cid)
    acc = (c.get("accession") or {}).get("uniprot")
    seq = fasta(acc) if acc else None
    res = run_all(None)
    scored = next((r for r in res["candidates"] if r["candidate_id"] == cid), None)
    return {"candidate": c, "sequence": seq, "scored": scored, "caveats": CAVEATS}

@app.get("/api/candidate/{cid}/scores")
def candidate_scores(cid: str, preset: str = "BALANCED"):
    from src.scoring.engine import PRESETS
    get_candidate(cid)
    res = run_all(PRESETS.get(preset, BASE))
    return next(r for r in res["candidates"] if r["candidate_id"] == cid)

@app.post("/api/score")
def score_custom(payload: dict):
    """payload: {"weights": {component: float}} — WHAT-IF engine"""
    w = {k: max(0.0, float(v)) for k, v in payload.get("weights", {}).items()}
    res = run_all(w)
    return {"weights": w, "ranking": res["candidates"]}

@app.get("/api/compare")
def compare(ids: str = Query(..., description="comma-separated candidate ids")):
    idl = [i.strip() for i in ids.split(",") if i.strip()]
    if not 2 <= len(idl) <= 4:
        raise HTTPException(400, "compare needs 2–4 candidate ids")
    res = run_all(None)
    rows = []
    for cid in idl:
        c = get_candidate(cid)
        s = next((r for r in res["candidates"] if r["candidate_id"] == cid), None)
        rows.append({"candidate": c, "scored": s})
    return {"comparison": rows}

@app.get("/api/sensitivity")
def sens(n: int = 400):
    return sensitivity(n=min(n, 800))

@app.get("/api/ablation")
def abl():
    return ablation()

@app.get("/api/baselines")
def base():
    return baselines()

# ------------------------------------------------ structures & ligand
@app.get("/api/structure/{cid}")
def structure(cid: str):
    fname = STRUCT_MAP.get(cid)
    if not fname:
        raise HTTPException(404, "structure unavailable for this candidate")
    return PlainTextResponse((STRUCT_DIR / fname).read_text())

@app.get("/api/sdf/tetracycline")
def sdf():
    return PlainTextResponse((ROOT / "data" / "processed" / "tetracycline_3d.sdf").read_text())

# ------------------------------------------------ reports
@app.get("/api/report/{cid}")
def report(cid: str, format: str = "json", preset: str = "BALANCED"):
    from src.scoring.engine import PRESETS
    c = get_candidate(cid)
    res = run_all(PRESETS.get(preset, BASE))
    scored = next(r for r in res["candidates"] if r["candidate_id"] == cid)
    r = rep.build_report(kb()["contaminant_tetracycline"], c, scored, preset, kb())
    if format == "json":
        return r
    if format == "csv":
        return Response(rep.to_csv(r), media_type="text/csv",
                        headers={"Content-Disposition": f"attachment; filename=tetra-shield_{cid}.csv"})
    if format == "pdf":
        out = ROOT / "results" / f"report_{cid}.pdf"
        rep.to_pdf(r, out)
        return FileResponse(out, media_type="application/pdf", filename=f"tetra-shield_{cid}.pdf")
    raise HTTPException(400, "format must be json|csv|pdf")

CAVEATS = [
    "REMOVAL ≠ DEGRADATION", "DEGRADATION ≠ DETOXIFICATION", "DOCKING ≠ PROOF OF CATALYSIS",
    "SEQUENCE SIMILARITY ≠ FUNCTIONAL PROOF", "PREDICTED STRUCTURE ≠ EXPERIMENTAL STRUCTURE",
    "NO AMR HIT ≠ AMR-FREE", "NO TOXICITY DATA ≠ SAFE",
    "TETRA-SHIELD PRIORITY SCORE = computational prioritisation, not a validated risk score",
]

@app.get("/api/caveats")
def caveats():
    return {"distinctions": CAVEATS}

app.mount("/static", StaticFiles(directory=STATIC), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
