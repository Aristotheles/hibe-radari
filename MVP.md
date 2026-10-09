# Hibe Radarı — Codex geliştirme sözleşmesi

Sürüm 2 · 9 Ekim 2026 · Son kullanıcı kararları 1.0 planının önüne geçer.

## Kesin kapsam

- İlk sürüm 30 kaynak; üçe düşürülmez. Her kaynak otomatik veya görünür manuel kontrol yolu taşımalı.
- Abonelik, Google giriş, tema tercihleri ve haftalık e-posta ilk sürüm hedefidir.
- Yönetici senoltemur@gmail.com; Firebase proje sahibi ana bilgisayardaki başka Gmail olabilir.
- Admin paneli çağrı/kanıt incelemesi, onay, kaynak sağlığı ve büyüme sayılarını içerir.
- Kullanıcı verisi Firebase Auth + Firestore; kamu sayfası hafif HTML/CSS/JS. Flutter kaldırıldı.
- Gemini modeli gemini-3.8-flash; API anahtarı sunucuda. Sahte çıkarıcı ve bellek deposu testlerde kullanılır.
- Pro özellikleri/ödeme sonraki sürüm; kullanıcı tier=free olarak başlar.
- Kaynak, Çağrı, BaşvuruYolu, Profil, TaramaÇalışması beş domain nesnesidir; kullanıcı/outbox kayıtları uygulama verisidir.
- Düz zorunlu koşullar, üç değerli mantık, kanıt konumu. Alternatifler tek koşulda korunur; belirsiz yorum başarılı sayılmaz.
- Uygunluk ile öncelik ayrı; LLM güveni puana girmez.
- Sayfa veya bağlı PDF normalize hash değişince tüm çağrı yeniden inceleme ister.
- Yerel approvals/ export'u vardır. Admin paneli gerçek modda onayı veri deposunda tutar; tam Git yayın workflow'u henüz yapılmadı. Otomatik commit onay sayılmayacak.

## Puanlama başlangıcı

Rol 40: doğrudan/öğretmen 40, ortak 25, uygulama yeri 15, belirsiz 10.
Tema 35: benzersiz eşleşen tema ağırlık toplamı ×5, tavan 35.
Zaman 25: 14–90 gün dahil 25; 0–13 gün 15 ve acil görünümü; >90 gün 10; tarih bilinmiyor 5; geçmiş öneri dışı.
Alt puanlar başlangıç uygulama önerisidir; kullanıcı ayarlayabilir. Uygun değil yol yüksek tema puanıyla uygun olamaz.

## Aşamalar ve ölçülebilir kabul

| Aşama | İş | Durum / kabul |
|---|---|---|
| 1 | Saf domain, düz koşullar, hash, bellek/yerel depo | Kodlandı; internetsiz testler geçti |
| 2 | Yerel ilan/admin/abonelik dikey akışı | Yerel demo arayüzü geliştirildi; 28 Python + 5 JS testi ve ziyaretçi/kullanıcı/yönetici tarayıcı akışları geçti; canlı giriş/gönderim kapsam dışı |
| 3 | Tam 30 kaynak | 19 doğrulanmamış isim + 11 eksik yer; özgün doküman ve gerçek URL/parser gerekli |
| 4 | Tarama ve Gemini | Güvenli fetch, bağlı belge hash'i, sıralı pipeline ve gerçek/fake çıkarıcı kodlandı; canlı test bekliyor |
| 5 | Google/Firebase | SDK/token doğrulama ve Firestore adaptörü kodlandı; gerçek proje/UID ve emulator testi bekliyor |
| 6 | Haftalık bülten | Outbox, SMTP kodu ve imzalı çıkış kodlandı; gerçek gönderim/teslimat testi bekliyor |
| 7 | Git/static yayın ve zamanlama | Statik HTML/JSON export var; ayrı güvenli yayın/cron job kurulacak |
| 8 | Canlı kabul | 30 kontrol yolu, gerçek 10 etiketli belge, 2 haftalık pilot, restore/rollback, veri metinleri gerekli |

Aşama 3 bütün 30 kaynağı kapsar; '3 kaynak tamam, MVP hazır' kabulü yoktur. Kaynak ismi/URL eksikliği diğer bağımsız işleri durdurmaz, 30 kaynak tamamlandı iddiasını engeller.

## Mimari sadeliği

Arayüzler ihtiyaç kanıtlanınca eklenir. Şimdilik bellek/SQLite/Firestore depoları ortak get/put/all sözleşmesini uygular; extractor fake/Gemini sözleşmesi extract'tir. Yayın ve maliyet için tek uygulamalı soyut katman yok. Saat testlere callable olarak enjekte edilir.

Firestore, kullanıcının abonelik kararından dolayı geri geldi. Admin paneliyle veri deposuna onay kaydı yazılması seçilmiş başlangıç uygulamasıdır; aynı süreçte yazma kilidi var. Birden fazla instance/tarayıcı çalıştırılacaksa conditional write/transaction şartı tekrar değerlendirilir.

## Codex Desktop devam istemi

Bu klasörü aç. README.md, MVP.md ve docs/SECURITY.md dosyalarını oku.
Önce `python -m unittest discover -s tests -v` çalıştır.
30 kaynak kapsamını azaltma. Kullanıcının özgün Hibe Radarı kaynak dokümanını
getir; yoksa kalan kayıtları uydurma. Sonraki görev bütün 30 kaynağın
kimlik/URL/kontrol yöntemini tamamlamak ve kaynaklara özgü fixture testleri.
Daha sonra gerçek Firebase projesi ve ADMIN_UID ile Google giriş pilotu yap.
GEMINI_MODEL gemini-3.8-flash kalacak, secret istemciye gitmeyecek.
Kullanıcı API anahtarlarını sohbet veya Git'e yapıştırmasın.
Her görev sonunda çalışan testleri, açık engelleri ve sonraki tek işi bildir.
Kurulmamış entegrasyonu tamamlandı sayma; e-posta veya deploy için oturum
kapsamındaki gerçek yetki ve ortam yapılandırması gerekir.

## Gerçek doğrulama kaydı

9 Ekim 2026: 26 unit/HTTP test geçti. JS module sözdizimi kontrolü geçti.
Statik export üretildi. Playwright kurulu fakat Chromium executable yok;
görsel ekran ve tarayıcı etkileşim doğrulaması yapılamadı.
Firebase, Gemini ve SMTP canlı denenmedi. Ürün henüz canlı MVP kabulünde değil.

9 Ekim 2026, sonraki arayüz oturumu: Lovable danışmanlık önerileri mevcut HTML/CSS/JS uygulamasına uyarlandı. Kalıcı DEMO, rol bazlı gezinme, açık rol seçimi, Türkçe tema araması, filtre/sıralama, kanıt ayrıntısı, uygunluk/öncelik ayrımı, abonelik ve onay mesajları eklendi. Kaynak dosyasının Windows UTF-8 okuma hatası düzeltildi. 28 Python ve 5 JS testi geçti; yerel kullanıcı/yönetici etkileşimleri ile masaüstü ve emüle mobil görünüm incelendi. Önceki “görsel test yapılmadı” kaydı bu yerel kapsam için güncellendi. Kanıt: docs/UI_VERIFICATION.md. Sıradaki aşama 3: tam 30 kaynak; özgün liste henüz mevcut değil.
