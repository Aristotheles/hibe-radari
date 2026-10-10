# Gemini Batch ve canlı yayın — 2026-10-10

Kapsam: mevcut Python/Firestore ve Firebase Hosting uygulamasına gerçek toplu AI incelemesi, kanıtlı yayın ve bulutta sonuç toplama. Mod: RELEASE. Ana geliştirme dalı `codex/cloud-handoff-20261010`; main birleştirilmedi.

## Gerçek sonuç

- Gemini `gemini-3.8-flash` Batch API: 115 + 28 + 10 = 153 belge, üç iş de tamamlandı; 153 başarılı model yanıtı. Model yanıtı tek başına yayın onayı değildir.
- Canlı `/api/calls`: 34 gerçek, DEMO olmayan fırsat. 32 ücretsiz öğretmen eğitimi, bir GençBizz lise girişimcilik programı, bir TÜBİTAK 2204-A yarışması. Eğitimler hibe olarak gösterilmez.
- Türkiye erişimi, lise düzeyi, başvuru rolü, kaynak alıntısı ve güncel açıklık ayrı kontrol edilir. Kişisel koşulun bilinmemesi hedef kitleyi otomatik belirsiz yapmaz. Geçmiş/kapalı çağrılar ve doğrulanamayan koşullar yayımlanmaz.
- ESEP gerçek katalog incelemesinde 38 farklı kurs belgesi değerlendirildi. Son normal çekici denemesi 31 kayıt, 0 kaynak hatası verdi; keşif sayısı yayın sayısı değildir. Katalogda daha sonra görünmeyen kayıtlar silinmez. Tekilleştirme farklı URL'lerdeki benzer başlıkları birleştirmez.
- Kaynak kayıt sayısı 154, çekici sayısı 30, koşulları izin veren çekici sayısı 24. Bunlar 170 çalışan kaynak anlamına gelmez. Envanterdeki bütün sitelerin entegrasyonu tamamlanmış değildir.

## Güncelleme ve maliyet koruması

Kaynak taraması Salı ve Cuma 08.15 Europe/Istanbul: keşif, belge incelemesi, filtreleme ve kanıtlı yayın akışı. Başlamış Batch sonuçları ayrı bulut göreviyle her saatin 05 ve 35. dakikasında toplanır; bu görev kaynak taramaz ve yeni AI işi başlatmaz. Yerel bilgisayar gerektirmez.

Atomik iş sahiplenme, belgenin parmak izi, bekleyen iş kontrolü, sürüm kontrolü ve aynı belge sonucunu yeniden kullanma yinelenen maliyeti sınırlar. Gemini anahtarı backend secret ortamındadır. Kaynak değişince eski onay kaldırılır; mevcut doğru alanlar eksik keşif bilgisiyle silinmez. Sürekli açık fırsatın doğrulaması 14 günü aşarsa yayın korunmaz. Sağlayıcının gerçekleşmiş fatura tutarı bu testte ölçülmedi.

## Doğrulama

| Kontrol | Sonuç ve kanıt |
|---|---|
| Python | PASS: 267 test, 36.429 saniye |
| Tarayıcı kuralları | PASS: 16 JS testi, 97.47 ms |
| Diff | PASS: `git diff --check`; yalnız Git satır sonu normalizasyon uyarıları |
| Veri/AI güvenliği | PASS: stale yanıt, eksik alıntı, kapalı çağrı, aynı belge, yarıda kalmış gönderim, mevcut alan koruma ve kaynak değişimi testleri |
| Backend build/yayın | PASS: build `9f05a122-6354-47a5-ad81-512aea9fb109`, canlı `hibe-backend-00003-lgw` |
| Tarama build/yayın | PASS: build `7206291e-0968-4d18-ab40-47224e81d307`, iki Cloud Run görevi `refresh:batch-r6-20261010` |
| Gerçek bulut sonuç toplama | PASS: `hibe-ai-batch-results-wtjrh`, Completed=True, succeededCount=1 |
| Zamanlama | PASS: iki Scheduler görevi ENABLED; haftalık tarama ve yalnız sonuç toplama ayrı |
| Hosting/public API | PASS: Hosting yayımlandı, canlı API 34 kayıt, anonim yönetim API 403 |
| Gerçek ekran | PASS: açık tema, tümü 34 / öğretmen 33 / öğrenci 2; fırsat türü, sürekli açık eğitim ve son güncelleme görünür |
| Gerçek yönetici Google oturumu | NOT VERIFIED: bu dilimde canlı giriş kabulü yeniden yapılmadı; giriş akışı değiştirilmedi |
| Gizli bilgi | Değişen ve yeni dosyalarda sağlayıcı anahtarı, özel anahtar ve erişim tokenı örüntüleri ayrıca kontrol edilir; anahtarlar rapora yazılmaz |
| Mobil mağaza/ödeme/çevrimdışı | N/A: bu web içerik/Batch değişikliğinin kapsamına girmez |

Canlı: https://hibe-radari-tr.web.app . Ekran kanıtı yerelde `.agent/live-batch-20261010.png`. İzin gerektiren siteler korunur; The Earth Prize'ın otomatik tarama yasağı aşılmadı. Eski Codex heartbeat yeniden oluşturulmadı. Daha geniş kaynak entegrasyonu ve canlı yönetici giriş kabulü açık işlerdir.
