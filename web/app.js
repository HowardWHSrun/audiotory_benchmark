(() => {
  'use strict';
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const state = { duration: 10, alphabet: 'C', window: 50, stage: 0, tone: 0, playing: false };
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const paperPath = '../sources/SONIC_2025_bioRxiv_v1.pdf';
  const model = window.SONICModel;
  const frequencies = {
    // Representative toy pitches, not a reconstruction of the source's C array.
    C: [2, 5, 8, 12, 16, 20, 24, 30],
    E: [2, 4, 6, 8, 9, 10.5, 17, 18.2, 19.5, 20.9, 22.4, 24, 25.8, 27]
  };
  const sequenceIndices = [3, 28, 12, 34, 8, 21, 16, 31];
  const details = [
    { title: 'Start with an answer you already know.', body: "A computer creates randomized pure tones. Each tone's frequency and start time are known, so the experiment has a clear answer against which to test the decoder.", source: 'Paper · pp. 4, 11', page: 11 },
    { title: 'Turn the waveform into sound.', body: 'An audio output converts the waveform to voltage, and a speaker sends sound through the air. Calibration near the ears establishes what sound actually arrives; a microphone can verify acoustic onset.', source: 'Paper · p. 11; microphone is a proposed Rice check', page: 11 },
    { title: 'Let the auditory system respond.', body: 'Neurons in primary auditory cortex respond to tone frequency. Those responses take time and overlap across adjacent tones. The paper recorded awake, alert sheep; Rice is planning a sedated preparation.', source: 'Paper · pp. 8, 13', page: 13 },
    { title: 'Measure the neural voltages.', body: 'The Connexus array contains 421 electrodes. The published experiment samples at 5.2 kHz, then filters and references the signals to isolate spike-band activity. The traces below are synthetic, not recorded data.', source: 'Paper · pp. 11, 13', page: 11 },
    { title: 'Summarize activity in 5-ms bins.', body: 'Each channel contributes spike counts and spike-band power. The main analysis combines ten bins over 50 ms. The shorter-window analysis asks how much information remains with less observed activity.', source: 'Paper · pp. 7–8, 11–12', page: 11 },
    { title: 'Predict the tone, then compare.', body: 'A neural-network decoder predicts which tone occurred. Predictions on held-out data are compared with the known tones. Their confusion matrix yields achieved information transfer rate; no achieved rate is simulated here.', source: 'Paper · pp. 6–7, 12', page: 12 }
  ];
  let timer = null;

  function switchView(view, focus = false) {
    if (view === 'main') {
      $('#main').focus({ preventScroll: true });
      return;
    }
    const anchorTarget = document.getElementById(view);
    const anchorView = anchorTarget && anchorTarget.closest('.view');
    if (anchorTarget && anchorView && !anchorView.hidden && !['setup', 'paper'].includes(view)) return;
    // Existing shared links continue to work after moving the Rice setup home.
    view = view === 'paper' || view === 'results' ? 'paper' : 'setup';
    $$('.view').forEach((section) => { section.hidden = section.id !== view; });
    $$('.nav-tab').forEach((button) => {
      const active = button.dataset.view === view;
      button.classList.toggle('active', active);
      if (active) button.setAttribute('aria-current', 'page');
      else button.removeAttribute('aria-current');
    });
    if (view !== 'paper') setPlaying(false);
    if (location.hash !== `#${view}`) history.replaceState(null, '', `#${view}`);
    if (focus) $('#main').focus({ preventScroll: true });
  }

  const components = {
    computer: { index: '01 / SOUND SOURCE', title: 'Stimulus computer', role: 'Prepare a known tone sequence and its intended start times. Keep tone identity and trial order as ground truth for later analysis.', confirm: 'Choose software, waveform specifications, and how event markers reach the acquisition system.' },
    dac: { index: '02 / WAVEFORM OUTPUT', title: 'DAC / audio output', role: 'Convert the digital waveform into an electrical signal for sound delivery.', confirm: 'Confirm the available output device, usable bandwidth, sample rate, output routing, and clock access.' },
    speaker: { index: '03 / SOUND DELIVERY', title: 'Amplifier + speaker', role: 'Deliver the tones through the air. Use an amplifier if the chosen speaker requires one, and measure the delivered sound at the ear position.', confirm: 'Choose the actual models, geometry, usable frequency range, and operating level from calibration evidence.' },
    sheep: { index: '04 / NEURAL RESPONSE', title: 'Sedated sheep', role: 'The planned preparation receives sound while auditory-cortex activity is recorded. A sound-isolation box or behavioral rig is not required for this plan.', confirm: 'Agree on sedation and monitoring with the experiment owners. Establish response timing and suitable analysis windows in this preparation.' },
    interface: { index: '05 / NEURAL MEASUREMENT', title: 'Neural interface', role: 'Measure the auditory-cortex response and pass neural signals to the recording system.', confirm: 'Confirm the actual interface, channel coverage, sampling settings, references, and access to timestamped data.' },
    recorder: { index: '06 / DATA CAPTURE', title: 'Recorder', role: 'Save neural data together with event timing, a synchronized reference, or aligned acquisition signals.', confirm: 'Specify marker inputs and clock sharing. Measure offset, jitter, drift, and missing-event handling before interpreting neural response times.' },
    microphone: { index: 'SOUND CHECK / AT THE EAR POSITION', title: 'Calibration microphone', role: 'Measure delivered sound level, frequency response, and the actual acoustic onset near the ear position.', confirm: 'Choose a calibrated microphone and acquisition route. Confirm its usable range and synchronization with event and neural timestamps.' }
  };

  function selectComponent(key) {
    const component = components[key];
    if (!component) return;
    $$('[data-component]').forEach((button) => {
      const active = button.dataset.component === key;
      button.classList.toggle('selected', active);
      button.setAttribute('aria-pressed', String(active));
    });
    $('#component-index').textContent = component.index;
    $('#component-title').textContent = component.title;
    $('#component-role').textContent = component.role;
    $('#component-confirm').textContent = component.confirm;
  }

  function frequencyForTone(index) {
    const set = frequencies[state.alphabet];
    return set[sequenceIndices[index % sequenceIndices.length] % set.length];
  }

  function formatFrequency(value) { return `${value.toFixed(1)} kHz`; }

  function renderSequence() {
    const set = frequencies[state.alphabet];
    $('#tone-sequence').innerHTML = sequenceIndices.map((n, index) => {
      const frequency = set[n % set.length];
      const cycles = 1.6 + frequency / 8;
      const points = Array.from({ length: 71 }, (_, x) => `${x},${14 + 8 * Math.sin(x / 70 * cycles * Math.PI * 2)}`).join(' ');
      return `<button type="button" class="tone-tile${index === state.tone ? ' active' : ''}" data-tone="${index}" aria-pressed="${index === state.tone}" aria-label="Illustrative tone ${index + 1}, ${formatFrequency(frequency)}"><svg viewBox="0 0 70 28" aria-hidden="true"><polyline points="${points}" fill="none" stroke-width="1.4"/></svg><span>${formatFrequency(frequency)}</span></button>`;
    }).join('');
    $$('.tone-tile').forEach((button) => button.addEventListener('click', () => {
      state.tone = Number(button.dataset.tone);
      renderSequence();
      renderTimeline();
    }));
    $('#current-tone').textContent = `Tone ${state.tone + 1} · ${formatFrequency(frequencyForTone(state.tone))}`;
  }

  function renderStage() {
    $$('.stage').forEach((button) => {
      const selected = Number(button.dataset.stage) === state.stage;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    const detail = details[state.stage];
    $('#detail-step').textContent = `0${state.stage + 1} / 06`;
    $('#detail-title').textContent = detail.title;
    $('#detail-body').textContent = detail.body;
    $('#detail-source').textContent = `${detail.source} ↗`;
    $('#detail-source').href = `${paperPath}#page=${detail.page}`;
  }

  function renderControls() {
    const count = model.results[state.alphabet].classes;
    const seconds = state.duration / 1000;
    $('#duration-output').textContent = `${state.duration} ms`;
    $('#tone-rate').innerHTML = `${(1 / seconds).toLocaleString('en-US', { maximumFractionDigits: 1 })} <small>tones/s</small>`;
    $('#input-ceiling').innerHTML = `${Math.round(model.ceilingBps(count, state.duration))} <small>bits/s</small>`;
    $('#alphabet-description').textContent = state.alphabet === 'C' ? '1.4–32 kHz in ⅛-octave steps.' : '2–10.5 kHz sampled coarsely; 17–27 kHz sampled more densely.';
    $$('[data-alphabet]').forEach((button) => {
      const active = button.dataset.alphabet === state.alphabet;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    $$('[data-window]').forEach((button) => {
      const active = Number(button.dataset.window) === state.window;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    $('#intrinsic-delay').innerHTML = `${model.intrinsicDelayMs(state.window)} <small>ms</small>`;
    $('#delay-mode').textContent = state.window === 50 ? 'Main 50-ms observation window' : 'Single 5-ms bin in the window sweep';
    $('#window-caveat').innerHTML = state.window === 50
      ? '<strong>56 ms:</strong> the reported main analysis. The ten 5-ms feature bins span 10–60 ms after tone onset.'
      : '<strong>11 ms:</strong> a single-session optimized-window sweep. The 5-ms bin shown here has an illustrative position near the response peak, not a recovered exact optimum.';
    const shared = Math.max(0, state.window - state.duration);
    $('#timeline-relationship').textContent = shared > 0
      ? `At ${state.duration}-ms tone spacing, adjacent ${state.window}-ms observation windows share ${shared} ms of data. Each tone still receives its own prediction, so a long window does not require slower output.`
      : `At ${state.duration}-ms tone spacing, the ${state.window}-ms observation bins are separate. Underlying neural responses can still overlap across adjacent tones; short bins sample only a brief part of those responses.`;
  }

  function renderTimeline() {
    const x0 = 170, width = 805, limit = 160, scale = width / limit;
    const x = (time) => x0 + time * scale;
    // Tone selection changes the schematic frequency pattern; the central tone
    // remains at a fixed place so overlapping windows stay visible on small screens.
    const anchor = state.duration * 2;
    const windowStart = anchor + (state.window === 50 ? 10 : 25);
    const windowEnd = windowStart + state.window;
    const selectedFrequency = frequencyForTone(state.tone);
    const pieces = [
      '<title id="timeline-svg-title">Illustrative tone and neural observation timing</title>',
      `<desc id="timeline-svg-description">Synthetic timing diagram at ${state.duration} milliseconds per tone. Selected neural observation lasts ${state.window} milliseconds. Adjacent observation windows ${state.window > state.duration ? 'overlap' : 'are separate'}. Neural activity is schematic, not measured.</desc>`,
      '<defs><clipPath id="plot-clip"><rect x="170" y="12" width="805" height="253"/></clipPath></defs>'
    ];
    for (let ms = 0; ms <= limit; ms += 20) {
      pieces.push(`<line x1="${x(ms)}" y1="24" x2="${x(ms)}" y2="248" stroke="#e6ebe4" stroke-width="1"/><text x="${x(ms)}" y="272" text-anchor="middle" fill="#68766e" font-size="10">${ms}</text>`);
    }
    pieces.push('<text x="15" y="54" fill="#293c33" font-size="12" font-weight="600">Tones in the air</text><text x="15" y="71" fill="#78847d" font-size="10">Back to back</text><text x="15" y="132" fill="#293c33" font-size="12" font-weight="600">Neural activity</text><text x="15" y="149" fill="#78847d" font-size="10">Synthetic raster · 8 rows</text><text x="15" y="222" fill="#293c33" font-size="12" font-weight="600">Observation windows</text><text x="15" y="239" fill="#78847d" font-size="10">Three adjacent tones</text><text x="975" y="284" fill="#78847d" font-size="9" text-anchor="end">Time after first tone onset (ms)</text>');
    pieces.push('<g clip-path="url(#plot-clip)">');
    for (let index = 0; index * state.duration < limit; index++) {
      const start = index * state.duration;
      const isSelected = index === 2;
      const toneWidth = state.duration * scale;
      pieces.push(`<rect x="${x(start) + 1}" y="37" width="${toneWidth - 2}" height="36" rx="3" fill="${isSelected ? '#c27c4d' : '#dbe8de'}"/><text x="${x(start) + toneWidth / 2}" y="59" font-size="${state.duration < 8 ? 7 : 9}" fill="${isSelected ? '#fff' : '#3e6352'}" text-anchor="middle">${isSelected ? '●' : index + 1}</text>`);
    }
    pieces.push(`<line x1="${x(anchor)}" y1="30" x2="${x(anchor)}" y2="248" stroke="#b96634" stroke-dasharray="3 4"/><text x="${x(anchor) + 5}" y="25" fill="#a86136" font-size="10">Selected tone · ${formatFrequency(selectedFrequency)}</text>`);
    // A reproducible stylized raster. More ticks occur around successive response
    // positions, but neither amplitudes nor rates claim to reproduce physiology.
    for (let row = 0; row < 8; row++) {
      const y = 102 + row * 9;
      pieces.push(`<line x1="${x0}" y1="${y + 4}" x2="${x0 + width}" y2="${y + 4}" stroke="#f0f3ee"/>`);
      for (let ms = 1; ms < limit; ms += 2) {
        const pseudo = ((ms * 29 + row * 43 + state.tone * 17) % 101) / 101;
        const nearestResponse = Math.abs(((ms - 27 + state.duration / 2) % state.duration + state.duration) % state.duration - state.duration / 2);
        const density = nearestResponse < Math.min(4, state.duration / 3) ? .45 : .13;
        if (pseudo < density) pieces.push(`<line x1="${x(ms)}" y1="${y - 2}" x2="${x(ms)}" y2="${y + 5}" stroke="#7c9b88" stroke-width="1.2" opacity=".7"/>`);
      }
    }
    pieces.push(`<rect x="${x(windowStart)}" y="94" width="${state.window * scale}" height="80" rx="3" fill="#db9a68" opacity=".13"/>`);
    for (let neighbor = -1; neighbor <= 1; neighbor++) {
      const start = windowStart + neighbor * state.duration;
      const y = 191 + (neighbor + 1) * 16;
      const current = neighbor === 0;
      pieces.push(`<rect x="${x(start)}" y="${y}" width="${state.window * scale}" height="11" rx="2" fill="${current ? '#c27c4d' : '#d8e2d8'}" opacity="${current ? '.8' : '.85'}"/>`);
      if (current) {
        for (let bin = 5; bin < state.window; bin += 5) pieces.push(`<line x1="${x(start + bin)}" y1="${y}" x2="${x(start + bin)}" y2="${y + 11}" stroke="#fff" opacity=".7"/>`);
      }
    }
    const labelX = Math.min(x(windowEnd) + 8, x0 + width - 100);
    pieces.push(`<text x="${labelX}" y="216" fill="#a86136" font-size="10">${state.window} ms observed</text></g>`);
    $('#timeline').innerHTML = pieces.join('');
  }

  function advance() {
    state.stage = (state.stage + 1) % details.length;
    if (state.stage === 0) {
      state.tone = (state.tone + 1) % sequenceIndices.length;
      renderSequence();
      renderTimeline();
    }
    renderStage();
  }

  function setPlaying(playing) {
    state.playing = playing;
    clearInterval(timer);
    timer = playing ? setInterval(advance, reducedMotion.matches ? 1500 : 1000) : null;
    $('#play-button').innerHTML = playing ? '<span aria-hidden="true">Ⅱ</span> Pause' : '<span aria-hidden="true">▶</span> Play';
    $('#play-button').setAttribute('aria-pressed', String(playing));
  }

  function renderResults() {
    const c = model.results.C.sessions, e = model.results.E.sessions;
    $('#results-chart').innerHTML = c.map((value, index) => `<div class="chart-group"><span class="chart-session">Session ${index + 2}</span><div class="bar-pair"><div class="result-bar" style="width:${value / 250 * 100}%" title="Sheep C, Session ${index + 2}: ${value} bits/s">${value.toFixed(1)}</div><div class="result-bar e" style="width:${e[index] / 250 * 100}%" title="Sheep E, Session ${index + 2}: ${e[index]} bits/s">${e[index].toFixed(1)}</div></div></div>`).join('');
  }

  $$('.nav-tab').forEach((button) => button.addEventListener('click', () => switchView(button.dataset.view)));
  $$('[data-component]').forEach((button) => button.addEventListener('click', () => selectComponent(button.dataset.component)));
  $$('[data-go-view]').forEach((button) => button.addEventListener('click', () => {
    switchView(button.dataset.goView, true);
    window.scrollTo({ top: 0, behavior: reducedMotion.matches ? 'auto' : 'smooth' });
  }));
  $$('.stage').forEach((button) => button.addEventListener('click', () => {
    setPlaying(false);
    state.stage = Number(button.dataset.stage);
    renderStage();
  }));
  $('#duration').addEventListener('input', (event) => {
    state.duration = Number(event.target.value);
    renderControls();
    renderTimeline();
  });
  $$('[data-alphabet]').forEach((button) => button.addEventListener('click', () => {
    state.alphabet = button.dataset.alphabet;
    renderControls();
    renderSequence();
    renderTimeline();
  }));
  $$('[data-window]').forEach((button) => button.addEventListener('click', () => {
    state.window = Number(button.dataset.window);
    renderControls();
    renderTimeline();
  }));
  $('#play-button').addEventListener('click', () => setPlaying(!state.playing));
  $('#next-button').addEventListener('click', () => { setPlaying(false); advance(); });
  $('#paper-walkthrough').addEventListener('toggle', (event) => {
    if (!event.target.open) setPlaying(false);
  });
  window.addEventListener('hashchange', () => switchView(location.hash.slice(1)));
  document.addEventListener('visibilitychange', () => { if (document.hidden) setPlaying(false); });
  renderControls();
  renderSequence();
  renderStage();
  renderTimeline();
  renderResults();
  switchView(location.hash.slice(1) || 'setup');
})();
