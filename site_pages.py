"""
site_pages.py - Landing page, features showcase, and welcome page for the full website
Registers routes on the Flask app for the public-facing marketing pages.
"""

import os, sys, json, html, random
from datetime import datetime

from flask import render_template_string, request, jsonify, redirect, url_for, session
from config import Config
from storage import Storage
from book import CATEGORIES as BOOK_CATEGORIES
from logger import log


def h(text): return html.escape(str(text))


def cat_color(c):
    colors = {"Fiction":"#4f46e5","Non-Fiction":"#059669","Science":"#0891b2","Technology":"#7c3aed",
        "History":"#d97706","Philosophy":"#be185d","Art":"#db2777","Biography":"#ca8a04","Children":"#16a34a",
        "Comics":"#e11d48","Poetry":"#9333ea","Drama":"#ea580c","Education":"#2563eb","Reference":"#64748b",
        "Religion":"#78716c","Self-Help":"#0d9488","Cooking":"#f97316","Travel":"#0ea5e9","Music":"#8b5cf6",
        "Sports":"#22c55e","Other":"#6b7280"}
    return colors.get(c, colors["Other"])


def init_site_pages(app, storage, lib, recommender, social, review_mgr, notif_mgr):
    """Register site pages on the Flask app."""

    def get_current_user():
        if "user_id" not in session: return None
        return storage.load_users().get(session["user_id"])

    def _library_stats():
        books = storage.load_books()
        users = storage.load_users()
        txns = storage.load_transactions()
        all_books = [b for b in books.values() if not b.is_deleted]
        now = datetime.now(); tms = datetime(now.year, now.month, 1)
        total_books = len(all_books); total_copies = sum(b.total_copies for b in all_books)
        avail_copies = sum(b.available_copies for b in all_books)
        avail_rate = (avail_copies/total_copies*100) if total_copies else 0
        total_users = len(users); active_users = sum(1 for u in users.values() if u.membership_status=="Active")
        blocked_users = sum(1 for u in users.values() if u.membership_status=="Blocked")
        new_users_month = sum(1 for u in users.values() if hasattr(u,'registered_on') and u.registered_on and datetime.fromisoformat(u.registered_on)>=tms)
        new_books_month = sum(1 for b in all_books if datetime.fromisoformat(b.added_on)>=tms)
        issues = [t for t in txns if t["type"]=="issue"]
        active_issues = [t for t in issues if t.get("return_date") is None]
        total_txns = len(txns); month_txns = sum(1 for t in txns if datetime.fromisoformat(t.get("issue_date",""))>=tms)
        unique_borrowers = len(set(t["user_id"] for t in issues))
        fines = storage.load_fines()
        total_fines = sum(f.get("amount",0) for f in fines)
        paid_fines = sum(f.get("amount",0) for f in fines if f.get("paid"))
        pending_fines = total_fines - paid_fines
        avg_bpu = round(len(issues)/total_users,1) if total_users else 0
        return {"total_books":total_books,"total_copies":total_copies,"avail_copies":avail_copies,
            "active_issues":len(active_issues),"total_issues":len(issues),
            "avail_rate":round(avail_rate,1),"new_books_month":new_books_month,
            "total_users":total_users,"active_users":active_users,"blocked_users":blocked_users,
            "new_users_month":new_users_month,"total_txns":total_txns,"month_txns":month_txns,
            "unique_borrowers":unique_borrowers,            "avg_books_per_user":avg_bpu,
            "total_fines":round(total_fines,2),"paid_fines":round(paid_fines,2),"pending_fines":round(pending_fines,2)}

    def _initials(name):
        parts = name.strip().split()
        if not parts: return "?"
        if len(parts) >= 2: return (parts[0][0] + parts[-1][0]).upper()
        return parts[0][:2].upper()

    def _avatar_html(name, size=32):
        i = _initials(name)
        colors = ["#4f46e5","#059669","#d97706","#dc2626","#0891b2","#7c3aed","#db2777","#ca8a04"]
        c = colors[hash(name) % len(colors)]
        return f'<div class="avatar" style="width:{size}px;height:{size}px;background:{c}20;color:{c};font-size:{size//2}px;font-weight:700;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;" title="{h(name)}">{h(i)}</div>'

    def render_page(title, content, **kw):
        """Reuse the app's base template."""
        # Build template using str.replace to avoid Python % formatting conflicts
        # with CSS/JS content that uses % (modulo, keyframes, etc.)
        _T = """
<!DOCTYPE html><html lang="en" data-theme="light">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>__TITLE__ &mdash; LibraryMS + BookSocial</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{--primary:#4f46e5;--primary-dark:#4338ca;--primary-light:#eef2ff;--primary-glow:rgba(79,70,229,.25);--bg:#f8fafc;--bg-card:rgba(255,255,255,.85);--text:#0f172a;--text-muted:#64748b;--text-dim:#94a3b8;--border:rgba(226,232,240,.8);--success:#10b981;--warning:#f59e0b;--danger:#ef4444;--info:#3b82f6;--glass-bg:rgba(255,255,255,.7);--glass-border:rgba(255,255,255,.3);--glass-shadow:0 8px 32px rgba(0,0,0,.06);--radius:16px;--radius-sm:10px;--font:'Inter','Segoe UI',system-ui,-apple-system,sans-serif;--ease:cubic-bezier(.4,0,.2,1);--ease-spring:cubic-bezier(.34,1.56,.64,1)}
[data-theme="dark"]{--bg:#0b1121;--bg-card:rgba(30,41,59,.85);--text:#f1f5f9;--text-muted:#94a3b8;--text-dim:#64748b;--border:rgba(51,65,85,.6);--glass-bg:rgba(30,41,59,.6);--glass-border:rgba(51,65,85,.3);--primary-light:#1e1b4b}
html{scroll-behavior:smooth}*{transition:background-color .3s,color .3s,border-color .3s,box-shadow .3s,transform .3s,opacity .3s}
body{background:var(--bg);color:var(--text);font-family:var(--font);min-height:100vh;opacity:0;animation:bodyIn .4s forwards}
::selection{background:var(--primary);color:white}
@keyframes bodyIn{to{opacity:1}}@keyframes fadeInUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes cardEnter{from{opacity:0;transform:translateY(16px) scale(.98)}to{opacity:1;transform:translateY(0) scale(1)}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
.page-wrapper{animation:pageEnter .5s ease both}
@keyframes pageEnter{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.glass-card{background:var(--glass-bg);backdrop-filter:blur(16px);border:1px solid var(--glass-border);border-radius:var(--radius);box-shadow:var(--glass-shadow);transition:all .35s var(--ease)}
.glass-card:hover{box-shadow:var(--glass-shadow),0 0 0 1px var(--primary-glow),0 12px 40px rgba(79,70,229,.08);transform:translateY(-3px)}
.section-title{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--text-muted);margin-bottom:.8rem;display:flex;align-items:center;gap:.4rem}
.btn{border-radius:var(--radius-sm);font-weight:600;padding:.5rem 1.2rem;transition:all .25s var(--ease);border:none;position:relative;overflow:hidden}
.btn-primary{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:white}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(79,70,229,.4);color:white}
.btn-outline{background:transparent;border:2px solid var(--border);color:var(--text)}
.btn-outline:hover{border-color:var(--primary);color:var(--primary);background:var(--primary-light)}
.btn-lg{padding:.7rem 1.8rem;font-size:1rem}
.badge{border-radius:50px;font-weight:500;font-size:.75rem}
</style>
<script>
function toggleTheme(){const h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n)}
document.addEventListener('DOMContentLoaded',()=>{const s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);
document.querySelectorAll('.count-up').forEach(el=>{const t=parseFloat(el.dataset.target);if(isNaN(t))return;const o=parseInt(el.textContent.replace(/[^0-9.-]/g,''))||0;const r=t-o;const st=performance.now();function step(ct){const p=Math.min((ct-st)/800,1);const e=1-Math.pow(1-p,3);el.textContent=t%1!==0?(o+r*e).toFixed(1):Math.round(o+r*e);if(p<1)requestAnimationFrame(step)}requestAnimationFrame(step)})
})
</script>
</head>
<body>
__CONTENT__
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body></html>"""
        filled = _T.replace("__TITLE__", h(title)).replace("__CONTENT__", content)
        return render_template_string(filled, **kw)

    # ═══════════════════════════════════════════════════════════
    # LANDING PAGE
    # ═══════════════════════════════════════════════════════════

    @app.route("/landing")
    @app.route("/")
    def landing_page():
        """Spectacular landing page — works for both guests and logged-in users."""
        uid = session.get("user_id")
        user = get_current_user() if uid else None

        # Logged-in users go to dashboard
        if user:
            # Just redirect to the existing dashboard
            try:
                users_data = storage.load_users()
                u = users_data.get(uid)
                if u:
                    return redirect(url_for("dashboard"))
            except:
                pass

        # ── Guest landing page ──
        s = _library_stats()
        books = storage.load_books()
        all_books = [b for b in books.values() if not b.is_deleted]
        featured_books = sorted(all_books, key=lambda b: b.issue_count, reverse=True)[:6]
        posts = storage.load_posts() if hasattr(storage, 'load_posts') else []
        reviews_data = storage.load_reviews() if hasattr(storage, 'load_reviews') else []

        cat_counts = {}
        for b in all_books:
            cat_counts[b.category] = cat_counts.get(b.category, 0) + 1
        top_cats = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:4]

        # Featured books cards
        featured_cards = ""
        for b in featured_books:
            cc = cat_color(b.category)
            featured_cards += '''<a href="/login" class="col-6 col-md-4 col-lg-2 text-decoration-none">
                <div class="glass-card p-3 text-center h-100" style="cursor:pointer;animation:cardEnter .4s ease both;">
                    <div style="width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,%s,%sdd);display:flex;align-items:center;justify-content:center;margin:0 auto .5rem;">
                        <i class="bi bi-book-fill" style="color:white;font-size:1.2rem;"></i></div>
                    <div style="font-size:.8rem;font-weight:600;line-height:1.2;">%s</div>
                    <small style="font-size:.65rem;color:var(--text-muted);">%s</small>
                    <div style="font-size:.6rem;color:var(--text-muted);margin-top:.3rem;"><i class="bi bi-eye me-1"></i>%d issues</div>
                </div></a>''' % (cc, cc, h(b.title[:40]), h(b.author[:30]), b.issue_count)
        if not featured_cards:
            featured_cards = '<div class="col-12 text-center text-muted">No books yet.</div>'

        cat_boxes = ""
        for cat, cnt in top_cats:
            cc = cat_color(cat)
            cat_boxes += '''<div class="col-6 col-md-3 mb-3">
                <div class="glass-card p-3 text-center h-100" style="border-top:3px solid %s;">
                    <div class="fw-bold" style="font-size:1.5rem;color:%s;">%d</div>
                    <small style="font-size:.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.5px;">%s</small>
                </div></div>''' % (cc, cc, cnt, h(cat))

        content = r'''<div class="page-wrapper">
<style>
.landing-hero{min-height:85vh;display:flex;align-items:center;position:relative;overflow:hidden;background:linear-gradient(135deg,#0b1121 0%,#162033 40%,#1a1b4e 100%)}
.landing-hero::before{content:'';position:absolute;inset:0;background:radial-gradient(circle at 20% 50%,rgba(79,70,229,.15) 0%,transparent 50%),radial-gradient(circle at 80% 20%,rgba(168,85,247,.1) 0%,transparent 50%),radial-gradient(circle at 50% 80%,rgba(16,185,129,.08) 0%,transparent 50%)}
.landing-hero::after{content:'';position:absolute;bottom:0;left:0;right:0;height:200px;background:linear-gradient(transparent,var(--bg))}
.hero-grid{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.03) 1px,transparent 1px);background-size:40px 40px}
.hero-content{position:relative;z-index:1;padding:4rem 0}
.hero-badge{display:inline-block;background:rgba(79,70,229,.2);border:1px solid rgba(79,70,229,.3);border-radius:50px;padding:.35rem 1.2rem;font-size:.8rem;color:#a5b4fc;margin-bottom:1.5rem;animation:fadeInUp .6s ease both}
.hero-title{font-size:3.5rem;font-weight:800;line-height:1.1;margin-bottom:1rem;color:white;animation:fadeInUp .6s ease .1s both}
.hero-title span{background:linear-gradient(135deg,#4f46e5,#a855f7,#f59e0b);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero-sub{font-size:1.15rem;color:rgba(255,255,255,.6);max-width:600px;margin-bottom:2rem;line-height:1.6;animation:fadeInUp .6s ease .15s both}
.hero-actions{display:flex;gap:1rem;flex-wrap:wrap;animation:fadeInUp .6s ease .2s both}
.hero-btn{display:inline-flex;align-items:center;gap:.5rem;padding:.8rem 2rem;border-radius:12px;font-weight:600;font-size:.95rem;text-decoration:none;transition:all .3s ease}
.hero-btn-primary{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:white;box-shadow:0 8px 30px rgba(79,70,229,.4)}
.hero-btn-primary:hover{transform:translateY(-3px);box-shadow:0 12px 40px rgba(79,70,229,.5);color:white}
.hero-btn-secondary{background:rgba(255,255,255,.08);color:white;border:1px solid rgba(255,255,255,.15)}
.hero-btn-secondary:hover{background:rgba(255,255,255,.12);transform:translateY(-3px);color:white}
.hero-stats{display:flex;gap:2.5rem;margin-top:3rem;padding-top:2rem;border-top:1px solid rgba(255,255,255,.08);animation:fadeInUp .6s ease .25s both}
.hs-num{font-size:2rem;font-weight:800;color:white;line-height:1}
.hs-label{font-size:.75rem;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:.5px;margin-top:.25rem}
.hero-visual-inner{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:2rem;backdrop-filter:blur(10px)}
.code-block{font-family:monospace;font-size:.75rem;color:rgba(255,255,255,.7);line-height:1.8}
.code-block .kw{color:#a855f7}.code-block .str{color:#10b981}.code-block .cm{color:rgba(255,255,255,.3)}
.feature-icon-box{width:64px;height:64px;border-radius:16px;display:flex;align-items:center;justify-content:center;margin:0 auto 1rem;color:white;font-size:1.8rem}
.stats-banner{background:linear-gradient(135deg,#4f46e5,#7c3aed);padding:3rem 0;margin:3rem 0}
.stats-banner .snum{font-size:2.5rem;font-weight:800;color:white}
.stats-banner .slabel{color:rgba(255,255,255,.7);font-size:.8rem;text-transform:uppercase;letter-spacing:1px}
.cta-box{background:linear-gradient(135deg,#4f46e510,#7c3aed10);border:2px dashed var(--primary-glow);border-radius:var(--radius);padding:3rem}
@media(max-width:768px){.hero-title{font-size:2rem}.hero-sub{font-size:.95rem}.hero-stats{gap:1rem;flex-wrap:wrap}.hs-num{font-size:1.3rem}}
</style>

<div class="landing-hero">
  <div class="hero-grid"></div>
  <div class="container hero-content">
    <div class="row align-items-center g-5">
      <div class="col-lg-7">
        <div class="hero-badge"><i class="bi bi-lightning-fill me-1"></i> v3.0 — The Ultimate Library Platform</div>
        <h1 class="hero-title">Manage Books.<br>Connect Readers.<br><span>Powered by AI.</span></h1>
        <p class="hero-sub">A complete ecosystem for library management and book lovers. Track inventory, issue books, get AI recommendations, and join a thriving social community of readers — all in one place.</p>
        <div class="hero-actions">
          <a href="/login" class="hero-btn hero-btn-primary"><i class="bi bi-rocket-takeoff-fill"></i> Get Started Free</a>
          <a href="/features" class="hero-btn hero-btn-secondary"><i class="bi bi-grid-3x3-gap-fill"></i> Explore Features</a>
        </div>
        <div class="hero-stats">
          <div><div class="hs-num count-up" data-target="''' + str(s["total_books"]) + r'''">''' + str(s["total_books"]) + r'''</div><div class="hs-label">Books</div></div>
          <div><div class="hs-num count-up" data-target="''' + str(s["total_users"]) + r'''">''' + str(s["total_users"]) + r'''</div><div class="hs-label">Readers</div></div>
          <div><div class="hs-num count-up" data-target="''' + str(s["total_txns"]) + r'''">''' + str(s["total_txns"]) + r'''</div><div class="hs-label">Transactions</div></div>
          <div><div class="hs-num count-up" data-target="''' + str(len(posts)) + r'''">''' + str(len(posts)) + r'''</div><div class="hs-label">Posts</div></div>
        </div>
      </div>
      <div class="col-lg-5 d-none d-lg-block">
        <div class="hero-visual-inner" style="animation:float 6s ease-in-out infinite;">
          <div class="code-block">
            <div><span class="cm">// LibraryMS v3.0</span></div>
            <div>&nbsp;</div>
            <div><span class="kw">Library</span> lib = <span class="kw">new</span> Library();</div>
            <div>lib.<span class="kw">addBook</span>(<span class="str">"The Great Gatsby"</span>);</div>
            <div>lib.<span class="kw">recommend</span>(user, { <span class="str">genre</span>: <span class="str">"Fiction"</span> });</div>
            <div>&nbsp;</div>
            <div><span class="cm">// BookSocial feed</span></div>
            <div>feed.<span class="kw">createPost</span>(<span class="str">"Just finished reading..."</span>);</div>
            <div>feed.<span class="kw">connect</span>(reader);</div>
            <div>&nbsp;</div>
            <div><span class="kw">return</span> <span class="str">"Library + Community + AI"</span>;</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="container py-5" id="features">
  <div class="text-center mb-5">
    <span class="badge" style="background:var(--primary)15;color:var(--primary);font-size:.8rem;padding:.4rem 1.2rem;border-radius:50px;">Everything You Need</span>
    <h2 class="fw-bold mt-3" style="font-size:2.5rem;">Two Powerful Platforms,<br><span style="background:linear-gradient(135deg,#4f46e5,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">One Unified Experience</span></h2>
  </div>
  <div class="row g-4 justify-content-center">
    <div class="col-lg-4 col-md-6">
      <div class="glass-card p-4 h-100 text-center" style="border-top:4px solid #4f46e5;">
        <div class="feature-icon-box" style="background:linear-gradient(135deg,#4f46e5,#7c3aed);"><i class="bi bi-building"></i></div>
        <h5 style="font-weight:700;">Library Management</h5>
        <p style="color:var(--text-muted);font-size:.9rem;">Complete inventory control with issue/return tracking, fine management, category organization, and CSV export.</p>
      </div>
    </div>
    <div class="col-lg-4 col-md-6">
      <div class="glass-card p-4 h-100 text-center" style="border-top:4px solid #f59e0b;">
        <div class="feature-icon-box" style="background:linear-gradient(135deg,#f59e0b,#d97706);"><i class="bi bi-stars"></i></div>
        <h5 style="font-weight:700;">AI Recommendations</h5>
        <p style="color:var(--text-muted);font-size:.9rem;">Smart book suggestions based on borrowing history, trending titles, similar books, and co-borrowed patterns.</p>
      </div>
    </div>
    <div class="col-lg-4 col-md-6">
      <div class="glass-card p-4 h-100 text-center" style="border-top:4px solid #10b981;">
        <div class="feature-icon-box" style="background:linear-gradient(135deg,#10b981,#059669);"><i class="bi bi-graph-up-arrow"></i></div>
        <h5 style="font-weight:700;">Analytics & Reports</h5>
        <p style="color:var(--text-muted);font-size:.9rem;">Beautiful charts, monthly trends, category breakdowns, overdue tracking, and exportable reports with Chart.js.</p>
      </div>
    </div>
    <div class="col-lg-4 col-md-6">
      <div class="glass-card p-4 h-100 text-center" style="border-top:4px solid #a855f7;">
        <div class="feature-icon-box" style="background:linear-gradient(135deg,#a855f7,#7c3aed);"><i class="bi bi-rss-fill"></i></div>
        <h5 style="font-weight:700;">BookSocial Feed</h5>
        <p style="color:var(--text-muted);font-size:.9rem;">Real-time social feed with posts, likes, comments, book tagging, image uploads, and Reddit-style voting.</p>
      </div>
    </div>
    <div class="col-lg-4 col-md-6">
      <div class="glass-card p-4 h-100 text-center" style="border-top:4px solid #0ea5e9;">
        <div class="feature-icon-box" style="background:linear-gradient(135deg,#0ea5e9,#0891b2);"><i class="bi bi-people-fill"></i></div>
        <h5 style="font-weight:700;">Profiles & Community</h5>
        <p style="color:var(--text-muted);font-size:.9rem;">Rich user profiles with reading stats, custom bookshelves, following/followers, badges, and achievements.</p>
      </div>
    </div>
    <div class="col-lg-4 col-md-6">
      <div class="glass-card p-4 h-100 text-center" style="border-top:4px solid #ec4899;">
        <div class="feature-icon-box" style="background:linear-gradient(135deg,#ec4899,#db2777);"><i class="bi bi-search-heart-fill"></i></div>
        <h5 style="font-weight:700;">Advanced Search</h5>
        <p style="color:var(--text-muted);font-size:.9rem;">Unified search across books, users, posts, reviews, and Goodreads seed data with faceted filters and live suggestions.</p>
      </div>
    </div>
  </div>
</div>

<div class="stats-banner">
  <div class="container">
    <div class="row text-center g-4">
      <div class="col-6 col-md-3"><div class="snum count-up" data-target="''' + str(s["total_books"]) + r'''">''' + str(s["total_books"]) + r'''</div><div class="slabel">Books in Library</div></div>
      <div class="col-6 col-md-3"><div class="snum count-up" data-target="''' + str(s["total_users"]) + r'''">''' + str(s["total_users"]) + r'''</div><div class="slabel">Registered Users</div></div>
      <div class="col-6 col-md-3"><div class="snum count-up" data-target="''' + str(s["total_txns"]) + r'''">''' + str(s["total_txns"]) + r'''</div><div class="slabel">Transactions</div></div>
      <div class="col-6 col-md-3"><div class="snum count-up" data-target="''' + str(len(posts)) + r'''">''' + str(len(posts)) + r'''</div><div class="slabel">Social Posts</div></div>
    </div>
  </div>
</div>

<div class="container py-4">
  <div class="text-center mb-4">
    <h3 class="fw-bold">Trending Books <span class="badge bg-warning text-dark" style="font-size:.6rem;">HOT</span></h3>
    <p class="text-muted">Most popular titles in the library</p>
  </div>
  <div class="row g-3 justify-content-center">''' + featured_cards + r'''</div>
</div>

<div class="container py-4">
  <div class="text-center mb-4">
    <h3 class="fw-bold">Browse by Category</h3>
    <p class="text-muted">''' + str(len(BOOK_CATEGORIES)) + r''' categories available</p>
  </div>
  <div class="row g-3">''' + cat_boxes + r'''</div>
</div>

<div class="container py-5 text-center">
  <div class="cta-box">
    <h2 class="fw-bold mb-3">Ready to Get Started?</h2>
    <p class="text-muted mb-4" style="max-width:500px;margin:0 auto 1.5rem;">Join ''' + str(s["total_users"]) + r''' readers and manage ''' + str(s["total_books"]) + r''' books with AI-powered recommendations and a thriving social community.</p>
    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
      <a href="/login" class="btn btn-primary btn-lg"><i class="bi bi-rocket-takeoff-fill me-2"></i>Sign In</a>
      <a href="/features" class="btn btn-outline btn-lg"><i class="bi bi-info-circle me-2"></i>Learn More</a>
      <small class="d-block w-100 text-muted mt-2">Demo: <code>ADMIN001</code> / <code>admin123</code></small>
    </div>
  </div>
</div>

<div style="border-top:1px solid var(--border);padding:2rem 0;margin-top:2rem;">
  <div class="container">
    <div class="row">
      <div class="col-md-6 mb-3">
        <h6 class="fw-bold"><i class="bi bi-book-fill me-2 text-primary"></i>LibraryMS + BookSocial</h6>
        <p style="font-size:.8rem;color:var(--text-muted);max-width:350px;">A complete library management system with AI recommendations and a social reading community.</p>
      </div>
      <div class="col-6 col-md-3 mb-3">
        <h6 style="font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--text-muted);">Platform</h6>
        <div style="display:flex;flex-direction:column;gap:.3rem;font-size:.8rem;">
          <a href="/login" style="color:var(--text);">Dashboard</a>
          <a href="/books" style="color:var(--text);">Books</a>
          <a href="/recommendations" style="color:var(--text);">Recommendations</a>
          <a href="/features" style="color:var(--text);">All Features</a>
        </div>
      </div>
      <div class="col-6 col-md-3 mb-3">
        <h6 style="font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--text-muted);">Social</h6>
        <div style="display:flex;flex-direction:column;gap:.3rem;font-size:.8rem;">
          <a href="/feed" style="color:var(--text);">Feed</a>
          <a href="/search" style="color:var(--text);">Search</a>
          <a href="/welcome" style="color:var(--text);">About</a>
        </div>
      </div>
    </div>
    <hr style="border-color:var(--border);margin:1.5rem 0 1rem;">
    <p style="font-size:.75rem;color:var(--text-muted);text-align:center;">&copy; 2026 LibraryMS v3.0 &bull; Built with Flask + Socket.IO</p>
  </div>
</div>
</div>'''

        return render_page("LibraryMS + BookSocial", content)

    # ═══════════════════════════════════════════════════════════
    # FEATURES PAGE
    # ═══════════════════════════════════════════════════════════

    @app.route("/features")
    def features_page():
        """Showcase all platform features."""
        s = _library_stats()
        books = storage.load_books()
        all_books = [b for b in books.values() if not b.is_deleted]
        posts = storage.load_posts() if hasattr(storage, 'load_posts') else []
        reviews_data = storage.load_reviews() if hasattr(storage, 'load_reviews') else []

        content = r'''<div class="page-wrapper">
<div class="container py-4">
  <div class="text-center mb-5">
    <span class="badge" style="background:var(--primary)15;color:var(--primary);font-size:.8rem;padding:.4rem 1.2rem;border-radius:50px;">v3.0</span>
    <h1 class="fw-bold mt-3" style="font-size:2.8rem;">Everything in <span style="background:linear-gradient(135deg,#4f46e5,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">One Platform</span></h1>
    <p class="text-muted" style="max-width:600px;margin:0 auto;">''' + str(s['total_books']) + ''' books, ''' + str(s['total_users']) + ''' users, and a complete social reading community</p>
  </div>

  <section class="glass-card p-4 mb-4" aria-labelledby="lib-mgmt-title">
    <h2 id="lib-mgmt-title" class="section-title"><i class="bi bi-building text-primary"></i> Library Management System</h2>
    <div class="row g-3 mt-2">
      <div class="col-md-6"><div class="d-flex gap-3"><div style="width:44px;height:44px;border-radius:10px;background:#4f46e515;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="bi bi-book-fill" style="color:#4f46e5;"></i></div><div><h6 class="fw-bold mb-1">Book Inventory</h6><p class="small text-muted mb-0">Full CRUD for books with title, author, ISBN, category, copies tracking. Search, filter, and export to CSV.</p></div></div></div>
      <div class="col-md-6"><div class="d-flex gap-3"><div style="width:44px;height:44px;border-radius:10px;background:#05966915;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="bi bi-arrow-left-right" style="color:#059669;"></i></div><div><h6 class="fw-bold mb-1">Issue & Return</h6><p class="small text-muted mb-0">Track book checkouts and returns with due dates, fine calculation (Rs. ''' + str(Config.FINE_PER_DAY) + '''/day), and reservation queue.</p></div></div></div>
      <div class="col-md-6"><div class="d-flex gap-3"><div style="width:44px;height:44px;border-radius:10px;background:#d9770615;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="bi bi-currency-rupee" style="color:#d97706;"></i></div><div><h6 class="fw-bold mb-1">Fine Management</h6><p class="small text-muted mb-0">Automatic fine calculation, overdue tracking, payment recording, and membership status management.</p></div></div></div>
      <div class="col-md-6"><div class="d-flex gap-3"><div style="width:44px;height:44px;border-radius:10px;background:#8b5cf615;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="bi bi-people-fill" style="color:#8b5cf6;"></i></div><div><h6 class="fw-bold mb-1">User Management</h6><p class="small text-muted mb-0">Register users with roles (admin/librarian/user), manage membership, view borrowing history and stats.</p></div></div></div>
    </div>
  </div>

  <div class="glass-card p-4 mb-4">
    <div class="section-title"><i class="bi bi-graph-up-arrow text-success"></i> Analytics & Reports</div>
    <div class="row g-3 mt-2">
      <div class="col-md-4"><div class="d-flex gap-3"><div style="width:44px;height:44px;border-radius:10px;background:#10b98115;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="bi bi-bar-chart-fill" style="color:#10b981;"></i></div><div><h6 class="fw-bold mb-1">Dashboard</h6><p class="small text-muted mb-0">Live stats with Chart.js — monthly trends, weekly activity, category breakdown. Animated count-ups.</p></div></div></div>
      <div class="col-md-4"><div class="d-flex gap-3"><div style="width:44px;height:44px;border-radius:10px;background:#3b82f615;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="bi bi-stars" style="color:#3b82f6;"></i></div><div><h6 class="fw-bold mb-1">Recommendations</h6><p class="small text-muted mb-0">AI-powered personalized, trending, similar, and co-borrowed book recommendations with Goodreads integration.</p></div></div></div>
      <div class="col-md-4"><div class="d-flex gap-3"><div style="width:44px;height:44px;border-radius:10px;background:#ef444415;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="bi bi-exclamation-triangle-fill" style="color:#ef4444;"></i></div><div><h6 class="fw-bold mb-1">Overdue Alerts</h6><p class="small text-muted mb-0">Automatic overdue detection with email reminders. Badge notifications for blocked and expiring memberships.</p></div></div></div>
    </div>
  </div>

  <div class="glass-card p-4 mb-4">
    <div class="section-title"><i class="bi bi-rss-fill" style="color:#a855f7;"></i> BookSocial Platform</div>
    <div class="row g-3 mt-2">
      <div class="col-md-6"><div class="d-flex gap-3"><div style="width:44px;height:44px;border-radius:10px;background:#a855f715;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="bi bi-rss-fill" style="color:#a855f7;"></i></div><div><h6 class="fw-bold mb-1">Social Feed</h6><p class="small text-muted mb-0">Real-time feed with following/trending/discover tabs. Posts support book tagging, image uploads, hashtags, and Reddit-style voting.</p></div></div></div>
      <div class="col-md-6"><div class="d-flex gap-3"><div style="width:44px;height:44px;border-radius:10px;background:#ec489915;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="bi bi-chat-dots-fill" style="color:#ec4899;"></i></div><div><h6 class="fw-bold mb-1">Comments & Real-time</h6><p class="small text-muted mb-0">Threaded comments with Socket.IO real-time updates. Typing indicators and read receipts included.</p></div></div></div>
      <div class="col-md-6"><div class="d-flex gap-3"><div style="width:44px;height:44px;border-radius:10px;background:#0ea5e915;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="bi bi-person-fill" style="color:#0ea5e9;"></i></div><div><h6 class="fw-bold mb-1">Profiles & Bookshelves</h6><p class="small text-muted mb-0">Rich profiles with reading stats, custom bookshelves (Want to Read/Reading/Read), follow system, and avatar upload.</p></div></div></div>
      <div class="col-md-6"><div class="d-flex gap-3"><div style="width:44px;height:44px;border-radius:10px;background:#f59e0b15;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="bi bi-trophy-fill" style="color:#f59e0b;"></i></div><div><h6 class="fw-bold mb-1">Gamification</h6><p class="small text-muted mb-0">Achievements, badges, leaderboard, and XP points for posts, reviews, likes, and community participation.</p></div></div></div>
    </div>
  </div>

  <div class="glass-card p-4 mb-4">
    <div class="section-title"><i class="bi bi-gear-fill text-secondary"></i> Technical Details</div>
    <div class="row g-3 mt-2">
      <div class="col-6 col-md-3"><div class="text-center p-3" style="background:var(--primary-light);border-radius:10px;"><div class="fw-bold" style="font-size:1.3rem;">''' + str(len(all_books)) + '''</div><small class="text-muted">Books</small></div></div>
      <div class="col-6 col-md-3"><div class="text-center p-3" style="background:var(--primary-light);border-radius:10px;"><div class="fw-bold" style="font-size:1.3rem;">''' + str(len(storage.load_users())) + '''</div><small class="text-muted">Users</small></div></div>
      <div class="col-6 col-md-3"><div class="text-center p-3" style="background:var(--primary-light);border-radius:10px;"><div class="fw-bold" style="font-size:1.3rem;">''' + str(len(BOOK_CATEGORIES)) + '''</div><small class="text-muted">Categories</small></div></div>
      <div class="col-6 col-md-3"><div class="text-center p-3" style="background:var(--primary-light);border-radius:10px;"><div class="fw-bold" style="font-size:1.3rem;">''' + str(len(posts)) + '''</div><small class="text-muted">Social Posts</small></div></div>
    </div>
    <div class="mt-4" style="font-size:.8rem;color:var(--text-muted);">
      <strong>Tech Stack:</strong> Python 3 &bull; Flask &bull; Socket.IO (WebSockets) &bull; Chart.js &bull; Bootstrap 5 &bull; Google Fonts (Inter) &bull; JSON storage
      <br><strong>Features:</strong> Real-time updates &bull; Dark/Light theme &bull; Ctrl+K search &bull; AI recommendations &bull; CSV export &bull; Print support &bull; Responsive design
      <br><strong>Social:</strong> Book tagging &bull; Image uploads &bull; Custom shelves &bull; Follow system &bull; Achievements &bull; Leaderboard &bull; Typing indicators &bull; Read receipts
    </div>
  </div>

  <div class="text-center mb-4">
    <a href="/login" class="btn btn-primary btn-lg"><i class="bi bi-rocket-takeoff-fill me-2"></i>Get Started</a>
    <a href="/" class="btn btn-outline btn-lg ms-2"><i class="bi bi-arrow-left me-2"></i>Back to Home</a>
  </div>
</div>
</div>'''

        return render_page("Features", content)

    # ═══════════════════════════════════════════════════════════
    # WELCOME / BOOKSOCIAL ONBOARDING
    # ═══════════════════════════════════════════════════════════

    @app.route("/welcome")
    def welcome_page():
        """BookSocial welcome/onboarding page."""
        uid = session.get("user_id")
        user = get_current_user() if uid else None

        posts = storage.load_posts() if hasattr(storage, 'load_posts') else []
        reviews_data = storage.load_reviews() if hasattr(storage, 'load_reviews') else []
        following_count = 0
        follower_count = 0
        if user and social:
            try:
                following_count = social.get_following_count(uid)
                follower_count = social.get_follower_count(uid)
            except:
                pass

        greeting = "Welcome to BookSocial!" + (", " + h(user.name) if user else "")
        profile_link = "/profile/" + h(uid) if uid else "/login"
        feed_link = "/feed" if uid else "/login"

        content = r'''<div class="page-wrapper">
<style>
.welcome-step{text-align:center;padding:2rem 1rem;transition:all .3s ease}
.welcome-step:hover{transform:translateY(-4px)}
.welcome-step .step-num{width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#4f46e5,#7c3aed);color:white;display:flex;align-items:center;justify-content:center;font-weight:700;margin:0 auto .8rem;font-size:1.1rem}
.welcome-step h6{font-weight:700}
.welcome-step p{font-size:.85rem;color:var(--text-muted);max-width:300px;margin:0 auto}
</style>
<div class="container py-4">
  <div class="glass-card p-5 text-center mb-4" style="background:linear-gradient(135deg,#4f46e520,#7c3aed20);">
    <div style="font-size:3rem;margin-bottom:.5rem;">\U0001f4da</div>
    <h2 class="fw-bold mb-2">''' + greeting + r'''</h2>
    <p class="text-muted mb-0" style="max-width:500px;margin:0 auto;">Your reading community awaits. Connect with other readers, share book recommendations, and track your reading journey.</p>
  </div>

  <div class="row g-4 mb-4">
    <div class="col-md-4"><div class="glass-card p-3 welcome-step h-100"><div class="step-num">1</div><h6>Create Your Profile</h6><p>Add a bio, location, favorite genres, and profile picture to tell others about your reading taste.</p><a href="''' + profile_link + r'''" class="btn btn-sm btn-outline mt-2"><i class="bi bi-person-fill"></i> My Profile</a></div></div>
    <div class="col-md-4"><div class="glass-card p-3 welcome-step h-100"><div class="step-num">2</div><h6>Explore the Feed</h6><p>See what others are reading, discover trending posts, and join conversations about books.</p><a href="''' + feed_link + r'''" class="btn btn-sm btn-outline mt-2"><i class="bi bi-rss-fill"></i> Open Feed</a></div></div>
    <div class="col-md-4"><div class="glass-card p-3 welcome-step h-100"><div class="step-num">3</div><h6>Build Your Shelves</h6><p>Create custom bookshelves, add books to Want to Read/Reading/Read, and write reviews.</p><a href="''' + profile_link + r'''" class="btn btn-sm btn-outline mt-2"><i class="bi bi-bookmark-fill"></i> My Shelves</a></div></div>
  </div>

  <div class="row g-3">
    <div class="col-md-3"><div class="glass-card p-3 text-center h-100"><div style="font-size:1.8rem;font-weight:700;color:var(--primary);">''' + str(len(posts)) + r'''</div><small class="text-muted">Community Posts</small></div></div>
    <div class="col-md-3"><div class="glass-card p-3 text-center h-100"><div style="font-size:1.8rem;font-weight:700;color:var(--success);">''' + str(len(reviews_data)) + r'''</div><small class="text-muted">Book Reviews</small></div></div>
    <div class="col-md-3"><div class="glass-card p-3 text-center h-100"><div style="font-size:1.8rem;font-weight:700;color:var(--warning);">''' + str(following_count) + r'''</div><small class="text-muted">Following</small></div></div>
    <div class="col-md-3"><div class="glass-card p-3 text-center h-100"><div style="font-size:1.8rem;font-weight:700;color:var(--info);">''' + str(follower_count) + r'''</div><small class="text-muted">Followers</small></div></div>
  </div>

  <div class="text-center mt-4">
    <a href="''' + feed_link + r'''" class="btn btn-primary btn-lg"><i class="bi bi-rss-fill me-2"></i>Go to Feed</a>
    <a href="/search" class="btn btn-outline btn-lg ms-2"><i class="bi bi-search me-2"></i>Discover Books</a>
    <a href="/" class="btn btn-outline btn-lg ms-2"><i class="bi bi-house me-2"></i>Home</a>
  </div>
</div>
</div>'''

        return render_page("Welcome to BookSocial", content)

    return app
