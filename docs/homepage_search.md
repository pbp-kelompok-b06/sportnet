Homepage search and filter

This document explains how to use the search bar and filters added to the homepage.

GET parameters
- q: free-text search that matches event name, description or location (case-insensitive)
- category: filter by sports category (one of Event.SPORTS_CATEGORY_CHOICES values)
- free: set to `1` to show only free events (fee is 0 or null)

Example URLs
- All events: / (default)
- Search for running events in Jakarta: /?q=jakarta&category=running
- Show only free yoga events: /?category=yoga&free=1

Notes for developers
- The form uses method=GET so the parameters appear in the URL and can be bookmarked or shared.
- The view `Homepage.views.show_main` reads the parameters and filters the Event queryset accordingly.
- The template populates the category select using `Event.SPORTS_CATEGORY_CHOICES` and shows the current selection using `filter_category`, `filter_q` and `filter_free` in the context.

If you want to add more filters (date ranges, price ranges, sorting), update the template to include the necessary inputs and adapt `show_main` to apply the filters on the queryset.
