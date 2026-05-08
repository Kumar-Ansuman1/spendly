# Spec: Login and Logout

## Overview

Implement user authentication via login and session termination via logout. Login verifies email/password against the database and establishes a session. Logout clears the session and redirects to landing page. This enables users to access protected routes.

## Depends on

Step 1 (Database Setup) - Requires working database with users table and `get_db()` function.
Step 2 (Registration) - Requires existing users who can login.

## Routes

- GET /login — Display login form - public
- POST /login — Process login submission, verify credentials, create session - public
- GET /logout — Clear session and redirect to landing - public (but useful only when logged in)

## Database changes

No database changes. Uses existing users table.

## Templates

- No new templates
- Modify: login.html - Already exists with POST form, add error display

## Files to change

- app.py — Implement POST /login route and GET /logout route

## Files to create

- None

## New dependencies

No new dependencies. Uses `werkzeug.security.check_password_hash` (already in requirements via werkzeug).

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterized queries only
- Passwords verified with werkzeug.security.check_password_hash
- Use CSS variables - never hardcode hex values
- All templates extend base.html
- Validate: email and password provided
- Fetch user by email from database
- If user exists, verify password hash matches
- On success: set session['user_id'] and redirect to profile
- On failure: re-render login.html with error message
- Logout: clear session with session.clear() and redirect to landing

## Definition of done

- [ ] POST /login validates form data
- [ ] Missing fields show error message
- [ ] Invalid email shows generic error (don't reveal which failed)
- [ ] Wrong password shows error message
- [ ] Correct credentials create session with user_id
- [ ] Successful login redirects to profile
- [ ] GET /logout clears session
- [ ] Logout redirects to landing page
- [ ] App tested with valid login
- [ ] App tested with invalid email
- [ ] App tested with wrong password
- [ ] App tested logout flow
