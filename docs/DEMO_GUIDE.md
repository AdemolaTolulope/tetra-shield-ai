# DEMO GUIDE — 90-second judge script + fallback

## Pre-flight (30 s)
- `python3 app/main.py` → open app. Everything is offline; Wi-Fi failure has zero effect.
- Confirm: home shows "OFFLINE CACHE MODE" pill.

## The 90-second flow (scripted)

**0:00 — Problem.** "Antibiotics in water are counted as 'removed' when the parent molecule
disappears. But disappearance is not detoxification — active transformation products and
resistance selection can remain. TETRA-SHIELD computes the whole chain."

**0:10 — ANALYZE.** Click **⟐ ANALYZE CONTAMINANT**. Ten stages fire with real data
(each line is a live local API result: contaminant CID, 6 candidates, 99.5% identity,
structure label, −9.7 kcal/mol, redock 1.84 Å, pathways, product safety, AMR, W=0.955).

**0:25 — Candidates.** Note evidence chips **E1/E2/E3** and AMR chips: the strongest
degraders (TetX family) are flagged **HIGH CONCERN** — resistance genes themselves.

**0:35 — Candidate.** Open **TETX2-BT**: 3D structure (experimental, 3.1 Å) with docked
tetracycline (yellow) and FAD (magenta); contacts table; "DOCKING ≠ CATALYSIS" banner;
re-dock validation 1.84 Å.

**0:50 — Transformation & Safety.** Pathway P1 shows C11a hydroxylation (KNOWN) and the
transient product (STRUCTURE UNCERTAIN). Abiotic matrix P4: **4-epitetracycline retains
activity** — the removable-parent trap, live.

**1:05 — AMR SHIELD.** Three resistance classes; per-candidate screening; One-Health frame
with Nigerian field records (310.2 ng/g TC in Lagos sludge).

**1:15 — DECISION.** Priority ranking (computed, inspectable). Click **WHY?** on #1 →
positive contributors vs risk penalties, verdict. Then hit **AMR CONSERVATIVE** →
ranking flips: laccase takes #1, resistance-enzymes demoted. That IS the point:
decision support, not arbitrary AI.

**1:30 — Impact.** "The engine tells a lab what to test first, and tells an engineer what
form (cell-free enzyme, cassava-biochar pre-concentration) avoids creating a new problem.
Nigeria-validated, offline, and honest about what it doesn't know."

**1:40 (optional)** — REPORT: export PDF/CSV/JSON with sources. COMPARE: 3-candidate view.

## Fallbacks
- If the venue machine is slow: all demos hit `127.0.0.1`; the heaviest call (sensitivity,
  400 iterations) takes <1 s.
- If a projector crops the page: every section also reachable via top nav.
- If asked "is this AI?": answer from MODEL_CARD — deterministic evidence integration +
  deterministic similarity; verified docking; ML deliberately not fitted (justify in one sentence).

## Dead battery / print fallback
`results/report_TETX2-BT.pdf` is a pre-generated judge-readable summary.
