"""İzinli HTTPS, IP sabitleme, sınırlı streaming ve koşullu kaynak istemcisi."""
import base64
import hashlib
import json
import math
import re
import os
import tempfile
from pathlib import Path
from urllib.robotparser import RobotFileParser
import ipaddress
import socket
import ssl
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit, urljoin
import httpx

USER_AGENT = 'HibeRadari/0.2 (+https://github.com/Aristotheles/hibe-radari)'
MAX_BYTES = 3_000_000

class FetchError(Exception):
    def __init__(self, message, kind='network'):
        super().__init__(message)
        self.kind = kind

class Fetcher:
    def __init__(self, allowed_hosts, relaxed_tls_hosts=(), transport=None, delay=1.0,
                 sleep=time.sleep, timeout=20.0, resolver=None, max_bytes=MAX_BYTES, cache_dir=None, access_policy=None):
        self.allowed = set(allowed_hosts)
        self.delay, self.sleep, self.max_bytes = delay, sleep, max_bytes
        self.last_call, self.calls = 0.0, 0
        self.resolver = resolver or (None if transport is not None else socket.getaddrinfo)
        self.cache = {}
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.access_policy = access_policy
        self.enforce_policy = transport is None or access_policy is not None
        self.robots = {}
        self.client = httpx.Client(headers={'User-Agent': USER_AGENT, 'Accept-Language': 'tr,en;q=0.8,de;q=0.6'},
            timeout=timeout, follow_redirects=False, transport=transport, trust_env=False,
            verify=ssl.create_default_context())

    def close(self):
        self.client.close()

    def check(self, url):
        try:
            u = urlsplit(url)
            valid = u.scheme == 'https' and u.hostname in self.allowed and not u.username and not u.password and u.port in (None, 443)
        except ValueError:
            valid = False
        if not valid:
            raise FetchError('İzin verilmeyen URL', 'blocked')
        return u

    def _target(self, url):
        u = self.check(url)
        try:
            literal = ipaddress.ip_address(u.hostname)
        except ValueError:
            literal = None
        if literal is not None and not literal.is_global:
            raise FetchError('Özel IP engellendi', 'blocked')
        if self.resolver is None:
            return url, {}
        try:
            addresses = self.resolver(u.hostname, 443, type=socket.SOCK_STREAM)
            ips = [ipaddress.ip_address(a[4][0]) for a in addresses]
        except (OSError, ValueError) as exc:
            raise FetchError('DNS çözülemedi', 'dns') from exc
        if not ips or any(not ip.is_global for ip in ips):
            raise FetchError('Özel IP engellendi', 'blocked')
        host = str(ips[0]); host = f'[{host}]' if ':' in host else host
        return urljoin(url, 'https://' + host + (u.path or '/') + ('?' + u.query if u.query else '')), {'sni_hostname': u.hostname}

    def _cached(self, url):
        if url in self.cache: return self.cache[url]
        if self.cache_dir is None: return None
        path = self.cache_dir / (hashlib.sha256(url.encode()).hexdigest() + '.json')
        try:
            if path.stat().st_size > self.max_bytes * 2 + 16384: return None
            data = json.loads(path.read_text(encoding='utf-8'))
            if data.get('url') != url: return None
            if not data.get('final_url'): return None
            self.check(data['final_url'])
            body = base64.b64decode(data['body'], validate=True)
            if len(body) > self.max_bytes: return None
            response = httpx.Response(200, headers=data['headers'], content=body, request=httpx.Request('GET', data['final_url']))
            self.cache[url] = response
            return response
        except (OSError, ValueError, KeyError, TypeError, FetchError):
            return None

    def _save_cache(self, url, response):
        self.cache[url] = response
        if self.cache_dir is None: return
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({'url': url, 'final_url': str(response.request.url), 'headers': dict(response.headers),
            'body': base64.b64encode(response.content).decode()}, ensure_ascii=False)
        path = self.cache_dir / (hashlib.sha256(url.encode()).hexdigest() + '.json')
        fd, name = tempfile.mkstemp(dir=self.cache_dir, suffix='.tmp')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(payload)
            os.replace(name, path)
        finally:
            if os.path.exists(name): os.unlink(name)

    def _permission(self, url):
        if not self.enforce_policy: return
        policy = self.access_policy or {}
        if policy.get('terms_status') != 'allowed' or not policy.get('evidence_url') or not policy.get('checked_at'):
            raise FetchError('Kaynak kullanım izni incelenmemiş; manuel inceleme gerekli', 'permission')
        # The provider explicitly documents these public API endpoints. This does
        # not exempt website HTML, other hosts, or arbitrary endpoints from robots.
        if (policy.get('documented_api') == 'grants_gov_public'
                and policy.get('evidence_url') == 'https://www.grants.gov/api/terms-conditions'
                and url in ('https://api.grants.gov/v1/api/search2',
                            'https://api.grants.gov/v1/api/fetchOpportunity')):
            return
        origin = 'https://' + urlsplit(url).netloc
        if origin not in self.robots:
            parser = RobotFileParser(origin + '/robots.txt')
            try:
                response = self.request('GET', origin + '/robots.txt', _robots=True)
                if 'html' in response.headers.get('content-type','').lower() or response.text.lstrip().startswith('<'):
                    raise FetchError('robots.txt yerine HTML alındı; manuel inceleme gerekli','permission')
                parser.parse(response.text.splitlines())
                parser.raw_rules = response.text
            except FetchError as exc:
                if str(exc) == 'HTTP 404': parser.parse([])
                else: raise FetchError('robots.txt doğrulanamadı; manuel inceleme gerekli', 'permission') from exc
            self.robots[origin] = parser
        parser = self.robots[origin]
        wildcard_blocked = False
        # RFC 9309 * ve $ desenlerini standart kütüphanenin sessizce atlamasına izin verme.
        current_agents, rules, has_rules = [], [], False
        groups = []
        for line in getattr(parser,'raw_rules','').splitlines()+['User-agent: __end__']:
            line=line.split('#',1)[0].strip()
            if ':' not in line: continue
            name,value=line.split(':',1);name=name.strip().lower();value=value.strip()
            if name=='user-agent':
                if has_rules:groups.append((current_agents,rules));current_agents=[];rules=[];has_rules=False
                current_agents.append(value.lower())
            elif name in ('allow','disallow'):
                rules.append((name,value));has_rules=True
        specific=[g for g in groups if any(a!='*' and a in USER_AGENT.lower() for a in g[0])]
        selected=specific or [g for g in groups if '*' in g[0]]
        target=urlsplit(url).path or '/'
        if urlsplit(url).query:target+='?'+urlsplit(url).query
        def normalize_unreserved(value):
            def decode(match):
                char=chr(int(match.group(1),16))
                return char if char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~' else '%'+match.group(1).upper()
            return re.sub(r'%([0-9a-fA-F]{2})',decode,value)
        target=normalize_unreserved(target)
        matched=[]
        for agents, group_rules in selected:
            for name,value in group_rules:
                if not value:continue
                value=normalize_unreserved(value)
                pattern='^'+re.escape(value).replace(r'\*','.*')
                if value.endswith('$'):pattern=pattern[:-2]+'$'
                if re.search(pattern,target):matched.append((len(value.replace('*','').rstrip('$')),name=='allow'))
        if matched:wildcard_blocked=not max(matched)[1]
        if not parser.can_fetch(USER_AGENT, url) or wildcard_blocked:
            raise FetchError('robots.txt taramayı engelliyor', 'permission')
        crawl_delay = parser.crawl_delay(USER_AGENT) or parser.crawl_delay('*')
        if crawl_delay: self.delay = max(self.delay, crawl_delay)

    def _pause(self):
        wait = self.delay - (time.monotonic() - self.last_call)
        if self.calls and wait > 0:
            self.sleep(wait)
        self.last_call = time.monotonic(); self.calls += 1

    def request(self, method, url, **kwargs):
        robots_request = kwargs.pop('_robots', False)
        original, method = url, method.upper()
        self.check(url)
        if not robots_request: self._permission(url)
        cached = self._cached(original) if method == 'GET' else None
        headers = dict(kwargs.pop('headers', {}) or {})
        if cached:
            if cached.headers.get('etag'): headers['If-None-Match'] = cached.headers['etag']
            if cached.headers.get('last-modified'): headers['If-Modified-Since'] = cached.headers['last-modified']
        retries, redirects = 0, 0
        while True:
            if not robots_request: self._permission(url)
            target, extensions = self._target(url)
            request_headers = dict(headers)
            if extensions: request_headers['Host'] = urlsplit(url).hostname
            self._pause()
            try:
                with self.client.stream(method, target, headers=request_headers, extensions=extensions, **kwargs) as response:
                    status = response.status_code
                    if status in (301, 302, 303, 307, 308):
                        redirects += 1
                        if redirects > 3 or not response.headers.get('location'):
                            raise FetchError('Yönlendirme sınırı/geçersiz yönlendirme', 'redirect')
                        next_url = urljoin(url, response.headers['location'])
                        self.check(next_url)
                        # Başka izinli host'a bile hassas başlık taşınmaz.
                        if urlsplit(next_url).hostname != urlsplit(url).hostname:
                            headers = {k:v for k,v in headers.items() if k.lower() not in ('authorization','cookie','if-none-match','if-modified-since')}
                        if status == 303 or (status in (301, 302) and method == 'POST'):
                            method, kwargs = 'GET', {}
                        url = next_url
                        continue
                    if status == 429 and retries < 1 and method == 'GET':
                        value = response.headers.get('retry-after', '1')
                        try: wait = float(value)
                        except ValueError:
                            try: wait = (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
                            except (ValueError, TypeError): wait = 1
                        if not math.isfinite(wait) or wait > 60: raise FetchError('Retry-After uzun; sonraki koşuyu bekle', 'rate_limit')
                        self.sleep(max(0, wait)); retries += 1
                        continue
                    if status == 304:
                        if cached is None: raise FetchError('304 için önceki veri yok', 'cache')
                        return httpx.Response(200, headers=cached.headers, content=cached.content,
                            request=httpx.Request(method, str(cached.request.url)), extensions={'not_modified': True})
                    if status != 200:
                        raise FetchError(f'HTTP {status}', 'rate_limit' if status == 429 else 'http')
                    try: length = int(response.headers.get('content-length', '0'))
                    except ValueError: raise FetchError('Geçersiz Content-Length', 'format')
                    if length > self.max_bytes: raise FetchError('Boyut sınırı aşıldı', 'size')
                    data = bytearray()
                    for chunk in response.iter_bytes(chunk_size=16384):
                        data.extend(chunk)
                        if len(data) > self.max_bytes: raise FetchError('Boyut sınırı aşıldı', 'size')
                    decoded_headers = dict(response.headers)
                    decoded_headers.pop('content-encoding', None)
                    decoded_headers['content-length'] = str(len(data))
                    result = httpx.Response(200, headers=decoded_headers, content=bytes(data), request=httpx.Request(method, url))
                    if method == 'GET': self._save_cache(original, result)
                    return result
            except httpx.HTTPError as exc:
                kind = 'tls' if 'CERTIFICATE_VERIFY_FAILED' in str(exc) else 'timeout' if isinstance(exc, httpx.TimeoutException) else 'network'
                raise FetchError(f'{kind}: {type(exc).__name__}', kind) from exc

    def get(self, url, **kwargs): return self.request('GET', url, **kwargs)
    def get_text(self, url):
        r = self.get(url)
        return r.content.decode(r.charset_encoding or 'utf-8', errors='replace')
