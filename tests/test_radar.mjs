import test from 'node:test';
import assert from 'node:assert/strict';
import { filterCalls, deadlineLabel, safeHttps, sourceSummary, normalizeSearch } from '../web/radar.mjs';
import { todayISO, daysLeft, groupOf, pathsFor, audienceCalls, calendarCells, calendarICS } from '../web/decision.mjs';

const records = [
  { id: 'unknown', title: 'Bir okul projesi', summary: '', themes: ['engelli_kapsayicilik'], paths: [{ role: 'ortak' }], deadline: null },
  { id: 'late', title: 'Bilim atölyesi', summary: 'Öğretmen', themes: ['bilim'], paths: [{ role: 'dogrudan' }], deadline: '2026-12-15' },
  { id: 'early', title: 'Su araştırması', summary: '', themes: ['cevre_su'], paths: [{ role: 'ortak' }], deadline: '2026-11-02' }
];

test('görünen Türkçe tema adı ve harfler aramada bulunur', () => {
  assert.deepEqual(filterCalls(records, { query: 'KAPSAYICILIK' }).map(c => c.id), ['unknown']);
  assert.deepEqual(filterCalls(records, { query: '  çevre ve su  ' }).map(c => c.id), ['early']);
  assert.deepEqual(filterCalls(records, { query: 'BİLİM' }).map(c => c.id), ['late']);
});

test('rol ve tema birlikte uygulanır; boş sonuç tüm listeye dönüşmez', () => {
  assert.deepEqual(filterCalls(records, { role: 'ortak', theme: 'cevre_su' }).map(c => c.id), ['early']);
  assert.deepEqual(filterCalls(records, { role: 'dogrudan', theme: 'cevre_su' }), []);
  assert.equal(filterCalls(records).length, 3);
});

test('bilinmeyen tarihler sona gelir ve orijinal sıra korunur', () => {
  assert.deepEqual(filterCalls(records, { sort: 'deadline' }).map(c => c.id), ['early', 'late', 'unknown']);
  assert.deepEqual(records.map(c => c.id), ['unknown', 'late', 'early']);
  assert.equal(deadlineLabel('2026-02-30'), 'Son tarih bilinmiyor');
  assert.equal(deadlineLabel(null), 'Son tarih bilinmiyor');
  assert.match(deadlineLabel('2026-11-02'), /2 Kasım 2026/);
});

test('kaynak bağlantısı script, http veya gömülü kimlik kabul etmez', () => {
  for (const value of ['javascript:alert(1)', 'http://example.org', 'https://user:pass@example.org', 'bozuk']) assert.equal(safeHttps(value), null);
  assert.equal(safeHttps('https://example.org/kanıt'), 'https://example.org/kan%C4%B1t');
});

test('kaynak hedefi eksik kimlik ve doğrulanmamış isimle karışmaz', () => {
  assert.deepEqual(sourceSummary([
    { name: 'Özgün isim', status: 'registry_pending' },
    { name: 'Kaynak 2 — özgün liste bekleniyor', status: 'registry_pending' },
    { name: 'Doğrulanmış kaynak', status: 'ready' }
  ]), { total: 3, missing: 1, unverified: 1 });
});

test('Türkçe aksansız ve büyük harfli arama aynı metni bulur', () => {
  assert.equal(normalizeSearch('EĞİTİM IŞIK'), normalizeSearch('egitim isik'));
  assert.equal(filterCalls(records, {query:'CEVRE'}).length, 1);
});

test('İstanbul günü UTC gece sınırından bağımsızdır', () => {
  assert.equal(todayISO(new Date('2026-10-08T21:30:00Z')), '2026-10-09');
  assert.equal(daysLeft('2026-10-09', '2026-10-09'), 0);
  assert.equal(daysLeft('2026-02-30'), null);
});

test('tarih grupları çakışmaz ve 14 günlük sınır açık kalır', () => {
  const today='2026-10-09';
  assert.equal(groupOf({deadline:'2026-10-22'},today),'Acil (14 günden az)');
  assert.equal(groupOf({deadline:'2026-10-23'},today),'Bu ay');
  assert.equal(groupOf({deadline:'2026-11-01'},today),'Daha ileri');
  assert.equal(groupOf({deadline:null},today),'Tarihi açıklanmadı');
  assert.equal(groupOf({deadline:'2026-10-08'},today),'Süresi geçti');
});

test('çok yollu çağrı okul ve bireysel görünümde ayrı yollar taşır', () => {
  const c={paths:[{role:'ortak'},{role:'ogretmen_birey'}]};
  assert.deepEqual(pathsFor(c,'school'), [{role:'ortak'}]);
  assert.deepEqual(pathsFor(c,'me'), [{role:'ogretmen_birey'}]);
  assert.equal(audienceCalls([c,{paths:[{role:'dogrudan'}]}],'me').length,1);
});

test('ay takvimi pazartesi başlar, artık yılı ve boş hücreleri korur', () => {
  const cells=calendarCells(2028,1);assert.equal(cells.length%7,0);assert.equal(cells.filter(Boolean).length,29);
  assert.equal(cells[0],null);assert.equal(cells[1],'2028-02-01');
});

test('ics yıl değişimini, Türkçeyi ve satır enjeksiyonunu güvenli işler', () => {
  const text=calendarICS({id:'demo-test',title:'Eğitim; okul, bilim\nEND:VEVENT '+ 'Ş'.repeat(90),deadline:'2026-12-31',demo:true},'http://127.0.0.1:8000/ilan/demo-test',new Date('2026-10-09T08:00:00Z'));
  assert.match(text,/DTSTART;VALUE=DATE:20261231/);assert.match(text,/DTEND;VALUE=DATE:20270101/);
  assert.equal((text.match(/\r\nEND:VEVENT/g)||[]).length,1);
  assert.ok(text.includes('Eğitim\\; okul\\, bilim\\nEND:VEVENT'));
  for(const line of text.split('\r\n')) assert.ok(Buffer.byteLength(line,'utf8')<=75);
  assert.equal(calendarICS({id:'test',deadline:null},''),null);
});
