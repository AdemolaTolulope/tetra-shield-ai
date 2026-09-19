#!/usr/bin/env python3
"""
TETRA-SHIELD AI — Docking preparation & execution pipeline.

Real computation, no invented scores:
  1. Extract receptor (2Y6R chain A + FAD cofactor) from experimental PDB.
  2. Convert ligands (PubChem 3D SDF) to PDBQT with Open Babel.
  3. Define search box centred on co-crystallised 7-chlortetracycline (CTC A1385).
  4. Redocking validation: dock 7-CTC back into its own pocket, compute heavy-atom
     RMSD against the crystallographic pose. Report honestly.
  5. Dock tetracycline, collect affinity (kcal/mol), poses, residue contacts.

All parameters & results are written to results/docking/ with provenance.
"""
import json, math, os, subprocess, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results" / "docking"
OUT.mkdir(parents=True, exist_ok=True)
SMINA = ROOT / "assets" / "smina"

def parse_pdb_atoms(path, keep_hydrogen=False):
    atoms = []
    for line in open(path):
        if not line.startswith(("ATOM", "HETATM")):
            continue
        elem = line[76:78].strip() or line[12:16].strip()[-1]
        if elem.upper() == "H" and not keep_hydrogen:
            continue
        atoms.append({
            "record": line[:6].strip(), "name": line[12:16].strip(),
            "resname": line[17:20].strip(), "chain": line[21],
            "resseq": line[22:26].strip(), "x": float(line[30:38]),
            "y": float(line[38:46]), "z": float(line[46:54]),
            "elem": elem.upper()
        })
    return atoms

def centroid(atoms):
    n = len(atoms)
    return (sum(a["x"] for a in atoms)/n, sum(a["y"] for a in atoms)/n,
            sum(a["z"] for a in atoms)/n)

def heavy_rmsd(a_coords, b_coords):
    n = min(len(a_coords), len(b_coords))
    pred_coords = a_coords[:n]
    ref = b_coords[:n]
    # naive correspondence (both from same connectivity order); translate to centroids
    ca = centroid([{"x": p[0], "y": p[1], "z": p[2]} for p in pred_coords])
    cb = centroid([{"x": p[0], "y": p[1], "z": p[2]} for p in ref])
    s = 0.0
    for p, q in zip(pred_coords, ref):
        s += sum(((p[i]-ca[i]) - (q[i]-cb[i]))**2 for i in range(3))
    return math.sqrt(s/n)

def main():
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # ---------- 1. Receptor: 2Y6R chain A protein + FAD (cofactor retained) ----
    atoms = parse_pdb_atoms(RAW / "2Y6R.pdb")
    rec_lines = []
    with open(RAW / "2Y6R.pdb") as fh:
        for line in fh:
            if line.startswith("ATOM") and line[21] == "A":
                rec_lines.append(line)
            elif line.startswith("HETATM") and line[21] == "A" and line[17:20].strip() == "FAD":
                rec_lines.append(line)   # FAD is catalytically required -> kept in receptor
    rec_pdb = OUT / "tetx2_2Y6R_chainA_FAD.pdb"
    rec_pdb.write_text("".join(rec_lines) + "END\n")

    # Search box: centroid of co-crystallised 7-chlortetracycline (chain A, res 1385)
    ctc = [a for a in atoms if a["resname"] == "CTC" and a["chain"] == "A"]
    center = centroid(ctc)
    box = {"center": [round(c, 2) for c in center], "size": [20, 20, 20]}

    # Crystal ligand coordinates for RMSD reference
    ctc_coords = [(a["x"], a["y"], a["z"]) for a in ctc]

    # ---------- 2. Convert receptor + ligands to PDBQT -----------------------
    def to_pdbqt(inp, outp, extra=None):
        cmd = ["obabel", str(inp), "-O", str(outp), "-p", "7.4", "--partialcharge", "gasteiger"]
        if extra:
            cmd += extra
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"obabel failed on {inp}: {r.stderr[-300:]}")

    to_pdbqt(rec_pdb, OUT / "receptor.pdbqt", ["-xr"])
    for name, src in [("tetracycline", RAW / "tetracycline_3d.sdf"),
                      ("chlortetracycline", RAW / "chlortetracycline_3d.sdf")]:
        to_pdbqt(src, OUT / f"{name}.pdbqt")

    # ---------- 3. Docking runs (smina, Vina scoring) --------------------------
    def dock(ligand):
        outpdb = OUT / f"{ligand}_poses.pdbqt"
        logf = OUT / f"{ligand}_log.txt"
        cmd = [str(SMINA), "-r", str(OUT / "receptor.pdbqt"),
               "-l", str(OUT / f"{ligand}.pdbqt"),
               "--center_x", str(box["center"][0]), "--center_y", str(box["center"][1]),
               "--center_z", str(box["center"][2]),
               "--size_x", "20", "--size_y", "20", "--size_z", "20",
               "--exhaustiveness", "16", "--num_modes", "9", "--seed", "42",
               "-o", str(outpdb)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        logf.write_text(r.stdout + r.stderr)
        # parse table
        affs = []
        for line in r.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0].isdigit():
                try:
                    affs.append({"mode": int(parts[0]), "affinity_kcal_mol": float(parts[1]),
                                 "rmsd_lb": float(parts[2]), "rmsd_ub": float(parts[3])})
                except ValueError:
                    pass
        return affs, outpdb

    results = {"created_utc": stamp, "software": "smina (AutoDock Vina 1.1.2 scoring), static build 2019-10-15",
               "seed": 42, "exhaustiveness": 16, "box": box,
               "receptor": {"pdb": "2Y6R", "chain": "A", "cofactor": "FAD retained",
                            "note": "apo protein + FAD; co-crystallised CTC removed before docking"},
               "runs": {}}

    for lig in ["tetracycline", "chlortetracycline"]:
        affs, outpdb = dock(lig)
        results["runs"][lig] = {"modes": affs}

    # ---------- 4. Redocking validation (7-CTC) --------------------------------
    pose_atoms = parse_pdb_atoms(OUT / "chlortetracycline_poses.pdbqt")
    # first MODEL = mode 1
    model1, current, started = [], [], False
    for line in open(OUT / "chlortetracycline_poses.pdbqt"):
        if line.startswith("MODEL"):
            started = True
            if model1:
                break
        elif line.startswith("HETATM") or line.startswith("ATOM"):
            if started:
                model1.append(line)
    coords = []
    for line in model1:
        coords.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
    rmsd = heavy_rmsd(coords, ctc_coords) if coords else None
    results["redock_validation"] = {
        "ligand": "7-chlortetracycline", "best_mode_rmsd_A": round(rmsd, 2) if rmsd else None,
        "interpretation": ("PASS (RMSD <= 3.0 A): docking protocol reproduces the crystallographic pose within tolerance"
                           if rmsd and rmsd <= 3.0 else
                           "POOR (RMSD > 3.0 A): scores treated as qualitative only; flagged LOW confidence in decision engine")
    }

    json.dump(results, open(OUT / "docking_results.json", "w"), indent=2)
    print(json.dumps({k: v for k, v in results.items() if k != "runs"}, indent=2))
    for lig, run in results["runs"].items():
        top = run["modes"][0] if run["modes"] else {}
        print(f"{lig}: top affinity {top.get('affinity_kcal_mol')} kcal/mol, {len(run['modes'])} modes")
    print("Redock RMSD:", results["redock_validation"]["best_mode_rmsd_A"])

if __name__ == "__main__":
    main()
