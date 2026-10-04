/* HK editor. Talks to tools/serve.py; saves one entry at a time into data/grantha.yaml. */
(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const FIELDS = ['title', 'hk', 'en', 'te', 'text'];
  const NON_HK = /[BCFKPQVWXYZfqwx]/g;
  const TE_PREFACE = 'ముందుమాట (Telugu preface)';

  let entries = [];       // rows of the list
  let current = null;     // the loaded entry { id, type, fields, committed, sourceTelugu }
  let pv = { script: 'telugu', mode: 'zuddha' };
  let lastPreview = null;
  let previewHk = null;   // the HK text the rendition on screen was made from
  let sync = null;        // [start, end) in the HK box picked out from the rendition

  const api = async (path, body) => {
    const r = await fetch(path, body === undefined ? {} : {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.error || r.statusText);
    return data;
  };

  // ---- list ---------------------------------------------------------------------------------
  function visible(e) {
    const q = $('#search').value.trim();
    if ($('#f-issues').checked && !e.issues) return false;
    if ($('#f-dirty').checked && !e.uncommitted) return false;
    if (!q) return true;
    return e.no === q || e.id === q || e.label.toLowerCase().includes(q.toLowerCase()) || (/^\d/.test(q) && e.no.startsWith(q));
  }

  function drawList() {
    const list = $('#list');
    list.replaceChildren();
    let group = null;
    const shown = entries.filter(visible);
    const groups = [...new Set(entries.map((e) => e.group))];
    if (!groups.includes(TE_PREFACE)) groups.splice(1, 0, TE_PREFACE);
    for (const g of groups) {
      const rows = shown.filter((e) => e.group === g);
      if (!rows.length && g !== TE_PREFACE) continue;
      const h = document.createElement('h3');
      h.textContent = g;
      list.append(h);
      for (const e of rows) {
        const a = document.createElement('a');
        a.href = '#' + e.id;
        a.dataset.id = e.id;
        if (current && current.id === e.id) a.setAttribute('aria-current', 'true');
        const n = Object.assign(document.createElement('span'), { className: 'n', textContent: e.no || (e.type === 'section' ? '§' : e.type === 'verse' ? '·' : '¶') });
        const t = Object.assign(document.createElement('span'), { className: 't', textContent: e.label || '(empty)' });
        const f = Object.assign(document.createElement('span'), { className: 'f' });
        if (e.issues) f.append(Object.assign(document.createElement('i'), { className: 'dot issue', title: `${e.issues} finding(s)` }));
        if (e.uncommitted) f.append(Object.assign(document.createElement('i'), { className: 'dot dirty', title: 'edited, not committed' }));
        a.append(n, t, f);
        list.append(a);
      }
      if (g === TE_PREFACE) {
        for (const [kind, label] of [['prose', '+ add a paragraph'], ['sloka', '+ add a sloka (HK)']]) {
          const a = Object.assign(document.createElement('a'), { href: '#', textContent: '' });
          a.append(Object.assign(document.createElement('span'), { className: 'n', textContent: '' }),
                   Object.assign(document.createElement('span'), { className: 't', textContent: label }));
          a.addEventListener('click', async (ev) => {
            ev.preventDefault();
            const { id } = await api('/api/preface/te/add', { type: kind });
            await refreshList();
            location.hash = id;
          });
          list.append(a);
        }
      }
    }
    $('#n-issues').textContent = `(${entries.filter((e) => e.issues).length})`;
    $('#n-dirty').textContent = `(${entries.filter((e) => e.uncommitted).length})`;
    markDrafts();
  }

  function drawGit(git) {
    const box = $('#git-status');
    if (!git.repo) { box.textContent = 'Not a git repository yet.'; $('#git-cmd').textContent = ''; return; }
    const n = entries.filter((e) => e.uncommitted).length;
    const dirty = git.dirty.some((l) => l.includes('data/grantha.yaml'));
    box.textContent = dirty
      ? `${n} edited entr${n === 1 ? 'y' : 'ies'} saved in data/grantha.yaml, not yet committed (branch ${git.branch}). This editor never runs git — when you are ready:`
      : `data/grantha.yaml matches the last commit (branch ${git.branch}).`;
    $('#git-cmd').textContent = dirty
      ? 'cd ~/krishnanandamayam\ngit diff data/grantha.yaml\ngit commit -m "Correct HK" data/grantha.yaml\ngit push'
      : '';
  }

  async function refreshList() {
    const data = await api('/api/entries');
    entries = data.entries;
    drawList();
    drawGit(data.git);
  }

  // ---- entry --------------------------------------------------------------------------------
  const values = () => Object.fromEntries(FIELDS.filter((k) => k in current.fields).map((k) => [k, $('#' + k).value.replace(/\r\n/g, '\n').replace(/^\n+|\n+$/g, '')]));
  const isDirty = () => !!current && FIELDS.some((k) => k in current.fields && values()[k] !== current.fields[k]);
  // Unsaved edits to entries you have moved away from. Save (button or Ctrl+S) writes them all.
  const drafts = new Map(); // id -> values
  function pending() {
    const all = new Map(drafts);
    if (current) { if (isDirty()) all.set(current.id, values()); else all.delete(current.id); }
    return all;
  }
  function markDrafts() {
    const all = pending();
    for (const a of $$('#list a[data-id]')) a.classList.toggle('draft', all.has(a.dataset.id));
  }
  const isUncommitted = () => !!current && !!current.committed && FIELDS.some((k) => k in current.fields && (current.committed[k] ?? '') !== current.fields[k]);

  function drawBadge() {
    const b = $('#badge');
    const state = isDirty() ? 'unsaved' : isUncommitted() ? 'uncommitted' : 'saved';
    b.className = 'badge ' + state;
    b.textContent = { unsaved: 'unsaved changes', uncommitted: 'saved · not committed', saved: current && current.committed ? 'matches last commit' : 'saved' }[state];
    const n = pending().size;
    $('#save').disabled = n === 0;
    $('#save').textContent = n > 1 ? `Save all (${n})` : 'Save';
    markDrafts();
    const canRevert = current && current.committed && FIELDS.some((k) => k in current.fields && (current.committed[k] ?? '') !== values()[k]);
    $('#revert').disabled = !canRevert;
  }

  function fill(entry) {
    current = entry;
    sync = null;
    const f = entry.fields;
    for (const k of FIELDS) $('#' + k).value = f[k] ?? '';
    $('#hk-wrap').hidden = !('hk' in f);
    $('#title-wrap').hidden = !('title' in f);
    $('#text-wrap').hidden = !('text' in f);
    $('#en-wrap').hidden = !('en' in f);
    $('#te-wrap').hidden = !('te' in f);
    $('.ref').hidden = !('hk' in f);
    const kind = { verse: 'Verse', section: 'Section title', sloka: 'Preface sloka', prose: 'Preface paragraph' }[entry.type];
    $('#heading').textContent = `${kind} ${entry.no || ''}`.trim() + `  ·  ${entry.id}`;
    document.title = `${entry.no || entry.id} · HK editor`;
    for (const a of $$('#list a[data-id]')) a.toggleAttribute('aria-current', false);
    const here = $(`#list a[data-id="${CSS.escape(entry.id)}"]`);
    if (here) { here.setAttribute('aria-current', 'true'); here.scrollIntoView({ block: 'nearest' }); }
    drawMarks();
    drawBadge();
    lastPreview = null;
    if ('hk' in f) preview(); else { $('#preview').replaceChildren(); drawSource(); }
    previewAllProse();
  }

  async function open(id) {
    if (current && current.id === id) return;
    // keep unsaved edits as a draft instead of asking: they are saved together later
    if (current) { if (isDirty()) drafts.set(current.id, values()); else drafts.delete(current.id); }
    try {
      fill(await api('/api/entry/' + encodeURIComponent(id)));
      const d = drafts.get(id);
      if (d) {
        for (const k of FIELDS) if (k in current.fields && k in d) $('#' + k).value = d[k];
        drafts.delete(id);
        drawMarks();
        drawBadge();
        schedulePreview();
        previewAllProse();
      }
    } catch (err) { alert(err.message); }
  }

  async function save() {
    const all = pending();
    if (!all.size) return;
    $('#save').disabled = true;
    $('#save').textContent = 'Saving…';
    try {
      await api('/api/save-all', { entries: Object.fromEntries(all) });
      if (all.has(current.id)) current.fields = { ...current.fields, ...all.get(current.id) };
      drafts.clear();
      await refreshList();
      const here = $(`#list a[data-id="${CSS.escape(current.id)}"]`);
      if (here) here.setAttribute('aria-current', 'true');
    } catch (err) { alert('Not saved: ' + err.message); }
    drawMarks();
    drawBadge();
  }

  // ---- HK box: underline letters that are not Harvard-Kyoto ----------------------------------
  function drawMarks() {
    const box = $('#hk-marks');
    box.replaceChildren();
    const text = $('#hk').value;
    const piece = (from, to) => {
      const part = text.slice(from, to);
      const out = [];
      let pos = 0;
      for (const m of part.matchAll(NON_HK)) {
        out.push(part.slice(pos, m.index), Object.assign(document.createElement('mark'), { textContent: m[0] }));
        pos = m.index + 1;
      }
      out.push(part.slice(pos));
      return out;
    };
    if (sync) {
      const picked = Object.assign(document.createElement('span'), { className: 'sync' });
      picked.append(...piece(sync[0], sync[1]));
      box.append(...piece(0, sync[0]), picked, ...piece(sync[1], text.length), '\n');
    } else box.append(...piece(0, text.length), '\n');
    box.scrollTop = $('#hk').scrollTop;
  }
  $('#hk').addEventListener('scroll', () => { $('#hk-marks').scrollTop = $('#hk').scrollTop; });

  // ---- live rendition -----------------------------------------------------------------------
  let timer = 0;
  let seq = 0;
  function schedulePreview() {
    $('#preview').classList.add('stale');
    clearTimeout(timer);
    timer = setTimeout(preview, 220);
  }
  async function preview() {
    const mine = ++seq;
    try {
      const hk = $('#hk').value;
      const data = await api('/api/preview', { hk, title: $('#title').value, script: pv.script, mode: pv.mode });
      if (mine !== seq) return;
      data.hk = hk;
      lastPreview = data;
      const box = $('#preview');
      box.classList.remove('stale');
      previewHk = data.hk;
      box.replaceChildren(...data.spans.map((words) => {
        const line = document.createElement('span');
        words.forEach(([t, a, b], i) => {
          const w = Object.assign(document.createElement('span'), { className: 'w', textContent: t });
          w.dataset.a = a;
          w.dataset.b = b;
          line.append(i ? ' ' : '', w);
        });
        return line;
      }));
      const font = scriptFonts.get(pv.script);
      if (font) box.style.fontFamily = `"${font}", "Noto Serif", serif`;
      const tp = $('#title-preview');
      tp.replaceChildren(data.titleLine, ...data.titleIssues.map((i) => Object.assign(document.createElement('span'), { className: 'warn', textContent: '⚠ ' + i })));
      if (font) tp.style.fontFamily = `"${font}", "Noto Serif", serif`;
      const notZuddha = data.zuddha !== $('#hk').value || data.titleZuddha !== $('#title').value;
      $('#zuddha-hint').hidden = !notZuddha;
      $('#issues').replaceChildren(...data.issues.filter((i) => !i.startsWith('not in zuddha')).map((i) => Object.assign(document.createElement('li'), { textContent: i })));
      drawSource();
      syncSelection();
    } catch (err) { console.error(err); }
  }

  // ---- selection sync: the rendition and the HK box point at each other ----------------------
  // Select (or click) words in the rendition and the HK they were made from is picked out in
  // the box; put the caret or a selection in the box and its words are picked out below.
  function setSync(range) {
    if (String(range) === String(sync)) return;
    sync = range;
    drawMarks();
    const picked = $('#hk-marks .sync');
    const ta = $('#hk');
    if (picked && (picked.offsetTop < ta.scrollTop || picked.offsetTop + picked.offsetHeight > ta.scrollTop + ta.clientHeight)) {
      ta.scrollTop = Math.max(0, picked.offsetTop - ta.clientHeight / 3);
      $('#hk-marks').scrollTop = ta.scrollTop;
    }
  }
  function hasSelected(range, w) {
    const t = w.firstChild;
    const head = range.comparePoint(t, 0), tail = range.comparePoint(t, t.length);
    if (head === tail && head !== 0) return false;   // the whole word is before or after it
    const r = range.cloneRange();
    if (head === 0) r.setStart(t, 0);
    if (tail === 0) r.setEnd(t, t.length);
    return r.toString() !== '';
  }
  function syncSelection() {
    const ta = $('#hk');
    const words = $$('#preview .w');
    const fresh = previewHk === ta.value;
    if (document.activeElement === ta) {
      setSync(null);
      const s = ta.selectionStart, e = ta.selectionEnd;
      for (const w of words) {
        const a = +w.dataset.a, b = +w.dataset.b;
        w.classList.toggle('on', fresh && (s === e ? a <= s && s <= b : a < e && s < b));
      }
      return;
    }
    for (const w of words) w.classList.remove('on');
    const sel = getSelection();
    const range = sel.rangeCount ? sel.getRangeAt(0) : null;
    let picked = [];
    if (fresh && range && $('#preview').contains(range.commonAncestorContainer)) {
      if (range.collapsed) {
        const at = range.startContainer;
        const w = (at.nodeType === 1 ? at : at.parentElement).closest('.w');
        if (w) picked = [w];
      } else picked = words.filter((w) => hasSelected(range, w));
    }
    setSync(picked.length ? [Math.min(...picked.map((w) => +w.dataset.a)), Math.max(...picked.map((w) => +w.dataset.b))] : null);
  }
  document.addEventListener('selectionchange', syncSelection);
  for (const ev of ['select', 'keyup', 'click', 'focus', 'blur']) $('#hk').addEventListener(ev, syncSelection);

  // ---- reference: the sheet's Telugu, with words that differ from the HK rendition marked ----
  const norm = (w) => w.replace(/[।॥|.,;:!?"'“”‘’()\[\]\-‌‍]/g, '');
  function lcsKeep(a, b) {
    const n = a.length, m = b.length;
    const t = Array.from({ length: n + 1 }, () => new Uint16Array(m + 1));
    for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) t[i][j] = a[i] === b[j] ? t[i + 1][j + 1] + 1 : Math.max(t[i + 1][j], t[i][j + 1]);
    const keep = new Set();
    for (let i = 0, j = 0; i < n && j < m;) {
      if (a[i] === b[j]) { keep.add(i); i++; j++; } else if (t[i + 1][j] >= t[i][j + 1]) i++; else j++;
    }
    return keep;
  }
  function drawSource() {
    const box = $('#source');
    box.replaceChildren();
    const src = current ? current.sourceTelugu : '';
    if (!src) {
      $('#source-note').textContent = current && 'hk' in current.fields ? 'The sheet has no Telugu for this entry.' : '';
      return;
    }
    const tokens = src.split(/(\s+)/);
    const words = tokens.map((t, i) => ({ t, i })).filter((x) => x.t.trim() && norm(x.t));
    const mine = lastPreview ? lastPreview.saraLaTelugu.join(' ').split(/\s+/).map(norm).filter(Boolean) : [];
    const theirs = words.map((w) => norm(w.t));
    const keep = lcsKeep(theirs, mine);
    const differs = new Set(words.filter((_, k) => !keep.has(k)).map((w) => w.i));
    tokens.forEach((t, i) => box.append(differs.has(i) && mine.length ? Object.assign(document.createElement('mark'), { textContent: t }) : t));
    const keptMine = lcsKeep(mine, theirs);
    const onlyMine = mine.filter((_, k) => !keptMine.has(k));
    $('#source-note').textContent = mine.length
      ? `${differs.size} of ${words.length} sheet words (marked) are not in the సరళ తెలుగు rendition of your HK`
        + (onlyMine.length ? `; ${onlyMine.length} word${onlyMine.length === 1 ? "" : "s"} of your rendition not in the sheet: ${onlyMine.slice(0, 12).join(' · ')}${onlyMine.length > 12 ? ' …' : ''}` : '')
        + '. A difference is a place to look — either side may be the one that is wrong.'
      : '';
  }

  // ---- wiring -------------------------------------------------------------------------------
  const scriptFonts = new Map();
  const loadedFonts = new Set(['Noto Serif Telugu', 'Noto Serif']);
  async function initScripts() {
    const { scripts } = await api('/api/scripts');
    const sel = $('#pv-script');
    for (const s of scripts) {
      scriptFonts.set(s.id, s.font);
      sel.append(Object.assign(document.createElement('option'), { value: s.id, textContent: s.label }));
    }
    sel.value = pv.script;
    sel.addEventListener('change', () => {
      pv.script = sel.value;
      const font = scriptFonts.get(pv.script);
      if (font && !loadedFonts.has(font)) {
        loadedFonts.add(font);
        document.head.append(Object.assign(document.createElement('link'), { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=' + font.replace(/ /g, '+') + ':wght@400;600&display=swap' }));
      }
      preview();
      previewAllProse();
    });
  }
  for (const b of $$('[data-pv-mode]')) b.addEventListener('click', () => {
    pv.mode = b.dataset.pvMode;
    for (const o of $$('[data-pv-mode]')) o.setAttribute('aria-pressed', String(o === b));
    preview();
    previewAllProse();
  });

  $('#hk').addEventListener('input', () => { sync = null; drawMarks(); drawBadge(); schedulePreview(); });
  $('#title').addEventListener('input', () => { drawBadge(); schedulePreview(); });
  // prose fields: show the paragraph with its inline $hk$ runs rendered
  const proseTimers = {};
  async function previewProse(k) {
    const box = $('#pp-' + k);
    const text = $('#' + k).value;
    if (!text.includes('$')) { box.hidden = true; return; }
    try {
      const data = await api('/api/preview-prose', { text, script: pv.script, mode: pv.mode });
      if ($('#' + k).value !== text) return;
      box.hidden = false;
      const font = scriptFonts.get(pv.script);
      box.replaceChildren(...data.paragraphs.map((segs) => {
        const p = document.createElement('p');
        for (const [kind, body] of segs) {
          if (kind === 'text') { p.append(body); continue; }
          const span = Object.assign(document.createElement('span'), { className: 'il', textContent: body });
          if (font) span.style.fontFamily = `"${font}", serif`;
          p.append(span);
        }
        return p;
      }), ...data.issues.map((i) => Object.assign(document.createElement('p'), { className: 'warn', textContent: '⚠ ' + i })));
    } catch (err) { console.error(err); }
  }
  const previewAllProse = () => { for (const k of ['en', 'te', 'text']) previewProse(k); };
  for (const k of ['en', 'te', 'text']) $('#' + k).addEventListener('input', () => {
    drawBadge();
    clearTimeout(proseTimers[k]);
    proseTimers[k] = setTimeout(() => previewProse(k), 250);
  });
  $('#save').addEventListener('click', save);
  $('#normalize').addEventListener('click', () => {
    if (!lastPreview) return;
    $('#hk').value = lastPreview.zuddha;
    $('#title').value = lastPreview.titleZuddha;
    $('#hk').dispatchEvent(new Event('input'));
  });
  $('#revert').addEventListener('click', () => {
    if (!current.committed) return;
    for (const k of FIELDS) if (k in current.fields) $('#' + k).value = current.committed[k] ?? '';
    $('#hk').dispatchEvent(new Event('input'));
    drawBadge();
  });

  function step(delta) {
    const shown = entries.filter(visible);
    const i = shown.findIndex((e) => current && e.id === current.id);
    const next = shown[i + delta] || (i === -1 ? shown[0] : null);
    if (next) location.hash = next.id;
  }
  $('#prev').addEventListener('click', () => step(-1));
  $('#next').addEventListener('click', () => step(1));
  window.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 's') { e.preventDefault(); save(); }
    if (e.altKey && e.key === 'ArrowDown') { e.preventDefault(); step(1); }
    if (e.altKey && e.key === 'ArrowUp') { e.preventDefault(); step(-1); }
  });
  for (const id of ['search', 'f-issues', 'f-dirty']) $('#' + id).addEventListener('input', drawList);
  window.addEventListener('hashchange', () => open(decodeURIComponent(location.hash.slice(1))));
  window.addEventListener('beforeunload', (e) => { if (pending().size) { e.preventDefault(); e.returnValue = ''; } });

  (async () => {
    await Promise.all([initScripts(), refreshList()]);
    const first = decodeURIComponent(location.hash.slice(1)) || (entries.find((e) => e.type === 'verse') || entries[0]).id;
    if (location.hash.slice(1) === first) open(first); else location.hash = first;
  })();
})();
