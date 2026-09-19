# INSTALLATION & DEPLOYMENT
## Local / demo laptop
pip install -r requirements.txt && python3 app/main.py  → http://localhost:8000
(curl/checks: /api/health must report offline-cache mode)
## Server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Bind 0.0.0.0; no env secrets required; static assets local (3Dmol bundled).
## Rebuild from scratch (with internet)
1) re-fetch: re-run curl steps from git history or src/pipeline comments
2) python3 src/docking/prep_docking.py && python3 src/docking/analyze_docking.py && python3 src/docking/redock_rmsd.py
3) python3 src/bioinformatics/sequence_analysis.py && python3 src/chemistry/mol_graphics.py
4) python3 src/pipeline/build_kb.py && python3 src/pipeline/gen_manifest.py
5) python3 tests/test_core.py
