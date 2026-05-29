import json, math, os

d = json.load(open('demo_project.json','r',encoding='utf-8'))
walls = d['w']
furniture = d['f']
rooms = d['r']
doors = d['d']

svg = open('output/floor_plan.svg','r',encoding='utf-8').read()
svg_lines = svg.split('\n')
svg_body = '\n'.join(svg_lines[1:])

furniture_by_room = {}
for f in furniture:
    fn = f['n']
    for r in rooms:
        rx, ry, rw, rd = r['x'], r['y'], r['w'], r['d']
        if rx <= f['x'] <= rx+rw and ry <= f['y'] <= ry+rd:
            furniture_by_room.setdefault(r['n'], []).append(fn)
            break
    else:
        furniture_by_room.setdefault('其他', []).append(fn)

os.makedirs('output/html', exist_ok=True)

ext = sum(1 for w in walls if w['t'] == '外')
int_ = sum(1 for w in walls if w['t'] == '内')
ext_len = sum(math.hypot(w['x2']-w['x1'], w['y2']-w['y1']) for w in walls if w['t'] == '外')
int_len = sum(math.hypot(w['x2']-w['x1'], w['y2']-w['y1']) for w in walls if w['t'] == '内')
total_area = sum(r['w']*r['d'] for r in rooms) / 1e6

room_colors = ['#2B5F8A','#2D8A4E','#C0392B','#D4A017','#7D3C98','#1ABC9C','#E67E22','#5D6D7E','#34495E','#F39C12']

rooms_html = ''
for i, r in enumerate(rooms):
    area = r['w'] * r['d'] / 1e6
    rooms_html += f'<div class="room-item"><div style="display:flex;align-items:center"><span class="dot" style="background:{room_colors[i%len(room_colors)]}"></span><span class="nm">{r["n"]}</span></div><span class="sz">{area:.1f} m²</span></div>'

wall_html = f'<div><span>外墙:</span> {ext}段·总长{ext_len/1000:.1f}m · 厚240mm</div><div><span>内墙:</span> {int_}段·总长{int_len/1000:.1f}m · 厚150mm</div><div style="margin-top:6px"><span>门:</span> {len(doors)}扇</div>'

furn_html = ''
for r in rooms:
    fn = r['n']
    items = furniture_by_room.get(fn, [])
    if items:
        furn_html += f'<div style="margin-bottom:6px"><div style="font-size:11px;color:rgba(255,255,255,0.4);margin-bottom:3px">{fn}</div>'
        for fi in items:
            furn_html += f'<span class="furniture-tag">{fi}</span>'
        furn_html += '</div>'
if '其他' in furniture_by_room:
    furn_html += '<div style="margin-bottom:6px"><div style="font-size:11px;color:rgba(255,255,255,0.4);margin-bottom:3px">其他</div>'
    for fi in furniture_by_room['其他']:
        furn_html += f'<span class="furniture-tag">{fi}</span>'
    furn_html += '</div>'

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>CAD 设计展示 · 室内平面布置图</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0d0d1a;color:#e0e0e0;font-family:system-ui,"Microsoft YaHei",sans-serif;min-height:100vh}}
.header{{background:linear-gradient(135deg,#1a1a2e,#16213e);border-bottom:1px solid rgba(255,255,255,0.06);padding:16px 24px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100;backdrop-filter:blur(12px)}}
.header h1{{font-size:18px;font-weight:800;background:linear-gradient(90deg,#6a9cff,#f0b840);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.header .sub{{font-size:11px;color:rgba(255,255,255,0.3);margin-top:2px}}
.header .actions{{display:flex;gap:6px}}
.btn{{background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);color:#ccc;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:11px;transition:all .2s;font-weight:600}}
.btn:hover{{background:rgba(255,255,255,0.12);color:#fff}}
.container{{max-width:1400px;margin:0 auto;padding:20px}}
.layout{{display:grid;grid-template-columns:1fr 360px;gap:24px}}
@media(max-width:1000px){{.layout{{grid-template-columns:1fr}}}}
.floorplan-wrap{{background:#111;border-radius:12px;border:1px solid rgba(255,255,255,0.06);padding:16px;overflow:hidden}}
.floorplan-wrap svg{{width:100%;height:auto;display:block;border-radius:4px}}
.sidebar{{display:flex;flex-direction:column;gap:16px}}
.card{{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:16px}}
.card h3{{font-size:13px;font-weight:700;margin-bottom:10px;color:rgba(255,255,255,0.7);text-transform:uppercase;letter-spacing:0.5px}}
.stats{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
.stat{{background:rgba(255,255,255,0.03);border-radius:8px;padding:12px;text-align:center}}
.stat .v{{font-size:20px;font-weight:800;color:#f0b840}}
.stat .l{{font-size:10px;color:rgba(255,255,255,0.35);margin-top:2px}}
.room-list{{display:flex;flex-direction:column;gap:0;margin:-4px}}
.room-item{{display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:12px}}
.room-item:last-child{{border:none}}
.room-item .nm{{color:rgba(255,255,255,0.7)}}
.room-item .sz{{color:rgba(255,255,255,0.3);font-size:11px}}
.room-item .dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0;margin-right:8px}}
.furniture-tag{{display:inline-block;background:rgba(255,255,255,0.06);padding:2px 8px;border-radius:4px;font-size:10px;color:rgba(255,255,255,0.5);margin:1px}}
.wall-info{{font-size:11px;color:rgba(255,255,255,0.4);line-height:1.6}}
.wall-info span{{color:rgba(255,255,255,0.6)}}
</style>
</head>
<body>
<div class="header">
<div><h1>🏭 CAD 自动化制图</h1><div class="sub">室内设计 · 平面布置图</div></div>
<div class="actions">
<button class="btn" onclick="window.open('floor_plan.svg','_blank')">SVG 原图</button>
<button class="btn" onclick="location.reload()">刷新</button>
</div>
</div>
<div class="container">
<div class="layout">
<div class="floorplan-wrap">
{svg_body}
</div>
<div class="sidebar">
<div class="card">
<h3>📊 项目概览</h3>
<div class="stats">
<div class="stat"><div class="v">{total_area:.1f}</div><div class="l">使用面积 (m²)</div></div>
<div class="stat"><div class="v">{len(rooms)}</div><div class="l">房间</div></div>
<div class="stat"><div class="v">{len(walls)}</div><div class="l">墙体</div></div>
<div class="stat"><div class="v">{len(furniture)}</div><div class="l">家具</div></div>
</div>
</div>
<div class="card">
<h3>📍 房间列表</h3>
<div class="room-list">
{rooms_html}
</div>
</div>
<div class="card">
<h3>🛠 墙体信息</h3>
<div class="wall-info">
{wall_html}
</div>
</div>
<div class="card">
<h3>🪑 家具导览</h3>
<div>
{furn_html}
</div>
</div>
</div>
</div>
</div>
<script>
document.querySelectorAll('.floorplan-wrap svg rect').forEach(function(el) {{
  var f = el.getAttribute('fill') || '';
  if (f.includes('rgba')) {{
    el.addEventListener('mouseenter', function(){{ this.style.opacity = '0.25'; }});
    el.addEventListener('mouseleave', function(){{ this.style.opacity = ''; }});
  }}
}});
</script>
</body>
</html>
"""

with open('output/html/index.html','w',encoding='utf-8') as f:
    f.write(html)
print(f'OK: output/html/index.html ({len(html)} bytes)')
