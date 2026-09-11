(() => {
  'use strict';
  const charters = [...document.querySelectorAll('.team-charter')];
  const search = document.getElementById('charter-search');
  const count = document.getElementById('search-count');
  const nav = [...document.querySelectorAll('.rail nav a')];
  const chapters = [...document.querySelectorAll('.chapter')];
  const cachedText = new Map(charters.map(item => [item, item.textContent.toLowerCase()]));
  let searchOpenState = null;

  function filterCharters() {
    const query = search.value.trim().toLowerCase();
    if (query && !searchOpenState) searchOpenState = new Map(charters.map(item => [item, item.open]));
    let matches = 0;
    for (const item of charters) {
      const match = query.split(/\s+/).every(word => cachedText.get(item).includes(word));
      item.hidden = !match;
      if (match) matches += 1;
      if (query && match) item.open = true;
      if (!query && searchOpenState) item.open = searchOpenState.get(item);
    }
    if (!query) searchOpenState = null;
    count.textContent = query ? `${matches} of ${charters.length} charters match` : `${charters.length} team charters`;
  }
  search.addEventListener('input', filterCharters);
  document.getElementById('clear-search').addEventListener('click', () => {
    search.value = '';
    filterCharters();
    search.focus();
  });
  document.getElementById('expand-charters').addEventListener('click', () => charters.forEach(item => { if (!item.hidden) item.open = true; }));
  document.getElementById('collapse-charters').addEventListener('click', () => charters.forEach(item => { item.open = false; }));

  function revealHash() {
    let hash;
    try { hash = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(hash);
    if (!target) return;
    const item = target.closest('.team-charter');
    if (item) {
      if (item.hidden) { search.value = ''; filterCharters(); }
      item.open = true;
    }
  }
  window.addEventListener('hashchange', revealHash);
  revealHash();

  let scrollPending = false;
  function updateNavigation() {
    let active = null;
    for (const chapter of chapters) {
      if (chapter.getBoundingClientRect().top <= 150) active = chapter.id;
    }
    nav.forEach(link => {
      if (link.hash.slice(1) === active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    scrollPending = false;
  }
  window.addEventListener('scroll', () => {
    if (!scrollPending) { scrollPending = true; requestAnimationFrame(updateNavigation); }
  }, { passive: true });
  updateNavigation();

  let printState = null;
  window.addEventListener('beforeprint', () => {
    printState = charters.map(item => ({ item, open: item.open, hidden: item.hidden }));
    charters.forEach(item => { item.hidden = false; item.open = true; });
  });
  window.addEventListener('afterprint', () => {
    if (printState) printState.forEach(({ item, open, hidden }) => { item.open = open; item.hidden = hidden; });
    printState = null;
  });
  document.getElementById('print-plan').addEventListener('click', () => window.print());
})();
