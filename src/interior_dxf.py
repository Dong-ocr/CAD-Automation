"""
interior_dxf.py — 室内设计 DXF 平面图生成引擎
参考 GitHub 项目: ezdxf (官方), AI-CAD (ishan-parihar), qsketchmetric
功能: 墙体/门窗/家具/尺寸标注/填充图案 的 DXF 输出
"""

from __future__ import annotations
import math, os, ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment
from ezdxf.math import Vec2
from typing import Optional

from interior_models import (
    InteriorProject, Room, Wall, WallType, Opening,
    FurnitureItem, Point2D, RoomType, FurnitureCategory
)

# ── 图层定义 ─────────────────────────────────────────────

LAYERS = {
    "A-WALL":       {"color": colors.WHITE, "linetype": "CONTINUOUS", "desc": "承重墙"},
    "A-WALL-PART":  {"color": colors.MAGENTA, "linetype": "CONTINUOUS", "desc": "隔断墙"},
    "A-DOOR":       {"color": colors.GREEN, "linetype": "CONTINUOUS", "desc": "门"},
    "A-WINDOW":     {"color": colors.CYAN, "linetype": "CONTINUOUS", "desc": "窗"},
    "A-FURN":       {"color": colors.YELLOW, "linetype": "CONTINUOUS", "desc": "家具"},
    "A-DIM":        {"color": colors.RED, "linetype": "CONTINUOUS", "desc": "尺寸标注"},
    "A-TEXT":       {"color": colors.WHITE, "linetype": "CONTINUOUS", "desc": "文字标注"},
    "A-HATCH":      {"color": colors.CYAN, "linetype": "CONTINUOUS", "desc": "填充图案"},
    "A-AXIS":       {"color": colors.RED, "linetype": "DASHDOT2", "desc": "轴线"},
    "F-FIXTURE":    {"color": colors.GREEN, "linetype": "CONTINUOUS", "desc": "固定设施"},
}

# ── 颜色映射 ─────────────────────────────────────────────

FURNITURE_COLORS = {
    FurnitureCategory.BED: 30,
    FurnitureCategory.SOFA: 40,
    FurnitureCategory.TABLE: 50,
    FurnitureCategory.CHAIR: 140,
    FurnitureCategory.CABINET: 32,
    FurnitureCategory.APPLIANCE: 8,
    FurnitureCategory.SANITARY: 140,
    FurnitureCategory.DECORATION: 220,
    FurnitureCategory.LIGHTING: 50,
}

def _setup_layers(doc):
    """初始化所有图层"""
    for name, cfg in LAYERS.items():
        lay = doc.layers.add(name)
        lay.color = cfg["color"]
        lay.linetype = cfg["linetype"]
        lay.description = cfg["desc"]

def _mm_to_dxf(p: Point2D) -> tuple[float, float]:
    """转换 mm 到 DXF 单位（ezdxf 用米或毫米均可，我们统一用毫米）"""
    return (p.x, p.y)

# ── 墙壁绘制 ─────────────────────────────────────────────

def _draw_walls(msp, proj: InteriorProject):
    """绘制双线墙（外轮廓+内轮廓）"""
    for w in proj.walls:
        layer = "A-WALL" if w.wall_type == WallType.EXTERIOR else "A-WALL-PART"
        nx, ny = w.normal()
        half = w.thickness / 2

        # 外轮廓
        p1 = (w.start.x + nx * half, w.start.y + ny * half)
        p2 = (w.end.x + nx * half, w.end.y + ny * half)
        msp.add_line(p1, p2, dxfattribs={"layer": layer})

        # 内轮廓
        p3 = (w.start.x - nx * half, w.start.y - ny * half)
        p4 = (w.end.x - nx * half, w.end.y - ny * half)
        msp.add_line(p3, p4, dxfattribs={"layer": layer})

        # 墙端封口
        msp.add_line(p1, p3, dxfattribs={"layer": layer, "color": LAYERS[layer]["color"]})
        msp.add_line(p2, p4, dxfattribs={"layer": layer, "color": LAYERS[layer]["color"]})

def _draw_doors(msp, proj: InteriorProject):
    """绘制门（平面图符号）"""
    for op in proj.openings:
        if not op.is_door:
            continue
        if op.wall_idx >= len(proj.walls):
            continue
        w = proj.walls[op.wall_idx]

        # 门的位置
        dx = w.end.x - w.start.x
        dy = w.end.y - w.start.y
        length = math.hypot(dx, dy)
        if length == 0:
            continue
        # 从墙角偏移
        ratio = op.position / length
        door_x = w.start.x + dx * ratio
        door_y = w.start.y + dy * ratio
        # 门扇宽度
        door_end_x = door_x + (dx / length) * op.width
        door_end_y = door_y + (dy / length) * op.width

        # 门洞线（断开墙体）
        msp.add_line((door_x, door_y), (door_end_x, door_end_y),
                     dxfattribs={"layer": "A-DOOR"})

        # 门弧（90度开扇）
        nx, ny = w.normal()
        arc_center = (door_x + nx * 100, door_y + ny * 100)
        arc_radius = op.width
        start_angle = math.degrees(math.atan2(dy, dx))
        if nx * dy - ny * dx > 0:  # 法线方向判断
            end_angle = start_angle + 90
        else:
            end_angle = start_angle - 90

        msp.add_arc(arc_center, arc_radius, start_angle, end_angle,
                    dxfattribs={"layer": "A-DOOR"})

def _draw_windows(msp, proj: InteriorProject):
    """绘制窗（平面图符号）"""
    for op in proj.openings:
        if op.is_door:
            continue
        if op.wall_idx >= len(proj.walls):
            continue
        w = proj.walls[op.wall_idx]

        dx = w.end.x - w.start.x
        dy = w.end.y - w.start.y
        length = math.hypot(dx, dy)
        if length == 0:
            continue
        ratio = op.position / length
        wx = w.start.x + dx * ratio
        wy = w.start.y + dy * ratio

        # 窗符号：四条平行短线
        nx, ny = w.normal()
        half = w.thickness / 2
        for i in range(4):
            offset = -half + (i + 1) * (w.thickness / 5)
            p1 = (wx + nx * offset, wy + ny * offset)
            p2 = (wx + (dx / length) * op.width + nx * offset,
                  wy + (dy / length) * op.width + ny * offset)
            msp.add_line(p1, p2, dxfattribs={"layer": "A-WINDOW"})

# ── 家具绘制 ─────────────────────────────────────────────

def _draw_furniture(msp, proj: InteriorProject):
    """绘制家具平面图"""
    for f in proj.furniture:
        color = FURNITURE_COLORS.get(f.category, 7)
        hw, hd = f.width / 2, f.depth / 2
        rad = math.radians(f.rotation)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        corners = []
        for dx, dy in [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)]:
            rx = f.x + dx * cos_a - dy * sin_a
            ry = f.y + dx * sin_a + dy * cos_a
            corners.append((rx, ry))

        # 画外框
        for i in range(4):
            msp.add_line(corners[i], corners[(i+1)%4],
                        dxfattribs={"layer": "A-FURN", "color": color})

        # 家具名称
        cx = sum(c[0] for c in corners) / 4
        cy = sum(c[1] for c in corners) / 4
        msp.add_text(f.name,
                     dxfattribs={"layer": "A-TEXT", "color": color, "height": 150}).set_placement(
                         (cx, cy), align=TextEntityAlignment.CENTER)

        # 对角线（表示填充）
        msp.add_line(corners[0], corners[2],
                    dxfattribs={"layer": "A-FURN", "color": color, "linetype": "CONTINUOUS"})

# ── 尺寸标注 ─────────────────────────────────────────────

def _draw_dimensions(msp, proj: InteriorProject):
    """绘制房间尺寸标注"""
    dim_style = "EZDXF_STANDARD"
    for room in proj.rooms:
        if len(room.corners) < 2:
            continue
        # 水平尺寸
        xs = [c.x for c in room.corners]
        ys = [c.y for c in room.corners]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        label_y = min_y - 500  # 尺寸线位置

        try:
            dim = msp.add_linear_dim(
                base=(min_x, label_y),
                p1=(min_x, min_y),
                p2=(max_x, min_y),
                dxfattribs={"layer": "A-DIM", "dimstyle": dim_style}
            )
            dim.render()
        except Exception:
            pass

        # 垂直尺寸
        label_x = max_x + 500
        try:
            dim = msp.add_linear_dim(
                base=(label_x, min_y),
                p1=(max_x, min_y),
                p2=(max_x, max_y),
                dxfattribs={"layer": "A-DIM", "dimstyle": dim_style}
            )
            dim.render()
        except Exception:
            pass

# ── 房间名称标注 ─────────────────────────────────────────

def _draw_room_labels(msp, proj: InteriorProject):
    """标注房间名称和面积"""
    for room in proj.rooms:
        c = room.center()
        area_m2 = room.area / 1e6
        text = f"{room.name}\n{area_m2:.1f}m2"
        msp.add_text(text,
                     dxfattribs={"layer": "A-TEXT", "height": 250}).set_placement(
                         (c.x, c.y), align=TextEntityAlignment.CENTER)

        # 房间填充（淡色）
        try:
            pts = [(c.x, c.y) for c in room.corners]
            msp.add_hatch(color=colors.CYAN, dxfattribs={"layer": "A-HATCH"}).paths.add_polyline_path(
                pts, is_closed=True
            )
        except Exception:
            pass

# ── 图框 ─────────────────────────────────────────────────

def _draw_title_block(msp, proj: InteriorProject):
    """绘制 A3 图框和标题栏"""
    # A3 尺寸: 420x297mm，但我们的绘图在毫米空间，缩放
    scale = 0.05  # 图纸比例 1:20
    w, h = 420 / scale, 297 / scale
    offset_x, offset_y = -2000, -2000

    # 图框
    msp.add_lwpolyline([
        (offset_x, offset_y),
        (offset_x + w, offset_y),
        (offset_x + w, offset_y + h),
        (offset_x, offset_y + h),
        (offset_x, offset_y),
    ], dxfattribs={"layer": "A-TEXT", "color": colors.WHITE})

    # 标题栏
    tb_y = offset_y
    tb_h = 600 / scale
    msp.add_lwpolyline([
        (offset_x + w * 0.6, tb_y),
        (offset_x + w, tb_y),
        (offset_x + w, tb_y + tb_h),
        (offset_x + w * 0.6, tb_y + tb_h),
        (offset_x + w * 0.6, tb_y),
    ], dxfattribs={"layer": "A-TEXT", "color": colors.WHITE})

    # 项目名称
    msp.add_text(f"项目: {proj.name}",
                 dxfattribs={"layer": "A-TEXT", "height": 300 / scale}).set_placement(
                     (offset_x + w * 0.8, tb_y + tb_h * 0.6),
                     align=TextEntityAlignment.CENTER)

    # 比例
    msp.add_text("比例 1:20",
                 dxfattribs={"layer": "A-TEXT", "height": 200 / scale}).set_placement(
                     (offset_x + w * 0.8, tb_y + tb_h * 0.3),
                     align=TextEntityAlignment.CENTER)

# ── 主渲染函数 ──────────────────────────────────────────

def render_dxf(proj: InteriorProject, output_path: str) -> str:
    """
    渲染室内设计项目为 DXF 文件
    返回 DXF 文件路径
    """
    doc = ezdxf.new("R2010")
    _setup_layers(doc)
    msp = doc.modelspace()

    _draw_walls(msp, proj)
    _draw_doors(msp, proj)
    _draw_windows(msp, proj)
    _draw_furniture(msp, proj)
    _draw_room_labels(msp, proj)
    _draw_dimensions(msp, proj)

    # 设置标注样式
    dim_style = doc.dimstyles.new("INTERIOR")
    dim_style.dimasz = 100
    dim_style.dimexe = 100
    dim_style.dimexo = 50
    dim_style.dimtxt = 150
    dim_style.dimgap = 50

    doc.saveas(output_path)
    return output_path

# ── SVG 渲染（预览用） ────────────────────────────────────

def render_svg(proj: InteriorProject, output_path: str) -> str:
    """使用 ezdxf 的 matplotlib 后端渲染 PNG/SVG 预览"""
    try:
        from ezdxf.addons.drawing import Frontend, RenderContext
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # 先导出临时 DXF
        temp_dxf = output_path.replace(".png", ".dxf").replace(".svg", ".dxf")
        doc = ezdxf.new("R2010")
        _setup_layers(doc)
        msp = doc.modelspace()
        _draw_walls(msp, proj)
        _draw_doors(msp, proj)
        _draw_windows(msp, proj)
        _draw_furniture(msp, proj)
        _draw_room_labels(msp, proj)
        _draw_dimensions(msp, proj)
        doc.saveas(temp_dxf)

        # 渲染
        doc2 = ezdxf.readfile(temp_dxf)
        fig = plt.figure(figsize=(16, 12), dpi=150)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_aspect("equal")
        ax.axis("off")

        backend = MatplotlibBackend(ax)
        Frontend(RenderContext(doc2), backend).draw(doc2.modelspace())

        if output_path.endswith(".svg"):
            fig.savefig(output_path, format="svg", bbox_inches="tight", pad_inches=0)
        else:
            fig.savefig(output_path, format="png", bbox_inches="tight", pad_inches=0, dpi=150)
        plt.close(fig)

        # 清理临时文件
        if os.path.exists(temp_dxf):
            os.remove(temp_dxf)
        return output_path
    except Exception as e:
        print(f"  SVG/PNG 渲染警告: {e}")
        return ""

# ── 测试 ──────────────────────────────────────────────────

if __name__ == "__main__":
    import tempfile

    # 创建项目
    from interior_models import create_apartment_template_fixed, Opening, FurnitureItem, FurnitureCategory

    proj = create_apartment_template_fixed()

    # 添加门
    proj.openings.append(Opening(wall_idx=0, position=1500, width=900, height=2100, is_door=True))
    proj.openings.append(Opening(wall_idx=2, position=1000, width=800, height=2100, is_door=True))
    proj.openings.append(Opening(wall_idx=4, position=2000, width=1500, height=1500, is_door=False))

    # 添加家具
    proj.furniture.extend([
        FurnitureItem("双人床", FurnitureCategory.BED, 1800, 2000, 500, x=2000, y=1500, color="#D2B48C", room="主卧"),
        FurnitureItem("衣柜", FurnitureCategory.CABINET, 1800, 600, 2400, x=300, y=500, color="#D2B48C", room="主卧"),
        FurnitureItem("三人沙发", FurnitureCategory.SOFA, 2200, 850, 800, x=2000, y=7500, color="#8B4513", room="客厅"),
        FurnitureItem("茶几", FurnitureCategory.TABLE, 1200, 600, 450, x=2500, y=8500, color="#D2691E", room="客厅"),
        FurnitureItem("电视柜", FurnitureCategory.CABINET, 1800, 400, 500, x=2000, y=5500, color="#3C3C3C", room="客厅"),
        FurnitureItem("餐桌", FurnitureCategory.TABLE, 1400, 800, 750, x=8000, y=7500, color="#DEB887", room="餐厅"),
        FurnitureItem("马桶", FurnitureCategory.SANITARY, 400, 700, 600, x=6200, y=4200, color="#F5F5F5", room="卫生间"),
        FurnitureItem("洗手盆", FurnitureCategory.SANITARY, 600, 500, 800, x=6500, y=4500, color="#FFFFFF", room="卫生间"),
    ])

    # 输出
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "output"), exist_ok=True)
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")

    dxf_path = os.path.join(output_dir, "interior_floorplan.dxf")
    render_dxf(proj, dxf_path)
    print(f"DXF 输出: {dxf_path}")

    png_path = os.path.join(output_dir, "interior_floorplan.png")
    render_svg(proj, png_path)
    print(f"PNG 预览: {png_path}")

    print(f"房间:")
    for r in proj.rooms:
        print(f"  {r.name}: {r.area/1e6:.1f}m2")
    print(f"家具: {len(proj.furniture)} 件")
    print("DXF 渲染测试完成 ✓")
