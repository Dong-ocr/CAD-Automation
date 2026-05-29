#!/usr/bin/env python3
"""
🏠 家装室内设计 CAD 系统 — 一键运行
输出: DXF 施工图 + PNG 预览 + Three.js 3D 场景 + 数据 JSON
"""

import os, sys, subprocess, json, webbrowser

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(root, "src")
    out_dir = os.path.join(root, "output")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 60)
    print("  🏠 家装室内设计 CAD 系统 — 自动化生成")
    print("=" * 60)

    # 1. 导出场景 JSON + 生成 DXF
    print("\n[1/4] 📦 导出场景数据 & DXF...")
    sys.path.insert(0, src_dir)
    from interior_models import create_apartment_template_fixed, FurnitureItem, FurnitureCategory, Opening

    proj = create_apartment_template_fixed()
    proj.openings.extend([
        Opening(wall_idx=0, position=1500, width=900, height=2100, is_door=True),
        Opening(wall_idx=2, position=1000, width=800, height=2100, is_door=True),
        Opening(wall_idx=4, position=2000, width=1500, height=1500, is_door=False),
    ])
    proj.furniture.extend([
        FurnitureItem("双人床", FurnitureCategory.BED, 1800, 2000, 500, x=2000, y=1500, color="#D2B48C", room="主卧"),
        FurnitureItem("衣柜", FurnitureCategory.CABINET, 1800, 600, 2400, x=300, y=500, color="#8B6914", room="主卧"),
        FurnitureItem("床头柜", FurnitureCategory.CABINET, 500, 450, 550, x=500, y=2500, color="#D2B48C", room="主卧"),
        FurnitureItem("三人沙发", FurnitureCategory.SOFA, 2200, 850, 800, x=2000, y=7500, color="#8B4513", room="客厅"),
        FurnitureItem("茶几", FurnitureCategory.TABLE, 1200, 600, 450, x=2500, y=8500, color="#D2691E", room="客厅"),
        FurnitureItem("电视柜", FurnitureCategory.CABINET, 1800, 400, 500, x=2000, y=5500, color="#3C3C3C", room="客厅"),
        FurnitureItem("餐桌", FurnitureCategory.TABLE, 1400, 800, 750, x=8000, y=7500, color="#DEB887", room="餐厅"),
        FurnitureItem("餐椅", FurnitureCategory.CHAIR, 450, 450, 850, x=7500, y=7200, color="#8B7355", room="餐厅"),
        FurnitureItem("餐椅", FurnitureCategory.CHAIR, 450, 450, 850, x=8500, y=7200, color="#8B7355", room="餐厅"),
        FurnitureItem("餐椅", FurnitureCategory.CHAIR, 450, 450, 850, x=7500, y=7800, color="#8B7355", room="餐厅"),
        FurnitureItem("餐椅", FurnitureCategory.CHAIR, 450, 450, 850, x=8500, y=7800, color="#8B7355", room="餐厅"),
        FurnitureItem("马桶", FurnitureCategory.SANITARY, 400, 700, 600, x=6200, y=4200, color="#F5F5F5", room="卫生间"),
        FurnitureItem("洗手盆", FurnitureCategory.SANITARY, 600, 500, 800, x=6500, y=4500, color="#FFFFFF", room="卫生间"),
        FurnitureItem("冰箱", FurnitureCategory.APPLIANCE, 900, 800, 1800, x=7500, y=4200, color="#C0C0C0", room="厨房"),
        FurnitureItem("书桌", FurnitureCategory.TABLE, 1200, 600, 750, x=7500, y=1500, color="#C4A882", room="次卧"),
    ])

    # JSON 导出
    json_path = os.path.join(out_dir, "interior_scene.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(proj.to_json())
    print(f"  ✅ JSON: {json_path}")

    # DXF 导出
    from interior_dxf import render_dxf
    dxf_path = os.path.join(out_dir, "interior_floorplan.dxf")
    render_dxf(proj, dxf_path)
    print(f"  ✅ DXF: {dxf_path}")

    # 导出为 Three.js 格式
    walls_data = []
    for w in proj.walls:
        nx, ny = w.normal()
        walls_data.append({
            "x1": w.start.x, "y1": w.start.y, "x2": w.end.x, "y2": w.end.y,
            "thickness": w.thickness, "height": w.height, "type": w.wall_type.value,
            "nx": nx, "ny": ny,
        })
    rooms_data = []
    for r in proj.rooms:
        rooms_data.append({
            "name": r.name, "type": r.room_type.value, "area": round(r.area / 1e6, 1),
            "corners": [{"x": c.x, "y": c.y} for c in r.corners],
            "center": {"x": r.center().x, "y": r.center().y},
        })
    furniture_data = []
    for f in proj.furniture:
        furniture_data.append({
            "name": f.name, "category": f.category.value,
            "w": f.width, "d": f.depth, "h": f.height,
            "x": f.x, "y": f.y, "rotation": f.rotation, "color": f.color, "room": f.room,
        })
    three_data = {"name": proj.name, "walls": walls_data, "rooms": rooms_data, "furniture": furniture_data}
    three_json_path = os.path.join(out_dir, "interior_scene.json")
    with open(three_json_path, "w", encoding="utf-8") as f:
        json.dump(three_data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 3D 数据: {three_json_path}")

    # 2. 生成 PNG 预览
    print("\n[2/4] 🖼️ 生成平面图预览...")
    try:
        from interior_dxf import render_svg
        png_path = os.path.join(out_dir, "interior_floorplan.png")
        render_svg(proj, png_path)
        print(f"  ✅ PNG: {png_path}")
    except Exception as e:
        print(f"  ⚠️ PNG 渲染跳过: {e}")

    # 3. 输出统计
    print("\n[3/4] 📊 生成报告...")
    total_area = sum(r.area for r in proj.rooms) / 1e6
    print(f"  🏠 户型: {proj.name}")
    print(f"  📐 总面积: {total_area:.1f} m²")
    print(f"  🚪 房间: {len(proj.rooms)} 个")
    print(f"  🛋️  家具: {len(proj.furniture)} 件")
    print(f"  🧱 墙壁: {len(proj.walls)} 面")
    for r in proj.rooms:
        print(f"    {r.name}: {r.area/1e6:.1f}m²")

    # 4. 启动 Web 服务器
    print("\n[4/4] 🌐 启动 3D 查看器...")
    import http.server
    import socketserver
    import threading
    import time

    PORT = 8765
    handler = http.server.SimpleHTTPRequestHandler

    httpd = socketserver.TCPServer(("", PORT), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    url = f"http://localhost:{PORT}/interior_index.html"
    print(f"\n  🎯 3D 室内查看器: {url}")
    webbrowser.open(url)

    print(f"\n  📁 DXF 施工图: file:///{dxf_path.replace(os.sep, '/')}")
    print(f"\n  💡 提示: 按 Ctrl+C 停止服务")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n  👋 服务已停止")
        httpd.shutdown()

if __name__ == "__main__":
    main()
