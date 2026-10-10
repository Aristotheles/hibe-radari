import { themes, roles, eligibilityLabels, conditionLabels, safeHttps, deadlineLabel, filterCalls } from './radar.mjs';
import { todayISO, daysLeft, groupOf, audienceCalls, pathsFor, fullDate, calendarCells, calendarICS } from './decision.mjs';

export function node(tag, text, cls) { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; }
const $ = id => document.getElementById(id);
const roleClass = role => ({ dogrudan: 'role-direct', ortak: 'role-partner', ogretmen_birey: 'role-individual', uygulama_yeri: 'role-venue' })[role] || 'role-venue';
function icon(name = 'arrow') {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 24 24'); svg.setAttribute('fill', 'none'); svg.setAttribute('stroke', 'currentColor'); svg.setAttribute('stroke-width', '1.7'); svg.setAttribute('aria-hidden', 'true');
  const path = document.createElementNS(svg.namespaceURI, 'path');
  path.setAttribute('d', name === 'check' ? 'm5 12 4 4 10-10' : 'M6 18 18 6M6 6h12v12'); svg.append(path); return svg;
}
function badge(path) { return node('span', roles[path?.role] || 'Rol belirsiz', 'role-badge ' + roleClass(path?.role)); }
function reason(call) { return (call.themes || []).length ? (call.themes || []).map(t => themes[t] || t).join(', ') + ' konusuyla ilgili. Başvuru koşullarını ayrıca inceleyin.' : 'İlgili başvuru yolunu ve koşulları inceleyin.'; }
function checked(call) { return call.last_checked ? fullDate(String(call.last_checked).slice(0, 10)) : 'Bilinmiyor'; }
function link(href, text, cls) { const a = node('a', text, cls); a.href = href; return a; }
function countText(call) { const days = daysLeft(call.deadline); return days === null ? 'Tarih bekleniyor' : days < 0 ? 'Süresi geçti' : days === 0 ? 'Son başvuru günü' : days + ' gün kaldı'; }

export function renderListing(calls, filters, audience) {
  const items = filterCalls(audienceCalls(calls, audience).map(c => ({...c, paths: pathsFor(c, audience)})), filters);
  $('cards').replaceChildren(); $('result-count').textContent = `${items.length} fırsat ${audience === 'school' ? 'okul yollarında' : 'bireysel yollarda'} listeleniyor`;
  $('radar-title').textContent = audience === 'school' ? 'Okulun için bir sonraki fırsat.' : 'Senin için bir sonraki fırsat.';
  for (const group of ['Acil (14 günden az)', 'Bu ay', 'Daha ileri', 'Tarihi açıklanmadı', 'Süresi geçti']) {
    const list = items.filter(c => groupOf(c) === group); if (!list.length) continue;
    const section = node('section', undefined, 'opportunity-section'), heading = node('div', undefined, 'section-heading'), title = node('h2', group);
    title.append(node('span', String(list.length), 'group-count')); heading.append(title, node('span', group === 'Tarihi açıklanmadı' ? 'Son tarih kaydı yok.' : 'Son tarihe göre değerlendirin.')); section.append(heading);
    const grid = node('div', undefined, 'opportunity-grid');
    for (const c of list) {
      const paths = pathsFor(c, audience).filter(p => !filters.role || filters.role === p.role);
      const a = link('/ilan/' + encodeURIComponent(c.id) + '?audience=' + audience, undefined, 'opportunity-card');
      const top = node('div', undefined, 'card-top'); top.append(badge(paths[0]), node('span', c.demo ? 'DEMO · Kurgusal' : 'Yayımlanmış kayıt', 'program-label'));
      const row = node('div', undefined, 'card-title-row'); row.append(node('h3', c.title), icon());
      const date = node('div', undefined, 'card-deadline'), days = daysLeft(c.deadline), time = node('time', c.deadline ? fullDate(c.deadline) : 'Son tarih bilinmiyor');
      if (c.deadline) time.dateTime = c.deadline;
      date.append(node('span', countText(c), days !== null && days >= 0 && days < 14 ? 'deadline-urgent' : 'deadline-normal'), time);
      const why = node('div', undefined, 'card-reason'); why.append(icon('check'), node('span', reason(c)));
      const bottom = node('div', undefined, 'card-bottom'); bottom.append(node('span', paths.length > 1 ? paths.length + ' başvuru yolu' : eligibilityLabels[paths[0]?.eligibility] || 'Uygunluk belirsiz'), node('span', 'Son kontrol: ' + checked(c)));
      a.append(top, row, date, why, bottom); grid.append(a);
    }
    section.append(grid); $('cards').append(section);
  }
  if (!items.length) { const empty = node('div', undefined, 'empty-state'); empty.append(node('h2', 'Bu filtrelere uyan fırsat yok.'), node('p', 'Başka bir tema veya başvuru yolu seçin.')); $('cards').append(empty); }
}

export function renderDetail(call, selected = 0) {
  const target = $('detail'); target.replaceChildren();
  if (!call) { const title = node('h1', 'İlan bulunamadı'); title.id = 'detail-title'; title.tabIndex = -1; target.append(title, link('/', 'İlanlara dön', 'back-link')); return; }
  const paths = call.paths || [], path = paths[selected], result = path?.eligibility || 'belirsiz';
  const back = link('/', 'Tüm ilanlar', 'back-link'), banner = node('div', undefined, 'eligibility-banner'); banner.dataset.result = result;
  const answer = node('div'); answer.append(node('span', path?.role === 'ogretmen_birey' ? 'Bu yoldan başvurabilir misin?' : 'Okulun bu yoldan başvurabilir mi?'), node('strong', eligibilityLabels[result] || 'Uygunluk belirsiz'));
  banner.append(answer, badge(path)); target.append(back, banner);
  const layout = node('div', undefined, 'detail-layout'), article = node('article'), heading = node('div', undefined, 'detail-heading'), h1 = node('h1', call.title); h1.id = 'detail-title'; h1.tabIndex = -1;
  heading.append(h1, node('p', call.demo ? 'DEMO · Kurgusal örnek; gerçek başvuruya dayanak değildir.' : call.summary), node('p', 'Son kontrol: ' + checked(call), 'verification')); article.append(heading);
  article.append(node('p', 'Kaynak: ' + (call.organization || call.source_id || 'Bilgi kaydı yok')));
  if (call.deadline_evidence) article.append(node('p', 'Son tarih kanıtı: ' + call.deadline_evidence, 'evidence'));
  if (call.deadline_precision && call.deadline_precision !== 'day') article.append(node('p', 'Son tarih kesin değil; doğrulama gerekli.', 'verification'));
  const facts = node('div', undefined, 'facts-grid');
  const support = call.budget_max != null ? new Intl.NumberFormat('tr-TR').format(call.budget_max) + (call.currency ? ' ' + call.currency : ' · para birimi bilinmiyor') : 'Bilgi kaydı yok';
  for (const [label, value, note] of [['Son başvuru', call.deadline ? fullDate(call.deadline) : 'Tarihi açıklanmadı', 'Kapanış saati bilinmiyor'], ['Destek', support, 'Yalnız mevcut veri gösterilir'], ['Eş finansman', 'Bilgi kaydı yok', 'Resmî metinden doğrulayın'], ['Ortak bilgisi', 'Bilgi kaydı yok', 'Başvuru rolü ortak gerekliliğini tek başına kanıtlamaz']]) {
    const fact = node('div'); fact.append(node('span', label), node('strong', value), node('small', note)); facts.append(fact);
  } article.append(facts);
  if (paths.length > 1) {
    const label = node('label', 'Başvuru yolu '), select = node('select'); select.id = 'detail-path';
    paths.forEach((p, i) => { const o = node('option', roles[p.role] || 'Rol belirsiz'); o.value = String(i); select.append(o); }); select.value = String(selected);
    select.onchange = () => { const i = Number(select.value); renderDetail(call, i); $('detail-path').focus(); }; label.append(select); article.append(label);
  }
  const why = node('section', undefined, 'detail-section'); why.append(node('h2', 'Neden ilgili olabilir?'), node('p', reason(call)), node('p', call.summary)); article.append(why);
  const conditions = node('section', undefined, 'detail-section'); conditions.append(node('h2', 'Başvuru koşulları'));
  if (!path?.conditions?.length) conditions.append(node('p', 'Bu yol için koşul kaydı bulunmuyor.'));
  for (const c of path?.conditions || []) {
    const row = node('div', undefined, 'condition-row'), state = node('span', undefined, 'condition-icon ' + (c.result === 'saglandi' ? 'condition-yes' : c.result === 'saglanmadi' ? 'condition-no' : 'condition-maybe'));
    state.append(c.result === 'saglandi' ? icon('check') : node('span', c.result === 'saglanmadi' ? '×' : '?')); state.setAttribute('aria-hidden', 'true');
    const body = node('div'); body.append(node('strong', c.text), node('p', 'Kanıt: ' + (c.evidence || 'Kanıt kaydı eksik.'), 'evidence'));
    if (c.evidence_location) body.append(node('p', 'Kanıt konumu: ' + (typeof c.evidence_location === 'string' ? c.evidence_location : JSON.stringify(c.evidence_location))));
    else body.append(node('p', 'Kanıt konumu belirtilmemiş.', 'muted'));
    row.append(state, body, node('span', conditionLabels[c.result] || 'Koşul bilinmiyor', 'condition-state')); conditions.append(row);
  }
  if (path?.ranking?.total != null) conditions.append(node('p', `Öncelik: ${path.ranking.total}/100. Başvuru hakkını veya kazanma olasılığını göstermez.`, 'priority'));
  article.append(conditions);
  const aside = node('aside', undefined, 'decision-sidebar'), box = node('div', undefined, 'decision-box'); box.append(node('h2', countText(call)), node('p', 'Güncel koşulları asıl kaynağından doğrulayın.'));
  const urls = (call.urls || []).map(safeHttps).filter(Boolean);
  if (!call.demo && urls.length) { const official = link(urls[0], 'Resmî sayfada doğrula', 'official-button'); official.target = '_blank'; official.rel = 'noopener noreferrer'; official.append(icon()); box.append(official); }
  else box.append(node('p', call.demo ? 'DEMO kaydı: gerçek bir resmî başvuru bağlantısı yok.' : 'Resmî kaynak bağlantısı bulunmuyor.', 'muted'));
  const actions = node('div', undefined, 'secondary-actions'), ics = node('button', 'Takvime ekle (.ics)', 'secondary'); ics.disabled = daysLeft(call.deadline) === null;
  ics.onclick = () => { const text = calendarICS(call, location.origin + '/ilan/' + encodeURIComponent(call.id)); if (!text) return; const url = URL.createObjectURL(new Blob([text], { type: 'text/calendar;charset=utf-8' })); const a = link(url); a.download = call.id + '.ics'; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000); };
  const shareText = `${call.demo ? 'DEMO · ' : ''}${call.title}\n${deadlineLabel(call.deadline)}\n${location.origin}/ilan/${encodeURIComponent(call.id)}`;
  const share = link('https://wa.me/?text=' + encodeURIComponent(shareText), 'WhatsApp’ta paylaş'); share.target = '_blank'; share.rel = 'noopener noreferrer'; actions.append(ics, share); box.append(actions, node('p', 'Takvim dosyası tüm gün kaydıdır; kapanış saatini belirtmez. Paylaşım WhatsApp’ı açar.', 'muted')); aside.append(box); layout.append(article, aside); target.append(layout, node('p', 'Başvurmadan önce resmî metni okuyun.', 'final-warning'));
}

export function renderCalendar(calls, audience, year, month) {
  const first = new Date(Date.UTC(year, month, 1)); $('calendar-month').textContent = first.toLocaleDateString('tr-TR', { month: 'long', year: 'numeric', timeZone: 'UTC' });
  const prefix = `${year}-${String(month + 1).padStart(2, '0')}`;
  const items = audienceCalls(calls, audience).filter(c => daysLeft(c.deadline) !== null && c.deadline.startsWith(prefix)).sort((a, b) => a.deadline.localeCompare(b.deadline));
  $('calendar-grid').replaceChildren(); $('calendar-agenda').replaceChildren();
  for (const day of ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']) $('calendar-grid').append(node('div', day, 'weekday'));
  for (const date of calendarCells(year, month)) {
    const cell = node('div', undefined, 'calendar-cell' + (date ? '' : ' outside'));
    if (date) {
      const events = items.filter(c => c.deadline === date), day = node('span', String(Number(date.slice(-2))), date === todayISO() ? 'today-day' : undefined); cell.append(day);
      if (events.length) { const jump = link('#agenda-' + date, events.length + ' ilan', 'day-link'); jump.setAttribute('aria-label', fullDate(date) + ' · ' + events.length + ' ilan'); cell.append(jump); }
      for (const c of events) cell.append(link('/ilan/' + encodeURIComponent(c.id), c.title, 'calendar-event ' + roleClass(pathsFor(c, audience)[0]?.role)));
    } $('calendar-grid').append(cell);
  }
  for (const c of items) { const a = link('/ilan/' + encodeURIComponent(c.id), undefined, 'agenda-row'); if (!$('agenda-' + c.deadline)) a.id = 'agenda-' + c.deadline;
    a.append(node('time', fullDate(c.deadline)), node('h3', c.title), badge(pathsFor(c, audience)[0])); $('calendar-agenda').append(a); }
  if (!items.length) $('calendar-agenda').append(node('p', 'Bu ay için açıklanmış bir son tarih yok.', 'calendar-empty'));
}
