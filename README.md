# Keyword Position Tracker — Odoo 19

Track where your Odoo website ranks on Google for every keyword you target, in
one premium, Ahrefs-style dashboard: **position, change, search volume,
difficulty, CPC, traffic, ranking URL and SERP features**, with daily history
and trend graphs.

## Install
Copy `cf_keyword_tracker/` into your Odoo add-ons path (or **Apps → Upload** the
zip), then **Apps → Update Apps List** and install **Keyword Position Tracker**.

## Use
1. **Keyword Tracker → Keywords → Collect keywords from site** — pulls every
   focus keyphrase (SEO Coach) and website meta keyword from your pages.
2. **Keyword Tracker → Configuration → Settings** — choose a data source and
   enter credentials:
   - **Google Search Console** (free, official) → exact position, clicks,
     impressions, CTR for your own site's keywords.
   - **DataForSEO / SerpApi** (paid) → position for any keyword plus volume,
     difficulty and CPC.
3. **Refresh positions** — fetches the latest ranking. Opening the dashboard
   auto-refreshes stale keywords, and a daily cron keeps history current.

Google blocks scraping, so checks run on a schedule via an official/licensed
API — exactly how professional rank trackers work. No fake data.

Module: [`cf_keyword_tracker/`](cf_keyword_tracker/) · By [Webooz](https://webooz.in/) · License: LGPL-3 · Support: akash00.hit@gmail.com
