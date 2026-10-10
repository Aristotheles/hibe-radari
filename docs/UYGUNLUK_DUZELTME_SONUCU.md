# Uygunluk düzeltmesi — doğrulama kaydı

11 Ekim 2026 · Codex · C:/hibe-radari · codex/cloud-handoff-20261010.

## Değişiklik

Eksik kanıt ile açık kapsam dışı, kapanmış çağrı ve teknik belge hatası ayrı kategorilerdir. Kişisel koşul çelişkisi ülke/hedef/tarih kanıtını kendiliğinden iptal etmez; eski alanı bilinmeyen çelişkiler güvenli biçimde incelemede kalır. Kaynaktaki uygun ülkeler listesi bağlamıyla kısa ülke alıntısı kabul edilir. İlgisiz tanıtım veya platform erişimi hibe uygunluğu değildir. Kaynakta dışlama hükmü bulunmayan alıntı kapsam dışı kararını doğrulamaz.

Gerçek PDF bağlantıları rolüne göre incelenir. İlgisiz ekin erişim hatası ana metni engellemez; eksik zorunlu belge cached HTML ile geçilemez. Uzun metinler sessizce kesilmeden en çok altı 24.000 karakterlik bölümde değerlendirilir; tüm bölüm numaraları yanıtta doğrulanmadan öneri oluşmaz. Daha büyük veya okunamayan belgeler teknik hata olarak kalır.

Varsayılan liste doğrulanmış fırsatlardır. Ayrı “Doğrulama bekleyen fırsatlar” görünümü yalnız resmî, kaynakta gerçek açık başvuru kanıtı bulunan kayıtları içerir. Eksik alan açık gösterilir; onay, geri sayım veya takvim tarihi üretilmez. Kamu API’si ham belge/özel iletişim/onay kaydı içermez. Açıklık çelişkileri ve önceki yıllara ait tarihli duyurular bekleyen listesine alınmaz; sunucu gün hesabı Türkiye saatini kullanır. Aynı belge/sürüm için politika 6 incelemesi tekrarlanmaz.

## Veri karşılaştırması ve gerçek AI incelemesi

1.339 çağrı, belge hash’leri, onaylar ve kararlar yerel, yayımlanmayan yedeğe alındı; SHA256 yeniden okunarak doğrulandı. Yedek ve ham metinler Git/public/bulut derleme paketine girmez.

1.181 güncel sürüme bağlı eski karar için önce yayını değiştirmeyen karşılaştırma yapıldı. 628 “kapsam dışı” kararı açık dışlama hükmü olmayan alıntıya dayanıyordu; bunlar uygun ilan sayılmadan eksik kanıta ayrıldı. 890 kaynak belgesi beş gerçek Gemini Batch işinde politika 6 ile yeniden değerlendirildi; önceki web belgeleri kullanıldı. Önceden PDF hatası alan 24 yayımlanmamış kayıttan dört belge yeni ek Batch’e gönderildi; 20 erişim/metin hatası sürüyor. Altı yeni Batch işinin tamamı BATCH_STATE_SUCCEEDED/completed; bekleyen sıfır.

00.13 ölçümünde yayımlanan gerçek fırsat sayısı 39; yeni inceleme ek doğrulanmış ilan üretmedi. Bu sonuç ilan sayısını artırma başarısı olarak sunulmaz. Güncel 1.220 inceleme kararı: 753 eksik/geçersiz kaynak kanıtı, 167 Türkiye kanıtı eksik, 122 kapalı/geçmiş, 83 açık kapsam dışı, 29 asıl kaynak gerekli, 39 yayımlanmış, üç hedef kanıtı eksik, 20 zorunlu belge eksik, dört güncel tarih eksik. “Eksik kanıt” başvuruya uygun olmadığının kanıtı değildir.

## Test ve yayın

- Python tam paket: 310 PASS, son koşu 46.796 saniye.
- JavaScript: 17 PASS, son koşu97.4059 ms; bekleyen fırsata tarih verilse bile ICS üretmemesi dahil.
- Derleme/sözdizimi ve diff denetimleri geçti.
- Gerçek sonuç işi xhkss SUCCESS 2m3.82s; z5zx4 SUCCESS 1m1.77s.
- Son r13 backend: hibe-backend-00012-nvv, yüzde 100 trafik; iki ürün işi rules-r13-20261011 imajında. Backend build68c31fcc-dfc4-4d05-bbd6-048d001df8d3 ve refresh build5a169977-a24a-49b9-8c7b-c917da80aff5 SUCCESS. Hosting başarılı.
- Son gerçek bulut sonuç işi hibe-ai-batch-results-k7p6s SUCCESS17.79s, 2026-10-10T21:26:53Z. Önceki r11dtcgq SUCCESS23.74s.
- Son canlı API: calls200/39, pending200/3, sources200/154, anonim yönetim403. Bekleyenlerde tarih null; onay ve ham belge yok.
- Tarayıcı: varsayılan39, ayrı bekleyen3; açıklık çelişkili TEKNOFEST ve 2024 tarihli FEE duyurusu bekleyen listesine girmiyor. Detayda takvim düğmesi kapalı. Lise filtresi çalışıyor; mobil375px içerik375px, yatay taşma yok. Masaüstü ve açık tema kontrol edildi.
- Yeni HTML/eski JS önbellek uyumsuzluğu Hosting-önce-yayın ve kabuk dahil dosya sürümüyle giderildi. Mobil dört başvuran seçeneği iki satırda; stil dosyası sürümlü.
- Haftalık kaynak taraması Salı/Cuma08.15 Europe/Istanbul; saat05/35 yalnız mevcut AI sonuçlarını toplama. İki Scheduler ENABLED, yeni geliştirme heartbeat yok.
- GitHub CI commit/push sonrası ayrıca ölçülecek; bu rapordaki yerel ve canlı kanıt CI yerine geçmez.

Gerçek yönetici Google oturumu yeniden sınanmadı; yeni kimlik/onay üretilmedi. Kaynak kapsamı hâlâ 154 yönetim kaydı/131 çekici/135 gerçek envanter URL’sidir. 170 ayrı URL depoda bulunmadı; erişimi yasak veya belirsiz kaynaklar çalışıyor gösterilmedi.

## Geri dönüş

Önceki sağlam imaj registry-r7-20261010 ve önceki Git checkpoint eec636c205a73c2314f04e188105333160c84571 korunur. Veri yedeği `.agent/correction-backup.json`, doğrulama özeti `.agent/correction-backup.sha256` içindedir; bu özel yerel dosyalar yayımlanmaz. Geri dönüş yalnız imaj değiştirmek değildir: bu çalışmanın değiştirdiği çağrı/onay/öneri/kararlar mevcut sürüm kontrolüyle yedekten geri alınmalı, arada değişen kayıtlar ezilmemelidir. Geri dönüş uygulanmadı ve uygulanmış gibi gösterilmez.
