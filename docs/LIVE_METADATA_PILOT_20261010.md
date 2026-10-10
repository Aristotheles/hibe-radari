# Canlı üstveri kontrolü — 10 Ekim 2026

Codex Desktop, C:/hibe-radari. Mevcut toplayıcı kullanıldı; ikinci toplayıcı veya üretim veritabanı oluşturulmadı.

## Kapsam ve sonuç

Mevcut 29 connector içinden politika kaydı `allowed` olan 23 API/RSS arayüzü, `run(only=...)` üzerinden kontrol edildi. Ayrıntı zenginleştirmesi bu ölçümde kapalıydı. Diğer altı connector silinmedi, kapatılmadı veya başarılı sayılmadı.

- 23 kaynak sağlığı `success`; 50 gerçek HTTP isteği; 951 üstveri kaydı.
- Rapor durumu **partial**: 29 kaynağın tam koşusu değildir.
- Gruplar: 0 accept, 155 review, 4 watch, 208 general, 584 reject. İlgililik etiketi insan onayı değildir.
- Keşifler yalnız geçici MemoryStore içinde doğrulandı; üretim DB, insan onayı, public veya latest değiştirilmedi.
- Önceki 127 public/latest dosyasının SHA-256 değerleri aynı kaldı.
- İzinli Fetcher yolu TLS, robots, host ve boyut sınırlarını uyguladı. Bot koruması aşılmadı.

Yerel kanıt: `.agent/source-audit/allowed-live-metadata.json`, `.agent/allowed-live-metadata-log.txt`. Başlangıç 06:34:26; sonuç 06:39:56 Europe/Istanbul. Bunlar ağ, tekilleştirme ve geçici kayıt doğrulamasını birlikte kapsar.

Bu tek canlı üstveri gözlemidir. İki tam üretim koşusu, çağrı ayrıntısı, Türkiye/okul uygunluğu, gerçek yönetici onayı veya RELEASE kabulü sayılmaz.

## Tekilleştirme süresi

Bu hacimde aynı URL/başlık/dönemlerin çift başına yeniden ayrıştırılması ve bütün başlık çiftlerinde pahalı benzerlik hesabı gözlendi. Mevcut `collector.dedupe` bu sabit değerleri koşu içinde önbellekler. Benzerlik eşiği ve kimlik kuralları değişmedi; benzer başlıklar hâlâ yalnız inceleme adayıdır.

[Python difflib dokümanı](https://docs.python.org/3/library/difflib.html), `quick_ratio` ve `real_quick_ratio` değerlerinin gerçek benzerlik oranının üst sınırı olduğunu açıklar. Üst sınır 0.9 altında olduğunda pahalı hesap atlanır; eşiğe ulaşan gerçek eşleşme elenmez.

| Aynı yerel veri | Önce | Sonra | Kanıt |
|---|---:|---:|---|
| Canlı kayıtlardan 180 kayıt | 1.631 s | 0.142 s | Bütün çıktı SHA-256 değerleri aynı |
| 951 kayıt, optimize edilmiş yol | Ölçülmedi | 8.094 s | 951 kayıt korunur |

Ölçüm kopyalama ve tekilleştirmeyi kapsar; ağ veya üretim SLA karşılaştırması değildir. İlk canlı koşunun toplam süresiyle 8.094 saniye doğrudan karşılaştırılamaz. Kanıt `.agent/source-audit/dedupe-benchmark.json`.

## Doğrulama ve açık işler

FEATURE: tam 214 Python testi PASS (67.456 s); 41 hedefli tekilleştirme/aggregator testi PASS. Eşik, Unicode, uzun başlık ve ayrı resmî kimlik örneklerinde inceleme adayları eski tam benzerlik hesabıyla aynı. Önceki 11 JavaScript testi PASS; bu dilimde JS değişmedi. Diff kontrolü PASS.

AŞAMA 9 gerçek Firebase Auth/ADC/admin UID/backend erişimi bekler. AŞAMA 10 gerçek tam pilot, üretim zamanlayıcı/SMTP/onay/deploy ve hosting rollback kabulü açık. RELEASE NOT VERIFIED; mevcut canlı site korunur.
