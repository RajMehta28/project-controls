"""'Start Here' pitch: a swipeable mini-deck shown first in each dashboard.
inject(html, role) fills the <!--PITCH-->, /*PITCHCSS*/ and /*PITCHJS*/ markers."""

SITE = "https://rajmehta28.github.io/project-controls/"

PROFILE = """<div class="pslide"><p class="p-eb">Who I am</p><h2 class="p-h">Analytics first, aimed at project money and time</h2>
<div class="p-stats">
<div class="p-stat"><p class="p-num">25+</p><p class="p-cap">KPIs tracked as co-founder and analytics head, City &amp; Talent; automated reporting cut manual effort 40%</p></div>
<div class="p-stat"><p class="p-num">$75–120K</p><p class="p-cap">Estimated annual savings from my cost models, Lean Six Sigma at Tessy Plastics</p></div>
<div class="p-stat"><p class="p-num">$105M</p><p class="p-cap">Light-rail cost simulation (Siemens, Forage): forecast EAC three ways, recommended a $112M re-baseline</p></div>
</div></div>"""

GAP = """<div class="pslide or"><p class="p-eb">The gap, and what I did about it</p><h2 class="p-h p-big">No access to {tool} yet. So I built my own.</h2>
<p class="p-sub">A simulated $120M site infrastructure scope: 6 work packages, 16 scheduled activities, PostgreSQL views and Power BI measures. This dashboard is the result.</p></div>"""

ROLES = {
 "cost": dict(
  role="Cost Engineer", req="294908", tool="Ecosys",
  promise="I turn cost data into decisions a project team can act on.",
  found_title="Three cost studies, each ending in a decision",
  found=[("$1.91M","Overtime bought time nobody used","Piers finished early; the next trade couldn’t use it."),
         ("$379K","A forecast running too low","Utilities is late, so CPI × SPI fits better."),
         ("$2.4M","Not an overrun: client scope","Recover by change order; real exposure $0.89M.")],
  fit=[("Cost studies with historical data and statistics","Overtime vs CPI (correlation −0.99), priced at $1.91M"),
       ("Review cost trends","Trend log split into client-recoverable and internal"),
       ("Estimating, analysis and control","Three forecast methods compared per package"),
       ("Accurate, consistent cost reports","Every KPI checked twice, in SQL and Python"),
       ("Summarize and recommend cost containment","Each study ends in a dollar impact and a decision"),
       ("Ecosys and Bechtel cost systems","Not yet; I built the same structure to learn fast")],
  explore=("studies","Open the cost studies"), other=(SITE+"planner-dashboard/","See my schedule view")),
 "planner": dict(
  role="Project Controls Planner", req="301200", tool="Primavera P6",
  promise="I find what drives the finish date, and how to win the time back.",
  found_title="What drives the finish, and how to recover it",
  found=[("+8 days","Late, driven by the utilities","Utility runs → testing → turnover."),
         ("8 days","Recovered on one activity","Brings back the Dec&#160;31 baseline."),
         ("Jan 21","80% confident finish","2,000 Monte Carlo runs."),
         ("3","Constraints on the critical path","Flagged in the 3-week look-ahead.")],
  fit=[("Critical and near-critical path analysis","Critical path, float and near-critical flags"),
       ("Schedule recovery plans","What-if: 8 days on one activity restores the baseline"),
       ("2 to 4 week look-ahead schedules","3-week look-ahead with a constraint log tied to risks"),
       ("Proficiency in Power BI","DAX and Power Query; 25+ KPI dashboards built"),
       ("Schedule metrics, presented clearly","SPI, CPLI and BEI, each insight ending in a recommendation"),
       ("Proficiency in Primavera P6","In training now; rebuilding this schedule in P6 next")],
  explore=("insights","Open the planner insights"), other=(SITE+"cost-dashboard/","See my cost view")),
}

CSS = """
.pitch-wrap{position:relative}
.ptrack{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;gap:16px;scrollbar-width:none;-webkit-overflow-scrolling:touch;border-radius:16px}
.ptrack::-webkit-scrollbar{display:none}
.pslide{--po:#B04A18;flex:0 0 100%;scroll-snap-align:start;min-height:470px;box-sizing:border-box;border-radius:16px;padding:clamp(24px,4vw,52px);display:flex;flex-direction:column;justify-content:center;gap:18px;background:var(--panel);border:1px solid var(--line);color:var(--ink)}
.pslide.dk{background:#13202B;border-color:#13202B;color:#F5F3EE;--po:#E9895A}
.pslide.or{background:#B04A18;border-color:#B04A18;color:#FCFBF8}
.pslide p{margin:0}
.p-eb{font-size:12px;letter-spacing:.16em;text-transform:uppercase;font-weight:600;color:var(--po)}
.pslide.or .p-eb{color:#FCEDE4}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .pslide:not(.or){--po:#E9895A}}
:root[data-theme="dark"] .pslide:not(.or){--po:#E9895A}
.p-h{font-family:"IBM Plex Sans",system-ui,sans-serif;font-weight:700;font-size:clamp(26px,4vw,46px);line-height:1.08;letter-spacing:-.02em;margin:0;max-width:960px}
.p-h.p-big{font-size:clamp(32px,5.4vw,64px)}
.p-sub{font-size:clamp(15px,1.7vw,19px);line-height:1.5;color:var(--mute);max-width:780px}
.pslide.dk .p-sub{color:#C9D3DA}.pslide.or .p-sub{color:#FCEDE4}
.p-rule{width:72px;height:6px;border-radius:3px;background:var(--po)}
.p-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.p-stat{border:1px solid var(--line);border-radius:12px;padding:16px 18px;display:flex;flex-direction:column;gap:8px}
.p-num{font-family:"IBM Plex Mono",monospace;font-weight:500;font-size:clamp(24px,3vw,36px);line-height:1;color:var(--po)}
.p-cap{font-size:14px;line-height:1.45;color:var(--mute)}.p-stat b{color:var(--ink);font-size:15px}
.p-fit{width:100%;border-collapse:collapse;font-size:14.5px}.p-fit th{font-size:12px;letter-spacing:.06em;text-transform:uppercase}.p-fit td{vertical-align:top}
.p-fit td:first-child{color:var(--mute);width:42%}
.p-ctas{display:flex;flex-wrap:wrap;gap:10px}
.p-btn{display:inline-block;padding:11px 18px;border-radius:8px;font-weight:600;text-decoration:none;font-size:15px;border:1px solid #F5F3EE;color:#F5F3EE}
.p-btn.pri{background:#E9895A;border-color:#E9895A;color:#13202B}
.p-contact{font-size:13.5px;color:#C9D3DA}
.pnav{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:12px}
.pdots{display:flex;gap:8px}.pdots button{width:10px;height:10px;padding:0;border-radius:50%;border:0;background:var(--line);cursor:pointer}
.pdots button.on{background:var(--accent);width:26px;border-radius:5px}
.parr{display:flex;gap:8px;align-items:center}.parr span{font-size:13px;color:var(--mute);font-family:"IBM Plex Mono",monospace;min-width:44px;text-align:center}
.parr button{width:40px;height:40px;border-radius:50%;font-size:18px;line-height:1;padding:0}
.phint{font-size:12.5px;color:var(--mute)}
@media(max-width:560px){.p-fit td:first-child{width:46%}.pslide{min-height:520px}.phint{display:none}}
"""

JS = """
(function(){const t=document.getElementById('ptrack');if(!t)return;const S=[...t.children],dots=document.getElementById('pdots'),cnt=document.getElementById('pcnt');
 dots.innerHTML=S.map((_,i)=>`<button aria-label="Slide ${i+1}"></button>`).join('');const D=[...dots.children];
 const cur=()=>Math.round(t.scrollLeft/(t.clientWidth+16));
 const go=i=>{i=Math.max(0,Math.min(S.length-1,i));t.scrollTo({left:i*(t.clientWidth+16),behavior:'smooth'})};
 const upd=()=>{const i=cur();D.forEach((d,k)=>d.classList.toggle('on',k===i));cnt.textContent=(i+1)+' / '+S.length};
 t.addEventListener('scroll',()=>{clearTimeout(t._u);t._u=setTimeout(upd,60)});D.forEach((d,k)=>d.onclick=()=>go(k));
 document.getElementById('pprev').onclick=()=>go(cur()-1);document.getElementById('pnext').onclick=()=>go(cur()+1);
 addEventListener('keydown',e=>{if(!document.getElementById('pitch').classList.contains('on'))return;if(e.key==='ArrowRight')go(cur()+1);if(e.key==='ArrowLeft')go(cur()-1)});
 document.querySelectorAll('[data-tab]').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();const a=document.querySelector('nav a[href="#'+b.dataset.tab+'"]');if(a)a.click();scrollTo(0,0)}));
 upd()})();
"""

def section(role):
    r = ROLES[role]
    stats = "".join(f'<div class="p-stat"><p class="p-num">{n}</p><p class="p-cap"><b>{h}</b><br>{s}</p></div>' for n, h, s in r["found"])
    fit = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in r["fit"])
    slides = [
     f"""<div class="pslide dk"><p class="p-eb">{r['role']} · Req {r['req']} · Clay, NY</p><h2 class="p-h p-big">Raj Mehta</h2><div class="p-rule"></div>
<p class="p-sub" style="font-size:clamp(18px,2.2vw,26px);color:#F5F3EE">{r['promise']}</p><p class="p-sub">MS Business Analytics, Syracuse University (2026). Swipe or use the arrows: 6 short slides, then the dashboard.</p></div>""",
     PROFILE,
     GAP.format(tool=r["tool"]),
     f"""<div class="pslide"><p class="p-eb">What I found</p><h2 class="p-h">{r['found_title']}</h2><div class="p-stats">{stats}</div></div>""",
     f"""<div class="pslide"><p class="p-eb">Why I fit · {r['role']} {r['req']}</p><h2 class="p-h">The role asks, I bring</h2><div class="tw"><table class="p-fit"><tr><th>The role asks for</th><th>What I bring</th></tr>{fit}</table></div></div>""",
     f"""<div class="pslide dk"><p class="p-eb">Now check my work</p><h2 class="p-h p-big">Ready to do this with real data.</h2>
<div class="p-ctas"><a class="p-btn pri" href="#{r['explore'][0]}" data-tab="{r['explore'][0]}">{r['explore'][1]} →</a><a class="p-btn" href="{r['other'][0]}">{r['other'][1]} →</a></div>
<p class="p-contact">rajcmehta03@gmail.com · +1 315 718 3162 · linkedin.com/in/rajmehta2810 · All data is simulated.</p></div>""",
    ]
    return f"""<section id="pitch"><div class="pitch-wrap"><div class="ptrack" id="ptrack">{''.join(slides)}</div>
<div class="pnav"><div class="pdots" id="pdots"></div><span class="phint">Tip: use ← → keys</span><div class="parr"><button id="pprev" aria-label="Previous slide">‹</button><span id="pcnt"></span><button id="pnext" aria-label="Next slide">›</button></div></div></div></section>"""

def inject(html, role):
    for m in ("<!--PITCH-->", "/*PITCHCSS*/", "/*PITCHJS*/"):
        assert m in html, m
    return html.replace("<!--PITCH-->", section(role)).replace("/*PITCHCSS*/", CSS).replace("/*PITCHJS*/", JS)
