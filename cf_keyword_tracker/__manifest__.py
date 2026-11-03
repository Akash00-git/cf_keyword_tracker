{
    'name': 'Keyword Position Tracker',
    'version': '19.0.1.0.0',
    'summary': 'Track your website keywords\' live Google ranking position, '
               'traffic, volume, difficulty and CPC — with history and trends',
    'description': """
Keyword Position Tracker
========================

Track where your Odoo website ranks on Google for every keyword you target —
in one premium, Ahrefs-style dashboard built natively in Odoo.

- Auto-collects every keyword from your website pages (SEO Coach focus
  keyphrases, related keyphrases and the standard website meta keywords), so
  nothing is missed.
- Shows the exact Google position of the page that targets each keyword, plus
  the change since last check, best position, search volume, difficulty, CPC,
  estimated traffic, the ranking URL and SERP features.
- Keeps daily history so you see the position trend over time on a graph.
- Distribution and visibility: how many keywords are in the Top 3 / Top 10 /
  Top 100, and an overall visibility score.
- Refresh button + automatic refresh of stale keywords when you open the
  dashboard; a daily scheduled check keeps everything current.

Data sources (you choose, configured in Settings)
--------------------------------------------------

Google never gives positions/volume/CPC by scraping (it is blocked and against
their rules), so this module uses official / licensed providers:

- **Google Search Console** (free, official): the exact position, clicks,
  impressions and CTR for your own site's keywords.
- **SERP / keyword data API** (e.g. DataForSEO, SerpApi — paid): position for
  ANY keyword plus search volume, keyword difficulty, CPC and traffic.

Columns automatically show whatever the active provider supplies.
""",
    'category': 'Website/SEO',
    'author': 'Webooz',
    'website': 'https://webooz.in/',
    'support': 'akash00.hit@gmail.com',
    'maintainer': 'Akash',
    'license': 'LGPL-3',
    'depends': ['website'],
    'external_dependencies': {'python': []},
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/keyword_tracker_views.xml',
        'views/res_config_settings_views.xml',
        'views/keyword_tracker_menus.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
}
