# Hibe Radarı — karar aracı görsel sözleşmesi

Kullanıcı tarafından 9 Ekim 2026'da seçilen Lovable tasarımının yerel uyarlaması. Görsel otorite: proje `097b2081-dd79-4182-915d-7052045ce218`, commit `4ffcc439d9441d52462793e206221f15418f8cc9`. Önceki üç tasarım planı tarihsel öneriler olarak docs/design içinde kalır.

Mod: Operate. Öğretmen fırsatı, son tarihi ve başvuru hakkını bulur. Yatay gezinme, sistem fontu, doğal/yeşil vurgu, rol renklendirmesi, iki sütun masaüstü ve tek sütun mobil liste. Bu yön 3D gösteri yüzeyi içermez.

## Tokenlar

| Token | Açık | Koyu |
|---|---|---|
| background | oklch(0.983 0.003 110) | oklch(0.19 0.007 155) |
| foreground | oklch(0.245 0.013 155) | oklch(0.94 0.005 155) |
| card | oklch(1 0 0) | oklch(0.225 0.009 155) |
| primary | oklch(0.465 0.103 160) | oklch(0.75 0.12 157) |
| muted-foreground | oklch(0.50 0.008 155) | oklch(0.71 0.009 155) |
| partner | oklch(0.48 0.123 302) | oklch(0.78 0.11 302) |
| individual | oklch(0.46 0.13 256) | oklch(0.78 0.1 256) |
| urgent | oklch(0.52 0.163 25) | oklch(0.76 0.13 25) |

Tam token/yüzey kuralları web/style.css içindedir. Sistem sans gövde 16px; ilan başlığı20px, ana başlık34px/28px mobil. Metadata12–14px; marka alt metni11px mobil. Dokunma kontrolleri44px; geçişler180ms; reduced-motion geçişleri kapatır. Seçili kontrol düz açık/koyu yüzey; görsel rol ve sonuç her zaman metin taşır.

## İçerik ve durum

Okulum/Ben başvuru yollarını filtreler; aynı çağrının alternatif yolları korunur. Uygunluk ve öncelik ayrı; tema açıklaması “ilgili olabilir” düzeyindedir. Gerçek kaynak/destek/son kontrol yoksa bilinmiyor; DEMO her görünümde açık. Tarih grupları çakışmaz, acil sınırı14 günden azdır. Sahte program/kurum filtresi yok; mevcut tema ve yol alanları kullanılır.

Detay önce seçili yolun uygunluğunu, sonra çağrı/koşul/kanıt bilgisini gösterir. Tek gerçek kaynak eylemi; DEMO'da resmî çağrı varmış gibi bağlantı verilmez. Yönetim yalnız ayrı adres, sunucu yetkisi; abonelik ayrı hesap akışı. UI rol gizleme güvenlik kontrolünün yerine geçmez.

## Kanıt sınırı

docs/LOVABLE_APPLIED.md gerçek kontrol kanıtıdır. Fiziksel cihaz, tam WCAG, 4G ve canlı hizmet kabulü ölçülmedi; tasarım sözleşmesi başarı belgesi değildir.
