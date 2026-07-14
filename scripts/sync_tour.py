#!/usr/bin/env python3
"""Sync the Tour section from Bandsintown + tour_extras.json.
Rewrites the block between <!-- TOUR LIST START --> and <!-- TOUR LIST END -->."""
import json, re, urllib.request, datetime, html as h, pathlib, sys

APP_ID = "6c96175f419d9630331d545ae437d211"
API = f"https://rest.bandsintown.com/artists/The%20Martin%20Boys/events?app_id={APP_ID}"
ROOT = pathlib.Path(__file__).resolve().parent.parent

def fetch():
    req = urllib.request.Request(API, headers={"User-Agent": "whoisdanbeattie-site-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def load_extras():
    p = ROOT / "tour_extras.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return []

def norm(events):
    out = []
    for e in events:
        dt = e["datetime"][:10]
        venue = e.get("title") or e["venue"]["name"]
        loc = f'{e["venue"]["city"]}, {e["venue"].get("region") or e["venue"]["country"]}'
        tickets = ""
        for o in e.get("offers", []):
            if o.get("type") == "Tickets" and o.get("url"):
                tickets = o["url"]; break
        out.append({"date": dt, "venue": venue, "location": loc, "tickets": tickets})
    return out

def fmt_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f'{d.strftime("%b")}. {d.day}, {d.year}'

def render(items):
    rows = []
    for it in items:
        t = (f'\n    <a href="{h.escape(it["tickets"])}" class="tour-tickets" target="_blank" rel="noopener">Tickets</a>'
             if it["tickets"] else "\n    ")
        rows.append(f'''  <div class="tour-item" data-date="{it["date"]}">
    <div><div class="tour-date">{fmt_date(it["date"])}</div></div>
    <div>
      <div class="tour-venue">{h.escape(it["venue"].upper())}</div>
      <div class="tour-location">{h.escape(it["location"].upper())}</div>
    </div>{t}
  </div>''')
    return "<!-- TOUR LIST START -->\n" + "\n".join(rows) + "\n<!-- TOUR LIST END -->"

def main():
    events = norm(fetch()) + load_extras()
    # de-dupe by date+venue, keep only today-or-future, sort
    today = datetime.date.today().isoformat()
    seen, items = set(), []
    for it in sorted(events, key=lambda x: x["date"]):
        key = (it["date"], it["venue"].lower())
        if key in seen or it["date"] < today: continue
        seen.add(key); items.append(it)
    if not items:
        print("No events returned; refusing to write an empty tour list."); sys.exit(0)
    block = render(items)
    changed = False
    for fname in ("docs/index.html", "index.html"):
        p = ROOT / fname
        src = p.read_text(encoding="utf-8")
        new = re.sub(r"<!-- TOUR LIST START -->.*?<!-- TOUR LIST END -->", block, src, flags=re.S)
        if new != src:
            p.write_text(new, encoding="utf-8"); changed = True
    print(f"{len(items)} events; changed: {changed}")

if __name__ == "__main__":
    main()
