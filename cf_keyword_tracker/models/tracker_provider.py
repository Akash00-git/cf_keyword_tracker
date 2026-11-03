# Part of Keyword Position Tracker. Copyright (C) 2026 Webooz
# <akash00.hit@gmail.com>. See LICENSE for details.
#
# Live keyword-metrics providers. Google never returns positions/volume/CPC by
# scraping (it is blocked and against their terms), so every real rank tracker
# uses an official or licensed API. We support:
#   * Google Search Console  (free, official)  -> position, clicks, impressions, CTR
#   * DataForSEO             (paid)            -> position, volume, difficulty, CPC
#   * SerpApi                (paid)            -> position, url, SERP features
#
# fetch_keyword_metrics(env, keywords) returns {keyword_id: {metric: value}}.
import logging
from datetime import date, timedelta
from urllib.parse import urlparse

import requests

_logger = logging.getLogger(__name__)
_TIMEOUT = 30


def _param(env, key, default=None):
    return env['ir.config_parameter'].sudo().get_param(
        'cf_keyword_tracker.%s' % key, default)


def _domain_host(value):
    """Normalise a domain/URL to a bare host for matching SERP URLs."""
    if not value:
        return ''
    value = value.strip()
    if '://' not in value:
        value = 'http://' + value
    host = (urlparse(value).hostname or '').lower()
    return host[4:] if host.startswith('www.') else host


def fetch_keyword_metrics(env, keywords):
    """Dispatch to the configured provider. Never raises: on failure every
    keyword gets {'error': ...} so the refresh records the failure cleanly."""
    provider = (_param(env, 'provider', 'none') or 'none').strip()
    if provider == 'none' or not keywords:
        return {kw.id: {'error': 'No data provider configured'} for kw in keywords}
    target = _param(env, 'target_domain') or ''
    if not target and keywords[:1].website_id:
        target = keywords[:1].website_id.domain or ''
    host = _domain_host(target)
    location = _param(env, 'location', 'United States')
    language = _param(env, 'language', 'en')
    try:
        if provider == 'gsc':
            return _gsc(env, keywords)
        if provider == 'dataforseo':
            return _dataforseo(env, keywords, host, location, language)
        if provider == 'serpapi':
            return _serpapi(env, keywords, host, location, language)
    except Exception as exc:  # noqa: BLE001 - provider calls must not crash refresh
        _logger.warning("Keyword provider '%s' failed: %s", provider, exc)
        return {kw.id: {'error': str(exc)} for kw in keywords}
    return {kw.id: {'error': 'Unknown provider %r' % provider} for kw in keywords}


# ── Google Search Console ───────────────────────────────────────────────────
def _gsc_access_token(env):
    """Exchange the stored refresh token for a short-lived access token."""
    resp = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id': _param(env, 'gsc_client_id'),
        'client_secret': _param(env, 'gsc_client_secret'),
        'refresh_token': _param(env, 'gsc_refresh_token'),
        'grant_type': 'refresh_token',
    }, timeout=_TIMEOUT)
    resp.raise_for_status()
    return resp.json()['access_token']


def _gsc(env, keywords):
    site = _param(env, 'gsc_site')
    if not site:
        raise ValueError('Set the Search Console property (gsc_site) in settings')
    token = _gsc_access_token(env)
    end = date.today()
    start = end - timedelta(days=28)
    url = ('https://searchconsole.googleapis.com/webmasters/v3/sites/%s/'
           'searchAnalytics/query' % requests.utils.quote(site, safe=''))
    resp = requests.post(
        url, headers={'Authorization': 'Bearer %s' % token},
        json={'startDate': start.isoformat(), 'endDate': end.isoformat(),
              'dimensions': ['query'], 'rowLimit': 25000},
        timeout=_TIMEOUT)
    resp.raise_for_status()
    rows = {}
    for row in resp.json().get('rows', []):
        query = (row.get('keys') or [''])[0].strip().lower()
        rows[query] = row
    out = {}
    for kw in keywords:
        row = rows.get((kw.name or '').strip().lower())
        if not row:
            out[kw.id] = {}  # no impressions for this query -> not ranking
            continue
        out[kw.id] = {
            'position': round(float(row.get('position') or 0), 1),
            'clicks': int(row.get('clicks') or 0),
            'impressions': int(row.get('impressions') or 0),
            'ctr': round(float(row.get('ctr') or 0) * 100, 2),
        }
    return out


# ── DataForSEO (position + volume + difficulty + CPC) ───────────────────────
def _dfs_auth(env):
    return (_param(env, 'dfs_login'), _param(env, 'dfs_password'))


def _dataforseo(env, keywords, host, location, language):
    auth = _dfs_auth(env)
    if not auth[0] or not auth[1]:
        raise ValueError('Set the DataForSEO login/password in settings')
    names = [kw.name for kw in keywords]
    out = {kw.id: {} for kw in keywords}

    # 1) organic position + ranking URL (one task per keyword, one POST)
    tasks = [{'keyword': n, 'location_name': location,
              'language_code': language, 'depth': 100} for n in names]
    serp = requests.post(
        'https://api.dataforseo.com/v3/serp/google/organic/live/advanced',
        auth=auth, json=tasks, timeout=_TIMEOUT * 3)
    serp.raise_for_status()
    by_keyword = {}
    for task in serp.json().get('tasks', []):
        for result in (task.get('result') or []):
            kw_text = (result.get('keyword') or '').strip().lower()
            pos, rank_url, features = None, None, []
            for item in (result.get('items') or []):
                if item.get('type') in ('organic', 'featured_snippet') and \
                        _domain_host(item.get('url') or item.get('domain')) == host:
                    pos = item.get('rank_absolute') or item.get('rank_group')
                    rank_url = item.get('url')
                    break
            serp_list = []
            for item in (result.get('items') or []):
                if item.get('type') in ('organic', 'featured_snippet'):
                    dom = _domain_host(item.get('domain') or item.get('url'))
                    rnk = item.get('rank_absolute') or item.get('rank_group')
                    if dom and rnk:
                        serp_list.append({'domain': dom, 'position': float(rnk),
                                          'url': item.get('url')})
            for item in (result.get('items') or []):
                t = item.get('type')
                if t and t not in ('organic',) and t not in features:
                    features.append(t)
            by_keyword[kw_text] = {
                'position': float(pos) if pos else None,
                'url': rank_url,
                'serp_features': ', '.join(features[:5]) or None,
                'serp': serp_list,
            }
    for kw in keywords:
        data = by_keyword.get((kw.name or '').strip().lower())
        if data:
            out[kw.id].update({k: v for k, v in data.items() if v is not None})

    # 2) search volume + CPC (one bulk POST)
    try:
        vol = requests.post(
            'https://api.dataforseo.com/v3/keywords_data/google_ads/'
            'search_volume/live', auth=auth,
            json=[{'keywords': names, 'location_name': location,
                   'language_code': language}], timeout=_TIMEOUT * 2)
        vol.raise_for_status()
        vmap = {}
        for task in vol.json().get('tasks', []):
            for r in (task.get('result') or []):
                vmap[(r.get('keyword') or '').strip().lower()] = r
        for kw in keywords:
            r = vmap.get((kw.name or '').strip().lower())
            if r:
                if r.get('search_volume') is not None:
                    out[kw.id]['search_volume'] = int(r['search_volume'])
                if r.get('cpc') is not None:
                    out[kw.id]['cpc'] = round(float(r['cpc']), 2)
    except Exception as exc:  # noqa: BLE001
        _logger.info("DataForSEO volume lookup skipped: %s", exc)

    # 3) keyword difficulty (one bulk POST)
    try:
        kd = requests.post(
            'https://api.dataforseo.com/v3/dataforseo_labs/google/'
            'bulk_keyword_difficulty/live', auth=auth,
            json=[{'keywords': names, 'location_name': location,
                   'language_code': language}], timeout=_TIMEOUT * 2)
        kd.raise_for_status()
        for task in kd.json().get('tasks', []):
            for r in (task.get('result') or []):
                for item in (r.get('items') or []):
                    kw_text = (item.get('keyword') or '').strip().lower()
                    for kw in keywords:
                        if (kw.name or '').strip().lower() == kw_text and \
                                item.get('keyword_difficulty') is not None:
                            out[kw.id]['difficulty'] = int(item['keyword_difficulty'])
    except Exception as exc:  # noqa: BLE001
        _logger.info("DataForSEO difficulty lookup skipped: %s", exc)
    return out


# ── SerpApi (position + SERP features) ──────────────────────────────────────
def _serpapi(env, keywords, host, location, language):
    key = _param(env, 'serpapi_key')
    if not key:
        raise ValueError('Set the SerpApi key in settings')
    out = {}
    for kw in keywords:
        resp = requests.get('https://serpapi.com/search.json', params={
            'engine': 'google', 'q': kw.name, 'location': location,
            'hl': language, 'num': 100, 'api_key': key,
        }, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        pos, rank_url = None, None
        serp_list = []
        for item in data.get('organic_results', []):
            dom = _domain_host(item.get('link'))
            rnk = item.get('position')
            if dom and rnk:
                serp_list.append({'domain': dom, 'position': float(rnk),
                                  'url': item.get('link')})
            if pos is None and dom == host:
                pos = item.get('position')
                rank_url = item.get('link')
        res = {'serp': serp_list}
        if pos:
            res['position'] = float(pos)
            res['url'] = rank_url
        out[kw.id] = res
    return out
