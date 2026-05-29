import os
with open("E:/CAD自动化制图/interior_cad.html","r",encoding="utf-8") as f:
    html = f.read()
c=0

# ==================== 1. SNAP INDICATORS ====================
snap_indicator = """
  // Snap indicators
  if(tool==="wall"||tool==="select"){
    var _snapDist=20/cam.zoom;
    // Endpoints
    for(var _si=0;_si<walls.length;_si++){
      var _ep=[
        {x:walls[_si].x1,y:walls[_si].y1},
        {x:walls[_si].x2,y:walls[_si].y2}
      ];
      for(var _ej=0;_ej<_ep.length;_ej++){
        var _d=Math.hypot(wp.x-_ep[_ej].x,wp.y-_ep[_ej].y);
        if(_d<_snapDist){
          var _sp=w2s(_ep[_ej].x,_ep[_ej].y);
          ctx.strokeStyle="#43E97B";ctx.lineWidth=2;
          ctx.beginPath();ctx.arc(_sp.x,_sp.y,8,0,Math.PI*2);ctx.stroke();
          ctx.fillStyle="rgba(67,233,123,0.2)";ctx.fill();
          ctx.fillStyle="#43E97B";
          ctx.beginPath();ctx.arc(_sp.x,_sp.y,3,0,Math.PI*2);ctx.fill();
        }
      }
      // Midpoints
      var _mx=(walls[_si].x1+walls[_si].x2)/2,_my=(walls[_si].y1+walls[_si].y2)/2;
      var _md=Math.hypot(wp.x-_mx,wp.y-_my);
      if(_md<_snapDist){
        var _mp=w2s(_mx,_my);
        ctx.strokeStyle="#FFD700";ctx.lineWidth=2;
        ctx.beginPath();ctx.moveTo(_mp.x,_mp.y-8);ctx.lineTo(_mp.x+5,_mp.y);
        ctx.lineTo(_mp.x,_mp.y+8);ctx.lineTo(_mp.x-5,_mp.y);ctx.closePath();ctx.stroke();
        ctx.fillStyle="rgba(255,215,0,0.15)";ctx.fill();
      }
    }
  }
"""
# Insert snap indicators right after coord-status update in pointermove
# Find the pointermove handler
pm_marker = "c2.addEventListener(\"pointermove\",e=>{"
if pm_marker in html:
    # Add snap indicator rendering call at the end of pointermove
    html = html.replace("render2D();\n  });\n\n  // Wall length tooltip", 
                        "render2D();\n    // Snap indicators\n    if(tool===\"wall\"||tool===\"select\"){\n      var _wp=s2w(e.clientX-c2.getBoundingClientRect().left,e.clientY-c2.getBoundingClientRect().top);\n"+snap_indicator+"\n    }\n  });\n\n  // Wall length tooltip")
    c+=1; print("+ Snap indicators")
else:
    print("  pointermove marker not found")

# ==================== 2. REAL-TIME DRAWING FEEDBACK ====================
rt_feedback = """
  // Real-time drawing feedback
  if(tool===\"wall\"&&wallDraw&&mPos){
    var _dx=mPos.x-wallDraw.x,_dy=mPos.y-wallDraw.y;
    var _len=Math.hypot(_dx,_dy);
    var _ang=Math.atan2(_dy,_dx)*180/Math.PI;
    document.getElementById(\"coord-status\").textContent=
      \"长度: \"+(_len/1000).toFixed(2)+\"m | 角度: \"+_ang.toFixed(1)+\"° | 起点: (\"+(wallDraw.x/1000).toFixed(1)+\", \"+(wallDraw.y/1000).toFixed(1)+\")\";
  }
"""
# Insert into pointermove after coord update
old_coord = "document.getElementById(\"coord-status\").textContent=(wp.x/1000).toFixed(1)+\"m, \"+(wp.y/1000).toFixed(1)+\"m\";"
new_coord = old_coord + "\n"+rt_feedback
if old_coord in html:
    html = html.replace(old_coord, new_coord)
    c+=1; print("+ Real-time drawing feedback")

# ==================== 3. PROFESSIONAL LINE WEIGHTS ====================
line_weight = """
// ===================== 专业线宽渲染 =====================
var LINE_WEIGHTS = {
  \"A-WALL\":    2.5, \"A-WALL-PART\": 1.5,
  \"A-DOOR\":    1.0, \"A-WINDOW\":    1.0,
  \"A-DIM\":     0.7, \"A-TEXT\":      0.5,
  \"A-FURN\":    0.5, \"A-HATCH\":     0.3,
  \"A-AXIS\":    0.3, \"A-COLUMN\":    2.0,
};

// Patch wall rendering to use layer weights
window.applyLineWeights = function(){
  for(var i=0;i<walls.length;i++){
    var layer=walls[i].layer||(walls[i].type===\"外墙\"?\"A-WALL\":\"A-WALL-PART\");
    walls[i]._weight=LINE_WEIGHTS[layer]||1.0;
  }
  render2D();
  document.getElementById(\"tool-status\").textContent=\"  专业线宽已应用\";
};
"""

am = "// ===================== ANIMATION LOOP"
if am in html:
    html = html.replace(am, line_weight + am)
    c+=1; print("+ Line weight system")

# Add button
old_gbt = 'onclick="setGBStandard()"> 国标</button>'
if 'applyLineWeights()' not in html:
    html = html.replace(old_gbt, 'onclick="setGBStandard()"> 国标</button>\n      <button class="btn" onclick="applyLineWeights()"> 线宽</button>')
    c+=1; print("+ Line weight button")

# ==================== 4. PROCEDURAL FURNITURE UPGRADE (better 3D) ====================
# Find the bed builder and make it more detailed
old_bed_3d = 'if(d.cat==="beds"){'
new_bed_3d = 'if(d.cat==="beds"){\n    var bm=fabric(d.color);\n    var b=new THREE.Mesh(new THREE.BoxGeometry(d.w,0.3,d.d),bm);\n    b.position.y=0.25;b.castShadow=true;g.add(b);\n    var hd2=new THREE.Mesh(new THREE.BoxGeometry(d.w,0.6,0.15),wood(d.color));\n    hd2.position.set(0,0.55,-d.d/2+0.07);hd2.castShadow=true;g.add(hd2);\n    var p=new THREE.Mesh(new THREE.BoxGeometry(d.w*0.6,0.15,0.35),fabric("#FFFFFF"));\n    p.position.set(0,0.5,-d.d/2+0.3);g.add(p);\n    var quilt=new THREE.Mesh(new THREE.BoxGeometry(d.w*0.85,0.08,d.d*0.6),fabric(new THREE.Color(d.color).offsetHSL(0,0,-0.15).getStyle()));\n    quilt.position.set(0,0.4,0.15);quilt.castShadow=true;g.add(quilt);'
if old_bed_3d in html:
    html = html.replace(old_bed_3d, new_bed_3d, 1)
    c+=1; print("+ Better 3D bed")

# Better sofa
old_sofa_3d = 'if(d.cat==="sofas"){'
new_sofa_3d = 'if(d.cat==="sofas"){\n    var sm=fabric(d.color);\n    var b=new THREE.Mesh(new THREE.BoxGeometry(d.w,0.3,d.d),sm);b.position.y=0.25;b.castShadow=true;g.add(b);\n    var bk=new THREE.Mesh(new THREE.BoxGeometry(d.w,0.45,0.1),sm);bk.position.set(0,0.55,-d.d/2+0.05);bk.castShadow=true;g.add(bk);\n    var arm=new THREE.Mesh(new THREE.BoxGeometry(0.1,0.3,d.d*0.7),sm);arm.position.set(-d.w/2+0.05,0.4,0.05);arm.castShadow=true;g.add(arm);\n    var arm2=arm.clone();arm2.position.x=d.w/2-0.05;g.add(arm2);\n    var cush=new THREE.Mesh(new THREE.BoxGeometry(d.w*0.42,0.08,d.d*0.65),fabric(new THREE.Color(d.color).offsetHSL(0,0,0.05).getStyle()));\n    cush.position.set(-d.w*0.13,0.43,0.03);cush.castShadow=true;g.add(cush);\n    var cush2=cush.clone();cush2.position.x=d.w*0.13;g.add(cush2);\n    [-1,1].forEach(function(x){var l=new THREE.Mesh(new THREE.CylinderGeometry(0.025,0.025,0.12),metal("#2D2D2D"));l.position.set(x*(d.w/2-0.08),0.06,d.d/2-0.08);g.add(l);var l2=new THREE.Mesh(new THREE.CylinderGeometry(0.025,0.025,0.12),metal("#2D2D2D"));l2.position.set(x*(d.w/2-0.08),0.06,-d.d/2+0.08);g.add(l2)});'
if old_sofa_3d in html:
    # Only replace if not already upgraded
    if 'cush2=cush.clone()' not in html:
        html = html.replace(old_sofa_3d, new_sofa_3d, 1)
        c+=1; print("+ Better 3D sofa")

with open("E:/CAD自动化制图/interior_cad.html","w",encoding="utf-8") as f:
    f.write(html)
print(f"Done! {c} changes, {len(html)} bytes")
