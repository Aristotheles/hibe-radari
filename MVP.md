# HİBE RADARI — TEK DOSYALIK MVP UYGULAMA PLANI

**Sürüm:** 1.0
**Plan tarihi:** 10 Ekim 2026
**Çalışma projesi:** `C:/hibe-radari` (Codex raporunda görülen yerel yol; bilgisayarda doğrula)
**Çalışma ilkesi:** Mevcut projeyi geliştir; ikinci toplayıcı, ikinci veritabanı veya yeni proje kurma.
**İşleyiş:** Kullanıcının güncel yetkisiyle aşamaları sırayla uygula, test et ve kaydet; rutin aşama onayı bekleme. Herhangi bir kota kalan yüzde5 veya altındaysa checkpoint/commit/push bırak; kota uygunken zamanlanmış takip sürdürsün. Gerçek hesap veya insan onayı uydurulmaz; deploy yalnız RELEASE ve yayın kapıları geçerse yapılır.
**Belgenin kullanımı:** Bu dosyayı proje köküne `MVP.md` adıyla yerleştir; Codex'e aşağıdaki **Başlatma komutu**nu ver. Bu dosya tüm işlerin tek kaynak kaydıdır.

---

## A. ÜRÜNÜN AMACI VE DEĞİŞMEZ KARARLAR

Hibe Radarı; Türkiye'deki **liseler, lise öğrencileri, öğretmenler ve okul idareleri** için Türkiye ve dünyadaki hibe, Erasmus+/proje, yarışma, burs, öğretmen eğitimi, çevre/STEM ve ortak bulma fırsatlarını toplar; resmî kaynağa bağlar; son başvuru/uygunluk şartlarını kanıt göstererek değerlendirir; aramayı ve uygun fırsata ulaşmayı kolaylaştırır.

- Kaynak listesinin **tamamı envantere alınacak**; her birine otomatik erişim sözü verilmeyecek. Erişim izni olmayan/engelli kaynaklar manuel veya izinli alternatif kaynak modunda kalacak.
- Kaynak araştırması anlatımında **127** deniyor; Codex `docs/KAYNAK_ENVANTERI.md` içinde **135 farklı URL/satır** saymış. **Sekiz satırı silme.** Kurum/program/URL düzeylerini ayrı sayıp uyuşmazlığı belgele.
- Kaynak sayısına 30 veya 127 gibi sabit limit koyma; mevcut sabit 30 kayıt denetimini kontrollü olarak kaldır/yeniden tasarla.
- **Uygunluk ≠ ilgililik.** İlgililik filtrelemesi ilk keşif sinyalidir; Türkiye'den lise/öğretmen/öğrenci başvurabilir hükmü ancak şartlardan çıkarılır.
- Doğrulanmamış son tarih ve koşullar kullanıcıya kesin bilgi olarak verilmez; `bilinmiyor` / `doğrulama gerekli` kullanılır.
- Tekilleştirme sırasında ikinci kaynağın URL'si, kanıtı, tarih güncellemesi ve çağrı dönemi kaybolmaz.
- Kaynak taraması başarısız olduğunda **son sağlam site verisi korunur**.
- İlk sürümde yönetici onayı, ilerleyen aşamada yalnız **kanıtı sağlam ve sürümü kontrol edilen** kayıtlar için kontrollü otomasyon. `accept` etiketi onay değildir.
- Mevcut teknoloji (Python + statik HTML/CSS/JS + Firebase Hosting; mevcut SQLite/Firestore adaptörleri) korunur. Yeni abonelik/giriş işlerinde Firebase Authentication kullanılabilir; ikinci backend kurulmaz.
- İzinli API/RSS/HTML önceliklidir; `robots.txt` ve kullanım koşulları denetlenir. CAPTCHA/bot koruması aşılmaz, TLS doğrulaması kapatılmaz, giriş gerektiren erişim zorlanmaz.
- Google ile giriş, yapılandırılabilir admin yetkisi, basit ücretsiz/Pro hak modeli ürün kapsamında bulunur; **gerçek ücretli tahsilat** ancak sağlayıcı, yasal gereklilikler ve webhook/doğrulama netleşince etkinleştirilir. Sahte 'ödeme başarılı' akışı kurulmaz.

### MVP'nin başarısı

1. Yeni ve eski kaynaklardan gelen ilanlar **kalıcı, doğrulanabilir** kayıtlara dönüşür; eksik/hatalı tarama doğru veriyi kaybettirmez.
2. Public sitede yalnız **onaylı ve geçerli** fırsatlar bulunur; kaynak/kanıt, tarih kesinliği ve uygunluk durumu görünür.
3. Yönetici kaynak durumunu ve onay kuyruğunu görür; sorunlu kaynakları kapatabilir.
4. Envanterdeki tüm 135 URL kayıtlıdır; otomatik toplama durumu **kaynak bazında** dürüstçe raporlanır. Hepsinin çalışır olması MVP kabul şartı **değildir**.
5. Okul odağı en yüksek kaynaklardan başlayarak **en az ilk öncelikli paket** için gerçek sayfa/fixture doğrulaması ve regresyon testi vardır.
6. Mevcut UI çalışmaya devam eder; test ve yayınlama/geri alma yolu bulunur.

---

## B. İŞE BAŞLARKEN BİLİNEN GERÇEK DURUM (Codex raporu, 9 Ekim 2026)

> Bunlar **yerel analiz** bulgularıdır. Canlı Firebase/Firestore/Auth/deploy ayrıca doğrulanmamıştır.

- `config/aggregator.json`: **13 kaynak bloğu**, RSS/AB API/HTML/sayfa izlemede altı toplama yöntemi var. Son raporda **188 çekilen**, **186 tekilleşen**, **81 public JSON kaydı** gözlenmiş. 13 blok, 13 resmî çağrı veya 13 farklı kurum demek değildir.
- `config/sources.json`: **30 kayıt, tümü `registry_pending`** (19 candidate + 11 missing). Bu, 13 kaynaklık agregatörle aynı kayıt sistemi değil.
- **İki ayrı veri hattı var:**
  1. `config/sources.json` → `hibe/pipeline.py` → `hibe/service.py` → `hibe/domain.py` → onaylı uygulama/API.
  2. `config/aggregator.json` → `hibe/aggregator/collector.py` → `latest.json` → `hibe/aggregator/site.py` → `public/` → Firebase Hosting.
- **Kritik hata 1:** Statik site hazırlığı insan onayı olmadan `accepted/review/watch/general` verisini alabiliyor.
- **Kritik hata 2:** HTTP 503/kısmi tarama/`--only` yeni snapshot'ı boşaltıp mevcut doğru site çıktısını silebiliyor.
- **Somut hatalar:** Başlangıç tarihi son tarih sanılıyor; ISO tarih kaçabiliyor; iki ayrı çağrı aynı ana sayfa bağlantısı yüzünden birleşebiliyor; URL query parametreleri atılabiliyor; bozuk RSS 0 başarılı öğe sayılıyor; redirect güvenliği istek sonrası kontrol ediliyor.
- Mevcut regresyon tabanı **85 Python + 11 JavaScript testidir** (rapor anındaki durum).

**Kaynak kodu referansları:** `hibe/aggregator/{collector.py,feeds.py,net.py,textutil.py,models.py,site.py,html_cards.py,eu_ft.py,__main__.py}`, `hibe/{service.py,domain.py,pipeline.py,store.py,server.py}`, `config/{sources.json,aggregator.json,relevance.json,profile.json}`, `web/app.js`, `tests/`, `docs/KAYNAK_ENVANTERI.md`.

---

## C. HEDEF VERİ AKIŞI

```text
Kaynak envanteri (URL / program / kurum)
    ↓ erişim yetkisi + yöntem + sağlık durumu
Mevcut connector sistemi (AB API, RSS, HTML, page_watch; gerekirse WP-JSON/genel JSON)
    ↓ ham keşif (kaynak URL + bulunan sayfa + zaman + kanıt)
Ayrıştırma / normalizasyon / tarih adayı ve kesinlik / sınıflandırma
    ↓
Çağrı kimliği + dönem + URL alias'ları üzerinden tekilleştirme
    ↓ geçmiş/upsert; eksik bilgi doğru önceki alanı silmez
İlgililik / 3 değerli uygunluk / güven ve kanıt denetimi
    ↓
Yönetici inceleme ve sürüm bağlı onay
    ↓ onaylı sürüm + geçerli veri
Staging site üretimi → test → atomik/geri alınabilir public değişimi
    ↓
Firebase Hosting, arama, filtre, takvim, kaynak linki, ücretsiz/Pro görünümü
```

**Önerilen fırsat yaşam döngüsü:** `DISCOVERED → ENRICHING → REVIEW_REQUIRED → APPROVED → PUBLISHED → ARCHIVED`; ayrıca `REJECTED`, `BLOCKED`, `FETCH_ERROR`. `FETCH_ERROR`, yayınlanmış doğru çağrıyı otomatik silmez. Bu statü adları mevcut veri modeliyle eşlenmeli, körlemesine eklenmemeli.

**Kaynak yaşam döngüsü:** `INVENTORIED → VERIFIED → CONNECTED`; ayrıca `MANUAL`, `BLOCKED`, `BROKEN`, `DISABLED`. Kaynak statüsü ile tekil çağrı statüsü farklıdır.

---

## D. AŞAMA AŞAMA UYGULAMA PLANI

### AŞAMA 0 — Temel durumu sabitle ve güvenli başlangıç yap

**İş:** `git status`, mevcut HEAD, dosya değişiklikleri, `latest.json` ve `public/` manifest/hash yedeği; 13 bağlantı, 30 bekleyen kayıt ve 135 URL sayımını karşılaştır; yerel kod/test çalıştırma komutlarını kaydet. Mevcut başlatma/deploy yöntemini öğren. Çalışan veri yolu ve canlı site aynı mı bunu ayrıca doğrulama listesine yaz.

**Dosyalar:** `docs/KAYNAK_ENVANTERI.md`, `config/*.json`, `data/aggregator/latest.json`, `public/`, `tests/`.

**Çıkış koşulu:** Geri dönülebilir referans ve test tabanı kaydedildi. Mevcut dosyalar değişmedi. Bilinmeyen canlı dağıtım 'çalışıyor' diye işaretlenmedi.

### AŞAMA 1 — Veriyi silmeyen yayın güvenlik kapısı (**ilk kod işi**)

**İş:** Kaynak toplamasında `success / partial / failed / suspicious_empty` durumlarını ayır. `--only` yalnız geçici/kısmi rapor oluştursun; ana `latest.json/public` üzerine yazmasın. Hatalı veya eksik koşu son sağlam çıktı ile merge edilmeksizin yayımlanmasın. Bozuk RSS ya da bakım HTML'i `başarılı boş feed` sayılmasın. Statik üretim, onaylı kayıt/sürüm bilgisi yoksa yeni yayını reddetsin; var olan siteyi silmesin. Staging'de dosyaları eksiksiz üret; doğrulamadan sonra kontrollü değiştir; rollback sağla.

**Dosyalar:** `aggregator/{collector.py,__main__.py,feeds.py,site.py}`, `tests/test_aggregator.py`.

**Test:** Sağlam çağrı → HTTP 503 → mevcut JSON/HTML/ICS hash'leri aynı; `--only`, bakım HTML'i, onaysız yeni kayıt için aynı. Hata exit kodu başarısız. Eski 85+11 test ve yeni testler geçer.

**Bitti demek için:** Onay köprüsü yokken otomatik yeni yayın **geçici olarak durabilir**; eski sağlam public korunuyor ve veri kaybı yok.

### AŞAMA 2 — Ağ/tarama güvenliği ve kaynak sağlığı

**İş:** Her redirect öncesi HTTPS/izinli host/port/IP kontrolü; stream olarak boyut sınırı; kaynak bazlı hız ve hata sınıflandırma; `429 Retry-After`, koşullu `ETag/Last-Modified` istekleri; 403/404 için gereksiz tekrar yok; kaynak izin durumu ve kullanıcı aracısı gerçek proje adresi/iletişimiyle güncel. TLS sertifikası sorununda **verify=False kullanma**; kaynağı hata/manual duruma al. JS/Playwright ancak gerçek ihtiyaç kanıtlanırsa, koruma aşmak için değil.

**Dosyalar:** `aggregator/net.py`, ilgili konektörler, sağlık logları ve testler.

**Test:** Dış redirect hiç istek almıyor, özel IP engelleniyor, max byte indirilmeden kesiliyor, 429 gecikme ve 304 doğru, 403/SSL doğru raporlanıyor.

### AŞAMA 3 — Tarih çıkarımı ve arşiv doğruluğu

**İş:** Orijinal kodun `norm`, `tarih_parse`, `son_basvuru_cikar` fikrini `aggregator/textutil.py` içine **işlev olarak uyarla**. Türkçe ayların 12'si; `İ/i̇`; ISO `2026-11-30`; `05.11.2026`; İngilizce/TR ay adı; çok aşamalı çağrılar; başvuru başlangıç/bitiriş ayrımı. Her son tarih: değer + `day/month/unknown` kesinlik + kaynak alıntısı/linki + doğrulama zamanı. **Yalnız ay varsa ayın 1'ini kesin son başvuru günü diye kaydetme.** Eski kesin tarihi yeni taramadaki `None` ile ezme; açık revizyonu belgeli olduğunda güncelle. Arşiv yalnız kanıtlı kapanışta veya günü kesin ve süresi geçmiş durumda; şüpheli tarihi `REVIEW_REQUIRED` olarak bırak.

**Dosyalar:** `aggregator/textutil.py`, `models.py`, gerekiyorsa `eu_ft.py`, `site.py`, testler.

**Test:** `Başvurular 1 Kasım'da başlar, son başvuru 30 Kasım'dır` → 30 Kasım. `Kasım 2026` → ay kesinliği, gün bilinmiyor. `Başvurular 05.11.2026 tarihinde kapanacaktır` → doğru. DST/UTC ve ICS testleri.

### AŞAMA 4 — Kimlik, URL ve tekilleştirmeyi güvenli hale getir

**İş:** Orijinal `canon` ve `rapidfuzz` fikrini değerlendir ama `?id=...` ve çağrı ayrımını sağlayan query'yi **asla silme**. Sadece bilinen izleme parametrelerini temizle (tüm `ref*` parametrelerini değil). Tekilleştirme anahtarı resmi çağrı ID'si + program + dönem + başvuru yolu; sonra güvenilir canonical/alias ve kanıta dayalı başlık. Aynı homepage farklı yıldaki çağrıları birleştirme. Başlık benzerliği otomatik silme gerekçesi değil, inceleme sinyali. Birleşirken yeni tarih/kanıt/kaynak listesini koru.

**Dosyalar:** `aggregator/{models.py,collector.py,html_cards.py,eu_ft.py}`, testler.

**Test:** `/call?id=1` ve `?id=2` ayrı; 2026/2027 çağrıları ayrı; aynı çağrı 3 kaynakla bir tane; daha güçlü son tarih bilgisi kaybolmaz; alias zinciri çalışır.

### AŞAMA 5 — Kalıcı keşif kaydı + gerçek yönetici onay köprüsü

**İş:** Statik toplayıcı `GrantOpportunity` ile mevcut onaylı uygulama `calls` modelini belge/kanıt/sürüm açısından eşleştir. Mevcut `store.py`, `Service.approve`, `domain.publishable` kullan. `latest.json` tek kalıcı veri kaynağı olmasın. Onay değişen içeriğin hash/sürümüne bağlansın; eski onay, yeni değişen önemli koşulu otomatik onaylamasın. Yönetici panelinde gerçek agregatör fırsat kuyruğu olsun. Yayımlama yalnız bu köprüden doğrulanmış sürümleri alsın.

**Dosyalar:** `aggregator/collector.py`, `service.py`, `pipeline.py`, `domain.py`, `store.py` (gerekirse), `server.py`, `web/app.js`, testler.

**Test:** Onaysız/eskimiş/onayı geri çekilmiş çağrı public'e çıkamaz. Yönetici onayladığında tam metin kopyalamadan kısa özgün açıklama + kanıt + resmî URL yayımlanır. Yeniden tarama silme yapmaz.

### AŞAMA 6 — İlgililik, uygunluk ve AI denetimi

**İş:** `RelevanceFilter` keşif/öncelik sinyalini üretmeye devam etsin. Ek uygunluk motoru: `UYGUN / UYGUN_DEĞİL / DOĞRULAMA_GEREKLİ`. Ayrı hedefler: Türk devlet lisesi/okul, öğretmen, 14–18 yaş lise öğrencisi, okulun ortağı olabileceği proje, okul dışı başvurucu isteyen fonlar. Burs, yarışma, öğretmen kursu, AB proje çağrısı, ortak bulma, yıllık program farklı fırsat türleri. Ülke, kurum türü, yaş, ortak zorunluluğu, başvuru yolu ve tarih için **kanıt + kontrol zamanı**. `gemini-3.8-flash` mevcut yapılandırmadaki doğrulanmış model adına göre kullanılsın; model çalışmazsa kurallı `doğrulama gerekli` yolu olsun. Model kesin kaynaksız karar üretmesin; riskli/çelişkili çağrı editöre gitsin.

**Dosyalar:** `aggregator/relevance.py`, `config/relevance.json`, mevcut eligibility ve LLM modülleri, testler.

**Test:** Lise çevre yarışması yanlış dışlanmaz; üniversiteye özel burs lise uygun olmaz; NGO-only fon lise adına kesin uygun denmez; belirsizlik görünür. 186 kaydın 5'i uygun diye rastgele çoğaltılmaz.

### AŞAMA 7 — 135 URL'lik kaynak kayıt sistemi ve yönetici sağlık paneli

**İş:** `docs/KAYNAK_ENVANTERI.md` kaynaklarını **tamamını**, tekil URL kaydı + kurum + program hiyerarşisine aktar. 127 ile 135 farkını açıklayan sayım raporu üret. `sources.json` (registry) ve `aggregator.json` (çalışan çekici) kimliklerini eşleştir, ama dosyaları körlemesine birleştirme. `registry.py` sabit 30 şartını testlerle birlikte yenile. Kaynak adı, ülke, grup, URL, connector, erişim/politika, son başarı/hata, son bulunan kayıt, değişiklik izleme, periyot ve aktif/manual/engel durumu saklanır. Yönetici panelinden kaynaklar görülebilir, yetkili tarafından açılıp kapatılabilir; başarısız tarama alarmı var.

**Dosyalar:** `docs/KAYNAK_ENVANTERI.md`, `config/{sources.json,aggregator.json}`, `hibe/registry.py`, uygun store ve admin dosyaları, testler.

**Test:** Envanter satırları kaybolmaz; 13 mevcut connector aynı kimlikle kalır; 135 kayıt entegre edildi diye 135'ine de `connected` denmez; bozuk kaynak sağlık ekranında görünür.

### AŞAMA 8 — Kaynak bağlama: okula yakın olandan başlayan testli dilimler

**İlk paket:** Türkiye Ulusal Ajansı; MEB'in ilgili genel müdürlük duyuruları (ayrı kaynaklar); Eurodesk Türkiye/Opportunity Finder; SALTO takvim; Terra Viva Grants. Her adres için **gerçek izin/erişim ve sayfa şeması doğrulaması**; otomatik yola uygun olanları bağla; diğerlerini manuel takipte bırak.

**Devam paketleri:** TÜBİTAK (mevcut akışın kapsamını tamamla), TEKNOFEST, DOKA/diğer kalkınma ajansları, EACEA, Erasmus+ platformları, Code Week/eTwinning, okul ve öğretmen odaklı ödüller → diğer vakıflar/elçilikler/BM → yıllık program sayfası izleme → derleme siteleri yalnız asıl kaynağa işaret ederek. Kaynak bağlanacaksa mevcut `CONNECTORS` genişletilir: WP-JSON/genel JSON yalnız gerekli site kanıtlanınca; baştan Playwright yığını ekleme.

**Her kaynak için kabul kartı:** Kimlik + resmî URL + erişim izni/politika + seçilen yöntem + liste/detay sayfası fixture'ı + örnek çağrı ve tarih/kanıt + aynı çağrı tekrar testi + boş/hata davranışı + güncelleme sıklığı.

**Test:** 13 mevcut kaynak gerilemez; yeni kaynağın en az bir gerçek fixture'ı vardır; açık çağrı bulunmadığında `0 ilan` ile `parser bozuk` ayrıdır. Bağlanamayan kaynak gizlenmez, sebebiyle görünür.

### AŞAMA 9 — Kullanıcı deneyimi, yönetici paneli ve üyelik çekirdeği

**İş:** Mevcut Lovable tasarımını koru; liste/arama/kategori/uygunluk filitresi, kaynak ve son doğrulama bilgisi, takvim/ICS, kapanan çağrının doğru durumu. Yönetici: inceleme kuyruğu, kaynak sağlığı, tekilleştirme eşleşmeleri, onay sürümleri. Google OAuth/Firebase Auth; admin kullanıcı kimliği yapılandırma ve yetki kontrolünden gelsin (e-posta görünmesi tek başına yetki verme kriteri değil). Ücretsiz/Pro özellik hakları backend'de kontrol edilsin; üyelik büyüme metrikleri minimal. Tahsilat üretime açılmadan önce gerçek sağlayıcı + webhook + iptal/iade/sözleşme/gizlilik akışı ayrıca test edilsin.

**Test:** Yetkisiz kullanıcı admin işlemi yapamaz; ücretsiz kullanıcı backend Pro uçlarını aşamaz; kaynak/son tarih bilgileri mobil ve masaüstünde anlaşılır.

### AŞAMA 10 — Pilot, zamanlama, canlıya alma ve geri dönüş

**İş:** Önce staging: iki ardışık başarılı tam toplama, bir HTTP hata, bir bozuk RSS, bir `--only` denemesi; onay ve yayın sürümü korunur. Kaynak başına uygun günlük/haftalık periyot; aşırı trafik yok. Zamanlama yöntemi mevcut projeye ve barındırmaya göre seçilsin. Firebase Hosting canlı deploy yalnız kullanıcı onayıyla. Deployment öncesi yedek/manifest, sonrası public JSON-kart sayısı kontrolü ve geri alma prosedürü. Geçen son başvurular kanıtlı statüyle arşivlensin.

**Test:** Doğru yayın → kaynak geçici hata → doğru yayın korunur; rollback pratikte denenir. 85 Python + 11 JS temel testinin güncel tam karşılıkları ve yeni regresyonlar geçer. Gerçek Auth/Firestore/SMTP ve abonelik testleri ancak altyapı erişimiyle çalıştırılıp raporlanır.

---

## E. HER AŞAMANIN ORTAK KABUL VE RAPOR KURALI

Her aşamanın sonunda Codex yalnız şu raporu verir:

1. **Ne uygulandı?** (dosya + fonksiyon + özet)
2. **Ne test edildi?** (komut ve PASS/FAIL sayısı)
3. **Ne kanıtlandı, ne doğrulanamadı?** (canlı/yerel ayrımı)
4. **Son sağlam veri/yayın korunuyor mu?** (hash/fixture açıklaması)
5. **Risk ve geri alma adımı nedir?**
6. **Sıradaki aşama hangisi?** (doğrulama kanıtından sonra sırayla devam; rutin yeni onay gerekmez)

**Her aşamadan önce:** `git diff` ve çalışma ağacı kontrolü; kullanıcı değişikliklerini silme. **Her aşamadan sonra:** `git diff --check`, ilgili testler, test sonuç kaydı. Kullanıcı bitiş/duruş öncesi commit/push ve güvenli deploy yetkilendirdi; deploy yalnız gerçek yayın/onay/veri koruma ve RELEASE kabulü geçerse yapılır. Main merge ve Cloud geliştirme yapılmaz. Kaynak bağlarken yalnız gerçekten doğrulanmış statü kullan. Kod karmaşıksa küçült; gereksiz mimari ekleme.

---

## F. BENİM VERDİĞİM PYTHON KODUNUN MEVCUT PROJEYE ENTEGRASYON PLANI

**Önemli:** Aşağıdaki `core.py`, kullanıcının verdiği **orijinal referans kodudur**; üretim için olduğu gibi kopyalanmamalıdır. Hataları ve güvenlik/uygunluk eksikleri bilerek işaretlenmiş bir kaynak taslaktır. Mevcut Hibe Radarı'nın ikinci veri yolu, `duyurular.db` ve ikinci JSON API'si oluşturulmayacaktır.

| Referans kod parçaları | Mevcut projede karşılığı / uygulanacak dönüşüm | Aşama |
|---|---|---|
| `UA`, `http_get` | `aggregator/net.py` Fetcher; güvenli redirect, stream, 429/304, TLS doğrulaması açık | 2 |
| `canon` | `aggregator/models.py` canonical URL + `html_cards.py`; çağrı kimliği taşıyan query korunur | 4 |
| `norm`, `AY`, `TARIH`, `tarih_parse`, `son_basvuru_cikar` | `aggregator/textutil.py`; Türkçe aylar, ISO, belirsiz tarih, başlangıç/son ayrımı | 3 |
| `KURALLAR`, `etiketle` | `aggregator/relevance.py` + ayrı 3 değerli eligibility; yalnız etiket uygunluk kanıtı değildir | 6 |
| `_html_parse`, `cek_html` | Mevcut `html_list/html_cards/html_crawl` bağlayıcıları; test fixtur'ları | 8 |
| `cek_rss` | Mevcut `feeds.collect`; bozuk feed/ETag/Last-Modified ekle | 1–2 |
| `cek_wpjson`, `cek_json` | Mevcut `CONNECTORS` içine ihtiyaç kanıtlanınca WP-JSON/genel JSON bağlayıcı | 8 |
| `cek_js` | Playwright yalnız meşru erişim ve teknik ihtiyaç kanıtlanınca | 8 |
| `SCHEMA`, `db` | **Yeni `duyurular.db` kurma**; mevcut `store.py` kayıt sözleşmesini genişlet | 5 |
| `kaydet` | Mevcut `collector.dedupe` + kalıcı upsert + alias/kanıt + sürüme bağlı onay | 4–5 |
| `main.py` / APScheduler / `arsivle` | Mevcut aggregator CLI, tam snapshot geçidi, koşu sağlığı, tarih kesinliğine göre arşivleme | 1,3,10 |
| `api.py` / FastAPI | Mevcut `server.py` ve statik `public/data.json`; **ikinci API başlatma** | 5,9 |
| `kesif.py` | Kaynak keşif aracı olabilir; mevcut izin/host/rate-limit kontrollerinden geçmeli | 7–8 |
| 2. belgedeki `detay_tamamla` | Detay kuyruğuna limit, per-domain hız, retry/backoff; geçici hata üzerine kalıcı `denendi` yazma | 3,8 |
| 2. belgedeki `verify=False` | **KESİNLİKLE UYGULAMA**: TLS doğrulamasını kapatmak çözüm değildir | — |
| 2. belgedeki başlangıçta tanımlı `KESME` | İstek sırasında UTC `now - 48 hours` hesapla; başlangıçta donmuş cutoff kullanma | 9 |

### Asgari referans veri alanları

`source_id`, `source_url`, `canonical_url`, `official_application_url`, `external_call_id`, `programme`, `call_year/period`, `title`, `summary_own`, `published_at`, `deadline_value`, `deadline_precision`, `deadline_evidence`, `eligibility_status`, `eligibility_evidence`, `review_status`, `approval_version`, `first_seen`, `last_seen`, `last_verified_at`, `source_health`, `source_aliases`, `content_hash`. Bunlar **hedef alanlardır**, mevcut modelde bulunmayanlar doğrulamadan sonra ve en az şema değişikliğiyle eklenir.

### Özellikle uygulanmayacak örüntüler

- `otomatik_yayin=True` varsayılanı.
- Ay bilgisi geldiğinde son gün kesinmiş gibi `YYYY-MM-01` saklamak.
- Kaybolan son başvuru alanını `None` ile ezmek.
- `fuzz.ratio >= 92` olan farklı çağrıları silmek.
- `urlsplit` ile çağrı ID'si taşıyan query'yi atmak.
- Tüm SSL sertifika hatalarında `verify=False` kullanmak veya uyarıları bastırmak.
- Statik yayın için mevcut onaylı hizmeti atlayıp yeni SQLite/FastAPI hattı kurmak.

---

## G. CODEX BAŞLATMA KOMUTU (TEK KOMUT)

> Codex Desktop'ta mevcut `C:/hibe-radari` projesini aç. Bu dosyayı kökte `MVP.md` olarak kaydet. Aşağıdaki komutu bir kez ver; daha sonra yalnızca `AŞAMA N'e geç` demen yeterli.

```text
Bu projenin tek uygulama planı kökteki MVP.md dosyasıdır.
MVP.md dosyasının A–H bölümlerini ve eklenmiş referans Python kodunu oku.
Mevcut projeyi ikinci bir toplayıcı ya da veritabanıyla değiştirme.
Aşamaları 0'dan 10'a kesin sırayla, TEK TEK uygula.
Her aşamada önce kapsamı göster, sonra yalnız o aşamanın kodunu değiştir,
sonra regresyon testlerini çalıştır ve MVP.md'deki kabul koşullarına göre rapor ver.
Ben 'devam' demeden sonraki aşamaya geçme.
Her aşama sonunda MVP.md'nin 'İLERLEME KAYDI' bölümünü güncelle,
uygulanan değişiklikler ile test sonuçlarını tarihle, kaynak ve yayın durumunu kaydet.
Önceden yapılmış işleri yeniden yapma; dosyadan doğrula.
Kullanıcı değişikliklerini silme; commit/push/deploy yapma.
İlk görev: AŞAMA 0'ı uygula; bitince dur.
```

---

## H. İLERLEME KAYDI (AJAN DEVİR NOKTASI)

**Son tamamlanan aşama:** AŞAMA 0 — TAMAMLANDI (2026-10-10 00:42 Europe/Istanbul).
**Son doğrulanmış test tabanı:** 85 Python OK (6.692 s), 11 JavaScript PASS; 3 JS syntax PASS. Testler Codex tarafından 10 Ekim 2026 tarihinde yeniden çalıştırıldı.
**Mevcut öncelik:** AŞAMA 1 — Veriyi silmeyen yayın güvenlik kapısı; kullanıcı onayı bekleniyor, başlanmadı.
**Canlı deploy durumu:** Bu aşamada doğrulanmadı; deploy/tarama/gerçek hizmet bağlantısı yapılmadı.
**Son commit:** b1633069bbc986a62033848ced0926dbb7bc1bf1; commit oluşturulmadı, çalışma ağacı mevcut değişiklikleri içeriyor.
**Açık sorular:** 127 anlatımı ile 135 benzersiz URL/etiket; 131 farklı hostname kurum sayısı değildir. Kurum/program kimlik eşlemesi AŞAMA 7'de doğrulanacak. Yerel onaylı API ile statik toplayıcı farklı akışlar; canlı dosya eşliği/gerçek giriş ayrıca doğrulanmalı.
**Devralan ajan için ilk iş:** Bu kaydı, docs/ASAMA_0_REFERANS.md ve HANDOFF'u oku. AŞAMA 1'e yalnız kullanıcı onayıyla geç.

### AŞAMA 0 sonuç kaydı

[AŞAMA 0] [2026-10-10 00:42 İstanbul]
Durum: TAMAMLANDI
Değişen dosyalar: MVP.md (verilen yeni plan ve bu ilerleme kaydı), docs/ASAMA_0_REFERANS.md; yerel .agent yedek/kanıt/devir ve Obsidian kayıtları. Uygulama kodu, config, tests, latest.json, public ve önceki kullanıcı dosyaları değişmedi.
Çalıştırılan testler: python -B -m unittest discover -s tests -v; node --test tests/test_radar.mjs; node --check web/app.js, web/views.mjs, web/decision.mjs; git diff --check.
PASS / FAIL: 85 Python/0 hata; 11 JS/0 hata; 3 syntax PASS. İlk diff-check yeni belgedeki satır sonu boşluklarını buldu; temizlendi ve kapanışta tekrar ölçüldü (kanıt: yedek klasöründeki diff-check.final logları).
Son sağlam rapor/public hash: latest.json SHA-256 41bdccb3be3cf55dcf14d56de2d99a295ecfc3a67f2345fb7af8e4a3198e1362; public/data.json SHA-256 9501b4d93f7f65bc4cfb605030b719bb791095570b4df5d2ea52d245d2cae52f; 126 dosyalık public manifest SHA-256 0322b72d91b7902986502df6439a3f4beecc6d7c24f1ac97bd83883255be39b5.
Yedek: C:/hibe-radari/.agent/backups/stage0-20261010-003950 (201 dosya; snapshot ve manifest.before.json). Eski kök MVP snapshot/MVP.md ve MVP.previous.md; verilen özgün plan HIBE_RADARI_MVP.incoming.md olarak korundu.
Doğrulanamayanlar: Canlı eşlik, gerçek kaynak/ülke/çağrı uygunluğu, Auth/Firestore/Gemini/SMTP, gerçek deploy/rollback. Mevcut public fotoğrafı korunmuştur; insan onayı/geçerli çağrı kabulü sayılmaz.
Geri alma: manifest.before.json'daki gereken dosyayı snapshot içinden aynı proje yoluna kopyala, SHA-256 ile doğrula; toplu git reset/clean kullanma. Sonraki düzenlemeleri koru. Canlı rollback denenmedi.
Sonraki önerilen tek adım: AŞAMA 1 (onay bekliyor).

### Doldurulacak kayıt şablonu

```text
[AŞAMA ...] [tarih/saat İstanbul]
Durum: BEKLİYOR / DEVAM EDİYOR / TAMAMLANDI / BLOKE
Değişen dosyalar:
Çalıştırılan testler:
PASS / FAIL:
Son sağlam rapor/public hash:
Doğrulanamayanlar:
Geri alma:
Sonraki önerilen tek adım:
```

---

## EK 1 — KULLANICININ ORİJİNAL `core.py` TASLAĞI (REFERANS; DOĞRUDAN ÇALIŞTIRMA)

Aşağıdaki kod, konuşmada paylaşılan **çekiciler, normalizasyon, tarih, etiketleme, SQLite ve `kaydet`** bölümünü kapsar. Hatalarını gidermeden projeye kopyalama. Orijinal metne sadık kalınmıştır; gerçek site ve kullanıcı-aracısı adresi yer tutucudur.

```python
import hashlib, os, re, sqlite3, time, unicodedata
from datetime import date, datetime
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode
import feedparser, requests, yaml
from bs4 import BeautifulSoup
from rapidfuzz import fuzz

UA  = {"User-Agent": "OkulDuyuruToplayici/1.0 (+https://siteniz.edu.tr; iletisim@siteniz.edu.tr)"}
DB  = "duyurular.db"

# ---------------- ağ ----------------
def http_get(url, **kw):
    hata = None
    for i in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=30, **kw)
            if r.status_code == 200: return r
            hata = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            hata = repr(e)
        time.sleep(3 * (i + 1))
    raise RuntimeError(f"alınamadı: {url} ({hata})")

# ---------------- yardımcılar ----------------
def canon(url):
    """utm/fbclid temizle, trailing slash normalize → tekilleştirme anahtarı"""
    s = urlsplit(url.strip())
    q = [(k, v) for k, v in parse_qsl(s.query) if not k.lower().startswith(("utm_", "fbclid", "gclid", "ref"))]
    return urlunsplit((s.scheme.lower(), s.netloc.lower(), s.path.rstrip("/") or "/", urlencode(q), ""))

def norm(t):
    t = unicodedata.normalize("NFKC", t or "").lower().replace("ı", "i").replace("İ", "i")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip()

AY = {"ocak":1,"şubat":2,"mart":3,"nisan":4,"mayıs":5,"haziran":6,"temmuz":7,
      "ağustos":8,"eylül":9,"ekim":10,"kasım":11,"aralık":12,
      "january":1,"february":2,"march":3,"april":4,"may":5,"june":6,"july":7,
      "august":8,"september":9,"october":10,"november":11,"december":12}
TARIH   = re.compile(r"(\d{1,2})\s*[.\-/]\s*(\d{1,2})\s*[.\-/]\s*(\d{2,4})")  # TR: gg.aa.yyyy
ANAHTAR = ["son başvuru","başvuru tarihi","başvuru son","son tarih","kapanış",
           "son gün","deadline","application deadline"]

def tarih_parse(s):
    if not s: return None
    s = norm(s)
    m = TARIH.search(s)
    if m:
        g, a, y = map(int, m.groups()); y += 2000 if y < 100 else 0
        try: return date(y, a, g)
        except ValueError: pass
    m = re.search(r"(\d{1,2})?\s*([a-zçğıöşü]+)\s+(\d{4})", s)   # "15 Ocak 2026" / "Ocak 2026"
    if m and m.group(2) in AY:
        return date(int(m.group(3)), AY[m.group(2)], int(m.group(1) or 1))
    return None

def son_basvuru_cikar(metin):
    """(date|None, kesinlik) — kesinlik: 'gun' | ''"""
    t = norm(metin)
    for a in ANAHTAR:
        i = t.find(a)
        if i >= 0:
            d = tarih_parse(t[i:i + 160])
            if d: return d, "gun"
    return (None, "")

KURALLAR = {
    "erasmus-okul":  ["ka1","ka2","okul eğitimi","school education","akreditasyon","accreditation"],
    "genclik":       ["gençlik","youth","dayanışma","solidarity","esc"],
    "cevre-iklim":   ["çevre","iklim","climate","environment","sürdürülebilir"],
    "dijital-stem":  ["kodlama","stem","robotik","dijital","digital"],
    "hibe":          ["hibe","grant","çağrı","call for proposals"],
}
def etiketle(metin):
    t = norm(metin)
    return sorted({k for k, ws in KURALLAR.items() if any(w in t for w in ws)})

# ---------------- çekiciler ----------------
def _html_parse(k, html, base):
    soup, out = BeautifulSoup(html, "lxml"), []
    for n in soup.select(k["item"]):
        a = n.select_one(k.get("link") or "a[href]")
        if not a: continue
        out.append({"baslik": a.get_text(" ", strip=True),
                    "url": urljoin(base, a.get("href", "")),
                    "tarih": n.select_one(k["tarih"]).get_text(" ", strip=True) if k.get("tarih") and n.select_one(k["tarih"]) else "",
                    "ozet":  n.select_one(k["ozet"]).get_text(" ", strip=True) if k.get("ozet") and n.select_one(k["ozet"]) else ""})
    return out

def cek_rss(k):
    d = feedparser.parse(k.get("feed") or k["liste_url"], request_headers=UA)
    return [{"baslik": e.get("title",""), "url": e.get("link",""),
             "tarih": e.get("published","") or e.get("updated",""), "ozet": e.get("summary","")} for e in d.entries]

def cek_wpjson(k):
    r = http_get(k["base"].rstrip("/") + "/wp-json/wp/v2/posts", params={"per_page": k.get("adet", 20)})
    return [{"baslik": p["title"]["rendered"], "url": p["link"],
             "tarih": p.get("date_gmt") or p.get("date",""),
             "ozet": p.get("excerpt",{}).get("rendered","")} for p in r.json()]

def cek_html(k):
    r = http_get(k["liste_url"])
    return _html_parse(k, r.text, r.url)

def cek_js(k):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(user_agent=UA["User-Agent"])
        pg.goto(k["liste_url"], wait_until="networkidle", timeout=60_000)
        html = pg.content(); b.close()
    return _html_parse(k, html, k["liste_url"])

def cek_json(k):
    veri = http_get(k["liste_url"]).json()
    for y in filter(None, k.get("yol","").split(".")): veri = veri[y]
    a = k.get("alanlar", {})
    return [{"baslik": d[a.get("baslik","title")], "url": d[a.get("url","url")],
             "tarih": d.get(a.get("tarih",""),""), "ozet": d.get(a.get("ozet",""),"")} for d in veri]

CEKICILER = {"rss": cek_rss, "wp-json": cek_wpjson, "html": cek_html, "js": cek_js, "json": cek_json}

# ---------------- veritabanı ----------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS duyuru(
  id INTEGER PRIMARY KEY, kaynak TEXT, baslik TEXT, url TEXT UNIQUE, ozet TEXT,
  kaynak_tarihi TEXT, son_basvuru TEXT, sb_kesinlik TEXT, etiketler TEXT,
  durum TEXT DEFAULT 'yayinda',            -- yayinda | onay | arsiv
  ilk_gorulme TEXT, son_kontrol TEXT, aktarildi INTEGER DEFAULT 0);
CREATE INDEX IF NOT EXISTS ix_ilk ON duyuru(ilk_gorulme);
CREATE TABLE IF NOT EXISTS kaynak_log(
  id INTEGER PRIMARY KEY, kaynak TEXT, zaman TEXT, ok INTEGER, mesaj TEXT, adet INTEGER);
"""
def db():
    c = sqlite3.connect(DB, timeout=30); c.row_factory = sqlite3.Row
    c.executescript(SCHEMA); return c

def kaydet(conn, k, ogeler):
    yeni = guncel = es = 0
    simdi = datetime.utcnow().isoformat(" ", "seconds")
    for o in ogeler:
        url = canon(o.get("url",""))
        if not url.startswith("http") or not norm(o.get("baslik")): continue
        bn  = norm(o["baslik"])[:180]
        met = f"{o['baslik']} {o.get('ozet','')}"
        sb, kes = son_basvuru_cikar(met)
        et = ",".join(etiketle(met))
        satir = conn.execute("SELECT id FROM duyuru WHERE url=?", (url,)).fetchone()
        if satir:   # aynı duyuru → deadline uzatıldıysa güncellenir
            conn.execute("UPDATE duyuru SET baslik=?, ozet=?, son_basvuru=?, sb_kesinlik=?, etiketler=?, son_kontrol=? WHERE id=?",
                         (o["baslik"], o.get("ozet",""), sb.isoformat() if sb else None, kes, et, simdi, satir["id"]))
            guncel += 1; continue
        cift = [r["id"] for r in conn.execute(                      # bulanık tekilleştirme
                 "SELECT id, baslik FROM duyuru WHERE ilk_gorulme > datetime('now','-120 day')")
               if fuzz.ratio(norm(r["baslik"]), bn) >= 92]
        if cift: es += 1; continue
        conn.execute("INSERT INTO duyuru(kaynak,baslik,url,ozet,kaynak_tarihi,son_basvuru,sb_kesinlik,"
                     "etiketler,durum,ilk_gorulme,son_kontrol) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                     (k["id"], o["baslik"], url, o.get("ozet",""), o.get("tarih","") or simdi,
                      sb.isoformat() if sb else None, kes, et,
                      "yayinda" if k.get("otomatik_yayin", True) else "onay", simdi, simdi))
        yeni += 1
    conn.commit()
    return yeni, guncel, es
```

## EK 2 — İLK TASLAKTAKİ DİĞER KODLARIN TAŞINMASI

İlk taslakta `kesif.py`, `sources.yaml`, `main.py` (APScheduler + Telegram uyarısı + arşiv), `api.py` (FastAPI) ve 5 deneme kaynağı da bulunuyordu. **İşlevlerinin hiçbiri kaybolmuyor**; F bölümündeki eşleme ile mevcut projeye taşınacak. Ancak aynı işlevlerin ikinci bağımsız sürümlerini kurmak **yasak**. İlk taslağın `main.py`'sindeki 2 saatlik döngü veya `api.py`'sindeki yeni FastAPI, mevcut sistemde eşdeğeri varsa kurulmayacak.

İkinci taslak düzeltmelerinden güvenli kabul edilen fikirler: tam tutarlı Türkçe normalizasyon, gün/ay kesinliği, ayrık detay tarama, UTC farkındalığı ve arşivde belirsizlik koruması. **Reddedilen veya düzeltilecek** öneriler: `urllib3.disable_warnings`/`verify=False`, geçici HTTP hata sonrası sonsuz `detay_denendi=1`, uygulama başlatılışında bir defa hesaplanmış 48 saat sınırı ve şartları kanıtlamadan otomatik yayın.

## EK 3 — REFERANS TEST ÖRNEKLERİ (EN AZINDAN BUNLAR)

```text
T1: Başvuru 1 Kasım 2026'da başlar, son başvuru 30 Kasım 2026 → deadline=30 Kasım.
T2: Son başvuru: Kasım 2026 → month precision, gerçek gün bilinmiyor; erken arşiv yok.
T3: Application deadline: 30 November 2026 → gün kesinliği.
T4: Başvurular 05.11.2026 tarihinde kapanacaktır → son gün 5 Kasım.
T5: /call?id=1 vs /call?id=2 → iki ayrı çağrı.
T6: Aynı resmî homepage'e bağlanan 2026/2027 çağrıları → iki ayrı çağrı.
T7: Aynı çağrı üç kaynaktan → tek kart, üç kaynak/kanıt.
T8: Eski kayıt deadline=2026-11-30, yeni çekim deadline=None → tarih korunur.
T9: Sağlam public ardından kaynak 503 → sağlam HTML/JSON/ICS hash korunur.
T10: --only → ana tam snapshot değişmez.
T11: Bozuk feed (HTTP 200, HTML bakım sayfası) → sağlıklı 0 kayıt sayılmaz.
T12: Onaysız / eski sürüm onaylı çağrı → public'e giremez.
T13: İzinli hosttan dış hosta redirect → dış hosta istek yapılmaz.
T14: TLS sertifika hatası → engel/hata; SSL verify kapatılmaz.
T15: Üniversite bursu vs lise bursu; yalnız STK hibesinde uygunluk → kanıtlı karar.
T16: Kaynak 135 URL kayıtlı; 13 mevcut entegrasyonun kimliği ve çalışması korunur.
T17: İstanbul 00:10 / UTC önceki gün → son gün/yeni rozet/ICS doğru.
T18: Google girişli normal kullanıcı admin işlemi yapamaz; Pro yetkisi backend'de denetlenir.
```

**Bitiş ölçütü:** Kod, API ve paneldeki durumlar gerçeği söyleyene; çalışan tüm çekiciler testle doğrulanana; son sağlam veri korunan, onaylı çağrı yayını sağlanana kadar projeyi 'tamamlandı' diye işaretleme.


### 2026-10-10 01:10 — Yerel AŞAMA 1 ilerleme eki
Yayın kapısı ve veri koruma uygulandı; 94 Python + 11 JS PASS. docs/ASAMA_1_YAYIN_GUVENLIGI.md kanıt ve sınırlardır. Cloud durdu; çalışma yalnız C:/hibe-radari içinde. Kullanıcı aşama başına onay beklemeyi kaldırdı. Sıradaki AŞAMA 2. Deploy onaylı veri olmadığı için yapılmadı.


### 2026-10-10 — Yerel AŞAMA 2 tamamlandı
105 Python + 11 JS PASS; ağ/robots/izin/kalıcı önbellek/sağlık kontrolleri uygulandı. Kaynaklar izin incelemesine kadar unreviewed; canlı başarı iddiası yok. Kanıt docs/ASAMA_2_AG_GUVENLIGI.md. Sıradaki AŞAMA 3; kullanıcı onayı beklenmez.


### 2026-10-10 — Yerel AŞAMA 3 tamamlandı
119 Python + 11 JS PASS; tarih kesinliği/kanıt/revizyon, başlangıç-bitiriş, belirsiz tarih takvim engeli ve UTC uygulandı. 127 public/latest dosyası değişmedi. Rapor docs/ASAMA_3_TARIH_GUVENLIGI.md. Sıradaki AŞAMA 4; kullanıcı onayı beklenmez.


### 2026-10-10 — Yerel AŞAMA 4 tamamlandı
128 Python + 11 JS PASS; query/çağrı kimliği, güvenli alias zinciri, dönem ayrımı, kanıt koruma ve çelişki incelemesi uygulandı. 127 public/latest dosyası aynı. Rapor docs/ASAMA_4_KIMLIK_GUVENLIGI.md. AŞAMA 5 yerelde devam; onay beklenmez.


### 2026-10-10 — AŞAMA 5 tamamlandı
136 Python + 11 JS PASS; kalıcı keşif, eski kayıt koruma, sürüme bağlı Service onayı/geri çekme, gerçek statik yayın köprüsü ve yönetici kuyruğu uygulandı. 127 public/latest dosyası değişmedi. Kanıt docs/ASAMA_5_KESIF_ONAY_KOPRUSU.md. AŞAMA 6 yerelde devam; aşama onayı beklenmez.


### 2026-10-10 — AŞAMA 6 özellikleri doğrulandı
147 Python + 11 JS PASS; hedef bazlı üç değerli uygunluk ve AI kanıt/fallback denetimi uygulandı. Canlı Gemini anahtarı yok; model erişim başarısı iddia edilmez. 127 public/latest dosyası aynı. Rapor docs/ASAMA_6_UYGUNLUK_GUVENLIGI.md. AŞAMA 7 yerelde devam.


### 2026-10-10 — AŞAMA 7 kayıt/sağlık özellikleri doğrulandı
152 Python + 11 JS PASS. 135 envanter URL'si + 19 korunan eski kayıt = 154 kayıt; eski 30 ID ve 13 çekici korundu. Sabit 30 denetimi yenilendi; yetkili kaynak açma-kapama/sağlık alarmı mevcut store'a bağlı. 131 host grubu kurum sayısı değildir; bilinmeyen kurum/ülke alanları açık. Raporlar docs/ASAMA_7_KAYNAK_KAYDI.md ve docs/KAYNAK_SAYIM_UZLASTIRMA.md. AŞAMA 8 canlı kabul kartlarıyla devam; onay beklenmez.


### 2026-10-10 — AŞAMA 8 aktif, ilk iki RSS dilimi doğrulandı
MEB abdigm/yegitek resmî RSS akışları strict gerçek istemciyle 200/rss20/50 kayıt; iki kısa gözlem fixture'ı ve hata/tekilleştirme regresyonları. 157 Python OK (11.509 s) + 11 JS PASS; syntax/diff-check temiz; 127 public/latest dosyası aynı. Mevcut 13 ID korunuyor, toplam 15 çekici. Kabul kartı 135; gözlemli 10, detay/tarih ve devam paketleri açık. SALTO ticari dağıtım izni gerektiriyor; Eurodesk robots 200 HTML hata sayfası. net.py robots HTML/wildcard/encoded-query regresyonları düzeltildi. AŞAMA 8 bitmedi, AŞAMA 9'a geçilmedi; yerelde devam. Kanıt docs/ASAMA_8_CANLI_KABUL_ILERLEME.md / config/source_acceptance.json.


## 2026-10-10 — AŞAMA 8 dört MEB kaynağı
OGM ve Meslekî Teknik Eğitim RSS'leri gerçek istemcide 200/rss20/50 kayıt; mevcut feed çekicisine meb-ogm/meb-mtegm olarak eklendi. Toplam 17 yapılandırma, başlangıçtaki 13 ID korunur. OGM GençBizz gerçek ayrıntı URL'sinden 2026-10-16 son tarihi çıkarıldı ve kısa alıntılı fixture/regresyonla doğrulandı. AB/Dış İlişkiler ve YEĞİTEK ayrıntıları 200; kesin tarih çıkarılamadığı için unknown ve review_required korunur, kısa başlık fixture'ları tam metin kopyası değildir. Kaynak fixture'larındaki duyurular otomatik yayımlanmadı; haber ile açık çağrı ayrımı editör kontrolünde.
159 Python OK (11.977 s) + 11 JS PASS; diff-check temiz. 127 public/latest dosyası SHA-256 aynı. AŞAMA 8 açık: MTEGM detay, ilk paket diğer kaynakları, mevcut 13 çekici canlı kabulü ve devam paketleri. AŞAMA 9'a geçilmedi; sıradaki tek adım kaynak kabul kartlarını testli paketler halinde sürdürmek.


## 2026-10-10 02:07 — AŞAMA 8 tüm URL erişim ölçümü ve RSS paketi
135 envanter URL'si gerçek güvenli istemciyle tek sayfa ölçümünden geçti: 93 okunabilir, 42 hata. Bütün kartlarda gerçek page_observation var; HTTP 200 tek başına izin/entegrasyon kabulü değildir. Kaynakların robots/TLS/host sınırları gevşetilmedi.
Mevcut altı RSS (ab-ilan iki akış, eTwinning, Institut français, TÜSEV, Sivil Sayfalar) tekrar ölçüldü ve kısa metadata fixture'ları eklendi. TÜSEV valid boş RSS; kurum genelinde fırsat yok denmedi. Eurodesk Finder ve Interreg NEXT MED, ardından Mercator/IKI/GEF SGP/ISEF/T4/Global Schools/Roots & Shoots/Opportunity Desk/Opportunities for Youth/EU Calls gerçek yayımlanmış RSS arayüzleri mevcut feed çekicisine eklendi. Toplam 29 yapılandırma, başlangıçtaki 13 ID korunur. GEF SGP valid boş akış; Sivil Toplum için Destek akışı bozo olduğundan kabul edilmedi.
Eurodesk 576 kayıtta ortak link ve farklı GUID döndürüyor. GUID kaynak kayıt kimliği olarak korunur; ortak linkten kayıtlar yanlış birleşmez. GUID adresleri yalnız genel JavaScript kabuğu döndürdü, doğrulanmış ayrıntı URL'si sayılmadı. Ortak oluşturulmuş pubDate çağrı yayın tarihi olarak kullanılmaz. Gerçek çağrı/tarih/uygunluk/yönetici onayı hâlâ gereklidir; haber veya kurum sayfası açık çağrı değildir.
163 Python PASS (15.549 s), 11 JS PASS, diff-check PASS; 127 public/latest SHA-256 aynı. AŞAMA 8 aktif; kalan liste/detay/politika kabulü tamamlanmadan AŞAMA 9'a geçilmedi. Kullanıcı kesin kuralı devam eder: rutin aşama onayı bekleme; yalnız kota <=%5 veya gerçek kullanıcı girdisi engeli checkpoint gerekçesidir. Deploy/main merge yapılmadı.


## 2026-10-10 02:11 — AŞAMA 8 kaynak yolları ve ilk paket kabulü
Envanterdeki 135 URL'nin hepsinde gerçek erişim gözlemi, yöntem, periyot ve görünür kabul/manuel inceleme gerekçesi var; yönetici kaynak satırları kabul kartlarıyla eşitlendi. Bunların tümü connected değildir. İlk pakette dört MEB RSS'si, OGM tarihli ayrıntı örneği, Eurodesk Finder GUID ayrımı ve Ulusal Ajans gerçek liste/kapalı başvuru ayrıntısı testli. Ulusal Ajans yeniden erişildi: 200; önceki timeout kaydı tarihsel ölçüm olarak korunur. 13 Ekim toplantı günü ile 7 Ekim son başvuru ayrıldı. Otomatik kullanım koşulları doğrulanamadığı için UA manuel; Eurodesk Türkiye/ Terra Viva robots nedeniyle manuel, SALTO ticari dağıtım ön izni gerekir.
29 aggregator yapılandırması, orijinal 13 ID korunur; bağlanan her yeni RSS kısa gerçek fixture ve tekrar/hata/boş testleriyle ölçüldü. Geçerli boş TÜSEV/GEF akışı kurum genelinde fırsat yok demek değildir. Eski çağrı ID formülünü GUID olmayan kayıtlar için koruyan regresyon eklendi; yeni GUID alanı eski kayıtları yeniden kimliklendirmez.
168 Python PASS (15.690 s), 11 JS PASS; diff-check temiz; 127 public/latest hash aynı. AŞAMA 8'in MVP kapsamındaki envanter/ilk paket/testli metadata ve dürüst manuel yönlendirme işleri doğrulandı. Her kaynakta otomatik açık çağrı veya Türkiye uygunluğu kanıtlanmış değildir; bunlar yönetici inceleme kuyruğunda kalır, yayın kapısı açılamaz. AŞAMA 9 kullanıcı deneyimi ve üyelik çekirdeğine yerelde geçiliyor; aşama onayı beklenmez. Main merge/deploy yok.


## 2026-10-10 02:17 — AŞAMA 9 üyelik/yetki ilk dilimi
Service.entitlements/export_csv mevcut store üzerindedir: doğrulanmış kullanıcı + sunucuda etkin Pro; ücretsiz/iptal/süresi geçmiş/bozuk tarih reddedilir. Kullanıcı preferences isteğiyle tier veya üyelik durumunu yükseltemez; tercihler var olan hakları silemez. GET /api/pro/export sunucuda kontrol edilir, yalnız onaylı public çağrıları CSV yapar, formül hücreleri metne çevrilir. Gerçek ödeme etkin değil; sahte tahsilat sonucu yok.
DEMO Service.save/approve kayıt/onay etiketini korur; üretim Service.public ve publication_report DEMO kayıt/onayları dışlar. Böylece yerel demo-admin gerçek keşfi üretime onaylayamaz. App üretim kimliğini Google provider, verified email ve revoked token denetiminden geçirir; admin UID şartı korunur. Mock sınır testleri canlı Google kanıtı değildir.
public_calls kaynak/tarih kanıtı/kesinlik ve onay kontrol zamanını verir; ayrıntı ve HTML fallback son kontrol/kaynak/son tarih kanıtını gösterir. Üyelik görünümü mevcut Lovable tasarımında; gerçek tarayıcı testinde Pro test hesabı CSV dosyasını indirdi. Masaüstü ve 390x844 mobil ekran kaydedildi; mobil scrollWidth375 <= viewport390. Test yalnız MemoryStore'da, gerçek DB'ye Pro üyelik yazılmadı. Test sunucusu ve sekmesi kapatıldı. Ekranlar .agent/a9-membership-desktop.png ve .agent/a9-membership-mobile.png; test CSV Downloads/hibe-radari.csv.
176 Python PASS (16.545 s), 11 JS PASS; app/views syntax ve diff-check PASS; 127 public/latest hash aynı. Firebase CLI configured hibe-radari-tr ACTIVE projesini okuyabiliyor, apps:list success fakat []: mevcut web uygulaması yok. İşlem ortamında Firebase web/Admin UID/Gemini değişkenleri yok. Firebase/Auth/Firestore canlı işlemi veya deploy başarılı denmez. AŞAMA 9 aktif; sıradaki tek işlem mevcut Firebase proje/Auth/web uygulama yapılandırmasını ve gerçek backend erişim koşullarını doğrulamak. Main/push/deploy bu dilimde yok.


## 2026-10-10 02:25 — AŞAMA 9 gerçek Firebase erişimi ve temiz kurulum
Mevcut hibe-radari-tr projesinde Hibe Radari Web uygulaması oluşturuldu; appId 1:820119325615:web:b792543cfeb9a898c4fd5a, ACTIVE. SDK config gerçek API'den alındı; gerekli dört alan ve projectId eşleşmesi doğrulandı. Config yalnız ignored .agent/firebase-web-config.json içinde; sır değerleri rapora/Git'e yazılmadı. Bu işlem deploy veya Google giriş başarısı değildir.
Auth/config ve provider API'si 404 CONFIGURATION_NOT_FOUND; Cloud Billing read-only ölçümü billingEnabled=false. Public Identity Platform initializeAuth endpoint'i yalnız billing-enabled projeler içindir (https://docs.cloud.google.com/identity-platform/docs/reference/rest/v2/projects.identityPlatform/initializeAuth); ücretli servis/plan açılmadı. Firebase konsolundaki açık Google hesabı projeye yetkisiz; CLI hesabı farklı ve tarayıcıda signed out. Oturum veya sözleşme aşılmadı. Kullanıcıya projeye erişen hesapla Auth/Google etkinleştirmesi ve gerçek admin UID için tek gerekli bilgi sorusu gönderildi. Backend ADC yok; env'de Firebase/Admin UID değerleri yok; canlı Firebase/Auth/Firestore NOT VERIFIED.
requirements.txt üzerinden .venv kuruldu: firebase-admin7.7.0 ve diğer mevcut bağımlılıklar. Temiz Windows kurulumunda tzdata eksikliği ilk testte 15 error/1 fail üretti; kök neden mevcut ZoneInfo kullanımı. Windows için tzdata>=2025.2 bağımlılığı eklendi, aynı tam koşu tekrarlandı: 180 Python PASS (18.594 s), 11 JS PASS, syntax/diff-check PASS. Kanıt .agent/a9-venv-tests.txt. Eklenen hibe.server --check sır değerlerini yazmadan eksik ayar/ADC bildirir ve exit1 döner; hazır görünüm canlı izin kanıtı değildir.
Statik site.build de DEMO kayıt/onaylarını bağımsız reddeder; symlink/junction yayın klasörü resolve öncesi engellenir. review_ready parola/standart dışı veya bozuk portlu resmî URL'yi reddeder. Yanlış insan-onaysız statik banner yeni onay kapısına göre düzeltildi. 127 public/latest SHA-256 aynı. AŞAMA 9 henüz tam kapanmadı; gerçek Google giriş/yetki ve backend erişimi kullanıcı girdisine bağlı. Bağımsız yayın/pilot güvenlik doğrulamalarına devam edilir, AŞAMA 10 tamamlandı sayılmaz.


## 2026-10-10 02:27 — Yayın ve rapor yazma hata sınırı
site.build commit_report callback ile site geçişini rapor yazımıyla birlikte hata sınırına aldı; rapor atomik yazımı başarısızsa eski public ağacı geri gelir, önceki site yoksa yeni site bırakılmaz. CLI --site bu yolu kullanır. --out public altında ham keşif yazımı toplama başlamadan exit2 ile reddedilir; incelemesiz ham veriler public içine çıkamaz. 183 Python PASS (34.700 s), önceki 11 JS PASS; 127 public/latest hash aynı. Ani güç kesintisi/işlem öldürme için kalıcı kurtarma günlüğü henüz yok; normal exception rollback testi bunun yerine geçmez. Gerçek Auth/ADC/admin UID engeli ve kullanıcı sorusu sürüyor; AŞAMA 9 tam kapanmadı. Sıradaki tek işlem kesintiden kurtarma ve staging pilot doğrulaması, gerçek üretim/deploy iddiası yok.


## 2026-10-10 02:30 — Kalıcı yayın kurtarma kaydı
site.build önce klasör/rapor önceki sürümünü atomik .<public>.transaction.json kaydında saklar. recover_publication yalnız beklenen çıktı, komşu yedek ve aynı rapor hedefini kabul eder; symlink/junction/bozuk/fazla büyük journal reddedilir. Yarım prepared geçiş eski site ve rapor bytesını geri getirir; committed geçişi korur. CLI --site toplama başlamadan yarım kaydı kurtarır, başarısız kaynak koşusu kurtarmayı bekletmez.
Gerçek subprocess os._exit(42) testi: yeni site+rapor yazıldıktan sonra süreç kapatıldı; yanlış hedef kurtarma reddedildi; doğru hedefle eski HTML/JSON/ICS manifesti ve rapor bytesı aynı şekilde geri döndü, ikinci kurtarma no-op. Son committed journal yazımı disk hatası da her iki ürünü geri alır. 185 Python PASS (33.939 s); bu dilimde JS değişmedi, önceki 11 JS PASS. 127 gerçek public/latest SHA-256 aynı. Kanıt .agent/recovery-tests.txt. Bu test gerçek işletim sistemi güç kesintisi değildir; fsync+atomik rename ile süreç kesintisi kapsamı doğrulandı.
AŞAMA 9 gerçek Auth/ADC/admin UID açık; kullanıcı sorusu bekliyor. Kota ölçümü kısa kalan29%, haftalık54%; duruş eşiği henüz yok. Sıradaki tek işlem staging ardışık koşu/hata/--only ve geri alma kabulünü doğrulamak; AŞAMA 10 tamamlandı denmez.


## 2026-10-10 02:33 — Offline staging pilotu ve temiz CI hazırlığı
tests/test_staging_pilot.py tüm 22 doğrulanmış RSS fixture arayüzünü mevcut run/persist_report/SQLiteStore/Service onayı/publication_report/site.build zincirinde iki ardışık koşuda sınadı. OGM gerçek GençBizz ayrıntı fixture son tarihi 2026-10-16; yalnız geçici test-admin onayıyla bir kayıt üretildi. Gerçek uygulama DB veya admin onayı değişmedi. HTTP503/bakım HTML bozuk RSS/--only tam snapshot kapısında reddedildi; onaylı HTML/JSON/ICS ve latest hash korundu. Önceki yedek klasörü+rapor pratikte geri alındı ve manifest eşleşti.
Bu 22 kaynaklı fixture pilotudur; canlı 29 yapılandırmanın iki tam koşusu değildir. Bilinmeyen/politikası incelenmemiş diğer kaynaklar ve gerçek Auth/ADC/admin UID, kaynak bazlı zamanlama, üretim backend ve RELEASE/deploy hâlâ açık. AŞAMA9 gerçek giriş doğrulaması bekler; AŞAMA10 tamamlandı sayılmaz.
Tam .venv koşusu 186 Python PASS (60.384s); bu dilimde JS kodu değişmedi, önceki11JS PASS. .github/workflows/test.yml bağımlılıkları test öncesi kuracak ve Ubuntu/Windows matrisiyle çalışacak şekilde düzeltildi; uzak CI NOT RUN, push henüz yapılmadı. Kanıt .agent/staging-pilot-tests.txt; diff-check PASS; gerçek public/latest önceki127SHA aynı. Sıradaki tek işlem kaynak periyodu/zamanlama güvenlik hazırlığı ve bekleyen canlı erişim gereksinimleri.


## 2026-10-10 02:38 — Kaynak periyodu güvenlik hazırlığı
Kaydı hazırlayan: Codex. Mevcut collector.due_sources ve CLI --scheduled periyotları UTC checked_at üzerinden uygular; varsayılan24saat, kapalı kaynaklar dışarıda. Bozuk/gelecek/zaman dilimsiz kayıt kaynakları gizlemez. Başarısız girişimler periyodu bekler. Hiç kaynak yoksa ağ/rapor yazımı yok; alt küme koşusu partial, ana yayın korunur. Tüm aktif kaynaklar zamanı geldiyse tam koşu. Henüz işletim sistemi zamanlayıcısı kurulmadı ve sürekli canlı yayın doğrulanmadı.
FEATURE: 191 Python PASS (62.874s), beş yeni test dahil; JS değişmedi, önceki11JS PASS; diff-check PASS. Kanıt .agent/schedule-tests.txt. Gerçek public/latest127SHA aynı. AŞAMA9 gerçek Auth/ADC/admin UID açık, AŞAMA10 tamamlanmadı. Rutin onay beklemeden yerel çalışma sürüyor. Sonraki tek adım AI kişisel bilgi maskelemesinin tarih kanıtlarını bozmaması denetimi.


## 2026-10-10 02:40 — AI maskelemesinde tarih kanıtı korunması
Kaydı hazırlayan: Codex. Gerçek hata: eski telefon regexi Son başvuru2026-11-30 değerini [PHONE] yapıyordu. hibe/llm.py redact_contacts geçerli ISO/yerel sayısal tarihleri parçalar halinde korur; e-posta/telefon aynı şekilde gizlenir, geçersiz tarih telefon istisnası olmaz. GeminiExtractor gerçek payload yolunda bu işlevi kullanır. Üç regresyon tarih/yaş/komşu telefon/yanlış tarih sınırlarını test eder.
FEATURE:194 Python PASS (62.263s), hedefli14PASS; JS değişmedi, önceki11JS PASS. Kanıt .agent/redaction-tests.txt; diff-check PASS; gerçek public/latest127SHA aynı. Gerçek Gemini çağrısı anahtar yokluğu nedeniyle NOT RUN; model gemini-3.8-flash değişmedi. AŞAMA9 Auth/ADC/admin UID sorusu bekliyor, AŞAMA10 hazırlığı sürüyor. Sonraki tek adım bülten opt-in bulunmayan üyelik kaydının güvenli atlanması.


## 2026-10-10 02:41 — Bülten üyelik/opt-in sınırı
Kaydı hazırlayan: Codex. hibe/notifications.py prepare/send_pending önceden u['subscribed'] nedeniyle tercih alanı bulunmayan üyelik kaydında KeyError verebiliyordu. Yalnız boolTrue açık opt-in kabul edilir; diğer değerler hazırlamada atlanır ve eski prepared kayıt gönderimden önce cancelled olur. Gerçek SMTP gönderilmedi.
FEATURE: notifications beş testi PASS, iki yeni regresyon dahil; önceki tam194Python PASS +11JS PASS. Son değişiklikten sonra tam suite tekrar koşulmadı; hedefli etkilenen kontroller PASS. diff-check PASS, gerçek public/latest127SHA aynı. AŞAMA9 gerçek Auth/ADC/admin UID hâlâ açık, AŞAMA10 tamamlanmadı. Kullanıcı kesin devam kuralı hafızada. Sonraki tek adım üretim erişimi gereksinimleri ve RELEASE kabul eksiklerini mevcut projeye göre denetlemek.


## 2026-10-10 02:44 — Üretim kabul denetimi ve bülten TLS
Kaydı hazırlayan: Codex. notifications.send_pending starttls artık ssl.create_default_context kullanır; test hostname ve CERT_REQUIRED doğrular. Tam196Python PASS (62.583s),11JS PASS; app/radar/decision/views syntax, compileall ve diff-check PASS. Kanıt .agent/release-local-tests.txt. Gerçek public/latest127SHA aynı. Gerçek SMTP gönderilmedi.
docs/RELEASE_KABUL_DENETIMI.md MVP0–10 gereksinimlerini kanıt/eksik matrisiyle denetler; RELEASE NOT VERIFIED. hibe.server --check aynı beş eksik env +ADC DefaultCredentialsError döndürdü. WEB uygulaması mevcut olsa da Auth önceki404CONFIGURATION_NOT_FOUND; bu dilimde gerçek API tekrar sorgulanmadı. firebase.json yalnız Hosting, backend rewrite yok: statik deploy Google giriş/API sunucusu çalıştırmaz. Gerçek admin/onay/Gemini/SMTP ve29canlıtamkoşu/zamanlayıcı/deploy açık. Ücretli altyapı veya gerçek UID uydurulmadı.
Kullanıcıya gerçek hesap/UID sorusu zaten gönderilmiş; tekrar rutin onay sorulmadı. Yerel somut ilerleme sürüyor, goal active. Sonraki tek ana adım AŞAMA9 canlı erişimi; beklerken kalan bağımsız yerel kabul eksikleri kontrol edilir.


## 2026-10-10 02:48 — EU API resmî politika ve eksik sayfalama
Kaydı hazırlayan: Codex. Resmî [API dokümanı](https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/support/apis) haricî sistem kullanımını açıkça yayımlar; [Komisyon yeniden kullanım bildirimi](https://commission.europa.eu/legal-notice_en) EU-owned içerik/atıf ve üçüncü taraf istisnalarını açıklar. Mevcut eu-ft politika allowed bu dar üstveri kapsamıyla kaydedildi; registry/kabul kartı api_interface_verified, çağrı ayrıntısı/ülke/insan onayı hâlâ açık. Yeni kaynak veya ikinci collector oluşturulmadı.
Gerçek mevcut Fetcher TLS/robots/policy yoluyla iki canlı ölçüm aynı15üstveri kaydı,3istek ve source health success verdi; run --only kapsamı partial. Yalnız .agent/source-audit/eu-policy-probe.json yazıldı; DB/onay/public/latest değişmedi. İki yapılandırılmış sorgu dışındaki tüm merkezî çağrıların alındığı iddiası yok.
eu_ft.collect önceden yalnız pageNumber1 alıyordu. Artık toplam/sonsayfa ile sonraki sayfalar alınır; tekrar sayfa/çelişkili toplam/şema/erken boş/sayfa tavanı hata ve mevcut yayın korumasına gider. Tavan10sayfa,50kayıt/sayfa;24saatperiyot. Dört yeni regresyon, mevcut40aggregator ve12registry+2kabul testi PASS; ilk yeni test Fetcher context manager desteklenmediği için test düzeneği hatası verdi, mevcut close() yoluyla düzeltilip tekrar PASS. Tam200Python PASS (62.010s), önceki11JS PASS; diff-check PASS. Kanıt .agent/eu-policy-tests.txt;127korunanSHAaynı. RELEASE hâlâ NOT VERIFIED: gerçek Auth/ADC/admin UID/backend/zamanlayıcı/tamcanlıpilot/deploy açık.
Sonraki tek adım kalan eski kaynak politika/erişim kabulünü resmî kanıtla ilerletmek; gerçek Auth kullanıcı sorusu bekliyor. Goal active; rutin aşama duruşu yok.


## 2026-10-10 02:53 — STGM gerçek tarih çelişkisi ve manuel kabul
Kaydı hazırlayan: Codex. [STGM listesi](https://www.stgm.org.tr/hibe-duyurulari) Agora kartında07.10.2926 gösteriyor; [ayrıntı](https://www.stgm.org.tr/demokrasi-burs-programi-agora-icin-basvurular-basladi) ve [özgün Böll sayfası](https://tr.boell.org/tr/agora-demokrasi-burs-programi) son tarihi7Ekim2026 ve üniversite başvuru koşullarını doğruluyor. Bu tarih10Ekimde geçmiş; lise çağrısı veya açık2926çağrısı sayılmaz. Kaynak kısa gerçek alıntı fixtureJSONda, HTML fixture diye sunulmadı. Kart onaylanmadı/yayımlanmadı.
html_cards.collect_cards bugün+10yıl ötesini tahminle düzeltmez: deadlineNone/unknown/review_required; özgün aday/alıntı/kaynak/kontrol zamanı korunur. Bu eşik inceleme sezgisidir, her uzun vadeli çağrıyı yanlış ilan etmez. Geçersiz gün de kanıtını korur; gerçek2028tarih kesin kalır. Resmî alıntıyla apply_deadline gerçek2026-10-07ye çözer; bu çözüm yeni canlı DB kaydı değildir.
İncelenen liste ve [çerez politikası](https://www.stgm.org.tr/cerez-politikasi) otomatik tarama/yeniden kullanım iznini açıkça doğrulamıyor; bütün sitede izin yok iddiası yapılmadı. STGM unreviewed/manual_pending korunur, politika/kabul/registry kanıtı eşlendi. Hiçbir eski connector silinmedi veya gizlenmedi.
FEATURE: tam202Python PASS (66.341s); ardından yeni gerçek kanıt testi dahil hedefli3PASS ve güncellenmiş config kabul2PASS, eski aggregator40PASS; JS değişmedi önceki11PASS. Son test eklenmesinden sonra tam203koşusu henüz yok. Kanıt .agent/stgm-date-tests.txt/.agent/stgm-aggregator-tests.txt; diff-check PASS, public/latest127SHA aynı. AŞAMA9 Auth/ADC/admin UID sorusu bekler; RELEASE NOT VERIFIED, deploy yok.
Sonraki tek adım kalan eski kaynak politika/erişim kabulü; rutin onay beklemeden bağımsız çalışma sürer.


## 2026-10-10 02:58 — Kullanıcı kota kuralıyla checkpoint/duruş
Kaydı hazırlayan: Codex. Proje: [[Projeler/Hibe Radarı/Hibe Radarı|Hibe Radarı]].
### Yapılanlar
Yerel tam203Python PASS66.727s +11JS PASS. Eski13connector/30registryID korunur; mevcut29aggregator/154registry/135URL.127public/latestSHAaynı.94değişen dosyada sınırlı secret-biçim taraması eşleşmesiz; yerel .agent/.env/DB/data/public/approvals dahil değil. Kod checkpoint ef89d9cb80d3b872a40048684aa37b7f96381e5a gerçek GitHub push ve ls-remote ile doğrulandı; main b32d6d02e1e424885d860684fb11d565b1ab061d aynı. [Uzak Tests38006766526](https://github.com/Aristotheles/hibe-radari/actions/runs/38006766526) terminal success; Ubuntu/Windows ayrısuccess. Son belge commit'inin yeniCI'si ayrıca kontrol edilecek.
### Alınan kararlar
Yeni karar yok; kullanıcı onaylı kesin devam/kota kuralı uygulanıyor. Kısaused95%=kalan5%,haftalıkused50%=kalan50%; yeni geliştirme başlatılmadı. 15dkheartbeatACTIVE güncel devam planıyla yeniden okunarak doğrulandı. Kullanıcı koşullu kota duruşu; proje tamamlandı değildir. Kota uygunken aynı yerel klasör ve dalda rutin aşama onayı beklemeden devam.
### Açık sorular ve sorunlar
AŞAMA9 gerçek Auth/ADC/admin UID/backend erişimi açık; kullanıcı sorusu zaten iletildi. AŞAMA10 gerçek29tamcanlıpilot, kaynak koşulları, üretimzamanlayıcı/SMTP/onay/deploy/hostingrollback açık. RELEASE NOT VERIFIED; mevcut canlı site korundu, deploy yapılmadı. Gerçek kimlik/onay/tahsilat uydurulmaz.
### Sonraki adım
- [ ] Kota yeniden uygunken docs/CONTINUATION_PLAN.md ve güncel devirden devam; önce uzak sonCI/Git/kota/süreçler, sonra AŞAMA9gerçekerişim. Erişim beklerken yetkili bağımsız eski kaynak kabulü. Mainmerge/Cloudgeliştirme yok.


## 2026-10-10 06:18 — Kota sonrası yerel devam ve TÜBİTAK manuel kanıtları
Kaydı hazırlayan: Codex. Proje: [[Projeler/Hibe Radarı/Hibe Radarı|Hibe Radarı]].
### Yapılanlar
Kota yenilendi: başlangıç kısa kalan99%, haftalık49%; koşullu duruştan aynı yerel klasör/dalda çalışma devam etti. 46b8260891f0c6125a01ebb7d61f2c754219e5a2 yerel/uzak SHA eş, GitHub38006983401 success, başlangıç ağacı temiz. Projeye ait başka Python/Claude/Antigravity süreci gözlenmedi; diğer projelerin süreçlerine dokunulmadı.
TÜBİTAK ana duyuru listesi ve resmî program/duyuru sayfaları manuel okundu. Bilim Söyleşileri son tarih5Kasım2026 saat17.30; 2204-A son tarih4Ocak2027 saat17:30. Kısa alıntı JSON fixture, HTML yanıt fixture değildir. İki regresyon gerçek son tarihi yayın/başlangıç tarihinden ayırır; eksik şartlarla öğrenci uygunluğu bilinmiyor kalır; bot doğrulama HTML'i geçerli boş RSS sayılmaz.
4000 RSS adresi manuel web okumasında Verifying your connection HTML'i döndürdü; robots/RSS güncelliği doğrulanmadı, koruma aşılmadı. Eski “son çağrı2024” notu bu yeni ölçümün sınırlarıyla düzeltildi. TÜBİTAK iki connector kimliği ve unreviewed/manual politikaları korunur; yeni izin/insan onayı/canlı DB başarısı yok.
### Doğrulama
Tam205Python PASS; hedefli29PASS; diff-check PASS. Bu dilimde JS değişmedi, son11JS/uzak Windows+Ubuntu checkpoint kanıtı korunur. Log .agent/resume-tubitak-tests.txt.127public/latestSHA aynı. Kaynak sayıları29aggregator/154registry/135URL değişmedi.
### Alınan kararlar
Yeni karar yok; kullanıcı onaylı kota sonrası devam ve tek aktif yerel ajan kuralı uygulandı.
### Açık sorular ve sorunlar
AŞAMA9 gerçek FirebaseAuth/ADC/admin UID/backend erişimi bekliyor; hesap/UID sorusu tekrar sorulmadı. AŞAMA10 gerçek tam canlı pilot/zamanlayıcı/SMTP/onay/RELEASE/deploy açık. Deploy yapılmadı.
### Sonraki adım
- [ ] Bağımsız kaynak kabulü ve kaynak sağlık iletilerinin Türkçe okunabilirliği; erişim sağlanınca AŞAMA9 gerçek giriş. Rutin aşama onayı/duruş yok.


## 2026-10-10 06:19 — Kaynak sağlık iletilerinde Türkçe düzeltmesi
Kaydı hazırlayan: Codex.
### Yapılanlar
hibe/aggregator/net.py içindeki15bozuk UTF-8/Windows-1252 metin satırı düzeltildi; URL/DNS/robots/boyut/yönlendirme hata mesajları artık doğru Türkçe. Aynı dosyanın ASCII kod/güvenlik koşulları değişmedi; geçmiş ham gözlem kayıtları yeniden yazılmadı.
### Doğrulama
FAST: ağ güvenliği+aggregator54test PASS5.168s, diff-check PASS. Önceki tam205Python PASS66.425s; bu yalnız mesaj değişikliğinden sonra tam koşu tekrarlanmadı. JS değişmedi. TÜBİTAK dilimi752b2cdyerelcommit; push henüz yapılmadı.
### Alınan kararlar
Yeni karar yok; yetkili yerel devam sürüyor.
### Açık sorular ve sorunlar
AŞAMA9Auth/ADC/adminUID sorusu bekler; AŞAMA10/RELEASE/deploy açık. Canlı site değiştirilmedi.
### Sonraki adım
- [ ] Gençlik Köprüsü mevcut connector için resmî erişim/yeniden kullanım koşullarını incele.


## 2026-10-10 06:20 — Gençlik Köprüsü izin ve başvuru rolü kabulü
Kaydı hazırlayan: Codex.
### Yapılanlar
Resmî [Impressum](https://www.jugendbruecke.de/impressum/) başka sitelerde içerik kullanımını açıkça kısıtlıyor; mevcut source-15/jugendbruecke kayıtları permission_required olarak eşlendi. Connector silinmedi veya gizlenmedi. Otomatik tarama/aktarım yapılmadı, izin uydurulmadı.
[2027/28 okul değişim çağrısı](https://www.jugendbruecke.de/foerderung/ausschreibung-schulaustausch-2027-28/) son tarihi6Aralık2026; başvuran Alman okul, Türk okul ortak. Kısa resmî alıntılar ve rol yorumu ayrı alanlarda kaydedildi. Türkiye lise doğrudan uygunluğu veya insan onayı ilan edilmedi.
### Doğrulama
FAST: source_acceptance+network16test PASS1.294s, diff-check PASS. Önceki tam205Python/son11JS kanıtı geçerli; bu yapılandırma adımından sonra tam suite yeniden koşulmadı. Canlı site/DB/onay değişmedi.
### Alınan kararlar
Yeni kullanıcı kararı yok; mevcut tarama koşullarına uyum kuralının resmî kanıtı kaydedildi.
### Açık sorular ve sorunlar
AŞAMA9 gerçek hesap/UID/ADC/backend sorusu bekler. AŞAMA10/RELEASE açık; deploy yok. British Council şartlarının sonraki bölüm okuması zaman aşımına uğradı, tam politika kabulü yapılmadı.
### Sonraki adım
- [ ] British Council kullanım şartlarının kalan bölümünü ve mevcut RSS erişimini doğrula; kaynak engelleri tam koşu başarısı sayılmaz.


## 2026-10-10 06:24 — HTTP eksik/yavaş gövde sınırı
Kaydı hazırlayan: Codex.
### Yapılanlar
hibe/server.py POST gövdesine10sokuma zaman aşımı koyar, eksik Content-Length gövdesini400 ve süre aşımını408 ile reddeder; JSONarray/scalar/null nesne olmayan istekleri400 yapar. Önceden eksik gövde süresiz bekleyebilir, JSONlistesi500 oluşturabilirdi. Kimlik/izin/yayın kuralları gevşetilmedi.
Gerçek loopback socket testinde gövdesiz istek0.1stest eşiğinde408, yarım gönderim400, dört nesne olmayan JSON400; oturum oluşturulmadı. Sonraki normal giriş200. Bu canlı Google/Firebase veya üretim yük testi değildir; toplam slow-client/iş parçacığı kotası ayrıca doğrulanmadı.
### Doğrulama
FEATURE: tam208Python PASS, hedefliHTTP+üyelik22PASS8.444s, diff-check PASS. JS değişmedi, önceki11PASS.127public/latestSHAaynı. Log .agent/http-body-tests.txt.
BritishCouncil iki resmî URLye tekil manuel yerel TLSkontrolü403 döndürdü; tekrar/koruma aşma yok. Webaracı RSSi unsupported-content-type olarak okuyamadı; tam kullanım şartları sonraki okumalarda timeout, otomatik izin verilmedi. Kanıt .agent/source-audit/british-manual.json. İnternet sitesinin herkes için kapalı olduğu iddiası yok.
### Alınan kararlar
Yeni karar yok; tüm aşamalara kadar yetkili yerel çalışma sürer.
### Açık sorular ve sorunlar
AŞAMA9 gerçek Auth/ADC/adminUID/backend erişimi; AŞAMA10 üretim SMTP/zamanlayıcı/tam canlı pilot/onay/RELEASE/deploy bekler. Kullanıcı sorusu tekrar sorulmadı.
### Sonraki adım
- [ ] Kalıcı keşif ön doğrulamasında sonraki satır hatasının önceki kayda etkisini sınamak; mevcut mimari ve tek aktif ajan korunur.


## 2026-10-10 06:28 — Keşif koşusu ön doğrulamasında veri koruma
Kaydı hazırlayan: Codex.
### Yapılanlar
Regresyonlar önce ikiFAIL/tekERROR gösterdi: sonraki manuel kimlik çakışması önceki onayı silebiliyor; aynı koşuda yinelenen kimlik kabul ediliyor; kimliği eksik sağlık satırı önceki kayıtlar yazıldıktan sonra KeyError üretiyordu.
hibe/aggregator/bridge.py bütün gözlemlerin manuel kimlik çakışmasını ve benzersizliğini, bütün sağlık satırlarının kimliklerini yazmadan önce doğrular. Manuel mevcut çağrı ve önceki onay geçersiz koşuda byte-equivalentMemoryStore verisiyle korunur. Bu tüm DBwrite/disk/Firestore arızalarına karşı atomik transaction iddiası değildir; mevcut adapterler korunur.
### Doğrulama
FEATURE: aynı kök hata regresyonları ve staging14PASS21.959s; tam210Python PASS67.315s,11JS PASS, diff-check PASS. Log .agent/bridge-preflight-tests.txt. hibe.server --check yeniden beş eksik ayar ve ADC DefaultCredentialsError gösterdi; gerçek erişim sağlanmadı.
### Alınan kararlar
Yeni karar yok; kullanıcı veri/insan onayı koruma kuralları uygulandı.
### Açık sorular ve sorunlar
AŞAMA9gerçekAuth/ADC/adminUID/backend; AŞAMA10canlıSMTP/tamkoşu/zamanlayıcı/onay/RELEASE/deploy açık. Kullanıcı sorusu bekler, tekrar sorulmadı.
### Sonraki adım
- [ ] Bülten gönderiminde DEMO ile üretim ayrımını ve gönderim öncesi onay sürümünü kontrol et.


## 2026-10-10 06:31 — Bülten DEMO ve güncel onay sürümü kapısı
Kaydı hazırlayan: Codex.
### Yapılanlar
hibe/notifications.py send_pending DEMOservice'i SMTPbağlantısından önce reddeder. prepare seçilmiş kamu çağrılarının aynı anda üretilen sürümhashlerini call_versions alanında saklar; hibe/domain.py public_calls bu hash'i aynı kayıt görüntüsünden üretir. Sonradan ayrı storeokuması eski içerik/yeni sürüm eşleşmesi yaratmaz.
Gönderimden hemen önce her seçilmiş çağrı hâlâ yayınlanabilir/güncel/onaylı/DEMOdışı mı denetlenir. Revoked/değişmiş/yeni sürümle yeniden onaylanmış veya sürüm kanıtı olmayan eski prepared bülten stale kalır; otomatik gönderilmez. İptal edilmiş opt-in mevcut cancelled yolu korunur. İşlem gönderimi ile DBcommit arasında dağıtık transaction iddiası değildir; gerçek SMTP yok.
### Doğrulama
FEATURE: tam212Python PASS; hedefli20PASS ve ardından yeni sürümle yeniden onay senaryosu dahilnotifications7PASS0.540s. Önceki11JS PASS, diff-check PASS. Log .agent/newsletter-version-tests.txt. MockSMTP fresh yolunda tek gönderim, diğer yollar sıfır; DEMO SMTPconstructor bile çağrılmadı. Gerçek e-posta gönderilmedi.
### Alınan kararlar
Yeni karar yok; kullanıcı gerçek yayın/onay/DEMO ayrımı kuralı bültene uygulandı.
### Açık sorular ve sorunlar
AŞAMA9 gerçekAuth/ADC/adminUID/backend engeli sürer; AŞAMA10/RELEASE tamamlanmadı, deploy yapılmadı.
### Sonraki adım
- [ ] HTML bültenin abonelikten çıkış bağlantısını içerdiğini doğrula; eksikse aynı bülten hattında düzelt.


## 2026-10-10 06:33 — HTML bülten abonelikten çıkış bağlantısı
Kaydı hazırlayan: Codex.
### Yapılanlar
Önceden prepare abonelikten çıkış bağlantısını yalnız plain-text e-postaya ekliyordu; HTMLalternatifinde yoktu. hibe/export.py render isteğe bağlı HTTPSunsubscribe_url ile kaçışlanmış footerlink üretir; notifications.prepare aynı imzalı URLyi HTML ve metne geçirir. Genel statik önizleme kişisel token üretmez.
### Doğrulama
FEATURE: tam213Python PASS67.977s; notifications8PASS0.571s. HTMLparsehref=metin=outboxURL; token doğrulaması doğruUID, HTMLenjeksiyon/scriptURL reddi testli. Önceki11JS PASS/diff-check PASS. Log .agent/newsletter-footer-tests.txt. Gerçek SMTP/mailclient NOT VERIFIED; e-posta gönderilmedi.
### Alınan kararlar
Yeni karar yok; mevcut opt-out kullanıcı akışı her iki bülten biçiminde korunur.
### Açık sorular ve sorunlar
AŞAMA9Auth/ADC/adminUID/backend hâlâ eksik; AŞAMA10/RELEASE/deploy açık. Üretim site/DB/onay değiştirilmedi.
### Sonraki adım
- [ ] Mevcut29connector içindeki izinli23API/RSS arayüzünün canlı metadata gözlemini mevcut run(only=...) ile yap; kalan6kaynağı saklama/silme, kapsamı partial olarak raporla. Bu29tamcanlıpilot veya insan onayı değildir.


## 2026-10-10 06:45 — Canlı23arayüz üstverisi ve tekilleştirme süre kontrolü
Kaydı hazırlayan: Codex.
### Yapılanlar
Mevcut29connector içinde allowed23API/RSS arayüzü gerçek Fetcher/robots/TLS yoluyla50HTTPisteği ve951kayıt verdi; tüm23healthsuccess, raporonlynedeniylepartial. Ayrıntı enrichment0, altı diğer connector silinmedi/başarılı sayılmadı. Yalnız geçiciMemoryStore951keşif;127public/latestSHAaynı. İlk helperimportyolu hatası düzeltildi; kaynak erişim hatası değildi.
collector.dedupe sabitURL/başlık/dönemleri koşu içinde önbellekler ve difflib matematiksel üst sınırlarıyla gereksizratiohesabını atlar. Aynı180canlıkayıtta1.631s→0.142s, bütünçıktıSHAaynı. Optimize951kayıt8.094s; tüm eski951 için ayrıkdedupesüresi ölçülmedi, ilk koşunun ağ+dbye toplamıyla kıyaslanmaz. Kimlik/0.9eşiği/yalnızinceleme kuralları korunur.
### Doğrulama
FEATURE:214Python PASS67.456s, hedefli41PASS2.804s, önceki11JS PASS, diff-checkPASS. Eşik/Unicode/uzunbaşlık adayları referansratioile eşit. Rapor docs/LIVE_METADATA_PILOT_20261010.md; gerçek gözlemler ignored.agent içinde.
### Alınan kararlar
Yeni karar yok; envanterin her kaynağına otomatik bağlantı sözü verilmez, kapsam dürüstçe partial kalır.
### Açık sorular ve sorunlar
AŞAMA9Auth/ADC/adminUID/backend sorusu bekler; AŞAMA10iki29tamcanlıpilot/SMTP/zamanlayıcı/onay/RELEASE/deploy açık. Bu tek üstveri gözlemi insanonayı veya tam canlı kabul değildir.
### Sonraki adım
- [ ] Aynı veri hacminde kalıcı kayıt yolunun her yeni çağrıda bütüncalls koleksiyonunu yeniden okuma maliyetini ölçmek; gerçek üretim erişimi uydurulmaz.


## 2026-10-10 06:52 — Kalıcı kayıt tarama maliyeti ve gerçek GUID ayrımı
Kaydı hazırlayan: Codex.
### Yapılanlar
hibe/aggregator/bridge.py eski çağrı eşlemesinde bütüncalls koleksiyonunu her yeni satırda okuyordu.250gerçeküstveride250tarama/31125satır/3.837s; yeni koşuiçi başlık→adayIDindeksi tekbaşlangıçtarama/0mevcutsatır/0.119s. Her eşleşen aday store.get ile güncel okunur; indeksteki eski editör özeti geri yazılmaz. Aynı koşuda oluşturulanlar indekse eklenir. Firestore canlı okuma/maliyet veya tüm eşzamanlı-yazar garantisi ölçülmedi; gerçek onay/veri koruma kuralları korunur.
Gerçek EurodeskFinderüstverisinde aynı3kelimelikbaşlık/RSSURL/farklıGUID iki kayıt var. Collector bunları ayırırken eski bridgelegacy başlık+URLeşlemesi tekrar birleştiriyordu. Önceki HEADişleviyle geçiciMemoryStore1çağrı, yeniyle2çağrı; iki özgün keşif kimliği aynı kalır. GUID/authority/programme uyuşmazlığı legacy eşleşmeyi durdurur. Gerçek kısaüstverifixture tests/fixtures/aggregator/duplicate_guid_live_evidence_20261010.json; çağrı şartı/insan onayı değildir.
### Doğrulama
FEATURE: tam218Python PASS; önceki217PASS66.063s ardından gerçekörnekte17hedefliPASS0.132s; indeks+staging16PASS21.238s. İlk sentetikGUIDtesti1!=2FAIL gösterdi, aynıtestdüzeltmeilePASS. Log .agent/bridge-live-guid-tests.txt; benchmarkbefore/after ve live-guid-remerge-regression ignored.agent içinde. Önceki11JS PASS/diff-checkPASS.127public/latestSHAaynı.
### Alınan kararlar
Yeni karar yok; aynı çağrı tekilleştirilir, farklı GUID çağrıları hatalı birleşmez. Mevcut store/collector korunur.
### Açık sorular ve sorunlar
AŞAMA9gerçekAuth/ADC/adminUID/backend; AŞAMA10tamcanlıpilot/zamanlayıcı/SMTP/insanonayı/RELEASE/deploy açık. Kullanıcı sorusu tekrar sorulmadı.
### Sonraki adım
- [ ] Aynı23izinliarayüzde ikinci gerçekpartialüstverigözlemi; altıincelenmemişkaynağın yokluğunu tam başarı sayma. Sonra güvenli checkpoint/uzakCI kabulü ve gerçek erişim kaydından devam.


## 2026-10-10 06:58 — Kota sonrası doğrulanmış yerel checkpoint
Kaydı hazırlayan: Codex.
### Yapılanlar
218Python PASS65.697s,11JS PASS, compileall/4JSsyntax/diff-check PASS. İki gerçek23API/RSS üstveri gözleminde23healthsuccess/951keşif; ikinciMemoryStore951ayrıkçağrı, iki farklıGUIDyenidenbirleşmez. İki raporpartial,29tamcanlıpilot veya ayrıntı/uygunluk/insanonayı değildir.127public/latestSHAaynı; eski13connector/30registryID korunur. Modelgemini-3.8-flash/backendsecret kuralı değişmedi.
TÜBİTAKtarihkanıtları, GençlikKöprüsüresmîizinkısıtı, okunurTürkçehatalar, HTTPgövdesınırı, kimlikönkontrolü, bültenDEMO/güncelonay/HTMLoptout ve dedupe/kayıt performansı yereltestlidir. Tam218kodHEAD68c69cbed9bfef160fdd3f9e27ece6160107a8fb. Belgecheckpoint commit/push hazırlanıyor; uzakSHAveCI gerçeksonuçla ayrıca kabul edilecek. Mainmerge/deploy/gerçekSMTPyok.
MVP'nin eski rutin dur/onay metni kullanıcı onaylı güncelkesindevamkuralıyla düzeltildi; geçmiş tarihli kayıtlar silinmedi. README ve canlıpilotraporu güncelkanıta eşlendi. Gitdiffsınırlısecretbiçim taraması eşleşmesiz; ignored.agent/env/DB/public/approvalsGit'e alınmaz.
### Alınan kararlar
Yeni karar yok; kullanıcı tüm aşamalara kadar yereldevam/koşullukota/commitpush/RELEASEdeploy yetkisi aynen uygulanır.
### Açık sorular ve sorunlar
GerçekAŞAMA9Auth/ADC/adminUID/backend erişimi hâlâ yok; sonservercheckbeşeksikenv+DefaultCredentialsError. Kullanıcıya hesap/UIDsorusu zaten gönderilmiş, rutin tekrar yok. AŞAMA10gerçekyayınonayı/üretimSMTP/zamanlayıcı/tamcanlıpilot/RELEASE/hostingrollback açık. Tamamlandı veya canlıçalışıyor denmez.
### Sonraki adım
- [ ] Uzakcheckpoint/UbuntuWindowsCI gerçekkabulü; ardından AŞAMA9 gerçekerişim değişimini mevcut15dktakiple kontrol etmek. Erişim yokken yeni kimlik/onay/ücretlialtyapı uydurma; anlamlı bağımsız iş varsa sürdür, aynı engelde sessizkal.


## 2026-10-10 — Boş ilan akışının gerçek nedeni ve aktarım
Kaydı hazırlayan: Codex.
### Yapılanlar
Registry154 kayıt, aggregator29 bağlantı:23allowed/5unreviewed/1permission_required. 170 dosyalardan doğrulanmadı. Önceki canlı üstveri gözleminden155inceleme+4izleme gerçek mevcut FirestoreStore/persist_report ile aktarıldı; exec90359 exit0,159calls/159discoveries/23source_health/0approval,public ve latest hashleri aynı. Sonuç .agent/source-audit/firestore-import-result.json. Veritabanının boş olması geçici MemoryStore taramalarının aktarılmamasından kaynaklanıyordu. Onaylı liste hâlâ boş; bu veri yok demek değil, koşulların editör incelemesi açık.
Resmî MEB3787 fotoğrafyarışması sayfası2025-10-27sonbaşvuru gösteriyor; güncel2026fırsatı diye sunulamaz. TÜBİTAK BilimSöyleşileri resmî güncelduyuru2026-11-05/17.30 tarihini yeniden doğruladı; tam şartlar hâlâ incelenecek. Kaynak/ilan durum raporu docs/KAYNAK_VE_ILAN_DURUMU.md.
### Açık sorular ve sorunlar
Gerçek yönetici giriş ekranda Çıkış gösteriyor; admin uçları/token kabulü ayrıca ölçülmeli. Tüm envanter otomatikçalışıyor denmez. Hosting deploy yok.
### Sonraki adım
159aday kuyruğunu yönetici ekranında doğrula; eskihaberleri ayır, güncelokul/öğretmen/öğrenci fırsatlarını resmî tamşartlarıyla hazırlayıp insanonayına sun.

## 2026-10-10 — Gerçek yönetici kuyruğu ve yavaşlık düzeltildi
Kaydı hazırlayan: Codex.
### Yapılanlar
Gerçek Google yönetici oturumuyla localhost8021/yonetim ekranında 159 kuyruk kaydı, 159 toplam çağrı ve 0 yayımlanan ilan ölçüldü. Hesap yetkisi doğru; ilk açılışta oturum yüklenmeden route çalışıyordu. web/app.js oturum sonrasında mevcut ekranı yeniler. hibe/service.py kaynak panelindeki kaynak başına uzak okumaları iki koleksiyon okumasına indirir; kapalı kaynak ayarı ve eksik/ortak sağlık kayıtları korunur. 170 satırlı sentetik regresyon testi gerçek kaynak sayısı iddiası değildir. 219 Python testi 55.472s PASS, 11 JS testi PASS, JS syntax ve diff check PASS. Önceki 3ec1da9 CI38049580523 Ubuntu/Windows başarı ölçüldü; bu yeni değişikliklerin CI sonucu değildir. Backend yeni exec29481 üzerinde8021 aktif.
### Açık sorular ve sorunlar
159 keşif kaydı güncel ve uygun 159 fırsat anlamına gelmez. İnsan yayın onayı ve RELEASE kabulü açık; Hosting değişmedi. 2204-A resmî2027 çağrı şartları incelendi; Bilim Söyleşileri ayrıntılı şartlar sitesi içerik vermedi. docs/GUNCEL_ILAN_INCELEMESI.md gerçek tarihler/uygunluk sınırlarını kaydeder.
### Sonraki adım
Güncel başvuru fırsatlarını mevcut taslak akışında resmî kanıtlarıyla hazırla; eski haberleri ayır. Önceki Auth engeli artık açık engel değildir.

## 2026-10-10 — İlk güncel lise çağrısı gerçek taslak akışında
Kaydı hazırlayan: Codex.
### Yapılanlar
2204-A 2027 çağrı PDF'si normal HTTPS erişiminde HTTP200, PDF879028byte; SHA256 1fd939ea30869d11972e64f85fdc472379e6d423e83ca2a60598ec2f5032654d. Gerçek yönetici ekranındaki JSON taslak formuyla tubitak-2204a-2027 kaydedildi. Ekran Taslak kaydedildi; onay bekliyor, kuyruk160, toplam160, yayımlanan0 ölçüldü. Öğrenciye özel yaş/proje/izin koşulları bilinmiyor bırakıldı; mevcut rol modeli öğrenci doğrudan rolü taşımadığından belirsiz yol kullanıldı, okulun kurumsal hibe başvurusu gibi gösterilmedi. Otomatik onay yok.
### Açık sorular ve sorunlar
Öğrenci rolünün mevcut kullanıcı görünümünde doğru temsil edilmesi ve resmî proje rehberi incelemesi açık. Bilim Söyleşileri şartları henüz tamamlanmadı. Son kod checkpoint c8e1a8f origin SHA eşliği doğrulandı; CI38049996782 halen çalışıyordu, başarı uydurulmadı. Backend exec29481.
### Sonraki adım
Öğrenci rolünü MVP kapsamıyla karşılaştır; resmî rehber incelemesini ve güncel fırsatları tamamla, sonra gerçek insan yayın onayıyla RELEASE değerlendirmesini yürüt.

## 2026-10-10 — Tarih/uygunluk filtresi ve yerel otomatik güncelleme
Kaydı hazırlayan: Codex.
### Yapılanlar
Mevcut siteye Son başvuru ve Uygunluk filtreleri eklendi; seçili başvuru yolunda aynı koşul/rol aranır. Gerçek browser seçim/temizleme ve ekran taşma kontrolü geçti. 221 Python testi39.277s,13JS testi PASS; syntax/diff PASS. Windows HibeRadari-KaynakGuncelleme görevi6günlük tetikle kuruldu. Mevcut collector/periyot/Firestore bridge; yalnız23allowed, kapalılar atlanır, genel/rejected kuyruk dışı, onay/deploy yok. İlk gerçek görev sonucu0,statusnot_due,0tarama/0değişiklik,finished2026-10-10T11:59:57.950999Z; yeniden tarandı denmez. Sonraki tetik16.15. docs/OTOMATIK_GUNCELLEME.md.
### Açık sorular ve sorunlar
Görev yalnız bilgisayar açık ve Windows oturumu mevcutken çalışır; sürekli sunucu otomasyonu değil. 160kuyruk kaydı0onay; bütün154registry çalışıyor sayılmaz. Türkiye koşulları kanıtı ve güncel fırsat incelemesi açık. Hosting aynı.
### Sonraki adım
Periyodu dolan ilk gerçek tarama sonucunu ölç; güncel lise/öğretmen fırsatlarını kanıtlarıyla tamamla ve insan onayı sonrası RELEASE değerlendir.

## 2026-10-10 — Otomatik kuyruk ön elemesi
Kaydı hazırlayan: Codex.
### Yapılanlar
hibe/auto_review.py mevcut160 çağrıya panel yüklemesinde sürüme bağlı otomatik sınıflandırma uygular. Lise/öğretmen/okul, fırsat türü ve Türkiye kanıt durumuna göre filtreler; haber/kapalı/bilgi eksik ayrı gruplar. Gerçek admin ekranı106/160fırsat adayı, lise filtresi15/160 ölçüldü. Aday kesin uygun fırsat değildir; kayıt/onay silinmez. auto_review kullanıcı taslağında gönderilse saklanmaz. 226Python testi41.239s PASS,13JS PASS,syntax/diff/detector PASS. Backend96132,8021aktif. docs/OTOMATIK_INCELEME.md.
### Açık sorular ve sorunlar
Tam metin/PDF otomatik incelemesi tamamlanmadı: ortamda Gemini anahtarı yok. Mevcut extractor/gemini-3.8-flash korundu; gerçek model çağrısı yapılmadı. Kullanıcıdan anahtarı sohbet yerine backend ortamına eklemesi asyncsoruldu. Keşiften güvenilir resmi belgeye mevcut pipeline sürüm kontrollü bağlanması açık. Yayın onayı/Hosting değişmedi.
### Sonraki adım
Mevcut extractor ile güvenilir resmi çağrı şartlarını otomatik çıkaran, kanıtı doğrulayan ve eski doğru bilgiyi koruyan keşif entegrasyonunu tamamla; Gemini yokken belirsiz sonucu uygun sayma.
