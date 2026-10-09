# Kaynak envanteri — okul, öğretmen ve lise öğrencisi için hibe/proje duyuruları

Hazırlayan: Claude Code · 2026-10-09. Kapsam: AB, Türkiye, ikili (ülke/elçilik), BM ve uluslararası kuruluşlar, vakıflar, çevre/sürdürülebilirlik, ödül-yarışma, derleme siteleri.

**Durum sütunu** aynı gün curl ile ölçüldü (normal tarayıcı kimliği, yönlendirme izlenerek): `200` = açıldı; `engel` = 403/429 (bot koruması, aşılmaz → elle izleme); `yanıt yok` = bu ağdan bağlanılamadı. Bu ölçüm yalnız adresin açıldığını gösterir; açık çağrı bulunduğunu ve Türkiye/okul uygunluğunu **göstermez** — "Not" sütunundaki uygunluk ifadeleri genel bilgidir, her çağrı metninde teyit edilmelidir. Tek tek doğrulanmamış adres listeye yazılmadı.

**Toplama yolu:** API = resmî arama arayüzü · RSS = akış · HTML = liste sayfası ayrıştırma · İzleme = tek sayfa değişiklik takibi (yılda 1 tur açan programlar) · Elle = bot koruması veya dinamik sayfa.

## 1. AB — merkezi programlar ve araçlar

| Kaynak | Adres | Durum | Yol | Not |
|---|---|---|---|---|
| EU Funding & Tenders Portal | https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home | 200 | API | Tüm merkezi AB çağrıları (Erasmus+ merkezi eylemler, CERV, Ufuk Avrupa, Yaratıcı Avrupa, LIFE). Toplayıcıda bağlı (`eu-ft`) |
| Erasmus+ (Komisyon) | https://erasmus-plus.ec.europa.eu/ | 200 | HTML | Program rehberi, yıllık genel çağrı, son tarihler |
| Erasmus+ Proje Sonuçları Platformu | https://erasmus-plus.ec.europa.eu/projects | 200 | Elle | Ortak bulma, örnek proje |
| Türkiye Ulusal Ajansı | https://www.ua.gov.tr/ | 200 | HTML | Okul eğitimi KA1/KA2, akreditasyon, gençlik, ESC — okul için ana kapı |
| Eurodesk Türkiye | https://eurodesk.ua.gov.tr/ | 200 | HTML | Gençlik fırsat duyuruları |
| Eurodesk Opportunity Finder | https://programmes.eurodesk.eu/ | 200 | HTML | Avrupa geneli fırsat veritabanı |
| European School Education Platform | https://school-education.ec.europa.eu/ | 200 | Elle | eTwinning, ortak arama, öğretmen kursları |
| eTwinning Türkiye | https://etwinning.meb.gov.tr/ | 200 | RSS | Toplayıcıda bağlı |
| Avrupa Gençlik Portalı | https://youth.europa.eu/ | 200 | HTML | DiscoverEU, gençlik fırsatları |
| Avrupa Dayanışma Programı (ESC) | https://youth.europa.eu/solidarity_en | 200 | HTML | Gönüllülük, dayanışma projeleri (18+) |
| SALTO Avrupa Eğitim Takvimi | https://www.salto-youth.net/tools/european-training-calendar/ | 200 | HTML | Öğretmen/gençlik çalışanı için masrafı karşılanan eğitimler |
| SALTO Otlas ortak bulma | https://www.salto-youth.net/tools/otlas-partner-finding/ | 200 | HTML | Ortak arayan projeler |
| EACEA | https://www.eacea.ec.europa.eu/ | 200 | HTML | Merkezi Erasmus+/CERV/Yaratıcı Avrupa yürütücüsü |
| Yaratıcı Avrupa | https://culture.ec.europa.eu/creative-europe | 200 | HTML | Kültür projeleri; Türkiye katılımı teyit edilmeli |
| LIFE (çevre/iklim) | https://cinea.ec.europa.eu/programmes/life_en | 200 | HTML | Türkiye uygunluğu teyit edilmeli |
| Marie Skłodowska-Curie | https://marie-sklodowska-curie-actions.ec.europa.eu/ | 200 | HTML | Avrupa Araştırmacılar Gecesi vb. (okul ortak olabilir) |
| Ufuk Avrupa Türkiye (TÜBİTAK) | https://ufukavrupa.org.tr/ | 200 | HTML | Türkçe çağrı duyuruları |
| EIT | https://eit.europa.eu/ | 200 | HTML | EIT Climate-KIC, Food vb. okul/gençlik programları |
| Yeni Avrupa Bauhausu | https://new-european-bauhaus.europa.eu/ | 200 | HTML | Ödül ve çağrılar (sürdürülebilirlik+tasarım) |
| Avrupa İklim Paktı | https://climate-pact.europa.eu/ | 200 | Elle | İklim elçiliği, etkinlik |
| EU Code Week | https://codeweek.eu/ | 200 | Elle | Okul etkinlikleri, yarışmalar |
| Scientix | https://www.scientix.eu/ | 200 | HTML | STEM öğretmen çağrıları, elçilik |
| European Schoolnet | https://www.eun.org/ | 200 | HTML | Pilot okul/öğretmen çağrıları |
| Avrupa Konseyi Avrupa Gençlik Vakfı | https://www.coe.int/en/web/european-youth-foundation | engel | Elle | Gençlik STK'ları için hibe |
| Anna Lindh Vakfı | https://www.annalindhfoundation.org/ | 503 | Elle | Avrupa-Akdeniz kültürlerarası diyalog |

## 2. AB — Türkiye'ye özgü ve sınır ötesi

| Kaynak | Adres | Durum | Yol | Not |
|---|---|---|---|---|
| AB Türkiye Delegasyonu | https://www.avrupa.info.tr/ | 200 | HTML | eeas.europa.eu/delegations/turkiye_tr adresine yönlenir |
| AB Başkanlığı | https://www.ab.gov.tr/ | 200 | HTML | IPA duyuruları, hibe programları |
| Jean Monnet Burs Programı | https://www.jeanmonnet.org.tr/ | 200 | İzleme | Kamu çalışanı (öğretmen) başvurabilir |
| Merkezi Finans ve İhale Birimi | https://www.cfcu.gov.tr/ | 200 | HTML | IPA hibe çağrıları |
| Sivil Düşün | https://www.sivildusun.net/ | 200 | HTML | Aktivist/STK destekleri |
| Etkiniz AB | https://etkiniz.eu/ | 200 | HTML | Hak temelli STK destekleri |
| Interreg NEXT Karadeniz Havzası | https://blacksea-cbc.net/ | 200 | HTML | Karadeniz illeri |
| Interreg NEXT MED | https://www.interregnextmed.eu/ | 200 | HTML | Akdeniz kıyı illeri |

## 3. Türkiye — kamu

| Kaynak | Adres | Durum | Yol | Not |
|---|---|---|---|---|
| TÜBİTAK duyurular | https://tubitak.gov.tr/tr/duyuru | 200 | HTML | 4006, 4004, 4005, 4007, 2204-A/B (lise/ortaokul proje yarışmaları). Bağlı |
| TÜBİTAK Bilim ve Toplum (4000) | https://4000.tubitak.gov.tr/rss.xml | 200 | RSS | Akış bayat olabiliyor |
| TÜBİTAK BİLİMİZ | https://bilimiz.tubitak.gov.tr/ | 200 | Elle | 4006 başvuru sistemi |
| MEB AB ve Dış İlişkiler GM | https://abdigm.meb.gov.tr/ | 200 | HTML | Uluslararası program/burs duyuruları |
| MEB YEĞİTEK | https://yegitek.meb.gov.tr/ | 200 | HTML | Teknoloji/yenilik projeleri |
| MEB Ortaöğretim GM | https://ogm.meb.gov.tr/ | 200 | HTML | Lise proje ve yarışma duyuruları |
| MEB Mesleki ve Teknik Eğitim GM | https://mtegm.meb.gov.tr/ | 200 | HTML | Meslek liseleri |
| Kalkınma Ajansları GM | https://ka.gov.tr/ | 200 | HTML | 26 ajansın tamamı; okul = teknik destek, SOGEP ortaklığı |
| KAYS | https://kaysuygulama.sanayi.gov.tr/ | 200 | Elle | Ajans başvuru sistemi |
| DOKA | https://www.doka.org.tr/ | 200 | HTML | TR90 illeri |
| DOKAP | https://www.dokap.gov.tr/ | 200 | HTML | Bölge kalkınma idaresi programları |
| Gençlik ve Spor Bakanlığı | https://www.gsb.gov.tr/ | 200 | HTML | Gençlik Projeleri Destek Programı (önceki ölçümde bağlantı sıfırlanmıştı) |
| İçişleri Sivil Toplumla İlişkiler GM | https://www.siviltoplum.gov.tr/ | 200 | HTML | PRODES — dernekler (okul aile birliği/mezun derneği yolu) |
| Sıfır Atık | https://sifiratik.gov.tr/ | 200 | Elle | Belge/ödül |
| TEKNOFEST | https://www.teknofest.org/ | 200 | HTML | Lise takımlarına yarışma + malzeme desteği |
| T3 Vakfı | https://t3vakfi.org/ | 200 | HTML | Deneyap, burs |
| UNESCO Türkiye Millî Komisyonu | https://www.unesco.org.tr/ | 200 | HTML | ASPnet okulları, yarışmalar |
| TÜRÇEV | https://www.turcev.org.tr/ | 200 | HTML | Eko-Okullar, Genç Çevre Muhabirleri |
| Eko-Okullar Türkiye | https://www.ekookullar.org.tr/ | 200 | HTML | |

## 4. Ülkeler — elçilik ve ikili fonlar

| Kaynak | Adres | Durum | Yol | Not |
|---|---|---|---|---|
| Avustralya DAP | https://turkey.embassy.gov.au/anka/Development_cooperat.html | 200 | İzleme | Yıllık tur |
| Kanada CFLI | https://www.international.gc.ca/world-monde/funding-financement/cfli-fcil/turkiye.aspx?lang=eng | 200 | İzleme | Yıllık tur |
| Japonya Büyükelçiliği (GGP) | https://www.tr.emb-japan.go.jp/ | engel | Elle | Okul yapım/donanım hibesi |
| Japan Foundation | https://www.jpf.go.jp/e/ | 200 | HTML | Kültür/dil programları |
| ABD Büyükelçiliği | https://tr.usembassy.gov/ | 200 | HTML | Kamu diplomasisi hibeleri (bu ölçümde açıldı) |
| Grants.gov | https://www.grants.gov/ | 200 | API | ABD federal çağrıları; arama arayüzü denenmedi |
| Fulbright Türkiye | https://fulbright.org.tr/ | 200 | HTML | Öğretmen programları, FLTA |
| YES Programı | https://www.yesprograms.org/ | 200 | İzleme | Lise öğrenci değişimi; Türkiye turu teyit edilmeli |
| British Council Türkiye | https://www.britishcouncil.org.tr/ | yanıt yok | RSS | Önceki çalıştırmada akış çalışmıştı |
| İngiltere Büyükelçilik Fonu | https://www.gov.uk/guidance/british-embassy-programme-fund-turkey | 200 | İzleme | Sayfa "kapandı" diyor |
| Türk-Alman Gençlik Köprüsü | https://www.jugendbruecke.de/foerderung/ | 200 | HTML | Okul değişimi + küçük proje. Bağlı |
| Almanya PAD (KMK) | https://www.kmk-pad.org/ | 200 | İzleme | Okul ortaklığı, öğretmen stajı |
| PASCH | https://www.pasch-net.de/ | 200 | İzleme | Almanca öğreten ortak okullar |
| Goethe-Institut Türkiye | https://www.goethe.de/ins/tr/tr/index.html | engel | Elle | Öğretmen bursları |
| DAAD Türkiye | https://www.daad-turkiye.org/ | 200 | HTML | Çoğu üniversite düzeyi |
| Almanya Büyükelçiliği | https://tuerkei.diplo.de/ | 200 | HTML | Küçük ölçekli projeler |
| Stiftung Mercator | https://www.stiftung-mercator.de/ | 200 | HTML | Türkiye-Almanya programları |
| Robert Bosch Stiftung | https://www.bosch-stiftung.de/ | 200 | HTML | |
| Heinrich Böll Stiftung Türkiye | https://tr.boell.org/ | 200 | HTML | Ekoloji/demokrasi |
| Friedrich Ebert Stiftung Türkiye | https://turkey.fes.de/ | 200 | HTML | |
| IKI Small Grants (Almanya) | https://iki-small-grants.de/ | 200 | İzleme | İklim/biyoçeşitlilik; kâr amacı gütmeyen kuruluş |
| Institut français Türkiye | https://www.ifturquie.org/ | 200 | RSS | Bağlı |
| Fransa Büyükelçiliği | https://tr.ambafrance.org/ | 200 | HTML | tr.diplomatie.gouv.fr adresine yönlenir |
| Hollanda (MATRA / İnsan Hakları Fonu) | https://www.netherlandsandyou.nl/ | 200 | Elle | Türkiye sayfası içinden |
| İsveç Enstitüsü | https://si.se/en/ | 200 | HTML | |
| Finlandiya Büyükelçiliği (Yerel İşbirliği Fonu) | https://finlandabroad.fi/web/tur | 200 | İzleme | |
| İsviçre Büyükelçiliği | https://www.eda.admin.ch/ankara | engel | Elle | |
| Avusturya OeAD | https://oead.at/ | 200 | İzleme | Okul/öğretmen değişimi |
| KEİ (BSEC) | https://www.bsec-organization.org/ | 200 | İzleme | Proje geliştirme fonu |
| GMF / Black Sea Trust | https://www.gmfus.org/ | 200 | HTML | Karadeniz bölgesi STK hibeleri |
| Dışişleri Bakanlığı | https://www.mfa.gov.tr/ | 200 | Elle | Türkiye'deki tüm elçiliklerin dizini (listede olmayan ülkeler için) |

## 5. BM ve uluslararası kuruluşlar

| Kaynak | Adres | Durum | Yol | Not |
|---|---|---|---|---|
| UNDP Türkiye | https://www.undp.org/tr/turkiye | engel | Elle | |
| UNDP GEF Küçük Destek Programı | https://sgp.undp.org/ | 200 | İzleme | Çevre; STK/kooperatif |
| UNDP ihale/çağrı ilanları | https://procurement-notices.undp.org/ | 200 | HTML | |
| UNESCO Associated Schools | https://www.unesco.org/en/aspnet | 200 | Elle | Okul ağı üyeliği |
| UNESCO ödülleri | https://www.unesco.org/en/prizes | 200 | İzleme | Sürdürülebilir kalkınma eğitimi ödülü vb. |
| UNICEF Türkiye | https://www.unicef.org/turkiye/ | 200 | HTML | |
| BM Demokrasi Fonu | https://www.un.org/democracyfund/ | 200 | İzleme | STK |
| UNEP Young Champions of the Earth | https://www.unep.org/youngchampions/ | 200 | İzleme | Genç çevre girişimcileri |

## 6. Türkiye — vakıf ve sivil toplum

| Kaynak | Adres | Durum | Yol | Not |
|---|---|---|---|---|
| Sabancı Vakfı | https://sabancivakfi.org/ | 200 | İzleme | Hibe programı (eğitim teması) |
| Vehbi Koç Vakfı | https://www.vkv.org.tr/ | 200 | HTML | |
| Öğretmen Akademisi Vakfı | https://www.orav.org.tr/ | 200 | HTML | Öğretmen programları |
| Öğretmen Ağı | https://www.ogretmenagi.org/ | 200 | HTML | Öğretmen fonları/çağrıları |
| Eğitim Reformu Girişimi | https://www.egitimreformugirisimi.org/ | 200 | HTML | |
| TEGV | https://www.tegv.org/ | 200 | HTML | |
| TEMA Vakfı | https://www.tema.org.tr/ | 200 | HTML | Okul çevre eğitim programları |
| WWF-Türkiye | https://www.wwf.org.tr/ | 200 | HTML | |
| TÜSEV | https://www.tusev.org.tr/ | 200 | RSS | Bağlı |
| Sivil Toplum için Destek Vakfı | https://siviltoplumdestek.org/ | 200 | HTML | Tematik fonlar |
| Turkey Mozaik Foundation | https://www.turkeymozaik.org.uk/ | 200 | HTML | |
| İhtiyaç Haritası | https://www.ihtiyacharitasi.org/ | 200 | Elle | Okul ihtiyaç desteği (hibe değil, ayni) |
| AFS Türkiye (Türk Kültür Vakfı) | https://www.turkkulturvakfi.org.tr/ | 200 | İzleme | Lise öğrenci değişimi bursları |

## 7. Uluslararası — çevre, bilim, ödül ve yarışma

| Kaynak | Adres | Durum | Yol | Not |
|---|---|---|---|---|
| The Earth Prize | https://www.theearthprize.org/ | 200 | İzleme | 13–19 yaş çevre projesi yarışması |
| Zayed Sustainability Prize | https://zayedsustainabilityprize.com/ | 200 | İzleme | "Global High Schools" kategorisi |
| Stockholm Junior Water Prize (SIWI) | https://www.siwi.org/ | 200 | İzleme | Lise su projeleri |
| Regeneron ISEF | https://www.societyforscience.org/isef/ | 200 | İzleme | TÜBİTAK 2204 üzerinden |
| Global Teacher Prize | https://www.globalteacherprize.org/ | 200 | İzleme | Öğretmen ödülü |
| T4 Education | https://t4.education/ | 200 | İzleme | World's Best School Prizes |
| National Geographic Society hibeleri | https://www.nationalgeographic.org/society/grants-and-investments/ | 200 | İzleme | Eğitimci/araştırmacı |
| The Pollination Project | https://thepollinationproject.org/ | 200 | İzleme | Küçük tohum hibeleri |
| Rufford Foundation | https://www.rufford.org/ | 200 | İzleme | Doğa koruma |
| Global Greengrants Fund | https://www.greengrants.org/ | 200 | Elle | |
| Mohamed bin Zayed Tür Koruma Fonu | https://www.speciesconservation.org/ | 200 | İzleme | |
| Young Reporters for the Environment | https://www.yre.global/ | 200 | İzleme | Türkiye'de TÜRÇEV yürütür |
| Eco-Schools (küresel) | https://www.ecoschools.global/ | 200 | Elle | |
| Global Schools Program (SDSN) | https://www.globalschoolsprogram.org/ | 200 | İzleme | Öğretmen elçilik çağrısı |
| Roots & Shoots | https://rootsandshoots.global/ | 200 | Elle | |
| GLOBE Program | https://www.globe.gov/ | 200 | Elle | Okul çevre ölçüm ağı |
| European Cultural Foundation | https://culturalfoundation.eu/ | 200 | HTML | |
| Allianz Foundation | https://allianzfoundation.org/ | 200 | HTML | |
| National Endowment for Democracy | https://www.ned.org/ | 200 | İzleme | STK |
| Rotary Gençlik Değişimi | https://www.rotary.org/en/our-programs/youth-exchanges | engel | Elle | Yerel kulüp üzerinden |

## 8. Derleme siteleri (ipucu — asıl kaynakta doğrulanır)

| Kaynak | Adres | Durum | Yol | Not |
|---|---|---|---|---|
| STGM Hibe Duyuruları | https://www.stgm.org.tr/hibe-duyurulari | 200 | HTML | Bağlı |
| ab-ilan.com | https://ab-ilan.com/category/hibe-duyurulari/ | 200 | RSS | Bağlı |
| Sivil Sayfalar | https://www.sivilsayfalar.org/ | 200 | RSS | Bağlı |
| fundsforNGOs | https://www2.fundsforngos.org/ | engel | Elle | Cloudflare |
| Terra Viva Grants | https://terravivagrants.org/ | 200 | HTML | Çevre/tarım/enerji hibeleri |
| Mladiinfo | https://www.mladiinfo.eu/ | 200 | RSS? | Gençlik fırsatları; akış sınanmadı |
| Opportunity Desk | https://opportunitydesk.org/ | 200 | RSS? | Akış sınanmadı |
| Opportunities for Youth | https://opportunitiesforyouth.org/ | 200 | RSS? | Akış sınanmadı |
| Youth Opportunities | https://www.youthop.com/ | 200 | HTML | |
| EU Calls | https://eucalls.net/ | 200 | HTML | AB çağrıları + ortak arama |
| On the Move | https://on-the-move.org/ | 200 | HTML | Kültür hareketlilik fonları |

## Bu ölçümde açılmayan, listeye alınmayanlar
Interreg IPA Bulgaristan–Türkiye (ipacbc-bgtr.eu), EIT Girls Go Circular, EOCA, UWC Türkiye, worldsbestschool.org, Kültür için Alan (kulturicinalan.com, 522): bağlantı kurulamadı; adres teyit edilmeden eklenmedi.

## Bilinen boşluklar
- 26 kalkınma ajansının tek tek adresleri (yalnız DOKA ve üst kurum ölçüldü), il/ilçe MEM AR-GE duyuru sayfaları, belediye ve üniversite çağrıları.
- Listede olmayan elçilikler (Norveç, Danimarka, İrlanda, Kore, Çekya, Polonya vb.): fon sayfası adresi doğrulanmadı.
- Şirket sosyal sorumluluk programları (banka, holding, teknoloji firmaları): düzenli çağrı sayfası doğrulanmadı.
