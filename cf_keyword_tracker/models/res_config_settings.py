# Part of Keyword Position Tracker. Copyright (C) 2026 Webooz
# <akash00.hit@gmail.com>. See LICENSE for details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cf_kt_provider = fields.Selection(
        [('none', 'Not configured'),
         ('gsc', 'Google Search Console (free, official)'),
         ('dataforseo', 'DataForSEO (paid — position, volume, KD, CPC)'),
         ('serpapi', 'SerpApi (paid — position)')],
        string='Rank data provider', default='none',
        config_parameter='cf_keyword_tracker.provider')
    cf_kt_target_domain = fields.Char(
        string='Your domain',
        help="The site whose rankings to track, e.g. www.example.com. "
             "Leave empty to use the website's own domain.",
        config_parameter='cf_keyword_tracker.target_domain')
    cf_kt_location = fields.Char(
        string='Location', default='United States',
        help="Search location, e.g. 'United Arab Emirates'.",
        config_parameter='cf_keyword_tracker.location')
    cf_kt_language = fields.Char(
        string='Language code', default='en',
        config_parameter='cf_keyword_tracker.language')
    cf_kt_auto_refresh_minutes = fields.Integer(
        string='Auto-refresh if older than (minutes)', default=60,
        help="When the dashboard is opened, keywords not checked within this "
             "many minutes are refreshed. Set 0 to disable auto-refresh on open.",
        config_parameter='cf_keyword_tracker.auto_refresh_minutes')

    # Google Search Console (OAuth)
    cf_kt_gsc_site = fields.Char(
        string='Search Console property',
        help="e.g. https://www.example.com/ or sc-domain:example.com",
        config_parameter='cf_keyword_tracker.gsc_site')
    cf_kt_gsc_client_id = fields.Char(
        config_parameter='cf_keyword_tracker.gsc_client_id')
    cf_kt_gsc_client_secret = fields.Char(
        config_parameter='cf_keyword_tracker.gsc_client_secret')
    cf_kt_gsc_refresh_token = fields.Char(
        config_parameter='cf_keyword_tracker.gsc_refresh_token')

    # DataForSEO
    cf_kt_dfs_login = fields.Char(
        string='DataForSEO login',
        config_parameter='cf_keyword_tracker.dfs_login')
    cf_kt_dfs_password = fields.Char(
        string='DataForSEO password',
        config_parameter='cf_keyword_tracker.dfs_password')

    # SerpApi
    cf_kt_serpapi_key = fields.Char(
        string='SerpApi key',
        config_parameter='cf_keyword_tracker.serpapi_key')
