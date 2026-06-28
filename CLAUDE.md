# Book-Tale

## Stack
- **Framework:** Flask (Python), Flask-SocketIO for real-time
- **Storage:** JSON-file based (no database)
- **Frontend:** HTML templates + vanilla JS, custom CSS
- **Auth:** Session-based with password hashing (werkzeug)
- **Testing:** pytest with coverage

## Dev commands
- `python start.py` or `python web_app.py` — start Flask server
- `python seed_data.py` — seed sample data
- `pytest tests/ -v` — run tests
- `flake8 . --max-line-length=120` — lint

## Key conventions
- 4-space indent for Python, 2-space for HTML/CSS/JS
- JSON storage in `data/` directory (not committed)
- Templates in `templates/` (Jinja2), static assets in `static/`
- Config via `config.py` with `.env` overrides
- Routes: `page_routes.py` (web), `social_routes.py` (social features)
