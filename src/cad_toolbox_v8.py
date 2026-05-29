# ====================================================================
#  cad_toolbox_v8.py — 岩泊渡水电站 专业施工图工具箱 v8（全面升级版）
#  功能: 国标图层 · 完整尺寸引擎 · MultiLeader · UCS 坐标变换
#        路径操作 · 构造几何 · 审计验证 · SVG 导出 · 3D 扩展
#  依赖: ezdxf>=1.4, pyclipper, shapely, svgwrite, cairosvg
#        cadquery / build123d (可选，用于 3D 导出)
# ====================================================================
import sys, os, math, json, datetime
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any, Union

import ezdxf
from ezdxf.enums import TextEntityAlignment
from ezdxf.math import Vec2, Vec3, UCS, Matrix44, OCS
from ezdxf.math import (
    ConstructionLine, ConstructionCircle, ConstructionArc,
    ConstructionBox, ConstructionRay, ConstructionPolyline,
    intersection_line_line_2d, intersection_line_line_3d,
    is_point_in_polygon_2d, convex_hull_2d,
    offset_vertices_2d, triangulation, closest_point,
)
from ezdxf import path as ezpath
from ezdxf import units
from ezdxf.render import arrows
from ezdxf.audit import Auditor
from ezdxf import zoom

# ---- 可选依赖 ----
try:
    import shapely.geometry as shp
    import shapely.ops as shp_ops
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False

try:
    import pyclipper
    HAS_PYCLIPPER = True
except ImportError:
    HAS_PYCLIPPER = False

try:
    import svgwrite
    HAS_SVGWRITE = True
except ImportError:
    HAS_SVGWRITE = False

try:
    import cadquery as cq
    HAS_CADQUERY = True
except ImportError:
    HAS_CADQUERY = False


# =========================== 国标图层配置 (GB/T 50001-2017) ===========================
GB_LAYERS_V8 = {
    # 建筑
    "0-建筑":       (7, "CONTINUOUS"),
    "A-WALL-墙体":   (7, "CONTINUOUS"),
    "A-COLM-立柱":   (6, "CONTINUOUS"),
    "A-FLOR-楼面":   (4, "CONTINUOUS"),
    "A-OVHD-吊车":   (5, "DASHED2"),
    "A-ROOF-屋面":   (7, "CONTINUOUS"),
    "A-DOOR-门窗":   (7, "CONTINUOUS"),
    "A-STRS-楼梯":   (7, "CONTINUOUS"),
    # 结构
    "S-CONC-混凝土": (8, "CONTINUOUS"),
    "S-REIN-钢筋":   (5, "CONTINUOUS"),
    "S-STRU-钢结构": (6, "CONTINUOUS"),
    "S-FNDN-基础":   (3, "CONTINUOUS"),
    "S-FILL-回填":   (8, "CONTINUOUS"),
    # 机械
    "M-EQPM-设备":   (7, "CONTINUOUS"),
    "M-HYDR-水力":   (4, "CONTINUOUS"),
    "M-PIPE-管道":   (4, "CONTINUOUS"),
    "M-VALV-阀门":   (4, "CONTINUOUS"),
    "M-STRU-金属结构": (3, "CONTINUOUS"),
    # 电气
    "E-CABL-电缆":   (6, "DASHED2"),
    "E-LINE-母线":   (1, "CONTINUOUS"),
    "E-GND-接地":    (6, "DASHED2"),
    # 标注
    "DIM-尺寸":     (3, "CONTINUOUS"),
    "DIM-半径":     (4, "CONTINUOUS"),
    "DIM-角度":     (2, "CONTINUOUS"),
    "DIM-高程":     (6, "CONTINUOUS"),
    "TEXT-文字":    (7, "CONTINUOUS"),
    "TEXT-说明":    (7, "CONTINUOUS"),
    "TEXT-标注":    (3, "CONTINUOUS"),
    "HATCH-填充":   (8, "CONTINUOUS"),
    "SYMB-符号":    (6, "CONTINUOUS"),
    "SYMB-剖切":    (1, "CONTINUOUS"),
    "SYMB-焊缝":    (6, "CONTINUOUS"),
    "AXIS-轴线":    (1, "CENTER2"),
    "AXIS-网格":    (2, "CENTER2"),
    "HIDN-隐藏":    (5, "DASHED2"),
    "HIDN-虚线":    (5, "DASHED2"),
    "BORD-图框":    (7, "CONTINUOUS"),
    "BORD-装订":    (8, "CONTINUOUS"),
    "TBLK-标题栏":  (2, "CONTINUOUS"),
    "LEAD-引线":    (4, "CONTINUOUS"),
    "LEAD-云线":    (6, "CONTINUOUS"),
    "LEAD-索引":    (4, "CONTINUOUS"),
    "NOTE-说明":    (7, "CONTINUOUS"),
    "VIEWPORTS":    (7, "CONTINUOUS"),
    "DEFPOINTS":    (7, "CONTINUOUS"),
}

# ===================== 项目常量数据 =====================
@dataclass
class ElevationData:
    """水电站各层高程 (mm)"""
    dt_bottom: float = 83500   # 尾水管底
    spiral_case_c: float = 95670  # 蜗壳中心
    turbine_floor: float = 98500  # 水轮机层
    generator_floor: float = 105000  # 发电机层
    crane_rail: float = 117000     # 吊车轨顶
    roof: float = 124200           # 屋顶

@dataclass
class DimensionData:
    """厂房尺寸 (mm)"""
    total_len: float = 94000
    unit_len: float = 30000
    install_len: float = 20000
    span: float = 17000
    crane_span: float = 16500
    axis_spacing: float = 6000

@dataclass
class EquipmentData:
    """主要设备参数 (mm)"""
    stator_od: float = 9760
    rotor_d: float = 7900
    hood_od: float = 10600
    sc_max_r: float = 9270
    dt_h: float = 10000
    dt_w: float = 10340
    runner_d: float = 3800

@dataclass
class ColumnData:
    """立柱截面 (mm)"""
    up_w: float = 600
    up_d: float = 800
    dw_w: float = 600
    dw_d: float = 1000


class HydroProjectV8:
    """岩泊渡水电站施工图工具箱 v8 — 全面升级版"""

    # ---- ezdxf 内置填充图案速查 ----
    HATCH_PATTERNS = {
        "concrete": "ANSI31",      # 混凝土
        "steel": "ANSI32",         # 钢材
        "earth": "AR-SAND",        # 砂土/回填
        "gravel": "GRAVEL",        # 碎石
        "brick": "BRICK",          # 砖
        "hatch": "ANSI31",         # 通用剖面线
        "solid": None,             # 实体填充
        "insulation": "INSUL",     # 保温
        "concrete_dot": "AR-CONC", # 混凝土点状
    }

    PAPER_SIZES = {
        "A0": (841, 1189),
        "A1": (594, 841),
        "A2": (420, 594),
        "A3": (297, 420),
        "A4": (210, 297),
    }

    def __init__(self, name: str = "岩泊渡水电站", version: str = "v8"):
        self.name = name
        self.version = version
        self.doc = ezdxf.new("R2010")
        self.doc.units = units.MM
        self.msp = self.doc.modelspace()

        # 工程数据
        self.elevations = ElevationData()
        self.dimensions = DimensionData()
        self.equipment = EquipmentData()
        self.columns = ColumnData()

        # 运行状态
        self._validation_errors: List[str] = []
        self._setup_complete = False

    # ===================== 初始化 =====================
    def setup_all(self):
        """一键初始化所有图层、样式、尺寸样式、图块"""
        self._setup_layers()
        self._setup_text_styles()
        self._setup_dimstyles()
        self._create_blocks()
        self._setup_complete = True
        return self
    # ===================== 图层管理 =====================
    def _setup_layers(self):
        for name, (color, ltype) in GB_LAYERS_V8.items():
            try:
                self.doc.layers.new(name, dxfattribs={
                    "color": color,
                    "linetype": ltype,
                    "lineweight": 25,
                })
            except ezdxf.DXFTableEntryError:
                pass

    def _setup_text_styles(self):
        styles = {
            "HZ": {"font": "simfang.ttf", "width": 0.7},
            "TXT": {"font": "txt.shx", "width": 0.8},
            "COMPLEX": {"font": "complex.shx", "width": 0.8},
        }
        for name, opts in styles.items():
            try:
                style = self.doc.styles.new(name, dxfattribs={
                    "font": opts["font"],
                    "width": opts["width"],
                    
                })
            except ezdxf.DXFTableEntryError:
                pass
        self.doc.styles.new("ROMANS", dxfattribs={
            "font": "romans.shx", "width": 0.8,
        })

    def _setup_dimstyles(self):
        """创建多比例尺寸样式"""
        for scale in [50, 100, 150, 200]:
            name = f"GB_DIM_{scale}"
            try:
                style = self.doc.dimstyles.new(name)
            except ezdxf.DXFTableEntryError:
                style = self.doc.dimstyles.get(name)
            dim_scale = scale / 100.0
            style.dxf.dimscale = dim_scale
            style.dxf.dimexe = 1.0 * dim_scale
            style.dxf.dimexo = 0.625 * dim_scale
            style.dxf.dimtxt = 2.5 * dim_scale
            style.dxf.dimasz = 2.0 * dim_scale
            style.dxf.dimclrd = 3
            style.dxf.dimclre = 3
            style.dxf.dimclrt = 7
            style.dxf.dimgap = 0.625 * dim_scale
            style.dxf.dimdec = 0

    def _create_blocks(self):
        """创建常用图块：高程符号、剖切符号、轴线号"""
        blk = self.doc.blocks.new("ELV_SYMBOL")
        blk.add_line((-4, 0), (4, 0), dxfattribs={"layer": "SYMB-符号"})
        blk.add_line((0, 0), (0, -3), dxfattribs={"layer": "SYMB-符号"})
        blk.add_polyline2d([(-4.5, 0.5), (0, -3), (4.5, 0.5)], dxfattribs={"layer": "SYMB-符号"})

        blk = self.doc.blocks.new("SECTION_MARK")
        blk.add_circle((0, 0), 5, dxfattribs={"layer": "SYMB-符号"})
        blk.add_line((-5, 0), (5, 0), dxfattribs={"layer": "SYMB-符号"})
        blk.add_line((0, -5), (0, 5), dxfattribs={"layer": "SYMB-符号"})
    # ===================== 基本绘图 =====================
    def line(self, x1, y1, x2, y2, layer="0-建筑", lw=0.18):
        return self.msp.add_line((x1, y1), (x2, y2), dxfattribs={
            "layer": layer, "lineweight": int(lw * 100),
        })

    def circle(self, x, y, r, layer="0-建筑", lw=0.18):
        return self.msp.add_circle((x, y), r, dxfattribs={
            "layer": layer, "lineweight": int(lw * 100),
        })

    def arc(self, x, y, r, sa, ea, layer="0-建筑", lw=0.18):
        return self.msp.add_arc((x, y), r, sa, ea, dxfattribs={
            "layer": layer, "lineweight": int(lw * 100),
        })

    def rect(self, x1, y1, x2, y2, layer="0-建筑", lw=0.18):
        pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)]
        return self.msp.add_lwpolyline(pts, dxfattribs={
            "layer": layer, "lineweight": int(lw * 100),
        })

    def polyline(self, pts, layer="0-建筑", lw=0.18, closed=False):
        return self.msp.add_lwpolyline(pts, dxfattribs={
            "layer": layer, "lineweight": int(lw * 100), "closed": closed,
        })

    def text(self, txt, x, y, h=2.5, layer="TEXT-文字", rot=0, style="HZ"):
        return self.msp.add_text(txt, height=h, dxfattribs={
            "layer": layer, "rotation": rot, "style": style,
        }).set_placement((x, y), align=TextEntityAlignment.LEFT)

    def text_c(self, txt, x, y, h=2.5, layer="TEXT-文字", style="HZ"):
        return self.msp.add_text(txt, height=h, dxfattribs={
            "layer": layer, "style": style,
        }).set_placement((x, y), align=TextEntityAlignment.CENTER)

    def text_r(self, txt, x, y, h=2.5, layer="TEXT-文字", style="HZ"):
        return self.msp.add_text(txt, height=h, dxfattribs={
            "layer": layer, "style": style,
        }).set_placement((x, y), align=TextEntityAlignment.RIGHT)

    def mtext(self, txt, x, y, w, h=2.5, layer="TEXT-文字", style="HZ"):
        """添加多行文字"""
        return self.msp.add_mtext(
            txt, dxfattribs={"layer": layer, "style": style, "char_height": h},
        ).set_location((x, y))


    # ===================== 轴线系统 =====================
    def axis_line(self, x1, y1, x2, y2):
        return self.msp.add_line((x1, y1), (x2, y2), dxfattribs={
            "layer": "AXIS-轴线", "lineweight": 15,
        })

    def axis_circle(self, x, y, label, r=450, h=3.0):
        self.msp.add_circle((x, y), r, dxfattribs={"layer": "AXIS-轴线"})
        self.text_c(label, x, y, h, "AXIS-轴线")

    def axis_grid(self, ox, oy, nx, ny, dx, dy, start_no=1):
        """生成轴线网格"""
        for i in range(nx):
            no = i + start_no
            label = str(no) if no <= 9 else chr(64 + no - 9)
            x = ox + i * dx
            self.axis_line(x, oy, x, oy + (ny - 1) * dy)
            self.axis_circle(x, oy - 400, label)
        for j in range(ny):
            y = oy + j * dy
            label = chr(65 + j)
            self.axis_line(ox, y, ox + (nx - 1) * dx, y)
            self.axis_circle(ox - 400, y, label)
    # ===================== 尺寸标注 (v8 升级版) =====================
    def dim_h(self, y, x1, x2, text="", scale=100):
        """水平线性标注"""
        if abs(x2 - x1) < 1:
            return
        ds = f"GB_DIM_{scale}"
        dim = self.msp.add_linear_dim(
            base=(x1, y), p1=(x1, y), p2=(x2, y), dimstyle=ds
        )
        if text:
            dim.set_text(text)
        dim.render()

    def dim_v(self, x, y1, y2, text="", scale=100):
        """垂直线性标注"""
        if abs(y2 - y1) < 1:
            return
        ds = f"GB_DIM_{scale}"
        dim = self.msp.add_linear_dim(
            base=(x, y1), p1=(x, y1), p2=(x, y2), dimstyle=ds
        )
        if text:
            dim.set_text(text)
        dim.render()

    def dim_chain_h(self, y, segments, scale=100):
        """水平连续标注"""
        for x1, x2, label in segments:
            if abs(x2 - x1) > 1:
                ds = f"GB_DIM_{scale}"
                dim = self.msp.add_linear_dim(
                    base=(x1, y), p1=(x1, y), p2=(x2, y), dimstyle=ds
                )
                if label:
                    dim.set_text(f"<> {label}")
                dim.render()

    def dim_chain_v(self, x, segments, scale=100):
        """垂直连续标注"""
        for y1, y2, label in segments:
            if abs(y2 - y1) > 1:
                ds = f"GB_DIM_{scale}"
                dim = self.msp.add_linear_dim(
                    base=(x, y1), p1=(x, y1), p2=(x, y2), dimstyle=ds
                )
                if label:
                    dim.set_text(f"<> {label}")
                dim.render()

    def dim_radius(self, cx, cy, px, py, text="", scale=100):
        """半径标注"""
        ds = f"GB_DIM_{scale}"
        dim = self.msp.add_radius_dim(
            center=(cx, cy), radius=Vec2(px, py).distance(Vec2(cx, cy)),
            location=(px, py), dimstyle=ds,
        )
        if text:
            dim.set_text(text)
        dim.render()

    def dim_diameter(self, cx, cy, r, text="", scale=100):
        """直径标注"""
        ds = f"GB_DIM_{scale}"
        loc = (cx + r * 1.4, cy + r * 1.4)
        dim = self.msp.add_diameter_dim(
            center=(cx, cy), radius=r, location=loc, dimstyle=ds,
        )
        if text:
            dim.set_text(text)
        dim.render()

    def dim_angular(self, center, p1, p2, location, text="", scale=100):
        """角度标注"""
        ds = f"GB_DIM_{scale}"
        dim = self.msp.add_angular_dim(
            center=center, p1=p1, p2=p2, location=location, dimstyle=ds,
        )
        if text:
            dim.set_text(text)
        dim.render()

    def dim_ordinate(self, origin, feature, text="", scale=100):
        """坐标标注"""
        ds = f"GB_DIM_{scale}"
        dim = self.msp.add_ordinate_dim(
            origin=origin, feature=location, dimstyle=ds,
        )
        if text:
            dim.set_text(text)
        dim.render()
    # ===================== MultiLeader (多重引线) =====================
    def add_leader_v8(self, x1, y1, x2, y2, text, h=3.0, gap=400):
        """使用 ezdxf 内置 MLeader (比手画线更专业)"""
        try:
            from ezdxf.render.mleader import MultiLeaderMTextBuilder
            mtext = self.msp.add_mtext(
                text,
                dxfattribs={"layer": "LEAD-引线", "style": "HZ", "char_height": h},
            )
            mtext.set_location((x2 + gap, y2 - h * 0.5))
            builder = MultiLeaderMTextBuilder.from_mtext(mtext)
            builder.add_leader_line([(x1, y1), (x2, y2)])
            builder.build(self.doc)
        except Exception:
            # fallback: 手动线+文字
            self.msp.add_line((x1, y1), (x2, y2),
                dxfattribs={"layer": "LEAD-引线", "lineweight": 25})
            tx = x2 + gap if x2 > x1 else x2 - gap * 3
            self.text(text, tx, y2 - 1.5, h, "NOTE-说明")

    # ===================== 填充图案 =====================
    def hatch_solid(self, pts, color=253, layer="HATCH-填充"):
        if len(pts) < 3:
            return
        hatch = self.msp.add_hatch(color=color, dxfattribs={"layer": layer})
        hatch.paths.add_polyline_path(pts, is_closed=True)
        hatch.set_solid_fill(color=color)

    def hatch_fill(self, pts, pattern="ANSI31", scale=100, color=8, layer="HATCH-填充"):
        if len(pts) < 3:
            return
        hatch = self.msp.add_hatch(color=color, dxfattribs={"layer": layer})
        hatch.paths.add_polyline_path(pts, is_closed=True)
        hatch.set_pattern_fill(pattern, scale=scale)

    def hatch_rect(self, x1, y1, x2, y2, pattern="ANSI31", scale=100, color=8, layer="HATCH-填充"):
        pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        self.hatch_fill(pts, pattern, scale, color, layer)

    # ===================== 高程符号 =====================
    def elevation(self, x, y, elev, label="", h=2.5):
        """插入高程符号"""
        self.msp.add_blockref(
            "ELV_SYMBOL", (x, y),
            dxfattribs={"layer": "SYMB-符号", "rotation": 0},
        )
        txt = f"{elev / 1000:.3f}" if not label else label
        self.text(txt, x + 200, y - 2.5, h, "DIM-高程")
    # ===================== 剖切符号 =====================
    def section_line(self, label, pts):
        """绘制剖切线及剖切符号"""
        if len(pts) < 2:
            return
        self.msp.add_lwpolyline(pts, dxfattribs={
            "layer": "SYMB-剖切", "lineweight": 50,
        })
        mid = len(pts) // 2
        self.text_c(label, pts[mid][0], pts[mid][1] + 300, 3.0, "SYMB-剖切")

    # ===================== 图框与标题栏 =====================
    def create_layout(self, name, paper_size, scale, view_center,
                      border_mm=15, landscape=False):
        """创建布局（带图框和标题栏）"""
        pw, ph = self.PAPER_SIZES.get(paper_size, (594, 841))
        if landscape:
            pw, ph = ph, pw
        try:
            layout = self.doc.layouts.new(name)
        except ezdxf.DXFTableEntryError:
            layout = self.doc.layouts.get(name)

        pw_mm = pw * scale
        ph_mm = ph * scale
        ox = view_center[0] - pw_mm / 2
        oy = view_center[1] - ph_mm / 2

        layout.page_setup(
            size=(pw, ph),
            margins=(0, 0, 0, 0),
            units="mm",
            scale_numerator=1,
            scale_denominator=scale,
        )

        b = border_mm * scale
        # 外框
        self.rect(ox, oy, ox + pw_mm, oy + ph_mm, "BORD-图框", 0.25)
        # 内框
        self.rect(ox + b, oy + b, ox + pw_mm - b, oy + ph_mm - b, "BORD-图框", 0.50)
        # 会签栏
        self.line(ox + pw_mm - b, oy + b, ox + pw_mm - 3 * b, oy + b, "BORD-图框", 0.25)

        # 标题栏数据
        tb_data = {
            "project": self.name,
            "drawing": name,
            "scale": f"1:{scale}",
            "version": self.version,
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "unit": "宜昌市水利水电勘察设计院",
        }
        self.title_block(layout, ox + b, oy + b, pw_mm - 2 * b, ph_mm - 2 * b, tb_data)
        return layout

    def title_block(self, layout, x, y, w, h, data):
        """绘制 A1 横向图框标题栏 (GB/T 14689-2008)"""
        tb_h = 56 * (w / 80000)
        tb_w = 180 * (w / 80000)
        tb_y = y
        tb_x = x + w - tb_w

        # 标题栏外框
        self.rect(tb_x, tb_y, tb_x + tb_w, tb_y + tb_h, "TBLK-标题栏", 0.35)
        row_h = tb_h / 4
        col_w = [tb_w * 0.15, tb_w * 0.35, tb_w * 0.15, tb_w * 0.35]

        rows_data = [
            [("单位", 1), (data.get("unit", ""), 3)],
            [("工程", 1), (data.get("project", ""), 3)],
            [("图纸", 1), (data.get("drawing", ""), 1),
             ("比例", 1), (f"1:{data.get('scale', '')}", 1)],
            [("日期", 1), (data.get("date", ""), 1),
             ("版次", 1), (data.get("version", ""), 1)],
        ]
        for ri, row in enumerate(rows_data):
            cy = tb_y + ri * row_h
            cx = tb_x
            for (txt, span) in row:
                cw = sum(col_w[si]) if isinstance(span, int) and span > 1 else col_w[0]
                # 竖向分割线
                if span == 1:
                    self.line(cx + col_w[0], cy, cx + col_w[0], cy + row_h, "TBLK-标题栏", 0.18)
                # 横向分割线
                if ri > 0:
                    self.line(tb_x, cy, tb_x + tb_w, cy, "TBLK-标题栏", 0.18)
                self.text_c(txt, cx + cw / 2, cy + row_h / 2, 2.0, "TBLK-标题栏")
                cx += cw

    # ===================== 图纸说明 & 材料表 =====================
    def note_block(self, x, y, w, notes, title="图纸说明"):
        """模型空间中的图纸说明"""
        h = len(notes) * 4.5 + 6
        self.rect(x, y, x + w, y + h, "NOTE-说明", 0.25)
        self.text_c(title, x + w / 2, y + h - 3, 3.0, "NOTE-说明")
        for i, note in enumerate(notes):
            self.text(f"{i + 1}. {note}", x + 2, y + h - 7 - i * 4.5, 2.5, "NOTE-说明")

    def note_block_ps(self, layout, x, y, w, notes, title="图纸说明"):
        """布局空间图纸说明"""
        h = len(notes) * 4.0 + 5
        layout.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)],
            dxfattribs={"layer": "NOTE-说明"})
        layout.add_text(title, height=2.5, dxfattribs={"layer": "NOTE-说明"}).set_pos(
            (x + w / 2, y + h - 3), align=TextEntityAlignment.CENTER)
        for i, note in enumerate(notes):
            layout.add_text(f"{i + 1}. {note}", height=2, dxfattribs={"layer": "NOTE-说明"}).set_pos(
                (x + 2, y + h - 6 - i * 4), align=TextEntityAlignment.LEFT)

    def material_table(self, layout, x, y, w, materials, scale_mm_per_unit=1):
        """材料表"""
        col_w = [w * 0.10, w * 0.40, w * 0.12, w * 0.13, w * 0.12, w * 0.13]
        row_h = 5.0
        header_h = 6.0
        tw = sum(col_w)
        total_h = header_h + len(materials) * row_h

        headers = ["编号", "名称及规格", "材料", "单位", "数量", "备注"]
        cx = x
        for hi, (hdr, cw) in enumerate(zip(headers, col_w)):
            self.line(cx, y, cx, y + total_h, "TBLK-标题栏", 0.15)
            layout.add_text(hdr, height=2.5, dxfattribs={"layer": "TBLK-标题栏"}).set_pos(
                (cx + cw / 2, y + total_h - header_h / 2), align=TextEntityAlignment.CENTER)
            cx += cw
        self.line(cx, y, cx, y + total_h, "TBLK-标题栏", 0.15)
        self.line(x, y + total_h - header_h, x + tw, y + total_h - header_h, "TBLK-标题栏", 0.15)
        self.line(x, y, x + tw, y, "TBLK-标题栏", 0.25)
        self.line(x, y + total_h, x + tw, y + total_h, "TBLK-标题栏", 0.25)
        self.line(x, y, x, y + total_h, "TBLK-标题栏", 0.25)
        self.line(x + tw, y, x + tw, y + total_h, "TBLK-标题栏", 0.25)

        for mi, mat in enumerate(materials):
            ry = y + total_h - header_h - (mi + 1) * row_h
            for ci, cw in enumerate(col_w):
                val = str(mat[ci]) if ci < len(mat) else ""
                layout.add_text(val, height=2, dxfattribs={"layer": "TBLK-标题栏"}).set_pos(
                    (x + sum(col_w[:ci]) + cw / 2, ry + row_h / 2),
                    align=TextEntityAlignment.CENTER)
            self.line(x, ry, x + tw, ry, "TBLK-标题栏", 0.10)
    # ===================== UCS 坐标变换 =====================
    def with_ucs(self, origin=(0, 0, 0), rotation=0):
        """创建旋转 UCS 并返回变换函数"""
        ucs = UCS()
        ucs = ucs.rotate_local_z(math.radians(rotation))
        ucs = ucs.moveto(Vec3(origin))
        return ucs

    def points_to_wcs(self, points, ucs):
        """将 UCS 坐标批量转为 WCS"""
        return [tuple(ucs.to_wcs(Vec3(p))) for p in points]

    # ===================== 路径操作 (fillet/chamfer/gear) =====================
    def path_fillet(self, pts, radius):
        """对折线路径倒圆角 (近似算法)"""
        if len(pts) < 3:
            return pts
        result = [pts[0]]
        for i in range(1, len(pts) - 1):
            v1 = Vec2(pts[i]) - Vec2(pts[i-1])
            v2 = Vec2(pts[i+1]) - Vec2(pts[i])
            d1, d2 = v1.normalize(), v2.normalize()
            angle = d1.angle_between(d2)
            r = min(radius, min(v1.magnitude, v2.magnitude) * 0.4)
            if angle > 0.01 and r > 1:
                offset_prev = d1 * r
                offset_next = -d2 * r
                p1 = Vec2(pts[i]) - offset_prev
                p2 = Vec2(pts[i]) + offset_next
                result.append((p1.x, p1.y))
                n = 8
                for j in range(1, n):
                    frac = j / n
                    t = d1.lerp(-d2, frac).normalize()
                    mp = Vec2(pts[i]) + t * r
                    result.append((mp.x, mp.y))
                result.append((p2.x, p2.y))
            else:
                result.append(pts[i])
        result.append(pts[-1])
        return result

    def path_chamfer(self, pts, distance):
        """对折线路径倒角 (近似算法)"""
        if len(pts) < 3:
            return pts
        result = [pts[0]]
        for i in range(1, len(pts) - 1):
            v1 = Vec2(pts[i]) - Vec2(pts[i-1])
            v2 = Vec2(pts[i+1]) - Vec2(pts[i])
            d1, d2 = v1.normalize(), v2.normalize()
            d = min(distance, min(v1.magnitude, v2.magnitude) * 0.4)
            if d > 1:
                p1 = Vec2(pts[i]) - d1 * d
                p2 = Vec2(pts[i]) + d2 * d
                result.append((p1.x, p1.y))
                result.append((p2.x, p2.y))
            else:
                result.append(pts[i])
        result.append(pts[-1])
        return result

    def draw_gear(self, cx, cy, teeth, pitch_radius, layer="0-建筑"):
        """绘制渐开线齿轮轮廓"""
        g = ezpath.gear(count=teeth, top_width=30, bottom_width=20, height=80, outside_radius=pitch_radius)
        from ezdxf.path import render_lwpolylines
        render_lwpolylines(self.msp, [g.transform(Matrix44.translate(cx, cy, 0))], dxfattribs={"layer": layer})

    def draw_star(self, cx, cy, outer_r, inner_r, points=5, layer="SYMB-符号"):
        """绘制星形"""
        s = ezpath.star(outer=outer_r, inner=inner_r, points=points)
        star_pts = [(cx + v[0], cy + v[1]) for v in s]
        return self.msp.add_lwpolyline(star_pts, dxfattribs={"layer": layer})

    def draw_ngon(self, cx, cy, n, r, layer="0-建筑", rot=0):
        """绘制正多边形"""
        ng = ezpath.ngon(cx=cx, cy=cy, n=n, r=r)
        if rot:
            ucs = UCS().rotate_local_z(math.radians(rot))
            ng = [ucs.to_wcs(Vec3(v))[:2] for v in ng]
        return self.msp.add_lwpolyline(ng, dxfattribs={"layer": layer})

    def draw_gear_ext(self, cx, cy, teeth, pitch_radius):
        """高级齿轮绘制（使用 pyclipper 优化）"""
        if HAS_PYCLIPPER:
            g = ezpath.gear(count=teeth, top_width=30, bottom_width=20, height=80, outside_radius=pitch_radius)
            from ezdxf.path import render_lwpolylines
            render_lwpolylines(self.msp, [g.transform(Matrix44.translate(cx, cy, 0))], dxfattribs={"layer": "M-STRU-金属结构"})
        return self.draw_gear(cx, cy, teeth, pitch_radius)

    # ===================== 构造几何工具 =====================
    def construction_intersection(self, line1_pts, line2_pts):
        """求两直线交点"""
        p1a = line1_pts[0] if isinstance(line1_pts[0], (list, tuple)) else (line1_pts[0], line1_pts[1])
        p1b = line1_pts[2] if isinstance(line1_pts[0], (list, tuple)) else (line1_pts[2], line1_pts[3])
        p2a = line2_pts[0] if isinstance(line2_pts[0], (list, tuple)) else (line2_pts[0], line2_pts[1])
        p2b = line2_pts[2] if isinstance(line2_pts[0], (list, tuple)) else (line2_pts[2], line2_pts[3])
        l1 = ConstructionLine(Vec2(p1a), Vec2(p1b))
        l2 = ConstructionLine(Vec2(p2a), Vec2(p2b))
        pt = intersection_line_line_2d((l1.start, l1.end), (l2.start, l2.end))
        return (pt.x, pt.y) if pt else None

    def convex_hull(self, points):
        """计算点集凸包"""
        result = convex_hull_2d([Vec2(p) for p in points])
        return [(p.x, p.y) for p in result]

    def point_in_polygon(self, pt, polygon):
        """判断点是否在多边形内"""
        return is_point_in_polygon_2d(Vec2(pt), [Vec2(p) for p in polygon])

    def offset_points(self, pts, distance):
        """偏置点集"""
        result = offset_vertices_2d([Vec2(p) for p in pts], distance)
        return [(p.x, p.y) for p in result]

    # ===================== EulerSpiral / 蜗壳螺旋线 =====================
    def spiral_case(self, cx, cy, r_max, turns=2.5, segments=200, layer="M-HYDR-水力"):
        """生成蜗壳螺旋线 (EulerSpiral 近似)"""
        from ezdxf.math import EulerSpiral
        spiral = EulerSpiral()
        pts = []
        for i in range(segments + 1):
            t = i / segments * turns * 2 * math.pi
            r = (t / (turns * 2 * math.pi)) * r_max
            x = cx + r * math.cos(t)
            y = cy + r * math.sin(t)
            pts.append((x, y))
        return self.msp.add_spline(pts, dxfattribs={"layer": layer})

    # ===================== 3D 导出 (CadQuery → STEP) =====================
    def export_step(self, filepath, shape_func=None):
        """使用 CadQuery 导出 3D STEP 文件"""
        if not HAS_CADQUERY:
            raise ImportError("cadquery 未安装。运行: pip install cadquery")
        import cadquery as cq
        result = shape_func(cq) if shape_func else cq.Workplane("XY").box(100, 100, 100)
        cq.exporters.export(result, filepath)
        return filepath

    # ===================== 审计 & 验证 =====================
    def validate(self):
        """运行 DXF 审计，返回错误列表"""
        self._validation_errors = []
        auditor = Auditor(self.doc)
        auditor.run()
        for error in auditor.errors:
            self._validation_errors.append(str(error))
        return self._validation_errors

    def print_validation_report(self):
        """打印审计报告"""
        errors = self.validate()
        if not errors:
            print("  [✓] DXF 审计通过，无错误")
            return
        print(f"  [!] DXF 审计发现 {len(errors)} 个问题:")
        for e in errors[:10]:
            print(f"      - {e}")
        if len(errors) > 10:
            print(f"      ... 还有 {len(errors) - 10} 个问题")

    # ===================== SVG 导出 =====================
    def export_svg(self, filepath, width=1600, height=1200):
        """导出为 SVG 矢量图"""
        if not HAS_SVGWRITE:
            raise ImportError("svgwrite 未安装。运行: pip install svgwrite")
        dwg = svgwrite.Drawing(filepath, size=(f"{width}px", f"{height}px"))
        # 遍历模型空间实体，简化绘制
        for e in self.msp:
            if e.dxftype() == "LINE":
                s = e.dxf.start
                end = e.dxf.end
                dwg.add(dwg.line(
                    (s.x, s.y), (end.x, end.y),
                    stroke="black", stroke_width=0.5,
                ))
        dwg.save()
        return filepath

    # ===================== 保存 =====================
    def save(self, path):
        """保存 DXF 文件并自动审计"""
        self.validate()
        self.doc.saveas(path)
        print(f"  [✓] 已保存: {os.path.basename(path)}")
        self.print_validation_report()
        return path
