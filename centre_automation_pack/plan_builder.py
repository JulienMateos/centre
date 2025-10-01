#!/usr/bin/env python3
import os, json, datetime as dt
from dateutil import tz
from icalendar import Calendar
import requests

TZ = os.getenv("TIMEZONE", "Europe/Madrid")
CAL_URL = os.getenv("CALENDAR_ICS_URL", "")  # optional: your private ICS link

def load_events_today():
    if not CAL_URL:
        return []

    r = requests.get(CAL_URL, timeout=20)
    r.raise_for_status()
    cal = Calendar.from_ical(r.content)

    today = dt.datetime.now(tz.gettz(TZ)).date()
    out = []
    for comp in cal.walk():
        if comp.name != "VEVENT":
            continue
        start = comp.get("dtstart").dt
        end = comp.get("dtend").dt
        # Normalize to aware datetime
        if isinstance(start, dt.date) and not isinstance(start, dt.datetime):
            # all-day
            s_local = dt.datetime.combine(start, dt.time.min).replace(tzinfo=tz.gettz(TZ))
        else:
            s_local = start.astimezone(tz.gettz(TZ))
        if isinstance(end, dt.date) and not isinstance(end, dt.datetime):
            e_local = dt.datetime.combine(end, dt.time.min).replace(tzinfo=tz.gettz(TZ))
        else:
            e_local = end.astimezone(tz.gettz(TZ))

        if s_local.date() == today:
            out.append((s_local, e_local, str(comp.get("summary"))))
    out.sort(key=lambda x: x[0])
    return out

def main():
    os.makedirs("data", exist_ok=True)
    events = load_events_today()
    hard = [{"time": e[0].strftime("%H:%M"), "text": e[2]} for e in events]

    # Basic focus heuristics
    focus = ["1: Deep work 90’", "2: Ship one important email", "3: 20’ movement"]

    data = {
        "hard": hard,
        "must": ["Top 3 emails", "One deliverable"],
        "nice": ["Read 10 pages"],
        "focus": focus
    }
    with open(os.path.join("data","plan.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Wrote data/plan.json")

if __name__ == "__main__":
    main()
