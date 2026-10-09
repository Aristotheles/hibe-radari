# Hibe Radarı — sürekli toplama ve güncel yayın çözümü

Durum: Codex teknik önerisi; kurulum veya otomatik yayın yapılmadı.
Kapsam: Kullanıcının 9 Ekim 2026 tarihinde bu sohbette verdiği sekiz kaynak grubu. Önceki 30 kaynak MVP taban kapsamıdır; yeni liste üç kaynağa veya yalnız 13 mevcut bağlayıcıya indirilmeyecek. Kaynak sayısı kurum/program/akış ayrımı yapılarak ölçülecek; tümü bağlı iddiası yok.

## Önerilen tek rota
Mevcut Python httpx + BeautifulSoup + feedparser toplayıcısı → Cloud Run Job → Firestore → onaylı statik üretim → mevcut Firebase Hosting.
Cloud Scheduler işi düzenli tetikler. Toplama ve yayın ayrı adımlardır; veri değişmese bile tarih/geçerlilik her gün yeniden hesaplanır. Yönetici incelemesi mevcut yerel demo panelinden kendiliğinden canlıya taşınmış sayılmaz; gerçek Google giriş ve yetki kontrolüyle ayrıca bağlanır.

## Kaynak kapsamı
1. AB merkezi: Funding & Tenders; Erasmus+ ve sonuç platformu; Türkiye Ulusal Ajansı; Eurodesk TR/Opportunity Finder; ESEP/eTwinning; Gençlik Portalı/ESC; SALTO/Otlas; EACEA; Creative Europe/LIFE; MSCA/Ufuk Avrupa TR; EIT/NEB/İklim Paktı; Code Week/Scientix/European Schoolnet; EYF/Anna Lindh.
2. AB–Türkiye/sınır ötesi: Delegasyon, AB Başkanlığı, Jean Monnet, CFCU, Sivil Düşün, Etkiniz, Interreg NEXT Karadeniz/MED.
3. Türkiye kamu: TÜBİTAK/Bilim ve Toplum/BİLİMİZ; MEB ilgili genel müdürlükleri; Kalkınma Ajansları/KAYS/DOKA/DOKAP; GSB; Sivil Toplumla İlişkiler; TEKNOFEST/T3/Sıfır Atık; UNESCO TR/TÜRÇEV/Eko-Okullar.
4. Ülkeler/ikili: Avustralya DAP; Kanada CFLI; Japonya GGP/Japan Foundation; ABD elçilik/Grants.gov/Fulbright/YES; İngiltere BC/elçilik; Almanya Gençlik Köprüsü/PAD/PASCH/Goethe/DAAD/elçilik/Mercator/Bosch/Böll/FES/IKI; Fransa IF/elçilik; Hollanda/İsveç/Finlandiya/İsviçre/Avusturya OeAD; KEİ/GMF; diğer ülkeler için Dışişleri dizini keşif kaynağı.
5. BM: UNDP TR/ilanlar/GEF SGP; UNESCO ASPnet/ödüller; UNICEF TR; UNDEF; UNEP Young Champions.
6. Türkiye vakıf/STK: Sabancı/Koç/TEGV/ÖRAV/Öğretmen Ağı/ERG/TEMA/WWF/TÜSEV/Destek Vakfı/Turkey Mozaik/İhtiyaç Haritası/AFS.
7. Uluslararası: Earth Prize/Zayed/Stockholm Junior Water Prize/ISEF/YRE; Global Teacher Prize/T4/Global Schools/National Geographic; Eco-Schools/Roots & Shoots/GLOBE; Pollination/Rufford/Greengrants/MBZ; ECF/Allianz/NED/Rotary.
8. Derleme: STGM/ab-ilan/Sivil Sayfalar/Terra Viva/Mladiinfo/Opportunity Desk/Opportunities for Youth/Youth Opportunities/EU Calls/On the Move/fundsforNGOs. Resmî asıl belgeye ulaşmak için ipucu; uygunluk kanıtı sayılmaz.

Bu liste kurum isimlerinin duyuru uç noktalarıyla doğrulandığı anlamına gelmez. docs/KAYNAK_ENVANTERI.md başlangıç haritasıdır; her URL, erişim yolu ve çağrı kapsamı uygulama sırasında ölçülür. Kullanıcının önceki erişim ölçümleri tarihsel verilerdir.

## Toplama kuralları
- Önce resmî API, sonra RSS/Atom, sonra kaynağa özgü HTML ayrıştırıcı; JavaScript zorunlu ve izinli sayfalarda sınırlı tarayıcı işleyicisi yalnız ihtiyaç ölçülürse eklenir.
- Program bilgi sayfası veya proje sonuçları yeni açık çağrı değildir; hibe/yarışma/burs/eğitim/ortak arama/izleme ayrılır.
- Her kaynak için izinli host, duyuru URL'si, kontrol aralığı, sayfa sınırı, yöntem ve son başarı/hata tutulur. robots.txt ve kullanım şartları incelenir; engel aşılmaz. Kaynak erişim hatası programın kapandığı anlamına gelmez.
- Başlangıç hedefi: aktif API/RSS ve yüksek öncelikli resmî duyurular 6 saatte bir; diğer HTML sayfaları günlük; yıllık program sayfaları haftalık. Dönemsel çağrılar ve yakın son tarihler daha sık kontrol edilir. Aralıklar ilk ölçüme göre ayarlanır.
- Ülke uygunluğu, başvuran türü (okul/öğretmen/lise öğrencisi/STK/üniversite), ortak gereksinimi, destek türü, tema, son tarih ve kaynak kanıtı ayrı alanlardır. Türkiye uygunluğu belirsizse kesin uygun rozeti yok; yurt dışı yalnız çağrılar silinmeden ayrı kategoride tutulabilir.

## Kalıcı kayıt ve değişiklikler
Firestore: sources, opportunities, revisions, reviews, runs, publication_snapshots.
Her duyuruda source_url/original_url, kurum, program/çağrı kimliği, çağrı yılı, first_seen, last_seen, last_checked, deadline/timezone, content_hash, evidence, approval_hash, status ve found_in alanları bulunur.
- Resmî çağrı kimliği ve aynı dönem en güçlü birleştirme anahtarıdır; sonra canonical URL. Başlık benzerliği yalnız birleşme önerisi üretir; farklı yıllar veya çağrılar otomatik birleştirilmez.
- Aynı çağrının STGM/ab-ilan/resmî kopyaları tek kartta birden fazla kaynakla gösterilir.
- Yeni veya anlamlı metin/PDF hash'i değişen kayıt inceleme bekler; hash'e bağlı eski onay geçersizleşir. Onaylanmamış yeni koşullar yayımlanmaz.
- Tarih dolduğunda açık listesinden arşive geçiş otomatik olabilir; bilinmeyen tarih uydurulmaz. Yaklaşık/gün düzeyinde tarihler kesin saat gibi sunulmaz.
- Kaynak hatası veya liste sayfasında kaybolma silme sebebi değildir. Son sağlam veri korunur, bayatlık uyarısı görünür; kapandı/silindi kararı kanıt ister.

## Yayın ve işletim
MVP'nin insan onayı kuralı korunur: otomatik toplama → yönetici incelemesi → onaylı yayın. Tam otomatik, insan onaysız yeni duyuru yayını ayrı kullanıcı kararı gerektirir.
Scheduler, onaylı değişiklikleri ve tarih durumlarını kullanarak statik siteyi üretir. Test/şema/güvenli link kontrolleri geçen çıktı Firebase Hosting'e gönderilir. Başarısız koşuda son sağlam yayın kalır; snapshot ile geri dönüş sağlanır.
Eşzamanlı işler ve tekrar tetiklemeler Firestore transaction tabanlı süreli iş kilidi ve aynı sürümü yeniden üretmeyen kayıt anahtarlarıyla kontrol edilir.
Sitede duyuru için son kaynak kontrolü, site için son başarılı güncelleme gösterilir. Hedef kontrol sıklığı anlık güncellik garantisi değildir; yeni ilanlar ayrıca insan onayı süresine bağlıdır.
Kaynak sağlık paneli: başarılı/hatalı/bayat/engel/manuel; ani sıfır duyuru veya büyük düşüş inceleme uyarısı verir. Hiçbir kaynak sessizce kapsamdan çıkarılmaz.

## Mevcut durumdan fark
13 kaynak yapılandırması ve günlük çıktı var. collector.dedupe canonical URL temellidir; farklı URL'li aynı programı her zaman birleştirmez. site.prepare accepted/review/watch/general gruplarını onay denetimi olmadan aktarır. Sürekli geçmiş deposu, canlı yönetici bağlantısı, zamanlama, güvenli otomatik yayın ve hata izleme tamamlanmadı.

## Sıralı uygulama ve kabul
1. Kalıcı kayıt, sürüm/hash onayı, kaynak sağlığı ve tekilleştirme. Fixture testleri: aynı çağrı çok kaynak, farklı dönemler ayrılır, hata veriyi silmez, değişiklik onayı kaldırır.
2. Kullanıcının tüm listesini envantere eşleştirme; okul odağı yüksek kaynaklardan başlayarak her bağlayıcıyı gerçek örnek + fixture ile doğrulama. Öncelik sırası kapsam azaltımı değildir. Ulusal Ajans/MEB/Eurodesk/SALTO temel okul kaynaklarıdır.
3. Firestore/Google giriş ile inceleme paneli, onaylı statik üretim. Onaysız kayıt yayına çıkmaz, onay sürümü değişirse reddedilir.
4. Kullanıcı yetkisi ve faturalandırma kontrolüyle Cloud Run/Scheduler/Hosting kurulumu. İki ardışık otomatik koşu, kaynak hatası, tekrar tetikleme ve geri dönüş gerçek ortamda doğrulanır; ardından iki haftalık izleme.

## Hesap, maliyet ve sınırlar
Cloud Run için proje faturalandırması etkin olmalıdır; mevcut hibe-radari-tr projesinin faturalandırma durumu bu çalışmada ölçülmedi. Harcama çalışma süresi, ağ ve Firestore kullanımına bağlıdır; ücretsiz çalışma veya sabit tutar vaat edilmez. Bütçe uyarıları harcamayı kendiliğinden durdurmaz; iş başına kaynak/süre/istek sınırları uygulanır. Kimlikler sunucu servis hesaplarında, en az gerekli yetkiyle tutulur.
Bu belge çözüm önerisidir; kaynakların tamamı kazınmış, bulut hesabı bağlanmış veya sürekli güncelleme kurulmuş değildir. Bu araştırmada kod değişmedi, testler yeniden koşulmadı; önceki 85 Python/11 JS kanıtı devir oturumuna aittir.

## Resmî teknik dayanaklar
- Cloud Run + Scheduler: https://docs.cloud.google.com/run/docs/execute/jobs-on-schedule
- Cloud Run faturalandırma önkoşulu: https://docs.cloud.google.com/run/docs/quickstarts/jobs/create-execute
- Firebase Hosting programatik yayın: https://firebase.google.com/docs/hosting/api-deploy
- Firestore transactions: https://firebase.google.com/docs/firestore/manage-data/transactions
- Erasmus+ ulusal/merkezi başvuru ayrımı: https://erasmus-plus.ec.europa.eu/resources-and-tools/how-to-apply/where-to-apply
