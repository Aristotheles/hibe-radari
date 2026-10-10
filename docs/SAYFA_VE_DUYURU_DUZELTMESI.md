# Sayfa ve gerçek duyuru düzeltmesi — 11 Ekim 2026

Kapsam: kısa filtreler, yenilemede kararlı kart düzeni, öğretmen kurslarının ayrılması ve gerçek ilanların toplama/yayın engelleri. Çalışma C:/hibe-radari, codex/cloud-handoff-20261010 dalında yapıldı. Bütün kaynakların entegrasyonu veya bütün proje tamamlandı değildir.

## Canlı sonuç

- https://hibe-radari-tr.web.app ilk HTML yanıtında 8 duyuru kartı ve kapalı 32 eğitim bölümü içeriyor. API toplam 40 doğrulanmış kayıt, ayrı bekleyen API 3 kayıt döndürüyor. Eğitimler hibe sayısı olarak sunulmaz.
- Masaüstünde filtre alanı 75,6 px; gelişmiş alanlar Diğer filtreler içinde. Mobil içerik/ekran genişliği 375/375 px; filtre yüksekliği 137,6 px. Jean Monnet araması 1 duyuru, 0 eğitim döndürdü. Konsolda hata gözlenmedi.
- İlk sunucu HTML'si ve etkileşimli görünüm aynı kart yapısını kullanıyor. Public JSON başlangıç verisi sayfada güvenli kaçışla taşınır; özel yönetici verisi taşınmaz. Google giriş SDK yüklemesi listeyi bekletmez. Bekleyen kayıtların arka plan isteği ana listeyi yeniden çizmez.

## İçerik hataları ve düzeltilenler

| Sorun | Değişiklik | Gerçek sonuç |
| --- | --- | --- |
| MEB yan menüsündeki eski PDF çağrı şartı sayılıyordu | section.article içinde metin ve ek çıkarımı; seçici bulunamazsa sessiz geri dönüş yok | İlgisiz yan menü belgesi inceleme girdisinden çıkarıldı; eski hata geçmişi korunur |
| YRE resmî PDF yönlendirmesi engelleniyordu | Gözlenen static1.squarespace.com CDN'i izinli host listesine eklendi | Bir gerçek PDF erişimi doğrulandı; Twinning PDF hâlâ 404, yarışma onaylanmadı |
| Düzelen belge hatası yayın kapısını kapalı tutuyordu | Başarılı yeni toplamada hata resolved, geçmiş korunur; aynı belge hash'inde mevcut AI sonucu yeniden değerlendirilir | Aynı metin gereksiz tekrar ücretlendirilmez |
| TÜBİTAK ana duyuru listesi çalıştırılmıyordu | Mevcut HTML çekicisi robots ve kamuya açık olgusal üstveri/iç doğrulama kapsamında etkinleşti | 36 gerçek kayıt, 21 ayrıntı, 0 ayrıntı hatası; tekrar kayıt üretmedi |
| 4006 başlığı AI aday seçimine girmiyordu | Bilim fuarı/destekleme programı aday ipucu | Onay yerine yalnız inceleme adayı üretir |
| 4006 ulusal uygulama kanıtı ve kısa tarih alıntısı reddediliyordu | Aynı resmî PDF'deki kamu okulu + MEB sözleşme imza şartı; kısa tarihin gerçek kapanış bağlamını doğrulama | 13. dönem 4006-A/B duyurusu 13 Kasım 2026 tarihi ve gerçek koşullarla yayımlandı |

Ülke alan adı tek başına uygunluk kanıtı değildir. Yeni ulusal koşul kuralı yalnız doğrulanmış resmî kaynağın kendi PDF'sindeki birlikte bulunan başvuru koşulları, resmî okul, sözleşme ve yerel MEB imza şartını kabul eder. Genel eğitim haberi ve yabancı çağrı karşı örnekleri reddedilir. Belirsiz kişisel koşul otomatik sağlandı yapılmaz.

## Gerçek Gemini Batch makbuzları

- aafdfb83ddf5fbe9e2dc40e6ba535704ca43ef11fd7f83417e89f3c60b2fd51e: 12 MEB/YRE aday girdisi, completed.
- 7ae9478c12735690537e28528ccc4ce85166d39df2d391e0e2a8004fec4dfd33: 1 ek MEB girdisi, completed.
- 238292f5c072b3fbfe13485b77173fff6d371dc3525f9736d8380f98e2b88c2a: 4006'nın duyuru, program sayfası ve iki güncel çağrı PDF'si, completed. Kaynak kanıtı ile yeniden değerlendirme sonunda yayımlandı.
- 57b35254d8124edbfd20f5e7b415f0fd78154699b23da642515968ac7e17c56f: 13 diğer TÜBİTAK adayı, completed. 5 ülke/başvuru kanıtı eksik, 8 geçersiz/yetersiz model kanıtı; bu sonuçlar 13 kaydın kesin uygunsuz olduğunu göstermez. Bilim Söyleşileri ve birleşik 2204 duyurusu da koşul kanıtı eksik grubundadır. Zaten mevcut 2204-A kaydı silinmedi veya yeni haberle çoğaltılmadı.
- Son toplama raporunda 1 TÜBİTAK ve 2 MEB/YRE belge hatası kaldı. Ham girdiler ve kişisel/özel yönetici verileri repoya alınmadı.

## RELEASE doğrulaması

| Alan | Sonuç / kanıt |
| --- | --- |
| Depo, mimari | PASS — mevcut Python/Firestore/JSON mimarisi, tek dal ve tek yazan ajan |
| Biçim/statik | PASS — git diff --check, compileall, app.js/views.mjs sözdizimi |
| Test | PASS — 316 Python testi 49,078 s; 17 JS testi 148,3135 ms |
| Build | PASS — refresh 17c6ced9-2072-4049-9bac-0be943eafbc5; backend b59c73a4-8665-43ce-9056-8fdaa8a7c6b7 |
| Yayın | PASS — Hosting; backend hibe-backend-00013-phh, yüzde 100 trafik; iki ürün işi ui-content-r15-20261011 |
| Gerçek bulut sonuç işi | PASS — hibe-ai-batch-results-4v69n tamamlandı |
| Veri | PASS — önceki 39 doğrulanmış kayıt korunarak 4006 ile 40 oldu; özgün yedek SHA256 978065f3518f904b88fbc1b8bd38fe805f17d398597d63382561e653ba52fec3 değişmedi |
| UX/dayanıklılık | PASS — masaüstü/mobil, gerçek arama, açılır filtre, ilk HTML kart düzeni, kapalı eğitim bölümü; SDK hata ve XSS testleri |
| Auth | Otomatik yetki testleri PASS; yeni gerçek Google yönetici oturumu bu kapsamda yeniden çalıştırılmadı |
| AI/maliyet | Aynı hash tekrar gönderilmez; anahtar backend'de. Gerçek Batch işleri tamamlandı; gerçek fatura tutarı ölçülmedi |
| Gizlilik/çevrimdışı | Özel bootstrap yok. Yeni çevrimdışı özellik yok; N/A |
| Ödeme/mağaza | Değişiklik yok; N/A |

Sonuç: Sayfa düzeltmesi ve belirtilen içerik hataları doğrulandı. Genel kaynak ve içerik kapsamı eksikliği açık; 8 duyuru yeterli içerik kapsamı olarak kabul edilmedi. Sıradaki iş mevcut adayların çağrıya özel resmî başvuru belgelerini tamamlamak ve izin/erişim engelli kaynakları tek tek kanıtla çözmektir. Kaynak taraması Salı/Cuma 08.15 Türkiye saati bulutta sürer; eski geliştirme heartbeat kapalıdır. SECURITY-REVIEW.md korunmuştur; main merge yapılmaz.
