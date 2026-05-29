import os

with open("E:/CAD自动化制图/interior_cad.html","r",encoding="utf-8") as f:
    html = f.read()

c = 0

# ==================== 1. ARC WALLS ====================
arc_data = """
// ===================== 弧墙 =====================
var wallsArc = [];

window._addArcWall = function(x1,y1,x2,y2,cx,cy,thick,type){
  var r=Math.hypot(cx-x1,cy-y1);
  var sa=Math.atan2(y1-cy,x1-cx);
  var ea=Math.atan2(y2-cy,x2-cx);
  // Ensure counter-clockwise
  if(sa>ea)ea+=Math.PI*2;
  wallsArc.push({id:nextId++,x1,y1,x2,y2,cx,cy,radius:r,startAngle:sa,endAngle:ea,thick:thick||200,type:type||"内墙"});
  saveState();render2D();rebuild3D();updateStatus();
};

var arcDrawState = null; // {x1,y1,x2,y2} collecting points

// Arc wall tool added as "7" key
"""

# Insert arc data before animation loop
am = "// ===================== ANIMATION LOOP"
if am in html:
    html = html.replace(am, arc_data + am)
    c += 1
    print("+ Arc wall data model")

# Add arc tool to toolbar
old_tools_end = '<button class="tool-btn" onclick="zoomFit()"> 适配</button>'
new_tools = '<button class="tool-btn" data-t="arc" onclick="setTool(\"arc\")"> 弧墙</button>\n      ' + old_tools_end
if "弧墙" not in html:
    html = html.replace(old_tools_end, new_tools)
    c += 1
    print("+ Arc wall tool button")

# Add arc to keyboard shortcuts
old_keys = '"6":"room"}'
new_keys = '"6":"room","7":"arc"}'
html = html.replace(old_keys, new_keys)
c += 1
print("+ Arc wall shortcut (7)")

# Add arc rendering to render2D
arc_render = """
  // Arc walls
  for(var a=0;a<wallsArc.length;a++){
    var aw=wallsArc[a];
    var p1=w2s(aw.x1,aw.y1),p2=w2s(aw.x2,aw.y2),pc=w2s(aw.cx,aw.cy);
    ctx.beginPath();
    ctx.arc(pc.x,pc.y,Math.hypot(aw.x1-aw.cx,aw.y1-aw.cy)*cam.zoom,aw.startAngle,aw.endAngle);
    ctx.strokeStyle=aw.type==="外墙"?"rgba(200,200,220,0.8)":"rgba(200,200,220,0.5)";
    ctx.lineWidth=Math.max(2,aw.thick*cam.zoom/20);
    ctx.stroke();
    // Inner arc
    var innerR=(Math.hypot(aw.x1-aw.cx,aw.y1-aw.cy)-aw.thick/2)*cam.zoom;
    if(innerR>2){
      ctx.beginPath();ctx.arc(pc.x,pc.y,innerR,aw.startAngle,aw.endAngle);
      ctx.strokeStyle=aw.type==="外墙"?"rgba(200,200,220,0.4)":"rgba(200,200,220,0.2)";
      ctx.lineWidth=1;ctx.stroke();
    }
    if(aw===sel){
      ctx.fillStyle="#667eea";ctx.beginPath();ctx.arc(p1.x,p1.y,6,0,Math.PI*2);ctx.fill();
      ctx.fillStyle="#fff";ctx.beginPath();ctx.arc(p1.x,p1.y,3,0,Math.PI*2);ctx.fill();
      ctx.fillStyle="#667eea";ctx.beginPath();ctx.arc(p2.x,p2.y,6,0,Math.PI*2);ctx.fill();
      ctx.fillStyle="#fff";ctx.beginPath();ctx.arc(p2.x,p2.y,3,0,Math.PI*2);ctx.fill();
    }
  }
"""
# Insert after walls rendering
wall_render_end = "ctx.stroke();\n\n  // Doors"
if wall_render_end in html:
    html = html.replace(wall_render_end, "ctx.stroke();\n" + arc_render + "  // Doors")
    c += 1
    print("+ Arc wall 2D rendering")

# Arc wall pointerdown handler
arc_handler = """
  if(tool==="arc"){
    if(!arcDrawState){
      arcDrawState={x1:wp.x,y1:wp.y};
      document.getElementById("tool-status").textContent="  弧墙: 点第二点(弧中点)";
    }else if(!arcDrawState.x2){
      arcDrawState.x2=wp.x;arcDrawState.y2=wp.y;
      document.getElementById("tool-status").textContent="  弧墙: 点第三点(终点)";
    }else{
      // Three points: start, middle control, end -> compute arc center
      var x1=arcDrawState.x1,y1=arcDrawState.y1;
      var x3=wp.x,y3=wp.y;
      var x2=arcDrawState.x2,y2=arcDrawState.y2;
      // Perpendicular bisectors intersection = center
      var ma=(y2-y1)/(x2-x1+0.001),mb=(y3-y2)/(x3-x2+0.001);
      var cx=(ma*mb*(y1-y3)+mb*(x1+x2)-ma*(x2+x3))/(2*(mb-ma)+0.001);
      var cy=-1/ma*(cx-(x1+x2)/2)+(y1+y2)/2;
      // Check if valid
      var r=Math.hypot(cx-x1,cy-y1);
      if(r>500&&r<50000){
        window._addArcWall(x1,y1,x3,y3,cx,cy);
      }else{
        document.getElementById("tool-status").textContent="  弧墙: 弧半径不合理, 重试";
      }
      arcDrawState=null;
    }
    return;
  }
"""

# Insert into pointerdown before the select handler
pd_sel = "  // select\n  const hit=hitTest(wp.x,wp.y);"
if pd_sel in html:
    html = html.replace(pd_sel, arc_handler + "\n" + pd_sel)
    c += 1
    print("+ Arc wall pointer handler")

with open("E:/CAD自动化制图/interior_cad.html","w",encoding="utf-8") as f:
    f.write(html)
print(f"Done! {c} changes, {len(html)} bytes")
