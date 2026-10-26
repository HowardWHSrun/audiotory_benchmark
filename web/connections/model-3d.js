const host = document.getElementById('model-canvas');
const status = document.getElementById('model-status');
const details = document.getElementById('model-detail');
const buttons = [...document.querySelectorAll('[data-3d]')];

try {
  const THREE = await import('three');
  const { OrbitControls } = await import('https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/controls/OrbitControls.js');
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#e9f0e9');
  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 150);
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  host.prepend(renderer.domElement);
  renderer.domElement.setAttribute('aria-label', 'Rotatable, illustrative device and cable models');
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.minDistance = 4;
  controls.maxDistance = 55;
  controls.maxPolarAngle = Math.PI * 0.49;
  controls.enablePan = true;
  scene.add(new THREE.HemisphereLight('#ffffff', '#c3d3c6', 2.2));
  const light = new THREE.DirectionalLight('#ffffff', 2.2);
  light.position.set(2, 10, 8);
  scene.add(light);

  const mat = (color, metalness = 0, roughness = 0.55) => new THREE.MeshStandardMaterial({ color, metalness, roughness });
  const black = mat('#202825', .25), charcoal = mat('#323e38', .12), silver = mat('#b9c4bd', .65, .3);
  const darkSilver = mat('#798b80', .7, .35), gold = mat('#d2b577', .7, .3), hole = mat('#101a16');
  const white = mat('#f8faf7'), green = '#387a60', blue = '#577fa6', orange = '#cb7740';
  const box = (w,h,d, material, x,y,z, parent=scene) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), material);
    m.position.set(x,y,z); parent.add(m); return m;
  };
  const disk = (r, depth, material, x,y,z, parent=scene) => {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(r,r,depth,20), material);
    m.rotation.x = Math.PI / 2; m.position.set(x,y,z); parent.add(m); return m;
  };
  function label(message, x, y, z, width=1.2, size=35) {
    const canvas = document.createElement('canvas'); canvas.width = 512; canvas.height = 120;
    const ctx = canvas.getContext('2d'); ctx.clearRect(0,0,512,120);
    ctx.fillStyle='rgba(248,251,248,.96)'; ctx.roundRect(3,5,506,110,18); ctx.fill();
    ctx.font=`600 ${size}px -apple-system, BlinkMacSystemFont, sans-serif`;
    ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillStyle='#263e34';ctx.fillText(message,256,60,485);
    const texture = new THREE.CanvasTexture(canvas); texture.colorSpace=THREE.SRGBColorSpace;
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map:texture, transparent:true, depthTest:false }));
    sprite.position.set(x,y,z); sprite.scale.set(width,width*120/512,1); sprite.renderOrder=9; scene.add(sprite); return sprite;
  }
  function port(x,y,z,shape='round') {
    if(shape==='hdmi') {box(.22,.12,.035,darkSilver,x,y,z); box(.17,.07,.045,hole,x,y,z+.025);}
    else if(shape==='usb') {box(.13,.09,.035,darkSilver,x,y,z);box(.09,.045,.04,hole,x,y,z+.025);}
    else if(shape==='sma') {disk(.083,.04,gold,x,y,z);disk(.035,.05,hole,x,y,z+.03);}
    else if(shape==='xlr') {disk(.15,.04,darkSilver,x,y,z);disk(.115,.05,hole,x,y,z+.03);[[-.04,-.025],[.04,-.025],[0,.04]].forEach(([a,b])=>disk(.013,.06,white,x+a,y+b,z+.06));}
    else {disk(.105,.035,darkSilver,x,y,z);disk(.067,.045,hole,x,y,z+.03);}
    return new THREE.Vector3(x,y,z+.06);
  }
  const ground = box(23,.06,12,mat('#dce7dd'),0,-.05,0); ground.receiveShadow=true;
  const P={};
  // iD14 rear, viewed directly: USB, optical, 4R, 3L, 2R, 1L, Mic 2, Mic 1.
  box(3.7,.73,2.3,black,-4.5,.55,0);
  box(3.45,.1,2.12,charcoal,-4.5,.96,0);
  [[-5.65,.17],[-5.05,.17],[-4.25,.26]].forEach(([x,r])=>{const knob=new THREE.Mesh(new THREE.CylinderGeometry(r,r,.18,32),darkSilver);knob.position.set(x,1.1,-.35);scene.add(knob);});
  label('Audient iD14 MkII · rear',-4.5,1.62,0,2.6);
  const idNames=['USB','OPT','4R','3L','2R','1L','MIC2','MIC1'];
  const idPorts={}; idNames.forEach((n,i)=>{const x=-6.1+i*.45;idPorts[n]=port(x,.57,1.17,i===0?'usb':i===1?'usb':i>=6?'xlr':'round');});
  P.usb=idPorts.USB;P.out3=idPorts['3L'];P.out1=idPorts['1L'];P.out2=idPorts['2R'];P.mic1=idPorts.MIC1;
  label('3L',P.out3.x,.27,1.25,.48);label('MIC 1',P.mic1.x,.27,1.25,.62);label('1L / 2R',-4.08,.27,1.25,.88);label('USB',P.usb.x,.27,1.25,.55);

  // ECU front and rear are opposite sides of one enclosure.
  box(3.4,.54,1.9,silver,0,.5,0);label('SpikeGadgets ECU · front',0,1.45,0,2.45);
  const eNames=['Audio','Ain1','Aout1','Din1','Din2','Din3','Din4','Dout1','Dout2','Dout3','Dout4','Power'];
  const ep={};eNames.forEach((n,i)=>{const x=-1.52+i*.276;ep[n]=port(x,.5,.98,i===0?'round':i===11?'round':'sma');});P.ain=ep.Ain1;
  label('Ain1',P.ain.x,.19,1.08,.6);
  // The MCU connector is on the *back* of the ECU, facing -Z.
  P.ecuRear = new THREE.Vector3(1.36,.5,-1.02);
  box(.25,.12,.06,hole,P.ecuRear.x,P.ecuRear.y,P.ecuRear.z);label('MCU · rear',1.32,1.12,-1.13,1.1);

  // MCU rear; ECU connector and headstage/HCU connector are distinct adjacent sockets.
  box(3.4,.54,1.9,silver,4.4,.5,0);label('SpikeGadgets MCU · rear',4.4,1.45,0,2.5);
  const mNames=['5V','Ethernet','GND','D I/O','ECU','Headstage'];const mp={};
  mNames.forEach((n,i)=>{const x=2.98+i*.58;mp[n]=port(x,.5,.98,i===4||i===5?'hdmi':i===1||i===3?'usb':'round');});
  P.ecuPort=mp.ECU;P.headPort=mp.Headstage;P.ether=mp.Ethernet;
  label('ECU',P.ecuPort.x,.18,1.1,.65);label('HEAD',P.headPort.x,.18,1.1,.64);label('Ethernet',P.ether.x,.18,1.1,.84);

  // Symbolic surrounding devices: proportions and exact hardware are not established.
  box(1.1,1.65,.85,charcoal,-6.8,.84,4.25);disk(.34,.06,hole,-6.8,1.03,4.7);disk(.12,.07,darkSilver,-6.8,1.48,4.71);
  box(1.1,1.65,.85,charcoal,-5.4,.84,4.25);disk(.34,.06,hole,-5.4,1.03,4.7);disk(.12,.07,darkSilver,-5.4,1.48,4.71);
  label('Speaker pair',-6.1,2.08,4.3,2.1);
  // A long slim cylinder represents the M50, not a manufacturer-supplied CAD model.
  const microphone = new THREE.Mesh(new THREE.CylinderGeometry(.10,.10,1.75,24), silver);
  microphone.rotation.z=Math.PI/2;microphone.position.set(-2.45,.65,4.3);scene.add(microphone);
  disk(.1,.03,darkSilver,-3.3,.65,4.3);label('M50 microphone',-2.45,1.28,4.3,1.7);
  box(1.5,.09,1.1,black,-7.1,.17,-3);box(1.5,1,.08,black,-7.1,.72,-3.5);box(1.34,.84,.09,mat('#6f8c80'),-7.1,.73,-3.44);
  label('Audio computer',-7.1,1.58,-3.1,1.7);
  box(.72,.18,.9,charcoal,7,.45,-3);label('Headstage / HCU*',7,1.18,-3,1.8);
  box(.28,.18,.22,charcoal,8.3,.75,-4.1);box(.11,.72,.055,silver,8.3,.31,-4.1);label('Probe · model TBD',8.3,1.15,-4.2,1.7);
  box(1.4,.09,1.0,black,8.1,.15,3.9);box(1.4,.9,.08,black,8.1,.65,3.45);box(1.25,.74,.09,mat('#718f80'),8.1,.66,3.5);label('Trodes computer',8.1,1.47,3.6,1.8);

  const cables=[];
  function cable(name, color, points, category, radius=.045) {
    const curve = new THREE.CatmullRomCurve3(points.map(p=>p.isVector3 ? p : new THREE.Vector3(...p)));
    const material=new THREE.MeshStandardMaterial({color,roughness:.56,transparent:true});
    const object=new THREE.Mesh(new THREE.TubeGeometry(curve,80,radius,8,false),material);scene.add(object);
    cables.push({name,category,material});
    const p=points[0].isVector3 ? points[0] : new THREE.Vector3(...points[0]);
    const connector=new THREE.Mesh(new THREE.SphereGeometry(.075,14,10),mat(color));connector.position.copy(p);scene.add(connector);
    return object;
  }
  cable('Audio USB',green,[P.usb,[-6.7,.8,1.5],[-7.5,.4,.4],[-7.3,.25,-2.5]],'sound');
  cable('Speaker 1',green,[P.out1,[-3.6,.55,2],[-4.5,.15,3],[-5.4,.2,4.1]],'sound');
  cable('Speaker 2',green,[P.out2,[-3.8,.4,2.1],[-5.1,.10,3.3],[-5.7,.2,4.1]],'sound');
  cable('M50 XLR',green,[P.mic1,[-2.6,.7,2.2],[-1.7,.25,3.2],[-1.6,.65,4.3]],'sound');
  // Proposed analogue route is deliberately marked in orange; adapters are schematic.
  cable('Proposed microphone cable',orange,[P.out3,[-4.4,.65,1.8],[-3.5,.22,2.65],[-2.1,.2,2.5],[-1.3,.4,1.9],P.ain],'analog');
  box(.52,.13,.13,charcoal,-3.5,.27,2.65);box(.4,.13,.13,silver,-2.7,.27,2.6);label('Adapter · proposed',-3.1,.88,2.6,1.55);
  cable('ECU to MCU',blue,[P.ecuRear,[1.9,.55,-1.8],[3.1,.4,-2.25],[4.8,.4,-1.9],[5.6,.6,-.3],P.ecuPort],'control');
  cable('Headstage cable',blue,[P.headPort,[6.3,.6,1.9],[7.5,.35,1],[7.4,.35,-1.6],[7,.45,-2.6]],'control');
  cable('Probe to headstage',blue,[[7.32,.48,-3],[7.9,.65,-3.6],[8.2,.75,-4.0]],'control',.028);
  cable('Trodes Ethernet',blue,[P.ether,[4,.35,2],[5.1,.12,2.7],[7,.10,3.2],[7.8,.2,3.6]],'control');

  const views={
    all:{target:[0,.5,.25],camera:[0,10,17], detail:'Whole setup: audio, neural and proposed microphone connections. The audio and Trodes computers can be the same machine. Rotate to see the ECU rear port.'},
    sound:{target:[-4.7,.7,2.0],camera:[-4.7,7,13],detail:'Sound: computer → iD14 USB; 1L/2R → speakers; M50 XLR → MIC 1. Confirm your actual speaker cabling.'},
    analog:{target:[-2.4,.55,1.0],camera:[-2.4,5.7,10.0],detail:'Proposed mic feed: iD14 output 3L → adapter assembly → ECU front Ain1. Set Cue A first; verify pinout and levels.'},
    control:{target:[2.7,.6,0],camera:[3.2,7,-10],detail:'ECU rear MCU socket → MCU rear ECU socket. Rotate to see the MCU rear ports; the adjacent socket is for the headstage / HCU.'},
    adapter:{target:[-3,.3,2.45],camera:[-3,3.6,6.9],detail:'Proposed adapter: Hosa tip branch → Pomona TS-to-BNC → BNC-to-SMA. See Adapter close-up below for connector details.'}
  };
  let selectedView = 'all';
  function select(view) {
    const cfg=views[view] || views.all;
    selectedView = view;
    buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset['3d']===view)));
    controls.target.set(...cfg.target);
    const fit=view==='all'?1.45 : view==='analog'||view==='control'?1.35 : view==='sound'?1.15 : .94;
    const mobileScale=Math.max(1, fit/camera.aspect);
    camera.position.set(...cfg.camera).sub(controls.target).multiplyScalar(mobileScale).add(controls.target);
    controls.update();
    details.textContent=cfg.detail;
    const category=view==='adapter'?'analog':view;
    cables.forEach(c=>{c.material.opacity=(category==='all'||c.category===category)?1:.16;c.material.needsUpdate=true;});
  }
  buttons.forEach(b=>b.addEventListener('click',()=>select(b.dataset['3d'])));
  function resize(){const w=host.clientWidth,h=host.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();select(selectedView);}
  new ResizeObserver(resize).observe(host);resize();select('all');
  status.textContent='';status.hidden=true;
  renderer.setAnimationLoop(()=>{controls.update();renderer.render(scene,camera);});
} catch (error) {
  console.error('3D connection guide unavailable', error);
  status.textContent='The 3D view could not load. Use the labeled 2D views and manufacturer photos below.';
  buttons.forEach(b=>b.disabled=true);
}
