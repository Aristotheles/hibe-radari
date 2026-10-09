import test from 'node:test';
import assert from 'node:assert/strict';
import { filterCalls, deadlineLabel, safeHttps, sourceSummary } from '../web/radar.mjs';

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
