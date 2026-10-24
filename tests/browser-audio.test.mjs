/** Offline DSP, worklet protocol and connection lifecycle checks.
 * This file uses synthetic arrays and mock Web Audio classes. It never opens
 * real audio hardware and its synthetic numbers are not experimental results. */
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
import {BrowserBench, E14_FREQUENCIES, raisedCosineEnvelope, makeSonicBlock, makeProbePlan, normalizedCorrelations, analyzeLag, analyzeCapture, assessCaptureChunks, wavBlob} from '../web/bench/audio.mjs';
const near = (a,b,epsilon=1e-8) => assert.ok(Math.abs(a-b) <= epsilon, `${a} ≠ ${b}`);
const shift = (values, samples, scale=1) => { const shifted = new Float32Array(values.length); for (let i=samples; i<shifted.length; i++) shifted[i]=values[i-samples]*scale; return shifted; };
const plan = makeProbePlan({repetitions:3});
const transport = {valid:true,errors:[],input_channel_minimum:2};

test('import and constructor never access microphone or create audio', () => {
  const bench = new BrowserBench(); assert.equal(bench.status().phase,'idle'); assert.equal(bench.context,null); assert.equal(bench.lastResult,null);
});
test('E14 pips use the documented frequencies, exact duration/ramp endpoints, balanced reproducible sequence and separate browser PRNG', () => {
  const a=makeSonicBlock({tonesPerFrequency:2}), b=makeSonicBlock({tonesPerFrequency:2});
  assert.deepEqual(a.waveform,b.waveform); assert.deepEqual(a.metadata.events,b.metadata.events);
  assert.equal(a.metadata.events.length,28); assert.equal(a.waveform.length,218880);
  assert.equal(a.metadata.tone_duration_samples,960); assert.equal(a.metadata.ramp_samples_each_end,192);
  const counts=new Map(); for (const e of a.metadata.events) { counts.set(e.frequency_hz,(counts.get(e.frequency_hz)||0)+1); near(a.waveform[e.output_start],0); near(a.waveform[e.output_stop-1],0); }
  for(const f of E14_FREQUENCIES) assert.equal(counts.get(f),2);
  assert.match(a.metadata.random_bit_generator,/Mulberry32/); assert.match(a.metadata.random_bit_generator,/PCG64/);
  assert.equal(a.metadata.exact_original_waveform,false); assert.equal(a.metadata.leading_silence_samples,96000);
  const env=raisedCosineEnvelope(960,192); assert.equal(env[0],0); assert.equal(env[191],1); assert.equal(env[959],0); assert.equal(env[768],1);
  let peak=0;for(const x of a.waveform)peak=Math.max(peak,Math.abs(x)); assert.ok(peak <= 10**(-36/20)+1e-8);
});
test('full block has 8,400 pips and 84 active seconds; quick block is explicitly shorter', () => {
  const full=makeSonicBlock(); assert.equal(full.metadata.tone_count,8400);assert.equal(full.metadata.active_duration_seconds,84);assert.equal(full.metadata.duration_seconds,86);assert.equal(full.metadata.within_published_block_tone_count_range,true);
  const quick=makeSonicBlock({tonesPerFrequency:50});assert.equal(quick.metadata.active_duration_seconds,7);assert.equal(quick.metadata.within_published_block_tone_count_range,false);
});
test('rejects unsupported E14 graph rate, invalid level/count/seed and nonintegral timing', () => {
  assert.throws(()=>makeSonicBlock({sampleRate:48000}),/96 kHz/);assert.throws(()=>makeSonicBlock({sampleRate:100001}),/exact 10 ms/);
  assert.throws(()=>makeSonicBlock({peakDbfs:-10}),/−60/);assert.throws(()=>makeSonicBlock({tonesPerFrequency:0}),/integer/);assert.throws(()=>makeSonicBlock({seed:-1}),/Seed/);
});
test('timing chirps are distinct from SONIC and retain one-second pads',()=>{
  assert.equal(plan.metadata.sonic_stimulus,false);assert.equal(plan.metadata.trials[0].output_start,96000);assert.equal(plan.metadata.trials[1].output_start-plan.metadata.trials[0].output_start,48000);
  assert.equal(plan.waveform[96000],0);assert.equal(plan.waveform[105599],0);assert.equal(plan.waveform.length,297600);
});
test('FFT normalized correlations agree with direct Pearson calculation',()=>{
  const reference=Float32Array.from({length:31},(_,i)=>Math.sin(i*i*.37)+.3*Math.cos(i*.91));
  const signal=Float32Array.from({length:53},(_,i)=>Math.sin(i*i*.71)+.1*i);
  const actual=normalizedCorrelations(reference,signal), rm=reference.reduce((a,b)=>a+b)/reference.length;
  for(let lag=0;lag<actual.length;lag++){const window=signal.subarray(lag,lag+reference.length),wm=window.reduce((a,b)=>a+b)/window.length;let num=0,re=0,we=0;for(let i=0;i<reference.length;i++){const a=reference[i]-rm,b=window[i]-wm;num+=a*b;re+=a*a;we+=b*b;}near(actual[lag],num/Math.sqrt(re*we),1e-10);}
});
test('correlation identifies integer lag and inverted polarity without wall-clock timing',()=>{
  const ref=plan.waveform.subarray(96000,105600), signal=new Float32Array(ref.length+24000);signal.set(ref,4567);
  let result=analyzeLag(ref,signal,96000);assert.equal(result.accepted,true);assert.equal(result.delay_samples,4567);near(result.peak_correlation,1,1e-7);
  for(let i=0;i<signal.length;i++)signal[i]*=-1;result=analyzeLag(ref,signal,96000);assert.equal(result.accepted,true);assert.equal(result.delay_samples,4567);near(result.peak_correlation,-1,1e-7);
});
test('rejects silence, clipping, weak noise, competing echoes and search boundaries',()=>{
  const ref=plan.waveform.subarray(96000,105600), empty=new Float32Array(ref.length+24000);
  assert.equal(analyzeLag(ref,empty,96000).candidate_delay_ms,null);
  const boundary=empty.slice();boundary.set(ref);assert.ok(analyzeLag(ref,boundary,96000).reasons.includes('boundary_peak_unresolved'));
  const echo=empty.slice();echo.set(ref,2000);for(let i=0;i<ref.length;i++)echo[13000+i]+=ref[i];assert.ok(analyzeLag(ref,echo,96000).reasons.includes('ambiguous_peak'));
  const clip=empty.slice();clip.set(ref,2000);clip[2200]=1;assert.ok(analyzeLag(ref,clip,96000).reasons.includes('microphone_clipping'));
  let seed=17;const noise=Float32Array.from(empty,()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed/2**32-.5)*.01;});assert.ok(analyzeLag(ref,noise,96000).reasons.includes('weak_correlation'));
});
test('roundtrip has actual array-derived delay; unknown processing and transport suppress all accepted delays',()=>{
  const microphone=shift(plan.waveform,1500,.4);
  const args={source:plan.waveform,microphone,sampleRate:96000,stimulus:plan.metadata,transport,processingVerified:true,inputChannels:2};
  const accepted=analyzeCapture(args);assert.equal(accepted.usable_measurement,true);assert.equal(accepted.summary.accepted_trials,3);near(accepted.summary.median_delay_ms,15.625);
  const unknown=analyzeCapture({...args,processingVerified:false});assert.equal(unknown.usable_measurement,false);assert.equal(unknown.status,'diagnostic_only');assert.equal(unknown.summary.median_delay_ms,null);assert.equal(unknown.trials[0].delay_ms,null);near(unknown.diagnostic_candidate_summary.median_delay_ms,15.625);
  const gaps=analyzeCapture({...args,transport:{...transport,valid:false,errors:['worklet_process_frame_gap']}});assert.equal(gaps.usable_measurement,false);assert.equal(gaps.summary.accepted_trials,0);
});
test('electrical method locates actual recorded reference rather than treating source coordinates as ADC onset',()=>{
  const result=analyzeCapture({source:plan.waveform,microphone:shift(plan.waveform,2700,.2),reference:shift(plan.waveform,900,.8),sampleRate:96000,stimulus:plan.metadata,transport,processingVerified:true,inputChannels:2,requireReference:true});
  assert.equal(result.usable_measurement,true);near(result.summary.median_delay_ms,18.75);assert.equal(result.trials[0].recorded_reference_start_sample,96900);assert.equal(result.trials[0].reference_alignment.delay_samples,900);
  const mono=analyzeCapture({source:plan.waveform,microphone:shift(plan.waveform,2700,.2),reference:shift(plan.waveform,900,.8),sampleRate:96000,stimulus:plan.metadata,transport:{...transport,input_channel_minimum:1},processingVerified:true,inputChannels:1,requireReference:true});
  assert.equal(mono.usable_measurement,false);assert.equal(mono.summary.median_delay_ms,null);
});
test('first-probe anchor prevents 600-ms delays aliasing to 100 ms across 500-ms repeats',()=>{
  const ten=makeProbePlan({repetitions:10});
  const result=analyzeCapture({source:ten.waveform,microphone:shift(ten.waveform,57600,.5),sampleRate:96000,stimulus:ten.metadata,transport,processingVerified:true,inputChannels:2});
  assert.equal(result.first_probe_anchor_accepted,false);assert.equal(result.usable_measurement,false);assert.equal(result.summary.median_delay_ms,null);assert.equal(result.diagnostic_candidate_summary.accepted_trials,9);
});
test('80-percent and three-trial rule rejects too many quiet trials',()=>{
  const ten=makeProbePlan({repetitions:10}),mic=shift(ten.waveform,1234,.5);
  for(const t of ten.metadata.trials.slice(7))mic.fill(0,t.output_start,Math.min(mic.length,t.output_stop+24000));
  const result=analyzeCapture({source:ten.waveform,microphone:mic,sampleRate:96000,stimulus:ten.metadata,transport,processingVerified:true,inputChannels:2});
  assert.equal(result.minimum_accepted_trials,8);assert.equal(result.usable_measurement,false);assert.equal(result.summary.median_delay_ms,null);
});
test('float32 WAV channels interleave correctly and preserve declared graph rate',async()=>{
  const blob=wavBlob([Float32Array.of(.25,-.5),Float32Array.of(.75,0)],96000),v=new DataView(await blob.arrayBuffer());
  assert.equal(v.getUint16(20,true),3);assert.equal(v.getUint16(22,true),2);assert.equal(v.getUint32(24,true),96000);near(v.getFloat32(44,true),.25);near(v.getFloat32(48,true),.75);near(v.getFloat32(52,true),-.5);
});

test('worklet protocol keeps output/capture on one frame grid, zeroes other channels and stops promptly',async()=>{
  let Processor;
  const sandbox={AudioWorkletProcessor:class{constructor(){this.port={messages:[],postMessage(message){this.messages.push(message);}};}},registerProcessor(_name,klass){Processor=klass;},Float32Array,Math,Number,sampleRate:96000,currentFrame:2048};
  vm.createContext(sandbox);new vm.Script(await readFile(new URL('../web/bench/processor.js',import.meta.url),'utf8')).runInContext(sandbox);
  const p=new Processor(), source=Float32Array.from({length:300},(_,i)=>i/1000),out=[new Float32Array(128),new Float32Array(128)];
  p.process([[new Float32Array(128).fill(.5)]],[out]);assert.ok(out.every(c=>c.every(x=>x===0)));assert.equal(p.port.messages[0].type,'input-ready');
  p.port.onmessage({data:{type:'start',id:7,source:source.buffer,capture:true,inputChannel:1,referenceChannel:2,outputChannel:1,referenceOutputChannel:2}});
  for(let block=0;block<3;block++){sandbox.currentFrame=2048+128*block;p.process([[new Float32Array(128).fill(.25),new Float32Array(128).fill(.75)]],[out]);for(let i=0;i<128;i++){const expected=block*128+i<300?source[block*128+i]:0;near(out[0][i],expected);near(out[1][i],expected);}}
  const done=p.port.messages.find(m=>m.type==='done'),chunks=p.port.messages.filter(m=>m.type==='capture');
  const capture=assessCaptureChunks(chunks,300,2048,done);assert.equal(capture.valid,true);assert.equal(capture.input_channel_minimum,2);assert.ok(capture.microphone.every(x=>x===.25));assert.ok(capture.reference.every(x=>x===.75));
  const broken=assessCaptureChunks([{...chunks[0],frame:2049}],300,2048,done);assert.equal(broken.valid,false);assert.ok(broken.errors.includes('capture_frame_gap_or_overlap'));
  p.port.onmessage({data:{type:'start',id:8,source:source.buffer,capture:false,inputChannel:1,referenceChannel:null,outputChannel:1,referenceOutputChannel:null}});p.port.onmessage({data:{type:'stop'}});p.process([[]],[out]);assert.ok(out.every(c=>c.every(x=>x===0)));
});

// Browser API mocks below cannot touch physical input/output devices.
async function withBrowserMocks(callback,{deferredPermission=false,graphRate=96000,settings={}}={}) {
  const names=['navigator','AudioContext','AudioWorkletNode','isSecureContext'], old=new Map(names.map(n=>[n,Object.getOwnPropertyDescriptor(globalThis,n)]));
  const state={contexts:[],tracks:[],constraints:[],resolvePermission:null,nodes:[]};
  const makeStream=()=>{const track={stopped:false,getSettings(){return {echoCancellation:false,noiseSuppression:false,autoGainControl:false,channelCount:2,sampleRate:graphRate,...settings};},stop(){this.stopped=true;}};state.tracks.push(track);return {getTracks:()=>[track],getAudioTracks:()=>[track]};};
  class AudioMock {
    constructor(){this.sampleRate=graphRate;this.state='suspended';this.destination={maxChannelCount:2};this.audioWorklet={addModule:async()=>{}};this.baseLatency=.01;state.contexts.push(this);}
    resume(){this.state='running';return Promise.resolve();}close(){this.state='closed';return Promise.resolve();}
    setSinkId(id){this.sinkId=id;return Promise.resolve();}
    createMediaStreamSource(){return {connect(node){queueMicrotask(()=>node.port.onmessage?.({data:{type:'input-ready',channels:2}}));},disconnect(){}};}
  }
  class WorkletMock {constructor(_context,_name,options){this.options=options;this.messages=[];this.port={postMessage:m=>this.messages.push(m),close(){}};state.nodes.push(this);}connect(){}disconnect(){this.disconnected=true;}}
  Object.defineProperty(globalThis,'navigator',{configurable:true,value:{userAgent:'offline-mock',mediaDevices:{getUserMedia:async c=>{state.constraints.push(c);if(deferredPermission)return await new Promise(resolve=>{state.resolvePermission=()=>resolve(makeStream());});return makeStream();},enumerateDevices:async()=>[{kind:'audioinput',deviceId:'input-A',groupId:'same-interface',label:'Input A'},{kind:'audiooutput',deviceId:'output-A',groupId:'same-interface',label:'Output A'}]}}});
  Object.defineProperty(globalThis,'AudioContext',{configurable:true,value:AudioMock});Object.defineProperty(globalThis,'AudioWorkletNode',{configurable:true,value:WorkletMock});Object.defineProperty(globalThis,'isSecureContext',{configurable:true,value:true});
  try {await callback(state);} finally {for(const name of names){if(old.get(name))Object.defineProperty(globalThis,name,old.get(name));else delete globalThis[name];}}
}
test('connect explicitly requests raw input, waits for actual input channels, reports graph/track rates and releases on stop',async()=>{
  await withBrowserMocks(async state=>{const bench=new BrowserBench(),devices=await bench.devices();assert.equal(devices.length,2);await bench.connect({inputDeviceId:'input-A',outputDeviceId:'output-A'});
    assert.equal(state.constraints[0].audio.echoCancellation,false);assert.equal(state.constraints[0].audio.noiseSuppression,false);assert.equal(state.constraints[0].audio.autoGainControl,false);assert.deepEqual(state.constraints[0].audio.deviceId,{exact:'input-A'});
    assert.equal(bench.status().connection.processingVerified,true);assert.equal(bench.status().connection.observedInputChannels,2);assert.equal(bench.status().connection.sampleRate,96000);assert.equal(bench.status().connection.hardwareClockVerified,false);
    assert.equal(state.nodes[0].options.channelCountMode,'max');assert.equal(state.nodes[0].options.channelInterpretation,'discrete');assert.equal(state.contexts[0].sinkId,'output-A');
    bench.stop();assert.equal(state.contexts[0].state,'closed');assert.ok(state.tracks.every(t=>t.stopped));assert.equal(bench.status().connected,false);
  });
});
test('stop cancels a pending connect and later permission completion cannot reopen audio',async()=>{
  await withBrowserMocks(async state=>{const bench=new BrowserBench(),connecting=bench.connect();bench.stop();assert.equal(bench.status().phase,'idle');state.resolvePermission();await assert.rejects(connecting,{name:'AbortError'});assert.ok(state.tracks.every(t=>t.stopped));assert.ok(state.contexts.every(c=>c.state==='closed'));assert.equal(bench.status().connected,false);},{deferredPermission:true});
});
test('processing flags are accepted only if explicitly false; lower context rate blocks E14',async()=>{
  await withBrowserMocks(async state=>{const bench=new BrowserBench();await bench.connect();assert.equal(bench.status().connection.processingVerified,false);assert.ok(bench.status().warnings.some(w=>/unverifiable/.test(w)));await assert.rejects(bench.play({tonesPerFrequency:1}),/96 kHz/);assert.ok(!state.nodes[0].messages.some(m=>m.type==='start'));bench.disconnect();},{graphRate:48000,settings:{autoGainControl:undefined}});
});
test('stalled worklet watchdog rejects and releases devices without a fabricated result',async()=>{
  await withBrowserMocks(async state=>{const bench=new BrowserBench();await bench.connect();const originalTimer=globalThis.setTimeout;globalThis.setTimeout=(callback,ms,...args)=>originalTimer(callback,ms>10000?1:ms,...args);
    try{await assert.rejects(bench.play({tonesPerFrequency:1}),/timed out/);assert.equal(bench.lastResult,null);assert.equal(bench.status().connected,false);assert.ok(state.tracks.every(t=>t.stopped));}finally{globalThis.setTimeout=originalTimer;bench.stop();}
  });
});

test('playback completes only with a contiguous full worklet frame range; known gaps and incomplete ends release devices',async()=>{
  for (const fault of [null,'gap','end','frames']) {
    await withBrowserMocks(async state=>{
      const bench=new BrowserBench();await bench.connect();const node=state.nodes[0];
      node.port.postMessage=message=>{
        node.messages.push(message);if(message.type!=='start')return;
        const frames=new Float32Array(message.source).length,firstFrame=4096;
        queueMicrotask(()=>{
          node.port.onmessage({data:{type:'started',id:message.id,frame:firstFrame}});
          node.port.onmessage({data:{type:'done',id:message.id,frames:fault==='frames'?frames-128:frames,
            firstFrame,endFrame:firstFrame+frames+(fault==='end'?128:0),processGaps:fault==='gap'?1:0,
            chunks:0,inputChannelMin:null,inputMissingFrames:0}});
        });
      };
      if(fault){await assert.rejects(bench.play({tonesPerFrequency:1}),/missing or inconsistent audio frames/);assert.equal(bench.lastResult,null);assert.equal(bench.status().connected,false);assert.ok(state.tracks.every(t=>t.stopped));}
      else{const result=await bench.play({tonesPerFrequency:1});assert.equal(result.completed,true);assert.equal(result.transport.worklet_end_frame-result.transport.worklet_first_frame,result.sample_count);assert.equal(bench.lastResult,result);assert.equal(bench.status().phase,'ready');bench.disconnect();}
    });
  }
});
