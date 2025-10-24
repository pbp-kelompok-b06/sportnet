from django.utils.translation import gettext as _

# Event Join Notifications
EVENT_JOIN_TITLE = _("Event Joined Successfully")
EVENT_JOIN_MESSAGE = _("You have joined the event {event_name}!")

# Event Cancellation Notifications
EVENT_CANCELLED_TITLE = _("Event Cancelled")
EVENT_CANCELLED_MESSAGE = _("Event {event_name} has been cancelled by the organizer. We apologize for the inconvenience.")

# H-1 Reminder Notifications
EVENT_REMINDER_TITLE = _("Event Reminder: {event_name} Tomorrow")
EVENT_REMINDER_MESSAGE = _("Event {event_name} will be happening tomorrow at {event_time}")

# Read Status Messages
MARK_AS_READ_SUCCESS = _("Notification marked as read")
MARK_ALL_READ_SUCCESS = _("All notifications marked as read")

# Error Messages
ERROR_NO_PARTICIPANT_PROFILE = _("You do not have a participant profile")
ERROR_FORBIDDEN = _("You do not have permission to perform this action")
ERROR_EVENT_NOT_FOUND = _("Event not found")