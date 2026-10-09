# Hibe Radarı — Fırsat Atlası

> LOVABLE İSTEMİ: Bu belgeyi bağımsız bir tasarım brifi olarak uygula. Zaman Gözlemevi veya Kanıt Atölyesi öğelerini ekleme. Önce keşif görünümü ve eşdeğer düz listeyi, ardından seçilen fırsatın detayını tasarla. Bu konsept henüz uygulanmış ürün yeteneği değildir.

## Tasarım fikri

**İlgi temaları, arasından geçilebilen geniş üç boyutlu şeritler; fırsatlar bu şeritlerin açık okuma kenarında bulunur.** Okulun bilim, çevre veya kültür ilgisi, renkli bir filtre etiketi olmaktan çıkar ve bir keşif yüzeyine dönüşür. Atlas gerçek coğrafya değildir; temaların okunabilir mekânsal dizinidir.

Görsel dünya: ultramarin alan, porselen beyaz tipografi, geniş kıvrılmış şeritler, keskin ölçek değişimi. Grafik cesareti yüksek; bilgisayar oyunu, gezegen sistemi, metaverse, 3D dünya küresi ve küçük parlak düğüm ağı yapma. Odak serbestçe dönen bir obje değil, okunabilir bir tema kenarıdır.

Ürün cümlesi: **“Okulunuzun bir sonraki yönü.”** İlk görünümde aktif tema adı büyük ama işlevli bir seçicidir; altında gerçek fırsat başlıkları okunur. Kullanıcı 3D sahneyi keşfetmeden arama veya düz listeden aynı fırsata ulaşabilir.

## Ürün gerçeği ve kapsam

- Hedef kitle okul yöneticileri ve öğretmenler. Başvuru yolları: doğrudan, ortaklık, öğretmen bireysel, uygulama yeri.
- Uygunluk sonucu ve öncelik ayrı alanlardır; yükseklik, yakınlık, renk veya parlaklık başvuru hakkı/kazanma ihtimali olarak yorumlanmamalı.
- 30 kaynak hedeftir; mevcut 19 aday isim ve 11 eksik kimlik “30 aktif taranan kaynak” değildir. Kaynak sayısı ile ilan sayısını eşitleme.
- DEMO etiketi bütün örneklerde görünür. Kuruluş, logo, bütçe, çağrı, kanıt, URL ve tarih uydurulmaz. Sentetik içerik “DEMO — sentetik örnek”; bilinmeyen kaynak/bütçe açıkça bilinmiyor.
- Gerçek Firebase/Google/Gemini/SMTP veya ödeme bağlantısı kurma, anahtar isteme, Cloud/Supabase açma, yayınlama. Giriş ve haftalık bülten canlı MVP hedefidir; prototipte bağlı değildir.
- Mevcut asıl mimari Python + hafif HTML/CSS/JS. Prototipte görsel sahneyi veri/DOM arayüzünden ayır; taşınabilir ve opsiyonel bir enhancement olarak tut.

## İlk görünüm — 1440 × 900

Koyu ultramarin sayfada 68 px yatay başlık. Logo/sözcük işareti açık renk, sağda görev gezinmesi ve hesap. Altında DEMO bilgisi. Ana bölgenin %60'ı 3D tema şeritleri; %40'ı seçili temanın düz okunabilir fırsat listesi. Seçili tema adı sahne üstündeki büyük tipografik kontrol; şeritlerin üzerine küçük metinler kazınmaz.

```text
Hibe Radarı                            Fırsatlar  Aboneliğim   Hesap
DEMO — Yerel örnekler; gerçek hizmet bağlantısı yok
───────────────────────────────────────────────────────────────────
Okulunuzun bir sonraki yönü.          İlan ara [                    ]

BİLİM  ← tema seçici →               Bu temadaki fırsatlar
                                     DEMO · çağrı başlığı
    ╭──────── geniş kıvrımlı şerit    Yol / son tarih / uygunluk
   ╱                                 Koşulları ve kanıtı aç →
  ╰────── seçili okuma kenarı         ────────────────────────
                                     DEMO · çağrı başlığı
          diğer temaların kenarları   Yol / son tarih / uygunluk
                                     ────────────────────────
Atlas / Liste                        Sonuç sayısı · Filtreleri temizle
```

Atlasın şeritleri tema kimliğini ayırır; gerçek harita sınırları, ülke koordinatları veya kurum konumları üretmez. Kaynak boşluğu sahneyi doldurmak için yüzlerce düğüme dönüştürülmez.

## Görsel sistem

| Öğe | Karar |
|---|---|
| Ana zemin | Derin ultramarin `#182C88` |
| Metin/okuma yüzeyi | Porselen `#F6F4EB` |
| Okuma yüzeyi metni | Gece `#14204A` |
| Seçilmemiş şerit | Tonal mavi `#334EB0`; UI metni için otomatik kullanma |
| Seçili kenar | Sıcak mercan `#FFAD87`; kısa ve işlevli vurgu |
| İkincil metin | Açık mavi-gri `#C5D0F2`; kontrastı ölç |
| Tipografi | Yerel WOFF2 Bricolage Grotesque display + sistem sans body |
| Ölçek | Aktif tema 64–88 px, kısa ürün başlığı 24–30 px, ilan başlığı 22–26 px, gövde 16 px |
| Geometri | Geniş şeritler + düz listeler; aynı boyut kutu tekrarı yok |
| İkonlar | Özel 1,5 px çizgi ailesi; yıldız/sihir/AI sparkle yok |

Tema adını eğik perspektifte veya baş aşağı döndürme. Büyük yazı tasarımın navigasyonudur; hiçbir kayıt büyük sloganın altında ekran dışında kalmaz. Çok uzun tema adlarında boyutu azaltmak yerine iki satır ve stabil alan kullan.

## 3D imza ve fiziksel davranış

**İmza: tema seçildiğinde geniş şerit bir kez açılır, sabit bir okuma kenarı oluşturur.** Şeritlerin nesne hissi geometriden gelir; parlak krom, cam lens, ışık patlaması ve yüzen kürelerden gelmez. Düşük parlaklıklı tek malzeme, iki basit ışık, yumuşak ton ayrımı. Tema değişiminde 250–350 ms kamera/şerit geçişi; otomatik dönüş yok.

Tema sırası metin kontrolünde sabittir. 3D yerleşim kategori ayrımıdır, sayısal eksen veya uygunluk sıralaması değildir; küçük legend bunu belirtir. Tema içindeki fırsatlar sağ listede açık sıralanır. Bir çağrı birden çok temaya bağlıysa farklı temalarda görülebilir ama toplam sonuç sayısı kimlik üzerinden tekilleşir. Çift ilan yaratma.

Gerçek çağrı başlığı ve eylemler DOM'da kalır. 3D sahnede yalnız büyük tema geometrisi ve seçilme sinyali bulunur. Shader içindeki minik metin, hover noktası veya ışık şiddetiyle bilgi verme. Kullanıcı bir şeride tıklayabilir; klavye, tema seçici ve liste aynı sonucu üretir. Sürükleme yalnız isteğe bağlı kısa yön değişimi; serbest kamera ve zorunlu gezinti yok.

Uygulama önce CSS/SVG katmanlı şeritlerle yapılabilir. Gerçek yüzey kıvrımı gerekli görülürse tek, lazy-load edilen WebGL sahnesi kullan; belirli framework/package sürümünü bu dosyadan tahmin etme. WebGL kodu ve bağımlılığı ayrı chunk'tır; başarısız yükleme diğer arayüzü etkilemez.

## Görev akışları

1. **İlgi bul:** tema seçici veya arama. Temalar dekorasyon değil mevcut veri alanlarıdır. Yeni tema etiketi icat etme.
2. **Daralt:** görünür başvuru yolu ve sıralama kontrolü. Liste ekranı aynı filtreleri taşır; görünüm değişince filtre ve seçili kayıt korunur.
3. **İncele:** çağrı seçilince sağ alan genişler ve gerekirse atlas daralır. Başlık → mevcut tarih → yollar → koşul/uygunluk → kanıt. 3D, okuyucunun görüşünü kapatmaz.
4. **Kanıta git:** gerçek alıntı/konum ve varsa kaynak bağlantısı. Eksik konum veya tarih açık metinle belirtilir. Tasarım uğruna kaynak logosu/sahte PDF sayfası oluşturma.
5. **Tercih:** tema seçimi ve bülten onayı ayrı formdur; atlas üzerinde temaya bakmak otomatik abonelik değildir.

Favoriler, okul profili sihirbazı, başvuru gönderme, ekip alanı ve takvim senkronu mevcut ürün özelliği değildir. Bu briefte yalnız gerekli mevcut akışlar kurulur; “premium” ödeme planı anlamına gelmez.

## Alt ekranlar ve durum tasarımı

**Aboneliğim:** atlas tonları korunur ama form düz porselen yüzeyde. Başlangıçta boş e-posta onayı, kayıt sonucu ve demo gönderim sınırı görünür. Kaydetme sırasında yinelenen istek engellenir.

**Yönetim:** büyük 3D sahne yok; ultramarin başlık ve aynı tipografik sistem içinde düz inceleme kuyruğu. Koşul/kanıt, görülen sürüm, onay ve kaynak eksikleri. 30 hedef / 19 aday / 11 eksik kimlik gerçek olarak gösterilir. Tasarım hiçbir kaynağı hazır ilan etmez.

**Boş tema:** şerit kalabilir; liste “Bu filtrelerle fırsat yok” ve temizleme eylemi. “Yakında yüzlerce fırsat” iddiası yok. **Veri hatası:** atlası başarı durumunda dondurmak yerine veri kullanılamıyor mesajı. **Sahne hatası:** otomatik düz liste ve tekrar yükleme seçeneği. **Yüklenme:** önce liste kabuğu, sonra sahne; tüm sayfa perde arkasında beklemez.

## Mobil ve erişilebilirlik

390 px ekranda tema seçici ve en fazla 120 px yüksekliğinde statik şerit kesiti; ardından liste. Gerçek WebGL mobilde varsayılan olarak yüklenmez; “3D görünüm” isteğe bağlı kontrol olabilir. 320 px ekranda sahne kalkabilir. Büyük tema metni 36–44 px; yatay taşma ve zorunlu scroll yok.

Keyboard listesi, arama label'ı, focus, 44 px hedefler, AA kontrast, %200 zoom ve reduced-motion tasarlanır. Sahne dekoratifse `aria-hidden`; kategori seçimi erişilebilir DOM kontrolündedir. Sahne elemanlarını ikinci kez tab sırasına ekleme. Hover, basılı tutma ve sürükleme tek erişim yolu değildir.

0/1/30/100 kayıt, tek tema, birçok tema, uzun başlık, aynı çağrının birden çok teması, bilinmeyen tarih/kanıt ve kayıt dışı kalan seçim durumları doğrulanır. Kanıt metni okuyucunun satır ve font büyütmesini destekler.

## Hız bütçesi ve geri dönüş yolu

- Liste HTML'si ve filtre JS'si sahneden bağımsız. Ana akış çalışana kadar 3D modülü indirilmez; düşük hareket tercihinde indirilmez. Mobil kullanıcı açıkça istemedikçe de indirilmez.
- Aktif olunca tek sahne, tek çizim yüzeyi; görünüm/sekme dışındayken render durur. Değişim bittiğinde sürekli loop çalışmaz.
- Tasarım hedefi: başlangıçta 3D'den sıfır ek ağ yükü; opsiyonel sahne JS+asset sıkıştırılmış toplam ≤350 KB. Aşılırsa CSS/SVG çözümüne dön. Bu bütçe ölçülmeden tutturulmuş sayılmaz.
- İlk sürümde haricî model, HDRI, video, bloom, SSAO, gerçek zamanlı gölge haritası ve texture paketi yok. Nesneler basit procedural geometri.
- DPR üst sınırı 1,5; mobilde daha düşük kalite veya statik alternatif. Context lost durumunda liste ve görevler kalır.
- LCP ≤2,5 s, INP ≤200 ms, CLS ≤0,1 hedefleri mobil throttling ile ölç; sahne açık/kapalı sonuçlarını ayrı bildir. Laboratuvar sonucu saha verisi değildir.
- Font hedefi toplam ≤120 KB. Büyük tipografi SVG path veya görsel olarak render edilmez; gerçek metin.

## Teslim planı ve kabul

Önce düz tema/list/detail/role/preferences akışını kur. Sonra CSS/SVG ile katmanlı atlas kompozisyonu; bu yeterli değilse bütçeli opsiyonel WebGL. En son tema geçişi ve responsive çözümü. İlk işi 3D motorunu kurmak olarak seçme.

Teslim: 1440 px atlas, aynı filtrelerin düz listesi, 390 px mobil, açık kanıt ve boş/hata/sahne kaybı. Atlas kapatıldığında hiçbir bilgi veya eylem kaybolmamalı. Bir fırsat birden çok temada görünse de toplam tekilleşmeli. Performans ve reduced-motion sonuçlarını raporla.

**Reddetme ölçütü:** rastgele 3D dünya, dönen küre, yapay ülke noktaları, generic neon network, kartların arkasında dekor olarak WebGL, “AI fırsat evreni” sloganı, kullanıcıyı kaydı bulmak için uçurmaya/sürüklemeye zorlamak. Bu briefte görsel cesaret, işlevi gizleme izni değildir.

## Bu yönün riski

Üç seçenek içinde görsel etkisi en yüksek, teknik riski de en yüksek yöndür. Şerit sahnesi bütçeyi aşar veya tema seçimini zorlaştırırsa yavaş “premium” demoyu kabul etme; aynı görsel dünyayı CSS/SVG ve sabit kesitle koru. Kalite gerçek cihaz/prototipte ölçülmeden iddia edilmez.
