(() => {
  'use strict';
  const data=window.AuditoryPartsData;
  const catalog=window.AuditoryPartsCatalog;
  const lists=[
    {key:'basic',name:'Basic',...data.options.basic},
    {key:'compact',...data.options.compact,name:'NI / Compact'},
    {key:'mcginley',...data.options.mcginley,name:'McGinley'},
    {key:'sonic',...data.options.sonic,name:'SONIC'},
    {key:'candidates',...data.candidates,name:'Budget candidates'}
  ];
  const money=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(n);
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const quantity=p=>p.qty>1 ? `${p.qty} × ${money(p.unitPrice)}` : p.id==='edifier-mr3' ? '1 pair' : p.id==='omnimic40k' ? '1 package' : ['mf1','mf2'].includes(p.id) ? '1 kit' : '';
  const genericFunctions={hmic010:'Connects the microphone to its input.'};
  const entries=new Map(lists.flatMap(list=>list.items).map(p=>[p.id,p]));
  function priceCell(list,id) {
    const p=list.items.find(p=>p.id===id);
    if(!p) return '<td class="comparison-absent"><span aria-label="Not listed in this option">—</span></td>';
    const date=p.observedDate||list.date;
    return `<td class="comparison-present" data-list="${list.key}"><a href="${esc(p.purchaseUrl||p.url)}" target="_blank" rel="noopener" title="${esc(p.source)} · ${esc(date)}" aria-label="${esc(list.name)} price for ${esc(p.name)}: ${money(p.price)}${p.kind==='estimate'?', planning estimate':''}">${money(p.price)}</a>${p.kind==='estimate'?'<small class="comparison-estimate">est.</small>':''}${quantity(p)?`<small>${quantity(p)}</small>`:''}</td>`;
  }
  const rows=catalog.groups.map(group=>{
    const parts=group.parts.map(id=>entries.get(id)).filter(Boolean);
    return `<tbody><tr class="comparison-group"><th colspan="6" scope="rowgroup">${group.title}</th></tr>${parts.map(p=>{
      const shared=lists.filter(list=>list.items.some(i=>i.id===p.id)).length>1;
      const reference=['ni-power-supply','ni-ferrite'].includes(p.id);
      return `<tr class="comparison-part${shared?' comparison-shared':''}" data-compare-part="${p.id}"><th scope="row"><div class="comparison-product"><span class="comparison-photo"><img src="assets/parts/${p.id}.jpg" alt="${esc(p.name)}${reference?' · reference photo':''}" width="100" height="80" loading="lazy"></span><div><strong>${esc(catalog.names[p.id]||p.name)}</strong><small>${esc(genericFunctions[p.id]||catalog.functions[p.id]||p.role)}</small>${reference?'<small class="comparison-reference">Reference photo</small>':''}</div></div></th>${lists.map(list=>priceCell(list,p.id)).join('')}</tr>`;
    }).join('')}</tbody>`;
  }).join('');
  document.querySelector('#comparison-table').innerHTML=`<table class="comparison-table"><caption class="sr-only">All parts across the five lists. Each filled cell gives that list's line price and quantity. Dashes mean the part is not listed in that option.</caption><colgroup><col class="comparison-product-col">${lists.map(()=>'<col class="comparison-list-col">').join('')}</colgroup><thead><tr><th scope="col">Part &amp; function</th>${lists.map(list=>`<th scope="col">${esc(list.name)}${list.key==='candidates'?'<small>2 devices only</small>':''}</th>`).join('')}</tr></thead>${rows}<tfoot><tr><th scope="row">Parts totals</th>${lists.map(list=>`<td data-total-list="${list.key}"><strong>${money(list.key==='candidates'?list.subtotal:list.total)}</strong><small>${list.key==='candidates'?'2-device subtotal':list.estimate?'Estimated parts total':'Includes calibrator'}</small></td>`).join('')}</tr></tfoot></table>`;
})();
