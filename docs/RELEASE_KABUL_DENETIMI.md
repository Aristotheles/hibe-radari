# Üretim kabul denetimi — 10 Ekim 2026

Kaydı hazırlayan: Codex Desktop. Kök: `C:/hibe-radari`. Dal: `codex/cloud-handoff-20261010`; main değişmedi. Bu rapor MVP kapsamını daraltmaz. Yerel test başarısı canlı hizmet veya deploy başarısı değildir.

## Sonuç

**RELEASE: NOT VERIFIED.** AŞAMA9 gerçek giriş/üretim erişimi ve AŞAMA10 canlı pilot/zamanlayıcı/yayın kabulü açık. Kullanıcının tüm aşamalara kadar devam kuralı geçerli; rutin aşama onayı beklenmiyor. Gerçek hesap, yönetici kimliği veya insan onayı uydurulamaz.

## Gereksinim ve kanıt

| Gereksinim | Mevcut kanıt | Sonuç / açık iş |
|---|---|---|
| A0 önceki yayını koruma | `.agent/stage0-current.json`, yedek manifest; 127 public/latest SHA karşılaştırması | Yerel koruma PASS; yeni deploy yapılmadı |
| A1 güvenli tam koşu/onay kapısı | `collector.run`, `site.check_publication`, `tests/test_publication_safety.py` | Yerel PASS; eski canlı baseline kendiliğinden onaylı sayılmaz |
| A2 ağ/sağlık/izin | `net.Fetcher`, `run_source`, network safety testleri; kalıcı source_health | Yerel PASS; her kaynağın canlı izin/ayrıntı kabulü ayrı açık |
| A3 kanıtlı son tarih/arşiv | `textutil.deadline_details`, deadline safety testleri; belirsiz yıl/ay inceleme yolu | Yerel PASS; canlı kaynağın eksik kanıtı kesin tarih sayılmaz |
| A4 farklı çağrıları koruyarak tekilleştirme | `collector.dedupe`, identity safety testleri; GUID farklılığı korunur | Yerel PASS; benzer başlık otomatik eşleştirme değildir |
| A5 mevcut DB, sürüm ve insan onayı | `bridge.persist_report/publication_report`, `Service.save/approve`; discovery bridge testleri | Yerel PASS; gerçek editör onayı yok |
| A6 uygunluk ve AI fallback | `eligibility.assess`, `llm.validate_evidence/redact_contacts`; eligibility/redaction testleri | Yerel PASS; gerçek Gemini anahtar/çağrısı NOT RUN |
| A7 envanter ve tarama politikası | 135 URL kabul kartı, korunan 19 eski kayıt; registry/source acceptance testleri | Envanter görünürlüğü PASS; 154 kayıt, 154 çalışan kaynak anlamına gelmez |
| A8 ilk kaynak paketi ve eski entegrasyonlar | 29 aggregator yapılandırma, eski13 kimlik korunur; 22 RSS fixture arayüzü, manuel/izin yolları | Fixture/manuel görünürlük PASS; 29 canlı kaynak çalışıyor veya 127 kaynak otomatik bağlı denmez |
| A9 kullanıcı/admin ve Free/Pro | `Service.entitlements/export_csv`, App.user UID/Google/verified kontrolleri; membership/HTTP testleri; önceki masaüstü/mobil kabul | Yerel PASS; gerçek OAuth/Firestore/admin oturumu NOT VERIFIED |
| A10 iki tam toplama + hata/RSS/only/rollback | `tests/test_staging_pilot.py` 22 RSS fixture ile iki koşu; gerçek alt süreç kesintisi ve kurtarma testleri | Offline PASS; 29 kaynaklı iki canlı tam koşu NOT RUN |
| A10 kaynak periyodu ve sürekli çalışma | `collector.due_sources`, CLI `--scheduled`, beş schedule testi | Periyot hesabı PASS; işletim sistemi/üretim zamanlayıcısı kurulmadı; kısmi koşu ana yayını korur |
| A10 canlı yayın ve geri dönüş | Yerel atomik build+journal/önceki yedek manifest eşliği | Yerel PASS; deploy, canlı JSON/kart sayısı ve hosting rollback NOT RUN |
| Gerçek bülten/abonelik | Prepare/send_pending opt-in, HMAC/idempotency ve TLS context testleri | Yerel PASS; gerçek SMTP/gönderici altyapısı NOT RUN; gönderim kapalı |
| Tahsilat | Backend payments_enabled=false | Üretim ödeme N/A: MVP henüz tahsilat açmıyor; gerçek sağlayıcı/webhook/iptal/iade yok |

## Ölçülmüş üretim engelleri

- `.venv/Scripts/python.exe -m hibe.server --check`: missing `FIREBASE_PROJECT_ID`, `FIREBASE_WEB_API_KEY`, `FIREBASE_AUTH_DOMAIN`, `FIREBASE_APP_ID`, `ADMIN_UID`; backend_credentials=false, ready=false, DefaultCredentialsError. Sır değerleri rapora yazılmadı.
- Firebase WEB uygulaması daha önce gerçek CLI ile oluşturuldu; bu işlem Firebase Auth başlatılması veya yönetici erişimi kanıtı değildir. Son gerçek Auth/provider ölçümü CONFIGURATION_NOT_FOUND; `.agent/firebase-auth-observation.json`. Bu dilimde API ölçümü tekrarlanmadı.
- Tarayıcıda projeye yetkili hesap oturumu bulunmadığı önceki gerçek konsol kontrolünde ölçüldü. Kullanıcıya gereken hesap erişimi ve yönetici UID sorusu zaten iletildi; yanıt bekliyor.
- `firebase.json` yalnız hosting içeriyor, `/api` backend rewrite yok. Python server yerel giriş/yönetim/Firestore API'sidir; Hosting'e statik dosya yüklemek bu sunucuyu çalıştırmaz. Üretim backend konumu ve erişimi doğrulanmadan canlı giriş ilan edilemez.
- Mevcut yapılandırmada incelenmemiş kaynak politikaları görünür ve ağ katmanında engellenir. Sessizce çıkarılarak kalan22 için tam29 canlı pilot başarı iddiası yapılmayacak.

## PROJECT VERIFICATION REPORT

| Alan | Durum | Kanıt / sınır |
|---|---|---|
| Repository/toolchain | PASS (yerel) | Windows, mevcut .venv/Python/Node; gereksiz DB/framework değişimi yok |
| Format | PASS | git diff --check; fixture özgün byte korunur |
| Static analysis | PASS (sınırlı) | compileall hibe; app/radar/decision/views Node syntax; ayrı linter/type sistemi yok |
| Tests | PASS | 196 Python, 62.583s; 11 JS, sıfır fail; `.agent/release-local-tests.txt` |
| Build/platform | PASS (offline); NOT VERIFIED (üretim) | Staging build testleri HTML/JSON/ICS; mevcut Windows kabul; uzak Ubuntu/Windows CI son yerel commitler için henüz koşmadı |
| Architecture | PASS (yerel); NOT VERIFIED (deploy) | Mevcut collector/records/store/server korunur; üretim API konumu eksik |
| Data/content | PASS (yerel); NOT VERIFIED (canlı onay) | Version/onay/deadline/GUID/None koruma testleri; test-admin gerçek kullanıcı onayı değildir |
| Auth/backend | NOT VERIFIED | Gerçek Firebase giriş, UID ve ADC eksik; mocks gerçek erişim kanıtı değildir |
| AI/cost | PASS (fallback); NOT RUN (gerçek model) | Anahtar backend, çağrı tavanı mevcut; gemini-3.8-flash gerçek çağrısı yok |
| Offline/persistence | PASS (kapsam) | SQLite mevcut records yapısı; iki fixture koşu; süreç kesintisinde site ve latest birlikte geri gelir |
| Accessibility/UX | PASS (sınırlı önceki kabul) | Masaüstü/390px yerel kontrol ve filtre/tarih testleri; fiziksel cihaz/ekran okuyucu NOT RUN |
| Secrets/privacy | PASS (bu değişiklik) | Secret değer yazılmadı; log/session/local Firebase config Git dışında; opt-in ve TLS testi |
| Reliability | PASS (yerel) | HTTP503/bakım RSS/only/boş/yarım yayın/telefon-tarih/periyot sınırı testleri |
| Diff review | PASS | Yalnız ilgili kod/test/ilerleme; üretim public/latest korunur |

## Sıradaki tek ana adım

Projeye yetkili gerçek Firebase hesap erişimi, Google provider ve yönetici UID ile AŞAMA9 canlı kabulünü tamamlamak. Bu erişim beklerken bağımsız yerel kabul eksikleri giderilir. Ardından aynı mevcut sistemle kaynak politikaları ve tam canlı staging kabulü, üretim zamanlama/backend, RELEASE ve kullanıcının yetkilendirdiği güvenli deploy doğrulanır. Rapor hiçbir eksik alanı PASS'a dönüştürmez.


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
