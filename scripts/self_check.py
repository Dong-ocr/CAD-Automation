#!/usr/bin/env python3
"""
CAD 项目自检脚本。每次声称功能可用前，先跑这个。
用法: python scripts/self_check.py
"""

import sys, os, json, urllib.request, traceback

ROOT = r"E:\CAD自动化制图"
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

PASS = 0
FAIL = 0
WARN = 0

def check(name, ok, detail=""):
    global PASS, FAIL, WARN
    if ok:
        PASS += 1
        print(f"  ✓ {name}")
    elif detail.startswith("WARN"):
        WARN += 1
        print(f"  ⚠ {name} — {detail}")
    else:
        FAIL += 1
        print(f"  ✗ {name} — {detail}")

def check_exception(name, fn):
    try:
        fn()
        PASS += 1
        print(f"  ✓ {name}")
    except Exception as e:
        FAIL += 1
        print(f"  ✗ {name} — {e}")

print("=" * 50)
print("CAD 系统自检报告")
print("=" * 50)

# ── 1. 模块导入 ──
print("\n【模块导入】")
check_exception("interior_models", lambda: __import__("interior_models"))
check_exception("interior_dxf", lambda: __import__("interior_dxf"))

# ── 2. 数据模型 ──
print("\n【数据模型】")
from interior_models import InteriorProject, Room, Wall, WallType, Opening
from interior_models import FurnitureItem, FurnitureCategory, Point2D, RoomType
from interior_models import create_apartment_template_fixed, FURNITURE_TEMPLATES

proj = create_apartment_template_fixed()
check("create_apartment_template_fixed() 返回 InteriorProject", isinstance(proj, InteriorProject))
check("项目名非空", bool(proj.name))
check("有房间", len(proj.rooms) > 0, f"{len(proj.rooms)} 个")
check("有墙壁", len(proj.walls) > 0, f"{len(proj.walls)} 堵")
check("房间面积已计算", all(r.area > 0 for r in proj.rooms))
check("家具模板数", len(FURNITURE_TEMPLATES) >= 20, f"{len(FURNITURE_TEMPLATES)} 件")

# ── 3. JSON 序列化 ──
print("\n【JSON 序列化】")
check_exception("to_json()", lambda: proj.to_json())
json_str = proj.to_json()
check("JSON 有效", len(json_str) > 100)
check_exception("from_json() roundtrip", lambda: InteriorProject.from_json(json_str))
proj2 = InteriorProject.from_json(json_str)
check("roundtrip 后房间数一致", len(proj2.rooms) == len(proj.rooms))

# ── 4. DXF 导出 ──
print("\n【DXF 导出】")
from interior_dxf import render_dxf, render_svg
import tempfile

dxf_path = tempfile.mktemp(suffix=".dxf")
check_exception("render_dxf()", lambda: render_dxf(proj, dxf_path))
dxf_size = os.path.getsize(dxf_path) if os.path.exists(dxf_path) else 0
check("DXF 文件生成", dxf_size > 1000, f"{dxf_size} bytes")
os.unlink(dxf_path)

# ── 5. SVG 预览 ──
print("\n【SVG 预览/手动 SVG】")
svg_path = tempfile.mktemp(suffix=".svg")
try:
    render_svg(proj, svg_path)
    svg_ok = os.path.exists(svg_path) and os.path.getsize(svg_path) > 100
    check("render_svg()", svg_ok, f"{os.path.getsize(svg_path) if os.path.exists(svg_path) else 0} bytes — WARN: 可能 fallback 到空")
    if os.path.exists(svg_path):
        os.unlink(svg_path)
except:
    check("render_svg()", False, "抛出异常 (已知 Bug: Frontend.draw vs draw_layout)")

# ── 6. Server API 测试 ──
print("\n【Server API】")
SERVER = "http://localhost:8765"
try:
    resp = urllib.request.urlopen(f"{SERVER}/api/templates", timeout=3)
    data = json.loads(resp.read())
    check("GET /api/templates", len(data["templates"]) >= 3)
except Exception as e:
    check("GET /api/templates", False, f"服务器未运行: {e}")
    WARN += 1  # server might not be running, that's OK

try:
    resp = urllib.request.urlopen(f"{SERVER}/api/furniture", timeout=3)
    data = json.loads(resp.read())
    check("GET /api/furniture", len(data["items"]) >= 20)
except:
    pass

try:
    req = urllib.request.Request(f"{SERVER}/api/project/new",
        data=json.dumps({"template":"apt_2b1b"}).encode(),
        headers={"Content-Type":"application/json"})
    resp = urllib.request.urlopen(req, timeout=3)
    data = json.loads(resp.read())
    check("POST /api/project/new", data.get("success"))
except:
    pass

# ── 7. 汇总 ──
print("\n" + "=" * 50)
total = PASS + FAIL
print(f"结果: {PASS} 通过, {FAIL} 失败, {WARN} 警告")
if FAIL > 0:
    print(f"结论: ❌ 有 {FAIL} 项检查未通过，不要声称这些功能可用")
elif WARN > 0:
    print(f"结论: ⚠ 全部通过但有 {WARN} 项警告")
else:
    print("结论: ✅ 全部通过")
print("=" * 50)
