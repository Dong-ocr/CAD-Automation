#!/usr/bin/env python3
"""AI Interior Design Studio — Backend Server"""
import os, sys, json, uuid, math, traceback, webbrowser, threading
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template_string
import urllib.request

ROOT = Path(__file__).parent.absolute()
SRC_DIR = ROOT / "src"
OUT_DIR = ROOT / "output" / "studio"
OUT_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SRC_DIR))

from interior_models import *
from interior_dxf import render_dxf, render_svg

app = Flask(__name__)
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY", "sk-329e23b7df6947419dd41fd08ea184c4")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

ROOM_COLORS = {
    "客厅":"#dbeafe","卧室":"#ede9fe","主卧":"#ddd6fe",
    "次卧":"#fae8ff","厨房":"#d1fae5","卫生间":"#fce7f3",
    "餐厅":"#fef3c7","阳台":"#e0f2fe","书房":"#fef9c3",
    "过道":"#f3f4f6","储物间":"#e5e7eb",
}

HTML = ""

@app.route("/")
def index():
    global HTML
    if not HTML:
        p = ROOT / "studio.html"
        if p.exists():
            HTML = p.read_text(encoding="utf-8")
    return render_template_string(HTML)

@app.route("/api/templates")
def get_templates():
    return jsonify({"templates":[
        {"id":"apt_2b1b","name":"标准两室一厅","area":72,"rooms":5},
        {"id":"apt_3b1b","name":"舒适三室一厅","area":95,"rooms":6},
        {"id":"apt_large","name":"大平层四室","area":140,"rooms":8},
        {"id":"studio","name":"Studio开间","area":35,"rooms":3},
    ]})

@app.route("/api/furniture")
def get_furniture():
    items = []
    for name, tmpl in FURNITURE_TEMPLATES.items():
        items.append({"name":name,"category":tmpl.category.value,"width":tmpl.width,"depth":tmpl.depth,"height":tmpl.height,"color":tmpl.color or "#cccccc"})
    return jsonify({"items":items})

@app.route("/api/project/new", methods=["POST"])
def new_project():
    data = request.json or {}
    tid = data.get("template", "apt_2b1b")
    try:
        if tid == "apt_3b1b": proj = create_larger_apartment()
        elif tid == "apt_large": proj = create_large_apartment()
        elif tid == "studio": proj = create_studio()
        else: proj = create_apartment_template_fixed()
        return jsonify({"success":True,"project":project_to_web(proj)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success":False,"error":str(e)})

@app.route("/api/design/ai", methods=["POST"])
def ai_design():
    prompt = request.json.get("prompt", "")
    if not prompt:
        return jsonify({"success":False,"error":"请输入设计需求"})
    try:
        ai_result = call_deepseek(prompt)
        proj = build_from_ai(ai_result)
        return jsonify({"success":True,"project":project_to_web(proj),"ai_analysis":ai_result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success":False,"error":str(e)})

@app.route("/api/export/dxf", methods=["POST"])
def export_dxf():
    data = request.json
    proj = web_to_project(data)
    oid = uuid.uuid4().hex[:8]
    od = OUT_DIR / oid; od.mkdir(parents=True, exist_ok=True)
    try:
        render_dxf(proj, str(od / "floorplan.dxf"))
        return jsonify({"success":True,"file":f"/output/studio/{oid}/floorplan.dxf"})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success":False,"error":str(e)})

@app.route("/api/export/preview", methods=["POST"])
def export_preview():
    data = request.json; fmt = data.get("format", "png")
    proj = web_to_project(data)
    oid = uuid.uuid4().hex[:8]; od = OUT_DIR / oid; od.mkdir(parents=True, exist_ok=True)
    ext = "png" if fmt == "png" else "svg"
    try:
        render_svg(proj, str(od / f"preview.{ext}"))
        return jsonify({"success":True,"file":f"/output/studio/{oid}/preview.{ext}"})
    except Exception as e:
        traceback.print_exc()
        svg = generate_svg_preview(proj)
        (od / "preview.svg").write_text(svg, encoding="utf-8")
        return jsonify({"success":True,"file":f"/output/studio/{oid}/preview.svg"})

@app.route("/output/studio/<oid>/<fn>")
def serve_output(oid, fn):
    return send_file(str(OUT_DIR / oid / fn))

# Villa 3D viewer
@app.route("/villa")
def villa_3d():
    html_path = ROOT / "web" / "villa_viewer.html"
    if html_path.exists():
        return render_template_string(html_path.read_text(encoding="utf-8"))
    return "404"

# NOTE: route removed (conflicts with STL file serving)
def project_to_web(proj):
    return {
        "name":proj.name,
        "walls":[{"idx":i,"x1":w.start.x,"y1":w.start.y,"x2":w.end.x,"y2":w.end.y,"thickness":w.thickness,"type":w.wall_type.value,"length":round(w.length(),1)} for i,w in enumerate(proj.walls)],
        "rooms":[{"name":r.name,"type":r.room_type.value,"corners":[{"x":c.x,"y":c.y} for c in r.corners],"area":round(r.area/1e6,2),"center":{"x":r.center().x,"y":r.center().y}} for r in proj.rooms],
        "openings":[{"wall_idx":op.wall_idx,"position":op.position,"width":op.width,"height":op.height,"is_door":op.is_door} for op in proj.openings],
        "furniture":[{"name":f.name,"category":f.category.value,"w":f.width,"d":f.depth,"h":f.height,"x":f.x,"y":f.y,"rotation":f.rotation,"color":f.color,"room":f.room} for f in proj.furniture],
        "total_area":round(sum(r.area for r in proj.rooms)/1e6,2),
        "stats":{"rooms":len(proj.rooms),"walls":len(proj.walls),"furniture":len(proj.furniture),"openings":len(proj.openings)},
    }

def web_to_project(data):
    proj = InteriorProject(name=data.get("name","设计项目"))
    for w in data.get("walls",[]):
        proj.walls.append(Wall(Point2D(w["x1"],w["y1"]),Point2D(w["x2"],w["y2"]),thickness=w.get("thickness",200),wall_type=WallType.EXTERIOR if w.get("type","外墙")=="外墙" else WallType.INTERIOR))
    for r in data.get("rooms",[]):
        corners=[Point2D(c["x"],c["y"]) for c in r.get("corners",[])]
        rt=RoomType.LIVING_ROOM
        for m in RoomType:
            if m.value==r.get("type",""): rt=m; break
        room=Room(r.get("name","房间"),rt,corners); room.calculate_area()
        proj.rooms.append(room)
    for op in data.get("openings",[]):
        proj.openings.append(Opening(wall_idx=op["wall_idx"],position=op["position"],width=op["width"],height=op.get("height",2100),is_door=op.get("is_door",True)))
    for f in data.get("furniture",[]):
        fc=FurnitureCategory.CABINET
        for m in FurnitureCategory:
            if m.value==f.get("category",""): fc=m; break
        proj.furniture.append(FurnitureItem(name=f["name"],category=fc,width=f["w"],depth=f["d"],height=f.get("h",800),x=f["x"],y=f["y"],rotation=f.get("rotation",0),color=f.get("color","#cccccc"),room=f.get("room","")))
    return proj

def generate_svg_preview(proj):
    lines=['<svg viewBox="-500 -500 11000 11000" xmlns="http://www.w3.org/2000/svg"><defs><style>.rm{font:bold 32px sans-serif;fill:#1f2937;text-anchor:middle}.rl{font:22px sans-serif;fill:#6b7280;text-anchor:middle}.fl{font:14px sans-serif;fill:#fff;text-anchor:middle;dominant-baseline:central}</style></defs>']
    lines.append('<rect x="-500" y="-500" width="11000" height="11000" fill="#f8f9fa" rx="20"/>')
    for r in proj.rooms:
        if not r.corners: continue
        pts=" ".join(f"{c.x},{c.y}" for c in r.corners)
        c=ROOM_COLORS.get(r.name,"#f3f4f6"); ct=r.center()
        lines.append(f'<polygon points="{pts}" fill="{c}" stroke="#374151" stroke-width="3" stroke-linejoin="round"/>')
        lines.append(f'<text x="{ct.x}" y="{ct.y-12}" class="rm">{r.name}</text>')
        lines.append(f'<text x="{ct.x}" y="{ct.y+22}" class="rl">{r.area/1e6:.1f}m\u00b2</text>')
    for w in proj.walls:
        lines.append(f'<line x1="{w.start.x}" y1="{w.start.y}" x2="{w.end.x}" y2="{w.end.y}" stroke="#374151" stroke-width="{max(2,w.thickness/60)}" stroke-linecap="round"/>')
    for op in proj.openings:
        if not op.is_door or op.wall_idx>=len(proj.walls): continue
        w=proj.walls[op.wall_idx]; dx,dy=w.end.x-w.start.x,w.end.y-w.start.y
        length=(dx*dx+dy*dy)**0.5
        if length==0: continue
        ratio=op.position/length; cx=w.start.x+dx*ratio; cy=w.start.y+dy*ratio
        lines.append(f'<circle cx="{cx}" cy="{cy}" r="{op.width//2}" fill="none" stroke="#f59e0b" stroke-width="4" stroke-dasharray="6,3"/>')
    for f in proj.furniture:
        lines.append(f'<rect x="{f.x}" y="{f.y}" width="{f.w}" height="{f.d}" fill="{f.color}" stroke="#1f2937" stroke-width="2" rx="4" opacity="0.8"/>')
        lines.append(f'<text x="{f.x+f.w//2}" y="{f.y+f.d//2}" class="fl">{f.name}</text>')
    lines.append('</svg>')
    return "\n".join(lines)

def call_deepseek(prompt):
    msg="你是专业室内设计师。分析需求输出JSON：{\"style\":\"风格\",\"description\":\"描述\",\"suggested_rooms\":[\"客厅\"],\"total_area\":80,\"furniture_suggestions\":[{\"name\":\"双人床\",\"room\":\"主卧\"}]}"
    data=json.dumps({"model":"deepseek-chat","messages":[{"role":"system","content":msg},{"role":"user","content":prompt}],"temperature":0.3,"max_tokens":2000}).encode()
    req=urllib.request.Request(DEEPSEEK_URL,data=data,headers={"Authorization":f"Bearer {DEEPSEEK_KEY}","Content-Type":"application/json"})
    resp=json.loads(urllib.request.urlopen(req,timeout=60).read())
    text=resp["choices"][0]["message"]["content"].strip()
    if "```json" in text: text=text.split("```json")[1].split("```")[0].strip()
    elif "```" in text: text=text.split("```")[1].split("```")[0].strip()
    return json.loads(text)

def build_from_ai(ai):
    proj=InteriorProject(name=f"AI设计·{ai.get('style','现代简约')}")
    suggested=ai.get("suggested_rooms",["客厅","主卧","厨房","卫生间","餐厅"])
    base=[("客厅",RoomType.LIVING_ROOM,[(1000,1000),(5000,1000),(5000,5500),(1000,5500)]),("主卧",RoomType.BEDROOM,[(5500,1000),(9500,1000),(9500,5000),(5500,5000)]),("厨房",RoomType.KITCHEN,[(1000,6000),(5000,6000),(5000,9000),(1000,9000)]),("卫生间",RoomType.BATHROOM,[(6000,5500),(7500,5500),(7500,7000),(6000,7000)]),("餐厅",RoomType.DINING_ROOM,[(5500,5500),(9500,5500),(9500,9000),(5500,9000)]),("书房",RoomType.STUDY,[(1000,9500),(5000,9500),(5000,12000),(1000,12000)])]
    rooms_to_use=[r for r in base if r[0] in suggested]
    if not rooms_to_use: rooms_to_use=base[:max(3,min(len(suggested),5))]
    for name,rtype,corners in rooms_to_use:
        room=Room(name,rtype,[Point2D(x,y) for x,y in corners])
        room.calculate_area(); proj.rooms.append(room)
    if not proj.rooms: return create_apartment_template_fixed()
    all_x=[c.x for room in proj.rooms for c in room.corners]
    all_y=[c.y for room in proj.rooms for c in room.corners]
    rx,ry=min(all_x)-200,min(all_y)-200
    rx2,ry2=max(all_x)+200,max(all_y)+200
    for s,e in [((rx,ry),(rx2,ry)),((rx2,ry),(rx2,ry2)),((rx2,ry2),(rx,ry2)),((rx,ry2),(rx,ry))]:
        proj.walls.append(Wall(Point2D(s[0],s[1]),Point2D(e[0],e[1]),thickness=240,wall_type=WallType.EXTERIOR))
    for fs in ai.get("furniture_suggestions",[]):
        name=fs.get("name",""); rn=fs.get("room","")
        if name in FURNITURE_TEMPLATES:
            tmpl=FURNITURE_TEMPLATES[name]; tr=None
            for r in proj.rooms:
                if r.name==rn: tr=r; break
            if not tr and proj.rooms: tr=proj.rooms[0]
            if tr:
                cx,cy=tr.center().x,tr.center().y
                proj.furniture.append(FurnitureItem(name=name,category=tmpl.category,width=tmpl.width,depth=tmpl.depth,height=tmpl.height,x=cx-tmpl.width//2,y=cy-tmpl.depth//2,color=tmpl.color or ROOM_COLORS.get(tr.name,"#cccccc"),room=tr.name))
    return proj

def create_larger_apartment():
    proj=InteriorProject("舒适三室一厅")
    for n,rt,cs in [("客厅",RoomType.LIVING_ROOM,[(500,500),(5500,500),(5500,5500),(500,5500)]),("主卧",RoomType.BEDROOM,[(6000,500),(10500,500),(10500,4500),(6000,4500)]),("次卧",RoomType.BEDROOM,[(6000,5000),(8500,5000),(8500,7500),(6000,7500)]),("厨房",RoomType.KITCHEN,[(500,6000),(3500,6000),(3500,9000),(500,9000)]),("卫生间",RoomType.BATHROOM,[(4000,6000),(5500,6000),(5500,7500),(4000,7500)]),("餐厅",RoomType.DINING_ROOM,[(6000,8000),(10500,8000),(10500,10500),(6000,10500)])]:
        r=Room(n,rt,[Point2D(x,y) for x,y in cs]); r.calculate_area(); proj.rooms.append(r)
    for s,e in [((0,0),(11000,0)),((11000,0),(11000,11000)),((11000,11000),(0,11000)),((0,11000),(0,0))]:
        proj.walls.append(Wall(Point2D(s[0],s[1]),Point2D(e[0],e[1]),thickness=240,wall_type=WallType.EXTERIOR))
    return proj

def create_large_apartment():
    proj=InteriorProject("大平层四室")
    for n,rt,cs in [("客厅",RoomType.LIVING_ROOM,[(500,500),(6500,500),(6500,6000),(500,6000)]),("主卧",RoomType.BEDROOM,[(7000,500),(12500,500),(12500,4500),(7000,4500)]),("次卧",RoomType.BEDROOM,[(7000,5000),(10000,5000),(10000,8000),(7000,8000)]),("书房",RoomType.STUDY,[(10500,5000),(12500,5000),(12500,7500),(10500,7500)]),("厨房",RoomType.KITCHEN,[(500,6500),(4000,6500),(4000,10000),(500,10000)]),("餐厅",RoomType.DINING_ROOM,[(4500,6500),(6500,6500),(6500,10000),(4500,10000)]),("卫生间1",RoomType.BATHROOM,[(4500,10500),(6500,10500),(6500,12000),(4500,12000)]),("卫生间2",RoomType.BATHROOM,[(11000,8000),(12500,8000),(12500,10000),(11000,10000)])]:
        r=Room(n,rt,[Point2D(x,y) for x,y in cs]); r.calculate_area(); proj.rooms.append(r)
    for s,e in [((0,0),(13000,0)),((13000,0),(13000,12500)),((13000,12500),(0,12500)),((0,12500),(0,0))]:
        proj.walls.append(Wall(Point2D(s[0],s[1]),Point2D(e[0],e[1]),thickness=240,wall_type=WallType.EXTERIOR))
    return proj

def create_studio():
    proj=InteriorProject("Studio开间")
    for n,rt,cs in [("客卧一体",RoomType.LIVING_ROOM,[(500,500),(6000,500),(6000,4500),(500,4500)]),("厨房",RoomType.KITCHEN,[(500,5000),(3000,5000),(3000,6500),(500,6500)]),("卫生间",RoomType.BATHROOM,[(3500,5000),(6000,5000),(6000,6500),(3500,6500)])]:
        r=Room(n,rt,[Point2D(x,y) for x,y in cs]); r.calculate_area(); proj.rooms.append(r)
    for s,e in [((0,0),(6500,0)),((6500,0),(6500,7000)),((6500,7000),(0,7000)),((0,7000),(0,0))]:
        proj.walls.append(Wall(Point2D(s[0],s[1]),Point2D(e[0],e[1]),thickness=240,wall_type=WallType.EXTERIOR))
    return proj



@app.route("/lib/<path:fn>")
def serve_lib(fn):
    ext = Path(fn).suffix.lower()
    mime = {".js":"application/javascript",".mjs":"application/javascript",".css":"text/css"}.get(ext)
    return send_file(str(ROOT / "lib" / fn), mimetype=mime)

@app.route("/output/villa_stl/<fn>")
def serve_villa_stl(fn):
    return send_file(str(ROOT / "output" / "villa_stl" / fn))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    print(f"✨ AI Interior Design Studio on http://localhost:{port}")
    #removed webbrowser.open(f"http://localhost:{port}")).start()
    app.run(host="0.0.0.0", port=port, debug=True)

