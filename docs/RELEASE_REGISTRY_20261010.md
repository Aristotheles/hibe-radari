# Kaynak entegrasyonu ve gerçek Batch inceleme — 2026-10-10

## Sonuç ve gerçek kapsam

135 gerçek envanter URL’sinin tamamı mevcut 131 çekiciye eşlendi. Eski 19 kayıt korunur; kaynak yönetimi 154 kayıt gösterir. Depoda 170 ayrı URL’lik liste bulunmadı. 35 adres veya çağrı uydurulmadı. Eşlenmiş olmak, her kaynağın sağlıklı veya ilanlarının uygun olması değildir.
Yeni 68 çekicinin canlı ölçümü: {'success': 53, 'partial': 6, 'suspicious_empty': 9}. 1130 keşif üstverisi. Erişim politikaları: {'allowed': 92, 'unreviewed': 31, 'permission_required': 8}.
Son ölçüm 2026-10-10T23:17:41.335843: 1339 saklanan çağrı, 39 ayrı yayımlanmış fırsat, bekleyen Batch 0.

## İnceleme sonucu nasıl okunmalı

Uygunsuzluk, kanıt eksikliği ve geçmiş/kapanmış çağrı ayrı sonuçlardır. Türkiye erişimi, lise/öğretmen/öğrenci başvuru yolu, güncel kesin tarih veya kanıtlı sürekli açıklık ve birincil kaynak aranır. Kişisel yaş, deneyim, önceki hibe ve proje koşulları otomatik sağlanmış sayılmaz. İncelemeye gönderilen yüzlerce arşiv haberi güncel fırsat değildir.
Güncel öneriye bağlı kararlar: {'invalid_evidence': 171, 'country_evidence_required': 119, 'closed': 111, 'out_of_scope': 709, 'current_deadline_required': 16, 'audience_evidence_required': 24, 'primary_source_required': 29, 'published': 39, 'application_path_required': 2}. Bu sayım tüm kayıtları kapsamaz; henüz belge alınamayan kayıtları uygunsuz saymaz. Yayımlanan karar sayısı ile görünür kart sayısı URL takma-adları nedeniyle farklı olabilir.
Gerçek inceleme: ilk 153 belgeye ek olarak 241 Grants.gov, 831 genel belge, 26 API alıntı düzeltmesi, 4 Rufford aşaması, 15 PDF ek incelemesi ve 169 alıntı düzeltmesi. Tüm sağlayıcı işleri terminal başarılı; bu, bütün kayıtların uygun olduğu anlamına gelmez. 40 gerçek bağlı-PDF adayından 25’inde erişim/metin sınırı hatası kaldı; hata sessizce aşılmadı.
MEB GençBizz yanlış Türkiye kapısı düzeltildi. Jean Monnet 2027–2028 bursu gerçek PDF koşullarıyla işlendi. Rufford’un dört gerçek hibe aşaması 7.000/8.000/12.000/18.000 GBP; ileri aşamalarda önceki hibe ve bekleme koşulları korunur. AB Başkanlığı aynı sayfa numarası, başvuru belgeleri, dönem ve tarihle iki URL verdiğinde tek kart gösterilir; kayıtlar silinmez, farklı aşamalar birleştirilmez.

## RELEASE doğrulaması

- PASS: 294 Python testi (38.695 s), 16 JavaScript testi (144.629 ms), compileall, JavaScript sözdizimi ve diff kontrolü.
- PASS: gerçek Grants.gov public API, 241 kayıt/6 istek. Belgelenmiş izin yalnız iki kesin endpoint; HTTPS/robots/özel IP ve diğer alan adı kontrolleri korunur. Gerekli resmî atıf altbilgide.
- PASS: PDF URL’leri gerçek sayfa bağlantılarından; dış alan/kimlikli URL ve sessiz kırpma engelli. Son tarih kanıtı gerçek PDF’ye bağlanır.
- PASS: mevcut Firestore/SQLite/JSON mimarisi korunur. Atomik süreli iş sahipliği aynı veritabanında; toplama ve sonuç yayınlama tek aktif yazıcıyla çalışır. Başarısız kaynak mevcut veriyi silmez.
- PASS: registry-r7 refresh build baed91eb-0552-491e-847a-db86a53d81f4; backend build c3e85d98-16bb-47e9-b0cb-58d32326785a. Backend hibe-backend-00008-fm9 yüzde100 trafikte, iki ürün işi r7 imajında. Hosting yayını başarılı.
- PASS: r5 gerçek bulut sonuç işi hibe-ai-batch-results-lss89 SUCCESS33.8s. Son r7 kabul çalışması hibe-ai-batch-results-dk2mj sonucu ayrıca devir kaydında ölçülür.
- Haftada iki kaynak taraması/temizlik/filtreleme: Salı/Cuma08.15 Europe/Istanbul. Saat05/35 yalnız bekleyen AI sonuçlarını alır; kaynak taramaz veya yeni AI isteği göndermez. Kullanıcının iptal ettiği Codex geliştirme heartbeat yeniden oluşturulmadı.
- NOT VERIFIED: gerçek Google yönetici oturumu bu dilimde yeniden test edilmedi. NOT MEASURED: gerçek fatura toplamı. N/A: mobil mağaza, uygulama içi ödeme, ikinci toplayıcı.
- Açık kapsam: izin/erişim koşulu nedeniyle kapalı 31 kaynağın ve açık yasaklı8 kaynağın çalıştığı iddia edilmez. Yeni ölçümde kısmi6/boş9 çekici ve bazı belgeler için güvenilir veri erişimi eksik. Tüm proje tamamlandı sayılmaz.

## Kaynak bazında bağlantı ve erişim

| Kaynak | Çekici yöntemi | Erişim politikası | Bu dilimde canlı ölçüm |
|---|---|---|---|
| [EU Funding & Tenders Portal](https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home) | eu_ft | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Erasmus+ (Komisyon)](https://erasmus-plus.ec.europa.eu/) | source_discovery | allowed | success (2 kayıt) |
| [Erasmus+ Proje Sonuçları Platformu](https://erasmus-plus.ec.europa.eu/projects) | source_discovery | allowed | success (2 kayıt) |
| [Türkiye Ulusal Ajansı](https://www.ua.gov.tr/) | source_discovery | allowed | success (20 kayıt) |
| [Eurodesk Türkiye](https://eurodesk.ua.gov.tr/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Eurodesk Opportunity Finder](https://programmes.eurodesk.eu/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [European School Education Platform](https://school-education.ec.europa.eu/) | html_list | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [eTwinning Türkiye](https://etwinning.meb.gov.tr/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Avrupa Gençlik Portalı](https://youth.europa.eu/) | source_discovery | allowed | success (1 kayıt) |
| [Avrupa Dayanışma Programı (ESC)](https://youth.europa.eu/solidarity_en) | source_discovery | allowed | success (1 kayıt) |
| [SALTO Avrupa Eğitim Takvimi](https://www.salto-youth.net/tools/european-training-calendar/) | source_discovery | permission_required | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [SALTO Otlas ortak bulma](https://www.salto-youth.net/tools/otlas-partner-finding/) | source_discovery | permission_required | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [EACEA](https://www.eacea.ec.europa.eu/) | source_discovery | allowed | success (7 kayıt) |
| [Yaratıcı Avrupa](https://culture.ec.europa.eu/creative-europe) | source_discovery | allowed | success (2 kayıt) |
| [LIFE (çevre/iklim)](https://cinea.ec.europa.eu/programmes/life_en) | source_discovery | allowed | success (7 kayıt) |
| [Marie Skłodowska-Curie](https://marie-sklodowska-curie-actions.ec.europa.eu/) | source_discovery | allowed | success (1 kayıt) |
| [Ufuk Avrupa Türkiye (TÜBİTAK)](https://ufukavrupa.org.tr/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [EIT](https://eit.europa.eu/) | source_discovery | allowed | success (17 kayıt) |
| [Yeni Avrupa Bauhausu](https://new-european-bauhaus.europa.eu/) | source_discovery | allowed | success (5 kayıt) |
| [Avrupa İklim Paktı](https://climate-pact.europa.eu/) | source_discovery | allowed | suspicious_empty (0 kayıt) |
| [EU Code Week](https://codeweek.eu/) | source_discovery | allowed | success (2 kayıt) |
| [Scientix](https://www.scientix.eu/) | source_discovery | allowed | success (1 kayıt) |
| [European Schoolnet](https://www.eun.org/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Avrupa Konseyi Avrupa Gençlik Vakfı](https://www.coe.int/en/web/european-youth-foundation) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Anna Lindh Vakfı](https://www.annalindhfoundation.org/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [AB Türkiye Delegasyonu](https://www.avrupa.info.tr/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [AB Başkanlığı](https://www.ab.gov.tr/) | source_discovery | allowed | success (50 kayıt) |
| [Jean Monnet Burs Programı](https://www.jeanmonnet.org.tr/) | source_discovery | allowed | success (100 kayıt) |
| [Merkezi Finans ve İhale Birimi](https://www.cfcu.gov.tr/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Sivil Düşün](https://www.sivildusun.net/) | source_discovery | allowed | success (6 kayıt) |
| [Etkiniz AB](https://etkiniz.eu/) | source_discovery | allowed | success (9 kayıt) |
| [Interreg NEXT Karadeniz Havzası](https://blacksea-cbc.net/) | source_discovery | allowed | success (4 kayıt) |
| [Interreg NEXT MED](https://www.interregnextmed.eu/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [TÜBİTAK duyurular](https://tubitak.gov.tr/tr/duyuru) | html_list | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [TÜBİTAK Bilim ve Toplum (4000)](https://4000.tubitak.gov.tr/rss.xml) | feed | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [TÜBİTAK BİLİMİZ](https://bilimiz.tubitak.gov.tr/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [MEB AB ve Dış İlişkiler GM](https://abdigm.meb.gov.tr/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [MEB YEĞİTEK](https://yegitek.meb.gov.tr/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [MEB Ortaöğretim GM](https://ogm.meb.gov.tr/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [MEB Mesleki ve Teknik Eğitim GM](https://mtegm.meb.gov.tr/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Kalkınma Ajansları GM](https://ka.gov.tr/) | source_discovery | allowed | success (2 kayıt) |
| [KAYS](https://kaysuygulama.sanayi.gov.tr/) | source_discovery | allowed | suspicious_empty (0 kayıt) |
| [DOKA](https://www.doka.org.tr/) | source_discovery | allowed | success (5 kayıt) |
| [DOKAP](https://www.dokap.gov.tr/) | source_discovery | allowed | success (6 kayıt) |
| [Gençlik ve Spor Bakanlığı](https://www.gsb.gov.tr/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [İçişleri Sivil Toplumla İlişkiler GM](https://www.siviltoplum.gov.tr/) | source_discovery | allowed | partial (5 kayıt) |
| [Sıfır Atık](https://sifiratik.gov.tr/) | source_discovery | allowed | success (15 kayıt) |
| [TEKNOFEST](https://www.teknofest.org/) | source_discovery | allowed | success (26 kayıt) |
| [T3 Vakfı](https://t3vakfi.org/) | source_discovery | allowed | success (100 kayıt) |
| [UNESCO Türkiye Millî Komisyonu](https://www.unesco.org.tr/) | source_discovery | allowed | success (100 kayıt) |
| [TÜRÇEV](https://www.turcev.org.tr/) | source_discovery | allowed | success (23 kayıt) |
| [Eko-Okullar Türkiye](https://www.ekookullar.org.tr/) | source_discovery | allowed | suspicious_empty (0 kayıt) |
| [Avustralya DAP](https://turkey.embassy.gov.au/anka/Development_cooperat.html) | page_watch | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Kanada CFLI](https://www.international.gc.ca/world-monde/funding-financement/cfli-fcil/turkiye.aspx?lang=eng) | page_watch | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Japonya Büyükelçiliği (GGP)](https://www.tr.emb-japan.go.jp/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Japan Foundation](https://www.jpf.go.jp/e/) | source_discovery | allowed | partial (13 kayıt) |
| [ABD Büyükelçiliği](https://tr.usembassy.gov/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Grants.gov](https://www.grants.gov/) | grants_gov | allowed | success (241 kayıt) |
| [Fulbright Türkiye](https://fulbright.org.tr/) | source_discovery | allowed | partial (21 kayıt) |
| [YES Programı](https://www.yesprograms.org/) | source_discovery | allowed | suspicious_empty (0 kayıt) |
| [British Council Türkiye](https://www.britishcouncil.org.tr/) | feed | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [İngiltere Büyükelçilik Fonu](https://www.gov.uk/guidance/british-embassy-programme-fund-turkey) | page_watch | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Türk-Alman Gençlik Köprüsü](https://www.jugendbruecke.de/foerderung/) | html_crawl | permission_required | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Almanya PAD (KMK)](https://www.kmk-pad.org/) | page_watch | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [PASCH](https://www.pasch-net.de/) | page_watch | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Goethe-Institut Türkiye](https://www.goethe.de/ins/tr/tr/index.html) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [DAAD Türkiye](https://www.daad-turkiye.org/) | source_discovery | allowed | success (4 kayıt) |
| [Almanya Büyükelçiliği](https://tuerkei.diplo.de/) | source_discovery | allowed | suspicious_empty (0 kayıt) |
| [Stiftung Mercator](https://www.stiftung-mercator.de/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Robert Bosch Stiftung](https://www.bosch-stiftung.de/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Heinrich Böll Stiftung Türkiye](https://tr.boell.org/) | source_discovery | allowed | success (5 kayıt) |
| [Friedrich Ebert Stiftung Türkiye](https://turkey.fes.de/) | source_discovery | allowed | suspicious_empty (0 kayıt) |
| [IKI Small Grants (Almanya)](https://iki-small-grants.de/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Institut français Türkiye](https://www.ifturquie.org/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Fransa Büyükelçiliği](https://tr.ambafrance.org/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Hollanda (MATRA / İnsan Hakları Fonu)](https://www.netherlandsandyou.nl/) | source_discovery | allowed | success (3 kayıt) |
| [İsveç Enstitüsü](https://si.se/en/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Finlandiya Büyükelçiliği (Yerel İşbirliği Fonu)](https://finlandabroad.fi/web/tur) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [İsviçre Büyükelçiliği](https://www.eda.admin.ch/ankara) | source_discovery | allowed | success (2 kayıt) |
| [Avusturya OeAD](https://oead.at/) | page_watch | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [KEİ (BSEC)](https://www.bsec-organization.org/) | source_discovery | allowed | success (2 kayıt) |
| [GMF / Black Sea Trust](https://www.gmfus.org/) | source_discovery | allowed | success (1 kayıt) |
| [Dışişleri Bakanlığı](https://www.mfa.gov.tr/) | source_discovery | allowed | partial (24 kayıt) |
| [UNDP Türkiye](https://www.undp.org/tr/turkiye) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [UNDP GEF Küçük Destek Programı](https://sgp.undp.org/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [UNDP ihale/çağrı ilanları](https://procurement-notices.undp.org/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [UNESCO Associated Schools](https://www.unesco.org/en/aspnet) | source_discovery | allowed | success (28 kayıt) |
| [UNESCO ödülleri](https://www.unesco.org/en/prizes) | source_discovery | allowed | success (28 kayıt) |
| [UNICEF Türkiye](https://www.unicef.org/turkiye/) | source_discovery | allowed | success (3 kayıt) |
| [BM Demokrasi Fonu](https://www.un.org/democracyfund/) | source_discovery | allowed | success (8 kayıt) |
| [UNEP Young Champions of the Earth](https://www.unep.org/youngchampions/) | source_discovery | allowed | suspicious_empty (0 kayıt) |
| [Sabancı Vakfı](https://sabancivakfi.org/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Vehbi Koç Vakfı](https://www.vkv.org.tr/) | source_discovery | allowed | success (2 kayıt) |
| [Öğretmen Akademisi Vakfı](https://www.orav.org.tr/) | source_discovery | allowed | success (20 kayıt) |
| [Öğretmen Ağı](https://www.ogretmenagi.org/) | source_discovery | allowed | success (1 kayıt) |
| [Eğitim Reformu Girişimi](https://www.egitimreformugirisimi.org/) | source_discovery | allowed | partial (25 kayıt) |
| [TEGV](https://www.tegv.org/) | source_discovery | allowed | success (22 kayıt) |
| [TEMA Vakfı](https://www.tema.org.tr/) | source_discovery | allowed | success (15 kayıt) |
| [WWF-Türkiye](https://www.wwf.org.tr/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [TÜSEV](https://www.tusev.org.tr/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Sivil Toplum için Destek Vakfı](https://siviltoplumdestek.org/) | source_discovery | allowed | partial (12 kayıt) |
| [Turkey Mozaik Foundation](https://www.turkeymozaik.org.uk/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [İhtiyaç Haritası](https://www.ihtiyacharitasi.org/) | source_discovery | allowed | suspicious_empty (0 kayıt) |
| [AFS Türkiye (Türk Kültür Vakfı)](https://www.turkkulturvakfi.org.tr/) | source_discovery | permission_required | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [The Earth Prize](https://www.theearthprize.org/) | source_discovery | permission_required | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Zayed Sustainability Prize](https://zayedsustainabilityprize.com/) | source_discovery | allowed | success (1 kayıt) |
| [Stockholm Junior Water Prize (SIWI)](https://www.siwi.org/) | source_discovery | allowed | success (3 kayıt) |
| [Regeneron ISEF](https://www.societyforscience.org/isef/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Global Teacher Prize](https://www.globalteacherprize.org/) | source_discovery | permission_required | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [T4 Education](https://t4.education/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [National Geographic Society hibeleri](https://www.nationalgeographic.org/society/grants-and-investments/) | source_discovery | permission_required | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [The Pollination Project](https://thepollinationproject.org/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Rufford Foundation](https://www.rufford.org/) | source_discovery | allowed | success (4 kayıt) |
| [Global Greengrants Fund](https://www.greengrants.org/) | source_discovery | allowed | suspicious_empty (0 kayıt) |
| [Mohamed bin Zayed Tür Koruma Fonu](https://www.speciesconservation.org/) | source_discovery | permission_required | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Young Reporters for the Environment](https://www.yre.global/) | source_discovery | allowed | success (47 kayıt) |
| [Eco-Schools (küresel)](https://www.ecoschools.global/) | source_discovery | allowed | success (14 kayıt) |
| [Global Schools Program (SDSN)](https://www.globalschoolsprogram.org/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Roots & Shoots](https://rootsandshoots.global/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [GLOBE Program](https://www.globe.gov/) | source_discovery | allowed | success (9 kayıt) |
| [European Cultural Foundation](https://culturalfoundation.eu/) | source_discovery | allowed | success (9 kayıt) |
| [Allianz Foundation](https://allianzfoundation.org/) | source_discovery | allowed | success (1 kayıt) |
| [National Endowment for Democracy](https://www.ned.org/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Rotary Gençlik Değişimi](https://www.rotary.org/en/our-programs/youth-exchanges) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [STGM Hibe Duyuruları](https://www.stgm.org.tr/hibe-duyurulari) | html_cards | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [ab-ilan.com](https://ab-ilan.com/category/hibe-duyurulari/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Sivil Sayfalar](https://www.sivilsayfalar.org/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [fundsforNGOs](https://www2.fundsforngos.org/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Terra Viva Grants](https://terravivagrants.org/) | source_discovery | allowed | success (17 kayıt) |
| [Mladiinfo](https://www.mladiinfo.eu/) | source_discovery | allowed | success (24 kayıt) |
| [Opportunity Desk](https://opportunitydesk.org/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Opportunities for Youth](https://opportunitiesforyouth.org/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [Youth Opportunities](https://www.youthop.com/) | source_discovery | unreviewed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [EU Calls](https://eucalls.net/) | feed | allowed | Bu dilimde ölçülmedi; önceki gözlem ve izin kaydı korunur |
| [On the Move](https://on-the-move.org/) | source_discovery | allowed | success (2 kayıt) |
