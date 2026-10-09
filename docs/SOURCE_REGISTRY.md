# Kaynak envanteri

Hedef 30 korunur. Özgün Hibe Radarı dokümanı mevcut aramada bulunamadı. config/sources.json konuşmada geçen 19 doğrulanmamış isim ve 11 bekleyen yer içerir. Bunlar özgün listenin yerini almaz. URL'ler uydurulmadı. Hiçbir kayıt otomatik tarandı diye gösterilmez.

Tam doküman verildiğinde Markdown buraya aktarılacak, gerçek ID/URL/erişim/kontrol yöntemi config'e işlenecek. Kaynaklara özgü liste parser'ları ve boş liste/hata testleri tamamlanmadan otomatik kaynak hazır sayılmaz.

## 9 Ekim — aşama 3 hazırlığı

Arayüz adımının ardından 30 kayıt internetsiz denetlendi. Kayıtlar silinmedi veya yeniden adlandırılmadı; 19 isme `identity_status: candidate`, 11 boş yere `identity_status: missing` eklendi. Hepsinin `status: registry_pending` ve URL/kontrol tarihi boş kalır. Bir kaydın `method: manual` olması, gerçekten kontrol edilmiş olması anlamına gelmez.

- `python -m hibe.registry`: kayıt ve eksik raporu; herhangi bir ağ isteği yapmaz.
- `python -m hibe.registry --strict`: eksik kaynak varken çıkış kodu 1 verir; bu mevcut envanterde beklenen sonuçtur.
- `python -m hibe.registry --markdown`: [SOURCE_CHECKLIST.md](SOURCE_CHECKLIST.md) içindeki 30 satırlık raporun içeriğini üretir.

Özgün belge konumu, kimlik doğrulama kanıtı ve resmî URL gerekir. Manuel kayıt için `manual_check.url` ve anlaşılır `manual_check.steps`; otomatik kayıtta `type: official`, `allowed_hosts`, izinli HTTPS `call_urls` ve belge URL'leri gerekir. `last_checked` gerçek kontrol olmadan doldurulmaz. Audit URL'ye bağlanmaz; biçim denetimi gerçek site/kontrol/fixture doğrulaması değildir. CLI'nin `complete` alanı yalnız kayıt alanlarının tamlığını anlatır; MVP aşama kabulünü tek başına sağlamaz.

Manuel fixture testleri kurgusaldır. Özgün 30 kaynak belgesi bulunmadan kaynaklara özgü gerçek parser fixture'ları üretilemez. Yerel aramada proje belgeleri ve iki Hibe-Radari-Codex ZIP'i incelendi; özgün liste bulunmadı. Diğer kişisel dosyaların içerikleri taranmadı. Kullanıcıdan belge yolu/bağlantısı istendi.
