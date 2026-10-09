"""httpx tabanlı kibar HTTP istemcisi: kaynak başına izinli host, https zorunlu, bayt sınırı.

TLS: varsayılan işletim sistemi sertifika deposudur (eksik ara sertifikalı Türk kamu siteleri
Windows deposuyla çoğunlukla açılır). Doğrulaması gerçekten kırık bir host varsa yalnız
config/aggregator.json -> tls_relaxed_hosts içinde adıyla yazılırsa doğrulamasız yeniden denenir."""
import ssl
import time
from urllib.parse import urlsplit

import httpx

USER_AGENT = 'HibeRadari/0.1 (+kamuya acik hibe duyuru dizini)'
MAX_BYTES = 3_000_000


class FetchError(Exception):
    pass


class Fetcher:
    def __init__(self, allowed_hosts, relaxed_tls_hosts=(), transport=None, delay=1.0,
                 sleep=time.sleep, timeout=20.0):
        self.allowed = set(allowed_hosts)
        self.relaxed = set(relaxed_tls_hosts)
        self.delay = delay
        self.sleep = sleep
        self.last_call = 0.0
        self.calls = 0
        args = dict(headers={'User-Agent': USER_AGENT, 'Accept-Language': 'tr,en;q=0.8,de;q=0.6'},
                    timeout=timeout, follow_redirects=True, max_redirects=3, transport=transport)
        self.client = httpx.Client(verify=ssl.create_default_context() if transport is None else True, **args)
        self._args = args

    def close(self):
        self.client.close()

    def check(self, url):
        u = urlsplit(url)
        if u.scheme != 'https' or u.hostname not in self.allowed or u.username or u.password \
                or u.port not in (None, 443):
            raise FetchError(f'İzin verilmeyen URL: {url}')

    def _pause(self):
        wait = self.delay - (time.monotonic() - self.last_call)
        if self.calls and wait > 0:
            self.sleep(wait)
        self.last_call = time.monotonic()
        self.calls += 1

    def request(self, method, url, **kwargs):
        self.check(url)
        self._pause()
        try:
            response = self.client.request(method, url, **kwargs)
        except httpx.ConnectError as exc:
            host = urlsplit(url).hostname
            if 'CERTIFICATE_VERIFY_FAILED' in str(exc) and host in self.relaxed:
                with httpx.Client(verify=False, **self._args) as relaxed:
                    response = relaxed.request(method, url, **kwargs)
            else:
                raise FetchError(f'Bağlantı hatası {url}: {exc}') from exc
        except httpx.HTTPError as exc:
            raise FetchError(f'HTTP hatası {url}: {exc}') from exc
        self.check(str(response.url))          # yönlendirme izinli host dışına çıkamaz
        if response.status_code != 200:
            raise FetchError(f'HTTP {response.status_code}: {url}')
        if len(response.content) > MAX_BYTES:
            raise FetchError(f'Boyut sınırı aşıldı: {url}')
        return response

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def get_text(self, url):
        r = self.get(url)
        return r.content.decode(r.charset_encoding or 'utf-8', errors='replace')
