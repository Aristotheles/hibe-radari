# İlan güncelliği — yerel otomatik çalışma

10 Ekim 2026: Windows `HibeRadari-KaynakGuncelleme` görevi kuruldu. Yerel saatle 00.15, 04.15, 08.15, 12.15, 16.15, 20.15'te mevcut toplayıcıyı kontrol eder. Her kaynak kendi `interval_hours` süresi dolunca taranır; alan yoksa 24 saat. Bilgisayar açık ve kullanıcı Windows oturumunda olmalıdır. Bilgisayar kapalıyken kesintisiz güncellik sağlanmaz.

Görev aynı projenin `.venv/Scripts/python.exe` dosyasıyla ignored `.agent/refresh-real-discoveries.py` başlatıcısını çalıştırır. Başlatıcı mevcut SDK/UID kayıtlarından yalnız süreç ortamını hazırlar; ADC mevcut hesaptan kullanılır. Yeni anahtar veya hesap oluşturulmaz. İş mantığı `hibe/refresh.py`, mevcut collector, periyot denetimi ve FirestoreStore/persist_report kullanır. İkinci toplayıcı yoktur.

Yalnız `access_policy.terms_status=allowed` olan bağlantılar taranır: mevcut ölçüm 23 bağlantı. Yönetici tarafından kapatılan kaynaklar atlanır. Belirsiz veya izin gerektiren kaynaklar açılmaz. Genel haber ve reddedilmiş gürültü inceleme kuyruğuna aktarılmaz. Aynı görev eşzamanlı çalışmaz; başlatıcı dosya kilidi de kullanır.

Yeni kayıtlar onaysızdır. Kaynak içeriği değişince mevcut sürüm/inceleme kontrolü kullanılır; eski onayla yeni içerik yayımlanmaz. Görev onay vermez, Hosting dağıtmaz, public veya canonical latest raporunu değiştirmez. Son deneme `data/aggregator/refresh-attempt.json`, süreç sonucu `data/aggregator/refresh-status.json`; kaynak sağlık kayıtları mevcut Firestore panelindedir. Hata otomatik başarı sayılmaz.

İlk gerçek görev koşusu 10 Ekim 2026 14.59'da tamamlandı: Windows sonuç kodu 0, `status=not_due`, 0 tarama ve 0 değişiklik. Bugünkü sağlık kayıtlarının periyodu henüz dolmadığı için ağ taraması yapmadı. Bu kanıt bütün kaynakların yeniden tarandığı iddiası değildir. Sonraki tetik 16.15 olarak ölçüldü.

Kullanıcı listesindeki yeni filtreler: süresi dolmamış / 14 günden az kalan / tarihi belirsiz ve koşulları uygun / inceleme gerekli. Uygunluk seçili başvuru yoluna uygulanır; bilinmeyen koşullar uygun kabul edilmez. Son başvuru günü dahil; 14 günlük sınır acil gruba dahil değildir. Süresi geçmiş ilanlar backend yayın filtresinde elenir. Türkiye uygunluğu kaynak ve çağrı kanıtı gerektirir; filtre, eksik kanıtı tamamlamaz. İnsan onayı bekleyen 160 kayıt kullanıcı listesinde yayımlanmaz.

Doğrulama: 221 Python testi, 13 JavaScript testi, JS syntax ve diff check geçti. Gerçek tarayıcıda filtre seçimi, temizleme ve dar/masaüstü ekran taşma kontrolü yapıldı. İlan listesi onay yokken boş kaldı; filtre testi için sahte kayıt yayımlanmadı.

## 2026-10-10 — Kullanıcı haftada iki çalışma istedi
Kaydı hazırlayan: Codex.
### Alınan kararlar
Önceki dört saatlik otomatik kontrol kaldırıldı. Kaynak tarama, yapay zekâ inceleme/filtreleme, temizlik ve site güncelleme için ortak hedef periyot haftada iki: salı/cuma08.15 Europe/Istanbul. HibeRadari-KaynakGuncelleme gerçek Windows tetikleri Weekly Tuesday/Friday08.15 olarak değiştirildi; sonraki13Ekim2026 08.15 ölçüldü. Kaynakların kapalı/izin koşulları korunur. İleride bağlanacak inceleme/yayın ayrı sık görev oluşturmayacak; aynı akışa bağlanacak.
### Mevcut sınır
Şu an görev kaynak keşif kuyruğunu günceller; yapay zekâ/publish/deploy henüz bağlı değil. Filtreler kullanıcı seçiminde anlık çalışmaya devam eder. Yerel bilgisayar/oturum gereksinimi sürer. Bu ayar değişiminde tarama/API/deploy başlatılmadı.
### Sonraki adım
Yetkilendirilmiş Tier1 kullanımını bütçe kontrollü şekilde bağla ve doğrula; tüm otomatik işlerin haftadaiki periyodunu koru.

## 2026-10-10 — Bilgisayardan bağımsız otomasyon düzeltmesi
Kaydı hazırlayan: Codex.
### Alınan kararlar
Kullanıcı yerel zamanlayıcıyı reddetti: tarama, kontrol, filtreleme, temizlik ve site güncellemesi bilgisayar kapalıyken de haftada iki çalışmalı. Geliştirme C:/hibe-radari içinde kalır; bulut yürütmesi bulutta geliştirme başlatmak değildir. Salı/cuma08.15 Europe/Istanbul korunur. Kullanıcı Tier1 Gemini kullanımını ve güvenli deploy/push işlemlerini ayrıca yetkilendirdi; eski ücretsiz kullanım bekleme kaydı artık geçerli değil.
### Yapılanlar
Git temiz; mevcut workflow yalnız test çalıştırıyor, üretim cron yok. gcloud billing projects describe hibe-radari-tr çıktısı billingEnabled=False. Cloud Run/Scheduler API etkin listede yok. Yerel HibeRadari-KaynakGuncelleme kapatıldı; yeniden tarama veya deploy yapılmadı.
### Açık sorular ve sorunlar
Bulut otomasyonu henüz kurulmadı. Önerilen tek rota mevcut Python toplayıcısını Cloud Run Job olarak, Cloud Scheduler salı/cuma08.15 tetikleriyle çalıştırmaktır. Bu servisler için projenin faturalandırması etkin olmalı. Gemini anahtarının başka projeden olması Hibe Radarı faturalandırmasını etkinleştirmez. Tam belge inceleme, temizlik ve güvenli yayın bağlantıları hâlâ açık; kurulmuş gibi gösterilmez.
### Sonraki adım
Kullanıcı Hibe Radarı projesine faturalandırma hesabı bağladıktan sonra mevcut kodun sunucu yürütme paketini ve dar yetkili servis kimliğini kur; gerçek ilk bulut koşusunu ve yayın kapılarını doğrula. Anahtar/şifre sohbetten istenmez.
