"""web_app.py - Library Management System Web Interface
Modern features: issue/return modals, autocomplete search, keyboard shortcuts,
loading skeletons, print-friendly CSS, avatar initials, PDF export.
"""

import os, sys, html, csv, io, json, random
from datetime import datetime, timedelta
from functools import wraps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if sys.platform == "win32":
    import io as _io
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import (Flask, render_template_string, request, jsonify,
                   redirect, url_for, session, Response)
from flask_cors import CORS
from book import CATEGORIES as BOOK_CATEGORIES
from storage import Storage
from library import Library
from auth import AuthManager, hash_password
from recommender import Recommender
from notifications import NotificationManager
from config import Config
from logger import log
from social_routes import init_social_routes
from site_pages import init_site_pages
from lists import BookLists
from communities import Communities
from gamification import Gamification
from series import SeriesManager
from reading_challenge import ReadingChallenge
from reading_progress import ReadingProgress
from wishlist import Wishlist
from diary import DiaryManager

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
CORS(app)
storage = Storage()
lib = Library(storage)
auth = AuthManager(storage)
recommender = Recommender(storage)
notif_mgr = NotificationManager(storage)
from main import bootstrap
bootstrap(storage, auth)

# Initialize social modules
from social import SocialFeed
from reviews import ReviewManager
from realtime import init_socketio as _init_socketio
socketio = _init_socketio(app, storage)
social = SocialFeed(storage)
review_mgr = ReviewManager(storage)
book_lists = BookLists(storage)
communities = Communities(storage)
gamification = Gamification(storage)
series_mgr = SeriesManager(storage)
challenge = ReadingChallenge(storage)
reading_progress = ReadingProgress(storage)
wishlist = Wishlist(storage)
diary_mgr = DiaryManager(storage)

# Register social routes
init_social_routes(app, storage, lib, auth, social, review_mgr, recommender, notif_mgr, book_lists, communities, gamification)

# Register new feature routes
from new_features_routes import init_new_features_routes
init_new_features_routes(app, storage, lib, auth, notif_mgr, series_mgr, challenge, reading_progress, wishlist, diary_mgr)
init_site_pages(app, storage, lib, recommender, social, review_mgr, notif_mgr)

def h(text): return html.escape(str(text))
def login_required(f):
    @wraps(f)
    def d(*a,**k):
        if "user_id" not in session: return redirect(url_for("login_page"))
        return f(*a,**k)
    return d
def admin_required(f):
    @wraps(f)
    def d(*a,**k):
        if "user_id" not in session: return redirect(url_for("login_page"))
        if session.get("role") != "admin": return jsonify({"error":"Admin access required"}),403
        return f(*a,**k)
    return d
def get_current_user():
    if "user_id" not in session: return None
    return storage.load_users().get(session["user_id"])
def render_page(title, content, **kw):
    user = get_current_user()
    return render_template_string(BASE_HTML+content+FOOTER_HTML, title=title,
        session=session, notif_count=notif_mgr.get_unread_count(user.user_id) if user else 0, **kw)

# ─── HELPERS ────────────────────────────────────────────────────────
def _load_library_data():
    return storage.load_books(), storage.load_users(), storage.load_transactions()

def _library_stats():
    books, users, txns = _load_library_data()
    all_books = [b for b in books.values() if not b.is_deleted]
    now = datetime.now(); tms = datetime(now.year, now.month, 1)
    total_books = len(all_books); total_copies = sum(b.total_copies for b in all_books)
    avail_copies = sum(b.available_copies for b in all_books)
    issued_copies = total_copies - avail_copies
    avail_rate = (avail_copies/total_copies*100) if total_copies else 0
    new_books_month = sum(1 for b in all_books if datetime.fromisoformat(b.added_on)>=tms)
    total_users = len(users); active_users = sum(1 for u in users.values() if u.membership_status=="Active")
    blocked_users = sum(1 for u in users.values() if u.membership_status=="Blocked")
    new_users_month = sum(1 for u in users.values() if hasattr(u,'added_on') and u.added_on and datetime.fromisoformat(u.added_on)>=tms)
    issues = [t for t in txns if t["type"]=="issue"]
    returns = [t for t in txns if t["type"]=="return"]
    active_issues = [t for t in issues if t.get("return_date") is None]
    total_txns = len(txns); month_txns = sum(1 for t in txns if datetime.fromisoformat(t.get("issue_date",""))>=tms)
    unique_borrowers = len(set(t["user_id"] for t in issues))
    fines = storage.load_fines()
    total_fines = sum(f.get("amount",0) for f in fines)
    paid_fines = sum(f.get("amount",0) for f in fines if f.get("paid"))
    pending_fines = total_fines - paid_fines
    avg_bpu = round(len(issues)/total_users,1) if total_users else 0
    return {"total_books":total_books,"total_copies":total_copies,"avail_copies":avail_copies,
        "issued_copies":issued_copies,"avail_rate":round(avail_rate,1),"new_books_month":new_books_month,
        "total_users":total_users,"active_users":active_users,"blocked_users":blocked_users,
        "new_users_month":new_users_month,"total_issues":len(issues),"total_returns":len(returns),
        "active_issues":len(active_issues),"total_txns":total_txns,"month_txns":month_txns,
        "unique_borrowers":unique_borrowers,"avg_books_per_user":avg_bpu,
        "total_fines":round(total_fines,2),"paid_fines":round(paid_fines,2),"pending_fines":round(pending_fines,2)}

def _book_borrowing_history(book_id):
    txns = storage.load_transactions(); users = storage.load_users()
    history = []
    for t in txns:
        if t["book_id"] == book_id:
            u = users.get(t["user_id"])
            history.append({**t,"user_name":u.name if u else t["user_id"],
                "issue_date_fmt":t.get("issue_date","")[:19],
                "return_date_fmt":t.get("return_date","")[:19] if t.get("return_date") else None})
    return sorted(history, key=lambda x: x.get("issue_date",""), reverse=True)

def _initials(name):
    """Generate initials from a name, up to 2 characters."""
    parts = name.strip().split()
    if not parts: return "?"
    if len(parts) >= 2: return (parts[0][0] + parts[-1][0]).upper()
    return parts[0][:2].upper()

def _avatar_color(name):
    """Generate a deterministic color from a name."""
    colors = ["#4f46e5","#059669","#d97706","#dc2626","#0891b2","#7c3aed","#db2777","#ca8a04"]
    return colors[hash(name) % len(colors)]

def _avatar_html(name, size=32):
    """Generate an avatar circle with initials."""
    i = _initials(name); c = _avatar_color(name)
    return f'<div class="avatar" style="width:{size}px;height:{size}px;background:{c}20;color:{c};font-size:{size//2}px;font-weight:700;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;" title="{h(name)}">{h(i)}</div>'

CAT_COLORS = {"Fiction":"#4f46e5","Non-Fiction":"#059669","Science":"#0891b2","Technology":"#7c3aed",
    "History":"#d97706","Philosophy":"#be185d","Art":"#db2777","Biography":"#ca8a04","Children":"#16a34a",
    "Comics":"#e11d48","Poetry":"#9333ea","Drama":"#ea580c","Education":"#2563eb","Reference":"#64748b",
    "Religion":"#78716c","Self-Help":"#0d9488","Cooking":"#f97316","Travel":"#0ea5e9","Music":"#8b5cf6",
    "Sports":"#22c55e","Other":"#6b7280"}
def cat_color(c): return CAT_COLORS.get(c, CAT_COLORS["Other"])

# Make helper functions available in Jinja2 templates
app.jinja_env.globals['_avatar_html'] = _avatar_html
app.jinja_env.globals['_initials'] = _initials

# ─── HTML TEMPLATES ──────────────────────────────────────────────────

BASE_HTML = r"""<!DOCTYPE html><html lang="en" data-theme="light">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#7c6af7">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="manifest" href="/static/manifest.json">
<link rel="apple-touch-icon" href="/static/icons/booktale-192.svg">
<title>{{ title }} — BookTale</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://covers.openlibrary.org">
<link rel="preconnect" href="https://www.googleapis.com">
<link rel="dns-prefetch" href="//cdn.jsdelivr.net">
<link rel="dns-prefetch" href="//fonts.googleapis.com">
<link rel="dns-prefetch" href="//fonts.gstatic.com">
<link rel="dns-prefetch" href="//covers.openlibrary.org">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js" defer></script>
<style>
:root{--primary:#4f46e5;--primary-dark:#4338ca;--primary-light:#eef2ff;--primary-glow:rgba(79,70,229,.25);--bg:#f8fafc;--bg-card:#fff;--text:#0f172a;--text-muted:#536471;--text-dim:#94a3b8;--border:#eff3f4;--success:#10b981;--warning:#f59e0b;--danger:#ef4444;--info:#3b82f6;--radius:16px;--radius-sm:10px;--font:'Poppins','Inter','Segoe UI',system-ui,-apple-system,sans-serif;--ease:cubic-bezier(.4,0,.2,1);--ease-out:cubic-bezier(0,.55,.45,1);--ease-spring:cubic-bezier(.34,1.56,.64,1);--sidebar-width:275px;--right-sidebar-width:350px}
[data-theme="dark"]{--bg:#000;--bg-card:#16181c;--text:#e7e9ea;--text-muted:#71767b;--text-dim:#536471;--border:#2f3336;--primary-light:#1d1f23}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
:focus-visible{outline:0.125rem solid var(--primary);outline-offset:0.125rem;box-shadow:0 0 0 3px var(--primary-glow)}
:focus:not(:focus-visible){outline:none;box-shadow:none}
body{background:var(--bg);color:var(--text);font-family:var(--font);min-height:100vh;overflow-x:hidden;opacity:0;animation:bodyFadeIn .4s var(--ease) forwards}
::selection{background:var(--primary);color:white}
@keyframes bodyFadeIn{from{opacity:0}to{opacity:1}}

/* ── Twitter/X Layout ── */
.app-layout{display:flex;justify-content:center;max-width:1280px;margin:0 auto;min-height:100vh}

/* ── Left Sidebar ── */
.sidebar{position:sticky;top:0;height:100vh;width:var(--sidebar-width);padding:0 12px;display:flex;flex-direction:column;overflow-y:auto;flex-shrink:0}
.sidebar-logo{padding:12px 12px 2px;font-size:1.5rem;font-weight:800;color:var(--primary)}
.sidebar-logo a{color:var(--primary);text-decoration:none}
.sidebar-logo a:hover{color:var(--primary-dark)}
.sidebar-nav{flex:1;padding:4px 0}
.nav-item-a{display:flex;align-items:center;gap:16px;padding:12px;border-radius:9999px;color:var(--text);text-decoration:none;font-size:1.1rem;font-weight:400;transition:all .2s var(--ease);cursor:pointer}
.nav-item-a:hover{background:rgba(79,70,229,.08);color:var(--primary)}
.nav-item-a.active{font-weight:700;color:var(--text)}
.nav-item-a .nav-icon{font-size:1.4rem;width:1.4rem;text-align:center}
.nav-item-a .nav-label{font-size:1.1rem;white-space:nowrap}
.sidebar-post-btn{background:var(--primary);color:white;border:none;border-radius:9999px;padding:12px 24px;font-size:1rem;font-weight:700;cursor:pointer;transition:all .2s;margin:8px 0;width:90%}
.sidebar-post-btn:hover{background:var(--primary-dark)}
.sidebar-user{display:flex;align-items:center;gap:10px;padding:12px;border-radius:9999px;margin-top:auto;cursor:pointer;transition:all .2s;position:relative;user-select:none}
.sidebar-user:hover{background:rgba(79,70,229,.08)}
.user-dropdown{position:absolute;bottom:calc(100% + 8px);left:0;right:0;background:var(--bg-card);border:1px solid var(--border);border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,.15);padding:6px;display:none;z-index:100;min-width:220px}
.user-dropdown.show{display:block;animation:fadeInUp .2s ease}
.user-dropdown-item{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:8px;color:var(--text);text-decoration:none;font-size:.9rem;transition:all .15s;cursor:pointer;border:none;background:none;width:100%;font-family:var(--font);text-align:left}
.user-dropdown-item:hover{background:var(--primary-light);color:var(--primary)}
.user-dropdown-item i{font-size:1.1rem;width:20px;text-align:center;flex-shrink:0}
.user-dropdown-item .dd-item-label{font-weight:500}
.user-dropdown-item .dd-item-desc{font-size:.75rem;color:var(--text-muted)}
.user-dropdown-divider{height:1px;background:var(--border);margin:4px 8px}
.user-dropdown-danger{color:var(--danger)!important}
.user-dropdown-danger:hover{background:rgba(239,68,68,.08)!important;color:var(--danger)!important}

/* ── Main Content ── */
.main-content{width:600px;flex-shrink:0;border-left:1px solid var(--border);border-right:1px solid var(--border);min-height:100vh}

/* ── Right Sidebar ── */
.right-sidebar{width:var(--right-sidebar-width);flex-shrink:0;padding:0 16px;position:sticky;top:0;height:100vh;overflow-y:auto;display:flex;flex-direction:column;gap:12px;padding-top:12px}
.rside-search{position:relative;margin-bottom:4px}
.rside-search input{width:100%;border:none;border-radius:9999px;background:var(--border);padding:12px 16px 12px 48px;font-size:.95rem;color:var(--text);outline:none;transition:all .2s}
.rside-search input:focus{background:var(--bg-card);border:1px solid var(--primary);box-shadow:0 0 0 1px var(--primary)}
.rside-search .search-icon{position:absolute;left:16px;top:50%;transform:translateY(-50%);color:var(--text-muted);font-size:1.1rem}
.rside-card{background:var(--border);border-radius:16px;padding:12px 0;overflow:hidden}
.rside-card .rside-header{padding:12px 16px;font-weight:800;font-size:1.1rem;border-bottom:1px solid var(--border)}
.rside-card .rside-item{padding:12px 16px;cursor:pointer;transition:all .2s;display:flex;align-items:center;gap:10px}
.rside-card .rside-item:hover{background:rgba(0,0,0,.03)}
.rside-card .rside-item .rside-rank{font-weight:700;color:var(--text-muted);font-size:.85rem;width:24px}
.rside-card .rside-item .rside-content{flex:1}
.rside-card .rside-item .rside-content .rside-title{font-weight:700;font-size:.9rem}
.rside-card .rside-item .rside-content .rside-meta{font-size:.8rem;color:var(--text-muted)}
.rside-card .rside-show-more{padding:12px 16px;color:var(--primary);font-size:.9rem;cursor:pointer;transition:all .2s;border-top:1px solid var(--border)}
.rside-card .rside-show-more:hover{background:rgba(0,0,0,.03)}
.rside-footer{font-size:.8rem;color:var(--text-muted);padding:8px 4px;display:flex;flex-wrap:wrap;gap:4px 12px}
.rside-footer a{color:var(--text-muted);text-decoration:none;font-size:.78rem}
.rside-footer a:hover{text-decoration:underline}

/* ── Tweet/Post Cards ── */
.post-card{display:flex;padding:12px 16px;border-bottom:1px solid var(--border);cursor:pointer;transition:all .15s;animation:fadeInUp .3s ease both}
.post-card:hover{background:rgba(0,0,0,.015)}
.vote-column{display:flex;flex-direction:column;align-items:center;gap:2px;min-width:34px;padding-top:2px}
.vote-btn{background:none;border:none;color:var(--text-muted);cursor:pointer;padding:4px;border-radius:9999px;font-size:1rem;line-height:1;transition:all .2s}
.vote-btn:hover{color:var(--primary);background:rgba(79,70,229,.08)}
.vote-btn.upvoted{color:var(--primary)}
.vote-btn.downvoted{color:var(--danger)}
.vote-score{font-weight:700;font-size:.75rem;color:var(--text-muted);line-height:1}
.vote-score.positive{color:var(--primary)}
.vote-score.negative{color:var(--danger)}
.post-card-body{flex:1;min-width:0;margin-left:0}
.post-card-header{display:flex;align-items:center;gap:8px;margin-bottom:4px}
.post-author-avatar{flex-shrink:0}
.post-author-name{font-weight:700;font-size:.95rem;color:var(--text);text-decoration:none}
.post-author-name:hover{text-decoration:underline}
.post-content-text{font-size:.95rem;line-height:1.5;margin:4px 0 8px;word-wrap:break-word}
.post-content-text a{color:var(--primary);text-decoration:none}
.post-content-text a:hover{text-decoration:underline}
.post-book-tag{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;border-radius:9999px;font-size:.8rem;font-weight:500;text-decoration:none;margin:4px 8px 4px 0;transition:all .2s}
.post-book-tag:hover{opacity:.8}
.post-images{display:flex;gap:4px;border-radius:16px;overflow:hidden;margin:8px 0}
.post-image{width:100%;max-height:300px;object-fit:cover;cursor:pointer;border-radius:16px;transition:all .3s}
.post-image:hover{opacity:.9}
.post-actions{display:flex;gap:48px;margin-top:4px;padding:4px 0}
.post-action{background:none;border:none;color:var(--text-muted);cursor:pointer;display:flex;align-items:center;gap:4px;font-size:.85rem;padding:4px 8px;border-radius:9999px;transition:all .2s}
.post-action:hover{color:var(--primary);background:rgba(79,70,229,.08)}
.post-action.liked{color:var(--danger)}
.post-action.liked:hover{background:rgba(239,68,68,.08)}

/* ── Compose Box ── */
.compose-box{display:flex;padding:12px 16px;border-bottom:8px solid var(--border)}
.compose-box textarea{flex:1;border:none;resize:none;font-size:1.15rem;padding:8px 0;background:transparent;color:var(--text);outline:none;font-family:var(--font);min-height:60px}
.compose-box textarea::placeholder{color:var(--text-muted)}
.compose-toolbar{display:flex;justify-content:space-between;align-items:center;padding-top:8px;border-top:1px solid var(--border);margin-top:4px}
.compose-toolbar .btn{border-radius:9999px;font-weight:700;padding:.4rem 1rem;font-size:.9rem;border:none;cursor:pointer;transition:all .2s}
.compose-toolbar .btn-primary{background:var(--primary);color:white}
.compose-toolbar .btn-primary:hover{background:var(--primary-dark)}
.compose-toolbar .btn-primary:disabled{opacity:.5;cursor:not-allowed}

/* ── Feed Tabs ── */
.feed-tab{flex:1;text-align:center;padding:12px 0;font-weight:500;color:var(--text-muted);text-decoration:none;border-bottom:2px solid transparent;transition:all .2s;cursor:pointer;font-size:.9rem}
.feed-tab:hover{background:rgba(79,70,229,.04);color:var(--text)}
.feed-tab.active{color:var(--text);font-weight:700;border-bottom-color:var(--primary)}

/* ── Comments Section ── */
.comments-section{padding:8px 0}
.comment-item{display:flex;gap:8px;padding:8px 0;border-bottom:1px solid var(--border)}
.comment-item.nested{margin-left:32px}
.comment-item.deep-nested{margin-left:64px}
.comment-body{flex:1;min-width:0}
.comment-author{font-weight:700;font-size:.85rem;color:var(--text);text-decoration:none}
.comment-text{font-size:.85rem;line-height:1.4;margin:2px 0}
.comment-meta{display:flex;gap:12px;font-size:.75rem;color:var(--text-muted);margin-top:4px}
.comment-reply-btn{background:none;border:none;color:var(--text-muted);cursor:pointer;font-size:.75rem;padding:0}
.comment-reply-btn:hover{color:var(--primary)}
.typing-indicator{display:flex;align-items:center;gap:4px;padding:4px 8px;font-size:.75rem;color:var(--text-muted)}
.typing-dots span{display:inline-block;width:4px;height:4px;border-radius:50%;background:var(--text-muted);animation:typingDot 1.4s infinite;margin:0 1px}
.typing-dots span:nth-child(2){animation-delay:.2s}
.typing-dots span:nth-child(3){animation-delay:.4s}
@keyframes typingDot{0%,60%,100%{opacity:.3}30%{opacity:1}}
.read-receipts{display:flex;align-items:center;gap:4px;padding:4px 8px;font-size:.7rem;color:var(--text-muted)}
.seen-by-text{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:200px}

/* ── Profile Page ── */
.profile-banner{height:200px;background:linear-gradient(135deg,#4f46e5,#a855f7);position:relative}
.profile-info-row{display:flex;gap:16px;padding:12px 16px 0}
.profile-avatar-wrapper{margin-top:-48px;flex-shrink:0}
.profile-avatar-wrapper .avatar{border:4px solid var(--bg-card)!important}
.profile-stats{display:flex;gap:16px;margin-top:8px}
.profile-stat .num{font-weight:700;font-size:1rem;color:var(--text)}
.profile-stat .label{font-size:.8rem;color:var(--text-muted)}
.shelf-book{padding:.6rem;border-radius:8px;margin-bottom:4px;cursor:pointer;transition:all .2s}
.shelf-book:hover{background:rgba(79,70,229,.04)}

/* ── Trending Sidebar ── */
.trending-item{padding:8px 0;cursor:pointer;transition:all .15s;border-bottom:1px solid var(--border)}
.trending-item:last-child{border-bottom:none}
.trending-item:hover{background:rgba(79,70,229,.02)}
.trending-rank{font-weight:700;color:var(--text-muted);font-size:.8rem}

/* ── Book Tag Autocomplete ── */
.book-tag-input-wrapper{position:relative}
.book-tag-dropdown{position:absolute;top:100%;left:0;right:0;background:var(--bg-card);border:1px solid var(--border);border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,.12);z-index:100;max-height:240px;overflow-y:auto}
.book-tag-item{display:flex;align-items:center;gap:8px;padding:8px 12px;cursor:pointer;transition:all .15s}
.book-tag-item:hover{background:var(--primary-light)}
.book-tag-pill{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:9999px;font-size:.75rem;background:rgba(79,70,229,.1);color:var(--primary);cursor:pointer;transition:all .2s}
.book-tag-pill:hover{background:rgba(79,70,229,.2)}

/* ── Verified Badge ── */
.verified-badge{display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:50%;background:var(--primary);color:white;font-size:.5rem;flex-shrink:0}

/* ── Modal ── */
.modal-content{background:var(--bg-card);border:1px solid var(--border);border-radius:16px}
.modal-header{border-bottom:1px solid var(--border);padding:1rem 1.25rem}
.modal-body{padding:1.25rem}
.modal-footer{border-top:1px solid var(--border);padding:.8rem 1.25rem}
.modal.fade .modal-dialog{transform:scale(.9) translateY(20px);transition:transform .35s var(--ease-spring)}
.modal.show .modal-dialog{transform:scale(1) translateY(0)}

/* ── Buttons ── */
.btn{border-radius:9999px;font-weight:700;padding:.5rem 1.2rem;transition:all .25s var(--ease);border:none;cursor:pointer;display:inline-flex;align-items:center;gap:6px;font-size:.9rem}
.btn-primary{background:var(--primary);color:white}
.btn-primary:hover{background:var(--primary-dark);transform:translateY(-1px)}
.btn-outline{background:transparent;border:1px solid var(--border);color:var(--text)}
.btn-outline:hover{border-color:var(--primary);color:var(--primary);background:var(--primary-light)}
.btn-sm{padding:.3rem .9rem;font-size:.8rem}

/* ── Forms ── */
.form-control,.form-select{background:var(--bg-card);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:.6rem 1rem;font-size:.9rem;transition:all .2s;width:100%}
.form-control:focus,.form-select:focus{border-color:var(--primary);outline:none;box-shadow:0 0 0 2px var(--primary-glow)}
.form-label{font-weight:600;font-size:.8rem;color:var(--text-muted);margin-bottom:.3rem}

/* ── Glass/Section Cards ── */
.glass-card{background:var(--bg-card);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid var(--border);border-radius:var(--radius);padding:1rem;margin-bottom:1rem;box-shadow:0 8px 32px rgba(0,0,0,.06);transition:all .35s ease}
.glass-card-static:hover{transform:none!important;box-shadow:none!important}
.glass-card:hover{box-shadow:0 8px 32px rgba(0,0,0,.06),0 0 0 1px rgba(79,70,229,.25),0 12px 40px rgba(79,70,229,.08);transform:translateY(-3px)!important}
.section-title{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--text-muted);margin-bottom:.8rem;display:flex;align-items:center;gap:.4rem}

/* ── Stats ── */
.stats-bar{display:flex;flex-wrap:wrap;gap:1rem;padding:.8rem 1rem;background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius)}
.stats-bar .stat-item{flex:1;min-width:80px}
.stats-bar .stat-item .num{font-size:1.3rem;font-weight:800}
.stats-bar .stat-item .desc{font-size:.7rem;color:var(--text-muted);text-transform:uppercase}
.info-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:.6rem}
.info-card{padding:.6rem;border-radius:8px;background:rgba(79,70,229,.04);border:1px solid var(--border);transition:all .2s}
.info-card:hover{background:rgba(79,70,229,.08)}
.info-card .value{font-size:1.1rem;font-weight:700}
.info-card .label{font-size:.6rem;color:var(--text-muted);text-transform:uppercase}

/* ── Badges ── */
.badge{border-radius:6px;padding:.3em .6em;font-weight:500;font-size:.75rem}
.badge-green{background:rgba(16,185,129,.12);color:#059669;font-weight:600}
.badge-red{background:rgba(239,68,68,.12);color:#dc2626;font-weight:600}
.nav-badge{position:absolute;top:-2px;right:-6px;font-size:.55rem;padding:.2em .45em;min-width:16px;border-radius:999px}

/* ── Tables ── */
.table{color:var(--text);margin-bottom:0;font-size:.9rem;width:100%}
.table th{font-weight:600;color:var(--text-muted);text-transform:uppercase;font-size:.7rem;letter-spacing:.8px;border-bottom:2px solid var(--border);padding:.75rem .5rem}
.table td{color:var(--text);vertical-align:middle;border-bottom:1px solid var(--border);padding:.7rem .5rem}
.table-hover tbody tr:hover{background:rgba(79,70,229,.04)}
.progress-thin{height:6px;border-radius:3px;background:var(--border);overflow:hidden}
.progress-thin .bar{height:100%;border-radius:3px;transition:width 1s var(--ease-out)}
.chart-container{position:relative;height:220px;width:100%}

/* ── Empty State ── */
.empty-state{text-align:center;padding:3rem 1rem;color:var(--text-muted)}
.empty-state .empty-icon{font-size:3rem;margin-bottom:1rem;opacity:.3}

/* ── Pagination ── */
.pagination .page-link{background:var(--bg-card);color:var(--text);border:1px solid var(--border);border-radius:8px;margin:0 2px;padding:.4rem .7rem;text-decoration:none}
.pagination .page-item.active .page-link{background:var(--primary);border-color:var(--primary);color:white}

/* ── Search Results ── */
.search-result-item{padding:.5rem .7rem;display:flex;align-items:center;gap:.7rem;cursor:pointer;transition:all .2s;border-bottom:1px solid var(--border)}
.search-result-item:last-child{border-bottom:none}
.search-result-item:hover{background:rgba(79,70,229,.04)}

/* ── Activity Feed ── */
.activity-item{padding:.6rem 0;border-bottom:1px solid var(--border);display:flex;align-items:flex-start;gap:.75rem;transition:all .2s}
.activity-icon{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0}

/* ── Overdue Items ── */
.overdue-item{border-left:4px solid var(--danger);background:rgba(239,68,68,.04);border-radius:8px;padding:.8rem 1rem;margin-bottom:.6rem;display:flex;align-items:center;gap:.8rem}

/* ── Welcome Hero ── */
.welcome-hero{background:linear-gradient(135deg,#4f46e5,#a855f7);border-radius:16px;padding:1.5rem 2rem;color:white;position:relative;overflow:hidden;margin-bottom:1.5rem}

/* ── Toast ── */
.toast-container{position:fixed;top:1rem;right:1rem;z-index:9999;display:flex;flex-direction:column;gap:.5rem}
.toast-msg{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:.8rem 1.2rem;box-shadow:0 8px 32px rgba(0,0,0,.1);display:flex;align-items:center;gap:.6rem;font-size:.9rem;min-width:300px;max-width:420px}
.toast-msg.success{border-left:4px solid var(--success)}
.toast-msg.error{border-left:4px solid var(--danger)}
.toast-msg.info{border-left:4px solid var(--info)}
.toast-msg .toast-progress{position:absolute;bottom:0;left:0;height:3px;border-radius:0 0 0 12px;animation:toastProgress 4s linear forwards}
.toast-msg.success .toast-progress{background:var(--success)}
.toast-msg.error .toast-progress{background:var(--danger)}
@keyframes toastProgress{from{width:100%}to{width:0%}}

/* ── Skeleton ── */
.skeleton{background:linear-gradient(90deg,var(--border) 25%,var(--bg-card) 50%,var(--border) 75%);background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:8px}
.skeleton-post{display:flex;gap:12px;padding:12px 16px;border-bottom:1px solid var(--border)}
.skeleton-avatar{width:40px;height:40px;border-radius:50%;background:var(--border);flex-shrink:0}
.skeleton-content{flex:1}
.skeleton-card{height:120px;margin-bottom:.8rem;border-radius:16px}
.skeleton-line{height:12px;margin-bottom:.5rem;border-radius:4px}
.skeleton-line.w60{width:60%}.skeleton-line.w40{width:40%}
@keyframes shimmer{0%{background-position:200% 0}to{background-position:-200% 0}}

/* ── Animations ── */
@keyframes fadeInUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes scaleIn{from{opacity:0;transform:scale(.95)}to{opacity:1;transform:scale(1)}}
@keyframes slideIn{from{opacity:0;transform:translateX(20px)}to{opacity:1;transform:translateX(0)}}
@keyframes slideOut{from{opacity:1;transform:translateX(0)}to{opacity:0;transform:translateX(100%)}}
.animate-in{animation:fadeInUp .5s var(--ease) both}
.animate-d1{animation:fadeInUp .5s var(--ease) .08s both}
.animate-d2{animation:fadeInUp .5s var(--ease) .16s both}
.animate-d3{animation:fadeInUp .5s var(--ease) .24s both}
.animate-d4{animation:fadeInUp .5s var(--ease) .32s both}
.animate-scale{animation:scaleIn .4s var(--ease) both}

/* ── Search Overlay ── */
.search-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.3);backdrop-filter:blur(6px);z-index:9998;display:flex;align-items:flex-start;justify-content:center;padding-top:5rem;display:none}
.search-overlay.active{display:flex}
.search-overlay .search-box{width:600px;max-width:90vw;background:var(--bg-card);border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.15);overflow:hidden}
.search-overlay .search-box input{border:none;font-size:1.2rem;padding:1.2rem 1.5rem;width:100%;background:transparent;color:var(--text);outline:none}
.search-overlay .search-box .search-results{max-height:400px;overflow-y:auto;border-top:1px solid var(--border)}
.search-overlay .search-box .search-results .sr-item{padding:.8rem 1.5rem;cursor:pointer;display:flex;align-items:center;gap:.8rem;transition:all .2s}
.search-overlay .search-box .search-results .sr-item:hover{background:var(--primary-light)}
.search-overlay .search-box .search-footer{padding:.6rem 1.5rem;font-size:.75rem;color:var(--text-muted);display:flex;justify-content:space-between}

/* ── Theme Toggle ── */
.theme-toggle{cursor:pointer;width:36px;height:36px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all .4s var(--ease-spring);font-size:1.1rem;color:var(--text)}
.theme-toggle:hover{background:var(--border);transform:rotate(25deg)}

/* ── Print ── */
@media(max-width:640px){.sidebar{width:56px!important}.sidebar-logo{font-size:1.2rem!important;padding:8px!important}.nav-item-a{padding:8px!important;justify-content:center!important}.main-content{width:100%!important;border:none!important}.profile-banner{height:80px!important}.profile-avatar-wrapper{margin-top:-24px!important}.stats-bar{gap:.5rem!important}.stats-bar .stat-item{min-width:60px!important}}@media print{body{background:white!important}.sidebar,.right-sidebar,.theme-toggle,.btn{display:none!important}.main-content{width:100%!important;border:none!important}}

/* ── Responsive ── */
@media(max-width:1280px){.right-sidebar{width:300px}}@media(max-width:1024px){.right-sidebar{width:280px}}@media(max-width:1200px){.right-sidebar{display:none}.main-content{width:100%;max-width:600px}}
@media(max-width:768px){.sidebar{width:72px}.sidebar .nav-label,.sidebar .sidebar-user-name,.sidebar .sidebar-post-btn span{display:none}.sidebar-post-btn{width:48px;height:48px;padding:0;border-radius:50%}.sidebar-post-btn i{margin:0}.main-content{width:100%}.profile-banner{height:120px}.profile-avatar-wrapper{margin-top:-32px}}
</style>
<script>
function toggleTheme(){const h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n);const e=document.querySelector('.theme-toggle i');if(e)e.className=n==='dark'?'bi bi-sun-fill':'bi bi-moon-stars-fill'}
document.addEventListener('DOMContentLoaded',function(){
  const s=localStorage.getItem('theme');if(s){document.documentElement.setAttribute('data-theme',s);const e=document.querySelector('.theme-toggle i');if(e)e.className=s==='dark'?'bi bi-sun-fill':'bi bi-moon-stars-fill'}
  document.querySelectorAll('.toast-msg').forEach(function(t){setTimeout(function(){t.style.animation='slideOut .3s ease-in forwards';setTimeout(function(){t.remove()},300)},4000)})
  document.addEventListener('keydown',function(e){if((e.ctrlKey||e.metaKey)&&e.key==='k'){e.preventDefault();openSearchOverlay()}if(e.key==='Escape'){closeSearchOverlay();closeAllModals()}})
})
// Register Service Worker for offline support & caching
if('serviceWorker' in navigator){
  navigator.serviceWorker.register('/static/sw.js', {scope: '/'}).then(function(reg){
    console.log('[PWA] SW registered for scope:', reg.scope);
    reg.onupdatefound = function(){
      var installing = reg.installing;
      installing.onstatechange = function(){
        if(installing.state === 'installed' && navigator.serviceWorker.controller){
          console.log('[PWA] New version available; reload to update.');
          if(window.showToast) showToast('Updated version available. Reload to apply.','info');
        }
      };
    };
  }).catch(function(err){
    console.warn('[PWA] SW registration failed:', err);
  });
}
function showToast(msg,type){var c=document.getElementById('toastContainer')||function(){var d=document.createElement('div');d.id='toastContainer';d.className='toast-container';document.body.appendChild(d);return d}();var t=document.createElement('div');t.className='toast-msg '+type;var icons={success:'bi-check-circle-fill text-success',error:'bi-x-circle-fill text-danger',info:'bi-info-circle-fill text-info'};t.innerHTML='<i class="bi '+(icons[type]||icons.info)+'"></i> '+msg+'<div class="toast-progress"></div>';c.appendChild(t);setTimeout(function(){t.style.animation='slideOut .3s ease-in forwards';setTimeout(function(){t.remove()},350)},4000)}
window.showToast=showToast;
function closeAllModals(){document.querySelectorAll('.modal.show').forEach(function(m){var bs=bootstrap.Modal.getInstance(m);if(bs)bs.hide()})}
function toggleUserDropdown(e){
  e.stopPropagation();
  var dd=document.getElementById('userDropdown');
  var chevron=document.getElementById('userDropdownChevron');
  if(!dd)return;
  var isOpen=dd.classList.contains('show');
  document.querySelectorAll('.user-dropdown.show').forEach(function(d){d.classList.remove('show')});
  document.querySelectorAll('.sidebar-user').forEach(function(s){s.setAttribute('aria-expanded','false')});
  if(!isOpen){
    dd.classList.add('show');
    e.currentTarget.setAttribute('aria-expanded','true');
    if(chevron)chevron.style.transform='rotate(180deg)';
  } else {
    if(chevron)chevron.style.transform='rotate(0deg)';
  }
}
document.addEventListener('click',function(e){
  if(!e.target.closest('.sidebar-user')){
    document.querySelectorAll('.user-dropdown.show').forEach(function(d){d.classList.remove('show')});
    document.querySelectorAll('.sidebar-user').forEach(function(s){s.setAttribute('aria-expanded','false')});
    var ch=document.getElementById('userDropdownChevron');
    if(ch)ch.style.transform='rotate(0deg)';
  }
});
document.addEventListener('keydown',function(e){
  if(e.key==='Escape'){
    document.querySelectorAll('.user-dropdown.show').forEach(function(d){d.classList.remove('show')});
    document.querySelectorAll('.sidebar-user').forEach(function(s){s.setAttribute('aria-expanded','false')});
    var ch=document.getElementById('userDropdownChevron');
    if(ch)ch.style.transform='rotate(0deg)';
  }
});
</script>
</head>
<body>
<a href="#mainContent" class="skip-to-content" style="position:absolute;top:-100%;left:0;z-index:10000;padding:0.75rem 1.5rem;background:var(--primary);color:white;font-weight:700;text-decoration:none;border-radius:0 0 8px 0;transition:top 0.2s;">Skip to main content</a>
<style>.skip-to-content:focus{top:0;outline:0.25rem solid white;outline-offset:-0.25rem;}</style>
<div id="toastContainer" class="toast-container"></div>

<!-- Twitter/X Layout -->
<div class="app-layout">
  <!-- Left Sidebar -->
  {% if session.user_id %}
  <aside class="sidebar" aria-label="User menu">
    <div class="sidebar-logo"><a href="/feed" aria-label="Home"><i class="bi bi-book-fill"></i></a></div>
    <nav class="sidebar-nav" aria-label="Main navigation">
      <ul style="list-style:none;padding:0;margin:0;" role="list">
        <li><a href="/feed" class="nav-item-a" id="nav-home" aria-current="page"><i class="bi bi-house-fill nav-icon"></i><span class="nav-label">Home</span></a></li>
      <li><a href="/explore" class="nav-item-a" id="nav-explore"><i class="bi bi-hash nav-icon"></i><span class="nav-label">Explore</span></a></li>
      <li><a href="/notifications" class="nav-item-a" id="nav-notifications"><i class="bi bi-bell-fill nav-icon"></i>{% if notif_count > 0 %}<span class="nav-badge badge rounded-pill bg-danger">{{ notif_count }}</span>{% endif %}<span class="nav-label">Notifications</span></a></li>
      <li><a href="/books" class="nav-item-a" id="nav-books"><i class="bi bi-book-fill nav-icon"></i><span class="nav-label">Books</span></a></li>
      <li><a href="/series" class="nav-item-a" id="nav-series"><i class="bi bi-collection-fill nav-icon"></i><span class="nav-label">Series</span></a></li>
      <li><a href="/reading-challenge" class="nav-item-a" id="nav-challenge"><i class="bi bi-trophy-fill nav-icon"></i><span class="nav-label">Challenge</span></a></li>
      <li><a href="/wishlist" class="nav-item-a" id="nav-wishlist"><i class="bi bi-star-fill nav-icon"></i><span class="nav-label">Wishlist</span></a></li>
      <li><a href="/diary" class="nav-item-a" id="nav-diary"><i class="bi bi-journal-text nav-icon"></i><span class="nav-label">Diary</span></a></li>
      <li><a href="/profile/{{session.user_id}}" class="nav-item-a" id="nav-profile"><i class="bi bi-person-fill nav-icon"></i><span class="nav-label">Profile</span></a></li>
      <li><a href="/settings" class="nav-item-a" id="nav-settings"><i class="bi bi-gear-fill nav-icon"></i><span class="nav-label">Settings</span></a></li>
      {% if session.role == 'admin' %}<li><a href="/users" class="nav-item-a" id="nav-users"><i class="bi bi-people-fill nav-icon"></i><span class="nav-label">Users</span></a></li>
      <li><a href="/reports" class="nav-item-a" id="nav-reports"><i class="bi bi-bar-chart-fill nav-icon"></i><span class="nav-label">Reports</span></a></li>{% endif %}
    </nav>
    <button class="sidebar-post-btn" onclick="document.getElementById('postContent')?.focus()" aria-label="Create a new post"><i class="bi bi-feather"></i> <span>Post</span></button>
    <div class="sidebar-user" role="button" tabindex="0" aria-label="User menu" aria-haspopup="true" aria-expanded="false" onclick="toggleUserDropdown(event)" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();toggleUserDropdown(event)}">
      {{ _avatar_html(session.get('user_name','?'),40)|safe }}
      <div class="sidebar-user-name" style="flex:1;min-width:0;"><div class="fw-bold" style="font-size:.9rem;">{{session.user_name}}</div><div style="font-size:.8rem;color:var(--text-muted);">@{{session.user_id}}</div></div>
      <i class="bi bi-three-dots" style="color:var(--text-muted);font-size:1.1rem;transition:transform .2s;transform:rotate(0deg);" id="userDropdownChevron"></i>
      <div class="user-dropdown" id="userDropdown" role="menu" aria-label="User options">
        <button class="user-dropdown-item" role="menuitem" onclick="event.stopPropagation();window.location.href='/profile/{{session.user_id}}'"><i class="bi bi-person-fill" style="color:var(--primary);"></i><div><div class="dd-item-label">Your Profile</div><div class="dd-item-desc">View your public profile</div></div></button>
        <div class="user-dropdown-divider"></div>
        <button class="user-dropdown-item" role="menuitem" onclick="event.stopPropagation();window.location.href='/settings'"><i class="bi bi-gear-fill" style="color:var(--text-muted);"></i><div><div class="dd-item-label">Settings</div><div class="dd-item-desc">Account &amp; preferences</div></div></button>
        <button class="user-dropdown-item" role="menuitem" onclick="event.stopPropagation();window.location.href='/help'"><i class="bi bi-question-circle-fill" style="color:var(--text-muted);"></i><div><div class="dd-item-label">Help</div><div class="dd-item-desc">Guides &amp; support</div></div></button>
        <div class="user-dropdown-divider"></div>
        <button class="user-dropdown-item user-dropdown-danger" role="menuitem" onclick="event.stopPropagation();window.location.href='/logout'"><i class="bi bi-box-arrow-right"></i><div><div class="dd-item-label">Logout</div><div class="dd-item-desc">Sign out of your account</div></div></button>
      </div>
    </div>
  </aside>
  {% endif %}
  
  <!-- Main Content -->
  <main class="main-content" id="mainContent">
"""  # noqa

FOOTER_HTML = r"""
  </main>
  <!-- Right Sidebar -->
  {% if session.user_id %}
  <aside class="right-sidebar" aria-label="Trending and suggestions">
    <div class="rside-search" role="search">
      <i class="bi bi-search search-icon"></i>
      <input type="text" placeholder="Search books..." onfocus="openSearchOverlay()" readonly aria-label="Search books">
    </div>
    <div class="rside-card" id="trendingSidebar">
      <div class="rside-header"><i class="bi bi-fire text-danger me-1"></i> Trending Books</div>
      <div id="trendingSidebarContent"><div class="text-center text-muted small py-3"><div class="spinner-border spinner-border-sm"></div></div></div>
      <a href="/search" class="rside-show-more text-decoration-none">Show more</a>
    </div>
    <div class="rside-card">
      <div class="rside-header"><i class="bi bi-people-fill me-1" style="color:var(--primary);"></i> Who to follow</div>
      <div id="whoToFollowContent"><div class="text-center text-muted small py-3"><div class="spinner-border spinner-border-sm"></div></div></div>
      <a href="/search?entity=users" class="rside-show-more text-decoration-none">Show more</a>
    </div>
    <footer class="rside-footer" aria-label="Site links" role="contentinfo">
      <nav aria-label="Quick links">
        <a href="/books">Books</a>
        <a href="/feed">Feed</a>
        <a href="/search">Search</a>
        <a href="/series">Series</a>
      </nav>
      <span>&copy; BookSocial 2026</span>
    </footer>
  </aside>
  {% endif %}
</div>
<!-- Search Overlay -->
<div class="search-overlay" id="searchOverlay" role="dialog" aria-label="Search books" onclick="if(event.target===this)closeSearchOverlay()">
<div class="search-box" role="search">
<input type="text" placeholder="Search books by title, author, or ISBN... (Ctrl+K)" oninput="searchBooks(this.value)" autofocus aria-label="Search query">
<div class="search-results" id="searchResults" role="listbox"><div class="text-center py-4 text-muted small" role="status">Type to search books...</div></div>
<div class="search-footer"><span>BookSocial Search</span><span><kbd>Esc</kbd> Close</span></div>
</div></div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" defer></script>
<script>
// Active nav highlighting
(function(){
  var path = window.location.pathname;
  document.querySelectorAll('.nav-item-a').forEach(function(el){
    var href = el.getAttribute('href');
    if(href && path.startsWith(href) && href !== '/feed'){el.classList.add('active')}
    else if(href === '/feed' && (path === '/' || path === '/feed' || path === '/dashboard')){el.classList.add('active')}
    else if(href === '/profile/'+document.querySelector('.sidebar-user-name')?.textContent?.trim()){el.classList.add('active')}
  });
})();

// Load trending sidebar
function loadTrendingSidebar(){
  fetch('/api/analytics/monthly').then(function(r){return r.json()}).then(function(d){
    var c=document.getElementById('trendingSidebarContent');
    if(!c)return;
    if(!d.labels||!d.labels.length){c.innerHTML='<div class="text-center text-muted small py-3">Not enough data yet</div>';return}
    var colors=['#4f46e5','#059669','#d97706','#dc2626','#0891b2','#7c3aed','#db2777','#ca8a04'];
    c.innerHTML=d.labels.slice(0,6).map(function(l,i){
      return '<div class="rside-item"><div class="rside-rank">'+(i+1)+'</div><div class="rside-content"><div class="rside-title" style="color:'+colors[i%colors.length]+';">'+l+'</div><div class="rside-meta">'+d.values[i]+' issues this month</div></div></div>'
    }).join('');
  }).catch(function(){document.getElementById('trendingSidebarContent').innerHTML='<div class="text-center text-muted small py-3">No data</div>'})
}
function loadWhoToFollow(){
  fetch('/api/analytics/activity').then(function(r){return r.json()}).then(function(d){
    var c=document.getElementById('whoToFollowContent');
    if(!c)return;
    if(!d||!d.length){c.innerHTML='<div class="text-center text-muted small py-3">No suggestions yet</div>';return}
    var users=[];var seen={};
    d.forEach(function(a){if(!seen[a.action.split(' ')[0]]){seen[a.action.split(' ')[0]]=true;users.push(a.action.split(' ')[0])}});
    c.innerHTML=users.slice(0,3).map(function(u){
      return '<div class="rside-item"><div style="width:40px;height:40px;border-radius:50%;background:var(--primary);color:white;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0;">'+u[0]+'</div><div class="rside-content"><div class="rside-title">'+u+'</div></div><button class="btn btn-outline btn-sm" onclick="alert(\'View profile\')">Follow</button></div>'
    }).join('');
  }).catch(function(){document.getElementById('whoToFollowContent').innerHTML='<div class="text-center text-muted small py-3">No suggestions</div>'})
}
setTimeout(loadTrendingSidebar,500);
setTimeout(loadWhoToFollow,700);
</script>
</body></html>"""

# ─── AUTH ────────────────────────────────────────────────────────────

@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("login_page"))

# ─── AUTH PAGES (Split-screen layout) ─────────────────────────────

def render_auth_page(title, content, **kw):
    """Render an auth page using the split-screen auth_base.html template."""
    from flask import render_template
    return render_template('auth_base.html', title=title,
        auth_content=content, session={}, **kw)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        s = _library_stats()
        CONTENT = (
            '<h2>Welcome Back</h2>'
            '<p class="auth-subtitle">Sign in to access your library dashboard</p>'
            '<form method="POST" role="form" aria-label="Login form">'
            '<div class="mb-3">'
            '<label class="form-label" for="loginUid">User ID</label>'
            '<input type="text" name="user_id" id="loginUid" class="form-control" placeholder="e.g. ADMIN001" required autofocus autocomplete="username">'
            '</div>'
            '<div class="mb-3">'
            '<label class="form-label" for="loginPw">Password</label>'
            '<div class="password-wrapper">'
            '<input type="password" name="password" id="loginPw" class="form-control" placeholder="Enter your password" required autocomplete="current-password">'
            '<button type="button" class="password-toggle" onclick="togglePasswordVisibility(this)" aria-label="Toggle password visibility" aria-pressed="false" tabindex="-1"><i class="bi bi-eye-fill"></i></button>'
            '</div>'
            '</div>'
            '<div class="d-flex justify-content-between align-items-center mb-3">'
            '<div class="form-check">'
            '<input type="checkbox" class="form-check-input" id="rememberMe" name="remember" value="1">'
            '<label class="form-check-label" for="rememberMe" style="font-size:.85rem;color:var(--text-muted);">Remember me</label>'
            '</div>'
            '<a href="/forgot-password" style="font-size:.8rem;color:var(--primary);text-decoration:none;font-weight:600;">Forgot password?</a>'
            '</div>'
            '<button type="submit" class="btn btn-primary py-2"><i class="bi bi-shield-lock-fill me-2"></i>Log In</button>'
            '</form>'
            '<div class="auth-footer">New here? <a href="/register">Create an account</a></div>'
        )
        hero_script = '<script>fetch("/api/analytics/monthly").then(function(r){return r.json()}).then(function(d){if(d.values&&d.values.length){var el=document.getElementById("heroTxnsCount");if(el)el.textContent=d.values.reduce(function(a,b){return a+b},0)}}).catch(function(){})</script>'
        return render_auth_page("Login", CONTENT + hero_script, form_aria_label="Login form")

    from exceptions import AuthenticationError
    try:
        user = auth.login(request.form["user_id"],request.form["password"])
        session["user_id"]=user.user_id;session["user_name"]=user.name;session["role"]=user.role
        log("Web login",user.user_id)
        return redirect(url_for("feed_page"))
    except AuthenticationError:
        return render_auth_page("Login", (
            '<div class="alert alert-danger" role="alert" aria-live="assertive"><i class="bi bi-x-circle-fill me-1"></i> Invalid credentials. Please try again.</div>'
            '<a href="/login" class="btn btn-primary"><i class="bi bi-arrow-repeat me-2"></i> Try Again</a>'
        ), form_aria_label="Login form")

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "GET":
        CONTENT = (
            '<h2>Create Your Account</h2>'
            '<p class="auth-subtitle">Join BookTale and start your reading journey</p>'
            '<div class="role-selector" role="radiogroup" aria-label="Account type">'
            '<label class="role-option selected">'
            '<input type="radio" name="role" value="user" checked>'
            '<span class="role-icon">📖</span>Reader'
            '<span class="role-desc">Browse, review, and connect</span>'
            '</label>'
            '<label class="role-option">'
            '<input type="radio" name="role" value="librarian">'
            '<span class="role-icon">📚</span>Librarian'
            '<span class="role-desc">Manage library collections</span>'
            '</label>'
            '</div>'
            '<form method="POST" role="form" aria-label="Registration form">'
            '<div class="mb-3">'
            '<label class="form-label" for="regName">Full Name</label>'
            '<input type="text" name="name" id="regName" class="form-control" placeholder="e.g. Jane Doe" required>'
            '</div>'
            '<div class="mb-3">'
            '<label class="form-label" for="regEmail">Email <span class="text-muted" style="font-weight:400;">(optional)</span></label>'
            '<input type="email" name="email" id="regEmail" class="form-control" placeholder="jane@example.com">'
            '</div>'
            '<div class="mb-3">'
            '<label class="form-label" for="regUid">User ID</label>'
            '<input type="text" name="user_id" id="regUid" class="form-control" placeholder="e.g. MEM-0001" pattern="MEM-\\d{4}" title="Format: MEM-XXXX (e.g. MEM-0001)" required>'
            '<small class="text-muted" style="font-size:.7rem;">Format: MEM-XXXX (e.g. <code>MEM-0001</code>)</small>'
            '</div>'
            '<div class="mb-3">'
            '<label class="form-label" for="regPw">Password</label>'
            '<div class="password-wrapper">'
            '<input type="password" name="password" id="regPw" class="form-control" placeholder="Create a strong password" required minlength="6" autocomplete="new-password">'
            '<button type="button" class="password-toggle" onclick="togglePasswordVisibility(this)" aria-label="Toggle password visibility" aria-pressed="false" tabindex="-1"><i class="bi bi-eye-fill"></i></button>'
            '</div>'
            '<div class="password-strength-bar" aria-hidden="true"><div class="segment"></div><div class="segment"></div><div class="segment"></div><div class="segment"></div></div>'
            '<div class="password-strength-text"></div>'
            '</div>'
            '<div class="mb-3">'
            '<label class="form-label" for="regPw2">Confirm Password</label>'
            '<div class="password-wrapper">'
            '<input type="password" name="confirm_password" id="regPw2" class="form-control" placeholder="Repeat your password" required minlength="6" autocomplete="new-password">'
            '<button type="button" class="password-toggle" onclick="togglePasswordVisibility(this)" aria-label="Toggle password visibility" aria-pressed="false" tabindex="-1"><i class="bi bi-eye-fill"></i></button>'
            '</div>'
            '</div>'
            '<button type="submit" class="btn btn-primary py-2"><i class="bi bi-person-plus-fill me-2"></i>Create Account</button>'
            '</form>'
            '<div class="auth-footer">Already have an account? <a href="/login">Sign in</a></div>'
        )
        return render_auth_page("Register", CONTENT, form_aria_label="Registration form")

    # POST - handle registration
    user_id = request.form.get("user_id", "").strip()
    name = request.form.get("name", "").strip()
    password = request.form.get("password", "")
    confirm_pw = request.form.get("confirm_password", "")
    email = request.form.get("email", "").strip()
    role = request.form.get("role", "user")

    errors = []
    if not user_id or not name or not password:
        errors.append("All required fields must be filled")
    if password != confirm_pw:
        errors.append("Passwords do not match")
    if len(password) < 6:
        errors.append("Password must be at least 6 characters")
    if user_id and not user_id.startswith("MEM-"):
        errors.append("User ID must follow MEM-XXXX format")

    if errors:
        error_html = '<div class="alert alert-danger" role="alert" aria-live="assertive"><i class="bi bi-exclamation-triangle-fill me-1"></i> ' + '<br>'.join(errors) + '</div>'
        return render_auth_page("Register", error_html + '<a href="/register" class="btn btn-primary"><i class="bi bi-arrow-repeat me-2"></i> Try Again</a>', form_aria_label="Registration form")

    users = storage.load_users()
    if user_id in users:
        return render_auth_page("Register", (
            '<div class="alert alert-danger" role="alert" aria-live="assertive"><i class="bi bi-exclamation-triangle-fill me-1"></i> User ID already exists</div>'
            '<a href="/register" class="btn btn-primary"><i class="bi bi-arrow-repeat me-2"></i> Try Again</a>'
        ), form_aria_label="Registration form")

    from auth import hash_password as _hp, generate_verify_token as _gvt
    lib.register_user(user_id, name, email, "", role, _hp(password), actor="registration")

    # Send welcome email with verification link
    if email:
        try:
            from email_notifier import send_email
            token = _gvt(user_id)
            verify_url = request.host_url.rstrip("/") + "/verify-email?token=" + token
            send_email(email, "Welcome to BookTale!", (
                "<h2>Welcome to BookTale!</h2>"
                "<p>Thanks for joining, " + name + "!</p>"
                "<p>Please verify your email address:</p>"
                '<p><a href="' + verify_url + '" style="display:inline-block;padding:.6rem 1.2rem;background:#4f46e5;color:white;text-decoration:none;border-radius:8px;">Verify Email</a></p>'
                "<p>Or copy this link: " + verify_url + "</p>"
                "<p>Happy reading!</p>"
            ))
        except Exception as e:
            print("Welcome email error:", e)

    CONTENT = (
        '<div class="text-center">'
        '<div style="font-size:4rem;margin-bottom:1rem;">🎉</div>'
        '<h2>Welcome, ' + name + '!</h2>'
        '<p class="auth-subtitle">Your account has been created successfully.</p>'
        '</div>'
        '<a href="/login" class="btn btn-primary"><i class="bi bi-shield-lock-fill me-2"></i> Sign In</a>'
    )
    if email:
        CONTENT = (
            '<div class="text-center">'
            '<div style="font-size:4rem;margin-bottom:1rem;">📧</div>'
            '<h2>Check Your Email</h2>'
            '<p class="auth-subtitle">We sent a verification link to <strong>' + email + '</strong></p>'
            '<p style="font-size:.8rem;color:var(--text-muted);">Please verify your email to access all features.</p>'
            '</div>'
            '<a href="/login" class="btn btn-primary"><i class="bi bi-shield-lock-fill me-2"></i> Sign In</a>'
        )
    return render_auth_page("Registered", CONTENT)

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password_page():
    if request.method == "GET":
        CONTENT = (
            '<div class="step-indicator" aria-label="Step 1 of 3: Identify account">'
            '<div class="step active"><span class="step-num">1</span> Identify</div>'
            '<div class="step-line"></div>'
            '<div class="step"><span class="step-num">2</span> Verify</div>'
            '<div class="step-line"></div>'
            '<div class="step"><span class="step-num">3</span> Reset</div>'
            '</div>'
            '<div class="text-center mb-3">'
            '<div style="font-size:3rem;margin-bottom:.5rem;">🔐</div>'
            '<h2>Forgot Password?</h2>'
            '<p class="auth-subtitle">Enter your email or User ID and we\'ll send you a reset link</p>'
            '</div>'
            '<form method="POST" role="form" aria-label="Password reset form">'
            '<div class="mb-3">'
            '<label class="form-label" for="fpIdent">Email or User ID</label>'
            '<div class="input-group">'
            '<span class="input-group-text"><i class="bi bi-envelope-fill"></i></span>'
            '<input type="text" name="identity" id="fpIdent" class="form-control" placeholder="jane@example.com or MEM-0001" required autofocus>'
            '</div>'
            '</div>'
            '<button type="submit" class="btn btn-primary py-2"><i class="bi bi-send-fill me-2"></i>Send Reset Link</button>'
            '</form>'
            '<div class="auth-footer">Remember your password? <a href="/login">Sign in</a></div>'
        )
        return render_auth_page("Forgot Password", CONTENT, form_aria_label="Password reset form")

    # POST - anti-enumeration: always show success
    CONTENT = (
        '<div class="step-indicator" aria-label="Step 2 of 3: Check email">'
        '<div class="step completed"><span class="step-num">✓</span> Identify</div>'
        '<div class="step-line completed"></div>'
        '<div class="step active"><span class="step-num">2</span> Verify</div>'
        '<div class="step-line"></div>'
        '<div class="step"><span class="step-num">3</span> Reset</div>'
        '</div>'
        '<div class="text-center">'
        '<div style="font-size:4rem;margin-bottom:1rem;">📧</div>'
        '<h2>Check Your Email</h2>'
        '<p class="auth-subtitle">If an account exists, we have sent a password reset link.</p>'
        '<p style="font-size:.8rem;color:var(--text-muted);">Please check your inbox and spam folder. The link expires in 1 hour.</p>'
        '</div>'
        '<a href="/login" class="btn btn-primary"><i class="bi bi-arrow-left me-2"></i> Back to Login</a>'
    )

    identity = request.form.get("identity", "").strip()
    if identity:
        try:
            from auth import generate_reset_token as _grt
            users = storage.load_users()
            target_user = None
            for u in users.values():
                if u.user_id == identity or u.email == identity:
                    target_user = u
                    break
            if target_user and target_user.email:
                from email_notifier import send_email
                token = _grt(target_user.user_id)
                reset_url = request.host_url.rstrip("/") + "/reset-password?token=" + token
                send_email(target_user.email, "Reset your BookTale password", (
                    "<h2>Password Reset Request</h2>"
                    "<p>Hi " + target_user.name + ",</p>"
                    "<p>Click the button below to reset your password:</p>"
                    '<p><a href="' + reset_url + '" style="display:inline-block;padding:.6rem 1.2rem;background:#4f46e5;color:white;text-decoration:none;border-radius:8px;">Reset Password</a></p>'
                    "<p>Or copy this link: " + reset_url + "</p>"
                    "<p>This link expires in 1 hour.</p>"
                    "<p>If you did not request this, you can safely ignore this email.</p>"
                ))
        except Exception as e:
            print("Reset email error:", e)

    return render_auth_page("Email Sent", CONTENT)

@app.route("/verify-email")
def verify_email_page():
    token = request.args.get("token", "")
    if not token:
        CONTENT = (
            '<div class="text-center">'
            '<div style="font-size:4rem;margin-bottom:1rem;">🔗</div>'
            '<h2>Invalid Link</h2>'
            '<p class="auth-subtitle">No verification token provided.</p>'
            '</div>'
            '<a href="/login" class="btn btn-primary"><i class="bi bi-arrow-left me-2"></i> Back to Login</a>'
        )
        return render_auth_page("Verify Email", CONTENT)

    from auth import consume_verify_token as _cvt
    user_id = _cvt(token)

    if not user_id:
        CONTENT = (
            '<div class="text-center">'
            '<div style="font-size:4rem;margin-bottom:1rem;">⏰</div>'
            '<h2>Invalid or Expired Link</h2>'
            '<p class="auth-subtitle">This verification link has expired or is invalid. Please register again for a new link.</p>'
            '</div>'
            '<a href="/register" class="btn btn-primary"><i class="bi bi-person-plus-fill me-2"></i> Register Again</a>'
        )
        return render_auth_page("Verify Email", CONTENT)

    users = storage.load_users()
    if user_id in users:
        users[user_id].email_verified = True
        storage.save_users(users)

    CONTENT = (
        '<div class="text-center">'
        '<div style="font-size:4rem;margin-bottom:1rem;">✅</div>'
        '<h2>Email Verified!</h2>'
        '<p class="auth-subtitle">Your email has been verified. You can now access all features.</p>'
        '</div>'
        '<a href="/login" class="btn btn-primary"><i class="bi bi-shield-lock-fill me-2"></i> Sign In</a>'
    )
    return render_auth_page("Email Verified", CONTENT)

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password_page():
    if request.method == "GET":
        token = request.args.get("token", "")
        if not token:
            return render_auth_page("Reset Password", (
                '<div class="text-center">'
                '<div style="font-size:4rem;margin-bottom:1rem;">🔗</div>'
                '<h2>Invalid Link</h2>'
                '<p class="auth-subtitle">This reset link is missing or invalid.</p>'
                '<a href="/forgot-password" class="btn btn-primary mt-3">Request New Link</a>'
                '</div>'
            ))
        from auth import verify_reset_token as _vrt
        uid = _vrt(token)
        if not uid:
            return render_auth_page("Reset Password", (
                '<div class="text-center">'
                '<div style="font-size:4rem;margin-bottom:1rem;">⏰</div>'
                '<h2>Link Expired</h2>'
                '<p class="auth-subtitle">This reset link has expired. Please request a new one.</p>'
                '<a href="/forgot-password" class="btn btn-primary mt-3">Request New Link</a>'
                '</div>'
            ))

        CONTENT = (
            '<h2>Set New Password</h2>'
            '<p class="auth-subtitle">Enter your new password for account <strong>' + h(uid) + '</strong></p>'
            '<form method="POST" onsubmit="return validateResetForm()">'
            '<input type="hidden" name="token" value="' + token + '">'
            '<div class="mb-3"><label class="form-label">New Password *</label>'
            '<div class="input-group"><span class="input-group-text"><i class="bi bi-lock-fill"></i></span>'
            '<input type="password" name="password" class="form-control" placeholder="Min 6 characters" required id="resetPw" minlength="6" oninput="checkPwStrength(this.value)"></div>'
            '<div class="password-strength" id="resetPwStrength"></div>'
            '<small class="text-muted" id="resetPwHelp">At least 6 characters</small></div>'
            '<div class="mb-3"><label class="form-label">Confirm Password *</label>'
            '<div class="input-group"><span class="input-group-text"><i class="bi bi-lock-fill"></i></span>'
            '<input type="password" name="confirm_password" class="form-control" placeholder="Repeat password" required id="resetConfirmPw"></div></div>'
            '<button type="submit" class="btn btn-primary"><i class="bi bi-check-lg me-1"></i> Reset Password</button>'
            '</form>'
            '<div class="auth-divider">Remember your password?</div>'
            '<a href="/login" class="btn btn-outline"><i class="bi bi-box-arrow-in-right me-1"></i> Sign In</a>'
            '<script>'
            'function checkPwStrength(pw) {'
            'var bar = document.getElementById("resetPwStrength");'
            'var help = document.getElementById("resetPwHelp");'
            'if (!bar) return;'
            'if (pw.length === 0) { bar.className = "password-strength"; help.textContent = "At least 6 characters"; return; }'
            'var score = 0;'
            'if (pw.length >= 6) score++;'
            'if (pw.length >= 10) score++;'
            'if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;'
            'if (/[0-9]/.test(pw)) score++;'
            'if (/[^A-Za-z0-9]/.test(pw)) score++;'
            'var classes = ["", "weak", "medium", "strong", "very-strong"];'
            'bar.className = "password-strength " + classes[Math.min(score, 4)];'
            'var labels = ["", "Weak", "Medium", "Strong", "Very Strong"];'
            'help.textContent = labels[Math.min(score, 4)];'
            '}'
            'function validateResetForm() {'
            'var pw = document.getElementById("resetPw").value;'
            'var cpw = document.getElementById("resetConfirmPw").value;'
            'if (pw !== cpw) { showToast("Passwords do not match", "error"); return false; }'
            'if (pw.length < 6) { showToast("Password must be at least 6 characters", "error"); return false; }'
            'return true;'
            '}'
            '</script>'
        )
        return render_auth_page("Reset Password", CONTENT)

    # POST - process password reset
    token = request.form.get("token", "")
    password = request.form.get("password", "")
    confirm_pw = request.form.get("confirm_password", "")

    if not token or not password:
        return render_auth_page("Reset Password", '<div class="alert alert-danger">Invalid request</div><a href="/forgot-password" class="btn btn-primary">Request New Link</a>')
    if password != confirm_pw:
        return render_auth_page("Reset Password", '<div class="alert alert-danger">Passwords do not match</div><a href="/forgot-password" class="btn btn-primary">Request New Link</a>')
    if len(password) < 6:
        return render_auth_page("Reset Password", '<div class="alert alert-danger">Password must be at least 6 characters</div><a href="/forgot-password" class="btn btn-primary">Request New Link</a>')

    from auth import consume_reset_token as _crt, hash_password as _hp
    user_id = _crt(token)
    if not user_id:
        return render_auth_page("Reset Password", '<div class="alert alert-danger">Invalid or expired reset link</div><a href="/forgot-password" class="btn btn-primary">Request New Link</a>')

    users = storage.load_users()
    user = users.get(user_id)
    if not user:
        return render_auth_page("Reset Password", '<div class="alert alert-danger">User not found</div><a href="/forgot-password" class="btn btn-primary">Request New Link</a>')

    user.password_hash = _hp(password)
    storage.save_users(users)
    log("Password reset", user_id)

    return render_auth_page("Password Reset", (
        '<div class="text-center">'
        '<div style="font-size:4rem;margin-bottom:1rem;">🔐</div>'
        '<h2>Password Reset!</h2>'
        '<p class="auth-subtitle">Your password has been successfully changed.</p>'
        '<a href="/login" class="btn btn-primary mt-3"><i class="bi bi-box-arrow-in-right me-1"></i> Sign In</a>'
        '</div>'
    ))


# HELP PAGE

@app.route("/help")
@login_required
def help_page():
    CONTENT = '<div class="animate-in">'
    CONTENT += '<div class="glass-card p-0 mb-4" style="overflow:hidden;">'
    CONTENT += '<div class="p-4" style="background:linear-gradient(135deg,var(--primary),#7c3aed);color:white;">'
    CONTENT += '<h4 class="fw-bold mb-0"><i class="bi bi-question-circle-fill me-2"></i> Help &amp; Support</h4>'
    CONTENT += '<p class="mb-0" style="opacity:.8;font-size:.85rem;">Guides, tips, and frequently asked questions</p>'
    CONTENT += '</div></div>'
    CONTENT += '<div class="row g-4">'
    # Getting Started
    CONTENT += '<div class="col-md-6"><div class="glass-card p-4">'
    CONTENT += '<h5 class="fw-bold mb-3"><i class="bi bi-book-fill text-primary me-2"></i>Getting Started</h5>'
    CONTENT += '<ul class="list-unstyled" style="font-size:.9rem;">'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-primary me-2"></i> Browse and search books from the Explore page</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-primary me-2"></i> Issue books from the book details page</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-primary me-2"></i> Write reviews and rate books you have read</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-primary me-2"></i> Connect with other readers in the community</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-primary me-2"></i> Create reading lists and track your progress</li>'
    CONTENT += '</ul></div>'
    # Account Settings
    CONTENT += '<div class="glass-card p-4">'
    CONTENT += '<h5 class="fw-bold mb-3"><i class="bi bi-gear-fill text-warning me-2"></i>Account Settings</h5>'
    CONTENT += '<ul class="list-unstyled" style="font-size:.9rem;">'
    CONTENT += "<li class=\"mb-2\"><i class=\"bi bi-arrow-right-circle text-warning me-2\"></i> Update your profile information in <a href='/settings'>Settings</a></li>"
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-warning me-2"></i> Change notification preferences</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-warning me-2"></i> Manage privacy settings for your profile</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-warning me-2"></i> Customize appearance with themes and font sizes</li>'
    CONTENT += '</ul></div></div>'
    # Library Rules
    CONTENT += '<div class="col-md-6"><div class="glass-card p-4">'
    CONTENT += '<h5 class="fw-bold mb-3"><i class="bi bi-shield-lock-fill text-info me-2"></i>Library Rules</h5>'
    CONTENT += '<ul class="list-unstyled" style="font-size:.9rem;">'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-info me-2"></i> Books can be issued for a limited period</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-info me-2"></i> Late returns incur a fine per day</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-info me-2"></i> Maximum borrow limit applies per user</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-info me-2"></i> Membership must be renewed periodically</li>'
    CONTENT += '</ul></div>'
    # Need Help
    CONTENT += '<div class="glass-card p-4">'
    CONTENT += '<h5 class="fw-bold mb-3"><i class="bi bi-envelope-fill text-success me-2"></i>Need Help?</h5>'
    CONTENT += '<p style="font-size:.9rem;">If you encounter any issues or have questions:</p>'
    CONTENT += '<ul class="list-unstyled" style="font-size:.9rem;">'
    CONTENT += '<li class="mb-2"><i class="bi bi-envelope-fill text-success me-2"></i> Contact the library staff for assistance</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-chat-dots-fill text-success me-2"></i> Post in the community for peer support</li>'
    CONTENT += "<li class=\"mb-2\"><i class=\"bi bi-journal-text text-success me-2\"></i> Check the <a href='/feed'>Feed</a> for announcements</li>"
    CONTENT += '</ul></div></div></div></div>'
    return render_page("Help & Support", CONTENT)


# ─── USER SETTINGS ─────────────────────────────────────────────────

@app.route("/settings")
@login_required
def settings_page():
    """User settings page with Profile, Notifications, Privacy, Appearance, and Reading tabs."""
    uid = session["user_id"]
    users = storage.load_users()
    user = users.get(uid)
    if not user:
        return render_page("Settings", '<div class="empty-state"><div class="empty-icon"><i class="bi bi-person-x-fill"></i></div><h4>User not found</h4></div>')

    esc = h
    name_v = esc(user.name)
    email_v = esc(user.email)
    phone_v = esc(user.phone) if user.phone else ""
    bio_v = esc(user.bio) if user.bio else ""
    loc_v = esc(user.location) if user.location else ""
    web_v = esc(user.website) if user.website else ""
    theme_v = user.theme or "light"
    font_v = user.font_size or "medium"

    n_checks = {
        "email_notifications": user.email_notifications,
        "push_notifications": user.push_notifications,
        "notify_on_comment": user.notify_on_comment,
        "notify_on_like": user.notify_on_like,
        "notify_on_follow": user.notify_on_follow,
        "notify_on_issue_return": user.notify_on_issue_return,
        "notify_on_overdue": user.notify_on_overdue,
        "notify_on_due_reminder": user.notify_on_due_reminder,
    }
    n_html = ""
    for key, val in n_checks.items():
        label = key.replace("notify_on_", "").replace("_", " ").title().replace("Email Notifications", "Email Notifications").replace("Push Notifications", "Push Notifications")
        chk = 'checked' if val else ''
        icon = {
            "email_notifications": "envelope-fill",
            "push_notifications": "bell-fill",
            "notify_on_comment": "chat-dots-fill",
            "notify_on_like": "heart-fill",
            "notify_on_follow": "person-plus-fill",
            "notify_on_issue_return": "arrow-left-right",
            "notify_on_overdue": "exclamation-triangle-fill",
            "notify_on_due_reminder": "clock-fill",
        }.get(key, "bell-fill")
        n_html += (
            '<div class="settings-toggle-item">'
            '<div class="d-flex align-items-center gap-3">'
            '<i class="bi bi-%s" style="font-size:1.2rem;color:var(--primary);width:24px;"></i>'
            '<div><div class="fw-medium">%s</div></div>'
            '</div>'
            '<label class="toggle-switch">'
            '<input type="checkbox" name="%s" %s onchange="saveSetting(this)">'
            '<span class="toggle-slider"></span>'
            '</label>'
            '</div>'
        ) % (icon, label, key, chk)

    # Privacy toggles
    p_checks = [
        ("privacy_show_activity", "Show reading activity on profile", "graph-up-arrow", user.privacy_show_activity),
        ("privacy_show_wishlist", "Show wishlist on profile", "star-fill", user.privacy_show_wishlist),
        ("privacy_show_bookmarks", "Show bookmarks on profile", "bookmark-fill", user.privacy_show_bookmarks),
        ("privacy_show_email", "Show email on profile", "envelope-fill", user.privacy_show_email),
    ]
    p_html = ""
    for key, label, icon, val in p_checks:
        chk = 'checked' if val else ''
        p_html += (
            '<div class="settings-toggle-item">'
            '<div class="d-flex align-items-center gap-3">'
            '<i class="bi bi-%s" style="font-size:1.2rem;color:var(--primary);width:24px;"></i>'
            '<div><div class="fw-medium">%s</div></div>'
            '</div>'
            '<label class="toggle-switch">'
            '<input type="checkbox" name="%s" %s onchange="saveSetting(this)">'
            '<span class="toggle-slider"></span>'
            '</label>'
            '</div>'
        ) % (icon, label, key, chk)

    vis_opts = ""
    for v in ["public", "members", "private"]:
        sel = 'selected' if user.privacy_profile_visibility == v else ''
        vis_opts += '<option value="%s" %s>%s</option>' % (v, sel, v.title())

    rating_opts = ""
    for v in ["perfection", "worth_it", "timepass", "skip"]:
        sel = 'selected' if user.reading_default_rating == v else ''
        label = {"perfection": "Perfection", "worth_it": "Worth It", "timepass": "Timepass", "skip": "Skip"}[v]
        rating_opts += '<option value="%s" %s>%s</option>' % (v, sel, label)

    goal_opts = ""
    for v in ["books", "pages"]:
        sel = 'selected' if user.reading_goal_type == v else ''
        goal_opts += '<option value="%s" %s>%s</option>' % (v, sel, v.title())

    CONTENT = '''<div class="animate-in">
<div class="glass-card p-0 mb-4" style="overflow:hidden;">
    <div class="p-4" style="background:linear-gradient(135deg,var(--primary),#7c3aed);color:white;">
        <h4 class="fw-bold mb-0"><i class="bi bi-gear-fill me-2"></i> Settings</h4>
        <p class="mb-0" style="opacity:.8;font-size:.85rem;">Manage your account preferences</p>
    </div>
</div>

<!-- Settings Tabs -->
<nav class="settings-tabs mb-3" role="tablist" aria-label="Settings sections">
    <button class="settings-tab active" role="tab" aria-selected="true" data-tab="profile" onclick="switchSettingsTab(this)"><i class="bi bi-person-fill"></i> Profile</button>
    <button class="settings-tab" role="tab" aria-selected="false" data-tab="notifications" onclick="switchSettingsTab(this)"><i class="bi bi-bell-fill"></i> Notifications</button>
    <button class="settings-tab" role="tab" aria-selected="false" data-tab="privacy" onclick="switchSettingsTab(this)"><i class="bi bi-shield-lock-fill"></i> Privacy</button>
    <button class="settings-tab" role="tab" aria-selected="false" data-tab="appearance" onclick="switchSettingsTab(this)"><i class="bi bi-palette-fill"></i> Appearance</button>
    <button class="settings-tab" role="tab" aria-selected="false" data-tab="reading" onclick="switchSettingsTab(this)"><i class="bi bi-book-fill"></i> Reading</button>
</nav>

<!-- Profile Tab -->
<div class="settings-panel active" id="tab-profile" role="tabpanel">
    <div class="glass-card p-4">
        <h5 class="fw-bold mb-3"><i class="bi bi-person-fill text-primary me-2"></i>Profile Information</h5>
        <form id="profileSettingsForm" onsubmit="return saveProfileSettings()">
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="form-label">Display Name</label>
                    <input type="text" class="form-control" id="sName" value="NAME_V" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-control" id="sEmail" value="EMAIL_V">
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="form-label">Phone</label>
                    <input type="text" class="form-control" id="sPhone" value="PHONE_V">
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Website</label>
                    <input type="url" class="form-control" id="sWebsite" value="WEB_V" placeholder="https://example.com">
                </div>
            </div>
            <div class="mb-3">
                <label class="form-label">Location</label>
                <input type="text" class="form-control" id="sLocation" value="LOC_V" placeholder="City, Country">
            </div>
            <div class="mb-3">
                <label class="form-label">Bio</label>
                <textarea class="form-control" id="sBio" rows="3" placeholder="Tell us about yourself...">BIO_V</textarea>
            </div>
            <div class="mb-3">
                <label class="form-label">Change Password</label>
                <div class="row">
                    <div class="col-md-4 mb-2"><input type="password" class="form-control" id="sCurPw" placeholder="Current password"></div>
                    <div class="col-md-4 mb-2"><input type="password" class="form-control" id="sNewPw" placeholder="New password" minlength="6"></div>
                    <div class="col-md-4 mb-2"><input type="password" class="form-control" id="sConfPw" placeholder="Confirm new password"></div>
                </div>
                <small class="text-muted">Leave password fields empty to keep current password</small>
            </div>
            <button type="submit" class="btn btn-primary"><i class="bi bi-check-lg me-1"></i> Save Changes</button>
        </form>
    </div>
</div>

<!-- Notifications Tab -->
<div class="settings-panel" id="tab-notifications" role="tabpanel">
    <div class="glass-card p-4">
        <h5 class="fw-bold mb-3"><i class="bi bi-bell-fill text-warning me-2"></i>Notification Preferences</h5>
        <p class="text-muted small mb-3">Control which notifications you receive</p>
        NOTIF_HTML
    </div>
</div>

<!-- Privacy Tab -->
<div class="settings-panel" id="tab-privacy" role="tabpanel">
    <div class="glass-card p-4">
        <h5 class="fw-bold mb-3"><i class="bi bi-shield-lock-fill text-info me-2"></i>Privacy Settings</h5>
        <div class="mb-3">
            <label class="form-label">Profile Visibility</label>
            <select class="form-select" id="sProfileVis" onchange="saveProfileVisibility(this)">
                VIS_OPTS
            </select>
        </div>
        <p class="text-muted small mb-3">Control what appears on your public profile</p>
        PRIV_HTML
    </div>
</div>

<!-- Appearance Tab -->
<div class="settings-panel" id="tab-appearance" role="tabpanel">
    <div class="glass-card p-4">
        <h5 class="fw-bold mb-3"><i class="bi bi-palette-fill text-purple me-2"></i>Appearance</h5>
        <div class="mb-4">
            <label class="form-label">Theme</label>
            <div class="d-flex gap-3">
                <label class="theme-option%s" onclick="selectTheme('light')">
                    <input type="radio" name="theme" value="light" class="d-none" %s>
                    <i class="bi bi-sun-fill" style="font-size:1.5rem;"></i>
                    <span>Light</span>
                </label>
                <label class="theme-option%s" onclick="selectTheme('dark')">
                    <input type="radio" name="theme" value="dark" class="d-none" %s>
                    <i class="bi bi-moon-fill" style="font-size:1.5rem;"></i>
                    <span>Dark</span>
                </label>
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">Font Size</label>
            <div class="d-flex gap-2">
                <button class="btn %s" onclick="selectFont('small')" id="fontSmall">A-</button>
                <button class="btn %s" onclick="selectFont('medium')" id="fontMedium">A</button>
                <button class="btn %s" onclick="selectFont('large')" id="fontLarge">A+</button>
            </div>
        </div>
    </div>
</div>

<!-- Reading Tab -->
<div class="settings-panel" id="tab-reading" role="tabpanel">
    <div class="glass-card p-4">
        <h5 class="fw-bold mb-3"><i class="bi bi-book-fill text-success me-2"></i>Reading Preferences</h5>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">Default Rating Label</label>
                <select class="form-select" id="sDefaultRating">RATING_OPTS</select>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">Reading Goal Type</label>
                <select class="form-select" id="sGoalType">GOAL_OPTS</select>
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">Default Reading Goal</label>
            <input type="number" class="form-control" id="sDefaultGoal" value="GOAL_VAL" min="1" max="365">
            <small class="text-muted">Books or pages per year</small>
        </div>
        <button class="btn btn-primary" onclick="saveReadingPrefs()"><i class="bi bi-check-lg me-1"></i> Save Reading Preferences</button>
    </div>
</div>
</div>
'''

    CONTENT = CONTENT.replace("NAME_V", name_v).replace("EMAIL_V", email_v)
    CONTENT = CONTENT.replace("PHONE_V", phone_v).replace("WEB_V", web_v)
    CONTENT = CONTENT.replace("LOC_V", loc_v).replace("BIO_V", bio_v)
    CONTENT = CONTENT.replace("NOTIF_HTML", n_html).replace("PRIV_HTML", p_html)
    CONTENT = CONTENT.replace("VIS_OPTS", vis_opts)
    CONTENT = CONTENT.replace("RATING_OPTS", rating_opts).replace("GOAL_OPTS", goal_opts)
    CONTENT = CONTENT.replace('GOAL_VAL', str(user.reading_default_goal or 12))

    # Theme/font button styling
    light_sel = ' active' if theme_v == 'light' else ''
    light_chk = 'checked' if theme_v == 'light' else ''
    dark_sel = ' active' if theme_v == 'dark' else ''
    dark_chk = 'checked' if theme_v == 'dark' else ''
    font_classes = ['btn btn-outline', 'btn btn-outline', 'btn btn-outline']
    if font_v == 'small': font_classes[0] = 'btn btn-primary'
    elif font_v == 'medium': font_classes[1] = 'btn btn-primary'
    elif font_v == 'large': font_classes[2] = 'btn btn-primary'
    CONTENT = CONTENT % (light_sel, light_chk, dark_sel, dark_chk,
        font_classes[0], font_classes[1], font_classes[2])

    return render_page("Settings", CONTENT + '''
<style>
.settings-tabs{display:flex;gap:4px;overflow-x:auto;padding:4px;background:var(--border);border-radius:12px;flex-wrap:wrap}
.settings-tab{display:flex;align-items:center;gap:6px;padding:8px 14px;border:none;background:transparent;color:var(--text-muted);font-size:.85rem;font-weight:600;border-radius:8px;cursor:pointer;transition:all .2s;white-space:nowrap;font-family:var(--font)}
.settings-tab:hover{color:var(--text);background:var(--bg-card)}
.settings-tab.active{background:var(--bg-card);color:var(--text);box-shadow:0 2px 8px rgba(0,0,0,.06)}
.settings-panel{display:none;animation:fadeInUp .3s ease}
.settings-panel.active{display:block}
.settings-toggle-item{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border)}
.settings-toggle-item:last-child{border-bottom:none}
.toggle-switch{position:relative;display:inline-block;width:44px;height:24px;flex-shrink:0}
.toggle-switch input{opacity:0;width:0;height:0}
.toggle-slider{position:absolute;cursor:pointer;inset:0;background:var(--border);border-radius:24px;transition:.3s}
.toggle-slider::before{content:"";position:absolute;height:18px;width:18px;left:3px;bottom:3px;background:white;border-radius:50%;transition:.3s;box-shadow:0 1px 3px rgba(0,0,0,.15)}
.toggle-switch input:checked+.toggle-slider{background:var(--primary)}
.toggle-switch input:checked+.toggle-slider::before{transform:translateX(20px)}
.theme-option{display:flex;flex-direction:column;align-items:center;gap:4px;padding:16px 24px;border-radius:12px;border:2px solid var(--border);cursor:pointer;transition:all .2s;min-width:100px}
.theme-option.active{border-color:var(--primary);background:var(--primary-light)}
.theme-option:hover{border-color:var(--primary)}
</style>
<script>
function switchSettingsTab(el) {
    document.querySelectorAll(".settings-tab").forEach(function(t){ t.classList.remove("active"); t.setAttribute("aria-selected","false"); });
    el.classList.add("active"); el.setAttribute("aria-selected","true");
    document.querySelectorAll(".settings-panel").forEach(function(p){ p.classList.remove("active"); });
    var tab = document.getElementById("tab-" + el.getAttribute("data-tab"));
    if(tab) tab.classList.add("active");
}
function saveSetting(el) {
    var data = {}; data[el.name] = el.checked;
    fetch("/api/settings/save", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    }).then(function(r){ return r.json() }).then(function(d){
        if(d.success) showToast("Setting saved", "success");
        else showToast(d.error || "Failed", "error");
    });
}
function saveProfileSettings() {
    var data = {
        name: document.getElementById("sName").value.trim(),
        email: document.getElementById("sEmail").value.trim(),
        phone: document.getElementById("sPhone").value.trim(),
        website: document.getElementById("sWebsite").value.trim(),
        location: document.getElementById("sLocation").value.trim(),
        bio: document.getElementById("sBio").value.trim()
    };
    var cpw = document.getElementById("sCurPw").value;
    var npw = document.getElementById("sNewPw").value;
    var cnpw = document.getElementById("sConfPw").value;
    if(cpw || npw || cnpw) {
        if(!cpw) { showToast("Enter current password", "error"); return false; }
        if(npw !== cnpw) { showToast("New passwords do not match", "error"); return false; }
        if(npw.length < 6) { showToast("New password must be at least 6 characters", "error"); return false; }
        data.current_password = cpw;
        data.new_password = npw;
    }
    var btn = document.querySelector("#tab-profile .btn-primary");
    btn.disabled = true; btn.innerHTML = "<span class=\'spinner-border spinner-border-sm\'></span> Saving...";
    fetch("/api/settings/save", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    }).then(function(r){ return r.json() }).then(function(d){
        btn.disabled = false; btn.innerHTML = "<i class=\'bi bi-check-lg\'></i> Save Changes";
        if(d.success) { showToast("Profile updated!", "success"); setTimeout(function(){ location.reload(); }, 1000); }
        else showToast(d.error || "Failed", "error");
    }).catch(function(){ btn.disabled = false; btn.innerHTML = "<i class=\'bi bi-check-lg\'></i> Save Changes"; });
    return false;
}
function saveProfileVisibility(el) {
    fetch("/api/settings/save", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({privacy_profile_visibility: el.value})
    }).then(function(r){ return r.json() }).then(function(d){
        if(d.success) showToast("Privacy updated", "success");
    });
}
function selectTheme(t) {
    document.querySelectorAll(".theme-option").forEach(function(o){ o.classList.remove("active"); });
    document.querySelector(".theme-option input[value=\'"+t+"\']").closest(".theme-option").classList.add("active");
    document.documentElement.setAttribute("data-theme", t);
    localStorage.setItem("theme", t);
    fetch("/api/settings/save", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({theme: t})
    });
}
function selectFont(s) {
    document.querySelectorAll("#fontSmall,#fontMedium,#fontLarge").forEach(function(b){ b.className = "btn btn-outline"; });
    document.getElementById("font"+s.charAt(0).toUpperCase()+s.slice(1)).className = "btn btn-primary";
    fetch("/api/settings/save", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({font_size: s})
    });
}
function saveReadingPrefs() {
    fetch("/api/settings/save", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            reading_default_rating: document.getElementById("sDefaultRating").value,
            reading_goal_type: document.getElementById("sGoalType").value,
            reading_default_goal: parseInt(document.getElementById("sDefaultGoal").value) || 12
        })
    }).then(function(r){ return r.json() }).then(function(d){
        if(d.success) showToast("Reading preferences saved!", "success");
        else showToast(d.error || "Failed", "error");
    });
}
</script>
''')


@app.route("/api/settings/save", methods=["POST"])
@login_required
def api_save_settings():
    """Save user settings."""
    uid = session["user_id"]
    data = request.get_json() or {}
    users = storage.load_users()
    user = users.get(uid)
    if not user:
        return jsonify({"success": False, "error": "User not found"})

    # Profile fields
    for key in ["name", "email", "phone", "bio", "website", "location"]:
        if key in data:
            setattr(user, key, data[key])
            if key == "name":
                session["user_name"] = data[key]

    # Toggle/boolean fields
    for key in ["email_notifications", "push_notifications", "notify_on_comment", "notify_on_like",
                "notify_on_follow", "notify_on_issue_return", "notify_on_overdue", "notify_on_due_reminder",
                "privacy_show_activity", "privacy_show_wishlist", "privacy_show_bookmarks", "privacy_show_email"]:
        if key in data:
            setattr(user, key, bool(data[key]))

    # String fields
    for key in ["theme", "font_size", "privacy_profile_visibility", "reading_default_rating", "reading_goal_type"]:
        if key in data:
            setattr(user, key, str(data[key]))

    # Integer fields
    if "reading_default_goal" in data:
        try:
            user.reading_default_goal = int(data["reading_default_goal"])
        except:
            pass

    # Password change
    if "new_password" in data and data["new_password"]:
        from auth import hash_password as _hp, verify_password as _vp
        cur = data.get("current_password", "")
        if not cur or not _vp(cur, user.password_hash):
            return jsonify({"success": False, "error": "Current password is incorrect"})
        user.password_hash = _hp(data["new_password"])
        log("Password changed via settings", uid)

    storage.save_users(users)
    return jsonify({"success": True, "message": "Settings saved"})


# ─── ADMIN SETTINGS ─────────────────────────────────────────────────

@app.route("/admin/settings")
@admin_required
def admin_settings_page():
    """Admin settings page for managing system-wide configuration."""
    from config import Config as C

    issue_d = C.ISSUE_DAYS
    fine_d = C.FINE_PER_DAY
    max_b = C.MAX_BORROW_LIMIT
    mem_v = C.MEMBERSHIP_VALIDITY_DAYS
    max_u = C.MAX_UPLOAD_SIZE // (1024 * 1024)  # Convert bytes to MB
    ext_s = ", ".join(sorted(C.ALLOWED_EXTENSIONS))
    smtp_h = C.SMTP_HOST
    smtp_p = C.SMTP_PORT
    smtp_u = C.SMTP_USER
    smtp_f = C.SMTP_FROM
    lib_n = C.LIBRARY_NAME
    email_en = C.EMAIL_NOTIFICATIONS_ENABLED

    CONTENT = '''<div class="animate-in">
<div class="glass-card p-0 mb-4" style="overflow:hidden;">
    <div class="p-4" style="background:linear-gradient(135deg,#7c3aed,#4f46e5);color:white;">
        <h4 class="fw-bold mb-0"><i class="bi bi-shield-lock-fill me-2"></i> Admin Settings</h4>
        <p class="mb-0" style="opacity:.8;font-size:.85rem;">System-wide configuration</p>
    </div>
</div>

<form id="adminSettingsForm" onsubmit="return saveAdminSettings()">
    <div class="glass-card p-4 mb-3">
        <h5 class="fw-bold mb-3"><i class="bi bi-building text-primary me-2"></i>Library Information</h5>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">Library Name</label>
                <input type="text" class="form-control" id="aLibName" value="%s">
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">Email From Address</label>
                <input type="email" class="form-control" id="aSmtpFrom" value="%s">
            </div>
        </div>
    </div>

    <div class="glass-card p-4 mb-3">
        <h5 class="fw-bold mb-3"><i class="bi bi-arrow-left-right text-success me-2"></i>Loan & Fine Policy</h5>
        <div class="row">
            <div class="col-md-3 mb-3">
                <label class="form-label">Issue Days</label>
                <input type="number" class="form-control" id="aIissueDays" value="%d" min="1" max="365">
                <small class="text-muted">Days per checkout</small>
            </div>
            <div class="col-md-3 mb-3">
                <label class="form-label">Fine per Day (&#8377;)</label>
                <input type="number" class="form-control" id="aFinePerDay" value="%s" min="0" step="0.5">
                <small class="text-muted">Late fee rate</small>
            </div>
            <div class="col-md-3 mb-3">
                <label class="form-label">Max Borrow Limit</label>
                <input type="number" class="form-control" id="aMaxBorrow" value="%d" min="1" max="50">
                <small class="text-muted">Books per user</small>
            </div>
            <div class="col-md-3 mb-3">
                <label class="form-label">Membership Validity</label>
                <input type="number" class="form-control" id="aMemValidity" value="%d" min="30" max="3650">
                <small class="text-muted">Days</small>
            </div>
        </div>
    </div>

    <div class="glass-card p-4 mb-3">
        <h5 class="fw-bold mb-3"><i class="bi bi-cloud-upload-fill text-info me-2"></i>Upload Settings</h5>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">Max Upload Size (MB)</label>
                <input type="number" class="form-control" id="aMaxUpload" value="%d" min="1" max="100">
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">Allowed Extensions</label>
                <input type="text" class="form-control" id="aAllowedExt" value="%s">
                <small class="text-muted">Comma-separated (e.g. .jpg,.png,.gif)</small>
            </div>
        </div>
    </div>

    <div class="glass-card p-4 mb-3">
        <h5 class="fw-bold mb-3"><i class="bi bi-envelope-fill text-warning me-2"></i>SMTP / Email Settings</h5>
        <div class="row">
            <div class="col-md-4 mb-3">
                <label class="form-label">SMTP Host</label>
                <input type="text" class="form-control" id="aSmtpHost" value="%s" placeholder="smtp.gmail.com">
            </div>
            <div class="col-md-2 mb-3">
                <label class="form-label">SMTP Port</label>
                <input type="number" class="form-control" id="aSmtpPort" value="%d" min="1" max="65535">
            </div>
            <div class="col-md-3 mb-3">
                <label class="form-label">SMTP User</label>
                <input type="text" class="form-control" id="aSmtpUser" value="%s" placeholder="your@email.com">
            </div>
            <div class="col-md-3 mb-3">
                <label class="form-label">SMTP Password</label>
                <input type="password" class="form-control" id="aSmtpPass" placeholder="App password">
                <small class="text-muted">Leave blank to keep current</small>
            </div>
        </div>
        <div class="d-flex align-items-center gap-3">
            <label class="form-label mb-0">Email Notifications</label>
            <label class="toggle-switch">
                <input type="checkbox" id="aEmailEnabled" %s>
                <span class="toggle-slider"></span>
            </label>
            <span class="small text-muted">Enable/disable all email notifications</span>
        </div>
    </div>

    <div class="glass-card p-4 mb-3">
        <h5 class="fw-bold mb-3"><i class="bi bi-key-fill text-danger me-2"></i>Admin Credentials</h5>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">Current Admin Password</label>
                <input type="password" class="form-control" id="aCurPw" placeholder="Enter current password to save changes">
                <small class="text-muted">Required to save admin settings</small>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">New Admin Password <span class="text-muted">(optional)</span></label>
                <input type="password" class="form-control" id="aNewAdminPw" placeholder="Leave blank to keep current" minlength="6">
            </div>
        </div>
    </div>

    <button type="submit" class="btn btn-primary btn-lg w-100"><i class="bi bi-check-lg me-2"></i> Save All Admin Settings</button>
</form>
</div>
''' % (h(lib_n), h(smtp_f), issue_d, "%.1f" % fine_d, max_b, mem_v, max_u, h(ext_s), h(smtp_h), smtp_p, h(smtp_u), 'checked' if email_en else '')

    return render_page("Admin Settings", CONTENT + '''
<style>
.toggle-switch{position:relative;display:inline-block;width:44px;height:24px;flex-shrink:0}
.toggle-switch input{opacity:0;width:0;height:0}
.toggle-slider{position:absolute;cursor:pointer;inset:0;background:var(--border);border-radius:24px;transition:.3s}
.toggle-slider::before{content:"";position:absolute;height:18px;width:18px;left:3px;bottom:3px;background:white;border-radius:50%;transition:.3s;box-shadow:0 1px 3px rgba(0,0,0,.15)}
.toggle-switch input:checked+.toggle-slider{background:var(--primary)}
.toggle-switch input:checked+.toggle-slider::before{transform:translateX(20px)}
</style>
<script>
function saveAdminSettings() {
    var btn = document.querySelector("#adminSettingsForm .btn-primary");
    btn.disabled = true; btn.innerHTML = "<span class=\'spinner-border spinner-border-sm\'></span> Saving...";
    var data = {
        library_name: document.getElementById("aLibName").value.trim(),
        smtp_from: document.getElementById("aSmtpFrom").value.trim(),
        issue_days: parseInt(document.getElementById("aIissueDays").value) || 14,
        fine_per_day: parseFloat(document.getElementById("aFinePerDay").value) || 5,
        max_borrow_limit: parseInt(document.getElementById("aMaxBorrow").value) || 3,
        membership_validity_days: parseInt(document.getElementById("aMemValidity").value) || 365,
        max_upload_size: (parseInt(document.getElementById("aMaxUpload").value) || 5) * 1024 * 1024,
        allowed_extensions: document.getElementById("aAllowedExt").value.trim(),
        smtp_host: document.getElementById("aSmtpHost").value.trim(),
        smtp_port: parseInt(document.getElementById("aSmtpPort").value) || 587,
        smtp_user: document.getElementById("aSmtpUser").value.trim(),
        smtp_password: document.getElementById("aSmtpPass").value,
        email_notifications_enabled: document.getElementById("aEmailEnabled").checked,
        current_admin_password: document.getElementById("aCurPw").value,
        new_admin_password: document.getElementById("aNewAdminPw").value
    };
    if(!data.current_admin_password) {
        showToast("Enter your current password to save admin settings", "error");
        btn.disabled = false; btn.innerHTML = "<i class=\'bi bi-check-lg\'></i> Save All Admin Settings";
        return false;
    }
    fetch("/api/admin/settings/save", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    }).then(function(r){ return r.json() }).then(function(d){
        btn.disabled = false; btn.innerHTML = "<i class=\'bi bi-check-lg\'></i> Save All Admin Settings";
        if(d.success) { showToast("Admin settings saved!", "success"); setTimeout(function(){ location.reload(); }, 1000); }
        else showToast(d.error || "Failed", "error");
    }).catch(function(){ btn.disabled = false; btn.innerHTML = "<i class=\'bi bi-check-lg\'></i> Save All Admin Settings"; });
    return false;
}
</script>
''')


@app.route("/api/admin/settings/save", methods=["POST"])
@admin_required
def api_save_admin_settings():
    """Save admin settings to settings_override.json."""
    data = request.get_json() or {}

    # Verify admin password
    from auth import verify_password as _vp, hash_password as _hp
    uid = session["user_id"]
    users = storage.load_users()
    admin = users.get(uid)
    if not admin:
        return jsonify({"success": False, "error": "Admin not found"})
    cur_pw = data.get("current_admin_password", "")
    if not cur_pw or not _vp(cur_pw, admin.password_hash):
        return jsonify({"success": False, "error": "Current password is incorrect"})

    # Build override dict
    override = {}
    mapping = {
        "library_name": "LIBRARY_NAME",
        "smtp_from": "SMTP_FROM",
        "issue_days": "ISSUE_DAYS",
        "fine_per_day": "FINE_PER_DAY",
        "max_borrow_limit": "MAX_BORROW_LIMIT",
        "membership_validity_days": "MEMBERSHIP_VALIDITY_DAYS",
        "max_upload_size": "MAX_UPLOAD_SIZE",
        "allowed_extensions": "ALLOWED_EXTENSIONS",
        "smtp_host": "SMTP_HOST",
        "smtp_port": "SMTP_PORT",
        "smtp_user": "SMTP_USER",
        "email_notifications_enabled": "EMAIL_NOTIFICATIONS_ENABLED",
    }
    for key, cfg_key in mapping.items():
        if key in data:
            override[cfg_key] = data[key]

    # SMTP password (only if provided)
    if data.get("smtp_password"):
        override["SMTP_PASSWORD"] = data["smtp_password"]

    # Change admin password if requested
    if data.get("new_admin_password"):
        npw = data["new_admin_password"]
        if len(npw) >= 6:
            admin.password_hash = _hp(npw)
            log("Admin password changed via admin settings", uid)

    import json
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    override_path = os.path.join(Config.DATA_DIR, "settings_override.json")
    with open(override_path, "w", encoding="utf-8") as f:
        json.dump(override, f, indent=2)

    storage.save_users(users)
    log("Admin settings saved", uid)
    return jsonify({"success": True, "message": "Admin settings saved. Some changes may require a restart."})


if __name__ == "__main__":
    print(f"  📚 Library Management System — Web Interface")
    print(f"  🌐 http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"  🔐 Default login: {Config.DEFAULT_ADMIN_ID} / {Config.DEFAULT_ADMIN_PASSWORD}")
    print(f"  ⌨️  Press Ctrl+K to search books from anywhere")
    socketio.run(app, host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG, allow_unsafe_werkzeug=True)
