# Kaynak sayım uzlaştırması

2026-10-10 · Araştırma envanterinin birebir satır sayımı.

| Ölçü | Sayı |
|---|---:|
| Kullanıcının başlangıç hedefi | 127 |
| Envanterdeki adresli satır / tekil URL | 135 |
| Hedef ile ölçülen URL farkı | +8 |
| Teknik host grubu | 131 |
| Config kayıtları (envanter + korunan eski kayıtlar) | 154 |
| Envanter dışı korunan eski kayıt | 19 |
| Korunan özgün kaynak kimliği | 30 |
| Korunan mevcut çekici | 13 |

127 sayı olarak önceki hedeftir; mevcut belge 135 URL içeriyor. Sekiz adres silinmedi veya kurum sayısıyla eşitlenmedi. Aynı host, aynı kurumun kanıtı değildir: 131 yalnız teknik host grubudur; institution_name ve country bilinmediğinde null kalır, institution_identity_status=unverified_host_group açıkça yazılır. Kaynak/program etiketleri belgeden aynen gelir. Resmî kurum/program kimliklerinin kanıtla zenginleştirilmesi kaynak kabul kartlarında sürer.

Eski 30 kaydın 11'i birebir URL ile envantere eşlendi. Kalan 19 kayıt silinmeden legacy_source/legacy_placeholder olarak kapalı tutuldu. Önceki değerlerin aynısı config/sources.legacy-stage0.json içinde korunur. Toplam 154 kayıt, 154 çalışan kaynak iddiası değildir. sources.json kayıt sistemi; aggregator.json mevcut çekiciler; iki dosya birleştirilmedi. Host eşlemeleri adaydır, eu-ft kimliği envanterde açıkça yazılıdır. Tüm 13 çekici görünür eşleme taşır; çalışma/politika başarıları ayrıca doğrulanır.

| Envanter grubu | URL |
|---|---:|
| 1. AB — merkezi programlar ve araçlar | 25 |
| 2. AB — Türkiye'ye özgü ve sınır ötesi | 8 |
| 3. Türkiye — kamu | 19 |
| 4. Ülkeler — elçilik ve ikili fonlar | 31 |
| 5. BM ve uluslararası kuruluşlar | 8 |
| 6. Türkiye — vakıf ve sivil toplum | 13 |
| 7. Uluslararası — çevre, bilim, ödül ve yarışma | 20 |
| 8. Derleme siteleri (ipucu — asıl kaynakta doğrulanır) | 11 |
