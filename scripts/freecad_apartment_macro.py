#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FreeCAD 室内设计 3D 宏 — 两室一厅精装户型
运行方式: 在 FreeCAD 中: Macro → Execute macro, 或命令行:
  freecadcmd.exe scripts\freecad_apartment_macro.py

生成内容:
  - 240mm 外墙 + 150mm 内墙 (高 2800mm)
  - 楼板 / 天花板
  - 门洞 + 窗洞
  - 家具: 沙发、餐桌椅、双人床、衣柜、橱柜、马桶等
  - 分组管理 + 颜色区分
"""

import sys, os, math

# ── FreeCAD 环境 ────────────────────────────────────────
FC_BIN = r"E:\CAD自动化制图\FreeCAD\FreeCAD_1.1.1-Windows-x86_64-py311\bin"
for p in [
    os.path.join(FC_BIN, "..", "Lib"),
    os.path.join(FC_BIN, "..", "Mod"),
    FC_BIN,
    os.path.join(FC_BIN, "..", "lib"),
]:
    pp = os.path.normpath(p)
    if pp not in sys.path:
        sys.path.insert(0, pp)

import FreeCAD
import FreeCADGui
import Part
from FreeCAD import Base, Vector

# ── 常量 ─────────────────────────────────────────────────
WALL_H = 2800.0        # 墙高 mm
SLAB_THK = 200.0       # 楼板厚
DOOR_W = 900.0         # 门宽
DOOR_H = 2100.0        # 门高
WINDOW_W = 1500.0      # 窗宽
WINDOW_H = 1500.0      # 窗高
WINDOW_SILL = 900.0    # 窗台高
EXT_T = 240.0          # 外墙厚
INT_T = 150.0          # 内墙厚

COLORS = {
    "exterior_wall": (0.75, 0.75, 0.75, 0.0),
    "interior_wall": (0.85, 0.85, 0.85, 0.0),
    "floor":         (0.60, 0.50, 0.35, 0.0),
    "ceiling":       (0.90, 0.90, 0.90, 0.0),
    "sofa":          (0.54, 0.27, 0.07, 0.0),
    "bed":           (0.40, 0.60, 0.80, 0.0),
    "table":         (0.73, 0.56, 0.36, 0.0),
    "chair":         (0.55, 0.35, 0.15, 0.0),
    "cabinet":       (0.60, 0.40, 0.20, 0.0),
    "door":          (0.68, 0.48, 0.24, 0.0),
    "window_frame":  (0.50, 0.70, 0.90, 0.0),
    "window_glass":  (0.75, 0.88, 0.98, 0.30),
    "appliance":     (0.80, 0.80, 0.85, 0.0),
    "toilet":        (0.90, 0.90, 0.95, 0.0),
    "lamp":          (0.95, 0.85, 0.50, 0.0),
}

# ── 工具函数 ────────────────────────────────────────────

def set_color(obj, name):
    """为对象设置颜色"""
    try:
        rgb = COLORS.get(name, (0.8, 0.8, 0.8, 0.0))
        vo = obj.ViewObject
        if vo is None:
            return
        vo.ShapeColor = (rgb[0], rgb[1], rgb[2])
        if len(rgb) > 3 and rgb[3] > 0:
            vo.Transparency = int(rgb[3] * 100)
    except Exception:
        pass

def make_box(length, width, height, pos=(0, 0, 0), name="Box", color=None):
    """创建 Box 并设置位置"""
    b = doc.addObject("Part::Box", name)
    b.Length = length
    b.Width = width
    b.Height = height
    b.Placement = Base.Placement(Vector(*pos), Base.Rotation())
    if color:
        set_color(b, color)
    return b

def make_cylinder(radius, height, pos=(0, 0, 0), name="Cylinder", color=None):
    c = doc.addObject("Part::Cylinder", name)
    c.Radius = radius
    c.Height = height
    c.Placement = Base.Placement(Vector(*pos), Base.Rotation())
    if color:
        set_color(c, color)
    return c

def wall_between(x1, y1, x2, y2, thick, height, name="Wall", color="interior_wall"):
    """在两点之间创建墙体"""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 1:
        return None
    angle = math.atan2(dy, dx)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    b = make_box(length, thick, height,
                 pos=(cx - length/2, cy - thick/2, 0),
                 name=name, color=color)
    b.Placement.Rotation = Base.Rotation(Vector(0, 0, 1), math.degrees(angle))
    b.Placement.Base = Vector(cx, cy, 0)
    return b

def cut_opening(wall_obj, cx, cy, w, h, z=0):
    """在墙体上切割门/窗洞"""
    hole = make_box(w, 500, h, (cx - w/2, cy - 250, z),
                    name="TempCut", color=None)
    # FreeCAD Boolean cut via Part::Cut
    cut = doc.addObject("Part::Cut", "Cut_" + wall_obj.Name)
    cut.Base = wall_obj
    cut.Tool = hole
    cut.Label = wall_obj.Label
    return cut

def add_opening_to_wall(wall_obj, wall_x1, wall_y1, wall_x2, wall_y2,
                         thick, offset, width, height, sill=0):
    """在墙上切洞，返回切割后的对象"""
    dx, dy = wall_x2 - wall_x1, wall_y2 - wall_y1
    length = math.hypot(dx, dy)
    if length < 1:
        return wall_obj
    # 沿墙壁方向偏移
    ratio = (offset + width/2) / length
    cx = wall_x1 + dx * ratio
    cy = wall_y1 + dy * ratio
    hole = make_box(width, thick + 10, height,
                    pos=(cx - width/2, cy - thick/2 - 5, sill),
                    name="Hole", color=None)
    cut = doc.addObject("Part::Cut", "Cut_" + wall_obj.Name)
    cut.Base = wall_obj
    cut.Tool = hole
    cut.Label = wall_obj.Label
    return cut

def group_objects(name, objs):
    """将对象归组"""
    grp = doc.addObject("App::DocumentObjectGroup", name)
    grp.Label = name
    for o in objs:
        if o:
            grp.addObject(o)
    return grp

# ══════════════════════════════════════════════════════════
#  主构建函数
# ══════════════════════════════════════════════════════════

def build_apartment():
    """构建两室一厅精装户型 FreeCAD 3D 模型"""
    global doc
    doc = FreeCAD.newDocument("ApartmentInterior")
    doc.Label = "两室一厅精装户型 - FreeCAD 3D"

    # ========================================================
    # 1. 楼板 (10000 x 10000)
    # ========================================================
    floor = make_box(10000, 10000, SLAB_THK,
                     pos=(0, 0, -SLAB_THK),
                     name="Floor", color="floor")

    # ========================================================
    # 2. 外墙 (外轮廓)
    # ========================================================
    ext_walls = []
    ext_pts = [(0, 0), (10000, 0), (10000, 10000), (0, 10000)]
    wall_objs = []
    for i in range(4):
        x1, y1 = ext_pts[i]
        x2, y2 = ext_pts[(i + 1) % 4]
        w = wall_between(x1, y1, x2, y2, EXT_T, WALL_H,
                         name=f"外墙_{i+1}", color="exterior_wall")
        wall_objs.append(w)
        ext_walls.append((x1, y1, x2, y2))

    # 在外墙上开门窗
    # 南墙 (下边 y=0): 主卧窗 + 次卧窗
    w0 = wall_objs[0]  # (0,0) -> (10000,0)
    w0 = add_opening_to_wall(w0, 0, 0, 10000, 0, EXT_T, 1400, WINDOW_W, WINDOW_H, WINDOW_SILL)  # 主卧窗
    w0 = add_opening_to_wall(w0, 0, 0, 10000, 0, EXT_T, 6400, WINDOW_W, WINDOW_H, WINDOW_SILL)  # 次卧窗

    # 东墙 (右边 x=10000): 客厅窗
    w1 = wall_objs[1]  # (10000,0) -> (10000,10000)
    w1 = add_opening_to_wall(w1, 10000, 0, 10000, 10000, EXT_T, 2000, WINDOW_W, WINDOW_H, WINDOW_SILL)
    w1 = add_opening_to_wall(w1, 10000, 0, 10000, 10000, EXT_T, 6000, WINDOW_W, WINDOW_H, WINDOW_SILL)

    # 北墙 (上边 y=10000): 厨房窗 + 大门
    w2 = wall_objs[2]  # (10000,10000) -> (0,10000)
    w2 = add_opening_to_wall(w2, 10000, 10000, 0, 10000, EXT_T, 7500, WINDOW_W, WINDOW_H, WINDOW_SILL)  # 厨房窗
    # 大门
    w2 = add_opening_to_wall(w2, 10000, 10000, 0, 10000, EXT_T, 500, DOOR_W, DOOR_H, 0)

    # ========================================================
    # 3. 内墙
    # ========================================================
    int_wall_data = [
        ((0, 4000),  (4500, 4000)),    # 主卧上
        ((5500, 4000), (10000, 4000)),  # 次卧上
        ((4500, 0),   (4500, 5000)),    # 过道左
        ((5500, 0),   (5500, 5000)),    # 过道右
        ((6000, 4000), (6000, 5000)),   # 卫生间左
        ((7000, 4000), (7000, 5000)),   # 厨卫分隔
        ((6000, 5000), (6000, 10000)),  # 客厅右
        ((0, 5000),   (10000, 5000)),   # 横向主分隔
    ]
    int_wall_objs = []
    for i, ((x1, y1), (x2, y2)) in enumerate(int_wall_data):
        w = wall_between(x1, y1, x2, y2, INT_T, WALL_H,
                         name=f"内墙_{i+1}", color="interior_wall")
        int_wall_objs.append(w)

    # 内墙开门洞
    # 卧室门 (过道左右墙)
    # 内墙[2] = 过道左 (4500,0)-(4500,5000)
    iw2 = int_wall_objs[2]
    if iw2:
        iw2 = add_opening_to_wall(iw2, 4500, 0, 4500, 5000, INT_T, 1800, DOOR_W, DOOR_H, 0)

    # 内墙[3] = 过道右 (5500,0)-(5500,5000)
    iw3 = int_wall_objs[3]
    if iw3:
        iw3 = add_opening_to_wall(iw3, 5500, 0, 5500, 5000, INT_T, 1800, DOOR_W, DOOR_H, 0)

    # 卫生间门 (内墙[4] = 6000,4000-6000,5000)
    iw4 = int_wall_objs[4]
    if iw4:
        iw4 = add_opening_to_wall(iw4, 6000, 4000, 6000, 5000, INT_T, 200, DOOR_W*0.7, DOOR_H, 0)

    # ========================================================
    # 4. 天花板
    # ========================================================
    ceiling = make_box(10000, 10000, 100,
                       pos=(0, 0, WALL_H),
                       name="Ceiling", color="ceiling")

    # ========================================================
    # 5. 门 (简化门板)
    # ========================================================
    def make_door(x, y, rot=0, name="门"):
        d = make_box(DOOR_W, 40, DOOR_H,
                     pos=(x - DOOR_W/2, y - 20, 0),
                     name=name, color="door")
        d.Placement.Rotation = Base.Rotation(Vector(0, 0, 1), rot)
        d.Placement.Base = Vector(x, y, 0)
        return d

    doors = [
        make_door(950, 10000, 0, "大门"),       # 大门
        make_door(4500, 1900, 90, "主卧门"),     # 主卧门
        make_door(5500, 1900, 90, "次卧门"),     # 次卧门
        make_door(6000, 4050, 90, "卫生间门"),   # 卫生间门
    ]

    # ========================================================
    # 6. 窗户 (窗框 + 玻璃)
    # ========================================================
    def make_window(x, y, w, h, sill, rot=0, name="窗"):
        """在 (x,y) 处创建一组窗框+玻璃"""
        frame_t = 50
        frame = make_box(w + 60, 60, h + 60,
                         pos=(x - w/2 - 30, y - 30, sill - 30),
                         name=name + "_框", color="window_frame")
        glass = make_box(w - 40, 10, h - 40,
                         pos=(x - w/2 + 20, y - 5, sill + 20),
                         name=name + "_玻璃", color="window_glass")
        return frame, glass

    windows = []
    # 主卧窗 (南墙)
    f, g = make_window(2150, 0, WINDOW_W, WINDOW_H, WINDOW_SILL, 0, "主卧窗")
    windows.extend([f, g])
    # 次卧窗 (南墙)
    f, g = make_window(7150, 0, WINDOW_W, WINDOW_H, WINDOW_SILL, 0, "次卧窗")
    windows.extend([f, g])
    # 客厅窗1 (东墙)
    f, g = make_window(10000, 2750, WINDOW_W, WINDOW_H, WINDOW_SILL, 90, "客厅窗1")
    windows.extend([f, g])
    # 客厅窗2 (东墙)
    f, g = make_window(10000, 6750, WINDOW_W, WINDOW_H, WINDOW_SILL, 90, "客厅窗2")
    windows.extend([f, g])
    # 厨房窗 (北墙)
    f, g = make_window(3100, 10000, WINDOW_W, WINDOW_H, WINDOW_SILL, 0, "厨房窗")
    windows.extend([f, g])

    # ========================================================
    # 7. 家具
    # ========================================================

    # 7a. 客厅家具 (0,5000)-(6000,10000)
    living_furniture = []
    # 三人沙发
    sofa = make_box(2200, 850, 800,
                    pos=(400, 9200, 0),
                    name="三人沙发", color="sofa")
    # 茶几
    tea_table = make_box(1200, 600, 450,
                         pos=(1800, 8200, 0),
                         name="茶几", color="table")
    # 电视柜
    tv_cabinet = make_box(2000, 450, 500,
                          pos=(200, 5200, 0),
                          name="电视柜", color="cabinet")
    # 地毯 (薄板)
    carpet = make_box(2500, 1800, 10,
                      pos=(400, 8400, 0),
                      name="地毯", color="cabinet")
    try:
        carpet.ViewObject.Transparency = 70
    except:
        pass

    living_furniture.extend([sofa, tea_table, tv_cabinet, carpet])

    # 7b. 餐厅家具 (6000,5000)-(10000,10000)
    dining_furniture = []
    # 餐桌
    dining_table = make_box(1400, 800, 750,
                            pos=(7700, 7500, 0),
                            name="餐桌", color="table")
    # 4 把餐椅
    for j, (dx, dy) in enumerate([(-600, 0), (600, 0), (0, -500), (0, 500)]):
        chair = make_box(450, 450, 850,
                         pos=(7700 + dx - 225, 7500 + dy - 225, 0),
                         name=f"餐椅_{j+1}", color="chair")
        dining_furniture.append(chair)
    dining_furniture.append(dining_table)

    # 7c. 主卧家具 (0,0)-(4500,4000)
    master_furniture = []
    # 双人床
    bed = make_box(1800, 2000, 500,
                   pos=(1300, 1000, 0),
                   name="双人床", color="bed")
    # 床头柜 x2
    nightstand1 = make_box(500, 450, 500,
                           pos=(100, 1100, 0),
                           name="床头柜1", color="cabinet")
    nightstand2 = make_box(500, 450, 500,
                           pos=(3800, 1100, 0),
                           name="床头柜2", color="cabinet")
    # 衣柜
    wardrobe = make_box(1800, 600, 2200,
                        pos=(200, 3400, 0),
                        name="衣柜", color="cabinet")
    # 台灯 x2
    lamp1 = make_cylinder(100, 400,
                          pos=(350, 1325, 500),
                          name="台灯1", color="lamp")
    lamp2 = make_cylinder(100, 400,
                          pos=(4050, 1325, 500),
                          name="台灯2", color="lamp")
    master_furniture.extend([bed, nightstand1, nightstand2, wardrobe, lamp1, lamp2])

    # 7d. 次卧家具 (5500,0)-(10000,4000)
    guest_furniture = []
    # 单人床
    single_bed = make_box(1200, 2000, 500,
                          pos=(6800, 1000, 0),
                          name="单人床", color="bed")
    # 书桌
    desk = make_box(1200, 600, 750,
                    pos=(6800, 3300, 0),
                    name="书桌", color="table")
    # 椅子
    desk_chair = make_box(450, 450, 850,
                          pos=(6800 - 225, 2800 - 225, 0),
                          name="书椅", color="chair")
    # 衣柜 (小)
    small_wardrobe = make_box(1200, 600, 2000,
                              pos=(8700, 3400, 0),
                              name="次卧衣柜", color="cabinet")
    guest_furniture.extend([single_bed, desk, desk_chair, small_wardrobe])

    # 7e. 厨房 (7000,4000)-(10000,5000)
    kitchen_furniture = []
    # L型橱柜
    cabinet1 = make_box(2800, 600, 850,
                        pos=(7200, 4400, 0),
                        name="橱柜1", color="cabinet")
    cabinet2 = make_box(600, 1000, 850,
                        pos=(9400, 4500, 0),
                        name="橱柜2", color="cabinet")
    # 冰箱
    fridge = make_box(700, 700, 1800,
                      pos=(8500, 4400, 0),
                      name="冰箱", color="appliance")
    # 灶台 (用薄片表示)
    stove = make_box(600, 500, 50,
                     pos=(7700, 4400, 850),
                     name="灶台", color="appliance")
    kitchen_furniture.extend([cabinet1, cabinet2, fridge, stove])

    # 7f. 卫生间 (6000,4000)-(7000,5000)
    bath_furniture = []
    toilet = make_box(400, 500, 600,
                      pos=(6100, 4100, 0),
                      name="马桶", color="toilet")
    washbasin = make_box(500, 400, 800,
                         pos=(6200, 4800, 0),
                         name="洗手台", color="toilet")
    bathtub = make_box(600, 1400, 400,
                       pos=(6500, 4300, 0),
                       name="浴缸", color="toilet")
    bath_furniture.extend([toilet, washbasin, bathtub])

    # ========================================================
    # 8. 分组
    # ========================================================
    # 收集所有有效对象
    all_objs = [o for o in doc.Objects if o.Name != "TempCut" and not o.Name.startswith("Hole")]

    # 创建分组
    walls_group = group_objects("墙体", [o for o in doc.Objects
                                          if o.Name.startswith("外墙") or o.Name.startswith("内墙")
                                          or o.Name.startswith("Cut_")])
    floors_group = group_objects("楼板", [floor, ceiling])
    doors_group = group_objects("门窗", doors + windows)
    living_group = group_objects("客厅家具", living_furniture)
    dining_group = group_objects("餐厅家具", dining_furniture)
    master_group = group_objects("主卧家具", master_furniture)
    guest_group = group_objects("次卧家具", guest_furniture)
    kitchen_group = group_objects("厨房", kitchen_furniture)
    bath_group = group_objects("卫生间", bath_furniture)

    doc.recompute()
    return doc

# ══════════════════════════════════════════════════════════
#  入口
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  FreeCAD 室内设计 3D 生成器")
    print("  两室一厅精装户型 (10m x 10m)")
    print("=" * 60)

    doc = build_apartment()

    # 导出
    output_dir = "E:/CAD自动化制图/output/professional"
    os.makedirs(output_dir, exist_ok=True)

    # FCStd
    fcstd_path = os.path.join(output_dir, "apartment_interior.fcstd")
    doc.saveAs(fcstd_path)
    print(f"\n✅ FreeCAD 文件: {fcstd_path}")

    # STEP
    try:
        shapes = [o.Shape for o in doc.Objects
                  if hasattr(o, "Shape") and not o.Shape.isNull()
                  and not o.Name.startswith("Temp") and not o.Name.startswith("Hole")]
        if shapes:
            compound = Part.makeCompound(shapes)
            step_path = os.path.join(output_dir, "apartment_interior.step")
            compound.exportStep(step_path)
            print(f"✅ STEP 文件: {step_path}")
    except Exception as e:
        print(f"⚠️ STEP 导出失败: {e}")

    # 统计
    n_walls = len([o for o in doc.Objects if "外墙" in o.Label or "内墙" in o.Label or o.Name.startswith("Cut_")])
    n_furn = len([o for o in doc.Objects if
                  any(kw in o.Label for kw in ["沙发", "茶几", "电视柜", "餐桌", "餐椅", "床", "床头柜",
                                                "衣柜", "台灯", "书桌", "书椅", "橱柜", "冰箱", "灶台",
                                                "马桶", "洗手台", "浴缸", "地毯", "门"])])
    print(f"\n📊 统计:")
    print(f"   墙体对象: {n_walls}")
    print(f"   家具数量: {n_furn}")
    print(f"   总对象数: {len(doc.Objects)}")
    print(f"\n💡 在 FreeCAD 中打开 {fcstd_path} 查看完整 3D 场景")
    print("=" * 60)
