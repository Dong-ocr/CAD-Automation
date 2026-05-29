#!/usr/bin/env python3
"""Phase 3+4: Master Showcase v3 with interactive floor plan, 3D iframe, and all features."""
import json, math, base64, os, re

d = json.load(open("demo_project.json","r",encoding="utf-8"))
walls = d["w"]; rooms = d["r"]; furniture = d["f"]; doors = d["d"]

total_area = sum(r["w"]*r["d"] for r in rooms) / 1e6
ext_walls = [w for w in walls if w["t"]=="外"]; int_walls = [w for w in walls if w["t"]=="内"]
ext_len = sum(math.hypot(w["x2"]-w["x1"],w["y2"]-w["y1"]) for w in ext_walls)
int_len = sum(math.hypot(w["x2"]-w["x1"],w["y2"]-w["y1"]) for w in int_walls)
room_list = sorted([(r["n"],round(r["w"]*r["d"]/1e6,1)) for r in rooms], key=lambda x:-x[1])

# Furniture by room
fbr = {}
for fi in furniture:
    fn = fi["n"]
    for r in rooms:
        if r["x"]<=fi["x"]<=r["x"]+r["w"] and r["y"]<=fi["y"]<=r["y"]+r["d"]:
            fbr.setdefault(r["n"],[]).append(fn); break
    else: fbr.setdefault("其他",[]).append(fn)

rc = ["#2B5F8A","#2D8A4E","#C0392B","#D4A017","#7D3C98","#1ABC9C","#E67E22","#5D6D7E","#34495E","#F39C12"]
rooms_html = ""
for i,(nm,area) in enumerate(room_list):
    its = fbr.get(nm,[])
    ft = "".join(f'<span class="ft">{x}</span>' for x in its) if its else '<span class="ft-dim">-</span>'
    rooms_html += f'<div class="rc" style="--a:{rc[i%10]}"><div class="rh"><span class="rd"></span><span class="rn">{nm}</span><span class="ra">{area}m\u00b2</span></div><div class="rb">{ft}</div></div>\n    '

# Furniture categories
cm = {}
for fi in furniture:
    n = fi["n"]
    if "床" in n: c="\u5e8a"
    elif "沙发" in n: c="\u6c99\u53d1"
    elif "桌" in n or "茶几" in n or "餐桌" in n: c="\u684c\u6905"
    elif "椅" in n: c="\u6905\u5b50"
    elif "柜" in n: c="\u67dc\u5b50"
    elif "盆" in n or "马桶" in n or "淋浴" in n or "洗手" in n or "挡水" in n: c="\u536b\u6d74"
    elif "冰" in n or "洗衣" in n or "拖把" in n or "电视" in n: c="\u7535\u5668"
    else: c="\u5176\u4ed6"
    cm[c] = cm.get(c,0)+1
cl = sorted(cm.items(), key=lambda x:-x[1])
cat_html = ""
for c,n in cl:
    p = round(n/len(furniture)*100)
    cat_html += f'<div class="cb"><span class="cl">{c}</span><div class="ct"><div class="cf" style="width:{p}%"></div></div><span class="cn">{n}</span></div>\n    '

# SVG inline
svg = open("output/floor_plan.svg","r",encoding="utf-8").read()

# Encode PNGs
def b64(path):
    with open(path,"rb") as f: return base64.b64encode(f.read()).decode()
fpng = b64("output/2d_floorplan.png")
ipng = b64("output/3d_isometric.png")

aft = "".join(f'<span class="ft" style="padding:5px 14px;font-size:11px">{f["n"]}</span>' for f in furniture)

# Wall data JSON for JS
wall_data = []
for w in walls[:12]:
    l = round(math.hypot(w["x2"]-w["x1"],w["y2"]-w["y1"])/1000,2)
    wall_data.append({"t":w["t"],"l":l})
wall_json = json.dumps(wall_data, ensure_ascii=False)

# Room data JSON for JS
room_data = []
for nm,area in room_list:
    its = fbr.get(nm,[])
    room_data.append({"n":nm,"a":area,"f":its})
room_json = json.dumps(room_data, ensure_ascii=False)

wx = round((max(w["x2"] for w in walls)-min(w["x1"] for w in walls))/1000)
wy = round((max(w["y2"] for w in walls)-min(w["y1"] for w in walls))/1000)

# Generate complete HTML
html = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>CAD 自动化制图 · 终极作品展 V3</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:#07070d;color:#e0e0e0;font-family:'Inter','Microsoft YaHei',system-ui,sans-serif;overflow-x:hidden}
::selection{background:#667eea;color:#fff}
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-track{background:#07070d}::-webkit-scrollbar-thumb{background:rgba(102,126,234,0.25);border-radius:3px}

nav{position:fixed;top:0;left:0;right:0;z-index:1000;height:48px;display:flex;justify-content:space-between;align-items:center;padding:0 20px;background:rgba(7,7,13,0.85);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,0.04);transition:.3s}
nav .logo{font-size:13px;font-weight:800;color:#fff;text-decoration:none;display:flex;align-items:center;gap:6px}
nav .logo span{color:#667eea}
nav .badge{font-size:8px;background:rgba(102,126,234,0.12);color:#667eea;padding:2px 6px;border-radius:4px;font-weight:700}
nav ul{display:flex;gap:2px;list-style:none}
nav ul a{padding:5px 12px;border-radius:5px;color:rgba(255,255,255,0.3);text-decoration:none;font-size:10px;font-weight:600;letter-spacing:.2px;transition:.2s}
nav ul a:hover{color:#fff;background:rgba(255,255,255,0.04)}
nav ul a.active{color:#667eea;background:rgba(102,126,234,0.08)}

.hero{min-height:100vh;display:flex;justify-content:center;align-items:center;position:relative;overflow:hidden;background:#07070d;flex-direction:column}
.hero canvas{position:absolute;inset:0}
.hero-g{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,0.015) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.015) 1px,transparent 1px);background-size:60px 60px;mask:radial-gradient(ellipse 60% 50% at center,black 30%,transparent 70%)}
.hero-glow{position:absolute;width:600px;height:600px;border-radius:50%;background:radial-gradient(circle,rgba(102,126,234,0.1),transparent 70%);top:20%;left:25%;animation:pulse 7s ease-in-out infinite;pointer-events:none}
@keyframes pulse{0%,100%{transform:scale(1);opacity:.5}50%{transform:scale(1.25);opacity:1}}
.hero-z{position:relative;z-index:2;text-align:center;padding:0 20px;max-width:900px}
.hero-b{display:inline-flex;align-items:center;gap:6px;padding:5px 16px;border-radius:100px;border:1px solid rgba(102,126,234,.15);background:rgba(102,126,234,.05);font-size:10px;font-weight:600;letter-spacing:2px;color:#667eea;margin-bottom:24px}
.hero-h1{font-size:clamp(2.2rem,7vw,6rem);font-weight:900;line-height:1.05;background:linear-gradient(135deg,#e8e8e8,#667eea 35%,#f0b840 65%,#e8e8e8);background-size:250% 250%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:gs 10s ease-in-out infinite;margin-bottom:10px}
@keyframes gs{0%,100%{background-position:0% 50%}33%{background-position:50% 50%}66%{background-position:100% 50%}}
.hero-p{font-size:clamp(.9rem,1.5vw,1.4rem);color:rgba(255,255,255,.3);font-weight:300;margin-bottom:32px;line-height:1.7}
.hero-st{display:flex;gap:36px;justify-content:center;flex-wrap:wrap;margin-bottom:36px}
.hs{text-align:center}
.hs-n{font-size:clamp(1.6rem,2.5vw,3rem);font-weight:900;color:#fff}
.hs-l{font-size:9px;color:rgba(255,255,255,.2);letter-spacing:1.5px;margin-top:4px}
.hero-cta{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.cta{padding:12px 28px;border-radius:8px;border:none;font-size:13px;font-weight:600;cursor:pointer;transition:.35s;text-decoration:none;display:inline-flex;align-items:center;gap:8px}
.cta-p{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;box-shadow:0 4px 20px rgba(102,126,234,.2)}
.cta-p:hover{transform:translateY(-2px);box-shadow:0 8px 32px rgba(102,126,234,.4)}
.cta-s{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.06);color:#999}
.cta-s:hover{background:rgba(255,255,255,.08);color:#fff}

.sec{padding:80px 20px;position:relative}
.sec-in{max-width:1300px;margin:0 auto}
.sh{text-align:center;margin-bottom:44px}
.st{display:inline-flex;align-items:center;gap:5px;padding:3px 12px;border-radius:100px;background:rgba(102,126,234,.06);border:1px solid rgba(102,126,234,.1);font-size:9px;font-weight:700;letter-spacing:1.5px;color:#667eea;margin-bottom:12px}
.s-title{font-size:clamp(1.4rem,2.5vw,2.2rem);font-weight:800;margin-bottom:6px;color:#f0f0f0}
.s-sub{color:rgba(255,255,255,.25);font-size:13px;font-weight:300}

.dg{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:28px}
.dc{background:linear-gradient(135deg,rgba(255,255,255,.025),rgba(255,255,255,.005));border:1px solid rgba(255,255,255,.04);border-radius:14px;padding:20px 14px;text-align:center;transition:.4s;position:relative;overflow:hidden}
.dc::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--a,#667eea),transparent);opacity:.4}
.dc:hover{transform:translateY(-4px);border-color:rgba(255,255,255,.08)}
.di{font-size:24px;margin-bottom:4px}
.dn{font-size:clamp(1.4rem,2vw,2.4rem);font-weight:900;color:#fff}
.dl{font-size:9px;color:rgba(255,255,255,.2);margin-top:3px}

.sm{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-top:10px}
.smc{background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.03);border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center}
.sml{font-size:10px;color:rgba(255,255,255,.25)}
.smv{font-size:11px;font-weight:600;color:rgba(255,255,255,.5)}

.vt{display:flex;gap:3px;margin-bottom:16px;justify-content:center;flex-wrap:wrap}
.vtb{padding:7px 18px;border-radius:6px;border:1px solid transparent;background:rgba(255,255,255,.02);color:rgba(255,255,255,.25);font-size:11px;font-weight:600;cursor:pointer;transition:.25s;font-family:inherit}
.vtb:hover{color:rgba(255,255,255,.5);background:rgba(255,255,255,.04)}
.vtb.a{border-color:rgba(102,126,234,.25);background:rgba(102,126,234,.08);color:#667eea}
.vp{display:none;border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,.04);background:#0d0d1a;cursor:pointer}
.vp.a{display:block}
.vp img,.vp svg{width:100%;height:auto;display:block}
.vi{display:none;position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.92);backdrop-filter:blur(20px);justify-content:center;align-items:center;padding:30px;cursor:zoom-out}
.vi.a{display:flex}
.vi img{max-width:95vw;max-height:90vh;border-radius:10px;box-shadow:0 20px 60px rgba(0,0,0,.5)}
.vi-c{position:absolute;top:20px;right:24px;color:rgba(255,255,255,.2);font-size:24px;cursor:pointer;background:none;border:none}
.vi-c:hover{color:#fff}

.if3d{width:100%;height:600px;border:none;border-radius:12px;display:block}

.rg{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}
.rc{background:linear-gradient(135deg,rgba(255,255,255,.02),rgba(255,255,255,.005));border:1px solid rgba(255,255,255,.04);border-radius:12px;padding:14px 16px;transition:.35s;cursor:pointer}
.rc:hover{border-color:var(--a);box-shadow:0 0 30px rgba(102,126,234,.04);transform:translateY(-2px)}
.rh{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.rd{width:8px;height:8px;border-radius:50%;background:var(--a);flex-shrink:0;box-shadow:0 0 8px var(--a)}
.rn{font-size:13px;font-weight:700;color:#f0f0f0}
.ra{margin-left:auto;font-size:10px;color:rgba(255,255,255,.2);font-weight:600}
.rb{display:flex;flex-wrap:wrap;gap:3px}
.ft{display:inline-block;padding:2px 8px;border-radius:5px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.02);font-size:9px;color:rgba(255,255,255,.35);transition:.2s}
.ft:hover{background:rgba(102,126,234,.08);border-color:rgba(102,126,234,.15);color:#667eea}
.ft-dim{font-size:9px;color:rgba(255,255,255,.1)}

.cs{max-width:600px;margin:0 auto}
.cb{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.cl{font-size:11px;color:rgba(255,255,255,.35);width:45px;flex-shrink:0;text-align:right;font-weight:500}
.ct{flex:1;height:8px;background:rgba(255,255,255,.03);border-radius:8px;overflow:hidden}
.cf{height:100%;background:linear-gradient(90deg,#667eea,#f0b840);border-radius:8px;width:0;transition:width 1.6s cubic-bezier(.25,.46,.45,.94)}
.cn{font-size:11px;color:rgba(255,255,255,.2);width:18px;text-align:right;font-weight:700}

.fc{display:flex;flex-wrap:wrap;gap:5px;justify-content:center;margin-top:30px}

.wg{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:6px}
.wr{display:flex;justify-content:space-between;align-items:center;padding:8px 14px;background:rgba(255,255,255,.015);border-radius:7px;border:1px solid rgba(255,255,255,.025);font-size:11px;transition:.2s}
.wr:hover{background:rgba(255,255,255,.03)}
.wt{color:rgba(255,255,255,.35)}
.wv{font-weight:600;color:rgba(255,255,255,.5)}

.sg{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:24px}
.sc{background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.03);border-radius:10px;padding:18px;transition:.3s}
.sc:hover{border-color:rgba(102,126,234,.1);background:rgba(102,126,234,.015)}
.sc h4{font-size:9px;color:rgba(255,255,255,.15);margin-bottom:8px;letter-spacing:1.5px}
.sc .sv{font-size:18px;font-weight:800;color:#f0f0f0}
.sc .sl{font-size:10px;color:rgba(255,255,255,.15);margin-top:2px}

.dl-section{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:16px}
.dl-btn{display:inline-flex;align-items:center;gap:6px;padding:8px 18px;border-radius:6px;background:rgba(102,126,234,.06);border:1px solid rgba(102,126,234,.15);color:#667eea;text-decoration:none;font-size:11px;font-weight:600;transition:.3s}
.dl-btn:hover{background:rgba(102,126,234,.12);color:#667eea}

.ftr{text-align:center;padding:40px 20px;border-top:1px solid rgba(255,255,255,.02);color:rgba(255,255,255,.08);font-size:10px;line-height:2;background:#05050a}
.ftr .br{font-size:12px;font-weight:700;color:rgba(255,255,255,.12);margin-bottom:4px}
.ftr .br span{color:#667eea}

.rv{opacity:0;transform:translateY(30px);transition:all .8s cubic-bezier(.25,.46,.45,.94)}
.rv.v{opacity:1;transform:translateY(0)}
@media(max-width:768px){.hero-st{gap:20px}.dg{grid-template-columns:repeat(3,1fr)}.rg{grid-template-columns:1fr}.wg{grid-template-columns:1fr}nav ul{display:none}.if3d{height:400px}}
@media(max-width:480px){.dg{grid-template-columns:repeat(2,1fr)}.sec{padding:50px 14px}}
</style>
</head>
<body>
""" + r"""
<nav><a href="#" class="logo">CAD<span>\u00b7</span>auto <span class="badge">V3</span></a>
<ul>
<li><a href="#dash">\U0001f4ca</a></li><li><a href="#viewer">\U0001f4d0</a></li><li><a href="#3d">\U0001f3d7</a></li><li><a href="#rooms">\U0001f3e0</a></li><li><a href="#furn">\U0001fa91</a></li><li><a href="#specs">\u2699</a></li>
</ul></nav>

<section class="hero">
<div class="hero-bg"><canvas id="pc"></canvas><div class="hero-g"></div><div class="hero-glow"></div></div>
<div class="hero-z">
<div class="hero-b">\u26a1 Python \u00b7 ezdxf \u00b7 Three.js</div>
<h1 class="hero-h1">CAD \u81ea\u52a8\u5316\u5236\u56fe</h1>
<p class="hero-p">\u4ece\u6570\u636e\u5230\u65bd\u5de5\u56fe\u7eb8\u7684\u5168\u81ea\u52a8\u7ba1\u7ebf<br>GB/T \u6807\u51c6\u56fe\u5c42 \u00b7 ACI \u989c\u8272 \u00b7 Three.js 3D \u4ea4\u4e92</p>
<div class="hero-st">
<div class="hs"><span class="hs-n" data-t="{t}">{t}</span><span class="hs-l">\u603b\u9762\u79ef m\u00b2</span></div>
<div class="hs"><span class="hs-n" data-t="{r}">{r}</span><span class="hs-l">\u623f\u95f4</span></div>
<div class="hs"><span class="hs-n" data-t="{fu}">{fu}</span><span class="hs-l">\u5bb6\u5177</span></div>
<div class="hs"><span class="hs-n" data-t="{wa}">{wa}</span><span class="hs-l">\u5899\u4f53</span></div>
</div>
<div class="hero-cta">
<a href="#dash" class="cta cta-p">\U0001f680 \u63a2\u7d22</a>
<a href="#viewer" class="cta cta-s">\U0001f4d0 \u56fe\u7eb8</a>
<a href="#3d" class="cta cta-s">\U0001f3d7 3D</a>
</div>
</div>
</section>
""".format(t=round(total_area), r=len(rooms), fu=len(furniture), wa=len(walls))

# Dashboard
html += r"""<section class="sec" id="dash"><div class="sec-in">
<div class="sh rv"><div class="st">\U0001f4ca 01</div><h2 class="s-title">\u9879\u76ee\u6570\u636e\u770b\u677f</h2><p class="s-sub">""" + str(len(rooms)) + r""" \u4e2a\u623f\u95f4 \u00b7 """ + str(len(walls)) + r""" \u6bb5\u5899\u4f53 \u00b7 """ + str(len(furniture)) + r""" \u4ef6\u5bb6\u5177</p></div>
<div class="dg">
""" + '\n'.join(f'<div class="dc rv" style="--a:{c}" data-d="{i+1}"><span class="di">{a}</span><span class="dn">{n}</span><span class="dl">{l}</span></div>' for i,(a,n,l,c) in enumerate([("\U0001f4d0",str(round(total_area,1)),"\u4f7f\u7528\u9762\u79ef","#667eea"),("\U0001f6aa",str(len(rooms)),"\u623f\u95f4\u6570\u91cf","#f0b840"),("\U0001f9f1",str(len(walls)),"\u5899\u4f53\u6bb5\u6570","#2ecc71"),("\U0001fa91",str(len(furniture)),"\u5bb6\u5177\u4ef6\u6570","#e74c3c"),("\U0001f6aa",str(len(doors)),"\u95e8\u6d1e\u6570\u91cf","#9b59b6"),("\U0001f4cf",str(round((ext_len+int_len)/1000,1)),"\u603b\u5899\u7ebf(m)","#1abc9c")])) + """
</div>
<div class="sm rv">
<div class="smc"><span class="sml">\U0001f9f1 \u5916\u5899</span><span class="smv">""" + str(len(ext_walls)) + """ \u6bb5 \u00b7 """ + str(round(ext_len/1000,1)) + """m \u00b7 240mm</span></div>
<div class="smc"><span class="sml">\u2b1c \u5185\u5899</span><span class="smv">""" + str(len(int_walls)) + """ \u6bb5 \u00b7 """ + str(round(int_len/1000,1)) + """m \u00b7 150mm</span></div>
<div class="smc"><span class="sml">\U0001f504 \u5f15\u64ce</span><span class="smv" style="color:#667eea">ezdxf 1.4.4 + Three.js</span></div>
</div>
</div></section>"""

# Viewer
html += r"""<section class="sec" id="viewer" style="background:rgba(255,255,255,.01)"><div class="sec-in">
<div class="sh rv"><div class="st">\U0001f4d0 02</div><h2 class="s-title">\u56fe\u7eb8\u67e5\u770b\u5668</h2><p class="s-sub">SVG \u77e2\u91cf\u56fe \u00b7 2D PNG \u00b7 3D PNG \u00b7 \u70b9\u51fb\u653e\u5927</p></div>
<div class="vt">
<button class="vtb a" data-t="svg">\U0001f4d0 SVG</button>
<button class="vtb" data-t="2d">\U0001f5bc 2D</button>
<button class="vtb" data-t="3d">\U0001f3d7 3D</button>
</div>
<div class="vp a" id="tv-svg" onclick="ol(this.innerHTML,'svg')"><div style="padding:12px;background:#0d0d1a">""" + svg + """</div></div>
<div class="vp" id="tv-2d" onclick="ol('<img src=\\'data:image/png;base64,""" + fpng + r"""\\'>','img')"><img src="data:image/png;base64,""" + fpng + r""""></div>
<div class="vp" id="tv-3d" onclick="ol('<img src=\\'data:image/png;base64,""" + ipng + r"""\\'>','img')"><img src="data:image/png;base64,""" + ipng + r""""></div>
</div></section>"""

# 3D Viewer iframe
html += r"""<section class="sec" id="3d" style="background:#05050a"><div class="sec-in">
<div class="sh rv"><div class="st">\U0001f3d7 03</div><h2 class="s-title">3D \u4ea4\u4e92\u573a\u666f</h2><p class="s-sub">Three.js \u5b9e\u65f6\u6e32\u67d3 \u00b7 \u62d6\u52a8\u65cb\u8f6c \u00b7 \u6eda\u8f6e\u7f29\u653e \u00b7 \u5bb6\u5177\u6807\u7b7e</p></div>
<iframe class="if3d" src="output/professional/3d_viewer.html" loading="lazy"></iframe>
</div></section>"""

# Rooms
html += r"""<section class="sec" id="rooms"><div class="sec-in">
<div class="sh rv"><div class="st">\U0001f3e0 04</div><h2 class="s-title">\u7a7a\u95f4\u5bfc\u89c8</h2><p class="s-sub">""" + str(len(rooms)) + """ \u4e2a\u623f\u95f4\u7684\u9762\u79ef\u4e0e\u5bb6\u5177\u914d\u7f6e</p></div>
<div class="rg">
""" + rooms_html + """</div>
</div></section>"""

# Furniture
html += r"""<section class="sec" id="furn" style="background:rgba(255,255,255,.01)"><div class="sec-in">
<div class="sh rv"><div class="st">\U0001fa91 05</div><h2 class="s-title">\u5bb6\u5177\u54c1\u7c7b\u5206\u5e03</h2><p class="s-sub">""" + str(len(furniture)) + """ \u4ef6\u5bb6\u5177 \u00b7 """ + str(len(cl)) + """ \u4e2a\u54c1\u7c7b</p></div>
<div class="cs">
""" + cat_html + """</div>
<div class="fc">
""" + aft + """</div>
</div></section>"""

# Specs + Downloads
html += r"""<section class="sec" id="specs"><div class="sec-in">
<div class="sh rv"><div class="st">\u2699\ufe0f 06</div><h2 class="s-title">\u6280\u672f\u53c2\u6570 & \u4e0b\u8f7d</h2><p class="s-sub">GB/T \u6807\u51c6\u5899\u4f53\u6570\u636e \u00b7 \u5de5\u7a0b\u5c3a\u5bf8 \u00b7 \u4e13\u4e1a DXF \u4e0b\u8f7d</p></div>
<div class="wg rv">
""" + "\n".join(f'<div class="wr"><span class="wt">{"\U0001f7e6 \u5916\u5899" if w["t"]=="\u5916" else "\u2b1c \u5185\u5899"}</span><span class="wv">{round(math.hypot(w["x2"]-w["x1"],w["y2"]-w["y1"])/1000,2)}m</span></div>' for w in walls[:8]) + """
</div>
<div class="sg rv">
<div class="sc"><h4>\U0001f4d0 \u5f00\u95f4</h4><div class="sv">""" + str(wx) + """ mm</div><div class="sl">\u4e1c\u897f\u65b9\u5411</div></div>
<div class="sc"><h4>\U0001f4cf \u8fdb\u6df1</h4><div class="sv">""" + str(wy) + """ mm</div><div class="sl">\u5357\u5317\u65b9\u5411</div></div>
<div class="sc"><h4>\U0001f3d7 \u5899\u9ad8</h4><div class="sv">2800 mm</div><div class="sl">\u6807\u51c6\u5c42\u9ad8</div></div>
<div class="sc"><h4>\U0001f504 \u751f\u6210\u5f15\u64ce</h4><div class="sv" style="font-size:13px;color:#667eea">ezdxf 1.4.4</div><div class="sl">R2010 \u00b7 GB/T \u56fe\u5c42</div></div>
</div>

<div class="dl-section rv">
<a href="output/professional/floor_plan_gbt.dxf" class="dl-btn" download>\U0001f4e5 \u4e0b\u8f7d DXF (GB/T \u6807\u51c6)</a>
<a href="output/professional/3d_viewer.html" class="dl-btn" target="_blank">\U0001f3d7 \u6253\u5f00 3D \u573a\u666f</a>
<a href="output/floor_plan.svg" class="dl-btn" download>\U0001f4e5 \u4e0b\u8f7d SVG</a>
</div>
</div></section>"""

# Lightbox + Footer
html += r"""<div class="vi" id="lb" onclick="cl()"><button class="vi-c" onclick="cl()">\u2715</button><div id="lbc"></div></div>

<footer class="ftr">
<div class="br">CAD<span>\u00b7</span>auto <span style="font-weight:400;font-size:9px;color:rgba(255,255,255,.05)">V3</span></div>
<p>\u5ca9\u6cca\u6e21\u6c34\u7535\u7ad9\u5de5\u7a0b \u00b7 \u5ba4\u5185\u8bbe\u8ba1\u4e00\u4f53\u5316</p>
<p style="font-size:9px;margin-top:4px">Python \u00b7 ezdxf 1.4.4 \u00b7 Three.js \u00b7 GB/T \u56fe\u5c42\u6807\u51c6</p>
</footer>

<script>
// Canvas particle
var c=document.getElementById("pc"),cx=c.getContext("2d"),W,H,P=[],mx,my;
function rs(){W=c.width=innerWidth;H=c.height=innerHeight;mx=W/2;my=H/2;}
rs();addEventListener("resize",rs);
function Pt(){this.x=Math.random()*W;this.y=Math.random()*H;this.vx=(Math.random()-.5)*.3;this.vy=(Math.random()-.5)*.3;this.r=Math.random()*1.5+.5;this.o=Math.random()*.1+.02}
Pt.prototype.up=function(){this.x+=this.vx;this.y+=this.vy;if(this.x<-10||this.x>W+10||this.y<-10||this.y>H+10){this.x=Math.random()*W;this.y=Math.random()*H}};
Pt.prototype.dr=function(){cx.beginPath();cx.arc(this.x,this.y,this.r,0,7);cx.fillStyle="rgba(255,255,255,"+this.o+")";cx.fill()};
for(var i=0;i<100;i++)P.push(new Pt());
onmousemove=function(e){mx=e.clientX;my=e.clientY};
function an(){cx.clearRect(0,0,W,H);P.forEach(function(p){p.up();p.dr()});for(var i=0;i<P.length;i++)for(var j=i+1;j<P.length;j++){var dx=P[i].x-P[j].x,dy=P[i].y-P[j].y,d=Math.sqrt(dx*dx+dy*dy);if(d<130){cx.beginPath();cx.moveTo(P[i].x,P[i].y);cx.lineTo(P[j].x,P[j].y);cx.strokeStyle="rgba(102,126,234,"+((1-d/130)*.07)+")";cx.stroke()}}requestAnimationFrame(an)}
an();

// Counters
var co=new IntersectionObserver(function(e){e.forEach(function(e){if(e.isIntersecting&&!e.target.dataset.c){var t=parseInt(e.target.dataset.t),st=performance.now();e.target.dataset.c=1;!function u(n){var p=Math.min(1,(n-st)/1800);e.target.textContent=Math.round(t*(p<.5?2*p*p:1-Math.pow(-2*p+2,2)/2));if(p<1)requestAnimationFrame(u)}(st)}})});
document.querySelectorAll(".hs-n[data-t]").forEach(function(e){co.observe(e)});

// Reveal
var ro=new IntersectionObserver(function(e){e.forEach(function(e){if(e.isIntersecting){e.target.classList.add("v")}})},{threshold:.1});
document.querySelectorAll(".rv").forEach(function(e){ro.observe(e)});

// Tab switch
document.querySelectorAll(".vtb").forEach(function(b){b.onclick=function(){document.querySelectorAll(".vtb").forEach(function(x){x.classList.remove("a")});document.querySelectorAll(".vp").forEach(function(x){x.classList.remove("a")});b.classList.add("a");document.getElementById("tv-"+b.dataset.t).classList.add("a")}});

// Lightbox
function ol(html,type){document.getElementById("lbc").innerHTML=html;document.getElementById("lb").classList.add("a");document.body.style.overflow="hidden"}
function cl(){document.getElementById("lb").classList.remove("a");document.body.style.overflow=""}
document.addEventListener("keydown",function(e){if(e.key==="Escape")cl()});

// Nav highlight
var ns=document.querySelectorAll("section[id]"),nl=document.querySelectorAll("nav ul a");
var no=new IntersectionObserver(function(e){e.forEach(function(e){if(e.isIntersecting){nl.forEach(function(a){a.classList.toggle("active",a.getAttribute("href")==="#"+e.target.id)})}})},{threshold:.3});
ns.forEach(function(s){no.observe(s)});

// Cat bar animation
var cbo=new IntersectionObserver(function(e){e.forEach(function(e){if(e.isIntersecting&&!e.target.dataset.a){e.target.dataset.a=1;var f=e.target.querySelector(".cf");if(f){var w=f.style.width;f.style.width=0;setTimeout(function(){f.style.width=w},200)}}})},{threshold:.3});
document.querySelectorAll(".cb").forEach(function(e){cbo.observe(e)});

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(function(a){a.onclick=function(e){e.preventDefault();var t=document.querySelector(a.getAttribute("href"));if(t)t.scrollIntoView({behavior:"smooth"})}});

console.log("%c CAD\u00b7auto V3 ","background:#667eea;color:#fff;padding:8px 16px;border-radius:6px;font-weight:bold;font-size:16px");
console.log("%c DXF: ezdxf 1.4.4 | 3D: Three.js | GB/T Layers | 16 walls, 34 furniture","color:#667eea;font-size:12px");
</script>
</body>
</html>"""

with open("showcase.html","w",encoding="utf-8") as f:
    f.write(html)
print("OK: showcase.html ("+str(len(html)//1024)+"KB)")
