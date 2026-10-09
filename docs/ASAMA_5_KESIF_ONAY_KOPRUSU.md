# AŞAMA 5 — Kalıcı keşif ve yönetici onay köprüsü

2026-10-10 · C:/hibe-radari · Codex · FEATURE doğrulaması geçti.

## Uygulanan akış
`aggregator.bridge.persist_report` mevcut store records tablosuna discoveries/source_health yazar; calls taslaklarını oluşturur. Eski aynı URL + aynı başlıklı çağrının kimliği ve editör alanları korunur. Boş/başarısız yeniden tarama kayıt silmez; eksik tarih önceki kanıtlı günü silmez. Keşif geçmişi saklanır. Belge hash alanı keşif metadata hash'idir ve kind=discovery_metadata ile açıkça ayrılır; indirilen belgenin hash'i olduğu iddia edilmez.
`Service.save/approve/revoke` mevcut yetki kontrolünü kullanır. Yeni/önemli değişmiş keşif; resmî URL ve özgün kısa özet incelenip kaydedilmeden onaylanamaz. Onay içerik sürümüne ve incelenen keşif sürümüne bağlıdır. Aynı içerik tekrar görüldüğünde onay korunur; değişimde geri çekilir. Editör alanları yeni ham metinle ezilmez.
`domain.publishable` köprü şartını da denetler. `publication_report` yalnız güncel onaylı calls sürümlerini alır; `site.build` önceki yayın güvenlik kapısından geçirir. Ham latest.json onay kaynağı değildir. CLI yerelde mevcut SQLite data/demo.db; --store-db ile mevcut başka uygulama DB'si, --firebase ile mevcut App/Firestore kullanır. Ayrı toplayıcı veya veritabanı teknolojisi eklenmedi.
`/api/admin` keşif/sağlık kayıtlarını döndürür; arayüzde gözlem kanıtı, düzenlemeye alma ve onay geri çekme vardır. /api/revoke yetkili yöneticiyi gerektirir.

## Doğrulama
136 Python OK (10.800 s), 11 JS PASS, app.js sözdizimi ve diff-check geçti. 8 köprü testi: onaysız/güncel onay, aynı/değişen tarama, eksik/boş kayıt korunması, yetki/geri çekme, SQLite yeniden açma/geçmiş, editör özeti + resmî URL ile gerçek statik build, bozuk parti ön kontrolü, eski çağrı kimliği korunması. Windows SQLite dosyası finally ile kapatılır. 127 public/latest dosyası SHA-256 olarak AŞAMA 0 ile aynı.

## Açık sınırlar ve sonraki adım
Canlı Firestore, Google hesabı veya gerçek editör onayı bu aşamada doğrulanmadı; yeni deploy yok. DEMO kayıtları korunur. Üretim/deploy yetkisi ve DEMO ayrımı AŞAMA 9/10 RELEASE kontrolünde yeniden sınanacak. Veri/sayfa iki-artifact crash journal değerlendirmesi RELEASE öncesi açık. AŞAMA 6 kanıtlı üç değerli uygunluk motoru ile devam.
