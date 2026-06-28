# Book-Tale — Project Overview

## 1. Project Title
**Book-Tale** — A community-driven library management system with social features, book recommendations, reading challenges, and real-time updates via Socket.IO.

## 2. Executive Summary
Book-Tale is a Flask-based web application that digitizes library operations — book cataloging, borrowing/returning, reservations, fines, and user management — while adding a social layer: user posts, comments, follows, reading challenges, and gamification. It integrates with OpenLibrary and Google Books APIs for cover images and metadata. The application uses JSON file-based storage (no external database required) and provides email notifications for overdue books and reservation pickups. Real-time features (live notifications, feed updates) are powered by Flask-SocketIO.

## 3. Problem Statement
Small libraries and community book exchanges lack affordable digital management tools that combine traditional library operations (catalog, loans, fines) with modern social engagement features (reviews, recommendations, reading challenges). Existing solutions are either expensive enterprise systems or lack community features.

## 4. Objectives
- Provide a complete digital catalog and loan management system
- Enable social interaction around books (posts, reviews, follows)
- Deliver personalized book recommendations using multiple algorithms
- Gamify reading through challenges, badges, and achievements
- Send timely email notifications for overdue items and reservations
- Offer real-time UI updates via Socket.IO

## 5. Key Features
- **Book catalog:** Add, search, browse by category; ISBN lookup with auto-populated metadata
- **Borrowing system:** Checkout, return, renew; configurable loan periods and overdue fines
- **User management:** Registration, login, roles (member/librarian/admin), membership tiers
- **Social feed:** User posts, comments, likes, follows, notifications with real-time updates
- **Recommendations:** Content-based, popularity-based, collaborative filtering, rule-based fallback
- **Reading challenges:** Create/join challenges with progress tracking
- **Gamification:** XP, levels, badges, streak tracking
- **Wishlists:** Personal and community book wishlists
- **Series management:** Group books into series
- **Real-time updates:** Socket.IO for live notifications and feed updates
- **Email notifications:** SMTP-based alerts for overdue, reservations, fines
- **AI Reading Companion:** Rule-based Q&A chatbot for book recommendations
- **Admin settings:** Web-based system configuration for loan policies, SMTP, upload limits

## 6. System Architecture
```
User Browser (Flask templates + JavaScript + Socket.IO client)
        │
        ▼
  Flask Application (web_app.py + route modules)
        │
        ├── Social features (social_routes.py — 25+ API endpoints)
        ├── Page routes (page_routes.py — 10+ page routes)
        ├── New features (new_features_routes.py)
        ├── API endpoints (search, analytics, settings, AI chat)
        │
        ▼
  Service Layer (Python modules)
        ├── book.py, user.py, library.py
        ├── recommender.py, cover_service.py
        ├── notifications.py, email_notifier.py
        ├── gamification.py, reading_challenge.py
        ├── social.py, reviews.py, lists.py, communities.py
        └── storage.py, auth.py, config.py, realtime.py
        │
        ▼
  Storage (JSON file-based on local filesystem)
        │
        ▼
  External APIs: OpenLibrary, Google Books (cover images)
  External: SMTP (email notifications)
  Real-time: Socket.IO (live feed updates, notifications)
```

## 7. Tech Stack
| Category | Technology |
|---|---|
| **Language** | Python 3.x |
| **Web Framework** | Flask with Jinja2 templates, Flask-CORS |
| **Real-time** | Flask-SocketIO |
| **Storage** | JSON files (no database engine) |
| **External APIs** | OpenLibrary, Google Books (via requests) |
| **Email** | smtplib (standard library) |
| **Testing** | pytest, pytest-cov |
| **Data** | pandas, numpy |
| **UI Utilities** | rich (CLI formatting), pyqrcode, pypng |
| **Configuration** | python-dotenv |

## 8. Architecture Diagram
See Section 6 — this is a monolithic Flask application. All components run in the same process with file-based JSON storage and Socket.IO for real-time features.

## 9. Folder Structure
```
Book-Tale/
├── main.py               # Application entry point (bootstrap function)
├── web_app.py            # Flask app setup + core routes + Socket.IO init
├── config.py             # Configuration (env vars, constants, library settings)
├── book.py               # Book dataclass, categories, and helpers
├── user.py               # User dataclass and helpers
├── library.py            # Core library operations (borrow, return, reserve)
├── social.py             # Social graph, follows, feed generation
├── social_routes.py      # API routes for social features (25+ endpoints)
├── page_routes.py        # Web page routes (explore, shelves, notifications, etc.)
├── new_features_routes.py# Routes for series, challenges, wishlists
├── recommender.py        # Recommendation engine (multiple strategies)
├── cover_service.py      # Book cover image fetching (OpenLibrary, Google Books)
├── notifications.py      # In-app notification system
├── email_notifier.py     # SMTP email alerts
├── gamification.py       # XP, levels, badges, streaks
├── reading_challenge.py  # Reading challenge management
├── reading_progress.py   # Reading progress tracking
├── reviews.py            # Book reviews and ratings
├── series.py             # Book series management
├── wishlist.py           # Wishlist functionality
├── lists.py              # Custom book lists
├── communities.py        # Community/group management
├── diary.py              # Reading diary entries
├── realtime.py           # Socket.IO event handlers for real-time updates
├── utils.py              # Shared utility functions
├── backup.py             # Data backup utilities
├── seed_data.py          # Seed data for testing/demo
├── seed_users.py         # Seed user accounts
├── auth.py               # Authentication helpers (hash, tokens)
├── exceptions.py         # Custom exception classes
├── logger.py             # Logging configuration
├── storage.py            # JSON file persistence layer
├── site_pages.py         # Static site pages
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
└── tests/                # Test suite (pytest)
```

## 10. Module Overview
- **library.py:** Core business logic — book checkouts, returns, renewals, reservations, fines calculation
- **social.py / social_routes.py:** Social graph (follows, followers), feed generation, post CRUD, comments, likes, hashtags, voting, reports
- **recommender.py:** Multi-strategy recommendation engine with trending, personalized, and all-time-best algorithms
- **gamification.py:** XP levels (1-50), badges (20+), streak tracking, leaderboards, achievements
- **reading_challenge.py:** Time-bound challenges with progress tracking
- **cover_service.py:** Fetches covers from OpenLibrary (primary) and Google Books (fallback); generates placeholder SVGs
- **email_notifier.py:** HTML email templates for welcome, verification, password reset, overdue, reservation available, fine notifications
- **realtime.py:** Socket.IO event handlers for real-time updates (new posts, likes, notifications)
- **reviews.py:** Book review system with ratings, helpful votes, comments, spoiler tags
- **auth.py:** Password hashing (werkzeug), token generation/verification for email verification and password reset

## 11. Database Overview
Not applicable — this project uses JSON file-based storage. Data files are stored in a configurable directory. There are no SQL tables, ORM schemas, or database migrations.

Key data entities stored as JSON:
- Books (title, author, ISBN, category, copies, availability)
- Users (profile, role, membership, settings, favorite_books, privacy settings)
- Transactions (borrow/return records with dates)
- Posts and comments with likes
- Reading challenges and progress
- Gamification state (XP, badges, streaks, achievements)
- Wishlist items
- Diary entries (reading journal)
- Notifications
- Custom shelves
- Fines records
- Reviews and ratings

## 12. API Overview
The application exposes REST-like API endpoints alongside template-rendered routes:

### Social API (from social_routes.py)
- `GET /api/feed` — Get feed posts (following/trending/discover)
- `POST /api/posts` — Create a social post
- `POST /api/posts/<id>/like` — Like/unlike a post
- `POST /api/posts/<id>/repost` — Repost
- `POST /api/posts/<id>/vote` — Upvote/downvote
- `POST /api/posts/<id>/delete` — Delete post
- `GET/POST /api/posts/<id>/comments` — List/add comments
- `POST /api/comments/<id>/reply` — Reply to comment
- `POST /api/upload` — Upload file (image)
- `POST /api/follow/<user_id>` — Follow/unfollow
- `GET /api/hashtags/trending` — Trending hashtags
- `GET /api/hashtags/<tag>/posts` — Posts by hashtag
- `GET /api/search` — Advanced search (books, users, posts)
- `GET /api/search/suggestions` — Search autocomplete

### Reviews & Shelves
- `POST /api/reviews/<book_id>` — Add review
- `GET /api/reviews/<book_id>/list` — List reviews
- `POST /api/reviews/<review_id>/helpful` — Mark review helpful
- `POST /api/bookshelves/<book_id>` — Add to shelf
- `GET /api/bookshelves/status/<book_id>` — Check shelf status
- `POST /api/bookshelves/<book_id>/remove` — Remove from shelf
- `POST /api/shelves/create` — Create custom shelf
- `GET /api/shelves` — List custom shelves
- `DELETE /api/shelves/<name>` — Delete shelf

### Book Lists
- `POST /api/lists` — Create list
- `GET/PUT/DELETE /api/lists/<id>` — List operations
- `POST/DELETE /api/lists/<id>/books` — Add/remove books
- `POST /api/lists/<id>/follow` — Follow/unfollow list
- `POST /api/lists/<id>/upvote` — Upvote list

### Settings
- `POST /api/settings/save` — Save user settings
- `POST /api/admin/settings/save` — Save admin settings

### Analytics & Data
- `GET /api/analytics/monthly` — Monthly stats
- `GET /api/analytics/categories` — Category distribution
- `GET /api/analytics/activity` — Recent activity
- `GET /api/seed/stats` — Seed dataset stats
- `GET /api/books/trending` — Trending books
- `GET /api/books/random` — Random book
- `GET /api/users/suggested` — Suggested users
- `GET /api/reading-streak` — User reading streak

### AI
- `POST /api/ai/chat` — AI Reading Companion (rule-based chatbot)

### Page Routes (from page_routes.py)
- `/explore` — Discover books, readers, hashtags
- `/notifications` — Notification center with filtering
- `/shelves` — My shelves with tabs (want_to_read, reading, read, favorites)
- `/recommendations` — For You, Trending, Bestsellers, By Genre
- `/clubs` — Book clubs listing and creation
- `/reading-calendar` — GitHub-style reading heatmap
- `/analytics` — Reading analytics with charts
- `/admin/users` — User management
- `/dashboard` — Admin dashboard with stats, levels, streaks, achievements
- `/books` — Book grid/list with search and filtering
- `/reports` — Reports & analytics for admins
- `/profile`, `/profile/edit` — User profiles
- `/author/<name>` — Author page
- `/settings`, `/admin/settings` — User and admin settings
- `/help` — Help & support page

## 13. Authentication & Authorization
- **Registration/login:** Custom implementation using werkzeug `generate_password_hash` / `check_password_hash` (pbkdf2:sha256)
- **Roles:** Three tiers — member (default), librarian, admin
- **Session-based auth:** Flask sessions with `login_required` and `admin_required` decorators
- **Email verification:** Token-based email verification flow
- **Password reset:** Token-based password reset with expiry
- **Settings-based preferences:** Notification preferences, privacy controls, theme, font size
- No OAuth, no JWT, no 2FA

## 14. Data Flow
1. User searches/browses books → Flask renders Jinja2 template
2. User checks out a book → library.py updates JSON storage, creates transaction record
3. Due date approaches → email_notifier.py sends reminder (triggered on access)
4. User returns book → library.py calculates fines if overdue, updates availability
5. User writes a review → review is stored, recommender re-indexes for future recommendations
6. User creates a post → Socket.IO emits real-time update to followers' feeds
7. User receives notification → Socket.IO pushes to UI in real-time

## 15. Request Lifecycle
1. HTTP request → Flask routing (web_app.py, social_routes.py, page_routes.py, new_features_routes.py)
2. Decorator check: `login_required` or `admin_required` (session-based)
3. Route handler calls business logic function (library.py, social.py, recommender.py, etc.)
4. Business logic reads/writes JSON storage via storage.py
5. Route handler renders Jinja2 template or returns JSON response
6. Socket.IO events are emitted for real-time updates when applicable

## 16. External Integrations
| Service | Purpose | Auth Method |
|---|---|---|
| **OpenLibrary API** | Fetch book cover images and metadata | None (public API) |
| **Google Books API** | Fallback cover image and metadata | None (public API, may require key) |
| **SMTP (email)** | Send welcome, verification, overdue, fine notifications | Configurable SMTP credentials |

## 17. Environment Variables
| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask session secret key |
| `SMTP_SERVER` | SMTP server hostname |
| `SMTP_PORT` | SMTP server port |
| `SMTP_USERNAME` | SMTP authentication username |
| `SMTP_PASSWORD` | SMTP authentication password |
| `SMTP_FROM_EMAIL` | Sender email address for notifications |
| `DATA_DIR` | Directory for JSON data files (optional, default: data/) |

## 18. Configuration
The `Config` class in `config.py` loads from `.env` files and supports runtime overrides via `settings_override.json`. It defines:
- Loan policies (max books, loan period days, fine rate)
- Upload settings (allowed extensions, max file size)
- Directory paths for data storage and uploads
- SMTP configuration
- Library name, default admin credentials
- Email verification and password reset token settings

## 19. Security Measures
- **Password hashing:** werkzeug `generate_password_hash` (pbkdf2:sha256)
- **Session-based auth:** Flask sessions with secret key from env
- **Login decorators:** `login_required` and `admin_required` guard routes
- **Input validation:** Email format validation, name validation, password strength check
- **Email verification:** Token-based email verification
- **Password reset tokens:** Time-limited tokens with verification
- **Anti-enumeration:** Forgot password does not reveal if account exists
- CORS is not configured (not needed for same-origin Flask app)

## 20. Logging & Monitoring
Basic Python logging configured via the `logger.py` module. No external monitoring, metrics collection, or alerting is configured.

## 21. Error Handling
Standard Flask error handling with `@app.errorhandler` decorators for 404 and 500. Business logic functions return success/error messages to route handlers. Custom `AuthenticationError` exception class for login failures.

## 22. Performance Optimizations
- **Recommendation caching:** Recommendation results are cached and refreshed periodically
- **Cover image caching:** Book cover images are fetched and stored locally
- No database indexes (JSON storage), no pagination on social feeds, no async processing

## 23. Deployment Architecture
No deployment configuration files found (no Dockerfile, docker-compose.yml, Procfile, or platform configs). The application runs with `python web_app.py` (uses Socket.IO's `run()` method). Deployable as a standard Flask app on any Python-compatible hosting (Render, Railway, Heroku, or VPS). Note: Socket.IO requires WebSocket support from the hosting provider.

## 24. Testing Strategy
- **Framework:** pytest with pytest-cov
- **Test files:** Located in `tests/` directory
- Tests cover: library operations, user management, social features, recommendations
- No CI pipeline configured

## 25. Development Workflow
No CONTRIBUTING.md found. No branch conventions, commit conventions, or PR templates documented.

## 26. Known Limitations
- **JSON file storage:** Not suitable for concurrent users; no ACID transactions; data loss risk on crash
- **No database:** No indexing, no query optimization, all data loaded into memory
- **SMTP dependency:** Email notifications fail silently if SMTP is not configured
- **Limited test coverage:** Tests exist but don't cover all modules
- **No containerization:** No Dockerfile for reproducible deployments
- **scikit-learn not used:** Recommendations use pandas/numpy-based logic, not ML libraries

## 27. Future Roadmap
No documented roadmap found. Evidence from code suggests potential future work on:
- Database migration (SQLite/PostgreSQL)
- Enhanced ML-based recommendations
- Enhanced social features

## 28. Troubleshooting
- **App crashes on start:** Check `SECRET_KEY` env var is set. Verify Python dependencies are installed (`pip install -r requirements.txt`).
- **Book covers not loading:** The OpenLibrary API may be rate-limiting; covers fall back to generated SVGs.
- **Email not sending:** Verify SMTP env vars are correct. Check for firewall/network issues.
- **Recommendations not working:** Run `seed_data.py` to populate sample data if the collection is empty.
- **Socket.IO not connecting:** Ensure your hosting provider supports WebSocket connections.

## 29. FAQ
- **How to run?** `pip install -r requirements.txt && python web_app.py`
- **How to reset the database?** Delete the JSON data files in the data directory — they will regenerate with defaults.
- **How to add the admin user?** Run `seed_users.py` or use default admin credentials from config.
- **What external APIs does it use?** OpenLibrary for book covers, Google Books as fallback.

## 30. Contributing Guidelines
Not yet defined. No CONTRIBUTING.md file exists in the repository.

## 31. License
No license file found in the repository root.

## 32. Maintainers & Contacts
No author/maintainer information specified in source files or package metadata.
