export const themes = { engelli_kapsayicilik: 'Kapsayıcılık', cevre_su: 'Çevre ve su', bilim: 'Bilim', dil_kultur: 'Dil ve kültür', dijital: 'Dijital' };
export const roles = { dogrudan: 'Doğrudan başvuru', ortak: 'Ortaklık', ogretmen_birey: 'Öğretmen bireysel', uygulama_yeri: 'Uygulama yeri', belirsiz: 'Rol belirsiz' };
export const eligibilityLabels = { uygun: 'Uygun', uygun_degil: 'Uygun değil', belirsiz: 'Uygunluk belirsiz' };
export const conditionLabels = { saglandi: 'Koşul sağlandı', saglanmadi: 'Koşul sağlanmadı', bilinmiyor: 'Koşul bilinmiyor' };

export function safeHttps(value) {
  try {
    const url = new URL(value);
    return url.protocol === 'https:' && !url.username && !url.password ? url.href : null;
  } catch { return null; }
}

export function dateValue(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return null;
  const date = new Date(value + 'T00:00:00Z');
  return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value ? date.getTime() : null;
}

export function deadlineLabel(value) {
  const timestamp = dateValue(value);
  return timestamp === null ? 'Son tarih bilinmiyor' : 'Son tarih: ' + new Intl.DateTimeFormat('tr-TR', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }).format(timestamp);
}

export function filterCalls(calls, { query = '', role = '', theme = '', sort = 'default' } = {}) {
  const q = query.trim().toLocaleLowerCase('tr');
  const list = calls.filter(c => [c.title, c.summary, ...(c.themes || []).map(t => themes[t] || t)].join(' ').toLocaleLowerCase('tr').includes(q)
    && (!role || (c.paths || []).some(p => p.role === role))
    && (!theme || (c.themes || []).includes(theme)));
  if (sort === 'deadline') list.sort((a, b) => (dateValue(a.deadline) ?? Infinity) - (dateValue(b.deadline) ?? Infinity));
  return list;
}

export function sourceSummary(sources) {
  const missingIdentity = s => s.identity_status === 'missing' || /özgün liste bekleniyor/i.test(s.name || '');
  return { total: sources.length, missing: sources.filter(missingIdentity).length, unverified: sources.filter(s => s.status === 'registry_pending' && !missingIdentity(s)).length };
}
