"""
Enhance web_app.py with smooth UI/UX transitions throughout.
Replaces the CSS <style> block and adds JS for scroll-triggered animations.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('web_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ══════════════════════════════════════════════════════════════════
# 1. REPLACE THE CSS STYLE BLOCK
# ══════════════════════════════════════════════════════════════════

old_css_start = '<style>\n:root{--primary:#4f46e5;--primary-dark:#4338ca;--primary-light:#eef2ff'
old_css_end = '}\n@media(max-width:768px){.stat-card .stat-number{font-size:1.8rem}.welcome-hero{padding:1.5rem}.welcome-hero h1{font-size:1.3rem}.search-filters .form-control,.search-filters .form-select{width:100%}.book-grid-card .book-cover{height:80px;font-size:1.8rem}.stats-bar{gap:.8rem}.stats-bar .stat-item{min-width:80px}.stats-bar .stat-item .num{font-size:1.2rem}}\n</style>'

new_css = """<style>
:root{--primary:#4f46e5;--primary-dark:#4338ca;--primary-light:#eef2ff;--primary-glow:rgba(79,70,229,.25);--bg:#f8fafc;--bg-card:rgba(255,255,255,.85);--text:#0f172a;--text-muted:#64748b;--text-dim:#94a3b8;--border:rgba(226,232,240,.8);--success:#10b981;--warning:#f59e0b;--danger:#ef4444;--info:#3b82f6;--glass-bg:rgba(255,255,255,.7);--glass-border:rgba(255,255,255,.3);--glass-shadow:0 8px 32px rgba(0,0,0,.06);--radius:16px;--radius-sm:10px;--font:'Inter','Segoe UI',system-ui,-apple-system,sans-serif;--ease: cubic-bezier(.4,0,.2,1);--ease-out: cubic-bezier(0,.55,.45,1);--ease-spring: cubic-bezier(.34,1.56,.64,1);--ease-bounce: cubic-bezier(.34,1.56,.64,1)}
[data-theme="dark"]{--bg:#0b1121;--bg-card:rgba(30,41,59,.85);--text:#f1f5f9;--text-muted:#94a3b8;--text-dim:#64748b;--border:rgba(51,65,85,.6);--glass-bg:rgba(30,41,59,.6);--glass-border:rgba(51,65,85,.3);--glass-shadow:0 8px 32px rgba(0,0,0,.3);--primary-light:#1e1b4b}
/* ── Base & Reset ── */
html{scroll-behavior:smooth}
*{transition:background-color .3s var(--ease),color .3s var(--ease),border-color .3s var(--ease),box-shadow .3s var(--ease),transform .3s var(--ease),opacity .3s var(--ease)}
body{background:var(--bg);color:var(--text);font-family:var(--font);min-height:100vh;overflow-x:hidden;opacity:0;animation:bodyFadeIn .4s var(--ease) forwards}
::selection{background:var(--primary);color:white}
@keyframes bodyFadeIn{from{opacity:0}to{opacity:1}}

/* ── Page Transitions ── */
.page-wrapper{animation:pageEnter .45s var(--ease) both}
@keyframes pageEnter{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}

/* ── Navbar ── */
.navbar{background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 50%,#a855f7 100%)!important;backdrop-filter:blur(20px);box-shadow:0 4px 30px rgba(79,70,229,.3);animation:navSlideDown .5s var(--ease) both}
@keyframes navSlideDown{from{transform:translateY(-100%);opacity:0}to{transform:translateY(0);opacity:1}}
.navbar-brand{font-weight:800;letter-spacing:-.5px;font-size:1.35rem;transition:transform .3s var(--ease)}
.navbar-brand:hover{transform:scale(1.03)}
.navbar .nav-link{font-weight:500;padding:.5rem .8rem!important;border-radius:8px;transition:all .25s var(--ease);position:relative}
.navbar .nav-link::after{content:'';position:absolute;bottom:2px;left:50%;width:0;height:2px;background:rgba(255,255,255,.6);border-radius:2px;transition:all .3s var(--ease);transform:translateX(-50%)}
.navbar .nav-link:hover::after{width:60%}
.navbar .nav-link:hover{background:rgba(255,255,255,.12)}

/* ── Glass Cards ── */
.glass-card{background:var(--glass-bg);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid var(--glass-border);box-shadow:var(--glass-shadow);border-radius:var(--radius);transition:all .35s var(--ease);will-change:transform,box-shadow}
.glass-card:hover{box-shadow:var(--glass-shadow),0 0 0 1px var(--primary-glow),0 12px 40px rgba(79,70,229,.08);transform:translateY(-3px)}
.glass-card-static:hover{transform:none!important;box-shadow:var(--glass-shadow)!important}

/* ── Stat Cards ── */
.stat-card{position:relative;overflow:hidden;border-radius:var(--radius);padding:1.5rem;color:white;min-height:130px;transition:all .4s var(--ease);will-change:transform,box-shadow}
.stat-card:hover{transform:translateY(-5px) scale(1.02);box-shadow:0 16px 48px rgba(0,0,0,.2)}
.stat-card:active{transform:translateY(-2px) scale(.98)}
.stat-card .stat-icon{position:absolute;right:1.2rem;top:1.2rem;font-size:3rem;opacity:.15;transition:all .5s var(--ease)}
.stat-card:hover .stat-icon{opacity:.25;transform:scale(1.1) rotate(-5deg)}
.stat-card .stat-number{font-size:2.4rem;font-weight:800;line-height:1.1;letter-spacing:-1px}
.stat-card .stat-label{opacity:.85;font-size:.8rem;font-weight:600;text-transform:uppercase;letter-spacing:.8px}
.stat-card .stat-trend{font-size:.8rem;opacity:.8;margin-top:.3rem}
.stat-card .stat-shine{position:absolute;top:-50%;right:-50%;width:100%;height:100%;background:radial-gradient(circle,rgba(255,255,255,.1) 0%,transparent 70%);border-radius:50%;pointer-events:none;transition:all .6s var(--ease)}
.stat-card:hover .stat-shine{transform:scale(1.3)}

/* ── Book Cards ── */
.book-grid-card{border-radius:var(--radius);overflow:hidden;background:var(--bg-card);border:1px solid var(--border);box-shadow:0 1px 3px rgba(0,0,0,.04);transition:all .35s var(--ease);cursor:pointer;position:relative;animation:cardEnter .4s var(--ease) both}
.book-grid-card:nth-child(1){animation-delay:0s}
.book-grid-card:nth-child(2){animation-delay:.04s}
.book-grid-card:nth-child(3){animation-delay:.08s}
.book-grid-card:nth-child(4){animation-delay:.12s}
.book-grid-card:nth-child(5){animation-delay:.16s}
.book-grid-card:nth-child(6){animation-delay:.2s}
.book-grid-card:nth-child(7){animation-delay:.24s}
.book-grid-card:nth-child(8){animation-delay:.28s}
.book-grid-card:nth-child(9){animation-delay:.32s}
.book-grid-card:nth-child(10){animation-delay:.36s}
.book-grid-card:nth-child(11){animation-delay:.4s}
.book-grid-card:nth-child(12){animation-delay:.44s}
@keyframes cardEnter{from{opacity:0;transform:translateY(20px) scale(.97)}to{opacity:1;transform:translateY(0) scale(1)}}
.book-grid-card:hover{transform:translateY(-8px);box-shadow:0 12px 40px rgba(0,0,0,.08),0 0 0 1px var(--primary-glow)}
.book-grid-card .book-cover{height:120px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;color:white;position:relative;overflow:hidden;transition:all .4s var(--ease)}
.book-grid-card:hover .book-cover{transform:scale(1.05)}
.book-grid-card .book-cover::after{content:'';position:absolute;bottom:0;left:0;right:0;height:40%;background:linear-gradient(transparent,rgba(0,0,0,.3));transition:opacity .4s var(--ease)}
.book-grid-card:hover .book-cover::after{opacity:.7}
.book-grid-card .book-cover .book-icon{position:relative;z-index:1;transition:all .4s var(--ease-spring)}
.book-grid-card:hover .book-cover .book-icon{transform:scale(1.15) rotate(-5deg)}
.book-grid-card .book-info{padding:.8rem 1rem;transition:transform .3s var(--ease)}
.book-grid-card:hover .book-info{transform:translateY(-2px)}
.book-grid-card .book-title{font-weight:600;font-size:.9rem;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.book-grid-card .book-author{font-size:.8rem;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

/* ── Welcome Hero ── */
.welcome-hero{background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 40%,#a855f7 100%);border-radius:var(--radius);padding:2rem 2.5rem;color:white;position:relative;overflow:hidden;margin-bottom:1.5rem;animation:heroEnter .6s var(--ease) both}
@keyframes heroEnter{from{opacity:0;transform:scale(.98)}to{opacity:1;transform:scale(1)}}
.welcome-hero::before{content:'';position:absolute;top:-50%;right:-20%;width:60%;height:200%;background:radial-gradient(circle,rgba(255,255,255,.06) 0%,transparent 60%);border-radius:50%;pointer-events:none;animation:heroPulse 8s ease-in-out infinite}
@keyframes heroPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.1)}}
.welcome-hero::after{content:'';position:absolute;bottom:-30%;left:20%;width:40%;height:100%;background:radial-gradient(circle,rgba(255,255,255,.04) 0%,transparent 60%);border-radius:50%;pointer-events:none}
.welcome-hero h1{font-weight:800;font-size:1.8rem;position:relative}
.welcome-hero p{opacity:.9;position:relative}

/* ── Buttons ── */
.btn{border-radius:var(--radius-sm);font-weight:600;padding:.5rem 1.2rem;transition:all .25s var(--ease);border:none;position:relative;overflow:hidden;cursor:pointer;user-select:none}
.btn::after{content:'';position:absolute;inset:0;background:radial-gradient(circle at var(--mx,50%) var(--my,50%),rgba(255,255,255,.2) 0%,transparent 60%);opacity:0;transition:opacity .3s;pointer-events:none}
.btn:hover::after{opacity:1}
.btn:active{transform:scale(.96)!important}
.btn-primary{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:white}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(79,70,229,.4)}
.btn-sm{padding:.35rem .9rem;font-size:.8rem;border-radius:8px}
.btn-outline{background:transparent;border:2px solid var(--border);color:var(--text)}
.btn-outline:hover{border-color:var(--primary);color:var(--primary);background:var(--primary-light);transform:translateY(-2px);box-shadow:0 4px 12px var(--primary-glow)}

/* ── Forms ── */
.form-control,.form-select{background:var(--bg-card);color:var(--text);border:2px solid var(--border);border-radius:var(--radius-sm);padding:.6rem 1rem;font-size:.9rem;transition:all .25s var(--ease)}
.form-control:hover,.form-select:hover{border-color:var(--text-dim)}
.form-control:focus,.form-select:focus{border-color:var(--primary);box-shadow:0 0 0 4px var(--primary-glow);background:var(--bg-card);color:var(--text);transform:translateY(-1px)}
.form-label{font-weight:600;font-size:.8rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:.3rem;transition:color .3s var(--ease)}
input:focus + .form-label{color:var(--primary)}

/* ── Tables ── */
.table{color:var(--text);margin-bottom:0;font-size:.9rem}
.table th{font-weight:600;color:var(--text-muted);text-transform:uppercase;font-size:.7rem;letter-spacing:.8px;border-bottom:2px solid var(--border);padding:.75rem .5rem}
.table td{color:var(--text);vertical-align:middle;border-bottom:1px solid var(--border);padding:.7rem .5rem;transition:all .2s var(--ease)}
.table-hover tbody tr{transition:all .2s var(--ease)}
.table-hover tbody tr:hover{background:rgba(79,70,229,.04);transform:translateX(3px)}
.table tbody tr:last-child td{border-bottom:none}
.table-row-enter{animation:rowEnter .3s var(--ease) both}
@keyframes rowEnter{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}

/* ── Section Title ── */
.section-title{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--text-muted);margin-bottom:.8rem;display:flex;align-items:center;gap:.4rem}

/* ── Stats Bar ── */
.stats-bar{display:flex;flex-wrap:wrap;gap:1.5rem;padding:1rem 1.25rem;background:var(--glass-bg);border-radius:var(--radius);border:1px solid var(--glass-border)}
.stats-bar .stat-item{flex:1;min-width:100px;transition:all .3s var(--ease)}
.stats-bar .stat-item:hover{transform:translateY(-2px)}
.stats-bar .stat-item .num{font-size:1.5rem;font-weight:800;line-height:1.1}
.stats-bar .stat-item .desc{font-size:.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.5px;margin-top:.15rem}

/* ── Charts ── */
.chart-container{position:relative;height:220px;width:100%;animation:chartFade .6s var(--ease) both}
@keyframes chartFade{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}

/* ── Badges ── */
.badge{border-radius:6px;padding:.35em .65em;font-weight:500;font-size:.75rem;transition:all .3s var(--ease)}
.badge-green{background:rgba(16,185,129,.12);color:#059669;font-weight:600}
.badge-red{background:rgba(239,68,68,.12);color:#dc2626;font-weight:600}
.badge-green:hover,.badge-red:hover{transform:scale(1.05)}

/* ── Empty State ── */
.empty-state{text-align:center;padding:3rem 1rem;color:var(--text-muted);animation:fadeInUp .5s var(--ease) both}
.empty-state .empty-icon{font-size:3rem;margin-bottom:1rem;opacity:.3;transition:all .5s var(--ease)}
.empty-state:hover .empty-icon{opacity:.5;transform:scale(1.1)}

/* ── Progress ── */
.progress-thin{height:6px;border-radius:3px;background:var(--border);overflow:hidden}
.progress-thin .bar{height:100%;border-radius:3px;transition:width 1s var(--ease-out);position:relative}
.progress-thin .bar::after{content:'';position:absolute;top:0;left:-100%;width:100%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.3),transparent);animation:shimmer 2s infinite}
.progress-thin:hover .bar{filter:brightness(1.1)}

/* ── Info Grid ── */
.info-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:.8rem}
.info-card{padding:.8rem;border-radius:var(--radius-sm);background:rgba(79,70,229,.04);border:1px solid var(--border);transition:all .3s var(--ease);animation:infoCardEnter .4s var(--ease) both}
.info-card:nth-child(2){animation-delay:.05s}
.info-card:nth-child(3){animation-delay:.1s}
.info-card:nth-child(4){animation-delay:.15s}
.info-card:nth-child(5){animation-delay:.2s}
.info-card:nth-child(6){animation-delay:.25s}
@keyframes infoCardEnter{from{opacity:0;transform:scale(.95)}to{opacity:1;transform:scale(1)}}
.info-card:hover{background:rgba(79,70,229,.08);border-color:var(--primary);transform:translateY(-2px);box-shadow:0 4px 12px var(--primary-glow)}
.info-card .value{font-size:1.2rem;font-weight:700;color:var(--text)}
.info-card .label{font-size:.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.5px;margin-top:.1rem}

/* ── Pagination ── */
.pagination .page-link{background:var(--bg-card);color:var(--text);border:1px solid var(--border);border-radius:8px!important;margin:0 2px;transition:all .2s var(--ease)}
.pagination .page-link:hover{background:var(--primary-light);border-color:var(--primary);color:var(--primary);transform:translateY(-2px);box-shadow:0 4px 12px var(--primary-glow)}
.pagination .page-item.active .page-link{background:var(--primary);border-color:var(--primary);color:white;transform:translateY(-2px);box-shadow:0 4px 12px var(--primary-glow)}

/* ── Search Filters ── */
.search-filters{display:flex;gap:.5rem;flex-wrap:wrap;align-items:center}
.search-filters .form-control,.search-filters .form-select{width:auto;min-width:140px}

/* ── Timeline ── */
.timeline{position:relative;padding-left:1.5rem}
.timeline::before{content:'';position:absolute;left:6px;top:0;bottom:0;width:2px;background:var(--border);transform-origin:top;animation:timelineGrow .6s var(--ease) both}
@keyframes timelineGrow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
.timeline-item{position:relative;padding:.6rem 0 .6rem .8rem;animation:tlItem .4s var(--ease) both}
.timeline-item:nth-child(1){animation-delay:.1s}
.timeline-item:nth-child(2){animation-delay:.2s}
.timeline-item:nth-child(3){animation-delay:.3s}
.timeline-item:nth-child(4){animation-delay:.4s}
.timeline-item:nth-child(5){animation-delay:.5s}
@keyframes tlItem{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:translateX(0)}}
.timeline-item::before{content:'';position:absolute;left:-1.15rem;top:1rem;width:10px;height:10px;border-radius:50%;background:var(--primary);border:2px solid var(--bg);transition:all .3s var(--ease-spring)}
.timeline-item:hover::before{transform:scale(1.4);box-shadow:0 0 0 4px var(--primary-glow)}
.timeline-item.return::before{background:var(--success)}
.timeline-item.return:hover::before{box-shadow:0 0 0 4px rgba(16,185,129,.3)}

/* ── Insight Banner ── */
.insight-banner{padding:.8rem 1.2rem;border-radius:var(--radius-sm);background:rgba(79,70,229,.06);border:1px solid rgba(79,70,229,.15);margin-bottom:.8rem;display:flex;align-items:center;gap:.6rem;font-size:.85rem;transition:all .3s var(--ease)}
.insight-banner:hover{background:rgba(79,70,229,.1);border-color:rgba(79,70,229,.25)}

/* ── Footer ── */
footer{color:var(--text-muted);font-size:.8rem;border-top:1px solid var(--border);padding:1.5rem 0;text-align:center;margin-top:2rem}

/* ── Nav Badge ── */
.nav-badge{position:absolute;top:-2px;right:-6px;font-size:.55rem;padding:.2em .45em;min-width:16px;animation:badgeBounce .5s var(--ease-spring)}
@keyframes badgeBounce{0%{transform:scale(0)}50%{transform:scale(1.3)}100%{transform:scale(1)}}

/* ── Links ── */
a{color:var(--primary);text-decoration:none;transition:all .25s var(--ease)}
a:hover{color:var(--primary-dark)}

/* ── Overdue Items ── */
.overdue-item{border-left:4px solid var(--danger);background:rgba(239,68,68,.04);border-radius:var(--radius-sm);padding:.8rem 1rem;margin-bottom:.6rem;display:flex;align-items:center;gap:.8rem;transition:all .3s var(--ease);animation:slideIn .3s var(--ease) both}
.overdue-item:nth-child(1){animation-delay:.05s}
.overdue-item:nth-child(2){animation-delay:.1s}
.overdue-item:nth-child(3){animation-delay:.15s}
.overdue-item:nth-child(4){animation-delay:.2s}
.overdue-item:nth-child(5){animation-delay:.25s}
.overdue-item:hover{background:rgba(239,68,68,.08);transform:translateX(4px)}

/* ── Activity Feed ── */
.activity-item{padding:.6rem 0;border-bottom:1px solid var(--border);display:flex;align-items:flex-start;gap:.75rem;animation:slideIn .3s var(--ease) both;transition:all .2s var(--ease)}
.activity-item:last-child{border-bottom:none}
.activity-item:hover{background:rgba(79,70,229,.02);padding-left:.5rem;border-radius:8px}
.activity-icon{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;transition:all .3s var(--ease-spring)}
.activity-item:hover .activity-icon{transform:scale(1.1)}

/* ── Quick Actions ── */
.quick-action{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:1rem .5rem;border-radius:var(--radius-sm);border:2px dashed var(--border);cursor:pointer;transition:all .3s var(--ease);text-decoration:none;color:var(--text-muted);background:var(--bg-card);min-height:80px;position:relative;overflow:hidden}
.quick-action::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,var(--primary),transparent);opacity:0;transition:opacity .4s var(--ease)}
.quick-action:hover{border-color:var(--primary);color:var(--primary);background:var(--primary-light);border-style:solid;box-shadow:0 8px 24px var(--primary-glow);transform:translateY(-4px)}
.quick-action:hover::before{opacity:.05}
.quick-action .qa-icon{font-size:1.5rem;margin-bottom:.25rem;transition:all .4s var(--ease-spring)}
.quick-action:hover .qa-icon{transform:scale(1.2) rotate(-5deg)}
.quick-action .qa-label{font-size:.65rem;font-weight:600;text-transform:uppercase;letter-spacing:.5px;text-align:center;position:relative}

/* ── Theme Toggle ── */
.theme-toggle{cursor:pointer;width:36px;height:36px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all .4s var(--ease-spring);font-size:1.1rem;color:rgba(255,255,255,.8)}
.theme-toggle:hover{background:rgba(255,255,255,.15);transform:rotate(25deg) scale(1.1)}

/* ── Skeleton Loading ── */
.skeleton{background:linear-gradient(90deg,var(--border) 25%,var(--bg) 50%,var(--border) 75%);background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:8px}
.skeleton-card{height:140px;margin-bottom:.8rem;border-radius:var(--radius)}
.skeleton-line{height:12px;margin-bottom:.5rem;width:80%;border-radius:4px}
.skeleton-line.w60{width:60%}.skeleton-line.w40{width:40%}
.skeleton-pulse{animation:skeletonPulse 2s ease-in-out infinite}
@keyframes skeletonPulse{0%,100%{opacity:1}50%{opacity:.5}}

/* ── Keyframes ── */
@keyframes shimmer{0%{background-position:200% 0}to{background-position:-200% 0}}
@keyframes fadeInUp{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}
@keyframes scaleIn{from{opacity:0;transform:scale(.9)}to{opacity:1;transform:scale(1)}}
@keyframes slideIn{from{opacity:0;transform:translateX(20px)}to{opacity:1;transform:translateX(0)}}
@keyframes slideOut{from{opacity:1;transform:translateX(0)}to{opacity:0;transform:translateX(100%)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes scaleUp{from{opacity:0;transform:scale(.95)}to{opacity:1;transform:scale(1)}}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}

/* ── Animation Utility Classes ── */
.animate-in{animation:fadeInUp .5s var(--ease) both}
.animate-d1{animation:fadeInUp .5s var(--ease) .08s both}
.animate-d2{animation:fadeInUp .5s var(--ease) .16s both}
.animate-d3{animation:fadeInUp .5s var(--ease) .24s both}
.animate-d4{animation:fadeInUp .5s var(--ease) .32s both}
.animate-d5{animation:fadeInUp .5s var(--ease) .4s both}
.animate-scale{animation:scaleIn .4s var(--ease) both}
.animate-fade{animation:fadeIn .4s var(--ease) both}
.animate-scale-up{animation:scaleUp .35s var(--ease) both}
.animate-pulse{animation:pulse 2s ease-in-out infinite}
.animate-float{animation:float 3s ease-in-out infinite}

/* ── Toast Notifications ── */
.toast-container{position:fixed;top:1rem;right:1rem;z-index:9999;display:flex;flex-direction:column;gap:.5rem}
.toast-msg{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-sm);padding:.8rem 1.2rem .8rem .8rem;box-shadow:0 8px 32px rgba(0,0,0,.1);display:flex;align-items:center;gap:.6rem;animation:toastIn .4s var(--ease-spring) both;font-size:.9rem;min-width:300px;max-width:420px;position:relative;overflow:hidden}
.toast-msg.success{border-left:4px solid var(--success)}
.toast-msg.error{border-left:4px solid var(--danger)}
.toast-msg.info{border-left:4px solid var(--info)}
.toast-msg .toast-progress{position:absolute;bottom:0;left:0;height:3px;background:var(--primary);border-radius:0 0 0 8px;animation:toastProgress 4s linear forwards}
.toast-msg.success .toast-progress{background:var(--success)}
.toast-msg.error .toast-progress{background:var(--danger)}
.toast-msg.info .toast-progress{background:var(--info)}
@keyframes toastIn{from{opacity:0;transform:translateX(100%) scale(.9)}to{opacity:1;transform:translateX(0) scale(1)}}
@keyframes toastOut{from{opacity:1;transform:translateX(0) scale(1)}to{opacity:0;transform:translateX(100%) scale(.9)}}
@keyframes toastProgress{from{width:100%}to{width:0%}}
.toast-msg.toast-closing{animation:toastOut .35s var(--ease) both}

/* ── Autocomplete ── */
.autocomplete-wrap{position:relative}
.autocomplete-results{position:absolute;top:100%;left:0;right:0;background:var(--bg-card);border:2px solid var(--border);border-top:none;border-radius:0 0 var(--radius-sm) var(--radius-sm);max-height:300px;overflow-y:auto;z-index:1000;display:none;animation:scaleUp .2s var(--ease) both;transform-origin:top center}
.autocomplete-results .ac-item{padding:.5rem .8rem;cursor:pointer;display:flex;align-items:center;gap:.5rem;border-bottom:1px solid var(--border);transition:all .15s var(--ease)}
.autocomplete-results .ac-item:last-child{border-bottom:none}
.autocomplete-results .ac-item:hover{background:var(--primary-light);transform:translateX(3px)}
.autocomplete-results .ac-item .ac-title{font-weight:500;font-size:.85rem}
.autocomplete-results .ac-item .ac-sub{font-size:.7rem;color:var(--text-muted)}

/* ── Keyboard Hint ── */
.kbd-hint{position:fixed;bottom:1rem;left:50%;transform:translateX(-50%);background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-sm);padding:.4rem 1rem;font-size:.75rem;color:var(--text-muted);z-index:999;opacity:0;transition:opacity .6s var(--ease),transform .6s var(--ease);pointer-events:none}
.kbd-hint.show{opacity:1;transform:translateX(-50%) translateY(0)}

/* ── Search Overlay ── */
.search-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0);backdrop-filter:blur(0);z-index:9998;display:flex;align-items:flex-start;justify-content:center;padding-top:5rem;transition:all .4s var(--ease);pointer-events:none;opacity:0}
.search-overlay.active{background:rgba(0,0,0,.3);backdrop-filter:blur(6px);pointer-events:all;opacity:1}
.search-overlay .search-box{width:600px;max-width:90vw;background:var(--bg-card);border:2px solid var(--border);border-radius:var(--radius);box-shadow:0 20px 60px rgba(0,0,0,.15);overflow:hidden;transform:translateY(-20px) scale(.97);transition:all .4s var(--ease-spring)}
.search-overlay.active .search-box{transform:translateY(0) scale(1)}
.search-overlay .search-box input{border:none;font-size:1.2rem;padding:1.2rem 1.5rem;width:100%;background:transparent;color:var(--text);outline:none}
.search-overlay .search-box .search-results{max-height:400px;overflow-y:auto;border-top:1px solid var(--border)}
.search-overlay .search-box .search-results .sr-item{padding:.8rem 1.5rem;cursor:pointer;display:flex;align-items:center;gap:.8rem;transition:all .2s var(--ease);border-bottom:1px solid var(--border);animation:slideIn .25s var(--ease) both}
.search-overlay .search-box .search-results .sr-item:nth-child(1){animation-delay:0s}
.search-overlay .search-box .search-results .sr-item:nth-child(2){animation-delay:.04s}
.search-overlay .search-box .search-results .sr-item:nth-child(3){animation-delay:.08s}
.search-overlay .search-box .search-results .sr-item:nth-child(4){animation-delay:.12s}
.search-overlay .search-box .search-results .sr-item:nth-child(5){animation-delay:.16s}
.search-overlay .search-box .search-results .sr-item:last-child{border-bottom:none}
.search-overlay .search-box .search-results .sr-item:hover{background:var(--primary-light);transform:translateX(4px)}
.search-overlay .search-box .search-footer{padding:.6rem 1.5rem;font-size:.75rem;color:var(--text-muted);display:flex;justify-content:space-between;align-items:center}
.search-overlay .search-box .search-footer kbd{background:var(--border);padding:.1rem .4rem;border-radius:4px;font-size:.7rem}

/* ── Modal ── */
.modal.fade .modal-dialog{transform:scale(.9) translateY(20px);transition:transform .35s var(--ease-spring),opacity .3s var(--ease)}
.modal.show .modal-dialog{transform:scale(1) translateY(0)}
.modal-backdrop{transition:opacity .3s var(--ease)!important}
.modal-content{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);animation:scaleUp .35s var(--ease-spring) both}
.modal-header{border-bottom:1px solid var(--border);padding:1.2rem 1.5rem}
.modal-body{padding:1.5rem}
.modal-footer{border-top:1px solid var(--border);padding:1rem 1.5rem}

/* ── Print ── */
@media print{body{background:white!important;animation:none!important}.navbar,.quick-action,.btn,.theme-toggle,.no-print{display:none!important}.glass-card{background:white!important;border:1px solid #ddd!important;box-shadow:none!important;backdrop-filter:none!important;transform:none!important}.chart-container{page-break-inside:avoid}.stats-bar{border:1px solid #ddd!important}footer{page-break-after:always}}

/* ── Responsive ── */
@media(max-width:768px){.stat-card .stat-number{font-size:1.8rem}.welcome-hero{padding:1.5rem}.welcome-hero h1{font-size:1.3rem}.search-filters .form-control,.search-filters .form-select{width:100%}.book-grid-card .book-cover{height:80px;font-size:1.8rem}.stats-bar{gap:.8rem}.stats-bar .stat-item{min-width:80px}.stats-bar .stat-item .num{font-size:1.2rem}}
</style>"""

# Find the exact CSS block in the content
css_start = content.find(old_css_start)
css_end = content.find(old_css_end)
if css_start >= 0 and css_end >= 0:
    css_end += len(old_css_end)
    old_css = content[css_start:css_end]
    content = content.replace(old_css, new_css, 1)
    print("✅ Replaced CSS style block with smooth UX transitions")
else:
    print(f"❌ Could not find CSS block. start={css_start}, end={css_end}")
    # Try to find partial match
    for i, m in enumerate(['<style>', ':root{--primary:', 'skeleton{background']):
        pos = content.find(m)
        print(f"  '{m}' found at {pos}" if pos >= 0 else f"  '{m}' NOT found")


# ══════════════════════════════════════════════════════════════════
# 2. ENHANCE THE JAVASCRIPT SECTION — add smooth interaction handlers
# ══════════════════════════════════════════════════════════════════

# Find the end of the main script tag (before </head>)
old_script_end = """\\n// ── Search Overlay (Ctrl+K) ──"""

js_additions = r"""

// ── Smooth UX: Enhanced Toast with Progress Bar ──
let originalShowToast = window.showToast;
window.showToast = function(msg, type){
  const c=document.getElementById('toastContainer')||(()=>{const d=document.createElement('div');d.id='toastContainer';d.className='toast-container';document.body.appendChild(d);return d})();
  const t=document.createElement('div');
  t.className='toast-msg '+type;
  const icons={success:'bi-check-circle-fill text-success',error:'bi-x-circle-fill text-danger',info:'bi-info-circle-fill text-info'};
  t.innerHTML='<i class="bi '+(icons[type]||icons.info)+'"></i> '+msg+'<div class="toast-progress"></div>';
  c.appendChild(t);
  setTimeout(()=>{t.classList.add('toast-closing');setTimeout(()=>t.remove(),350)},4000);
};

// ── Smooth UX: Button Ripple on Click ──
document.addEventListener('click', function(e){
  const btn=e.target.closest('.btn');
  if(!btn)return;
  const rect=btn.getBoundingClientRect();
  btn.style.setProperty('--mx',((e.clientX-rect.left)/rect.width*100)+'%');
  btn.style.setProperty('--my',((e.clientY-rect.top)/rect.height*100)+'%');
});

// ── Smooth UX: Scroll-triggered animations ──
(function(){
  if(!window.IntersectionObserver)return;
  const observer=new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        entry.target.style.animationPlayState='running';
        observer.unobserve(entry.target);
      }
    });
  },{threshold:.1});
  document.querySelectorAll('.glass-card:not(.glass-card-static), .animate-on-scroll').forEach(el=>{
    el.style.animation='none';
    el.style.opacity='0';
    observer.observe(el);
    // Force reflow then restore animation
    void el.offsetHeight;
    el.style.animation='';
    el.style.opacity='';
    el.style.animationPlayState='paused';
  });
})();

// ── Smooth UX: Form input glow on hover ──
document.querySelectorAll('.form-control, .form-select').forEach(el=>{
  el.addEventListener('mouseenter',function(){if(this!==document.activeElement)this.style.borderColor='var(--text-dim)'});
  el.addEventListener('mouseleave',function(){if(this!==document.activeElement)this.style.borderColor=''});
});

// ── Smooth UX: Animate count-up numbers with spring easing ──
function animateValue(el, start, end, duration){
  if(start===end)return;
  const range=end-start;
  const startTime=performance.now();
  function step(currentTime){
    const elapsed=currentTime-startTime;
    const progress=Math.min(elapsed/duration,1);
    // Spring-like easing
    const eased=1-Math.pow(1-progress,3)+Math.sin(progress*Math.PI*2)*.03*(1-progress);
    const current=start+range*eased;
    el.textContent=end%1!==0?current.toFixed(1):Math.round(current);
    if(progress<1)requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// Override original count-up with smoother version
document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('.count-up').forEach(el=>{
    const t=parseFloat(el.dataset.target);
    if(isNaN(t))return;
    const start=0;
    animateValue(el, start, t, 800);
  });
});

// ── Smooth UX: Enhanced search overlay animation ──
(function(){
  const origOpen=window.openSearchOverlay;
  if(origOpen){
    window.openSearchOverlay=function(){
      const o=document.getElementById('searchOverlay');
      if(!o)return origOpen&&origOpen();
      o.classList.add('active');
      document.body.style.overflow='hidden';
      const inp=o.querySelector('input');
      if(inp){inp.value='';setTimeout(()=>inp.focus(),100);if(typeof searchBooks==='function')searchBooks(inp.value)}
    };
  }
  const origClose=window.closeSearchOverlay;
  if(origClose){
    window.closeSearchOverlay=function(){
      const o=document.getElementById('searchOverlay');
      if(!o||!o.classList.contains('active'))return;
      o.classList.remove('active');
      document.body.style.overflow='';
    };
  }
})();

// ── Smooth UX: Table row stagger animation ──
(function(){
  document.querySelectorAll('.table tbody tr').forEach((el,i)=>{
    el.style.animation='rowEnter .3s ease-out '+(i*0.04)+'s both';
  });
})();"""

# Insert JS additions before the search overlay section
insert_pos = content.find(old_script_end)
if insert_pos >= 0:
    content = content[:insert_pos] + js_additions + content[insert_pos:]
    print("✅ Added smooth UX JavaScript enhancements")
else:
    print("❌ Could not find JS insertion point")

# ══════════════════════════════════════════════════════════════════
# 3. WRITE THE FILE
# ══════════════════════════════════════════════════════════════════

with open('web_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ All UX enhancements applied!")
