#!/usr/bin/env python3
"""Sequence intelligence: global pairwise identity (Biopython), sequence stats,
and family similarity matrix. SIMILARITY != DEMONSTRATED FUNCTION (stated on outputs)."""
import json
from pathlib import Path
from Bio.Align import PairwiseAligner
from Bio.SeqUtils.ProtParam import ProteinAnalysis

ROOT = Path(__file__).resolve().parents[2]
SEQS = {"TetX (B. fragilis)": "Q01911", "TetX2 (B. thetaiotaomicron)": "Q93L51",
        "Tet(X3) (P. aeruginosa)": "Q7X2A0", "MnP1 (P. chrysosporium)": "Q02567",
        "Laccase-2 (T. versicolor)": "Q12718"}

def load(acc):
    return "".join(l.strip() for l in open(ROOT / "data" / "raw" / f"{acc}.fasta") if not l.startswith(">"))

def main():
    seqs = {name: load(acc) for name, acc in SEQS.items()}
    al = PairwiseAligner()
    al.mode = "global"; al.match_score = 1.0; al.mismatch_score = 0.0
    al.open_gap_score = -0.5; al.extend_gap_score = -0.1
    matrix = {}
    names = list(seqs)
    for a in names:
        matrix[a] = {}
        for b in names:
            if a == b:
                matrix[a][b] = 100.0
                continue
            score = al.score(seqs[a], seqs[b])
            matrix[a][b] = round(100.0 * score / max(len(seqs[a]), len(seqs[b])), 1)
    stats = {}
    for name, s in seqs.items():
        pa = ProteinAnalysis(s)
        stats[name] = {"length": len(s), "mw_da": round(pa.molecular_weight(), 1),
                       "pI": round(pa.isoelectric_point(), 2),
                       "gravy": round(pa.gravy(), 3),
                       "aromaticity": round(pa.aromaticity(), 3)}
    out = {"method": "Biopython PairwiseAligner, global, match=1 mismatch=0, gap -0.5/-0.1; identity% = score/max_len",
           "caveat": "Sequence similarity is NOT functional proof; family members vary in activity (e.g., inactive Tet(X1)).",
           "sequences": stats, "identity_percent_matrix": matrix,
           "interpretation_notes": [
             "TetX/TetX2/Tet(X3) cluster = tetracycline-destructase family (FAD-monooxygenases).",
             "Fungal MnP1 and laccase are sequence-unrelated — independent oxidative solutions to the same contaminant."]}
    json.dump(out, open(ROOT / "results" / "sequence_analysis.json", "w"), indent=2)
    print(json.dumps(matrix, indent=1))

if __name__ == "__main__":
    main()
