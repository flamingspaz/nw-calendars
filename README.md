# nw-calendars

Calendars for Wembley Stadium events and Harrow bin collections, auto-updated daily.

Harrow council offers the ecal service, but it is never updated for any exceptions. This cal will show any updates from the council, and when your bins were collected last week.

## Calendars

| | iCal | JSON |
|---|---|---|
| **Wembley Stadium** | [wembley.ics](https://flamingspaz.github.io/nw-calendars/wembley.ics) | [wembley.json](https://flamingspaz.github.io/nw-calendars/wembley.json) |
| **Harrow Bins** | [bins.ics](https://flamingspaz.github.io/nw-calendars/bins.ics) | [bins.json](https://flamingspaz.github.io/nw-calendars/bins.json) |

Subscribe to an `.ics` URL directly in Google Calendar, Apple Calendar, or Outlook.

> **Note:** The bin calendar is specific to one address in Harrow. To use it for a different property, find your UPRN (Unique Property Reference Number) and update the ID in `bins.py` You can also open an issue and I can add a calendar.

## Home Assistant

Add a REST sensor to `configuration.yaml` for each feed you want:

```yaml
sensor:
  - platform: rest
    name: Next Wembley Event
    resource: https://flamingspaz.github.io/nw-calendars/wembley.json
    value_template: "{{ value_json.next.summary }}"
    json_attributes:
      - next
      - events
    scan_interval: 3600

  - platform: rest
    name: Next Bin Collection
    resource: https://flamingspaz.github.io/nw-calendars/bins.json
    value_template: "{{ value_json.next.summary }}"
    json_attributes:
      - next
      - events
    scan_interval: 3600
```

The sensor state is the next event title. Additional attributes available via `next`:

```yaml
{{ states.sensor.next_wembley_event.attributes.next.start }}      # e.g. "2026-04-12"
{{ states.sensor.next_wembley_event.attributes.next.days_until }} # e.g. 1
{{ states.sensor.next_wembley_event.attributes.next.description }}
```
