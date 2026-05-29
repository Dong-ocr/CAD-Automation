import json, os, sys, math

# 修正路径
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(script_dir), "src")
sys.path.insert(0, src_dir)
os.chdir(os.path.dirname(script_dir))  # cd to project root

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

walls_data = []
for w in proj.walls:
    nx, ny = w.normal()
    walls_data.append({
        "x1": w.start.x, "y1": w.start.y,
        "x2": w.end.x, "y2": w.end.y,
        "thickness": w.thickness, "height": w.height,
        "type": w.wall_type.value,
        "nx": nx, "ny": ny,
    })

rooms_data = []
for r in proj.rooms:
    rooms_data.append({
        "name": r.name, "type": r.room_type.value,
        "area": round(r.area / 1e6, 1),
        "corners": [{"x": c.x, "y": c.y} for c in r.corners],
        "center": {"x": r.center().x, "y": r.center().y},
    })

furniture_data = []
for f in proj.furniture:
    furniture_data.append({
        "name": f.name, "category": f.category.value,
        "w": f.width, "d": f.depth, "h": f.height,
        "x": f.x, "y": f.y, "rotation": f.rotation,
        "color": f.color, "room": f.room,
    })

data = {
    "name": proj.name,
    "walls": walls_data,
    "rooms": rooms_data,
    "furniture": furniture_data,
}

out_dir = os.path.join(os.path.dirname(script_dir), "output")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "interior_scene.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"JSON: {out_path}")
print(f"墙壁: {len(walls_data)}, 房间: {len(rooms_data)}, 家具: {len(furniture_data)}")
print("完成 ✓")
