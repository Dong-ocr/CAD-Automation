import json, math, os
d = json.load(open("demo_project.json","r",encoding="utf-8"))
walls = d["w"]; rooms = d["r"]; furniture = d["f"]; doors = d["d"]
os.makedirs("output/professional", exist_ok=True)
scene = {"walls":[],"rooms":[],"furniture":[],"doors":[]}
for w in walls:
    x1,y1,x2,y2=w["x1"],w["y1"],w["x2"],w["y2"]
    t=w.get("thickness",240 if w["t"]=="\u5916" else 150)
    dx,dy=x2-x1,y2-y1; l=math.hypot(dx,dy)
    if l==0: continue
    c="#4a8aff" if w["t"]=="\u5916" else "#7a9cff"
    scene["walls"].append({"x":(x1+x2)/2/10,"z":(y1+y2)/2/10,"w":l/10,"h":280,"d":t/10,"rot":math.degrees(math.atan2(dy,dx)),"color":c,"type":w["t"]})
for r in rooms:
    scene["rooms"].append({"x":(r["x"]+r["w"]/2)/10,"z":(r["y"]+r["d"]/2)/10,"w":r["w"]/10,"d":r["d"]/10,"name":r["n"]})
for fi in furniture:
    scene["furniture"].append({"x":(fi["x"]+fi["w"]/2)/10,"z":(fi["y"]+fi["d"]/2)/10,"w":fi["w"]/10,"d":fi["d"]/10,"h":fi.get("h",500)/10,"color":fi.get("c","#A0A0A0"),"name":fi["n"]})
all_x=[w["x1"]/10 for w in walls]+[w["x2"]/10 for w in walls]
all_z=[w["y1"]/10 for w in walls]+[w["y2"]/10 for w in walls]
b={"min_x":min(all_x)-50,"max_x":max(all_x)+50,"min_z":min(all_z)-50,"max_z":max(all_z)+50}
scene["bounds"]=b; scene["center"]={"x":(b["min_x"]+b["max_x"])/2,"z":(b["min_z"]+b["max_z"])/2}
with open("output/professional/3d_scene.json","w",encoding="utf-8") as f:
    json.dump(scene,f,ensure_ascii=False,indent=2)
print("Scene: "+str(len(scene["walls"]))+" walls, "+str(len(scene["furniture"]))+" furniture")

sj=json.dumps(scene, ensure_ascii=False)
h=[]; A=h.append
A('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">')
A('<title>3D Scene</title><style>*{margin:0;padding:0}body{background:#07070d;overflow:hidden;font-family:"Inter","Microsoft YaHei",sans-serif}')
A('#info{position:absolute;top:16px;left:50%;transform:translateX(-50%);z-index:10;color:rgba(255,255,255,0.3);font-size:12px;background:rgba(0,0,0,0.5);padding:6px 18px;border-radius:8px;pointer-events:none}')
A('#legend{position:absolute;bottom:24px;left:24px;z-index:10;color:rgba(255,255,255,0.25);font-size:10px;line-height:1.8}')
A('.ld{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:middle}')
A('</style></head><body>')
A('<div id="info">&#x1f3d7; <strong>3D Scene</strong> &middot; Drag &middot; Scroll</div>')
A('<div id="legend"><div><span class="ld" style="background:#4a8aff"></span>Outer</div><div><span class="ld" style="background:#7a9cff"></span>Inner</div><div><span class="ld" style="background:#e74c3c"></span>Furniture</div></div>')
A('<script type="importmap">')
A('{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}')
A('</script><script type="module">')
A('import*as THREE from"three";import{OrbitControls}from"three/addons/controls/OrbitControls.js";')
A('var d='+sj+';')
A('var s=new THREE.Scene();s.background=new THREE.Color(0x07070d);')
A('var c=new THREE.PerspectiveCamera(45,innerWidth/innerHeight,1,10000);')
A('var r=new THREE.WebGLRenderer({antialias:true});r.setSize(innerWidth,innerHeight);r.setPixelRatio(Math.min(devicePixelRatio,2));')
A('r.shadowMap.enabled=true;r.toneMapping=THREE.ACESFilmicToneMapping;r.toneMappingExposure=1.2;document.body.appendChild(r.domElement);')
A('var o=new OrbitControls(c,r.domElement);o.enableDamping=true;o.dampingFactor=0.08;o.minDistance=200;o.maxDistance=5000;')
A('o.target.set(d.center.x,0,d.center.z);c.position.set(d.center.x+800,600,d.center.z+800);o.update();')
A('var gs=Math.max(d.bounds.max_x-d.bounds.min_x,d.bounds.max_z-d.bounds.min_z)+200;')
A('var gm=new THREE.LineBasicMaterial({color:0x1a1a2e,transparent:true,opacity:0.3});var gh=new THREE.Group();')
A('for(var x=-gs;x<=gs;x+=100){var bg=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(x,0,-gs),new THREE.Vector3(x,0,gs)]);gh.add(new THREE.Line(bg,gm))}')
A('for(var z=-gs;z<=gs;z+=100){var bg=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-gs,0,z),new THREE.Vector3(gs,0,z)]);gh.add(new THREE.Line(bg,gm))}')
A('s.add(gh);')
A('var gg=new THREE.Mesh(new THREE.PlaneGeometry(gs*2,gs*2),new THREE.ShadowMaterial({opacity:0.3}));gg.rotation.x=-Math.PI/2;gg.position.set(d.center.x,-1,d.center.z);gg.receiveShadow=true;s.add(gg);')
A('s.add(new THREE.AmbientLight(0x404060,0.6));s.add(new THREE.HemisphereLight(0x667eea,0x08080f,0.8));')
A('var dl=new THREE.DirectionalLight(0xffeedd,1.5);dl.position.set(500,800,500);dl.castShadow=true;dl.shadow.mapSize.width=2048;dl.shadow.mapSize.height=2048;dl.shadow.camera.near=0.5;dl.shadow.camera.far=2000;dl.shadow.camera.left=-1000;dl.shadow.camera.right=1000;dl.shadow.camera.top=1000;dl.shadow.camera.bottom=-1000;s.add(dl);')
A('var fl=new THREE.DirectionalLight(0x8888ff,0.5);fl.position.set(-300,400,-300);s.add(fl);')
A('d.walls.forEach(function(w){var m=new THREE.Mesh(new THREE.BoxGeometry(w.w,w.h,w.d),new THREE.MeshPhysicalMaterial({color:w.color,metalness:0.05,roughness:0.6,transparent:true,opacity:w.type=="\\u5916"?0.85:0.6,clearcoat:0.1}));m.position.set(w.x,w.h/2,w.z);m.rotation.y=w.rot*Math.PI/180;m.castShadow=true;m.receiveShadow=true;s.add(m)});')
A('d.furniture.forEach(function(f){var col=parseInt(f.color.replace("#",""),16);var m=new THREE.Mesh(new THREE.BoxGeometry(f.w,f.h,f.d),new THREE.MeshPhysicalMaterial({color:new THREE.Color(((col>>16)&255)/255,((col>>8)&255)/255,(col&255)/255),metalness:0.1,roughness:0.5}));m.position.set(f.x,f.h/2,f.z);m.castShadow=true;m.receiveShadow=true;s.add(m);var ca=document.createElement("canvas");ca.width=256;ca.height=64;var cx=ca.getContext("2d");cx.fillStyle="rgba(0,0,0,0.5)";cx.fillRect(0,0,256,64);cx.fillStyle="#fff";cx.font="bold 22px \\"Microsoft YaHei\\",sans-serif";cx.textAlign="center";cx.textBaseline="middle";cx.fillText(f.name,128,32);var tx=new THREE.CanvasTexture(ca);tx.needsUpdate=true;var sp=new THREE.Sprite(new THREE.SpriteMaterial({map:tx,transparent:true,depthWrite:false}));sp.position.set(f.x,f.h+30,f.z);sp.scale.set(80,20,1);s.add(sp)});')
A('d.rooms.forEach(function(r){var ca=document.createElement("canvas");ca.width=512;ca.height=128;var cx=ca.getContext("2d");cx.fillStyle="rgba(255,255,255,0.04)";cx.fillRect(0,0,512,128);cx.fillStyle="rgba(255,255,255,0.15)";cx.font="bold 36px \\"Microsoft YaHei\\",sans-serif";cx.textAlign="center";cx.textBaseline="middle";cx.fillText(r.name,256,64);var tx=new THREE.CanvasTexture(ca);tx.needsUpdate=true;var sp=new THREE.Sprite(new THREE.SpriteMaterial({map:tx,transparent:true,depthWrite:false,opacity:0.6}));sp.position.set(r.x,5,r.z);sp.scale.set(120,30,1);s.add(sp);var cg=new THREE.Mesh(new THREE.RingGeometry(Math.max(r.w,r.d)/2-5,Math.max(r.w,r.d)/2,32),new THREE.MeshBasicMaterial({color:0x667eea,side:THREE.DoubleSide,transparent:true,opacity:0.06}));cg.position.set(r.x,2,r.z);cg.rotation.x=-Math.PI/2;s.add(cg)});')
A('function a(){requestAnimationFrame(a);o.update();r.render(s,c)}a();')
A('addEventListener("resize",function(){c.aspect=innerWidth/innerHeight;c.updateProjectionMatrix();r.setSize(innerWidth,innerHeight)});')
A('</script></body></html>')
with open("output/professional/3d_viewer.html","w",encoding="utf-8") as f:
    f.write("\n".join(h))
import os as _os
print("OK: 3d_viewer.html ("+str(_os.path.getsize("output/professional/3d_viewer.html")//1024)+"KB)")
