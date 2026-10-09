# Hibe Radarı — kodlanmış başlangıç sürümü

Türkçe ilan arayüzü, admin incelemesi, sürüm onayı, abonelik tercihleri, kaynak envanteri, başlangıç büyüme sayıları, Gemini/Firebase adaptörleri ve bülten outbox'ı.

## Hemen dene

Python 3.11+ kurulu bilgisayarda proje klasörünü Codex Desktop'ta aç:

```bash
python -m unittest discover -s tests -v
node --test tests/test_radar.mjs
python -m hibe.server --demo
```

http://127.0.0.1:8000 adresini aç. Lovable karar aracı tasarımı mevcut hafif web yapısına uygulandı: “Okulum / Ben”, Türkçe/aksansız arama, tema/yol filtresi ve tarih grupları. İlanlar `/ilan/<id>` adresinde; `/takvim` son tarihleri, `/nasil-calisir` kaynak envanterini gösterir. JavaScript olmadan kamu içeriği HTML içinde okunabilir. Karanlık görünüm düğmesi ve mobil yerleşim vardır.

“Demoyu dene” kamu sitesinde kullanıcı demosunu açar. Abonelik tercihlerine `/aboneligim` adresinden erişilir. Yönetici demosu için ayrı http://127.0.0.1:8000/yonetim adresini açıp giriş alanını kullan; kamu gezinmesinde yönetici bağlantısı yoktur. Backend yetki ve sürüm onayı korunur. Demo veriler yerel SQLite data/demo.db'de tutulur; gerçek hizmet veya e-posta bağlı değildir. Örnekler DEMO etiketlidir. Tarih/koşul/kanıt bilinmiyorsa uydurulmaz. Windows'ta run_demo.bat kullanılabilir. Node.js 24 yalnız JS testleri içindir. Uygulama kanıtı: [docs/LOVABLE_APPLIED.md](docs/LOVABLE_APPLIED.md).

## Firebase ve Google giriş

1. Ana bilgisayarındaki diğer Gmail ile Firebase projesini oluştur. Bu proje sahibi hesabı, site yöneticisi hesabından farklı olabilir.
2. Authentication → Google sağlayıcısını etkinleştir; test domainini Authorized Domains'e ekle.
3. Firebase web yapılandırmasındaki değerleri .env.example isimleriyle işletim sistemi ortamına tanımla. .env dosyası kendiliğinden okunmaz. PowerShell örneği: `$env:FIREBASE_PROJECT_ID='proje-id'`.
4. Senoltemur@gmail.com Google hesabının Firebase Authentication UID'sini al; ADMIN_UID olarak tanımla. UID kurulmadan admin yetkisi verilmez. Giriş email_verified ve google.com sağlayıcısı gerektirir.
5. Firestore bölgesi ve kişisel veri koşullarını belirle; firestore.rules ile istemci erişimini kapat. Backend için en az ayrıcalıklı servis kimliği ayrıca gerekir.
6. `python -m pip install -r requirements.txt`. Yerelde Google Cloud ADC kur; üretimde servis kimliği kullan. Secret veya servis hesabı JSON'unu depoya koyma.
7. `python -m hibe.server` gerçek modda açılır. Bu geliştirme sunucusudur; canlı kullanım için desteklenen sunucu, HTTPS ve SECURITY.md kontrolleri gerekir.

Gerçek giriş ve Firestore bu ortamda hesap olmadığı için denenmedi.

## Gemini ve tarama

Model: gemini-3.8-flash; GEMINI_API_KEY yalnızca backend ortamına girilir. Model değişkenle değiştirilebilir. Kaynak metni talimat sayılmaz, email/telefon maskelenir. Çağrı tavanı 30, giriş 24.000 karakter, çıkış 4096 token; gerçek fiyat/harcama limiti ayrıca kontrol edilir.

`config/sources.json`: Hedef 30 kayıt. Konuşmada adı görülen 19 isim doğrulanmamış; 11 özgün kaynak eksik. Tam listenin yerine uydurma kaynak kullanılmaz. Gerçek kaynak için `status: ready`, `type: official`, `allowed_hosts` ve `call_urls` gerekir. Her call_urls girdisi `{ "url": "https://...", "documents": ["https://...pdf"] }` biçimindedir. Liste sayfasından otomatik yeni çağrı keşfi henüz kaynak adaptörleriyle tamamlanmadı.

İnternetsiz envanter kontrolü: `python -m hibe.registry`. `--strict` eksik kimlik/URL/kontrol yolu varsa çıkış kodu 1 verir (mevcut envanterde beklenir). 30 kaydın eksikleri `docs/SOURCE_CHECKLIST.md` içindedir. Bu denetim gerçek kaynak taraması veya canlı doğrulama yapmaz.

```bash
python -m hibe.pipeline --fake
python -m hibe.pipeline --firebase
python -m hibe.export
```

Fake pipeline internetsiz LLM kullanır ama kaynak URL'leri konmuşsa fetch yine internete gider. Registry bekleyen kaynak fetch edilmez. İkinci komut gerçek Firebase ve Gemini gerektirir. Belge hash'i değişirse LLM hata verse dahi eski onay kaldırılır. Statik HTML/JSON data/export içinde üretilir.

## Haftalık bülten

Tercihler kaydedilir; gerçek gönderim varsayılan kapalıdır. SMTP sağlayıcısı henüz seçilmedi. Canlı açılıştan önce aydınlatma/saklama metni, gönderen domain, SMTP ve unsubscribe secret tanımlanır.

PUBLIC_BASE_URL HTTPS; UNSUBSCRIBE_SECRET en az 32 karakter. SMTP_HOST, SMTP_FROM, SMTP_USER/PASSWORD secret ortamda tutulur.

```bash
python -m hibe.notifications --firebase
# Açık gönderim talimatı ve NEWSLETTER_ENABLED=true olmadan gönderim yok:
python -m hibe.notifications --firebase --send
```

Hazırlama aynı hafta/kullanıcı için tek outbox kaydı üretir. Çıkış bağlantısı süreli HMAC imzalıdır ve kullanıcıya onay düğmesi gösterir; link tarayıcılarının GET ziyareti aboneliği değiştirmez. Gönderimden önce son opt-in kontrol edilir. SMTP sonucu belirsizse otomatik yeniden gönderilmez; elle mutabakat gerekir.

## Bugünkü durum

9 Ekim son doğrulaması: 37 unit/HTTP/envanter ve 5 JavaScript testi geçti; JS sözdizimi ve Python derleme kontrolü geçti. Yerel tarayıcıda ziyaretçi/kullanıcı/yönetici, arama, kanıt, tercih kalıcılığı/opt-out, demo onayı ve JSON hata akışları incelendi. 390 ve 1280 piksel görünümünde yatay taşma yok; bu kontrol gerçek telefon testi değildir. Ayrıntılı kanıt: docs/UI_VERIFICATION.md ve docs/VERIFICATION.md. Gerçek model/auth/SMTP testi yapılmadı. 30 kaynak henüz taranmıyor. Pro tier alanı var; ödeme ve premium erişim yok. Büyüme sayıları kayıtlı kullanıcı ve bülten tercihi açık kullanıcı sayısıdır; günlük aktif kullanıcı grafiği henüz yok.

MVP.md aşamaları ve Codex devam istemini, docs/SECURITY.md canlıya çıkış sınırlarını içerir.


## 10 Ekim güncel geliştirme durumu

Önceki tarihli doğrulama sayıları tarihsel kayıttır. Yerel temiz .venv: 196 Python + 11 JS testi başarılı. Kaynak envanteri135URL ve korunan19eski kayıt; aggregator29 yapılandırma içerir. 22 gerçek RSS fixture arayüzü offline uçtan uca pilotta doğrulandı; 29 canlı kaynak çalışıyor iddiası yok. Backend ücretsiz/etkin Pro CSV yetkisi uygulandı; gerçek tahsilat kapalı. DEMO onayı üretim yayınına geçmez.

Backend eksiklerini sır değerlerini göstermeden kontrol et: `.venv/Scripts/python.exe -m hibe.server --check`. Gerçek Auth/ADC/admin UID eksik; canlı giriş/Firestore/SMTP ve üretim backend/deploy doğrulanmadı. Kaynak başına izin/periyot ve gerçek yayın onayı gerekir. Güncel plan MVP.md, ortak durum .agent/HANDOFF.md; pilot kanıt docs/ASAMA_10_PILOT_HAZIRLIK.md.

Üretim kabul durumu: [RELEASE_KABUL_DENETIMI.md](docs/RELEASE_KABUL_DENETIMI.md). `--scheduled` zamanı gelmeyen kaynaklara istek göndermez; alt küme koşusu ana yayını korur. Sürekli üretim zamanlayıcısı henüz kurulmadı. Bülten TLS sertifika/hostname doğrulaması ve açık bool opt-in zorunludur; gerçek gönderim kapalıdır.
