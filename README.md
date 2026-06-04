<div align="center">

# 📚 Library Management System v3.0 — BookTale Edition

**A full-featured, Python-based library management platform with CLI + Web interfaces, AI-powered recommendations, social BookSocial platform, gamification, reading diary, PWA support, and a knowledge base of 11,000+ books.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-black?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-5.0+-gray?style=flat&logo=socket.io)](https://flask-socketio.readthedocs.io)
[![PWA](https://img.shields.io/badge/PWA-Enabled-5A0FC8?style=flat&logo=pwa&logoColor=white)]()
[![License](https://img.shields.io/badge/license-MIT-green?style=flat)]()
[![Tests](https://img.shields.io/badge/tests-53%20passing-brightgreen?style=flat)]()
[![Code style](https://img.shields.io/badge/code%20style-black-000000?style=flat)]()

**CLI Mode** — Rich terminal interface with 60+ features  
**Web Mode** — BookTale cinematic design with dark mode + REST API  
**BookSocial** — Social feed, profiles, reviews, book clubs & achievements  
**Recommendations** — 6 AI strategies powered by Goodreads knowledge base  
**Real-time** — Socket.IO live updates, typing indicators, read receipts  
**PWA** — Offline support, service worker, installable web app  

</div>

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment (optional — defaults work out-of-the-box)
copy .env.example .env

# 3. Launch CLI mode
python main.py

# 4. Or launch the web dashboard
python web_app.py

# 5. Launch with the unified launcher (menu-driven)
python start.py
python start.py --web    # Launch web only
python start.py --cli    # Launch CLI only
python start.py --both   # Launch both

# 6. Run the full test suite
python -m pytest tests/ -v
```

**Default Admin Login** → `ADMIN001` / `admin123`

---

## 🎬 Demo

| Mode | Command | Access |
|------|---------|--------|
| CLI  | `python main.py` | Interactive terminal |
| Web  | `python web_app.py` | `http://localhost:5000` |
| Launcher | `python start.py` | Menu-driven launcher |
| Tests| `python -m pytest tests/ -v` | 53 tests |

> **Web keyboard shortcut:** Press `Ctrl+K` from any page for instant global book search.

---

## 🏗 Project Architecture

```
LIB_MS/
├── main.py                 # CLI entry point — Rich interactive shell
├── web_app.py              # Flask web app — BookTale cinematic design
├── start.py                # Unified launcher (web, CLI, or both)
│
├── library.py              # Core business logic (issue, return, fines)
├── recommender.py          # Recommendation engine (6 strategies)
├── seed_data.py            # Goodreads knowledge base (11,127 books)
├── cover_service.py        # Cover fetching waterfall (OpenLibrary → Google → SVG)
├── email_notifier.py       # SMTP email notification system
├── notifications.py        # In-app notification manager
│
├── book.py                 # Book model & ID generator
├── user.py                 # User model with social + favorite_books fields
├── auth.py                 # Authentication (SHA-256 + salt)
├── diary.py                # Reading diary with custom rating labels
├── reading_challenge.py    # Annual reading challenge with progress tracking
├── reading_progress.py     # Currently reading progress tracker
├── wishlist.py             # Book wishlist / suggestion system
├── series.py               # Book series management
├── lists.py                # Book lists & collections system
├── communities.py          # Book clubs, forums, fan communities & polls
├── gamification.py         # Points, levels, achievements & leaderboards
├── reviews.py              # Review system — ratings, bookshelves, reading stats
├── social.py               # Social feed engine — posts, comments, likes, follows
├── social_routes.py        # Social feed web routes
├── realtime.py             # Socket.IO real-time events manager
├── site_pages.py           # Landing page, features showcase, welcome page
│
├── storage.py              # JSON persistence (thread-safe, cached)
├── backup.py               # Backup & restore system
├── logger.py               # Dual-format activity logging
├── config.py               # Centralized .env configuration
├── exceptions.py           # Custom exception hierarchy
├── utils.py                # Rich-powered CLI helpers
├── _ux_enhance.py          # Smooth UI/UX transition enhancements
│
├── static/
│   ├── css/booktale.css    # Full design system (dark/light, animations, glass cards)
│   ├── js/
│   │   ├── api.js          # Shared API client with retry + toast on error
│   │   ├── animations.js   # Animation engine (stagger reveal, counters, parallax, confetti)
│   │   ├── toast.js        # Queue-based toast notification system
│   │   ├── theme.js        # Cinematic dark/light theme switcher
│   │   ├── search.js       # Live search with cover previews + keyboard nav
│   │   └── a11y.js         # Accessibility enhancements
│   ├── sw.js               # Service Worker (cache strategies + offline)
│   ├── manifest.json       # PWA Web App Manifest
│   ├── offline.html        # Offline fallback page
│   └── icons/              # PWA icon assets
│
├── tests/
│   └── test_library.py     # 53 comprehensive tests
│
├── Recommendation Systems/
│   ├── Dataset/books.csv   # Goodreads 11K-book dataset
│   └── Model/              # ML notebook (KNN, t-SNE, DBSCAN)
│
├── data/                   # Runtime JSON database (auto-created)
├── logs/                   # Activity logs (auto-created)
├── backups/                # Timestamped data backups
├── uploads/                # User-uploaded images (avatars, post images)
│
├── requirements.txt        # Python dependencies
├── .env.example            # Environment configuration template
└── README.md               # You are here
```

---

## ✨ Complete Feature Map (100+ Features)

### 📚 Core Library Operations

| # | Feature | Details |
|---|---------|---------|
| 1 | **Auto Book ID** | Format `BK-2026-0001`, collision-free |
| 2 | **Book CRUD** | Add, update, soft-delete with full metadata |
| 3 | **User Registration** | Role-based (admin / librarian / user) |
| 4 | **Issue Book** | Availability check, auto due-date (14 days) |
| 5 | **Return Book** | Calculates fine, checks reservation queue |
| 6 | **Fine Calculation** | ₹5/day overdue with accrual tracking |
| 7 | **Role-Based Login** | Admin, Librarian, User with distinct menus |
| 8 | **Reservation Queue** | Auto-notify next user on return |
| 9 | **Borrow Limit** | Max 3 books per user (configurable) |
| 10 | **Overdue Tracking** | Days overdue + accrued fine display |
| 11 | **Membership Management** | Auto-expiry, renewal, block/unblock |
| 12 | **Advanced Search** | By title, author, ISBN, category, availability |
| 13 | **Book Spotlight** | Random featured book on dashboard |
| 14 | **ISBN Auto-Lookup** | Auto-fetch from OpenLibrary API |
| 15 | **QR Code Generation** | Per-book QR barcodes (optional) |

### 🎨 Cover Service & Metadata

| # | Feature | Details |
|---|---------|---------|
| 16 | **Cover Fetching Waterfall** | OpenLibrary Covers → Google Books → OpenLibrary search → SVG placeholder |
| 17 | **Dominant Color Extraction** | Median-cut algorithm on 5×5 pixel grid (no Pillow) |
| 18 | **SVG Gradient Placeholders** | Deterministic hue from book title hash |
| 19 | **Google Books Enrichment** | Description, page count, genres auto-fetched |
| 20 | **Refresh Cover API** | Admin endpoint to force re-fetch |
| 21 | **Cover Proxy Endpoint** | `/covers/proxy` with caching headers + domain whitelist |

### 📊 Reports & Analytics

| # | Feature | Details |
|---|---------|---------|
| 22 | **Most Issued Books** | Top books ranked by issue count |
| 23 | **Active Users** | Top borrowers leaderboard |
| 24 | **Issues Today / This Month** | Date-filtered real-time counts |
| 25 | **Fine Collection Report** | Total / Collected / Pending breakdown |
| 26 | **Category Distribution** | Book counts per category |
| 27 | **Monthly Trends Chart** | Bar chart with month-over-month comparison |
| 28 | **Weekly Trend Line Chart** | 7-day issue activity visualization |
| 29 | **Category Doughnut Chart** | Visual category distribution |
| 30 | **Availability Rate** | System-wide availability percentage |
| 31 | **Avg Borrow Duration** | Average days per borrowing session |
| 32 | **CSV Export** | Books, users, transactions, most-issued |
| 33 | **Activity Feed** | Live real-time transaction stream |

### 🤖 Recommendation Engine (6 Strategies)

| # | Strategy | How It Works |
|---|----------|-------------|
| 34 | **Content-Based** | Similar books by category + author match |
| 35 | **Trending** | Most popular in the last 30 days |
| 36 | **All-Time Bestsellers** | Highest total issue count ever |
| 37 | **Personalized** | Collaborative filtering + preference matching |
| 38 | **Co-Borrow** | "Users who borrowed X also borrowed Y" |
| 39 | **Category Highlights** | Top N books per category |

All 6 strategies fall back to the Goodreads knowledge base when the library has fewer than 10 books (cold-start scenario).

### 🌐 Web Dashboard (BookTale Design)

| # | Feature | Details |
|---|---------|---------|
| 40 | **Dashboard** | Stats cards, trends, overdue alerts, activity |
| 41 | **Book Grid/List** | Toggleable views with pagination |
| 42 | **Book Detail Page** | Full info, history, similar books, reservations |
| 43 | **User Management** | List all users with avatars, roles, fines |
| 44 | **Recommendations Page** | Personalized, trending, bestsellers, categories |
| 45 | **Notifications Center** | Time-grouped with type distribution |
| 46 | **Reports Page** | Metrics, charts, fine summary, category table |
| 47 | **Cinematic Dark Mode** | Light/dark theme with localStorage persistence |
| 48 | **Animated Counters** | Scroll-triggered stat counters on dashboard |
| 49 | **Loading Skeletons** | Shimmer placeholders during data fetch |
| 50 | **Quick Search (Ctrl+K)** | Global search overlay with live cover previews |
| 51 | **Responsive Design** | Fully mobile-friendly with sticky sidebars |
| 52 | **User Avatars** | Auto-generated initials with deterministic colors |
| 53 | **Print-Friendly CSS** | Clean print/PDF layout |
| 54 | **PDF Report Export** | Dedicated print-optimized report route |

### 🎭 Animation System & UI

| # | Feature | Details |
|---|---------|---------|
| 55 | **Staggered Card Entrance** | Cards animate in with 40ms delay per card |
| 56 | **Parallax Hero** | Scroll-driven parallax on book covers |
| 57 | **Magnetic Hover** | Elements follow cursor slightly |
| 58 | **Tilt Effect** | Gyroscope (mobile) + mouse tilt on cover cards |
| 59 | **Button Ripples** | Material-style ripple on click |
| 60 | **Confetti Burst** | Canvas-based confetti on achievement unlock |
| 61 | **Typewriter Effect** | Typing animation for taglines |
| 62 | **Page Transitions** | Smooth fade + slide between routes |
| 63 | **Progress Bar** | YouTube-style top-of-page loading bar |
| 64 | **Queue-Based Toasts** | Max 4 visible, auto-dismiss, slide animations |
| 65 | **Smooth Theme Switch** | Overlay blink effect on dark/light toggle |
| 66 | **Reduced Motion Support** | All animations respect `prefers-reduced-motion` |

### 📝 Reading Diary & Custom Ratings

| # | Feature | Details |
|---|---------|---------|
| 67 | **Log Reads** | Track books with date read, re-read status |
| 68 | **Custom Rating Labels** | Perfection / Worth It / Timepass / Skip |
| 69 | **Star Rating** | Traditional 1-5 star as alternative |
| 70 | **Vibe Tags** | Up to 10 custom tags per entry |
| 71 | **Diary Text** | Free-form diary entries with spoiler toggle |
| 72 | **Spoiler Support** | Mark entries as containing spoilers |
| 73 | **Pagination & Filters** | Filter diary by rating label |
| 74 | **Activity Heatmap** | GitHub-style 52×7 SVG grid on profile |
| 75 | **Diary Search** | Full-text search across diary text and tags |
| 76 | **Reading Stats** | Total books, pages, rereads, genre breakdown |

### 🌟 BookSocial: Social Feed Platform

| # | Feature | Details |
|---|---------|---------|
| 77 | **Rich Text Posts** | Create posts with content, book tags, image uploads |
| 78 | **Following Feed** | Posts from followed users ranked by engagement |
| 79 | **Trending Feed** | Reddit-style hot ranking algorithm |
| 80 | **Discover Feed** | Posts from people you haven't discovered yet |
| 81 | **Reddit-Style Voting** | Upvote/downvote with net score display |
| 82 | **Like System** | Heart-based likes with real-time count updates |
| 83 | **Threaded Comments** | Nested replies with 3-level depth |
| 84 | **Book Tagging** | Tag books in posts with auto-search dropdown |
| 85 | **Image Upload** | Upload post images (up to 5MB, multiple formats) |
| 86 | **Hashtags** | Auto-linked hashtags with trending feed |
| 87 | **Follow System** | Follow/unfollow with counts |
| 88 | **Repost / Share** | Share posts to your own feed |
| 89 | **Profile Pages** | Rich profiles with reading stats, shelves, posts |
| 90 | **Profile Showcase** | Favorite 4 books grid, heatmap, Chart.js, badges, diary |
| 91 | **Profile Editing** | Bio, website, location, favorite genres, avatar |
| 92 | **Avatar Upload** | Custom profile pictures via upload |
| 93 | **Author Pages** | Aggregate author view with all their books |
| 94 | **Advanced Search** | Unified search across books, users, posts, reviews |

### 📋 Reviews, Ratings & Bookshelves

| # | Feature | Details |
|---|---------|---------|
| 95 | **Star Ratings** | 1-5 star rating system |
| 96 | **Written Reviews** | Full text reviews with spoiler tag support |
| 97 | **Helpful Votes** | Mark reviews as helpful |
| 98 | **Default Shelves** | Want to Read / Currently Reading / Read |
| 99 | **Custom Shelves** | Create, rename, and delete custom shelves |
| 100 | **Reading Stats** | Total read, avg rating, category breakdown, monthly reading |
| 101 | **Rating Distribution** | Visual breakdown per book (Chart.js) |
| 102 | **Review Comments** | Comment on reviews with user enrichment |

### 🏆 Gamification System

| # | Feature | Details |
|---|---------|---------|
| 103 | **Experience Points** | Earn points for reviews, posts, comments |
| 104 | **7 Reviewer Levels** | New Reader → Bronze → Silver → Gold → Platinum → Diamond → Legendary |
| 105 | **Achievement Badges** | 15 achievements (First Review, Book Critic, Streaks, etc.) |
| 106 | **Daily Streaks** | 3-day, 7-day, and 30-day streak tracking |
| 107 | **Leaderboard** | Top users ranked by points or reviews |
| 108 | **Auto-Achievement Unlock** | Automatically checks and awards on activity |
| 109 | **Level Progression** | Clear next-level tracking with points needed |

### 📚 New Feature Modules

| # | Feature | Details |
|---|---------|---------|
| 110 | **Reading Challenge** | Annual goal with SVG arc progress ring, milestone toasts |
| 111 | **Reading Progress** | Track currently reading books with progress % |
| 112 | **Wishlist** | Suggest books with voting system, approve/deny workflow |
| 113 | **Series Management** | Group books into series with order tracking |
| 114 | **Book Lists** | Custom lists, collaborative, followable, upvotable |

### 📋 Book Lists & Communities

| # | Feature | Details |
|---|---------|---------|
| 115 | **Custom Lists** | Watchlists, top 10, curated collections |
| 116 | **Public/Private** | Toggle visibility on any list |
| 117 | **Collaborative Lists** | Multiple editors per list |
| 118 | **List Following** | Follow lists from other users |
| 119 | **Upvote Lists** | Upvote/downvote public lists |
| 120 | **Weekly Trending Books** | Auto-calculated from recent activity |
| 121 | **Book Clubs** | Create clubs with members, max limits, moderators |
| 122 | **Club Book Selection** | Set a current book for club discussion |
| 123 | **Discussion Forums** | Topics with replies per club |
| 124 | **Polls** | Create polls with multiple choice, expiry |
| 125 | **Fan Communities** | Auto-generated genre/author communities |

### ⚡ Real-Time Features (Socket.IO)

| # | Feature | Details |
|---|---------|---------|
| 126 | **Live Feed Updates** | New posts appear instantly without refresh |
| 127 | **Real-Time Notifications** | Likes, follows, comments delivered instantly |
| 128 | **Live Comments** | Comments appear in real-time for post viewers |
| 129 | **Typing Indicators** | See when someone is typing a comment |
| 130 | **Read Receipts** | See who's viewing a post's comments |
| 131 | **Online Status** | Track which users are currently online |

### 📱 PWA & Performance

| # | Feature | Details |
|---|---------|---------|
| 132 | **Service Worker** | Cache-first (static), network-first (API/HTML), stale-while-revalidate (covers) |
| 133 | **Web App Manifest** | Standalone PWA with icons, shortcuts, theme color |
| 134 | **Offline Fallback Page** | Styled offline page with retry + navigation links |
| 135 | **Preconnect Hints** | Early connections to CDN, Google Fonts, OpenLibrary |
| 136 | **Cache-Control Headers** | Static assets (7d), covers (1d), HTML/API (no-cache) |
| 137 | **Cover Proxy** | `/covers/proxy` with domain whitelist + caching |
| 138 | **Lazy Loading** | All cover images use `loading="lazy" decoding="async"` |

### 🖥️ Landing Page & Site Pages

| # | Feature | Details |
|---|---------|---------|
| 139 | **Landing Page** | Animated hero, live stats, featured books, CTA |
| 140 | **Features Showcase** | Full feature tour with live library statistics |
| 141 | **Welcome / Onboarding** | BookSocial welcome page with guided steps |
| 142 | **Footer Navigation** | Quick links to all platform sections |

### 📧 Email Notification System

| # | Feature | Details |
|---|---------|---------|
| 143 | **Overdue Alerts** | Email when books are overdue |
| 144 | **Reservation Available** | Email when reserved book is returned |
| 145 | **Fine Notices** | Email when fines are applied |
| 146 | **Batch Sender** | Send all overdue alerts at once |
| 147 | **HTML Templates** | Branded responsive email design |
| 148 | **Graceful Degradation** | No-email mode if SMTP unconfigured |

### 🧠 Goodreads Knowledge Base

| # | Feature | Details |
|---|---------|---------|
| 149 | **11,127 Books** | Full Goodreads dataset loaded in memory |
| 150 | **19 Categories** | Auto-inferred via author/title heuristics |
| 151 | **Smart Recommendations** | Trending, similar, author, category strategies |
| 152 | **Search Across Seed** | Full-text search by title, author, ISBN |
| 153 | **One-Click Import** | Import any seed book into your library |
| 154 | **Cold-Start Protection** | Meaningful recs even with an empty library |

### ⚙️ System Features

| # | Feature | Details |
|---|---------|---------|
| 155 | **Password Security** | SHA-256 with 16-byte random salt |
| 156 | **Soft Delete** | Books marked `is_deleted`, preserving history |
| 157 | **Backup & Restore** | Timestamped folder snapshots with metadata |
| 158 | **Auto-Backup on Exit** | Always runs on program close |
| 159 | **Dual Logging** | Text `.log` + structured `.json` files |
| 160 | **Thread-Safe Storage** | File locking prevents concurrent corruption |
| 161 | **In-Memory Cache** | 2-second TTL for frequently accessed data |
| 162 | **JSON Schema Validation** | Data integrity checks on every read/write |
| 163 | **Type Hints** | Full Python typing throughout |
| 164 | **53 Pytest Tests** | Comprehensive test coverage |
| 165 | **Unified Launcher** | `python start.py` for web, CLI, or both |

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/books` | List/search books |
| GET | `/api/books/<id>` | Book details |
| POST | `/api/books/<id>/issue` | Issue a book to a user |
| POST | `/api/books/<id>/return` | Return a book |
| POST | `/api/books/<id>/refresh-cover` | Force re-fetch cover (admin) |
| GET | `/api/recommendations/trending` | Trending books |
| GET | `/api/recommendations/similar/<id>` | Similar books |
| GET | `/api/recommendations/for/<user>` | Personalized recs |
| GET | `/api/recommendations/frequently/<id>` | Co-borrowed books |
| GET | `/api/reports/most-issued` | Most issued report |
| GET | `/api/reports/overdue` | Overdue books list |
| GET | `/api/analytics/monthly` | Monthly issue data |
| GET | `/api/analytics/categories` | Category distribution |
| GET | `/api/analytics/activity` | Recent activity feed |
| GET | `/api/analytics/daily-weekly` | Daily issue counts |
| POST | `/api/email/send-overdue` | Send overdue email alerts |
| GET | `/api/seed/stats` | Goodreads KB statistics |
| GET | `/api/seed/trending` | Trending from seed |
| GET | `/api/seed/search` | Search seed database |
| POST | `/api/books/add-from-seed` | Import a seed book into library |
| GET | `/api/feed` | Social feed |
| POST | `/api/posts` | Create a post |
| POST | `/api/posts/<id>/like` | Like/unlike a post |
| POST | `/api/posts/<id>/vote` | Upvote/downvote a post |
| GET/POST | `/api/posts/<id>/comments` | Get/add comments |
| POST | `/api/follow/<user_id>` | Follow/unfollow user |
| POST | `/api/upload` | Upload images |
| POST | `/api/reviews/<book_id>` | Add review |
| GET | `/api/reviews/<book_id>/list` | List reviews for a book |
| POST | `/api/bookshelves/<book_id>` | Add to shelf |
| POST | `/api/shelves/create` | Create custom shelf |
| GET | `/api/shelves` | Get custom shelves |
| POST | `/api/lists` | Create a book list |
| GET | `/api/lists/my` | My book lists |
| GET | `/api/lists/trending` | Trending book lists |
| POST | `/api/clubs` | Create book club |
| POST | `/api/clubs/<id>/join` | Join/leave club |
| POST | `/api/topics` | Create forum topic |
| POST | `/api/polls` | Create poll |
| POST | `/api/polls/<id>/vote` | Vote on poll |
| GET | `/api/gamification/my` | My gamification stats |
| GET | `/api/gamification/leaderboard` | Global leaderboard |
| GET | `/api/search` | Advanced unified search |
| GET | `/api/search/suggestions` | Search autocomplete |
| GET | `/api/profile/favorites` | Get favorite books |
| PUT | `/api/profile/favorites` | Update favorite books order |
| GET | `/api/profile/heatmap` | Reading activity heatmap data |
| GET | `/api/profile/stats` | Profile reading statistics |
| GET | `/api/diary/heatmap` | Diary activity heatmap data |
| GET | `/api/diary/search` | Diary full-text search |
| GET | `/api/reading-challenge/stats` | Challenge progress |
| GET | `/api/reading-progress/stats` | Currently reading stats |
| GET | `/api/wishlist/stats` | Wishlist statistics |
| GET | `/covers/proxy` | Cover image proxy with caching |
| POST | `/api/clear-cache` | Clear server-side caches (admin) |

---

## 🎨 BookTale Design System

The BookTale UI features a modern, cinematic design system:

### Design Tokens

- **Surfaces**: Dark mode default (`#0f0f13`), light mode optional
- **Accent**: Purple (`#7c6af7`) with glow effects and accent-2 (`#e8507a`)
- **Spring easing**: `cubic-bezier(0.16, 1, 0.3, 1)` throughout
- **Glass cards**: Backdrop blur with subtle borders
- **Cover cards**: 2:3 aspect ratio, hover scale + overlay, stagger animation

### Animation Engine (`static/js/animations.js`)

All 9 animation functions respect `prefers-reduced-motion`:

| Function | Description |
|----------|-------------|
| `staggerReveal()` | IntersectionObserver-based staggered reveal |
| `animateCounter()` | Morphing number counter (0 → 142) |
| `initParallax()` | Scroll-driven parallax on hero images |
| `burstConfetti()` | Canvas confetti on achievement unlock |
| `magneticHover()` | Elements follow cursor slightly |
| `addRipple()` | Material-style ripple on button click |
| `initPageTransitions()` | Smooth fade + slide page transitions |
| `initTilt()` | Mouse/gyroscope tilt on cover cards |
| `typewriter()` | Typing animation for taglines |

### Toast Notifications (`static/js/toast.js`)

Queue-based system with max 4 visible toasts, auto-dismiss, SVG icons, close button.

### Live Search (`static/js/search.js`)

Debounced 300ms, fetch `/api/books?q=`, arrow key nav, Enter to navigate, scaleY dropdown animation.

### Theme Switcher (`static/js/theme.js`)

Dark/light toggle with localStorage persistence, cinematic blink overlay on switch.

---

## 📖 Reading Diary & Profile Showcase

### Diary System

Users can log reads with custom rating labels:

| Rating Label | Color | Meaning |
|-------------|-------|---------|
| 📖 Perfection | Teal (#0D9488) | A masterpiece |
| ☕ Worth It | Green (#16A34A) | Worth the read |
| ⌛ Timepass | Amber (#D97706) | Timepass |
| ❌ Skip | Red (#DC2626) | Skip it |

### Profile Showcase

The profile page includes:
- **Favorite 4 Books Grid** — Drag-and-drop reordering with debounced save
- **Reading Heatmap** — GitHub-style 52×7 SVG grid with tooltips
- **Chart.js Stats** — Books by month (bar), rating distribution (doughnut)
- **Badges Grid** — Locked/unlocked display with burst confetti on unlock
- **Recent Diary Entries** — Cover thumbnail + date + rating badge + text
- **Animated Stat Counters** — Scroll-triggered count-up animations
- **Reading Challenge Ring** — SVG arc progress ring

---

## 📱 PWA Features

BookTale is a fully installable Progressive Web App:

| Feature | Implementation |
|---------|---------------|
| **Service Worker** | Cache-first for CSS/JS/fonts, network-first for API/HTML, stale-while-revalidate for cover images |
| **Manifest** | Standalone display, `#7c6af7` theme color, shortcuts to Books/Diary/Search |
| **Offline Fallback** | Styled offline page with retry button and nav links |
| **Preconnect** | Early connections to cdn.jsdelivr.net, fonts.gstatic.com, covers.openlibrary.org |
| **Cache-Control** | Static: 7d immutable, Covers: 1d, Pages: no-cache |
| **Cover Proxy** | `/covers/proxy?url=` with domain whitelist and caching headers |

---

## 📦 Dataset: Goodreads Knowledge Base

The system includes a **Goodreads dataset** of **11,127 books** across **19 categories**. Used for cold-start recommendations when the library has fewer than 10 books, browse & import from seed data, category exploration, and author lookup.

---

## 🎮 BookSocial Gamification

Users earn **experience points** and unlock **achievement badges** by participating:
- **7 Levels**: New Reader (0 pts) → Legendary Reader (5,000 pts)
- **15 Achievements**: First Review, Book Critic, Social Butterfly, Streak milestones, and more
- **Daily Streaks**: 3-day, 7-day, and 30-day tracking

---

## 👥 Roles & Permissions

| Action | Admin | Librarian | User |
|--------|:-----:|:---------:|:----:|
| Add / Edit / Delete Books | ✅ | ❌ | ❌ |
| Register Users | ✅ | ❌ | ❌ |
| Issue / Return Books | ✅ | ✅ | ❌ |
| Search & Browse | ✅ | ✅ | ✅ |
| View Own Books / Fines | ✅ | ✅ | ✅ |
| Recommendations | ✅ | ✅ | ✅ |
| Notifications | ✅ | ✅ | ✅ |
| Reports & Analytics | ✅ | ❌ | ❌ |
| Backup & Restore | ✅ | ❌ | ❌ |
| View Activity Logs | ✅ | ❌ | ❌ |
| Web Dashboard Access | ✅ | ✅ | ✅ |
| Social Feed & Posts | ✅ | ✅ | ✅ |
| Reviews & Shelves | ✅ | ✅ | ✅ |
| Book Clubs & Forums | ✅ | ✅ | ✅ |
| Manage Club Members | ✅ | ✅ | ❌ |
| View Leaderboard | ✅ | ✅ | ✅ |

---

## 🔧 Configuration

All settings are configurable via `.env` file or environment variables:

```ini
# Default Admin Credentials
DEFAULT_ADMIN_ID=ADMIN001
DEFAULT_ADMIN_PASSWORD=admin123

# Loan & Fine Settings
ISSUE_DAYS=14
FINE_PER_DAY=5.0
MAX_BORROW_LIMIT=3
MEMBERSHIP_VALIDITY_DAYS=365

# Flask Web Server
SECRET_KEY=change-this-to-a-random-secret-key
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True

# Upload Settings
MAX_UPLOAD_SIZE=5242880        # 5 MB
ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.gif,.webp

# SMTP Email (leave blank to disable)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@libraryms.com
LIBRARY_NAME=Library Management System
EMAIL_NOTIFICATIONS_ENABLED=True
```

---

## 🧪 Testing

```bash
# Run all 53 tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=. --cov-report=term

# Run a specific test class
python -m pytest tests/ -k "TestRecommender" -v
```

### Test Coverage

| Module | Tests | What's Covered |
|--------|:-----:|----------------|
| `Book` | 3 | Creation, serialization, display |
| `User` | 4 | Creation, status, borrow limit, serialization |
| `Auth` | 6 | Password hashing, login, logout, roles |
| `Library` | 18 | CRUD, issue/return, fines, overdue, search |
| `Recommender` | 5 | Similar, trending, category, personalized, categories |
| `Notifications` | 6 | Add, read, batch operations, overdue, reservation |
| `Storage` | 6 | Save/load, transactions, fines, notifications, cache |
| `Backup` | 3 | Create, list, restore |
| `Logger` | 2 | Logging, retrieval |

---

## 💡 Architecture Decisions

**Why JSON instead of a database?** Zero-dependency setup. No PostgreSQL, no SQLite schema migrations. JSON files are human-readable, easy to inspect, and trivially backup-able.

**Why in-memory caching with a 2-second TTL?** The `storage.py` module caches JSON reads to avoid repeated disk I/O during rapid-fire operations. The 2-second TTL ensures data is never stale for long.

**Why soft-delete for books?** When a book is "deleted", it's marked `is_deleted = True` but all its transaction history is preserved. Borrowing statistics, popularity rankings, and recommendation signals remain accurate.

**Why SHA-256 with salt instead of bcrypt?** Zero external dependencies. Uses Python's built-in `hashlib` with a random 16-byte salt. Adequate for local/small-team use.

**Why Socket.IO for real-time?** Flask-SocketIO provides seamless WebSocket integration with automatic fallback to long-polling. Enables live feed updates, typing indicators, and read receipts.

**Why modular service classes?** Each feature (diary, challenge, reading progress, etc.) is a self-contained service class with its own data schema, enabling independent extension.

**Why PWA without a build tool?** Vanilla ES6 modules served statically. No webpack, no Vite. The service worker handles caching strategies directly, leveraging the browser's native capabilities.

---

## 🚀 Deployment

```bash
# Production web server
pip install waitress
waitress-serve --port=5000 web_app:app

# Or with Gunicorn (Linux/Mac)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

**Production checklist:**
1. Copy `.env.example` to `.env`
2. Set a strong `SECRET_KEY`
3. Set `FLASK_DEBUG=False`
4. Configure SMTP for email notifications
5. Set `EMAIL_NOTIFICATIONS_ENABLED=True`
6. Use a reverse proxy (nginx/Caddy) for TLS termination
7. Consider using `waitress` (Windows) or `gunicorn` (Linux/Mac)

---

## 📁 Data Persistence

All data is stored in the `data/` directory as JSON files:

```
data/
├── books.json              # Book catalog (with cover_url, description, dominant_color)
├── users.json              # User accounts (with favorite_books, social profile)
├── transactions.json       # Issue/return history
├── reservations.json       # Reservation queues
├── fines.json              # Fine records
├── notifications.json      # In-app notifications
├── diary.json              # Reading diary entries
├── challenges.json         # Annual reading challenges
├── reading_progress.json   # Currently reading progress
├── wishlist.json           # Book wishlist suggestions
├── series.json             # Book series
├── posts.json              # Social feed posts
├── comments.json           # Post comments
├── follows.json            # Follow relationships
├── reviews.json            # Book reviews
├── bookshelves.json        # Bookshelf assignments
├── shelves_custom.json     # Custom shelf definitions
├── review_comments.json    # Review comments
├── book_lists.json         # Book lists & collections
├── clubs.json              # Book clubs
├── forum_topics.json       # Discussion forum topics
├── forum_replies.json      # Forum replies
├── polls.json              # Polls & votes
├── gamification.json       # Points, levels, achievements, streaks
├── activity.json           # Activity log (JSON format)
└── search_index.json       # Inverted search index
```

---

## 📜 License

This project is provided for educational and personal use. The Goodreads dataset (`books.csv`) is sourced from the [Goodreads 10K dataset](https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks) and is subject to its original license terms.

---

<div align="center">

Built with ❤️ using Python, Flask, Socket.IO, Bootstrap 5, Rich, and Chart.js

**v3.0 — BookTale Edition • 165+ features • 30+ modules • 53 tests • PWA-enabled**

</div>
