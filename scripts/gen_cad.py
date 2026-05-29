import os

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title> CAD 2D 交互编辑器</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Microsoft YaHei,sans-serif;overflow:hidden;background:#1a1a2e;color:#fff;height:100vh;display:flex;flex-direction:column}

#header{height:42px;background:rgba(26,26,46,0.97);border-bottom:1px solid rgba(255,255,255,0.08);display:flex;align-items:center;padding:0 12px;gap:8px;flex-shrink:0;z-index:300}
#header .logo{font-size:14px;font-weight:700;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
#header .spacer{flex:1}
.btn{padding:3px 10px;border:1px solid rgba(255,255,255,0.15);border-radius:4px;background:rgba(255,255,255,0.05);color:#fff;cursor:pointer;font-size:11px;font-family:inherit;transition:all .15s}
.btn:hover{background:rgba(255,255,255,0.12)}
.btn-p{background:linear-gradient(135deg,#667eea,#764ba2);border:none}
.btn-p:hover{opacity:.9}

#main{flex:1;display:flex;overflow:hidden}
#left-panel{width:340px;min-width:280px;border-right:1px solid rgba(255,255,255,0.08);display:flex;flex-direction:column;background:rgba(22,22,40,0.95)}
#canvas-wrap{flex:1;position:relative;overflow:hidden;background:#161628}
#canvas-2d{width:100%;height:100%;display:block}
#status-bar{height:26px;display:flex;align-items:center;padding:0 10px;border-top:1px solid rgba(255,255,255,0.05);font-size:10px;color:rgba(255,255,255,0.35);gap:12px;flex-shrink:0}
#status-bar .coord{color:rgba(255,255,255,0.5)}
#right-panel{flex:1;display:flex;flex-direction:column;position:relative}
#canvas-3d{width:100%;height:100%;display:block}

/* 左侧工具列 */
#tools{display:flex;gap:2px;padding:5px 6px;border-bottom:1px solid rgba(255,255,255,0.08);flex-wrap:wrap;flex-shrink:0}
.tool-btn{padding:3px 8px;border:1px solid transparent;border-radius:3px;background:transparent;color:rgba(255,255,255,0.6);cursor:pointer;font-size:11px;font-family:inherit;transition:all .12s}
.tool-btn:hover{background:rgba(255,255,255,0.08);color:#fff}
.tool-btn.active{border-color:#667eea;color:#fff;background:rgba(102,126,234,0.15)}
.tool-sep{width:1px;height:16px;background:rgba(255,255,255,0.1);margin:auto 4px}

/* 右侧 3D 工具栏（覆盖） */
#toolbar-3d{position:absolute;top:6px;left:50%;transform:translateX(-50%);z-index:100;display:flex;gap:3px;background:rgba(0,0,0,0.5);padding:3px 6px;border-radius:6px}
#toolbar-3d .btn3d{padding:2px 7px;border:1px solid transparent;border-radius:3px;background:transparent;color:rgba(255,255,255,0.6);cursor:pointer;font-size:10px;font-family:inherit}
#toolbar-3d .btn3d:hover{background:rgba(255,255,255,0.1);color:#fff}
#toolbar-3d .btn3d.active{border-color:#667eea;color:#fff}

/* 右侧属性面板 */
#props{position:absolute;top:42px;right:6px;z-index:100;width:200px;background:rgba(0,0,0,0.75);backdrop-filter:blur(6px);border-radius:6px;border:1px solid rgba(255,255,255,0.08);padding:8px;font-size:11px;display:none}
#props .row{display:flex;justify-content:space-between;padding:2px 0;color:rgba(255,255,255,0.6)}
#props .title{font-weight:600;color:#fff;margin-bottom:4px}

/* 右下面具栏 */
#furn-bar{height:32px;display:flex;align-items:center;gap:4px;padding:0 8px;border-top:1px solid rgba(255,255,255,0.08);background:rgba(22,22,40,0.8);flex-shrink:0;overflow-x:auto}
.furn-chip{padding:2px 8px;border:1px solid rgba(255,255,255,0.1);border-radius:10px;font-size:10px;cursor:pointer;white-space:nowrap;background:rgba(255,255,255,0.03);color:rgba(255,255,255,0.6);transition:all .12s}
.furn-chip:hover{background:rgba(102,126,234,0.15);color:#fff;border-color:#667eea}

::-webkit-scrollbar{width:2px;height:2px}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:2px}
</style>
</head>
<body>

<div id="header">
  <span class="logo"> CAD 交互编辑器</span>
  <span style="font-size:10px;color:rgba(255,255,255,0.3)">左侧画图 · 右侧3D预览</span>
  <span class="spacer"></span>
  <button class="btn" onclick="saveDoc()"> 保存</button>
  <button class="btn" onclick="loadDoc()"> 打开</button>
  <button class="btn btn-p" onclick="exportDXF()"> DXF</button>
  <button class="btn" onclick="clearAll()" style="color:#e74c3c"> 清空</button>
</div>

<div id="main">
  <!-- 左侧 2D -->
  <div id="left-panel">
    <div id="tools">
      <button class="tool-btn active" data-t="select" onclick="setTool('select')"> 选择</button>
      <button class="tool-btn" data-t="wall" onclick="setTool('wall')"> 画墙</button>
      <button class="tool-btn" data-t="door" onclick="setTool('door')"> 门</button>
      <button class="tool-btn" data-t="window" onclick="setTool('window')"> 窗</button>
      <button class="tool-btn" data-t="dim" onclick="setTool('dim')"> 标注</button>
      <button class="tool-btn" data-t="room" onclick="setTool('room')"> 房间</button>
      <div class="tool-sep"></div>
      <button class="tool-btn" onclick="undo()">↩</button>
      <button class="tool-btn" onclick="redo()">↪</button>
      <button class="tool-btn" onclick="zoomFit()"> 适配</button>
    </div>
    <div id="canvas-wrap">
      <canvas id="canvas-2d"></canvas>
    </div>
    <div id="status-bar">
      <span id="tool-status">就绪</span>
      <span class="coord" id="coord-status">0, 0</span>
    </div>
  </div>

  <!-- 右侧 3D -->
  <div id="right-panel">
    <div id="toolbar-3d">
      <button class="btn3d active" onclick="set3DView('3d')"> 3D</button>
      <button class="btn3d" onclick="set3DView('top')"> 俯视</button>
      <button class="btn3d" onclick="toggleAutoRotate()"> 漫游</button>
      <button class="btn3d" onclick="snapshot()"> 截图</button>
    </div>
    <canvas id="canvas-3d"></canvas>
    <div id="props"></div>
    <div id="furn-bar"></div>
  </div>
</div>

<script type="importmap">{"imports":{"three":"./lib/three.module.js","three/addons/":"./lib/"}}</script>
<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/OrbitControls.js";

// ===================== CAD DATA MODEL =====================
let walls = [];        // {id,x1,y1,x2,y2,thick,type}
let doors = [];        // {id,wallId,pos,width}
let windows = [];      // {id,wallId,pos,width}
let rooms = [];        // {id,name,corners,color,area}
let dims = [];         // {id,x1,y1,x2,y2,offset}
let furniture = [];    // {id,name,cat,x,y,w,d,color}
let nextId = 1;

// Undo
let history = [];
let histIdx = -1;
const MAX_HIST = 50;

function saveState(){const s=JSON.stringify({walls,doors,windows,rooms,dims,furniture});history=history.slice(0,histIdx+1);history.push(s);if(history.length>MAX_HIST)history.shift();histIdx=history.length-1;}

function restoreState(i){if(i<0||i>=history.length)return;const s=JSON.parse(history[i]);walls=s.walls;doors=s.doors;windows=s.windows;rooms=s.rooms;dims=s.dims;furniture=s.furniture;histIdx=i;render2D();rebuild3D();updateStatus();}

// ===================== 2D CANVAS ENGINE =====================
const c2 = document.getElementById("canvas-2d"), ctx = c2.getContext("2d");
let cam = {x:0,y:0,zoom:0.8};
let tool = "select";
let drag = null, sel = null, hover = null;
let mDown = null, mPos = null;
let wallDraw = null; // {x,y} for wall drawing start

function resize2D(){const w=document.getElementById("canvas-wrap");c2.width=w.clientWidth;c2.height=w.clientHeight;render2D()}
window.addEventListener("resize",resize2D);

function w2s(wx,wy){return {x:c2.width/2+(wx-cam.x)*cam.zoom,y:c2.height/2-(wy-cam.y)*cam.zoom}}
function s2w(sx,sy){return {x:(sx-c2.width/2)/cam.zoom+cam.x,y:-(sy-c2.height/2)/cam.zoom+cam.y}}

function snapToGrid(p){const g=50;return{x:Math.round(p.x/g)*g,y:Math.round(p.y/g)*g}}
function snapToEndpoint(p,dist=20){
  for(const w of walls){
    for(const ep of [{x:w.x1,y:w.y1},{x:w.x2,y:w.y2}]){
      if(Math.hypot(p.x-ep.x,p.y-ep.y)*cam.zoom<dist)return ep;
    }
  }
  return null;
}

// ===================== 2D RENDER =====================
function render2D(){
  const W=c2.width,H=c2.height;
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle="#161628";ctx.fillRect(0,0,W,H);

  // Grid
  const gs=50;const gsPx=gs*cam.zoom;
  if(gsPx>4){
    const origin=w2s(0,0);ctx.strokeStyle="rgba(255,255,255,0.04)";ctx.lineWidth=1;
    for(let x=origin.x%gsPx;x<W;x+=gsPx){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke()}
    for(let y=origin.y%gsPx;y<H;y+=gsPx){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke()}
  }

  // Rooms
  for(const r of rooms){
    const pts=r.corners.map(p=>w2s(p.x,p.y));
    ctx.beginPath();ctx.moveTo(pts[0].x,pts[0].y);
    for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i].x,pts[i].y);
    ctx.closePath();
    ctx.fillStyle=r.color+"22";ctx.fill();
    ctx.strokeStyle=r.color+"44";ctx.lineWidth=1;ctx.setLineDash([4,4]);ctx.stroke();ctx.setLineDash([]);
    const cx=pts.reduce((a,p)=>({x:a.x+p.x/pts.length,y:a.y+p.y/pts.length}),{x:0,y:0});
    ctx.fillStyle="rgba(255,255,255,0.3)";ctx.font="11px Microsoft YaHei";ctx.textAlign="center";
    ctx.fillText(r.name+" "+r.area+"m2",cx.x,cx.y);
  }

  // Walls
  for(const w of walls){
    const p1=w2s(w.x1,w.y1),p2=w2s(w.x2,w.y2);
    const dx=p2.x-p1.x,dy=p2.y-p1.y;
    const len=Math.hypot(dx,dy);
    if(len<1)continue;
    const nx=-dy/len*w.thick*cam.zoom/2,ny=dx/len*w.thick*cam.zoom/2;
    ctx.beginPath();
    ctx.moveTo(p1.x+nx,p1.y+ny);ctx.lineTo(p2.x+nx,p2.y+ny);
    ctx.lineTo(p2.x-nx,p2.y-ny);ctx.lineTo(p1.x-nx,p1.y-ny);
    ctx.closePath();
    ctx.fillStyle=w.type==="外墙"?"rgba(200,200,210,0.25)":"rgba(200,200,210,0.12)";
    ctx.fill();
    ctx.strokeStyle=w.type==="外墙"?"rgba(200,200,220,0.6)":"rgba(200,200,220,0.35)";
    ctx.lineWidth=w===sel?2:1;
    if(w===hover&&tool==="select"){ctx.strokeStyle="#667eea";ctx.lineWidth=2}
    ctx.stroke();

    // endpoints
    if(w===sel||w===hover){
      for(const p of[p1,p2]){
        ctx.fillStyle="#667eea";ctx.beginPath();ctx.arc(p.x,p.y,5,0,Math.PI*2);ctx.fill();
        ctx.fillStyle="#fff";ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fill();
      }
    }
  }

  // Doors
  for(const d of doors){
    const w=walls.find(x=>x.id===d.wallId);if(!w)continue;
    const p=pointOnWall(w,d.pos);
    if(!p)continue;
    const ps=w2s(p.x,p.y);
    const ang=Math.atan2(w.y2-w.y1,w.x2-w.x1);
    const sw=d.width*cam.zoom;
    ctx.save();ctx.translate(ps.x,ps.y);ctx.rotate(ang);
    // door leaf arc
    ctx.strokeStyle="#43e97b";ctx.lineWidth=2;
    ctx.beginPath();ctx.moveTo(0,0);ctx.arc(0,0,sw,0,Math.PI/2);ctx.stroke();
    ctx.beginPath();ctx.moveTo(sw,0);ctx.lineTo(sw,-sw*0.1);ctx.stroke();
    ctx.fillStyle="rgba(67,233,123,0.15)";ctx.beginPath();ctx.moveTo(0,0);ctx.arc(0,0,sw,0,Math.PI/2);ctx.closePath();ctx.fill();
    ctx.restore();
  }

  // Windows
  for(const wd of windows){
    const w=walls.find(x=>x.id===wd.wallId);if(!w)continue;
    const p=pointOnWall(w,wd.pos);
    if(!p)continue;
    const ps=w2s(p.x,p.y);
    const ang=Math.atan2(w.y2-w.y1,w.x2-w.x1);
    const sw=wd.width*cam.zoom;
    ctx.save();ctx.translate(ps.x,ps.y);ctx.rotate(ang);
    ctx.fillStyle="rgba(135,206,235,0.2)";ctx.fillRect(0,-3,sw,6);
    ctx.strokeStyle="#4facfe";ctx.lineWidth=1.5;
    ctx.strokeRect(0,-3,sw,6);
    ctx.beginPath();ctx.moveTo(sw/3,-3);ctx.lineTo(sw/3,3);ctx.stroke();
    ctx.beginPath();ctx.moveTo(sw*2/3,-3);ctx.lineTo(sw*2/3,3);ctx.stroke();
    ctx.restore();
  }

  // Dimensions
  for(const d of dims){
    const p1=w2s(d.x1,d.y1),p2=w2s(d.x2,d.y2);
    const mid={x:(p1.x+p2.x)/2,y:(p1.y+p2.y)/2};
    const ang=Math.atan2(p2.y-p1.y,p2.x-p1.x);
    const off=d.offset||40;
    const nx=-Math.sin(ang)*off,ny=Math.cos(ang)*off;
    ctx.strokeStyle="#ff6b6b";ctx.lineWidth=1;
    ctx.beginPath();ctx.moveTo(p1.x+nx,p1.y+ny);ctx.lineTo(p2.x+nx,p2.y+ny);ctx.stroke();
    // ticks
    ctx.beginPath();ctx.moveTo(p1.x,p1.y);ctx.lineTo(p1.x+nx*0.65,p1.y+ny*0.65);ctx.stroke();
    ctx.beginPath();ctx.moveTo(p2.x,p2.y);ctx.lineTo(p2.x+nx*0.65,p2.y+ny*0.65);ctx.stroke();
    // text
    const dist=Math.hypot(d.x2-d.x1,d.y2-d.y1);
    ctx.fillStyle="#ff6b6b";ctx.font="10px sans-serif";ctx.textAlign="center";ctx.textBaseline="bottom";
    ctx.fillText((dist/1000).toFixed(1)+"m",mid.x+nx,mid.y+ny-3);
  }

  // Furniture (from 3D sync)
  for(const f of furniture){
    const p=w2s(f.x,f.y);
    const w=f.w*cam.zoom,d=f.d*cam.zoom;
    ctx.save();ctx.translate(p.x,p.y);
    ctx.fillStyle=f.color+"66";ctx.strokeStyle=f.color;ctx.lineWidth=1.5;
    ctx.fillRect(-w/2,-d/2,w,d);ctx.strokeRect(-w/2,-d/2,w,d);
    ctx.fillStyle="rgba(255,255,255,0.5)";ctx.font="8px sans-serif";ctx.textAlign="center";
    ctx.fillText(f.name,0,3);
    ctx.restore();
  }

  // Wall drawing preview
  if(tool==="wall"&&wallDraw&&mPos){
    const p1=w2s(wallDraw.x,wallDraw.y),p2=w2s(mPos.x,mPos.y);
    ctx.strokeStyle="#667eea";ctx.lineWidth=2;ctx.setLineDash([6,4]);
    ctx.beginPath();ctx.moveTo(p1.x,p1.y);ctx.lineTo(p2.x,p2.y);ctx.stroke();ctx.setLineDash([]);
  }
}

function pointOnWall(w,pos){
  const dx=w.x2-w.x1,dy=w.y2-w.y1;
  const len=Math.hypot(dx,dy);if(len<1)return null;
  const r=pos/len;
  return {x:w.x1+dx*r,y:w.y1+dy*r};
}

function distToSegment(px,py,x1,y1,x2,y2){
  const dx=x2-x1,dy=y2-y1;
  const len2=dx*dx+dy*dy;if(len2<1)return Math.hypot(px-x1,py-y1);
  let t=((px-x1)*dx+(py-y1)*dy)/len2;t=Math.max(0,Math.min(1,t));
  return Math.hypot(px-(x1+t*dx),py-(y1+t*dy));
}

function hitTest(px,py){
  // walls
  for(const w of walls){
    if(distToSegment(px,py,w.x1,w.y1,w.x2,w.y2)<Math.max(w.thick/2,50))return{type:"wall",obj:w};
  }
  return null;
}

// ===================== 2D TOOLS =====================
window.setTool=function(t){
  tool=t;wallDraw=null;sel=null;
  document.querySelectorAll("[data-t]").forEach(b=>b.classList.toggle("active",b.dataset.t===t));
  document.getElementById("tool-status").textContent={select:"选择 - 点击墙选中，拖端点改尺寸",wall:"画墙 - 点击起点，移动后点击终点",door:"门 - 点击墙放置门",window:"窗 - 点击墙放置窗",dim:"标注 - 点击两点标注尺寸",room:"房间 - 自动识别房间"}[t]||t;
};

window.undo=function(){if(histIdx>0){restoreState(histIdx-1);render2D();rebuild3D()}};
window.redo=function(){if(histIdx<history.length-1){restoreState(histIdx+1);render2D();rebuild3D()}};

function addWall(x1,y1,x2,y2,thick,type){
  walls.push({id:nextId++,x1,y1,x2,y2,thick:thick||200,type:type||"内墙"});
  saveState();render2D();rebuild3D();updateStatus();
}

function addDoor(wallId,pos,width){
  doors.push({id:nextId++,wallId,pos,width:width||900});
  saveState();render2D();rebuild3D();updateStatus();
}

function addWindow(wallId,pos,width){
  windows.push({id:nextId++,wallId,pos,width:width||1200});
  saveState();render2D();rebuild3D();updateStatus();
}

function addDim(x1,y1,x2,y2,offset){
  dims.push({id:nextId++,x1,y1,x2,y2,offset:offset||40});
  saveState();render2D();
}

function detectRoom(){
  // Simple room detection from wall loops
  if(walls.length<3)return;
  saveState();
  rooms=[];
  const pts=[];
  // Build connected wall segments
  const used=new Set();
  let cur=walls[0];let path=[{x:cur.x1,y:cur.y1},{x:cur.x2,y:cur.y2}];used.add(cur.id);
  let found=true;
  while(found){
    found=false;
    for(const w of walls){
      if(used.has(w.id))continue;
      const last=path[path.length-1];
      const d1=Math.hypot(w.x1-last.x,w.y1-last.y);
      const d2=Math.hypot(w.x2-last.x,w.y2-last.y);
      if(d1<10){path.push({x:w.x2,y:w.y2});used.add(w.id);found=true;break}
      if(d2<10){path.push({x:w.x1,y:w.y1});used.add(w.id);found=true;break}
    }
  }
  // Close path
  path.push({...path[0]});
  // Calculate area
  let area=0;for(let i=0;i<path.length-1;i++)area+=path[i].x*path[i+1].y-path[i+1].x*path[i].y;
  area=Math.abs(area)/2;
  if(area>1){
    const colors={"#667eea","#f093fb","#4facfe","#43e97b","#fa709a","#764ba2","#a8a8a8"};
    rooms.push({id:nextId++,name:"房间"+(rooms.length+1),corners:path.slice(0,-1),color:colors[rooms.length%colors.length],area:Math.round(area/1e6*10)/10});
  }
  // Add remaining unconnected walls as separate rooms
  for(const w of walls){
    if(!used.has(w.id)){
      rooms.push({id:nextId++,name:"房间"+(rooms.length+1),corners:[{x:w.x1,y:w.y1},{x:w.x2,y:w.y2},{x:(w.x1+w.x2)/2+2000,y:(w.y1+w.y2)/2+2000}],color:colors[rooms.length%colors.length],area:0});
    }
  }
  render2D();rebuild3D();updateStatus();
}

// ===================== 2D MOUSE EVENTS =====================
c2.addEventListener("pointerdown",e=>{
  const r=c2.getBoundingClientRect();
  const wp=s2w(e.clientX-r.left,e.clientY-r.top);
  mDown=wp;mPos=wp;
  if(tool==="wall"){
    const snap=snapToEndpoint(wp,15/cam.zoom);
    const p=snap||snapToGrid(wp);
    if(!wallDraw){wallDraw=p}
    else{
      if(Math.hypot(p.x-wallDraw.x,p.y-wallDraw.y)>100){
        addWall(wallDraw.x,wallDraw.y,p.x,p.y);wallDraw=p;
      }else{wallDraw=null}
    }
    return;
  }
  if(tool==="door"||tool==="window"){
    for(const w of walls){
      if(distToSegment(wp.x,wp.y,w.x1,w.y1,w.x2,w.y2)<w.thick/2+100){
        const dx=w.x2-w.x1,dy=w.y2-w.y1;
        const len=Math.hypot(dx,dy);
        const pos=((wp.x-w.x1)*dx+(wp.y-w.y1)*dy)/len;
        if(pos>200&&pos<len-200){
          if(tool==="door")addDoor(w.id,pos,900);
          else addWindow(w.id,pos,1200);
        }
        return;
      }
    }
    return;
  }
  if(tool==="dim"){
    if(!mDown){mDown=wp;return}
    addDim(mDown.x,mDown.y,wp.x,wp.y);mDown=null;return;
  }
  if(tool==="room"){detectRoom();return}
  // select
  const hit=hitTest(wp.x,wp.y);
  if(hit&&hit.type==="wall"){
    sel=hit.obj;render2D();showProps(sel);
  }else{
    sel=null;document.getElementById("props").style.display="none";render2D();
  }
});

c2.addEventListener("pointermove",e=>{
  const r=c2.getBoundingClientRect();
  const wp=s2w(e.clientX-r.left,e.clientY-r.top);
  mPos=wp;
  document.getElementById("coord-status").textContent=(wp.x/1000).toFixed(1)+"m, "+(wp.y/1000).toFixed(1)+"m";
  if(tool==="wall"){render2D();return}
  if(tool==="select"){
    const hit=hitTest(wp.x,wp.y);
    hover=hit?hit.obj:null;
    c2.style.cursor=hover?"pointer":"";
    render2D();
  }
});

c2.addEventListener("wheel",e=>{
  e.preventDefault();
  const r=c2.getBoundingClientRect();
  const wp=s2w(e.clientX-r.left,e.clientY-r.top);
  cam.zoom*=e.deltaY>0?0.9:1.1;
  cam.zoom=Math.max(0.05,Math.min(10,cam.zoom));
  // Zoom toward cursor
  const np=s2w(e.clientX-r.left,e.clientY-r.top);
  cam.x+=wp.x-np.x;cam.y+=wp.y-np.y;
  render2D();
},{passive:false});

c2.addEventListener("contextmenu",e=>e.preventDefault());

// ===================== 3D SCENE =====================
const c3d=document.getElementById("canvas-3d");
const scene=new THREE.Scene();scene.background=new THREE.Color("#F0EBE5");
const camera3=new THREE.PerspectiveCamera(50,c3d.clientWidth/c3d.clientHeight,0.1,100);
camera3.position.set(8,6,10);
const renderer3=new THREE.WebGLRenderer({antialias:true});
renderer3.setSize(c3d.clientWidth,c3d.clientHeight);
renderer3.setPixelRatio(Math.min(devicePixelRatio,2));
renderer3.shadowMap.enabled=true;renderer3.shadowMap.type=THREE.PCFSoftShadowMap;
renderer3.toneMapping=THREE.ACESFilmicToneMapping;renderer3.toneMappingExposure=1.0;
c3d.appendChild(renderer3.domElement);
const controls3=new OrbitControls(camera3,renderer3.domElement);
controls3.target.set(0,1.2,0);controls3.enableDamping=true;controls3.dampingFactor=0.08;
controls3.maxPolarAngle=Math.PI/2.05;controls3.minDistance=1;controls3.maxDistance=30;
controls3.update();
scene.add(new THREE.AmbientLight(0x404060,0.5));
scene.add(new THREE.HemisphereLight(0x8888ff,0x444422,0.6));
const sun3=new THREE.DirectionalLight(0xffeedd,1.2);
sun3.position.set(5,12,8);sun3.castShadow=true;
sun3.shadow.mapSize.set(1024,1024);sun3.shadow.camera.near=0.1;sun3.shadow.camera.far=30;
sun3.shadow.camera.left=-12;sun3.shadow.camera.right=12;
sun3.shadow.camera.top=12;sun3.shadow.camera.bottom=-12;
scene.add(sun3);
scene.add(new THREE.DirectionalLight(0x4488ff,0.3).position.set(-3,4,-5));

const roomG=new THREE.Group();scene.add(roomG);
const floorMat3=new THREE.MeshStandardMaterial({color:"#E8E0D6",roughness:0.8});
const floor3=new THREE.Mesh(new THREE.PlaneGeometry(20,20),floorMat3);
floor3.rotation.x=-Math.PI/2;floor3.position.y=-2;floor3.receiveShadow=true;
roomG.add(floor3);

function rebuild3D(){
  // Clear old
  while(roomG.children.length)roomG.remove(roomG.children[0]);
  const fl=new THREE.Mesh(new THREE.PlaneGeometry(30,30),floorMat3);
  fl.rotation.x=-Math.PI/2;fl.position.y=-2;fl.receiveShadow=true;roomG.add(fl);

  const wMat=new THREE.MeshStandardMaterial({color:"#F0EBE5",roughness:0.9});
  const h=2800;
  for(const w of walls){
    const dx=w.x2-w.x1,dy=w.y2-w.y1;
    const len=Math.hypot(dx,dy);if(len<1)continue;
    const m=new THREE.Mesh(new THREE.BoxGeometry(len/1000,h/1000,w.thick/1000),wMat);
    m.position.set((w.x1+w.x2)/2000,h/2000,(w.y1+w.y2)/2000);
    m.rotation.y=-Math.atan2(dy,dx);
    m.castShadow=true;m.receiveShadow=true;roomG.add(m);
  }
  for(const f of furniture){
    const mat=new THREE.MeshStandardMaterial({color:f.color||"#cccccc",roughness:0.6});
    const m=new THREE.Mesh(new THREE.BoxGeometry(f.w/1000,300/1000,f.d/1000),mat);
    m.position.set(f.x/1000,0.15,f.y/1000);
    m.castShadow=true;roomG.add(m);
  }
}

// ===================== 3D VIEW CONTROL =====================
window.set3DView=function(m){
  document.querySelectorAll("#toolbar-3d .btn3d").forEach(b=>b.classList.remove("active"));
  if(m==="top"){camera3.position.set(0,15,0.01);controls3.target.set(0,0,0)}
  else{camera3.position.set(8,6,10);controls3.target.set(0,1.2,0)}
  controls3.update();
};
window.toggleAutoRotate=function(){controls3.autoRotate=!controls3.autoRotate;controls3.autoRotateSpeed=0.6};
window.snapshot=function(){renderer3.render(scene,camera3);const a=document.createElement("a");a.download="cad_snapshot.png";a.href=renderer3.domElement.toDataURL("image/png");a.click()};

// ===================== PROPS PANEL =====================
function showProps(w){
  const p=document.getElementById("props");p.style.display="block";
  p.innerHTML=`<div class="title">  墙属性</div>
    <div class="row"><span>长度</span><span>${Math.hypot(w.x2-w.x1,w.y2-w.y1)/1000|0}m</span></div>
    <div class="row"><span>厚度</span><span>${w.thick}mm</span></div>
    <div class="row"><span>类型</span><span>${w.type}</span></div>
    <div style="margin-top:4px;display:flex;gap:4px">
      <button class="btn" style="padding:2px 6px;font-size:10px" onclick="delWall()"> 删除</button>
      <button class="btn" style="padding:2px 6px;font-size:10px" onclick="toggleWallType()">切换内外</button>
    </div>`;
}
window.delWall=function(){if(!sel)return;walls=walls.filter(w=>w!==sel);sel=null;saveState();render2D();rebuild3D();updateStatus();document.getElementById("props").style.display="none"};
window.toggleWallType=function(){if(!sel)return;sel.type=sel.type==="外墙"?"内墙":"外墙";saveState();render2D();showProps(sel)};

// ===================== FURNITURE BAR =====================
const FURN_CATALOG=[
  {id:"bed1",name:"双人床",icon:" ",w:2000,d:1800,color:"#D2B48C"},
  {id:"sofa1",name:"沙发",icon:" ",w:2200,d:850,color:"#8B4513"},
  {id:"table1",name:"餐桌",icon:" ",w:1400,d:800,color:"#DEB887"},
  {id:"chair1",name:"餐椅",icon:" ",w:480,d:520,color:"#C4A882"},
  {id:"cabinet1",name:"衣柜",icon:" ",w:1800,d:600,color:"#C4A882"},
  {id:"toilet1",name:"马桶",icon:" ",w:400,d:700,color:"#F5F5F5"},
  {id:"sink1",name:"洗手盆",icon:" ",w:600,d:500,color:"#FFFFFF"},
  {id:"fridge1",name:"冰箱",icon:" ",w:900,d:800,color:"#C0C0C0"},
];

function buildFurnBar(){
  const bar=document.getElementById("furn-bar");
  FURN_CATALOG.forEach(f=>{
    const chip=document.createElement("span");chip.className="furn-chip";
    chip.innerHTML=`${f.icon} ${f.name}`;
    chip.onclick=()=>{
      saveState();
      furniture.push({id:nextId++,name:f.name,cat:"",x:0,y:0,w:f.w,d:f.d,color:f.color});
      render2D();rebuild3D();updateStatus();
    };
    bar.appendChild(chip);
  });
}

// ===================== STATUS =====================
function updateStatus(){
  document.getElementById("tool-status").textContent=
    `墙:${walls.length} 门:${doors.length} 窗:${windows.length} 房间:${rooms.length} 家具:${furniture.length}`;
}

// ===================== SAVE/LOAD =====================
window.saveDoc=function(){
  const d={walls,doors,windows,rooms,dims,furniture};
  const a=document.createElement("a");a.download="cad_plan.json";
  a.href=URL.createObjectURL(new Blob([JSON.stringify(d,null,2)],{type:"application/json"}));a.click();
};
window.loadDoc=function(){
  const i=document.createElement("input");i.type="file";i.accept=".json";
  i.onchange=async e=>{
    const d=JSON.parse(await e.target.files[0].text());
    walls=d.walls||[];doors=d.doors||[];windows=d.windows||[];
    rooms=d.rooms||[];dims=d.dims||[];furniture=d.furniture||[];
    saveState();render2D();rebuild3D();updateStatus();
  };i.click();
};
window.exportDXF=function(){
  const d={walls,doors,windows,furniture};
  const a=document.createElement("a");a.download="cad_export.json";
  a.href=URL.createObjectURL(new Blob([JSON.stringify(d,null,2)],{type:"application/json"}));a.click();
  alert("JSON 数据已下载，运行:\\npython interior_run.py --input cad_export.json");
};
window.clearAll=function(){if(!confirm("确定清空所有？"))return;walls=[];doors=[];windows=[];rooms=[];dims=[];furniture=[];saveState();render2D();rebuild3D();updateStatus()};
window.zoomFit=function(){cam.x=0;cam.y=0;cam.zoom=0.8;render2D()};

// ===================== INIT =====================
buildFurnBar();
resize2D();
saveState();

// Demo: 画一个默认户型
addWall(-5000,-5000,5000,-5000,240,"外墙");
addWall(5000,-5000,5000,5000,240,"外墙");
addWall(5000,5000,-5000,5000,240,"外墙");
addWall(-5000,5000,-5000,-5000,240,"外墙");
addWall(-5000,0,5000,0,150,"内墙");
addWall(0,-5000,0,0,150,"内墙");
detectRoom();
// Doors
addDoor(walls[0].id,3000,900);
addDoor(walls[4].id,2000,900);
addDoor(walls[1].id,3000,900);
// Windows
addWindow(walls[2].id,2500,1500);
addWindow(walls[3].id,2000,1500);
// Furniture
furniture.push({id:nextId++,name:"双人床",cat:"",x:-2000,y:-2500,w:2000,d:1800,color:"#D2B48C"});
furniture.push({id:nextId++,name:"沙发",cat:"",x:-1500,y:2500,w:2200,d:850,color:"#8B4513"});
furniture.push({id:nextId++,name:"餐桌",cat:"",x:2000,y:2500,w:1400,d:800,color:"#DEB887"});
saveState();
render2D();rebuild3D();updateStatus();
document.getElementById("tool-status").textContent="  默认户型已加载！试试左侧工具：画墙/放门/放窗/标注";

// ===================== ANIMATION LOOP =====================
function animate(){requestAnimationFrame(animate);controls3.update();renderer3.render(scene,camera3)}
animate();
console.log(" CAD 2D 编辑器启动完成");
</script>
</body>
</html>"""

out = r"E:\CAD自动化制图\interior_cad.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)
print(f"Written: {len(HTML)} bytes to {out}")
