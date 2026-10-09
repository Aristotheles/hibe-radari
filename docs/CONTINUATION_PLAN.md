# Hibe Radarı — sıradaki çalışma

Yerel kök: `C:/hibe-radari`. Aynı geliştirme dalı: `codex/cloud-handoff-20261010`. Kod checkpoint'i `ef89d9cb80d3b872a40048684aa37b7f96381e5a`, GitHub'a gönderildi; main değişmedi. Yerel tam203Python/11JS PASS. Güncel ölçüm ve test kanıtları `.agent/HANDOFF.md` içinde; bu belge ikinci bir güncel durum kaynağı değildir.

## Devralma

1. Ortak ajan protokolü, güncel devir, MVP ve Obsidian proje kaydını oku. Git durumu/farklar, çalışan test veya sunucu süreçleri ve kısa/haftalık kota kalanını ölç. Başka ajan başlatma, Cloud geliştirme kullanma, main merge yapma.
2. Herhangi bir kota kalan<=%5 ise geliştirme başlatma; bu kullanıcı tarafından istenen kota duruşudur. Aktif15dkheartbeat kota yeniden uygun olduğunda aynı kayıttan devam eder. Süren gerçek CI/test handle'ını yeni süreç başlatmadan ölç.
3. Checkpoint uzak SHA ve GitHub Tests sonucunu ölç. İlk run `38006766526` bu kod checkpoint'ine aittir; bir job veya aynı kodun yerel sonucu bütün uzak matrisi PASS yapmaz. Belge commit'i sonrası oluşan yeni run'ı ayrı tanımla. Hata varsa başarısız job logundan kök nedeni düzelt ve aynı kontrolü yeniden çalıştır.

## Sıradaki tek ana adım: AŞAMA9 gerçek giriş

Yetkili gerçek hesapla Firebase Auth Google provider, gerçek yönetici UID ve backend ADC/Firestore erişimi doğrulanmalı. Kullanıcıya gereken hesap/UID sorusu zaten iletildi; aynı soruyu rutin biçimde tekrar sorma. Kamuya açık WEB SDK ayarı `.agent/firebase-web-config.json` içinde, sır değerleri Git/Obsidian'a taşınmaz. `hibe.server --check` yalnız yapılandırma ön kontrolüdür; hazır sonucu gerçek giriş veya Firestore yetkisi kanıtı değildir.

Gerçek Google tokenıyla ziyaretçi/normal kullanıcı/admin uçları; revoked/expired token, doğrulanmamış veya Google dışı giriş, admin UID eşleşmesi ve ücretsiz Pro ihracı engeli sınanır. Test-admin, DEMO oturumu veya uydurma UID bunun yerine geçmez. Gerçek ödeme kapalı kalır; ek sağlayıcı/ücretli altyapı kararı uydurma.

Erişim beklerken bağımsız eski kaynak kabulü sırayla ilerletilebilir: TÜBİTAK4000/duyuru, Gençlik Köprüsü, BritishCouncil, sabit izleme. Önce resmî sayfa/şartlar/robots ve gerçek arayüz kanıtı; sonra mevcut connector/fixture/sağlık testleri. STGM incelenen sayfalarında açık tarama/yeniden kullanım kabulü bulunmadı; manuel rota, Agora2926/2026resmî kanıtı korunur. Hiçbir kaynağı silerek, gizleyerek veya izin var sayarak tam koşu üretme. Yeni collector/DB/proje kurma.

## AŞAMA10 kabul sırası

1. Aynı kaynak kapsamıyla iki başarılı tam canlı staging koşusu ve HTTP hata/bozukRSS/only denemesi. 22RSSfixture pilotunu29canlıkaynak pilotu diye sunma. İnsan onaylı sürüm ve önceki sağlam HTML/JSON/ICS/latest korunmalı.
2. Mevcut barındırma ve backend için tek zamanlama yöntemi kur/doğrula. `--scheduled` periyot kodu mevcut; yalnız alt küme geldiğinde tam snapshot sayılmaz. Son kontrol tarihi/cache tazeliği uydurma; trafik/çakışma ve kaynak kapatma davranışını ölç.
3. Gerçek backend/Firestore/SMTP/abonelik, üretim insan onayı ve RELEASE matrisi. Hosting config yalnız statik site içerir; API rewrite/backend konumu doğrulanmadan üyelik canlı ilan edilmez. Secret backend ortamında; model gemini-3.8-flash, çalışmazsa mevcut kurallı inceleme fallback.
4. RELEASE ve yayın/onay kapıları geçtiyse kullanıcı deploy yetkisini kullan: yeni ön-yayın yedek/manifest, güvenli build/deploy, canlı JSON/kart ve kaynak/tarih sayısı kontrolü. Hosting rollback gerçek kabulünü ölç. Geçmezse eski canlı siteyi koru ve kesin engeli kaydet.

Her anlamlı adımın test/kanıt/sınırı MVP/devir/Obsidian'a yazılır ve yeniden okunur. Rutin aşama sonunda onay beklenmez; yalnız gerçek hesap veya insan onayı gereksinimi otomasyonla uydurulmaz. Tüm gereksinimler kanıtlanmadan goal complete denmez.
