#!/usr/bin/env python3

import hashlib
import json
import urllib.request
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
from icalendar import Calendar, Event


def fetch_events():
    req = urllib.request.Request(
        "https://www.wembleystadium.com/events",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req) as resp:
        soup = BeautifulSoup(resp.read(), "html.parser")

    events = []
    for item in soup.select(".fa-filter-content__item"):
        spans = item.select("span.small-text")
        h2 = item.find("h2")
        p = item.find("p")

        if not h2 or not spans:
            continue

        raw_date = spans[0].get_text(strip=True)
        raw_time = spans[1].get_text(strip=True) if len(spans) > 1 else ""
        title = h2.get_text(" ", strip=True)
        desc = p.get_text(" ", strip=True) if p else ""

        if not raw_date or raw_date == "TBC":
            continue

        try:
            event_date = datetime.strptime(raw_date, "%d %b %Y").date()
        except ValueError:
            continue

        has_time = raw_time and raw_time != "TBC"
        summary = f"{raw_time} {title}" if has_time else title

        events.append({"date": event_date, "summary": summary, "description": desc})

    return events


def build_calendar(events):
    cal = Calendar()
    cal.add("prodid", "-//Pesky Potato//pesky.moe//EN")
    cal.add("version", "2.0")
    cal.add("X-WR-CALNAME", "Wembley Stadium")

    for e in events:
        uid_base = f"{e['date'].isoformat()}-{e['summary']}@flamingspaz.github.io"
        uid = hashlib.sha1(uid_base.encode()).hexdigest() + "@flamingspaz.github.io"
        event = Event()
        event.add("uid", uid)
        event.add("dtstart", e["date"])
        event.add("dtend", e["date"] + timedelta(days=1))
        event.add("summary", e["summary"])
        if e["description"]:
            event.add("description", e["description"])
        cal.add_component(event)

    return cal


def write_ha_json(events, path):
    today = date.today()

    def to_entry(e):
        return {
            "summary": e["summary"],
            "start": e["date"].isoformat(),
            "description": e["description"],
        }

    future = [e for e in events if e["date"] >= today]
    next_event = None
    if future:
        n = future[0]
        next_event = {
            "summary": n["summary"],
            "start": n["date"].isoformat(),
            "description": n["description"],
            "days_until": (n["date"] - today).days,
        }

    payload = {
        "next": next_event,
        "events": [to_entry(e) for e in events],
    }

    with open(path, "w") as f:
        json.dump(payload, f, indent=2)


events = fetch_events()
print(f"Fetched {len(events)} events")
for e in events:
    print(e)

cal = build_calendar(events)
with open("wembley.ics", "wb") as f:
    f.write(cal.to_ical())
print("Written to wembley.ics")

write_ha_json(events, "wembley.json")
print("Written to wembley.json")
