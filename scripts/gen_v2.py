#!/usr/bin/env python3
"""Generate the ULTIMATE CAD showcase - v2 with advanced interactions."""
import json, math, base64

d = json.load(open('demo_project.json','r',encoding='utf-8'))
walls = d['w']; rooms = d['r']; furniture = d['f']; doors = d['d']

total_area = sum(r['w']*r['d'] for r in rooms) / 1e6
ext_walls = [w for w in walls if w['t']=='外']; int_walls = [w for w in walls if w['t']=='内']
ext_len = sum(math.hypot(w['x2']-w['x1'],w['y2']-w['y1']) for w in ext_walls)
int_len = sum(math.hypot(w['x2']-w['x1'],w['y2']-w['y1']) for w in int_walls)
room_list = sorted([(r['n'],round(r['w']*r['d']/1e6,1),r.get('type','')) for r in rooms], key=lambda x:-x[1])

fbr = {}
for fi in furniture:
    fn = fi['n']
    for r in rooms:
        rx, ry, rw, rd = r['x'], r['y'], r['w'], r['d']
        if rx <= fi['x'] <= rx+rw and ry <= fi['y'] <= ry+rd:
            fbr.setdefault(r['n'],[]).append(fn); break
    else: fbr.setdefault('其他',[]).append(fn)

rc = ['#2B5F8A','#2D8A4E','#C0392B','#D4A017','#7D3C98','#1ABC9C','#E67E22','#5D6D7E','#34495E','#F39C12']
rooms_html = ''
for i,(nm,area,typ) in enumerate(room_list):
    its = fbr.get(nm,[]); ft = ''.join(f'<span class="ft">{x}</span>' for x in its) if its else '<span class="ft-dim">-</span>'
    rooms_html += f'\n    <div class="room-card" style="--a:{rc[i%10]}" data-room="{nm}"><div class="rc-h"><span class="rc-dot"></span><span class="rc-name">{nm}</span><span class="rc-type">{typ}</span><span class="rc-area">{area} m\u00b2</span></div><div class="rc-b">{ft}</div></div>'

wall_js = []
for w in walls:
    l = round(math.hypot(w['x2']-w['x1'],w['y2']-w['y1'])/1000,2)
    wall_js.append({'t':w['t'],'l':l})

wall_html = ''
for w in walls[:8]:
    t = '\U0001f7e6 外墙' if w['t']=='外' else '\u2b1c 内墙'
    l = round(math.hypot(w['x2']-w['x1'],w['y2']-w['y1'])/1000,2)
    wall_html += f'\n    <div class="wr"><span class="wt">{t}</span><span class="wl">{l}m</span></div>'

cm = {}
for fi in furniture:
    n = fi['n']
    if '床' in n: c='床'
    elif '沙发' in n: c='沙发'
    elif '桌' in n or '茶几' in n or '餐桌' in n: c='桌椅'
    elif '椅' in n: c='椅子'
    elif '柜' in n: c='柜子'
    elif '盆' in n or '马桶' in n or '淋浴' in n or '洗手' in n or '挡水' in n: c='卫浴'
    elif '冰' in n or '洗衣' in n or '拖把' in n or '电视' in n: c='电器'
    else: c='其他'
    cm[c] = cm.get(c,0)+1
cl = sorted(cm.items(), key=lambda x:-x[1])
cat_html = ''
for c,n in cl:
    pct = round(n/len(furniture)*100)
    cat_html += f'\n    <div class="cat-bar"><span class="cat-label">{c}</span><div class="cat-track"><div class="cat-fill" style="width:{pct}%"></div></div><span class="cat-num">{n}</span></div>'

svg = open('output/floor_plan.svg','r',encoding='utf-8').read()
def b64(path):
    with open(path,'rb') as f: return base64.b64encode(f.read()).decode()
fpng = b64('output/2d_floorplan.png'); ipng = b64('output/3d_isometric.png')
aft = ''.join(f'<span class="ft" style="padding:5px 14px;font-size:11px">{f["n"]}</span>' for f in furniture)
wx = max(w['x2'] for w in walls) - min(w['x1'] for w in walls)
wy = max(w['y2'] for w in walls) - min(w['y1'] for w in walls)

# ===================== BUILD HTML =====================
css = '''
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:#07070d;color:#e0e0e0;font-family:'Inter','Microsoft YaHei',system-ui,sans-serif;overflow-x:hidden}
::selection{background:#667eea;color:#fff}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:#07070d}
::-webkit-scrollbar-thumb{background:rgba(102,126,234,0.3);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:rgba(102,126,234,0.5)}

/* ── NAV ── */
nav{position:fixed;top:0;left:0;right:0;z-index:1000;padding:0 24px;height:52px;display:flex;justify-content:space-between;align-items:center;background:rgba(7,7,13,0.85);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border-bottom:1px solid rgba(255,255,255,0.04);transition:all .4s}
nav.scrolled{background:rgba(7,7,13,0.95);box-shadow:0 4px 30px rgba(0,0,0,0.3)}
nav .logo{font-size:15px;font-weight:800;color:#fff;text-decoration:none;display:flex;align-items:center;gap:6px}
nav .logo .accent{color:#667eea}
nav .logo .badge{font-size:8px;background:rgba(102,126,234,0.15);color:#667eea;padding:2px 6px;border-radius:4px;font-weight:600;letter-spacing:0.5px}
nav ul{display:flex;gap:4px;list-style:none}
nav ul a{padding:6px 14px;border-radius:6px;color:rgba(255,255,255,0.35);text-decoration:none;font-size:11px;font-weight:600;letter-spacing:0.3px;transition:all .25s}
nav ul a:hover{color:#fff;background:rgba(255,255,255,0.04)}
nav ul a.active{color:#667eea;background:rgba(102,126,234,0.1)}

/* ── HERO ── */
.hero{min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;position:relative;overflow:hidden;background:#07070d}
.hero canvas{position:absolute;inset:0;width:100%;height:100%}
.hero-grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,0.015) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.015) 1px,transparent 1px);background-size:60px 60px;mask:radial-gradient(ellipse 60% 50% at center,black 30%,transparent 70%);-webkit-mask:radial-gradient(ellipse 60% 50% at center,black 30%,transparent 70%)}
.hero-glow{position:absolute;width:700px;height:700px;border-radius:50%;background:radial-gradient(circle,rgba(102,126,234,0.1),transparent 70%);top:15%;left:25%;animation:pulseSlow 7s ease-in-out infinite;pointer-events:none}
.hero-glow2{position:absolute;width:500px;height:500px;border-radius:50%;background:radial-gradient(circle,rgba(240,184,64,0.07),transparent 70%);bottom:5%;right:15%;animation:pulseSlow 9s ease-in-out infinite 2s;pointer-events:none}
.hero-glow3{position:absolute;width:400px;height:400px;border-radius:50%;background:radial-gradient(circle,rgba(231,76,60,0.05),transparent 70%);top:50%;left:60%;animation:pulseSlow 8s ease-in-out infinite 4s;pointer-events:none}
@keyframes pulseSlow{0%,100%{transform:scale(1);opacity:0.5}50%{transform:scale(1.3);opacity:1}}
.hero-content{position:relative;z-index:2;text-align:center;padding:0 20px;max-width:950px}
.hero-badge{display:inline-flex;align-items:center;gap:8px;padding:6px 18px;border-radius:100px;border:1px solid rgba(102,126,234,0.2);background:rgba(102,126,234,0.06);font-size:11px;font-weight:600;letter-spacing:2px;color:#667eea;margin-bottom:28px;backdrop-filter:blur(8px)}
.hero-badge .dot{width:6px;height:6px;border-radius:50%;background:#2ecc71;animation:pulseDot 2s ease-in-out infinite}
@keyframes pulseDot{0%,100%{opacity:1}50%{opacity:0.3}}
.hero-title{font-size:clamp(2.5rem,8vw,7rem);font-weight:900;line-height:1.05;background:linear-gradient(135deg,#e8e8e8 0%,#667eea 35%,#f0b840 65%,#e8e8e8 100%);background-size:250% 250%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:gradientShift 10s ease-in-out infinite;margin-bottom:12px}
@keyframes gradientShift{0%,100%{background-position:0% 50%}33%{background-position:50% 50%}66%{background-position:100% 50%}}
.hero-sub{font-size:clamp(1rem,2vw,1.5rem);color:rgba(255,255,255,0.35);font-weight:300;margin-bottom:36px;line-height:1.7}
.hero-stats{display:flex;gap:48px;justify-content:center;flex-wrap:wrap;margin-bottom:44px}
.hs-item{text-align:center;position:relative}
.hs-item::after{content:'';position:absolute;right:-24px;top:8px;bottom:8px;width:1px;background:rgba(255,255,255,0.06)}
.hs-item:last-child::after{display:none}
.hs-num{font-size:clamp(1.8rem,3vw,3.5rem);font-weight:900;color:#fff;display:block;line-height:1}
.hs-label{font-size:10px;color:rgba(255,255,255,0.25);letter-spacing:1.5px;text-transform:uppercase;margin-top:6px}
.hero-cta{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.cta-btn{padding:13px 34px;border-radius:10px;border:none;font-size:14px;font-weight:600;cursor:pointer;transition:all .35s;text-decoration:none;display:inline-flex;align-items:center;gap:8px;position:relative;overflow:hidden}
.cta-primary{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;box-shadow:0 4px 24px rgba(102,126,234,0.25)}
.cta-primary:hover{transform:translateY(-3px);box-shadow:0 8px 40px rgba(102,126,234,0.45)}
.cta-secondary{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);color:#999}
.cta-secondary:hover{background:rgba(255,255,255,0.08);color:#fff;border-color:rgba(255,255,255,0.15)}
.scroll-hint{position:absolute;bottom:28px;left:50%;transform:translateX(-50%);z-index:2;display:flex;flex-direction:column;align-items:center;gap:6px;color:rgba(255,255,255,0.15);font-size:9px;letter-spacing:2px;animation:bounceDown 2.5s ease-in-out infinite;cursor:pointer}
@keyframes bounceDown{0%,100%{opacity:0.4;transform:translateX(-50%) translateY(0)}50%{opacity:1;transform:translateX(-50%) translateY(8px)}}

/* ── SECTION COMMON ── */
.section{padding:100px 20px;position:relative}
.section-inner{max-width:1300px;margin:0 auto}
.section-header{text-align:center;margin-bottom:56px}
.section-tag{display:inline-flex;align-items:center;gap:6px;padding:4px 14px;border-radius:100px;background:rgba(102,126,234,0.08);border:1px solid rgba(102,126,234,0.12);font-size:10px;font-weight:700;letter-spacing:1.5px;color:#667eea;margin-bottom:14px}
.section-title{font-size:clamp(1.6rem,3vw,2.6rem);font-weight:800;margin-bottom:8px;color:#f0f0f0}
.section-sub{color:rgba(255,255,255,0.3);font-size:14px;font-weight:300;max-width:600px;margin:0 auto}

/* ── DASHBOARD ── */
#dashboard{background:linear-gradient(180deg,#07070d 0%,#0a0a18 100%)}
.dash-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin-bottom:32px}
.dash-card{background:linear-gradient(135deg,rgba(255,255,255,0.025),rgba(255,255,255,0.008));border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:22px 16px;text-align:center;backdrop-filter:blur(12px);transition:all .4s;position:relative;overflow:hidden}
.dash-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--accent,#667eea),transparent);opacity:0.4;transition:opacity .3s}
.dash-card:hover{transform:translateY(-6px);border-color:rgba(255,255,255,0.1);box-shadow:0 16px 48px rgba(0,0,0,0.4)}
.dash-card:hover::before{opacity:0.8}
.dash-icon{font-size:26px;margin-bottom:6px;display:block}
.dash-num{font-size:clamp(1.6rem,2.5vw,2.8rem);font-weight:900;color:#fff;display:block;line-height:1.2}
.dash-label{font-size:10px;color:rgba(255,255,255,0.25);letter-spacing:0.5px;margin-top:4px}
.spec-mini{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.spec-mini-card{background:rgba(255,255,255,0.015);border:1px solid rgba(255,255,255,0.04);border-radius:10px;padding:14px 18px;display:flex;justify-content:space-between;align-items:center}
.spec-mini-label{font-size:11px;color:rgba(255,255,255,0.3)}
.spec-mini-val{font-size:12px;font-weight:600;color:rgba(255,255,255,0.6)}

/* ── VIEWER ── */
#viewer{background:linear-gradient(180deg,#0a0a18 0%,#07070d 100%)}
.viewer-tabs{display:flex;gap:3px;margin-bottom:20px;justify-content:center}
.vt-btn{padding:9px 22px;border-radius:8px;border:1px solid transparent;background:rgba(255,255,255,0.02);color:rgba(255,255,255,0.3);font-size:12px;font-weight:600;cursor:pointer;transition:all .3s;font-family:inherit}
.vt-btn:hover{color:rgba(255,255,255,0.6);background:rgba(255,255,255,0.04)}
.vt-btn.active{border-color:rgba(102,126,234,0.3);background:rgba(102,126,234,0.1);color:#667eea;box-shadow:0 0 20px rgba(102,126,234,0.05)}
.viewer-panel{display:none;border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,0.05);background:#0d0d1a;cursor:pointer;transition:all .3s}
.viewer-panel:hover{border-color:rgba(102,126,234,0.15)}
.viewer-panel.active{display:block}
.viewer-panel svg{width:100%;height:auto;display:block}
.viewer-panel img{width:100%;height:auto;display:block}

/* ── LIGHTBOX ── */
.lightbox{display:none;position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.92);backdrop-filter:blur(20px);justify-content:center;align-items:center;padding:40px;cursor:zoom-out}
.lightbox.show{display:flex}
.lightbox img{max-width:95vw;max-height:90vh;border-radius:12px;box-shadow:0 20px 80px rgba(0,0,0,0.6)}
.lightbox-close{position:absolute;top:24px;right:28px;color:rgba(255,255,255,0.3);font-size:28px;cursor:pointer;transition:color .2s;background:none;border:none;font-family:inherit}
.lightbox-close:hover{color:#fff}

/* ── ROOMS ── */
.room-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.room-card{background:linear-gradient(135deg,rgba(255,255,255,0.02),rgba(255,255,255,0.005));border:1px solid rgba(255,255,255,0.05);border-radius:14px;padding:16px 18px;transition:all .35s;cursor:pointer}
.room-card:hover{border-color:var(--a);box-shadow:0 0 40px rgba(102,126,234,0.06);transform:translateY(-2px)}
.rc-h{display:flex;align-items:center;gap:8px;margin-bottom:10px}
.rc-dot{width:8px;height:8px;border-radius:50%;background:var(--a);flex-shrink:0;box-shadow:0 0 8px var(--a)}
.rc-name{font-size:14px;font-weight:700;color:#f0f0f0}
.rc-type{font-size:9px;color:rgba(255,255,255,0.2);background:rgba(255,255,255,0.04);padding:1px 8px;border-radius:4px}
.rc-area{margin-left:auto;font-size:11px;color:rgba(255,255,255,0.25);font-weight:600}
.rc-b{display:flex;flex-wrap:wrap;gap:4px}
.ft{display:inline-block;padding:3px 10px;border-radius:6px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.03);font-size:10px;color:rgba(255,255,255,0.4);transition:all .2s}
.ft:hover{background:rgba(102,126,234,0.1);border-color:rgba(102,126,234,0.2);color:#667eea}
.ft-dim{font-size:10px;color:rgba(255,255,255,0.1)}

/* ── FURNITURE ── */
.cat-section{max-width:650px;margin:0 auto}
.cat-bar{display:flex;align-items:center;gap:14px;margin-bottom:12px;opacity:0;transform:translateX(-15px);transition:all .8s ease}
.cat-bar.visible{opacity:1;transform:translateX(0)}
.cat-label{font-size:12px;color:rgba(255,255,255,0.4);width:50px;flex-shrink:0;text-align:right;font-weight:500}
.cat-track{flex:1;height:10px;background:rgba(255,255,255,0.03);border-radius:10px;overflow:hidden}
.cat-fill{height:100%;background:linear-gradient(90deg,#667eea,#f0b840);border-radius:10px;width:0;transition:width 1.8s cubic-bezier(0.25,0.46,0.45,0.94)}
.cat-num{font-size:12px;color:rgba(255,255,255,0.25);width:20px;text-align:right;font-weight:700}
.furn-cloud{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin-top:36px}

/* ── SPECS ── */
.wall-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px}
.wr{display:flex;justify-content:space-between;align-items:center;padding:10px 16px;background:rgba(255,255,255,0.015);border-radius:8px;border:1px solid rgba(255,255,255,0.03);font-size:12px;transition:all .2s}
.wr:hover{background:rgba(255,255,255,0.03)}
.wt{color:rgba(255,255,255,0.4)}
.wl{font-weight:600;color:rgba(255,255,255,0.6)}
.spec-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-top:28px}
.spec-c{background:rgba(255,255,255,0.015);border:1px solid rgba(255,255,255,0.04);border-radius:12px;padding:20px;transition:all .3s}
.spec-c:hover{border-color:rgba(102,126,234,0.12);background:rgba(102,126,234,0.02)}
.spec-c h4{font-size:10px;color:rgba(255,255,255,0.2);margin-bottom:10px;letter-spacing:1.5px;text-transform:uppercase}
.spec-c .sv{font-size:20px;font-weight:800;color:#f0f0f0}
.spec-c .sl{font-size:11px;color:rgba(255,255,255,0.2);margin-top:3px}

/* ── FOOTER ── */
footer{text-align:center;padding:50px 20px;border-top:1px solid rgba(255,255,255,0.03);color:rgba(255,255,255,0.1);font-size:11px;line-height:2;background:#05050a}
footer .brand{font-size:13px;font-weight:700;color:rgba(255,255,255,0.15);margin-bottom:4px}
footer .brand span{color:#667eea}
footer .links{display:flex;gap:20px;justify-content:center;margin-top:8px}
footer .links a{color:rgba(255,255,255,0.15);text-decoration:none;transition:color .2s;font-size:10px}
footer .links a:hover{color:#667eea}

/* ── ANIMATIONS ── */
.reveal{opacity:0;transform:translateY(40px);transition:all .9s cubic-bezier(0.25,0.46,0.45,0.94)}
.reveal.visible{opacity:1;transform:translateY(0)}
.reveal-left{opacity:0;transform:translateX(-40px);transition:all .9s cubic-bezier(0.25,0.46,0.45,0.94)}
.reveal-left.visible{opacity:1;transform:translateX(0)}
.reveal-right{opacity:0;transform:translateX(40px);transition:all .9s cubic-bezier(0.25,0.46,0.45,0.94)}
.reveal-right.visible{opacity:1;transform:translateX(0)}
[data-delay="1"]{transition-delay:.1s}[data-delay="2"]{transition-delay:.2s}[data-delay="3"]{transition-delay:.3s}
[data-delay="4"]{transition-delay:.4s}[data-delay="5"]{transition-delay:.5s}[data-delay="6"]{transition-delay:.6s}

/* ── RESPONSIVE ── */
@media(max-width:768px){.hero-stats{gap:24px}.hs-item::after{display:none}.dash-grid{grid-template-columns:repeat(3,1fr)}.room-grid{grid-template-columns:1fr}.wall-grid{grid-template-columns:1fr}nav ul{display:none}.spec-grid{grid-template-columns:1fr}}
@media(max-width:480px){.dash-grid{grid-template-columns:repeat(2,1fr)}.hero-stats{gap:16px;margin-bottom:28px}.section{padding:60px 16px}}
'''

h = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width,initial-scale=1.0">\n<title>CAD 自动化制图 · 终极作品展</title>\n'
h += '<style>' + css + '</style>\n</head>\n<body>\n'

# ── NAV ──
h += '<nav><a href="#" class="logo">CAD<span class="accent">\u00b7</span>auto <span class="badge">PRO</span></a><ul>'
for s in [('dashboard','\U0001f4ca 数据'),('viewer','\U0001f4d0 平面'),('rooms','\U0001f3e0 房间'),('furniture','\U0001fa91 家具'),('specs','\u2699 技术')]:
    h += f'<li><a href="#{s[0]}">{s[1]}</a></li>'
h += '</ul></nav>\n'

# ── HERO ──
h += '<section class="hero" id="hero"><div class="hero-bg"><canvas id="c"></canvas><div class="hero-grid"></div><div class="hero-glow"></div><div class="hero-glow2"></div><div class="hero-glow3"></div></div>'
h += '<div class="hero-content"><div class="hero-badge"><span class="dot"></span>Python \u00b7 SVG \u00b7 DXF \u00b7 Three.js</div>'
h += '<h1 class="hero-title">CAD \u81ea\u52a8\u5316\u5236\u56fe</h1>'
h += '<p class="hero-sub">\u4ece\u539f\u59cb\u6570\u636e\u5230\u65bd\u5de5\u56fe\u7eb8\u7684\u5168\u81ea\u52a8\u7ba1\u7ebf<br>\u5ba4\u5185\u8bbe\u8ba1 \u00b7 \u5de5\u7a0b\u56fe\u7eb8 \u00b7 3D \u5efa\u6a21 \u00b7 \u7edf\u4e00\u5f15\u64ce</p>'
h += '<div class="hero-stats"><div class="hs-item"><span class="hs-num" data-target="' + str(round(total_area)) + '">0</span><span class="hs-label">总面积 m\u00b2</span></div>'
h += '<div class="hs-item"><span class="hs-num" data-target="' + str(len(rooms)) + '">0</span><span class="hs-label">房间</span></div>'
h += '<div class="hs-item"><span class="hs-num" data-target="' + str(len(furniture)) + '">0</span><span class="hs-label">家具</span></div>'
h += '<div class="hs-item"><span class="hs-num" data-target="' + str(len(walls)) + '">0</span><span class="hs-label">墙体</span></div></div>'
h += '<div class="hero-cta"><a href="#dashboard" class="cta-btn cta-primary">\U0001f680 探索作品</a><a href="#viewer" class="cta-btn cta-secondary">\U0001f4d0 查看图纸</a></div></div>'
h += '<div class="scroll-hint" onclick="document.getElementById(\'dashboard\').scrollIntoView({behavior:\'smooth\'})"><svg width="22" height="30" viewBox="0 0 22 30" fill="none"><rect x="1" y="1" width="20" height="28" rx="10" stroke="currentColor" stroke-width="2" opacity="0.3"/><circle cx="11" cy="10" r="3" fill="currentColor" opacity="0.5"><animate attributeName="cy" values="10;18;10" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.5;0.2;0.5" dur="2s" repeatCount="indefinite"/></circle></svg></div></section>\n'

# ── DASHBOARD ──
h += '<section class="section" id="dashboard"><div class="section-inner">'
h += '<div class="section-header reveal"><div class="section-tag">\U0001f4ca 01</div><h2 class="section-title">项目数据看板</h2><p class="section-sub">基于 ' + str(len(rooms)) + ' 个房间、' + str(len(walls)) + ' 段墙体、' + str(len(furniture)) + ' 件家具的完整室内设计</p></div>'
h += '<div class="dash-grid">'
for icon, num, label, color in [
    ('\U0001f4d0', str(round(total_area,1)), '使用面积 m\u00b2', '#667eea'),
    ('\U0001f6aa', str(len(rooms)), '房间数量', '#f0b840'),
    ('\U0001f9f1', str(len(walls)), '墙体段数', '#2ecc71'),
    ('\U0001fa91', str(len(furniture)), '家具件数', '#e74c3c'),
    ('\U0001f6aa', str(len(doors)), '门洞数量', '#9b59b6'),
    ('\U0001f4cf', str(round((ext_len+int_len)/1000,1)), '总墙线 (m)', '#1abc9c'),
]:
    h += f'<div class="dash-card reveal" style="--accent:{color}" data-delay="{dash_items.index((icon,num,label,color))%6+1 if False else 1}"><span class="dash-icon">{icon}</span><span class="dash-num">{num}</span><span class="dash-label">{label}</span></div>'
h = h.replace('dash_items.index((icon,num,label,color))%6+1 if False else 1', '1')  # fix placeholder

# Fix the delayed dash cards properly
dash_html_fixed = ''
for idx,(icon,num,label,color) in enumerate([
    ('\U0001f4d0', str(round(total_area,1)), '使用面积 m\u00b2', '#667eea'),
    ('\U0001f6aa', str(len(rooms)), '房间数量', '#f0b840'),
    ('\U0001f9f1', str(len(walls)), '墙体段数', '#2ecc71'),
    ('\U0001fa91', str(len(furniture)), '家具件数', '#e74c3c'),
    ('\U0001f6aa', str(len(doors)), '门洞数量', '#9b59b6'),
    ('\U0001f4cf', str(round((ext_len+int_len)/1000,1)), '总墙线 (m)', '#1abc9c'),
]):
    dash_html_fixed += f'<div class="dash-card reveal" style="--accent:{color}" data-delay="{idx+1}"><span class="dash-icon">{icon}</span><span class="dash-num">{num}</span><span class="dash-label">{label}</span></div>\n    '

h = h[:h.index('<div class="dash-grid">') + len('<div class="dash-grid">') + 1] + '\n    ' + dash_html_fixed + '\n  </div>'
# Actually the string replacement is fragile. Let me find a cleaner way.
# The issue is I used a for loop before with a broken ref. Let me just rebuild the whole section.

# Rebuild cleanly - find the start of dash-grid and replace until its closing
import re
pattern = r'<div class="dash-grid">.*?</div>\s*</div>'
h = re.sub(pattern, '<div class="dash-grid">\n    ' + dash_html_fixed + '\n  </div>\n  </div>', h, count=1, flags=re.DOTALL)

h += '\n<div class="spec-mini reveal"><div class="spec-mini-card"><span class="spec-mini-label">外墙</span><span class="spec-mini-val">厚度 240mm \u00b7 ' + str(len(ext_walls)) + ' 段 \u00b7 ' + str(round(ext_len/1000,1)) + 'm</span></div>'
h += '<div class="spec-mini-card"><span class="spec-mini-label">内墙</span><span class="spec-mini-val">厚度 150mm \u00b7 ' + str(len(int_walls)) + ' 段 \u00b7 ' + str(round(int_len/1000,1)) + 'm</span></div></div>\n'
h += '</div></section>\n'

# ── VIEWER ──
h += '<section class="section" id="viewer"><div class="section-inner">'
h += '<div class="section-header reveal"><div class="section-tag">\U0001f4d0 02</div><h2 class="section-title">图纸查看器</h2><p class="section-sub">SVG 矢量平面图 \u00b7 2D 渲染 \u00b7 3D 等轴测 \u00b7 点击放大</p></div>'
h += '<div class="viewer-tabs"><button class="vt-btn active" data-tab="svg">\U0001f4d0 平面 SVG</button><button class="vt-btn" data-tab="d2">\U0001f5bc 2D 渲染</button><button class="vt-btn" data-tab="d3">\U0001f3d7 3D 等轴测</button></div>'
h += '<div class="viewer-panel active" id="tab-svg" onclick="openLightbox(this.innerHTML,\'svg\')"><div class="svg-wrap">' + svg + '</div></div>'
h += '<div class="viewer-panel" id="tab-d2" onclick="openLightbox(\'data:image/png;base64,' + fpng + '\',\'img\')"><img src="data:image/png;base64,' + fpng + '" alt="2D Floor Plan" loading="lazy"></div>'
h += '<div class="viewer-panel" id="tab-d3" onclick="openLightbox(\'data:image/png;base64,' + ipng + '\',\'img\')"><img src="data:image/png;base64,' + ipng + '" alt="3D Isometric" loading="lazy"></div>'
h += '</div></section>\n'

# ── ROOMS ──
h += '<section class="section" id="rooms"><div class="section-inner">'
h += '<div class="section-header reveal"><div class="section-tag">\U0001f3e0 03</div><h2 class="section-title">空间导览</h2><p class="section-sub">每个房间的面积与家具配置 \u00b7 悬停高亮平面图对应区域</p></div>'
h += '<div class="room-grid">' + rooms_html + '\n</div></div></section>\n'

# ── FURNITURE ──
h += '<section class="section" id="furniture"><div class="section-inner">'
h += '<div class="section-header reveal"><div class="section-tag">\U0001fa91 04</div><h2 class="section-title">家具品类分布</h2><p class="section-sub">共 ' + str(len(furniture)) + ' 件家具，覆盖 ' + str(len(cl)) + ' 个品类</p></div>'
h += '<div class="cat-section">' + cat_html + '\n</div>'
h += '<div class="furn-cloud">' + aft + '</div></div></section>\n'

# ── SPECS ──
h += '<section class="section" id="specs"><div class="section-inner">'
h += '<div class="section-header reveal"><div class="section-tag">\u2699\ufe0f 05</div><h2 class="section-title">技术参数</h2><p class="section-sub">墙体结构 \u00b7 工程尺寸 \u00b7 生成引擎规格</p></div>'
h += '<div class="wall-grid reveal">' + wall_html + '\n</div>'
h += '<div class="spec-grid">'
for spec in [
    ('\U0001f4d0 开间', str(round(wx/1000)) + ' mm', '东西方向'),
    ('\U0001f4cf 进深', str(round(wy/1000)) + ' mm', '南北方向'),
    ('\U0001f3d7 标准层高', '2800 mm', '墙高统一'),
    ('\U0001f504 生成引擎', 'cad_toolbox_v8', 'Python \u00b7 DXF \u00b7 SVG \u00b7 STEP \u00b7 IFC'),
]:
    h += f'<div class="spec-c reveal"><h4>{spec[0]}</h4><div class="sv">{spec[1]}</div><div class="sl">{spec[2]}</div></div>'
h += '</div></div></section>\n'

# ── LIGHTBOX ──
h += '<div class="lightbox" id="lb" onclick="closeLightbox()"><button class="lightbox-close" onclick="closeLightbox()">\u2715</button><div id="lb-content"></div></div>\n'

# ── FOOTER ──
h += '<footer><div class="brand">CAD<span>\u00b7</span>auto</div>'
h += '<p>\u5ca9\u6cca\u6e21\u6c34\u7535\u7ad9\u5de5\u7a0b \u00b7 \u5ba4\u5185\u8bbe\u8ba1\u4e00\u4f53\u5316</p>'
h += '<p style="font-size:10px;color:rgba(255,255,255,0.08);margin-top:8px">Generated by Python \u00b7 Three.js \u00b7 SVG Engine</p></footer>\n'

# ── JAVASCRIPT ──
h += '''<script>
// ── Hero Canvas: Particle Network ──
const c=document.getElementById('c'),cx=c.getContext('2d');
let W,H,parts=[],mx,my;
function resize(){W=c.width=innerWidth;H=c.height=innerHeight;mx=W/2;my=H/2}
resize();addEventListener('resize',resize);
class P{
  constructor(){this.reset()}
  reset(){this.x=Math.random()*W;this.y=Math.random()*H;this.vx=(Math.random()-.5)*.4;this.vy=(Math.random()-.5)*.4;this.r=Math.random()*1.8+0.8;this.o=Math.random()*.12+.04}
  update(){this.x+=this.vx;this.y+=this.vy;if(this.x<-20||this.x>W+20||this.y<-20||this.y>H+20)this.reset()}
  draw(){cx.beginPath();cx.arc(this.x,this.y,this.r,0,7);cx.fillStyle='rgba(255,255,255,'+this.o+')';cx.fill()}
}
for(let i=0;i<150;i++)parts.push(new P());
document.addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY});
function drawConnections(){
  for(let i=0;i<parts.length;i++){
    for(let j=i+1;j<parts.length;j++){
      const dx=parts[i].x-parts[j].x,dy=parts[i].y-parts[j].y,d=Math.sqrt(dx*dx+dy*dy);
      if(d<140){cx.beginPath();cx.moveTo(parts[i].x,parts[i].y);cx.lineTo(parts[j].x,parts[j].y);cx.strokeStyle='rgba(102,126,234,'+((1-d/140)*.08)+')';cx.stroke()}
    }
    const dx=parts[i].x-mx,dy=parts[i].y-my,d=Math.sqrt(dx*dx+dy*dy);
    if(d<180){cx.beginPath();cx.moveTo(parts[i].x,parts[i].y);cx.lineTo(mx,my);cx.strokeStyle='rgba(102,126,234,'+((1-d/180)*.06)+')';cx.stroke()}
  }
}
function animate(){cx.clearRect(0,0,W,H);parts.forEach(p=>{p.update();p.draw()});drawConnections();requestAnimationFrame(animate)}
animate();

// ── Scroll-based Nav Highlight ──
const sections=document.querySelectorAll('section[id]'),navLinks=document.querySelectorAll('nav ul a');
const nav=document.querySelector('nav');
const obsOptions={threshold:.3,rootMargin:'-80px 0px 0px 0px'};
const obs=new IntersectionObserver(entries=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      navLinks.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+e.target.id));
      nav.classList.toggle('scrolled',e.target.id!=='hero');
    }
  });
},obsOptions);
sections.forEach(s=>obs.observe(s));

// ── Reveal Animations ──
const revealObs=new IntersectionObserver(entries=>{
  entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');}});
},{threshold:.1});
document.querySelectorAll('.reveal,.reveal-left,.reveal-right,.cat-bar').forEach(el=>revealObs.observe(el));

// ── Animated Counters ──
const counterObs=new IntersectionObserver(entries=>{
  entries.forEach(e=>{
    if(e.isIntersecting&&!e.target.dataset.counted){
      e.target.dataset.counted='1';
      const target=parseInt(e.target.dataset.target),dur=1800,start=performance.now();
      function update(now){const p=Math.min(1,(now-start)/dur);e.target.textContent=Math.round(target*(p<.5?2*p*p:1-Math.pow(-2*p+2,2)/2));if(p<1)requestAnimationFrame(update)}
      requestAnimationFrame(update);
    }
  });
});
document.querySelectorAll('.hs-num[data-target]').forEach(el=>counterObs.observe(el));

// ── Cat Bar Animations ──
const catObs=new IntersectionObserver(entries=>{
  entries.forEach(e=>{
    if(e.isIntersecting&&!e.target.dataset.animated){
      e.target.dataset.animated='1';
      e.target.classList.add('visible');
      const fill=e.target.querySelector('.cat-fill');
      if(fill){const w=fill.style.width;fill.style.width='0';setTimeout(()=>{fill.style.transition='width 1.6s cubic-bezier(0.25,0.46,0.45,0.94)';fill.style.width=w;},200);}
    }
  });
},{threshold:.2});
document.querySelectorAll('.cat-bar').forEach(el=>catObs.observe(el));

// ── Lightbox ──
function openLightbox(content,type){
  const lb=document.getElementById('lb'),lbc=document.getElementById('lb-content');
  if(type==='img'){lbc.innerHTML='<img src="'+content+'" alt="Full view">'}
  else{lbc.innerHTML='<div style="max-width:95vw;max-height:90vh;overflow:auto;background:#0d0d1a;border-radius:12px;padding:20px">'+content+'</div>'}
  lb.classList.add('show');document.body.style.overflow='hidden';
}
function closeLightbox(){document.getElementById('lb').classList.remove('show');document.body.style.overflow='';}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeLightbox()});

// ── Smooth Scroll ──
document.querySelectorAll('a[href^="#"]').forEach(a=>{
  a.addEventListener('click',e=>{e.preventDefault();const t=document.querySelector(a.getAttribute('href'));if(t)t.scrollIntoView({behavior:'smooth',block:'start'});});
});

// ── SVG Room Hover Helper ──
document.querySelectorAll('.room-card').forEach(card=>{
  card.addEventListener('mouseenter',()=>{
    const name=card.dataset.room;
    document.querySelectorAll('.room-card').forEach(c=>c.style.opacity='.4');
    card.style.opacity='1';
  });
  card.addEventListener('mouseleave',()=>{
    document.querySelectorAll('.room-card').forEach(c=>c.style.opacity='');
  });
});

// ── Viewer Tab Persistence ──
document.querySelectorAll('.vt-btn').forEach(b=>{
  b.addEventListener('click',()=>{
    document.querySelectorAll('.vt-btn').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('.viewer-panel').forEach(x=>x.classList.remove('active'));
    b.classList.add('active');
    document.getElementById('tab-'+b.dataset.tab).classList.add('active');
  });
});

console.log('%c CAD\u00b7auto PRO ','background:#667eea;color:#fff;padding:8px 16px;border-radius:6px;font-weight:bold;font-size:16px');
console.log('%c Generated showcase v2 with particle network, animations & lightbox','color:#667eea;font-size:12px');
</script>\n'''

h += '</body>\n</html>'

with open('showcase.html','w',encoding='utf-8') as f:
    f.write(h)
print('OK: showcase.html (' + str(len(h)) + ' bytes)')
print('CSS:', len(css), 'bytes')
