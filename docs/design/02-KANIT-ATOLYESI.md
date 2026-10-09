# Hibe Radarı — Kanıt Atölyesi

> LOVABLE İSTEMİ: Bu dosyanın tamamına göre ayrı bir tasarım prototipi üret. Diğer iki yönle karıştırma. Önce seçilmiş bir fırsatın görüldüğü ana ekranı tasarla; boş pazarlama sayfasıyla başlama. Bu plan öneridir; yeni backend özellikleri onaylanmış veya tamamlanmış sayılmaz.

## Tasarım fikri

**Bir fırsat, kapağı açılınca başvuru yolları ve kanıt katmanları görünen bir dosyadır.** Arayüzün merkezinde sonsuz eş kartlar yerine tek bir seçilmiş fırsat; yanında taranabilir başlık dizini bulunur. Kullanıcı bir kaydı seçtiğinde aynı çalışma yüzeyinde başka dosya açar. Premium etki pahalı malzeme taklidiyle değil, çok iyi oranlar, özel harf düzeni, kesin kesitler ve özenli açılma hareketiyle oluşur.

Görsel dünya: gün ışığı, kemik rengi geniş alan, koyu mürekkep tipografi, ince kobalt işaretler ve mimari maket kesiti gibi sınırlı derinlik. Klasör ikonlarıyla dolu masaüstü taklidi, sararmış kâğıt, deri dikiş, sahte bürokratik damga kullanma. Gerçek dünya fikrini soyut geometriye taşı.

Ürün cümlesi: **“Bir fırsatı aç. Dayanağını gör.”** Bu cümle 40–48 px; seçilen gerçek içerikle yarışmaz. Arayüz kullanıcının başvuru hakkını anlamasını, belirsiz noktayı bulmasını ve kaynak incelemesine geçmesini sağlar.

## Ürün gerçeği ve sınırlar

- Okul ve öğretmen kullanıcıları; doğrudan, ortaklık, öğretmen bireysel ve uygulama yeri başvuru yolları.
- Uygunluk üç değerlidir; inceleme önceliği ayrı gösterilir. Yüksek öncelik “kazanırsınız” veya “başvurabilirsiniz” demek değildir. Doğrulanmamış garanti, AI güven yüzdesi ve bütçe üretme.
- 30 kaynak hedefi korunur. Şu an 19 aday isim ve 11 eksik kimlik vardır; “30 kaynak doğrulandı/izleniyor” yazma.
- Her sentetik kayıt DEMO etiketli kalır. Gerçek kuruluş adı, logo, tarih, URL, kanıt veya sosyal başarı iddiası uydurulmaz. Tasarım fixture'larında “DEMO — sentetik örnek” kullan; kaynağı/bütçeyi “Bilinmiyor” bırak.
- Google giriş ve haftalık bülten MVP hedefidir; canlı entegrasyon hazır değildir. Bu prototip gerçek Firebase, Gemini, SMTP, Google, ödeme veya başka servise bağlanmaz, anahtar istemez, Cloud/Supabase açmaz, yayınlanmaz.
- Asıl ürün Python backend ve hafif HTML/CSS/JS. Prototipin görsel parçaları taşınabilir olsun. Demo rol seçimi gerçek auth değildir; yönetici yetkisi sunucuda korunmalıdır.

## İlk görünüm — 1440 × 900

72 px yatay başlık: solda özel sözcük işareti, sağda Fırsatlar / Aboneliğim / hesap. DEMO şeridi her zaman görünür. Sol bölüm yaklaşık 340 px: görünür etiketli arama, açılan filtreler ve ince çizgilerle ayrılmış ilan başlık dizini. Sağdaki geniş bölüm tek bir açık fırsat dosyasıdır. Başlıklar dizinde tam okunur; kırpılmış “…” tek başına normal durum değildir.

```text
Hibe Radarı                       Fırsatlar   Aboneliğim    Hesap
DEMO — Yerel örnekler; gerçek hizmet bağlantısı yok
─────────────────────────────────────────────────────────────────
İlan ara                  Bir fırsatı aç. Dayanağını gör.
[                     ]   ───────────────────────────────────────
Tema / Başvuru yolu       DEMO · seçilmiş çağrının tam başlığı
                          Başvuru yolu      Son tarih / bilinmiyor
FIRSAT DİZİNİ             ┌─────────────────────────────────────┐
→ Seçilmiş çağrı          │ BAŞVURU YOLLARI                     │
  İkinci çağrı            │ Koşullar / uygunluk / belirsizlik   │
  Üçüncü çağrı            └─────────────────────────────────────┘
                          ╲ ince katman / kaynak ve kanıt     ╲
Sonuç sayısı              Kanıtı aç →                Kaynağa git
```

Sayfa ilk açıldığında gerçekten bulunan ilk ilan seçilebilir; filtre değişiminde seçili ilan sonuç dışına çıkarsa seçimi temizle, sessizce başka ilanı onaylatma. Tek ilan varsa boş dizini tasarım uğruna sahte kayıtlarla doldurma. Hiç ilan yoksa açık dosya alanı bağlamlı boş durum olur.

## Görsel sistem

| Öğe | Karar |
|---|---|
| Ana zemin | Kireç `#F0EEE6` |
| Dosya yüzeyi | Sıcak beyaz `#FCFBF7` |
| Ana metin | Mürekkep `#192324` |
| İkincil metin | Kurşun `#536265`; kontrastı gerçek zeminde ölç |
| Eylem/seçim | Kobalt `#2148D6`; bir yüzeyde tek baskın eylem |
| İnce katman | Açık taş `#D9D8CE`; metin için değil |
| Belirsizlik | Koyu pas `#8F4028`, açık zemin üzerinde metin/simge |
| Tipografi | Display: yerel WOFF2 Newsreader; arayüz: sistem sans; başlıklarda kontrollü serif |
| Ölçek | Display 40–48 px; kayıt başlığı 28–34 px; gövde 16–18 px; uzun kanıt 70 karakter satır hedefi |
| Şekil | Düz kenarlı panel, 2–4 px köşe; ince üst/alt çizgi; yuvarlak kutu yığını yok |
| Ritim | 8 px temel; açık dosyada 24/40/64 px aralıklar; tüm ekranı aynı boşluklarla doldurma |

Sözcük işaretinde “Radarı”nın son harfiyle hizalanan küçük açık kesit, seçili başvuru yolunun alt çizgisinde tekrar eder. Arka plan dokusu şart değildir. Premium algı için grain/glow yığma.

## 3D imza: başvuru yolunun kesiti

Açık dosya en çok üç katmana sahiptir: **çağrı / başvuru yolu / kanıt**. İlk bakışta ön yüz düz ve okunur, arkasında 2–3 ince kenar görünür. “Kanıtı aç” eyleminde yalnız ilgili katman 180–240 ms içinde 12–18 px ayrılır; ardından okunabilir düz kanıt bölümü açılır. Her koşula kanıt varsa aynı satırın işareti kanıttaki ilgili bölümü gösterir. Eşleştirme verisi yoksa çizgi icat etme; bağımsız kanıt paneli aç.

3D kâğıt kıvrılması için ağır fizik/materyal shader yok. CSS perspective, transform ve basit yerel SVG yeterli. Metin HTML'de kalır; yazıyı eğik texture veya canvas içine gömme. Seçili katman gerçek bilgi hiyerarşisini anlatır; sürükleme zorunlu değildir, açık düğmelerle kontrol edilir.

Başvuru yolu sayısı üçü aşarsa sahneye daha fazla katman yığma; düz seçici/liste kullan. İçeriği 3D'nin kapasitesine göre kesme. Kapak/katman, dosya indirme yeteneği veya gerçek PDF varmış izlenimi vermemeli.

## Temel kullanıcı akışı

1. **Bul:** arama + tema + başvuru yolu; değişen sonuç sayısı ve tek satır liste. Dizindeki seçili öğe yalnız renk değil işaret ve `aria-current` ile de belirgin.
2. **Aç:** kayıt başlığı, mevcut son tarih, başvuru yolu adları. Tarih yoksa “Son tarihi bilinmiyor”; geri sayım yok.
3. **Ayır:** seçilen başvuru yolunun koşulları ve üç değerli uygunluk sonucu. Alternatif koşullar tek yapıda korunur; “A veya B” iki zorunlu koşula dönüşmez.
4. **Dayanağa in:** mevcut kanıt alıntısı ve mevcut konumu; resmî kaynak bağlantısı varsa görünür. Kanıt yoksa “Kanıt bilgisi eksik” ve neden onay/uygunluk iddiası yapılmadığı açıkça görünür.
5. **Karar:** kullanıcı kaynağa gidebilir veya başka fırsatı açabilir. Başvurunun uygulama içinden gönderilebildiğini iddia etme.

İnceleme önceliği tarih/metaveri alanında sade satırdır. Uygunluk sonucu başvuru yolu bölümünde kalır. Büyük yeşil yüzde, 100 üzerinden halka ve ödül konfeti yok.

## Diğer ekranlar aynı dünyada

**Aboneliğim:** açık dosya alanı sade tercihler formuna dönüşür. Temalar, başlangıçta boş bülten onayı, kaydetme ve sonucu. “Demo: tercih kaydedildi; e-posta gönderilmedi.” Giriş hiçbir kutuyu otomatik işaretlemez.

**Yönetim:** solda inceleme kuyruğu, sağda aynı kanıt yüzeyi. Görülen sürüm ve onay eylemi yan yana. İçerik/sürüm değiştiğinde eylem durur ve tekrar inceleme ister. Kaynaklar ayrı düz tabloda 30 hedef / 19 aday / 11 kimlik eksik olarak gösterilir. Sırf estetik diye bilinmeyen kontrol zamanını başarı işaretine çevirme.

**Hesap:** demo rol seçimi açık “Kullanıcı demosu / Yönetici demosu”; canlı Google akışı taklit edilmez. Demo ile gerçek mod birbirine karışmaz.

## Mobil ve erişilebilirlik

390 px ekranda önce arama ve sonuç dizini; bir ilan açılınca üstte geri kontrolüyle tek açık dosya. Split-screen'i sıkıştırma. Geri dönerken filtre/scroll korunur. Katman kenarları en fazla 4 px derinlik verir; metin düz kalır. Kanıt accordion'u okuyucunun aynı yere dönmesini sağlar.

44 px hedefler, doğru input label'ları, görünür focus, mantıklı başlık sırası, yüksek kontrast ve %200 zoom gerekir. Reduced-motion'da katman ayrılması anında gerçekleşir. Hover olmadan bütün anlam ve eylemler erişilebilir. Seçim sonrası başlığa focus taşı; eylem sonucunu aria-live ile sade duyur.

0/1/30/100 ilan, 140 karakter başlık, çoklu başvuru yolu, kanıtı olmayan çağrı, uzun alıntı, güncelliği değişmiş sürüm, yüklenme/hata/boş sonuç durumlarını üret. Okunabilirlik için metni aşırı küçültme; içerik büyüdüğünde dosya yüksekliği doğal artar.

## Hız ve teknik bütçe

- CSS/SVG 3D; yeni WebGL bağımlılığı, video, dış 3D viewer veya sürekli animation loop yok.
- Ana içerik server/static veriden okunabilir DOM olarak gelir; animasyon kodu bir fırsatı açmanın önkoşulu değildir.
- En fazla iki yerel WOFF2 alt kümesi; toplam font hedefi ≤120 KB. Serif yalnız başlıkta, koşul ve kanıt okumada sans/system.
- Katman animasyonu yalnız transform/opacity; layout ölçümleri pointer hareketinde tekrarlanmaz. Hareket toplamı 240 ms üstüne uzamaz.
- Mobil throttling LCP ≤2,5 s, INP ≤200 ms, CLS ≤0,1 hedefleri ölçülür. Demo laboratuvar sonucu canlı saha performansı sayılmaz.
- Sahnede bir açık dosya bulunur; 30 ilan için 30 ayrı 3D nesne yaratılmaz.

## Uygulama planı ve teslim ölçütleri

Önce dizin + seçim + düz koşul/kanıt ekranını tamamla. Sonra dosya katman geometrisini ve tek açılma etkileşimini ekle. Son olarak abonelik/yönetim/rol durumlarını uygula. Teknoloji eklemek yerine oran, tipografi ve hareketi kesinleştir.

Teslim: 1440 px ana ekran, 390 px açık fırsat, kanıt açılmış durum, eksik kanıt, boş arama ve değişmiş sürüm. İşlevli arama/filtre, koşul/kanıt ayrımı, yönetici görünümü, tercihler. Açılan dosya hızla okunmalı; kaynak bağlantısı iki etkileşimden fazla uzakta olmamalı.

Ölçülmüş bundle/performance, klavye/reduced-motion, kontrast ve uzun metin davranışını raporla. Bunları ölçmeden “hızlı ve erişilebilir” ilan etme.

**Reddetme ölçütü:** 3D'nin sıradan kart gridinin üzerine süs olarak konması, kitap/kâğıt animasyonu uğruna bekletme, premium görünüm için dev boş hero, sahte fon kuruluşu logoları, “size %98 uygun” veya ücretli Pro plan kutuları. Bu yönde ödeme ekranı yok.

## Bu yönün riski ve seçim gerekçesi

Serif + açık zemin tek başına özgün değildir. Ayırt edici kısım, bir başvuru yolunun koşul ve kanıt katmanlarının aynı dosya kesitinde ilişkilendirilmesidir. Bu mekanizma uygulanmazsa tasarım sıradan bir dergiye dönüşür.

Üç yön içindeki **önerilen ilk üretim rotası** budur: ürünün en güçlü özelliği kanıtı görünür kılar; 3D sınırlı ama anlamlıdır; mobilde doğrudan düzleşir; mevcut hafif web mimarisine en az ek yükle uyarlanabilir. Görsel kalite yine gerçek prototipte doğrulanmalıdır.
