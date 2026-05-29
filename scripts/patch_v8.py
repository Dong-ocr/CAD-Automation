import os

with open("E:/CAD自动化制图/interior_cad.html","r",encoding="utf-8") as f:
    html = f.read()
c = 0

# ==================== 1. FULL PROCEDURAL FURNITURE SYSTEM ====================
# This replaces the simple box rendering in rebuild3D
furniture_system = """
// ===================== 程序化家具生成器 =====================
function wood(c){return new THREE.MeshStandardMaterial({color:c,roughness:0.7,metalness:0})}
function fabric(c){return new THREE.MeshStandardMaterial({color:c,roughness:0.9,metalness:0})}
function metal(c){return new THREE.MeshStandardMaterial({color:c,roughness:0.3,metalness:0.7})}

function buildFurniture3D(f){
  var g=new THREE.Group(),W=wood(f.color||"#C4A882"),M=fabric(f.color||"#cccccc"),LM=metal("#2D2D2D");
  var w=f.w/1000||1,h=f.h/1000||0.5,d=f.d/1000||1;
  var leg=function(h2){return new THREE.Mesh(new THREE.CylinderGeometry(0.02,0.02,h2||0.12),LM)};
  
  // Bed
  if(f.name.indexOf("床")>=0||f.name==="双人床"||f.name==="单人床"){
    M=fabric(f.color||"#D2B48C");
    var b=new THREE.Mesh(new THREE.BoxGeometry(w,0.25,d),M);
    b.position.y=0.125;b.castShadow=true;g.add(b);
    var hd=new THREE.Mesh(new THREE.BoxGeometry(w,0.5,0.1),wood(f.color||"#8B6914"));
    hd.position.set(0,0.4,-d/2+0.05);hd.castShadow=true;g.add(hd);
    var p=new THREE.Mesh(new THREE.BoxGeometry(w*0.5,0.1,0.3),fabric("#FFFFFF"));
    p.position.set(0,0.25,-d/2+0.25);g.add(p);
    var q=new THREE.Mesh(new THREE.BoxGeometry(w*0.8,0.06,d*0.5),fabric(new THREE.Color(f.color||"#D2B48C").offsetHSL(0,0,-0.1).getStyle()));
    q.position.set(0,0.2,0.1);q.castShadow=true;g.add(q);
    return g;
  }
  // Sofa
  if(f.name.indexOf("沙发")>=0){
    M=fabric(f.color||"#8B4513");
    var b=new THREE.Mesh(new THREE.BoxGeometry(w,0.25,d),M);
    b.position.y=0.2;b.castShadow=true;g.add(b);
    var bk=new THREE.Mesh(new THREE.BoxGeometry(w,0.4,0.08),M);
    bk.position.set(0,0.45,-d/2+0.04);bk.castShadow=true;g.add(bk);
    var ar=new THREE.Mesh(new THREE.BoxGeometry(0.08,0.25,d*0.6),M);
    ar.position.set(-w/2+0.04,0.35,0);ar.castShadow=true;g.add(ar);
    var ar2=ar.clone();ar2.position.x=w/2-0.04;g.add(ar2);
    var cs=new THREE.Mesh(new THREE.BoxGeometry(w*0.42,0.06,d*0.6),fabric(new THREE.Color(f.color||"#8B4513").offsetHSL(0,0,0.05).getStyle()));
    cs.position.set(-w*0.13,0.35,0);cs.castShadow=true;g.add(cs);
    var cs2=cs.clone();cs2.position.x=w*0.13;g.add(cs2);
    [-1,1].forEach(function(x){var l=leg();l.position.set(x*(w/2-0.06),0.06,d/2-0.06);g.add(l);var l2=leg();l2.position.set(x*(w/2-0.06),0.06,-d/2+0.06);g.add(l2)});
    return g;
  }
  // Table
  if(f.name.indexOf("桌")>=0||f.name.indexOf("茶几")>=0){
    W=wood(f.color||"#DEB887");
    var t=new THREE.Mesh(new THREE.BoxGeometry(w,0.04,d),W);
    t.position.y=h;t.castShadow=true;t.receiveShadow=true;g.add(t);
    [-1,1].forEach(function(x){[-1,1].forEach(function(z){var l=new THREE.Mesh(new THREE.CylinderGeometry(0.025,0.025,h-0.02),LM);l.position.set(x*(w/2-0.05),(h-0.02)/2,z*(d/2-0.05));l.castShadow=true;g.add(l)})});
    return g;
  }
  // Chair
  if(f.name.indexOf("椅")>=0||f.name.indexOf("凳")>=0){
    W=wood(f.color||"#C4A882");
    var sh=0.4;
    var s=new THREE.Mesh(new THREE.BoxGeometry(w*0.7,0.04,d*0.7),W);
    s.position.y=sh;s.castShadow=true;g.add(s);
    var bk=new THREE.Mesh(new THREE.BoxGeometry(w*0.6,0.3,0.03),W);
    bk.position.set(0,sh+0.15,-d*0.35);bk.castShadow=true;g.add(bk);
    [-1,1].forEach(function(x){[-1,1].forEach(function(z){var l=new THREE.Mesh(new THREE.CylinderGeometry(0.015,0.015,sh),W);l.position.set(x*w*0.3,sh/2,z*d*0.3);g.add(l)})});
    return g;
  }
  // Cabinet
  if(f.name.indexOf("柜")>=0||f.name.indexOf("橱")>=0){
    W=wood(f.color||"#C4A882");
    var bd=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),W);
    bd.position.y=h/2;bd.castShadow=true;g.add(bd);
    for(var i=0;i<3;i++){var sh2=new THREE.Mesh(new THREE.BoxGeometry(w-0.02,0.02,d-0.02),W);sh2.position.set(0,(i+1)*h/4,0);g.add(sh2)}
    return g;
  }
  // Appliance (fridge, etc.)
  if(f.name.indexOf("冰箱")>=0||f.name.indexOf("洗衣")>=0){
    var aMat=new THREE.MeshStandardMaterial({color:new THREE.Color(f.color||"#C0C0C0"),roughness:0.3,metalness:0.5});
    var bd=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),aMat);
    bd.position.y=h/2;bd.castShadow=true;g.add(bd);
    return g;
  }
  // Sanitary
  if(f.name.indexOf("马桶")>=0||f.name.indexOf("洗手")>=0||f.name.indexOf("浴缸")>=0){
    var sMat=new THREE.MeshStandardMaterial({color:new THREE.Color(f.color||"#F5F5F5"),roughness:0.4,metalness:0.1});
    if(f.name.indexOf("马桶")>=0){
      var bd=new THREE.Mesh(new THREE.BoxGeometry(w,h*0.5,d),sMat);
      bd.position.y=h*0.25;bd.castShadow=true;g.add(bd);
      var tk=new THREE.Mesh(new THREE.BoxGeometry(w*0.6,h*0.4,d*0.6),sMat);
      tk.position.set(0,h*0.5+d*0.1,0);g.add(tk);
    } else if(f.name.indexOf("洗手")>=0){
      var bd=new THREE.Mesh(new THREE.BoxGeometry(w,h*0.6,d),sMat);
      bd.position.y=h*0.3;bd.castShadow=true;g.add(bd);
      var bs=new THREE.Mesh(new THREE.BoxGeometry(w*0.8,0.05,d*0.7),sMat);
      bs.position.y=h*0.65;g.add(bs);
    } else {
      var bd=new THREE.Mesh(new THREE.BoxGeometry(w,h*0.4,d),sMat);
      bd.position.y=h*0.2;bd.castShadow=true;g.add(bd);
    }
    return g;
  }
  // Default: simple box with label
  var dft=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),new THREE.MeshStandardMaterial({color:f.color||"#cccccc",roughness:0.6}));
  dft.position.y=h/2;dft.castShadow=true;g.add(dft);
  return g;
}
"""

# Insert before rebuild3D
rebuild_start = "function rebuild3D(){"
if rebuild_start in html:
    if "buildFurniture3D" not in html:
        html = html.replace(rebuild_start, furniture_system + rebuild_start)
        c+=1; print("+ Procedural furniture system")
else:
    print("  rebuild3D not found!")

# Replace the box rendering in rebuild3D
old_furn = """  for(const f of furniture){
    const mat=new THREE.MeshStandardMaterial({color:f.color||"#cccccc",roughness:0.6});
    const m=new THREE.Mesh(new THREE.BoxGeometry(f.w/1000,300/1000,f.d/1000),mat);
    m.position.set(f.x/1000,0.15,f.y/1000);
    m.castShadow=true;roomG.add(m);
  }"""

new_furn = """  for(var fi=0;fi<furniture.length;fi++){
    var f=furniture[fi];
    var m=buildFurniture3D(f);
    if(m){
      m.position.set(f.x/1000,0,f.y/1000);
      m.rotation.y=(f.rotation||0)*Math.PI/180;
      m.castShadow=true;
      roomG.add(m);
    }
  }"""

if old_furn in html:
    html = html.replace(old_furn, new_furn)
    c+=1; print("+ Integrated procedural furniture into rebuild3D")
else:
    # Try finding the exact code
    idx = html.find("BoxGeometry(f.w/1000,300/1000")
    if idx >= 0:
        print("  Found box rendering at", idx)
        # Replace the whole for loop
        loop_start = html.rfind("for(const f of furniture)", 0, idx)
        if loop_start >= 0:
            loop_end = html.find("}", loop_start)
            loop_end = html.find("}", loop_end+1)
            if loop_end > loop_start:
                html = html[:loop_start] + new_furn + html[loop_end+1:]
                c+=1; print("+ Replaced furniture loop (surgical)")
    else:
        print("  Box rendering not found!")

# ==================== 2. CTB PRINT STYLES ====================
ctb_code = """
// ===================== CTB 打印样式 =====================
var CTB = {
  color: {
    "1":{name:"红色",weight:0.18,halftone:100},
    "2":{name:"黄色",weight:0.25,halftone:80},
    "3":{name:"绿色",weight:0.35,halftone:100},
    "4":{name:"青色",weight:0.50,halftone:80},
    "5":{name:"蓝色",weight:0.18,halftone:100},
    "6":{name:"品红",weight:0.25,halftone:100},
    "7":{name:"白色",weight:0.35,halftone:100},
    "8":{name:"灰色",weight:0.13,halftone:60},
  },
  applyToLayer: function(layerName, colorIdx, weight, halftone){
    if(!this.color[colorIdx])return;
    this.color[colorIdx].weight=weight;
    this.color[colorIdx].halftone=halftone;
    render2D();
  },
  preview: function(){
    render2D();
    document.getElementById("tool-status").textContent="  CTB打印样式预览 (权重:"+
      Object.values(this.color).map(function(c){return c.weight.toFixed(2)}).join(",")+")";
  }
};

window.showCTB = function(){
  var msg="CTB 打印样式表\\n\\n颜色→权重→灰度\\n";
  for(var k in CTB.color){
    var c=CTB.color[k];
    msg+=k+". "+c.name+" → "+c.weight.toFixed(2)+"mm → "+c.halftone+"%\\n";
  }
  msg+="\\n可通过 CTB.color[id].weight/halftone 自定义";
  alert(msg);
};
"""

am = "// ===================== ANIMATION LOOP"
if am in html:
    html = html.replace(am, ctb_code + am)
    c+=1; print("+ CTB print styles")

# Add CTB button
old_lineweight = 'onclick="applyLineWeights()"> 线宽</button>'
if 'showCTB()' not in html:
    html = html.replace(old_lineweight, 'onclick="applyLineWeights()"> 线宽</button>\n      <button class="btn" onclick="showCTB()"> CTB</button>')
    c+=1; print("+ CTB button")

# ==================== 3. ENHANCED RIGHT-CLICK MENU ====================
# Add more items to the context menu
old_menu = 'items.push({label:" 适应画面", action:zoomFit});'
new_menu = 'items.push({label:" 适应画面", action:zoomFit});\n  items.push({label:" 网格开关", action:toggleGrid});\n  items.push({label:" 吸附开关", action:toggleSnap});\n  items.push({label:" 极轴开关", action:togglePolar});\n  items.push({label:"---",action:null});\n  items.push({label:" 国标图层", action:setGBStandard});\n  items.push({label:" 线宽应用", action:applyLineWeights});\n  items.push({label:" CTB预览", action:showCTB});'

if old_menu in html:
    html = html.replace(old_menu, new_menu)
    c+=1; print("+ Enhanced right-click menu")

with open("E:/CAD自动化制图/interior_cad.html","w",encoding="utf-8") as f:
    f.write(html)
print(f"Done! {c} changes, {len(html)} bytes")
