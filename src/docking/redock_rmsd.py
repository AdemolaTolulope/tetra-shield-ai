#!/usr/bin/env python3
"""Robust heavy-atom RMSD: element-aware Hungarian assignment after centroid alignment.
Used because the 2Y6R crystal ligand has no CONECT records, so bond-perception
based matchers (RDKit GetBestRMS) cannot establish atom correspondence."""
import json, math
import numpy as np
from pathlib import Path
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[2]
RAW, OUT = ROOT / "data" / "raw", ROOT / "results" / "docking"

def pose_coords(pdbqt):
    """top-model heavy atoms with element from pdbqt ATOM lines"""
    pts, elems, started = [], [], False
    for line in open(pdbqt):
        if line.startswith("MODEL") and started:
            break
        if line.startswith(("ATOM", "HETATM")):
            started = True
            e = line[77:79].strip() or line[12:16].strip()[0]
            if e.upper() == "H":
                continue
            pts.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
            elems.append(e.upper())
    return np.array(pts), elems

def crystal_coords():
    pts, elems = [], []
    for line in open(RAW / "2Y6R.pdb"):
        if line.startswith("HETATM") and line[17:20].strip() == "CTC" and line[21] == "A":
            e = line[76:78].strip()
            if e.upper() == "H":
                continue
            pts.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
            elems.append(e.upper())
    return np.array(pts), elems

def svd_rmsd(P, Q):
    """RMSD after optimal rotation (Kabsch) on pre-aligned (matched) arrays"""
    Pc, Qc = P - P.mean(0), Q - Q.mean(0)
    C = Pc.T @ Qc
    V, S, W = np.linalg.svd(C)
    d = np.sign(np.linalg.det(V @ W))
    D = np.diag([1, 1, d])
    U = V @ D @ W
    Prot = Pc @ U
    return float(np.sqrt(((Prot - Qc) ** 2).sum() / len(P)))

def main():
    P, eP = pose_coords(OUT / "chlortetracycline_poses.pdbqt")
    Q, eQ = crystal_coords()
    # element-aware Hungarian assignment on centroid-aligned coordinates
    Pc, Qc = P - P.mean(0), Q - Q.mean(0)
    pair_P, pair_Q = [], []
    for elem in ("C", "N", "O", "CL", "S"):
        iP = [i for i, e in enumerate(eP) if e == elem]
        iQ = [i for i, e in enumerate(eQ) if e == elem]
        if not iP or not iQ:
            continue
        cost = np.linalg.norm(Pc[iP][:, None, :] - Qc[iQ][None, :, :], axis=2)
        ri, ci = linear_sum_assignment(cost)
        for a, b in zip(ri, ci):
            pair_P.append(iP[a]); pair_Q.append(iQ[b])
    Pm, Qm = P[np.array(pair_P)], Q[np.array(pair_Q)]
    rmsd = svd_rmsd(Pm, Qm)
    rep = json.load(open(OUT / "docking_results.json"))
    rep["redock_validation"].pop("error", None)
    rep["redock_validation"]["best_mode_rmsd_A"] = round(rmsd, 2)
    rep["redock_validation"]["method"] = ("element-aware Hungarian assignment + Kabsch, heavy atoms "
                                          f"({len(pair_P)} atom pairs); crystal pose has no CONECT records")
    rep["redock_validation"]["interpretation"] = (
        "PASS (RMSD <= 3.0 A): protocol reproduces crystallographic pose within tolerance"
        if rmsd <= 3.0 else
        "MARGINAL/POOR (RMSD > 3.0 A): docking scores used as QUALITATIVE evidence only, "
        "down-weighted in decision engine; structural confidence flagged")
    json.dump(rep, open(OUT / "docking_results.json", "w"), indent=2)
    print(json.dumps(rep["redock_validation"], indent=2))

if __name__ == "__main__":
    main()
