# AŞAMA 7 — Tam kaynak kaydı ve sağlık paneli

2026-10-10 · C:/hibe-radari · Codex · FEATURE doğrulaması.

## Kapsam
135 envanter URL'si kayıpsız kaynak kaydına alındı; 30 eski ID/13 çekici korundu. 19 eski kapsam dışı kayıt silinmedi. Sayım docs/KAYNAK_SAYIM_UZLASTIRMA.md; bilinmeyen kurum/ülke adı uydurulmadı. Envanter etiketi/program referansı ve teknik host grup hiyerarşisi saklanır; resmî kimlik kanıtı kabul kartlarıyla tamamlanır.
`registry.inventory_rows/audit_sources` sabit 30 yerine canlı envanter URL kapsamını denetler. Eksik satır, ID çakışması ve hazır bayrağıyla kanıt atlama denetlenir. `complete=False` beklenen sonuçtur: registry kabulü tarama izni/fixture başarısı değildir.
Kaynaklarda ülke/kurum/program, grup/URL/yöntem, connector eşlemesi, erişim/politika, son başarı/hata/kayıt, değişiklik, periyot ve enabled/manual/engel durumu alanları vardır.
`Service.sources/set_source` yetkili açma-kapama ve sağlık görünümü sağlar. /api/source-settings kullanıcı için 403, yanlış değer için 400 döner. Ayarlar mevcut records deposuna kaydedilir; config kullanıcı düzenlemeleri ezilmez. CLI/collector bu ayarlara uyar. Kapalı bütün kaynaklar başarı/boş latest üretmez; suspicious_empty ile korunur. Pipeline da kapalı kaynakları manual_pending bırakır.
Sağlık kaydı parser hatasında önceki başarılı tarama/kayıt sayısını korur; admin alarmında son hata görünür. Son değişiklik sayısı ve manuel takip periyodu kayıtlıdır. Genel arayüzde sabit 30 iddiası kaldırıldı.

## Kanıt
152 Python testi OK (10.934 s), 11 JS PASS. Ek regresyonlar tüm URL/ID/13 eşleme koruma, yetkisiz toggle, başarısız kaynak alarmı, disabled kaynağın hiç fetch almaması, boş kapsam yayın koruma ve son sağlığın korunmasını sınar. app.js sözdizimi ve diff-check temiz.

## Açık sınır ve devam
AŞAMA 8 canlı kaynak kabul kartları/izin/fixture ve otomatik yola uygun çekiciler. Kurum adları/ülke null alanları ilgili resmî kaynak kanıtı bulununca tamamlanır. 135 kayıt entegre edildi diye 135 connected denmez. Gerçek admin Firebase oturumu ve RELEASE yayın denetimi henüz açık.
