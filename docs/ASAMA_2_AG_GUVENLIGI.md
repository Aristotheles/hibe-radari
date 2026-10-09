# AŞAMA 2 — Ağ güvenliği ve kaynak sağlığı
Mod: FEATURE · Yerel C:/hibe-radari

Yönlendirme otomatik takibi kaldırıldı; her adım HTTPS/host/port/kimlik kontrolü yapar. Gerçek DNS yanıtındaki tüm IP'ler genel adres olmalı; bağlantı seçilen IP'ye sabitlenir, Host ve TLS SNI özgün hostname olur. TLS doğrulamasız tekrar kaldırıldı. Sıkıştırılmış içerik açıldıktan sonra stream boyut sınırı uygulanır, bilinen fazla Content-Length baştan reddedilir. 429 GET tek sınırlı Retry-After tekrarı yapar; 403/404 tekrar edilmez. 60 saniyeden uzun/sonsuz Retry-After yeni koşuya bırakılır. ETag/Last-Modified JSON önbelleği data/aggregator/http-cache içinde koşular arasında korunur; 304 önceki içerikle ayrıştırılır.

Kullanım izni/evidence/tarih yoksa gerçek ağ isteği yapılmaz. config/aggregator.json mevcut 13 kaynağı silmeden unreviewed olarak açıkça kaydeder: önceki HTTP erişimi tarama izni değildir. İzin incelemesi AŞAMA 7/8'de yapılacak. İzinli kaynakta robots.txt kontrolü, Disallow ve Crawl-delay uygulanır; okunamayan robots manuel incelemeye bırakılır. Kullanıcı aracısı gerçek GitHub proje adresini taşır. data/aggregator/health.jsonl koşu geçmişini ve hata türünü kaydeder.

105 Python ve 11 JS test PASS; DNS/private IP, dış redirect'in hiç istek almaması, SNI/IP sabitleme, header/body sınırı, 429/403, kalıcı 304 önbelleği, robots/izin ve gzip regresyonları içerir. Diff-check PASS. Public/latest hashleri değişmedi. Gerçek canlı kaynak/SSL kabulü NOT VERIFIED; güvenlik ve önbellek ağsız mock ile kanıtlandı. Üretim benzeri statik çıktı AŞAMA 1 testleri içinde doğrulanır. UI değişmedi; tarayıcı/telefon N/A. Auth/ödeme/AI/veritabanı şeması değişmedi. DNS sabitleme doğrulaması HTTPX resmî sni_hostname sözleşmesine dayanır: https://www.python-httpx.org/advanced/extensions/ .

Sıradaki AŞAMA 3: tarih çıkarımı. Deploy yapılmadı; mevcut çağrılarda onay köprüsü ve kaynak kullanım izinleri tamamlanmadı.
