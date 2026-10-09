# MEVCUT SİSTEM ANALİZİ

Hibe Radarı · Codex · 9 Ekim 2026 · Europe/Istanbul

**Sonuç:** Mevcut Python/HTML/CSS/JS mimarisi korunabilir. Kaynak çekme, tarih çıkarımı, ilgililik süzgeci, URL tekilleştirmesi, SQLite/Firestore adaptörleri, JSON API, yönetici onayı ve statik üretim zaten var. Ancak yönetici onaylı uygulama ile statik site toplayıcısı aynı onay/veri yoluna bağlı değil. Kaynakları genişletmeden önce başarısız toplamanın doğru veriyi kaldırması ve onaysız yayın üretimi engellenmeli. Yeni proje, ikinci toplayıcı, SQL teknolojisi veya yapılandırma formatı değişikliği gerekmiyor.

**İnceleme sınırı:** Kod, yapılandırmalar, yerel veri/çıktı, testler, hata kayıtları ve yerel görev zamanlayıcı incelendi. Ağsız testler ve bellek/geçici klasör içinde hata tekrarları çalıştırıldı. Yeni canlı kaynak taraması, Firebase deploy, bulut zamanlayıcı sorgusu, gerçek Auth/Firestore/Gemini/SMTP testi yapılmadı. Bu çalışmada yalnız bu rapor oluşturuldu; uygulama kodu, entegrasyonlar ve ortak hafıza değiştirilmedi; commit oluşturulmadı.

Kullanıcının sözünü ettiği ayrı RSS/WP-JSON/JS/SQLite/RapidFuzz taslağı, proje içindeki taslak/draft/crawler/scraper/scheduler dosya adı ve bağımlılık/çağrı aramalarıyla bulunmadı. Dışarıdaki taslağın dosya içeriği incelenmiş değildir. Bölüm 3, kullanıcının bildirdiği işlevlerle mevcut kodu karşılaştırır.

## 1. Mevcut sistem mimarisi

### Aynı proje içinde iki veri akışı

**Onaylı uygulama yolu:** config/sources.json → pipeline.scan_source → scan.fetch → FakeExtractor/GeminiExtractor → calls/runs deposu → Service.approve → domain.publishable/public_calls → /api/calls veya hibe.export.

- [pipeline.scan_source](C:/hibe-radari/hibe/pipeline.py:9): Önceden tanımlı call_urls ve bağlı belgeleri işler. registry_pending, eksik host veya eksik çağrı URL'sinde manual_pending kaydeder. Yeni çağrı keşfi bu fonksiyonun işi değildir.
- [scan.fetch](C:/hibe-radari/hibe/scan.py:13): HTTPS/izinli host, genel IP kontrolü, IP pinleme, 2 MB okuma sınırı, 100 sayfa PDF sınırı ve normalize metin hash'i içerir. Yönlendirmeyi izlemez.
- [GeminiExtractor](C:/hibe-radari/hibe/llm.py:6): Model varsayılanı gemini-3.8-flash; anahtar backend ortamından alınır. Metin/çağrı/çıktı sınırları ve telefon/e-posta maskelemesi vardır. Gerçek model yanıtı denenmedi.
- [Service.save/approve/public](C:/hibe-radari/hibe/service.py:6) ve [domain.publishable](C:/hibe-radari/hibe/domain.py:34): Yönetici yetkisi ve içerik sürümüne bağlı onay vardır. Onaysız, eski onaylı, kapanmış veya askıya alınmış çağrı kamu listesinden çıkarılır.

**Duyuru toplama/statik yayın yolu:** config/aggregator.json + config/relevance.json → collector.run_source → RSS/API/HTML bağlayıcıları → RelevanceFilter → collector.dedupe → latest.json → site.build → public/ → ayrıca Firebase Hosting deploy.

- [CONNECTORS](C:/hibe-radari/hibe/aggregator/collector.py:16): eu_ft, feed, html_list, html_cards, html_crawl, page_watch olmak üzere altı yöntem.
- [collector.run](C:/hibe-radari/hibe/aggregator/collector.py:91): Kaynakları sıralı çalıştırır; karar grupları ve kaynak durumlarını üretir.
- [CLI main](C:/hibe-radari/hibe/aggregator/__main__.py:11): Raporu yazar; --site verilirse site üretir. Firebase deploy yapmaz.
- [site.build](C:/hibe-radari/hibe/aggregator/site.py:528): Lovable görünümü, detay, takvim, ICS, JSON, sitemap ve varlıkları üretir. [firebase.json](C:/hibe-radari/firebase.json) public/ klasörünü Hosting kökü yapar; Python API'ye rewrite yoktur.

**Model ayrımı:** [GrantOpportunity](C:/hibe-radari/hibe/aggregator/models.py:31), uygulamadaki calls kaydı değildir. Toplayıcı deadline_evidence, audience, original_url ve relevance taşır; documents hash'leri, paths, official_status, içerik version ve yönetici approval alanlarını taşımaz. Doğrudan Service.save içine aktarmak [domain.validate](C:/hibe-radari/hibe/domain.py:13) sözleşmesini karşılamaz. Veri/onay köprüsü mevcut sayılmamalı.

### Depo ve API

[store.py](C:/hibe-radari/hibe/store.py:7): MemoryStore, SQLiteStore ve FirestoreStore; ortak sözleşme get/put/all.

SQLite şeması salt okunur incelendi: records(kind TEXT, id TEXT, value TEXT, PRIMARY KEY(kind,id)). JSON değer, INSERT OR REPLACE ile değiştirilir. Oturumdaki data/demo.db: 2 calls, 1 users kaydı. Bu, gerçek toplayıcının SQLite'a yazıldığı anlamına gelmez. Pipeline ayrıca runs, bülten kodu outbox türlerini kullanır.

FirestoreStore koleksiyon/belge set kullanır; transaction veya kalıcı sürüm geçmişi yoktur. [firestore.rules](C:/hibe-radari/firestore.rules) istemci erişimini kapatır; sunucu Admin SDK/IAM ayrı konudur. Yeni SQLite/PostgreSQL geçişi önerilmiyor.

[server.handler](C:/hibe-radari/hibe/server.py:29): GET /api/config, /api/calls, /api/sources, /api/me, /api/admin; POST /api/call, /api/approve, /api/preferences, /api/unsubscribe. Bu API onaylı uygulama yolundadır; statik Hosting'in data.json dosyası ayrı çıktıdır.

Sunucunun süreç içi POST kilidi ve SQLite RLock'u vardır; ayrı pipeline süreci veya birden fazla sunucu için ortak transaction garantisi değildir.

## 2. Gerçekte çalışan kaynaklar ve toplama yöntemleri

### config/sources.json

[Dosya](C:/hibe-radari/config/sources.json) 30 kayıt içeriyor: 19 candidate, 11 missing; **30'un tamamı registry_pending**. 15 kayıtta URL/last_checked bulunması çalışan otomatik entegrasyon anlamına gelmez. Bunlar pipeline.scan_source tarafından hazır çağrı kaynağı olarak işlenmez.

[registry.TARGET/audit_sources](C:/hibe-radari/hibe/registry.py:10) tam 30 kayıt şartını sabit kodlar. Kimlik kanıtı, yöntem, izinli host, call_urls/manuel adım ve ready durumunu denetler. Bu kayıt biçimi, aggregator.json liste keşif biçiminden farklıdır; iki dosyayı körlemesine birleştirmek mevcut akışı/testleri bozar.

### config/aggregator.json

[Dosyada](C:/hibe-radari/config/aggregator.json) **13 kaynak bloğu** bulunuyor. sabit-izleme altı ülke/program sayfasını tek blokta toplar. 13 blok, 13 bağımsız kurum veya 13 doğrulanmış açık çağrı değildir.

Sayılar data/aggregator/latest.json dosyasındaki **2026-10-09T19:38:21** tarihli çalıştırmadan okundu. Bu incelemede yeniden canlı çekim yapılmadı. error=null, parser doğruluğunun bağımsız kanıtı değildir.

| Kimlik | Yöntem / yapılandırılmış uç nokta | Çekilen | Sınır |
|---|---|---:|---|
| eu-ft | eu_ft; api.tech.ec.europa.eu arama JSON API'si | 15 | 2 sorgu; Ulusal Ajans okul çağrıları yerine geçmez |
| tubitak-4000 | feed; 4000.tubitak.gov.tr/rss.xml | 10 | Akışın güncelliği erişimden ayrı |
| tubitak-duyuru | html_list; tubitak.gov.tr/tr/duyuru ve page=1 | 36 | 21 detay; en fazla 40 öğe |
| ab-ilan-hibe | feed; ab-ilan.com/category/hibe-duyurulari/feed/ | 10 | Derleme; 4 detay |
| ab-ilan-genel | feed; ab-ilan.com/feed/ | 10 | Derleme; 2 detay; diğer akışla örtüşür |
| stgm-hibe | html_cards; www.stgm.org.tr/hibe-duyurulari | 18 | CSS seçicileri; acik sınıfı; detay kapalı |
| jugendbruecke | html_crawl; www.jugendbruecke.de/foerderung/ | 3 | Bir seviye; max_pages=12 |
| etwinning-tr | feed; etwinning.meb.gov.tr/feed/ | 10 | Haber/fırsat ayrımı süzgece bağlı |
| ifturquie | feed; www.ifturquie.org/feed/ | 11 | WP-JSON fizibilitesi var; mevcut çekici RSS |
| britishcouncil-tr | feed; www.britishcouncil.org.tr/rss.xml | 50 | Tarihsel sonuç; sonraki erişimi garanti etmez |
| tusev | feed; www.tusev.org.tr/feed/ | **0** | Hata yok; boş akış mı parser sorunu mu belirsiz |
| sivilsayfalar | feed; www.sivilsayfalar.org/feed/ | 9 | Derleme; 2 detay |
| sabit-izleme | page_watch; DAP, CFLI, İngiltere fonu, PAD, PASCH, OeAD | 6 | Program sayfası açık çağrı değildir; son üçünde no_deadline=true |

Fonksiyon kanıtları: [feeds.collect](C:/hibe-radari/hibe/aggregator/feeds.py:10), [eu_ft.collect](C:/hibe-radari/hibe/aggregator/eu_ft.py:67), [collect_list](C:/hibe-radari/hibe/aggregator/html_cards.py:30), [collect_cards](C:/hibe-radari/hibe/aggregator/html_cards.py:49), [collect_crawl](C:/hibe-radari/hibe/aggregator/html_cards.py:120), [collect_pages](C:/hibe-radari/hibe/aggregator/html_cards.py:98).

Son rapor: 188 çekilmiş öğe; tekilleştirme sonrası 186 = 5 kabul + 11 inceleme + 21 izleme + 44 genel + 105 ret. Yerel public/data.json aynı tarih/sayıları taşıyor ve **81 öğe** içeriyor. Devirdeki 78 liste kaydıyla bu yerel dosya örtüşmüyor; canlı kart sayısı yeniden ölçülmedi.

### 127 kaynak sayım farkı

[KAYNAK_ENVANTERI.md](C:/hibe-radari/docs/KAYNAK_ENVANTERI.md) sekiz kategori içeriyor; HTTPS adres taşıyan tablo satırları sayılınca **135 satır ve 135 farklı URL** var.

| Kategori | Satır |
|---|---:|
| AB merkezi | 25 |
| AB–Türkiye / sınır ötesi | 8 |
| Türkiye kamu | 19 |
| Elçilik / ikili fon | 31 |
| BM | 8 |
| Türkiye vakıf/STK | 13 |
| Çevre/bilim/ödül/yarışma | 20 |
| Derleme | 11 |
| **Toplam** | **135** |

Dosyanın yöntem etiketleri: 2 API, 70 HTML, 23 Elle, 7 RSS, 30 İzleme, 3 RSS?. Tarihsel durum etiketleri: 126 adet 200, 7 engel, 1 adet 503, 1 yanıt yok. Bunlar 135 çalışan çekici değildir. 127'ye ulaşmak için sekiz kaynağı keyfî silmek yerine kurum/program/uç nokta sayımı uzlaştırılmalı.

## 3. Zaten mevcut olan özellikler

| Bildirilen taslak işlevi | Mevcut dosya/fonksiyon | Gerçek durum |
|---|---|---|
| RSS/Atom | feeds.collect, feedparser | Var; bozuk/boş akış doğrulaması yetersiz |
| JSON/API | eu_ft.build_query/collect/parse | AB API'sine özel var; genel mapping çekicisi yok |
| WP-JSON | docs/FEASIBILITY_SCRAPLING.md | Fizibilite var; CONNECTORS içinde uygulama yok |
| HTML liste/kart | collect_list, collect_cards | Var; config seçici/desenleri |
| Sınırlı keşif | collect_crawl | Var; bir seviye/sayfa sınırı |
| Program izleme | collect_pages, collector.pin | Okuma/sezgi var; hash değişiklik geçmişi yok |
| JavaScript sayfa çekme | Uygulamada karşılık yok | Tarayıcı veri çekicisi yok; arayüz JS'i bunun yerine geçmez |
| SQLite | store.SQLiteStore | Demo/domain için var; toplayıcı yazmıyor |
| Firestore | store.FirestoreStore, server.App | Adaptör var; canlı bağlantı doğrulanmadı |
| RapidFuzz | collector.dedupe, models.canonical_url | URL tekilleştirme var; fuzzy bağımlılık/yöntem yok |
| Son tarih | textutil.find_deadline, eu_ft.parse, collect_cards | Var; somut doğruluk hataları mevcut |
| İlgililik filtresi | RelevanceFilter.evaluate, relevance.json | Açıklanabilir puan; kesin ülke/başvuran uygunluğu değil |
| Koşullu uygunluk | domain.eligibility, profile, paths/conditions | Onaylı uygulamada var; toplayıcıya bağlı değil |
| JSON API | server.handler | Var; statik yayında Python API çalışmıyor |
| JSON çıktı | collector.write_report, site.build | Var; koşular arası geçmiş/birleştirme yok |
| Yönetici onayı | Service.approve, web/app.js admin | Sürüme bağlı var; toplayıcı statik yayını kullanmıyor |
| Kaynak yönetimi | /api/admin sources, web/app.js admin | Görüntüleme var; kaynak CRUD/anında tara yok |
| Hata izolasyonu | run_source, pipeline.scan_source | Var; boş parser/kısmi hata görünürlüğü eksik |
| Zamanlama | CLI, GitHub test workflow'u | Repo içinde otomatik toplama/yayın görevi yok |

Taslağı doğrudan kopyalamak ikinci depo/API/onay modeli doğurabilir. Eksik davranışlar mevcut fonksiyonlara eklenmeli.

## 4. Eksik özellikler ve gerçek hatalar

**Yeniden üretildi** ifadesi gerçek sitelere gitmeden mevcut fonksiyonlarla bellek/geçici dosya denemesi yapıldığını gösterir. Diğer bulgular kod yoluna dayanır; canlıda yaşandığı varsayılmaz.

### R1 — Onaysız kayıt yayın yolunda: kritik, yeniden üretildi

[site.prepare](C:/hibe-radari/hibe/aggregator/site.py:117) accepted/review/watch/general gruplarını approval kontrolü olmadan alıyor. Approval'sız tek review öğesi verildi; çıktı 1 öğe oldu. build bunu detay/JSON'a yazar. İnsan onayı yapılmadığı site metninde açıkça söyleniyor; açıklama MVP onay kapısının yerine geçmez. Service.approve var fakat bu kayıtlara uygulanmıyor. Heuristik accept kararını yönetici onayı saymak çözüm değildir.

### R2 — Hatalı koşu doğru veriyi çıktıdan kaldırıyor: kritik, yeniden üretildi

run_source hata halinde boş liste döndürür; run eski veriyi okumaz. write_report latest.json üzerine yazar. CLI, hata için exit=1 dönmeden **önce raporu ve siteyi üretir**.

[site.build](C:/hibe-radari/hibe/aggregator/site.py:528) eski ilan HTML/ICS dosyalarını siler. Geçici klasörde önce 1 doğru ilan üretildi; ardından HTTP 503 kaynak hata raporuyla build çağrıldı: detay **1 → 0**, public JSON öğesi **1 → 0**. Bu SQL DELETE değildir; raporun üzerine yazılması ve statik çıktıdan kaldırmadır. Sonraki deploy canlı ilanı da kaldırabilir.

--only kısmî koşusunu aynı latest.json/public yoluna yazmak diğer kaynakların sonuçlarını da kaldırabilir. Tam/kısmî snapshot ayrımı, son sağlam kayıt koruması ve atomik çıktı değişimi yoktur.

### R3 — Başlangıç tarihi son tarih seçiliyor: yüksek, yeniden üretildi

[find_deadline](C:/hibe-radari/hibe/aggregator/textutil.py:66) tarih çevresindeki ipuçlarını arar ve en yakın gelecek tarihi seçer. “Başvurular 1 Kasım 2026 tarihinde başlar; son başvuru 30 Kasım 2026.” girdisinde **2026-11-01** seçildi; doğru son tarih **2026-11-30**.

“Son başvuru: 2026-11-30” girdisi None döndürdü: ISO tarih metin regex'inde yok. Genel başvurular/kadar ipuçları etkinlik/başlangıç tarihini de yakalayabilir. Çok aşamalı tarih, saat/zaman dilimi ve belirsizlik seviyesi modellenmiyor. eu_ft.parse da birden fazla deadlineDate içinden en yakın gelecek günü alır; aşama/başvuru yolu ilişkisi saklanmaz.

### R4 — Fazla/eksik birleşme ve alan kaybı: yüksek, yeniden üretildi

[dedupe](C:/hibe-radari/hibe/aggregator/collector.py:74) source_url/original_url canonical eşleşmesini yeterli sayar; dönem/çağrı kimliği yok.

- Farklı URL'li “2026 çağrısı” ve “2027 farklı çağrı” aynı genel resmî homepage original_url taşırken **2 → 1** birleşti. enrich, resmî aday olarak ilk uygun dış bağlantıyı da seçebilir; dolayısıyla bu durum mevcut veri yolunda mümkündür.
- Aynı URL'li ilk öğenin deadline=None, ikinci öğenin deadline=2026-11-30 olduğu denemede sonuç **None** kaldı. Kopyanın daha iyi alanları/kanıtı birleştirilmez.
- A ile B'yi bağlayan kopya atılırken B alias'ı indekse eklenmez; üçüncü B kopyası kalır: beklenen 1 yerine **2**.
- Aynı program farklı URL'lerde ve original_url çıkarılamadığında birleşmez. Sabit program URL'sinden üretilen id yıllar arasında aynı olabilir. Körlemesine fuzzy eşleştirme bu riskleri çözmez; farklı dönemleri karıştırabilir.

### R5 — Query kimlikleri kayboluyor: yüksek, yeniden üretildi

[collect_list](C:/hibe-radari/hibe/aggregator/html_cards.py:30) yalnız path ile seen tutar ve hostname+path URL üretir; query atılır. collect_cards/crawl da query taşımaz. Farklı başlıklı /call?id=1 ve /call?id=2 bağlantıları **tek /call** kaydına indirildi. Query tabanlı kurum sitelerinde gerçek çağrı kaybı yaratır.

### R6 — Sessiz parser bozulması: yüksek, yeniden üretildi

[feeds.collect](C:/hibe-radari/hibe/aggregator/feeds.py:10), feedparser format/bozo durumunu kontrol etmez. HTTP 200 bakım HTML'i verildi: **fetched=0, error=None**. TÜSEV'in son raporda 0/error=null olması aynı tür belirsizliği taşır; kesin bozuk olduğu söylenemez.

HTML seçici kaybı da başarılı sıfır öğe görünebilir. collect_crawl ara sayfa hatalarını kaydetmeden continue eder. run_source detay hatalarını yalnız öğe gerekçesine koyar; kaynak error boş kalır. how_body buna göre başarı simgesi gösterebilir. Önceki sayı karşılaştırması, parser sürümü, anomali alarmı ve kalıcı sağlık geçmişi yok.

### R7 — Host sınırı yönlendirmeden sonra denetleniyor: yüksek, yeniden üretildi

[Fetcher](C:/hibe-radari/hibe/aggregator/net.py:21) HTTPS/host/port/timeout/bekleme uygular. Ancak follow_redirects=True; son hedef kontrolü istek tamamlandıktan sonradır. Mock deneyde izinli example.org ardından izin dışı outside.example.org'a **ikinci istek gönderildi**, daha sonra FetchError oluştu. Her redirect takip edilmeden kontrol edilmeli.

3 MB sınırı response.content tamamen alındıktan sonra ölçülür; ağ/bellek kullanımını baştan kesmez. scan.fetch genel IP/pinleme önlemleri bu istemcide yoktur. tls_relaxed_hosts şu an boş; TLS istisna özelliği var ama yapılandırmada açık değil.

### R8 — İlgi puanı Türkiye/lise uygunluğu değil: yüksek

[evaluate](C:/hibe-radari/hibe/aggregator/relevance.py:42) başlık/kategori ve kısa açıklama terimlerini puanlar. config/profile.json ülke/kurum profili evaluate'a verilmez. Ülke listesi, yaş, sınıf, başvuran tüzel kişilik ve ortak zorunluluğu değerlendirilmez. school terimleri ilkokul/ortaokulu da kapsar.

**Yeniden üretildi:** “Lise öğretmenlerine hibe çağrısı” accept/7; “Lise öğretmenlerine çevre ve iklim hibe çağrısı” review/3. Çevre/iklim negatif ngo-humanitarian listesinde. “Lise öğrencilerine değişim bursu başvurusu” general/1. Bireysel burs ve eğitim/kurs cezaları yeni öğrenci/eğitim fırsatı kapsamıyla uzlaştırılmalı. Bu örnekler gerçek çağrı kararı değil, kural davranışı kanıtıdır.

run_source yalnız ilk süzgeçte elenmeyen ve tarihi olmayan öğeleri detaylandırır. Başlığı alakasız fakat ayrıntısı okula uygun çağrı kurtarılamayabilir. Tarihi bulunan derleme kaydı detaylandırılmadığından asıl kaynak adayı da çıkarılmayabilir.

### Diğer kanıtlı eksikler

- [eu_ft.collect](C:/hibe-radari/hibe/aggregator/eu_ft.py:67) her sorguda pageNumber=1; tüm sonuçları dolaşan pagination yok. RSS yalnız son akış öğelerini, HTML sabit sayfa/öğe sınırlarını işler.
- collect_pages sayfa hash'i/first_seen/last_seen/sürüm tutmaz. Eski closed ifadesi yeni dönemin durumuna karışabilir. Sabit izleme açık çağrı onayı değildir.
- Toplayıcı koşular arası upsert/geçmiş taşımaz. Mevcut store adaptörünün varlığı bu bağlantıyı sağlamaz.
- WP-JSON, genel JSON ve JS çekicileri yok. Kaynak robots.txt/politika kontrol kaydı, Retry-After, ETag/Last-Modified/304 ve kontrollü retry yok. Üretilen sitenin robots.txt dosyası kaynak tarama koşulu kontrolü değildir.
- [web/app.js admin](C:/hibe-radari/web/app.js:157): İnceleme, belge bağlantısı, sürüm onayı, JSON calls içe aktarma ve sayılar var. Kaynak CRUD, kaynak tara, runs/sağlık geçmişi ve GrantOpportunity köprüsü yok. /api/admin 13 gerçek toplayıcı yerine sources.json'daki 30 bekleyen kaydı gösterir.
- Statik build yönetim/abonelik/API backend'i üretmez. Yerel /yonetim, canlı panelin çalıştığının kanıtı değildir.
- [.github/workflows/test.yml](C:/hibe-radari/.github/workflows/test.yml:13) testten önce requirements kurmaz. test_aggregator.py üst düzey httpx import eder. Bağımlılıksız geçici venv'de discovery exit=1; httpx ve Windows timezone verisi tzdata eksikleri ölçüldü. Bu deney GitHub runner'ının birebir taklidi değildir; temiz ortam ihtiyacını gösterir. Dependency install adımının eksikliği gerçek CI açığıdır. requirements.txt Windows timezone ihtiyacını ayrıca beyan etmiyor.
- models.today ve site.build host datetime.now gününü kullanır. generated_at zaman dilimsizken ICS damgasına Z eklenir. İstanbul günü/UTC ayrımı ve rapor günü/build günü tutarlılığı toplayıcıda doğrulanmıyor; JS İstanbul testi bu Python yolunu kapsamaz.

## 5. 127 kaynak için önerilen entegrasyon yaklaşımı

**Tek rota:** Mevcut hibe.aggregator sözleşmesini genişlet; JSON yapılandırmalarını, store adaptörlerini, domain onayını ve Lovable statik üretimini koru. Önceki Cloud Run/Firestore önerisi ilk geliştirme için zorunlu kabul edilmemeli; barındırma/zamanlama sağlam veri ve yayın yolu doğrulandıktan sonra ele alınmalı.

1. **Envanteri uzlaştır:** 135 satırı kurum/program/uç nokta olarak eşleştir; mevcut id'leri koru. 127 hedefiyle farkı görünür tut; kayıt silerek sayıyı tutturma. sources.json/aggregator.json kimlik eşlemesi kur. Sabit 30 kontrolü/metinlerini planlı genişlet; topluca ready yapma.
2. **Mevcut CONNECTORS'ı genişlet:** API/RSS → HTML → yıllık program izleme. WP-JSON/genel JSON sadece gereken kaynakta aynı Fetcher ve GrantOpportunity sözleşmesine eklenir. JS gereksinimi ölçülmedikçe tarayıcı bağımlılığı ekleme. Engel/politika sorunu manuel yol ve nedeniyle kayıtta kalır.
3. **Kaynak başına kabul kanıtı:** Gerçek küçültülmüş fixture, seçici/sayfalama, çağrı kimliği, tarih kanıtı, izinli uç nokta. Açık boş liste ile bakım/bozuk parser ayrılmalı.
4. **İlgililik/uygunluğu ayır:** Hibe, yarışma, eğitim, burs, ortak arama ve izleme türleri; ülke/başvuran koşulları kanıtla değerlendirilsin. Çevre/öğrenci bursu/eğitim kapsamı eski negatif kurallarla çelişmesin.
5. **Var olan onay yoluna köprü:** GrantOpportunity keşif kaydı; gerçek belge/hash ve başvuru yolu elde edilince calls modeline aktarılır. Eksik belge/koşul uydurulmaz. Service.approve/domain.publishable tekrar kullanılır; accept onay değildir. Sürüm değişince onay kaldırılır.
6. **Küçük doğrulanmış kaynak dilimleri:** Önce mevcut 13'ün güvenliği; sonra Ulusal Ajans/MEB/Eurodesk/SALTO ve diğer gruplar. Öncelik kapsam azaltımı değildir. Her satır bağlı/doğrulama bekliyor/engel/manuel durumuyla takip edilir.
7. **En son zamanlama/deploy:** Kalıcı doğru kayıt, onaylı üretim ve geri dönüş testlerinden sonra düzenli çalışma. İki ardışık koşu ve kaynak hatası senaryosu geçmeden sürekli güncel çalışma iddiası yapılmaz.

## 6. Mevcut sistemi bozmadan yapılacak en küçük ilk geliştirme paketi

**İlk paket: güvenli rapor ve statik çıktı kapısı.** Amaç kaynak eklemek değil, başarısız/onaysız koşunun mevcut doğru çıktıyı değiştirmesini engellemek.

- run_source raporunda tam başarı/kısmi hata/şüpheli boş ayrıştırma ayrılsın. Detay/crawl hatası sağlık bilgisine taşınsın; gerçek sıfır duyuru otomatik bozuk sayılmasın.
- CLI yazma/build öncesi kontrol etsin. Hatalı/kısmi koşu, --only sonucu veya onay şartını karşılamayan yayın adayında **son sağlam latest.json/public korunsun**. Hata ayrı koşu raporunda kalabilir; mevcut JSON formatı korunur.
- feeds.collect bakım HTML'ini başarılı boş RSS saymasın.
- Approval'sız rapordan yeni statik yayın üretimi reddedilsin. İlk pakette bulunmayan admin köprüsü varmış gibi gösterilmesin; mevcut canlı içerik kendiliğinden yeniden yayımlanmasın/silinmesin. Onaylı modele köprü sonraki ayrı dilimdir.
- Çıktı önce geçici alanda tamamlansın; başarı sonrası atomik değiştirilsin. Giriş doğrulanmadan eski dosyalar silinmesin.

**Kabul:** Doğru ilan üret; ardından kaynak hatası, bozuk akış, kısmi koşu ve approval'sız rapor dene. Son sağlam JSON/HTML/ICS byte/hash değerleri değişmemeli; açıklanabilir hata ve başarısız exit oluşmalı. Normal rapor kaydı çalışmalı; mevcut 85 Python/11 JS testi korunmalı.

Bu paket tarih/tekilleştirme/yönlendirme sorunlarını çözmüş sayılmaz; bunlar sonraki küçük paketlerdir ve toplu 127 kaynak geçişinden önce düzeltilir. Bulut kurulumu, SQL taşıması, RapidFuzz, yeni panel/deploy ilk pakete eklenmez. Kullanıcı onayı olmadan uygulanmaz.

## 7. Değiştirilmesi önerilen dosyalar

**Aşağıdakiler öneridir; değişiklik yapılmadı.**

| Dosya | Gerekçe | Dilim |
|---|---|---|
| hibe/aggregator/collector.py | Kısmi sağlık, güvenli rapor yazımı, --only ayrımı | İlk paket |
| hibe/aggregator/__main__.py | Yazma/build öncesi hata/tam snapshot kapısı | İlk paket |
| hibe/aggregator/feeds.py | Bozuk feed/HTML yanıtını ayırma | İlk paket |
| hibe/aggregator/site.py | Doğrulama/onay kapısı; geçici/atomik çıktı | İlk paket |
| tests/test_aggregator.py | Doğru çıktıyı koruma/onaysız üretim regresyonları | İlk paket |
| hibe/aggregator/net.py | Redirect öncesi izin, stream byte sınırı, politika/retry | Sonraki güvenlik dilimi |
| hibe/aggregator/textutil.py | Başlangıç/son tarih, ISO, çoklu aday belirsizliği | Tarih dilimi |
| hibe/aggregator/models.py + collector.py | Çağrı/dönem kimliği, alias ve alan/kanıt koruması | Tekilleştirme |
| hibe/aggregator/html_cards.py + eu_ft.py | Query koruma, resmî aday doğrulama, pagination | Bağlayıcı dilimi |
| config/relevance.json + relevance.py | Yeni çevre/burs/eğitim kapsamı, uygunluk ayrımı | Uygunluk |
| config/aggregator.json | Fixture kabulü geçen kaynakları eklemek | Kaynak dilimleri |
| config/sources.json + registry.py + test_registry.py | Kaynak eşlemesi/sabit 30 hedefini uzlaştırma | Envanter |
| hibe/store.py | Var olan sözleşmede gereken kayıt/koşu koruması | Ancak ihtiyaç kanıtlanırsa |
| service.py + pipeline.py + server.py + web/app.js | Onaylı modele köprü, gerçek kaynak sağlığı/yönetimi | Köprü/panel |
| .github/workflows/test.yml + requirements.txt | Temiz dependency kurulumu/Windows timezone doğrulaması | Ayrı küçük CI düzeltmesi |
| Envanter/AGGREGATOR/README/MVP belgeleri | Sayım ve iki veri akışının durumunu düzeltmek | İlgili iş sonrası |

WP-JSON/JSON bağlayıcı dosyası yalnız gerçekten gereken kaynak fixture ile doğrulandığında mevcut pakete eklenir. firebase.json, görünüm CSS'i ve SQLite şeması ilk paket için değiştirilmez.

## 8. Riskler ve gerekli testler

### Bu incelemede ölçülenler

| Kontrol | Sonuç / sınır |
|---|---|
| python -B -m unittest discover -s tests -v | **85 test OK, 7.194 s**; ağsız |
| node --test tests/test_radar.mjs | **11/11 PASS** |
| git diff --check | PASS; LF/CRLF uyarıları |
| Gerçek küçültülmüş fixture dosyaları | STGM HTML, AB JSON, ab-ilan RSS; diğerleri önemli ölçüde sentetik/MockTransport |
| Kontrollü hata deneyleri | Tarih/ISO, fazla-eksik birleşme, alan/query kaybı, boş feed başarısı, dış redirect, onaysız prepare, çıktı kaybı yeniden üretildi |
| SQLite | Şema/kind sayıları salt okunur ölçüldü |
| Hata logları | .agent/demo.stderr.log 0 byte; stdout yalnız demo adresi. server.log_message bastırılıyor; boş log hata yok kanıtı değildir |
| Toplayıcı kaynak durumları | Son raporda error alanları null; TÜSEV 0. Detay hataları öğe gerekçesinde bulunabilir |
| Repo zamanlama | Workflow push/pull_request; schedule yok. CLI'de zamanlama döngüsü yok |
| Windows Görev Zamanlayıcı | Action'ında proje yolu/modülü görünen görev bulunmadı; dış wrapper/başka makine ihtimali dışlanmış değil |
| Bulut/canlı | Bu incelemede sorgulanmadı; var/yok varsayılmadı |

Testlerin geçmesi yeni negatif senaryoların güvenli olduğu anlamına gelmez. [test_only_published_groups_leave_the_report](C:/hibe-radari/tests/test_aggregator.py:435) yalnız gürültünün çıkarılmasını kontrol eder; insan onayını kontrol etmez. Domain eski onay/eski ekran testleri toplayıcı statik yoluna uygulanmaz.

### Gerekli regresyonlar

| Risk | Test / kabul |
|---|---|
| Yanlış tarih | Başlangıç+bitiriş+etkinlik+çok aşama; ISO/eksik yıl/geçersiz tarih/saat. Başlangıç son tarih olamaz; belirsizlik görünür |
| Tekrar | Üç kaynak/alias zinciri tek çağrı; tarih/kanıt kaybolmaz |
| Yanlış birleşme | Aynı homepage fakat farklı çağrı/yıl/program/yol ayrı kalır; başlık benzerliği yeterli değildir |
| Onaysız yayın | Eksik/eskimiş approval, değişen hash, review kaydı public'e çıkamaz |
| Veri kaybı | 503/timeout/bozuk RSS/eksik tarih/--only sonrası doğru kayıt ve dosya hash'leri korunur |
| Sessiz parser | HTML RSS, bozo, seçici kaybı, bakım sayfası, JSON şema değişimi, ara crawl/detail hatası açık sağlık üretir |
| Tarama koşulu | Dış redirect öncesi duruş, özel IP, stream sınırı, 429/Retry-After, izin/bekleme koşulları |
| Türkiye/lise uygunluğu | Ülke/yaş/lisansüstü/STK/okul ortaklığı/öğretmen bireysel yol; kanıtlı üç durum |
| Yeni fırsat türleri | Çevre yarışması, öğrenci bursu, öğretmen eğitimi, geçmiş haber, ticari kurs ve iş ilanı etiketli örnekleri |
| Eksik toplama | AB ikinci/son sayfa, query ID, RSS pencere sınırı, tek sayfa hata, tam ve tekrarsız sonuç |
| Eşzamanlılık | Tarama sırasında eski sürüm onayı yanlış kalmaz; iki koşu doğru kaydı ezmez |
| Gün/ICS | İstanbul gece sınırı, UTC DTSTAMP, rapor/build günü farkı, kapanma geçişi |
| CI/genişleme | Dependency kurulmuş temiz Linux ve desteklenen Windows; her yeni kaynak fixture kabulü |

**Koruma kanıtı:** İnceleme başlangıcı main HEAD b1633069bbc986a62033848ced0926dbb7bc1bf1. Önceki değişiklikler korundu. hibe/, web/, config/, tests/, .github/ ve temel yapılandırmaların başlangıç/son SHA-256 karşılaştırmasında değişen/eklenen kod dosyası yok. Yalnız bu rapor oluşturuldu; commit/push/deploy yapılmadı.

**Sonraki tek adım:** Kullanıcı güvenli rapor/statik çıktı kapısı paketini onaylarsa yalnız o dilim uygulanır. Rapor, 127 kaynak entegrasyonu veya otomatik yayın kurulumu tamamlandı iddiası değildir.
