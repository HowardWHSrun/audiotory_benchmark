const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const read = (name) => JSON.parse(fs.readFileSync(path.join(root,name),'utf8'));
const context = {window:{}};
vm.runInNewContext(fs.readFileSync(path.join(root,'web/parts-data.js'),'utf8'),context);
const data = context.window.AuditoryPartsData;
const cents = (n) => Math.round(n*100);
const sum = (items) => items.reduce((s,p)=>s+cents(p.price),0);

test('presentation baskets reconcile quantities, estimates and line totals',()=>{
  for(const [key,option] of Object.entries(data.options)) {
    assert.equal(new Set(option.items.map(p=>p.id)).size,option.items.length,`${key}: duplicate line`);
    for(const p of option.items) {
      assert.equal(cents(p.unitPrice)*p.qty,cents(p.price),`${key}/${p.id}: unit vs line cost`);
      assert.ok(['observed','estimate'].includes(p.kind));
      assert.match(p.url,/^https:\/\//);
      assert.match(p.observedDate,/^2026-10-\d\d$/);
    }
    assert.equal(sum(option.items),cents(option.total),`${key}: total`);
    assert.equal(sum(option.items.filter(p=>p.kind==='estimate')),cents(option.estimate),`${key}: estimates`);
    assert.equal(sum(option.items.filter(p=>p.kind==='observed')),cents(option.observed),`${key}: observations`);
    if(key!=='basic') assert.equal(sum(option.items.filter(p=>p.group==='measurement')),cents(data.sharedMeasurementKitTotal),`${key}: shared kit once`);
  }
});

test('Basic uses the October 15 source and preserves the borrowed-reference scenario',()=>{
  const source=read('sources/Audio_Setup_Budget_Precision_2026-10-15.json').basic_current_basket;
  for(const p of source.items) {
    const row=data.options.basic.items.find(r=>r.url===p.url);
    assert.ok(row,`${p.item}: source item missing`);
    assert.equal(row.qty,p.quantity);
    assert.equal(cents(row.unitPrice),cents(p.unit_usd));
  }
  assert.equal(cents(data.options.basic.total),cents(source.subtotal_purchased_calibrator_usd));
  const calibrator=data.options.basic.items.find(p=>p.id==='r8090');
  assert.equal(cents(data.options.basic.total)-cents(calibrator.price),cents(source.subtotal_borrowed_calibrator_usd));
});

test('specialized budgets and new candidates match their separate source records',()=>{
  const source=read('sources/Planning_Estimates_2026-10-10.json');
  for(const [key,sourceKey] of Object.entries({compact:'Compact',mcginley:'McGinley',sonic:'SONIC'})) assert.equal(cents(data.options[key].total),cents(source.parts_totals[sourceKey]));
  const speaker=read('sources/Consumer_Ultrasonic_Speakers_2026-10-15.json').candidates.find(p=>p.model==='Edifier MR3');
  const mic=read('sources/Microphone_32kHz_NI_Comparison_2026-10-15.json').microphones.find(p=>p.model.includes('OmniMic'));
  assert.equal(cents(data.candidates.items[0].price),cents(speaker.observed_price.amount));
  assert.equal(cents(data.candidates.items[1].price),cents(mic.observed_price_usd));
  assert.equal(sum(data.candidates.items),cents(data.candidates.subtotal));
  assert.match(data.candidates.scope,/not a complete setup budget/);
});

test('every reference photo has a source and exists locally',()=>{
  const photos=read('web/assets/parts/sources.json').sources;
  assert.equal(new Set(photos.map(p=>p.file)).size,photos.length);
  for(const p of photos) {
    assert.match(p.source_page,/^https:\/\//);
    assert.match(p.image_url,/^https:\/\//);
    assert.ok(fs.statSync(path.join(root,'web/assets/parts',p.file)).size>1000,p.file);
  }
});
