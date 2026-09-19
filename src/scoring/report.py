#!/usr/bin/env python3
"""Report generator: JSON / CSV / PDF (reportlab). Graceful failure: any missing
field renders 'Data unavailable' instead of crashing."""
import json, csv, io, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def _g(d, *ks, default="Data unavailable"):
    cur = d
    for k in ks:
        if not isinstance(cur, dict) or cur.get(k) in (None, "", []):
            return default
        cur = cur[k]
    return cur

def build_report(contaminant, cand, scored, preset, kb):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return {
        "report_title": "TETRA-SHIELD AI — Contaminant Biotransformation Intelligence Report",
        "generated_utc": now, "mode": "offline cached reference data",
        "disclaimer": ("TETRA-SHIELD PRIORITY SCORE is a computational prioritisation framework, not a validated "
                       "clinical, regulatory, toxicological or environmental risk score. Predictions are labelled "
                       "PREDICTED; literature-supported and experimentally demonstrated items are labelled as such."),
        "contaminant": {"name": contaminant["preferred_name"], "formula": contaminant["formula"],
                        "mw": contaminant["molecular_weight"], "pubchem_cid": contaminant["identifiers"]["pubchem_cid"]},
        "candidate": {"id": cand["candidate_id"], "protein": cand["protein_name"], "organism": cand["organism"],
                      "evidence_level": cand["evidence_level"],
                      "accession": cand.get("accession", {})},
        "decision": {"preset": preset, "priority_score": scored["score"], "rank": scored["rank"],
                     "verdict": scored["explanation"]["verdict"]},
        "components": scored["components"],
        "uncertainty_flags": scored["components"]["_flags"],
        "amr": cand["resistance_association"],
        "transformation": cand["transformation"],
        "structure": cand.get("structure", {}),
        "docking": cand.get("docking") or "Data unavailable",
        "key_distinctions": ["REMOVAL != DEGRADATION", "DEGRADATION != DETOXIFICATION", "DOCKING != CATALYSIS",
                             "SEQUENCE SIMILARITY != FUNCTIONAL PROOF", "PREDICTED STRUCTURE != EXPERIMENTAL STRUCTURE",
                             "NO AMR HIT != AMR-FREE", "NO TOXICITY DATA != SAFE"],
        "sources": [l for l in kb["literature"] if l["id"] in set(cand.get("refs", []))],
    }

def to_csv(rep):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["section", "field", "value"])
    w.writerow(["meta", "generated_utc", rep["generated_utc"]])
    w.writerow(["contaminant", "name", rep["contaminant"]["name"]])
    w.writerow(["contaminant", "formula", rep["contaminant"]["formula"]])
    w.writerow(["candidate", "id", rep["candidate"]["id"]])
    w.writerow(["candidate", "protein", rep["candidate"]["protein"]])
    w.writerow(["candidate", "evidence_level", rep["candidate"]["evidence_level"]])
    w.writerow(["decision", "priority_score", rep["decision"]["priority_score"]])
    w.writerow(["decision", "verdict", rep["decision"]["verdict"]])
    for k, v in rep["components"].items():
        if not k.startswith("_"):
            w.writerow(["components", k, v])
    return buf.getvalue()

def to_pdf(rep, out_path):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Title"], fontSize=17, textColor=colors.HexColor("#0b3b36"))
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=colors.HexColor("#0e5a52"), fontSize=12)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=9, leading=12)
    small = ParagraphStyle("small", parent=styles["BodyText"], fontSize=7.5, leading=10, textColor=colors.HexColor("#444"))
    doc = SimpleDocTemplate(str(out_path), pagesize=A4, leftMargin=16*mm, rightMargin=16*mm, topMargin=14*mm, bottomMargin=14*mm)
    el = []
    el.append(Paragraph("TETRA-SHIELD AI", h1))
    el.append(Paragraph("Contaminant Biotransformation Intelligence Report (offline cached data)", h2))
    el.append(Paragraph(f"Generated: {rep['generated_utc']}", small))
    el.append(Paragraph(rep["disclaimer"], small))
    el.append(Spacer(1, 6)); el.append(HRFlowable(width="100%", color=colors.HexColor("#0e5a52"))); el.append(Spacer(1, 8))
    el.append(Paragraph(f"CONTAMINANT — {rep['contaminant']['name']} ({rep['contaminant']['formula']}, MW {rep['contaminant']['mw']})", h2))
    el.append(Paragraph(f"CANDIDATE — {rep['candidate']['protein']} [{rep['candidate']['id']}] from <i>{rep['candidate']['organism']}</i>; evidence level {rep['candidate']['evidence_level']}", body))
    el.append(Spacer(1, 6))
    d = rep["decision"]
    el.append(Paragraph(f"TETRA-SHIELD PRIORITY SCORE ({d['preset']}): <b>{d['priority_score']} / 100</b> — rank #{d['rank']}", h2))
    el.append(Paragraph(str(d["verdict"]), body)); el.append(Spacer(1, 6))
    comps = rep["components"]
    rows = [["Layer", "Value 0–1", "Layer", "Value 0–1"]]
    keys = [k for k in comps if not k.startswith("_")]
    for i in range(0, len(keys), 2):
        row = [keys[i], f"{comps[keys[i]]:.2f}"]
        if i + 1 < len(keys):
            row += [keys[i+1], f"{comps[keys[i+1]]:.2f}"]
        rows.append(row)
    t = Table(rows, colWidths=[60*mm, 20*mm, 60*mm, 20*mm])
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0e5a52")),
                           ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                           ("FONTSIZE", (0,0), (-1,-1), 7.5),
                           ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#bcd4cf")),
                           ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#eef5f3")])]))
    el.append(t); el.append(Spacer(1, 8))
    el.append(Paragraph("UNCERTAINTY FLAGS", h2))
    el.append(Paragraph("; ".join(rep["uncertainty_flags"]) or "none", body))
    el.append(Paragraph("AMR SHIELD", h2))
    a = rep["amr"]
    el.append(Paragraph(f"{a.get('status','Data unavailable')} — {a.get('mechanism','')} (computational screening category, not a clinical/regulatory determination)", body))
    el.append(Paragraph("CORE DISTINCTIONS", h2))
    el.append(Paragraph(" | ".join(rep["key_distinctions"]), small))
    el.append(Paragraph("SOURCES (candidate-scoped)", h2))
    for s in rep["sources"]:
        el.append(Paragraph(f"[{s['id']}] {s['cite']} — {s.get('doi','')}", small))
    doc.build(el)
    return str(out_path)
