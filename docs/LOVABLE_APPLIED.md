# Lovable karar aracı tasarımının yerel uygulaması

9 Ekim 2026 · Codex · FEATURE · **VERIFIED WITH WARNINGS**.

## Referans ve kapsam

Kullanıcının verdiği konuşma: https://lovable.dev/chats/27e5dd5a-0d6c-47f5-8888-3323d1faeb52?artifact=project%3A097b2081-dd79-4182-915d-7052045ce218

Lovable eklentisiyle proje, konuşma geçmişi ve dosyalar okundu. Teacher's Choice projesi `097b2081-dd79-4182-915d-7052045ce218`; referans commit `4ffcc439d9441d52462793e206221f15418f8cc9`. Okuma sırasında agentFinished=true, is_published=false. Kaynak tasarımın sistem fontu, yeşil vurgu, yatay gezinme, rol renkleri ve masaüstü/mobil kompozisyonu mevcut Python/HTML/CSS/JS yapısına uyarlandı. React/TanStack, cloud veritabanı veya yeni bağımlılık taşınmadı.

## Uygulanan davranış

- `/`: Okulum/Ben ayrımı; Türkçe ve aksansız arama; tema/yol filtresi; birbirini dışlayan tarih grupları; tamamı detay bağlantısı olan kartlar.
- `/ilan/<id>`: ayrı, yeniden yüklenebilir adres; sunucuda üretilen başlık ve Open Graph metaverisi; başvuru yoluna bağlı mevcut üç değerli uygunluk; koşul/kanıt/öncelik ayrımı.
- `/takvim`: ay gezinmesi, okul/bireysel seçimi, tarihli kayıtlara bağlantılar. Mevcut iki demo kaydının tarihi olmadığı için takvim boş görünür; tarih uydurulmadı.
- `/nasil-calisir`: gerçek 30 kayıt yeri, 19 aday/11 eksik kimlik, süreç açıklaması; son tarama ve kontrol bilinmiyor olarak korunur.
- `/aboneligim`: mevcut tema ve açık bülten onayı akışı korunur. Demo gerçek e-posta göndermez.
- `/yonetim`: ayrı adres; kamu gezinmesinde yönetici bağlantısı yok. Oturum olmadan yönetici içerik bölümü gizli, API sunucu yetkisi zorunlu. Demo yönetici seçimi yalnız bu adresin giriş alanında görünür; gerçek modda demo giriş kapalı.
- Karanlık/açık görünüm, yerel görünüm tercihi, reduced-motion, görünür focus ve etiketli kontroller.
- Geçerli tarihli kayıtta `.ics` tüm gün dosyası; bilinmeyen saati uydurmaz. Tarihsiz kayıtta indirme kapalı. WhatsApp paylaşım bağlantısı sabit son tarih ve ilan adresi taşır; dış servise mesaj gönderilmedi.
- Sunucu HTML'si JavaScript olmadan liste/detay/takvim/kaynak içeriğini taşır. Dinamik filtre/giriş/tercihler JS gerektirir. Bu işlem haftalık statik yayın/zamanlama işini kurmaz; MVP yayın aşaması açık kalır.

Lovable prototipindeki gerçek kuruluş adlarına bağlanmış sentetik çağrılar, örnek bütçeler, “Evet başvurabilir”, sabit kontrol tarihi ve “kişisel veri toplamayız” iddiası taşınmadı. Bilinmeyen destek, eş finansman ve ortak alanları bilgi kaydı yok olarak gösterilir. Kanıt konumu yoksa belirtilmemiştir. DEMO kaydında example.org gerçek resmî çağrı bağlantısı olarak sunulmaz.

## Doğrulama kanıtları

| Alan | Sonuç ve kanıt |
|---|---|
| Başlangıç testi | 37 Python + 5 JavaScript, PASS |
| Son testler | `python -m unittest discover -s tests -q`: 45 test OK; `node --test tests/test_radar.mjs`: 11 PASS |
| Statik/build | Python compileall ve app/views/decision JS syntax PASS; kaynak tabanlı uygulama, bundler yok |
| Güvenlik/veri | HTML/metaveri escape, unsafe link reddi, yayımlanmamış detaya 404, admin yetkisi ve cross-origin testleri PASS |
| Tarih/indirme | İstanbul gün sınırı, 14 gün sınırı, çakışmayan gruplar, artık yıl, yıl geçişi, UTF-8 ICS satır katlama ve satır enjeksiyonu testli |
| JS olmadan | HTTP testlerinde gömülü public içerik/başlık ve route 200; HTML fallback testli. JS kapalı gerçek tarayıcı oturumu ayrıca çalıştırılmadı |
| Yerel tarayıcı | Liste→detay, kanıt, bilinmeyen uygunluk, tema araması, filtre reset, bireysel boş durum, takvim ay değişimi, 30 kaynak sayfası, kullanıcı/yönetici giriş ve abonelik formu incelendi |
| Mobil/odak | 390×844: innerWidth390/scrollWidth375, yatay taşma yok; detay başlığına focus, bilinmeyen tarihte ICS disabled; 1440×900 masaüstü incelendi |
| Tasarım taraması | İlk detector küçük metin uyarıları verdi; marka alt metni ve filtre reset büyütüldü. Hesaplanan boyutlar mobil11px marka,13px reset; yeniden detector çalıştırılmadı |
| Performans | İlk HTML+CSS+4JS module+calls/config gövdeleri toplam 79.946 byte (sıkıştırılmamış, ölçüm anı); font/video/haricî 3D indirmesi yok. 4G/LCP/INP/CLS ölçülmedi |
| Dış servisler | Firebase/Gemini/SMTP/WhatsApp mesajı, kaynak taraması, push ve deploy NOT RUN; kullanıcının yerel sınırı korundu |

Tarayıcıda bulunan “Tüm yollar” seçenek değeri boş olmadığı için filtrelerin tüm kayıtları elemesi düzeltildi. Aynı akış yeniden kontrol edildi: CEVRE→1, filtre temizle→2, Ben→0, Okulum→2 ve detay açılışı.

## Açık sınırlar

Fiziksel telefon, ekran okuyucu, tam WCAG/kontrast taraması ve gerçek 4G performansı doğrulanmadı. ICS dosyasının gerçek takvim uygulamasına import'u ve WhatsApp dış önizleme testi yapılmadı; demo adresi loopback olduğu için başka kullanıcı cihazından erişilemez. Kayıtlı kullanıcı verisi ve opt-in SQLite'da tutulduğu için genel kişisel veri toplamama iddiası yok. Gerçek hizmetler, özgün 30 kaynak ve canlı MVP kabulü tamamlanmadı.

## İncelenen/değişen dosyalar

web/index.html, style.css, app.js, radar.mjs, yeni decision.mjs/views.mjs; hibe/server.py, yeni presentation.py; HTTP/JS/yeni presentation testleri ve CI syntax kontrolleri. Lovable ham referans dosyaları `.agent/lovable-reference` içinde Git dışındadır; başka tasarım planları `docs/design` altında korunmuştur.

## Sıradaki tek adım

Kullanıcının yerel demo üzerinde bu uygulanmış tasarımı incelemesi. MVP kaynak aşaması için özgün 30 kaynak belgesi hâlâ gerekir.
