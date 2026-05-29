import json, os

def gen_html():
    materials_js = json.dumps({
        "墙面":"#F0EBE5","橡木":"#C4A882","大理石":"#E0D8D0",
        "混凝土":"#A0A0A0","瓷砖":"#E8E0D0","金属":"#A0A0A0",
        "皮革":"#8B5E3C","天鹅绒":"#7B6B8A","纯棉":"#F0EDE8",
        "地板深色":"#6B4226","地板浅色":"#DEB887","地毯":"#8B7D6B",
        "玻璃":"#ADD8E6","白色":"#F5F5F5","黑色":"#2C2C2C",
        "红色":"#8B0000","蓝色":"#00008B","绿色":"#006400"
    }, ensure_ascii=False)

    html = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,user-scalable=no">
<title>CAD 交互式室内设计</title>
<style>
:root{--bg:#161628;--bg2:#1a1a2e;--border:rgba(255,255,255,0.08);--text:#fff;--text2:rgba(255,255,255,0.6);
--accent:#667eea;--accent2:#764ba2;--danger:#e74c3c;--font:system-ui,-apple-system,Microsoft YaHei,sans-serif}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:var(--font);overflow:hidden;background:var(--bg);color:var(--text);height:100vh;display:flex;flex-direction:column}
#header{height:36px;background:rgba(26,26,46,0.98);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 6px;gap:2px;flex-shrink:0;z-index:300;overflow-x:auto}
.btn{padding:2px 6px;border:1px solid rgba(255,255,255,0.12);border-radius:3px;background:rgba(255,255,255,0.04);color:var(--text);cursor:pointer;font-size:9px;font-family:var(--font);white-space:nowrap;transition:all .12s;height:20px;display:inline-flex;align-items:center;gap:2px;flex-shrink:0}
.btn:hover{background:rgba(255,255,255,0.1)}
.btn-p{background:linear-gradient(135deg,var(--accent),var(--accent2));border:none}
.btn-p:hover{opacity:.85}
.btn-d{border-color:rgba(231,76,60,0.4);color:var(--danger)}
#main{flex:1;display:flex;overflow:hidden;min-height:0}
#left-panel{width:280px;min-width:220px;border-right:1px solid var(--border);display:flex;flex-direction:column;background:rgba(22,22,40,0.96)}
#canvas-wrap{flex:1;position:relative;overflow:hidden;background:var(--bg)}
#canvas-2d{width:100%;height:100%;display:block}
#status-bar{height:20px;display:flex;align-items:center;padding:0 4px;border-top:1px solid var(--border);font-size:8px;color:var(--text2);gap:4px;flex-shrink:0}
#right-panel{flex:1;display:flex;flex-direction:column;position:relative;min-width:0}
#canvas-3d{width:100%;height:100%;display:block;background:var(--bg)}
#tools{display:flex;gap:1px;padding:2px 3px;border-bottom:1px solid var(--border);flex-wrap:wrap;flex-shrink:0}
.tool-btn{padding:1px 5px;border:1px solid transparent;border-radius:2px;background:transparent;color:var(--text2);cursor:pointer;font-size:9px;font-family:var(--font)}
.tool-btn:hover{background:rgba(255,255,255,0.06);color:var(--text)}
.tool-btn.active{border-color:var(--accent);color:var(--text);background:rgba(102,126,234,0.12)}
.tool-sep{width:1px;height:10px;background:var(--border);margin:auto 2px}
#toolbar-3d{position:absolute;top:3px;left:50%;transform:translateX(-50%);z-index:100;display:flex;gap:2px;background:rgba(0,0,0,0.5);padding:2px 4px;border-radius:4px}
.btn3d{padding:1px 5px;border:none;border-radius:2px;background:transparent;color:var(--text2);cursor:pointer;font-size:8px;font-family:var(--font)}
.btn3d:hover{background:rgba(255,255,255,0.08);color:var(--text)}
#furn-bar{height:24px;display:flex;align-items:center;gap:2px;padding:0 4px;border-top:1px solid var(--border);background:rgba(22,22,40,0.85);flex-shrink:0;overflow-x:auto}
.furn-chip{padding:0 5px;border:1px solid rgba(255,255,255,0.06);border-radius:6px;font-size:8px;cursor:pointer;white-space:nowrap;background:rgba(255,255,255,0.02);color:var(--text2)}
.furn-chip:hover{background:rgba(102,126,234,0.12);border-color:var(--accent)}
#loading-3d{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:var(--bg);z-index:50;flex-direction:column;gap:6px;transition:opacity .4s}
#loading-3d.hidden{opacity:0;pointer-events:none}
.loader-bar{width:160px;height:2px;background:rgba(255,255,255,0.08);border-radius:2px;overflow:hidden}
.loader-bar-inner{height:100%;width:0%;background:linear-gradient(90deg,var(--accent),var(--accent2));transition:width .3s}
.loader-text{font-size:9px;color:var(--text2)}
::-webkit-scrollbar{width:2px;height:2px}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.06);border-radius:2px}
.modal-overlay{display:none;position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.5);backdrop-filter:blur(3px);align-items:center;justify-content:center}
.modal-overlay.show{display:flex}
.modal-box{background:#1e1e3a;border:1px solid var(--border);border-radius:8px;padding:14px;width:90%;max-width:380px;max-height:80vh;overflow-y:auto}
.modal-box h3{margin-bottom:8px;font-size:12px}
.modal-box label{font-size:9px;color:var(--text2);display:block;margin-top:5px}
.modal-box input,.modal-box select{width:100%;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:3px;padding:3px 5px;color:var(--text);font-size:11px;font-family:var(--font)}
.modal-box .btn-row{display:flex;gap:4px;justify-content:flex-end;margin-top:8px}
#toast{position:fixed;bottom:12px;left:50%;transform:translateX(-50%);z-index:99999;background:rgba(0,0,0,0.85);color:#fff;padding:4px 10px;border-radius:4px;font-size:9px;opacity:0;transition:opacity .3s;pointer-events:none}
#toast.show{opacity:1}
#props{position:absolute;top:32px;right:3px;z-index:100;width:160px;background:rgba(0,0,0,0.8);backdrop-filter:blur(4px);border-radius:4px;border:1px solid var(--border);padding:4px 5px;font-size:9px;display:none}
#props .title{font-weight:600;color:var(--text);margin-bottom:2px}
#props .row{display:flex;justify-content:space-between;padding:1px 0;color:var(--text2)}
</style>
</head>
<body>
<div id="header">
<span class="btn" style="border:none;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:700;font-size:12px">CAD</span>
<button class="btn btn-p" onclick="showGenModal()">生成</button>
<button class="btn" onclick="saveProj()">保存</button>
<button class="btn" onclick="loadProj()">打开</button>
<button class="btn btn-p" onclick="exportDXF()">DXF</button>
<button class="btn" onclick="exportPNG()">PNG</button>
<button class="btn" onclick="exportSVG()">SVG</button>
<button class="btn" onclick="undo()">撤销</button>
<button class="btn" onclick="redo()">重做</button>
<button class="btn" onclick="zoomFit()">适配</button>
<button class="btn" onclick="toggleSnap()" id="snap-btn">吸附</button>
<button class="btn btn-d" onclick="clearAll()">清空</button>
</div>
<div id="main">
<div id="left-panel">
<div id="tools">
<button class="tool-btn active" data-t="select" onclick="setTool('select')">选择</button>
<button class="tool-btn" data-t="wall" onclick="setTool('wall')">墙</button>
<button class="tool-btn" data-t="door" onclick="setTool('door')">门</button>
<button class="tool-btn" data-t="window" onclick="setTool('window')">窗</button>
<button class="tool-btn" data-t="dim" onclick="setTool('dim')">标注</button>
<div class="tool-sep"></div>
<button class="tool-btn" onclick="undo()">↩</button>
<button class="tool-btn" onclick="redo()">↪</button>
</div>
<div id="canvas-wrap"><canvas id="canvas-2d"></canvas></div>
<div id="status-bar">
<span id="tool-status">选择</span>
<span id="coord-display"></span>
<span id="obj-count"></span>
</div>
<div id="furn-bar"></div>
</div>
<div id="right-panel">
<div id="loading-3d">
<div class="loader-text">3D 加载中...</div>
<div class="loader-bar"><div class="loader-bar-inner" id="loader-progress"></div></div>
<div class="loader-text" id="loader-detail">初始化</div>
</div>
<div id="toolbar-3d">
<button class="btn3d" onclick="setView3D('top')">俯视</button>
<button class="btn3d" onclick="setView3D('perspective')">透视</button>
<button class="btn3d" onclick="rebuild3D()">刷新</button>
</div>
<canvas id="canvas-3d"></canvas>
</div>
</div>
<div id="toast"></div>
<div class="modal-overlay" id="gen-modal">
<div class="modal-box">
<h3>参数化户型生成</h3>
<label>整体尺寸 (mm)</label>
<div style="display:flex;gap:4px">
<input id="gw" value="10000" style="flex:1">
<span style="color:var(--text3);line-height:28px">x</span>
<input id="gd" value="8000" style="flex:1">
</div>
<label>房间配置</label>
<div id="room-configs"></div>
<button onclick="addRoomRowUI()" style="background:transparent;border:1px dashed rgba(255,255,255,0.2);border-radius:2px;padding:1px 6px;color:var(--text2);cursor:pointer;font-size:9px;margin-top:3px">+ 添加房间</button>
<div class="btn-row">
<button onclick="closeModal('gen-modal')" class="btn">取消</button>
<button onclick="generatePlan()" class="btn btn-p">生成</button>
</div>
</div>
</div>
"""

    # Add JS
    js = r"""<script>
const MATERIALS=""" + materials_js + r""";
const FL={"双人床":{"w":2000,"d":1800,"c":"#D2B48C","h":450},"单人床":{"w":1200,"d":2000,"c":"#D2B48C","h":450},"沙发":{"w":2200,"d":850,"c":"#8B4513","h":800},"茶几":{"w":1200,"d":600,"c":"#D2691E","h":450},"餐桌":{"w":1400,"d":800,"c":"#DEB887","h":750},"餐椅":{"w":480,"d":520,"c":"#C4A882","h":450},"衣柜":{"w":1800,"d":600,"c":"#C4A882","h":2000},"书桌":{"w":1200,"d":600,"c":"#8B7355","h":750},"电视柜":{"w":1800,"d":400,"c":"#3C3C3C","h":500},"冰箱":{"w":900,"d":800,"c":"#C0C0C0","h":1800},"洗衣机":{"w":600,"d":600,"c":"#E0E0E0","h":850},"马桶":{"w":400,"d":700,"c":"#F5F5F5","h":400},"洗手盆":{"w":600,"d":500,"c":"#FFF","h":800},"淋浴房":{"w":900,"d":900,"c":"#D0E0F0","h":2000},"灶台":{"w":800,"d":600,"c":"#2C2C2C","h":850},"水槽":{"w":800,"d":600,"c":"#A0A0A0","h":850},"钢琴":{"w":1500,"d":600,"c":"#1A1A1A","h":1200},"书架":{"w":800,"d":400,"c":"#8B7355","h":1800}};
const RT={"客厅":{"m":15,"x":50},"主卧":{"m":12,"x":30},"次卧":{"m":8,"x":20},"厨房":{"m":5,"x":15},"卫生间":{"m":3,"x":10},"餐厅":{"m":8,"x":25},"书房":{"m":6,"x":20},"阳台":{"m":3,"x":15}};

// ====== Core State ======
let S={w:[],d:[],wd:[],r:[],dm:[],f:[]},nid=1,hist=[[]],hidx=0;
let tool="select",snap=true,ds=null,sel=null,mp=[],hl={};
let c,cx,ox=0,oy=0,sc=1,W,H,pan=false,ps=null,ts=null;
const MS=50,SN=15,GD=100;

function sv(){
  let s=JSON.parse(JSON.stringify(S));
  hist=hist.slice(0,hidx+1);hist.push(s);
  if(hist.length>MS)hist.shift();hidx=hist.length-1;uc();
}
function undo(){if(hidx>0){hidx--;S=JSON.parse(JSON.stringify(hist[hidx]));r2();r3();uc()}}
function redo(){if(hidx<hist.length-1){hidx++;S=JSON.parse(JSON.stringify(hist[hidx]));r2();r3();uc()}}
function toast(m,d=2000){let e=document.getElementById("toast");e.textContent=m;e.classList.add("show");clearTimeout(e._t);e._t=setTimeout(()=>e.classList.remove("show"),d)}
function ci(i){document.getElementById(i).classList.remove("show")}
function uc(){document.getElementById("obj-count").textContent=S.w.length+"w "+S.d.length+"d "+S.f.length+"f"}

function ic(){
  c=document.getElementById("canvas-2d");cx=c.getContext("2d");rc();
  window.addEventListener("resize",rc);se();r2();
}
function rc(){
  let r=document.getElementById("canvas-wrap").getBoundingClientRect();
  W=c.width=r.width*devicePixelRatio;H=c.height=r.height*devicePixelRatio;
  c.style.width=r.width+"px";c.style.height=r.height+"px";
  cx.setTransform(1,0,0,1,0,0);cx.scale(devicePixelRatio,devicePixelRatio);
  W=r.width;H=r.height;r2();
}
function s2w(sx,sy){return{x:(sx-W/2)/sc-ox,y:(sy-H/2)/sc-oy}}
function w2s(wx,wy){return{x:(wx+ox)*sc+W/2,y:(wy+oy)*sc+H/2}}
function sn(p){
  if(!snap)return p;
  let x=Math.round(p.x/GD)*GD,y=Math.round(p.y/GD)*GD;
  for(let w of S.w){if(Math.abs(p.x-w.x1)<SN)x=w.x1;if(Math.abs(p.x-w.x2)<SN)x=w.x2;if(Math.abs(p.y-w.y1)<SN)y=w.y1;if(Math.abs(p.y-w.y2)<SN)y=w.y2}
  return{x,y};
}
function zf(){
  if(!S.w.length&&!S.f.length){ox=oy=0;sc=1;r2();return}
  let mn=Infinity,mx=-Infinity,mny=Infinity,mxy=-Infinity;
  for(let w of S.w){mn=Math.min(mn,w.x1,w.x2);mx=Math.max(mx,w.x1,w.x2);mny=Math.min(mny,w.y1,w.y2);mxy=Math.max(mxy,w.y1,w.y2)}
  for(let f of S.f){mn=Math.min(mn,f.x-f.w/2);mx=Math.max(mx,f.x+f.w/2);mny=Math.min(mny,f.y-f.d/2);mxy=Math.max(mxy,f.y+f.d/2)}
  mn-=200;mx+=200;mny-=200;mxy+=200;
  let w=mx-mn,h=mxy-mny;if(!w||!h)return;
  sc=Math.min(W*.8/w,H*.8/h,5);
  ox=-(mn+mx)/2;oy=-(mny+mxy)/2;r2();
}

function r2(){
  if(!cx)return;
  cx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);
  cx.clearRect(0,0,W,H);
  cx.fillStyle="#161628";cx.fillRect(0,0,W,H);
  let gs=GD,o=s2w(0,0),e=s2w(W,H);
  cx.strokeStyle="rgba(255,255,255,0.03)";cx.lineWidth=.5;
  for(let x=Math.floor(o.x/gs)*gs;x<e.x;x+=gs){let sx=(x+ox)*sc+W/2;cx.beginPath();cx.moveTo(sx,0);cx.lineTo(sx,H);cx.stroke()}
  for(let y=Math.floor(o.y/gs)*gs;y<e.y;y+=gs){let sy=(y+oy)*sc+H/2;cx.beginPath();cx.moveTo(0,sy);cx.lineTo(W,sy);cx.stroke()}
  cx.save();cx.translate(W/2,H/2);cx.scale(sc,sc);cx.translate(ox,oy);
  let lw=1/sc;
  for(let w of S.w){cx.strokeStyle=w.t==="外"?"#4a7cff":"#6a9cff";cx.lineWidth=w.th/sc;cx.lineCap="round";cx.beginPath();cx.moveTo(w.x1,w.y1);cx.lineTo(w.x2,w.y2);cx.stroke()}
  for(let d of S.d){let w=S.w.find(x=>x.id===d.wi);if(!w)continue;let dx=w.x2-w.x1,dy=w.y2-w.y1,len=Math.hypot(dx,dy);if(!len)continue;let r=d.p/len,cx=w.x1+dx*r,cy=w.y1+dy*r;cx.strokeStyle="#ff6b6b";cx.lineWidth=2/sc;cx.beginPath();cx.arc(cx,cy,d.wd/2,0,Math.PI*.5);cx.stroke()}
  for(let r of S.r){cx.fillStyle="rgba(102,126,234,0.06)";cx.strokeStyle="rgba(102,126,234,0.25)";cx.lineWidth=lw;cx.fillRect(r.x,r.y,r.w,r.d);cx.strokeRect(r.x,r.y,r.w,r.d);cx.fillStyle="rgba(255,255,255,0.5)";cx.font=10/sc+"px var(--font)";cx.textAlign="center";cx.fillText(r.n+" "+r.a+"m2",r.x+r.w/2,r.y+r.d/2)}
  for(let d of S.dm){cx.strokeStyle="#ffd700";cx.lineWidth=lw;cx.setLineDash([4/sc,3/sc]);cx.beginPath();cx.moveTo(d.x1,d.y1);cx.lineTo(d.x2,d.y2);cx.stroke();cx.setLineDash([]);let len=Math.hypot(d.x2-d.x1,d.y2-d.y1);cx.fillStyle="#ffd700";cx.font=8/sc+"px var(--font)";cx.textAlign="center";cx.fillText(Math.round(len)+"mm",(d.x1+d.x2)/2,(d.y1+d.y2)/2-3/sc)}
  for(let f of S.f){cx.fillStyle=f.c||"#888";cx.strokeStyle="rgba(255,255,255,0.3)";cx.lineWidth=lw;let x=f.x-f.w/2,y=f.y-f.d/2;cx.fillRect(x,y,f.w,f.d);cx.strokeRect(x,y,f.w,f.d);cx.fillStyle="rgba(255,255,255,0.7)";cx.font=7/sc+"px var(--font)";cx.textAlign="center";cx.fillText(f.n,f.x,f.y+3/sc)}
  if(ds&&ds.t==="wall"){cx.strokeStyle="rgba(255,255,0,0.5)";cx.lineWidth=150/sc;cx.lineCap="round";cx.beginPath();cx.moveTo(ds.x1,ds.y1);cx.lineTo(ds.x2,ds.y2);cx.stroke()}
  cx.restore();
}

function fi(id){for(let a of[S.w,S.d,S.wd,S.f,S.dm,S.r]){let f=a.find(e=>e.id===id);if(f)return f}return null}
function fa(px,py){let th=10/sc;for(let w of S.w){let dx=w.x2-w.x1,dy=w.y2-w.y1,len=Math.hypot(dx,dy);if(!len)continue;let t=((px-w.x1)*dx+(py-w.y1)*dy)/(len*len);if(t<0||t>1)continue;if(Math.hypot(px-(w.x1+t*dx),py-(w.y1+t*dy))<th)return{t:"wall",d:w}}for(let f of S.f){if(px>=f.x-f.w/2&&px<=f.x+f.w/2&&py>=f.y-f.d/2&&py<=f.y+f.d/2)return{t:"furn",d:f}}return null}
function gp(e){let r=c.getBoundingClientRect();return{x:e.clientX-r.left,y:e.clientY-r.top}}

function se(){
  c.onmousedown=e=>{
    if(e.button===1||e.button===2){pan=true;ps=gp(e);c.style.cursor="grabbing";return}
    let p=gp(e),w=s2w(p.x,p.y),s=sn(w);
    if(tool==="select"){let h=fa(w.x,w.y);sel=h?h.d.id:null;r2();return}
    if(tool==="wall")ds={t:"wall",x1:s.x,y1:s.y,x2:s.x,y2:s.y};
    if(tool==="dim"){if(!mp.length)mp=[s];else{S.dm.push({id:nid++,x1:mp[0].x,y1:mp[0].y,x2:s.x,y2:s.y});mp=[];sv();r2()}}
  };
  c.onmousemove=e=>{
    let p=gp(e),w=s2w(p.x,p.y),s=sn(w);
    document.getElementById("coord-display").textContent=Math.round(s.x)+","+Math.round(s.y);
    if(pan&&ps){ox+=(p.x-ps.x)/sc;oy+=(p.y-ps.y)/sc;ps=p;r2();return}
    if(ds&&ds.t==="wall"){ds.x2=s.x;ds.y2=s.y;r2()}
    let h=fa(w.x,w.y);c.style.cursor=h||tool!=="select"?"crosshair":"default";
  };
  c.onmouseup=e=>{
    if(pan){pan=false;c.style.cursor="crosshair";return}
    if(ds&&ds.t==="wall"){let dx=ds.x2-ds.x1,dy=ds.y2-ds.y1;if(Math.hypot(dx,dy)>100){let out=ds.x1===0||ds.x2===0||ds.y1===0||ds.y2===0||ds.x1>=10000||ds.x2>=10000||ds.y1>=10000||ds.y2>=10000;S.w.push({id:nid++,x1:ds.x1,y1:ds.y1,x2:ds.x2,y2:ds.y2,th:out?240:150,t:out?"外":"内"});sv();r3()}ds=null;r2()}
  };
  c.ondblclick=e=>{
    let p=gp(e),w=s2w(p.x,p.y),h=fa(w.x,w.y);
    if(h&&h.t==="furn"){let f=h.d,n=prompt("名称:",f.n);if(n)f.n=n;let w2=parseFloat(prompt("宽(mm):",f.w));if(w2)f.w=w2;let d=parseFloat(prompt("深(mm):",f.d));if(d)f.d=d;sv();r2();r3()}
  };
  c.onwheel=e=>{e.preventDefault();let d=e.deltaY>0?.9:1.1,p=gp(e),w=s2w(p.x,p.y);sc=Math.max(.05,Math.min(20,sc*d));ox=w.x-(p.x-W/2)/sc;oy=w.y-(p.y-H/2)/sc;r2()};
  c.oncontextmenu=e=>e.preventDefault();
  c.ontouchstart=e=>{e.preventDefault();if(e.touches.length===1){let t=e.touches[0],r=c.getBoundingClientRect();ts={m:"pan",sx:t.clientX-r.left,sy:t.clientY-r.top}}else if(e.touches.length===2){ts={m:"zoom",d:Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY),sc:sc}}};
  c.ontouchmove=e=>{e.preventDefault();if(!ts)return;let r=c.getBoundingClientRect();if(ts.m==="pan"&&e.touches.length===1){let t=e.touches[0];ox+=(t.clientX-r.left-ts.sx)/sc;oy+=(t.clientY-r.top-ts.sy)/sc;ts.sx=t.clientX-r.left;ts.sy=t.clientY-r.top;r2()}else if(ts.m==="zoom"&&e.touches.length===2){let d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);sc=Math.max(.05,Math.min(20,ts.sc*d/ts.d));r2()}};
  c.ontouchend=e=>{ts=null};
}

function st(t){tool=t;document.querySelectorAll(".tool-btn").forEach(b=>b.classList.toggle("active",b.dataset.t===t));document.getElementById("tool-status").textContent=t==="select"?"选择":t==="wall"?"画墙":t==="dim"?"标注":t;if(t!=="dim")mp=[]}
function tsn(){snap=!snap;document.getElementById("snap-btn").style.opacity=snap?"1":".4";toast(snap?"吸附:ON":"吸附:OFF")}
function ca(){if(!S.w.length&&!S.f.length)return;if(!confirm("确定清空？"))return;S={w:[],d:[],wd:[],r:[],dm:[],f:[]};sel=null;sv();r2();r3()}

// ====== Exports ======
function exD(){fetch("/api/export_dxf",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({walls:S.w,doors:S.d,windows:S.wd,rooms:S.r,furniture:S.f})}).then(r=>r.blob()).then(b=>{let u=URL.createObjectURL(b),a=document.createElement("a");a.href=u;a.download="plan.dxf";a.click();URL.revokeObjectURL(u);toast("DXF OK")}).catch(e=>toast("ERR: "+e.message))}
function exP(){let a=document.createElement("a");a.href=c.toDataURL("image/png");a.download="plan.png";a.click();toast("PNG OK")}
function exS(){let s='<svg xmlns="http://www.w3.org/2000/svg" viewBox="-5000 -4000 15000 12000"><rect x="-5000" y="-4000" width="15000" height="12000" fill="#161628"/>';for(let w of S.w)s+='<line x1="'+w.x1+'" y1="'+(-w.y1)+'" x2="'+w.x2+'" y2="'+(-w.y2)+'" stroke="'+(w.t==="外"?"#4a7cff":"#6a9cff")+'" stroke-width="'+w.th/10+'"/>';for(let f of S.f)s+='<rect x="'+(f.x-f.w/2)+'" y="'+(-f.y-f.d/2)+'" width="'+f.w+'" height="'+f.d+'" fill="'+(f.c||"#888")+'" opacity=".7"/><text x="'+f.x+'" y="'+(-f.y+4)+'" fill="white" font-size="12" text-anchor="middle">'+f.n+'</text>';s+='</svg>';let b=new Blob([s],{type:"image/svg+xml"}),u=URL.createObjectURL(b),a=document.createElement("a");a.href=u;a.download="plan.svg";a.click();URL.revokeObjectURL(u);toast("SVG OK")}

function svP(){let n=prompt("名称:","CAD_"+new Date().toISOString().slice(0,10));if(!n)return;let d={name:n,state:S,nextId:nid};fetch("/api/save_project",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(d)}).then(r=>r.json()).then(d=>{if(d.ok)toast("已保存")}).catch(e=>toast("保存失败"));try{localStorage.setItem("cad_p",JSON.stringify(d))}catch(e){}}
function ldP(){try{let s=localStorage.getItem("cad_p");if(s){let d=JSON.parse(s);if(d.state){S=d.state;nid=d.nextId||1;sv();r2();r3();toast("已加载");return}}}catch(e){}toast("无保存项目")}

// ====== Furniture Bar ======
function sFB(){let b=document.getElementById("furn-bar");for(let[n,l]of Object.entries(FL)){let e=document.createElement("span");e.className="furn-chip";e.textContent=n;e.onclick=()=>{let x=0,y=0;if(S.w.length){let w=S.w[0];x=(w.x1+w.x2)/2;y=(w.y1+w.y2)/2}S.f.push({id:nid++,n,x,y,w:l.w,d:l.d,c:l.c,h:l.h});sv();r2();r3();toast("+ "+n)};b.appendChild(e)}}

// ====== 3D Scene ======
let scn,cam,rend,ctrl,grp;
let tl=false,tg=false;

function i3(){
  let cv=document.getElementById("canvas-3d"),ld=document.getElementById("loading-3d");
  if(!cv||!cv.getContext)return;ld.classList.remove("hidden");
  document.getElementById("loader-detail").textContent="加载Three.js...";
  
  let im=document.createElement("script");im.type="importmap";
  im.textContent=JSON.stringify({imports:{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}});
  document.head.appendChild(im);
  
  let m=document.createElement("script");m.type="module";
  m.textContent='import*as THREE from"three";import{OrbitControls}from"three/addons/OrbitControls.js";window.THREE=THREE;window.OrbitControls=OrbitControls;window._3r=true';
  document.body.appendChild(m);
  
  let tr=0,ck=setInterval(()=>{
    tr++;document.getElementById("loader-detail").textContent="加载Three.js"+".".repeat(tr%4);
    if(window._3r||tr>60){clearInterval(ck);if(window._3r){document.getElementById("loader-detail").textContent="初始化3D...";setTimeout(itS,150)}else{document.getElementById("loader-detail").textContent="3D简化模式";setTimeout(if3,100)}}
  },500);
}

function if3(){tl=true;tg=false;document.getElementById("loading-3d").classList.add("hidden");toast("3D简化模式");r3()}

function itS(){
  let cv=document.getElementById("canvas-3d"),ld=document.getElementById("loading-3d");
  scn=new THREE.Scene();scn.background=new THREE.Color(0x161628);
  let w=cv.clientWidth||cv.parentElement.clientWidth||400,h=cv.clientHeight||cv.parentElement.clientHeight||300;
  cam=new THREE.PerspectiveCamera(45,w/h,1,50000);cam.position.set(8000,6000,8000);cam.lookAt(0,0,0);
  rend=new THREE.WebGLRenderer({canvas:cv,antialias:true});rend.setSize(w,h);rend.setPixelRatio(Math.min(devicePixelRatio,2));
  rend.shadowMap.enabled=true;rend.shadowMap.type=THREE.PCFSoftShadowMap;
  rend.toneMapping=THREE.ACESFilmicToneMapping;rend.toneMappingExposure=1.2;
  ctrl=new OrbitControls(cam,cv);ctrl.target.set(0,0,0);ctrl.enableDamping=true;ctrl.dampingFactor=.1;ctrl.maxPolarAngle=Math.PI/2.1;ctrl.minDistance=1000;ctrl.maxDistance=30000;
  let a=new THREE.AmbientLight(0x404060,.6);scn.add(a);
  let d=new THREE.DirectionalLight(0xffeedd,1.5);d.position.set(10000,15000,5000);d.castShadow=true;d.shadow.mapSize.set(1024,1024);scn.add(d);
  grp=new THREE.Group();scn.add(grp);
  window._3d={s:scn,c:cam,r:rend,ctl:ctrl,g:grp};
  document.getElementById("loader-progress").style.width="100%";tl=true;tg=false;
  ld.classList.add("hidden");
  window.addEventListener("resize",()=>{let w2=cv.clientWidth||cv.parentElement.clientWidth||400,h2=cv.clientHeight||cv.parentElement.clientHeight||300;cam.aspect=w2/h2;cam.updateProjectionMatrix();rend.setSize(w2,h2)});
  r3();a3();
}

function a3(){if(!tl)return;if(ctrl)ctrl.update();if(rend&&scn&&cam)rend.render(scn,cam);requestAnimationFrame(a3)}

function r3(){
  if(!tl){i3();return}
  if(!grp&&window._3d)grp=window._3d.g;if(!grp)return;
  while(grp.children.length)grp.remove(grp.children[0]);
  for(let w of S.w){let dx=w.x2-w.x1,dy=w.y2-w.y1,len=Math.hypot(dx,dy);if(!len)continue;let g=new THREE.BoxGeometry(len,w.th,2800);let m=new THREE.MeshStandardMaterial({color:w.t==="外"?0x4a7cff:0x6a9cff,roughness:.7});let me=new THREE.Mesh(g,m);me.position.set((w.x1+w.x2)/2,(w.y1+w.y2)/2,1400);me.rotation.z=-Math.atan2(dy,dx);me.castShadow=true;me.receiveShadow=true;grp.add(me)}
  for(let r of S.r){let g=new THREE.PlaneGeometry(r.w,r.d);let m=new THREE.MeshStandardMaterial({color:0x2a2a4a,roughness:.8,side:THREE.DoubleSide});let me=new THREE.Mesh(g,m);me.position.set(r.x+r.w/2,r.y+r.d/2,0);me.rotation.x=-Math.PI/2;me.receiveShadow=true;grp.add(me)}
  for(let f of S.f){let g=new THREE.BoxGeometry(f.w,f.d,f.h||800);let col=parseInt((f.c||"#888888").replace("#",""),16);let m=new THREE.MeshStandardMaterial({color:col,roughness:.6});let me=new THREE.Mesh(g,m);me.position.set(f.x,f.y,(f.h||800)/2);me.castShadow=true;me.receiveShadow=true;grp.add(me)}
  let gg=new THREE.PlaneGeometry(30000,30000);let gm=new THREE.MeshStandardMaterial({color:0x101020,roughness:1,side:THREE.DoubleSide});let gnd=new THREE.Mesh(gg,gm);gnd.position.set(0,0,-5);gnd.rotation.x=-Math.PI/2;gnd.receiveShadow=true;grp.add(gnd);
}

function sv3(v){if(!cam||!ctrl)return;let d=15000;if(v==="top"){cam.position.set(0,0,d);ctrl.target.set(0,0,0)}else{cam.position.set(d,d*.6,d*.4);ctrl.target.set(0,0,0)}ctrl.update()}

// ====== Generator ======
function sGM(){document.getElementById("gen-modal").classList.add("show")}

function aRR(n,a,t){
  let c=document.getElementById("room-configs"),d=document.createElement("div");
  d.style.cssText="display:flex;gap:3px;margin-bottom:3px";
  d.innerHTML='<input value="'+(n||"房间")+'" style="width:60px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:2px;padding:2px 4px;color:#fff;font-size:9px"><input value="'+(a||"10")+'" style="width:40px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:2px;padding:2px 4px;color:#fff;font-size:9px" placeholder="m2"><select style="flex:1;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:2px;padding:2px 4px;color:#fff;font-size:9px">'+Object.keys(RT).map(t=>'<option>'+t+'</option>').join("")+'</select><button onclick="this.parentElement.remove()" style="background:transparent;border:none;color:#e74c3c;cursor:pointer;font-size:12px">x</button>';
  if(t)d.querySelector("select").value=t;c.appendChild(d);
}
aRR("客厅",25,"客厅");aRR("主卧",18,"卧室");aRR("次卧",14,"卧室");aRR("厨房",8,"厨房");aRR("卫生间",6,"卫生间");aRR("餐厅",12,"餐厅");

function gP(){
  let gw=parseFloat(document.getElementById("gw").value)||10000,gd=parseFloat(document.getElementById("gd").value)||8000;
  let rows=document.getElementById("room-configs").children,rooms=[];
  for(let r of rows){let ins=r.querySelectorAll("input"),sel=r.querySelector("select");rooms.push({n:ins[0].value,a:parseFloat(ins[1].value)||10,t:sel.value})}
  if(!rooms.length){toast("请添加房间");return}
  let ta=rooms.reduce((s,r)=>s+r.a,0);if(ta*1.2>gw*gd/1e6){toast("总面积过大");return}
  if(!confirm("将清空并生成户型？"))return;
  S={w:[],d:[],wd:[],r:[],dm:[],f:[]};sel=null;
  let cells=[{x:0,y:0,w:gw,d:gd,rs:[...rooms]}],fr=[],nc=nid;
  
  function div(cell){
    let rl=cell.rs;if(!rl.length)return;
    if(rl.length===1){fr.push({n:rl[0].n,t:rl[0].t,a:rl[0].a,x:cell.x,y:cell.y,w:cell.w,d:cell.d});return}
    let sH=cell.w>cell.d,tA=rl.reduce((s,r)=>s+r.a,0),sA=sH?cell.w*(rl[0].a/tA):cell.d*(rl[0].a/tA);
    sA=Math.max(cell.w*.2,Math.min(cell.w*.8,sA));
    if(sH){cells.push({x:cell.x,y:cell.y,w:sA,d:cell.d,rs:[rl[0]]});cells.push({x:cell.x+sA,y:cell.y,w:cell.w-sA,d:cell.d,rs:rl.slice(1)})}
    else{cells.push({x:cell.x,y:cell.y,w:cell.w,d:sA,rs:[rl[0]]});cells.push({x:cell.x,y:cell.y+sA,w:cell.w,d:cell.d-sA,rs:rl.slice(1)})}
  }
  for(let i=0;i<rooms.length-1;i++){let td=cells.findIndex(c=>c.rs.length>1);if(td<0)break;div(cells.splice(td,1)[0])}
  
  for(let r of fr){
    let cx=r.x+r.w/2,cy=r.y+r.d/2;S.r.push({id:nc++,n:r.n,a:Math.round(r.w*r.d/1e6*10)/10,t:r.t,x:r.x,y:r.y,w:r.w,d:r.d});
    let ws=[{x1:r.x,y1:r.y,x2:r.x+r.w,y2:r.y},{x1:r.x+r.w,y1:r.y,x2:r.x+r.w,y2:r.y+r.d},{x1:r.x+r.w,y1:r.y+r.d,x2:r.x,y2:r.y+r.d},{x1:r.x,y1:r.y+r.d,x2:r.x,y2:r.y}];
    for(let w of ws){let dx=w.x2-w.x1,dy=w.y2-w.y1,len=Math.hypot(dx,dy);if(len<50)continue;let isE=w.x1===0||w.x2===0||w.y1===0||w.y2===0||w.x1>=gw||w.x2>=gw||w.y1>=gd||w.y2>=gd;let ex=S.w.find(ew=>Math.hypot(ew.x1-w.x1,ew.y1-w.y1)+Math.hypot(ew.x2-w.x2,ew.y2-w.y2)<50||Math.hypot(ew.x1-w.x2,ew.y1-w.y2)+Math.hypot(ew.x2-w.x1,ew.y2-w.y1)<50);if(!ex)S.w.push({id:nc++,x1:w.x1,y1:w.y1,x2:w.x2,y2:w.y2,th:isE?240:150,t:isE?"外":"内"})}
  }
  
  for(let r of fr){let dw=[];for(let w of S.w){if(Math.abs(w.x1-r.x)<50&&Math.abs(w.x2-r.x)<50)dw.push(w);else if(Math.abs(w.x1-(r.x+r.w))<50&&Math.abs(w.x2-(r.x+r.w))<50)dw.push(w);else if(Math.abs(w.y1-r.y)<50&&Math.abs(w.y2-r.y)<50)dw.push(w);else if(Math.abs(w.y1-(r.y+r.d))<50&&Math.abs(w.y2-(r.y+r.d))<50)dw.push(w)}dw.sort((a,b)=>Math.hypot(b.x2-b.x1,b.y2-b.y1)-Math.hypot(a.x2-a.x1,a.y2-a.y1));if(dw.length){let w=dw[0],len=Math.hypot(w.x2-w.x1,w.y2-w.y1);if(len>1500)S.d.push({id:nc++,wi:w.id,p:len*.3,wd:900})}}
  
  for(let r of fr){
    if(r.t==="卧室"){tAF("双人床",r.x+r.w*.3,r.y+r.d*.4);tAF("衣柜",r.x+r.w*.85,r.y+r.d*.2)}
    else if(r.t==="客厅"){tAF("沙发",r.x+r.w*.3,r.y+r.d*.7);tAF("茶几",r.x+r.w*.5,r.y+r.d*.5);tAF("电视柜",r.x+r.w*.5,r.y+r.d*.15)}
    else if(r.t==="餐厅"){tAF("餐桌",r.x+r.w*.5,r.y+r.d*.5);tAF("餐椅",r.x+r.w*.3,r.y+r.d*.65)}
    else if(r.t==="厨房"){tAF("冰箱",r.x+r.w*.85,r.y+r.d*.5);tAF("灶台",r.x+r.w*.3,r.y+r.d*.3);tAF("水槽",r.x+r.w*.3,r.y+r.d*.7)}
    else if(r.t==="卫生间"){tAF("马桶",r.x+r.w*.3,r.y+r.d*.3);tAF("洗手盆",r.x+r.w*.7,r.y+r.d*.7);tAF("淋浴房",r.x+r.w*.7,r.y+r.d*.3)}
    else if(r.t==="书房"){tAF("书桌",r.x+r.w*.5,r.y+r.d*.5)}
  }
  function tAF(n,fx,fy){let l=FL[n];if(!l)return;S.f.push({id:nc++,n,x:fx,y:fy,w:l.w,d:l.d,c:l.c,h:l.h})}
  nid=nc;sv();ci("gen-modal");r2();zf();setTimeout(r3,100);toast("户型已生成: "+fr.length+"房间");
}

// ====== Init ======
document.addEventListener("DOMContentLoaded",()=>{ic();sFB();try{let s=localStorage.getItem("cad_p");if(s){let d=JSON.parse(s);if(d.state){S=d.state;nid=d.nextId||1;sv();r2();setTimeout(r3,300);toast("已加载上次项目")}}}catch(e){}});
</script>
</body>
</html>"""

    html += js
    with open('interior_cad.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"OK: {len(html)} chars generated")

if __name__ == "__main__":
    gen_html()
