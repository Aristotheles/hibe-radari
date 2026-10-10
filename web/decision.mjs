import { dateValue } from './radar.mjs?v=20261011-r11';

export function todayISO(now = new Date()) {
  const parts = new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Istanbul', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(now);
  return ['year', 'month', 'day'].map(key => parts.find(p => p.type === key).value).join('-');
}

export function daysLeft(deadline, today = todayISO()) {
  const end = dateValue(deadline), start = dateValue(today);
  return end === null || start === null ? null : Math.round((end - start) / 86400000);
}

export function groupOf(call, today = todayISO()) {
  if (call.application_schedule?.kind && ['rolling', 'self_paced'].includes(call.application_schedule.kind)) return 'Sürekli açık fırsatlar';
  const days = daysLeft(call.deadline, today);
  if (days === null) return 'Tarihi açıklanmadı';
  if (days < 0) return 'Süresi geçti';
  if (days < 14) return 'Acil (14 günden az)';
  return call.deadline.slice(0, 7) === today.slice(0, 7) ? 'Bu ay' : 'Daha ileri';
}

export function pathsFor(call, audience) {
  const tag = audience === 'student' ? 'student' : audience === 'me' ? 'teacher' : audience === 'school' ? 'school' : null;
  if (tag && (call.audience_tags || []).includes(tag)) return call.paths || [];
  return (call.paths || []).filter(p => audience === 'all' || (audience === 'me' ? p.role === 'ogretmen_birey' : audience === 'student' ? p.role === 'ogrenci_birey' : !['ogretmen_birey','ogrenci_birey'].includes(p.role)));
}

export function audienceCalls(calls, audience) { return calls.filter(c => pathsFor(c, audience).length); }

export function fullDate(value) {
  const stamp = dateValue(value);
  return stamp === null ? 'Bilinmiyor' : new Intl.DateTimeFormat('tr-TR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }).format(stamp);
}

export function calendarCells(year, month) {
  const first = new Date(Date.UTC(year, month, 1)), offset = (first.getUTCDay() + 6) % 7;
  const count = new Date(Date.UTC(year, month + 1, 0)).getUTCDate();
  return Array.from({ length: Math.ceil((offset + count) / 7) * 7 }, (_, i) => {
    const day = i - offset + 1;
    return day > 0 && day <= count ? `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}` : null;
  });
}

function escapeICS(value) { return String(value).replace(/\\/g, '\\\\').replace(/\r\n?|\n/g, '\\n').replace(/,/g, '\\,').replace(/;/g, '\\;'); }
function foldLine(line) {
  const encoder = new TextEncoder(); let output = '', length = 0;
  for (const char of line) {
    const size = encoder.encode(char).length;
    if (length + size > 75) { output += '\r\n '; length = 1; }
    output += char; length += size;
  }
  return output;
}

export function calendarICS(call, detailURL, now = new Date()) {
  if(call.publication_status==='verification_pending') return null;
  const stamp = dateValue(call.deadline);
  if (stamp === null || !/^[a-zA-Z0-9_-]{1,100}$/.test(call.id)) return null;
  const end = new Date(stamp + 86400000).toISOString().slice(0, 10).replaceAll('-', '');
  const lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Hibe Radari//TR', 'BEGIN:VEVENT',
    `UID:${call.id}@hibe-radari.local`, `DTSTAMP:${now.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '')}`,
    `DTSTART;VALUE=DATE:${call.deadline.replaceAll('-', '')}`, `DTEND;VALUE=DATE:${end}`,
    `SUMMARY:${escapeICS((call.demo ? 'DEMO · ' : '') + call.title + ' — Son başvuru günü')}`,
    `DESCRIPTION:${escapeICS('Kapanış saati bilinmiyor. Başvurmadan önce resmî metni okuyun. ' + detailURL)}`,
    'END:VEVENT', 'END:VCALENDAR'];
  return lines.map(foldLine).join('\r\n') + '\r\n';
}
