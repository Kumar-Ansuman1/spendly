# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Spendly is a Flask-based expense tracking web application. This is a learning project where students progressively implement features across multiple steps.

## Development Commands

### Running the Application
```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Unix)
source .venv/bin/activate

# Run the Flask development server
python app.py
```

The app runs on `http://localhost:5001` with debug mode enabled.

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Running Tests
```bash
pytest
```

## Architecture

### Application Structure
- `app.py` — Main Flask application with all routes. Currently has placeholder routes for `/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit`, and `/expenses/<id>/delete` that students will implement.
- `database/db.py` — Database module (placeholder for students to implement). Should contain:
  - `get_db()` — Returns SQLite connection with row_factory and foreign keys enabled
  - `init_db()` — Creates all tables using CREATE TABLE IF NOT EXISTS
  - `seed_db()` — Inserts sample data for development
- `templates/` — Jinja2 templates with `base.html` as the parent template
- `static/css/style.css` — All styling
- `static/js/main.js` — JavaScript (currently minimal placeholder)

### Template Inheritance
All templates extend `base.html` which provides:
- Navigation bar with brand, sign in, and get started links
- Footer with terms and privacy links
- Common head elements (Google Fonts, CSS, JS)

Templates use `{% block %}` for:
- `title` — Page title
- `head` — Additional head elements
- `content` — Main page content
- `scripts` — Additional JavaScript

### Current Routes
- `/` — Landing page
- `/register` — Registration page
- `/login` — Login page
- `/terms` — Terms and conditions
- `/privacy` — Privacy policy
- `/logout` — Placeholder (Step 3)
- `/profile` — Placeholder (Step 4)
- `/expenses/add` — Placeholder (Step 7)
- `/expenses/<id>/edit` — Placeholder (Step 8)
- `/expenses/<id>/delete` — Placeholder (Step 9)

### Landing Page Features
The landing page includes:
- Hero section with CTA buttons
- "See how it works" button that opens a YouTube video modal
- Feature cards highlighting key functionality
- CTA section
- Video modal with YouTube embed (https://www.youtube.com/embed/-Lt-ntUDj-g)

## Notes

- The project uses SQLite for data persistence
- The database module is intentionally left as a placeholder for students to implement
- All placeholder routes return string messages indicating which step they belong to
- The app uses DM Serif Display and DM Sans fonts from Google Fonts
