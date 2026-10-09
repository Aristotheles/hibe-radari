# AŞAMA10 pilot hazırlığı — yerel kanıt

AŞAMA9 canlı giriş açık; bu belge bağımsız offline hazırlık kanıtıdır, aşama tamamlama iddiası değildir.

## Kaynak periyodu güvenlik hazırlığı

Mevcut collector.due_sources UTC checked_at ve kaynak interval_hours alanını kullanır; varsayılan 24 saat. Bozuk/gelecek/zaman dilimsiz kayıt kaynakları gizlemez. Başarısız denemeler de periyodu bekler; her tetiklemede tekrar istek gönderilmez. Kapalı kaynaklar taranmaz; periyot 1–168 saat aralığında doğrulanır.

Mevcut CLI --scheduled yalnız zamanı gelen kaynakları çalıştırır. Hiç kaynak yoksa ağ/rapor yazımı yapmadan başarılı çıkar. Tüm aktif kaynaklar geldiyse tam koşu; alt küme geldiyse partial ve ana rapor/site korunur. Bu düzen henüz sürekli yayın veya kurulmuş işletim sistemi zamanlayıcısı değildir; kısmi gözlemler mevcut depoya saklanır. Önceki başarılı kaynağın kontrol tarihi yenilenmez. Gerçek üretim zamanlayıcısı, canlı erişim ve tam kaynak kabulü açık.

FEATURE: 191 Python testi PASS (62.874s), beş yeni periyot/CLI testi dahil. JS değişmedi; önceki 11 JS PASS. Kanıt .agent/schedule-tests.txt. Gerçek canlı koşu/deploy bu dilimde yapılmadı.


## 2026-10-10 02:33 — Offline staging pilotu ve temiz CI hazırlığı
tests/test_staging_pilot.py tüm 22 doğrulanmış RSS fixture arayüzünü mevcut run/persist_report/SQLiteStore/Service onayı/publication_report/site.build zincirinde iki ardışık koşuda sınadı. OGM gerçek GençBizz ayrıntı fixture son tarihi 2026-10-16; yalnız geçici test-admin onayıyla bir kayıt üretildi. Gerçek uygulama DB veya admin onayı değişmedi. HTTP503/bakım HTML bozuk RSS/--only tam snapshot kapısında reddedildi; onaylı HTML/JSON/ICS ve latest hash korundu. Önceki yedek klasörü+rapor pratikte geri alındı ve manifest eşleşti.
Bu 22 kaynaklı fixture pilotudur; canlı 29 yapılandırmanın iki tam koşusu değildir. Bilinmeyen/politikası incelenmemiş diğer kaynaklar ve gerçek Auth/ADC/admin UID, kaynak bazlı zamanlama, üretim backend ve RELEASE/deploy hâlâ açık. AŞAMA9 gerçek giriş doğrulaması bekler; AŞAMA10 tamamlandı sayılmaz.
Tam .venv koşusu 186 Python PASS (60.384s); bu dilimde JS kodu değişmedi, önceki11JS PASS. .github/workflows/test.yml bağımlılıkları test öncesi kuracak ve Ubuntu/Windows matrisiyle çalışacak şekilde düzeltildi; uzak CI NOT RUN, push henüz yapılmadı. Kanıt .agent/staging-pilot-tests.txt; diff-check PASS; gerçek public/latest önceki127SHA aynı. Sıradaki tek işlem kaynak periyodu/zamanlama güvenlik hazırlığı ve bekleyen canlı erişim gereksinimleri.


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
