import sys, os

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title> InteriorDesign Pro</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Microsoft YaHei,sans-serif;overflow:hidden;background:#1a1a2e;color:#fff;height:100vh;display:flex;flex-direction:column}
#header{height:44px;background:rgba(26,26,46,0.97);border-bottom:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;padding:0 14px;gap:10px;flex-shrink:0;z-index:200}
#header .logo{font-size:15px;font-weight:700;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
#header .spacer{flex:1}
.btn{padding:4px 12px;border:1px solid rgba(255,255,255,0.2);border-radius:5px;background:rgba(255,255,255,0.06);color:#fff;cursor:pointer;font-size:12px;font-family:inherit}
.btn:hover{background:rgba(255,255,255,0.12)}
.btn-p{background:linear-gradient(135deg,#667eea,#764ba2);border:none}
#main{flex:1;display:flex;overflow:hidden}
#panel-3d{flex:1;position:relative;background:#1a1a2e}
#canvas-3d{width:100%;height:100%;display:block}
#panel-3d .toolbar{position:absolute;top:6px;left:50%;transform:translateX(-50%);z-index:100;display:flex;gap:3px;background:rgba(0,0,0,0.6);padding:3px 6px;border-radius:6px}
.tool-btn{padding:3px 8px;border:1px solid transparent;border-radius:4px;background:transparent;color:rgba(255,255,255,0.7);cursor:pointer;font-size:11px;font-family:inherit}
.tool-btn:hover{background:rgba(255,255,255,0.1);color:#fff}
.tool-btn.active{border-color:#667eea;color:#fff;background:rgba(102,126,234,0.2)}
#sidebar{width:240px;display:flex;flex-direction:column;border-left:1px solid rgba(255,255,255,0.1);background:rgba(22,22,40,0.97);flex-shrink:0}
#sidebar .tabs{display:flex;border-bottom:1px solid rgba(255,255,255,0.1)}
#sidebar .tabs button{flex:1;padding:7px;border:none;background:transparent;color:rgba(255,255,255,0.5);cursor:pointer;font-size:11px;font-family:inherit;border-bottom:2px solid transparent}
#sidebar .tabs button.active{color:#fff;border-bottom-color:#667eea;background:rgba(102,126,234,0.08)}
#sidebar .tab-content{flex:1;overflow-y:auto;padding:6px}
.furn-grid{display:grid;grid-template-columns:1fr 1fr;gap:4px}
.furn-card{border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:6px;cursor:pointer;text-align:center;background:rgba(255,255,255,0.02)}
.furn-card:hover{border-color:#667eea;background:rgba(102,126,234,0.08)}
.furn-card .icon{font-size:24px}
.furn-card .name{font-size:10px;color:rgba(255,255,255,0.7)}
.mat-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px}
.mat-swatch{height:32px;border-radius:6px;cursor:pointer;border:2px solid transparent}
.mat-swatch:hover{border-color:#fff}
.mat-label{font-size:8px;text-align:center;color:rgba(255,255,255,0.4)}
#item-info{background:rgba(0,0,0,0.3);border-radius:6px;padding:8px;margin-top:6px;font-size:11px;display:none}
#item-info .row{display:flex;justify-content:space-between;padding:2px 0;color:rgba(255,255,255,0.6)}
#hint{position:fixed;bottom:10px;left:50%;transform:translateX(-50%);z-index:100;background:rgba(0,0,0,0.5);padding:4px 14px;border-radius:14px;font-size:10px;color:rgba(255,255,255,0.4);pointer-events:none}
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.15);border-radius:2px}
</style>
</head>
<body>

<div id="header">
  <span class="logo"> InteriorDesign Pro</span>
  <span style="font-size:10px;color:rgba(255,255,255,0.3)">2D/3D 编辑器</span>
  <span class="spacer"></span>
  <button class="btn" onclick="saveProject()"> 保存</button>
  <button class="btn" onclick="loadProject()"> 打开</button>
  <button class="btn btn-p" onclick="exportDXF()"> DXF</button>
</div>

<div id="main">
  <div id="panel-3d">
    <div class="toolbar">
      <button class="tool-btn active" onclick="setView('3d')"> 3D</button>
      <button class="tool-btn" onclick="setView('top')"> 俯视</button>
      <button class="tool-btn" onclick="setView('front')"> 正面</button>
      <span style="width:4px"></span>
      <button class="tool-btn" onclick="toggleRotate()"> 漫游</button>
      <button class="tool-btn" onclick="snapshot()"> 截图</button>
    </div>
    <canvas id="canvas-3d"></canvas>
  </div>

  <div id="sidebar">
    <div class="tabs">
      <button class="active" onclick="switchTab('furniture',this)"> 家具</button>
      <button onclick="switchTab('materials',this)"> 材质</button>
      <button onclick="switchTab('info',this)"> 信息</button>
    </div>
    <div class="tab-content" id="tab-furniture"></div>
    <div class="tab-content" id="tab-materials" style="display:none"></div>
    <div class="tab-content" id="tab-info" style="display:none">
      <div id="project-stats" style="font-size:11px"></div>
      <div id="item-info"></div>
    </div>
  </div>
</div>

<div id="hint"> 点击家具拖拽移动  |  右键旋转  |  滚轮缩放  |  选中后改材质</div>

<script type="importmap">{"imports":{"three":"./lib/three.module.js","three/addons/":"./lib/"}}</script>
<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/OrbitControls.js";

// ========== CONFIG ==========
const CATALOG = [
  {id:"sofa1",name:"北欧沙发",cat:"sofas",icon:" ",w:2.2,h:0.85,d:0.9,color:"#C8B8A4"},
  {id:"sofa2",name:"L型沙发",cat:"sofas",icon:" ",w:2.8,h:0.82,d:1.8,color:"#A09080"},
  {id:"sofa3",name:"单人沙发",cat:"sofas",icon:" ",w:0.85,h:0.8,d:0.85,color:"#B8A898"},
  {id:"table1",name:"餐桌",cat:"tables",icon:" ",w:1.8,h:0.76,d:0.9,color:"#C4A882"},
  {id:"table2",name:"茶几",cat:"tables",icon:" ",w:1.2,h:0.42,d:0.6,color:"#B89B78"},
  {id:"table3",name:"边几",cat:"tables",icon:" ",w:0.5,h:0.55,d:0.5,color:"#D4B896"},
  {id:"chair1",name:"餐椅",cat:"chairs",icon:" ",w:0.48,h:0.82,d:0.52,color:"#C4A882"},
  {id:"chair2",name:"吧凳",cat:"chairs",icon:" ",w:0.38,h:0.65,d:0.38,color:"#8B6F4E"},
  {id:"bed1",name:"双人床",cat:"beds",icon:" ",w:2.0,h:0.5,d:1.8,color:"#D2B48C"},
  {id:"bed2",name:"单人床",cat:"beds",icon:" ",w:1.2,h:0.5,d:2.0,color:"#D2B48C"},
  {id:"cabinet1",name:"衣柜",cat:"cabinets",icon:" ",w:1.8,h:2.4,d:0.6,color:"#C4A882"},
  {id:"cabinet2",name:"书柜",cat:"cabinets",icon:" ",w:0.8,h:1.8,d:0.35,color:"#C4A882"},
  {id:"lamp1",name:"吊灯",cat:"lighting",icon:" ",w:0.4,h:0.35,d:0.4,color:"#2D2D2D"},
  {id:"lamp2",name:"落地灯",cat:"lighting",icon:" ",w:0.35,h:1.6,d:0.35,color:"#3A3A3A"},
  {id:"lamp3",name:"台灯",cat:"lighting",icon:" ",w:0.25,h:0.45,d:0.25,color:"#C4A882"},
  {id:"deco1",name:"盆栽",cat:"decor",icon:" ",w:0.35,h:0.8,d:0.35,color:"#8FA584"},
  {id:"deco2",name:"花瓶",cat:"decor",icon:" ",w:0.2,h:0.4,d:0.2,color:"#C67D5B"},
  {id:"deco3",name:"地毯",cat:"decor",icon:" ",w:2.5,h:0.02,d:1.8,color:"#D4C8B8"},
];
const MATERIALS = {"橡木Oak":"#C4A882","胡桃木":"#6B4E37","枫木":"#D4B896","亚麻":"#E8DFD5","天鹅绒":"#7B6B8A","皮革":"#8B5E3C","大理石":"#E0D8D0","混凝土":"#A0A0A0","纯棉":"#F0EDE8"};
const ROOM = {w:10,h:3.0,d:8};

// ========== THREE.JS SCENE ==========
const c3d = document.getElementById("canvas-3d");
const scene = new THREE.Scene();
scene.background = new THREE.Color("#F0EBE5");

const camera = new THREE.PerspectiveCamera(50,c3d.clientWidth/c3d.clientHeight,0.1,100);
camera.position.set(6,5,8);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(c3d.clientWidth,c3d.clientHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
c3d.appendChild(renderer.domElement);

const controls = new OrbitControls(camera,renderer.domElement);
controls.target.set(0,1.2,0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI/2.05;
controls.minDistance = 1;
controls.maxDistance = 20;
controls.update();

// Lights
scene.add(new THREE.AmbientLight(0x404060,0.5));
scene.add(new THREE.HemisphereLight(0x8888ff,0x444422,0.6));
const sun = new THREE.DirectionalLight(0xffeedd,1.2);
sun.position.set(5,12,8);
sun.castShadow = true;
sun.shadow.mapSize.set(1024,1024);
sun.shadow.camera.near = 0.1; sun.shadow.camera.far = 30;
sun.shadow.camera.left = -8; sun.shadow.camera.right = 8;
sun.shadow.camera.top = 8; sun.shadow.camera.bottom = -8;
scene.add(sun);
const fill = new THREE.DirectionalLight(0x4488ff,0.3);
fill.position.set(-3,4,-5);
scene.add(fill);

// Room
const roomG = new THREE.Group();
scene.add(roomG);
const floor = new THREE.Mesh(new THREE.PlaneGeometry(ROOM.w-0.1,ROOM.d-0.1),new THREE.MeshStandardMaterial({color:"#E8E0D6",roughness:0.8}));
floor.rotation.x = -Math.PI/2;
floor.receiveShadow = true;
roomG.add(floor);

function makeWall(w,h,x,y,z,ry){
  const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,0.1),new THREE.MeshStandardMaterial({color:"#F0EBE5",roughness:0.9}));
  m.position.set(x,y,z);
  if(ry) m.rotation.y = ry;
  m.castShadow = true; m.receiveShadow = true;
  roomG.add(m);
}
const hw=ROOM.w/2, hd=ROOM.d/2;
makeWall(ROOM.w,ROOM.h,0,ROOM.h/2,-hd);
makeWall(ROOM.w,ROOM.h,0,ROOM.h/2,hd);
makeWall(ROOM.d,ROOM.h,-hw,ROOM.h/2,0,Math.PI/2);
makeWall(ROOM.d,ROOM.h,hw,ROOM.h/2,0,Math.PI/2);

// Window
const win = new THREE.Mesh(new THREE.BoxGeometry(2.5,1.5,0.05),new THREE.MeshStandardMaterial({color:"#87CEEB",roughness:0.1,metalness:0.3,transparent:true,opacity:0.3}));
win.position.set(1,1.8,hd-0.03);
roomG.add(win);

// ========== FURNITURE BUILDER ==========
function wood(c){return new THREE.MeshStandardMaterial({color:c,roughness:0.7,metalness:0})}
function fabric(c){return new THREE.MeshStandardMaterial({color:c,roughness:0.9,metalness:0})}
function metal(c){return new THREE.MeshStandardMaterial({color:c,roughness:0.3,metalness:0.7})}

function buildFurniture(d){
  const g = new THREE.Group();
  const M = fabric(d.color), W = wood(d.color), LM = metal("#2D2D2D");
  const leg = (h)=>new THREE.Mesh(new THREE.CylinderGeometry(0.02,0.02,h||0.12),LM);

  if(d.cat==="sofas"){
    const b = new THREE.Mesh(new THREE.BoxGeometry(d.w,0.3,d.d),M);
    b.position.y=0.25;b.castShadow=true;g.add(b);
    const bk = new THREE.Mesh(new THREE.BoxGeometry(d.w,0.4,0.08),M);
    bk.position.set(0,0.55,-d.d/2+0.04);bk.castShadow=true;g.add(bk);
    [-1,1].forEach(x=>{const l=leg();l.position.set(x*(d.w/2-0.06),0.06,d.d/2-0.06);g.add(l);const l2=leg();l2.position.set(x*(d.w/2-0.06),0.06,-d.d/2+0.06);g.add(l2)});
  } else if(d.cat==="tables"){
    const t = new THREE.Mesh(new THREE.BoxGeometry(d.w,0.04,d.d),W);
    t.position.y=d.h;t.castShadow=true;g.add(t);
    [-1,1].forEach(x=>[-1,1].forEach(z=>{const l=new THREE.Mesh(new THREE.CylinderGeometry(0.025,0.025,d.h-0.02),LM);l.position.set(x*(d.w/2-0.05),(d.h-0.02)/2,z*(d.d/2-0.05));l.castShadow=true;g.add(l)}));
  } else if(d.cat==="chairs"){
    const seat = new THREE.Mesh(new THREE.BoxGeometry(d.w*0.8,0.04,d.d*0.8),W);
    const sh=0.45;seat.position.y=sh;seat.castShadow=true;g.add(seat);
    const bk = new THREE.Mesh(new THREE.BoxGeometry(d.w*0.7,0.35,0.03),W);
    bk.position.set(0,sh+0.18,-d.d*0.4);bk.castShadow=true;g.add(bk);
    [-1,1].forEach(x=>[-1,1].forEach(z=>{const l=new THREE.Mesh(new THREE.CylinderGeometry(0.015,0.015,sh),W);l.position.set(x*(d.w*0.35),sh/2,z*(d.d*0.35));g.add(l)}));
  } else if(d.cat==="beds"){
    const b = new THREE.Mesh(new THREE.BoxGeometry(d.w,0.3,d.d),fabric(d.color));
    b.position.y=0.25;b.castShadow=true;g.add(b);
    const hd2 = new THREE.Mesh(new THREE.BoxGeometry(d.w,0.5,0.08),wood(d.color));
    hd2.position.set(0,0.5,-d.d/2+0.04);hd2.castShadow=true;g.add(hd2);
    const p = new THREE.Mesh(new THREE.BoxGeometry(d.w*0.6,0.12,0.35),fabric("#FFFFFF"));
    p.position.set(0,0.46,-d.d/2+0.25);g.add(p);
  } else if(d.cat==="cabinets"){
    const b = new THREE.Mesh(new THREE.BoxGeometry(d.w,d.h,d.d),wood(d.color));
    b.position.y=d.h/2;b.castShadow=true;g.add(b);
  } else if(d.cat==="lighting"){
    if(d.id==="lamp1"){
      const s = new THREE.Mesh(new THREE.ConeGeometry(0.25,0.3,32,1,true),metal(d.color));
      s.position.y=ROOM.h-0.15;s.castShadow=true;g.add(s);
      const blb = new THREE.Mesh(new THREE.SphereGeometry(0.04),new THREE.MeshStandardMaterial({color:"#FFF5E0",emissive:"#FFF5E0",emissiveIntensity:0.5}));
      blb.position.y=ROOM.h-0.25;g.add(blb);
      const pl = new THREE.PointLight("#FFF0D4",0.5,5);
      pl.position.y=ROOM.h-0.25;g.add(pl);
    } else if(d.id==="lamp2"){
      const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.015,0.015,d.h),metal(d.color));
      pole.position.y=d.h/2;g.add(pole);
      const base = new THREE.Mesh(new THREE.CylinderGeometry(0.12,0.14,0.02),metal(d.color));
      base.position.y=0.01;g.add(base);
      const shd = new THREE.Mesh(new THREE.ConeGeometry(0.15,0.2,32,1,true),fabric("#E8DFD5"));
      shd.position.y=d.h-0.1;shd.castShadow=true;g.add(shd);
      const pl = new THREE.PointLight("#FFF0D4",0.3,4);
      pl.position.y=d.h-0.05;g.add(pl);
    } else {
      const wm = wood(d.color);
      const b = new THREE.Mesh(new THREE.CylinderGeometry(0.06,0.08,0.05),wm);b.position.y=0.025;g.add(b);
      const body = new THREE.Mesh(new THREE.CylinderGeometry(0.025,0.04,0.15),wm);body.position.y=0.12;g.add(body);
    }
  } else {
    if(d.id==="deco1"){
      const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.1,0.08,0.2,16),wood("#8B7D6B"));
      pot.position.y=0.1;pot.castShadow=true;g.add(pot);
      const lv = new THREE.Mesh(new THREE.SphereGeometry(0.15,8,8),fabric(d.color));
      lv.position.y=0.55;lv.castShadow=true;g.add(lv);
    } else if(d.id==="deco2"){
      const pts=[];for(let i=0;i<10;i++){const t=i/9;pts.push(new THREE.Vector2(0.05+0.06*Math.sin(t*Math.PI),t*d.h));}
      const v = new THREE.Mesh(new THREE.LatheGeometry(pts,24),new THREE.MeshStandardMaterial({color:d.color,roughness:0.4,metalness:0.1}));
      v.castShadow=true;g.add(v);
    } else {
      const r = new THREE.Mesh(new THREE.BoxGeometry(d.w,d.h,d.d),fabric(d.color));
      r.position.y=d.h/2;r.receiveShadow=true;g.add(r);
    }
  }
  g.userData={...d,placed:true};
  g.traverse(c=>{if(c.isMesh){c.castShadow=true;c.userData.furnitureGroup=g}});
  return g;
}

// ========== FURNITURE MANAGEMENT ==========
let placed = [], selected = null;

function addFurniture(d){
  const m = buildFurniture(d);
  const margin=0.5;
  m.position.set((Math.random()-0.5)*(ROOM.w-margin*2),0,(Math.random()-0.5)*(ROOM.d-margin*2));
  scene.add(m);
  placed.push(m);
  updateStats();
  return m;
}

function removeFurniture(m){
  scene.remove(m);
  placed=placed.filter(f=>f!==m);
  if(selected===m) selected=null;
  updateStats();
}

// ========== RAYCASTER ==========
const ray = new THREE.Raycaster(), ms = new THREE.Vector2();
const fp = new THREE.Plane(new THREE.Vector3(0,1,0),0);
const ip = new THREE.Vector3();
let dragging=false, dragObj=null, dragOff=new THREE.Vector3(), mDown=new THREE.Vector2(), wasDrag=false;

function getFurnAt(e){
  const r=c3d.getBoundingClientRect();
  ms.x=((e.clientX-r.left)/r.width)*2-1;
  ms.y=-((e.clientY-r.top)/r.height)*2+1;
  ray.setFromCamera(ms,camera);
  const meshes=[];
  placed.forEach(g=>g.traverse(c=>{if(c.isMesh)meshes.push(c)}));
  const hits=ray.intersectObjects(meshes);
  if(hits.length>0){
    let o=hits[0].object;
    while(o.parent&&!o.userData.placed)o=o.parent;
    if(o.userData.placed)return o;
  }
  return null;
}

function selectObj(obj){
  deselectObj();
  selected=obj;
  obj.traverse(c=>{
    if(c.isMesh&&c._origM===undefined){
      c._origM=c.material;
      c.material=c.material.clone();
      c.material.emissive=new THREE.Color("#667eea");
      c.material.emissiveIntensity=0.2;
    }
  });
  showInfo(obj.userData);
}
function deselectObj(){
  if(!selected)return;
  selected.traverse(c=>{
    if(c.isMesh&&c._origM!==undefined){
      c.material.dispose();
      c.material=c._origM;
      delete c._origM;
    }
  });
  selected=null;
  document.getElementById("item-info").style.display="none";
}

c3d.addEventListener("pointerdown",e=>{
  mDown.set(e.clientX,e.clientY);wasDrag=false;
  const o=getFurnAt(e);
  if(o){
    dragging=true;dragObj=o;controls.enabled=false;
    const r=c3d.getBoundingClientRect();
    ms.x=((e.clientX-r.left)/r.width)*2-1;
    ms.y=-((e.clientY-r.top)/r.height)*2+1;
    ray.setFromCamera(ms,camera);
    ray.ray.intersectPlane(fp,ip);
    dragOff.copy(o.position).sub(ip);
    c3d.style.cursor="grabbing";
  }
});
c3d.addEventListener("pointermove",e=>{
  const dx=e.clientX-mDown.x,dy=e.clientY-mDown.y;
  if(Math.abs(dx)>3||Math.abs(dy)>3)wasDrag=true;
  if(dragging&&dragObj){
    const r=c3d.getBoundingClientRect();
    ms.x=((e.clientX-r.left)/r.width)*2-1;
    ms.y=-((e.clientY-r.top)/r.height)*2+1;
    ray.setFromCamera(ms,camera);
    ray.ray.intersectPlane(fp,ip);
    const np=ip.add(dragOff);
    const m=0.3;
    dragObj.position.x=Math.max(-ROOM.w/2+m,Math.min(ROOM.w/2-m,np.x));
    dragObj.position.z=Math.max(-ROOM.d/2+m,Math.min(ROOM.d/2-m,np.z));
  } else if(!dragging){
    c3d.style.cursor=getFurnAt(e)?"grab":"default";
  }
});
c3d.addEventListener("pointerup",e=>{
  if(dragging){
    c3d.style.cursor="grab";dragging=false;controls.enabled=true;
    if(!wasDrag){deselectObj();selectObj(dragObj);}
    dragObj=null;
  } else if(!wasDrag)deselectObj();
});

// ========== VIEW CONTROL ==========
window.setView=function(m){
  document.querySelectorAll("#panel-3d .toolbar .tool-btn").forEach(b=>b.classList.remove("active"));
  if(m==="top"){camera.position.set(0,12,0.01);controls.target.set(0,0,0)}
  else if(m==="front"){camera.position.set(0,2,10);controls.target.set(0,1.5,0)}
  else{camera.position.set(6,5,8);controls.target.set(0,1.2,0)}
  controls.update();
};
window.toggleRotate=function(){controls.autoRotate=!controls.autoRotate;controls.autoRotateSpeed=0.8};
window.snapshot=function(){renderer.render(scene,camera);const a=document.createElement("a");a.download="snapshot.png";a.href=renderer.domElement.toDataURL("image/png");a.click()};

// ========== ROTATE / DELETE ==========
window.rotateSel=function(d){if(!selected)return;selected.rotation.y+=d*Math.PI/180};
window.delSel=function(){if(!selected)return;removeFurniture(selected);document.getElementById("item-info").style.display="none"};

// ========== UI ==========
function buildCatalog(){
  const c=document.getElementById("tab-furniture");c.innerHTML="";
  const cats=[...new Set(CATALOG.map(f=>f.cat))];
  const catNames={sofas:" 沙发",tables:" 桌几",chairs:" 椅子",beds:" 床",cabinets:" 柜子",lighting:" 灯具",decor:" 装饰"};
  for(const cat of cats){
    const h=document.createElement("div");
    h.style.cssText="font-size:11px;color:rgba(255,255,255,0.4);margin:4px 0 3px";
    h.textContent=catNames[cat]||cat;c.appendChild(h);
    const g=document.createElement("div");g.className="furn-grid";
    CATALOG.filter(f=>f.cat===cat).forEach(f=>{
      const cd=document.createElement("div");cd.className="furn-card";
      cd.innerHTML=`<div class="icon">${f.icon}</div><div class="name">${f.name}</div>`;
      cd.onclick=()=>addFurniture(f);
      g.appendChild(cd);
    });
    c.appendChild(g);
  }
}

function buildMaterials(){
  const c=document.getElementById("tab-materials");c.innerHTML="";
  const g=document.createElement("div");g.className="mat-grid";
  for(const [n,hex] of Object.entries(MATERIALS)){
    const w=document.createElement("div");w.style.textAlign="center";
    const s=document.createElement("div");s.className="mat-swatch";s.style.background=hex;
    s.onclick=()=>{if(selected){selected.traverse(c=>{if(c.isMesh)c.material.color.set(hex)});document.querySelectorAll(".mat-swatch").forEach(x=>x.classList.remove("active"));s.classList.add("active")}};
    w.appendChild(s);
    const l=document.createElement("div");l.className="mat-label";l.textContent=n;
    w.appendChild(l);g.appendChild(w);
  }
  c.appendChild(g);
}

function showInfo(d){
  const i=document.getElementById("item-info");i.style.display="block";
  i.innerHTML=`<div class="row"><span>名称</span><span>${d.name}</span></div>
    <div class="row"><span>尺寸</span><span>${(d.w*100).toFixed(0)}x${(d.d*100).toFixed(0)}x${(d.h*100).toFixed(0)}</span></div>
    <div style="margin-top:4px"><button class="tool-btn" onclick="rotateSel(-15)" style="padding:2px 6px;font-size:10px"> 左转</button>
    <button class="tool-btn" onclick="rotateSel(15)" style="padding:2px 6px;font-size:10px"> 右转</button>
    <button class="tool-btn" onclick="delSel()" style="padding:2px 6px;font-size:10px;color:#e74c3c"> 删除</button></div>`;
}

function updateStats(){
  document.getElementById("project-stats").innerHTML=
    `<div style="margin-bottom:4px">  项目统计</div>
    <div class="row"><span>家具</span><span>${placed.length}</span></div>
    <div class="row"><span>房间</span><span>4</span></div>`;
}

window.switchTab=function(t,btn){
  document.querySelectorAll("#sidebar .tabs button").forEach(b=>b.classList.remove("active"));
  btn.classList.add("active");
  ["furniture","materials","info"].forEach(x=>document.getElementById("tab-"+x).style.display=x===t?"block":"none");
};

// ========== SAVE/LOAD/EXPORT ==========
window.saveProject=function(){
  const d={furniture:placed.map(m=>({...m.userData,x:m.position.x,z:m.position.z,ry:m.rotation.y}))};
  const a=document.createElement("a");a.download="project.json";a.href=URL.createObjectURL(new Blob([JSON.stringify(d,null,2)],{type:"application/json"}));a.click();
};
window.loadProject=function(){
  const i=document.createElement("input");i.type="file";i.accept=".json";
  i.onchange=async e=>{
    const d=JSON.parse(await e.target.files[0].text());
    [...placed].forEach(m=>removeFurniture(m));
    if(d.furniture) for(const f of d.furniture){const m=addFurniture(f);if(f.x!==undefined){m.position.set(f.x,0,f.z);m.rotation.y=f.ry||0}}
    updateStats();
  };
  i.click();
};
window.exportDXF=function(){
  const d={furniture:placed.map(m=>({...m.userData,x:m.position.x,z:m.position.z}))};
  const a=document.createElement("a");a.download="interior_data.json";a.href=URL.createObjectURL(new Blob([JSON.stringify(d,null,2)],{type:"application/json"}));a.click();
  alert("DXF 导出:\n1. 数据 JSON 已下载\n2. 运行: python interior_run.py --input interior_data.json");
};

// ========== INIT ==========
buildCatalog(); buildMaterials();
setTimeout(()=>{
  ["sofa1","table1","chair1","deco1","lamp2"].forEach(id=>{
    const d=CATALOG.find(f=>f.id===id);if(d)addFurniture(d);
  });
  updateStats();
},100);

// ========== ANIMATION ==========
function animate(){requestAnimationFrame(animate);controls.update();renderer.render(scene,camera)}
animate();
console.log(" InteriorDesign Pro loaded");
</script>
</body>
</html>"""
with open("E:\\CAD自动化制图\\interior_pro.html", "w", encoding="utf-8") as f:
    f.write(HTML)
print(f"Written: {len(HTML)} bytes")
