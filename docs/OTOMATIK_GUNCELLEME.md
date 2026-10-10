# İlan güncelliği — yerel otomatik çalışma

10 Ekim 2026: Windows `HibeRadari-KaynakGuncelleme` görevi kuruldu. Yerel saatle 00.15, 04.15, 08.15, 12.15, 16.15, 20.15'te mevcut toplayıcıyı kontrol eder. Her kaynak kendi `interval_hours` süresi dolunca taranır; alan yoksa 24 saat. Bilgisayar açık ve kullanıcı Windows oturumunda olmalıdır. Bilgisayar kapalıyken kesintisiz güncellik sağlanmaz.

Görev aynı projenin `.venv/Scripts/python.exe` dosyasıyla ignored `.agent/refresh-real-discoveries.py` başlatıcısını çalıştırır. Başlatıcı mevcut SDK/UID kayıtlarından yalnız süreç ortamını hazırlar; ADC mevcut hesaptan kullanılır. Yeni anahtar veya hesap oluşturulmaz. İş mantığı `hibe/refresh.py`, mevcut collector, periyot denetimi ve FirestoreStore/persist_report kullanır. İkinci toplayıcı yoktur.

Yalnız `access_policy.terms_status=allowed` olan bağlantılar taranır: mevcut ölçüm 23 bağlantı. Yönetici tarafından kapatılan kaynaklar atlanır. Belirsiz veya izin gerektiren kaynaklar açılmaz. Genel haber ve reddedilmiş gürültü inceleme kuyruğuna aktarılmaz. Aynı görev eşzamanlı çalışmaz; başlatıcı dosya kilidi de kullanır.

Yeni kayıtlar onaysızdır. Kaynak içeriği değişince mevcut sürüm/inceleme kontrolü kullanılır; eski onayla yeni içerik yayımlanmaz. Görev onay vermez, Hosting dağıtmaz, public veya canonical latest raporunu değiştirmez. Son deneme `data/aggregator/refresh-attempt.json`, süreç sonucu `data/aggregator/refresh-status.json`; kaynak sağlık kayıtları mevcut Firestore panelindedir. Hata otomatik başarı sayılmaz.

İlk gerçek görev koşusu 10 Ekim 2026 14.59'da tamamlandı: Windows sonuç kodu 0, `status=not_due`, 0 tarama ve 0 değişiklik. Bugünkü sağlık kayıtlarının periyodu henüz dolmadığı için ağ taraması yapmadı. Bu kanıt bütün kaynakların yeniden tarandığı iddiası değildir. Sonraki tetik 16.15 olarak ölçüldü.

Kullanıcı listesindeki yeni filtreler: süresi dolmamış / 14 günden az kalan / tarihi belirsiz ve koşulları uygun / inceleme gerekli. Uygunluk seçili başvuru yoluna uygulanır; bilinmeyen koşullar uygun kabul edilmez. Son başvuru günü dahil; 14 günlük sınır acil gruba dahil değildir. Süresi geçmiş ilanlar backend yayın filtresinde elenir. Türkiye uygunluğu kaynak ve çağrı kanıtı gerektirir; filtre, eksik kanıtı tamamlamaz. İnsan onayı bekleyen 160 kayıt kullanıcı listesinde yayımlanmaz.

Doğrulama: 221 Python testi, 13 JavaScript testi, JS syntax ve diff check geçti. Gerçek tarayıcıda filtre seçimi, temizleme ve dar/masaüstü ekran taşma kontrolü yapıldı. İlan listesi onay yokken boş kaldı; filtre testi için sahte kayıt yayımlanmadı.
