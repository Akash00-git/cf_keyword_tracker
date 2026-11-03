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
    striking_distance = fields.Boolean(
        string='Striking distance', compute='_compute_striking_distance',
        store=True,
        help="Ranks just off page 1 (positions 11-20): small on-page "
             "improvements can push it onto page 1 — a quick win.")
    competitor_rank_ids = fields.One2many(
        'cf.keyword.competitor.rank', 'keyword_id',
        string='Competitor positions')

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

    @api.depends('position')
    def _compute_striking_distance(self):
        for kw in self:
            p = kw.position
            kw.striking_distance = bool(p and 10 < p <= 20)

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
        from .tracker_provider import fetch_keyword_metrics, _domain_host
        results = fetch_keyword_metrics(self.env, self)
        today = fields.Date.context_today(self)
        History = self.env['cf.keyword.history'].sudo()
        competitors = self.env['cf.keyword.competitor'].sudo().search(
            [('active', '=', True)])
        Rank = self.env['cf.keyword.competitor.rank'].sudo()
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
            serp = data.get('serp')
            if competitors and serp is not None:
                serp_map = {}
                for r in serp:
                    dom = (r.get('domain') or '').lower()
                    if dom.startswith('www.'):
                        dom = dom[4:]
                    if dom and dom not in serp_map:
                        serp_map[dom] = r
                for comp in competitors:
                    hit = serp_map.get(_domain_host(comp.name))
                    existing = Rank.search(
                        [('keyword_id', '=', kw.id),
                         ('competitor_id', '=', comp.id)], limit=1)
                    if hit:
                        rvals = {'position': float(hit['position']),
                                 'url': hit.get('url'), 'date': today}
                        if existing:
                            existing.write(rvals)
                        else:
                            Rank.create(dict(rvals, keyword_id=kw.id,
                                             competitor_id=comp.id))
                    elif existing:
                        existing.write({'position': 0.0, 'date': today})

    def action_refresh(self):
        """Refresh the selected keywords now (manual Refresh button)."""
        (self or self.search([]))._cf_refresh()
        return {
            'type': 'ir.actions.client', 'tag': 'reload',
        }

    @api.model
    def _cf_cron_refresh_all(self):
        """Daily scheduled refresh of every tracked keyword, then email a
        digest if any keyword lost significant ground."""
        kws = self.search([])
        if not kws:
            return
        kws._cf_refresh()
        self._cf_send_alerts(kws)

    @api.model
    def _cf_send_alerts(self, keywords):
        """Email a digest of keywords that dropped since the previous check."""
        ICP = self.env['ir.config_parameter'].sudo()
        if ICP.get_param('cf_keyword_tracker.alert_enabled') not in ('True', '1', True):
            return
        recipients = (ICP.get_param('cf_keyword_tracker.alert_email') or '').strip()
        if not recipients:
            return
        try:
            threshold = int(ICP.get_param('cf_keyword_tracker.alert_drop_threshold') or 3)
        except (TypeError, ValueError):
            threshold = 3
        alerts = []
        for kw in keywords:
            prev, now = kw.previous_position, kw.position
            if not (prev and prev > 0 and now and now > 0):
                continue
            lost = now - prev
            reasons = []
            if lost >= threshold:
                reasons.append("dropped %d position(s): #%d \u2192 #%d"
                               % (round(lost), round(prev), round(now)))
            if prev <= 10 and now > 10:
                reasons.append("fell off page 1")
            if not reasons:
                continue
            ahead = kw.competitor_rank_ids.filtered(
                lambda r: r.position and 0 < r.position < now)
            alerts.append((kw, reasons, ahead))
        if not alerts:
            return
        rows = ''
        for kw, reasons, ahead in alerts:
            comp = ', '.join('%s (#%d)' % (c.competitor_id.name, round(c.position))
                             for c in ahead) or '\u2014'
            rows += ('<tr><td style="padding:4px 8px">%s</td>'
                     '<td style="padding:4px 8px">%s</td>'
                     '<td style="padding:4px 8px">%s</td></tr>'
                     % (kw.name, '; '.join(reasons), comp))
        body = ('<p>These tracked keywords lost ground in the latest check:</p>'
                '<table style="border-collapse:collapse;border:1px solid #ddd">'
                '<tr style="background:#f5f5f5">'
                '<th style="padding:4px 8px;text-align:left">Keyword</th>'
                '<th style="padding:4px 8px;text-align:left">What changed</th>'
                '<th style="padding:4px 8px;text-align:left">Competitors ahead</th>'
                '</tr>%s</table>'
                '<p style="color:#888">Sent by Keyword Position Tracker.</p>' % rows)
        self.env['mail.mail'].sudo().create({
            'subject': 'Keyword Tracker: %d keyword(s) dropped' % len(alerts),
            'body_html': body,
            'email_to': recipients,
            'auto_delete': True,
        }).send(raise_exception=False)

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


class CfKeywordCompetitor(models.Model):
    _name = 'cf.keyword.competitor'
    _description = 'Tracked Competitor'
    _order = 'name'

    name = fields.Char(
        string='Competitor domain', required=True,
        help="e.g. competitor.com — matched against the Google results for "
             "each of your tracked keywords.")
    active = fields.Boolean(default=True)
    website_id = fields.Many2one('website', string='Website', ondelete='cascade')
    rank_ids = fields.One2many(
        'cf.keyword.competitor.rank', 'competitor_id', string='Positions')
    keywords_tracked = fields.Integer(
        string='Keywords ranking', compute='_compute_stats',
        help="How many of your tracked keywords this competitor ranks for.")
    avg_position = fields.Float(
        string='Avg position', digits=(16, 1), compute='_compute_stats')
    keywords_ahead = fields.Integer(
        string='Keywords ahead of you', compute='_compute_stats',
        help="Keywords where this competitor ranks better than your site.")

    _sql_constraints = [
        ('name_website_uniq', 'unique(name, website_id)',
         'This competitor is already tracked for this website.'),
    ]

    @api.depends('rank_ids.position', 'rank_ids.keyword_id.position')
    def _compute_stats(self):
        for comp in self:
            ranked = comp.rank_ids.filtered(lambda r: r.position and r.position > 0)
            comp.keywords_tracked = len(ranked)
            comp.avg_position = round(
                sum(ranked.mapped('position')) / len(ranked), 1) if ranked else 0.0
            ahead = 0
            for r in ranked:
                our = r.keyword_id.position
                if our and our > 0 and r.position < our:
                    ahead += 1
            comp.keywords_ahead = ahead


class CfKeywordCompetitorRank(models.Model):
    _name = 'cf.keyword.competitor.rank'
    _description = 'Competitor Position'
    _order = 'position asc'

    keyword_id = fields.Many2one(
        'cf.keyword.tracker', string='Keyword', required=True,
        ondelete='cascade', index=True)
    competitor_id = fields.Many2one(
        'cf.keyword.competitor', string='Competitor', required=True,
        ondelete='cascade', index=True)
    name = fields.Char(related='keyword_id.name', store=True, string='Keyword')
    competitor_name = fields.Char(
        related='competitor_id.name', store=True, string='Competitor domain')
    our_position = fields.Float(
        related='keyword_id.position', string='Your position', digits=(16, 1))
    position = fields.Float(string='Competitor position', digits=(16, 1))
    url = fields.Char(string='URL')
    date = fields.Date(string='Checked on')

    _sql_constraints = [
        ('kw_comp_uniq', 'unique(keyword_id, competitor_id)',
         'One current position per competitor per keyword.'),
    ]
