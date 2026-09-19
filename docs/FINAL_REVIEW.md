# FINAL RED-TEAM REVIEW (post-build self-attack)

## STRENGTHS
- End-to-end *real* computation: validated docking (RMSD 1.84 Å vs co-crystal), real sequences,
  RDKit triage, Monte-Carlo robustness (W=0.955), ablation, 39 passing tests.
- The distinctive scientific doctrine (removal≠degradation≠detoxification; docking≠catalysis;
  similarity≠function; no-hit≠free/safe) is enforced in data + UI, not just prose.
- Honest negatives surfaced (laccase rigid-docking failure; BSFL candidate scored low;
  epimer retains activity) — trust capital with expert judges.
- Offline-proof demo; Nigeria evidence genuinely incorporated (3 point studies, One Health).
- Cassava layer is evidence-bounded and models spent-adsorbent fate (defensible under Q&A).

## WEAKNESSES
- Only 6 candidates; one contaminant. **Fix**: pipeline already generalises (add records +
  rerun scripts); next batch: doxycycline/ciprofloxacin, more destructases (Tet(50)–Tet(56)).
- Component constants expert-set. **Fix**: elicit weights from domain experts (Delphi),
  document each constant ↔ citation mapping more tightly.
- Laccase/MnP substrate-compatibility leans on E2 literature only. **Fix**: MD/covalent-dock
  or mediator-included docking in v1.1; until then the app says exactly this.
- 2Y6R is 3.1 Å. **Fix**: prefer 4A6N (2.3 Å) tetX for a second docking target in v1.1 and compare poses.
- Pei 2025 (L09) citation metadata incompletely resolved → flagged "verify"; conservative claim only.
- No Tox21/CompTox batch integration in offline mode. **Fix**: cache DSSTox records at build time.

## SCIENTIFIC RISKS
- Over-reading docking by judges → mitigated by banners + validation panel; rehearse the
  "docking is 1 of 13 components" answer.
- Cassava confusion (sludge vs peel; TC vs CFX evidence) → UI states it; presenter must too.
- n=6 sensitivity W is *weight-space* stability, not truth stability — say so if pressed.

## DATA RISKS
- Lagos records are point studies; if asked "national levels?" answer: unknown by design.
- CARD coverage: concept-level. Bulk CARD download + AMRFinderPlus run = v1.1.

## MODEL RISKS
- Score interpreted as risk score → disclaimer on every report + UI; test asserts disclaimer exists.
- Rank flip under AMR_CONSERVATIVE is a *feature* (shows stance-sensitivity) — present it as such.

## NOVELTY RISKS
- Integration-level novelty claim made deliberately conservative; not "world's first".
- Risk: a close analog exists in conference abstracts. Mitigation: emphasise concrete
  differentiators (validated docking + product/AMR/uncertainty joint scoring + offline Nigeria
  context + open provenance).

## DEMO RISKS
- 3Dmol requires WebGL: if venue machine lacks it, viewers show fallback text; all data still
  browsable; PDF fallback ready.
- Timing: 90-s script rehearsed; ANALYZE flow < 15 s.

## RECOMMENDED FIXES (ranked)
1. Cache DSSTox/CompTox lookups at build (product tox upgrade).
2. Add 4A6N as second docking target + compare.
3. Bulk CARD/ResFinder checks for ≥1 AMR-positive and 1 AMR-unknown test candidate.
4. Expert-elicited component weights documentation.
5. Pytest CI wrapper + coverage report.
