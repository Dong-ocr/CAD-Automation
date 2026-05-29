<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,user-scalable=no">
<title>CAD ??????</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#161628;color:#fff;font-family:system-ui,-apple-system,Microsoft YaHei,sans-serif;overflow:hidden;height:100vh;display:flex;flex-direction:column}
#hdr{height:34px;background:rgba(26,26,46,0.98);border-bottom:1px solid rgba(255,255,255,0.08);display:flex;align-items:center;padding:0 6px;gap:2px;flex-shrink:0;overflow-x:auto}
.btn{padding:2px 6px;border:1px solid rgba(255,255,255,0.12);border-radius:3px;background:rgba(255,255,255,0.04);color:#fff;cursor:pointer;font-size:9px;font-family:inherit;white-space:nowrap;height:20px}
.btn:hover{background:rgba(255,255,255,0.1)}
.btn-p{background:linear-gradient(135deg,#667eea,#764ba2);border:none}
.btn-d{color:#e74c3c;border-color:rgba(231,76,60,0.4)}
#main{flex:1;display:flex;overflow:hidden}
#left{width:260px;border-right:1px solid rgba(255,255,255,0.08);display:flex;flex-direction:column;background:rgba(22,22,40,0.96)}
#wrap{flex:1;position:relative;overflow:hidden}
#c2d{width:100%;height:100%;display:block}
#bar{height:20px;display:flex;align-items:center;padding:0 4px;border-top:1px solid rgba(255,255,255,0.05);font-size:8px;color:rgba(255,255,255,0.4);gap:4px;flex-shrink:0}
#right{flex:1;display:flex;flex-direction:column;position:relative}
#c3d{width:100%;height:100%;display:block;background:#161628}
#tools{display:flex;gap:1px;padding:2px 3px;border-bottom:1px solid rgba(255,255,255,0.08);flex-wrap:wrap;flex-shrink:0}
.tl{padding:1px 5px;border:1px solid transparent;border-radius:2px;background:transparent;color:rgba(255,255,255,0.5);cursor:pointer;font-size:9px;font-family:inherit}
.tl:hover{background:rgba(255,255,255,0.06);color:#fff}
.tl.a{border-color:#667eea;color:#fff;background:rgba(102,126,234,0.12)}
.sp{width:1px;height:10px;background:rgba(255,255,255,0.08);margin:auto 2px}
#fbar{height:22px;display:flex;align-items:center;gap:2px;padding:0 4px;border-top:1px solid rgba(255,255,255,0.08);background:rgba(22,22,40,0.85);flex-shrink:0;overflow-x:auto}
.fc{padding:0 5px;border:1px solid rgba(255,255,255,0.06);border-radius:6px;font-size:8px;cursor:pointer;white-space:nowrap;background:rgba(255,255,255,0.02);color:rgba(255,255,255,0.5)}
.fc:hover{background:rgba(102,126,234,0.12);border-color:#667eea}
#toast{position:fixed;bottom:12px;left:50%;transform:translateX(-50%);z-index:999;background:rgba(0,0,0,0.85);color:#fff;padding:4px 10px;border-radius:4px;font-size:9px;opacity:0;transition:opacity .3s;pointer-events:none}
#toast.s{opacity:1}
#t3d{position:absolute;top:3px;left:50%;transform:translateX(-50%);z-index:100;display:flex;gap:2px;background:rgba(0,0,0,0.5);padding:2px 4px;border-radius:4px}
.b3{padding:1px 5px;border:none;border-radius:2px;background:transparent;color:rgba(255,255,255,0.5);cursor:pointer;font-size:8px;font-family:inherit}
.b3:hover{background:rgba(255,255,255,0.08);color:#fff}
::-webkit-scrollbar{width:2px;height:2px}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.06);border-radius:2px}
</style>
</head>
<body>
<div id=hdr>
<button class=btn btn-p onclick=loadDemo()>Demo</button>
<button class=btn onclick=svProj()>Save</button>
<button class=btn onclick=ldProj()>Load</button>
<button class=btn btn-p onclick=exD()>DXF</button>
<button class=btn onclick=exP()>PNG</button>
<button class=btn onclick=undo()>Undo</button>
<button class=btn onclick=redo()>Redo</button>
<button class=btn onclick=zf()>Fit</button>
<button class=btn onclick=tsn() id=sb>Snap</button>
<button class=btn btn-d onclick=ca()>Clear</button>
</div>
<div id=main>
<div id=left>
<div id=tools>
<button class="tl a" data-t=select onclick=st('select')>Sel</button>
<button class=tl data-t=wall onclick=st('wall')>Wall</button>
<button class=tl data-t=door onclick=st('door')>Door</button>
<button class=tl data-t=dim onclick=st('dim')>Dim</button>
<div class=sp></div>
<button class=tl onclick=undo()>Undo</button>
<button class=tl onclick=redo()>Redo</button>
</div>
<div id=wrap><canvas id=c2d></canvas></div>
<div id=bar><span id=ts>Ready</span><span id=cd></span><span id=oc></span></div>
<div id=fbar></div>
</div>
<div id=right>
<div id=t3d>
<button class=b3 onclick=tt()>Top</button>
<button class=b3 onclick=r3()>Ref</button>
</div>
<canvas id=c3d></canvas>
</div>
</div>
<div id=toast></div>
<script>
// ====== State ======
var S={w:[],d:[],r:[],dm:[],f:[]},nid=1,hist=[[]],hidx=0,tl='select',sn=true,ds=null,sel=null,mp=[],ly={};
var c2,cx,ox=0,oy=0,sc=1,W,H,pan=false,ps=null,ts=null,tl3=true;

function sv(){var s=JSON.parse(JSON.stringify(S));hist=hist.slice(0,hidx+1);hist.push(s);if(hist.length>50)hist.shift();hidx=hist.length-1;uc()}
function undo(){if(hidx>0){hidx--;S=JSON.parse(JSON.stringify(hist[hidx]));r2();r3();uc()}}
function redo(){if(hidx<hist.length-1){hidx++;S=JSON.parse(JSON.stringify(hist[hidx]));r2();r3();uc()}}
function uc(){var e=document.getElementById('oc');e.textContent=S.w.length+'w '+S.d.length+'d '+S.f.length+'f'}
function tm(m,d){var e=document.getElementById('toast');e.textContent=m;e.classList.add('s');clearTimeout(e._t);e._t=setTimeout(function(){e.classList.remove('s')},d||2000)}

// ====== Canvas 2D ======
function ic(){
  c2=document.getElementById('c2d');cx=c2.getContext('2d');rc();
  window.addEventListener('resize',rc);se();r2();
}
function rc(){
  var r=document.getElementById('wrap').getBoundingClientRect();
  W=c2.width=r.width*devicePixelRatio;H=c2.height=r.height*devicePixelRatio;
  c2.style.width=r.width+'px';c2.style.height=r.height+'px';
  cx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);W=Math.max(r.width,100);H=Math.max(r.height,100);r2();
}
function s2w(sx,sy){return{x:(sx-W/2)/sc-ox,y:(sy-H/2)/sc-oy}}
function snp(p){
  if(!sn)return p;
  var x=Math.round(p.x/100)*100,y=Math.round(p.y/100)*100;
  for(var i=0;i<S.w.length;i++){var w=S.w[i];if(Math.abs(p.x-w.x1)<15)x=w.x1;if(Math.abs(p.x-w.x2)<15)x=w.x2;if(Math.abs(p.y-w.y1)<15)y=w.y1;if(Math.abs(p.y-w.y2)<15)y=w.y2}
  return{x:x,y:y};
}
function zf(){
  if(!S.w.length&&!S.f.length){ox=0;oy=0;sc=1;r2();return}
  var mn=999999,mx=-999999,mny=999999,mxy=-999999;
  for(var i=0;i<S.w.length;i++){var w=S.w[i];mn=Math.min(mn,w.x1,w.x2);mx=Math.max(mx,w.x1,w.x2);mny=Math.min(mny,w.y1,w.y2);mxy=Math.max(mxy,w.y1,w.y2)}
  for(var i=0;i<S.f.length;i++){var f=S.f[i];mn=Math.min(mn,f.x-f.w/2);mx=Math.max(mx,f.x+f.w/2);mny=Math.min(mny,f.y-f.d/2);mxy=Math.max(mxy,f.y+f.d/2)}
  mn-=200;mx+=200;mny-=200;mxy+=200;
  var w=mx-mn,h=mxy-mny;if(!w||!h)return;
  sc=Math.min(W*0.8/w,H*0.8/h,5);ox=-(mn+mx)/2;oy=-(mny+mxy)/2;r2();
}

function r2(){
  if(!cx)return;
  cx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);
  cx.clearRect(0,0,W,H);cx.fillStyle='#161628';cx.fillRect(0,0,W,H);
  var o=s2w(0,0),e=s2w(W,H);
  cx.strokeStyle='rgba(255,255,255,0.03)';cx.lineWidth=0.5;
  for(var x=Math.floor(o.x/100)*100;x<e.x;x+=100){var sx=(x+ox)*sc+W/2;cx.beginPath();cx.moveTo(sx,0);cx.lineTo(sx,H);cx.stroke()}
  for(var y=Math.floor(o.y/100)*100;y<e.y;y+=100){var sy=(y+oy)*sc+H/2;cx.beginPath();cx.moveTo(0,sy);cx.lineTo(W,sy);cx.stroke()}
  cx.save();cx.translate(W/2,H/2);cx.scale(sc,sc);cx.translate(ox,oy);
  for(var i=0;i<S.w.length;i++){var w=S.w[i];if(ly.w===0)continue;cx.strokeStyle=w.t==='\u5916'?'#4a7cff':'#6a9cff';cx.lineWidth=w.th/sc;cx.lineCap='round';cx.beginPath();cx.moveTo(w.x1,w.y1);cx.lineTo(w.x2,w.y2);cx.stroke()}
  for(var i=0;i<S.d.length;i++){var d=S.d[i];var wa=null;for(var j=0;j<S.w.length;j++){if(S.w[j].id===d.wi){wa=S.w[j];break}}if(!wa)continue;var dx=wa.x2-wa.x1,dy=wa.y2-wa.y1,len=Math.hypot(dx,dy);if(!len)continue;var r2=d.p/len,cx2=wa.x1+dx*r2,cy2=wa.y1+dy*r2;cx.strokeStyle='#ff6b6b';cx.lineWidth=2/sc;cx.beginPath();cx.arc(cx2,cy2,d.wd/2,0,Math.PI*0.5);cx.stroke()}
  for(var i=0;i<S.dm.length;i++){var d=S.dm[i];cx.strokeStyle='#ffd700';cx.lineWidth=1/sc;cx.setLineDash([4/sc,3/sc]);cx.beginPath();cx.moveTo(d.x1,d.y1);cx.lineTo(d.x2,d.y2);cx.stroke();cx.setLineDash([]);var len2=Math.hypot(d.x2-d.x1,d.y2-d.y1);cx.fillStyle='#ffd700';cx.font=(9/sc)+'px sans-serif';cx.textAlign='center';cx.fillText(Math.round(len2)+'mm',(d.x1+d.x2)/2,(d.y1+d.y2)/2-3/sc)}
  for(var i=0;i<S.f.length;i++){var f=S.f[i];cx.fillStyle=f.c||'#888';cx.strokeStyle='rgba(255,255,255,0.3)';cx.lineWidth=1/sc;cx.fillRect(f.x-f.w/2,f.y-f.d/2,f.w,f.d);cx.strokeRect(f.x-f.w/2,f.y-f.d/2,f.w,f.d);cx.fillStyle='rgba(255,255,255,0.7)';cx.font=(7/sc)+'px sans-serif';cx.textAlign='center';cx.fillText(f.n,f.x,f.y+3/sc)}
  if(ds&&ds.t==='wall'){cx.strokeStyle='rgba(255,255,0,0.5)';cx.lineWidth=150/sc;cx.lineCap='round';cx.beginPath();cx.moveTo(ds.x1,ds.y1);cx.lineTo(ds.x2,ds.y2);cx.stroke()}
  cx.restore();
}

function fa(px,py){var th=10/sc;for(var i=0;i<S.w.length;i++){var w=S.w[i];var dx=w.x2-w.x1,dy=w.y2-w.y1,len=Math.sqrt(dx*dx+dy*dy);if(!len)continue;var t=((px-w.x1)*dx+(py-w.y1)*dy)/(len*len);if(t<0||t>1)continue;if(Math.sqrt((px-(w.x1+t*dx))*(px-(w.x1+t*dx))+(py-(w.y1+t*dy))*(py-(w.y1+t*dy)))<th)return{t:'w',d:w}}for(var i=0;i<S.f.length;i++){var f=S.f[i];if(px>=f.x-f.w/2&&px<=f.x+f.w/2&&py>=f.y-f.d/2&&py<=f.y+f.d/2)return{t:'f',d:f}}return null}
function gp(e){var r=c2.getBoundingClientRect();return{x:e.clientX-r.left,y:e.clientY-r.top}}

function se(){
  c2.onmousedown=function(e){
    if(e.button===1||e.button===2){pan=true;ps=gp(e);c2.style.cursor='grabbing';return}
    var p=gp(e),w=s2w(p.x,p.y),s=snp(w);
    if(tl==='select'){var h=fa(w.x,w.y);sel=h?h.d.id:null;r2();return}
    if(tl==='wall')ds={t:'wall',x1:s.x,y1:s.y,x2:s.x,y2:s.y};
    if(tl==='dim'){if(!mp.length)mp=[s];else{S.dm.push({id:nid++,x1:mp[0].x,y1:mp[0].y,x2:s.x,y2:s.y});mp=[];sv();r2()}}
  };
  c2.onmousemove=function(e){
    var p=gp(e),w=s2w(p.x,p.y),s=snp(w);
    document.getElementById('cd').textContent=Math.round(s.x)+','+Math.round(s.y);
    if(pan&&ps){ox+=(p.x-ps.x)/sc;oy+=(p.y-ps.y)/sc;ps=p;r2();return}
    if(ds&&ds.t==='wall'){ds.x2=s.x;ds.y2=s.y;r2()}
    var h=fa(w.x,w.y);c2.style.cursor=h||tl!=='select'?'crosshair':'default';
  };
  c2.onmouseup=function(e){
    if(pan){pan=false;c2.style.cursor='crosshair';return}
    if(ds&&ds.t==='wall'){var dx=ds.x2-ds.x1,dy=ds.y2-ds.y1;if(Math.sqrt(dx*dx+dy*dy)>100){var out=ds.x1===0||ds.x2===0||ds.y1===0||ds.y2===0||ds.x1>=10000||ds.x2>=10000||ds.y1>=10000||ds.y2>=10000;S.w.push({id:nid++,x1:ds.x1,y1:ds.y1,x2:ds.x2,y2:ds.y2,th:out?240:150,t:out?'\u5916':'\u5185'});sv();r3()}ds=null;r2()}
  };
  c2.onwheel=function(e){e.preventDefault();var d=e.deltaY>0?0.9:1.1,p=gp(e),w=s2w(p.x,p.y);sc=Math.max(0.05,Math.min(20,sc*d));ox=w.x-(p.x-W/2)/sc;oy=w.y-(p.y-H/2)/sc;r2()};
  c2.oncontextmenu=function(e){e.preventDefault()};
  c2.ontouchstart=function(e){e.preventDefault();if(e.touches.length===1){var t=e.touches[0],r=c2.getBoundingClientRect();ts={m:'p',sx:t.clientX-r.left,sy:t.clientY-r.top}}};
  c2.ontouchmove=function(e){e.preventDefault();if(!ts)return;var r=c2.getBoundingClientRect();if(ts.m==='p'&&e.touches.length===1){var t=e.touches[0];ox+=(t.clientX-r.left-ts.sx)/sc;oy+=(t.clientY-r.top-ts.sy)/sc;ts.sx=t.clientX-r.left;ts.sy=t.clientY-r.top;r2()}};
  c2.ontouchend=function(e){ts=null};
}

function st(t){tl=t;var bs=document.querySelectorAll('.tl');for(var i=0;i<bs.length;i++)bs[i].classList.remove('a');var es=document.querySelectorAll('[data-t='+t+']');for(var i=0;i<es.length;i++)es[i].classList.add('a');document.getElementById('ts').textContent=t;if(t!=='dim')mp=[]}
function tsn(){sn=!sn;document.getElementById('sb').style.opacity=sn?'1':'0.4';tm(sn?'Snap:ON':'Snap:OFF')}
function ca(){if(!S.w.length&&!S.f.length)return;if(!confirm('Clear?'))return;S={w:[],d:[],r:[],dm:[],f:[]};sel=null;sv();r2();r3()}

// ====== Exports ======
function exD(){fetch('/api/export_dxf',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({walls:S.w,doors:S.d,windows:[],rooms:S.r,furniture:S.f})}).then(function(r){return r.blob()}).then(function(b){var u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download='plan.dxf';a.click();URL.revokeObjectURL(u);tm('DXF OK')}).catch(function(e){tm('Err: '+e.message)})}
function exP(){var a=document.createElement('a');a.href=c2.toDataURL('image/png');a.download='plan.png';a.click();tm('PNG OK')}
function svProj(){var n=prompt('Name:','CAD_'+new Date().toISOString().slice(0,10));if(!n)return;var d={name:n,state:S,nextId:nid};localStorage.setItem('cad_p',JSON.stringify(d));tm('Saved')}
function ldProj(){try{var s=localStorage.getItem('cad_p');if(s){var d=JSON.parse(s);if(d.state){S=d.state;nid=d.nextId||1;sv();r2();r3();tm('Loaded');return}}}catch(e){}tm('No saved project')}

// ====== Furniture Bar ======
var FL={};
function sFB(){
  var b=document.getElementById('fbar');var names=['Sofa','Table','Chair','Bed','Wardrobe','Desk','Fridge','Toilet','Sink'];
  var ws=[2200,1400,480,2000,1800,1200,900,400,600];
  var ds=[850,800,520,1800,600,600,800,700,500];
  var cs=['#8B4513','#DEB887','#C4A882','#D2B48C','#C4A882','#8B7355','#C0C0C0','#F5F5F5','#FFFFFF'];
  var hs=[800,750,450,450,2000,750,1800,400,800];
  for(var i=0;i<names.length;i++){
    (function(n,w,d,c,h){
      var e=document.createElement('span');e.className='fc';e.textContent=n;
      e.onclick=function(){var x=0,y=0;if(S.w.length>0){var w2=S.w[0];x=(w2.x1+w2.x2)/2;y=(w2.y1+w2.y2)/2}S.f.push({id:nid++,n:n,x:x,y:y,w:w,d:d,c:c,h:h});sv();r2();r3();tm('+ '+n)};
      b.appendChild(e);
    })(names[i],ws[i],ds[i],cs[i],hs[i]);
  }
}

// ====== Canvas 3D (no CDN needed) ======
function r3(){
  if(!tl3)return;
  var cv=document.getElementById('c3d');if(!cv||!cv.getContext)return;
  var cx=cv.getContext('2d');
  var w=cv.clientWidth||400,h=cv.clientHeight||300;
  if(w<10)w=400;if(h<10)h=300;
  cv.width=w*devicePixelRatio;cv.height=h*devicePixelRatio;
  cx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);
  cx.fillStyle='#161628';cx.fillRect(0,0,w,h);
  cx.fillStyle='rgba(16,16,32,0.5)';cx.fillRect(0,h*0.65,w,h*0.35);
  
  var sc3=0.15;var cx3=function(x,y,z){return w/2+(x-y)*sc3};
  var cy3=function(x,y,z){return h/2+(x+y)*sc3*0.4-z*sc3*0.6};
  var py3=function(x,y,z){return cy3(x,y,0)+h*0.1};
  
  // Walls
  for(var i=0;i<S.w.length;i++){
    var wd=S.w[i];var dx=wd.x2-wd.x1,dy=wd.y2-wd.y1;
    var ang=Math.atan2(dy,dx);var nx=-Math.sin(ang)*wd.th/2,ny=Math.cos(ang)*wd.th/2;
    var hgt=2800;var col=wd.t==='\u5916'?'#4a7cff':'#6a9cff';
    
    cx.fillStyle=col;cx.globalAlpha=0.7;
    cx.beginPath();
    cx.moveTo(cx3(wd.x1+nx,wd.y1+ny,hgt),py3(wd.x1+nx,wd.y1+ny,hgt));
    cx.lineTo(cx3(wd.x2+nx,wd.y2+ny,hgt),py3(wd.x2+nx,wd.y2+ny,hgt));
    cx.lineTo(cx3(wd.x2-nx,wd.y2-ny,hgt),py3(wd.x2-nx,wd.y2-ny,hgt));
    cx.lineTo(cx3(wd.x1-nx,wd.y1-ny,hgt),py3(wd.x1-nx,wd.y1-ny,hgt));
    cx.closePath();cx.fill();
    
    cx.fillStyle=col;cx.globalAlpha=0.5;
    cx.beginPath();
    cx.moveTo(cx3(wd.x1+nx,wd.y1+ny,0),py3(wd.x1+nx,wd.y1+ny,0));
    cx.lineTo(cx3(wd.x2+nx,wd.y2+ny,0),py3(wd.x2+nx,wd.y2+ny,0));
    cx.lineTo(cx3(wd.x2+nx,wd.y2+ny,hgt),py3(wd.x2+nx,wd.y2+ny,hgt));
    cx.lineTo(cx3(wd.x1+nx,wd.y1+ny,hgt),py3(wd.x1+nx,wd.y1+ny,hgt));
    cx.closePath();cx.fill();
    
    cx.fillStyle=col;cx.globalAlpha=0.3;
    cx.beginPath();
    cx.moveTo(cx3(wd.x2+nx,wd.y2+ny,0),py3(wd.x2+nx,wd.y2+ny,0));
    cx.lineTo(cx3(wd.x2-nx,wd.y2-ny,0),py3(wd.x2-nx,wd.y2-ny,0));
    cx.lineTo(cx3(wd.x2-nx,wd.y2-ny,hgt),py3(wd.x2-nx,wd.y2-ny,hgt));
    cx.lineTo(cx3(wd.x2+nx,wd.y2+ny,hgt),py3(wd.x2+nx,wd.y2+ny,hgt));
    cx.closePath();cx.fill();cx.globalAlpha=1;
  }
  
  // Furniture
  for(var i=0;i<S.f.length;i++){
    var f=S.f[i];var fh=f.h||800;var col=f.c||'#888';
    cx.fillStyle=col;cx.globalAlpha=0.8;
    cx.beginPath();
    cx.moveTo(cx3(f.x-f.w/2,f.y-f.d/2,fh),py3(f.x-f.w/2,f.y-f.d/2,fh));
    cx.lineTo(cx3(f.x+f.w/2,f.y-f.d/2,fh),py3(f.x+f.w/2,f.y-f.d/2,fh));
    cx.lineTo(cx3(f.x+f.w/2,f.y+f.d/2,fh),py3(f.x+f.w/2,f.y+f.d/2,fh));
    cx.lineTo(cx3(f.x-f.w/2,f.y+f.d/2,fh),py3(f.x-f.w/2,f.y+f.d/2,fh));
    cx.closePath();cx.fill();
    
    cx.fillStyle=col;cx.globalAlpha=0.6;
    cx.beginPath();
    cx.moveTo(cx3(f.x-f.w/2,f.y+f.d/2,0),py3(f.x-f.w/2,f.y+f.d/2,0));
    cx.lineTo(cx3(f.x+f.w/2,f.y+f.d/2,0),py3(f.x+f.w/2,f.y+f.d/2,0));
    cx.lineTo(cx3(f.x+f.w/2,f.y+f.d/2,fh),py3(f.x+f.w/2,f.y+f.d/2,fh));
    cx.lineTo(cx3(f.x-f.w/2,f.y+f.d/2,fh),py3(f.x-f.w/2,f.y+f.d/2,fh));
    cx.closePath();cx.fill();cx.globalAlpha=1;
  }
  
  cx.fillStyle='rgba(255,255,255,0.1)';cx.font='9px sans-serif';cx.textAlign='center';cx.fillText('3D Canvas',w/2,14);
}
function tt(){r3();tm('View refreshed')}

// ====== Load Demo ======
function loadDemo(){
  fetch('/api/load_demo').then(function(r){return r.json()}).then(function(d){
    if(d.walls){S=d;nid=100;sv();r2();zf();setTimeout(function(){r3()},100);tm('Demo: '+d.rooms.length+' rooms, '+d.furniture.length+' furniture')}
    else tm('No demo data')
  }).catch(function(e){tm('Error: '+e.message)});
}

// ====== Keyboard ======
document.addEventListener('keydown',function(e){
  if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA')return;
  if(e.key==='Delete'||e.key==='Backspace'){ca();e.preventDefault()}
  if(e.key==='Escape'){sel=null;ds=null;mp=[];r2()}
  if(e.ctrlKey&&e.key==='z'){undo();e.preventDefault()}
  if(e.ctrlKey&&e.key==='y'){redo();e.preventDefault()}
  if(e.key===' '){e.preventDefault();tsn()}
});

// ====== Init ======
ic();sFB();
try{var s=localStorage.getItem('cad_p');if(s){var d=JSON.parse(s);if(d.state){S=d.state;nid=d.nextId||1;sv();r2();setTimeout(function(){r3()},200);tm('Last project loaded')}}}catch(e){}
</script>
</body>
</html>