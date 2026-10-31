
const esc = (s) => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const grid = document.querySelector('[data-products]');
const empty = document.querySelector('[data-empty]');
const tabs = [...document.querySelectorAll('[data-filter]')];
fetch('./data/products.json').then(r=>r.json()).then(items=>{
  const render = (filter='all') => {
    const shown = filter === 'all' ? items : items.filter(x => x.category === filter);
    grid.innerHTML = shown.map(x => `<article class="card"><span class="pill">${esc(x.status_label)}</span><h3>${esc(x.name)}</h3><p>${esc(x.note)}</p><a href="mailto:hello@example.com?subject=${encodeURIComponent('Запрос: '+x.name)}">${esc(x.cta)}</a></article>`).join('');
    empty.hidden = shown.length !== 0;
  };
  tabs.forEach(t => t.addEventListener('click', () => {tabs.forEach(x=>x.setAttribute('aria-selected','false'));t.setAttribute('aria-selected','true');render(t.dataset.filter)}));
  render();
}).catch(() => { grid.innerHTML=''; empty.hidden=false; empty.textContent='Каталог временно недоступен. Запросите актуальный список у оператора.'; });
