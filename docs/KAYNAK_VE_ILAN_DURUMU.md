# Kaynak ve ilan durumu — 10 Ekim 2026

Dosya ölçümü: `config/sources.json` 154 kayıt içeriyor. Mevcut toplayıcı yapılandırmasında 29 bağlantı var. Bunların 23'ü izin kanıtıyla otomatik taramaya açık, beşi henüz doğrulanmamış, biri izin gerektiriyor. Kullanıcının belirttiği 170 sayısı mevcut dosyalardan doğrulanmadı. Kurum, program, URL ve toplayıcı bağlantısı aynı sayım birimi değildir.

İki gerçek üstveri taramasında 23 bağlantı sağlıklı yanıt verdi. İkinci tarama 951 ayrı keşif üretti: 155 inceleme, dört izleme, 208 genel içerik ve 584 elenen kayıt. Ayrıntı metni ve başvuru uygunluğu bu taramada doğrulanmadı. Tam 29 bağlantı başarıyla çalışıyor veya bütün envanter otomatik entegre demek için kanıt yok.

Yerel gerçek uygulamanın boş görünmesinin doğrudan nedeni yeni Firestore veritabanında kayıt bulunmamasıydı. Bu taramalar daha önce geçici MemoryStore üzerinde doğrulanmış, üretim deposuna aktarılmamıştı. Mevcut `hibe.aggregator.bridge.persist_report` üzerinden 159 inceleme/izleme adayının gerçek Firestore deposuna aktarımı başlatıldı. Tamamlanma kanıtı `.agent/source-audit/firestore-import-result.json` dosyasında oluşunca sayılar ayrıca doğrulanacak; başlangıç bildirimi tamamlanma kanıtı değildir.

Aktarım yayın onayı değildir. Her duyurunun resmi metni, kesin tarih, Türkiye ve okul/öğretmen/öğrenci başvuru koşulları incelenmeden halka açık listede görünmesi beklenmez. Yönetici inceleme kuyruğu dolarken halka açık liste boş kalabilir. Bu sınır gerçek ilan eksikliğini gizlemek için kullanılmamalı: sıradaki iş güncel adayları resmi koşullarıyla hazırlayıp yönetici onayına sunmaktır.

İlk Firestore veritabanı kullanıcı onayıyla eur3 bölgesinde oluşturuldu; backend okuma HTTP200, anonim okuma HTTP403; istemci okuma/yazmasını kapatan mevcut güvenlik kuralları kuruldu. Gerçek yönetici UID Auth kaydıyla doğrulandı. Yerel uygulama localhost:8021 üzerinde çalışıyor; canlı Hosting değiştirilmedi. Kaynaklar silinmedi, eski halka açık HTML/JSON/ICS ve son sağlam rapor aktarım kapsamı dışında korunuyor.

Sıradaki tek ana adım: mevcut inceleme kuyruğunun gerçek veriyle dolduğunu doğrulamak ve güncel duyuruların resmi şartlarını hazırlamak. Engelli veya izin gerektiren kaynaklar başarısızlığı saklamak için listeden çıkarılmayacak.

Aktarım tamamlandı: gerçek Firestore sayımları 159 çağrı, 159 keşif, 23 kaynak sağlık kaydı ve sıfır yayın onayı. Son sağlam yayın hashleri aynı. Exec90359 exit0, sonuç yukarıdaki ignored kanıt dosyasında.
