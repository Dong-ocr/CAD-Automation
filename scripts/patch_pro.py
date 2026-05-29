import os
with open("E:/CAD自动化制图/interior_cad.html","r",encoding="utf-8") as f:
    html = f.read()
c=0

# Find the dimension rendering section
idx = html.find("dimension line")
if idx < 0:
    idx = html.find("Main dimension")
if idx < 0:
    idx = html.find("d.x2-d.x1,d.y2-d.y1")
if idx >= 0:
    print("Found dim rendering at", idx)
    # Replace the text rendering
    old_txt = 'ctx.fillText((dist/1000).toFixed(1)+"m",mid.x+nx,mid.y+ny-3);'
    new_txt = 'ctx.font="bold 11px sans-serif";var txt=(dist/1000).toFixed(1)+"m";var tw=ctx.measureText(txt).width;ctx.fillStyle="rgba(22,22,40,0.7)";ctx.fillRect(mid.x+nx-tw/2-3,mid.y+ny-10,tw+6,14);ctx.fillStyle="#ff6b6b";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText(txt,mid.x+nx,mid.y+ny-3);'
    if old_txt in html:
        html = html.replace(old_txt, new_txt)
        c+=1; print("+ Professional dim text")
    else:
        print("  Text format different, skipping")
else:
    print("Dim rendering not found")

# Add 3D arc wall rendering to rebuild3D
arc_3d = """
  // 3D Arc walls
  for(var a=0;a<wallsArc.length;a++){
    var aw=wallsArc[a];
    var shape=new THREE.Shape();
    var ir=aw.radius-aw.thick/2, or=aw.radius+aw.thick/2;
    var steps=32;
    shape.moveTo(Math.cos(aw.startAngle)*ir,Math.sin(aw.startAngle)*ir);
    for(var s=1;s<=steps;s++){
      var t=aw.startAngle+(aw.endAngle-aw.startAngle)*s/steps;
      shape.lineTo(Math.cos(t)*ir,Math.sin(t)*ir);
    }
    for(var s=steps;s>=0;s--){
      var t=aw.startAngle+(aw.endAngle-aw.startAngle)*s/steps;
      shape.lineTo(Math.cos(t)*or,Math.sin(t)*or);
    }
    shape.closePath();
    var extSettings={depth:2.8,bevelEnabled:false};
    var geo=new THREE.ExtrudeGeometry(shape,extSettings);
    var mat=new THREE.MeshStandardMaterial({color:0xF0EBE5,roughness:0.9});
    var mesh=new THREE.Mesh(geo,mat);
    mesh.position.set(aw.cx/1000,-1.4,aw.cy/1000);
    mesh.rotation.x=0;
    mesh.castShadow=true;mesh.receiveShadow=true;
    roomG.add(mesh);
  }
"""
# Find 3D rebuild section
idx3d = html.find("roomG.add(fl);")
if idx3d >= 0:
    count = html.count("roomG.add(fl);")
    if count > 1:
        # Add after the second occurrence
        parts = html.split("roomG.add(fl);")
        html = "roomG.add(fl);".join(parts[:2]) + "roomG.add(fl);" + arc_3d + "roomG.add(fl);".join(parts[2:])
    else:
        html = html.replace("roomG.add(fl);", "roomG.add(fl);" + arc_3d, 1)
    c+=1; print("+ 3D arc walls")

# Add hatch UI to header
old_hatch_btn = 'onclick="editRoom()"> 房间名</button>'
if 'applyHatch' not in html:
    html = html.replace(old_hatch_btn, 'onclick="editRoom()"> 房间名</button>\n      <select onchange="if(rooms.length>0)applyHatch(0,this.value)" style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:3px;color:#fff;font-size:10px;padding:2px 4px"><option value="">无填充</option><option value="ansi31">混凝土</option><option value="wood">木纹</option><option value="tile">瓷砖</option><option value="concrete">点状</option></select>')
    c+=1; print("+ Hatch dropdown")

# Add tool tip for arc
old_status = '"7":"arc"});\n'
new_status = '"7":"arc"});\n    if(t==="arc")document.getElementById("tool-status").textContent="弧墙: 点三点(起点-中点-终点)";\n'
html = html.replace(old_status, new_status)
c+=1; print("+ Arc tool tip")

with open("E:/CAD自动化制图/interior_cad.html","w",encoding="utf-8") as f:
    f.write(html)
print(f"Done! {c} changes, {len(html)} bytes")
