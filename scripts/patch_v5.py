import os

with open("E:/CAD自动化制图/interior_cad.html","r",encoding="utf-8") as f:
    html = f.read()

c = 0

# ==================== 1. PDF EXPORT using native canvas ====================
pdf_code = """
// ===================== PDF 导出 =====================
window.exportPDF=function(){
  render2D();
  var W=c2.width,H=c2.height;
  // Create PDF-like SVG wrapper that browsers can print to PDF
  var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="'+W+'" height="'+H+'" viewBox="0 0 '+W+' '+H+'">';
  svg += '<rect width="100%" height="100%" fill="#161628"/>';
  svg += '<foreignObject width="100%" height="100%"><img src="'+c2.toDataURL("image/png")+'" width="'+W+'" height="'+H+'"/></foreignObject></svg>';
  var win=window.open("","_blank");
  win.document.write('<html><head><title>Floor Plan PDF</title><style>body{margin:0}@media print{@page{size:A3 landscape;margin:0}}img{width:100%;height:auto}</style></head><body>');
  win.document.write('<img src="'+c2.toDataURL("image/png")+'" onload="window.print()" style="width:100%"/>');
  win.document.write('</body></html>');
  win.document.close();
};
"""
marker_pdf = "window.exportPNG=function(){"
if marker_pdf in html:
    html = html.replace(marker_pdf, pdf_code + marker_pdf)
    c += 1
    print("+ PDF export")

# Add PDF button
old_png_btn = '<button class="btn" onclick="exportPNG()"> PNG</button>'
if old_png_btn in html:
    html = html.replace(old_png_btn, '<button class="btn" onclick="exportPNG()"> PNG</button>\n      <button class="btn" onclick="exportPDF()"> PDF</button>')
    c += 1
    print("+ PDF button")

# ==================== 2. IMAGE TRACING LAYER ====================
image_code = """
// ===================== 图片描图 =====================
var bgImage = null;
var bgImageOpacity = 0.3;

window.loadBgImage=function(){
  var input = document.createElement("input");
  input.type = "file";
  input.accept = "image/*";
  input.onchange = function(e){
    var reader = new FileReader();
    reader.onload = function(ev){
      var img = new Image();
      img.onload = function(){
        bgImage = img;
        render2D();
        document.getElementById("tool-status").textContent = "  描图图片已加载 (透明: "+(bgImageOpacity*100)+"%)";
      };
      img.src = ev.target.result;
    };
    reader.readAsDataURL(e.target.files[0]);
  };
  input.click();
};

window.adjustBgOpacity = function(delta){
  bgImageOpacity = Math.max(0.1, Math.min(0.8, bgImageOpacity + delta));
  if(bgImage) render2D();
};
"""
marker_img = "var gridVisible=true,snapEnabled=true;"
if marker_img in html:
    html = html.replace(marker_img, image_code + "\n" + marker_img)
    c += 1
    print("+ Image tracing")

# Add image button to header
old_clr = 'onclick="clearAll()" style="color:#e74c3c"> 清空</button>'
if 'onclick="loadBgImage()"' not in html:
    html = html.replace(old_clr, 'onclick="loadBgImage()"> 图片</button>\n      <button class="btn" onclick="clearAll()" style="color:#e74c3c"> 清空</button>')
    c += 1
    print("+ Image button")

# Add image rendering to render2D
old_grid_start = "ctx.fillRect(0,0,W,H);"
new_grid = "ctx.fillRect(0,0,W,H);\n  // Background image tracing layer\n  if(bgImage){ctx.save();ctx.globalAlpha=bgImageOpacity;ctx.drawImage(bgImage,0,0,W,H);ctx.restore();}"
if old_grid_start in html:
    html = html.replace(old_grid_start, new_grid)
    c += 1
    print("+ Image rendering in canvas")

# ==================== 3. WALL SPLIT TOOL ====================
split_code = """
// ===================== 墙分割 =====================
window.splitWall=function(){
  if(!sel){document.getElementById("tool-status").textContent="  请先选中要分割的墙";return;}
  var mx=(sel.x1+sel.x2)/2, my=(sel.y1+sel.y2)/2;
  saveState();
  var len=Math.hypot(sel.x2-sel.x1,sel.y2-sel.y1);
  var dx=(sel.x2-sel.x1)/len*50, dy=(sel.y2-sel.y1)/len*50;
  walls.push({id:nextId++,x1:sel.x1,y1:sel.y1,x2:mx-dx,y2:my-dy,thick:sel.thick,type:sel.type});
  walls.push({id:nextId++,x1:mx+dx,y1:my+dy,x2:sel.x2,y2:sel.y2,thick:sel.thick,type:sel.type});
  walls=walls.filter(function(w){return w!==sel});
  sel=walls[walls.length-1];
  saveState();render2D();rebuild3D();updateStatus();
  document.getElementById("tool-status").textContent="  墙已分割为两段";
};
"""
marker_split = "window.delWall=function(){if(!sel)return;walls=walls.filter"
if marker_split in html and "splitWall" not in html:
    html = html.replace(marker_split, split_code + "\n" + marker_split)
    c += 1
    print("+ Wall split tool")

# Add split button to props panel
old_del_btn = 'onclick="delWall()"> 删除</button>'
if 'splitWall()"' not in html:
    html = html.replace(old_del_btn, 'onclick="delWall()"> 删除</button>\n      <button class="btn" style="padding:2px 6px;font-size:10px" onclick="toggleWallType()">切换内外</button>\n      <button class="btn" style="padding:2px 6px;font-size:10px" onclick="splitWall()">分割</button>')
    c += 1
    print("+ Split button in props")

# ==================== 4. SCALE BAR ====================
scale_code = """
  // Scale bar
  var sbLen=2000; // 2m in mm
  var sbPx=sbLen*cam.zoom;
  var sbX=20, sbY=c2.height-30;
  ctx.fillStyle="rgba(255,255,255,0.6)";
  ctx.fillRect(sbX,sbY,sbPx,3);
  ctx.fillRect(sbX,sbY-3,1,6);
  ctx.fillRect(sbX+sbPx,sbY-3,1,6);
  ctx.fillStyle="rgba(255,255,255,0.5)";
  ctx.font="9px sans-serif";ctx.textAlign="center";
  ctx.fillText((sbLen/1000)+"m",sbX+sbPx/2,sbY-6);
"""
marker_scale = "ctx.textAlign = \"center\";\n    ctx.fillText(r.name+\" \"+r.area+\"m2\",cx.x,cx.y);"
if marker_scale in html:
    html = html.replace(marker_scale, marker_scale + "\n" + scale_code)
    c += 1
    print("+ Scale bar")

# ==================== 5. ROOM NAME EDITING ====================
room_edit = """
// ===================== 房间编辑 =====================
window.editRoom=function(){
  // Find room at center of view or selected room
  var wp=s2w(c2.width/2,c2.height/2);
  var closest=null, minDist=Infinity;
  for(var i=0;i<rooms.length;i++){
    var cx=0,cy=0;
    for(var j=0;j<rooms[i].corners.length;j++){cx+=rooms[i].corners[j].x;cy+=rooms[i].corners[j].y;}
    cx/=rooms[i].corners.length;cy/=rooms[i].corners.length;
    var d=Math.hypot(wp.x-cx,wp.y-cy);
    if(d<minDist){minDist=d;closest=i;}
  }
  if(closest===null||minDist>5000/cam.zoom)return;
  var newName=prompt("房间名称:",rooms[closest].name);
  if(newName&&newName.trim()){rooms[closest].name=newName.trim();render2D();rebuild3D();updateStatus();}
};
"""
# Insert before animation loop
anim_marker = "// ===================== ANIMATION LOOP"
if anim_marker in html and "editRoom" not in html:
    html = html.replace(anim_marker, room_edit + "\n" + anim_marker)
    c += 1
    print("+ Room name editing")

# Add room edit button to header
old_pdf_btn = 'exportPDF()"> PDF</button>'
if 'editRoom()"' not in html:
    html = html.replace(old_pdf_btn, 'exportPDF()"> PDF</button>\n      <button class="btn" onclick="editRoom()"> 房间名</button>')
    c += 1
    print("+ Room edit button")

# ==================== 6. 3D ENVIRONMENT UPGRADE ====================
env_code = """
  // Sky
  var skyGeo=new THREE.SphereGeometry(80,32,32);
  var skyMat=new THREE.MeshBasicMaterial({color:0x87CEEB,side:THREE.BackSide});
  var sky=new THREE.Mesh(skyGeo,skyMat);
  roomG.add(sky);
  
  // Ground plane with grass
  var groundMat=new THREE.MeshStandardMaterial({color:0x7CB342,roughness:0.9});
  var ground=new THREE.Mesh(new THREE.PlaneGeometry(60,60),groundMat);
  ground.rotation.x=-Math.PI/2;ground.position.y=-2.1;ground.receiveShadow=true;
  roomG.add(ground);
  
  // Some simple trees (cones + cylinders)
  var treePositions=[[-12,-8],[10,-10],[-10,12],[14,9]];
  var trunkMat=new THREE.MeshStandardMaterial({color:0x5D4037,roughness:0.9});
  var leafMat=new THREE.MeshStandardMaterial({color:0x4CAF50,roughness:0.8});
  for(var t=0;t<treePositions.length;t++){
    var trunk=new THREE.Mesh(new THREE.CylinderGeometry(0.15,0.2,1.5),trunkMat);
    trunk.position.set(treePositions[t][0],-1.25,treePositions[t][1]);
    trunk.castShadow=true;roomG.add(trunk);
    var leaf=new THREE.Mesh(new THREE.ConeGeometry(0.8,1.5,6),leafMat);
    leaf.position.set(treePositions[t][0],0,treePositions[t][1]);
    leaf.castShadow=true;roomG.add(leaf);
    var leaf2=new THREE.Mesh(new THREE.ConeGeometry(0.6,1.2,6),leafMat);
    leaf2.position.set(treePositions[t][0],0.8,treePositions[t][1]);
    leaf2.castShadow=true;roomG.add(leaf2);
  }
"""
# Find the 3D rebuild section where floors are created
marker_3d = "roomG.add(fl);\n"
env_marker = "roomG.add(fl);"
if env_marker in html:
    env_count = html.count(env_marker)
    if env_count > 0:
        # Add after the second occurrence (after ground floor and after the new floor)
        parts = html.split(env_marker)
        if len(parts) >= 2:
            # Check if env already exists
            if "0x87CEEB" not in html:
                parts[1] = env_code + parts[1]
                html = env_marker.join(parts)
                c += 1
                print("+ 3D environment")
            else:
                print("  3D env already exists, skip")

with open("E:/CAD自动化制图/interior_cad.html","w",encoding="utf-8") as f:
    f.write(html)

print(f"Done! {c} changes, {len(html)} bytes")
