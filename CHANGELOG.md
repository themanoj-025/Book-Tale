# Changelog

All notable changes to **Book-Tale** are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-06-01

### Added

#### Core Application
- Flask web application with Jinja2 templating
- Book CRUD with metadata, genres, tags, and cover images
- User registration, login, and profile management
- Role-based access control: Member, Librarian, Admin
- Session-based authentication with Flask sessions

#### Social Features
- Book reviews, ratings, and comments
- User communities and groups
- Reading lists (custom shelves)
- Bookmarking system
- 25+ social API endpoints for community interactions

#### Reading Experience
- Reading progress tracking with page/percentage updates
- Reading challenges with goals and achievements
- Reading calendar and streak tracking
- Gamification: badges, XP, leaderboards
- Wishlist management

#### Discovery & Recommendations
- Book recommendation engine
- Series management and tracking
- Search and browse by genre, author, tags
- Trending and popular books

#### Real-Time Features
- Flask-SocketIO integration for real-time updates
- Live notifications for social interactions
- PWA support for mobile-friendly experience

#### AI Integration
- AI Reading Companion for book recommendations and discussions
- Personalized book suggestions based on reading history

#### Administration
- Admin dashboard with analytics
- User management and moderation tools
- Content management for books and reviews
- System settings configuration

#### Infrastructure
- JSON file-based storage with backup and recovery
- Email notifications via SMTP
- QR code generation for sharing
- Comprehensive logging with `rich` console output
- CORS support for API access

---

## [0.1.0] — Initial Development

### Added
- Project scaffolding and Flask application setup
- Basic book and user models
- Initial template structure
- Authentication foundation
