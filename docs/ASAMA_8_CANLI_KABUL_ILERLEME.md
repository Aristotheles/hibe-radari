# AŞAMA 8 — Canlı kaynak kabul ilerlemesi

2026-10-10 · Aktif çalışma; aşama tamamlanmadı.

135 URL için kabul kartı config/source_acceptance.json içinde oluşturuldu. Karttaki fixture/örnek çağrı/test alanları gerçek kanıt bulunana kadar null; kayıt oluşturmak connected anlamına gelmez.

İlk inceleme: Ulusal Ajans web timeout, robots 404; Eurodesk Türkiye ana sayfa/news açıldı fakat robots adresi 200 HTML hata sayfası; Opportunity Finder web timeout; Terra Viva web okuyucuda açılamadı, robots yönlendirmesi izinli host dışında engellendi. Bunlar kaynakların küresel olarak bozuk olduğu iddiası değildir; bu ortamın ölçümüdür. TLS/host denetimi gevşetilmedi.

SALTO liste açıldı. Resmî kullanım şartları https://www.salto-youth.net/about/legal-notice/ eğitim alanındaki atıflı dağıtımı destekliyor fakat ticari dağıtımı önceden yazılı izne bağlıyor. Ücretsiz/Pro hedefi nedeniyle otomatik yayın permission_required; kaynak görünür, silinmedi. Robots içindeki wildcard query kuralları dikkate alınmalıdır.

Canlı ölçüm iki istemci hatasını açığa çıkardı: robots yerine 200 HTML kabulü ve wildcard Disallow deseninin sessiz atlanması. net.py düzeltildi; 13 ağ testi PASS (1.166 s), yeni iki regresyon HTML sahte başarı ve wildcard query yasağıdır. Tüm test koşusu ve AŞAMA 8 diğer kaynak paketleri henüz tamamlanmadı. Ölçüm ham kaydı .agent/source-audit/first-package-robots.json.

Sıradaki tek adım: İlk paketin MEB ve erişim/izin durumu belirsiz diğer adreslerini doğrula, uygun olanın gerçek liste/detay fixture'ını al; ardından mevcut 13 kaynak ve devam paketlerinin kabul kartlarını tamamla. Sonraki katmana henüz geçilmedi.


## 2026-10-10 — AŞAMA 8 ilk kaynak dilimi
MEB AB/Dış İlişkiler ve YEĞİTEK, resmî ana sayfalarında yayımlanan RSS URL'leriyle mevcut feed çekicisine eklendi. Gerçek istemci strict TLS/robots kontrolüyle ikisinde 200, geçerli rss20, 50 kayıt doğruladı. İki kısa gerçek üstveri fixture'ı; tekilleştirme ve HTML/boş akış hatası testleri mevcut. İlanların çağrı/uygunluk/onay statüsü hâlâ inceleme gerektirir; kurum haberine açık çağrı denmedi. Mevcut 13 çekici aynı ID'lerle kalır, toplam 15 yapılandırma; baseline_source_ids 13'ü kaydeder.

157 Python OK (11.509 s), 11 JS PASS; son app.js syntax ve diff-check temiz. Robots HTML 200 ve wildcard/percent-encoding engel regresyonları eklendi. 135 kabul kartından 10'u erişim/politika gözlemi taşıyor; yalnız iki yeni RSS çekicisi fixture testli. Detay fixture/kanıtlı son tarih ve diğer paketler açık; AŞAMA 8 tamamlanmadı. Ana public/latest korunuyor.


## 2026-10-10 — AŞAMA 8 dört MEB kaynağı
OGM ve Meslekî Teknik Eğitim RSS'leri gerçek istemcide 200/rss20/50 kayıt; mevcut feed çekicisine meb-ogm/meb-mtegm olarak eklendi. Toplam 17 yapılandırma, başlangıçtaki 13 ID korunur. OGM GençBizz gerçek ayrıntı URL'sinden 2026-10-16 son tarihi çıkarıldı ve kısa alıntılı fixture/regresyonla doğrulandı. AB/Dış İlişkiler ve YEĞİTEK ayrıntıları 200; kesin tarih çıkarılamadığı için unknown ve review_required korunur, kısa başlık fixture'ları tam metin kopyası değildir. Kaynak fixture'larındaki duyurular otomatik yayımlanmadı; haber ile açık çağrı ayrımı editör kontrolünde.
159 Python OK (11.977 s) + 11 JS PASS; diff-check temiz. 127 public/latest dosyası SHA-256 aynı. AŞAMA 8 açık: MTEGM detay, ilk paket diğer kaynakları, mevcut 13 çekici canlı kabulü ve devam paketleri. AŞAMA 9'a geçilmedi; sıradaki tek adım kaynak kabul kartlarını testli paketler halinde sürdürmek.
