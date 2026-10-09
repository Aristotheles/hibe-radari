# Hibe Radarı — kodlanmış başlangıç sürümü

Türkçe ilan arayüzü, admin incelemesi, sürüm onayı, abonelik tercihleri, kaynak envanteri, başlangıç büyüme sayıları, Gemini/Firebase adaptörleri ve bülten outbox'ı.

## Hemen dene

Python 3.11+ kurulu bilgisayarda proje klasörünü Codex Desktop'ta aç:

```bash
python -m unittest discover -s tests -v
python -m hibe.server --demo
```

http://127.0.0.1:8000 adresini aç. “Demoyu dene” ile yönetici veya kullanıcı rolünü seç. Yönetici olarak panelden kurgusal kaydı inceleyip onaylayabilirsin. Abonelik ekranında tema/opt-in seçebilirsin. Demo veriler yalnızca yerel SQLite data/demo.db'de tutulur; örnekler gerçek ilan değildir. Windows'ta run_demo.bat kullanılabilir.

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

26 anlamlı unit/HTTP test geçti; JavaScript sözdizimi kontrol edildi. Gerçek model/auth/SMTP testi ve görsel tarayıcı testi yapılmadı. 30 kaynak henüz taranmıyor. Pro tier alanı var; ödeme ve premium erişim yok. Büyüme sayıları kayıtlı kullanıcı ve aktif abone sayısıdır; günlük aktif kullanıcı grafiği henüz yok.

MVP.md aşamaları ve Codex devam istemini, docs/SECURITY.md canlıya çıkış sınırlarını içerir.
