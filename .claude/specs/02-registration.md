# Spec: Registration

## Overview

Implement user registration functionality. Users submit the registration form which creates a new account in the database. This is the entry point for new users to join Spendly.

## Depends on

Step 1 (Database Setup) - Requires working database with users table and `get_db()` function.

## Routes

- GET /register — Display registration form (already implemented) - public
- POST /register — Process registration form submission - public

## Database changes

No database changes. Uses existing users table with columns: id, name, email, password_hash, created_at.

## Templates

- No new templates
- Modify: register.html - Already exists with form pointing to POST /register

## Files to change

- app.py — Implement POST /register route with form handling

## Files to create

- None

## New dependencies

No new dependencies.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterized queries only
- Passwords hashed with werkzeug.security.generate_password_hash
- Use CSS variables - never hardcode hex values
- All templates extend base.html
- Validate: name, email, password provided
- Minimum password length: 8 characters
- Hash password before storing
- Handle duplicate email (UNIQUE constraint violation)
- On success: redirect to login with success message (flash)
- On error: re-render register.html with error message

## Definition of done

- [ ] POST /register validates form data
- [ ] Invalid/missing fields show error message
- [ ] Passwords shorter than 8 characters rejected
- [ ] Passwords hashed before storing
- [ ] Duplicate email handled gracefully
- [ ] Successful registration redirects to login
- [ ] App tested with valid registration
- [ ] App tested with duplicate email
- [ ] App tested with short password