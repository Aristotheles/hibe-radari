# Otomatik inceleme — 10 Ekim 2026

Mevcut yönetici kuyruğuna otomatik ön eleme eklendi. `hibe/auto_review.py` her panel yüklemesinde güncel çağrı sürümünden sınıflandırma üretir; kullanıcı 160 kaydı tek tek etiketlemez. Yeni taramadan gelen kayıtlar aynı akışa girer. Ham kayıtlar ve mevcut onaylar silinmez veya değiştirilmez.

Seçenekler: lise öğrencisi, öğretmen, okul; hibe/fon, yarışma, burs, öğretmen eğitimi, AB projesi, ortak arama; Türkiye için kanıtla uygun / kanıt eksik / uygun değil. Gruplar: fırsat adayı, haber, süresi geçmiş, Türkiye uygun değil, bilgi eksik. Varsayılan fırsat adaylarıdır; bütün kayıtlar ayrı seçenekten erişilebilir.

Gerçek yönetici ekranında 160 kayıt, 106 fırsat adayı; lise seçeneğinde 15 aday ölçüldü. Bu sayılar doğrulanmış ve açık 106 veya 15 başvuru anlamına gelmez. Başlık/metin sinyaliyle hedef kitle adaylığı çıkarılır; yalnız ülke kelimesi geçmesi Türkiye uygunluğu kanıtı değildir. Kesin olmayan/inferred tarihle kayıt kapatılmaz. Haber başlığına göre eleme bir sınıflandırma önerisidir; kayıt silinmez.

Türkiye sonucu yalnız mevcut resmî uygunluk değerlendirmesindeki ülke kanıtından alınır. Eksik/çelişkili kanıt belirsiz kalır. Türetilmiş `auto_review` istemci tarafından taslak kaydetmede gönderilse bile saklanmaz; koşul kanıtı veya yayın onayı yerine geçemez. Yeni otomatik yayın/onay açılmadı.

**Henüz tamamlanmayan kısım:** resmî tam metin/PDF koşullarının mevcut GeminiExtractor üzerinden otomatik incelenmesi. Mevcut ortamda GEMINI_API_KEY yok; gemini-3.8-flash modeliyle gerçek çağrı yapılmadı. Kullanıcıdan anahtarı sohbet yerine backend ortamına eklemesi istendi. Mevcut pipeline manuel call_urls yapılandırmasını bekler; keşif kuyruğundaki güvenilir resmî belge URL'lerine sürüm kontrollü bağlanması sonraki iştir. Tam otomatik içerik incelemesi tamamlandı denmez.

`hibe/document_review.py` mevcut extractor ve kanıt doğrulayıcıyı kullanarak ayrı `review_proposals` kaydı hazırlama adımını sağlar. Belge metni yoksa veya URL izinli host dışındaysa işlem reddedilir. Uydurulmuş alıntı uygun koşula dönüşmez. Model hatası önceki öneriyi ve doğru çağrıyı korur; çıkarım sırasında çağrı sürümü değişirse öneri saklanmaz. Çağrı veya yayın onayı bu işlemle değiştirilmez. Bu modül henüz zamanlanmış taramaya bağlanmadı; gerçek model ve canlı belge incelemesi yapılmadı.
