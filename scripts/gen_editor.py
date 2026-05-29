import json, os

os.chdir(r"E:\CAD自动化制图")

with open("demo_project.json", "r", encoding="utf-8") as f:
    demo_data = json.load(f)

demo_json = json.dumps(demo_data, ensure_ascii=False)

# Build HTML in parts using list
parts = []
A = parts.append

A("<!DOCTYPE html>")
A('<html lang="zh-CN">')
A("<head>")
A('<meta charset="UTF-8">')
A('<meta name="viewport" content="width=device-width,initial-scale=1.0">')
A("<title>CAD 编辑器 - 岩泊渡水电站</title>")
A("<style>")
A("*{margin:0;padding:0;box-sizing:border-box}")
A("body{background:#0d0d1a;color:#fff;font-family:system-ui,-apple-system,'Microsoft YaHei',sans-serif;overflow:hidden;height:100vh;display:flex;flex-direction:column}")
A("#hdr{height:38px;background:linear-gradient(90deg,#0f0f23,#1a1a3e);border-bottom:1px solid rgba(255,255,255,0.06);display:flex;align-items:center;padding:0 8px;gap:3px;flex-shrink:0;overflow-x:auto}")
A(".btn{padding:3px 10px;border:1px solid rgba(255,255,255,0.1);border-radius:4px;background:rgba(255,255,255,0.04);color:#ccc;cursor:pointer;font-size:11px;font-family:inherit;white-space:nowrap;height:24px;transition:.15s}")
A(".btn:hover{background:rgba(255,255,255,0.1);color:#fff}")
A(".btn-p{background:linear-gradient(135deg,#667eea,#764ba2);border:none;color:#fff}")
A(".btn-d{color:#e74c3c;border-color:rgba(231,76,60,0.3)}")
A("#main{flex:1;display:flex;overflow:hidden}")
A("#left{width:280px;border-right:1px solid rgba(255,255,255,0.06);display:flex;flex-direction:column;background:rgba(13,13,26,0.96)}")
A("#wrap{flex:1;position:relative;overflow:hidden}")
A("#c2d{width:100%;height:100%;display:block}")
A("#bar{height:22px;display:flex;align-items:center;padding:0 6px;border-top:1px solid rgba(255,255,255,0.04);font-size:10px;color:rgba(255,255,255,0.35);gap:8px;flex-shrink:0}")
A("#right{flex:1;display:flex;flex-direction:column;position:relative}")
A("#c3d{width:100%;height:100%;display:block;background:#0d0d1a}")
A("#tools{display:flex;gap:2px;padding:4px 6px;border-bottom:1px solid rgba(255,255,255,0.06);flex-wrap:wrap;flex-shrink:0}")
A(".tl{padding:3px 8px;border:1px solid transparent;border-radius:3px;background:transparent;color:rgba(255,255,255,0.4);cursor:pointer;font-size:10px;font-family:inherit}")
A(".tl:hover{background:rgba(255,255,255,0.06);color:#ccc}")
A(".tl.a{border-color:#667eea;color:#fff;background:rgba(102,126,234,0.15)}")
A(".sp{width:1px;height:14px;background:rgba(255,255,255,0.06);margin:auto 3px}")
A("#fbar{height:28px;display:flex;align-items:center;gap:3px;padding:0 6px;border-top:1px solid rgba(255,255,255,0.06);background:rgba(13,13,26,0.85);flex-shrink:0;overflow-x:auto}")
A(".fc{padding:2px 8px;border:1px solid rgba(255,255,255,0.05);border-radius:4px;font-size:10px;cursor:pointer;white-space:nowrap;background:rgba(255,255,255,0.02);color:rgba(255,255,255,0.45)}")
A(".fc:hover{background:rgba(102,126,234,0.12);border-color:#667eea;color:#fff}")
A("#toast{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);z-index:999;background:rgba(0,0,0,0.88);color:#fff;padding:6px 14px;border-radius:6px;font-size:11px;opacity:0;transition:opacity .3s;pointer-events:none;border:1px solid rgba(255,255,255,0.06)}")
A("#toast.s{opacity:1}")
A("#t3d{position:absolute;top:6px;left:50%;transform:translateX(-50%);z-index:100;display:flex;gap:3px;background:rgba(0,0,0,0.55);padding:3px 6px;border-radius:6px}")
A(".b3{padding:2px 8px;border:none;border-radius:3px;background:transparent;color:rgba(255,255,255,0.4);cursor:pointer;font-size:9px;font-family:inherit}")
A(".b3:hover{background:rgba(255,255,255,0.08);color:#fff}")
A("#info{position:absolute;bottom:4px;left:4px;z-index:50;font-size:9px;color:rgba(255,255,255,0.2);pointer-events:none}")
A("::selection{background:rgba(102,126,234,0.3)}")
A("::-webkit-scrollbar{width:3px;height:3px}")
A("::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.08);border-radius:2px}")
A("</style></head><body>")
A('<div id=hdr>')
A('<button class="btn btn-p" onclick=loadDemo()>导入 Demo</button>')
A('<button class=btn onclick=svProj()>保存</button>')
A('<button class=btn onclick=ldProj()>加载</button>')
A('<span style="color:rgba(255,255,255,0.08);width:1px;height:14px;margin:0 3px;background:currentColor"></span>')
A('<button class=btn onclick=exDxf()>导出 DXF</button>')
A('<button class=btn onclick=exJson()>导出 JSON</button>')
A('<span style="color:rgba(255,255,255,0.08);width:1px;height:14px;margin:0 3px;background:currentColor"></span>')
A('<button class=btn onclick=undo()>撤销</button>')
A('<button class=btn onclick=redo()>重做</button>')
A('<span style="color:rgba(255,255,255,0.08);width:1px;height:14px;margin:0 3px;background:currentColor"></span>')
A('<button class=btn onclick=zf()>适应</button>')
A('<button class=btn onclick=tsn() id=sb>捕捉</button>')
A('<button class="btn btn-d" onclick=ca()>清除</button>')
A('</div><div id=main><div id=left><div id=tools>')
A('<button class="tl a" data-t=select onclick=st("select")>选择</button>')
A('<button class=tl data-t=wall onclick=st("wall")>墙</button>')
A('<button class=tl data-t=door onclick=st("door")>门</button>')
A('<button class=tl data-t=dim onclick=st("dim")>尺寸</button>')
A('<button class=tl data-t=room onclick=st("room")>房间</button>')
A('<div class=sp></div>')
A('<button class=tl onclick=undo()>←</button>')
A('<button class=tl onclick=redo()>→</button>')
A('</div><div id=wrap><canvas id=c2d></canvas>')
A('<div id=info>左键: 绘制 | 右键: 移动 | 滚轮: 缩放 | Del: 删除 | 空格: 捕捉切换</div></div>')
A('<div id=bar><span id=ts style="color:rgba(255,255,255,0.5)">选择</span><span id=cd></span><span id=oc></span></div>')
A('<div id=fbar></div></div>')
A('<div id=right><div id=t3d><button class=b3 onclick=r3()>≡ 3D</button></div><canvas id=c3d></canvas></div></div>')
A('<div id=toast></div>')

# Script
A('<script>')
A('var DEMO_DATA = ' + demo_json + ';')

# Minimal JS that works
JS = '''
var S={w:[],d:[],r:[],dm:[],f:[]},nid=1,hist=[[]],hidx=0,tl="select",sn=true,ds=null,sel=null,mp=[],V={ox:0,oy:0,sc:1,W:600,H:400},GRID=100;
function tm(t){var e=document.getElementById("toast");e.textContent=t;e.classList.add("s");clearTimeout(e._t);e._t=setTimeout(function(){e.classList.remove("s")},2000)}
function sv(){hist=hist.slice(0,hidx+1);hist.push(JSON.parse(JSON.stringify(S)));hidx=hist.length-1;if(hist.length>50)hist.shift()}
function undo(){if(hidx>0){hidx--;S=JSON.parse(JSON.stringify(hist[hidx]));r2();r3()}}
function redo(){if(hidx<hist.length-1){hidx++;S=JSON.parse(JSON.stringify(hist[hidx]));r2();r3()}}
function ca(){if(confirm("确定清除所有？")){S={w:[],d:[],r:[],dm:[],f:[]};nid=1;hist=[[JSON.parse(JSON.stringify(S))]];hidx=0;r2();r3();tm("已清除")}}
function st(t){tl=t;ds=null;mp=[];document.querySelectorAll(".tl").forEach(function(e){e.classList.remove("a")});var el=document.querySelector(".tl[data-t=\\""+t+"\\\"]");if(el)el.classList.add("a");document.getElementById("ts").textContent=t;}
function tsn(){sn=!sn;tm(sn?"捕捉开":"捕捉关")}
function snap(x,y){if(!sn)return[x,y];var g=GRID*V.sc,b=[x,y],bd=10;for(var gx=Math.floor((x-V.ox)/g)*g+V.ox;gx<=x+g;gx+=g)for(var gy=Math.floor((y-V.oy)/g)*g+V.oy;gy<=y+g;gy+=g){var d=Math.hypot(gx-x,gy-y);if(d<bd){b=[gx,gy];bd=d}}for(var i=0;i<S.w.length;i++){var w=S.w[i];[[w.x1,w.y1],[w.x2,w.y2]].forEach(function(p){var d=Math.hypot(p[0]-x,p[1]-y);if(d<bd){b=[p[0],p[1]];bd=d}})}return b}
function rc(){var c=document.getElementById("c2d");if(!c)return;var p=c.parentElement;V.W=p.clientWidth||600;V.H=p.clientHeight||400;c.width=V.W*devicePixelRatio;c.height=V.H*devicePixelRatio;if(V.ox===0&&V.oy===0){V.ox=V.W/2;V.oy=V.H/2;V.sc=0.3}var c3=document.getElementById("c3d");if(!c3)return;var p3=c3.parentElement;c3.width=(p3.clientWidth||400)*devicePixelRatio;c3.height=(p3.clientHeight||300)*devicePixelRatio}
function r2(){var cv=document.getElementById("c2d");if(!cv||!cv.getContext)return;var cx=cv.getContext("2d");cx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);cx.fillStyle="#0d0d1a";cx.fillRect(0,0,V.W,V.H);cx.save();cx.translate(V.W/2,0);cx.scale(V.sc,V.sc);cx.translate(-V.ox,V.oy);if(GRID*V.sc>4){cx.strokeStyle="rgba(255,255,255,0.04)";cx.lineWidth=1;for(var gx=Math.floor(0/GRID)*GRID;gx<V.W/V.sc*2;gx+=GRID){cx.beginPath();cx.moveTo(gx,-V.H*2);cx.lineTo(gx,V.H*2);cx.stroke()}for(var gy=Math.floor(0/GRID)*GRID;gy<V.H/V.sc*2;gy+=GRID){cx.beginPath();cx.moveTo(-V.W*2,gy);cx.lineTo(V.W*2,gy);cx.stroke()}}for(var i=0;i<S.r.length;i++){var r=S.r[i];cx.strokeStyle="rgba(100,200,255,0.15)";cx.lineWidth=1;cx.setLineDash([5*V.sc,5*V.sc]);cx.strokeRect(r.x,r.y,r.w,r.d);cx.setLineDash([]);cx.fillStyle="rgba(100,200,255,0.06)";cx.fillRect(r.x,r.y,r.w,r.d);cx.fillStyle="rgba(255,255,255,0.2)";cx.font=Math.max(8,14*V.sc)+"px sans-serif";cx.textAlign="center";cx.fillText(r.n,r.x+r.w/2,r.y+r.d/2+4*V.sc)}for(var i=0;i<S.w.length;i++){var w=S.w[i],isSel=sel&&sel.t==="w"&&sel.i===i,th=w.th||(w.t==="\u5916"?240:150),nx=0,ny=0,dx=w.x2-w.x1,dy=w.y2-w.y1,ln=Math.hypot(dx,dy);if(ln>0){nx=-dy/ln*th/2;ny=dx/ln*th/2}cx.fillStyle=isSel?"rgba(102,126,234,0.3)":(w.t==="\u5916"?"rgba(74,124,255,0.2)":"rgba(106,156,255,0.15)");cx.beginPath();cx.moveTo(w.x1+nx,w.y1+ny);cx.lineTo(w.x2+nx,w.y2+ny);cx.lineTo(w.x2-nx,w.y2-ny);cx.lineTo(w.x1-nx,w.y1-ny);cx.closePath();cx.fill();cx.strokeStyle=isSel?"#667eea":(w.t==="\u5916"?"#4a7cff":"#6a9cff");cx.lineWidth=isSel?3:(w.t==="\u5916"?2.5:1.5);cx.beginPath();cx.moveTo(w.x1+nx,w.y1+ny);cx.lineTo(w.x2+nx,w.y2+ny);cx.stroke();cx.lineWidth=1;cx.beginPath();cx.moveTo(w.x1-nx,w.y1-ny);cx.lineTo(w.x2-nx,w.y2-ny);cx.stroke()}for(var i=0;i<S.d.length;i++){var d=S.d[i],isSel=sel&&sel.t==="d"&&sel.i===i;cx.strokeStyle=isSel?"#e74c3c":"#f0c040";cx.lineWidth=isSel?2.5:1.5;var r=d.w||80;cx.beginPath();cx.arc(d.x,d.y,r,0,Math.PI/2);cx.stroke();cx.beginPath();cx.moveTo(d.x,d.y);cx.lineTo(d.x,d.y+r);cx.stroke();cx.beginPath();cx.moveTo(d.x,d.y);cx.lineTo(d.x+r,d.y);cx.stroke()}for(var i=0;i<S.f.length;i++){var f=S.f[i],isSel=sel&&sel.t==="f"&&sel.i===i;cx.fillStyle=isSel?"rgba(102,126,234,0.25)":(f.c||"rgba(160,160,160,0.15)");cx.fillRect(f.x-f.w/2,f.y-f.d/2,f.w,f.d);cx.strokeStyle=isSel?"#667eea":"rgba(160,160,160,0.5)";cx.lineWidth=isSel?2:0.5;cx.strokeRect(f.x-f.w/2,f.y-f.d/2,f.w,f.d);cx.fillStyle=isSel?"#fff":"rgba(255,255,255,0.5)";cx.font=Math.max(7,9*V.sc)+"px sans-serif";cx.textAlign="center";cx.textBaseline="middle";cx.fillText(f.n,f.x,f.y)}if(ds){cx.strokeStyle="rgba(255,255,255,0.3)";cx.lineWidth=1;cx.setLineDash([4*V.sc,4*V.sc]);cx.beginPath();cx.moveTo(ds.x1,ds.y1);cx.lineTo(ds.x2,ds.y2);cx.stroke();cx.setLineDash([]);var dd=Math.hypot(ds.x2-ds.x1,ds.y2-ds.y1);cx.fillStyle="rgba(255,255,255,0.4)";cx.font=Math.max(8,10*V.sc)+"px monospace";cx.textAlign="left";cx.fillText(Math.round(dd)+"mm",ds.x2+5*V.sc,ds.y2-5*V.sc)}cx.restore();document.getElementById("oc").textContent=S.w.length+"w "+S.f.length+"f "+S.r.length+"r"}
function zf(){if(S.w.length===0){V.ox=V.W/2;V.oy=V.H/2;V.sc=1;r2();return}var minx=Infinity,maxx=-Infinity,miny=Infinity,maxy=-Infinity;for(var i=0;i<S.w.length;i++){var w=S.w[i];minx=Math.min(minx,w.x1,w.x2);maxx=Math.max(maxx,w.x1,w.x2);miny=Math.min(miny,w.y1,w.y2);maxy=Math.max(maxy,w.y1,w.y2)}var bw=maxx-minx+200,bh=maxy-miny+200;V.sc=Math.min(V.W/bw,V.H/bh)*0.8;V.ox=(minx+maxx)/2;V.oy=(miny+maxy)/2;r2()}
function r3(){var cv=document.getElementById("c3d");if(!cv||!cv.getContext)return;var cx3=cv.getContext("2d");var w=cv.clientWidth||400,h=cv.clientHeight||300;if(w<10)w=400;if(h<10)h=300;cx3.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);cx3.fillStyle="#0d0d1a";cx3.fillRect(0,0,w,h);var s3=0.12,cx=0,cy=0;if(S.w.length>0){for(var i=0;i<S.w.length;i++){cx+=S.w[i].x1+S.w[i].x2;cy+=S.w[i].y1+S.w[i].y2}cx/=(S.w.length*2);cy/=(S.w.length*2)}var ox3=function(x,y,z){return w/2+(x-cx-(y-cy))*s3};var oy3=function(x,y,z){return h/2+(x-cx+(y-cy))*s3*0.35-z*s3*0.5};for(var i=0;i<S.w.length;i++){(function(){var w=S.w[i],th=w.th||(w.t==="\u5916"?240:150),dx=w.x2-w.x1,dy=w.y2-w.y1,ln=Math.hypot(dx,dy);if(ln<1)return;var nx=-dy/ln*th/2,ny=dx/ln*th/2,hgt=2800,col=w.t==="\u5916"?"#4a7cff":"#6a9cff";cx3.fillStyle=col;cx3.globalAlpha=0.5;cx3.beginPath();cx3.moveTo(ox3(w.x1+nx,w.y1+ny,hgt),oy3(w.x1+nx,w.y1+ny,hgt));cx3.lineTo(ox3(w.x2+nx,w.y2+ny,hgt),oy3(w.x2+nx,w.y2+ny,hgt));cx3.lineTo(ox3(w.x2-nx,w.y2-ny,hgt),oy3(w.x2-nx,w.y2-ny,hgt));cx3.lineTo(ox3(w.x1-nx,w.y1-ny,hgt),oy3(w.x1-nx,w.y1-ny,hgt));cx3.closePath();cx3.fill();cx3.fillStyle=col;cx3.globalAlpha=0.25;cx3.beginPath();cx3.moveTo(ox3(w.x1+nx,w.y1+ny,0),oy3(w.x1+nx,w.y1+ny,0));cx3.lineTo(ox3(w.x2+nx,w.y2+ny,0),oy3(w.x2+nx,w.y2+ny,0));cx3.lineTo(ox3(w.x2+nx,w.y2+ny,hgt),oy3(w.x2+nx,w.y2+ny,hgt));cx3.lineTo(ox3(w.x1+nx,w.y1+ny,hgt),oy3(w.x1+nx,w.y1+ny,hgt));cx3.closePath();cx3.fill();cx3.fillStyle=col;cx3.globalAlpha=0.15;cx3.beginPath();cx3.moveTo(ox3(w.x2+nx,w.y2+ny,0),oy3(w.x2+nx,w.y2+ny,0));cx3.lineTo(ox3(w.x2-nx,w.y2-ny,0),oy3(w.x2-nx,w.y2-ny,0));cx3.lineTo(ox3(w.x2-nx,w.y2-ny,hgt),oy3(w.x2-nx,w.y2-ny,hgt));cx3.lineTo(ox3(w.x2+nx,w.y2+ny,hgt),oy3(w.x2+nx,w.y2+ny,hgt));cx3.closePath();cx3.fill()})();cx3.globalAlpha=1}for(var i=0;i<S.f.length;i++){(function(){var f=S.f[i],fh=f.h||800,col=f.c||"#666";cx3.fillStyle=col;cx3.globalAlpha=0.6;cx3.beginPath();cx3.moveTo(ox3(f.x-f.w/2,f.y-f.d/2,fh),oy3(f.x-f.w/2,f.y-f.d/2,fh));cx3.lineTo(ox3(f.x+f.w/2,f.y-f.d/2,fh),oy3(f.x+f.w/2,f.y-f.d/2,fh));cx3.lineTo(ox3(f.x+f.w/2,f.y+f.d/2,fh),oy3(f.x+f.w/2,f.y+f.d/2,fh));cx3.lineTo(ox3(f.x-f.w/2,f.y+f.d/2,fh),oy3(f.x-f.w/2,f.y+f.d/2,fh));cx3.closePath();cx3.fill();cx3.fillStyle=col;cx3.globalAlpha=0.4;cx3.beginPath();cx3.moveTo(ox3(f.x-f.w/2,f.y+f.d/2,0),oy3(f.x-f.w/2,f.y+f.d/2,0));cx3.lineTo(ox3(f.x+f.w/2,f.y+f.d/2,0),oy3(f.x+f.w/2,f.y+f.d/2,0));cx3.lineTo(ox3(f.x+f.w/2,f.y+f.d/2,fh),oy3(f.x+f.w/2,f.y+f.d/2,fh));cx3.lineTo(ox3(f.x-f.w/2,f.y+f.d/2,fh),oy3(f.x-f.w/2,f.y+f.d/2,fh));cx3.closePath();cx3.fill()})();cx3.globalAlpha=1}cx3.fillStyle="rgba(255,255,255,0.06)";cx3.font="11px sans-serif";cx3.textAlign="center";cx3.fillText("3D 视图 ("+S.w.length+"墙 "+S.f.length+"家具)",w/2,16)}
function loadDemo(){try{S=JSON.parse(DEMO_DATA);nid=100;sv();zf();setTimeout(function(){r3()},50);tm("Demo: "+S.r.length+"房间 "+S.f.length+"家具")}catch(e){tm("加载失败: "+e.message)}}
function svProj(){try{localStorage.setItem("cad_project",JSON.stringify(S));tm("已保存")}catch(e){tm("保存失败")}}
function ldProj(){try{var j=localStorage.getItem("cad_project");if(!j){tm("未找到保存的项目");return}S=JSON.parse(j);nid=100;hist=[[JSON.parse(JSON.stringify(S))]];hidx=0;sv();zf();r3();tm("已加载")}catch(e){tm("加载失败")}}
function exDxf(){var l=[];l.push("0","SECTION","2","HEADER","9","$ACADVER","1","AC1009","9","$INSUNITS","70","4","0","ENDSEC");l.push("0","SECTION","2","ENTITIES");for(var i=0;i<S.w.length;i++){var w=S.w[i],th=w.th||(w.t==="\u5916"?240:150),dx=w.x2-w.x1,dy=w.y2-w.y1,ln=Math.hypot(dx,dy),nx=0,ny=0;if(ln>0){nx=-dy/ln*th/2;ny=dx/ln*th/2}var ly=w.t==="\u5916"?"A-WALL-OUTER":"A-WALL-INNER",co=w.t==="\u5916"?"62\\n1":"62\\n6";l.push("0","LINE","8",ly,co,"10",String(w.x1+nx),"20",String(w.y1+ny),"11",String(w.x2+nx),"21",String(w.y2+ny));l.push("0","LINE","8",ly,co,"10",String(w.x1-nx),"20",String(w.y1-ny),"11",String(w.x2-nx),"21",String(w.y2-ny))}for(var i=0;i<S.f.length;i++){var f=S.f[i];l.push("0","LWPOLYLINE","8","A-FURN","62","5","90","4","10",String(f.x-f.w/2),"20",String(f.y-f.d/2),"10",String(f.x+f.w/2),"20",String(f.y-f.d/2),"10",String(f.x+f.w/2),"20",String(f.y+f.d/2),"10",String(f.x-f.w/2),"20",String(f.y+f.d/2))}l.push("0","ENDSEC","0","EOF");var b=new Blob([l.join("\\r\\n")],{type:"application/dxf"});var a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="cad_export.dxf";a.click();tm("DXF 导出 ("+S.w.length+"墙 "+S.f.length+"家具)")}
function exJson(){var j=JSON.stringify(S,null,2),b=new Blob([j],{type:"application/json"});var a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="cad_project.json";a.click();tm("JSON 导出 ("+Math.round(j.length/1024)+"KB)")}
function sFB(){var FN=["\u5e8a 1.8m","\u5e8a 1.5m","\u6c99\u53d1","\u8336\u51e0","\u9910\u684c","\u8863\u67dc","\u4e66\u684c","\u4e66\u67b6","\u7535\u89c6\u67dc","\u51b0\u7bb1","\u6d17\u8863\u673a","\u6253\u5370\u673a","\u6d17\u624b\u53f0","\u9a6c\u6876","\u6dcb\u6d74\u623f","\u7076\u53f0"];var FW=[2200,1500,2200,800,1600,1200,1200,900,1800,800,700,600,800,500,1000,1800];var FD=[2000,2000,850,600,900,600,600,350,500,700,700,600,550,700,800,600];var FC=["#8B4513","#D2691E","#DEB887","#C4A882","#D2B48C","#C4A882","#8B7355","#C4A882","#3C3C3C","#C0C0C0","#2C2C2C","#A0A0A0","#F5F5F5","#FFFFFF","#E0E0E0","#2d7d46"];var FH=[800,450,750,450,750,2000,750,2000,500,1800,850,850,850,400,2200,850];var b=document.getElementById("fbar");b.innerHTML="";for(var i=0;i<FN.length;i++){(function(n,w,d,c,h){var e=document.createElement("span");e.className="fc";e.textContent=n;e.onclick=function(){var x=0,y=0;if(S.w.length>0){var w2=S.w[0];x=(w2.x1+w2.x2)/2;y=(w2.y1+w2.y2)/2}S.f.push({id:nid++,n:n,x:x,y:y,w:w,d:d,c:c,h:h});sv();r2();r3();tm("添加 "+n)};b.appendChild(e)})(FN[i],FW[i],FD[i],FC[i],FH[i])}}
// Mouse events
(function(){var cv=document.getElementById("c2d"),isPan=false,panStart;if(!cv)return;cv.addEventListener("wheel",function(e){e.preventDefault();var zf=1.1;if(e.deltaY>0)zf=1/zf;V.sc*=zf;V.sc=Math.max(0.02,Math.min(5,V.sc));var r=cv.getBoundingClientRect();V.ox-=(e.clientX-r.left-V.W/2)/V.sc*(zf-1);V.oy+=(e.clientY-r.top-V.H/2)/V.sc*(zf-1);r2()});function gp(e){var r=cv.getBoundingClientRect();return[(e.clientX-r.left-V.W/2)/V.sc+V.ox,-(e.clientY-r.top-V.H/2)/V.sc+V.oy]}cv.addEventListener("mousedown",function(e){var p=gp(e);if(e.button===2||e.shiftKey){isPan=true;panStart={cx:e.clientX,cy:e.clientY,ox:V.ox,oy:V.oy};cv.style.cursor="grabbing";return}if(e.button!==0)return;if(tl==="select"){sel=null;for(var i=S.w.length-1;i>=0;i--){var w=S.w[i];if(Math.abs((w.x2-w.x1)*(w.y1-p[1])-(w.x1-p[0])*(w.y2-w.y1))/Math.hypot(w.x2-w.x1,w.y2-w.y1)<20/V.sc&&p[0]>=Math.min(w.x1,w.x2)-10&&p[0]<=Math.max(w.x1,w.x2)+10&&p[1]>=Math.min(w.y1,w.y2)-10&&p[1]<=Math.max(w.y1,w.y2)+10){sel={t:"w",i:i};break}}if(!sel)for(var i=S.f.length-1;i>=0;i--){var f=S.f[i];if(p[0]>=f.x-f.w/2&&p[0]<=f.x+f.w/2&&p[1]>=f.y-f.d/2&&p[1]<=f.y+f.d/2){sel={t:"f",i:i};break}}r2()}else if(tl==="wall"||tl==="dim"||tl==="room"){mp=[snap(p[0],p[1])]}});cv.addEventListener("mousemove",function(e){if(isPan&&panStart){V.ox=panStart.ox-(e.clientX-panStart.cx)/V.sc;V.oy=panStart.oy+(e.clientY-panStart.cy)/V.sc;r2();return}var p=gp(e);document.getElementById("cd").textContent=Math.round(p[0])+", "+Math.round(p[1]);if(mp.length===1){var s=snap(p[0],p[1]);ds={t:"l",x1:mp[0][0],y1:mp[0][1],x2:s[0],y2:s[1]};r2()}});cv.addEventListener("mouseup",function(e){if(isPan){isPan=false;cv.style.cursor="";return}if(mp.length!==1||!ds)return;var p=gp(e),s=snap(p[0],p[1]);if(tl==="wall"){if(Math.hypot(s[0]-mp[0][0],s[1]-mp[0][1])>10){var isOuter=confirm("外墙？")?"\u5916":"\u5185";S.w.push({id:nid++,x1:mp[0][0],y1:mp[0][1],x2:s[0],y2:s[1],t:isOuter,th:isOuter==="\u5916"?240:150});sv()}ds=null;mp=[];r2();r3()}else if(tl==="dim"){S.dm.push({id:nid++,x1:mp[0][0],y1:mp[0][1],x2:s[0],y2:s[1]});sv();mp=[];ds=null;r2()}else if(tl==="room"){var w=Math.abs(s[0]-mp[0][0]),d=Math.abs(s[1]-mp[0][1]);if(w>50&&d>50){var name=prompt("房间名称:","房间"+(S.r.length+1));if(name){S.r.push({n:name,x:Math.min(mp[0][0],s[0]),y:Math.min(mp[0][1],s[1]),w:w,d:d});sv()}}mp=[];ds=null;r2()}})});document.addEventListener("keydown",function(e){if(e.target.tagName==="INPUT"||e.target.tagName==="TEXTAREA")return;if((e.key==="Delete"||e.key==="Backspace")&&sel){if(sel.t==="w")S.w.splice(sel.i,1);else if(sel.t==="f")S.f.splice(sel.i,1);sel=null;sv();r2();r3();tm("已删除")}if(e.key==="Escape"){sel=null;ds=null;mp=[];r2()}if(e.ctrlKey&&e.key==="z"){undo();e.preventDefault()}if(e.ctrlKey&&e.key==="y"){redo();e.preventDefault()}if(e.key===" "){e.preventDefault();tsn()}});cv.addEventListener("contextmenu",function(e){e.preventDefault()})})();
setTimeout(function(){rc();sFB();window.addEventListener("resize",function(){rc();r3()});loadDemo()},100);
</script></body></html>
'''

A(JS)
A("")

with open("interior_cad.html", "w", encoding="utf-8") as f:
    f.writelines(parts)

sz = os.path.getsize("interior_cad.html")
print("interior_cad.html written: %d bytes (%.1f KB)" % (sz, sz/1024))
