# Backlog

## ticket-001 [todo] Search/Filter Catalog
- Add a text input above the catalog grid to filter by title
- Filter should be case-insensitive and match any substring
- Results update as the user types (no submit button needed)

## ticket-002 [todo] Remove from Watchlist
- Add a DELETE /api/watchlist/{id} backend endpoint
- Add a remove button on each watchlist card
- Button should have a confirmation step ("Remove?" → click again to confirm)
- After removal, refresh the watchlist list

## ticket-003 [todo] Loading & Error States
- Show a loading spinner or skeleton cards while data is being fetched
- Show an error message if the API call fails (network down, 500, etc.)
- Disable action buttons during API calls to prevent double-submit
- Add a "Retry" button on error states

## ticket-004 [todo] Sort Watchlist
- Add a sort dropdown above the watchlist grid
- Options: title (A-Z), release year, date added
- Toggle asc/desc direction
- Sorting works with the existing pagination

## ticket-005 [todo] Watchlist Stats Bar
- Show a stats bar above the watchlist grid
- Display: total items, watched count, unwatched count
- Stats update when items are toggled or removed

## ticket-006 [todo] Catalog Already-in-Watchlist Badge
- In the catalog view, if a title is already in the watchlist, show a badge
- Disable the "+ Watchlist" button for items already added
- Fetch the watchlist IDs on catalog load to check membership
