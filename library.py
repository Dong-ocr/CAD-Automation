
# ======================================================================
#  library.py - CAD 模块化块（Block）定义与插入库
#
#  功能：预定义常用 CAD 块（建筑、树木、车位、指北针等），
#        提供统一的插入接口，实现"模块化制图"。
#
#  核心概念：
#    - Block（块定义）= 可复用的几何图形模板
#    - BlockRef（块引用）= 在图纸中插入块的一个实例
#    - 插入时可独立控制 位置、缩放、旋转
#    - 支持属性（Attribute）：块中的文字标签，插入时可赋值
#
#  使用示例：
#    from library import BlockLibrary
#    blib = BlockLibrary(doc)
#    blib.insert("TREE", (100, 200), scale=1.5)
#    blib.insert("BUILDING", (0, 0), scale=(40, 20))
#
#  依赖：ezdxf >= 1.4
# ======================================================================

import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment
import math


class BlockLibrary(object):
    """CAD 块库: 定义 + 管理 + 插入"""

    def __init__(self, doc):
        self.doc = doc
        self.msp = doc.modelspace()
        self._blocks = {}
        self._define_all()

    # ========== 内部: 注册所有预定义块 ==========

    def _define_all(self):
        self._define_building()
        self._define_dormitory()
        self._define_rect("GREEN_PATCH", colors.GREEN)
        self._define_rect("PLAZA_PATCH", 8)
        self._define_rect("SPORT_FIELD", colors.GREEN)
        self._define_door()
        self._define_window()
        self._define_tree()
        self._define_parking()
        self._define_north_arrow()
        self._define_room_tag()
        self._define_legend_item()
        self._define_basketball_court()
        self._define_tennis_court()
        self._define_flower_bed()
        self._define_street_lamp()
        self._define_flag_pole()
        self._define_bench()
        self._define_gate()
        self._define_pavilion()

    # --- 矩形基础块 ---

    def _define_rect(self, name, color):
        b = self.doc.blocks.new(name)
        b.add_lwpolyline(
            [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5)],
            dxfattribs={"color": color},
        )
        self._blocks[name] = b

    def _define_building(self):
        b = self.doc.blocks.new("BUILDING")
        b.add_lwpolyline(
            [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5)],
            dxfattribs={"color": colors.YELLOW},
        )
        b.add_lwpolyline(
            [(-0.45, -0.45), (0.45, -0.45), (0.45, 0.45), (-0.45, 0.45), (-0.45, -0.45)],
            dxfattribs={"color": colors.YELLOW},
        )
        self._blocks["BUILDING"] = b

    def _define_dormitory(self):
        b = self.doc.blocks.new("DORMITORY")
        b.add_lwpolyline(
            [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5)],
            dxfattribs={"color": 30},
        )
        for i in range(4):
            x = -0.375 + i * 0.25
            b.add_line((x, -0.4), (x, 0.4), dxfattribs={"color": 30})
        self._blocks["DORMITORY"] = b

    def _define_door(self):
        b = self.doc.blocks.new("DOOR")
        b.add_line((0, 0), (0, 1), dxfattribs={"color": colors.YELLOW})
        b.add_line((0, 1), (1, 1), dxfattribs={"color": colors.YELLOW})
        b.add_line((0, 0), (0.5, 0.5), dxfattribs={"color": colors.YELLOW})
        self._blocks["DOOR"] = b

    def _define_window(self):
        b = self.doc.blocks.new("WINDOW")
        b.add_line((0, 0), (1, 0), dxfattribs={"color": colors.CYAN})
        b.add_line((0, 0.3), (1, 0.3), dxfattribs={"color": colors.CYAN})
        self._blocks["WINDOW"] = b

    def _define_tree(self):
        b = self.doc.blocks.new("TREE")
        b.add_circle((0, 0), 1, dxfattribs={"color": colors.GREEN})
        b.add_line((-0.7, 0), (0.7, 0), dxfattribs={"color": colors.GREEN})
        b.add_line((0, -0.7), (0, 0.7), dxfattribs={"color": colors.GREEN})
        self._blocks["TREE"] = b

    def _define_parking(self):
        b = self.doc.blocks.new("PARKING")
        w, h = 2.5, 5.0
        b.add_lwpolyline(
            [(0, 0), (w, 0), (w, h), (0, h), (0, 0)],
            dxfattribs={"color": colors.WHITE},
        )
        self._blocks["PARKING"] = b

    def _define_north_arrow(self):
        b = self.doc.blocks.new("NORTH_ARROW")
        b.add_line((0, -0.5), (0, 0.5), dxfattribs={"color": colors.RED})
        b.add_line((0, 0.5), (-0.2, 0.1), dxfattribs={"color": colors.RED})
        b.add_line((0, 0.5), (0.2, 0.1), dxfattribs={"color": colors.RED})
        txt_n = b.add_text("\u5317", height=0.3, dxfattribs={"color": colors.RED})
        txt_n.set_placement((0, -0.85), align=TextEntityAlignment.MIDDLE_CENTER)
        txt_e = b.add_text("N", height=0.3, dxfattribs={"color": colors.RED})
        txt_e.set_placement((0, 0.75), align=TextEntityAlignment.MIDDLE_CENTER)
        self._blocks["NORTH_ARROW"] = b

    def _define_room_tag(self):
        b = self.doc.blocks.new("ROOM_TAG")
        b.add_circle((0, 0), 1.5, dxfattribs={"color": colors.CYAN})
        b.add_attdef("NAME", insert=(0, 0), text="ROOM", height=2.0)
        self._blocks["ROOM_TAG"] = b

    def _define_legend_item(self):
        b = self.doc.blocks.new("LEGEND_ITEM")
        b.add_lwpolyline(
            [(-0.5, -0.3), (0.5, -0.3), (0.5, 0.3), (-0.5, 0.3), (-0.5, -0.3)],
            dxfattribs={"color": colors.WHITE},
        )
        b.add_attdef("LABEL", insert=(1, 0), text="\u8bf4\u660e", height=2.0)
        self._blocks["LEGEND_ITEM"] = b

    # --- 篮球场 (半场 14m x 15m) ---

    def _define_basketball_court(self):
        b = self.doc.blocks.new("BASKETBALL_COURT")
        b.add_lwpolyline([(-7,-7.5),(7,-7.5),(7,7.5),(-7,7.5),(-7,-7.5)],
            dxfattribs={"color": 7})
        b.add_line((-7,0),(7,0), dxfattribs={"color": 7})
        b.add_circle((0,3.6), 1.8, dxfattribs={"color": 7})
        b.add_circle((0,-3.6), 3.5, dxfattribs={"color": 7})
        self._blocks["BASKETBALL_COURT"] = b

    # --- 网球场 (24m x 11m) ---

    def _define_tennis_court(self):
        b = self.doc.blocks.new("TENNIS_COURT")
        w, h = 12, 24
        b.add_lwpolyline([(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2),(-w/2,-h/2)],
            dxfattribs={"color": 4})
        b.add_line((0,-h/2),(0,h/2), dxfattribs={"color": 4})
        b.add_line((-w/2,-h/4),(w/2,-h/4), dxfattribs={"color": 4})
        b.add_line((-w/2,h/4),(w/2,h/4), dxfattribs={"color": 4})
        self._blocks["TENNIS_COURT"] = b

    # --- 花坛 ---

    def _define_flower_bed(self):
        b = self.doc.blocks.new("FLOWER_BED")
        b.add_circle((0,0), 2, dxfattribs={"color": 3})
        for i in range(6):
            a = math.radians(i * 60)
            px, py = 1.5 * math.cos(a), 1.5 * math.sin(a)
            b.add_circle((px,py), 0.8, dxfattribs={"color": 1})
        self._blocks["FLOWER_BED"] = b

    # --- 路灯 ---

    def _define_street_lamp(self):
        b = self.doc.blocks.new("STREET_LAMP")
        b.add_line((0,0),(0,5), dxfattribs={"color": 7})
        b.add_line((0,5),(-1,5.5), dxfattribs={"color": 2})
        b.add_line((0,5),(1,5.5), dxfattribs={"color": 2})
        b.add_lwpolyline([(-0.3,0),(0.3,0),(0.2,-0.3),(-0.2,-0.3),(-0.3,0)],
            dxfattribs={"color": 7})
        self._blocks["STREET_LAMP"] = b

    # --- 旗杆 ---

    def _define_flag_pole(self):
        b = self.doc.blocks.new("FLAG_POLE")
        b.add_line((0,0),(0,8), dxfattribs={"color": 7})
        b.add_lwpolyline([(0,6),(3,5.5),(0,5)],
            dxfattribs={"color": 1})
        b.add_lwpolyline([(-0.4,0),(0.4,0),(0.3,-0.4),(-0.3,-0.4),(-0.4,0)],
            dxfattribs={"color": 7})
        self._blocks["FLAG_POLE"] = b

    # --- 长椅 ---

    def _define_bench(self):
        b = self.doc.blocks.new("BENCH")
        b.add_line((-1,0),(1,0), dxfattribs={"color": 8})
        b.add_line((-1,0.3),(1,0.3), dxfattribs={"color": 8})
        b.add_line((-0.8,0.3),(-0.8,1), dxfattribs={"color": 8})
        b.add_line((0.8,0.3),(0.8,1), dxfattribs={"color": 8})
        b.add_line((-0.8,1),(0.8,1), dxfattribs={"color": 8})
        b.add_line((-0.8,-0.5),(-0.8,0), dxfattribs={"color": 8})
        b.add_line((0.8,-0.5),(0.8,0), dxfattribs={"color": 8})
        self._blocks["BENCH"] = b

    # --- 大门 ---

    def _define_gate(self):
        b = self.doc.blocks.new("GATE")
        b.add_line((-3,0),(-3,4), dxfattribs={"color": 2})
        b.add_line((3,0),(3,4), dxfattribs={"color": 2})
        b.add_line((-3,4),(3,4), dxfattribs={"color": 2})
        b.add_line((-2.5,0),(-2.5,3), dxfattribs={"color": 2})
        b.add_line((2.5,0),(2.5,3), dxfattribs={"color": 2})
        b.add_line((-2.5,3),(-0.1,3), dxfattribs={"color": 2})
        b.add_line((0.1,3),(2.5,3), dxfattribs={"color": 2})
        self._blocks["GATE"] = b

    # --- 凉亭 ---

    def _define_pavilion(self):
        b = self.doc.blocks.new("PAVILION")
        b.add_lwpolyline([(-2,-2),(2,-2),(2,2),(-2,2),(-2,-2)],
            dxfattribs={"color": 8})
        b.add_line((-1.8,-1.8),(-1.8,-1.2), dxfattribs={"color": 8})
        b.add_line((1.8,-1.8),(1.8,-1.2), dxfattribs={"color": 8})
        b.add_line((-1.8,1.8),(-1.8,1.2), dxfattribs={"color": 8})
        b.add_line((1.8,1.8),(1.8,1.2), dxfattribs={"color": 8})
        b.add_lwpolyline([(-2.5,1.2),(0,2.5),(2.5,1.2)], dxfattribs={"color": 1})
        b.add_lwpolyline([(-2.5,-1.2),(0,-2.5),(2.5,-1.2)], dxfattribs={"color": 1})
        self._blocks["PAVILION"] = b

    # ========== \u5916\u90e8\u63a5\u53e3: \u63d2\u5165\u5757 ==========

    def insert(self, name, x, y, scale=1.0, rotation=0.0, attrs=None, layer=None):
        if name not in self._blocks:
            raise ValueError("Unknown block: " + name)

        if isinstance(scale, (int, float)):
            sx = sy = float(scale)
        else:
            sx, sy = float(scale[0]), float(scale[1])

        dxfattribs = {"xscale": sx, "yscale": sy}
        if layer is not None:
            dxfattribs["layer"] = layer

        ref = self.msp.add_blockref(name, insert=(x, y), dxfattribs=dxfattribs)
        if rotation:
            ref.dxf.rotation = rotation

        if attrs:
            block = self._blocks[name]
            for tag, value in attrs.items():
                if block.has_attdef(tag):
                    ref.add_attrib(tag, str(value))

        return ref

    def make_room_tag(self, x, y, room_name, scale=1.0, layer=None):
        return self.insert("ROOM_TAG", x, y, scale=scale,
                           attrs={"NAME": room_name}, layer=layer)

    def make_tree_row(self, x_start, y, count, spacing=5.0, scale=1.0, layer=None):
        return [self.insert("TREE", x_start + i * spacing, y,
                            scale=scale, layer=layer) for i in range(count)]

    def make_parking_row(self, x_start, y, count, spacing=2.5, layer=None):
        return [self.insert("PARKING", x_start + i * spacing, y,
                            layer=layer) for i in range(count)]

    def make_grid(self, name, x0, y0, cols, rows, col_spacing, row_spacing,
                  scale=1.0, layer=None):
        refs = []
        for r in range(rows):
            for c in range(cols):
                ref = self.insert(name, x0 + c * col_spacing, y0 + r * row_spacing,
                                  scale=scale, layer=layer)
                refs.append(ref)
        return refs

    # ========== 查询 ==========

    @property
    def block_names(self):
        return list(self._blocks.keys())

    def count_refs(self, name=None):
        if name:
            return len(self.msp.query("INSERT[name==%r]" % name))
        return len(self.msp.query("INSERT"))

    def __repr__(self):
        return "BlockLibrary(%s)" % self.block_names


# ======================================================================
#  演示 & 自测
# ======================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("  library.py - 块库演示")
    print("=" * 50)

    doc = ezdxf.new("R2010")
    lib = BlockLibrary(doc)

    print()
    print("已定义块:", lib.block_names)

    lib.insert("BUILDING", 0, 0, scale=(40, 20), layer="BUILDING")
    lib.insert("DORMITORY", 0, 30, scale=(30, 15), layer="DORMITORY")
    lib.insert("BUILDING", 50, 0, scale=(20, 15), rotation=30, layer="BUILDING")

    lib.insert("TREE", 50, 20, scale=1.5, layer="GREEN")
    lib.make_tree_row(-30, -30, 4, spacing=6, scale=1.2, layer="GREEN")

    lib.make_parking_row(20, -10, 3, layer="PLAZA")

    lib.insert("NORTH_ARROW", -60, 30, scale=10)

    lib.make_room_tag(0, 0, "A-101", scale=1.5, layer="TEXT")
    lib.make_room_tag(30, -20, "B-201", layer="TEXT")

    lib.insert("LEGEND_ITEM", 0, -50, attrs={"LABEL": "\u5efa\u7b51\u7269"}, layer="LEGEND")
    lib.insert("LEGEND_ITEM", 0, -55, attrs={"LABEL": "\u6811\u6728"}, layer="LEGEND")

    lib.make_grid("TREE", 20, 20, 3, 2, 5, 5, scale=1.0, layer="GREEN")

    print("块引用总数:", lib.count_refs())
    for bname in lib.block_names:
        cnt = lib.count_refs(bname)
        if cnt:
            print("  %s: %d 次引用" % (bname, cnt))

    OUTPUT = "C:\\Users\\王东浩\\Documents\\CAD自动化制图\\test.dxf"
    doc.saveas(OUTPUT)
    print()
    print("OK - 已保存:", OUTPUT)
    print("请用 QCAD 打开预览")
