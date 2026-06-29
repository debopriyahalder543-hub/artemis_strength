/* Exercise Library — vanilla JS, zero deps. */
(() => {
  'use strict';
  const $ = s => document.querySelector(s);
  const PAGE = 60;                 // cards rendered per batch
  const LANGS = { en:'English', es:'Español', it:'Italiano', tr:'Türkçe' };

  let ALL = [], view = [], shown = 0, lang = localStorage.lang || 'en';
  const state = { q:'', b:'', q2:'', t:'' };   // search, body_part, equipment, target

  /* ---------- theme ---------- */
  const root = document.documentElement;
  root.dataset.theme = localStorage.theme || 'dark';
  $('#theme').onclick = () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    localStorage.theme = root.dataset.theme;
  };

  /* ---------- boot ---------- */
  fetch('data/index.json').then(r => r.json()).then(data => {
    ALL = data;
    buildFilters(data);
    apply();
    route();                       // open modal if URL has a hash
  }).catch(() => { $('#grid').innerHTML = '<div class="empty">Could not load data.</div>'; });

  /* ---------- auto-hide header on scroll (phones) ---------- */
  (() => {
    const hdr = document.querySelector('header');
    let ticking = false;
    addEventListener('scroll', () => {
      if (ticking) return; ticking = true;
      requestAnimationFrame(() => {
        // hidden whenever scrolled away from the top; only shows at the very top
        hdr.classList.toggle('hide', window.scrollY > 140);
        ticking = false;
      });
    }, { passive: true });
  })();

  /* ---------- filters ---------- */
  function uniq(arr, key){ return [...new Set(arr.map(x => x[key]))].sort(); }

  function buildFilters(data){
    fillSelect('#fbody', uniq(data,'b'), 'All body parts');
    fillSelect('#fequip', uniq(data,'q'), 'All equipment');
    fillSelect('#ftarget', uniq(data,'t'), 'All muscles');
  }
  function fillSelect(sel, items, allLabel){
    const el = $(sel);
    el.innerHTML = `<option value="">${allLabel}</option>` +
      items.map(v => `<option value="${v}">${v}</option>`).join('');
  }

  $('#search').addEventListener('input', e => { state.q = e.target.value.toLowerCase().trim(); apply(); });
  $('#fbody').addEventListener('change', e => { state.b = e.target.value; apply(); });
  $('#fequip').addEventListener('change', e => { state.q2 = e.target.value; apply(); });
  $('#ftarget').addEventListener('change', e => { state.t = e.target.value; apply(); });
  $('#clear').onclick = () => {
    Object.assign(state,{q:'',b:'',q2:'',t:''});
    $('#search').value=''; $('#fbody').value=''; $('#fequip').value=''; $('#ftarget').value='';
    apply();
  };

  /* ---------- filtering ---------- */
  function apply(){
    const {q,b,q2,t} = state;
    view = ALL.filter(x =>
      (!b  || x.b === b) &&
      (!q2 || x.q === q2) &&
      (!t  || x.t === t) &&
      (!q  || x.n.toLowerCase().includes(q) || x.t.includes(q) || x.q.includes(q))
    );
    $('#count').textContent = view.length.toLocaleString() + (view.length===1?' exercise':' exercises');
    $('#clear').style.display = (q||b||q2||t) ? '' : 'none';
    shown = 0;
    $('#grid').innerHTML = '';
    if(!view.length){ $('#grid').innerHTML = '<div class="empty">No exercises match your filters.</div>'; return; }
    more();
  }

  function more(){
    const frag = document.createDocumentFragment();
    const end = Math.min(shown + PAGE, view.length);
    for(let i=shown;i<end;i++){
      const x = view[i];
      const c = document.createElement('a');
      c.className = 'card';
      c.href = 'e/' + (x.s || x.i) + '/';        // real, crawlable URL
      c.onclick = e => {                          // intercept for instant modal
        if(e.metaKey||e.ctrlKey||e.shiftKey||e.button) return; // let new-tab work
        e.preventDefault(); open(x.i);
      };
      c.innerHTML =
        `<img class="thumb" loading="lazy" width="190" height="190" src="images/${x.m}.jpg" alt="${esc(x.n)}">`+
        `<div class="body"><h3>${esc(x.n)}</h3><div class="tags">`+
          `<span class="tag t">${esc(x.t)}</span>`+
          `<span class="tag">${esc(x.q)}</span></div></div>`;
      frag.appendChild(c);
    }
    $('#grid').appendChild(frag);
    shown = end;
  }

  /* infinite scroll */
  new IntersectionObserver(es => {
    if(es[0].isIntersecting && shown < view.length) more();
  }, {rootMargin:'600px'}).observe($('#sentinel'));

  /* ---------- detail modal ---------- */
  const modal = $('#modal'), sheet = $('#sheet');
  function open(id){ location.hash = '/x/' + id; }
  function route(){
    const m = location.hash.match(/\/x\/(\w+)/);
    if(m) load(m[1]); else closeModal(true);
  }
  window.addEventListener('hashchange', route);

  function closeModal(silent){
    modal.classList.remove('open');
    document.body.style.overflow='';
    if(!silent && location.hash) history.replaceState(null,'',location.pathname+location.search);
  }
  $('#close').onclick = () => closeModal();
  modal.addEventListener('click', e => { if(e.target===modal) closeModal(); });
  document.addEventListener('keydown', e => { if(e.key==='Escape') closeModal(); });

  function load(id){
    modal.classList.add('open');
    document.body.style.overflow='hidden';
    sheet.innerHTML = `<div class="sec" style="padding:60px 22px;text-align:center" class="skel">Loading…</div>`;
    fetch('data/ex/'+id+'.json').then(r=>r.json()).then(render)
      .catch(()=>{ sheet.innerHTML='<div class="sec" style="padding:40px;text-align:center">Not found.</div>'; });
  }

  function render(x){
    const sec = m => m && Object.keys(m).length ? m : null;
    sheet.dataset.id = x.id;
    sheet._data = x;
    drawSheet(x);
  }
  function drawSheet(x){
    const steps = (x.instruction_steps && x.instruction_steps[lang]) || x.instruction_steps?.en || [];
    const para  = (x.instructions && x.instructions[lang]) || x.instructions?.en || '';
    const langBtns = Object.keys(LANGS).filter(l => x.instructions?.[l] || x.instruction_steps?.[l])
      .map(l => `<button data-l="${l}" class="${l===lang?'on':''}">${LANGS[l]}</button>`).join('');
    const sec = arr => (arr&&arr.length) ? arr.map(s=>`<span>${esc(s)}</span>`).join('') : '';

    sheet.innerHTML =
      `<div class="top">
         <img class="gif" loading="lazy" src="videos/${x.media}.gif" alt="${esc(x.name)} animation">
         <div class="head">
           <button class="close" id="close2" aria-label="Close">×</button>
           <h2>${esc(x.name)}</h2>
           <div class="kv">
             <span><b>Body</b>${esc(x.body_part)}</span>
             <span><b>Equipment</b>${esc(x.equipment)}</span>
             <span><b>Target</b>${esc(x.target)}</span>
             ${x.muscle_group?`<span><b>Group</b>${esc(x.muscle_group)}</span>`:''}
           </div>
         </div>
       </div>
       <div class="sec">
         ${langBtns?`<div class="shead">Instructions</div><div class="langs">${langBtns}</div>`:''}
         ${steps.length
            ? `<ol class="steps">${steps.map(s=>`<li>${esc(s)}</li>`).join('')}</ol>`
            : (para?`<p>${esc(para)}</p>`:'<p style="color:var(--mut)">No instructions available.</p>')}
         ${x.secondary_muscles&&x.secondary_muscles.length
            ? `<div class="shead">Secondary muscles</div><div class="muscles">${sec(x.secondary_muscles)}</div>` : ''}
       </div>`;

    $('#close2').onclick = () => closeModal();
    sheet.querySelectorAll('.langs button').forEach(b => b.onclick = () => {
      lang = b.dataset.l; localStorage.lang = lang; drawSheet(x);
    });
  }

  function esc(s){ return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
})();
