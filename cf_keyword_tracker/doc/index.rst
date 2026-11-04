========================
Keyword Position Tracker
========================

:Version: 19.0.1.2.0 (for Odoo 19, LGPL-3, by Webooz)

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

1. **Add keywords** — in **Keyword Tracker**, use **Collect from website**
   (reads your pages' focus keyphrases and website meta keywords) and/or, if
   your provider is Google Search Console, **Import from Search Console** (adds
   every query your site already ranks for, with its position). You can also add
   keywords by hand with **New**.
2. **Connect a data source** — **Keyword Tracker -> Configuration -> Settings**,
   choose a provider and enter its credentials, set your domain and location.
3. **Refresh** — click **Refresh positions**. Opening the dashboard also
   auto-refreshes keywords that have gone stale, and a daily scheduled job keeps
   the history current.

Connecting Google Search Console (step by step)
===============================================

Google Search Console is the free data source. To connect it you need four
values: the **Property**, the **OAuth client ID**, the **OAuth client secret**
and the **OAuth refresh token**. You create them once (about 10-15 minutes)
across three Google websites. Use the **same Google account** throughout — the
one that owns your site in Search Console.

Before you start
----------------

Your website must already be verified in Google Search Console
(https://search.google.com/search-console). Open it and note the exact property
shown at the top-left — for example ``https://www.example.com/`` (a URL-prefix
property) or ``sc-domain:example.com`` (a domain property). That exact text is
your **Property** value (used in step 21).

Step 1 — Create a Google Cloud project and enable the API
---------------------------------------------------------

1. Open https://console.cloud.google.com/ and sign in.
2. In the top bar open the project dropdown -> **New project** -> give it a name
   (e.g. *SEO Keyword Tracker*) -> **Create**, then select that project.
3. In the top search bar type **Google Search Console API**, open it, and click
   **Enable**.

Step 2 — Set up the OAuth consent screen
----------------------------------------

4. Left menu -> **APIs & Services -> OAuth consent screen** (this opens the
   *Google Auth Platform*).
5. Click **Get started** and fill: **App name** (any name), **User support
   email** (your email), **Audience** = **External**, **Contact email** (your
   email). Agree and click **Create**.
6. Open the **Branding** page and fill:

   - **Application home page**: your site, e.g. ``https://www.example.com/``
   - **Application privacy policy link**: your privacy page, e.g.
     ``https://www.example.com/privacy-policy``
   - If a message says **Authorised domains: Missing domain**, click
     **Add domain**, enter your bare domain (``example.com`` — no https, no
     www), and **Save**.
   - Do **not** upload an app logo (it forces app verification).

7. Open the **Audience** page and click **Publish app** -> **Confirm** so the
   status becomes **In production**. (If you leave it in *Testing*, Google
   expires the refresh token after 7 days.)

Step 3 — Create the OAuth client (Client ID + Client secret)
------------------------------------------------------------

8. Left menu -> **Clients** -> **Create OAuth client** (older layout:
   *Credentials -> Create credentials -> OAuth client ID*).
9. **Application type** = **Web application**; give it a name (e.g.
   *Odoo Keyword Tracker*).
10. Under **Authorised redirect URIs** click **Add URI** and paste exactly
    ``https://developers.google.com/oauthplayground``.
11. Click **Create**. A box shows your **Client ID** and **Client secret** —
    copy both. (Two of your four values.)

Step 4 — Get the refresh token (OAuth Playground)
-------------------------------------------------

12. Open https://developers.google.com/oauthplayground/ (keep the trailing
    slash).
13. Click the **gear** icon (top-right) -> tick **Use your own OAuth
    credentials** -> paste your **Client ID** and **Client secret** -> **Close**.
14. On the left, in the **Input your own scopes** box, paste exactly
    ``https://www.googleapis.com/auth/webmasters.readonly`` and click
    **Authorize APIs**.
15. Sign in with the Google account that owns your Search Console property.
16. If you see **"Google hasn't verified this app"**, click **Advanced** ->
    **Go to <your app name> (unsafe)** -> **Allow**. This is normal for your own
    private app.
17. Back in the Playground, under **Step 2** click **Exchange authorization code
    for tokens**.
18. Copy the **Refresh token** shown (a long value starting with ``1//``).

Step 5 — Enter the values in Odoo
---------------------------------

19. In Odoo go to **Keyword Tracker -> Configuration -> Settings**.
20. **Provider** = *Google Search Console*.
21. **Property** = your exact Search Console property (e.g.
    ``https://www.example.com/`` or ``sc-domain:example.com``).
22. **OAuth client ID** = from step 11.
23. **OAuth client secret** = from step 11.
24. **OAuth refresh token** = from step 18.
25. Click **Save**, then **Keyword Tracker -> Import from Search Console**. Your
    ranking keywords appear with position, clicks, impressions and CTR.

Tips and troubleshooting
------------------------

- The **Property** must match Search Console exactly (keep ``https://`` and the
  trailing ``/`` for a URL-prefix property).
- The **Client ID and secret in Odoo must be the same ones** used in the OAuth
  Playground, or the refresh token will not work.
- **Publish the app** (step 7), or Google revokes the refresh token after 7 days
  and tracking stops.
- The **refresh token** and **client secret** are passwords to your Search
  Console data — keep them private. If they ever leak, delete the OAuth client
  in Google Cloud and create a new one.
- Search Console's **position is a 28-day average** over searches where your
  site was actually shown — not a live, everyone-sees-it rank. Check the
  **Impressions** column to judge how solid a position is. For true live,
  de-personalised rankings and competitor positions, use a paid provider
  (DataForSEO or SerpApi).

.. note::

   Uninstall any time from **Apps -> Keyword Position Tracker -> Uninstall**.

Support
=======

Built by **Webooz** — https://webooz.in/ — akash00.hit@gmail.com
