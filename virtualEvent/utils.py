from icalendar import Calendar, Event
from datetime import timedelta


def generate_ics(event):
    cal = Calendar()
    cal.add("prodid", "-//EventPulse//Event Calendar//EN")
    cal.add("version", "2.0")

    ics_event = Event()
    ics_event.add("summary", event.title)
    ics_event.add("description", event.description)
    ics_event.add("dtstart", event.start_datetime)
    ics_event.add(
        "dtend", event.start_datetime + timedelta(minutes=event.duration_minutes)
    )
    ics_event.add("dtstamp", event.created_at)
    ics_event.add("uid", f"event-{event.id}@eventpulse.com")
    ics_event.add("status", "CONFIRMED")
    ics_event.add("location", "Virtual Event")

    cal.add_component(ics_event)
    return cal.to_ical().decode("utf-8")
