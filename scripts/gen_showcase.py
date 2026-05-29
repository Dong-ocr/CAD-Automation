#!/usr/bin/env python3
import json, math, base64

d = json.load(open('demo_project.json','r',encoding='utf-8'))
walls = d['w']; rooms = d['r']; furniture = d['f']; doors = d['d']

total_area = sum(r['w']*r['d'] for r in rooms) / 1e6
ext_walls = [w for w in walls if w['t']=='外']
int_walls = [w for w in walls if w['t']=='内']
ext_len = sum(math.hypot(w['x2']-w['x1'],w['y2']-w['y1']) for w in ext_walls)
int_len = sum(math.hypot(w['x2']-w['x1'],w['y2']-w['y1']) for w in int_walls)

room_list = sorted([(r['n'],round(r['w']*r['d']/1e6,1)) for r in rooms], key=lambda x:-x[1])

# Furniture by room
fbr = {}
for fi in furniture:
    fn = fi['n']
    for r in rooms:
        rx, ry, rw, rd = r['x'], r['y'], r['w'], r['d']
        if rx <= fi['x'] <= rx+rw and ry <= fi['y'] <= ry+rd:
            fbr.setdefault(r['n'],[]).append(fn)
            break
    else:
        fbr.setdefault('其他',[]).append(fn)

rc = ['#2B5F8A','#2D8A4E','#C0392B','#D4A017','#7D3C98','#1ABC9C','#E67E22','#5D6D7E','#34495E','#F39C12']

rooms_html = ''
for i,(nm,area) in enumerate(room_list):
    its = fbr.get(nm,[])
    ft = ''.join(f'<span class="ft">{x}</span>' for x in its) if its else '<span class="ft-dim">-</span>'
    rooms_html += '\n    <div class="room-card" style="--accent:' + rc[i%10] + '"><div class="rc-head"><span class="rc-dot"></span><span class="rc-name">' + nm + '</span><span class="rc-area">' + str(area) + ' m²</span></div><div class="rc-body">' + ft + '</div></div>'

wall_html = ''
for w in walls[:8]:
    t = '🟦 外墙' if w['t']=='外' else '⬜ 内墙'
    l = round(math.hypot(w['x2']-w['x1'],w['y2']-w['y1'])/1000,2)
    wall_html += '\n    <div class="wr"><span class="wt">' + t + '</span><span class="wl">' + str(l) + 'm</span></div>'

# Category
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
    cat_html += '\n    <div class="cat-bar"><span class="cat-label">' + c + '</span><div class="cat-track"><div class="cat-fill" style="width:' + str(pct) + '%"></div></div><span class="cat-num">' + str(n) + '</span></div>'

# Embed files
svg = open('output/floor_plan.svg','r',encoding='utf-8').read()
def b64(path):
    with open(path,'rb') as f: return base64.b64encode(f.read()).decode()
fpng = b64('output/2d_floorplan.png')
ipng = b64('output/3d_isometric.png')

aft = ''.join('<span class="ft" style="padding:5px 14px;font-size:11px">' + f['n'] + '</span>' for f in furniture)

wall_max_x = max(w['x2'] for w in walls) - min(w['x1'] for w in walls)
wall_max_y = max(w['y2'] for w in walls) - min(w['y1'] for w in walls)

# Build HTML with string concat (avoid f-string curly brace issues)
h = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width,initial-scale=1.0">\n<title>CAD 自动化制图 · 终极作品展</title>\n<style>\n'
h += '*{margin:0;padding:0;box-sizing:border-box}html{scroll-behavior:smooth}body{background:#08080f;color:#e0e0e0;font-family:\'Inter\',\'Microsoft YaHei\',system-ui,sans-serif;overflow-x:hidden}::selection{background:#667eea;color:#fff}'
h += '.hero{min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;position:relative;overflow:hidden;background:#08080f}'
h += '.hero-bg canvas{position:absolute;inset:0;width:100%;height:100%}'
h += '.hero-grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.02) 1px,transparent 1px);background-size:60px 60px;mask:radial-gradient(ellipse 60% 50% at center,black 30%,transparent 70%);-webkit-mask:radial-gradient(ellipse 60% 50% at center,black 30%,transparent 70%)}'
h += '.hero-glow{position:absolute;width:600px;height:600px;border-radius:50%;background:radial-gradient(circle,rgba(102,126,234,0.12),transparent 70%);top:20%;left:30%;animation:pulseSlow 6s ease-in-out infinite;pointer-events:none}'
h += '.hero-glow2{position:absolute;width:400px;height:400px;border-radius:50%;background:radial-gradient(circle,rgba(240,184,64,0.08),transparent 70%);bottom:10%;right:20%;animation:pulseSlow 8s ease-in-out infinite 2s;pointer-events:none}'
h += '@keyframes pulseSlow{0%,100%{transform:scale(1);opacity:0.5}50%{transform:scale(1.2);opacity:1}}'
h += '.hero-content{position:relative;z-index:2;text-align:center;padding:0 20px;max-width:900px}'
h += '.hero-badge{display:inline-block;padding:6px 18px;border-radius:100px;border:1px solid rgba(102,126,234,0.25);background:rgba(102,126,234,0.08);font-size:12px;font-weight:600;letter-spacing:2px;color:#667eea;margin-bottom:24px;backdrop-filter:blur(8px)}'
h += '.hero-title{font-size:clamp(2.5rem,8vw,7rem);font-weight:900;line-height:1.05;background:linear-gradient(135deg,#e0e0e0 0%,#667eea 40%,#f0b840 70%,#e0e0e0 100%);background-size:200% 200%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:gradientShift 8s ease-in-out infinite;margin-bottom:16px}'
h += '@keyframes gradientShift{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}'
h += '.hero-sub{font-size:clamp(1rem,2vw,1.6rem);color:rgba(255,255,255,0.4);font-weight:300;margin-bottom:40px;line-height:1.6}'
h += '.hero-stats{display:flex;gap:40px;justify-content:center;flex-wrap:wrap;margin-bottom:48px}.hs-item{text-align:center}'
h += '.hs-num{font-size:clamp(1.8rem,3vw,3.5rem);font-weight:900;color:#fff}.hs-label{font-size:11px;color:rgba(255,255,255,0.3);letter-spacing:1px;margin-top:4px}'
h += '.hero-cta{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}'
h += '.cta-btn{padding:12px 32px;border-radius:8px;border:none;font-size:14px;font-weight:600;cursor:pointer;transition:all .3s;text-decoration:none;display:inline-flex;align-items:center;gap:8px}'
h += '.cta-primary{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;box-shadow:0 4px 24px rgba(102,126,234,0.3)}.cta-primary:hover{transform:translateY(-2px);box-shadow:0 8px 32px rgba(102,126,234,0.5)}'
h += '.cta-secondary{background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);color:#ccc}.cta-secondary:hover{background:rgba(255,255,255,0.1);color:#fff}'
h += '.scroll-hint{position:absolute;bottom:30px;left:50%;transform:translateX(-50%);z-index:2;display:flex;flex-direction:column;align-items:center;gap:6px;color:rgba(255,255,255,0.2);font-size:10px;letter-spacing:2px;animation:bounceDown 2s ease-in-out infinite}'
h += '@keyframes bounceDown{0%,100%{opacity:0.5}50%{opacity:1;transform:translateX(-50%) translateY(8px)}}'
h += '.section{padding:80px 20px;position:relative}.section-inner{max-width:1300px;margin:0 auto}'
h += '.section-tag{display:inline-block;padding:4px 12px;border-radius:100px;background:rgba(102,126,234,0.1);border:1px solid rgba(102,126,234,0.15);font-size:10px;font-weight:600;letter-spacing:1px;color:#667eea;margin-bottom:12px}'
h += '.section-title{font-size:clamp(1.5rem,3vw,2.5rem);font-weight:800;margin-bottom:8px}.section-sub{color:rgba(255,255,255,0.35);font-size:14px;margin-bottom:40px;font-weight:300}'
h += '.dash-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:40px}'
h += '.dash-card{background:linear-gradient(135deg,rgba(255,255,255,0.03),rgba(255,255,255,0.01));border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:24px;text-align:center;backdrop-filter:blur(12px);transition:all .3s;position:relative;overflow:hidden}'
h += '.dash-card::before{content:\'\';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--accent,#667eea),transparent);opacity:0.5}'
h += '.dash-card:hover{transform:translateY(-4px);border-color:rgba(255,255,255,0.12);box-shadow:0 12px 40px rgba(0,0,0,0.3)}'
h += '.dash-icon{font-size:28px;margin-bottom:8px}.dash-num{font-size:clamp(1.8rem,3vw,3rem);font-weight:900;color:#fff}.dash-label{font-size:11px;color:rgba(255,255,255,0.3);letter-spacing:0.5px;margin-top:4px}'
h += '.viewer-tabs{display:flex;gap:4px;margin-bottom:20px;background:rgba(255,255,255,0.03);border-radius:10px;padding:4px;width:fit-content}'
h += '.vt-btn{padding:8px 20px;border-radius:6px;border:none;background:transparent;color:rgba(255,255,255,0.4);font-size:12px;font-weight:600;cursor:pointer;transition:all .25s;font-family:inherit}'
h += '.vt-btn.active{background:rgba(102,126,234,0.2);color:#667eea}.vt-btn:hover:not(.active){color:rgba(255,255,255,0.6)}'
h += '.viewer-panel{display:none;border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,0.06);background:#0d0d1a}'
h += '.viewer-panel.active{display:block}.viewer-panel svg{width:100%;height:auto;display:block}.viewer-panel img{width:100%;height:auto;display:block}'
h += '.room-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}'
h += '.room-card{background:linear-gradient(135deg,rgba(255,255,255,0.03),rgba(255,255,255,0.01));border:1px solid rgba(255,255,255,0.06);border-radius:14px;padding:18px;transition:all .3s}'
h += '.room-card:hover{border-color:var(--accent);box-shadow:0 0 30px rgba(102,126,234,0.05)}'
h += '.rc-head{display:flex;align-items:center;gap:10px;margin-bottom:12px}.rc-dot{width:10px;height:10px;border-radius:50%;background:var(--accent);flex-shrink:0}'
h += '.rc-name{font-size:14px;font-weight:700;color:#fff}.rc-area{margin-left:auto;font-size:12px;color:rgba(255,255,255,0.3);font-weight:600}'
h += '.rc-body{display:flex;flex-wrap:wrap;gap:4px}'
h += '.ft{display:inline-block;padding:3px 10px;border-radius:6px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.04);font-size:10px;color:rgba(255,255,255,0.45)}.ft-dim{font-size:10px;color:rgba(255,255,255,0.15)}'
h += '.cat-section{max-width:700px;margin:0 auto}'
h += '.cat-bar{display:flex;align-items:center;gap:12px;margin-bottom:10px}.cat-label{font-size:12px;color:rgba(255,255,255,0.5);width:60px;flex-shrink:0;text-align:right}'
h += '.cat-track{flex:1;height:8px;background:rgba(255,255,255,0.04);border-radius:10px;overflow:hidden}'
h += '.cat-fill{height:100%;background:linear-gradient(90deg,#667eea,#f0b840);border-radius:10px}'
h += '.cat-num{font-size:12px;color:rgba(255,255,255,0.3);width:24px;text-align:right;font-weight:600}'
h += '.wall-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}'
h += '.wr{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:rgba(255,255,255,0.02);border-radius:8px;border:1px solid rgba(255,255,255,0.04);font-size:12px}'
h += '.wt{color:rgba(255,255,255,0.5)}.wl{font-weight:600;color:rgba(255,255,255,0.7)}'
h += '.spec-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}'
h += '.spec-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:12px;padding:20px}'
h += '.spec-card h4{font-size:12px;color:rgba(255,255,255,0.3);margin-bottom:12px;letter-spacing:1px;text-transform:uppercase}'
h += '.spec-card .sv{font-size:18px;font-weight:700;color:#fff}.spec-card .sl{font-size:11px;color:rgba(255,255,255,0.3);margin-top:2px}'
h += '.footer{text-align:center;padding:40px 20px;border-top:1px solid rgba(255,255,255,0.04);color:rgba(255,255,255,0.15);font-size:11px;line-height:1.8}'
h += 'nav{position:fixed;top:0;left:0;right:0;z-index:100;padding:12px 24px;display:flex;justify-content:space-between;align-items:center;background:rgba(8,8,15,0.8);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,0.04)}'
h += 'nav .logo{font-size:14px;font-weight:800;color:#fff;text-decoration:none}nav .logo span{color:#667eea}'
h += 'nav ul{display:flex;gap:20px;list-style:none}nav ul a{color:rgba(255,255,255,0.4);text-decoration:none;font-size:11px;font-weight:600;letter-spacing:0.5px;transition:color .2s}nav ul a:hover{color:#fff}'
h += '@media(max-width:600px){.hero-stats{gap:16px}.dash-grid{grid-template-columns:repeat(2,1fr)}.room-grid{grid-template-columns:1fr}.wall-grid{grid-template-columns:1fr}nav ul{display:none}}'
h += '</style>\n</head>\n<body>\n'

# Nav
h += '<nav><a href="#" class="logo">CAD<span>\u00b7</span>auto</a><ul>'
h += '<li><a href="#dashboard">数据</a></li><li><a href="#viewer">平面图</a></li><li><a href="#rooms">房间</a></li><li><a href="#furniture">家具</a></li><li><a href="#specs">技术</a></li>'
h += '</ul></nav>\n'

# Hero
h += '<section class="hero"><div class="hero-bg"><canvas id="c"></canvas><div class="hero-grid"></div><div class="hero-glow"></div><div class="hero-glow2"></div></div>'
h += '<div class="hero-content"><div class="hero-badge">\u26a1 Python \u00b7 SVG \u00b7 DXF \u00b7 Three.js</div>'
h += '<h1 class="hero-title">CAD \u81ea\u52a8\u5316\u5236\u56fe</h1>'
h += '<p class="hero-sub">\u4ece JSON \u6570\u636e\u5230\u65bd\u5de5\u56fe\u7eb8 \u00b7 \u5168\u81ea\u52a8\u7ba1\u7ebf<br>\u5ba4\u5185\u8bbe\u8ba1 \u00b7 \u5de5\u7a0b\u56fe\u7eb8 \u00b7 \u7edf\u4e00\u5f15\u64ce</p>'
h += '<div class="hero-stats">'
h += '<div class="hs-item"><span class="hs-num">' + str(round(total_area)) + '</span><span class="hs-label">\u603b\u9762\u79ef m\u00b2</span></div>'
h += '<div class="hs-item"><span class="hs-num">' + str(len(rooms)) + '</span><span class="hs-label">\u623f\u95f4</span></div>'
h += '<div class="hs-item"><span class="hs-num">' + str(len(furniture)) + '</span><span class="hs-label">\u5bb6\u5177</span></div>'
h += '<div class="hs-item"><span class="hs-num">' + str(len(walls)) + '</span><span class="hs-label">\u5899\u4f53</span></div>'
h += '</div><div class="hero-cta"><a href="#dashboard" class="cta-btn cta-primary">\U0001f680 \u63a2\u7d22\u4f5c\u54c1</a><a href="#viewer" class="cta-btn cta-secondary">\U0001f4d0 \u67e5\u770b\u56fe\u7eb8</a></div></div>'
h += '<div class="scroll-hint"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 13l5 5 5-5M7 6l5 5 5-5"/></svg><span>\u5411\u4e0b\u6eda\u52a8</span></div></section>\n'

# Dashboard
h += '<section class="section" id="dashboard"><div class="section-inner">'
h += '<div class="section-tag">\U0001f4ca 01 \u00b7 \u9879\u76ee\u6570\u636e</div>'
h += '<h2 class="section-title">\u8bbe\u8ba1\u6982\u89c8</h2>'
h += '<p class="section-sub">\u57fa\u4e8e ' + str(len(rooms)) + ' \u4e2a\u623f\u95f4\u3001' + str(len(walls)) + ' \u6bb5\u5899\u4f53\u3001' + str(len(furniture)) + ' \u4ef6\u5bb6\u5177\u7684\u5b8c\u6574\u8bbe\u8ba1</p>'
h += '<div class="dash-grid">'
dash_items = [
    ('\U0001f4d0', str(round(total_area,1)), '\u4f7f\u7528\u9762\u79ef (m\u00b2)', '#667eea'),
    ('\U0001f6aa', str(len(rooms)), '\u623f\u95f4\u6570\u91cf', '#f0b840'),
    ('\U0001f9f1', str(len(walls)), '\u5899\u4f53\u6bb5\u6570', '#2ecc71'),
    ('\U0001fa91', str(len(furniture)), '\u5bb6\u5177\u4ef6\u6570', '#e74c3c'),
    ('\U0001f6aa', str(len(doors)), '\u95e8\u6d1e\u6570\u91cf', '#9b59b6'),
    ('\U0001f4cf', str(round((ext_len+int_len)/1000,1)), '\u603b\u5899\u7ebf (m)', '#1abc9c'),
]
for icon, num, label, color in dash_items:
    h += '<div class="dash-card" style="--accent:' + color + '"><span class="dash-icon">' + icon + '</span><span class="dash-num">' + num + '</span><span class="dash-label">' + label + '</span></div>'
h += '</div>\n'
h += '<div class="spec-grid"><div class="spec-card"><h4>\U0001f9f1 \u5916\u5899</h4><div style="display:flex;justify-content:space-between;font-size:13px"><span>\u539a\u5ea6 240mm</span><span style="color:rgba(255,255,255,0.3)">' + str(len(ext_walls)) + ' \u6bb5 \u00b7 ' + str(round(ext_len/1000,1)) + 'm</span></div></div>'
h += '<div class="spec-card"><h4>\u2b1c \u5185\u5899</h4><div style="display:flex;justify-content:space-between;font-size:13px"><span>\u539a\u5ea6 150mm</span><span style="color:rgba(255,255,255,0.3)">' + str(len(int_walls)) + ' \u6bb5 \u00b7 ' + str(round(int_len/1000,1)) + 'm</span></div></div></div>'
h += '</div></section>\n'

# Viewer
h += '<section class="section" id="viewer" style="background:rgba(255,255,255,0.01)"><div class="section-inner">'
h += '<div class="section-tag">\U0001f4d0 02 \u00b7 \u56fe\u7eb8\u67e5\u770b\u5668</div>'
h += '<h2 class="section-title">\u5e73\u9762 & \u4e09\u7ef4</h2>'
h += '<p class="section-sub">SVG \u77e2\u91cf\u5e73\u9762\u56fe \u00b7 3D \u7b49\u8f74\u6d4b\u6e32\u67d3 \u00b7 \u4e00\u952e\u5207\u6362</p>'
h += '<div class="viewer-tabs"><button class="vt-btn active" data-tab="svg">\U0001f4d0 \u5e73\u9762 SVG</button><button class="vt-btn" data-tab="d2">\U0001f5bc \u4e8c\u7ef4\u6e32\u67d3</button><button class="vt-btn" data-tab="d3">\U0001f3d7 \u4e09\u7ef4\u7b49\u8f74\u6d4b</button></div>'
h += '<div class="viewer-panel active" id="tab-svg">' + svg + '</div>'
h += '<div class="viewer-panel" id="tab-d2"><img src="data:image/png;base64,' + fpng + '" alt="2D"></div>'
h += '<div class="viewer-panel" id="tab-d3"><img src="data:image/png;base64,' + ipng + '" alt="3D"></div>'
h += '</div></section>\n'

# Rooms
h += '<section class="section" id="rooms"><div class="section-inner">'
h += '<div class="section-tag">\U0001f3e0 03 \u00b7 \u623f\u95f4\u5bfc\u89c8</div>'
h += '<h2 class="section-title">\u7a7a\u95f4\u5206\u5e03</h2>'
h += '<p class="section-sub">\u6bcf\u4e2a\u623f\u95f4\u7684\u9762\u79ef\u4e0e\u5bb6\u5177\u914d\u7f6e</p>'
h += '<div class="room-grid">' + rooms_html + '\n</div></div></section>\n'

# Furniture
h += '<section class="section" id="furniture" style="background:rgba(255,255,255,0.01)"><div class="section-inner">'
h += '<div class="section-tag">\U0001fa91 04 \u00b7 \u5bb6\u5177\u6e05\u5355</div>'
h += '<h2 class="section-title">\u5bb6\u5177\u54c1\u7c7b\u5206\u5e03</h2>'
h += '<p class="section-sub">\u5171 ' + str(len(furniture)) + ' \u4ef6\u5bb6\u5177</p>'
h += '<div class="cat-section">' + cat_html + '\n</div>'
h += '<div style="margin-top:30px;display:flex;flex-wrap:wrap;gap:6px;justify-content:center">' + aft + '</div>'
h += '</div></section>\n'

# Specs
h += '<section class="section" id="specs"><div class="section-inner">'
h += '<div class="section-tag">\u2699\ufe0f 05 \u00b7 \u6280\u672f\u53c2\u6570</div>'
h += '<h2 class="section-title">\u5de5\u7a0b\u6570\u636e</h2>'
h += '<p class="section-sub">\u5899\u4f53\u5c3a\u5bf8 \u00b7 \u7ed3\u6784\u4fe1\u606f \u00b7 \u751f\u6210\u5f15\u64ce</p>'
h += '<div class="wall-grid">' + wall_html + '\n</div>'
h += '<div style="margin-top:30px" class="spec-grid">'
h += '<div class="spec-card"><h4>\U0001f4d0 \u5f00\u95f4</h4><div class="sv">' + str(round(wall_max_x/1000)) + ' mm</div><div class="sl">\u4e1c\u897f\u65b9\u5411</div></div>'
h += '<div class="spec-card"><h4>\U0001f4cf \u8fdb\u6df1</h4><div class="sv">' + str(round(wall_max_y/1000)) + ' mm</div><div class="sl">\u5357\u5317\u65b9\u5411</div></div>'
h += '<div class="spec-card"><h4>\U0001f3d7 \u5899\u9ad8</h4><div class="sv">2800 mm</div><div class="sl">\u6807\u51c6\u5c42\u9ad8</div></div>'
h += '<div class="spec-card"><h4>\U0001f504 \u751f\u6210\u5f15\u64ce</h4><div class="sv" style="font-size:14px;color:#667eea">cad_toolbox_v8</div><div class="sl">Python \u00b7 DXF \u00b7 SVG \u00b7 STEP \u00b7 IFC</div></div>'
h += '</div></div></section>\n'

# Footer
h += '<footer class="footer"><p>CAD \u81ea\u52a8\u5316\u5236\u56fe\u7cfb\u7edf \u00b7 \u7531 Python + SVG + Three.js \u9a71\u52a8</p><p>\u5ca9\u6cca\u6e21\u6c34\u7535\u7ad9\u5de5\u7a0b \u00b7 \u5ba4\u5185\u8bbe\u8ba1\u4e00\u4f53\u5316</p></footer>\n'

# JS
h += '<script>\n'
h += 'const c=document.getElementById(\'c\'),cx=c.getContext(\'2d\');\n'
h += 'let W,H,P=[];\n'
h += 'function rs(){W=c.width=innerWidth;H=c.height=innerHeight;}\n'
h += 'rs();addEventListener(\'resize\',rs);\n'
h += 'class Pt{constructor(){this.rs();}rs(){this.x=Math.random()*W;this.y=Math.random()*H;this.vx=(Math.random()-.5)*.4;this.vy=(Math.random()-.5)*.4;this.r=Math.random()*2+1;}up(){this.x+=this.vx;this.y+=this.vy;if(this.x<0||this.x>W||this.y<0||this.y>H)this.rs();}dr(){cx.beginPath();cx.arc(this.x,this.y,this.r,0,7);cx.fillStyle=\'rgba(255,255,255,\'+(.15+Math.random()*.1)+\')\';cx.fill();}}\n'
h += 'for(let i=0;i<120;i++)P.push(new Pt());\n'
h += 'let mx=W/2,my=H/2;\n'
h += 'onmousemove=e=>{mx=e.clientX;my=e.clientY;};\n'
h += 'function an(){cx.clearRect(0,0,W,H);P.forEach(p=>{p.up();p.dr();});for(let i=0;i<P.length;i++)for(let j=i+1;j<P.length;j++){let dx=P[i].x-P[j].x,dy=P[i].y-P[j].y,d=Math.sqrt(dx*dx+dy*dy);if(d<150){cx.beginPath();cx.moveTo(P[i].x,P[i].y);cx.lineTo(P[j].x,P[j].y);cx.strokeStyle=\'rgba(102,126,234,\'+((1-d/150)*.12)+\')\';cx.stroke();}}P.forEach(p=>{let dx=p.x-mx,dy=p.y-my,d=Math.sqrt(dx*dx+dy*dy);if(d<200){cx.beginPath();cx.moveTo(p.x,p.y);cx.lineTo(mx,my);cx.strokeStyle=\'rgba(102,126,234,\'+((1-d/200)*.08)+\')\';cx.stroke();}});requestAnimationFrame(an);}\n'
h += 'an();\n'
h += 'document.querySelectorAll(\'.vt-btn\').forEach(b=>b.onclick=()=>{document.querySelectorAll(\'.vt-btn\').forEach(x=>x.classList.remove(\'active\'));document.querySelectorAll(\'.viewer-panel\').forEach(x=>x.classList.remove(\'active\'));b.classList.add(\'active\');document.getElementById(\'tab-\'+b.dataset.tab).classList.add(\'active\');});\n'
h += 'document.querySelectorAll(\'a[href^="#"]\').forEach(a=>a.onclick=e=>{e.preventDefault();let t=document.querySelector(a.getAttribute(\'href\'));if(t)t.scrollIntoView({behavior:\'smooth\'});});\n'
h += '</script>\n'

h += '</body>\n</html>'

with open('showcase.html','w',encoding='utf-8') as f:
    f.write(h)
print('OK: showcase.html (' + str(len(h)) + ' bytes)')
