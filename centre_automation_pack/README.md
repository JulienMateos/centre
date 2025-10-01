# Centre — Automation

This folder contains the GitHub Actions workflow and Python scripts that update your dashboard every morning at **08:00 Europe/Madrid**.

## What it does
- Fetches **news** from RSS (Reuters/WSJ world, Reuters tech) → `data/news.json`
- Reads **important emails** from your **Gmail mirror** via IMAP → `data/emails.json`
- Pulls **today's calendar** (optional ICS URL) → `data/plan.json`
- Commits the new JSON files so your GitHub Pages (Plash) dashboard refreshes automatically.

## Setup
1. Copy all these files into your repository root (same level as `index.html` and `data/` folder).
2. In your repo → **Settings → Secrets and variables → Actions** → **New repository secret**:
   - `GMAIL_USER` = your mirror Gmail (e.g., `u3853016604@gmail.com`)
   - `GMAIL_APP_PASSWORD` = a Gmail App Password (Google Account → Security → 2FA → App passwords → "Mail (Mac)" works)
   - *(optional)* `IMPORTANCE_WHITELIST` = comma-separated emails you always want marked important
   - *(optional)* `IMPORTANCE_BLACKLIST` = comma-separated emails to de-prioritize
   - *(optional)* `CALENDAR_ICS_URL` = your private iCloud/Google ICS link
3. Commit and push. The workflow runs daily at **06:00 UTC** (08:00 Madrid). You can also run it manually: **Actions → Update Centre Data → Run workflow**.

> Make sure your repo has GitHub Pages enabled (Settings → Pages → deploy from `main` / root).

## Files
- `.github/workflows/update.yml` — cron job + steps
- `requirements.txt` — Python deps
- `update_data.py` — orchestrator
- `news_builder.py` — builds bilingual news
- `emails_builder.py` — IMAP triage (scores %, suggests replies if score ≥ 60)
- `plan_builder.py` — calendar → plan (hard/must/nice/focus)

Timezone: Europe/Madrid (handled in both Python and workflow env).

