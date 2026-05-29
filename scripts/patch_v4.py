import os
with open("E:/CAD自动化制图/interior_cad.html","r",encoding="utf-8") as f:
    html = f.read()
c=0

wall_tt = """
  if(tool==="select"&&!sel){
    var hit=hitTest(wp.x,wp.y);
    if(hit&&hit.type==="wall"){
      var wl=Math.hypot(hit.obj.x2-hit.obj.x1,hit.obj.y2-hit.obj.y1);
      document.getElementById("coord-status").textContent="\u7899\u957f: "+(wl/1000).toFixed(2)+"m";
      c2.style.cursor="pointer";
    }
  }
"""
marker1 = "// Handle drag for wall endpoints"
if marker1 in html:
    if wall_tt.strip() not in html:
        html = html.replace(marker1, wall_tt + "\n" + marker1)
        c += 1
        print("+ Wall length tooltip")

old_ctrl = 'case "z": case "Z": e.shiftKey ? redo() : undo(); e.preventDefault(); break;'
new_ctrl = 'case "c": if(sel){clipboardItem={id:sel.id,x1:sel.x1,y1:sel.y1,x2:sel.x2,y2:sel.y2,thick:sel.thick,type:sel.type};document.getElementById("tool-status").textContent=" Copied wall";e.preventDefault()}break;\n      case "v": if(clipboardItem){saveState();var nid=nextId++;walls.push({id:nid,x1:clipboardItem.x1+1000,y1:clipboardItem.y1,x2:clipboardItem.x2+1000,y2:clipboardItem.y2,thick:clipboardItem.thick,type:clipboardItem.type});sel=walls[walls.length-1];saveState();render2D();rebuild3D();updateStatus();document.getElementById("tool-status").textContent=" Pasted wall";e.preventDefault()}break;\n      case "z": case "Z": e.shiftKey ? redo() : undo(); e.preventDefault(); break;'
if "clipboardItem" not in html:
    html = html.replace(
        'document.addEventListener("keydown", function(e){',
        'var clipboardItem=null;\ndocument.addEventListener("keydown", function(e){'
    )
    html = html.replace(old_ctrl, new_ctrl)
    c += 1
    print("+ Copy/paste walls")

old_render_wall = 'if(w===sel||w===hover){'
new_render_wall = 'if(w===sel||w===hover){\n      ctx.fillStyle="#667eea";ctx.beginPath();ctx.arc(p1.x,p1.y,6,0,Math.PI*2);ctx.fill();\n      ctx.fillStyle="#fff";ctx.beginPath();ctx.arc(p1.x,p1.y,3,0,Math.PI*2);ctx.fill();\n      ctx.fillStyle="#667eea";ctx.beginPath();ctx.arc(p2.x,p2.y,6,0,Math.PI*2);ctx.fill();\n      ctx.fillStyle="#fff";ctx.beginPath();ctx.arc(p2.x,p2.y,3,0,Math.PI*2);ctx.fill();'
if 'arc(p1.x,p1.y,6' not in html:
    html = html.replace(old_render_wall, new_render_wall)
    c += 1
    print("+ Wall handle rendering")

old_props_title = '<div class="title">  墙属性</div>'
new_props = '<div class="title">  墙属性 <span style="font-size:10px;color:rgba(255,255,255,0.3)">(拖端点改尺寸)</span></div>'
if old_props_title in html:
    html = html.replace(old_props_title, new_props)
    c += 1
    print("+ Enhanced props panel")

with open("E:/CAD自动化制图/interior_cad.html","w",encoding="utf-8") as f:
    f.write(html)
print(f"Done! {c} changes, {len(html)} bytes")
