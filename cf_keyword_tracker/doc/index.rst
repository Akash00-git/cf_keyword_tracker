========================
Keyword Position Tracker
========================

:Version: 19.0.1.1.0 (for Odoo 19, LGPL-3, by Webooz)

Track where your Odoo website ranks on Google for every keyword you target, in
one premium dashboard — position, change, search volume, difficulty, CPC,
traffic, the ranking URL and SERP features, with daily history and trends.

.. tip::

   Install, click **Collect keywords from site**, connect a data source in
   **Settings**, then **Refresh positions**. That is the whole setup.

What you get
============

- **Current position** with the change (up / down) since the last check, plus
  your best-ever position.
- **Search volume, difficulty (KD), CPC** and **estimated traffic** from the
  data provider you connect.
- **Clicks, impressions and CTR** for your own site (Google Search Console).
- The exact **ranking URL** and **SERP features**.
- **Distribution** (Top 3 / Top 10 / Top 100) and a **position trend** graph
  from daily history.
- **Competitor tracking** — add competitor domains and see where they rank for
  each of your keywords, and how many you are behind on.
- **Email alerts** — a digest email after the daily check whenever a keyword
  drops, so you can react fast.
- **Quick wins** — keywords sitting in positions 11-20 (just off page 1): your
  fastest page-1 opportunities.

How positions are fetched
=========================

Google blocks scraping, so — like every professional rank tracker — checks run
on a schedule through an official or licensed API. You pick the source in
**Settings**:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Source
     - Gives you
   * - Google Search Console (free, official)
     - Exact position, clicks, impressions, CTR for your own site's keywords
   * - DataForSEO / SerpApi (paid)
     - Position for any keyword, plus volume, difficulty and CPC

Installation
============

This is a full app (it has its own database models and logic), so you install
it the standard Odoo way: put the module folder in your Odoo **add-ons**
(modules) folder, then install it from **Apps**.

.. warning::

   Do **not** use **Apps -> Import Module** / "Upload a Module" (the zip upload)
   for this app. That screen only loads *data-only* add-ons and cannot install
   an app that contains code — it fails with a "model not found" error. Use one
   of the methods below instead.

Odoo.sh
-------

1. Add the ``cf_keyword_tracker`` folder to your Odoo.sh project's add-ons
   (commit it to your project's GitHub repository, or add this repository as a
   submodule) and push. Odoo.sh rebuilds automatically.
2. Open **Apps -> Update Apps List**, search **Keyword Position Tracker**, and
   click **Install**.

Self-hosted / on-premise
------------------------

1. Get the ``cf_keyword_tracker`` folder (the one that contains
   ``__manifest__.py``) from the Odoo Apps download or from git.
2. Copy that folder into your server's add-ons path. With git::

      git clone -b 19.0 https://github.com/Akash00-git/cf_keyword_tracker.git /tmp/src
      cp -r /tmp/src/cf_keyword_tracker /path/to/your/odoo/addons/cf_keyword_tracker

3. Restart the Odoo service so it sees the new folder.
4. In Odoo open **Apps**, click **Update Apps List**, clear the search filter,
   type **Keyword Position Tracker**, and click **Install**.

Odoo Online (the free odoo.com / SaaS)
--------------------------------------

Odoo Online does not allow third-party apps, so this app cannot run there. Use
Odoo.sh or a self-hosted Odoo.

Troubleshooting
---------------

- **Not in the Apps search.** The folder is not in the add-ons path yet, or you
  have not run **Update Apps List**. Also remove the default **Apps** filter in
  the search box.
- **"Invalid Operation / model not found" after uploading a zip.** You used
  **Import Module**; install from the add-ons path instead (above).

Setup
=====

1. **Collect keywords** — open **Keyword Tracker -> Keywords** and click
   **Collect keywords from site**. Every focus keyphrase (SEO Coach) and website
   meta keyword on your pages, posts and products is added.
2. **Connect a data source** — **Keyword Tracker -> Configuration -> Settings**,
   choose a provider and enter its credentials, set your domain and location.
3. **Refresh** — click **Refresh positions**. Opening the dashboard also
   auto-refreshes keywords that have gone stale, and a daily scheduled job keeps
   the history current.

.. note::

   Uninstall any time from **Apps -> Keyword Position Tracker -> Uninstall**.

Support
=======

Built by **Webooz** — https://webooz.in/ — akash00.hit@gmail.com
