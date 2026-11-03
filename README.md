# Keyword Position Tracker — Odoo 19

Track where your Odoo website ranks on Google for every keyword you target, in
one premium, Ahrefs-style dashboard: **position, change, search volume,
difficulty, CPC, traffic, ranking URL and SERP features**, with daily history
and trend graphs. Also **watch competitor domains**, get **email alerts** when a
keyword drops, and surface **quick wins** (keywords ranking in positions 11-20,
just off page 1).

## Install
Copy `cf_keyword_tracker/` into your Odoo add-ons path, then **Apps → Update
Apps List** and install **Keyword Position Tracker**.

> This module has its own database models, so it must be installed from the
> add-ons path. Odoo's **Apps → Upload a Module** (zip import) only loads
> data-only modules — it never loads Python code — so it cannot install this
> app. That is a limitation of the Upload feature, not the module.

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
4. **Keyword Tracker → Quick wins** — keywords ranking in positions 11-20, your
   fastest page-1 opportunities.
5. **Keyword Tracker → Competitors** — add a competitor domain (e.g.
   `competitor.com`); each refresh records where they rank for your keywords and
   how many you are behind on. Needs a SERP provider (DataForSEO or SerpApi);
   Search Console only reports your own site.
6. **Settings → Email alerts** — turn on an email digest sent after the daily
   check whenever a keyword drops by more than your chosen number of positions.

Google blocks scraping, so checks run on a schedule via an official/licensed
API — exactly how professional rank trackers work. No fake data.

Module: [`cf_keyword_tracker/`](cf_keyword_tracker/) · By [Webooz](https://webooz.in/) · License: LGPL-3 · Support: akash00.hit@gmail.com
