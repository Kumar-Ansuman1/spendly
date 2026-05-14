---
# Spec: Add Expense

## Overview
This feature allows logged-in users to add new expenses to their tracking system. Users can specify amount, category, date, and optional description for each expense. This implements the core expense tracking functionality of the Spendly application.

## Depends on
Step 4 (Profile page) and Step 6 (Date filter for profile page) - requires user authentication and database setup.

## Routes
- `GET /expenses/add` — Display expense addition form — logged-in
- `POST /expenses/add` — Process form submission and add expense to database — logged-in

## Database changes
No database changes required. The expenses table already exists with columns: id, user_id, amount, category, date, description, created_at.

## Templates
- **Create:** templates/expenses/add.html
- **Modify:** 
  - base.html - Add link to add expense in navigation (optional, but common)
  - profile.html - Ensure new expenses appear in list (should happen automatically)

## Files to change
- app.py - Replace placeholder route with actual implementation
- base.html - Add navigation link to add expense (optional)
- profile.html - May need to ensure proper display (likely automatic)

## Files to create
- templates/expenses/add.html - Form for adding new expenses
- Possibly templates/expenses/_form.html - reusable form partial (optional)

## New dependencies
No new dependencies required. Uses existing Flask, Werkzeug, and SQLite dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (already implemented elsewhere)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Form must validate: amount required and positive, category required, date required and valid YYYY-MM-DD
- After successful addition, redirect to profile page with success message
- Use flash messages for user feedback
- Check that user is logged in (use @login_required decorator)
- Get current user_id from session

## Definition of done
A specific testable checklist. Each item must be something that can be verified by running the app.
- User can navigate to /expenses/add when logged in
- Form displays with fields for amount, category, date, description
- Form validates input (amount > 0, valid date, required fields)
- On successful submission, expense is added to database
- User is redirected to profile page after submission
- New expense appears in profile expenses list
- Appropriate error messages shown for invalid input
- User cannot access add expense page when not logged in (redirects to login)
- Form resets after successful submission
- Date field defaults to today's date (optional enhancement)
- Category field uses same categories as in seed data (Food, Transport, Bills, Health, Entertainment, Shopping, Other) or allows custom input
---