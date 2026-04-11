#!/usr/bin/env python3

import json
import urllib.request
from datetime import datetime, timedelta, timezone
from icalendar import Calendar, Event
import zoneinfo


def fetch_events():
    with urllib.request.urlopen("https://www.harrow.gov.uk/ajax/bins/summary/010070265940") as url:
        data = json.load(url)

    events = []
    for bin in data["results"]["collections"]["all"]:

        match bin["binType"]:
            case "FOOD":
                binType = "Food Waste"
            case "RESIDUAL":
                binType = "General Waste"
            case "GARDEN":
                binType = "Garden Waste"
            case "RECYCLABLES":
                binType = "Recycling Waste"
            case _:
                binType = bin["binType"]

        time = datetime.fromisoformat(bin["eventTime"]).replace(tzinfo=zoneinfo.ZoneInfo('Europe/London'))

        match bin["eventType"]:
            case "COLLECTED":
                description = "Bins were collected successfully"
                binType = "✅ " + binType
            case "COLLECTION DUE":
                description = """Please put your bins outside of your property before 6:30am on your collection day.

                            ❓Do you need to order more food waste bio bags? You can order more bags online at https://www.harrow.gov.uk/bins-waste-recycling/food-waste-bio-bags

                            Bin, Waste & Recycling
                            https://www.harrow.gov.uk/bins-waste-recycling

                            What goes in which bin?
                            https://www.harrow.gov.uk/binguide"""
                time = time.replace(hour=5, minute=0, second=0, microsecond=0)
            case _:
                binType = "⚠️  " + binType
                description = bin["uiDetails"]["summary"]["messageMain"] + "\\n\\n" + bin["uiDetails"]["details"]["messageMain"]

        events.append({
            "summary": binType,
            "time": time,
            "description": description,
        })

    return events


def build_calendar(events):
    cal = Calendar()
    cal.add("prodid", "-//Pesky Potato//pesky.moe//EN")
    cal.add("version", "2.0")
    cal.add("summary", "Harrow Bin Calendar")
    cal.add("X-WR-CALNAME", "Bins")

    for e in events:
        event = Event()
        event.add('dtstart', e["time"])
        event.add('dtend', e["time"] + timedelta(minutes=5))
        event.add('summary', e["summary"])
        event.add('description', e["description"])
        cal.add_component(event)

    return cal


def write_ha_json(events, path):
    now = datetime.now(tz=zoneinfo.ZoneInfo('Europe/London'))

    def to_entry(e):
        return {
            "summary": e["summary"],
            "start": e["time"].isoformat(),
            "description": e["description"],
        }

    future = [e for e in events if e["time"] >= now]
    next_event = None
    if future:
        n = future[0]
        next_event = {
            "summary": n["summary"],
            "start": n["time"].isoformat(),
            "description": n["description"],
            "days_until": (n["time"].date() - now.date()).days,
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
with open("bins.ics", "wb") as f:
    f.write(cal.to_ical())
print("Written to bins.ics")

write_ha_json(events, "bins.json")
print("Written to bins.json")
