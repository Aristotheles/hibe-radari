# Uygunluk ve yayın kuralları düzeltme planı

Tarih: 10 Ekim 2026 · Codex. Durum: kullanıcının başla talimatıyla uygulandı; altı adımın yerel/canlı kabulü ve uygulama commit/push Linux–Windows CI doğrulaması geçti. Kaynak erişim kapsamı ayrı açık iştir. Sonuç: [UYGUNLUK_DUZELTME_SONUCU.md](UYGUNLUK_DUZELTME_SONUCU.md).

## Amaç ve sınır

Türkiye’deki lise öğrencileri, öğretmenler ve okullar için uygun gerçek fırsatları gereksiz biçimde dışlamamak. Başarı ölçütü ilan sayısı değil, yanlış elemenin azalması ve yanlış uygunluk üretmemektir. Mevcut Python/Firestore, JSON yapılandırması, çekiciler, Batch iş akışı ve haftada iki bulut taraması korunur. Yeni toplayıcı veya veritabanı kurulmaz.

Referans: `hibe/batch_publication.py:publication_decision`, `quote_present`, `schedule_is_open`; `hibe/llm.py:validate_evidence`; `hibe/batch_pipeline.py:submit_candidates`; `hibe/gemini_batch.py:request_payload`, `poll`; `hibe/review_batch.py:document_text`, `linked_pdf_urls`. Son kayıtlı canlı checkpoint 39 ayrı fırsat; 294 Python ve 16 JavaScript testi geçmişti. Bu paragraf plan hazırlanırken kaydedilen başlangıç durumudur; sonraki gerçek test ve yeniden inceleme kanıtları sonuç raporundadır.

## 1. Kararları birbirinden ayır

Önce mevcut kararları tek anlamlı sınıflara eşle: doğrulanmış uygun, açıkça kapsam dışı, kapanmış/geçmiş, kritik kanıt eksik, kişisel koşullar kontrol edilmeli, teknik belge hatası. `invalid_evidence` uygunsuzluk anlamına gelmeyecek. AI çelişkileri ülke, hedef kitle, tarih/açıklık ve kişisel koşul alanlarına ayrı kaydedilecek; genel `ai_conflict` yerine alanların etkisi belirlenerek eski kayıtlarla uyumlu geçiş yapılacak.

Ülke, hedef kitle veya güncel açıklık çelişkisi doğrulanmış yayın için engel olmaya devam eder. Bir kişisel koşuldaki belirsizlik bu üç doğrulanmış alanı silmez. Haber, sonuç duyurusu ve geçmiş etkinlik sırf tarih/kanıt eksik diye yeni fırsat listesine alınmaz.

Kabul: aynı kayıt için kapsam dışı ile belge hatası ayrı sonuç verir; bilinmeyen kişisel koşul hiçbir zaman sağlanmış sayılmaz.

## 2. Kelime ve uzunluk kapılarını bağlamlı kanıtla değiştir

- **Ülke:** resmî uygun ülkeler listesindeki Türkiye kaydı, açık ulusal başvuru koşulları veya gerçekten ülke kısıtı bulunmayan başvuru hükmü kabul edilir. Kurumun Türkiye’de olması, Türkiye’den söz eden bir haber veya platforma erişim tek başına hibe uygunluğu sayılmaz.
- **Hedef:** başvuran türü ve katılım yolu değerlendirilir. Genel bireysel başvuru öğretmen için koşullu yol olabilir; okulun kurum olarak başvuru hakkı bundan türetilmez. Lise öğrencisinin yaş ve eğitim düzeyi erişimi ayrı doğrulanır. ESEP’te tek bir İngilizce başlık düzeni yerine resmî eğitim düzeyi bilgisi kontrol edilir; yalnız ilkokula açık kurs lise fırsatı sayılmaz.
- **Kısa kanıt:** bütün alıntılara uygulanan 12 karakter eşiği kaldırılır. Kısa bir ülke/yaş/başvuran değeri ancak resmî belgedeki uygunluk başlığı veya tablo/listesiyle birlikte doğrulanır. Kaynakta rastgele geçen “Türkiye” yeterli değildir. Alıntı, kaynak URL’si ve belge hash’i korunur; uydurulmuş alıntı kabul edilmez.
- **Tarih:** kesin tarih varsa belgeyle doğrulanır. Sürekli veya kendi hızında başvuru için belirli kalıp kelimeler yerine kaynakta açık başvuru anlamı doğrulanır. Tarih açıklanmamış gerçek açık çağrı yalnız doğrulama bekleyen görünümde yer alabilir; sahte tarih veya “sürekli açık” etiketi verilmez.

Kabul: mevcut MEB ve Rufford örnekleri doğru kalır; Türkiye yalnız kurum tanıtımında geçiyorsa, öğrenci yarışması okul hibesi gibi yorumlanıyorsa veya eski kurs açık varsayılıyorsa doğrulanmış yayın yapılmaz.

## 3. Belge hatasını ilgili alanla sınırla

Bağlı PDF’ler başvuru rehberi, uygunluk, tarih, form ve ilgisiz ek olarak ayrılır. İlgisiz tek ek alınamadığında doğrulanmış ana metin değerlendirilir. Kritik koşulların yalnız alınamayan belgede bulunabileceği durumda ilgili alan doğrulama bekler.

48.000 karakter sınırı körlemesine artırılmaz. Uzun belgeler bölüm/sayfa temelli sınırlı incelemeye ayrılır; incelenen ve eksik bölümler kaydedilir. Ülke, başvuran, yaş, tarih ve zorunlu ön koşullar için kapsam doğrulanmadan tam inceleme tamamlandı denmez. Sessiz kırpma yapılmaz. HTTPS, izinli alan adları, robots ve dosya güvenliği korunur.

Kabul: ilgisiz PDF hatası doğru ana metni engellemez; eksik zorunlu rehber uygunluk üretmez; uzun belgenin son bölümündeki dışlama koşulu atlanmaz.

## 4. Sitede doğrulama ve kişisel koşulları ayrı göster

Varsayılan liste doğrulanmış fırsatlar olarak kalır. Ayrı “Doğrulama bekleyen fırsatlar” filtresi eklenir: yalnız resmî kaynaklı, gerçek başvuru fırsatı olduğu kanıtlanmış kayıtlar gösterilir; eksik alan ve kontrol tarihi açık yazılır. Bunlara onaylı/uygun etiketi, kesin olmayan geri sayım veya doğrulanmış fırsat bildirimi verilmez.

Mevcut `review_proposals` ve yayın kararları kullanılır; güvenli genel alanlar API’ye aktarılır, ham belgeler ve özel iletişim bilgileri açılmaz. Detay sayfası ve takvim aynı durumu korur. Ülke/hedef doğrulanmış ama kişisel koşullar bilinmiyorsa kart “Kişisel koşulları kontrol edin” der. Teknik olarak okunamayan sayfa tek başına ilan kartı olmaz.

Kabul: öğretmen/okul/öğrenci ve fırsat türü filtreleri iki görünümde de doğru çalışır; takvim belirsiz tarihe gün uydurmaz; bekleyen kayıt onaylı listeye sızmaz.

## 5. Mevcut kayıtları kontrollü yeniden değerlendir

Önce veritabanının mevcut kayıtları, belge hash’leri, onay sürümleri, kararlar ve canlı kimlikler yedeklenir. Karar değişiklikleri önce yayını değiştirmeyen karşılaştırma koşusunda ölçülür.

Yeni doğrulayıcıyla aynı kaynak belgelerinin kayıtlı sonuçları yeniden kontrol edilir; yalnız gerçekten yeni bağlam incelemesi gereken kayıtlar Gemini Batch’e gönderilir. Belgeleri yeniden indirmek veya bütün kayıtları ücretli incelemeye tekrar göndermek varsayılan olmaz. Gerekli yeniden inceleme, politika sürümü değiştiğinde mevcut “aynı belgeyi atla” kontrolüne takılmadan seçili kayıtlara uygulanır. Sürüm/hash eşleşmeyen eski inceleme yayımlanmaz. Her kayıt ve politika sürümü için sınırlı yeniden deneme tutulur; sonsuz tekrar ve çift gönderim engellenir.

Öncelik: ülke/hedef kanıtı eksik kayıtlar, alıntı/alan çelişkileri, tarih/açıklık belirsizliği, ardından PDF erişim/metin sınırı hataları. Açıkça kapalı veya kaynak kanıtıyla kapsam dışı kayıtlar yalnız yeni belge/değişen kanıt varsa yeniden değerlendirilir. Önce/sonra kararları ve gerekçeleri saklanır; kayıt silinmez, sayı hedefiyle onay verilmez.

## 6. Test, yayın ve geri dönüş

Her adımın ilgili testleri geçmeden sonraki adıma geçilmez. Asgari örnek seti: uygun ülke listesinde kısa “Türkiye”; tanıtımda geçen Türkiye; genel bireysel öğretmen yolu; yalnız üniversite/lisansüstü bursu; öğrenci yarışması ve okul kurumu ayrımı; sürekli açık başvuru; tarihi açıklanmamış çağrı; kapanmış haber; ilgisiz PDF hatası; eksik zorunlu rehber; uzun belgenin sonundaki dışlama; eski sürümlü onay; aynı çağrının iki URL’si ve farklı hibe aşamaları.

Bilinen olumsuz örneklerin hiçbiri yanlışlıkla doğrulanmış uygunya dönmemeli. Olumlu örnekler gerekçesiz engellenmemeli. Belirsiz örnekler açık etiketle ayrı kalmalı. Değişen kararların örnekleri kaynak belgeleriyle kontrol edilir. Python/JavaScript, Linux/Windows CI, API yetki sınırları ve gerçek tarayıcı kontrolleri tamamlanır.

Ardından mevcut geliştirme dalında commit/push ve kullanıcı tarafından önceden yetkilendirilmiş güvenli yayın yapılır; main birleştirilmez. Aynı politika backend ve iki bulut işinde kullanılır. Canlı filtreler, tarih/saat, tekrarlar ve bir gerçek sonuç-toplama çalışması doğrulanır. Geri dönüşte önceki imajla birlikte bu koşunun değiştirdiği onay/kararlar da yedekten kontrollü geri alınabilir; yalnız kod geri dönüşü veri geri dönüşü sayılmaz.

## Dosya kapsamı

`hibe/batch_publication.py`, `hibe/llm.py`, `hibe/gemini_batch.py`, `hibe/batch_pipeline.py`, `hibe/review_batch.py`, `hibe/verified_review.py`, `hibe/domain.py`, mevcut `hibe/service.py` ve HTTP yönlendirme dosyası; `web/app.js`, `web/views.mjs`, `web/radar.mjs`, gerekirse `web/decision.mjs` ve `web/index.html`; bunlara bağlı mevcut testler. API dosyasının kesin kapsamı uygulama başında mevcut yönlendirmeye bakılarak belirlenir. `MVP.md`, `.agent/HANDOFF.md` ve Obsidian ilerleme kayıtları her ana adım sonunda güncellenir.

Sıradaki tek uygulama adımı: karar sınıfları ve alan bazlı çelişkiler için testleri ve geriye uyumlu veri davranışını hazırlamak. Bu belge çalışma planıdır; kod değişikliği veya tamamlanma kanıtı değildir.
