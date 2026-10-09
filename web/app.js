import { themes, roles, conditionLabels, safeHttps, deadlineLabel, sourceSummary } from '/radar.mjs';

import { renderListing, renderDetail, renderCalendar } from '/views.mjs';
import { todayISO } from '/decision.mjs';

const $ = s => document.querySelector(s);
let audience = 'school', calendarAudience = 'school', currentView = 'radar';
const today = todayISO();
if(new URLSearchParams(location.search).get('audience')==='me') audience='me'; let calendarYear = Number(today.slice(0,4)), calendarMonth = Number(today.slice(5,7))-1;
const managementRoute = location.pathname === '/yonetim';
let publicSources = null;
let token = '', auth = null, fb = null, calls = [], me = null, config = null, listState = 'loading';

function el(tag, text, className) {
  const n = document.createElement(tag);
  if (text !== undefined) n.textContent = text;
  if (className) n.className = className;
  return n;
}

function message(text, tone = 'info', target = '#notice') {
  const n = $(target);
  n.textContent = text;
  n.dataset.tone = tone;
}

function friendlyError(error) {
  if (error.name === 'AbortError') return 'İşlem zamanında tamamlanamadı. Yeniden deneyin.';
  if (error instanceof TypeError) return 'Sunucuya ulaşılamadı. Bağlantınızı kontrol edip yeniden deneyin.';
  if (error.message === 'İçerik değişti; yeniden inceleyin') return 'Bu kayıt değişmiş. Güncel sürümü yeniden inceleyin.';
  if (error.status === 403) return 'Bu işlem için uygun yetkiyle giriş yapmanız gerekiyor.';
  if (error.status === 400) return 'İşlem tamamlanamadı. Girdiğiniz bilgileri kontrol edin.';
  if (error.status >= 500) return 'Sunucu işlemi tamamlayamadı. Yeniden deneyin.';
  if (error.code === 'auth/popup-closed-by-user') return 'Giriş penceresi kapatıldı. Yeniden deneyebilirsiniz.';
  return 'İşlem tamamlanamadı. Yeniden deneyin.';
}

async function api(path, data) {
  if (auth?.currentUser) token = await auth.currentUser.getIdToken();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch('/api/' + path, {
      method: data === undefined ? 'GET' : 'POST', signal: controller.signal,
      headers: { ...(token ? { Authorization: 'Bearer ' + token } : {}), ...(data === undefined ? {} : { 'Content-Type': 'application/json' }) },
      body: data === undefined ? undefined : JSON.stringify(data)
    });
    const result = await response.json();
    if (!response.ok) {
      const error = new Error(result.error || 'İşlem tamamlanamadı');
      error.status = response.status;
      throw error;
    }
    return result;
  } finally { clearTimeout(timer); }
}

async function action(button, task, target = '#notice') {
  if (button.disabled) return;
  button.disabled = true;
  try { await task(); } catch (error) { message(friendlyError(error), 'error', target); }
  finally { button.disabled = false; }
}

function showView(view, focus = true) {
  currentView = view;
  for (const id of ['radar', 'detail', 'calendar', 'how', 'preferences', 'admin']) $('#'+id).hidden = id !== view;
  $('.skip-link').href = '#' + view + '-title';
  for (const a of document.querySelectorAll('[data-route]')) {
    const active = a.dataset.route === view || view === 'detail' && a.dataset.route === 'radar';
    a.classList.toggle('active', active); if (active) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current');
  }
  const heading=$('#'+view+'-title');
  if(heading) document.title=heading.textContent+' | Hibe Radarı';
  if (focus) heading?.focus();
}

async function route(focus = true) {
  const path = location.pathname;
  if (path.startsWith('/ilan/')) {
    const c = calls.find(c => '/ilan/'+encodeURIComponent(c.id) === path);
    const want = new URLSearchParams(location.search).get('audience') || audience;
    const index = c ? Math.max(0, (c.paths || []).findIndex(p => want === 'me' ? p.role === 'ogretmen_birey' : p.role !== 'ogretmen_birey')) : 0;
    renderDetail(c,index); showView('detail',focus);
  } else if (path === '/takvim') {
    renderCalendar(calls,calendarAudience,calendarYear,calendarMonth);showView('calendar',focus);
  } else if (path === '/nasil-calisir') {
    showView('how',focus);
    try {
      publicSources ||= await api('sources');
      const stats=sourceSummary(publicSources);
      $('#public-source-summary').textContent=`${stats.total} kayıt yeri · ${stats.unverified} doğrulanmamış aday · ${stats.missing} eksik kimlik.`;
      $('#public-sources').replaceChildren();
      for (const s of publicSources) {
        const n=el('div',undefined,'source-row'), body=el('div'); body.append(el('strong',s.name),el('span','Son kontrol: '+(s.last_checked || 'Bilinmiyor')));n.append(body,el('span',s.identity_status==='missing'?'Kimlik bekleniyor':s.status==='ready'?'Kontrol yolu tanımlı':'Doğrulama bekleniyor'));$('#public-sources').append(n);
      }
    } catch { $('#public-source-summary').textContent='Kaynak listesi yüklenemedi. Sayfayı yeniden yükleyin.'; }
  } else if (path === '/aboneligim') showView('preferences',focus);
  else if (path === '/yonetim') {
    showView('admin',focus);
    if (me?.admin) await admin(); else message('Yönetici oturumu gerekli. Demo modunda yukarıdaki giriş alanını kullanın.','info','#admin-status');
  } else { draw(); showView('radar',focus); }
}

function syncSessionUI() {
  $('#admin-content').hidden = !me?.admin;
  $('#identity').textContent = me ? (config.demo ? (me.admin ? 'Yönetici demosu' : 'Kullanıcı demosu') : me.email) : '';
  $('#login').hidden = !!me;
  $('#logout').hidden = !me;
  $('#prefs').hidden = !me;
  $('#preferences-login').hidden = !!me;
  $('#subscribe').checked = me?.preferences?.subscribed === true;
  for (const i of document.querySelectorAll('[name="theme"]')) i.checked = me?.preferences?.themes?.includes(i.value) || false;
  if (!me) {
    $('#review').replaceChildren(); $('#sources').replaceChildren(); $('#metrics').replaceChildren();
    $('#import').value = ''; message('', 'info', '#prefs-status'); message('', 'info', '#admin-status'); message('', 'info', '#import-status');
    if (currentView === 'admin') message('Yönetici oturumu gerekli.','info','#admin-status');
  }
}

async function session() {
  try { me = token ? await api('me') : null; }
  catch (error) { token = ''; me = null; syncSessionUI(); throw error; }
  syncSessionUI();
}

function conditions(p, target) {
  if (!p.conditions?.length) target.append(el('p', 'Bu yol için koşul kaydı bulunmuyor.', 'muted'));
  for (const x of p.conditions || []) {
    const n = el('div', undefined, 'condition');
    n.append(el('strong', x.text), el('p', conditionLabels[x.result] || 'Koşul bilinmiyor'), el('p', 'Kanıt: ' + (x.evidence || 'Bu koşul için kanıt kaydı eksik.'), 'evidence'));
    target.append(n);
  }
}

function sourceLink(url, text) {
  const href = safeHttps(url);
  if (!href) return null;
  const a = el('a', text);
  a.href = href; a.target = '_blank'; a.rel = 'noopener noreferrer';
  return a;
}

function draw() {
  if (listState !== 'ready') return;
  renderListing(calls, {query:$('#search').value,role:$('#role').value,theme:$('#theme').value,sort:$('#sort').value},audience);
}

async function loadCalls() {
  listState = 'loading'; $('#cards').setAttribute('aria-busy', 'true'); $('#cards').replaceChildren();
  $('#result-count').textContent = 'Fırsatlar yükleniyor…'; $('#list-error').hidden = true;
  try { calls = await api('calls'); listState = 'ready'; draw(); }
  catch { listState = 'error'; $('#result-count').textContent = 'Liste yüklenemedi'; $('#list-error').hidden = false; }
  finally { $('#cards').setAttribute('aria-busy', 'false'); }
}

async function admin() {
  message('Panel yükleniyor…', 'info', '#admin-status'); $('#retry-admin').hidden = true;
  $('#review').setAttribute('aria-busy', 'true');
  try {
    const data = await api('admin');
    $('#metrics').replaceChildren();
    for (const [key, label] of Object.entries({ registered: 'Kayıtlı kullanıcı', subscribed: 'Bülten tercihi açık kullanıcı', published: 'Yayımlanan ilan', calls: 'Toplam çağrı kaydı' })) {
      const n = el('div', undefined, 'metric'); n.dataset.metric = key; n.append(el('dt', label), el('dd', String(data.metrics[key]))); $('#metrics').append(n);
    }
    const stats = sourceSummary(data.sources);
    $('#source-summary').textContent = '30 kaynak hedefi · ' + stats.total + ' kayıt yeri · ' + stats.unverified + ' doğrulanmamış isim · ' + stats.missing + ' eksik kimlik. Kayıt durumu, taramanın çalıştığını göstermez.';
    $('#sources').replaceChildren();
    for (const s of data.sources) {
      const n = el('div', undefined, 'source-row');
      const missing = s.identity_status === 'missing' || /özgün liste bekleniyor/i.test(s.name || '');
      n.append(el('strong', s.name), el('span', s.status === 'registry_pending' ? (missing ? 'Özgün kaynak kimliği bekleniyor' : 'Kimlik ve URL doğrulaması bekleniyor') : (s.status === 'ready' ? 'Kayıt taramaya hazır' : 'Durum: ' + s.status)));
      n.append(el('small', 'Son kontrol: ' + (s.last_checked || 'Bilinmiyor'))); $('#sources').append(n);
    }
    $('#review').replaceChildren();
    if (!data.calls.length) $('#review').append(el('p', 'İncelenecek kayıt yok.'));
    for (const c of data.calls) {
      const n = el('details');
      const approved = c.approval?.reviewed && c.approval.version === c.version;
      n.append(el('summary', c.title + (approved ? ' · Bu sürüm onaylı' : ' · İnceleme bekliyor')));
      if (c.demo) n.append(el('p', 'DEMO · Kurgusal kayıt', 'tag'));
      n.append(el('p', c.summary), el('p', deadlineLabel(c.deadline)));
      for (const p of c.paths || []) { n.append(el('h3', roles[p.role] || 'Rol belirsiz')); conditions(p, n); }
      for (const [index, doc] of (c.documents || []).entries()) { const a = c.demo ? null : sourceLink(doc.url, 'Kaynak / belge ' + (index + 1)); if (a) n.append(a); }
      n.append(el('p', 'İncelenen sürüm: ' + c.version, 'version'));
      const b = el('button', approved ? 'Bu sürüm onaylı' : 'İnceledim — bu sürümü onayla'); b.disabled = !!approved;
      const status = el('p', undefined, 'message'); status.setAttribute('role', 'status');
      b.onclick = async () => {
        if (b.disabled) return;
        b.disabled = true;
        try {
          await api('approve', { id: c.id, version: c.version });
          message('İncelediğiniz sürüm onaylandı.', 'success', '#admin-status');
          b.textContent = 'Bu sürüm onaylı'; n.querySelector('summary').textContent = c.title + ' · Bu sürüm onaylı';
          await loadCalls();
          if (listState === 'ready') $('[data-metric="published"] dd').textContent = String(calls.length);
        } catch (error) { status.textContent = friendlyError(error); status.dataset.tone = 'error'; $('#retry-admin').hidden = false; b.disabled = false; }
      };
      n.append(b, status); $('#review').append(n);
    }
    message('', 'info', '#admin-status');
  } catch (error) {
    message(friendlyError(error), 'error', '#admin-status'); $('#retry-admin').hidden = false;
    $('#review').replaceChildren(); $('#sources').replaceChildren(); $('#metrics').replaceChildren();
  } finally { $('#review').setAttribute('aria-busy', 'false'); }
}


function closeRoles() { $('#demo-roles').hidden = true; $('#login').setAttribute('aria-expanded', 'false'); }
$('#close-roles').onclick = () => { closeRoles(); $('#login').focus(); };
$('#demo-roles').onkeydown = e => { if (e.key === 'Escape') { closeRoles(); $('#login').focus(); } };
$('#login').onclick = () => action($('#login'), async () => {
  if (config.demo) {
    $('#demo-roles').hidden = !$('#demo-roles').hidden; $('#login').setAttribute('aria-expanded', String(!$('#demo-roles').hidden));
    if (!$('#demo-roles').hidden) $('[data-demo-role="user"]').focus();
  } else { await fb.signInWithPopup(auth, new fb.GoogleAuthProvider()); }
});
for (const b of document.querySelectorAll('[data-demo-role]')) b.onclick = () => action(b, async () => {
  const choices = [...document.querySelectorAll('[data-demo-role]')];
  choices.forEach(choice => { choice.disabled = true; });
  try {
    token = (await api('demo-login', { role: b.dataset.demoRole })).token;
    await session(); closeRoles(); message('Yerel demo oturumu açıldı.', 'success'); await route();
  } finally { choices.forEach(choice => { choice.disabled = false; }); }
});
$('#logout').onclick = () => action($('#logout'), async () => {
  if (auth) await fb.signOut(auth);
  token = ''; me = null; syncSessionUI(); closeRoles(); await route(); message('Oturum kapatıldı.');
});
$('#prefs').onsubmit = e => {
  e.preventDefault();
  action($('#save-prefs'), async () => {
    message('Tercihler kaydediliyor…', 'info', '#prefs-status');
    await api('preferences', { subscribed: $('#subscribe').checked, themes: [...document.querySelectorAll('[name="theme"]:checked')].map(n => n.value) });
    await session(); message('Tercihleriniz kaydedildi. E-posta gönderimi bağlı değil.', 'success', '#prefs-status');
  }, '#prefs-status');
};
$('#import-button').onclick = () => action($('#import-button'), async () => {
  let draft;
  try { draft = JSON.parse($('#import').value); } catch { message('Taslak kaydedilemedi. JSON biçimini kontrol edin.', 'error', '#import-status'); return; }
  if (!draft || typeof draft !== 'object' || Array.isArray(draft)) { message('JSON tek bir çağrı nesnesi içermeli.', 'error', '#import-status'); return; }
  await api('call', draft); message('Taslak kaydedildi; onay bekliyor.', 'success', '#import-status'); await admin();
}, '#import-status');
$('#search').oninput = draw;
for (const id of ['role', 'theme', 'sort']) $('#' + id).onchange = draw;
$('#clear-filters').onclick = () => { $('#search').value = ''; $('#role').value = ''; $('#theme').value = ''; $('#sort').value = 'deadline'; draw(); $('#search').focus(); };
$('#retry-calls').onclick = () => action($('#retry-calls'), loadCalls);
$('#retry-admin').onclick = () => action($('#retry-admin'), admin, '#admin-status');

for (const [key, label] of Object.entries(themes)) {
  const n = el('label', undefined, 'check'), i = el('input'); i.type = 'checkbox'; i.name = 'theme'; i.value = key;
  n.append(i, document.createTextNode(' ' + label)); $('#themes').append(n);
  const option = el('option', label); option.value = key; $('#theme').append(option);
}

const unsub = new URLSearchParams(location.search).get('unsubscribe');
if (unsub) {
  $('#unsubscribe-panel').hidden = false;
  $('#unsubscribe-button').onclick = () => action($('#unsubscribe-button'), async () => {
    await api('unsubscribe', { token: unsub }); message('Bülten aboneliğiniz kapatıldı.', 'success', '#unsubscribe-status');
    $('#unsubscribe-button').hidden = true; history.replaceState(null, '', '/');
  }, '#unsubscribe-status');
}

try {
  config = await api('config');
  $('#mode').textContent = config.demo ? 'YEREL DEMO' : 'Google / Firebase';
  if (config.demo) {
    $('#environment').hidden = false;
    $('#environment').textContent = 'Yerel demo · Örnek ilanlar kurgusaldır. Gerçek Firebase bağlantısı ve e-posta gönderimi yok.';
    $('#login').textContent = 'Demoyu dene'; $('#login').setAttribute('aria-controls', 'demo-roles'); $('#login').setAttribute('aria-expanded', 'false');
  } else {
    const sdk = await import('https://www.gstatic.com/firebasejs/11.10.0/firebase-app.js');
    fb = await import('https://www.gstatic.com/firebasejs/11.10.0/firebase-auth.js');
    auth = fb.getAuth(sdk.initializeApp(config.firebase));
    fb.onAuthStateChanged(auth, async user => { try { token = user ? await user.getIdToken() : ''; await session(); } catch (error) { message(friendlyError(error), 'error'); } });
    $('#login').textContent = 'Google ile giriş';
  }
  $('#login').disabled = false; syncSessionUI(); await loadCalls(); $('#server-content').hidden = listState === 'ready'; $('#app-shell').hidden = listState !== 'ready'; if(listState==='ready') await route(false); else message('Etkileşimli liste yüklenemedi. Aşağıdaki ilanları okuyabilir veya sayfayı yeniden yükleyebilirsiniz.','error');
} catch (error) {
  $('#mode').textContent = 'Uygulama bilgisi yüklenemedi'; $('#result-count').textContent = 'Liste yüklenemedi';
  message('Uygulama başlatılamadı. Sayfayı yeniden yükleyin.', 'error'); $('#cards').setAttribute('aria-busy', 'false');
}

function updateRoles() {
  const role=$('#role'),all=el('option','Tüm yollar');all.value='';role.replaceChildren(all);
  for(const [key,label] of Object.entries(roles)) if(audience==='me'?key==='ogretmen_birey':key!=='ogretmen_birey') {const o=el('option',label);o.value=key;role.append(o);}
}
for(const b of document.querySelectorAll('[data-audience]')) b.onclick=()=>{audience=b.dataset.audience;for(const other of document.querySelectorAll('[data-audience]')){other.classList.toggle('selected',other===b);other.setAttribute('aria-pressed',String(other===b));}updateRoles();draw();};
for(const b of document.querySelectorAll('[data-calendar-audience]')) b.onclick=()=>{calendarAudience=b.dataset.calendarAudience;for(const other of document.querySelectorAll('[data-calendar-audience]')){other.classList.toggle('selected',other===b);other.setAttribute('aria-pressed',String(other===b));}renderCalendar(calls,calendarAudience,calendarYear,calendarMonth);};
function moveMonth(delta) {const date=new Date(Date.UTC(calendarYear,calendarMonth+delta,1));calendarYear=date.getUTCFullYear();calendarMonth=date.getUTCMonth();renderCalendar(calls,calendarAudience,calendarYear,calendarMonth);}
$('#calendar-prev').onclick=()=>moveMonth(-1);$('#calendar-next').onclick=()=>moveMonth(1);$('#calendar-today').onclick=()=>{const d=todayISO();calendarYear=Number(d.slice(0,4));calendarMonth=Number(d.slice(5,7))-1;moveMonth(0);};
document.addEventListener('click',e=>{const a=e.target.closest('a');if($('#app-shell').hidden||!a||e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||a.target||a.hasAttribute('download'))return;const u=new URL(a.href,location.href);if(u.origin!==location.origin||u.hash)return;if(!['/','/takvim','/nasil-calisir','/aboneligim','/yonetim'].includes(u.pathname)&&!u.pathname.startsWith('/ilan/'))return;e.preventDefault();history.pushState(null,'',u.pathname+u.search);route();window.scrollTo(0,0);});
window.addEventListener('popstate',()=>route());
function setTheme(dark){document.documentElement.classList.toggle('dark',dark);$('#theme-toggle').textContent=dark?'Açık':'Karanlık';$('#theme-toggle').setAttribute('aria-label',dark?'Açık görünüm':'Karanlık görünüm');}
let dark=matchMedia('(prefers-color-scheme: dark)').matches;try{const saved=localStorage.getItem('hibe-theme');if(saved)dark=saved==='dark';}catch{}
setTheme(dark);$('#theme-toggle').onclick=()=>{dark=!dark;setTheme(dark);try{localStorage.setItem('hibe-theme',dark?'dark':'light');}catch{}};
$('#admin-demo').hidden=!managementRoute;updateRoles();
for(const b of document.querySelectorAll('[data-audience]')){b.classList.toggle('selected',b.dataset.audience===audience);b.setAttribute('aria-pressed',String(b.dataset.audience===audience));}
