# ======================================================================
#  cad_toolbox_v6.py — 岩泊渡水电站 专业施工图工具箱 v6.1 (专业升级版)
#  新增: 引线标注、多链尺寸、图纸说明、剖切符号(带转折)、会签栏
# ======================================================================
import ezdxf, math, os
from ezdxf.enums import TextEntityAlignment
from ezdxf.math import Vec2
from ezdxf import units
from ezdxf.tools.standards import setup_dimstyle
from ezdxf.render.arrows import ARROWS as _ARROWS
from ezdxf.layouts import Paperspace
import ezdxf.zoom as zoom

# =========================== 国标配置 ===========================
GB_LAYERS = {
    "0-建筑":        (7, "CONTINUOUS"),
    "S-CONC-混凝土":  (8, "CONTINUOUS"),
    "S-REIN-钢筋":    (5, "CONTINUOUS"),
    "M-EQPM-设备":    (7, "CONTINUOUS"),
    "M-HYDR-水力":    (4, "CONTINUOUS"),
    "M-STRU-结构":    (3, "CONTINUOUS"),
    "A-WALL-墙体":    (7, "CONTINUOUS"),
    "A-COLM-立柱":    (6, "CONTINUOUS"),
    "A-OVHD-吊车":    (5, "DASHED2"),
    "A-ROOF-屋面":    (7, "CONTINUOUS"),
    "A-FLOR-楼面":    (4, "CONTINUOUS"),
    "DIM-尺寸":      (3, "CONTINUOUS"),
    "TEXT-文字":      (7, "CONTINUOUS"),
    "HATCH-填充":     (8, "CONTINUOUS"),
    "SYMB-符号":      (6, "CONTINUOUS"),
    "AXIS-轴线":      (1, "CENTER2"),
    "HIDN-隐藏":      (5, "DASHED2"),
    "BORD-图框":      (7, "CONTINUOUS"),
    "TBLK-标题栏":    (2, "CONTINUOUS"),
    "LEAD-引线":      (4, "CONTINUOUS"),
    "NOTE-说明":      (7, "CONTINUOUS"),
    "VIEWPORTS":     (7, "CONTINUOUS"),
}

PAPER_SIZES = {
    "A0": (841, 1189), "A1": (594, 841), "A2": (420, 594),
    "A3": (297, 420), "A4": (210, 297),
}

class HydroProject:
    def __init__(self, name="岩泊渡水电站"):
        self.name = name
        self.doc = ezdxf.new("R2010", units=units.MM, setup=True)
        self.msp = self.doc.modelspace()
        self._setup_all()
        
    def _setup_all(self):
        self._setup_layers()
        self._setup_dimstyles()
        self._setup_styles()
        self._create_blocks()
        
    def _setup_styles(self):
        for name, font in [("HZ","simsun.ttc"),("TXT","txt"),("COMPLEX","complex")]:
            if name not in self.doc.styles:
                s = self.doc.styles.new(name, dxfattribs={"font": font, "height": 0})
                if name == "HZ":
                    s.dxf.width = 0.7
                    
    def _setup_layers(self):
        for name, (c, lt) in GB_LAYERS.items():
            if name not in self.doc.layers:
                try:
                    self.doc.layers.new(name, dxfattribs={"color": c, "linetype": lt})
                except:
                    pass
        if "VIEWPORTS" in self.doc.layers:
            self.doc.layers.get("VIEWPORTS").off()
            
    def _setup_dimstyles(self):
        for scale in [100, 150, 200, 50]:
            name = f"GB_DIM_{scale}"
            ds = setup_dimstyle(self.doc, fmt=f"EZ_M_{scale}_H25_CM", name=name)
            if ds:
                ds.dxf.dimtsz = 1.0
                ds.dxf.dimtad = 1
                ds.dxf.dimtix = 0
                ds.dxf.dimclrd = 3
                ds.dxf.dimclre = 3
                ds.dxf.dimclrt = 7
                ds.dxf.dimdec = 0
                ds.dxf.dimzin = 8
                ds.dxf.dimdsep = ord(".")
                ds.dxf.dimtxsty = "HZ"
                
    def _create_blocks(self):
        from ezdxf.render.arrows import ARROWS as _ARROWS
        blk = self.doc.blocks
        
        # 1. 高程符号
        if "标高" not in blk:
            b = blk.new(name="标高")
            b.add_line((-6, 0), (6, 0), dxfattribs={"layer": "SYMB-符号"})
            b.add_line((6, 0), (0, -5), dxfattribs={"layer": "SYMB-符号"})
            b.add_line((0, -5), (-6, 0), dxfattribs={"layer": "SYMB-符号"})
            b.add_attdef("VAL", (8, -2.5), dxfattribs={"layer": "TEXT-文字", "height": 3.0, "style": "HZ"})
            
        # 2. 轴号
        if "轴号" not in blk:
            b = blk.new(name="轴号")
            b.add_circle((0, 0), 5, dxfattribs={"layer": "AXIS-轴线"})
            b.add_attdef("NUM", (0, -2), dxfattribs={"layer": "TEXT-文字", "height": 3.5, "style": "HZ"})
            
        # 3. 剖切符号（带箭头）
        if "剖切符号" not in blk:
            b = blk.new(name="剖切符号")
            b.add_line((0, 0), (12, 0), dxfattribs={"layer": "SYMB-符号", "lineweight": 50})
            b.add_line((12, 0), (15, 3), dxfattribs={"layer": "SYMB-符号"})
            b.add_line((12, 0), (15, -3), dxfattribs={"layer": "SYMB-符号"})
            b.add_attdef("NAME", (2, -6), dxfattribs={"layer": "TEXT-文字", "height": 4.0, "style": "HZ"})

        from ezdxf.render.arrows import ARROWS as _ARROWS
        # 4. ??????? (ACAD ????)
        self._arrow_closed_blank = _ARROWS.create_block(self.doc.blocks, _ARROWS.closed_blank)
        self._arrow_closed_filled = _ARROWS.create_block(self.doc.blocks, _ARROWS.closed_filled)

    # ====================== 基本绘图 ======================
    
    def line(self, x1, y1, x2, y2, layer="0-建筑", lw=0.25):
        self.msp.add_line((x1,y1), (x2,y2), dxfattribs={"layer": layer, "lineweight": int(lw*100)})
        
    def polyline(self, pts, layer="0-建筑", lw=0.25):
        if len(pts) < 2: return
        self.msp.add_lwpolyline(pts, dxfattribs={"layer": layer, "lineweight": int(lw*100)})
        
    def rect(self, x1, y1, x2, y2, layer="0-建筑", lw=0.25):
        self.msp.add_lwpolyline([(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)],
            dxfattribs={"layer": layer, "lineweight": int(lw*100)})
        
    def circle(self, x, y, r, layer="0-建筑", lw=0.25):
        self.msp.add_circle((x,y), r, dxfattribs={"layer": layer, "lineweight": int(lw*100)})
        
    def text(self, txt, x, y, h=2.5, layer="TEXT-文字", rot=0):
        t = self.msp.add_text(txt, height=h, dxfattribs={"layer": layer, "style": "HZ", "rotation": rot})
        t.set_placement((x, y), align=TextEntityAlignment.LEFT)
        
    def text_c(self, txt, x, y, h=2.5, layer="TEXT-文字"):
        t = self.msp.add_text(txt, height=h, dxfattribs={"layer": layer, "style": "HZ"})
        t.set_placement((x, y), align=TextEntityAlignment.CENTER)
        
    def axis_line(self, x1, y1, x2, y2):
        self.line(x1, y1, x2, y2, "AXIS-轴线", 0.15)
        
    def elevation(self, x, y, val, layer="SYMB-符号"):
        ref = self.msp.add_auto_blockref("标高", (x, y), {"VAL": f"▽{val:.0f}"})
        
    def axis_circle(self, x, y, num, layer="AXIS-轴线"):
        ref = self.msp.add_auto_blockref("轴号", (x, y-5), {"NUM": str(num)})
        self.line(x-20, y, x+20, y, "AXIS-轴线", 0.15)
        
    def hatch_solid(self, pts, color=253):
        if len(pts) < 3: return
        hatch = self.msp.add_hatch(dxfattribs={"layer": "HATCH-填充", "color": color})
        hatch.paths.add_polyline_path(pts, is_closed=True)
        
    def hatch_fill(self, pts, pattern="ANSI31", scale=100, color=8):
        if len(pts) < 3: return
        hatch = self.msp.add_hatch(dxfattribs={"layer": "HATCH-填充", "color": color})
        hatch.set_pattern_fill(pattern, scale=scale)
        hatch.paths.add_polyline_path(pts, is_closed=True)
        
    def dim_h(self, y, x1, x2, text="", scale=100):
        if abs(x2 - x1) < 1: return
        ds = f"GB_DIM_{scale}"
        dim = self.msp.add_linear_dim(base=(x1, y), p1=(x1, y), p2=(x2, y), dimstyle=ds)
        dim.render()
        if text:
            dim.set_text_format(f"<> {text}")
            
    def dim_v(self, x, y1, y2, text="", scale=100):
        if abs(y2 - y1) < 1: return
        ds = f"GB_DIM_{scale}"
        dim = self.msp.add_linear_dim(base=(x, y1), p1=(x, y1), p2=(x, y2), dimstyle=ds)
        dim.render()
        if text:
            dim.set_text_format(f"<> {text}")
            
    # ====================== 新增功能 ======================
    
    def add_leader(self, x1, y1, x2, y2, text, h=3.0, gap=300):
        """引线标注: 从 (x1,y1) 引出折线到 (x2,y2), 末端带文字"""
        layer = "LEAD-引线"
        # 带箭头的引线
        pts = [(x1, y1), (x2, y2)]
        self.msp.add_lwpolyline(pts, dxfattribs={"layer": layer, "lineweight": 25})
        # 箭头块
        self.msp.add_blockref(self._arrow_closed_blank, (x1, y1), dxfattribs={"layer": layer, "rotation": self._angle(x1,y1,x2,y2)})
        # 文字（默认在终点右侧）
        tx, ty = x2 + gap, y2
        self.text(text, tx, ty - h/2, h, "TEXT-文字")
        # 文字下划线
        txt_w = len(text) * h * 0.6
        self.line(tx, ty - h*0.8, tx + txt_w, ty - h*0.8, "LEAD-引线", 0.15)
        
    def _angle(self, x1, y1, x2, y2):
        dx, dy = x2-x1, y2-y1
        return math.degrees(math.atan2(dy, dx))
        
    def add_multi_dim_h(self, y, segments, scale=100):
        """多链水平尺寸: segments = [(x1,x2,label), ...]"""
        for x1, x2, label in segments:
            if abs(x2-x1) > 1:
                ds = f"GB_DIM_{scale}"
                dim = self.msp.add_linear_dim(base=(x1, y), p1=(x1, y), p2=(x2, y), dimstyle=ds)
                if label:
                    dim.set_text_format(f"<> {label}")
                dim.render()
                    
    def add_multi_dim_v(self, x, segments, scale=100):
        """多链垂直尺寸"""
        for y1, y2, label in segments:
            if abs(y2-y1) > 1:
                ds = f"GB_DIM_{scale}"
                dim = self.msp.add_linear_dim(base=(x, y1), p1=(x, y1), p2=(x, y2), dimstyle=ds)
                if label:
                    dim.set_text_format(f"<> {label}")
                dim.render()

    def add_section_mark(self, label, x, y, direction="right"):
        """剖切符号: 在 (x,y) 位置放置带文字的剖切符号"""
        ref = self.msp.add_auto_blockref("剖切符号", (x, y), {"NAME": label})
        if direction == "left":
            ref.dxf.rotation = 180.0
        elif direction == "up":
            ref.dxf.rotation = 90.0
        elif direction == "down":
            ref.dxf.rotation = 270.0
            
    def add_section_line_turn(self, label, pts):
        """剖切转折线: pts = [(x1,y1), (x2,y2), ...] 剖切路径带两端箭头"""
        if len(pts) < 2: return
        self.msp.add_lwpolyline(pts, dxfattribs={"layer": "SYMB-符号", "lineweight": 60})
        # 起始端箭头
        self.msp.add_blockref(self._arrow_closed_blank, pts[0], dxfattribs={"layer": "SYMB-符号",
            "rotation": self._angle(pts[0][0], pts[0][1], pts[1][0], pts[1][1])})
        # 末端箭头
        self.msp.add_blockref(self._arrow_closed_blank, pts[-1], dxfattribs={"layer": "SYMB-符号",
            "rotation": self._angle(pts[-2][0], pts[-2][1], pts[-1][0], pts[-1][1]) + 180})
        # 两端标注
        x1, y1 = pts[0]
        self.text_c(label, x1 + (x1-pts[1][0])*0.5, y1 + (y1-pts[1][1])*0.5, 4.0, "SYMB-符号")
        xn, yn = pts[-1]
        xn2, yn2 = pts[-2]
        self.text_c(label, xn + (xn-xn2)*0.5, yn + (yn-yn2)*0.5, 4.0, "SYMB-符号")

    def add_note_block(self, x, y, w, notes, title="图纸说明"):
        """图纸说明区"""
        n = len(notes) + 1  # +1 for title
        rh = 6.0
        h = n * rh + 4
        # 外框
        self.msp.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)],
            dxfattribs={"layer": "NOTE-说明", "lineweight": 25})
        # 标题行
        self.msp.add_lwpolyline([(x,y+h-rh),(x+w,y+h-rh)],
            dxfattribs={"layer": "NOTE-说明", "lineweight": 15})
        self.text_c(title, x+w/2, y+h-rh+1, 3.5, "NOTE-说明")
        # 说明条目
        for i, note in enumerate(notes):
            ty = y + h - (i+1)*rh - rh
            self.text(f"{i+1}. {note}", x+3, ty+1, 2.5, "NOTE-说明")
            
    # ====================== Paper Space 布局 ======================
    
    def create_layout(self, name, paper_size, scale, view_center, view_size_mm=None,
                     border_mm=15, landscape=False):
        pw, ph = PAPER_SIZES[paper_size]
        if landscape: pw, ph = ph, pw
        layout = self.doc.layouts.new(name)
        layout.page_setup(size=(pw, ph), margins=(border_mm,border_mm,border_mm,border_mm), units="mm")
        for vp in list(layout.query("VIEWPORT")):
            layout.delete_entity(vp)
        vp_w = pw - 2*border_mm
        vp_h = ph - 2*border_mm
        if view_size_mm:
            vp_w, vp_h = view_size_mm
        view_h = vp_h * scale
        vp = layout.add_viewport(
            center=(pw/2, ph/2), size=(vp_w, vp_h),
            view_center_point=view_center, view_height=view_h, status=2)
        vp.dxf.layer = "VIEWPORTS"
        layout.add_lwpolyline([(0,0),(pw,0),(pw,ph),(0,ph),(0,0)],
            dxfattribs={"layer": "BORD-图框", "lineweight": 70})
        layout.add_lwpolyline([(10,10),(pw-10,10),(pw-10,ph-10),(10,ph-10),(10,10)],
            dxfattribs={"layer": "BORD-图框", "lineweight": 35})
        return layout, pw, ph
        
    def add_title_block(self, layout, x, y, w, h, data):
        """完整标题栏 + 会签栏"""
        # 左半：图纸信息
        left_w = int(w * 0.65)
        rows_def = [
            ("工程项目", data.get("project", "")),
            ("子项名称", data.get("subname", "")),
            ("图纸名称", data.get("dname", "")),
            ("图号",     data.get("dno", "")),
            ("比例",     data.get("scale", "")),
            ("阶段",     data.get("stage", "施工图")),
            ("日期",     data.get("date", "2026.05")),
            ("图幅",     data.get("size", "")),
            ("第 1 张",  data.get("sheets", "共 1 张")),
        ]
        n = len(rows_def)
        rh = h / n
        # 画左半标题栏
        for i, (label, value) in enumerate(rows_def):
            y1 = y + i*rh
            self._tblk_cell(layout, x, y1, left_w, rh, f"{label}: {value}")
        
        # 右半：会签栏
        right_x = x + left_w
        right_w = w - left_w
        sign_rows = [
            ("设计", data.get("designer", "")),
            ("制图", data.get("drafter", "")),
            ("校对", data.get("checker", "")),
            ("审核", data.get("auditor", "")),
            ("批准", data.get("approver", "")),
            ("审定", data.get("reviewer", "")),
            ("专业", data.get("major", "水工")),
        ]
        sr = len(sign_rows)
        srh = h / sr
        # 画标题"会签"
        layout.add_text("会 签", height=3.5,
            dxfattribs={"layer": "TEXT-文字", "style": "HZ"}
            ).set_placement((right_x+2, y+h-srh+1), align=TextEntityAlignment.LEFT)
        for i, (label, value) in enumerate(sign_rows):
            y1 = y + i*srh
            self._tblk_cell(layout, right_x, y1, right_w, srh, f"{label}: {value}")

    def _tblk_cell(self, layout, x, y, w, h, text):
        layout.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)],
            dxfattribs={"layer": "TBLK-标题栏", "lineweight": 15})
        layout.add_text(text, height=2.5,
            dxfattribs={"layer": "TEXT-文字", "style": "HZ"}
            ).set_placement((x+2, y+1), align=TextEntityAlignment.LEFT)
                
    def add_material_table(self, layout, x, y, w, materials):
        headers = ["序号", "名称", "规格/型号", "单位", "数量", "备注"]
        col_widths = [8, 40, 28, 12, 14, 20]
        row_h = 6.0
        n_rows = len(materials) + 1
        th = n_rows * row_h
        layout.add_lwpolyline([(x,y),(x+w,y),(x+w,y+th),(x,y+th),(x,y)],
            dxfattribs={"layer": "TBLK-标题栏", "lineweight": 25})
        # 表头
        cx = x
        for hi, (hdr, cw) in enumerate(zip(headers, col_widths)):
            layout.add_lwpolyline([(cx,y+th-row_h),(cx+cw,y+th-row_h),
                (cx+cw,y+th),(cx,y+th),(cx,y+th-row_h)],
                dxfattribs={"layer": "TBLK-标题栏", "lineweight": 15})
            layout.add_text(hdr, height=2.5,
                dxfattribs={"layer": "TEXT-文字", "style": "HZ"}
                ).set_placement((cx+1, y+th-row_h+1), align=TextEntityAlignment.LEFT)
            cx += cw
        for ri, mat in enumerate(materials):
            ry = y + th - (ri+1)*row_h
            cx = x
            for ci, val in enumerate([ri+1, *mat]):
                cw = col_widths[ci]
                layout.add_text(str(val), height=2.0,
                    dxfattribs={"layer": "TEXT-文字", "style": "HZ"}
                    ).set_placement((cx+1, ry+1), align=TextEntityAlignment.LEFT)
                cx += cw
    
    def add_drawing_note_ps(self, layout, x, y, w, notes, title="图纸说明"):
        """在 Paper Space 中添加图纸说明"""
        n = len(notes)
        rh = 6.0
        h = (n + 1) * rh + 4
        layout.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)],
            dxfattribs={"layer": "NOTE-说明", "lineweight": 25})
        layout.add_lwpolyline([(x,y+h-rh),(x+w,y+h-rh)],
            dxfattribs={"layer": "NOTE-说明", "lineweight": 15})
        layout.add_text(title, height=3.5,
            dxfattribs={"layer": "TEXT-文字", "style": "HZ"}
            ).set_placement((x+w/2, y+h-rh+1), align=TextEntityAlignment.CENTER)
        for i, note in enumerate(notes):
            ty = y + h - (i+1)*rh - rh
            layout.add_text(f"{i+1}. {note}", height=2.5,
                dxfattribs={"layer": "TEXT-文字", "style": "HZ"}
                ).set_placement((x+3, ty+1), align=TextEntityAlignment.LEFT)
                
    # ====================== 输出 ======================
    
    def save(self, path):
        zoom.extents(self.msp, factor=1.1)
        self.doc.saveas(path)
        return path
