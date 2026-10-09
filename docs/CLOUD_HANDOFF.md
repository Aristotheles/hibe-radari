# Hibe Radarı — Cloud çalışma kopyası

Tarih: 2026-10-10 · Hazırlayan: Codex Desktop

## Güncel kapsam ve yetki

Kullanıcı mevcut yerel projenin Cloud kopyasını güncellemeyi onayladı. Bu aktarım için commit/push yetkisi vardır; uygulama geliştirme, sonraki MVP aşaması, deploy veya canlı tarama yetkisi yoktur. Aktarım ayrı geliştirme dalında yapılır; GitHub main değiştirilmez.

Ana kaynak klasörü C:/hibe-radari olarak kalır. Cloud kendi mevcut depo klasöründe çalışır; Windows yolu Cloud üzerinde kullanılmaz. Yeni proje, ikinci toplayıcı veya ikinci backend kurulmaz.

## Önce okunacak dosyalar

1. MVP.md: güncel plan ve H ilerleme kaydı; AŞAMA 0 tamamlandı.
2. MEVCUT_SISTEM_ANALIZI.md: kanıtlı mimari ve açık hatalar.
3. docs/ASAMA_0_REFERANS.md: referans testleri, kaynak sayımı, veri hashleri ve geri dönüş kaydı.
4. AGENTS.md, README.md, docs/SECURITY.md ve docs/AGGREGATOR.md.

Eski Cloud kurulum kaydındaki 26 testli sürüm güncel değildir. Eski sabit 30 kaynak sınırı ile yeni plan çelişirse MVP.md esas alınır; mevcut 30 kayıt bu aktarımda korunur. Ek Python taslağı doğrudan kopyalanmaz/çalıştırılmaz.

## Doğrulama tabanı

- Python: python -B -m unittest discover -s tests -v → 85 test.
- JavaScript: node --test tests/test_radar.mjs → 11 test.
- Sözdizimi: node --check web/app.js, node --check web/views.mjs, node --check web/decision.mjs (ayrı komutlar).
- git diff --check. Aktarım öncesi staged kontrol yalnız ham RSS fixture tests/fixtures/aggregator/abilan_feed.xml içindeki özgün satır sonu boşluklarını işaretledi. Bu kaynak örneği byte düzeyinde korunur; kod hatası sayılmaz. Diğer dosyalar ayrı diff --check ile doğrulanır.

Cloud sanal ortamı varsa Python komutlarında .venv/bin/python kullanılır. Yeni requirements.txt bağımlılıkları mevcut ortamla karşılaştırılıp kurulur; test sonucu ölçülmeden başarılı sayılmaz. Eski başlangıç talimatındaki pipeline --fake çalıştırılmaz: güncel URL kayıtlarıyla gerçek ağ istekleri yapabilir.

## Veri ve açık riskler

13 toplayıcı bloğu, 30 registry_pending (19 candidate/11 missing), 135 farklı envanter URL'si vardır. Kurum/program kimlik sayımı henüz uzlaştırılmadı. Onaysız statik yayın, veri kaybı, tarih ve tekilleştirme bulguları açık; test geçişi bunları kapatmaz.

Yerel latest.json, public çıktıları, kullanıcı DB'si, .env, onay kayıtları ve .agent yedekleri GitHub'a aktarılmaz. Yerel geri dönüş ve SHA-256 kanıtları docs/ASAMA_0_REFERANS.md içinde bulunur. Cloud bu veriler yokken eski yayını yeniden üretmiş/korumuş olduğunu iddia etmez; gerçek tarama/üretim/deploy yapmaz.

## Bu aktarımın kabulü

Cloud mevcut dosyalarda fark varsa durup bildirir; kullanıcı değişikliklerini sıfırlamaz. İletilen GitHub dalı ve commit'e geçer, kurulum bağımlılıklarını günceller, testleri çalıştırır; HEAD, Git durumu ve test sayılarıyla yanıt verir. Kurulum taslağı değişirse yayımlama durumunu ayrıca belirtir.

Aktarım tamamlandığında durur. Sıradaki uygulama işi yalnız kullanıcı onayıyla AŞAMA 1 — Veriyi silmeyen yayın güvenlik kapısıdır. Her aşama raporlanıp doğrulandıktan sonra durulur. Sırlar yalnız güvenli backend ortamında tutulur; Gemini modeli gemini-3.8-flash. Yerel Obsidian/.agent kayıtlarına Cloud eriştiğini varsaymaz; teslim raporunu Codex Desktop yerel ortak hafızaya işler.
