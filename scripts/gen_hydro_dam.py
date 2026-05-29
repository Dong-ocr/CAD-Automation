"""Generate Hydropower Station 3D Dam - Three.js immersive scene"""
import json, os, math

os.makedirs("output/hydro", exist_ok=True)

# ===== DAM PARAMETERS =====
dam = {
    "name": "岩泊渡水电站",
    "nameEn": "Yanbodu Hydropower Station",
    "damType": "混凝土重力坝",
    "damHeight": 45.0,      # meters
    "crestElevation": 185.5,
    "baseElevation": 140.5,
    "crestWidth": 5.0,
    "baseWidth": 35.0,
    "damLength": 120.0,      # along crest
    "upstreamSlope": 0.05,
    "downstreamSlope": 0.78,
    "nwl": 183.0,            # normal water level
    "nwlElevation": 183.0,
    "flwl": 185.0,           # flood water level
    "tailwater": 142.0,
    "spillwayWidth": 24.0,
    "spillwayGates": 3,      # number of gates
    "installedCapacity": "3×20MW",
    "turbineType": "混流式",
    "penstockDiameter": 3.5,  # meters
    "centerX": 0,
    "centerZ": 0,
}

# Generate the HTML
html_parts = []
A = html_parts.append

A('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>岩泊渡水电站 - 3D 大坝</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#070710;color:#fff;font-family:'Microsoft YaHei','Inter',system-ui,sans-serif;overflow:hidden;height:100vh}
#info{position:absolute;top:20px;left:50%;transform:translateX(-50%);z-index:10;text-align:center;pointer-events:none}
#info h1{font-size:22px;font-weight:600;background:linear-gradient(135deg,#667eea,#e74c3c);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-shadow:none;letter-spacing:2px}
#info p{font-size:11px;color:rgba(255,255,255,0.3);margin-top:2px;letter-spacing:1px}
#stats{position:absolute;bottom:24px;left:24px;z-index:10;font-size:10px;color:rgba(255,255,255,0.2);line-height:1.8;pointer-events:none}
#stats .sv{color:rgba(255,255,255,0.6)}
#legend{position:absolute;bottom:24px;right:24px;z-index:10;font-size:10px;color:rgba(255,255,255,0.3);line-height:2;pointer-events:none}
.ld{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:middle}
#controls{position:absolute;top:80px;right:20px;z-index:10;display:flex;flex-direction:column;gap:4px}
.ct{padding:5px 10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:4px;color:rgba(255,255,255,0.5);cursor:pointer;font-size:10px;font-family:inherit;transition:.2s}
.ct:hover{background:rgba(102,126,234,0.15);border-color:#667eea;color:#fff}
.ct.a{background:rgba(102,126,234,0.2);border-color:#667eea;color:#fff}
canvas{display:block}
#loading{position:fixed;inset:0;z-index:999;background:#070710;display:flex;flex-direction:column;align-items:center;justify-content:center;transition:opacity .8s}
#loading.h{opacity:0;pointer-events:none}
.spin{width:40px;height:40px;border:2px solid rgba(102,126,234,0.1);border-top-color:#667eea;border-radius:50%;animation:s 1s linear infinite}
@keyframes s{to{transform:rotate(360deg)}}
#loading p{margin-top:16px;font-size:12px;color:rgba(255,255,255,0.3)}
</style>
</head>
<body>
<div id=loading><div class=spin></div><p>加载 3D 场景...</p></div>
<div id=info><h1>岩泊渡水电站 · 3D 大坝</h1><p>Yanbodu Hydropower Station — Gravity Dam</p></div>
<div id=controls>
<div class="ct a" onclick="viewFull()">全景</div>
<div class="ct" onclick="viewUp()">俯瞰</div>
<div class="ct" onclick="viewDown()">下游</div>
<div class="ct" onclick="viewSide()">侧面</div>
<div class="ct" onclick="toggleWater()">水位</div>
<div class="ct" onclick="toggleAnnot()">标注</div>
</div>
<div id=stats>
<div>坝型: <span class=sv>''' + dam["damType"] + '''</span></div>
<div>坝高: <span class=sv>''' + str(dam["damHeight"]) + '''m</span></div>
<div>坝顶高程: <span class=sv>''' + str(dam["crestElevation"]) + '''m</span></div>
<div>装机: <span class=sv>''' + dam["installedCapacity"] + '''</span></div>
<div>溢洪道: <span class=sv>''' + str(dam["spillwayGates"]) + '''孔×''' + str(dam["spillwayWidth"]//dam["spillwayGates"]) + '''m</span></div>
</div>
<div id=legend>
<div><span class=ld style="background:#5a7eff"></span>坝体</div>
<div><span class=ld style="background:#3d8c40"></span>地形</div>
<div><span class=ld style="background:#2a6b9e"></span>水面</div>
<div><span class=ld style="background:#e8c840"></span>闸门</div>
<div><span class=ld style="background:#888"></span>厂房</div>
</div>
<script type="importmap">
{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}
</script>
<script type="module">
''')

# Main Three.js code
A('''
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CSS2DRenderer, CSS2DObject } from "three/addons/renderers/CSS2DRenderer.js";

// === DIMENSIONS ===
const H = 45, CW = 5, BW = 35, DL = 120;
const EL_CREST = 185.5, EL_BASE = 140.5;
const NWL = 183.0;
const UP_SLOPE = 0.05, DOWN_SLOPE = 0.78;
const SW_W = 24, SW_N = 3;

// Calculate dam section coordinates
// Origin at heel (upstream base)
const heelX = 0;
const toeX = BW;
const crestUpX = CW + H * UP_SLOPE;
const crestDownX = CW + H * UP_SLOPE + CW;
const crestY = 0; // at crest elevation

// === SCENE SETUP ===
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x070710);
scene.fog = new THREE.Fog(0x070710, 300, 600);

const camera = new THREE.PerspectiveCamera(40, innerWidth / innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.8;
document.body.appendChild(renderer.domElement);

const labelRenderer = new CSS2DRenderer();
labelRenderer.setSize(innerWidth, innerHeight);
labelRenderer.domElement.style.position = "absolute";
labelRenderer.domElement.style.top = "0";
labelRenderer.domElement.style.pointerEvents = "none";
document.body.appendChild(labelRenderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 20;
controls.maxDistance = 300;
controls.target.set(DL/2, 0, 0);
camera.position.set(DL/2 + 60, 40, 80);
controls.update();

// === LIGHTS ===
scene.add(new THREE.AmbientLight(0x404060, 0.4));
scene.add(new THREE.HemisphereLight(0x667eea, 0x08080f, 0.6));
const sun = new THREE.DirectionalLight(0xffeedd, 2.0);
sun.position.set(80, 100, 60);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 0.5;
sun.shadow.camera.far = 300;
sun.shadow.camera.left = -100;
sun.shadow.camera.right = 100;
sun.shadow.camera.top = 100;
sun.shadow.camera.bottom = -100;
scene.add(sun);
const fill = new THREE.DirectionalLight(0x8888ff, 0.3);
fill.position.set(-30, 40, -20);
scene.add(fill);

// === TERRAIN ===
function createTerrain() {
  const group = new THREE.Group();
  const geo = new THREE.PlaneGeometry(400, 300, 60, 40);
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i);
    const z = pos.getY(i);
    const dx = x - DL/2;
    // Valley shape: V-shaped with dam site
    let y = 0;
    const dist = Math.abs(z);
    if (dist < 50) {
      // River valley
      y = -H * 0.15 * (1 - dist/50);
      // Add some roughness
      y += Math.sin(x * 0.3) * 1.5 + Math.cos(z * 0.5) * 1.0;
    } else {
      // Hillside
      y = (dist - 50) * 0.15 + Math.sin(x * 0.2) * 2;
    }
    // Dam area flattening
    if (x > -10 && x < DL + 10 && Math.abs(z) < 30) {
      y = Math.max(y, -H * 0.15);
    }
    pos.setY(i, y);
  }
  geo.computeVertexNormals();
  const mat = new THREE.MeshPhysicalMaterial({
    color: 0x2d4a2d,
    roughness: 0.9,
    metalness: 0,
    flatShading: false,
    side: THREE.DoubleSide,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.rotation.x = -Math.PI / 2;
  mesh.position.set(0, -H * 0.15, -150);
  mesh.receiveShadow = true;
  group.add(mesh);
  return group;
}
scene.add(createTerrain());

// === DAM BODY ===
function createDam() {
  const group = new THREE.Group();
  
  // Main dam body - extruded along Z axis
  const shape = new THREE.Shape();
  const s = 1; // scale factor for display
  
  // Dam profile points (gravity dam section)
  // [x, y] where y is elevation from base
  const profile = [
    [0, 0],                         // heel
    [BW, 0],                        // toe
    [BW - H * 0.78, H],            // downstream crest
    [CW + H * 0.05, H],            // upstream crest
    [H * 0.05, H * 0.3],           // upstream slope break
    [0, 0],                         // close at heel
  ];
  
  // Scale for display
  const sc = 0.5;
  shape.moveTo(profile[0][0]*sc, profile[0][1]*sc);
  for (let i = 1; i < profile.length; i++) {
    shape.lineTo(profile[i][0]*sc, profile[i][1]*sc);
  }
  
  const extrudeSettings = {
    steps: 1,
    depth: DL * sc,
    bevelEnabled: true,
    bevelThickness: 0.5,
    bevelSize: 0.3,
    bevelSegments: 3,
  };
  
  const geo = new THREE.ExtrudeGeometry(shape, extrudeSettings);
  const mat = new THREE.MeshPhysicalMaterial({
    color: 0x5a7eff,
    metalness: 0.05,
    roughness: 0.4,
    clearcoat: 0.1,
    side: THREE.DoubleSide,
  });
  const mesh = new THREE.Mesh(geo, mat);
  // Position: centered on Z, base at y=-H*sc
  mesh.position.set(-profile[0][0]*sc, -H*sc*0.5, -DL*sc/2);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  group.add(mesh);
  
  // Spillway section (cutout)
  const spillCenter = DL/2;
  const swShape = new THREE.Shape();
  const sw = SW_W * sc;
  swShape.moveTo(0, 0);
  swShape.lineTo(sw, 0);
  swShape.lineTo(sw, H * 0.3 * sc);
  swShape.lineTo(0, H * 0.3 * sc);
  swShape.lineTo(0, 0);
  
  // Spillway channel
  const spExtrude = {
    steps: 1,
    depth: 3,
    bevelEnabled: false,
  };
  const spGeo = new THREE.ExtrudeGeometry(swShape, spExtrude);
  const spMat = new THREE.MeshPhysicalMaterial({
    color: 0x8a9ccc, roughness: 0.6, metalness: 0.1,
  });
  // Place spillway section
  for (let g = 0; g < SW_N; g++) {
    const gx = (spillCenter - sw/2*SW_N + g * sw + sw/2) * sc;
    const sp = new THREE.Mesh(spGeo, spMat);
    sp.position.set(gx, -H*sc*0.5 + 0.1, -DL*sc/2);
    group.add(sp);
    
    // Gate (golden)
    const gate = new THREE.Mesh(
      new THREE.BoxGeometry(sw*0.8*sc, H*0.25*sc, 0.5),
      new THREE.MeshPhysicalMaterial({color:0xe8c840, metalness:0.8, roughness:0.2})
    );
    gate.position.set(gx, -H*sc*0.5 + H*0.15*sc, -DL*sc/2 + 0.3);
    group.add(gate);
  }
  
  // Crest detail
  const crestMat = new THREE.MeshPhysicalMaterial({color:0x7a8acc, roughness:0.5});
  const crest = new THREE.Mesh(
    new THREE.BoxGeometry((CW+H*0.05)*sc, 0.5, DL*sc),
    crestMat
  );
  crest.position.set((CW+H*0.05)*sc/2, H*sc*0.5, 0);
  group.add(crest);
  
  return group;
}
const damGroup = createDam();
scene.add(damGroup);

// === POWERHOUSE ===
function createPowerhouse() {
  const g = new THREE.Group();
  const phMat = new THREE.MeshPhysicalMaterial({color:0x888888, roughness:0.7, metalness:0.1});
  const roofMat = new THREE.MeshPhysicalMaterial({color:0x555555, roughness:0.5});
  
  // Main building
  const b = new THREE.Mesh(new THREE.BoxGeometry(12, 7, 20), phMat);
  b.position.set(BW*0.25 + 18, -H*0.5 + 3.5, -DL*0.3);
  b.castShadow = true;
  g.add(b);
  
  // Roof
  const r = new THREE.Mesh(new THREE.BoxGeometry(13, 1, 21), roofMat);
  r.position.set(BW*0.25 + 18, -H*0.5 + 7.5, -DL*0.3);
  g.add(r);
  
  // Penstocks
  const pipeMat = new THREE.MeshPhysicalMaterial({color:0x666666, metalness:0.8, roughness:0.3});
  for (let i = 0; i < 3; i++) {
    const pipe = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 1.2, 8, 12), pipeMat);
    pipe.rotation.x = Math.PI/2;
    pipe.position.set(BW*0.25 + 10, -H*0.5 + 2, -DL*0.2 + i*4 - 4);
    g.add(pipe);
  }
  
  // Tailrace
  const tr = new THREE.Mesh(
    new THREE.BoxGeometry(8, 2, 15),
    new THREE.MeshPhysicalMaterial({color:0x444466, roughness:0.9})
  );
  tr.position.set(BW*0.25 + 22, -H*0.5, -DL*0.3);
  g.add(tr);
  
  return g;
}
scene.add(createPowerhouse());

// === WATER SURFACE ===
let waterMesh;
function createWater() {
  const wGeo = new THREE.PlaneGeometry(200, 100, 80, 40);
  const wMat = new THREE.MeshPhysicalMaterial({
    color: 0x1a6b9e,
    transparent: true,
    opacity: 0.6,
    roughness: 0.1,
    metalness: 0.3,
    side: THREE.DoubleSide,
  });
  const w = new THREE.Mesh(wGeo, wMat);
  w.rotation.x = -Math.PI/2;
  // Water at NWL elevation
  const waterH = (NWL - EL_BASE) / (EL_CREST - EL_BASE) * H * 0.5;
  w.position.set(DL*0.25, -H*0.5 + waterH, -50);
  waterMesh = w;
  return w;
}
scene.add(createWater());

// Water animation
const wPos = waterMesh.geometry.attributes.position;
const wOrigY = new Float32Array(wPos.count);
for (let i = 0; i < wPos.count; i++) wOrigY[i] = wPos.getY(i);

let waterVisible = true;
window.toggleWater = function() {
  waterVisible = !waterVisible;
  waterMesh.visible = waterVisible;
  document.querySelectorAll(".ct")[4].classList.toggle("a");
};

// === ANNOTATIONS ===
const annotGroup = new THREE.Group();
let annotVisible = true;

function createLabel(text, x, y, z, color = "#fff", size = "14px") {
  const div = document.createElement("div");
  div.textContent = text;
  div.style.color = color;
  div.style.fontSize = size;
  div.style.fontWeight = "600";
  div.style.textShadow = "0 0 10px rgba(0,0,0,0.8), 0 0 20px rgba(0,0,0,0.5)";
  div.style.background = "rgba(0,0,0,0.3)";
  div.style.padding = "2px 8px";
  div.style.borderRadius = "4px";
  div.style.borderLeft = "2px solid " + color;
  div.style.pointerEvents = "none";
  div.style.fontFamily = "'Microsoft YaHei',sans-serif";
  const label = new CSS2DObject(div);
  label.position.set(x, y, z);
  return label;
}

annotGroup.add(createLabel("坝顶 EL 185.50m", DL*0.5, H*0.5+3, 0, "#667eea"));
annotGroup.add(createLabel("正常蓄水位 EL 183.00m", DL*0.25, (183-EL_BASE)/(EL_CREST-EL_BASE)*H*0.5-1.5+H*0.1, -35, "#2a6b9e", "12px"));
annotGroup.add(createLabel("溢洪道 3孔×8m", DL*0.5, -H*0.5+8, DL*0.5+2, "#e8c840"));
annotGroup.add(createLabel("厂房 3×20MW", BW*0.25+22, -H*0.5+8, -DL*0.15, "#aaa"));
annotGroup.add(createLabel("坝基 EL 140.50m", 0, -H*0.5-3, -DL*0.4, "#888", "11px"));
scene.add(annotGroup);

window.toggleAnnot = function() {
  annotVisible = !annotVisible;
  labelRenderer.domElement.style.display = annotVisible ? "block" : "none";
  document.querySelectorAll(".ct")[5].classList.toggle("a");
};

// === VIEW CONTROLS ===
window.viewFull = function() {
  controls.target.set(DL/2, 0, 0);
  camera.position.set(DL/2 + 50, 30, 70);
  controls.update();
  document.querySelectorAll(".ct")[0].classList.add("a");
  for (let i = 1; i <= 3; i++) document.querySelectorAll(".ct")[i].classList.remove("a");
};
window.viewUp = function() {
  controls.target.set(DL/2, 0, 0);
  camera.position.set(DL/2, 60, 0.1);
  controls.update();
  document.querySelectorAll(".ct")[1].classList.add("a");
  for (let i = 0; i <= 3; i++) if (i !== 1) document.querySelectorAll(".ct")[i].classList.remove("a");
};
window.viewDown = function() {
  controls.target.set(DL/2, -H*0.2, 0);
  camera.position.set(DL/2 + 20, -H*0.2, 90);
  controls.update();
  document.querySelectorAll(".ct")[2].classList.add("a");
  for (let i = 0; i <= 3; i++) if (i !== 2) document.querySelectorAll(".ct")[i].classList.remove("a");
};
window.viewSide = function() {
  controls.target.set(DL/2, 0, 0);
  camera.position.set(DL/2, 5, 100);
  controls.update();
  document.querySelectorAll(".ct")[3].classList.add("a");
  for (let i = 0; i <= 3; i++) if (i !== 3) document.querySelectorAll(".ct")[i].classList.remove("a");
};

// === ANIMATION LOOP ===
let time = 0;
function animate() {
  requestAnimationFrame(animate);
  time += 0.02;
  
  // Animate water surface
  if (waterMesh && waterMesh.visible) {
    const pos = waterMesh.geometry.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const z = pos.getZ ? pos.getZ(i) : 0;
      const wave = Math.sin(x * 0.1 + time) * 0.3 + Math.sin(z * 0.08 + time * 0.7) * 0.2;
      pos.setY(i, wOrigY[i] + wave);
    }
    pos.needsUpdate = true;
  }
  
  controls.update();
  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
}

// === RESIZE ===
window.addEventListener("resize", () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  labelRenderer.setSize(innerWidth, innerHeight);
});

// === START ===
// Hide loading
setTimeout(() => document.getElementById("loading").classList.add("h"), 500);
animate();
</script>
</body>
</html>
''')

html = "\n".join(html_parts)
with open("output/hydro/dam_3d_viewer.html", "w", encoding="utf-8") as f:
    f.write(html)
sz = len(html)
print("Dam 3D HTML: %d bytes (%.1f KB)" % (sz, sz/1024))
