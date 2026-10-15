(() => {
  'use strict';
  const data = window.AuditoryPartsData;
  const list = document.querySelector('#parts-list');
  const buttons = [...document.querySelectorAll('[data-parts-option]')];
  const money = (n) => new Intl.NumberFormat('en-US', { style:'currency', currency:'USD' }).format(n);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const names = {'usb6361-terminal':'NI USB-6361 · screw terminals','usb6361-bnc':'NI USB-6361 · BNC',jbl305:'JBL 305P MkII',mf1:'TDT MF1-M speaker',mf2:'TDT MF2-M speaker',sa1:'TDT SA1 amplifier',zb1ps:'TDT ZB1PS powered enclosure',m50:'Earthworks M50',mm1:'Sound Devices MM-1',r8090:'REED R8090 calibrator','aa-battery':'AA batteries','bias-resistor':'100 kΩ resistors',hmic010:'Hosa HMIC-010 XLR cable',hss005:'Hosa HSS-005 TRS cable','mic-stand':'Gator microphone stand','pomona-output':'Pomona BNC output lead',phx106:'Hosa PHX-106F-BULK','ni-power-cord':'NI AC power cord',pxie1082:'NI PXIe-1082 chassis',pxie6363:'NI PXIe-6363',pxi4461:'NI PXI-4461',pxie8360:'NI PXIe-8360',pcie8361:'NI PCIe-8361','mxi-cable':'NI MXI-Express cable','shc68-cable':'NI SHC68-68-EPM cable',bnc2090a:'NI BNC-2090A',ed1:'TDT ED1 + enclosure/power',es1:'TDT ES1 + cable','bnc-output':'Hosa BNC-58-103 cable','ni-power-supply':'NI power supply','ni-usb-cable':'NI locking USB cable','ni-ferrite':'NI power-cable ferrite'};
  const functions = {
    'usb6361-terminal':'Outputs tones and records electrical signals.',
    'usb6361-bnc':'Outputs tones and records electrical signals.',
    umc204hd:'Plays sound and records the microphone.',
    jbl305:'Plays sound with a built-in amplifier.',
    emm6:'Measures sound near the ear.',
    mf1:'Produces tones from the amplifier output.',
    mf2:'Produces tones from the amplifier output.',
    m50:'Measures sound near the ear.',
    mm1:'Powers the microphone and amplifies its signal.',
    r8090:'Provides a 1-kHz sound-level reference.',
    tm2500c:'Provides a clock and network timing reference.',
    'edifier-mr3':'Plays sound with built-in amplification.',
    omnimic40k:'Measures sound for level and frequency calibration.'
  };
  function picture(p) {
    const reference = ['ni-power-supply','ni-ferrite'].includes(p.id);
    return `<img src="assets/parts/${p.id}.jpg" alt="${esc(p.name)}${reference ? ' · reference photo' : ''}" width="600" height="420" loading="lazy">${reference ? '<span class="photo-label">Reference photo</span>' : ''}`;
  }
  const groups = [
    { id:'sound', title:'Sound hardware', parts:['umc204hd','usb6361-terminal','usb6361-bnc','pxie1082','pxi4461','pxie6363','sa1','ed1','jbl305','mf2','mf1','es1','edifier-mr3'] },
    { id:'measurement', title:'Sound measurement', parts:['emm6','m50','mm1','omnimic40k','r8090','mic-stand'] },
    { id:'connections', title:'Connections & power', parts:['pxie8360','pcie8361','mxi-cable','shc68-cable','bnc2090a','tm2500c','hmic010','hss005','pomona-output','phx106','bnc-output','bias-resistor','zb1ps','ni-power-supply','ni-power-cord','ni-usb-cable','ni-ferrite','aa-battery'] }
  ];
  function card(p,candidate) {
    return `<li class="part-card" data-part-id="${p.id}"><a class="part-photo" href="${esc(p.url)}" target="_blank" rel="noopener" aria-label="Product source: ${esc(p.name)}">${picture(p)}</a><div class="part-caption"><h3>${esc(names[p.id] || p.name)}</h3><div class="part-price">${money(p.price)}${p.kind === 'estimate' ? '<small class="estimated-price">est.</small>' : ''}${p.qty>1 ? `<small>${p.qty} × ${money(p.unitPrice)}</small>` : ''}${candidate ? `<small>${p.id === 'edifier-mr3' ? 'powered pair' : 'package'}</small>` : ''}</div></div><p class="part-function">${esc(functions[p.id] || p.role)}</p></li>`;
  }
  function groupedParts(option,candidate) {
    if (candidate) return `<ul class="parts-grid" aria-label="Budget candidates">${option.items.map(p=>card(p,true)).join('')}</ul>`;
    return groups.map(group=>{
      const items=group.parts.map(id=>option.items.find(p=>p.id===id)).filter(Boolean);
      if (!items.length) return '';
      return `<section class="parts-group" aria-labelledby="group-${group.id}"><div class="parts-group-heading"><h2 id="group-${group.id}">${group.title}</h2></div><ul class="parts-grid">${items.map(p=>card(p,false)).join('')}</ul></section>`;
    }).join('');
  }
  function render(key) {
    const candidate = key === 'candidates';
    const option = candidate ? data.candidates : data.options[key];
    buttons.forEach((b) => b.setAttribute('aria-pressed',String(b.dataset.partsOption===key)));
    list.innerHTML = `${key === 'mcginley' ? '<p class="lab-reference"><a href="../sources/hardware_slides_2026-10-09/01_system_diagram.png" target="_blank" rel="noopener">Original lab diagram ↗</a><a href="../sources/hardware_slides_2026-10-09/02_equipment_links.png" target="_blank" rel="noopener">Parts slide ↗</a></p>' : ''}${groupedParts(option,candidate)}<div class="parts-total"><span>${candidate ? 'Two-part subtotal' : option.estimate ? 'Estimated parts total' : 'Parts total'}</span><strong>${money(candidate ? option.subtotal : option.total)}</strong></div>${candidate ? '<p class="candidate-note">These two candidates still need testing. NI, connections and calibration needs are additional.</p>' : ''}`;
  }
  buttons.forEach((b) => b.addEventListener('click',()=>render(b.dataset.partsOption)));
  render('basic');
})();
