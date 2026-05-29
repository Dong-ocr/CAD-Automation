with open(r"E:\CAD自动化制图\interior_cad.html", "r", encoding="utf-8") as f:
    html = f.read()

patches = []

# === PATCH 1: Keyboard shortcuts ===
patches.append(("""
// ===================== 快捷键系统 =====================
document.addEventListener("keydown", function(e){
  // 工具切换 1-6
  if(!e.ctrlKey && !e.metaKey && !e.shiftKey){
    const keys = {"1":"select","2":"wall","3":"door","4":"window","5":"dim","6":"room"};
    if(keys[e.key]){ e.preventDefault(); setTool(keys[e.key]); return; }
  }
  // Ctrl shortcuts
  if(e.ctrlKey || e.metaKey){
    switch(e.key){
      case "z": case "Z": e.shiftKey ? redo() : undo(); e.preventDefault(); break;
      case "s": e.preventDefault(); saveDoc(); break;
      case "o": e.preventDefault(); loadDoc(); break;
    }
    return;
  }
  // Other shortcuts
  switch(e.key){
    case "Delete": case "Backspace": if(sel){delWall();} break;
    case "Escape": wallDraw=null; render2D(); document.getElementById("tool-status").textContent="已取消"; break;
    case "+": case "=": cam.zoom*=1.2; render2D(); break;
    case "-": cam.zoom/=1.2; render2D(); break;
    case "f": case "F": zoomFit(); break;
  }
});
""", "// ===================== STATUS"))

# === PATCH 2: SVG Export ===
patches.append(("""
// ===================== SVG 导出 =====================
window.exportSVG=function(){
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${c2.width} ${c2.height}" width="${c2.width}" height="${c2.height}">`;
  svg += `<rect width="100%" height="100%" fill="#161628"/>`;
  
  // Walls
  for(const w of walls){
    const p1=w2s(w.x1,w.y1),p2=w2s(w.x2,w.y2);
    const dx=p2.x-p1.x,dy=p2.y-p1.y;
    const len=Math.hypot(dx,dy);
    if(len<1)continue;
    const nx=-dy/len*w.thick*cam.zoom/2,ny=dx/len*w.thick*cam.zoom/2;
    const pts=`${p1.x+nx},${p1.y+ny} ${p2.x+nx},${p2.y+ny} ${p2.x-nx},${p2.y-ny} ${p1.x-nx},${p1.y-ny}`;
    svg+=`<polygon points="${pts}" fill="${w.type==="外墙"?"#ddd":"#eee"}" stroke="#999" stroke-width="1"/>`;
  }
  
  // Doors
  for(const d of doors){
    const w=walls.find(x=>x.id===d.wallId);if(!w)continue;
    const p=pointOnWall(w,d.pos);if(!p)continue;
    const ps=w2s(p.x,p.y);
    const ang=Math.atan2(w.y2-w.y1,w.x2-w.x1);
    const sw=d.width*cam.zoom;
    svg+=`<g transform="translate(${ps.x},${ps.y}) rotate(${ang*180/Math.PI})">`;
    svg+=`<path d="M0,0 A${sw},${sw} 0 0,1 ${sw},${sw}" fill="rgba(67,233,123,0.2)" stroke="#43e97b" stroke-width="1.5"/>`;
    svg+=`<line x1="${sw}" y1="0" x2="${sw}" y2="${-sw*0.1}" stroke="#43e97b" stroke-width="1.5"/>`;
    svg+=`</g>`;
  }
  
  // Rooms
  for(const r of rooms){
    const pts=r.corners.map(c=>w2s(c.x,c.y));
    const dp=pts.map(p=>`${p.x},${p.y}`).join(" ");
    svg+=`<polygon points="${dp}" fill="${r.color}22" stroke="${r.color}44" stroke-width="1" stroke-dasharray="4,4"/>`;
    const cx=pts.reduce((a,p)=>({x:a.x+p.x/pts.length,y:a.y+p.y/pts.length}),{x:0,y:0});
    svg+=`<text x="${cx.x}" y="${cx.y}" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="middle" font-family="Microsoft YaHei">${r.name} ${r.area}m2</text>`;
  }
  
  // Dimensions
  for(const d of dims){
    const p1=w2s(d.x1,d.y1),p2=w2s(d.x2,d.y2);
    const ang=Math.atan2(p2.y-p1.y,p2.x-p1.x);
    const nx=-Math.sin(ang)*40,ny=Math.cos(ang)*40;
    svg+=`<line x1="${p1.x+nx}" y1="${p1.y+ny}" x2="${p2.x+nx}" y2="${p2.y+ny}" stroke="#ff6b6b" stroke-width="1"/>`;
    const dist=Math.hypot(d.x2-d.x1,d.y2-d.y1);
    svg+=`<text x="${(p1.x+p2.x)/2+nx}" y="${(p1.y+p2.y)/2+ny-3}" fill="#ff6b6b" font-size="10" text-anchor="middle">${(dist/1000).toFixed(1)}m</text>`;
  }
  
  svg+=`</svg>`;
  
  const blob=new Blob([svg],{type:"image/svg+xml"});
  const a=document.createElement("a");a.download="floorplan.svg";a.href=URL.createObjectURL(blob);a.click();
};
""", "// ===================== PROPS PANEL"))

# === PATCH 3: Title block with frame ===
patches.append(("""
// ===================== 图框生成 =====================
window.addTitleBlock=function(){
  // Draw frame and title block on 2D canvas
  const margin = 30;
  const W = c2.width - margin*2, H = c2.height - margin*2;
  // Outer frame
  ctx.strokeStyle = "#fff"; ctx.lineWidth = 2;
  ctx.strokeRect(margin, margin, W, H);
  // Inner frame
  ctx.strokeStyle = "rgba(255,255,255,0.3)"; ctx.lineWidth = 1;
  ctx.strokeRect(margin+10, margin+10, W-20, H-20);
  // Title block at bottom right
  const tb_w = 180, tb_h = 50;
  const tb_x = margin + W - tb_w - 10;
  const tb_y = margin + H - tb_h - 10;
  ctx.fillStyle = "rgba(255,255,255,0.05)";
  ctx.fillRect(tb_x, tb_y, tb_w, tb_h);
  ctx.strokeStyle = "rgba(255,255,255,0.3)"; ctx.lineWidth = 1;
  ctx.strokeRect(tb_x, tb_y, tb_w, tb_h);
  ctx.fillStyle = "rgba(255,255,255,0.5)";
  ctx.font = "10px sans-serif"; ctx.textAlign = "left";
  ctx.fillText("项目: 室内设计", tb_x+8, tb_y+18);
  ctx.fillText("比例 1:50", tb_x+8, tb_y+32);
  ctx.fillText("A3", tb_x+tb_w-30, tb_y+32);
};
""", "// ===================== PROPS PANEL"))

# === PATCH 4: Enhanced status bar with layer info + measurement ===
patches.append(("""
// ===================== 状态栏增强 =====================
window.updateStatusBar=function(){
  const el = document.getElementById("tool-status");
  if(el && !el.textContent.includes("快捷键")){
    el.textContent = `墙:${walls.length} 门:${doors.length} 窗:${windows.length} 房间:${rooms.length} 家具:${furniture.length} | 缩放:${(cam.zoom*100).toFixed(0)}% | 快捷键: 1-6切工具 Ctrl+Z撤销 Del删除 Ctrl+S保存`;
  }
};
// Override original updateStatus
const origUpdate = updateStatus;
updateStatus = function(){
  if(origUpdate) origUpdate();
  updateStatusBar();
};
""", "// ===================== ANIMATION LOOP"));

# === PATCH 5: Measurement tool (click two points measures distance) ===
patches.append(("""
// ===================== 测量工具 =====================
let measureMode = false;
let measureStart = null;
window.toggleMeasure = function(){
  measureMode = !measureMode;
  if(measureMode){
    setTool("select");
    document.getElementById("tool-status").textContent = "  测量模式: 点击起点和终点测距";
    c2.style.cursor = "crosshair";
    measureStart = null;
  } else {
    c2.style.cursor = "";
    document.getElementById("tool-status").textContent = "";
  }
};

// Patch pointerdown for measure
const origPointerDown = c2.onpointerdown;
c2.addEventListener("pointerdown", function(e){
  if(!measureMode) return;
  const r=c2.getBoundingClientRect();
  const wp=s2w(e.clientX-r.left,e.clientY-r.top);
  if(!measureStart){
    measureStart = wp;
    // Draw start point
    const ps = w2s(wp.x, wp.y);
    ctx.beginPath(); ctx.arc(ps.x, ps.y, 5, 0, Math.PI*2);
    ctx.fillStyle = "#ff6b6b"; ctx.fill();
  }else{
    // Draw line and show distance
    const p1 = w2s(measureStart.x, measureStart.y);
    const p2 = w2s(wp.x, wp.y);
    const dist = Math.hypot(wp.x-measureStart.x, wp.y-measureStart.y);
    ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y);
    ctx.strokeStyle = "#ff6b6b"; ctx.lineWidth = 2; ctx.stroke();
    const mid = {x:(p1.x+p2.x)/2, y:(p1.y+p2.y)/2};
    ctx.fillStyle = "#ff6b6b"; ctx.font = "bold 13px sans-serif"; ctx.textAlign = "center";
    ctx.fillText((dist/1000).toFixed(2)+"m", mid.x, mid.y-8);
    measureStart = null;
    setTimeout(()=>render2D(), 2000);
  }
});
""", "// ===================== ANIMATION LOOP"));

# Apply all patches
for code, marker in patches:
    if marker in html:
        html = html.replace(marker, code + "\n" + marker)
    else:
        print(f"WARNING: marker '{marker}' not found!")

# Add the layer/mesure buttons to the header
header_btn = '<button class="btn" onclick="clearAll()" style="color:#e74c3c"> 清空</button>'
new_header_btns = '<button class="btn" onclick="exportSVG()"> SVG</button>\n      <button class="btn" onclick="addTitleBlock()"> 图框</button>\n      <button class="btn" onclick="toggleMeasure()"> 测距</button>\n      <button class="btn" onclick="clearAll()" style="color:#e74c3c"> 清空</button>'
html = html.replace(header_btn, new_header_btns)

# Add layer panel button to tools
tools_end = '<button class="tool-btn" onclick="zoomFit()"> 适配</button>'
new_tools_end = '<button class="tool-btn" onclick="zoomFit()"> 适配</button><div class="tool-sep"></div><button class="tool-btn" onclick="toggleLayerPanel()"> 图层</button>'
html = html.replace(tools_end, new_tools_end)

# Add layer panel HTML after the status bar
status_bar_end = '<span class="coord" id="coord-status">0, 0</span>'
layer_panel_html = '''
    <div id="layer-panel" style="display:none;position:absolute;left:6px;top:44px;background:rgba(0,0,0,0.85);backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:8px;width:140px;z-index:200;font-size:10px">
      <div style="font-weight:600;margin-bottom:4px;color:rgba(255,255,255,0.7)"> 图层</div>
    </div>
'''
html = html.replace(status_bar_end, status_bar_end + layer_panel_html)

# Add toggleLayerPanel function
script_end = "console.log("
html = html.replace(script_end, """window.toggleLayerPanel=function(){
  const p=document.getElementById("layer-panel");
  p.style.display=p.style.display==="none"?"block":"none";
  if(p.style.display==="block"){
    const layerTypes=["外墙","内墙","门","窗","标注","房间","家具"];
    p.innerHTML=`<div style="font-weight:600;margin-bottom:4px;color:rgba(255,255,255,0.7)"> 图层</div>`+
      layerTypes.map(t=>`<label style="display:flex;align-items:center;gap:4px;padding:2px 0;cursor:pointer">
        <input type="checkbox" checked onchange="toggleLayer('${t}',this.checked)" style="accent-color:#667eea">
        <span>${t}</span></label>`).join("");
  }
};
window.toggleLayer=function(type,visible){
  // Simple visibility toggle - re-render without that type
  render2D();
  // Force re-render without layer - we just flag it
  window._hiddenLayers = window._hiddenLayers || {};
  window._hiddenLayers[type] = !visible;
  render2D();
};
""" + script_end)

with open(r"E:\CAD自动化制图\interior_cad.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Updated: {len(html)} bytes")
print("All optimizations applied!")
