/* Reader: script switch, saraLa/zuddha, meaning toggles, print dialog. No dependencies. */
(() => {
  'use strict';

  const cfg = JSON.parse(document.getElementById('cfg').textContent);
  const scripts = new Map(cfg.scripts.map((s) => [s.id, s]));
  const MODES = ['saraLa', 'zuddha'];
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  // ---- state: URL > localStorage > defaults -------------------------------------------------
  const store = {
    get(k) { try { return localStorage.getItem('kam.' + k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem('kam.' + k, v); } catch { /* private mode */ } },
  };
  const params = new URLSearchParams(location.search);
  const pick = (key, ok, fallback) => [params.get(key), store.get(key)].find((v) => v && ok(v)) || fallback;
  const state = {
    script: pick('script', (v) => scripts.has(v), cfg.default),
    mode: pick('mode', (v) => MODES.includes(v), cfg.defaultMode),
  };

  // ---- fonts --------------------------------------------------------------------------------
  const fontLinks = new Set(['Noto Serif']);
  function ensureFont(family) {
    if (!family || fontLinks.has(family)) return;
    fontLinks.add(family);
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=' + family.replace(/ /g, '+') + ':wght@400;600&display=swap';
    document.head.append(link);
  }
  async function fontsReady(family, sample) {
    if (!document.fonts) return;
    const wait = (ms) => new Promise((r) => setTimeout(r, ms));
    try {
      // the stylesheet has to arrive before the face can be requested
      for (let i = 0; i < 40 && ![...document.fonts].some((f) => f.family.replace(/"/g, '') === family); i++) await wait(100);
      await Promise.race([
        Promise.all([document.fonts.load(`400 16px "${family}"`, sample), document.fonts.load(`600 16px "${family}"`, sample)]),
        wait(8000),
      ]);
      await Promise.race([document.fonts.ready, wait(8000)]);
    } catch { /* print with fallback fonts rather than not at all */ }
  }

  // ---- script data --------------------------------------------------------------------------
  const cache = new Map();
  function load(script, mode) {
    const key = `${script}-${mode}`;
    if (!cache.has(key)) {
      cache.set(key, fetch(`data/${key}.json`).then((r) => {
        if (!r.ok) throw new Error(`${key}: HTTP ${r.status}`);
        return r.json();
      }).catch((err) => { cache.delete(key); throw err; }));
    }
    return cache.get(key);
  }

  function paint(data) {
    const sc = scripts.get(data.script);
    const root = document.documentElement;
    root.dataset.script = sc.id;
    root.style.setProperty('--indic-font', `"${sc.font}"`);
    $('#grantha').lang = sc.lang;
    for (const el of $$('[data-e]')) {
      const lines = data.e[el.dataset.e];
      if (!lines) continue;
      el.lang = sc.lang;
      if ('inline' in el.dataset) { el.textContent = lines.join(' '); continue; }
      el.replaceChildren(...lines.map((t) => {
        const span = document.createElement('span');
        span.className = 'ln';
        span.textContent = t;
        return span;
      }));
    }
    for (const el of $$('[data-ui]')) { el.textContent = data.ui[el.dataset.ui]; el.lang = sc.lang; }
  }

  // Repainting in another script changes every height, so re-anchor once after the first paint.
  let first = true;
  function scrollToHash() {
    const target = location.hash.length > 1 && document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target) requestAnimationFrame(() => target.scrollIntoView({ behavior: 'instant' }));
  }

  let ticket = 0;
  async function apply({ remember = true } = {}) {
    const mine = ++ticket;
    const sc = scripts.get(state.script);
    ensureFont(sc.font);
    $('#script').value = state.script;
    for (const b of $$('[data-mode]')) b.setAttribute('aria-pressed', String(b.dataset.mode === state.mode));
    document.body.classList.add('loading');
    try {
      const data = await load(state.script, state.mode);
      if (mine !== ticket) return null; // a newer choice overtook this one
      paint(data);
      if (first) { first = false; scrollToHash(); }
      if (remember) {
        store.set('script', state.script);
        store.set('mode', state.mode);
        const url = new URL(location.href);
        url.searchParams.set('script', state.script);
        url.searchParams.set('mode', state.mode);
        history.replaceState(null, '', url);
      }
      return data;
    } catch (err) {
      console.error(err);
      return null;
    } finally {
      if (mine === ticket) document.body.classList.remove('loading');
    }
  }

  $('#script').addEventListener('change', (e) => { state.script = e.target.value; apply(); });
  for (const b of $$('[data-mode]')) b.addEventListener('click', () => { state.mode = b.dataset.mode; apply(); });

  // ---- meanings -----------------------------------------------------------------------------
  function setAll(lang, open) {
    for (const d of $$(`details.m-${lang}`)) d.open = open;
    $(`#all-${lang}`).setAttribute('aria-pressed', String(open));
    store.set('all-' + lang, open ? '1' : '');
  }
  for (const lang of ['en', 'te']) {
    const btn = $(`#all-${lang}`);
    btn.addEventListener('click', () => setAll(lang, btn.getAttribute('aria-pressed') !== 'true'));
    if (store.get('all-' + lang)) setAll(lang, true);
  }
  if (cfg.hasTe) { $('#all-te').hidden = false; $('#print-te-row').hidden = false; }

  $('#open-toc').addEventListener('click', () => $('#toc').scrollIntoView());

  // ---- print --------------------------------------------------------------------------------
  const dialog = $('#print-dialog');
  const form = $('#print-form');
  const partsBox = $('#print-parts');
  const PAPER = { A4: 'A4', letter: 'letter' };

  const checkbox = (name, label, checked = true) => {
    const l = document.createElement('label');
    const i = Object.assign(document.createElement('input'), { type: 'checkbox', name, checked });
    l.append(i, ' ' + label);
    return l;
  };
  const prefaceNames = { en: 'Preface (English)', te: 'ముందుమాట (Telugu preface)' };
  for (const lang of cfg.prefaces) $('#print-prefaces').append(checkbox('preface-' + lang, prefaceNames[lang]));
  for (const p of cfg.parts) {
    const l = checkbox('part', p.label + (p.range ? ` (${p.range})` : ''));
    l.firstChild.value = p.id;
    partsBox.append(l);
  }
  $('#print-all').addEventListener('change', (e) => { partsBox.hidden = e.target.checked; });

  $('#open-print').addEventListener('click', () => {
    $('#print-script').value = state.script;
    form.elements.mode.value = state.mode;
    const saved = store.get('paper');
    if (saved && PAPER[saved]) form.elements.paper.value = saved;
    dialog.showModal();
  });
  $('#print-cancel').addEventListener('click', () => dialog.close());

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const f = form.elements;
    const go = $('#print-go');
    go.disabled = true;
    go.textContent = 'Preparing…';

    const before = { ...state, open: $$('details.m').map((d) => d.open) };
    const paper = PAPER[f.paper.value] || 'A4';
    store.set('paper', f.paper.value);
    state.script = f.script.value;
    state.mode = f.mode.value;

    const data = await apply({ remember: false });
    $('#page-size').textContent = `@page { size: ${paper}; }`;
    document.body.classList.toggle('print-no-en', !f.en.checked);
    document.body.classList.toggle('print-no-te', !(f.te && f.te.checked));
    document.body.classList.toggle('print-no-toc', !f.toc.checked);
    for (const d of $$('details.m-en')) d.open = f.en.checked;
    for (const d of $$('details.m-te')) d.open = !!(f.te && f.te.checked);

    const wanted = new Set($('#print-all').checked ? cfg.parts.map((p) => p.id) : $$('input[name=part]:checked', form).map((i) => i.value));
    for (const lang of cfg.prefaces) if (f['preface-' + lang].checked) wanted.add('preface-' + lang);
    for (const el of $$('[data-part]')) {
      if (el.dataset.part === 'toc') continue;
      el.toggleAttribute('data-print-skip', !wanted.has(el.dataset.part));
    }
    for (const li of $$('.toc li[data-toc]')) li.toggleAttribute('data-print-skip', !wanted.has(li.dataset.toc));

    const sc = scripts.get(state.script);
    if (data) await fontsReady(sc.font, Object.values(data.e).slice(0, 40).flat().join(' '));

    dialog.close();
    go.disabled = false;
    go.textContent = 'Print';

    const restore = () => {
      window.removeEventListener('afterprint', restore);
      for (const el of $$('[data-print-skip]')) el.removeAttribute('data-print-skip');
      document.body.classList.remove('print-no-en', 'print-no-te', 'print-no-toc');
      $$('details.m').forEach((d, i) => { d.open = before.open[i]; });
      state.script = before.script;
      state.mode = before.mode;
      apply({ remember: false });
    };
    window.addEventListener('afterprint', restore);
    // let the layout settle with the final fonts before the print snapshot is taken
    requestAnimationFrame(() => requestAnimationFrame(() => window.print()));
  });

  // ---- start --------------------------------------------------------------------------------
  // The page is pre-rendered in the default script; only repaint when the reader wants another.
  if (state.script !== cfg.default || state.mode !== cfg.defaultMode) apply({ remember: false });
  else { ensureFont(scripts.get(state.script).font); $('#script').value = state.script; load(state.script, state.mode).then((d) => { paint(d); first = false; scrollToHash(); }).catch(() => {}); }
  for (const b of $$('[data-mode]')) b.setAttribute('aria-pressed', String(b.dataset.mode === state.mode));

  // For automated PDF checks: ?print=A4|letter applies a paper size and marks the page ready.
  if (params.get('print')) {
    const paper = PAPER[params.get('print')] || 'A4';
    $('#page-size').textContent = `@page { size: ${paper}; }`;
    for (const d of $$('details.m-en')) d.open = params.get('en') !== '0';
  }
})();
