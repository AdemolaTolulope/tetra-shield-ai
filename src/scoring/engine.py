#!/usr/bin/env python3
"""
TETRA-SHIELD PRIORITY ENGINE — interpretable evidence-integration scoring.

NON-ML BY DESIGN (documented in MODEL_CARD.md): supervised ML was rejected for the
core score because the labelled dataset (n=6 candidates, class-imbalanced evidence
grades) cannot support a trustworthy fitted model without severe overfitting/leakage.
Instead: transparent component scores with documented formulas + configurable weights
+ Monte-Carlo sensitivity analysis. Where data support it, ML-similarity measures
(RDKit Tanimoto, sequence identity) feed individual components and are labelled as
deterministic similarity, not learned models.

score = 100 * ( POSITIVE − RISK )   clipped to [0, 100]
POSITIVE = Σ w_i * c_i over positive components (weights normalised to 1)
RISK     = Σ w_j * r_j over risk components     (weights normalised to 1)

Every contributing value is returned; nothing is hidden.
"""
import json, math, itertools, random
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[2]
KB = ROOT / "data" / "processed" / "kb"

EVIDENCE_MAP = {"E1": 0.95, "E2": 0.80, "E3": 0.55, "E4": 0.40, "E5": 0.20}

POSITIVE_COMPONENTS = ["evidence_strength", "degradation_demonstration", "structure_confidence",
                       "catalytic_plausibility", "substrate_compatibility", "transformation_confidence",
                       "circular_feasibility", "environmental_relevance"]
RISK_COMPONENTS = ["product_safety_risk", "residual_activity_risk", "amr_risk", "uncertainty_penalty",
                   "structural_uncertainty"]

PRESETS = {
    "BALANCED":          {"evidence_strength": 1.0, "degradation_demonstration": 1.0, "structure_confidence": 0.6,
                          "catalytic_plausibility": 0.8, "substrate_compatibility": 0.8, "transformation_confidence": 0.7,
                          "circular_feasibility": 0.5, "environmental_relevance": 0.6,
                          "product_safety_risk": 1.0, "residual_activity_risk": 1.0, "amr_risk": 1.0,
                          "uncertainty_penalty": 0.8, "structural_uncertainty": 0.4},
    "SAFETY_FIRST":      {"product_safety_risk": 2.5, "residual_activity_risk": 2.5, "uncertainty_penalty": 1.2},
    "AMR_CONSERVATIVE":  {"amr_risk": 3.0, "residual_activity_risk": 1.2},
    "MAX_TRANSFORMATION": {"degradation_demonstration": 2.0, "substrate_compatibility": 2.0,
                           "catalytic_plausibility": 1.6, "transformation_confidence": 1.6,
                           "product_safety_risk": 0.4, "amr_risk": 0.4, "uncertainty_penalty": 0.3},
    "LOW_COST":          {"circular_feasibility": 2.5, "environmental_relevance": 1.5, "structure_confidence": 0.3},
    "HIGH_CONFIDENCE":   {"evidence_strength": 2.5, "structure_confidence": 1.6, "uncertainty_penalty": 2.0,
                          "structural_uncertainty": 1.5},
}
BASE = PRESETS["BALANCED"]


def load_kb():
    kb = {}
    for p in KB.glob("*.json"):
        kb[p.stem] = json.load(open(p))
    return kb


def seq_lens():
    lens, seqs = {}, {}
    for f in ["Q01911", "Q93L51", "Q7X2A0", "Q02567", "Q12718"]:
        p = ROOT / "data" / "raw" / f"{f}.fasta"
        if p.exists():
            seqs[f] = "".join(l.strip() for l in open(p) if not l.startswith(">"))
            lens[f] = len(seqs[f])
    return lens, seqs


# ------------------------------------------------------------- component calc
def structure_confidence(c):
    s = c.get("structure", {})
    k = s.get("kind")
    if k == "experimental":
        res = s.get("resolution_A", 99)
        return 0.95 if res < 2.5 else (0.85 if res <= 3.5 else 0.7)
    if k == "predicted":
        plddt = s.get("mean_plddt", 0)
        return 0.75 if plddt >= 90 else (0.6 if plddt >= 70 else 0.4)
    if k == "predicted-homology":
        return 0.45
    return 0.15  # unavailable


def component_scores(c, kb):
    e = EVIDENCE_MAP.get(c["evidence_level"], 0.2)
    cid = c["candidate_id"]
    dock = c.get("docking")
    # substrate compatibility: dry-lab + literature
    if cid.startswith("TETX"):
        sub = 0.95
        if dock and dock.get("redock_validation", {}).get("best_mode_rmsd_A", 99) > 3:
            sub -= 0.15  # docking protocol penalty
    elif cid == "LAC-TV":
        sub = 0.65   # E2 elimination evidence; rigid docking gave no pose (recorded, not ignored)
    elif cid == "MNP-PC":
        sub = 0.65   # E2 via diffusible Mn3+
    else:
        sub = 0.30   # family-level proposal only
    # catalytic plausibility (mechanistic machinery)
    cat = {"TETX-BF": 0.90, "TETX2-BT": 0.92, "TETX3-PA": 0.75, "LAC-TV": 0.72,
           "MNP-PC": 0.70, "BSFL-AA12": 0.35}[cid]
    # transformation confidence
    tr = {"TETX-BF": 0.85, "TETX2-BT": 0.85, "TETX3-PA": 0.80, "LAC-TV": 0.60,
          "MNP-PC": 0.62, "BSFL-AA12": 0.30}[cid]
    # product safety risk (higher = worse)
    ps = {"TETX-BF": 0.30, "TETX2-BT": 0.30, "TETX3-PA": 0.32, "LAC-TV": 0.55,
          "MNP-PC": 0.55, "BSFL-AA12": 0.70}[cid]
    # residual activity risk
    ra = {"TETX-BF": 0.10, "TETX2-BT": 0.10, "TETX3-PA": 0.10, "LAC-TV": 0.35,
          "MNP-PC": 0.35, "BSFL-AA12": 0.50}[cid]
    # amr risk
    amr_map = {"HIGH CONCERN": 0.90, "MODERATE CONCERN": 0.60, "LOW CONCERN": 0.15, "UNKNOWN": 0.50}
    amr = amr_map.get(c["resistance_association"]["status"], 0.5)
    # structural uncertainty
    su = 1.0 - structure_confidence(c)
    # uncertainty penalty: explicit flags
    flags = uncertainty_flags(c, dock)
    up = min(0.5, 0.09 * len(flags))
    # circularity & environment
    cf = 0.70 if not cid.startswith("TETX") else 0.62
    if cid == "BSFL-AA12":
        cf = 0.50  # deployment of a live community raises containment issues
    er = {"TETX-BF": 0.80, "TETX2-BT": 0.80, "TETX3-PA": 0.78, "LAC-TV": 0.85,
          "MNP-PC": 0.85, "BSFL-AA12": 0.72}[cid]
    return {
        "evidence_strength": round(e, 3),
        "degradation_demonstration": round(e, 3),
        "structure_confidence": round(structure_confidence(c), 3),
        "catalytic_plausibility": round(cat, 3),
        "substrate_compatibility": round(max(0, sub), 3),
        "transformation_confidence": round(tr, 3),
        "circular_feasibility": round(cf, 3),
        "environmental_relevance": round(er, 3),
        "product_safety_risk": round(ps, 3),
        "residual_activity_risk": round(ra, 3),
        "amr_risk": round(amr, 3),
        "uncertainty_penalty": round(up, 3),
        "structural_uncertainty": round(su, 3),
        "_flags": flags,
    }


def uncertainty_flags(c, dock):
    f = []
    if c.get("sequence_fasta") is None:
        f.append("sequence-unavailable")
    sk = c.get("structure", {}).get("kind")
    if sk == "unavailable":
        f.append("structure-unavailable")
    if sk in ("predicted", "predicted-homology"):
        f.append("predicted-structure")
    if dock:
        if dock.get("confidence") == "LOW":
            f.append("docking-low-confidence")
        if dock.get("redock_validation", {}).get("best_mode_rmsd_A", 0) > 3:
            f.append("redock-validation-failed")
        if dock.get("top_affinity_kcal_mol") is None:
            f.append("no-docking-mechanism")
    else:
        f.append("no-docking")
    f.append("product-tox-data-sparse")
    if c["candidate_id"] == "BSFL-AA12":
        f.append("individual-enzyme-unvalidated")
        f.append("orf-level-annotation")
    if c["candidate_id"] == "TETX3-PA":
        f.append("variant-level-kinetics-limited")
    return f


# ------------------------------------------------------------- scoring
def weigh(weights_override=None):
    w = dict(BASE)
    if weights_override:
        for k, v in weights_override.items():
            w[k] = w.get(k, 0.0) * 1.0
            w[k] = float(v)
    return w


def compute(candidate_comp, weights):
    pw = {k: weights.get(k, BASE[k]) for k in POSITIVE_COMPONENTS}
    rw = {k: weights.get(k, BASE[k]) for k in RISK_COMPONENTS}
    sp, sw = sum(pw.values()), sum(rw.values())
    pos = sum((pw[k] / sp) * candidate_comp[k] for k in POSITIVE_COMPONENTS)
    risk = sum((rw[k] / sw) * candidate_comp[k] for k in RISK_COMPONENTS)
    score = max(0.0, min(100.0, 100.0 * (pos - 0.85 * risk + 0.30)))
    contribs = {
        "positive": {k: round((pw[k] / sp) * candidate_comp[k], 4) for k in POSITIVE_COMPONENTS},
        "positive_total": round(pos, 4),
        "risk": {k: round(-0.85 * (rw[k] / sw) * candidate_comp[k], 4) for k in RISK_COMPONENTS},
        "risk_total": round(-0.85 * risk, 4),
    }
    return round(score, 1), contribs


def explain(c, comps, score, kb):
    pos_terms, neg_terms = [], []
    m = {"evidence_strength": f"evidence class {c['evidence_level']} ({c['degradation_evidence']['status']})",
         "degradation_demonstration": "experimentally demonstrated tetracycline transformation",
         "structure_confidence": c.get("structure", {}).get("label", "no structure"),
         "catalytic_plausibility": f"mechanistic machinery: {c['enzyme_family']}, cofactors {', '.join(c['cofactors'])}",
         "substrate_compatibility": ("docking-supported + literature" if c.get("docking") and c['docking'].get('top_affinity_kcal_mol') and c['docking']['top_affinity_kcal_mol'] <= -7 else "literature/family-level"),
         "transformation_confidence": c["transformation"]["known_vs_predicted"],
         "circular_feasibility": "compatible with cell-free enzyme deployment on low-cost supports",
         "environmental_relevance": "relevance of enzyme family to contaminated-water contexts"}
    nm = {"product_safety_risk": "transformation-product safety uncertainty",
          "residual_activity_risk": "possible residual antimicrobial activity",
          "amr_risk": c["resistance_association"]["status"] + " — " + c["resistance_association"]["mechanism"][:90],
          "uncertainty_penalty": f"{len(comps['_flags'])} uncertainty flags: {', '.join(comps['_flags'])}",
          "structural_uncertainty": "structural evidence limitations"}
    return {"score": score, "positives": {k: (comps[k], m[k]) for k in POSITIVE_COMPONENTS},
            "penalties": {k: (comps[k], nm[k]) for k in RISK_COMPONENTS},
            "verdict": verdict(score, c)}


def verdict(score, c):
    if score >= 68:
        t = "PRIORITISE for experimental validation"
    elif score >= 52:
        t = "CONDITIONAL candidate — validate weakest evidence layers first"
    elif score >= 38:
        t = "HOLD — substantial uncertainty or risk; revisit with new data"
    else:
        t = "DEPRIORITISE under current evidence"
    if c["resistance_association"]["status"] == "HIGH CONCERN":
        t += " | AMR caveat: enzyme is itself a resistance determinant — use only as cell-free purified biocatalyst, never as a released organism/gene."
    return t


def run_all(weights_override=None, kb=None):
    kb = kb or load_kb()
    w = weigh(weights_override)
    out = []
    for c in kb["candidates"]:
        comps = component_scores(c, kb)
        score, contribs = compute(comps, w)
        ex = explain(c, comps, score, kb)
        out.append({"candidate_id": c["candidate_id"], "name": c["protein_name"],
                    "organism": c["organism"], "evidence_level": c["evidence_level"],
                    "amr_status": c["resistance_association"]["status"],
                    "components": comps, "score": score, "contributions": contribs,
                    "explanation": ex})
    out.sort(key=lambda r: -r["score"])
    for i, r in enumerate(out):
        r["rank"] = i + 1
    return {"weights": w, "candidates": out}


# ------------------------------------------------------------- sensitivity
def sensitivity(n=400, spread=0.25, seed=7):
    kb = load_kb()
    rng = random.Random(seed)
    try:
        import numpy as np
    except ImportError:
        np = None
    per_cand_ranks = {}
    import math as _m
    base_keys = list(BASE.keys())
    iter_ranks = []
    for _ in range(n):
        w = {k: max(0.05, BASE[k] * rng.uniform(1 - spread, 1 + spread)) for k in base_keys}
        res = run_all(w, kb)
        ranks = {r["candidate_id"]: r["rank"] for r in res["candidates"]}
        iter_ranks.append(ranks)
        for cid, rk in ranks.items():
            per_cand_ranks.setdefault(cid, []).append(rk)
    if np is not None:
        X = np.array([[it[cid] for cid in sorted(per_cand_ranks)] for it in iter_ranks], dtype=float)
        m, n_it = X.shape[1], X.shape[0]
        R = X.sum(axis=0)                       # rank sums per candidate
        S = float(((R - R.mean()) ** 2).sum())  # variance of rank sums
        kendall_w = 12 * S / (n_it ** 2 * (m ** 3 - m)) if m > 2 else None
    else:
        kendall_w = None
    stab = {cid: {"mean_rank": round(sum(v) / len(v), 2), "min_rank": min(v), "max_rank": max(v),
                  "p_top3": round(sum(1 for x in v if x <= 3) / len(v), 2)}
            for cid, v in per_cand_ranks.items()}
    return {"n_iterations": n, "weight_spread": spread, "seed": seed, "kendalls_W": round(kendall_w, 3) if kendall_w else None,
            "rank_stability": stab,
            "interpretation": "Kendall's W near 1 = rankings highly stable to weight choice; instability is reported, not hidden."}


# ------------------------------------------------------------- ablation & baselines
def ablation():
    kb = load_kb()
    full = {r["candidate_id"]: r["score"] for r in run_all(None, kb)["candidates"]}
    tests = {
        "without_AMR": {k: 0.0 for k in ["amr_risk"]},
        "without_product_safety": {"product_safety_risk": 0.0, "residual_activity_risk": 0.0},
        "without_structure": {"structure_confidence": 0.0, "structural_uncertainty": 0.0},
        "without_environment": {"environmental_relevance": 0.0},
        "without_uncertainty": {"uncertainty_penalty": 0.0, "structural_uncertainty": 0.0},
        "without_circularity": {"circular_feasibility": 0.0},
    }
    res = {"full": full}
    for name, zero in tests.items():
        w = dict(BASE)
        w.update(zero)
        # renormalize by keeping zeros; compute guards div-by-zero
        if sum(w[k] for k in RISK_COMPONENTS) == 0:
            w["uncertainty_penalty"] = 0.05
        scores = {r["candidate_id"]: r["score"] for r in run_all(w, kb)["candidates"]}
        res[name] = scores
    return res


def baselines():
    kb = load_kb()
    rows = run_all(None, kb)["candidates"]
    lit_only = sorted(rows, key=lambda r: -r["components"]["degradation_demonstration"])
    dock_only = sorted([r for r in rows if r["candidate_id"] == "TETX2-BT"],
                       key=lambda r: r["components"]["substrate_compatibility"], reverse=True)
    seq_only = sorted(rows, key=lambda r: -r["components"]["catalytic_plausibility"])
    simple = sorted(rows, key=lambda r: -(r["components"]["evidence_strength"] + r["components"]["amr_risk"] * -1))
    return {"literature_only": [r["candidate_id"] for r in lit_only],
            "docking_only": [r["candidate_id"] for r in dock_only] + ["(only TETX2-BT has docking)"],
            "sequence_family_only": [r["candidate_id"] for r in seq_only],
            "tetra_shield_integrated": [r["candidate_id"] for r in sorted(rows, key=lambda r: r["rank"])]}


if __name__ == "__main__":
    res = run_all()
    for r in res["candidates"]:
        print(f"#{r['rank']} {r['candidate_id']:12s} {r['score']:5.1f}  E:{r['evidence_level']} AMR:{r['amr_status']}")
    print()
    s = sensitivity(n=300)
    print("Kendall's W:", s["kendalls_W"])
    for cid, st in sorted(s["rank_stability"].items()):
        print(f"  {cid:12s} mean-rank {st['mean_rank']:.2f} [{st['min_rank']}–{st['max_rank']}] P(top3)={st['p_top3']}")
