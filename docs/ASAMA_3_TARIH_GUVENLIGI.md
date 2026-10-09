# AŞAMA 3 — Tarih çıkarımı ve arşiv doğruluğu

2026-10-10, C:/hibe-radari, Codex. FEATURE doğrulaması geçti.

## Değişiklikler
`textutil.deadline_details`: 12 Türkçe ay, İngilizce/Almanca aylar, ISO ve sayısal tarih; başlangıç/bitiriş ayrımı, ay ve yıl eksikliği, çok aşamalı adaylar. Katlama konumları özgün kanıt metnine eşlenir.
`GrantOpportunity.apply_deadline`: day/month/unknown, alıntı/link/kontrol zamanı, adaylar ve açık revizyon geçmişi. Eksik bilgi önceki kesin günü silmez; yılı belirtilmeyen gün kesin tarih olarak saklanmaz. RSS/sabit sayfa/tarama ve detay çekicileri ortak işlevi kullanır. API adayları korunur.
`RelevanceFilter.evaluate` ve `collector.pin`: yalnız kesin geçmiş gün veya sayfa kapanış ipucu arşivleme sinyali üretir; eski kayıtta kapanış bilinmiyorsa inceleme gerekir. Çok aşamalı/şüpheli tarih kesin uygunluğa dönüşmez. Kapanış ipucu yönetici doğrulamasına tabidir.
`site.prepare/ics/when_html/utc_stamp`: belirsiz tarih geri sayım/ICS üretmez; ay bilgisinde gün bilinmiyor gösterilir; UTC dönüşümü gerçek saat dilimine göre yapılır.

## Kanıt
119 Python testi OK (10.341 s), 11 JS testi PASS, git diff --check temiz. Yeni tarih regresyonları 14 test. Eski kesin tarih testleri kanıtlı fixture ile korunmuştur; eski tarihsiz kaydın watch beklentisi MVP gereği review olarak düzeltildi. 127 korunan public/latest dosyasının SHA-256 karşılaştırmasında değişiklik yok.

## Sınır ve sonraki adım
Canlı tarama/yayın yapılmadı. Çok aşamalı adaylarda yakın gelecek günü öncelik sinyalidir; yönetici incelemesi gerekir. AŞAMA 5 kalıcı kayıt/onay köprüsü olmadan otomatik yayın kapısı açılmaz. AŞAMA 4 kimlik ve güvenli tekilleştirme ile yerelde devam.
