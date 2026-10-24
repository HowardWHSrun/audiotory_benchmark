/* Local-only UI fixture server. No microphone or audio APIs are opened.
 * node tests/browser-bench-fixture.cjs [port]
 * All numbers are synthetic UI fixtures, never experimental results.
 * Production pages import the real audio.mjs; only this test server substitutes it.
 */
'use strict';
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../web/bench');
const events = [];
let fixtureMode = 'pass';
const fixture = `
export class BrowserBench {
  constructor({onStatus}) { this.onStatus=onStatus; this.phase='idle';this.connection=null;this.progress=0;this.warnings=[];this._pending=null; }
  get capabilities(){return {secureContext:true,audioWorklet:true,mediaDevices:true,outputSelection:true};}
  status(){return {phase:this.phase,message:'MOCK UI TEST ONLY — no audio hardware',progress:this.progress,connected:!!this.connection,connection:this.connection,warnings:this.warnings,capabilities:this.capabilities};}
  emit(phase){this.phase=phase;this.onStatus(this.status());}
  async log(action,options={}) {await fetch('/__fixture/event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action,options})});}
  async devices(){return [{kind:'audioinput',deviceId:'mock-input',label:'MOCK UI TEST interface input'},{kind:'audiooutput',deviceId:'mock-output',label:'MOCK UI TEST interface output'}];}
  async connect(options){await this.log('connect',options);this.emit('connecting');await new Promise(r=>setTimeout(r,80));const mode=await (await fetch('/__fixture/mode')).text();
    this.connection={...options,sampleRate:mode==='rate48'?48000:options.sampleRate,requestedSampleRate:options.sampleRate,inputSettings:{sampleRate:96000,channelCount:2,echoCancellation:false,noiseSuppression:false,autoGainControl:false},inputChannels:2,observedInputChannels:2,outputChannels:2,processingVerified:true,baseLatency:0.01,outputSelectionSupported:true};this.emit('ready');return this.status();}
  async _run(kind,options){await this.log(kind,options);const initialMode=await (await fetch('/__fixture/mode')).text();this.lastResult=null;this.progress=0.25;this.emit(kind==='play'?'playing':'calibrating');
    return new Promise((resolve,reject)=>{this._pending={reject,timer:setTimeout(async()=>{this._pending=null;const mode=await (await fetch('/__fixture/mode')).text();
      const pass=mode==='pass';const result=kind==='play'?{kind:'sonic_e14_reconstruction',completed:true,tone_count:options.tonesPerFrequency*14,active_duration_seconds:options.tonesPerFrequency*.14,fixture:true}:{kind:'browser_delay_screen',status:pass?'screening_pass':'diagnostic_only',usable_measurement:pass,summary:{median_delay_ms:pass?12.34:null,accepted_trials:pass?10:0,total_trials:10,jitter_p95_minus_p05_ms:pass?0.04:null},diagnostic_candidate_summary:{median_delay_ms:12.34},transport:{valid:pass,errors:pass?[]:['browser_input_processing_not_verified_off']},trials:[],interpretation:'MOCK UI TEST fixture — never measured data',fixture:true};
      this.lastResult=result;this.lastSourceWav=new Blob(['mock-source'],{type:'audio/wav'});this.lastCaptureWav=kind==='calibrate'?new Blob(['mock-capture'],{type:'audio/wav'}):null;this.progress=1;this.emit('ready');resolve(result);},initialMode==='slow'?30000:1200)};});}
  play(options){return this._run('play',options);}
  calibrate(options){return this._run('calibrate',options);}
  stop(){this.log('stop');if(this._pending){clearTimeout(this._pending.timer);const error=new Error('Stopped mock run');error.name='AbortError';this._pending.reject(error);this._pending=null;}this.connection=null;this.emit('idle');}
  disconnect(){this.log('disconnect');this.stop();}
}`;
const server = http.createServer((req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.url === '/__fixture/event' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => { events.push(JSON.parse(body)); res.end('ok'); });
    return;
  }
  if (req.url === '/__fixture/events') { res.setHeader('Content-Type','application/json'); return res.end(JSON.stringify(events)); }
  if (req.url.startsWith('/__fixture/mode')) {
    if (req.url.includes('?')) fixtureMode = new URL(req.url, 'http://localhost').searchParams.get('value') || 'pass';
    return res.end(fixtureMode);
  }
  if (req.url === '/audio.mjs') { res.setHeader('Content-Type','text/javascript'); return res.end(fixture); }
  const names = {'/':'index.html','/index.html':'index.html','/app.mjs':'app.mjs','/styles.css':'styles.css'};
  const name = names[req.url?.split('#')[0]];
  if (!name) { res.writeHead(404); return res.end('Not a fixture resource'); }
  res.setHeader('Content-Type',name.endsWith('.html')?'text/html':name.endsWith('.css')?'text/css':'text/javascript');
  res.end(fs.readFileSync(path.join(root,name)));
});
server.listen(Number(process.argv[2] || 8891),'127.0.0.1',()=>process.stdout.write(`Mock UI only: http://127.0.0.1:${server.address().port}/\n`));
