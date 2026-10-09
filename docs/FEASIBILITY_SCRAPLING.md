# Fizibilite — Scrapling ile toplu hibe toplama (2026-10-09, Claude Code)

Hedef: AB, diğer ülkeler ve Türkiye içi öğretmen/okul hibe ve proje çağrılarını düzenli toplayıp sitede duyurmak. Bu belge öneridir; onaylanmış karar değildir.

## Karar özeti
**Evet, yapılabilir; ama Scrapling çekirdek olmamalı.** Kaynakların büyük kısmı kazımaya ihtiyaç duymuyor: resmî API ve RSS var. Scrapling yalnız HTML-only sayfalarda ve **yalnız ayrıştırıcı** olarak (kendi ağ katmanı değil) işe yarar. Anti-bot/Cloudflare aşma özelliklerini kullanmıyoruz.

## Ölçülenler (bugün, izole venv, proje değişmedi)
| Bulgu | Kanıt |
|---|---|
| Scrapling 0.4.15 (BSD-3, Python ≥3.10) Python 3.14.5'e kuruldu | `pip install "scrapling[fetchers]"` başarılı; venv 258 MB (playwright/patchright/curl_cffi dahil). Yalnız ayrıştırıcı kurulumu küçük (lxml, cssselect) |
| Düz `Fetcher` 9 sayfadan 6'sını 0,2–0,8 sn'de çekti (ab-ilan, STGM, jugendbruecke, DOKA, TÜBİTAK, IF Türkiye) | HTTP 200 |
| **2 sitede TLS hatası**: ua.gov.tr ve blacksea-cbc.net | curl_cffi kendi CA paketini kullanıyor, eksik ara sertifika zincirini kabul etmiyor. Projenin mevcut `hibe.scan.fetch` aynı iki siteyi **başarıyla** çekti |
| fundsforNGOs Cloudflare "Just a moment" ekranı veriyor (HTTP 403) | Aşmak için stealth gerekir; bunu önermiyoruz (bkz. Hukuk) |
| **AB Funding & Tenders arama API'si çalışıyor** | `api.tech.ec.europa.eu/search-api/prod/rest/search` HTTP 200, yapılandırılmış sonuç (kimlik, başlık, son tarih); kazıma gereksiz |
| RSS/JSON mevcut | ab-ilan.com `/category/hibe-duyurulari/feed/`, stgm.org.tr `/rss.xml`, tubitak.gov.tr `/tr/rss.xml`, ifturquie.org `/wp-json/wp/v2/posts` (hepsi 200) |
| HTML liste yapısı çıkarılabilir | ab-ilan: `h3.entry-title a`; TÜBİTAK: `/tr/duyuru/...` bağlantıları. STGM/DOKA/jugendbruecke için seçici henüz yazılmadı (benim tahmin seçicilerim 0 eşleşti; sayfa çekimi sorun değil) |

## Önerilen mimari: dört katman
1. **API** (AB F&T; muhtemelen grants.gov benzeri programlar): en güvenilir, tarih/ID yapılandırılmış.
2. **RSS/JSON**: ab-ilan, STGM, TÜBİTAK, IF Türkiye ve benzerleri; sıfır kırılganlık.
3. **HTML liste**: DOKA, Ulusal Ajans, jugendbruecke, blacksea-cbc, büyükelçilik sayfaları. Çekimi mevcut güvenli `fetch` yapar (izinli host, özel IP engeli, yönlendirme yok), ayrıştırmayı Scrapling `Selector` yapar. Mevcut `parse_listing` kuralı kalır: yapı belirteci yoksa hata, sıfır ilan başarı sayılmaz.
4. **Tarayıcı (Playwright)**: yalnız JS ile yüklenen ve robots/ToS'a izin veren sayfalar; şimdilik hedef yok.

Toplayıcı kaynaklar (ab-ilan, STGM, fundsforNGOs) mevcut `type: discovery` mantığıyla **ipucu** sayılır; çağrı, resmî belge incelenmeden yayınlanmaz. Admin onayı ve kanıt kuralı aynen kalır.

## Neden Scrapling'i çekirdek yapmıyoruz
- Kendi ağ katmanı proje güvenlik duvarını (SSRF: pinned IP, izinli host, yönlendirme yok) atlar; `docs/SECURITY.md` ile çelişir.
- 0.x sürüm (API değişebilir), ağır bağımlılıklar (playwright, patchright, browserforge) — mevcut requirements yalnız `firebase-admin` ve `pypdf`; CI/cron ve barındırma ağırlaşır.
- TLS bulgusu: tam bu projenin hedeflediği Türk kamu siteleri en sorunlu olanlar.
- "Adaptive parser" ve anti-bot iddiaları README'den; biz bağımsız doğrulamadık.

## Hukuk, etik, KVKK (bağlayıcı kurallar)
- robots.txt ve site koşullarına uyulur; kaynak başına gecikme (≥ 5 sn), günde en çok birkaç istek; tanımlı User-Agent (`HibeRadari/0.1`, iletişim adresiyle).
- Cloudflare/Turnstile gibi koruma **aşılmaz**. fundsforNGOs bu yüzden kazınmaz; gerekirse yayıncıdan izin istenir veya yalnız bağlantı verilir.
- Telif: tam metin kopyalanmaz. Yalnız olgusal alanlar (başlık, kurum, son tarih, uygunluk, tutar), kısa özet ve **kaynağa bağlantı**; "resmî sayfada doğrulayın" notu.
- Kişisel veri: çağrı metinlerindeki kişi e-posta/telefonları saklanmaz; yalnız kurum iletişimi.
- sabancivakfi.org robots.txt yalnız bir bot adına izin veriyor (genel kural yok); otomatik tarama yerine manuel/duyuru takibi tercih edilir.

## Ölçek ve maliyet (tahmin, ölçülmedi)
- 30–50 kaynakta tahminen yarısından fazlası API/RSS ile karşılanır; HTML kaynak başına seçici + fixture + boş-liste testi için yarım–bir gün.
- LLM (Gemini) yalnız hash'i değişen sayfada çağrılır; haftalık 50 kaynak için maliyet düşük ama gerçek rakam canlı pilotta ölçülmeli.
- Bakım: site yapısı değişince parser kırılır → "yapı değişti" alarmı admin panelinde görünür (mevcut tasarım buna uygun).

## Riskler
Yanlış tarih/uygunluk çıkarımı (kanıt konumu + insan onayı ile azaltılır) · site engeli/IP yasağı · telif/ToS itirazı · bakım yükü · Türk kamu sitelerinin TLS/erişim sorunları (bazı gsb.gov.tr, tr.emb-japan adresleri bu ağdan açılmadı).

## Önerilen sıradaki adım (1 günlük kanıt çalışması)
Üç bağlayıcı: (a) AB F&T API, (b) genel RSS okuyucu (ab-ilan, STGM, TÜBİTAK), (c) bir HTML kaynak (jugendbruecke) için Scrapling `Selector`. Fixture testleri + mevcut `scan_source` boru hattına bağlama. Başarı ölçütü: 3 kaynaktan en az 10 gerçek çağrı adayı, hepsi kaynak bağlantılı, sıfır uydurma alan. Sonra `config/sources.json`'a `method: api|feed|html` eklenir. Bu adım için yetki: mevcut yerel kapsam yeterli; Firebase/Gemini/deploy gerekmez.
