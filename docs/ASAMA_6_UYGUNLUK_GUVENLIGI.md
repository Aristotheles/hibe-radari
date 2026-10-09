# AŞAMA 6 — Kanıtlı uygunluk ve AI denetimi

2026-10-10 · C:/hibe-radari · Codex · FEATURE kontrolleri geçti.

## İşlevler
`hibe.eligibility.assess` okul/devlet lisesi, öğretmen, 14–18 öğrenci, okul ortaklığı ve NGO kanalı için UYGUN/UYGUN_DEĞİL/DOĞRULAMA_GEREKLİ üretir. Ülke, hedef/kurum türü, yaş, ortak zorunluluğu, başvuru yolu ve tarih alıntı/URL/kontrol zamanı taşır. Resmî kaynak koşulları doğrulanmadan kesin sonuç üretmez; yalnız URL doğrulaması yeterli değildir. Eksik/çelişkili ve kısmi yaş aralığı inceleme gerektirir. Türler burs/yarışma/öğretmen eğitimi/AB projesi/ortak arama/yıllık program olarak ayrılır; bilinmeyen tür uydurulmaz.
`RelevanceFilter` keşif puanını ayrı tutar; metadata uygunluk değerlendirmesini taşır. `bridge.publication_report` kesin hedef uygunluğu yoksa onaylı çağrıyı review etiketine alır. Yönetici paneli hedef bazlı kanıtları gösterir.
`llm.validate_evidence` gerçek kısa alıntıyla eşleşmeyen, dışlayıcı metinle çelişen veya belgesi belirlenemeyen koşulu bilinmiyor yapar. Çok belgeli kaynakta alıntı doğru belge URL'sine bağlanır. Tarih/kapanış kanıtı olmayan model iddiası kabul edilmez. `extract_with_fallback` AI başarısızken inceleme gereken kayıt üretir; eski doğru alanlar korunur, eski onay kullanılamaz. Tekrar taramada unavailable sonucu yeniden denenebilir.
Mevcut model adı gemini-3.8-flash korunmuştur; secret backend ortamındadır. Bu süreçte GEMINI_API_KEY ve FIREBASE_PROJECT_ID yok. Canlı model erişimi/sağlayıcı desteği doğrulanmadı; model çalışıyor denmez, kesin karar yerine kurallı belirsizlik yolu kullanılır.

## Kanıt
147 Python OK (10.457 s), 11 JS PASS; app.js sözdizimi/diff-check temiz. Uygunluk testleri çevre yarışması, lise/üniversite/NGO ayrımı, yaş, ülke çelişkisi, tarih, uydurma AI alıntısı, kaynak URL'sinin tek başına yetmemesi, doğru belgeye atıf, zaman damgasının içerik sürümünü değiştirmemesi, AI fallback kapsar. 127 public/latest dosyası değişmedi. Son küçük unavailable tekrar kontrolü ayrıca pipeline regresyonunda doğrulanacak.

## Sonraki adım
AŞAMA 7: 135 URL ve kurum/program kayıtları, kaynak sağlık/açma-kapama. Gerçek Gemini/Firebase hesabı ve canlı kaynak kabulü RELEASE pilotunda açık kontrol maddeleridir.
