# 19 aday kaynak — internet araştırması (2026-10-09, Claude Code)

Özgün 30 kaynak listesi hiçbir yerde bulunamadı: proje, Obsidian kasası, Serena hafızası (boş), iki ZIP ve Codex/Claude oturum kayıtları tarandı; adlar yalnız projenin kendi dosyalarında geçiyor. Bu rapor 19 aday ismin resmî sitelerini web aramasıyla bulur. `identity_status` **candidate** kalır (özgün belge yok); 11 boş yer doldurulmadı.

URL durumu: "200" = curl ile açıldı ve TLS doğrulandı (2026-10-09). Çağrı durumu web aramasından gelir, ikincil kaynak içerebilir; her kaynağın kendi sayfasında teyit edilmelidir.

| ID | Kaynak | Adres | URL durumu | Çağrı durumu (arama bulgusu) |
|---|---|---|---|---|
| 1 | Türkiye Ulusal Ajansı | https://www.ua.gov.tr/ | 200 | Güncel okul eğitimi çağrı tarihi aramada çıkmadı; sitede kontrol gerekir |
| 2 | TÜBİTAK 4006 | tubitak.gov.tr 13. dönem duyurusu | 200 | 13. dönem 4006-A/B açık: başvuru 13 Kasım 2026 17:30'a kadar (bilimiz.tubitak.gov.tr) |
| 3 | Avustralya DAP | https://turkey.embassy.gov.au/anka/Development_cooperat.html | 200 | 2025-26 turu kapalı; 2026-27 durumu doğrulanamadı |
| 4 | DOKA | https://www.doka.org.tr/destekler.php?tab=acik | 200 | Açık program bulunamadı; yalnız TR90 illeri (Artvin, Giresun, Gümüşhane, Ordu, Rize, Trabzon) |
| 5 | EU Funding & Tenders | https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home | 200 | Dinamik portal; Erasmus+ 2026 çağrıları orada, otomatik tarama için uygun değil |
| 6 | Japonya GGP | **adres doğrulanamadı** | tr.emb-japan.go.jp çözülmedi; www.tr.emb-japan.go.jp 403 | 2025-26 turu 26 Aralık 2025'te kapandı; sonraki tur duyurulmadı |
| 7 | GSB Gençlik Projeleri | **adres doğrulanamadı** | gsb.gov.tr / gpdp.gsb.gov.tr bağlantıyı sıfırladı | 2026'ya ait Gençlik Projeleri çağrısı bulunamadı (Mayıs 2026'da ayrı bir bağımlılık programı var) |
| 8 | Kanada CFLI | https://www.international.gc.ca/world-monde/funding-financement/cfli-fcil/turkiye.aspx?lang=eng | 200 | 2026 çağrısı kapalı |
| 9 | Interreg NEXT Black Sea Basin | https://blacksea-cbc.net/ | 200 | 2. çağrı 28 Haziran 2024'te kapandı; sonrası bulunamadı |
| 10 | Institut français | https://www.ifturquie.org/biz-kimiz/haberler/ | 200 | 2026 İnsan Hakları ve Çevre çağrıları var (Temmuz 2026'da kapandı); eğitim odaklı değil |
| 11 | İngiltere Büyükelçiliği | https://www.gov.uk/guidance/british-embassy-programme-fund-turkey | 200 | Sayfa "kapandı", son güncelleme 17 Ağustos 2023 |
| 12 | UNDP GEF SGP | https://sgp.undp.org/ (küresel) | 200 | Türkiye 2026 çağrısı STGM'de duyuruldu (STK/kooperatif, en çok 50.000 USD); Türkiye'ye özgü resmî adres doğrulanamadı, sgp.org.tr çözülmüyor |
| 13 | ABD Public Diplomacy Grants | **adres doğrulanamadı** | tr.usembassy.gov 403; grants.gov bağlantısı 404 | Son bilinen FY2025 turu kapandı |
| 14 | Sabancı Vakfı | https://sabancivakfi.org/ | 200 | 2026 Açık Çağrılı Hibe (9–27 Şubat) kapandı; "Nitelikli ve Kapsayıcı Eğitim" teması okul düzeyini kapsıyor |
| 15 | Deutsch-Türkische Jugendbrücke | https://www.jugendbruecke.de/foerderung/ | 200 | Okul değişimi 2027/28 çağrısı var, başvuru 6 Aralık; Küçük Proje Desteği (5.000 € e kadar) yıl boyu |
| 16 | Aile Bakanlığı Proje Geliştirme Destek Masası | https://www.aile.gov.tr/abdidb/faaliyetler/projeler/proje-gelistirme-destek-masasi/ | 200 | Hibe değil, kapasite/eğitim hizmeti (SSS, 2019); okul hibe kaynağı olarak uygunluğu şüpheli |
| 17 | STGM Hibe Duyuruları | https://www.stgm.org.tr/hibe-duyurulari | 200 | Sürekli güncel duyuru listesi |
| 18 | ab-ilan.com | https://ab-ilan.com/category/hibe-duyurulari/ | 200 | Güncel (9 Ekim 2026 ilanları var); derleme sitesi, asıl kaynak ayrıca doğrulanmalı |
| 19 | fundsforNGOs | **adres doğrulanamadı** | www/www2.fundsforngos.org 403 (bot engeli) | Türkiye listelerinin son tarihleri geçmiş; derleme sitesi |

## Sonuç
- URL'si doğrulanıp `config/sources.json`'a işlenen: 15 (1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18). Her biri için `manual_check` adımları ve `last_checked` 2026-10-09 yazıldı.
- URL'si doğrulanamayan: 4 (6, 7, 13, 19); `research_note` alanında nedeni var, URL uydurulmadı.
- `status` hepsinde `registry_pending` kaldı; kimlik özgün belgede doğrulanmadığı için `ready_controls` hâlâ 0. Aşama 3 tamamlanmadı.
- 11 boş yer (kaynak 20–30) için özgün listeye bağlı kimlik yok; doldurulmadı.
- Okul/öğretmen odağına uymayan adaylar (11 kapalı, 16 hibe değil, 7/19 erişilemedi) için kullanıcı kararı gerekir.
