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
