import * as THREE from 'three';
import { OrbitControls } from 'three/examples/controls/OrbitControls.js';

// Scene globals
let scene, camera, renderer, controls, raycaster, mouse;
let placedFurniture = [];
let selectedObject = null;
let floorMesh = null;
let isDragging = false;
let dragObject = null;
const floorPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
const dragOffset = new THREE.Vector3();
const intersection = new THREE.Vector3();
const ROOM = { w: 10, h: 3.2, d: 8 };

// Material library
const MAT_COLORS = {
  'Oak': '#C4A882', 'Walnut': '#6B4E37', 'Maple': '#D4B896',
  'Linen': '#E8DFD5', 'Velvet': '#7B6B8A', 'Leather': '#8B5E3C',
  'Marble': '#E0D8D0', 'Concrete': '#A0A0A0', 'Cotton': '#F0EDE8'
};

const FURNITURE_DATA = [
  { id:'sofa1', name:'Nordic Sofa', cat:'sofas', w:2.2, h:0.85, d:0.9, price:'$1,290', color:'#C8B8A4' },
  { id:'sofa2', name:'L-Shape Sofa', cat:'sofas', w:2.8, h:0.82, d:1.8, price:'$2,150', color:'#A09080' },
  { id:'sofa3', name:'Armchair', cat:'sofas', w:0.85, h:0.8, d:0.85, price:'$680', color:'#B8A898' },
  { id:'table1', name:'Dining Table', cat:'tables', w:1.8, h:0.76, d:0.9, price:'$890', color:'#C4A882' },
  { id:'table2', name:'Coffee Table', cat:'tables', w:1.2, h:0.42, d:0.6, price:'$450', color:'#B89B78' },
  { id:'table3', name:'Side Table', cat:'tables', w:0.5, h:0.55, d:0.5, price:'$280', color:'#D4B896' },
  { id:'chair1', name:'Dining Chair', cat:'chairs', w:0.48, h:0.82, d:0.52, price:'$320', color:'#C4A882' },
  { id:'chair2', name:'Stool', cat:'chairs', w:0.38, h:0.65, d:0.38, price:'$180', color:'#8B6F4E' },
  { id:'lamp1', name:'Pendant Lamp', cat:'lighting', w:0.4, h:0.35, d:0.4, price:'$220', color:'#2D2D2D' },
  { id:'lamp2', name:'Floor Lamp', cat:'lighting', w:0.35, h:1.6, d:0.35, price:'$340', color:'#3A3A3A' },
  { id:'lamp3', name:'Table Lamp', cat:'lighting', w:0.25, h:0.45, d:0.25, price:'$160', color:'#C4A882' },
  { id:'deco1', name:'Plant Pot', cat:'decor', w:0.35, h:0.8, d:0.35, price:'$90', color:'#8FA584' },
  { id:'deco2', name:'Vase', cat:'decor', w:0.2, h:0.4, d:0.2, price:'$65', color:'#C67D5B' },
  { id:'deco3', name:'Rug', cat:'decor', w:2.5, h:0.02, d:1.8, price:'$420', color:'#D4C8B8' },
  { id:'deco4', name:'Bookshelf', cat:'decor', w:0.9, h:1.8, d:0.35, price:'$560', color:'#C4A882' },
];

function createWoodMaterial(color) {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.7, metalness: 0.0 });
}
function createFabricMaterial(color) {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.9, metalness: 0.0 });
}
function createMetalMaterial(color) {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.3, metalness: 0.7 });
}

// Build furniture meshes
function buildSofa(data) {
  const g = new THREE.Group();
  const mat = createFabricMaterial(data.color);
  const base = new THREE.Mesh(new THREE.BoxGeometry(data.w, 0.35, data.d), mat);
  base.position.y = 0.3; base.castShadow = true;
  g.add(base);
  const back = new THREE.Mesh(new THREE.BoxGeometry(data.w, 0.45, 0.12), mat);
  back.position.set(0, 0.6, -data.d/2 + 0.06); back.castShadow = true;
  g.add(back);
  if (data.id === 'sofa2') {
    const side = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.35, 0.9), mat);
    side.position.set(data.w/2 - 0.45, 0.3, data.d/2 - 0.45); side.castShadow = true;
    g.add(side);
  }
  const legMat = createMetalMaterial('#2D2D2D');
  [[-1,-1],[1,-1],[1,1],[-1,1]].forEach(([x,z]) => {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.02,0.02,0.12), legMat);
    leg.position.set(x*(data.w/2-0.08), 0.06, z*(data.d/2-0.08));
    g.add(leg);
  });
  // cushions
  const cush = createFabricMaterial(new THREE.Color(data.color).offsetHSL(0,0,0.05).getStyle());
  const cw = data.id==='sofa3'? data.w*0.7 : data.w/2-0.05;
  const nc = data.id==='sofa3'? 1 : 2;
  for(let i=0;i<nc;i++){
    const c = new THREE.Mesh(new THREE.BoxGeometry(cw,0.1,data.d*0.7), cush);
    c.position.set(nc===1?0:(i===0?-cw/2-0.01:cw/2+0.01), 0.53, 0.04);
    c.castShadow=true; g.add(c);
  }
  return g;
}

function buildTable(data) {
  const g = new THREE.Group();
  const mat = createWoodMaterial(data.color);
  const top = new THREE.Mesh(new THREE.BoxGeometry(data.w, 0.04, data.d), mat);
  top.position.y = data.h; top.castShadow = true; top.receiveShadow = true;
  g.add(top);
  const legH = data.h - 0.02;
  const legMat = data.id==='table2' ? createMetalMaterial('#2D2D2D') : mat;
  const lr = data.id==='table2' ? 0.015 : 0.03;
  [[-1,-1],[1,-1],[1,1],[-1,1]].forEach(([x,z]) => {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(lr,lr,legH), legMat);
    leg.position.set(x*(data.w/2-0.06), legH/2, z*(data.d/2-0.06));
    leg.castShadow = true; g.add(leg);
  });
  return g;
}

function buildChair(data) {
  const g = new THREE.Group();
  const mat = createWoodMaterial(data.color);
  const seatH = data.id==='chair2' ? data.h : 0.46;
  const seat = new THREE.Mesh(new THREE.BoxGeometry(data.w, 0.04, data.d*0.85), mat);
  seat.position.y = seatH; seat.castShadow = true; g.add(seat);
  const cushMat = createFabricMaterial('#B0A898');
  const cush = new THREE.Mesh(new THREE.BoxGeometry(data.w*0.85, 0.03, data.d*0.7), cushMat);
  cush.position.y = seatH + 0.035; cush.castShadow = true; g.add(cush);
  [[-1,-1],[1,-1],[1,1],[-1,1]].forEach(([x,z]) => {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.02,0.02,seatH), mat);
    leg.position.set(x*(data.w/2-0.04), seatH/2, z*(data.d*0.85/2-0.04));
    g.add(leg);
  });
  if(data.id !== 'chair2') {
    const back = new THREE.Mesh(new THREE.BoxGeometry(data.w*0.9, data.h-seatH, 0.03), mat);
    back.position.set(0, seatH+(data.h-seatH)/2, -data.d*0.85/2+0.015);
    back.castShadow=true; g.add(back);
  }
  return g;
}

function buildLamp(data) {
  const g = new THREE.Group();
  if(data.id==='lamp1') {
    const shadeMat = createMetalMaterial(data.color);
    const shade = new THREE.Mesh(new THREE.ConeGeometry(data.w/2,data.h*0.6,32,1,true), shadeMat);
    shade.position.y = ROOM.h - 0.3; shade.castShadow=true; g.add(shade);
    const cord = new THREE.Mesh(new THREE.CylinderGeometry(0.005,0.005,0.6), shadeMat);
    cord.position.y = ROOM.h; g.add(cord);
    const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.04), new THREE.MeshStandardMaterial({color:'#FFF5E0',emissive:'#FFF5E0',emissiveIntensity:0.8}));
    bulb.position.y = ROOM.h - 0.35; g.add(bulb);
    const pl = new THREE.PointLight('#FFF0D4', 0.6, 5);
    pl.position.y = ROOM.h - 0.35; g.add(pl);
  } else if(data.id==='lamp2') {
    const mat = createMetalMaterial(data.color);
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.015,0.015,data.h), mat);
    pole.position.y = data.h/2; g.add(pole);
    const baseMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.15,0.15,0.02), mat);
    baseMesh.position.y = 0.01; g.add(baseMesh);
    const shade = new THREE.Mesh(new THREE.ConeGeometry(0.18,0.25,32,1,true), createFabricMaterial('#E8DFD5'));
    shade.position.y = data.h - 0.1; shade.castShadow=true; g.add(shade);
    const pl = new THREE.PointLight('#FFF0D4', 0.4, 4);
    pl.position.y = data.h - 0.05; g.add(pl);
  } else {
    const mat = createWoodMaterial(data.color);
    const baseMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.08,0.1,0.06), mat);
    baseMesh.position.y = 0.03; g.add(baseMesh);
    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.03,0.05,0.2), mat);
    body.position.y = 0.16; g.add(body);
    const shade = new THREE.Mesh(new THREE.CylinderGeometry(0.08,0.12,0.18,32,1,true), createFabricMaterial('#F0EDE8'));
    shade.position.y = 0.35; g.add(shade);
    const pl = new THREE.PointLight('#FFF0D4', 0.3, 3);
    pl.position.y = 0.35; g.add(pl);
  }
  return g;
}

function buildDecor(data) {
  const g = new THREE.Group();
  if(data.id==='deco1') {
    const potMat = createWoodMaterial('#8B7D6B');
    const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.12,0.1,0.25,16), potMat);
    pot.position.y = 0.125; pot.castShadow=true; g.add(pot);
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.01,0.015,0.35), createWoodMaterial('#6B5E4E'));
    trunk.position.y = 0.42; g.add(trunk);
    const leaves = new THREE.Mesh(new THREE.SphereGeometry(0.18,8,8), createFabricMaterial(data.color));
    leaves.position.y = 0.65; leaves.castShadow=true; g.add(leaves);
  } else if(data.id==='deco2') {
    const pts = [];
    for(let i=0;i<10;i++){
      const t=i/9, r=0.05+0.06*Math.sin(t*Math.PI)*((t<0.3)?t/0.3:1);
      pts.push(new THREE.Vector2(r, t*data.h));
    }
    const vaseMat = new THREE.MeshStandardMaterial({color:data.color, roughness:0.4, metalness:0.1});
    const vase = new THREE.Mesh(new THREE.LatheGeometry(pts,24), vaseMat);
    vase.castShadow=true; g.add(vase);
  } else if(data.id==='deco3') {
    const rugMat = createFabricMaterial(data.color);
    const rug = new THREE.Mesh(new THREE.BoxGeometry(data.w, data.h, data.d), rugMat);
    rug.position.y = data.h/2; rug.receiveShadow=true; g.add(rug);
  } else {
    const mat = createWoodMaterial(data.color);
    const frame = new THREE.Mesh(new THREE.BoxGeometry(data.w, data.h, data.d), mat);
    frame.position.y = data.h/2; frame.castShadow=true; g.add(frame);
    for(let i=0;i<4;i++){
      const shelf = new THREE.Mesh(new THREE.BoxGeometry(data.w-0.04,0.02,data.d-0.02), mat);
      shelf.position.set(0, 0.3+i*0.38, 0); g.add(shelf);
    }
  }
  return g;
}

function buildFurniture(data) {
  let g;
  if(data.cat==='sofas') g = buildSofa(data);
  else if(data.cat==='tables') g = buildTable(data);
  else if(data.cat==='chairs') g = buildChair(data);
  else if(data.cat==='lighting') g = buildLamp(data);
  else g = buildDecor(data);
  g.userData = { ...data, placed: true };
  g.traverse(c => { if(c.isMesh){ c.castShadow=true; c.userData.furnitureGroup=g; }});
  return g;
}

// Scene init
function initScene(container) {
  scene = new THREE.Scene();
  scene.background = new THREE.Color('#F0EBE5');

  camera = new THREE.PerspectiveCamera(50, container.clientWidth/container.clientHeight, 0.1, 100);
  camera.position.set(5, 4, 7);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;
  container.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.maxPolarAngle = Math.PI/2 - 0.05;
  controls.minDistance = 2;
  controls.maxDistance = 15;
  controls.target.set(0, 1.2, 0);

  raycaster = new THREE.Raycaster();
  mouse = new THREE.Vector2();

  buildRoom();
  setupLights();
  addDefaultFurniture();

  window.addEventListener('resize', () => {
    camera.aspect = container.clientWidth/container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  });

  animate();
  return { scene, camera, renderer, controls };
}

function buildRoom() {
  const { w, h, d } = ROOM;
  // Floor
  const floorMat = new THREE.MeshStandardMaterial({ color:'#E8DDD2', roughness:0.8 });
  floorMesh = new THREE.Mesh(new THREE.PlaneGeometry(w, d), floorMat);
  floorMesh.rotation.x = -Math.PI/2;
  floorMesh.receiveShadow = true;
  floorMesh.userData.isFloor = true;
  scene.add(floorMesh);

  // Floor planks (subtle lines)
  const plankMat = new THREE.MeshStandardMaterial({ color:'#DDD2C5', roughness:0.85 });
  for(let i=-w/2; i<w/2; i+=0.3) {
    const line = new THREE.Mesh(new THREE.PlaneGeometry(0.005, d), plankMat);
    line.rotation.x=-Math.PI/2; line.position.set(i,0.001,0);
    scene.add(line);
  }

  const wallMat = new THREE.MeshStandardMaterial({ color:'#F5F0EB', roughness:0.9, side:THREE.DoubleSide });
  // Back wall
  const bw = new THREE.Mesh(new THREE.PlaneGeometry(w, h), wallMat);
  bw.position.set(0, h/2, -d/2); scene.add(bw);
  // Left wall
  const lw = new THREE.Mesh(new THREE.PlaneGeometry(d, h), wallMat);
  lw.rotation.y = Math.PI/2; lw.position.set(-w/2, h/2, 0); scene.add(lw);
  // Right wall
  const rw = new THREE.Mesh(new THREE.PlaneGeometry(d, h), wallMat);
  rw.rotation.y = -Math.PI/2; rw.position.set(w/2, h/2, 0); scene.add(rw);

  // Baseboard
  const bbMat = new THREE.MeshStandardMaterial({ color:'#DDD5CA', roughness:0.6 });
  [[0,0.04,-d/2,w,0.08,0],[0,0.04,0,0.08,0.08,d],[-w/2,0.04,0,0.08,0.08,d],[w/2,0.04,0,0.08,0.08,d]].forEach(([x,y,z,sw,sh,sd],i)=>{
    if(i===0) sd=0.01;
    const bb = new THREE.Mesh(new THREE.BoxGeometry(sw||0.01,sh,sd||0.01), bbMat);
    bb.position.set(x,y,z);
    if(i>0) bb.rotation.y = 0;
    scene.add(bb);
  });

  // Window on back wall
  const winFrame = new THREE.MeshStandardMaterial({color:'#D8D0C5', roughness:0.5});
  const winGlass = new THREE.MeshStandardMaterial({color:'#C8DEE8', transparent:true, opacity:0.3, roughness:0.1});
  const wf = new THREE.Mesh(new THREE.BoxGeometry(2.5,1.8,0.05), winFrame);
  wf.position.set(0, 1.8, -d/2+0.01); scene.add(wf);
  const wg = new THREE.Mesh(new THREE.PlaneGeometry(2.3,1.6), winGlass);
  wg.position.set(0, 1.8, -d/2+0.03); scene.add(wg);

  // Ceiling
  const ceilMat = new THREE.MeshStandardMaterial({ color:'#FAFAFA', roughness:0.95 });
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(w, d), ceilMat);
  ceil.rotation.x = Math.PI/2; ceil.position.y = h; scene.add(ceil);
}

function setupLights() {
  const amb = new THREE.AmbientLight('#FFF5E8', 0.5);
  scene.add(amb);

  const dir = new THREE.DirectionalLight('#FFFAF0', 1.2);
  dir.position.set(3, 5, 4);
  dir.castShadow = true;
  dir.shadow.mapSize.set(2048,2048);
  dir.shadow.camera.left=-8; dir.shadow.camera.right=8;
  dir.shadow.camera.top=8; dir.shadow.camera.bottom=-8;
  dir.shadow.bias = -0.001;
  dir.shadow.radius = 3;
  scene.add(dir);

  const fill = new THREE.DirectionalLight('#E8F0FF', 0.3);
  fill.position.set(-3, 3, -2); scene.add(fill);

  const windowLight = new THREE.RectAreaLight('#FFF8F0', 2, 2.3, 1.6);
  windowLight.position.set(0, 1.8, -ROOM.d/2+0.1);
  windowLight.lookAt(0, 1.8, 0);
  scene.add(windowLight);
}

function addDefaultFurniture() {
  const defaults = [
    { id:'sofa1', pos:[0,0,1.5] },
    { id:'table2', pos:[0,0,0] },
    { id:'deco3', pos:[0,0,0.5] },
    { id:'deco1', pos:[-3,0,-2.5] },
    { id:'lamp2', pos:[3.5,0,2] },
  ];
  defaults.forEach(({id, pos}) => {
    const data = FURNITURE_DATA.find(f=>f.id===id);
    if(data) {
      const mesh = buildFurniture(data);
      mesh.position.set(...pos);
      scene.add(mesh);
      placedFurniture.push(mesh);
    }
  });
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

function addToScene(itemId) {
  const data = FURNITURE_DATA.find(f=>f.id===itemId);
  if(!data) return null;
  const mesh = buildFurniture(data);
  mesh.position.set(Math.random()*2-1, 0, Math.random()*2-1);
  scene.add(mesh);
  placedFurniture.push(mesh);
  return mesh;
}

function removeFromScene(obj) {
  scene.remove(obj);
  placedFurniture = placedFurniture.filter(f=>f!==obj);
  if(selectedObject===obj) selectedObject=null;
}

function selectObject(obj) {
  if(selectedObject) deselectObject();
  selectedObject = obj;
  obj.traverse(c => {
    if(c.isMesh && c._origMat === undefined) {
      c._origMat = c.material;
      c.material = c.material.clone();
      c.material.emissive = new THREE.Color('#C4A882');
      c.material.emissiveIntensity = 0.15;
    }
  });
}

function deselectObject() {
  if(!selectedObject) return;
  selectedObject.traverse(c => {
    if(c.isMesh && c._origMat !== undefined) {
      c.material.dispose();
      c.material = c._origMat;
      delete c._origMat;
    }
  });
  selectedObject = null;
}

function getClickedFurniture(event, container) {
  const rect = container.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left)/rect.width)*2-1;
  mouse.y = -((event.clientY - rect.top)/rect.height)*2+1;
  raycaster.setFromCamera(mouse, camera);
  const meshes = [];
  placedFurniture.forEach(g=>g.traverse(c=>{if(c.isMesh)meshes.push(c)}));
  const hits = raycaster.intersectObjects(meshes);
  if(hits.length>0) {
    let obj = hits[0].object;
    while(obj.parent && !obj.userData.placed) obj = obj.parent;
    if(obj.userData.placed) return obj;
  }
  return null;
}

function changeMaterialColor(obj, hexColor) {
  if(!obj) return;
  obj.traverse(c => {
    if(c.isMesh) {
      c.material.color.set(hexColor);
      // Also update the stored original material so color persists after deselect
      if(c._origMat) {
        c._origMat = c._origMat.clone();
        c._origMat.color.set(hexColor);
      }
    }
  });
}

function setView(mode) {
  const t = 0.6;
  if(mode==='top') {
    camera.position.set(0, 12, 0.01);
    controls.target.set(0,0,0);
  } else if(mode==='front') {
    camera.position.set(0, 2, 10);
    controls.target.set(0,1.5,0);
  } else {
    camera.position.set(5, 4, 7);
    controls.target.set(0,1.2,0);
  }
  controls.update();
}

// Drag-to-move system
function setupDrag(container, onSelect, onDeselect) {
  let mouseDownPos = new THREE.Vector2();
  let wasDragged = false;

  container.addEventListener('pointerdown', (e) => {
    mouseDownPos.set(e.clientX, e.clientY);
    wasDragged = false;
    const obj = getClickedFurniture(e, container);
    if (obj) {
      // Start drag
      isDragging = true;
      dragObject = obj;
      controls.enabled = false;
      // Calculate offset so object doesn't snap to cursor
      const rect = container.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      raycaster.ray.intersectPlane(floorPlane, intersection);
      dragOffset.copy(obj.position).sub(intersection);
      container.style.cursor = 'grabbing';
    }
  });

  container.addEventListener('pointermove', (e) => {
    const dx = e.clientX - mouseDownPos.x;
    const dy = e.clientY - mouseDownPos.y;
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) wasDragged = true;

    if (isDragging && dragObject) {
      const rect = container.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      raycaster.ray.intersectPlane(floorPlane, intersection);
      const newPos = intersection.add(dragOffset);
      // Clamp to room bounds
      const hw = ROOM.w / 2 - 0.3, hd = ROOM.d / 2 - 0.3;
      dragObject.position.x = Math.max(-hw, Math.min(hw, newPos.x));
      dragObject.position.z = Math.max(-hd, Math.min(hd, newPos.z));
    } else if (!isDragging) {
      // Hover cursor
      const obj = getClickedFurniture(e, container);
      container.style.cursor = obj ? 'grab' : 'default';
    }
  });

  container.addEventListener('pointerup', (e) => {
    if (isDragging) {
      container.style.cursor = 'grab';
      isDragging = false;
      controls.enabled = true;
      if (!wasDragged) {
        // It was a click, not a drag — select
        deselectObject();
        selectObject(dragObject);
        if (onSelect) onSelect(dragObject);
      }
      dragObject = null;
    } else {
      // Clicked empty space
      if (!wasDragged) {
        deselectObject();
        if (onDeselect) onDeselect();
      }
    }
  });
}

export {
  initScene, FURNITURE_DATA, addToScene, removeFromScene,
  selectObject, deselectObject, getClickedFurniture,
  changeMaterialColor, setView, setupDrag,
  placedFurniture, selectedObject,
  scene, camera, renderer, controls
};
