import os
with open("E:/CAD自动化制图/interior_cad.html","r",encoding="utf-8") as f:
    html = f.read()
c=0

# ======== 1. Auto-save to localStorage ========
if "autoSaveInterval" not in html:
    auto_save = """
// ===================== Auto-save =====================
var autoSaveInterval = setInterval(function(){
  try {
    var d={walls:walls.slice(0,50),doors:doors.slice(0,20),windows:windows.slice(0,10),rooms:rooms.slice(0,20)};
    localStorage.setItem("cad_autosave", JSON.stringify(d));
  }catch(e){}
}, 30000);

window.recoverAutoSave=function(){
  try {
    var d=JSON.parse(localStorage.getItem("cad_autosave"));
    if(d&&d.walls&&d.walls.length>0){
      if(confirm("发现自动保存的草图 ("+d.walls.length+"面墙), 恢复?")){
        walls=d.walls;doors=d.doors||[];windows=d.windows||[];rooms=d.rooms||[];
        saveState();render2D();rebuild3D();updateStatus();
      }
    }
  }catch(e){}
};
"""
    anim_marker = "// ===================== ANIMATION LOOP"
    if anim_marker in html:
        html = html.replace(anim_marker, auto_save + "\n" + anim_marker)
        c+=1
        print("+ Auto-save")

# ======== 2. Wall length display on canvas ========
wall_len_code = """
  // Wall length label
  if(w===sel||w===hover){
    var mx=(p1.x+p2.x)/2, my=(p1.y+p2.y)/2;
    var wl=Math.hypot(w.x2-w.x1,w.y2-w.y1);
    ctx.fillStyle="#667eea";
    ctx.font="bold 10px sans-serif";
    ctx.textAlign="center";
    ctx.fillText((wl/1000).toFixed(1)+"m",mx,my-15);
  }
"""
# Find wall rendering section where endpoints are drawn
old_wall_end = 'ctx.fillStyle="#667eea";ctx.beginPath();ctx.arc(p1.x,p1.y,6,0,Math.PI*2);ctx.fill();'
if old_wall_end in html and "wl/1000).toFixed(1)+"m"" not in html:
    # Insert wall length label after endpoint rendering
    # Find the wall loop block end
    html = html.replace(
        'if(w===sel||w===hover){',
        'if(w===sel||w===hover){' + wall_len_code
    )
    c+=1
    print("+ Wall length labels")

# ======== 3. Snap to wall midpoint ========
if "snapToMidpoint" not in html:
    snap_mid = """
window.snapToMidpoint=function(p,dist){
  if(!snapEnabled)return null;
  for(var w=0;w<walls.length;w++){
    var mx=(walls[w].x1+walls[w].x2)/2,my=(walls[w].y1+walls[w].y2)/2;
    if(Math.hypot(p.x-mx,p.y-my)*cam.zoom<dist)return {x:mx,y:my};
  }
  return null;
};
"""
    # Insert before snapToEndpoint
    ste_marker = "var origSnapToEndpoint = snapToEndpoint;"
    if ste_marker in html:
        html = html.replace(ste_marker, snap_mid + "\n" + ste_marker)
        c+=1
        print("+ Midpoint snap")

    # Patch the snap chain in wall drawing
    old_snap = "const snap=snapToEndpoint(wp,15/cam.zoom)||snapToGrid(wp);"
    new_snap = "const snap=snapToEndpoint(wp,15/cam.zoom)||snapToMidpoint(wp,15/cam.zoom)||snapToGrid(wp);"
    html = html.replace(old_snap, new_snap)
    c+=1
    print("+ Midpoint snap in wall draw")

    # Also in handle drag
    old_handle = "var snap=snapEnabled?(snapToEndpoint(wp,15/cam.zoom)||snapToGrid(wp)):wp;"
    new_handle = "var snap=snapEnabled?(snapToEndpoint(wp,15/cam.zoom)||snapToMidpoint(wp,15/cam.zoom)||snapToGrid(wp)):wp;"
    html = html.replace(old_handle, new_handle)
    c+=1
    print("+ Midpoint snap in handle drag")

# ======== 4. Help/About modal ========
if "showHelp" not in html:
    help_code = """
// ===================== Help =====================
window.showHelp=function(){
  alert(" CAD 交互编辑器 v3.0\\n\\n=== 快捷键 ===\\n1-6: 切换工具\\nCtrl+Z: 撤销  Ctrl+Shift+Z: 重做\\nCtrl+S: 保存  Ctrl+O: 打开\\nCtrl+C/V: 复制/粘贴墙\\nDel: 删除选中  F: 适配画面\\nEsc: 取消  +/-: 缩放\\n\\n=== 工具 ===\\n画墙: 点起点-点终点，自动吸附\\n门/窗: 点击墙放置\\n标注: 点两点出尺寸\\n房间: 自动识别封闭区域\\n选择: 点击墙-拖端点改尺寸\\n\\n=== 导出 ===\\nPNG/SVG/PDF/DXF/JSON\\n\\n图片: 上传户型图当背景描图\\n生成: 参数化自动生成户型\\n测距: 点两点量距离");
};
"""
    anim_marker2 = "// ===================== ANIMATION LOOP"
    if anim_marker2 in html:
        html = html.replace(anim_marker2, help_code + "\n" + anim_marker2)
        c+=1
        print("+ Help dialog")

# Add help button
old_clr_btn = 'onclick="clearAll()" style="color:#e74c3c"> 清空</button>'
if 'showHelp()"' not in html:
    html = html.replace(old_clr_btn, 'onclick="showHelp()"> ?</button>\n      <button class="btn" onclick="clearAll()" style="color:#e74c3c"> 清空</button>')
    c+=1
    print("+ Help button")

# ======== 5. 3D Window frames ========
win_frame = """
  // Window frames
  var frameMat=new THREE.MeshStandardMaterial({color:0x5D4037,roughness:0.7});
  var glassMat=new THREE.MeshStandardMaterial({color:0x87CEEB,roughness:0.1,metalness:0.3,transparent:true,opacity:0.3});
  for(var wf=-1;wf<=1;wf+=2){
    var frame=new THREE.Mesh(new THREE.BoxGeometry(0.05,1.5,1.2),frameMat);
    frame.position.set(wf*ROOM.w/2-0.1,ROOM.h/2-0.2,0);frame.castShadow=true;roomG.add(frame);
    var glass=new THREE.Mesh(new THREE.BoxGeometry(0.03,1.2,1.0),glassMat);
    glass.position.set(wf*ROOM.w/2-0.1,ROOM.h/2-0.2,0);roomG.add(glass);
  }
"""
# Find the 3D window section
if "0x87CEEB" in html and "Window frames" not in html:
    html = html.replace(
        "var win=new THREE.Mesh(new THREE.BoxGeometry(2.5,1.5,0.05),new THREE.MeshStandardMaterial({color:\"#87CEEB\",roughness:0.1,metalness:0.3,transparent:true,opacity:0.3}));",
        "var win=new THREE.Mesh(new THREE.BoxGeometry(2.5,1.5,0.05),new THREE.MeshStandardMaterial({color:\"#87CEEB\",roughness:0.1,metalness:0.3,transparent:true,opacity:0.3}));\n" + win_frame
    )
    c+=1
    print("+ 3D Window frames")

# ======== 6. Wall intersection cleanup ========
# When walls share an endpoint, merge them
intersection_code = """
// ===================== Wall cleanup =====================
window.cleanupWalls=function(){
  saveState();
  var merged=true;
  while(merged){
    merged=false;
    for(var i=0;i<walls.length&&!merged;i++){
      for(var j=i+1;j<walls.length&&!merged;j++){
        var w1=walls[i],w2=walls[j];
        var d11=Math.hypot(w1.x1-w2.x1,w1.y1-w2.y1);
        var d12=Math.hypot(w1.x1-w2.x2,w1.y1-w2.y2);
        var d21=Math.hypot(w1.x2-w2.x1,w1.y2-w2.y1);
        var d22=Math.hypot(w1.x2-w2.x2,w1.y2-w2.y2);
        var tol=50;
        if((d11<tol||d12<tol||d21<tol||d22<tol)&&Math.abs(w1.thick-w2.thick)<10){
          // Merge: keep the longer wall, extend it
          var len1=Math.hypot(w1.x2-w1.x1,w1.y2-w1.y1);
          var len2=Math.hypot(w2.x2-w2.x1,w2.y2-w2.y1);
          if(len2>len1){var tmp=w1;w1=w2;w2=tmp;}
          // Extend w1 to cover w2's far end
          if(d11<tol||d21<tol){
            if(d11<tol){w1.x1=w2.x2;w1.y1=w2.y2;}
            else if(d21<tol){w1.x2=w2.x2;w1.y2=w2.y2;}
          }else{
            if(d12<tol){w1.x1=w2.x1;w1.y1=w2.y1;}
            else if(d22<tol){w1.x2=w2.x1;w1.y2=w2.y1;}
          }
          walls.splice(j,1);
          merged=true;
        }
      }
    }
  }
  saveState();render2D();rebuild3D();updateStatus();
};
"""
if "cleanupWalls" not in html:
    anim_marker3 = "// ===================== ANIMATION LOOP"
    if anim_marker3 in html:
        html = html.replace(anim_marker3, intersection_code + "\n" + anim_marker3)
        c+=1
        print("+ Wall cleanup")

with open("E:/CAD自动化制图/interior_cad.html","w",encoding="utf-8") as f:
    f.write(html)
print(f"Done! {c} changes, {len(html)} bytes")
