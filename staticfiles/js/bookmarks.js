// Reactive Bookmarks Listing
(function(){
  const grid = document.getElementById('bookmarksGrid');
  if(!grid) return;
  const searchInput = document.querySelector('.search-box-inline input, .search-box input');
  const typeSelect = document.getElementById('typeFilter');
  // Tag filter removed
  const pagingContainer = document.querySelector('.pagination-wrap');
  let currentPage = 1; let loading=false;

  function debounce(fn, wait){ let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn.apply(this,a),wait);}; }

  const iconMap = { pdf:'file-pdf', ppt:'file-powerpoint', pptx:'file-powerpoint', doc:'file-word', docx:'file-word', image:'image', link:'link', txt:'file-lines' };

  function cardHTML(r){
    const verifyBadge = r.verification_status === 'verified' ? '<span class="rcv2-verify-badge" title="Verified"><i class="fas fa-check"></i></span>' : (r.verification_status === 'pending' ? '<span class="rcv2-pending-badge" title="Pending"><i class="fas fa-clock"></i></span>' : '');
    const extraTags = r.tags_extra && r.tags_extra > 0 ? `<span class="rcv2-tag more" title="More tags">+${r.tags_extra}</span>` : '';
    const icon = iconMap[r.resource_type] || 'file-alt';
    return `<div class="resource-card-v2" data-resource-id="${r.id}">
      <div class="rcv2-head">
        <span class="rcv2-type">${r.resource_type.toUpperCase()}</span>
        <span class="rcv2-remove-indicator" data-remove="${r.id}" title="Remove bookmark" aria-label="Remove bookmark"><i class="fas fa-xmark"></i></span>
      </div>
      <a href="/resources/${r.id}/" class="rcv2-body" aria-label="View resource ${r.title}">
        <div class="rcv2-icon-wrapper">
          <div class="rcv2-icon"><i class="fas fa-${icon}"></i></div>
          ${verifyBadge}
        </div>
        <h3 class="rcv2-title" title="${r.title}">${r.title}</h3>
        <div class="rcv2-metrics">
          <span><i class="fas fa-eye"></i> ${r.views_count}</span>
          <span><i class="fas fa-download"></i> ${r.download_count}</span>
          ${r.average_rating? `<span><i class='fas fa-star'></i> ${r.average_rating}</span>`:''}
        </div>
        ${r.tags.length? `<div class="rcv2-tags">${r.tags.map(t=>`<span class=\"rcv2-tag\">${t}</span>`).join('')}${extraTags}</div>`:''}
      </a>
      <div class="rcv2-footer">
        <span class="rcv2-author">By: ${r.uploader}</span>
        <span class="rcv2-age">${r.created_since}</span>
      </div>
    </div>`;
  }

  function getCSRF(){ const m = document.cookie.match(/csrftoken=([^;]+)/); return m? m[1]:''; }

  async function removeBookmark(id){
    try {
      const resp = await fetch(`/bookmarks/toggle/${id}/`, { method:'POST', headers:{'X-CSRFToken': getCSRF()} });
      if(!resp.ok){ throw new Error('Failed'); }
      const el = grid.querySelector(`.resource-card-v2[data-resource-id='${id}']`);
      if(el){ el.remove(); }
      if(!grid.children.length){ grid.innerHTML = '<div class="resources-empty">No bookmarks yet. <a href="/resources/list/" class="upload-inline">Browse resources</a>.</div>'; grid.classList.add('is-empty'); }
    } catch(e){ console.warn('Remove bookmark failed', e); }
  }

  async function fetchBookmarks(page=1){
    if(loading) return; loading=true; grid.classList.add('loading');
    const params = new URLSearchParams();
    if(searchInput && searchInput.value.trim()) params.append('q', searchInput.value.trim());
    if(typeSelect && typeSelect.value) params.append('resource_type', typeSelect.value);
    params.append('page', page);
    try {
      const resp = await fetch('/bookmarks/api/list/?'+params.toString(), { headers:{'Accept':'application/json'} });
      if(!resp.ok) throw new Error('Network');
      const json = await resp.json();
      if(!json.success) throw new Error('API');
      currentPage = json.page;
      const html = json.results.map(cardHTML).join('');
      if(html){ grid.innerHTML = html; grid.classList.remove('is-empty'); } else { grid.innerHTML = '<div class="resources-empty">No bookmarks found.</div>'; grid.classList.add('is-empty'); }
      renderPagination(json);
      bindRemove();
    } catch(err){ grid.innerHTML='<div class="resources-empty">Error loading bookmarks.</div>'; grid.classList.add('is-empty'); }
    finally { grid.classList.remove('loading'); loading=false; }
  }

  function renderPagination(meta){
    if(!pagingContainer) return; const {page,num_pages,has_previous,has_next}=meta;
    if(num_pages<=1){ pagingContainer.innerHTML=''; return; }
    let out='<ul class="pagination justify-content-center">';
    if(has_previous){ out+=`<li class='page-item'><a class='page-link' data-page='${page-1}' href='#'>Previous</a></li>`; }
    out+=`<li class='page-item active'><span class='page-link'>Page ${page} of ${num_pages}</span></li>`;
    if(has_next){ out+=`<li class='page-item'><a class='page-link' data-page='${page+1}' href='#'>Next</a></li>`; }
    out+='</ul>'; pagingContainer.innerHTML=out;
    pagingContainer.querySelectorAll('a.page-link').forEach(a=>{ a.addEventListener('click',e=>{ e.preventDefault(); fetchBookmarks(parseInt(a.dataset.page)); }); });
  }

  function bindRemove(){
    grid.querySelectorAll('.rcv2-remove-indicator').forEach(btn=>{
      btn.addEventListener('click',e=>{ e.preventDefault(); const id=btn.getAttribute('data-remove'); removeBookmark(id); });
    });
  }

  const debouncedFetch = debounce(()=>fetchBookmarks(1), 400);
  if(searchInput) searchInput.addEventListener('input', debouncedFetch);
  if(typeSelect) typeSelect.addEventListener('change', ()=>fetchBookmarks(1));

  // Enhance selects (reuse from resources)
  function enhanceSelect(sel){
    if(!sel || sel.dataset.enhanced) return; sel.dataset.enhanced='1'; sel.classList.add('hidden-native-select');
    const wrapper=document.createElement('div'); wrapper.className='filter-dd';
    const trigger=document.createElement('button'); trigger.type='button'; trigger.className='filter-dd-trigger'; trigger.setAttribute('aria-haspopup','listbox'); trigger.setAttribute('aria-expanded','false'); trigger.innerHTML=`<span class='dd-icon'><i class='fas fa-filter'></i></span><span class='dd-label'>${sel.options[sel.selectedIndex]?.text||'Select'}</span>`;
    const menu=document.createElement('ul'); menu.className='filter-dd-menu'; menu.setAttribute('role','listbox'); menu.tabIndex=-1;
    const isType= sel.id==='typeFilter'; const localIconMap=iconMap;
    Array.from(sel.options).forEach(opt=>{ const li=document.createElement('li'); li.className='filter-dd-item'; li.setAttribute('role','option'); li.dataset.value=opt.value; if(opt.selected) li.setAttribute('aria-selected','true'); const icon=isType && opt.value? `<span class='type-icon'><i class='fas fa-${localIconMap[opt.value]||'file-alt'}'></i></span>`:'<span class="type-icon"></span>'; li.innerHTML=`${icon}<span class='opt-text'>${opt.text}</span>`; li.addEventListener('click',()=>{ Array.from(menu.children).forEach(c=>c.removeAttribute('aria-selected')); li.setAttribute('aria-selected','true'); sel.value=opt.value; sel.dispatchEvent(new Event('change',{bubbles:true})); trigger.querySelector('.dd-label').textContent=opt.text; closeMenu(); fetchBookmarks(1); }); menu.appendChild(li); });
    function openMenu(){ wrapper.classList.add('open'); trigger.setAttribute('aria-expanded','true'); menu.focus(); }
    function closeMenu(){ wrapper.classList.remove('open'); trigger.setAttribute('aria-expanded','false'); }
    trigger.addEventListener('click',()=>{ wrapper.classList.contains('open')? closeMenu():openMenu(); });
    trigger.addEventListener('keydown',e=>{ if(['ArrowDown','Enter',' '].includes(e.key)){ e.preventDefault(); openMenu(); } });
    menu.addEventListener('keydown',e=>{ const items=Array.from(menu.querySelectorAll('.filter-dd-item')); const current=items.findIndex(i=>i.getAttribute('aria-selected')==='true'); if(e.key==='Escape'){ closeMenu(); trigger.focus(); } else if(e.key==='ArrowDown'){ e.preventDefault(); const next=items[current+1]||items[0]; next.click(); } else if(e.key==='ArrowUp'){ e.preventDefault(); const prev=items[current-1]||items[items.length-1]; prev.click(); } else if(e.key==='Enter'){ e.preventDefault(); closeMenu(); trigger.focus(); } });
    document.addEventListener('click',e=>{ if(!wrapper.contains(e.target)) closeMenu(); });
    sel.parentNode.insertBefore(wrapper, sel); wrapper.appendChild(trigger); wrapper.appendChild(menu); wrapper.appendChild(sel);
  }
  enhanceSelect(typeSelect);

  // Initial load (JS overrides server fallback)
  fetchBookmarks(currentPage);
})();