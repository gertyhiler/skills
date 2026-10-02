# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx==0.28.1", "python-dotenv==1.2.4"]
# ///
"""Read Grafana logs and metrics using explicit project-local configuration."""
import argparse
import asyncio
import json
import re
import time
from datetime import datetime, timezone
from urllib.parse import urlsplit, quote
import httpx
from access_common import AccessError, load_env, positive, write_private, run


def configuration(env, instance=None):
    env = dict(env)
    for alias, canonical in (("GRAFANA_USER", "GRAFANA_USERNAME"), ("GRAFANA_PASS", "GRAFANA_PASSWORD"),
                             ("GRAFANA_LOGIN_PASSWORD", "GRAFANA_PASSWORD"), ("GRAFANA_BASIC_USER", "GRAFANA_BASIC_AUTH_USER")):
        if not env.get(canonical) and env.get(alias):
            env[canonical] = env[alias]
    ids = [s.strip() for s in env.get('GRAFANA_INSTANCES', '').split(',') if s.strip()]
    if not ids and env.get('GRAFANA_URL'):
        ids = ['default']
    if not ids or (instance is None and len(ids) != 1):
        raise AccessError("Configure a Grafana instance; select --instance explicitly for multiple instances.")
    selected = instance or ids[0]
    if selected not in ids:
        raise AccessError("Selected Grafana instance is not configured.")
    prefix = 'GRAFANA_' if selected == 'default' else 'GRAFANA_' + re.sub('[^A-Z0-9]', '_', selected.upper()) + '_'
    url = env.get(prefix + 'URL', '').strip().rstrip('/')
    try:
        parsed = urlsplit(url)
        if parsed.scheme not in ('https', 'http') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError()
        parsed.port
    except ValueError:
        raise AccessError("Invalid Grafana base URL; credentials, query and fragment are forbidden.") from None
    username, password = env.get('GRAFANA_USERNAME'), env.get('GRAFANA_PASSWORD')
    basic_user, basic_password = env.get('GRAFANA_BASIC_AUTH_USER'), env.get(prefix + 'BASIC_AUTH_PASSWORD')
    if not username or not password or bool(basic_user) != bool(basic_password):
        raise AccessError("Configure Grafana login and either both or neither ingress auth fields.")
    return dict(id=selected, url=url, username=username, password=password, basic_user=basic_user, basic_password=basic_password)


class Grafana:
    def __init__(self, config, timeout_ms=30000):
        self.config = config
        self.auth = (config['basic_user'], config['basic_password']) if config['basic_user'] else None
        self.timeout = timeout_ms / 1000
        self.cookies = httpx.Cookies()
        self.logged_in = False

    def close(self):
        self.cookies.clear()

    async def _request(self, path, method, kwargs):
        async with httpx.AsyncClient(auth=self.auth, timeout=self.timeout,
                                     follow_redirects=False, trust_env=False,
                                     cookies=self.cookies) as client:
            try:
                response = await asyncio.wait_for(
                    client.request(method, self.config['url'] + '/' + path.lstrip('/'), **kwargs),
                    timeout=self.timeout,
                )
            except (TimeoutError, httpx.TimeoutException):
                raise AccessError("Grafana request exceeded its deadline.") from None
            self.cookies.update(client.cookies)
            return response

    def request(self, path, method='GET', allow_login_redirect=False, **kwargs):
        response = asyncio.run(self._request(path, method, kwargs))
        if allow_login_redirect and response.status_code == 302:
            return {}  # login() still requires the returned session cookie.
        if response.status_code < 200 or response.status_code >= 300:
            raise AccessError(f"Grafana request failed (HTTP {response.status_code}); response body suppressed.")
        if 'application/json' not in response.headers.get('content-type', ''):
            raise AccessError("Unexpected Grafana response type; cannot establish query outcome.")
        try:
            return response.json()
        except ValueError:
            raise AccessError("Grafana returned malformed JSON; response body suppressed.") from None

    def login(self):
        if not self.logged_in:
            # A redirect without a verified session is never treated as success.
            self.request('/login', 'POST', allow_login_redirect=True, json={'user': self.config['username'], 'password': self.config['password']})
            if not any(c.name == 'grafana_session' for c in self.cookies.jar):
                raise AccessError("Grafana did not return a session cookie; password login is required.")
            self.logged_in = True

    def datasource(self, kind, explicit=None):
        self.login()
        if explicit:
            return explicit
        sources = self.request('/api/datasources')
        if not isinstance(sources, list):
            raise AccessError("Unexpected Grafana datasource response.")
        sources = [s for s in sources if isinstance(s, dict) and s.get('type') == kind and s.get('uid')]
        if len(sources) != 1:
            raise AccessError(f"Expected one {kind} datasource; select its UID explicitly when ambiguous.")
        return sources[0]['uid']

    def logs(self, expr, start, end, limit, uid=None):
        uid = self.datasource('loki', uid)
        payload = self.request('/api/ds/query', 'POST', json={
            'queries': [{'refId': 'A', 'expr': expr, 'queryType': 'range', 'datasource': {'type': 'loki', 'uid': uid}, 'maxLines': limit}],
            'from': start, 'to': end})
        if not isinstance(payload, dict) or not isinstance(payload.get('results'), dict) or not isinstance(payload['results'].get('A'), dict):
            raise AccessError("Unexpected Grafana log response; cannot establish query outcome.")
        entries = []
        for result in payload['results'].values():
            if not isinstance(result, dict) or result.get('error') or result.get('status', 200) >= 400:
                raise AccessError("Grafana datasource query failed; response body suppressed.")
            frames = result.get('frames', [])
            if not isinstance(frames, list):
                raise AccessError("Unexpected Grafana log frames.")
            for frame in frames:
                entries.extend(frame_entries(frame))
        entries.sort(key=lambda row: row['timestamp'] or '')
        return {'datasourceUid': uid, 'entries': entries, 'count': len(entries),
                'query': {'expr': expr, 'from': start, 'to': end, 'limit': limit}}

    def prometheus(self, endpoint, params, uid=None):
        uid = self.datasource('prometheus', uid)
        payload = self.request('/api/datasources/proxy/uid/' + quote(uid, safe='') + '/api/v1/' + endpoint, params=params)
        if not isinstance(payload, dict) or payload.get('status') != 'success' or 'data' not in payload:
            raise AccessError("Prometheus query failed or returned an unexpected response.")
        return uid, payload['data']


def frame_entries(frame):
    fields = frame.get('schema', {}).get('fields', [])
    values = frame.get('data', {}).get('values', [])
    if not fields or not values:
        return []
    def index(names, field_type=None):
        return next((i for i, f in enumerate(fields) if f.get('name') in names or (field_type and f.get('type') == field_type)), None)
    ti = index(('Time', 'timestamp', 'time'), 'time')
    li = index(('Line', 'line', 'body', 'message'))
    labels_i = index(('labels', 'Labels'))
    if ti is None or li is None or len(values) != len(fields) or len({len(v) for v in values}) != 1:
        raise AccessError("Unexpected Grafana log frame schema.")
    entries = []
    for n in range(len(values[0])):
        stamp = values[ti][n]
        if isinstance(stamp, (int, float)):
            stamp = datetime.fromtimestamp(stamp / 1000 if stamp > 1e12 else stamp, timezone.utc).isoformat().replace('+00:00', 'Z')
        labels = values[labels_i][n] if labels_i is not None else frame.get('schema', {}).get('meta', {}).get('custom', {}).get('labels', {})
        if isinstance(labels, str):
            try:
                labels = json.loads(labels)
            except ValueError:
                labels = {'raw': labels}
        entries.append({'timestamp': stamp, 'line': str(values[li][n] or ''), 'labels': labels if isinstance(labels, dict) else {}})
    return entries


def seconds(value, now):
    if value == 'now':
        return now
    match = re.fullmatch(r'now-(\d+(?:\.\d+)?)([smhdw])', value)
    if match:
        return now - float(match[1]) * dict(s=1, m=60, h=3600, d=86400, w=604800)[match[2]]
    try:
        return float(value)
    except ValueError:
        try:
            parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
            if parsed.tzinfo is None:
                raise ValueError()
            return parsed.timestamp()
        except ValueError:
            raise AccessError("Use now, now-1h, Unix seconds or an ISO timestamp with timezone.") from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('config', 'check', 'logs', 'metrics', 'labels'):
        p = sub.add_parser(name)
        p.add_argument('--env-file')
        p.add_argument('--instance')
        p.add_argument('--timeout-ms', type=positive, default=30000)
        p.add_argument('--json', action='store_true', help='JSON is always the output format')
        if name in ('logs', 'metrics', 'labels'):
            p.add_argument('--from', dest='start', default='now-1h')
            p.add_argument('--to', dest='end', default='now')
            p.add_argument('--datasource-uid')
        if name in ('logs', 'metrics'):
            p.add_argument('--expr', required=True)
        if name == 'logs':
            p.add_argument('--limit', type=positive, default=1000)
            p.add_argument('--output')
            p.add_argument('--format', choices=('json', 'ndjson', 'text'), default='ndjson')
        elif name == 'metrics':
            p.add_argument('--instant', action='store_true')
            p.add_argument('--time', default='now')
            p.add_argument('--step', default='60s')
        elif name == 'labels':
            group = p.add_mutually_exclusive_group(required=True)
            group.add_argument('--metric')
            group.add_argument('--match', action='append')
            p.add_argument('--limit', type=positive, default=20)
    args = parser.parse_args()
    config = configuration(load_env(args.env_file), args.instance)
    if args.command == 'config':
        return {'instance': config['id'], 'url': config['url'], 'hasIngressAuth': bool(config['basic_user'])}
    client = Grafana(config, args.timeout_ms)
    try:
        if args.command == 'check':
            health = client.request('/api/health')
            client.login()
            return {'instance': config['id'], 'health': {'database': health.get('database'), 'version': health.get('version')},
                    'loki': client.datasource('loki'), 'prometheus': client.datasource('prometheus')}
        now = time.time()
        start, end = seconds(args.start, now), seconds(args.end, now)
        if start > end:
            raise AccessError("Query start must precede end.")
        if args.command == 'logs':
            result = client.logs(args.expr, str(int(start * 1000)), str(int(end * 1000)), args.limit, args.datasource_uid)
            result['instance'] = config['id']
            if args.output:
                content = json.dumps(result, indent=2) if args.format == 'json' else '\n'.join(json.dumps(row) if args.format == 'ndjson' else f"[{row['timestamp']}] {row['line']}" for row in result['entries'])
                write_private(args.output, content + '\n')
                return {k: v for k, v in result.items() if k != 'entries'} | {'output': args.output, 'format': args.format}
            return result
        if args.command == 'labels':
            uid, series = client.prometheus('series', [('match[]', x) for x in (args.match or [args.metric])] + [('start', start), ('end', end)], args.datasource_uid)
            if not isinstance(series, list) or not all(isinstance(s, dict) for s in series):
                raise AccessError("Unexpected Prometheus series response.")
            keys = sorted({key for item in series for key in item})
            return {'instance': config['id'], 'datasourceUid': uid, 'seriesCount': len(series), 'labelKeys': keys,
                    'labels': {k: sorted({str(s[k]) for s in series if k in s}) for k in keys}, 'sampleSeries': series[:args.limit]}
        if not re.fullmatch(r'(?:\d+(?:\.\d+)?)(?:[smhdw])?', args.step) or float(re.match(r'[\d.]+', args.step)[0]) <= 0:
            raise AccessError("Step must be positive seconds or a duration such as 60s.")
        params = {'query': args.expr, 'time': seconds(args.time, now)} if args.instant else {'query': args.expr, 'start': start, 'end': end, 'step': args.step}
        uid, data = client.prometheus('query' if args.instant else 'query_range', params, args.datasource_uid)
        if not isinstance(data, dict) or 'resultType' not in data or not isinstance(data.get('result'), list):
            raise AccessError("Unexpected Prometheus result shape.")
        return {'instance': config['id'], 'datasourceUid': uid, 'query': params, **data}
    finally:
        client.close()

if __name__ == '__main__':
    raise SystemExit(run(main))
