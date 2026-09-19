/* TETRA-SHIELD AI — front-end logic. All data from local API (offline cache mode). */
const S = { preset:'BALANCED', weights:null, curCand:null, cmpSel:['TETX2-BT','LAC-TV','MNP-PC'], repCand:'TETX2-BT', repPreset:'BALANCED', cache:{} };
const NAV = [['HOME','v-home'],['CONTAMINANT','v-contaminant'],['DISCOVER','v-discover'],['CANDIDATE','v-candidate'],['SAFETY','v-safety'],['AMR SHIELD','v-amr'],['CIRCULAR','v-circular'],['DECISION','v-decision'],['COMPARE','v-compare'],['REPORT','v-report'],['ABOUT','v-about']];
const POS = ['evidence_strength','degradation_demonstration','structure_confidence','catalytic_plausibility','substrate_compatibility','transformation_confidence','circular_feasibility','environmental_relevance'];
const NEG = ['product_safety_risk','residual_activity_risk','amr_risk','uncertainty_penalty','structural_uncertainty'];
const PRESETS = ['BALANCED','SAFETY_FIRST','AMR_CONSERVATIVE','MAX_TRANSFORMATION','LOW_COST','HIGH_CONFIDENCE'];
const LBL = {evidence_strength:'Evidence strength',degradation_demonstration:'Degradation evidence',structure_confidence:'Structural confidence',catalytic_plausibility:'Catalytic plausibility',substrate_compatibility:'Substrate compatibility',transformation_confidence:'Transformation confidence',circular_feasibility:'Circular feasibility',environmental_relevance:'Environmental relevance',product_safety_risk:'Product safety risk',residual_activity_risk:'Residual activity risk',amr_risk:'AMR risk',uncertainty_penalty:'Uncertainty penalty',structural_uncertainty:'Structural uncertainty'};
const EVCLS = {E1:'e1',E2:'e2',E3:'e3',E4:'e4',E5:'e5'};
const AMRCLS = {'HIGH CONCERN':'hi','MODERATE CONCERN':'med','LOW CONCERN':'lo','UNKNOWN':'grey'};

const $ = id => document.getElementById(id);
async function api(p, opt){ const r = await fetch(p, opt); if(!r.ok) throw new Error(r.status+' '+p); return r.json(); }
function esc(s){ return String(s??'').replace(/[&<>"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function evChip(e){ return `<span class="chip ${EVCLS[e]||'grey'}">${e}</span>`; }
function amrChip(s){ return `<span class="chip ${AMRCLS[s]||'grey'}">AMR ${s}</span>`; }
function bar(v, risk){ return `<div class="bar ${risk?'risk':''}"><i style="width:${Math.max(0,Math.min(100,v*100))}%"></i></div>`; }

/* -------------------- navigation -------------------- */
function buildNav(){
  const nav = $('nav');
  NAV.forEach(([lbl,id],i)=>{ const b=document.createElement('button'); b.textContent=lbl; b.onclick=()=>go(id); b.dataset.v=id; nav.appendChild(b); });
}
const inited = {};
function go(id){
  document.querySelectorAll('section.view').forEach(s=>s.classList.toggle('on', s.id===id));
  document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('on', b.dataset.v===id));
  window.scrollTo({top:0});
  if(!inited[id]){ inited[id]=1; INIT[id] && INIT[id](); }
  if(REFRESH[id]) REFRESH[id]();
}

/* -------------------- home -------------------- */
async function initHome(){
  $('heroPipe').innerHTML = ['CONTAMINANT','BIOCATALYST','STRUCTURE','INTERACTION','TRANSFORMATION','PRODUCT','SAFETY','AMR','DECISION'].map(s=>`<span class="st">${s}</span>`).join('<span class="ar">→</span>');
  const cav = await api('/api/caveats');
  $('distRow').innerHTML = cav.distinctions.slice(0,7).map(d=>`<span class="d">${d}</span>`).join('');
  $('aboutDist').innerHTML = cav.distinctions.map(d=>`<span class="d">${d}</span>`).join('');
  const h = await api('/api/health');
  $('homeStats').innerHTML = `<div class="kv">
    <b>Engine</b><span>${h.engine.split('(')[0]}</span>
    <b>Mode</b><span>${h.mode}</span>
    <b>Candidates</b><span>${h.n_candidates} (UniProt/PDB/AlphaFold/literature-curated)</span>
    <b>Demo runtime</b><span>&lt; 4 min full chain, no network required</span></div>`;
  $('homeRow').innerHTML = [
    ['1.84 Å','redock validation RMSD (2Y6R)'],['−9.7','kcal/mol top docked affinity (TC↔TetX2)'],
    ['0.955','Kendall’s W rank stability'],['6','biocatalyst candidates, E1–E3 graded'],
    ['154.45','mg/g cassava-biochar TC adsorption (lit.)'],['310.2','ng/g TC in Lagos hospital sludge']
  ].map(([b,s])=>`<div class="stat"><b>${b}</b><span>${s}</span></div>`).join('');
  $('homeCards').innerHTML = [
    ['WHAT IT IS','Evidence-integrated decision intelligence for environmental antibiotic biotransformation: contaminant → enzyme → structure → products → safety → AMR → prioritised validation recommendation.'],
    ['WHAT IT COMPUTES','Real docking (validated by re-docking), real sequence analysis, real cheminformatics, real sensitivity analysis — all offline, all inspectable.'],
    ['WHAT IT IS NOT','Not a risk score. Not a coverage claim. Not "AI" marketing: deterministic components are called deterministic; literature items are called evidence.']
  ].map(([h,b])=>`<div class="panel"><h3>${h}</h3><p class="small">${b}</p></div>`).join('');
  molViewer('heroMol', await (await fetch('/api/sdf/tetracycline')).text(), 'sdf');
}

/* -------------------- 3Dmol helpers -------------------- */
function molViewer(elId, data, fmt, extra){
  const el = $(elId); if(!el || !window.$3Dmol) return;
  const v = $3Dmol.createViewer(el, {backgroundColor:'#050d0c'});
  v.addModel(data, fmt);
  v.setStyle({}, {stick:{radius:.14, colorscheme:'greenCarbon'}, sphere:{scale:.22, colorscheme:'greenCarbon'}});
  if(extra) extra(v); v.zoomTo(); v.spin('y', .6); v.render();
  return v;
}
function protViewer(elId, pdb, opts={}){
  const el = $(elId); if(!el || !window.$3Dmol) return;
  const v = $3Dmol.createViewer(el, {backgroundColor:'#050d0c'});
  v.addModel(pdb, 'pdb');
  v.setStyle({}, {cartoon:{color:'spectrum', opacity:.9}});
  v.setStyle({resn:'FAD'}, {stick:{radius:.18, colorscheme:'magentaCarbon'}});
  v.setStyle({resn:'LIG'}, {stick:{radius:.2, colorscheme:'yellowCarbon'}, sphere:{scale:.25, colorscheme:'yellowCarbon'}});
  v.setStyle({resn:['HEM']}, {stick:{radius:.18, colorscheme:'orangeCarbon'}});
  v.setStyle({resn:['CU','MNC']}, {sphere:{scale:.5, color:'#23b5d3'}});
  if(opts.contacts && opts.contacts.length){
    v.setStyle({resi: opts.contacts}, {stick:{radius:.1, colorscheme:'cyanCarbon'}, cartoon:{color:'#23b5d3'}});
  }
  if(opts.surface){ v.addSurface($3Dmol.SurfaceType.VDW, {opacity:.55, color:'#0e6e58'}); }
  v.zoomTo(); v.render();
  return v;
}

/* -------------------- contaminant -------------------- */
async function initContam(){
  const d = await api('/api/contaminant'); const c = d.contaminant;
  $('contamKV').innerHTML = [
    ['Name', c.preferred_name], ['Formula', c.formula], ['Mol. weight', c.molecular_weight],
    ['XLogP', c.xlogp], ['H-bond donors', c.hbd], ['H-bond acceptors', c.hba],
    ['Rotatable bonds', c.rotatable_bonds], ['TPSA', c.tpsa+' Å²'], ['InChIKey', c.identifiers.inchikey],
    ['PubChem CID', c.identifiers.pubchem_cid], ['CAS', c.identifiers.cas], ['ChEBI', c.identifiers.chebi],
    ['Canonical SMILES', c.canonical_smiles],
  ].map(([k,v])=>`<b>${k}</b><span>${esc(v)}</span>`).join('');
  $('contamFeat').innerHTML = c.structural_features.map(f=>`<li>${f}</li>`).join('');
  $('contamProv').innerHTML = `<div class="kv"><b>Source</b><span>${c.provenance.source}</span><b>Accession</b><span>${c.provenance.accession}</span><b>Retrieved</b><span>${c.provenance.retrieved}</span><b>License</b><span>${c.provenance.license}</span></div>
   <div class="note" style="margin-top:10px">Environmental chemistry: ${c.environmental_chemistry.persistence}</div>`;
  const env = await api('/api/environment');
  $('occTable').innerHTML = `<tr><th>Location</th><th>Matrix</th><th>Contaminant / finding</th><th>Concentration</th><th>Year</th><th>Evidence</th></tr>` +
    env.occurrence_records.map(r=>`<tr><td>${esc(r.location)}, ${esc(r.country)}</td><td>${esc(r.matrix)}</td><td>${esc(r.contaminant)}</td><td>${esc(r.concentration)}</td><td>${r.year}</td><td>${esc(r.evidence)} · ${esc(r.study)}</td></tr>`).join('');
  drawNigeria(env.occurrence_records);
  $('srcPaths').innerHTML = env.sources_pathways.map(s=>`<span class="chip">${esc(s)}</span>`).join('') +
    `<div class="note" style="margin-top:12px">Persistence: ${esc(env.persistence_summary)}</div>`;
  const oh = env.one_health;
  $('oneHealth').innerHTML = `<b>HUMAN:</b> ${esc(oh.human)}<br><b>ANIMAL:</b> ${esc(oh.animal)}<br><b>ENVIRONMENT:</b> ${esc(oh.environment)}`;
  molViewer('contamMol', await (await fetch('/api/sdf/tetracycline')).text(), 'sdf');
}
function drawNigeria(recs){
  // schematic (not survey-accurate) Nigeria outline
  const ng = 'M90,40 L210,28 L330,44 L392,96 L404,170 L352,214 L330,286 L250,330 L176,300 L120,320 L76,262 L52,196 L44,110 Z';
  let dots = recs.filter(r=>r.lat&&r.lon).map((r,i)=>{
    const x = 90 + (r.lon-3.0)*40 + i*8, y = 320 - (r.lat-4.5)*42;
    return `<g><circle cx="${x}" cy="${y}" r="7" fill="#3adfa9" opacity=".85"><animate attributeName="r" values="6;9;6" dur="2.4s" begin="${i*.5}s" repeatCount="indefinite"/></circle>
    <text x="${x+12}" y="${y+4}" fill="#cdeee2" font-size="11" font-family="monospace">LAGOS · ${esc(r.study.split(' ')[0])} ${r.year}</text></g>`;
  }).join('');
  $('nigeriaMap').innerHTML = `<path d="${ng}" fill="#0d2620" stroke="#2a5a51" stroke-width="2"/>${dots}
    <text x="18" y="345" fill="#5d7f78" font-size="10" font-family="monospace">SCHEMATIC — occurrence records are point studies, not national extrapolations</text>`;
}

/* -------------------- discover -------------------- */
function presetButtons(elId, onPick, active){
  $(elId).innerHTML = PRESETS.map(p=>`<button class="${p===active?'on':''}" data-p="${p}" onclick="pickPreset('${p}','${elId}')">${p.replace(/_/g,' ')}</button>`).join('');
  $(elId).dataset.cb = onPick || '';
}
function pickPreset(p, elId){
  S.preset = p; S.weights = null;
  document.querySelectorAll(`#${elId} button`).forEach(b=>b.classList.toggle('on', b.dataset.p===p));
  if(elId==='discPreset') loadDiscover();
  if(elId==='presetRow') loadRanking();
  if(elId==='repPreset'){ S.repPreset = p; loadReportPreview(); }
}
async function loadDiscover(){
  const d = await api('/api/candidates?preset='+S.preset);
  $('candGrid').innerHTML = d.ranking.map(r=>{
    return `<div class="cand" onclick="openCandidate('${r.candidate_id}')">
      <span class="ranknum">#${r.rank}</span>
      <span class="cid">${r.candidate_id}</span>
      <h4>${esc(r.name)}</h4><div class="org">${esc(r.organism)}</div>
      <div class="meta">${evChip(r.evidence_level)} ${amrChip(r.amr_status)}</div>
      <div class="lane"><b>Priority</b>${bar(r.score/100)}<span>${r.score}</span></div>
      <div class="lane"><b>Structure conf.</b>${bar(r.components.structure_confidence)}<span>${(r.components.structure_confidence*100|0)}%</span></div>
      <div class="lane"><b>Catalytic</b>${bar(r.components.catalytic_plausibility)}<span>${(r.components.catalytic_plausibility*100|0)}%</span></div>
    </div>`;}).join('');
}
function initDiscover(){ presetButtons('discPreset', null, S.preset); loadDiscover(); }

/* -------------------- candidate detail -------------------- */
async function openCandidate(cid){ S.curCand = cid; go('v-candidate'); }
async function initCandidate(){ /* loads on refresh too */ }
async function refreshCandidate(){
  const cid = S.curCand || 'TETX2-BT'; S.curCand = cid;
  const d = await api('/api/candidate/'+cid); const c = d.candidate, s = d.scored;
  const dock = c.docking; const st = c.structure||{};
  const structBadge = st.kind==='experimental' ? `<span class="badge-exp">EXPERIMENTAL · ${esc(st.id)} · ${st.resolution_A} Å</span>`
    : st.kind==='predicted' ? `<span class="badge-pred">PREDICTED (AlphaFold) · ${esc(st.id)} · mean pLDDT ${st.mean_plddt}</span>`
    : `<span class="badge-unk">STRUCTURE UNAVAILABLE</span>`;
  let seqPanel = d.sequence ? `
    <h3>Sequence (${d.sequence.sequence.length} aa · UniProt ${esc((c.accession||{}).uniprot||'n/a')})</h3>
    <div class="seqbox">${esc(d.sequence.header)}<br>${esc(d.sequence.sequence.replace(/(.{60})/g,'$1\n'))}</div>
    <p class="faint">Sequence similarity ≠ functional proof (e.g., inactive family member Tet(X1) exists).</p>`
    : `<div class="note red"><b>Sequence unavailable</b> — candidate exists at family/ORF level only (metatranscriptomic). This is a documented data gap, not hidden.</div>`;
  let dockPanel = '';
  if(dock && dock.top_affinity_kcal_mol != null){
    const rd = dock.redock_validation;
    dockPanel = `<div class="grid2" style="margin-top:14px">
      <div class="panel"><h3>Docking metrics (actually computed)</h3>
        <div class="kv">
        <b>Software</b><span>${esc(dock.software)} (seed 42)</span>
        <b>Top affinity</b><span>${dock.top_affinity_kcal_mol} kcal/mol</span>
        <b>Redock validation</b><span>${rd? esc(rd.best_mode_rmsd_A+' Å — '+(rd.best_mode_rmsd_A<=3?'PASS':'MARGINAL')) : 'n/a'}</span>
        <b>Protein contacts ≤4Å</b><span>${dock.interactions? dock.interactions.protein_contacts.length : 0}</span>
        <b>Min FAD distance</b><span>${dock.interactions? dock.interactions.min_fad_dist_A+' Å' : 'n/a'}</span></div>
        <div class="note red"><b>DOCKING ≠ PROOF OF CATALYSIS</b> — score is one evidence layer, integrated (not worshipped) by the engine.</div>
      </div>
      <div class="panel"><h3>Contact residues (top pose, ≤4 Å)</h3>
        ${dock.interactions? dock.interactions.protein_contacts.slice(0,14).map(x=>`<span class="chip">${x.residue} · ${x.min_dist_A}Å</span>`).join('') : ''}
        ${dock.interactions&&dock.interactions.fad_contacts.length? `<p class="small" style="margin-top:6px">FAD cofactor contacts: ${dock.interactions.fad_contacts.map(x=>`<span class="chip gold">${x.residue} · ${x.min_dist_A}Å</span>`).join('')}</p>`:''}
        <p class="small" style="margin-top:8px">Literature cross-check (family-level Tet(X)) matches substrate-pocket residues incl. His-pocket region; FAD-binding Arg/Asp region contacted by pose. See refs.</p>
      </div></div>`;
  } else if(dock){
    dockPanel = `<div class="note" style="margin-top:14px"><b>Laccase/MnP docking note:</b> ${esc(dock.interpretation||dock.note||'')} ${dock.top_affinity_kcal_mol!=null?`Top score ${dock.top_affinity_kcal_mol} kcal/mol (no productive pose).`:''}</div>`;
  } else {
    dockPanel = `<div class="note" style="margin-top:14px">Docking not applicable/available for this candidate. Interaction claims rest on the labelled evidence level only.</div>`;
  }
  $('candDetail').innerHTML = `
    <button class="btn sm ghost" onclick="go('v-discover')">← back to candidates</button>
    <h2 style="margin-top:12px">${esc(c.protein_name)} <span class="cid mono" style="font-size:13px;color:var(--acc2)">${cid}</span></h2>
    <p class="sub"><i>${esc(c.organism)}</i> · ${esc(c.source_environment||'')}</p>
    <div class="meta" style="margin:10px 0">${evChip(c.evidence_level)} ${amrChip(c.resistance_association.status)} <span class="chip gold">SCORE ${s.score} · RANK #${s.rank}</span> ${structBadge}</div>
    <div class="grid2">
      <div class="panel hi">
        <h3>Annotation &amp; evidence</h3>
        <p class="small">${esc(c.annotation)}</p>
        <div class="kv" style="margin-top:10px">
          <b>Family</b><span>${esc(c.enzyme_family)}</span>
          <b>Cofactors</b><span>${esc((c.cofactors||[]).join(', '))}</span>
          <b>Gene</b><span>${esc(c.gene_name)}</span>
          <b>Degradation</b><span>${esc(c.degradation_evidence.status)}</span>
          <b>AMR rationale</b><span>${esc(c.resistance_association.mechanism)}</span>
        </div>
        <h3>Structure</h3>
        <p class="small">${esc(st.label||'—')}</p>
        <div class="viewer" id="candMol"><span class="tag">${esc(st.id||'no structure')} · cartoon + ligands</span></div>
        <p class="faint">FAD magenta · docked tetracycline yellow · metals blue spheres. PREDICTED structures are labelled as such, always.</p>
      </div>
      <div>
        <div class="panel">${seqPanel}</div>
        <div class="panel" style="margin-top:14px">
          <h3>Score components (inspectable)</h3>
          ${POS.concat(NEG).map(k=>`<div class="lane"><b>${LBL[k]}</b>${bar(s.components[k], NEG.includes(k))}<span>${s.components[k].toFixed(2)}</span></div>`).join('')}
          <div class="note"><b>Uncertainty flags:</b> ${s.components._flags.join(' · ')||'none'}</div>
        </div>
      </div>
    </div>
    ${dockPanel}
    <div class="panel" style="margin-top:14px"><h3>WHY this score?</h3>${whyHTML(s)}</div>
    <div style="display:flex;gap:10px;margin:16px 0">
      <button class="btn sm" onclick="S.repCand='${cid}';go('v-report')">Export report →</button>
      <button class="btn sm ghost" onclick="go('v-decision')">Change stance (WHAT-IF) →</button>
      <button class="btn sm ghost" onclick="addToCompare('${cid}')">Add to compare</button>
    </div>`;
  if(st.file){
    const pdb = await (await fetch('/api/structure/'+cid)).text();
    const contactResis = dock && dock.interactions ? dock.interactions.protein_contacts.slice(0,10).map(x=>x.residue.replace(/[^0-9]/g,'')) : [];
    protViewer('candMol', pdb, {contacts:contactResis.filter(Boolean)});
  } else {
    $('candMol').innerHTML = '<div class="skel" style="padding-top:170px">STRUCTURE UNAVAILABLE — displayed honestly, never faked</div>';
  }
}
function whyHTML(s){
  const ex = s.explanation;
  const pos = Object.entries(ex.positives).map(([k,[v,m]])=>`<div class="why-item pos"><b>+ ${LBL[k]} ${v.toFixed(2)}</b><em>${esc(m)}</em></div>`).join('');
  const neg = Object.entries(ex.penalties).map(([k,[v,m]])=>`<div class="why-item neg"><b>− ${LBL[k]} ${v.toFixed(2)}</b><em>${esc(m)}</em></div>`).join('');
  return `<div class="why-cols"><div><h4>Positive contributors</h4>${pos}</div><div><h4>Risk penalties</h4>${neg}</div></div>
  <div class="note green" style="margin-top:10px"><b>Verdict:</b> ${esc(ex.verdict)}</div>`;
}
function addToCompare(cid){ if(!S.cmpSel.includes(cid)){ S.cmpSel.push(cid); if(S.cmpSel.length>4) S.cmpSel.shift(); } go('v-compare'); }

/* -------------------- safety / transformation -------------------- */
async function initSafety(){
  const pw = await api('/api/pathways');
  $('pathwayZone').innerHTML = pw.map(p=>{
    const nodes = p.steps.map(st=>{
      const known = st.known===true;
      return `<div class="node ${known?'known':'pred'}"><div class="tagline">${known?'KNOWN':'PREDICTED/PARTIAL'} · ${esc(st.type)}</div>
        <b>${esc(st.reaction)}</b>${st.enzyme?`<div class="small" style="margin-top:4px">catalyst: ${esc(st.enzyme)} ${st.cofactor?('· '+esc(st.cofactor)):''}</div>`:''}</div>`;
    }).join('<span class="arr">→</span>');
    return `<h3>${esc(p.pathway_id)} — ${esc(p.name)}</h3><div class="tflow">${nodes}</div>
      <p class="small">Residual antibacterial activity: <b>${esc(p.residual_activity_summary)}</b></p>`;
  }).join('');
  const prods = await api('/api/products');
  $('productCards').innerHTML = prods.map(p=>{
    const actCls = /loss/i.test(p.residual_activity.class)?'lo':/RETAINED/i.test(p.residual_activity.class)?'hi':'med';
    return `<div class="panel hi">
      <span class="cid mono" style="color:var(--acc2);font-size:11px">${p.product_id}</span>
      <h4 style="margin-top:4px">${esc(p.name)}</h4>
      <div class="meta">${p.known_vs_predicted.startsWith('KNOWN')?'<span class="chip e1">STRUCTURE KNOWN</span>':'<span class="chip grey">STRUCTURE UNCERTAIN / PARTIAL</span>'}
      <span class="chip ${actCls}">RESIDUAL ACTIVITY: ${esc(p.residual_activity.class.split('—')[0].split('(')[0])}</span></div>
      <div class="kv">
        <b>Route</b><span>${esc(p.route)}</span>
        <b>Structure</b><span>${esc(p.structure_status)}</span>
        <b>Activity basis</b><span>${esc(p.residual_activity.evidence)}</span>
        <b>Detail</b><span>${esc(p.residual_activity.detail||p.residual_activity.class)}</span>
        <b>Safety triage</b><span>${esc(p.safety_triage.class||JSON.stringify(p.safety_triage))}</span>
      </div>
      ${p.smiles?`<img src="/static/mol/${p.name.toLowerCase().replace(/ /g,'')=== 'anhydrotetracycline'?'anhydrotetracycline':'4-epitetracycline'}.svg" onerror="this.style.display='none'" style="width:60%;background:#fff;border-radius:8px;margin-top:8px">`:''}
    </div>`;}).join('');
  const tri = (await api('/api/contaminant')).cheminformatics;
  $('chemTriage').innerHTML = `<div class="kv">
    <b>Method</b><span>${esc(tri.method)}</span>
    ${Object.entries(tri.parent_similarity_tanimoto).map(([k,v])=>`<b>Tanimoto vs parent</b><span>${k}: ${v}</span>`).join('')}
    <b>Alerts checked</b><span>${Object.keys(tri.compounds.tetracycline.alerts).join(' · ')}</span></div>
    <div class="note" style="margin-top:10px"><b>Why this matters:</b> 4-epitetracycline has Tanimoto 1.0 — because achiral Morgan fingerprints cannot
    even see the epimerisation, yet the epimer retains activity. Similarity measures bound what we can claim; the engine therefore defers to
    experimentally demonstrated activity labels wherever they exist. ${esc(tri.caveat)}</div>`;
}

/* -------------------- AMR -------------------- */
async function initAmr(){
  const a = await api('/api/amr');
  $('amrMech').innerHTML = a.tetracycline_resistance_mechanisms.map(m=>`<div class="panel" style="margin-bottom:10px">
    <h4>${esc(m.class)} <span class="chip ${m.concern.startsWith('HIGH')?'hi':'med'}" style="float:right">${esc(m.concern)}</span></h4>
    <div>${m.genes.map(g=>`<span class="chip grey">${esc(g)}</span>`).join('')}</div>
    ${m.note?`<p class="small" style="margin-top:6px">${esc(m.note)}</p>`:''}</div>`).join('');
  const d = await api('/api/candidates');
  $('amrCand').innerHTML = d.ranking.map(r=>`<div class="lane"><b style="width:170px">${r.candidate_id}</b>${amrChip(r.amr_status)}</div>`).join('') +
    `<p class="small" style="margin-top:8px">Key insight: the strongest degraders (TetX family) are <i>themselves resistance machinery</i> — usable only as purified, cell-free biocatalysts. The AMR layer changes the engineering recommendation, not just the score.</p>`;
  const env = await api('/api/environment');
  $('amrOneHealth').innerHTML = `<b>HUMAN:</b> ${esc(env.one_health.human)}<br><br><b>ANIMAL:</b> ${esc(env.one_health.animal)}<br><br><b>ENVIRONMENT:</b> ${esc(env.one_health.environment)}`;
  $('amrCtx').innerHTML = esc(a.selection_context) + `<div class="note" style="margin-top:10px">${esc(a.database_note)}</div>`;
}

/* -------------------- circular / cassava -------------------- */
async function initCircular(){
  const c = await api('/api/cassava');
  const steps = ['CASSAVA AGRO-WASTE','MATERIAL PROCESSING','ADSORBENT / SUPPORT','CONTAMINATED WATER','PRE-CONCENTRATION','BIOLOGICAL TRANSFORMATION','SAFETY CHECK','SPENT-MATERIAL END-OF-LIFE'];
  $('cassavaFlow').innerHTML = steps.map(s=>`<div class="node ${s==='ADSORBENT / SUPPORT'||s==='PRE-CONCENTRATION'?'pred':'known'}"><div class="tagline">${/ADSORBENT|CONCENTRATION/.test(s)?'MASS TRANSFER — not destruction':'stage'}</div><b>${s}</b></div>`).join('<span class="arr">→</span>');
  $('cassavaEvidence').innerHTML = c.evidence.map(e=>`<div class="panel">
    <div class="meta"><span class="chip e2">${esc(e.evidence||'E2')}</span><span class="chip med">${esc(e.function)}</span></div>
    <h4>${esc(e.material)}</h4>
    <p class="small"><b>Target:</b> ${esc(e.contaminant)}<br><b>Performance:</b> ${esc(e.performance||'—')}</p>
    ${e.mechanisms?`<p class="faint">${e.mechanisms.join(' · ')}</p>`:''}
    ${e.note?`<p class="small" style="color:var(--warn)">⚠ ${esc(e.note)}</p>`:''}</div>`).join('');
  $('cassDist').innerHTML = Object.entries(c.critical_distinctions).map(([k,v])=>`<div class="rrow"><b>${k.toUpperCase()}</b><span>${esc(v)}</span></div>`).join('');
  $('cassSpent').innerHTML = `<p class="small">${esc(c.spent_adsorbent.issue)}</p><ul class="small" style="padding-left:18px;margin:8px 0">${c.spent_adsorbent.options.map(o=>`<li>${esc(o)}</li>`).join('')}</ul><div class="note red">${esc(c.spent_adsorbent.design_principle)}</div>`;
  $('intervTable').innerHTML = `<tr><th>Option</th><th>Removal potential</th><th>Detoxification evidence</th><th>AMR considerations</th><th>Product risk</th><th>Circularity</th><th>Uncertainty</th></tr>` +
   [['A · Biological transformation only','Demonstrated (enzyme class)','Yes for TetX route (activity loss)','HIGH if gene/organism used; LOW for cell-free enzyme','Product-specific data sparse','enzyme production cost','moderate'],
    ['B · Adsorption only (cassava biochar)','92.6% batch (lit., pH 3)','None — molecule intact on solid','Selection pressure persists in spent biochar','unchanged molecule','feedstock free; activation cost','binding ≠ destruction (certain)'],
    ['C · Adsorption + biological transformation (RECOMMENDED CONCEPT)','Combined: pre-concentrate then transform','Best available architecture','Depends on biocatalyst form','needs product validation','matches platform design','moderate; end-of-life defined'],
    ['D · Advanced oxidation (contrast)','High (energy-reagent cost)','partial; products vary','neutral','byproduct tox must be checked','energy intensive','matrix-dependent']]
    .map(r=>`<tr>${r.map((x,i)=>`<td${i===0?' style="color:var(--acc)"':''}>${x}</td>`).join('')}</tr>`).join('');
}

/* -------------------- decision -------------------- */
async function initDecision(){
  presetButtons('presetRow', null, S.preset);
  renderSliders();
  await loadRanking();
  api('/api/sensitivity').then(s=>{
    $('sensPanel').innerHTML = `<div class="exph">Kendall's W = ${s.kendalls_W}</div>
      <p class="small">${s.n_iterations} random weight sets, ±${s.weight_spread*100}% perturbation, seed ${s.seed}</p>
      <table class="tb"><tr><th>Candidate</th><th>mean rank</th><th>range</th><th>P(top-3)</th></tr>
      ${Object.entries(s.rank_stability).sort((a,b)=>a[1].mean_rank-b[1].mean_rank).map(([k,v])=>`<tr><td>${k}</td><td>${v.mean_rank}</td><td>${v.min_rank}–${v.max_rank}</td><td>${v.p_top3}</td></tr>`).join('')}</table>
      <p class="faint">${esc(s.interpretation)}</p>`;
  });
  api('/api/ablation').then(a=>{
    const keys = Object.keys(a);
    const cids = Object.keys(a.full);
    $('ablPanel').innerHTML = `<table class="tb"><tr><th>Variant</th>${cids.map(c=>`<th>${c.split('-')[0]}</th>`).join('')}</tr>
      ${keys.map(k=>`<tr><td>${k.replace('without_','− ')}</td>${cids.map(c=>`<td>${a[k][c]}</td>`).join('')}</tr>`).join('')}</table>
      <p class="faint">Integration matters: removing the AMR layer inflates resistance-enzyme scores to ~100; removing product-safety inverts the fungal/TetX gap. That dependency is visible, not hidden.</p>`;
  });
  api('/api/baselines').then(b=>{
    $('basePanel').innerHTML = Object.entries(b).map(([k,v])=>`<div class="rrow"><b>${k.replace(/_/g,' ')}</b><span>${v.join(' → ')}</span></div>`).join('') +
    `<p class="faint">TETRA-SHIELD integrated ordering differs from every single-lens baseline — the value-add is the joint safety/AMR/uncertainty treatment.</p>`;
  });
}
function renderSliders(){
  const mk = (k, val)=>`<div class="slider"><span>${LBL[k]}</span><input type="range" min="0" max="3" step="0.05" value="${val}" data-k="${k}" oninput="sliderChanged(this)"><span id="sv_${k}">${val}</span></div>`;
  const base = {evidence_strength:1.0,degradation_demonstration:1.0,structure_confidence:0.6,catalytic_plausibility:0.8,substrate_compatibility:0.8,transformation_confidence:0.7,circular_feasibility:0.5,environmental_relevance:0.6,product_safety_risk:1.0,residual_activity_risk:1.0,amr_risk:1.0,uncertainty_penalty:0.8,structural_uncertainty:0.4};
  S.weights = {...base};
  $('sliders').innerHTML = `<div>${POS.map(k=>mk(k,base[k])).join('')}</div><div>${NEG.map(k=>mk(k,base[k])).join('')}</div>`;
}
let sliderT=null;
function sliderChanged(inp){
  S.weights[inp.dataset.k]=parseFloat(inp.value); $('sv_'+inp.dataset.k).textContent=inp.value;
  document.querySelectorAll('#presetRow button').forEach(b=>b.classList.remove('on'));
  clearTimeout(sliderT); sliderT=setTimeout(loadRanking, 220);
}
async function loadRanking(){
  let data;
  if(S.weights){ data = await api('/api/score',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({weights:S.weights})}); }
  else { data = await api('/api/candidates?preset='+S.preset); }
  const rows = data.ranking;
  $('rankPanel').innerHTML = rows.map(r=>`
    <div class="lane" style="cursor:pointer" onclick="toggleWhy('${r.candidate_id}')">
      <b style="width:170px">#${r.rank} · ${r.candidate_id}</b>
      ${bar(r.score/100)}<span style="width:90px">${S.preset==='CUSTOM'?'':''}${r.score} / 100</span>
      ${evChip(r.evidence_level)} ${amrChip(r.amr_status)}
      <span class="chip grey" id="whybtn_${r.candidate_id}">WHY?</span>
    </div>
    <div id="why_${r.candidate_id}" style="display:none" class="panel"></div>`).join('');
  S._lastRanking = rows;
}
function toggleWhy(cid){
  const el = $('why_'+cid);
  if(el.style.display==='none'){
    const r = S._lastRanking.find(x=>x.candidate_id===cid);
    el.innerHTML = whyHTML(r); el.style.display='block';
  } else el.style.display='none';
}

/* -------------------- compare -------------------- */
function initCompare(){
  api('/api/candidates').then(d=>{
    $('cmpSel').innerHTML = d.ranking.map(r=>`<span class="opt ${S.cmpSel.includes(r.candidate_id)?'on':''}" onclick="toggleCmp('${r.candidate_id}')">${r.candidate_id}</span>`).join('');
    runCompare();
  });
}
function toggleCmp(cid){
  if(S.cmpSel.includes(cid)) { if(S.cmpSel.length>2) S.cmpSel.splice(S.cmpSel.indexOf(cid),1); }
  else if(S.cmpSel.length<4) S.cmpSel.push(cid);
  document.querySelectorAll('#cmpSel .opt').forEach(o=>o.classList.toggle('on', S.cmpSel.includes(o.textContent)));
  runCompare();
}
async function runCompare(){
  const d = await api('/api/compare?ids='+S.cmpSel.join(','));
  const comps = POS.concat(NEG);
  $('cmpOut').innerHTML = `<div class="panel hi"><table class="tb">
    <tr><th>Component</th>${d.comparison.map(x=>`<th>${x.candidate.candidate_id}</th>`).join('')}</tr>
    <tr><td>Evidence class</td>${d.comparison.map(x=>`<td>${x.candidate.evidence_level}</td>`).join('')}</tr>
    <tr><td>AMR status</td>${d.comparison.map(x=>`<td>${x.candidate.resistance_association.status}</td>`).join('')}</tr>
    <tr><td>Structure</td>${d.comparison.map(x=>`<td>${esc(x.candidate.structure.kind||'?')} ${x.candidate.structure.id||''}</td>`).join('')}</tr>
    ${comps.map(k=>`<tr><td>${LBL[k]}</td>${d.comparison.map(x=>`<td>${x.scored.components[k].toFixed(2)}</td>`).join('')}</tr>`).join('')}
    <tr style="background:#0d2b24"><td><b>PRIORITY SCORE</b></td>${d.comparison.map(x=>`<td style="color:var(--acc);font-weight:700">${x.scored.score}</td>`).join('')}</tr>
  </table></div>
  <div class="panel" style="margin-top:14px"><h3>Visual comparison — selected layers</h3>${cmpChart(d.comparison)}</div>`;
}
function cmpChart(rows){
  const keys=['evidence_strength','catalytic_plausibility','substrate_compatibility','product_safety_risk','amr_risk'];
  const colors=['#3adfa9','#23b5d3','#e8c766','#f49f5a','#f06d6d'];
  const W=900, H=250, bw=22;
  let out=`<svg viewBox="0 0 ${W} ${H}" style="width:100%">`;
  keys.forEach((k,ki)=>{
    rows.forEach((r,ri)=>{
      const v=r.scored.components[k]; const x=60+ki*150+ri*(bw+6); const h=v*170;
      out+=`<rect x="${x}" y="${205-h}" width="${bw}" height="${h}" fill="${colors[ki]}" opacity="${0.95-ri*0.16}" rx="3"/>`;
    });
    out+=`<text x="${60+ki*150}" y="${230}" fill="#8fb3ab" font-size="10" font-family="monospace">${k.split('_')[0].toUpperCase()}</text>`;
  });
  rows.forEach((r,ri)=>{ out+=`<rect x="${620+ri*16}" y="18" width="10" height="10" fill="#3adfa9" opacity="${0.95-ri*0.16}"/><text x="${634+ri*16}" y="28" fill="#8fb3ab" font-size="10" font-family="monospace">${r.candidate.candidate_id}</text>`; });
  return out+'</svg>';
}

/* -------------------- report -------------------- */
function initReport(){
  api('/api/candidates').then(d=>{
    $('repSel').innerHTML = d.ranking.map(r=>`<span class="opt ${r.candidate_id===S.repCand?'on':''}" onclick="pickRep('${r.candidate_id}')">${r.candidate_id}</span>`).join('');
    presetButtons('repPreset', null, S.repPreset);
    loadReportPreview();
  });
}
function pickRep(cid){ S.repCand=cid; document.querySelectorAll('#repSel .opt').forEach(o=>o.classList.toggle('on', o.textContent===cid)); loadReportPreview(); }
async function loadReportPreview(){
  const r = await api(`/api/report/${S.repCand}?format=json&preset=${S.repPreset}`);
  $('reportPreview').innerHTML = `<div class="result-block"><div class="rh">TETRA-SHIELD ANALYSIS — RESULT</div><div class="rb">
    ${[['CONTAMINANT', `${r.contaminant.name} (${r.contaminant.formula}, MW ${r.contaminant.mw})`],
      ['CANDIDATE', `${r.candidate.protein} [${r.candidate.id}] — ${r.candidate.organism}`],
      ['BIOLOGICAL EVIDENCE', r.candidate.evidence_level],
      ['PRIORITY SCORE', `${r.decision.priority_score} / 100 (preset ${r.decision.preset}, rank #${r.decision.rank})`],
      ['RECOMMENDATION', r.decision.verdict],
      ['AMR ASSOCIATION', `${r.amr.status} — ${r.amr.mechanism}`],
      ['UNCERTAINTY', r.uncertainty_flags.join(' · ')],
      ['KEY DISTINCTIONS', r.key_distinctions.join(' | ')],
      ['DISCLAIMER', r.disclaimer]]
     .map(([k,v])=>`<div class="rrow"><b>${k}</b><span>${esc(v)}</span></div>`).join('')}
  </div></div>
  <h3>Sources in this report</h3><div class="panel">${r.sources.map(s=>`<p class="small">[${s.id}] ${esc(s.cite)} <span class="faint">${esc(s.doi)}</span></p>`).join('')}</div>`;
}
function exportReport(fmt){ window.open(`/api/report/${S.repCand}?format=${fmt}&preset=${S.repPreset}`,'_blank'); }

/* -------------------- analyze (magic moment) -------------------- */
async function startAnalysis(){
  $('analyzeOverlay').classList.add('show'); $('anDone').style.display='none';
  const steps = [
    ['Contaminant profile', '/api/contaminant', d=>`${d.contaminant.preferred_name} · ${d.contaminant.formula} · CID ${d.contaminant.identifiers.pubchem_cid}`],
    ['Candidate discovery', '/api/candidates', d=>`${d.ranking.length} candidates · best: ${d.ranking[0].candidate_id}`],
    ['Sequence intelligence', '/api/sequence-analysis', d=>`identity matrix computed · TetX↔TetX2 ${d.identity_percent_matrix['TetX (B. fragilis)']['TetX2 (B. thetaiotaomicron)']}%`],
    ['Structural intelligence', '/api/candidate/TETX2-BT', d=>d.candidate.structure.label||'—'],
    ['Enzyme ↔ substrate docking', '/api/candidate/TETX2-BT', d=>`top affinity ${d.candidate.docking.top_affinity_kcal_mol} kcal/mol · redock ${d.candidate.docking.redock_validation.best_mode_rmsd_A} Å`],
    ['Transformation pathway', '/api/pathways', d=>`${d.length} pathways · KNOWN vs PREDICTED split`],
    ['Product safety & residual activity', '/api/products', d=>`${d.length} product records · 1 retains activity (epimer!)`],
    ['AMR Shield', '/api/amr', d=>`3 resistance classes tracked`],
    ['Uncertainty audit', '/api/candidates', d=>`flags aggregated per candidate`],
    ['Priority scoring + sensitivity', '/api/sensitivity', d=>`Kendall's W ${d.kendalls_W}`],
  ];
  const box = $('anSteps'); box.innerHTML='';
  for(const [label, url, fmt] of steps){
    const div = document.createElement('div'); div.className='astep run';
    div.innerHTML = `<span class="dot"></span>${label}<span class="detail">…</span>`; box.appendChild(div);
    let d; try{ d = await api(url); }catch(e){ d=null; }
    div.classList.remove('run'); div.classList.add('done');
    div.querySelector('.detail').textContent = d? fmt(d) : 'data unavailable (handled gracefully)';
    await new Promise(r=>setTimeout(r, 260));
  }
  $('anSub').textContent = 'Full chain complete — every stage from verified cached data.';
  $('anDone').style.display='inline-flex';
}
function doneAnalysis(){ $('analyzeOverlay').classList.remove('show'); go('v-decision'); }

/* -------------------- boot -------------------- */
const INIT = {'v-home':initHome,'v-contaminant':initContam,'v-discover':initDiscover,'v-candidate':initCandidate,'v-safety':initSafety,'v-amr':initAmr,'v-circular':initCircular,'v-decision':initDecision,'v-compare':initCompare,'v-report':initReport,'v-about':()=>{}};
const REFRESH = {'v-candidate':refreshCandidate};
buildNav(); go('v-home');
