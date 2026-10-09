# Hibe duyuru toplayıcı (hibe.aggregator)

Kamuya açık, lise/okul/öğretmen odaklı çağrıların **üst verisini** (başlık, kurum, son tarih, hedef kitle, program, kaynak linki) toplar ve süzer. Tam metin kopyalamaz; her kayıt kaynağına bağlanır. Koruma aşma, tarayıcı otomasyonu yoktur: yalnız `httpx`, `BeautifulSoup4`, `feedparser`.

```
python -m hibe.aggregator                 # tüm kaynaklar → data/aggregator/latest.json
python -m hibe.aggregator --only eu-ft jugendbruecke
python -m hibe.aggregator --rejected      # elenenleri gerekçesiyle yazdır
```

## Kaynaklar (`config/aggregator.json`)
| Kaynak | Yol | Not |
|---|---|---|
| `eu-ft` | AB Funding & Tenders arama API'si (JSON) | Erasmus+ çerçeve programı + "school teacher pupil" metin sorgusu. Okul KA1/KA2 çağrıları ulusal ajansta (ua.gov.tr) olduğundan portalda az çıkar |
| `tubitak-4000` | RSS | Akış bayat (son çağrı 2024); 4000 sitesi güncellenirse çalışır |
| `tubitak-duyuru` | HTML liste + ayrıntı | Güncel 4004/4006/2204 çağrıları burada |
| `ab-ilan-hibe`, `ab-ilan-genel` | RSS + ayrıntı | Derleme sitesi: gürültü yüksek, resmî link adayı (`original_url`) çıkarılır |
| `stgm-hibe` | HTML kartları | Kart: başlık, konu, özet, son tarih |
| `jugendbruecke` | HTML, bir seviye tarama | Almanca; "Ausschreibung" sayfaları |

Yeni kaynak = config'e bir blok. Her kaynak yalnız `allowed_hosts` içinde dolaşır (https, yönlendirme dahil).

## Süzgeç (`config/relevance.json`, `hibe/aggregator/relevance.py`)
Her duyuru kabul / inceleme / ret alır ve **gerekçe listesi** taşır (`relevance.reasons`).
- **Puan**: hedef kitle (okul, öğretmen, genç; "eğitim" kelimesi tek başına yetmez) + program (Erasmus+, TÜBİTAK 4004–4008, gençlik değişimi, ikili değişim) + çağrı dili. Başlık/kategori eşleşmesi tam, açıklama eşleşmesi yarım ağırlıktır.
- **Düşürenler**: iş ilanı, bireysel burs, ticari/girişim, sanat/kültür, STK/insani konular, Horizon araştırma konsorsiyumları, etkinlik/kurs, lisansüstü/araştırmacı; derleme sitesi kategorileri (Kamu İş İlanları, Burs Duyuruları…).
- **Zaman kuralları** (puandan bağımsız): son tarihi geçmiş → ret; son tarih yok ve 120 günden eski → ret.
- Kabul için puan ≥ 5 **ve** okul/öğretmen/güçlü program eşleşmesi; inceleme için puan ≥ 2 ve olumlu eşleşme. İncelemedekiler insan kararı bekler.
- Son tarih yalnız "son başvuru / deadline / bis zum / kadar" gibi ipucu kelimenin yanındaysa çıkarılır; bulunamazsa boş kalır ve kayıtta "resmî sayfada doğrulayın" notu düşer. Tarih uydurulmaz.
- Elenenler `rejected` bölümünde gerekçeleriyle durur: yanlış elenen varsa terimi `relevance.json`'dan ayarlayın.

## Ağ ve TLS
Varsayılan işletim sistemi sertifika deposudur. Doğrulaması kırık bir kamu sitesi çıkarsa yalnız `tls_relaxed_hosts` listesine adıyla yazılır (varsayılan boş); yalnız o host için doğrulamasız yeniden denenir. Kaynak başına 1 sn bekleme, tanımlı `User-Agent`, 3 MB sınır.

## Kısıtlar
- Çıktı yerel `data/aggregator/` altındadır (git dışı). Sitede yayınlama, Firestore'a yazma ve zamanlama henüz yoktur.
- Çağrı durumu/uygunluk resmî sayfada teyit edilmeden "kesin" gösterilmemelidir.
- Testler: `python -m unittest tests.test_aggregator` (ağ yok, gerçek yanıtlardan küçültülmüş fixture'lar).
