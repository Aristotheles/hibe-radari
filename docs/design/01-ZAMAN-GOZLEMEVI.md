# Hibe Radarı — Zaman Gözlemevi

> LOVABLE İSTEMİ: Bu dosyanın tamamını tasarım ve prototip brifi olarak kullan. Diğer tasarım seçenekleriyle karıştırma. Önce bu yönün masaüstü ve mobil ana ekranını, sonra aşağıdaki etkileşimleri kur. Bu bir tasarım önerisidir; mevcut ürünün tamamlanmış yeteneklerini anlatan bir belge değildir.

## Tasarım fikri

Hibe fırsatlarını bir kart kataloğu yerine **zamanın içinden geçen ince bilgi şeritleri** olarak göster. Kullanıcı okuluna uygun bir fırsat ararken önce hangi çağrıya ne zaman bakması gerektiğini görsün; bir şeridi açınca başvuru yolları ve dayandıkları kanıt ortaya çıksın.

İlk ekranın karakteri: karanlık, ölçülü, teknik hassasiyeti yüksek bir zaman kompozisyonu. Eğik düzlemdeki şeritler, tek bir bakışta görülen yaklaşan tarihler ve çok iyi işlenmiş tipografi. Bilimkurgu HUD, oyun ekranı, borsa terminali veya dönen radar diski yapma. Etkileyici an, gerçek bir fırsatın zaman çizgisinden okunabilir bir inceleme yüzeyine dönüşmesi olsun.

Ürün cümlesi: **“Sıradaki fırsatın zamanı.”** Alt metin: “Başvuru yolunu, koşulları ve dayandığı kanıtı birlikte inceleyin.” Büyük kahraman alanı yerine gerçek fırsat ekranını ilk görünümde göster.

## Ürün gerçeği ve sınırlar

- Hibe Radarı okullar ve öğretmenler içindir. Temalar, doğrudan başvuru, ortaklık, öğretmen bireysel ve uygulama yeri yolları bulunur.
- Uygunluk ile inceleme önceliği ayrı kavramlardır. Yüksek öncelik başvuru hakkı veya kazanma olasılığı değildir. Yüzdelik başarı olasılığı üretme.
- Kaynak kapsamı 30'dur; mevcut envanter 19 doğrulanmamış aday ve 11 eksik kimlik içerir. “30 aktif kaynak”, canlı tarama ve gerçek fırsat sayısı iddiası yazma.
- DEMO örnekleri her görünümde DEMO olarak işaretlenir. İsim, kuruluş logosu, çağrı, tarih, bütçe, kanıt veya kaynak URL'si uydurulmaz. Tasarım verisi gerekiyorsa açıkça “DEMO — sentetik örnek” kullan; kaynak ve bütçe alanlarını bilinmiyor bırak.
- Gerçek Firebase, Google, Gemini, e-posta, ödeme veya haricî servis bağlama; anahtar isteme; yayınlama. Google giriş ve haftalık bülten canlı MVP hedefidir; demo rol seçimi gerçek Google girişi gibi gösterilmez.
- Mevcut ürün hafif HTML/CSS/JS ve Python backend kullanır. Lovable prototipinin bileşenlerini bu yapıya taşınabilir biçimde ayır. Supabase/Cloud provision etme.

## İlk görünüm — 1440 × 900

64 px yüksekliğinde yatay başlık; sabit kalın sol sidebar yok. Sol üstte özel çizilmiş açık bir kesik çizgi ve “Hibe Radarı” sözcük işareti. Ortada Fırsatlar / Aboneliğim; Yönetim yalnız yönetici rolünde. Sağda sade hesap kontrolü. Başlığın hemen altında ince fakat belirgin DEMO şeridi.

Solda 260 px genişliğinde sabit olmayan bir görev alanı: başlık, görünür etiketli arama, tema seçimi, başvuru yolu. Kalan alan zaman sahnesi ve altında okunabilir sonuç listesi. İlk görünümün en az yarısı gerçek içerik; giriş animasyonu veya slogan için boş tutulmaz.

```text
Hibe Radarı                         Fırsatlar   Aboneliğim        Hesap
DEMO — Yerel örnekler; gerçek hizmet bağlantısı yok
──────────────────────────────────────────────────────────────────────
Sıradaki fırsatın     BUGÜN              SON TARİHLER →
zamanı.              ────────────┬───────────────────────────
                     ╱ DEMO çağrı başlığı                 ╱
İlan ara             ╱ Başvuru yolu / tema                ╱
[                  ] ───────────┼───────────────────────────
Tema                 ╱ DEMO çağrı başlığı                 ╱
Başvuru yolu         ───────────┼───────────────────────────
                     Tarihi bilinmeyenler: ayrı, açık bölüm
                     ───────────────────────────────────────
Sonuç sayısı         Başlık / yol / tarih / uygunluk / kanıt
```

Şema yerleşim tarifidir; karakterleri arayüzde dekor olarak basma. Çizgiler gerçek bilgi hizalamasını kurar. Desktop ana sahne 320–380 px yükseklikte; günler okunabilir metin olarak DOM'da bulunur.

## Görsel sistem

| Öğe | Karar |
|---|---|
| Ana zemin | Mürekkep `#101719` |
| İnceleme yüzeyi | Koyu mineral `#1B2426`; kalın cam efekti yok |
| Birincil metin | Kırık beyaz `#F2F1E9` |
| İkincil metin | Sis `#ADBAB8`; gerçek zeminde kontrastı ölç |
| Tek vurgu | Kontrollü sarı-yeşil `#D8F26B`; seçili tarih ve eylem için |
| Uyarı | Kayısı `#F0B07D`; yazı ve simgeyle birlikte |
| Tipografi | Başlık/ürün: yerel WOFF2 Space Grotesk; okuma: sistem sans; sayılar tabular |
| Ölçek | Başlık 46–54 px, liste başlığı 20–24 px, metin 16 px, veri 14 px; mobil başlık 32 px |
| Kenar/ayırıcı | 1 px, çok kontrollü; 4–6 px köşe, kapsül yığını yok |
| Doku | Uzak zemin üzerinde çok hafif sabit çizgiler; metin yüzeyleri düz |

Marka fikri: sözcük işaretindeki kesik, zaman şeridindeki bugünün işaretine dönüşür. Tek motif, üç kullanım: marka, bugün, seçili kaydın açılma kesiti. Dev kısaltma logosu yapma.

## 3D imza ve kullanım gerekçesi

**İmza: seçilen zaman şeridi düzleşir ve inceleme yüzeyine açılır.** Şeritlerde derinlik abartısız, maksimum yaklaşık 8° eğim. Gölgeler yalnız ön/arka ilişkisini anlatır. Hover'da 2–3 px yükselme; klavye focus'unda aynı seçilme sinyali. Pointer takibi tüm sayfayı sallamaz.

Zaman konumu yalnız mevcut, geçerli son tarihten hesaplanır. Tarih bulunmayan kayıtlar x eksenine yerleştirilmez; “Son tarihi bilinmiyor” rafında aynı erişilebilirlikle gösterilir. Bugün ve görünür ölçek açıkça belirtilir; eksen her filtre değişiminde gizlice değişmez. Yoğun kayıtlarda üst üste yazı yerine kümeyi açan sayılı kontrol ve alttaki tam liste kullanılır.

Sahnenin çekirdeği HTML/SVG ve CSS perspective olsun. WebGL gerekli değildir. Bütün başlıklar, tarih ve eylemler semantik DOM'da kalır. 3D, veriyi bulmak için zorunlu bir mekanizma değildir; düz listeden aynı kayıt açılabilir.

## Temel etkileşimler

1. **Keşif:** arama ve filtreleme zaman şeritleriyle listeyi birlikte değiştirir. Sonuç sayısı görünür, boş sonuçta “Filtreleri temizle”. Konum/hareketle gizlenen kayıt olmaz.
2. **İnceleme:** seçilen şerit 220–280 ms içinde düz bir yüzeye dönüşür; sağda 480–560 px panel açılır. Başlık → başvuru yolu → koşullar → kanıt → resmî kaynak sırası. Açılma bitmeden metin erişilebilir olmalıdır.
3. **Uygunluk:** her başvuru yolu için ayrı sonuç ve gerekçe. Uygun / uygun değil / belirsiz; yalnız gerçekten hesaplanan durumu göster. Öncelik ayrı bir metin satırıdır, parlak oyun puanı değildir.
4. **Kanıt:** kısa alıntı ve mevcut konum bilgisi, ardından dış kaynak bağlantısı. Konum verisi yoksa “Kanıt konumu belirtilmemiş”. Tooltip tek erişim yolu olamaz.
5. **Abonelik:** temaları seç → açık, başlangıçta boş bülten onayı → kaydet. Demo mesajı gönderim yapılmadığını söyler. Giriş abonelik anlamına gelmez.
6. **Yönetim:** aynı zaman dilinde ama düz çalışma yüzeyi; inceleme kuyruğu, sürüme bağlı onay, kaynak eksikleri. Değişmiş sürümde inceleme yenilenir. Kullanıcıdan gizlemek tek başına yetkilendirme değildir.

Kaydetme, favori ve takvim ihracı mevcut backend özelliği değildir; bu prototipe sessizce ekleme. Tarihe göre filtreleme eklenirse “prototipte yerel filtre” olarak uygula; backend varmış gibi davranma.

## Mobil, durumlar, erişilebilirlik

390 px ekranda 3D sahne otomatik düzleşir; yatay kaydırma zorunlu değildir. Üstte arama ve “Filtreler” kontrolü; ardından tarih bölümleri altında tam genişlik satırlar. İnceleme paneli sayfa içinde tam ekran bölüme dönüşür, geri kontrolü scroll konumunu korur. 44 px dokunma hedefi. 320 px genişlikte ve %200 zoom'da temel görevler çalışmalı.

Yüklenme: sabit boyutlu sessiz satır iskeletleri, hızlı shimmer yok. Hata: bağlamlı mesaj ve yeniden dene. 0/1/30/100 kayıt, 140 karakter başlık, bilinmeyen tarih, farklı uzunlukta koşullar ve kanıtlar tasarlanır. Canvas/context kaybında düz liste sürer. Metin/simge ile durum bilgisi, ölçülmüş AA kontrast, görünür focus, Escape ile panel kapanışı ve tetikleyiciye focus dönüşü gerekir.

`prefers-reduced-motion` açıkken açılma/focus anında, perspective hareketi kapalı. Ekran okuyucunun erişebildiği asıl liste tek kaynak; sahnenin dekoratif tekrarları `aria-hidden` ve focus dışı olur.

## Hız hedefleri — ölçülmeden başarı ilan etme

- Ana içerik 3D yüklenmesini beklemez. Haricî video, dev model, particles, postprocessing, sürekli render yok.
- Bu konseptin 3D'si CSS/SVG; yeni WebGL paketi indirme. En fazla iki yerel font dosyası, toplam font bütçesi hedefi 120 KB.
- Filtre sonrası görünür geri bildirim hedefi 100 ms altı; liste güncellemesi ana thread'i bloke etmemeli. 100 kayıtta ölç.
- Mobil throttling ile LCP ≤2,5 s, INP ≤200 ms, CLS ≤0,1 hedeflenir; bunlar tasarım bütçesidir, sonuç iddiası değildir. Demo laboratuvar ölçümünü gerçek kullanıcı verisiyle karıştırma.
- Filtre ile üç sonuç değiştiğinde 30 öğe sırayla uçmaz; yalnız seçili öğe hareket eder.

## Lovable'ın teslim sırası ve kabul

Önce sahnesiz işleyen keşif/list/detail/mobile akışını kur. Sonra zaman şeritleri ve açılma hareketini ekle. En son rol, abonelik ve yönetici durumlarını aynı tasarım diliyle tamamla. Ana ekranı renk değişmiş standart dashboard'dan türetme.

Teslim: 1440 px masaüstü, 390 px mobil, açık fırsat/kanıt görünümü, hata ve boş durum. 3D kapalıyken aynı görevler; tarih ekseni doğru ve bilinmeyen tarihler ayrılmış; DEMO kaybolmuyor; sekme/klavye akışı çalışıyor. Ölçülmüş bundle, erişilebilirlik ve performans sonuçlarını ayrıca bildir.

**Reddetme ölçütü:** merkezi büyük slogan + üç metrik kutusu + eş kartlar, yeşil neon radar, hareketli starfield, sürekli dönen şeritler veya açık kanıt yerine “AI size en uygun fırsatı buldu” metni. Bunlardan biri ana kompozisyona dönüşürse bu brief uygulanmamıştır.

## Bu yönün riski

Gerçek veri az ve tarihler eksikse zaman sahnesi seyrek kalır. Dekoratif sahte fırsat ekleyerek doldurma; sahneyi küçült, bilinmeyenler bölümünü ve listeyi öne çıkar. Prestij, güvenilir bilgi ve ölçülü mekânsal davranıştan gelmeli.
