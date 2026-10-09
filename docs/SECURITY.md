# Güvenlik ve canlıya çıkış sınırı

Demo yalnızca 127.0.0.1'e bağlanır; rol seçimi gerçek modda kapalıdır. Gerçek Firebase ID token revoke kontrolüyle doğrulanır. Google sağlayıcısı ve doğrulanmış email gerekir; yönetici ADMIN_UID'dir. Firestore istemci erişimi kapalıdır; Admin SDK için ayrıca IAM gerekir.

Onay hash bağlı; eski ekran reddedilir. Süreç içi yazma kilidi çok instance ve eşzamanlı tarama yazmasını korumaz. Üretimi çoğaltmadan conditional write/transaction eklenmeli. approvals/ yerel dosyalar audit export'udur; otomatik Git commit yapmaz.

İçerik textContent/HTML escape ile render edilir. Güvenli fetch yalnız izinli HTTPS domain ve global IP; IP pinleme/TLS asıl host doğrulaması; byte/page limiti ve redirect reddi kullanır. PDF için ayrı işlem süre/bellek limiti henüz yok; küçük ve güvenilen dosyalarla pilot yapılmalı.

LLM araç/secret okuyamaz. Email/telefon maskelenir; kişi adları için tam maskeleme henüz yok. Girdi güvenilmeyen veri. Kanıt konumu insan tarafından doğrulanmalıdır; testler model doğruluğunu garanti etmez.

İmzalı süreli unsubscribe bağlantısı GET ile silme yapmaz; POST onayı ister. Outbox hafta/kullanıcı tekilleştirmesi vardır. SMTP sending/uncertain kayıtları elle mutabakat ister; çok işçi gönderim desteği yok.

Canlıya geçmeden: veri envanteri/aydınlatma/saklama/silme/yurt dışı aktarım değerlendirmesi, HTTPS ve güvenli sunucu, rate limit, Google/Firestore emulator ve gerçek auth testi, SMTP domain ve teslimat testi, tam 30 kontrol yolu, yedek/geri yükleme, rollback, gizli anahtar taraması tamamlanmalı.

Bu paket bir geliştirme başlangıcıdır; kontroller tamamlanmış güvenli üretim iddiası yoktur.
