(() => {
  'use strict';
  const data = window.AuditoryPartsData;
  const list = document.querySelector('#parts-list');
  const buttons = [...document.querySelectorAll('[data-parts-option]')];
  const money = (n) => new Intl.NumberFormat('en-US', { style:'currency', currency:'USD' }).format(n);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const photos = new Set(['usb6361-terminal','usb6361-bnc','mf1','mf2','sa1','zb1ps','umc204hd','jbl305','emm6','m50','mm1','r8090','edifier-mr3','omnimic40k']);
  const names = {'usb6361-terminal':'NI USB-6361 · screw terminals','usb6361-bnc':'NI USB-6361 · BNC',jbl305:'JBL 305P MkII',mf1:'TDT MF1-M speaker',mf2:'TDT MF2-M speaker',sa1:'TDT SA1 amplifier',zb1ps:'TDT ZB1PS powered enclosure',m50:'Earthworks M50',mm1:'Sound Devices MM-1',r8090:'REED R8090 calibrator','aa-battery':'AA batteries','bias-resistor':'100 kΩ resistors'};
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
    if (photos.has(p.id)) return `<img src="assets/parts/${p.id}.jpg" alt="${esc(p.name)}" width="120" height="85" loading="lazy">`;
    return '<span class="part-placeholder" aria-hidden="true"><svg viewBox="0 0 60 50" fill="none" stroke="currentColor" stroke-width="1.2"><rect x="9" y="12" width="42" height="27" rx="3"/><path d="M17 21h15m-15 9h9"/><circle cx="42" cy="26" r="4"/></svg></span>';
  }
  function render(key) {
    const candidate = key === 'candidates';
    const option = candidate ? data.candidates : data.options[key];
    buttons.forEach((b) => b.setAttribute('aria-pressed',String(b.dataset.partsOption===key)));
    list.innerHTML = `<table class="parts-table"><caption class="sr-only">${esc(candidate ? 'Budget candidates' : option.name)} parts, functions and prices</caption><thead><tr><th scope="col">Part</th><th scope="col">Function</th><th scope="col">Price</th></tr></thead><tbody>${option.items.map((p) => `<tr><td><div class="part-name">${picture(p)}<a href="${esc(p.url)}" target="_blank" rel="noopener">${esc(names[p.id] || p.name)}${candidate ? `<small>${p.id === 'edifier-mr3' ? 'Powered pair' : 'USB measurement package'}</small>` : ''}</a></div></td><td>${esc(functions[p.id] || p.role)}</td><td class="part-price">${money(p.price)}${p.kind === 'estimate' ? '<small class="estimated-price">est.</small>' : ''}${p.qty>1 ? `<small>${p.qty} × ${money(p.unitPrice)}</small>` : ''}</td></tr>`).join('')}</tbody><tfoot><tr><th colspan="2" scope="row">${candidate ? 'Two-part subtotal' : option.estimate ? 'Estimated parts total' : 'Parts total'}</th><td>${money(candidate ? option.subtotal : option.total)}</td></tr></tfoot></table>${candidate ? '<p class="candidate-note">These two candidates still need testing. NI, connections and calibration needs are additional.</p>' : ''}`;
  }
  buttons.forEach((b) => b.addEventListener('click',()=>render(b.dataset.partsOption)));
  render('basic');
})();
