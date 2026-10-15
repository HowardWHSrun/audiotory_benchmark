(() => {
  'use strict';
  const data = window.AuditoryPartsData;
  const $ = (s) => document.querySelector(s);
  const stage = $('#parts-stage');
  const dialog = $('#part-detail');
  const money = (n) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
  const photoIds = new Set(['usb6361-terminal','usb6361-bnc','mf1','mf2','sa1','zb1ps','umc204hd','jbl305','emm6','m50','mm1','r8090','edifier-mr3','omnimic40k']);
  let chapter = 0;
  let borrowCalibrator = false;
  let detailTrigger = null;
  const allItems = [...Object.values(data.options).flatMap((o) => o.items), ...data.candidates.items];
  const item = (id, option) => (option ? data.options[option].items : allItems).find((p) => p.id === id);
  const basicTotal = () => data.options.basic.total - (borrowCalibrator ? item('r8090','basic').price : 0);
  const icons = {
    computer: '<rect x="10" y="12" width="76" height="48" rx="4"/><path d="M35 61v12m26-12v12M25 74h46M20 39h12l7-13 12 25 9-17 15 6"/>',
    sheep: '<ellipse cx="40" cy="48" rx="29" ry="20"/><path d="m58 37 12-17 18 7-4 24-16 6m5-34-10-7m21 14 9-8M22 65l-4 11m27-8-2 10m20-15 5 12"/><circle cx="77" cy="32" r="1.5"/>',
    recorder: '<rect x="12" y="12" width="72" height="55" rx="4"/><path d="M21 39h12l6-16 12 30 10-20 9 9h7M23 58h49M34 76h29"/>',
    cable: '<path d="M18 20h18v15H18zm9 15v12c0 21 42 21 42 0V35m-9-15h18v15H60zM22 12v8m10-8v8m32-8v8m10-8v8"/>',
    box: '<rect x="12" y="22" width="72" height="43" rx="4"/><path d="M20 43h22m-22 9h30M69 34v20"/><circle cx="69" cy="45" r="6"/>'
  };
  const svg = (type) => `<svg viewBox="0 0 96 90" aria-hidden="true">${icons[type] || icons.box}</svg>`;
  function photo(id, alt = '') {
    return photoIds.has(id) ? `<img src="assets/parts/${id}.jpg" alt="${esc(alt)}" loading="lazy" width="400" height="300">` : svg(id);
  }
  const heading = (label,title,body,tag='',estimate=false) => `<div class="chapter-heading"><div><span class="chapter-label">${label}</span><h2>${title}</h2><p>${body}</p></div>${tag ? `<span class="chapter-tag${estimate ? ' estimate' : ''}">${tag}</span>` : ''}</div>`;
  const notes = {
    umc204hd: 'Plays the computer waveform and powers/records the EMM-6 microphone. Its sample-rate setting does not extend the acoustic bandwidth of the speaker or microphone. A separate, compatible neural-recorder timing connection is still needed.',
    jbl305: 'One powered speaker is budgeted; its amplifier is built in. Specified to 20 kHz, so it is for a selected audible subset. Keep geometry fixed and measure the actual level and arrival time at the reference position.',
    emm6: 'The nominal 18 Hz–20 kHz range does not cover 32 kHz. Use its individual calibration file and a suitable phantom-powered input. Confirm calibrator fit and seal. This is not the full-band NI measurement baseline.',
    'usb6361-terminal': 'NI is our stimulus/timing reference. It outputs the waveform and acquires conditioned microphone/electrical references. It does not supply XLR phantom power. Confirm host/NI-DAQmx support, exact terminal wiring and neural-recorder input compatibility. Photo shows the terminal block removed.',
    'usb6361-bnc': 'BNC version used as the SONIC sound-chain reference. This basket adds power/accessories and our measurement kit; it is not an exact inventory of everything the paper authors purchased.',
    mf2: 'Nominal free-field range is 1–80 kHz. Use SA1 with its powered enclosure; the speaker kit includes its support/cable/adapter. The photo shows free-field and closed-field configurations, not two speakers to buy. Full-chain at-ear response remains unmeasured.',
    mf1: 'Paper speaker reference, with a nominal free-field band encompassing the paper tones. The photo shows free-field and closed-field configurations, not two purchased units. The $1,500 figure is our allowance, not a TDT quotation.',
    sa1: 'This amplifier drives the magnetic speaker. It requires a compatible powered enclosure. The $2,000 figure is our planning allowance; confirm the complete supplier configuration and included accessories.',
    zb1ps: 'Houses and powers the SA1. Its $750 figure is an author-set allowance. Confirm what the actual amplifier quote includes to avoid buying duplicate power hardware.',
    m50: 'Nominal microphone band reaches 50 kHz. In our NI proposal, MM-1 supplies microphone power/gain before NI acquisition. This is our measurement addition, not a microphone identified by SONIC. Confirm hardware revision, calibration file, loading and assembled response.',
    mm1: 'Supplies phantom power and converts the microphone signal to line level for NI. Two AA cells are budgeted. Check fixed gain, clipping and filter/limiter settings; the custom NI input connection remains to be verified.',
    r8090: 'Checks microphone sensitivity at 1 kHz. Its ±0.5 dB reference specification does not establish full-band at-ear accuracy. A suitable borrowed reference could replace this purchase; availability and adapters are unconfirmed.',
    'edifier-mr3': 'Nominal 52 Hz–40 kHz range includes the paper band, with no numeric flatness tolerance established in the retrieved specs. Use a wired input. Measure actual short-tone output, level, distortion and latency before selection. Built-in amplification means no separate SA1 is assumed for this candidate.',
    omnimic40k: 'USB microphone with its own ADC; it connects to the computer separately from NI. Candidate for level/frequency calibration, not a proven replacement for continuously recording arbitrary 10-ms pips into NI. PhotoLink timing is limited to sweep mode. Windows is recommended; raw capture and neural alignment remain unverified. A 40-kHz ceiling misses the 64-kHz second harmonic of a 32-kHz tone. Photo shows microphone only.',
    tm2500c: 'GPS/PTP/10-MHz time reference reported in the paper architecture. It only helps if the DAQ and recorder support the chosen routing. It does not establish acoustic arrival time or automatically prevent all alignment error.',
    es1: 'ES1 starts at 4 kHz and therefore omits the paper’s 1.4–4 kHz tones. Confirm its matched high-voltage cable and ED1 drive configuration. The $500 figure is an allowance, not a current supplier price.',
    ed1: 'The listed used bundle already includes an enclosure and power supply. Do not add a second powered chassis to this basket. Seller testing is not our physical verification.'
  };
  const shortNames = { umc204hd:'UMC204HD',jbl305:'JBL 305P MkII',emm6:'Dayton EMM-6','usb6361-terminal':'NI USB-6361',sa1:'TDT SA1 + power',mf2:'TDT MF2-M',m50:'Earthworks M50' };
  function card(id, option, role, summary, combinedPrice) {
    const p = item(id,option);
    return `<button type="button" class="part-card" data-part="${id}" data-option="${option}" aria-label="Details for ${esc(p.name)}"><span class="part-open" aria-hidden="true">↗</span><div class="part-photo">${photo(id,p.name)}</div><div class="part-info"><span class="part-function">${role}</span><h3>${shortNames[id] || esc(p.name)}</h3><p class="part-summary">${summary}</p><div class="part-cost"><span>${money(combinedPrice ?? p.price)}</span><small>${p.kind === 'estimate' ? 'Planning estimate' : 'Listed price'}${combinedPrice ? ' · incl. enclosure' : ''}</small></div></div></button>`;
  }
  function basket(key) {
    const o = data.options[key];
    return `<details class="basket-details"><summary>See every part, quantity &amp; source <span>${o.items.length} line items</span></summary><div class="basket-scroll"><table class="basket-table"><caption class="sr-only">${esc(o.name)} complete parts basket</caption><thead><tr><th scope="col">Part</th><th scope="col">Purpose</th><th scope="col">Qty</th><th scope="col">Basis</th><th scope="col">Line cost</th></tr></thead><tbody>${o.items.map((p) => `<tr><td><button type="button" data-part="${p.id}" data-option="${key}">${esc(p.name)}</button><span class="unit-note">${esc(p.source)} · ${p.observedDate}</span></td><td>${esc(p.role)}</td><td>${p.qty}</td><td class="${p.kind === 'estimate' ? 'table-estimate' : ''}">${p.kind === 'estimate' ? 'Estimate' : 'Observed'}${p.qty > 1 ? `<span class="unit-note">${money(p.unitPrice)} each</span>` : ''}</td><td>${key === 'basic' && p.id === 'r8090' && borrowCalibrator ? 'Borrow · $0.00' : money(p.price)}</td></tr>`).join('')}</tbody></table></div><p class="basket-note">${key === 'basic' ? 'Borrowing assumes a suitable reference is available. Recorder-specific timing connections remain extra.' : `Includes the ${money(data.sharedMeasurementKitTotal)} microphone/calibration kit once. Recorder-specific connections remain extra.`} <a href="${data.sources.currentBudget}" target="_blank" rel="noopener">Budget evidence ↗</a></p></details>`;
  }
  function overview() {
    return heading('01 / The setup','Make sound. Measure what arrives.','Our planned sheep experiment needs a sound path, an acoustic check, and a common timeline.','Planning only') +
      `<div class="signal-map"><div class="signal-route"><button type="button" class="signal-node" data-context="computer"><span class="signal-picture">${svg('computer')}</span><small>01 / Prepare</small><strong>Computer</strong><span>Known tones + event times</span></button><button type="button" class="signal-node" data-part="usb6361-terminal" data-option="compact"><span class="signal-picture">${photo('usb6361-terminal','NI USB-6361')}</span><small>02 / Output</small><strong>Sound device</strong><span>NI is our reference</span></button><button type="button" class="signal-node" data-part="mf2" data-option="compact"><span class="signal-picture">${photo('mf2','TDT MF2 speaker configurations')}</span><small>03 / Deliver</small><strong>Amplifier + speaker</strong><span>Turn voltage into sound</span></button><button type="button" class="signal-node" data-context="sheep"><span class="signal-picture">${svg('sheep')}</span><small>04 / Record</small><strong>Sedated sheep</strong><span>NET threads → neural recorder</span></button></div><div class="signal-returns"><div class="signal-return"><span aria-hidden="true">↳</span><div><strong>Microphone at the ear position</strong><p>Checks sound level, response and actual arrival.</p></div></div><div class="signal-return"><span aria-hidden="true">↔</span><div><strong>Timing reference to the recorder</strong><p>Connection TBD; measure offset, jitter and drift.</p></div></div></div></div><p class="overview-caption"><span>Diagram uses the NI/TDT candidate to show the roles. Select a component for details.</span><span>Sound source → acoustic check → neural timestamps</span></p>`;
  }
  function basic() {
    return heading('02 / Basic','Start with selected audible tones.','A small sound-and-measurement setup. It does not cover the complete 1.4–32 kHz paper band.','Below 20 kHz') +
      `<div class="part-gallery three">${card('umc204hd','basic','Playback + input','Converts the waveform; records the microphone.')}${card('jbl305','basic','Sound delivery','One powered speaker. No separate amplifier.')}${card('emm6','basic','Acoustic check','Measures sound near the ear; specified to 20 kHz.')}</div><div class="setup-bottom"><div><p>The basket also includes an XLR lead, two TRS leads, a microphone stand and a 1-kHz calibrator. Computer and neural recorder are reused, subject to compatibility.</p><label class="borrow-control"><input type="checkbox" id="borrow-calibrator" ${borrowCalibrator ? 'checked' : ''}>Borrow a suitable calibrator instead of buying one <span>(availability TBD)</span></label></div><div class="budget-total"><span>Parts total</span><strong id="basic-total">${money(basicTotal())}</strong><small>Oct 15 price snapshot · extras excluded</small></div></div>${basket('basic')}<p class="basis-note">The older PDF lists ${money(data.historicalBasicTotal)}. This view uses the October 15 microphone-price refresh. Playback-to-neural timing is still unmeasured.</p>`;
  }
  function compact() {
    return heading('03 / NI reference','A compact path for the paper’s tone band.','The proposed NI/TDT chain covers 1.4–32 kHz nominally. Its assembled response and recorder alignment still need verification.','Proposed · untested',true) +
      `<div class="part-gallery">${card('usb6361-terminal','compact','Waveform + timing','Outputs tones; acquires conditioned references.')}${card('sa1','compact','Amplify + power','SA1 in a ZB1PS powered enclosure.',item('sa1','compact').price + item('zb1ps','compact').price)}${card('mf2','compact','Sound delivery','Magnetic speaker; full paper-band candidate.')}${card('m50','compact','Acoustic check','M50 → MM-1 → NI analog input.')}</div><div class="setup-bottom"><p>Includes the M50, MM-1 preamp/power, calibrator and accessories. Speaker, amplifier and enclosure contribute <strong>$4,250 in author-set estimates</strong>; supplier quotes are still needed.</p><div class="budget-total"><span>Estimated parts total</span><strong>${money(data.options.compact.total)}</strong><small>Includes the measurement kit once</small></div></div>${basket('compact')}<p class="basis-note">NI does not provide microphone phantom power. The MM-1 and custom microphone input wiring are part of this proposal. The newer MR3 candidate is another route to evaluate.</p>`;
  }
  function candidates() {
    return heading('04 / New lower-cost candidates','Keep NI. Evaluate cheaper sound and calibration.','These alternatives were added October 15. Nominal bandwidth is a reason to test them, not proof of experimental performance.','Needs bench checks',true) +
      `<div class="candidate-grid">${data.candidates.items.map((p,i) => `<article class="candidate"><button type="button" class="candidate-image" data-part="${p.id}" aria-label="Details for ${esc(p.name)}">${photo(p.id,p.name)}</button><div><p class="candidate-purpose">${i === 0 ? 'Speaker alternative' : 'Measurement alternative'}</p><h3>${esc(p.name)}</h3><p class="candidate-price">${money(p.price)} <small>${i === 0 ? '/ powered pair' : '/ package'}</small></p><p>${i === 0 ? 'Nominal 52 Hz–40 kHz. Built-in amplification; evaluate with a wired input.' : 'Calibrated response shape to 40 kHz. USB connects separately from NI.'}</p><button type="button" class="text-link" data-part="${p.id}">Connection &amp; limits ↗</button></div></article>`).join('')}</div><div class="candidate-comparison"><div><h3>Our NI measurement baseline</h3><span class="path-label">M50 → MM-1 → NI analog input</span><p>Microphone and preamp: <strong>${money(data.referenceNI.microphone_and_preamp_subtotal_usd)}</strong>. NI can capture the conditioned microphone signal with configured hardware timing; neural alignment remains open.</p><p>OmniMic’s <strong>${money(item('omnimic40k').price)}</strong> package is a cheaper calibration candidate. Arbitrary short-pip recording and alignment to NI/neural timestamps remain unverified.</p></div><div><h3>What this changes</h3><p>MR3 could replace the TDT speaker/amplifier path if it passes measured output checks. OmniMic can be evaluated alongside NI for level and frequency calibration.</p><p>PhotoLink timing is for sweep mode. The 40-kHz microphone ceiling also misses a 32-kHz tone’s 64-kHz second harmonic.</p><p class="subtotal">${money(data.candidates.subtotal)} <small>for these two devices only; add NI, connections and any calibration needs.</small></p></div></div>`;
  }
  function compare() {
    const order = ['basic','compact','mcginley','sonic'];
    const labels = {basic:'Audible bench candidate',compact:'Proposed NI/TDT chain',mcginley:'Supplied slide architecture',sonic:'Paper-based reference + our additions'};
    const scopes = {basic:'Selected audible subset',compact:'Full paper-band candidate',mcginley:'ES1 starts at 4 kHz',sonic:'Full paper-band reference'};
    return heading('05 / Compare','Four baskets. Four different scopes.','These are alternatives; do not add their totals together. Reuse and recorder compatibility remain to be confirmed.') +
      `<div class="comparison-scroll"><table class="option-comparison"><caption class="sr-only">Four alternative auditory hardware baskets</caption><thead><tr><th scope="col">Setup</th><th scope="col">Parts budget</th><th scope="col">Sound coverage</th><th scope="col">Explore</th></tr></thead><tbody>${order.map((key) => `<tr><td><strong>${esc(data.options[key].name)}</strong><small>${labels[key]}</small></td><td><strong class="compare-price">${money(key === 'basic' ? basicTotal() : data.options[key].total)}</strong><small>${key === 'basic' ? (borrowCalibrator ? 'Borrowed calibrator assumed' : 'Includes calibrator purchase') : `Includes ${money(data.options[key].estimate)} in estimates`}</small></td><td>${scopes[key]}<small>${key === 'basic' ? 'Does not cover all 1.4–32 kHz tones' : key === 'mcginley' ? 'Omits the lowest SONIC tones' : 'Assembled acoustic response unverified'}</small></td><td><button type="button" class="compare-action" ${key === 'basic' || key === 'compact' ? `data-jump="${key === 'basic' ? 1 : 2}"` : `data-basket="${key}"`}>${key === 'basic' || key === 'compact' ? 'View setup' : 'View all parts'} ↗</button></td></tr>`).join('')}</tbody></table></div><div class="compare-footer"><p>Specialized totals include our ${money(data.sharedMeasurementKitTotal)} measurement kit once. Shipping, tax, added import charges, recorder-specific adapters and labor remain extra. These budgets do not predict precision or ITR.</p><button type="button" data-jump="3">New consumer candidates ↗</button></div><div id="reference-basket"></div><p class="basis-note">Basic uses the October 15 refresh; specialized baskets mix dated observations and estimates. The NI/TDT candidate is not the only possible full-band route.</p>`;
  }
  function needed() {
    return heading('06 / Still needed','Confirm what we have. Fill the actual gaps.','Choose the required sound range first, then settle the recorder connection and inventory. No purchase status is assumed.') +
      `<div class="needs-layout"><div class="reuse-list"><h3>Reuse or borrow, if suitable.</h3><div class="reuse-item"><strong>Lab computer</strong><p>Confirm operating system, drivers and playback software.</p><small>Availability / compatibility TBD</small></div><div class="reuse-item"><strong>NET threads + neural recorder</strong><p>NET family is confirmed; exact recorder, channels and marker/clock inputs are still unknown.</p><small>Model / interface TBD</small></div><div class="reuse-item"><strong>Calibration equipment</strong><p>A suitable borrowed calibrator or microphone chain could avoid duplicate purchases.</p><small>Borrowing / fit / calibration TBD</small></div></div><ol class="needs-list"><li><h3>Choose the frequency band</h3><p>Selected audible tones, or the full 1.4–32 kHz paper band? This determines which speaker and microphone are candidates.</p><small>TBD · Howard + Jiaao with the research team</small></li><li><h3>Identify recorder inputs and clock support</h3><p>Confirm connector, voltage levels and how repeated markers or a shared reference will be recorded.</p><small>TBD · recorder owner; Howard + Jiaao to coordinate</small></li><li><h3>Confirm inventory and complete quotes</h3><p>Check what the lab owns. Quote TDT kits if selected and count bundled cables/power once.</p><small>TBD · Howard + Jiaao</small></li><li><h3>Verify the assembled sound and timing</h3><p>Measure at-ear response, short-tone envelope and onset; check offset, jitter and drift against neural timestamps.</p><small>Planned bench work · Howard + Jiaao</small></li></ol></div><p class="needs-boundary">Rice’s planned sedated-sheep preparation differs from SONIC’s awake sheep. Response windows and achieved performance remain unverified. No soundproof box or behavioral rig is required by the current team direction.</p>`;
  }
  const chapters = [overview,basic,compact,candidates,compare,needed];
  function render(moveFocus = false) {
    stage.innerHTML = chapters[chapter]();
    document.querySelectorAll('[data-chapter]').forEach((b) => {
      if (Number(b.dataset.chapter) === chapter) b.setAttribute('aria-current','step');
      else b.removeAttribute('aria-current');
    });
    $('#parts-progress').textContent = `${String(chapter+1).padStart(2,'0')} / 06`;
    $('#parts-prev').disabled = chapter === 0;
    $('#parts-next').disabled = chapter === chapters.length-1;
    if (moveFocus) {
      const title = stage.querySelector('h2');
      title.tabIndex = -1;
      title.focus({preventScroll:true});
    }
  }
  function go(n,focus=true) { chapter = Math.max(0,Math.min(chapters.length-1,n)); render(focus); }
  function openPart(id,option,trigger) {
    const p = item(id,option);
    if (!p) return;
    const combined = id === 'sa1' && option === 'compact';
    detailTrigger = trigger;
    $('#part-body').innerHTML = `<div class="part-dialog-grid"><div class="part-dialog-photo">${photo(id,p.name)}</div><div><span class="chapter-label">${p.kind === 'estimate' ? 'Author-set estimate · quote needed' : 'Planning price snapshot'}</span><h2 id="part-title">${esc(p.name)}</h2><p>${esc(p.role)}</p><p class="part-detail-price">${money(p.price)}<small>${p.qty} ${p.qty > 1 ? `× ${money(p.unitPrice)}` : 'item / package'} · ${esc(p.source)}${p.observedDate ? ` · ${p.observedDate}` : ''}</small></p>${combined ? '<p>The card combines SA1 ($2,000) and ZB1PS power/enclosure ($750); both are estimates.</p>' : ''}<a class="part-detail-source" href="${esc(p.url)}" target="_blank" rel="noopener">Product / listing source ↗</a>${p.manualUrl ? ` · <a class="part-detail-source" href="${esc(p.manualUrl)}" target="_blank" rel="noopener">Manual ↗</a>` : ''}</div></div><div class="part-dialog-note"><p class="eyebrow">Role &amp; what to confirm</p><p>${esc(notes[id] || p.note || 'Confirm the exact connector, configuration, included accessories and compatibility before purchase. This is a planning line item; it has not been physically verified.')}</p></div>`;
    dialog.showModal();
  }
  function openContext(key,trigger) {
    const descriptions = {computer:['Stimulus computer','Prepare known tones and event times.','Reuse a compatible lab computer. NI-DAQmx, operating-system support, waveform software and physical marker output need confirmation.'],sheep:['Sheep + neural recording','Record auditory cortical responses under sedation.','The team plans sedated sheep with NET threads; exact recorder interface and channel count remain unconfirmed. SONIC used awake sheep. Response windows and achieved performance cannot be inherited from the paper.']};
    const [name,role,note] = descriptions[key];
    detailTrigger=trigger;
    $('#part-body').innerHTML=`<div class="part-dialog-grid"><div class="part-dialog-photo">${svg(key)}</div><div><span class="chapter-label">Reuse / team direction</span><h2 id="part-title">${name}</h2><p>${role}</p><p>No new purchase price assigned.</p></div></div><div class="part-dialog-note"><p class="eyebrow">To confirm</p><p>${note}</p></div>`;
    dialog.showModal();
  }
  document.querySelectorAll('[data-chapter]').forEach((b) => b.addEventListener('click',()=>go(Number(b.dataset.chapter))));
  stage.addEventListener('click',(event)=>{
    const target=event.target.closest('button');
    if (!target) return;
    if (target.dataset.part) openPart(target.dataset.part,target.dataset.option,target);
    if (target.dataset.context) openContext(target.dataset.context,target);
    if (target.dataset.jump) go(Number(target.dataset.jump));
    if (target.dataset.basket) {
      $('#reference-basket').innerHTML=basket(target.dataset.basket);
      $('#reference-basket details').open=true;
      $('#reference-basket summary').focus({preventScroll:true});
    }
  });
  stage.addEventListener('change',(event)=>{
    if (event.target.id !== 'borrow-calibrator') return;
    borrowCalibrator=event.target.checked;
    const expanded=stage.querySelector('.basket-details').open;
    render();
    stage.querySelector('.basket-details').open=expanded;
    $('#borrow-calibrator').focus({preventScroll:true});
  });
  $('#parts-prev').addEventListener('click',()=>go(chapter-1));
  $('#parts-next').addEventListener('click',()=>go(chapter+1));
  $('#parts-present').addEventListener('click',()=>{
    const active=document.body.classList.toggle('presenting-parts');
    $('#parts-present').setAttribute('aria-pressed',String(active));
    $('#parts-present').firstChild.textContent=active ? 'Exit presentation ' : 'Present ';
    window.scrollTo({top:0,behavior:'instant'});
  });
  document.addEventListener('keydown',(event)=>{
    if ($('#parts').hidden || dialog.open || event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.key==='Escape' && document.body.classList.contains('presenting-parts')) { $('#parts-present').click(); return; }
    if (event.target.closest('input,select,textarea,summary,button,a,[contenteditable]')) return;
    if (event.key==='ArrowRight' || event.key==='ArrowLeft') { event.preventDefault(); go(chapter+(event.key==='ArrowRight' ? 1 : -1)); }
  });
  $('#part-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('close',()=>{ if(detailTrigger?.isConnected) detailTrigger.focus({preventScroll:true}); });
  dialog.addEventListener('click',(event)=>{
    if(event.target!==dialog) return;
    const b=dialog.getBoundingClientRect();
    if(event.clientX<b.left || event.clientX>b.right || event.clientY<b.top || event.clientY>b.bottom) dialog.close();
  });
  render();
})();
