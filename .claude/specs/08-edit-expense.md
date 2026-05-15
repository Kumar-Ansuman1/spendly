---
# Spec: Edit Expense

## Overview
This feature allows logged-in users to edit existing expenses. Users can navigate to an expense edit page from their profile's transaction list, modify the amount, category, date, and description, and save changes back to the database. This completes the CRUD cycle for expenses alongside the existing add functionality.

## Depends on
Steps 4 (Profile page), 6 (Date filter for profile page), and 7 (Add expense) must be complete. Requires user authentication, database with expenses table, and existing add expense pattern.

## Routes
- `GET /expenses/<int:id>/edit` — Display edit expense form with current values — logged-in, owner only
- `POST /expenses/<int:id>/edit` — Process form submission and update expense in database — logged-in, owner only

## Database changes
No new tables or columns. Requires a new query function `get_expense_by_id` in `database/queries.py` to fetch a single expense by its ID for pre-populating the edit form.

## Templates
- **Create:** templates/expenses/edit.html — Edit form pre-populated with existing expense data
- **Modify:**
  - templates/profile.html — Add "Edit" link/button in the transactions table rows
  - base.html — Add navigation link to edit expense page when active (optional)

## Files to change
- app.py — Replace placeholder `edit_expense` route with GET/POST implementation; add `@login_required`
- database/queries.py — Add `get_expense_by_id(user_id, expense_id)` function
- templates/profile.html — Add edit link column to transactions table
- base.html — Optionally add "Edit Expense" nav link (mirroring "Add Expense")

## Files to create
- templates/expenses/edit.html — Form for editing an existing expense, pre-filled with current data

## New dependencies
No new dependencies required. Uses existing Flask, Werkzeug, and SQLite dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (already implemented elsewhere)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Form must validate: amount required and positive, category required, date required and valid YYYY-MM-DD
- On successful update, redirect to profile page with success flash message
- Use flash messages for user feedback (both success and error)
- Check that user is logged in (use @login_required decorator)
- Verify expense belongs to the logged-in user before allowing edit (owner check)
- If expense not found or not owned by user, redirect to profile with error
- Pre-populate all form fields with existing expense data on GET
- Use same form layout and styling as the add expense template
- After successful edit, redirect to profile page
- Cancel button should return to profile page without changes
- The edit link in profile table should be accessible and clearly visible

## Definition of done
- [ ] User can click "Edit" on any transaction in the profile page
- [ ] Edit expense page displays with all current values pre-filled
- [ ] Form validates input (amount > 0, valid date, required fields)
- [ ] On successful submission, expense is updated in database
- [ ] User is redirected to profile page after successful edit
- [ ] Updated expense values appear in profile transactions list
- [ ] Cancel button returns to profile page without changes
- [ ] User cannot edit another user's expense (owner check)
- [ ] Appropriate error messages shown for invalid input or missing expense
- [ ] User cannot access edit page when not logged in (redirects to login)
- [ ] Form uses same styling as add expense form
- [ ] Flash success message shown after successful edit
---