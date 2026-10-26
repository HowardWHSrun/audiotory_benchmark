'use strict';
(() => {
  const svg = document.getElementById('diagram');
  const NS = 'http://www.w3.org/2000/svg';
  const ui = {title:document.getElementById('view-title'), kicker:document.getElementById('view-kicker'), fn:document.getElementById('function'), sources:document.getElementById('sources')};
  const A = '<a href="https://d9w4fhj63j193.cloudfront.net/2021/iD14MKII/English/iD14%20MKII%20Manual%20V1.3.pdf#page=47" target="_blank" rel="noopener noreferrer">Audient manual</a>';
  const M = '<a href="https://audient.github.io/audient-documentation-site/id14/system-panel-routing/" target="_blank" rel="noopener noreferrer">Audient mixer routing</a>';
  const S = '<a href="https://spikegadgets.com/wp-content/uploads/2020/02/Control-units-manual.pdf" target="_blank" rel="noopener noreferrer">SpikeGadgets control units</a>';
  const E = '<a href="https://spikegadgets.com/downloads/ECUManual.pdf" target="_blank" rel="noopener noreferrer">ECU manual</a>';
  const H = '<a href="https://hosatech.com/products/analog-audio/stereo-breakouts/hosa-breakouts/ypp-117/" target="_blank" rel="noopener noreferrer">Hosa YPP-117</a>';
  const P = '<a href="https://www.pomonaelectronics.com/products/adapters/coaxial/bnc-f-14-in-phone-plug" target="_blank" rel="noopener noreferrer">Pomona 1297</a>';
  const B = '<a href="https://www.datapro.net/products/sma-to-bnc-antenna-cable.html" target="_blank" rel="noopener noreferrer">BNC-to-SMA cable example</a>';
  const data={
    overview:['01 / THE COMPLETE PATH','The whole setup','Play a stimulus, record the microphone on the ECU, and acquire neural data on the MCU.',`${A}; ${S}; ${E}. Port drawings represent manufacturer layouts; cable and headstage details remain to be confirmed on your units.`],
    sound:['02 / SOUND CHAIN','Sound & microphone','The computer plays through the iD14 and speakers. The M50 listens and enters Mic/Line 1 over XLR.',`${A}; ${M}. Enable 48 V for microphone input 1. Speaker port placement is not independently verified.`],
    analog:['03 / PROPOSED MICROPHONE FEED','iD14 to ECU','Route microphone input 1 to Cue A left and output 3L, then carry that analog signal to ECU Ain1.',`${A}; ${M}; ${E}. The dashed adapter path is proposed and has not been connected or tested.`],
    control:['04 / RECORDING CONNECTION','ECU to MCU','The ECU and neural headstage use two different sockets on the MCU.',`${S}; ${E}. The headstage may require an HCU or active commutator before the MCU; confirm the exact model.`],
    adapter:['05 / CONNECTOR DETAIL','Proposed adapter','Hosa: ¼-inch TRS male → two ¼-inch TS female sockets. Connect only the left / tip socket to the Pomona ¼-inch TS male → BNC female adapter, then use a BNC male → SMA male cable to ECU Ain1. Leave the right / ring socket open.',`${H}; ${P}; ${B}; ${E}. Verify ECU center/shell, impedance, continuity and levels with the manufacturer before use.`]
  };
  const ELEM=(name,attrs={},parent=svg)=>{const n=document.createElementNS(NS,name);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v)));parent.appendChild(n);return n;};
  const text=(x,y,content,cls='small',anchor='middle')=>{const n=ELEM('text',{x,y,'text-anchor':anchor,class:cls});n.textContent=content;return n;};
  const line=(path,proposed=false)=>{ELEM('path',{d:path,class:proposed?'wire-shell proposed':'wire-shell'});ELEM('path',{d:path,class:proposed?'wire proposed':'wire'});};
  // Lead each cable to the socket itself, then offset it clear of the printed port label.
  const out=(port,dx)=>`M ${port.x} ${port.cy+8} v 8 h ${dx} V ${port.bottom}`;
  const box=(x,y,w,h,label,sub,kind='unit')=>{ELEM('rect',{x,y,width:w,height:h,rx:8,class:kind});text(x+w/2,y+22,label,'node-label');if(sub)text(x+w/2,y+40,sub,'node-sub');};
  const name=(x,y,title,side)=>{text(x,y,title,'device-title','start');text(x,y+16,side,'device-sub','start');};
  const ports={
    id14:[['USB','usb'],['OPT','wide'],['4R','jack'],['3L','jack'],['2R','jack'],['1L','jack'],['MIC 2','xlr'],['MIC 1','xlr']],
    ecuFront:[['AUDIO','jack'],['AIN1','sma'],['AOUT1','sma'],['DIN1','sma'],['DIN2','sma'],['DIN3','sma'],['DIN4','sma'],['DOUT1','sma'],['DOUT2','sma'],['DOUT3','sma'],['DOUT4','sma'],['POWER','power']],
    ecuRear:[['5V','power'],['DIGITAL','wide'],['ANALOG','wide'],['SD','usb'],['MCU','hdmi']],
    mcu:[['5V','power'],['ETHERNET','wide'],['GND','power'],['D I/O','wide'],['ECU','hdmi'],['HEADSTAGE','hdmi']]
  };
  function panel(x,y,w,type,focus=[]){
    ELEM('rect',{x,y,width:w,height:76,rx:5,class:'panel'});
    ELEM('path',{d:`M ${x+5} ${y+7} H ${x+w-5}`,class:'bevel'});
    [x+5,x+w-5].forEach(sx=>{ELEM('circle',{cx:sx,cy:y+70,r:2,class:'screw'});});
    const p={};
    ports[type].forEach(([label,shape],i)=>{
      const cx=x+w*(i+.5)/ports[type].length, cy=y+29, selected=focus.includes(label), c=selected?'socket chosen':'socket';
      p[label]={x:cx,y, bottom:y+76,cy};
      if(shape==='hdmi'){
        ELEM('path',{d:`M ${cx-9} ${cy-7} H ${cx+9} V ${cy+2} L ${cx+6} ${cy+7} H ${cx-6} L ${cx-9} ${cy+2} Z`,class:c});
        ELEM('path',{d:`M ${cx-6} ${cy-4} H ${cx+6}`,class:'metal-detail'});
      } else if(['usb','wide'].includes(shape)){
        ELEM('rect',{x:cx-(shape==='wide'?11:8),y:cy-7,width:shape==='wide'?22:16,height:14,rx:2,class:c});
        ELEM('path',{d:`M ${cx-5} ${cy+2} H ${cx+5}`,class:'metal-detail'});
      } else if(shape==='xlr'){
        ELEM('circle',{cx,cy,r:11,class:'socket-rim'});ELEM('circle',{cx,cy,r:8.5,class:c});
        [[-3,-3],[3,-3],[0,3.5]].forEach(([dx,dy])=>ELEM('circle',{cx:cx+dx,cy:cy+dy,r:1.5,class:'pin'}));
      } else if(shape==='sma'){
        ELEM('path',{d:`M ${cx-6} ${cy-3} L ${cx-3.5} ${cy-6} H ${cx+3.5} L ${cx+6} ${cy-3} V ${cy+3} L ${cx+3.5} ${cy+6} H ${cx-3.5} L ${cx-6} ${cy+3} Z`,class:'sma-nut'});
        ELEM('circle',{cx,cy,r:3.5,class:c});ELEM('circle',{cx,cy,r:1,class:'pin'});
      } else {
        ELEM('circle',{cx,cy,r:9,class:'socket-rim'});ELEM('circle',{cx,cy,r:5.5,class:c});
      }
      let short=type==='ecuFront'&&w<520?['AUD','AIN1','AO','D1','D2','D3','D4','O1','O2','O3','O4','PWR'][i]:label;
      if(type==='ecuFront'&&w<360) short=({1:'AIN1',4:'DIN 1–4',9:'DOUT 1–4'})[i] || '';
      if(type==='id14'&&w<360) short=label==='MIC 1'?'MIC1':label==='MIC 2'?'MIC2':short;
      const shrink=(type==='mcu'&&w<420&&label==='HEADSTAGE')?'HEAD':short;
      if(shrink)text(cx,y+61,shrink,'port-label');
    });return p;
  }
  function connector(cx,cy,index){
    if(index===0){
      ELEM('circle',{cx,cy,r:15,class:'socket-rim'});ELEM('circle',{cx,cy,r:9,class:'socket'});
    } else if(index===1){
      ELEM('rect',{x:cx-20,y:cy-8,width:24,height:16,rx:3,class:'plug-body'});
      ELEM('rect',{x:cx+4,y:cy-5,width:16,height:10,rx:3,class:'plug-metal'});
      [cx+9,cx+14].forEach(x=>ELEM('line',{x1:x,y1:cy-5,x2:x,y2:cy+5,class:'plug-ring'}));
    } else if(index===2){
      ELEM('path',{d:`M ${cx-23} ${cy} H ${cx-7} M ${cx-7} ${cy} L ${cx+5} ${cy-10} M ${cx-7} ${cy} L ${cx+5} ${cy+10}`,class:'branch'});
      ELEM('rect',{x:cx+3,y:cy-15,width:18,height:10,rx:3,class:'plug-body'});
      ELEM('rect',{x:cx+3,y:cy+5,width:18,height:10,rx:3,class:'plug-red'});
      ELEM('circle',{cx:cx+17,cy:cy-10,r:2,class:'pin'});ELEM('circle',{cx:cx+17,cy:cy+10,r:2,class:'pin'});
    } else if(index===3){
      ELEM('rect',{x:cx-21,y:cy-7,width:24,height:14,rx:2,class:'plug-metal'});ELEM('rect',{x:cx+2,y:cy-10,width:19,height:20,rx:3,class:'plug-body'});
      ELEM('line',{x1:cx-13,y1:cy-7,x2:cx-13,y2:cy+7,class:'plug-ring'});
    } else if(index===4){
      ELEM('rect',{x:cx-22,y:cy-8,width:15,height:16,rx:2,class:'plug-metal'});ELEM('path',{d:`M ${cx-7} ${cy} H ${cx+8}`,class:'branch'});ELEM('rect',{x:cx+8,y:cy-6,width:14,height:12,rx:2,class:'sma-nut'});
    } else {
      ELEM('path',{d:`M ${cx-13} ${cy-7} L ${cx-7} ${cy-13} H ${cx+7} L ${cx+13} ${cy-7} V ${cy+7} L ${cx+7} ${cy+13} H ${cx-7} L ${cx-13} ${cy+7} Z`,class:'sma-nut'});ELEM('circle',{cx,cy,r:7,class:'socket'});ELEM('circle',{cx,cy,r:2,class:'pin'});
    }
  }
  function layout(view){
    const w=Math.max(240,Math.floor(svg.getBoundingClientRect().width)), narrow=w<540, x=14, pw=w-28;
    const dims={overview:725,sound:335,analog:350,control:400,adapter:295};svg.setAttribute('viewBox',`0 0 ${w} ${dims[view]}`);svg.replaceChildren();
    const title=ELEM('title',{id:'svg-title'});title.textContent=data[view][1];const desc=ELEM('desc',{id:'svg-desc'});desc.textContent=data[view][2];
    const defs=ELEM('defs');const gradient=ELEM('linearGradient',{id:'panel-metal',x1:'0',x2:'0',y1:'0',y2:'1'},defs);ELEM('stop',{offset:'0%','stop-color':'#e7ece8'},gradient);ELEM('stop',{offset:'50%','stop-color':'#c7d0c8'},gradient);ELEM('stop',{offset:'100%','stop-color':'#dce2dc'},gradient);
    if(view==='overview'){
      const bw=narrow?72:120;let xs=narrow?[bw/2+5,w/2,w-bw/2-5]:[w*.16,w*.5,w*.84];
      xs.forEach((cx,i)=>box(cx-bw/2,10,bw,52,['COMPUTER','SPEAKERS','M50'][i],['USB-C','sound','XLR'][i],'node'));
      name(x,92,'iD14 MkII','REAR PANEL');const a=panel(x,116,pw,'id14',['USB','3L','2R','1L','MIC 1']);
      line(`M ${xs[0]} 62 V 91 H ${a.USB.x} V ${a.USB.cy-8}`);
      line(`M ${xs[1]} 62 V 94 H ${a['1L'].x} V ${a['1L'].cy-8}`);
      line(`M ${xs[1]+8} 62 V 99 H ${a['2R'].x} V ${a['2R'].cy-8}`);
      line(`M ${xs[2]} 62 V 91 H ${a['MIC 1'].x} V ${a['MIC 1'].cy-10}`);
      name(x,251,'SpikeGadgets ECU','FRONT PANEL');const e=panel(x,275,pw,'ecuFront',['AIN1']);
      line(`${out(a['3L'],-12)} V 218 H ${e.AIN1.x} V ${e.AIN1.cy-6}`,true);text(w/2,231,'PROPOSED ANALOG ADAPTER','cable-label');
      name(x,410,'SpikeGadgets ECU','REAR PANEL · SAME UNIT');const r=panel(x,434,pw,'ecuRear',['MCU']);
      text(w/2,389,'ECU FRONT AND REAR ARE THE SAME UNIT','cable-label');
      name(x,560,'SpikeGadgets MCU','REAR PANEL');const m=panel(x,584,pw,'mcu',['ECU','HEADSTAGE','ETHERNET']);
      line(`${out(r.MCU,-12)} V 535 H ${m.ECU.x} V ${m.ECU.cy-8}`);text(w*.4,548,'ECU–MCU HDMI CABLE','cable-label');
      text(w*.24,694,'TRODES / ETHERNET','cable-label');text(w*.75,694,'PROBE / HEADSTAGE*','cable-label');line(`${out(m.ETHERNET,-12)} V 677 H ${w*.24}`);line(`${out(m.HEADSTAGE,-12)} V 677 H ${w*.75}`);text(w/2,718,'* HCU / commutator may be required','note');
    } else if(view==='sound'){
      name(x,25,'iD14 MkII','REAR PANEL');const a=panel(x,49,pw,'id14',['USB','2R','1L','MIC 1']);
      let bw=narrow?72:150, xs=narrow?[bw/2+5,w/2,w-bw/2-5]:[w*.18,w*.52,w*.84];
      line(`${out(a.USB,-12)} V 165 H ${xs[0]} V 205`);line(`${out(a['1L'],-12)} V 155 H ${xs[1]} V 205`);line(`${out(a['2R'],-12)} V 149 H ${xs[1]-7} V 205`);line(`${out(a['MIC 1'],-12)} V 173 H ${xs[2]} V 205`);
      box(xs[0]-bw/2,205,bw,55,'COMPUTER','USB-C','node');box(xs[1]-bw/2,205,bw,55,'SPEAKERS','1L / 2R','node');box(xs[2]-bw/2,205,bw,55,'M50','XLR / 48 V','node');
      text(w/2,305,'SPEAKERS  · · ·  SOUND THROUGH AIR  · · ·  M50','cable-label');
    } else if(view==='analog'){
      name(x,25,'iD14 MkII','REAR PANEL');const a=panel(x,49,pw,'id14',['3L']);
      name(x,249,'SpikeGadgets ECU','FRONT PANEL');const e=panel(x,273,pw,'ecuFront',['AIN1']);
      line(`${out(a['3L'],-12)} V 145 H 26 V 230 H ${e.AIN1.x} V ${e.AIN1.cy-6}`,true);
      text(w/2+10,170,'¼-INCH TRS → BREAKOUT → TS / BNC','cable-label');text(w/2+10,190,'BNC MALE → SMA MALE','cable-label');text(w/2+10,213,'PROPOSED · NOT YET TESTED','note');
    } else if(view==='control'){
      name(x,25,'SpikeGadgets ECU','REAR PANEL');const e=panel(x,49,pw,'ecuRear',['MCU']);
      name(x,249,'SpikeGadgets MCU','REAR PANEL');const m=panel(x,273,pw,'mcu',['ECU','HEADSTAGE']);
      line(`${out(e.MCU,-12)} V 171 H ${m.ECU.x} V ${m.ECU.cy-8}`);text(w*.43,199,'ECU–MCU HDMI CABLE','cable-label');
      text(w/2,382,'HEADSTAGE INPUT IS THE ADJACENT SOCKET','note');
    } else {
      const names=['iD14 3L','HOSA','TIP / LEFT','POMONA','BNC / SMA','ECU AIN1'];const subtitles=['¼ TRS','YPP-117','RING OPEN','1297','COAX','SMA'];const count=narrow?3:6;
      names.forEach((s,i)=>{const row=Math.floor(i/count),col=i%count,bw=(w-40)/count,cx=20+bw*(col+.5),y=20+row*110;
        connector(cx,y+17,i);text(cx,y+53,s,'node-label');text(cx,y+72,subtitles[i],'node-sub');
        if(col<count-1&&i<5)line(`M ${cx+25} ${y+17} H ${cx+bw-25}`,true);
      });
      if(narrow)line(`M ${w-25} 37 V 100 H 25 V 147`,true);
      text(w/2,narrow?266:195,'PROPOSED ASSEMBLY · VERIFY BEFORE CONNECTING','note');
    }
  }
  let selected='overview';
  function select(view){if(!data[view])return;selected=view;document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));const d=data[view];ui.kicker.textContent=d[0];ui.title.textContent=d[1];ui.fn.textContent=d[2];ui.sources.innerHTML=d[3];layout(view);}
  const css=document.createElementNS(NS,'style');css.textContent='.panel{fill:url(#panel-metal);stroke:#8b9b90;stroke-width:1.3}.bevel{fill:none;stroke:#f4f8f4;stroke-width:1}.screw{fill:#8b9b90}.socket{fill:#202d28;stroke:#718277;stroke-width:1.2}.socket-rim{fill:#dce4dd;stroke:#5a6a60;stroke-width:1}.sma-nut{fill:#d7c28e;stroke:#88774e;stroke-width:1}.pin{fill:#c6d0c6}.metal-detail{fill:none;stroke:#acbab0;stroke-width:1}.adapter-ring{fill:#fafcf9;stroke:#53695b;stroke-width:1.4}.chosen{stroke:#c27847;stroke-width:2.6}.center{fill:#53695b}.wire-shell{fill:none;stroke:#354b40;stroke-width:5;stroke-linejoin:round;stroke-linecap:round}.wire-shell.proposed{stroke:#965f3e;stroke-dasharray:7 4}.wire{fill:none;stroke:#7baa8f;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}.wire.proposed{stroke:#e4af89;stroke-dasharray:7 4}.node,.unit{fill:#fff;stroke:#d2dfd4;stroke-width:1.2}.device-title{font:600 13px -apple-system,BlinkMacSystemFont,sans-serif;fill:#253a2f}.device-sub,.port-label,.cable-label,.node-sub,.note{font:11px -apple-system,BlinkMacSystemFont,sans-serif;fill:#46594d}.device-sub{letter-spacing:1px}.cable-label{fill:#46594d}.node-label{font:600 11px -apple-system,BlinkMacSystemFont,sans-serif;fill:#263d30}';document.head.appendChild(document.createElement('style')).textContent=css.textContent;
  const connectorCss=document.createElement('style');connectorCss.textContent='.plug-body{fill:#2e3b33;stroke:#15231c}.plug-red{fill:#a85e4c;stroke:#7a4439}.plug-metal{fill:#d9dfd9;stroke:#85948a}.plug-ring{stroke:#526158;stroke-width:2}.branch{fill:none;stroke:#2e3b33;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}';document.head.appendChild(connectorCss);
  document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>select(b.dataset.view)));
  new ResizeObserver(()=>layout(selected)).observe(svg);
  select('overview');
})();
