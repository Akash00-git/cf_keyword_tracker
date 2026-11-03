# Part of Keyword Position Tracker. Copyright (C) 2026 Webooz
# <akash00.hit@gmail.com>. See LICENSE for details.
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Models that carry website SEO metadata (and so may hold keywords).
_KEYWORD_SOURCE_MODELS = (
    'website.page', 'blog.post', 'product.template', 'event.event',
)


class CfKeywordTag(models.Model):
    _name = 'cf.keyword.tag'
    _description = 'Keyword Tag'

    name = fields.Char(required=True)
    color = fields.Integer(string='Color')


class CfKeywordTracker(models.Model):
    _name = 'cf.keyword.tracker'
    _description = 'Tracked Keyword'
    _order = 'position_sortable asc, name asc'
    _rec_name = 'name'

    name = fields.Char(string='Keyword', required=True, index=True)
    active = fields.Boolean(default=True)
    website_id = fields.Many2one('website', string='Website', ondelete='cascade')
    page_url = fields.Char(
        string='Target page',
        help="The page on your site that targets this keyword.")
    source = fields.Selection(
        [('seo_coach', 'SEO Coach keyphrase'),
         ('related', 'Related keyphrase'),
         ('meta', 'Website meta keywords'),
         ('manual', 'Added manually')],
        string='Source', default='manual')
    tag_ids = fields.Many2many('cf.keyword.tag', string='Tags')

    # ── Current snapshot (latest check) ─────────────────────────────────
    position = fields.Float(
        string='Position', digits=(16, 1),
        help="Latest Google ranking position (lower is better). "
             "0 / empty means not in the tracked results.")
    position_sortable = fields.Float(
        string='Position (sort)', compute='_compute_position_sortable',
        store=True, help="Position with non-ranking pushed to the bottom.")
    previous_position = fields.Float(string='Previous position', digits=(16, 1))
    position_change = fields.Float(
        string='Change', digits=(16, 1), compute='_compute_position_change',
        store=True, help="Positions gained (+) or lost (-) since last check.")
    best_position = fields.Float(string='Best position', digits=(16, 1))
    ranking_url = fields.Char(
        string='Ranking URL', help="The exact URL Google ranks for this keyword.")

    # ── Metrics (filled by the active data provider) ────────────────────
    search_volume = fields.Integer(string='Volume')
    difficulty = fields.Integer(string='KD', help="Keyword difficulty, 0-100.")
    cpc = fields.Float(string='CPC', digits=(16, 2))
    traffic = fields.Integer(string='Traffic', help="Estimated monthly traffic.")
    clicks = fields.Integer(string='Clicks')
    impressions = fields.Integer(string='Impressions')
    ctr = fields.Float(string='CTR', digits=(16, 2))
    serp_features = fields.Char(string='SERP features')

    status = fields.Selection(
        [('new', 'Not checked yet'),
         ('tracked', 'Ranking'),
         ('not_ranking', 'Not ranking'),
         ('error', 'Check failed')],
        string='Status', default='new', index=True)
    last_checked = fields.Datetime(string='Last checked')
    bucket = fields.Selection(
        [('top3', 'Top 3'), ('top10', 'Top 10'), ('top100', 'Top 100'),
         ('beyond', 'Beyond 100')],
        string='Bucket', compute='_compute_bucket', store=True)

    history_ids = fields.One2many(
        'cf.keyword.history', 'keyword_id', string='History')

    _sql_constraints = [
        ('name_website_uniq', 'unique(name, website_id)',
         'This keyword is already tracked for this website.'),
    ]

    # ── Computes ────────────────────────────────────────────────────────
    @api.depends('position')
    def _compute_position_sortable(self):
        for kw in self:
            kw.position_sortable = kw.position if kw.position and kw.position > 0 else 9999.0

    @api.depends('position', 'previous_position')
    def _compute_position_change(self):
        for kw in self:
            if kw.position and kw.previous_position:
                # a lower position number is better, so "gain" = previous - now
                kw.position_change = kw.previous_position - kw.position
            else:
                kw.position_change = 0.0

    @api.depends('position')
    def _compute_bucket(self):
        for kw in self:
            p = kw.position
            if not p or p <= 0:
                kw.bucket = 'beyond'
            elif p <= 3:
                kw.bucket = 'top3'
            elif p <= 10:
                kw.bucket = 'top10'
            elif p <= 100:
                kw.bucket = 'top100'
            else:
                kw.bucket = 'beyond'

    # ── Keyword collection from the website ─────────────────────────────
    @api.model
    def _cf_website_url(self, rec):
        """Best-effort public URL for a source record."""
        for attr in ('website_url', 'url'):
            if attr in rec._fields:
                val = rec[attr]
                if val:
                    return val
        return ''

    @api.model
    def cf_collect_keywords(self):
        """Scan the website's pages and create a tracked keyword for every
        focus keyphrase, related keyphrase and meta keyword found. Idempotent:
        existing keywords are kept, only new ones are added."""
        website = self.env['website'].get_current_website() or \
            self.env['website'].search([], limit=1)
        existing = set(self.with_context(active_test=False).search(
            [('website_id', '=', website.id)]).mapped('name'))
        created = self.browse()
        for model_name in _KEYWORD_SOURCE_MODELS:
            if model_name not in self.env:
                continue
            Model = self.env[model_name]
            domain = []
            if 'website_published' in Model._fields:
                domain = [('website_published', '=', True)]
            for rec in Model.sudo().search(domain, limit=5000):
                url = self._cf_website_url(rec)
                found = []  # (keyword, source)
                if rec._fields.get('cf_seo_keyphrase') and rec.cf_seo_keyphrase:
                    found.append((rec.cf_seo_keyphrase, 'seo_coach'))
                if rec._fields.get('cf_seo_related_keyphrases') and rec.cf_seo_related_keyphrases:
                    for kw in rec.cf_seo_related_keyphrases.split(','):
                        found.append((kw, 'related'))
                if rec._fields.get('website_meta_keywords') and rec.website_meta_keywords:
                    for kw in rec.website_meta_keywords.split(','):
                        found.append((kw, 'meta'))
                for raw, src in found:
                    kw = (raw or '').strip()
                    if not kw or kw.lower() in {e.lower() for e in existing}:
                        continue
                    existing.add(kw)
                    created |= self.create({
                        'name': kw, 'website_id': website.id,
                        'page_url': url, 'source': src, 'status': 'new',
                    })
        return created

    def action_collect_keywords(self):
        created = self.cf_collect_keywords()
        return {
            'type': 'ir.actions.client', 'tag': 'display_notification',
            'params': {
                'title': 'Keywords collected',
                'message': '%d new keyword(s) added from your website pages.'
                           % len(created),
                'type': 'success', 'sticky': False,
            },
        }

    # ── Refresh (fetch live positions from the active provider) ─────────
    def _cf_refresh(self):
        """Fetch live metrics for these keywords from the active provider and
        store a daily history point."""
        if not self:
            return
        from .tracker_provider import fetch_keyword_metrics
        results = fetch_keyword_metrics(self.env, self)
        today = fields.Date.context_today(self)
        History = self.env['cf.keyword.history'].sudo()
        for kw in self:
            data = results.get(kw.id) or {}
            vals = {'last_checked': fields.Datetime.now()}
            pos = data.get('position')
            if pos is not None and pos > 0:
                if kw.position and kw.position > 0:
                    vals['previous_position'] = kw.position
                vals['position'] = pos
                vals['ranking_url'] = data.get('url') or kw.ranking_url
                vals['best_position'] = pos if not (kw.best_position and kw.best_position > 0) \
                    else min(kw.best_position, pos)
                vals['status'] = 'tracked'
            elif data.get('error'):
                vals['status'] = 'error'
            else:
                vals['status'] = 'not_ranking'
            for metric in ('search_volume', 'difficulty', 'cpc', 'traffic',
                           'clicks', 'impressions', 'ctr', 'serp_features'):
                if data.get(metric) is not None:
                    vals[metric] = data[metric]
            kw.write(vals)
            if pos is not None and pos > 0:
                point = History.search(
                    [('keyword_id', '=', kw.id), ('date', '=', today)], limit=1)
                point_vals = {
                    'position': pos, 'ranking_url': vals.get('ranking_url'),
                    'clicks': data.get('clicks') or 0,
                    'impressions': data.get('impressions') or 0,
                    'traffic': data.get('traffic') or 0,
                }
                if point:
                    point.write(point_vals)
                else:
                    History.create(dict(point_vals, keyword_id=kw.id, date=today))

    def action_refresh(self):
        """Refresh the selected keywords now (manual Refresh button)."""
        (self or self.search([]))._cf_refresh()
        return {
            'type': 'ir.actions.client', 'tag': 'reload',
        }

    @api.model
    def _cf_cron_refresh_all(self):
        """Daily scheduled refresh of every tracked keyword."""
        self.search([])._cf_refresh()

    @api.model
    def action_open_dashboard(self):
        """Menu entry: refresh keywords that are stale (older than the
        configured threshold) so opening the dashboard shows fresh data,
        then open the list. Refreshing only stale rows avoids hammering the
        provider on every open."""
        get_param = self.env['ir.config_parameter'].sudo().get_param
        try:
            minutes = int(get_param('cf_keyword_tracker.auto_refresh_minutes', '60'))
        except (TypeError, ValueError):
            minutes = 60
        if minutes > 0:
            from datetime import timedelta
            cutoff = fields.Datetime.now() - timedelta(minutes=minutes)
            stale = self.search(['|', ('last_checked', '=', False),
                                 ('last_checked', '<', cutoff)])
            if stale:
                stale._cf_refresh()
        return self.env['ir.actions.actions']._for_xml_id(
            'cf_keyword_tracker.action_cf_keyword_tracker')


class CfKeywordHistory(models.Model):
    _name = 'cf.keyword.history'
    _description = 'Keyword Position History'
    _order = 'date desc'

    keyword_id = fields.Many2one(
        'cf.keyword.tracker', string='Tracked keyword', required=True,
        ondelete='cascade', index=True)
    name = fields.Char(related='keyword_id.name', store=True, string='Keyword')
    date = fields.Date(string='Date', required=True, index=True)
    position = fields.Float(string='Position', digits=(16, 1))
    ranking_url = fields.Char(string='Ranking URL')
    clicks = fields.Integer(string='Clicks')
    impressions = fields.Integer(string='Impressions')
    traffic = fields.Integer(string='Traffic')

    _sql_constraints = [
        ('keyword_date_uniq', 'unique(keyword_id, date)',
         'One history point per keyword per day.'),
    ]
