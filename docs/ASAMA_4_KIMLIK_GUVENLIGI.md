# AŞAMA 4 — Kimlik ve güvenli tekilleştirme

2026-10-10 · Yerel C:/hibe-radari · Codex · FEATURE doğrulaması geçti.

## Uygulama
`models.canonical_url` çağrı query alanlarını, boş değerleri ve standart dışı portu korur; yalnız utm_* / fbclid / gclid temizlenir. Query sırası normalize edilir. HTML liste/kart/tarama bağlantıları query bilgisiyle saklanır.
`GrantOpportunity.id` resmî kimlik/otorite/program/dönem/başvuru yolu ve ortak ana sayfalarda başlık bağlamını taşır. EU API identifier alanı resmî kimliktir. Başlıktaki yıl açık dönem çatışmasını ayırır; bilinmeyen dönem tahmin edilmez.
`collector.dedupe` kimlik çatışmasını engeller. Ayrıntı alias zinciri kanıtlı bağlantı ve aynı başlık bağlamıyla eşleşir; genel ana sayfa alias değildir. Benzer başlık otomatik birleşmez, duplicate_candidates inceleme sinyali oluşturur. Kaynaklar/provenance/tarih alıntıları/adaylar/geçmiş kaybolmaz; çelişen kesin tarih review gerektirir.

## Kanıt
128 Python testi OK (10.268 s), 11 JS PASS, git diff --check temiz. Dokuz yeni kimlik regresyonu: query id/ref, ana sayfa dönemleri, 3 kaynaklı alias zinciri, kesin tarih aktarımı, kanıtsız link, başlık sinyali, çelişen tarihler, resmî kimlik/başvuru yolları, eksik dönemin iki dönemi köprülememesi, HTML query korunması (aynı test dosyasında 9 yöntem).
127 public/latest dosyasının SHA-256 değeri AŞAMA 0 ile aynı. Canlı yayın yapılmadı.

## Sınır ve devam
Başvuru bağlantısı henüz resmî uygunluk kanıtı değildir. Başlık benzerliği için mevcut standart kütüphane kullanıldı; bağımlılık eklenmedi. Yeni kimlikleri eski kalıcı kayıtlarla eşleme AŞAMA 5 köprüsünde korunacak. AŞAMA 5 kalıcı keşif ve gerçek yönetici onayı ile devam.
