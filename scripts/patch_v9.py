import os

with open("E:/CAD自动化制图/interior_cad.html","r",encoding="utf-8") as f:
    html = f.read()
c = 0

# ==================== 1. POLYLINE TOOL (多段线) ====================
# Add polyline tool function
polyline_func = """
// ===================== 多段线 =====================
var polylinePts = []; // [{x,y}]

// Enhanced setTool to handle polyline cleanup
var origSetTool = setTool;
setTool = function(t){
  if(t!=="polyline" && polylinePts.length>1){polylinePts=[];}
  origSetTool(t);
};

// Polyline pointer handler
function handlePolylineClick(wp){
  if(polylinePts.length===0){
    // First point
    polylinePts.push({x:wp.x,y:wp.y});
    document.getElementById("tool-status").textContent="  多段线: 点第2点 (回车/Esc结束, 双击结束)";
    render2D();
    return true;
  }
  // Add point and create wall
  var last = polylinePts[polylinePts.length-1];
  var snap = snapEnabled ? (snapToEndpoint(wp,15/cam.zoom)||snapToMidpoint(wp,15/cam.zoom)||snapToGrid(wp)) : wp;
  if(Math.hypot(snap.x-last.x,snap.y-last.y)>100){
    polylinePts.push({x:snap.x,y:snap.y});
    walls.push({id:nextId++,x1:last.x,y1:last.y,x2:snap.x,y2:snap.y,thick:200,type:"内墙"});
    saveState();
    render2D();
    rebuild3D();
    updateStatus();
    document.getElementById("tool-status").textContent="  多段线: 已画"+(polylinePts.length-1)+"段, 继续点 / 结束";
  }
  return true;
}

// Finish polyline
function finishPolyline(){
  if(polylinePts.length<2)return;
  polylinePts=[];
  setTool("select");
  document.getElementById("tool-status").textContent="  多段线结束";
}
"""

am = "// ===================== ANIMATION LOOP"
if am in html:
    html = html.replace(am, polyline_func + am)
    c+=1; print("+ Polyline tool")

# Add polyline tool button
old_tools = 'data-t="arc" onclick="setTool('
new_tools = 'data-t="polyline" onclick="setTool(\'polyline\')"> 多段</button>\n      <button class="tool-btn" data-t="arc" onclick="setTool('
if 'polyline' not in html:
    html = html.replace(old_tools, new_tools)
    c+=1; print("+ Polyline button")

# Add DblClick handler for polyline finish
dbl_handler = """
c2.addEventListener("dblclick",function(e){
  if(tool==="polyline"&&polylinePts.length>1){finishPolyline();}
});
"""
pm_register = 'c2.addEventListener("pointermove"'
if pm_register in html:
    html = html.replace(pm_register, dbl_handler + pm_register)
    c+=1; print("+ Double-click handler")

# Add polyline wall drawing in pointerdown
old_arc_handler = 'if(tool==="arc"){'
new_poly_handler = 'if(tool==="polyline"){handlePolylineClick(wp);return;}\n  '+old_arc_handler
if old_arc_handler in html:
    html = html.replace(old_arc_handler, new_poly_handler, 1)
    c+=1; print("+ Polyline pointer integration")

# Add keyboard shortcut for polyline end
old_escape = 'case "Escape": wallDraw=null;'
new_escape = 'case "Escape": if(tool==="polyline"){finishPolyline()}else{wallDraw=null;}'
html = html.replace(old_escape, new_escape)
c+=1; print("+ Esc to end polyline")

# Add Enter key for polyline
old_f_case = 'case "f": case "F": zoomFit(); break;'
new_f_case = 'case "Enter": if(tool==="polyline"){e.preventDefault();finishPolyline()}break;\n      case "f": case "F": zoomFit(); break;'
html = html.replace(old_f_case, new_f_case)
c+=1; print("+ Enter to finish polyline")

# Add polyline keyboard shortcut "8"
old_keys = '"7":"arc"}'
new_keys = '"7":"arc","8":"polyline"}'
html = html.replace(old_keys, new_keys)
c+=1; print("+ Polyline shortcut 8")

# Polyline rendering (show connected segments while drawing)
polyline_render = """
  // Polyline preview
  if(tool==="polyline"&&polylinePts.length>0){
    for(var pi=1;pi<polylinePts.length;pi++){
      var pp1=w2s(polylinePts[pi-1].x,polylinePts[pi-1].y);
      var pp2=w2s(polylinePts[pi].x,polylinePts[pi].y);
      ctx.strokeStyle="#667eea";ctx.lineWidth=3;
      ctx.beginPath();ctx.moveTo(pp1.x,pp1.y);ctx.lineTo(pp2.x,pp2.y);ctx.stroke();
      ctx.fillStyle="#667eea";ctx.beginPath();ctx.arc(pp1.x,pp1.y,4,0,Math.PI*2);ctx.fill();
    }
    // Line to cursor
    if(polylinePts.length>0&&mPos){
      var last=w2s(polylinePts[polylinePts.length-1].x,polylinePts[polylinePts.length-1].y);
      var cur=w2s(mPos.x,mPos.y);
      ctx.strokeStyle="rgba(102,126,234,0.4)";ctx.lineWidth=2;ctx.setLineDash([5,3]);
      ctx.beginPath();ctx.moveTo(last.x,last.y);ctx.lineTo(cur.x,cur.y);ctx.stroke();ctx.setLineDash([]);
      // Distance
      var dist=Math.hypot(mPos.x-polylinePts[polylinePts.length-1].x,mPos.y-polylinePts[polylinePts.length-1].y);
      ctx.fillStyle="rgba(102,126,234,0.8)";ctx.font="10px sans-serif";ctx.textAlign="center";
      ctx.fillText((dist/1000).toFixed(2)+"m",(last.x+cur.x)/2,(last.y+cur.y)/2-8);
    }
  }
"""
# Insert into render2D
render_marker = "// Polyline preview"
if render_marker not in html:
    # Insert before scale bar
    html = html.replace("// Scale bar", polyline_render + "\n// Scale bar")
    c+=1; print("+ Polyline rendering")

# ==================== 2. OFFSET COMMAND ====================
offset_func = """
// ===================== 偏移 =====================
var offsetDist = 1000; // 1m default
var offsetPreview = null; // {x1,y1,x2,y2}

window.doOffset = function(){
  if(!sel){
    document.getElementById("tool-status").textContent="  偏移: 先选中要偏移的墙";
    return;
  }
  var dx=sel.x2-sel.x1, dy=sel.y2-sel.y1;
  var len=Math.hypot(dx,dy);
  if(len<1)return;
  var nx=-dy/len*offsetDist, ny=dx/len*offsetDist;
  saveState();
  walls.push({id:nextId++,x1:sel.x1+nx,y1:sel.y1+ny,x2:sel.x2+nx,y2:sel.y2+ny,thick:sel.thick,type:sel.type});
  saveState();render2D();rebuild3D();updateStatus();
  document.getElementById("tool-status").textContent="  偏移: 已创建平行墙 (距离"+offsetDist+"mm)";
};

window.setOffsetDist = function(d){
  offsetDist = Math.max(100, Math.min(10000, d));
  document.getElementById("tool-status").textContent="  偏移距离: "+offsetDist+"mm";
};
"""

if am in html:
    html = html.replace(am, offset_func + am)
    c+=1; print("+ Offset command")

# Add offset button to props panel
old_props_btns = 'onclick="splitWall()">分割</button>'
if 'doOffset()' not in html:
    html = html.replace(old_props_btns, 'onclick="splitWall()">分割</button>\n      <button class="btn" style="padding:2px 6px;font-size:10px" onclick="doOffset()">偏移</button>')
    c+=1; print("+ Offset button in props")

# ==================== 3. TOUCH SUPPORT ====================
touch_support = """
// ===================== 触屏适配 =====================
// Touch-to-mouse translation for better mobile support
// Also add pinch zoom
var touchDist = 0;

document.addEventListener("touchstart", function(e){
  if(e.touches.length===1){
    // Forward to pointer handlers - create a synthetic event
    var touch = e.touches[0];
    var me = new MouseEvent("pointerdown", {
      clientX: touch.clientX, clientY: touch.clientY,
      bubbles: true, cancelable: true
    });
    e.target.dispatchEvent(me);
  } else if(e.touches.length===2){
    touchDist = Math.hypot(
      e.touches[0].clientX-e.touches[1].clientX,
      e.touches[0].clientY-e.touches[1].clientY
    );
  }
}, {passive: true});

document.addEventListener("touchmove", function(e){
  if(e.touches.length===1 && tool!=="select"){
    e.preventDefault();
    var touch = e.touches[0];
    var me = new MouseEvent("pointermove", {
      clientX: touch.clientX, clientY: touch.clientY,
      bubbles: true, cancelable: true
    });
    e.target.dispatchEvent(me);
  } else if(e.touches.length===2){
    e.preventDefault();
    var newDist = Math.hypot(
      e.touches[0].clientX-e.touches[1].clientX,
      e.touches[0].clientY-e.touches[1].clientY
    );
    var scale = newDist / touchDist;
    cam.zoom *= scale;
    cam.zoom = Math.max(0.05, Math.min(10, cam.zoom));
    touchDist = newDist;
    render2D();
  }
}, {passive: false});

document.addEventListener("touchend", function(e){
  if(e.changedTouches.length===1 && e.touches.length===0){
    var touch = e.changedTouches[0];
    var me = new MouseEvent("pointerup", {
      clientX: touch.clientX, clientY: touch.clientY,
      bubbles: true, cancelable: true
    });
    e.target.dispatchEvent(me);
  }
}, {passive: true});

// Responsive UI - make side panels collapsible
function checkMobile(){
  var isMobile = window.innerWidth < 768;
  var leftPanel = document.getElementById("left-panel");
  var sidebar = document.getElementById("sidebar");
  if(isMobile){
    leftPanel.style.width = "100%";
    leftPanel.style.height = "50%";
    sidebar.style.display = "none";
  } else {
    leftPanel.style.width = "";
    leftPanel.style.height = "";
    sidebar.style.display = "";
  }
}
window.addEventListener("resize", checkMobile);
setTimeout(checkMobile, 500);
"""

if am in html:
    html = html.replace(am, touch_support + am)
    c+=1; print("+ Touch support")

with open("E:/CAD自动化制图/interior_cad.html","w",encoding="utf-8") as f:
    f.write(html)
print(f"Done! {c} changes, {len(html)} bytes")
