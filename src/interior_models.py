"""
家装室内设计 CAD — 核心数据模型
参考 blueprint3D 架构: model/ → floorplanner/ → three/ → items/
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import json, math

# ── 枚举 ─────────────────────────────────────────────────

class RoomType(Enum):
    LIVING_ROOM = "客厅"
    BEDROOM = "卧室"
    KITCHEN = "厨房"
    BATHROOM = "卫生间"
    DINING_ROOM = "餐厅"
    STUDY = "书房"
    BALCONY = "阳台"
    HALLWAY = "过道"
    STORAGE = "储物间"

class WallType(Enum):
    EXTERIOR = "外墙"
    INTERIOR = "内墙"
    PARTITION = "隔断"

class FurnitureCategory(Enum):
    BED = "床"
    SOFA = "沙发"
    TABLE = "桌子"
    CHAIR = "椅子"
    CABINET = "柜子"
    APPLIANCE = "电器"
    SANITARY = "卫浴"
    LIGHTING = "灯具"
    DECORATION = "装饰"

# ── 数据模型 ─────────────────────────────────────────────

@dataclass
class Point2D:
    x: float
    y: float

    def to_tuple(self): return (self.x, self.y)
    def distance_to(self, other: Point2D) -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

@dataclass
class Wall:
    start: Point2D
    end: Point2D
    thickness: float = 200.0   # mm
    wall_type: WallType = WallType.EXTERIOR
    height: float = 2800.0     # mm

    def length(self) -> float:
        return self.start.distance_to(self.end)

    def angle(self) -> float:
        return math.atan2(self.end.y - self.start.y, self.end.x - self.start.x)

    def normal(self) -> tuple[float, float]:
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        length = math.hypot(dx, dy)
        return (-dy / length, dx / length) if length else (0, 0)

@dataclass
class Opening:
    """门或窗的洞口"""
    wall_idx: int
    position: float          # 沿墙壁的偏移量 (mm)
    width: float             # 洞口宽度
    height: float            # 洞口高度
    is_door: bool = True     # True=门, False=窗
    sill_height: float = 0.0 if True else 800.0  # 窗台高

@dataclass
class Room:
    name: str
    room_type: RoomType
    corners: list[Point2D]   # 房间多边形顶点 (逆时针)
    area: float = 0.0
    level: float = 0.0       # 标高

    def calculate_area(self):
        """计算多边形面积"""
        n = len(self.corners)
        if n < 3: return 0.0
        s = 0.0
        for i in range(n):
            j = (i + 1) % n
            s += self.corners[i].x * self.corners[j].y
            s -= self.corners[j].x * self.corners[i].y
        self.area = abs(s) / 2
        return self.area

    def center(self) -> Point2D:
        cx = sum(c.x for c in self.corners) / len(self.corners)
        cy = sum(c.y for c in self.corners) / len(self.corners)
        return Point2D(cx, cy)

@dataclass
class FurnitureItem:
    name: str
    category: FurnitureCategory
    width: float             # mm
    depth: float             # mm
    height: float = 800.0
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0    # 角度 (度)
    color: str = "#cccccc"
    room: str = ""
    fixed: bool = False      # 是否固定（如橱柜）

    def bbox(self):
        """返回包围盒 [x_min, y_min, x_max, y_max]"""
        hw, hd = self.width / 2, self.depth / 2
        rad = math.radians(self.rotation)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        corners = [
            ( -hw, -hd), (  hw, -hd),
            (  hw,  hd), ( -hw,  hd)
        ]
        xs, ys = [], []
        for dx, dy in corners:
            rx = self.x + dx * cos_a - dy * sin_a
            ry = self.y + dx * sin_a + dy * cos_a
            xs.append(rx)
            ys.append(ry)
        return (min(xs), min(ys), max(xs), max(ys))

# ── 家具库（标准尺寸） ──────────────────────────────────────

FURNITURE_TEMPLATES = {
    "双人床":    FurnitureItem("双人床", FurnitureCategory.BED, 1800, 2000, 500),
    "单人床":    FurnitureItem("单人床", FurnitureCategory.BED, 1200, 2000, 500),
    "三人沙发":  FurnitureItem("三人沙发", FurnitureCategory.SOFA, 2200, 850, 800, color="#8B4513"),
    "双人沙发":  FurnitureItem("双人沙发", FurnitureCategory.SOFA, 1600, 850, 800, color="#A0522D"),
    "茶几":      FurnitureItem("茶几", FurnitureCategory.TABLE, 1200, 600, 450, color="#D2691E"),
    "餐桌":     FurnitureItem("餐桌", FurnitureCategory.TABLE, 1400, 800, 750, color="#DEB887"),
    "餐椅":     FurnitureItem("餐椅", FurnitureCategory.CHAIR, 450, 450, 850, color="#8B7355"),
    "书桌":     FurnitureItem("书桌", FurnitureCategory.TABLE, 1200, 600, 750, color="#C4A882"),
    "衣柜":     FurnitureItem("衣柜", FurnitureCategory.CABINET, 1800, 600, 2400, color="#D2B48C"),
    "电视柜":   FurnitureItem("电视柜", FurnitureCategory.CABINET, 1800, 400, 500, color="#3C3C3C"),
    "床头柜":   FurnitureItem("床头柜", FurnitureCategory.CABINET, 500, 450, 550, color="#D2B48C"),
    "鞋柜":     FurnitureItem("鞋柜", FurnitureCategory.CABINET, 800, 350, 1000, color="#8B7355"),
    "书柜":     FurnitureItem("书柜", FurnitureCategory.CABINET, 800, 400, 2000, color="#C4A882"),
    "冰箱":     FurnitureItem("冰箱", FurnitureCategory.APPLIANCE, 900, 800, 1800, color="#C0C0C0"),
    "洗衣机":   FurnitureItem("洗衣机", FurnitureCategory.APPLIANCE, 600, 600, 850, color="#E0E0E0"),
    "马桶":     FurnitureItem("马桶", FurnitureCategory.SANITARY, 400, 700, 600, color="#F5F5F5"),
    "洗手盆":   FurnitureItem("洗手盆", FurnitureCategory.SANITARY, 600, 500, 800, color="#FFFFFF"),
    "浴缸":     FurnitureItem("浴缸", FurnitureCategory.SANITARY, 1700, 750, 600, color="#F0F0F0"),
    "淋浴房":   FurnitureItem("淋浴房", FurnitureCategory.SANITARY, 900, 900, 2000, color="#E8E8E8"),
    "橱柜(地柜)": FurnitureItem("橱柜(地柜)", FurnitureCategory.CABINET, 600, 600, 850, color="#A0A0A0", fixed=True),
    "油烟机":   FurnitureItem("油烟机", FurnitureCategory.APPLIANCE, 900, 500, 500, color="#808080"),
    "电视":     FurnitureItem("电视", FurnitureCategory.APPLIANCE, 1400, 100, 800, color="#1A1A1A"),
}

# ── 室内设计项目 ──────────────────────────────────────────

@dataclass
class InteriorProject:
    name: str
    rooms: list[Room] = field(default_factory=list)
    walls: list[Wall] = field(default_factory=list)
    openings: list[Opening] = field(default_factory=list)
    furniture: list[FurnitureItem] = field(default_factory=list)

    def to_dict(self):
        def p2d(p): return {"x": p.x, "y": p.y}
        return {
            "name": self.name,
            "rooms": [{
                "name": r.name,
                "type": r.room_type.value,
                "corners": [p2d(c) for c in r.corners],
                "area": r.area,
                "level": r.level,
            } for r in self.rooms],
            "walls": [{
                "start": p2d(w.start), "end": p2d(w.end),
                "thickness": w.thickness,
                "type": w.wall_type.value,
            } for w in self.walls],
            "furniture": [{
                "name": f.name, "category": f.category.value,
                "width": f.width, "depth": f.depth, "height": f.height,
                "x": f.x, "y": f.y, "rotation": f.rotation,
                "color": f.color, "room": f.room,
            } for f in self.furniture],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @staticmethod
    def from_dict(d: dict) -> InteriorProject:
        proj = InteriorProject(name=d.get("name", "未命名"))
        for rd in d.get("rooms", []):
            corners = [Point2D(c["x"], c["y"]) for c in rd.get("corners", [])]
            room_type = next((rt for rt in RoomType if rt.value == rd.get("type", "")), RoomType.LIVING_ROOM)
            room = Room(name=rd["name"], room_type=room_type, corners=corners, level=rd.get("level", 0))
            room.calculate_area()
            proj.rooms.append(room)
        for wd in d.get("walls", []):
            wtype = next((wt for wt in WallType if wt.value == wd.get("type", "")), WallType.INTERIOR)
            proj.walls.append(Wall(Point2D(wd["start"]["x"], wd["start"]["y"]),
                                   Point2D(wd["end"]["x"], wd["end"]["y"]),
                                   thickness=wd.get("thickness", 200),
                                   wall_type=wtype))
        for fd in d.get("furniture", []):
            fcat = next((fc for fc in FurnitureCategory if fc.value == fd.get("category", "")), FurnitureCategory.DECORATION)
            proj.furniture.append(FurnitureItem(
                name=fd["name"], category=fcat,
                width=fd["width"], depth=fd["depth"], height=fd.get("height", 800),
                x=fd["x"], y=fd["y"], rotation=fd.get("rotation", 0),
                color=fd.get("color", "#cccccc"), room=fd.get("room", ""),
            ))
        return proj

    @staticmethod
    def from_json(s: str) -> InteriorProject:
        return InteriorProject.from_dict(json.loads(s))

# ── 户型模板 ──────────────────────────────────────────────

def create_apartment_template() -> InteriorProject:
    """创建一套标准两室一厅户型模板（约80㎡）"""
    proj = InteriorProject(name="两室一厅标准户型")

    # 房间多边形 (mm)
    # 整体外轮廓 10000x13000
    rooms_data = [
        ("客厅", RoomType.LIVING_ROOM, [(0, 5000), (6000, 5000), (6000, 10000), (0, 10000)]),
        ("餐厅", RoomType.DINING_ROOM, [(6000, 5000), (10000, 5000), (10000, 10000), (6000, 10000)]),
        ("主卧", RoomType.BEDROOM, [(0, 0), (4500, 0), (4500, 4000), (0, 4000)]),
        ("次卧", RoomType.BEDROOM, [(5500, 0), (10000, 0), (10000, 4000), (5500, 4000)]),
        ("厨房", RoomType.KITCHEN, [(7000, 4000), (10000, 4000), (10000, 5000), (7000, 5000)]),
        ("卫生间", RoomType.BATHROOM, [(6000, 4000), (7000, 4000), (7000, 5000), (6000, 5000)]),
        ("过道", RoomType.HALLWAY, [(4500, 0), (5500, 0), (5500, 5000), (4500, 5000)]),
    ]
    for name, rtype, corners in rooms_data:
        pts = [Point2D(x, y) for x, y in corners]
        room = Room(name, rtype, pts)
        room.calculate_area()
        proj.rooms.append(room)

    # 外墙（外轮廓）
    exterior_pts = [(0, 0), (10000, 0), (10000, 10000), (0, 10000)]
    for i in range(4):
        p1 = Point22D(exterior_pts[i][0], exterior_pts[i][1])
        p2 = Point2D(exterior_pts[(i+1)%4][0], exterior_pts[(i+1)%4][1])
        proj.walls.append(Wall(p1, p2, thickness=240, wall_type=WallType.EXTERIOR))

    # 内墙
    interior_walls = [
        ((0, 4000), (4500, 4000)),    # 主卧上边界
        ((5500, 4000), (10000, 4000)), # 次卧上边界
        ((4500, 0), (4500, 5000)),     # 过道左边界
        ((5500, 0), (5500, 5000)),     # 过道右边界
        ((6000, 4000), (6000, 5000)),  # 卫生间左边界
        ((7000, 4000), (7000, 5000)),  # 卫生间/厨房边界
        ((6000, 5000), (6000, 10000)), # 客厅右边界
        ((0, 5000), (10000, 5000)),    # 横向分隔
    ]
    for s, e in interior_walls:
        proj.walls.append(Wall(Point2D(s[0], s[1]), Point2D(e[0], e[1]),
                               thickness=150, wall_type=WallType.INTERIOR))

    return proj

# 导出时自动修正 Point2D 拼写错误（上面函数内的）
def create_apartment_template_fixed() -> InteriorProject:
    """创建一套标准两室一厅户型模板（约80㎡）- 修正版"""
    proj = InteriorProject(name="两室一厅标准户型")

    rooms_data = [
        ("客厅", RoomType.LIVING_ROOM, [(0, 5000), (6000, 5000), (6000, 10000), (0, 10000)]),
        ("餐厅", RoomType.DINING_ROOM, [(6000, 5000), (10000, 5000), (10000, 10000), (6000, 10000)]),
        ("主卧", RoomType.BEDROOM, [(0, 0), (4500, 0), (4500, 4000), (0, 4000)]),
        ("次卧", RoomType.BEDROOM, [(5500, 0), (10000, 0), (10000, 4000), (5500, 4000)]),
        ("厨房", RoomType.KITCHEN, [(7000, 4000), (10000, 4000), (10000, 5000), (7000, 5000)]),
        ("卫生间", RoomType.BATHROOM, [(6000, 4000), (7000, 4000), (7000, 5000), (6000, 5000)]),
        ("过道", RoomType.HALLWAY, [(4500, 0), (5500, 0), (5500, 5000), (4500, 5000)]),
    ]
    for name, rtype, corners in rooms_data:
        pts = [Point2D(x, y) for x, y in corners]
        room = Room(name, rtype, pts)
        room.calculate_area()
        proj.rooms.append(room)

    exterior_pts = [(0, 0), (10000, 0), (10000, 10000), (0, 10000)]
    for i in range(4):
        p1 = Point2D(exterior_pts[i][0], exterior_pts[i][1])
        p2 = Point2D(exterior_pts[(i+1)%4][0], exterior_pts[(i+1)%4][1])
        proj.walls.append(Wall(p1, p2, thickness=240, wall_type=WallType.EXTERIOR))

    interior_walls = [
        ((0, 4000), (4500, 4000)),
        ((5500, 4000), (10000, 4000)),
        ((4500, 0), (4500, 5000)),
        ((5500, 0), (5500, 5000)),
        ((6000, 4000), (6000, 5000)),
        ((7000, 4000), (7000, 5000)),
        ((6000, 5000), (6000, 10000)),
        ((0, 5000), (10000, 5000)),
    ]
    for s, e in interior_walls:
        proj.walls.append(Wall(Point2D(s[0], s[1]), Point2D(e[0], e[1]),
                               thickness=150, wall_type=WallType.INTERIOR))
    return proj

# ── 测试 ──────────────────────────────────────────────────

if __name__ == "__main__":
    proj = create_apartment_template_fixed()
    print(f"项目: {proj.name}")
    print(f"房间数: {len(proj.rooms)}")
    for r in proj.rooms:
        print(f"  {r.name}: {r.area/1e6:.1f}m2 ({r.room_type.value})")
    print(f"墙壁数: {len(proj.walls)}")
    total_area = sum(r.area for r in proj.rooms)
    print(f"总面积: {total_area/1e6:.1f}m2")

    # 导出 JSON 测试
    json_str = proj.to_json()
    print(f"\nJSON 大小: {len(json_str)} bytes")

    # 导入测试
    proj2 = InteriorProject.from_json(json_str)
    assert len(proj2.rooms) == len(proj.rooms)
    assert proj2.name == proj.name
    print("数据模型测试通过 ✓")
