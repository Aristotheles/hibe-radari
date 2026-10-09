# AŞAMA 1 — Yayın güvenlik kapısı
Mod: FEATURE · Yerel çalışma: C:/hibe-radari

## Uygulama
Cloud WIP 6cbda4d yerelde incelenip devralındı. Kaynak durumları success/partial/failed/suspicious_empty. Bozuk RSS reddedilir. Kısmi ve --only koşular ana latest yerine last-attempt raporuna gider. Yayın öncesi mevcut domain.validate/publishable sürüm onayı zorunlu. Mevcut aggregator kayıtları onay köprüsü kurulana kadar yeni site üretemez. Staging eksiksiz JSON/ilan/ICS kontrolünden sonra değiştirilir; geçiş hatasında eski ağaç geri alınır. Başarılı geçişte önceki ağaç backup olarak saklanır.

## Kanıt
94 Python test OK (7.420 s), 11 JS PASS. Eski 85 Python testi korunur; 9 yeni test onaysız/stale/kısmi/boş yayın, üretim/geçiş hatası, CLI ana veri koruma, rollback kopyası, bakım HTML, HTTP 503 ve atomik JSON yazma hatasını sınar. Git diff --check PASS. Gerçek yerel public ağacı ve latest başlangıç hashleri aynı.

## Sınırlar ve riskler
Tam onay köprüsü AŞAMA 5'te; yeni toplayıcı yayını şimdilik engellenir. Sunucu yetki akışı değişmedi; mevcut domain onayı kullanılır. İki dosya sistemi işlemi arasındaki süreç/elektrik kesintisinin journal ile toparlanması henüz yok; dosya yazma/geçiş istisnasında geri dönüş testli. Backup dosyaları otomatik silinmez. UI işaretlemesi değişmedi; gerçek tarayıcı/telefon kabulü bu backend değişikliğinde NOT RUN. Gerçek Auth/Firestore/Gemini/SMTP, ağ taraması ve canlı yayın NOT VERIFIED. Deploy yapılmadı: mevcut gerçek aggregator verilerinde sürüm onayı yok; yeni güvenlik kapısı bunu reddeder. Yeni bağımlılık/DB/backend yok. Sır/gizlilik/ödeme akışı değişmedi.

## Sonraki tek aşama
AŞAMA 2 — Ağ/tarama güvenliği ve kaynak sağlığı. Kullanıcı aşamalar arası onay beklemeyi kaldırdı; yerelde devam edilecek.
