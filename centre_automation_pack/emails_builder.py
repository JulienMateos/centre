#!/usr/bin/env python3
import os, json, imaplib, email, datetime as dt, re

GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
WHITELIST = set([x.strip().lower() for x in os.getenv("IMPORTANCE_WHITELIST","").split(",") if x.strip()])
BLACKLIST = set([x.strip().lower() for x in os.getenv("IMPORTANCE_BLACKLIST","").split(",") if x.strip()])

KEYWORDS_URGENT = [
    r"\burgent\b", r"\basap\b", r"\bdeadline\b", r"\bby\s+eod\b", r"\btoday\b", r"\bimportant\b", r"\baction required\b",
]
KEYWORDS_LOW = [r"\bnewsletter\b", r"\bunsubscribe\b", r"\bdigest\b", r"\boffer\b", r"\bpromo\b"]

def score_email(from_addr, subject):
    score = 50
    f = (from_addr or "").lower()
    s = (subject or "").lower()

    if any(w in f for w in WHITELIST): score += 30
    if any(b in f for b in BLACKLIST): score -= 40

    for kw in KEYWORDS_URGENT:
        if re.search(kw, s): score += 20
    for kw in KEYWORDS_LOW:
        if re.search(kw, s): score -= 15

    score = max(0, min(100, score))
    return score

def extract_from(msg):
    hdr = msg.get("From", "")
    # very rough extract
    m = re.search(r'("?([^"]+)"?\s)?<([^>]+)>', hdr)
    if m:
        name = (m.group(2) or "").strip()
        addr = (m.group(3) or "").strip()
        return (name or addr), addr
    return hdr, hdr

def fetch_recent_imap(limit=50):
    items = []
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("Missing GMAIL_USER or GMAIL_APP_PASSWORD env vars")
        return items

    M = imaplib.IMAP4_SSL("imap.gmail.com")
    M.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    M.select("INBOX")

    # Search last 3 days
    date = (dt.datetime.utcnow() - dt.timedelta(days=3)).strftime("%d-%b-%Y")
    typ, data = M.search(None, '(SINCE "{}")'.format(date))
    if typ != "OK":
        M.logout()
        return items

    ids = data[0].split()
    ids = ids[-limit:][::-1]  # most recent first

    for i in ids:
        typ, msg_data = M.fetch(i, '(RFC822)')
        if typ != "OK": continue
        msg = email.message_from_bytes(msg_data[0][1])

        subj = msg.get("Subject", "")
        name, addr = extract_from(msg)
        s = score_email(addr, subj)

        items.append({
            "score": int(s),
            "from": name,
            "subject": subj,
            "suggest": s >= 60
        })
    M.close()
    M.logout()
    return items

def main():
    os.makedirs("data", exist_ok=True)
    items = fetch_recent_imap(80)
    # Keep top 8 by score
    items = sorted(items, key=lambda x: x["score"], reverse=True)[:8]
    out = {"items": items}
    with open(os.path.join("data","emails.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("Wrote data/emails.json with", len(items), "items")

if __name__ == "__main__":
    main()
