#!/usr/bin/env python3
"""TETRA-SHIELD pitch deck: PIL-rendered slides -> PNG + PPTX + PDF.
Every figure comes from the running prototype (results/*.json)."""
import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/home/user/tetra-shield-ai")
OUT = ROOT / "results" / "deck"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1600, 900

F = "/usr/share/fonts/truetype/dejavu/"
def font(sz, bold=False, mono=False):
    return ImageFont.truetype(F + ("DejaVuSansMono-Bold.ttf" if mono and bold else
            "DejaVuSansMono.ttf" if mono else "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), sz)

BG=(7,18,17); PAN=(14,35,32); LINE=(29,63,57); ACC=(58,223,169); CY=(35,181,211)
GOLD=(232,199,102); WARN=(244,159,90); RED=(240,109,109); OK=(87,217,157)
TX=(230,242,238); DIM=(143,179,171); FAINT=(93,127,120); DK=(6,31,26)

CK = json.load(open(ROOT/"results/decision_engine_validation.json"))

def canvas():
    im = Image.new("RGB", (W,H), BG)
    d = ImageDraw.Draw(im)
    for i in range(60):  # subtle glow top-right
        a = int(60*(1-i/60))
        d.ellipse([W-520-i*6,-260-i*6,W+320+i*6,420+i*6], outline=(13,43,38))
    return im, d

def kicker(d, txt, y=64):
    d.text((80,y), txt, font=font(21, mono=True), fill=ACC)
def title(d, txt, y=96, size=58):
    d.text((80,y), txt, font=font(size, bold=True), fill=TX)
def foot(d, page, txt="TETRA-SHIELD AI · BioShield-X · NSBS Innovation Challenge 2026"):
    d.text((80,H-56), txt, font=font(18), fill=FAINT)
    d.text((W-130,H-56), f"{page:02d}", font=font(20,mono=True,bold=True), fill=ACC)
def bullet(d, x, y, txt, color=TX, size=26, mark="•", gap=52, width=None, dim_first=None):
    d.text((x,y), mark, font=font(size,bold=True), fill=ACC)
    if dim_first:
        d.text((x+34,y), dim_first, font=font(size,bold=True), fill=GOLD)
        w0 = d.textlength(dim_first+" ", font=font(size,bold=True))
        wrap_text(d, txt, x+34+w0, y, size, color, width or (W-(x+34+w0)-80))
    else:
        wrap_text(d, txt, x+34, y, size, color, width or (W-x-34-80))
    return y+gap

def wrap_text(d, txt, x, y, size, fill, maxw):
    fb = font(size); words = txt.split(); line = ""
    for wd in words:
        t = (line+" "+wd).strip()
        if d.textlength(t, font=fb) > maxw:
            d.text((x,y), line, font=fb, fill=fill); y += size+8; line = wd
        else: line = t
    d.text((x,y), line, font=fb, fill=fill)
    return y

def stat(d, x, y, big, small, w=300, color=ACC):
    d.rounded_rectangle([x,y,x+w,y+120], 16, fill=PAN, outline=LINE, width=2)
    d.text((x+22,y+16), big, font=font(46,bold=True,mono=True), fill=color)
    d.text((x+22,y+74), small, font=font(18), fill=DIM)

def panel(d, x, y, w, h, head=None):
    d.rounded_rectangle([x,y,x+w,y+h], 16, fill=PAN, outline=LINE, width=2)
    if head:
        d.text((x+22,y+16), head.upper(), font=font(20,bold=True), fill=ACC)

def bar(d, x, y, w, v, h=16, color1=CY, color2=ACC):
    d.rounded_rectangle([x,y,x+w,y+h], h//2, fill=(18,39,35))
    d.rounded_rectangle([x,y,x+max(h,int(w*v)),y+h], h//2, fill=color2)

def flow(d, x, y, steps, box_w=150, box_h=64, size=17, known=None):
    for i, s in enumerate(steps):
        k = known[i] if known else True
        col = LINE if k else (91,81,34)
        d.rounded_rectangle([x,y,x+box_w,y+box_h], 10, fill=PAN, outline=col, width=2)
        wrap_center(d, s, x+box_w/2, y+box_h/2, size, TX, box_w-14)
        if i < len(steps)-1:
            d.text((x+box_w+6,y+box_h/2-14), "→", font=font(26,bold=True), fill=ACC)
        x += box_w + 30
    return y + box_h

def wrap_center(d, txt, cx, cy, size, fill, maxw):
    fb = font(size, bold=True); words = txt.split(); lines=[]; line=""
    for wd in words:
        t=(line+" "+wd).strip()
        if d.textlength(t,font=fb)>maxw: lines.append(line); line=wd
        else: line=t
    lines.append(line)
    th = len(lines)*(size+5)
    for j,l in enumerate(lines):
        d.text((cx-d.textlength(l,font=fb)/2, cy-th/2+j*(size+5)), l, font=fb, fill=fill)

def shield(d, cx, cy, s=1.0):
    pts=[(cx,cy-56*s),(cx+44*s,cy-38*s),(cx+44*s,cy+8*s),(cx,cy+56*s),(cx-44*s,cy+8*s),(cx-44*s,cy-38*s)]
    d.polygon(pts, fill=(12,30,26), outline=ACC)
    d.ellipse([cx-18*s,cy-26*s,cx+18*s,cy+10*s], outline=ACC, width=4)

S = []

# ---- S1 PROBLEM ----
im,d = canvas(); kicker(d,"THE PROBLEM"); title(d,"Antibiotic 'removal' is not detoxification", size=50)
y=190
y=bullet(d,80,y,"was measured in Lagos hospital wastewater sludge (Ajibola & Zwiener 2022)",size=25,dim_first="310 ng/g tetracycline")
y=bullet(d,80,y,"tetracycline-resistance genes circulate in Lagos aquatic isolates (2025 field study)",size=25,dim_first="tetA / tetB / tetM")
y=bullet(d,80,y,"parent-molecule disappearance is counted as success — while products and selection continue",size=25,dim_first="Yet:")
stat(d,80,430,"310.2","ng/g TC · Lagos sludge"); stat(d,420,430,"<0.05–8.84","µg/L range · Lagos waters (class)"); stat(d,760,430,"3","resistance classes in environment")
stat(d,1100,430,"ng–µg/L","sub-MIC selection pressure persists",color=WARN)
d.rounded_rectangle([80,600,1520,780],16,fill=(30,14,14),outline=RED,width=2)
d.text((110,622),"The molecule can vanish from the LC-MS trace while its active epimer remains —",font=font(28,bold=True),fill=TX)
d.text((110,664),"and sub-inhibitory residues keep training resistant bacteria.",font=font(28,bold=True),fill=TX)
d.text((110,716),"Nigeria needs remediation verified SAFE, not just analytically invisible.",font=font(24),fill=WARN)
foot(d,1); S.append(("s01_problem.png",im))

# ---- S2 WHY CURRENT INCOMPLETE ----
im,d = canvas(); kicker(d,"WHY CURRENT APPROACHES ARE INCOMPLETE"); title(d,"Three facts the routine metrics miss", size=50)
cards=[("REMOVAL ≠ DEGRADATION","Sorption & epimerisation hide the molecule without changing its activity.",WARN),
       ("DEGRADATION ≠ DETOXIFICATION","4-epitetracycline retains antibacterial activity; anhydrotetracycline alters it.",RED),
       ("DEGRADERS CAN BE RISKS","The best tetracycline-destroying enzymes ARE resistance genes (tet(X) family).",GOLD)]
for i,(h1,b1,c1) in enumerate(cards):
    x=80+i*490; panel(d,x,210,460,300); d.rounded_rectangle([x,210,x+460,300],16,fill=c1)
    d.text((x+30,222),h1,font=font(27,bold=True),fill=DK)
    wrap_text(d,b1,x+30,330,24,TX,400)
flow(d,80,610,["CONTAMINANT","PARENT DISAPPEARS","…PRODUCT?","…ACTIVITY?","…AMR SELECTION?"],box_w=220,box_h=80,known=[True,True,False,False,False])
d.text((80,740),"Analytics answers the first box. TETRA-SHIELD computes all five.",font=font(26,bold=True),fill=ACC)
foot(d,2); S.append(("s02_gap.png",im))

# ---- S3 BIOLOGICAL INSIGHT ----
im,d = canvas(); kicker(d,"THE BIOLOGICAL INSIGHT"); title(d,"Nature already runs this chemistry", size=50)
y=190
y=bullet(d,80,y,"FAD monooxygenases hydroxylate tetracycline at C11a → Mg²⁺-chelating pharmacophore destroyed → lost antibacterial activity",dim_first="Tet(X) family:",gap=64)
y=bullet(d,80,y,"multicopper oxidases + Mn-peroxidases oxidise tetracyclines (Suda 2012; Wen 2010)",dim_first="Fungal white-rot enzymes:",gap=64)
y=bullet(d,80,y,"black-soldier-fly gut microbiomes enrich laccase/peroxidase-like genes and triple degradation (2023–2025 studies)",dim_first="Insect microbiomes:",gap=64)
flow(d,80,500,["TC + NADPH + O₂","11α-OH-TC","hemiketal","INACTIVE PRODUCTS"],box_w=260,box_h=76)
d.text((80,600),"Tension: Tet(X) is literature's strongest degrader — and a mobile resistance determinant.",font=font(27,bold=True),fill=WARN)
d.text((80,650),"Deployment must therefore prefer purified, cell-free enzymes — never released genes/organisms.",font=font(25),fill=TX)
flow(d,80,720,["SEQUENCE ≠ FUNCTION","DOCKING ≠ CATALYSIS","PREDICTED ≠ EXPERIMENTAL"],box_w=290,box_h=70,known=[False]*3)
foot(d,3); S.append(("s03_insight.png",im))

# ---- S4 THE PRODUCT ----
im,d = canvas(); kicker(d,"TETRA-SHIELD — BioShield-X platform, module 1"); title(d,"Can this transformation help — and could it create another problem?", size=40)
flow(d,80,210,["CONTAMINANT","CANDIDATES","SEQUENCE","STRUCTURE","DOCKING","PATHWAY","PRODUCTS","SAFETY","AMR","SCORE"],box_w=125,box_h=60,size=15,known=[True]*10)
y=330
for t1,c1 in [("EXPLAINABLE","Every score: positive contributors vs risk penalties, click 'WHY?'"),
          ("STANCE-AWARE","WHAT-IF presets recalculate: safety-first, AMR-conservative, low-cost…"),
          ("OFFLINE-FIRST","Judges' demo runs with zero network; all data provenance-tagged"),
          ("HONEST","UNKNOWN stays UNKNOWN; negatives are reported, never hidden")]:
    y=bullet(d,80,y,c1,dim_first=t1+":",gap=54)
panel(d,80,610,1440,180,"The one-sentence differentiation")
d.text((110,660),"BLAST answers 'similar?'. Docking answers 'binds?'. CARD answers 'resistance?'.",font=font(28),fill=DIM)
d.text((110,712),"TETRA-SHIELD chains them into one decision: which biocatalyst to validate first — and what hazard comes with it.",font=font(28,bold=True),fill=ACC)
foot(d,4); S.append(("s04_product.png",im))

# ---- S5 ENGINE ----
im,d = canvas(); kicker(d,"HOW THE ENGINE WORKS"); title(d,"13 inspectable components — no black box", size=50)
pos=["Evidence strength","Degradation demo","Structural confidence","Catalytic plausibility","Substrate fit","Transformation","Circularity","Environment"]
neg=["Product-safety risk","Residual activity","AMR risk","Uncertainty","Structural uncert."]
panel(d,80,200,700,420,"Positive evidence (8)")
yy=254
for i,p in enumerate(pos):
    d.text((110,yy),"+" ,font=font(24,bold=True),fill=OK)
    d.text((140,yy+2),p,font=font(23),fill=TX); bar(d,430,yy+6,320,0.85-(i%4)*0.12); yy+=44
panel(d,820,200,700,420,"Risk penalties (5)")
yy=254
for i,p in enumerate(neg):
    d.text((850,yy),"−",font=font(24,bold=True),fill=WARN)
    d.text((880,yy+2),p,font=font(23),fill=TX); bar(d,1170,yy+6,320,0.5-(i%3)*0.1,color1=WARN,color2=WARN); yy+=60
d.text((80,660),"score = 100 × (Σw⁺·evidence − 0.85·Σw⁻·risk + 0.30)",font=font(26,mono=True),fill=CY)
d.text((80,706),"Weights are sliders, not doctrine — and stability is measured, not assumed.",font=font(24),fill=DIM)
d.text((80,748),"No ML fitted on n=6 — deterministic evidence integration (choice documented in MODEL_CARD).",font=font(24,bold=True),fill=GOLD)
foot(d,5); S.append(("s05_engine.png",im))

# ---- S6 LIVE DEMO / DOCKING ----
im,d = canvas(); kicker(d,"LIVE COMPUTATIONAL DEMONSTRATION"); title(d,"Actually computed. Actually validated.", size=50)
panel(d,80,200,470,360,"Validated docking")
d.text((110,255),"−9.7",font=font(64,bold=True,mono=True),fill=ACC)
d.text((110,330),"kcal/mol · tetracycline ↔ TetX2 (2Y6R+FAD)",font=font(19),fill=DIM)
d.text((110,380),"1.84 Å",font=font(54,bold=True,mono=True),fill=CY)
d.text((110,444),"re-dock RMSD vs co-crystal ligand → PASS",font=font(19),fill=DIM)
d.text((110,494),"smina/Vina 1.1.2 · seed 42 · exhaustiveness 16",font=font(16),fill=FAINT)
panel(d,580,200,470,360,"Contact map (top pose)")
contacts=["HIS234","ARG213","GLU114","PHE224","MET215","PRO318–GLY321"]
yy=260
for i,c1 in enumerate(contacts):
    d.rounded_rectangle([610,yy,900,yy+40],9,fill=(18,60,52),outline=LINE)
    d.text((624,yy+7),c1,font=font(22,mono=True),fill=CY); yy+=52
d.text((610,yy+4),"FAD 2.36 Å · matches literature pocket",font=font(17),fill=GOLD)
panel(d,1080,200,440,360,"Honest negatives")
wrap_text(d,"Laccase rigid docking: all poses ≈ 0 kcal/mol — reported, not hidden. Substrate case rests on E2 literature.",1110,260,23,TX,380)
d.text((1110,430),"DOCKING ≠ CATALYSIS",font=font(25,bold=True),fill=WARN)
d.text((80,620),"Sequence intelligence (real alignments):",font=font(25,bold=True),fill=TX)
flow(d,80,670,["TetX ↔ TetX2  99.5%","↔ Tet(X3)  82%","↔ fungi  18–21%","2 independent solutions"],box_w=340,box_h=70,size=19)
foot(d,6); S.append(("s06_demo.png",im))

# ---- S7 AMR + SAFETY + CIRCULAR ----
im,d = canvas(); kicker(d,"AMR SHIELD + PRODUCT SAFETY + CIRCULAR BIOREMEDIATION"); title(d,"The safety layers change the decision", size=44)
panel(d,80,190,470,300,"AMR Shield")
for i,(c1,lv,cl) in enumerate([("TetX family","HIGH",RED),("TetX2","HIGH",RED),("Tet(X3)","HIGH",RED),("Laccase","LOW",OK),("MnP1","LOW",OK),("BSFL family","MODERATE",WARN)]):
    yy=250+i*38; d.text((110,yy),f"{c1:14s}",font=font(21,mono=True),fill=TX)
    d.rounded_rectangle([300,yy,430,yy+26],8,fill=cl); d.text((316,yy+2),lv,font=font(17,bold=True),fill=DK)
panel(d,580,190,470,300,"Product safety triage")
wrap_text(d,"Epimer: RETAINS activity — the removal trap.",610,250,22,TX,410)
wrap_text(d,"Anhydro-TC: altered activity + TetX inhibitor.",610,320,22,TX,410)
wrap_text(d,"11α-OH product: unstable → label UNCERTAIN, not 'safe'.",610,390,22,TX,410)
panel(d,1080,190,440,300,"Cassava layer (evidence-bounded)")
wrap_text(d,"Sludge biochar adsorbs TC: 154.45 mg/g (batch).",1110,250,22,TX,380)
wrap_text(d,"Peel biochar: CFX evidence only — labelled as such.",1110,330,22,TX,380)
wrap_text(d,"ADS ORPTION ≠ destruction; spent-material fate modelled.",1110,410,21,WARN,380)
flow(d,80,560,["CASSAVA WASTE","BIOCHAR","PRE-CONCENTRATE","CELL-FREE ENZYME","SAFETY CHECK","END-OF-LIFE"],box_w=215,box_h=70,known=[True,True,True,True,True,False])
d.text((80,690),"Recommended architecture — Option C: adsorption pretreatment + enzymatic transformation.",font=font(26,bold=True),fill=ACC)
d.text((80,738),"Never merely moving pollution from water to solid waste.",font=font(24),fill=DIM)
foot(d,7); S.append(("s07_safety.png",im))

# ---- S8 RESULTS ----
im,d = canvas(); kicker(d,"RESULTS / VALIDATION"); title(d,"Rankings that survive being poked", size=50)
rank=[("TETX2-BT",89.2,ACC),("TETX-BF",84.2,ACC),("LAC-TV",82.7,CY),("MNP-PC",81.2,CY),("TETX3-PA",74.1,GOLD),("BSFL-AA12",22.0,DIM)]
panel(d,80,190,800,520,"Balanced priority ranking")
yy=250
for n,v,c1 in rank:
    d.text((110,yy),f"{n:12s}",font=font(24,mono=True),fill=TX)
    bar(d,300,yy+8,460,v/100,color1=c1,color2=c1); d.text((780,yy),f"{v}",font=font(24,bold=True,mono=True),fill=c1)
    yy+=68
d.text((110,660),"TetX2 leads — with HIGH-CONCERN AMR caveat printed on its own card.",font=font(20),fill=WARN)
stat(d,920,200,"0.955","Kendall's W · 400 weight sets",w=280); stat(d,1230,200,"39/39","automated tests pass",w=280)
panel(d,920,350,590,170,"Ablation — integration matters")
wrap_text(d,"Remove AMR layer → resistance enzymes inflate to ~100/100. Remove product safety → fungal/TetX gap inverts. Effects visible, not hidden.",950,410,22,TX,540)
panel(d,920,540,590,170,"Stance-aware (WHAT-IF)")
wrap_text(d,"AMR-conservative stance: LAC-TV takes #1 (86.0), resistance enzymes demoted to #3–5. Decision support, not arbitrary AI ranking.",950,600,22,TX,540)
foot(d,8); S.append(("s08_results.png",im))

# ---- S9 SCALE / NIGERIA ----
im,d = canvas(); kicker(d,"SCALABILITY / NIGERIAN IMPACT"); title(d,"Frugal by design — because the deployment context demands it", size=40)
y=210
y=bullet(d,80,y,"runs offline on a laptop; venue-proof demo; zero cloud dependency",dim_first="Software:",gap=58)
y=bullet(d,80,y,"feedstock is a free waste stream in the world's largest cassava producer",dim_first="Materials:",gap=58)
y=bullet(d,80,y,"purified cell-free enzyme — no GMO release, no gene transfer",dim_first="Biocatalyst form:",gap=58)
y=bullet(d,80,y,"hospital + farm effluent cartridges → municipal polishing",dim_first="Pilot sites:",gap=58)
path=[("1","COMPUTE (done)"),("2","LAB VALIDATION"),("3","EFFLUENT PILOT"),("4","MUNICIPAL SCALE")]
for i,(n1,t1) in enumerate(path):
    x=80+i*370; col = ACC if i==0 else LINE
    d.rounded_rectangle([x,520,x+330,620],14,fill=PAN if i else (18,60,52),outline=col,width=3)
    d.text((x+20,538),f"PHASE {n1}",font=font(18,bold=True),fill=ACC)
    d.text((x+20,572),t1,font=font(24,bold=True),fill=TX)
d.text((80,680),"Revenue paths: engine licensing · enzyme-cartridge product with local biochar manufacturing · circular-economy grants.",font=font(23),fill=TX)
d.text((80,730),"Costs not quoted on purpose: they require the wet-lab phase the roadmap defines.",font=font(22),fill=GOLD)
foot(d,9); S.append(("s09_scale.png",im))

# ---- S10 FUTURE ----
im,d = canvas(); kicker(d,"FUTURE DEPLOYMENT"); title(d,"From decision engine to verified clean water", size=50)
steps=["express & purify candidate enzyme","tetracycline degradation assay (HPLC)","LC-MS/MS product identification","residual antimicrobial activity assay","toxicity + AMR monitoring","cassava-biochar cartridge pilot"]
for i,s1 in enumerate(steps):
    x=80+(i%3)*480; yy=200+(i//3)*150
    panel(d,x,yy,440,120, f"step {i+1}")
    d.text((x+22,yy+54),s1,font=font(23,bold=(i==0)),fill=TX)
d.text((80,530),"Platform next modules (only where evidence exists):",font=font(25,bold=True),fill=TX)
flow(d,80,580,["DOXY-SHIELD","CIPRO-SHIELD","MYCO-SHIELD (mycotoxins)","PESTI-SHIELD"],box_w=330,box_h=70,known=[True,True,False,False])
d.rounded_rectangle([80,710,1520,820],16,fill=(14,60,52),outline=ACC,width=3)
d.text((140,738),"Removal is not detoxification. TETRA-SHIELD makes remediation safe, explainable, and ready for the bench.",font=font(27,bold=True),fill=TX)
shield(d,120,765,0.7)
foot(d,10); S.append(("s10_future.png",im))

# ---- save PNGs ----
paths=[]
for name,im in S:
    p = OUT/name; im.save(p); paths.append(p)
    print("saved", name)

# ---- PPTX ----
from pptx import Presentation
from pptx.util import Inches as In
prs = Presentation(); prs.slide_width=In(13.333); prs.slide_height=In(7.5)
for p in paths:
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.shapes.add_picture(str(p),0,0,width=prs.slide_width,height=prs.slide_height)
prs.save(ROOT/"results/TETRA-SHIELD_Pitch_Deck.pptx")
print("PPTX saved")

# ---- PDF ----
import reportlab.lib.pagesizes as P
from reportlab.pdfgen import canvas as pdfc
from reportlab.lib.utils import ImageReader
pw,ph = 1600,900  # points==px here for simplicity
c = pdfc.Canvas(str(ROOT/"results/TETRA-SHIELD_Pitch_Deck.pdf"), pagesize=(pw,ph))
for p in paths:
    c.drawImage(ImageReader(str(p)),0,0,width=pw,height=ph)
    c.showPage()
c.save(); print("PDF saved")
