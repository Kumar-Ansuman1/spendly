---
# Spec: Date Filter for Profile Page

## Overview
This feature adds a date filter to the profile page, allowing users to view their expenses and summary statistics for a specific date range (e.g., last week, last month, custom range). This enhances the profile page by providing more control over the data displayed, helping users analyze their spending patterns over time.

## Depends on
Steps 1-5 (database setup, registration, login/logout, profile page, profile backend) must be complete because we are building upon the existing profile page and its backend queries.

## Routes
No new routes. We will modify the existing profile route to handle date filter parameters via query strings.

## Database changes
No database changes. The existing expenses table already includes a date column.

## Templates
- **Modify:** templates/profile.html - Add date filter UI (date pickers, preset range buttons) and adjust the display of transactions and category breakdown based on selected date range.

## Files to change
- app.py - Modify profile route to accept date range parameters and pass to query functions
- database/queries.py - Modify get_summary_stats, get_recent_transactions, get_category_breakdown to accept optional date range parameters
- templates/profile.html - Add date filter controls and update template to use filtered data

## Files to create
None

## New dependencies
No new dependencies

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (already implemented)
- Use CSS variables — never hardcode hex values
- All templates extend base.html
- Maintain existing functionality when no date filter is applied (show all data)
- Date format in database is YYYY-MM-DD, use consistent format for queries
- Preserve existing responsive design and accessibility

## Definition of done
- [ ] Profile page loads with default view (no filter) showing all expenses
- [ ] User can select preset date ranges (Last 7 days, Last 30 days, This month, Last month)
- [ ] User can set custom date range via date pickers
- [ ] Summary statistics update based on selected date range
- [ ] Recent transactions list updates based on selected date range
- [ ] Category breakdown chart updates based on selected date range
- [ ] Clearing date filter returns to showing all expenses
- [ ] Invalid date ranges handled gracefully (show error or reset to valid range)
- [ ] URL updates with query parameters when date filter is applied (for shareability)
- [ ] Existing functionality (logout, etc.) remains intact