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


## 2026-10-10 02:07 — AŞAMA 8 tüm URL erişim ölçümü ve RSS paketi
135 envanter URL'si gerçek güvenli istemciyle tek sayfa ölçümünden geçti: 93 okunabilir, 42 hata. Bütün kartlarda gerçek page_observation var; HTTP 200 tek başına izin/entegrasyon kabulü değildir. Kaynakların robots/TLS/host sınırları gevşetilmedi.
Mevcut altı RSS (ab-ilan iki akış, eTwinning, Institut français, TÜSEV, Sivil Sayfalar) tekrar ölçüldü ve kısa metadata fixture'ları eklendi. TÜSEV valid boş RSS; kurum genelinde fırsat yok denmedi. Eurodesk Finder ve Interreg NEXT MED, ardından Mercator/IKI/GEF SGP/ISEF/T4/Global Schools/Roots & Shoots/Opportunity Desk/Opportunities for Youth/EU Calls gerçek yayımlanmış RSS arayüzleri mevcut feed çekicisine eklendi. Toplam 29 yapılandırma, başlangıçtaki 13 ID korunur. GEF SGP valid boş akış; Sivil Toplum için Destek akışı bozo olduğundan kabul edilmedi.
Eurodesk 576 kayıtta ortak link ve farklı GUID döndürüyor. GUID kaynak kayıt kimliği olarak korunur; ortak linkten kayıtlar yanlış birleşmez. GUID adresleri yalnız genel JavaScript kabuğu döndürdü, doğrulanmış ayrıntı URL'si sayılmadı. Ortak oluşturulmuş pubDate çağrı yayın tarihi olarak kullanılmaz. Gerçek çağrı/tarih/uygunluk/yönetici onayı hâlâ gereklidir; haber veya kurum sayfası açık çağrı değildir.
163 Python PASS (15.549 s), 11 JS PASS, diff-check PASS; 127 public/latest SHA-256 aynı. AŞAMA 8 aktif; kalan liste/detay/politika kabulü tamamlanmadan AŞAMA 9'a geçilmedi. Kullanıcı kesin kuralı devam eder: rutin aşama onayı bekleme; yalnız kota <=%5 veya gerçek kullanıcı girdisi engeli checkpoint gerekçesidir. Deploy/main merge yapılmadı.


## 2026-10-10 02:11 — AŞAMA 8 kaynak yolları ve ilk paket kabulü
Envanterdeki 135 URL'nin hepsinde gerçek erişim gözlemi, yöntem, periyot ve görünür kabul/manuel inceleme gerekçesi var; yönetici kaynak satırları kabul kartlarıyla eşitlendi. Bunların tümü connected değildir. İlk pakette dört MEB RSS'si, OGM tarihli ayrıntı örneği, Eurodesk Finder GUID ayrımı ve Ulusal Ajans gerçek liste/kapalı başvuru ayrıntısı testli. Ulusal Ajans yeniden erişildi: 200; önceki timeout kaydı tarihsel ölçüm olarak korunur. 13 Ekim toplantı günü ile 7 Ekim son başvuru ayrıldı. Otomatik kullanım koşulları doğrulanamadığı için UA manuel; Eurodesk Türkiye/ Terra Viva robots nedeniyle manuel, SALTO ticari dağıtım ön izni gerekir.
29 aggregator yapılandırması, orijinal 13 ID korunur; bağlanan her yeni RSS kısa gerçek fixture ve tekrar/hata/boş testleriyle ölçüldü. Geçerli boş TÜSEV/GEF akışı kurum genelinde fırsat yok demek değildir. Eski çağrı ID formülünü GUID olmayan kayıtlar için koruyan regresyon eklendi; yeni GUID alanı eski kayıtları yeniden kimliklendirmez.
168 Python PASS (15.690 s), 11 JS PASS; diff-check temiz; 127 public/latest hash aynı. AŞAMA 8'in MVP kapsamındaki envanter/ilk paket/testli metadata ve dürüst manuel yönlendirme işleri doğrulandı. Her kaynakta otomatik açık çağrı veya Türkiye uygunluğu kanıtlanmış değildir; bunlar yönetici inceleme kuyruğunda kalır, yayın kapısı açılamaz. AŞAMA 9 kullanıcı deneyimi ve üyelik çekirdeğine yerelde geçiliyor; aşama onayı beklenmez. Main merge/deploy yok.


## 2026-10-10 02:48 — EU API resmî politika ve eksik sayfalama
Kaydı hazırlayan: Codex. Resmî [API dokümanı](https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/support/apis) haricî sistem kullanımını açıkça yayımlar; [Komisyon yeniden kullanım bildirimi](https://commission.europa.eu/legal-notice_en) EU-owned içerik/atıf ve üçüncü taraf istisnalarını açıklar. Mevcut eu-ft politika allowed bu dar üstveri kapsamıyla kaydedildi; registry/kabul kartı api_interface_verified, çağrı ayrıntısı/ülke/insan onayı hâlâ açık. Yeni kaynak veya ikinci collector oluşturulmadı.
Gerçek mevcut Fetcher TLS/robots/policy yoluyla iki canlı ölçüm aynı15üstveri kaydı,3istek ve source health success verdi; run --only kapsamı partial. Yalnız .agent/source-audit/eu-policy-probe.json yazıldı; DB/onay/public/latest değişmedi. İki yapılandırılmış sorgu dışındaki tüm merkezî çağrıların alındığı iddiası yok.
eu_ft.collect önceden yalnız pageNumber1 alıyordu. Artık toplam/sonsayfa ile sonraki sayfalar alınır; tekrar sayfa/çelişkili toplam/şema/erken boş/sayfa tavanı hata ve mevcut yayın korumasına gider. Tavan10sayfa,50kayıt/sayfa;24saatperiyot. Dört yeni regresyon, mevcut40aggregator ve12registry+2kabul testi PASS; ilk yeni test Fetcher context manager desteklenmediği için test düzeneği hatası verdi, mevcut close() yoluyla düzeltilip tekrar PASS. Tam200Python PASS (62.010s), önceki11JS PASS; diff-check PASS. Kanıt .agent/eu-policy-tests.txt;127korunanSHAaynı. RELEASE hâlâ NOT VERIFIED: gerçek Auth/ADC/admin UID/backend/zamanlayıcı/tamcanlıpilot/deploy açık.
Sonraki tek adım kalan eski kaynak politika/erişim kabulünü resmî kanıtla ilerletmek; gerçek Auth kullanıcı sorusu bekliyor. Goal active; rutin aşama duruşu yok.


## 2026-10-10 02:53 — STGM gerçek tarih çelişkisi ve manuel kabul
Kaydı hazırlayan: Codex. [STGM listesi](https://www.stgm.org.tr/hibe-duyurulari) Agora kartında07.10.2926 gösteriyor; [ayrıntı](https://www.stgm.org.tr/demokrasi-burs-programi-agora-icin-basvurular-basladi) ve [özgün Böll sayfası](https://tr.boell.org/tr/agora-demokrasi-burs-programi) son tarihi7Ekim2026 ve üniversite başvuru koşullarını doğruluyor. Bu tarih10Ekimde geçmiş; lise çağrısı veya açık2926çağrısı sayılmaz. Kaynak kısa gerçek alıntı fixtureJSONda, HTML fixture diye sunulmadı. Kart onaylanmadı/yayımlanmadı.
html_cards.collect_cards bugün+10yıl ötesini tahminle düzeltmez: deadlineNone/unknown/review_required; özgün aday/alıntı/kaynak/kontrol zamanı korunur. Bu eşik inceleme sezgisidir, her uzun vadeli çağrıyı yanlış ilan etmez. Geçersiz gün de kanıtını korur; gerçek2028tarih kesin kalır. Resmî alıntıyla apply_deadline gerçek2026-10-07ye çözer; bu çözüm yeni canlı DB kaydı değildir.
İncelenen liste ve [çerez politikası](https://www.stgm.org.tr/cerez-politikasi) otomatik tarama/yeniden kullanım iznini açıkça doğrulamıyor; bütün sitede izin yok iddiası yapılmadı. STGM unreviewed/manual_pending korunur, politika/kabul/registry kanıtı eşlendi. Hiçbir eski connector silinmedi veya gizlenmedi.
FEATURE: tam202Python PASS (66.341s); ardından yeni gerçek kanıt testi dahil hedefli3PASS ve güncellenmiş config kabul2PASS, eski aggregator40PASS; JS değişmedi önceki11PASS. Son test eklenmesinden sonra tam203koşusu henüz yok. Kanıt .agent/stgm-date-tests.txt/.agent/stgm-aggregator-tests.txt; diff-check PASS, public/latest127SHA aynı. AŞAMA9 Auth/ADC/admin UID sorusu bekler; RELEASE NOT VERIFIED, deploy yok.
Sonraki tek adım kalan eski kaynak politika/erişim kabulü; rutin onay beklemeden bağımsız çalışma sürer.
