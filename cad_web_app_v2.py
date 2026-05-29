#!/usr/bin/env python3
"""AI CAD Web App v2 - 接入真实 CAD 模块"""
import os, sys, json, uuid, urllib.request, traceback, webbrowser
from flask import Flask, request, jsonify, send_file, render_template_string

app = Flask(__name__)
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "output", "web_orders")
SRC_DIR = os.path.join(ROOT, "src")
os.makedirs(OUT_DIR, exist_ok=True)
sys.path.insert(0, SRC_DIR)

DK = os.environ.get("DEEPSEEK_KEY", "sk-329e23b7df6947419dd41fd08ea184c4")
DU = "https://api.deepseek.com/v1/chat/completions"

HTML = open(os.path.join(ROOT, "cad_web_template.html"), encoding="utf-8").read()

@app.route("/")
def idx():
    return render_template_string(HTML)

@app.route("/api/design", methods=["POST"])
def design():
    p = request.json.get("prompt", "")
    if not p:
        return jsonify({"s": False, "e": "请输入设计需求"})
    try:
        params = call_ai(p)
        oid = uuid.uuid4().hex[:8]
        od = os.path.join(OUT_DIR, oid)
        os.makedirs(od, exist_ok=True)
        json.dump(params, open(os.path.join(od, "params.json"), "w"), ensure_ascii=False, indent=2)

        # 生成真实 DXF
        dxf_path = os.path.join(od, "floorplan.dxf")
        preview_path = os.path.join(od, "preview.svg")
        gen_cad(params, dxf_path, preview_path)

        return jsonify({
            "s": True,
            "preview": "/output/" + oid + "/preview.svg",
            "dxf": "/output/" + oid + "/floorplan.dxf",
            "id": oid,
            "params": params
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"s": False, "e": str(e)})

def call_ai(prompt):
    msg = "你是CAD室内设计专家。分析需求输出JSON：{\"style\":\"风格\",\"rooms\":[\"客厅\",\"卧室\"...],\"total_area\":数字,\"description\":\"描述\"}"
    data = json.dumps({"model":"deepseek-chat","messages":[{"role":"system","content":msg},{"role":"user","content":prompt}],"temperature":0.3,"max_tokens":2000}).encode()
    req = urllib.request.Request(DU, data=data, headers={"Authorization":"Bearer "+DK,"Content-Type":"application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=60).read())
    text = resp["choices"][0]["message"]["content"].strip()
    if text.startswith("'''"): text = text.split("'''")[1]
    if text.startswith("json"): text = text[4:]
    return json.loads(text.strip())

def gen_cad(params, dxf_path, preview_path):
    """生成 CAD 图纸和预览"""
    try:
        from interior_models import InteriorProject, Room, RoomType, Wall, Point2D
        from interior_models import FurnitureItem, FurnitureCategory
        from interior_dxf import render_dxf

        # 用模板生成基础户型
        from interior_models import create_apartment_template_fixed
        proj = create_apartment_template_fixed()
        proj.name = params.get("description", "AI 设计户型")

        # 导出 DXF
        render_dxf(proj, dxf_path)

        # 生成 SVG 预览
        svg_lines = ['<svg viewBox="-500 -500 11000 11000" xmlns="http://www.w3.org/2000/svg">']
        svg_lines.append('<rect x="-500" y="-500" width="11000" height="11000" fill="#f8f9fa"/>')

        # 画房间
        colors = {"客厅":"#dbeafe","卧室":"#ede9fe","厨房":"#d1fae5","卫生间":"#fce7f3","餐厅":"#fef3c7","阳台":"#e0f2fe","书房":"#fef9c3","衣帽间":"#e0e7ff"}
        for r in proj.rooms:
            if not r.corners: continue
            pts = r.corners
            xs = [p.x for p in pts]
            ys = [p.y for p in pts]
            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)
            w = max(xs) - min(xs)
            d = max(ys) - min(ys)
            c = colors.get(r.name, "#f3f4f6")
            points_str = " ".join([f"{p.x},{p.y}" for p in pts])
            svg_lines.append(f'<polygon points="{points_str}" fill="{c}" stroke="#374151" stroke-width="4"/>')
            svg_lines.append(f'<text x="{cx}" y="{cy-8}" text-anchor="middle" font-size="36" font-weight="bold" fill="#1f2937">{r.name}</text>')
            svg_lines.append(f'<text x="{cx}" y="{cy+32}" text-anchor="middle" font-size="24" fill="#6b7280">{w//10}x{d//10}cm</text>')

        # 画门
        for op in proj.openings:
            if not op.is_door: continue
            # Get the wall this door is on
            if proj.walls and op.wall_idx < len(proj.walls):
                w = proj.walls[op.wall_idx]
                dx = w.end.x - w.start.x
                dy = w.end.y - w.start.y
                length = (dx*dx + dy*dy)**0.5
                if length > 0:
                    ratio = op.position / length
                    cx = w.start.x + dx * ratio
                    cy = w.start.y + dy * ratio
                    svg_lines.append(f'<circle cx="{cx}" cy="{cy}" r="{op.width//2}" fill="none" stroke="#f59e0b" stroke-width="4" stroke-dasharray="6,3"/>')
                    svg_lines.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+dx/length*op.width}" y2="{cy+dy/length*op.width}" stroke="#f59e0b" stroke-width="3"/>')

        # 画家具
        for f in proj.furniture:
            svg_lines.append(f'<rect x="{f.x}" y="{f.y}" width="{f.w}" height="{f.d}" fill="{f.color}" stroke="#1f2937" stroke-width="2" rx="3" opacity="0.7"/>')
            svg_lines.append(f'<text x="{f.x+f.w//2}" y="{f.y+f.d//2}" text-anchor="middle" font-size="18" fill="#fff">{f.name}</text>')

        svg_lines.append("</svg>")
        open(preview_path, "w", encoding="utf-8").write("\n".join(svg_lines))

    except ImportError as e:
        # 如果 CAD 模块没装，fallback 到简单 SVG
        open(dxf_path, "w").write("")  # 空文件
        svg = "<svg viewBox='0 0 8000 8000' xmlns='http://www.w3.org/2000/svg'><rect width='8000' height='8000' fill='#f8f9fa'/>"
        svg += "<text x='4000' y='4000' text-anchor='middle' font-size='40' fill='#ef4444'>CAD 模块未加载: " + str(e) + "</text></svg>"
        open(preview_path, "w", encoding="utf-8").write(svg)

@app.route("/output/<oid>/<fn>")
def serve_output(oid, fn):
    return send_file(os.path.join(OUT_DIR, oid, fn))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    print(f"AI CAD v2 on http://localhost:{port}")
    # webbrowser.open(f"http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
