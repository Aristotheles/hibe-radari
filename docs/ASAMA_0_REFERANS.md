# AŞAMA 0 — Temel durum ve geri dönüş referansı
Tarih: 2026-10-10 00:42 Europe/Istanbul · Codex · Durum: TAMAMLANDI

## 1. Ne uygulandı?
Kullanıcının C:/Users/senol/Downloads/HIBE_RADARI_MVP.md belgesi A–H ve referans ekleriyle okundu; yeni plan kökte MVP.md oldu. Eski plan yedeklendi. Yeni planın satır sonu boşlukları temizlendi ve H ilerleme kaydı güncellendi. Referans core.py çalıştırılmadı/kopyalanmadı. AŞAMA 1 koduna geçilmedi.
Git HEAD: b1633069bbc986a62033848ced0926dbb7bc1bf1. Başlangıç Git status ve unstaged/staged binary diff yedekte. Kaynak/config/test/ilan dosyaları değişmedi; commit/push/deploy yok.

## 2. Ne test edildi?
- Python 3.14.5: python -B -m unittest discover -s tests -v → 85 OK, 6.692 s.
- Node v24.12.0: node --test tests/test_radar.mjs → 11 PASS, 0 FAIL.
- node --check web/app.js; web/views.mjs; web/decision.mjs → 3 PASS.
- git diff --check → ilk denemede verilen belgedeki 11 satır sonu boşluğu bulundu; içerik kuralı değişmeden temizlendi. Son ölçüm diff-check.final logunda.
Yardımcı JS log yazdırması Windows cp1254 kodlamasında hata verdi; testin kendisi exit=0 idi. UTF-8 çıktı düzeltildi; test tekrar edilmeden korunmuş logdan 11 PASS/0 FAIL doğrulandı. Loglar yedek klasöründe. Gereksiz bağımlılık veya yeni test dosyası eklenmedi.

## 3. Ne kanıtlandı, ne doğrulanamadı?
- config/aggregator.json: 13 kaynak bloğu; 6 connector türü (1 eu_ft, 8 feed, 1 html_list, 1 html_cards, 1 html_crawl, 1 page_watch). page_watch içinde 6 sayfa.
- config/sources.json: 30 kayıt; tamamı registry_pending; 19 candidate, 11 missing.
- docs/KAYNAK_ENVANTERI.md: 8 kategori, 135 satır, 135 benzersiz URL, 135 farklı etiket, 131 farklı hostname. Kategori sayıları 25/8/19/31/8/13/20/11. Sekiz satır silinmedi.
- URL sayısı 135 kesin; kurum/program sayısı henüz kimlik eşlemesiyle doğrulanmış değil. 131 hostname kurum sayısı, 135 etiket de program sayısı olarak sunulmaz. Envanterde kurum/program/araç/derleme etiketleri karışıktır. aggregator blokları, registry yerleri ve envanter URL'leri farklı ölçülerdir. Satır düzeyi CSV ve sayım summary.json yedekte.
- latest.json üretim tarihi 2026-10-09T19:38:21; 188 çekilmiş, 186 tekilleşmiş; kabul 5/inceleme 11/izleme 21/genel 44/ret 105. Yerel public/data.json 81 öğe ve aynı üretim tarihini taşıyor. Bu tarihsel sonuç yeniden kaynak taraması değildir.
- Yedek snapshot dosyalarının tümü manifest SHA-256 değerleriyle doğrulandı; başlangıç uygulama/config/test/public dosyalarında değişiklik yok.
- Yerel onaylı yol: sources.json → pipeline.scan_source → scan.fetch/extractor → store calls/runs → Service.approve/domain.publishable → server /api/calls veya hibe.export.
- Statik yol: aggregator.json → collector.run → latest.json → site.build → public → ayrı Firebase CLI deploy. firebase.json Hosting public klasörünü seçer; Python API rewrite yok. Bu iki yol aynı çalışan API değildir.

### Canlı eşliği ayrıca doğrulama listesi
- [ ] Canlı /data.json üretim tarihi, öğe sayısı ve SHA-256 yerel public/data.json ile karşılaştırılmalı.
- [ ] Canlı index/app/style ve örnek ilan/ICS dosyaları yerel manifest ile karşılaştırılmalı.
- [ ] Canlı kullanıcı/admin/API akışının gerçekten hangi backend'e bağlı olduğu ölçülmeli; yerel /yonetim canlı çalışıyor sayılmamalı.
- [ ] Firebase aktif Hosting sürümü ve geri dönüş imkânı gerçek hesapta ölçülmeli; .firebaserc proje adı tek başına kanıt değildir.
Bu kontroller AŞAMA 0'da çalıştırılmadı; bilinmeyen canlı dağıtım çalışıyor diye işaretlenmedi.

## 4. Son sağlam veri/yayın korunuyor mu?
Mevcut yerel referans fotoğrafı byte düzeyinde korundu. Bu fotoğrafın insan onaylı/güncel çağrı kabulü olduğunu iddia etmiyoruz.
- Yedek: C:/hibe-radari/.agent/backups/stage0-20261010-003950.
- Toplam 201 dosya; snapshot içinde kod, web, config, tests, docs, temel proje dosyaları, latest.json ve public mevcut. Sır dosyaları, .env, kullanıcı DB'si ve .git dizini bu dosya yedeğine alınmadı.
- latest.json SHA-256: 41bdccb3be3cf55dcf14d56de2d99a295ecfc3a67f2345fb7af8e4a3198e1362.
- public/data.json SHA-256: 9501b4d93f7f65bc4cfb605030b719bb791095570b4df5d2ea52d245d2cae52f.
- 126 dosyalık public manifest SHA-256: 0322b72d91b7902986502df6439a3f4beecc6d7c24f1ac97bd83883255be39b5.
Manifest toplamı, manifest.before.json'daki path'i public/ ile başlayan sıralı kayıt listesinin json.dumps(sort_keys=True,separators=(',',':'),ensure_ascii=False) UTF-8 çıktısının SHA-256 değeridir. Her dosyanın ayrı size/hash bilgisi de kayıtta bulunur.
MVP.md plan/ilerleme değişikliği bilinçli istisnadır. Yeni sonuç/devir kayıtları referans fotoğrafını değiştirmez.

## 5. Risk ve geri alma
Mevcut onaysız üretim/veri kaybı, tarih, query, tekilleştirme ve ağ sorunları MEVCUT_SISTEM_ANALIZI.md içinde açık; AŞAMA 0 bunları düzeltmedi. Toplayıcı/site üretim komutları bu yüzden çalıştırılmadı.
Geri dönüş: manifest.before.json'dan gereken dosyanın yolu/hash'ini bul; snapshot içindeki kopyayı yalnız o hedefe kopyala; hash eşliğini kontrol et. Bütün çalışma ağacını reset/clean ile temizleme. Yedek kendi oluşturulduğu andaki unstaged/untracked kodu da içerir; sonraki değişiklikleri körlemesine ezme. Canlı deploy/rollback gerçekleştirilmedi.

### Mevcut çalışma komutları (öğrenildi; yan etkili olanlar çalıştırılmadı)
- Yerel demo: python -m hibe.server --demo veya run_demo.bat; 127.0.0.1:8000. Yeniden demo başlatmak seed/DB işlemi yapabilir; bu aşamada başlatılmadı.
- Registry: python -m hibe.registry; --strict eksikler nedeniyle başarısız olması beklenir, bu bir yeni parser doğrulaması değildir.
- Toplama/üretim: python -m hibe.aggregator --site public. Ağ ve çıktı yazımı yapar; AŞAMA 0'da çalıştırılmadı.
- Eski onaylı yol: python -m hibe.pipeline --fake/--firebase; --fake kaynak fetch'ini kendiliğinden ağsız yapmaz. Çalıştırılmadı.
- Yayın: firebase deploy --only hosting --project hibe-radari-tr. .firebaserc default aynı proje; firebase.json public kökü. Deploy gerçek yetki/hesap ve kullanıcı onayı gerektirir, çalıştırılmadı.
- UI/test yönergeleri README.md, kaynak komutları docs/AGGREGATOR.md, uygulanmış komut girişi aggregator/__main__.py ve yayın ayarı firebase.json üzerinden doğrulandı.

## 6. Sıradaki aşama
AŞAMA 1 — Veriyi silmeyen yayın güvenlik kapısı. Başlanmadı; onay bekleniyor.
