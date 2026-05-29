#!/usr/bin/env python3
"""AI CAD Web App"""
import os, sys, json, uuid, urllib.request, traceback, webbrowser
from flask import Flask, request, jsonify, send_file, render_template_string

app = Flask(__name__)
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "output", "web_orders")
os.makedirs(OUT_DIR, exist_ok=True)
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
        svg = build_svg(params)
        open(os.path.join(od, "preview.svg"), "w", encoding="utf-8").write(svg)
        return jsonify({"s": True, "preview": "/output/" + oid + "/preview.svg", "id": oid})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"s": False, "e": str(e)})

def call_ai(prompt):
    msg = "你是CAD室内设计专家。输出JSON格式：{\\\"style\\\":\\\"风格\\\",\\\"rooms\\\":[{\\\"name\\\":\\\"房间\\\",\\\"width_mm\\\":数字,\\\"depth_mm\\\":数字}],\\\"total_area\\\":数字}"
    data = json.dumps({"model":"deepseek-chat","messages":[{"role":"system","content":msg},{"role":"user","content":prompt}],"temperature":0.3,"max_tokens":2000}).encode()
    req = urllib.request.Request(DU, data=data, headers={"Authorization":"Bearer "+DK,"Content-Type":"application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=60).read())
    text = resp["choices"][0]["message"]["content"].strip()
    if text.startswith("'''"): text = text.split("'''")[1]
    if text.startswith("json"): text = text[4:]
    return json.loads(text.strip())

def build_svg(params):
    out = ["<svg viewBox='0 0 8000 8000' xmlns='http://www.w3.org/2000/svg'>"]
    out.append("<rect width='8000' height='8000' fill='#f8f9fa'/>")
    colors = {"客厅":"#dbeafe","卧室":"#ede9fe","厨房":"#d1fae5","卫生间":"#fce7f3","餐厅":"#fef3c7","阳台":"#e0f2fe"}
    x, y = 500, 500
    for r in params.get("rooms", []):
        w = max(r.get("width_mm", 4000)//5, 100)
        d = max(r.get("depth_mm", 4000)//5, 100)
        c = colors.get(r.get("name", ""), "#f3f4f6")
        out.append(f"<rect x='{x}' y='{y}' width='{w}' height='{d}' fill='{c}' stroke='#374151' stroke-width='6' rx='6'/>")
        out.append(f"<text x='{x+w//2}' y='{y+d//2-10}' text-anchor='middle' font-size='36' font-weight='bold' fill='#1f2937'>{r.get('name','')}</text>")
        out.append(f"<text x='{x+w//2}' y='{y+d//2+30}' text-anchor='middle' font-size='24' fill='#6b7280'>{w//10}x{d//10}cm</text>")
        x += w + 200
        if x > 7000:
            x, y = 500, y+d+300
    out.append("</svg>")
    return "\n".join(out)

@app.route("/output/<oid>/<fn>")
def serve_output(oid, fn):
    return send_file(os.path.join(OUT_DIR, oid, fn))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    print(f"AI CAD on http://localhost:{port}")
    webbrowser.open(f"http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
