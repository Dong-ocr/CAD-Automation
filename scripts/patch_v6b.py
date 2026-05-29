import os
with open("E:/CAD自动化制图/interior_cad.html","r",encoding="utf-8") as f:
    html = f.read()
c=0

# 1 - Auto-save
if "autoSaveInterval" not in html:
    as_code = "var autoSaveInterval=setInterval(function(){try{var d={walls:walls.slice(0,50),doors:doors.slice(0,20),windows:windows.slice(0,10),rooms:rooms.slice(0,20)};localStorage.setItem(\"cad_autosave\",JSON.stringify(d))}catch(e){}},30000);\nwindow.recoverAutoSave=function(){try{var d=JSON.parse(localStorage.getItem(\"cad_autosave\"));if(d&&d.walls&&d.walls.length>0){if(confirm(\"恢复自动保存的草图?\")){walls=d.walls;doors=d.doors||[];windows=d.windows||[];rooms=d.rooms||[];saveState();render2D();rebuild3D();updateStatus()}}}catch(e){}};\n"
    am = "// ===================== ANIMATION LOOP"
    if am in html:
        html = html.replace(am, as_code + am)
        c+=1; print("+ Auto-save")

# 2 - Snap to midpoint
if "snapToMidpoint" not in html:
    sm = "window.snapToMidpoint=function(p,dist){if(!snapEnabled)return null;for(var w=0;w<walls.length;w++){var mx=(walls[w].x1+walls[w].x2)/2,my=(walls[w].y1+walls[w].y2)/2;if(Math.hypot(p.x-mx,p.y-my)*cam.zoom<dist)return{x:mx,y:my}}return null};\n"
    sm_marker = "var origSnapToEndpoint = snapToEndpoint;"
    if sm_marker in html:
        html = html.replace(sm_marker, sm + sm_marker)
        c+=1; print("+ Midpoint snap")
    # Patch wall drawing snap chain
    html = html.replace(
        "const snap=snapToEndpoint(wp,15/cam.zoom)||snapToGrid(wp);",
        "const snap=snapToEndpoint(wp,15/cam.zoom)||snapToMidpoint(wp,15/cam.zoom)||snapToGrid(wp);"
    )
    c+=1; print("+ Midpoint in wall draw")

# 3 - Help
if "showHelp" not in html:
    h = "window.showHelp=function(){alert(\" CAD v3.0\\n\\n1-6: 工具切换\\nCtrl+Z: 撤销\\nCtrl+C/V: 复制/粘贴墙\\nDel: 删除\\nF: 适配\\n+/-: 缩放\\n\\n画墙: 点起点/终点\\n门/窗: 点墙放置\\n选择: 拖端点改尺寸\\n\\nPNG/SVG/PDF/DXF 导出\\n图片: 描图底图\\n生成: 自动户型\");};\n"
    am2 = "// ===================== ANIMATION LOOP"
    if am2 in html:
        html = html.replace(am2, h + am2)
        c+=1; print("+ Help dialog")
    # Add help button
    old_clr = 'onclick="clearAll()" style="color:#e74c3c"> 清空</button>'
    if 'showHelp()' not in html:
        html = html.replace(old_clr, 'onclick="showHelp()"> ?</button>\n      <button class="btn" onclick="clearAll()" style="color:#e74c3c"> 清空</button>')
        c+=1; print("+ Help button")

# 4 - Wall cleanup
if "cleanupWalls" not in html:
    cw = "window.cleanupWalls=function(){saveState();var merged=true;while(merged){merged=false;for(var i=0;i<walls.length&&!merged;i++){for(var j=i+1;j<walls.length&&!merged;j++){var w1=walls[i],w2=walls[j];var d11=Math.hypot(w1.x1-w2.x1,w1.y1-w2.y1);var d12=Math.hypot(w1.x1-w2.x2,w1.y1-w2.y2);var d21=Math.hypot(w1.x2-w2.x1,w1.y2-w2.y1);var d22=Math.hypot(w1.x2-w2.x2,w1.y2-w2.y2);var tol=50;if((d11<tol||d12<tol||d21<tol||d22<tol)&&Math.abs(w1.thick-w2.thick)<10){var len1=Math.hypot(w1.x2-w1.x1,w1.y2-w1.y1);var len2=Math.hypot(w2.x2-w2.x1,w2.y2-w2.y1);if(len2>len1){var tmp=w1;w1=w2;w2=tmp}if(d11<tol||d21<tol){if(d11<tol){w1.x1=w2.x2;w1.y1=w2.y2}else{w1.x2=w2.x2;w1.y2=w2.y2}}else{if(d12<tol){w1.x1=w2.x1;w1.y1=w2.y1}else{w1.x2=w2.x1;w1.y2=w2.y1}}walls.splice(j,1);merged=true}}}}}saveState();render2D();rebuild3D();updateStatus();};\n"
    am3 = "// ===================== ANIMATION LOOP"
    if am3 in html:
        html = html.replace(am3, cw + am3)
        c+=1; print("+ Wall cleanup")
    # Add cleanup button to header
    html = html.replace(
        'onclick="showHelp()"> ?</button>',
        'onclick="showHelp()"> ?</button>\n      <button class="btn" onclick="cleanupWalls()"> 合并</button>'
    )
    c+=1; print("+ Cleanup button")

# 5 - 3D scene enhancements (window frames)
if "Window frame" not in html:
    wf_code = "  // Window frame\n  var fMat=new THREE.MeshStandardMaterial({color:0x5D4037,roughness:0.7});\n  var gMat=new THREE.MeshStandardMaterial({color:0x87CEEB,roughness:0.1,metalness:0.3,transparent:true,opacity:0.3});\n"
    wf_marker = "roomG.add(win);"
    if wf_marker in html:
        html = html.replace(wf_marker, wf_marker + "\n  for(var wfi=-1;wfi<=1;wfi+=2){var f=new THREE.Mesh(new THREE.BoxGeometry(0.05,1.5,1.2),fMat);f.position.set(wfi*ROOM.w/2-0.1,ROOM.h/2-0.2,0);f.castShadow=true;roomG.add(f);var g=new THREE.Mesh(new THREE.BoxGeometry(0.03,1.2,1.0),gMat);g.position.set(wfi*ROOM.w/2-0.1,ROOM.h/2-0.2,0);roomG.add(g)}")
        c+=1; print("+ 3D Window frames")

with open("E:/CAD自动化制图/interior_cad.html","w",encoding="utf-8") as f:
    f.write(html)
print(f"Done! {c} changes, {len(html)} bytes")
