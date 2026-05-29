import os
with open("E:/CAD自动化制图/interior_cad.html","r",encoding="utf-8") as f:
    html = f.read()
c=0

# ==================== 2D HATCH PATTERNS ====================
hatch_code = """
// ===================== 填充图案 =====================
window.hatchPatterns = {
  // ANSI31: 45 degree parallel lines
  ansi31: function(ctx,x,y,w,h,scale){
    ctx.save();
    ctx.beginPath();
    for(var i=-h;i<w+h;i+=4*scale){
      ctx.moveTo(x+i,y);ctx.lineTo(x+i+h,y+h);
    }
    ctx.strokeStyle="rgba(100,100,100,0.3)";ctx.lineWidth=0.5;
    ctx.stroke();
    ctx.restore();
  },
  // Wood grain: horizontal wavy lines
  wood: function(ctx,x,y,w,h,scale){
    ctx.save();
    for(var i=0;i<h;i+=6*scale){
      ctx.beginPath();
      ctx.moveTo(x,y+i);
      for(var j=0;j<w;j+=3){
        ctx.lineTo(x+j,y+i+Math.sin(j*0.1)*1.5*scale);
      }
      ctx.strokeStyle="rgba(180,140,100,0.25)";ctx.lineWidth=0.5;
      ctx.stroke();
    }
    ctx.restore();
  },
  // Tile: grid pattern
  tile: function(ctx,x,y,w,h,scale){
    ctx.save();
    ctx.strokeStyle="rgba(150,150,150,0.2)";ctx.lineWidth=0.5;
    for(var i=0;i<w;i+=20*scale){ctx.beginPath();ctx.moveTo(x+i,y);ctx.lineTo(x+i,y+h);ctx.stroke();}
    for(var i=0;i<h;i+=20*scale){ctx.beginPath();ctx.moveTo(x,y+i);ctx.lineTo(x+w,y+i);ctx.stroke();}
    ctx.restore();
  },
  // Concrete: random dots
  concrete: function(ctx,x,y,w,h,scale){
    ctx.save();
    ctx.fillStyle="rgba(120,120,120,0.15)";
    var seed=12345;
    for(var i=0;i<50;i++){
      seed=(seed*9301+49297)%233280;
      var dx=seed/233280*w;
      seed=(seed*9301+49297)%233280;
      var dy=seed/233280*h;
      seed=(seed*9301+49297)%233280;
      var dr=seed/233280*3*scale+1;
      ctx.beginPath();ctx.arc(x+dx,y+dy,dr,0,Math.PI*2);ctx.fill();
    }
    ctx.restore();
  }
};

window.applyHatch=function(roomIdx,pattern){
  if(roomIdx<0||roomIdx>=rooms.length)return;
  rooms[roomIdx].hatch=pattern;
  render2D();
};
"""

am = "// ===================== ANIMATION LOOP"
if am in html:
    html = html.replace(am, hatch_code + am)
    c+=1; print("+ Hatch patterns")

# Add hatch rendering to room drawing section
old_room_fill = 'ctx.fillStyle=r.color+"22";ctx.fill();'
new_room_fill = 'ctx.fillStyle=r.color+"22";ctx.fill();\n    // Apply hatch pattern\n    if(r.hatch&&window.hatchPatterns[r.hatch]){\n      var box=pts.reduce(function(a,p){return{x:Math.min(a.x,p.x),y:Math.min(a.y,p.y)}},{x:Infinity,y:Infinity});\n      var box2=pts.reduce(function(a,p){return{x:Math.max(a.x,p.x),y:Math.max(a.y,p.y)}},{x:-Infinity,y:-Infinity});\n      window.hatchPatterns[r.hatch](ctx,box.x,box.y,box2.x-box.x,box2.y-box.y,1);\n    }'
if old_room_fill in html:
    html = html.replace(old_room_fill, new_room_fill)
    c+=1; print("+ Hatch rendering in rooms")

# ==================== PROFESSIONAL DIMENSIONS ====================
dim_code = """
// ===================== 专业标注 =====================
window.addDimPro=function(x1,y1,x2,y2){
  var off=40/cam.zoom;
  dims.push({id:nextId++,x1,y1,x2,y2,offset:off});
  saveState();render2D();
};

// Override dimension rendering
var origDimRender = null;
"""
# Find and enhance dimension rendering
old_dim = 'ctx.strokeStyle="#ff6b6b";ctx.lineWidth=1;\n  ctx.beginPath();ctx.moveTo(p1.x+nx,p1.y+ny);ctx.lineTo(p2.x+nx,p2.y+ny);ctx.stroke();\n  // ticks\n  ctx.beginPath();ctx.moveTo(p1.x,p1.y);ctx.lineTo(p1.x+nx*0.65,p1.y+ny*0.65);ctx.stroke();\n  ctx.beginPath();ctx.moveTo(p2.x,p2.y);ctx.lineTo(p2.x+nx*0.65,p2.y+ny*0.65);ctx.stroke();\n  // text\n  const dist=Math.hypot(d.x2-d.x1,d.y2-d.y1);\n  ctx.fillStyle="#ff6b6b";ctx.font="10px sans-serif";ctx.textAlign="center";ctx.textBaseline="bottom";\n  ctx.fillText((dist/1000).toFixed(1)+"m",mid.x+nx,mid.y+ny-3);'

new_dim = 'ctx.strokeStyle="#ff6b6b";ctx.lineWidth=1.5;\n  // Main dimension line\n  ctx.beginPath();ctx.moveTo(p1.x+nx,p1.y+ny);ctx.lineTo(p2.x+nx,p2.y+ny);ctx.stroke();\n  // Arrow heads\n  var arrSize=8;\n  var ax=-Math.sin(ang)*arrSize,ay=Math.cos(ang)*arrSize;\n  ctx.beginPath();ctx.moveTo(p1.x+nx,p1.y+ny);ctx.lineTo(p1.x+nx+ax+ny*0.3,p1.y+ny+ay-nx*0.3);ctx.lineTo(p1.x+nx-ax+ny*0.3,p1.y+ny-ay-nx*0.3);ctx.closePath();ctx.fillStyle="#ff6b6b";ctx.fill();\n  ctx.beginPath();ctx.moveTo(p2.x+nx,p2.y+ny);ctx.lineTo(p2.x+nx+ax+ny*0.3,p2.y+ny+ay-nx*0.3);ctx.lineTo(p2.x+nx-ax+ny*0.3,p2.y+ny-ay-nx*0.3);ctx.closePath();ctx.fill();\n  // Extension lines with gap\n  var gap=6;\n  ctx.setLineDash([2,2]);ctx.lineWidth=0.5;ctx.strokeStyle="#ff6b6b66";\n  ctx.beginPath();ctx.moveTo(p1.x,p1.y+gap);ctx.lineTo(p1.x+nx*0.8,p1.y+ny*0.8);ctx.stroke();\n  ctx.beginPath();ctx.moveTo(p2.x,p2.y+gap);ctx.lineTo(p2.x+nx*0.8,p2.y+ny*0.8);ctx.stroke();\n  ctx.setLineDash([]);\n  // Text with background\n  var dist=Math.hypot(d.x2-d.x1,d.y2-d.y1);\n  ctx.fillStyle="rgba(22,22,40,0.7)";\n  ctx.font="bold 11px sans-serif";\n  var txt=(dist/1000).toFixed(1)+"m";\n  var tw=ctx.measureText(txt).width;\n  ctx.fillRect(mid.x+nx-tw/2-3,mid.y+ny-10,tw+6,14);\n  ctx.fillStyle="#ff6b6b";ctx.textAlign="center";ctx.textBaseline="middle";\n  ctx.fillText(txt,mid.x+nx,mid.y+ny-3);'

if old_dim in html:
    html = html.replace(old_dim, new_dim)
    c+=1; print("+ Professional dimensions")

# ==================== LAYER LINE TYPE ====================
linetype_code = """
// ===================== 图层线型 =====================
var layerConfig = {
  "外墙":{color:"rgba(200,200,220,0.8)",weight:3,dash:[]},
  "内墙":{color:"rgba(200,200,220,0.5)",weight:2,dash:[]},
  "门":{color:"rgba(67,233,123,0.8)",weight:1.5,dash:[]},
  "窗":{color:"rgba(79,172,254,0.8)",weight:1.5,dash:[]},
  "标注":{color:"rgba(255,107,107,0.8)",weight:1,dash:[]},
  "房间":{color:"rgba(255,255,255,0.3)",weight:1,dash:[4,4]},
  "家具":{color:"rgba(255,204,0,0.6)",weight:1,dash:[]},
};

window.setLayerLineType=function(layer,ltype){
  if(!layerConfig[layer])return;
  var dashes={solid:[],dashed:[6,3],dotted:[2,3],center:[12,4,2,4],dashdot:[6,3,1,3]};
  layerConfig[layer].dash=dashes[ltype]||[];
  render2D();
};
window.setLayerWeight=function(layer,w){
  if(!layerConfig[layer])return;
  layerConfig[layer].weight=Math.max(0.5,Math.min(5,w));
  render2D();
};
"""

if am in html:
    html = html.replace(am, linetype_code + am)
    c+=1; print("+ Layer line types")

with open("E:/CAD自动化制图/interior_cad.html","w",encoding="utf-8") as f:
    f.write(html)
print(f"Done! {c} changes, {len(html)} bytes")
