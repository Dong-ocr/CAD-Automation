# ======================================================================
#  cad_toolbox.py — CAD 统一绘图工具箱
#
#  所有绘图任务的单入口库。包含：
#    - 基本图元（线/圆/弧/矩形/文字）
#    - 尺寸标注（带箭头）
#    - 剖面线/填充
#    - 表面粗糙度符号
#    - 形位公差框格
#    - 螺纹表示
#    - 图层预设
#    - 图框/标题栏
#    - SVG/PDF 导出
#
#  用法：
#    from cad_toolbox import CADProject
#    p = CADProject("零件图")
#    p.line(0,0, 100,0, "OUTLINE")
#    p.dim_h(0, 100, -10)
#    p.save("output.dxf")
#    p.export_pdf("output.pdf")
# ======================================================================

import ezdxf, math, os
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment
from hatch_lib import HatchFiller
from frame_lib import FrameLib
from render import DXFRenderer

AL = TextEntityAlignment.MIDDLE_CENTER


class CADProject:
    """统一 CAD 项目类 — 管理画布、图层、样式、输出"""

    # ── 常用图层预设 ──────────────────────────────────────────────
    PRESET_LAYERS = {
        # (name, color, linetype)
        "OUTLINE":      (7, "CONTINUOUS"),
        "HIDDEN":       (5, "HIDDEN"),
        "CENTERLINE":   (1, "CENTER2"),
        "DIMENSION":    (3, "CONTINUOUS"),
        "TEXT":         (7, "CONTINUOUS"),
        "TITLE":        (2, "CONTINUOUS"),
        "SECTION":      (7, "CONTINUOUS"),
        "HATCH":        (8, "CONTINUOUS"),
        "THREAD":       (4, "CONTINUOUS"),
        "TOLERANCE":    (6, "CONTINUOUS"),
        "ROUGHNESS":    (6, "CONTINUOUS"),
        "AUX":          (4, "DASHED2"),
        "BORDER":       (7, "CONTINUOUS"),
        "FILL":         (8, "CONTINUOUS"),
    }

    def __init__(self, title="Untitled"):
        self.doc = ezdxf.new("R2010")
        self.msp = self.doc.modelspace()
        self.title = title
        self._last_dxf = None
        self._setup()
        print("  CADProject: '%s' initialized" % title)

    def _setup(self):
        """Setup default styles and layers"""
        # Standard style
        self.doc.styles.new("TXT", dxfattribs={"font": "txt", "height": 2.5})
        # Setup dimstyles for dimension addon
        try:
            from ezdxf.addons import dimstyles
            dimstyles.setup(self.doc)
            style = self.doc.dimstyles.get("Standard")
            style.dxf.dimtxt = 2.5
            style.dxf.dimtsz = 1.0
            style.dxf.dimtad = 1
            style.dxf.dimasz = 1.5
        except:
            pass

    def setup_layers(self, *layer_names):
        """Setup specific layers or all preset layers

        Usage:
            p.setup_layers()                          # all presets
            p.setup_layers("OUTLINE", "DIMENSION")     # specific only
        """
        if not layer_names:
            layer_names = self.PRESET_LAYERS.keys()
        for name in layer_names:
            if name in self.PRESET_LAYERS:
                c, lt = self.PRESET_LAYERS[name]
                if name not in self.doc.layers:
                    lt_val = "CONTINUOUS" if lt == 1 else lt
                    self.doc.layers.new(name, dxfattribs={"color": c, "linetype": lt_val})

    # ══════════════════════════════════════════════════════════════
    #  基本图元
    # ══════════════════════════════════════════════════════════════

    def line(self, x1, y1, x2, y2, layer="OUTLINE", lw=0.5):
        """画直线"""
        self.msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": layer, "lineweight": lw})

    def circle(self, cx, cy, r, layer="OUTLINE", lw=0.5):
        """画圆"""
        self.msp.add_circle((cx, cy), r, dxfattribs={"layer": layer, "lineweight": lw})

    def arc(self, cx, cy, r, a1, a2, layer="OUTLINE", lw=0.5):
        """画圆弧（角度制）"""
        if a2 <= a1:
            a2 += 360
        self.msp.add_arc((cx, cy), r, a1, a2, dxfattribs={"layer": layer, "lineweight": lw})

    def rect(self, cx, cy, w, h, layer="OUTLINE", lw=0.5):
        """矩形（中心点+宽高）"""
        x1, y1 = cx - w / 2, cy - h / 2
        x2, y2 = cx + w / 2, cy + h / 2
        self.polyline([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], layer, lw)

    def rect_xy(self, x1, y1, x2, y2, layer="OUTLINE", lw=0.5):
        """矩形（两点）"""
        self.polyline([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], layer, lw)

    def polyline(self, pts, layer="OUTLINE", lw=0.5, closed=True):
        """画多段线"""
        pts = list(pts)
        if closed and pts[0] != pts[-1]:
            pts.append(pts[0])
        self.msp.add_lwpolyline(pts, dxfattribs={"layer": layer, "lineweight": lw})

    def text(self, text, x, y, h=2.5, layer="TEXT", rot=0):
        """写文字"""
        te = self.msp.add_text(str(text), height=h, dxfattribs={"layer": layer, "lineweight": 0.25})
        te.set_placement((x, y), align=AL)
        if rot:
            te.dxf.rotation = rot

    # ══════════════════════════════════════════════════════════════
    #  尺寸标注
    # ══════════════════════════════════════════════════════════════

    def dim_h(self, x1, x2, y, offset=12, text=None, layer="DIMENSION"):
        """水平尺寸标注（带箭头）"""
        mid = (x1 + x2) / 2
        arr = 2.5
        L = layer
        self.line(x1, y, x2, y, L, 0.18)
        self.line(x1, y, x1, y - 3, L, 0.18)
        self.line(x2, y, x2, y - 3, L, 0.18)
        # arrows
        self.line(x1, y, x1 + arr, y - arr * 0.5, L, 0.18)
        self.line(x1, y, x1 + arr, y + arr * 0.5, L, 0.18)
        self.line(x2, y, x2 - arr, y - arr * 0.5, L, 0.18)
        self.line(x2, y, x2 - arr, y + arr * 0.5, L, 0.18)
        self.text(text or str(int(abs(x2 - x1))), mid, y + offset + 1, 2.5, L)

    def dim_v(self, x, y1, y2, offset=12, text=None, layer="DIMENSION"):
        """垂直尺寸标注"""
        mid = (y1 + y2) / 2
        arr = 2.5
        L = layer
        self.line(x, y1, x, y2, L, 0.18)
        self.line(x, y1, x + 3, y1, L, 0.18)
        self.line(x, y2, x + 3, y2, L, 0.18)
        # arrows
        self.line(x, y1, x + arr * 0.5, y1 + arr, L, 0.18)
        self.line(x, y1, x - arr * 0.5, y1 + arr, L, 0.18)
        self.line(x, y2, x + arr * 0.5, y2 - arr, L, 0.18)
        self.line(x, y2, x - arr * 0.5, y2 - arr, L, 0.18)
        self.text(text or str(int(abs(y2 - y1))), x + offset + 1, mid, 2.5, L, rot=90)

    def dim_radius(self, cx, cy, r, x, y, text=None, layer="DIMENSION"):
        """半径标注"""
        L = layer
        self.line(cx, cy, x, y, L, 0.18)
        self.line(cx, cy, cx + (x - cx) * 0.7, cy + (y - cy) * 0.7, L, 0.18)
        self.text(text or ("R%d" % r), (cx + x) / 2, (cy + y) / 2 + 3, 2.5, L)

    # ══════════════════════════════════════════════════════════════
    #  剖面线 / 填充
    # ══════════════════════════════════════════════════════════════

    def hatch_section(self, boundary_pts, pattern="ANSI31", scale=1.2, angle=0, color=7, layer="HATCH"):
        """添加剖面线（边界点列表）"""
        if len(boundary_pts) < 3:
            return None
        h = self.msp.add_hatch(color=color, dxfattribs={"layer": layer})
        h.set_pattern_fill(pattern, angle=angle, scale=scale)
        pts = list(boundary_pts)
        if pts[0] != pts[-1]:
            pts.append(pts[0])
        try:
            h.paths.add_polyline_path(pts)
        except:
            pass
        return h

    def hatch_solid(self, pts, color=7, layer="FILL"):
        """实心填充"""
        if len(pts) < 3:
            return None
        h = self.msp.add_hatch(color=color, dxfattribs={"layer": layer})
        h.set_solid_fill()
        pts = list(pts)
        if pts[0] != pts[-1]:
            pts.append(pts[0])
        try:
            h.paths.add_polyline_path(pts)
        except:
            pass
        return h

    # ══════════════════════════════════════════════════════════════
    #  表面粗糙度
    # ══════════════════════════════════════════════════════════════

    def roughness(self, x, y, ra=3.2, s=5, layer="ROUGHNESS"):
        """标准表面粗糙度符号 ✓Ra X.X"""
        h = s * 1.5
        self.polyline([(x, y), (x + s, y - h), (x, y - 2 * h)], layer, 0.25, closed=False)
        self.line(x + s, y - h, x + s + s * 0.6, y - h, layer, 0.25)
        self.text("Ra %.1f" % ra, x + s + s * 0.3, y - h, 2, "TEXT")

    # ══════════════════════════════════════════════════════════════
    #  形位公差
    # ══════════════════════════════════════════════════════════════

    def tolerance(self, x, y, feature="//", tolerance="0.02", datum=None, w=50, h=10, layer="TOLERANCE"):
        """形位公差框格"""
        hw, hh = w / 2, h / 2
        self.rect(x, y, w, h, layer, 0.25)
        self.line(x - hw + w * 0.25, y - hh, x - hw + w * 0.25, y + hh, layer, 0.25)
        self.line(x - hw + w * 0.6, y - hh, x - hw + w * 0.6, y + hh, layer, 0.25)
        self.text(feature, x - hw + w * 0.125, y, 3, layer)
        self.text(tolerance, x - hw + w * 0.425, y, 3, layer)
        if datum:
            self.text(datum, x - hw + w * 0.8, y, 3, layer)

    def tolerance_leader(self, x1, y1, x2, y2, layer="TOLERANCE"):
        """形位公差指引线"""
        self.line(x1, y1, x2, y2, layer, 0.25)

    # ══════════════════════════════════════════════════════════════
    #  螺纹
    # ══════════════════════════════════════════════════════════════

    def thread_ext(self, x1, x2, y, major_r, minor_r, layer_major="OUTLINE", layer_minor="THREAD", chamfer=0):
        """外螺纹表示（水平放置）
        
        Args:
            x1, x2: 螺纹起止 X
            y: 轴线 Y
            major_r: 大径半径
            minor_r: 小径半径
            chamfer: 倒角长度
        """
        # 大径（粗实线）
        self.line(x1, y + major_r, x2, y + major_r, layer_major)
        self.line(x1, y - major_r, x2, y - major_r, layer_major)
        # 小径（细实线）
        if chamfer:
            self.line(x1 + chamfer, y + minor_r, x2, y + minor_r, layer_minor, 0.25)
            self.line(x1 + chamfer, y - minor_r, x2, y - minor_r, layer_minor, 0.25)
            # 倒角
            self.line(x2, y + major_r, x2 + chamfer, y + major_r - chamfer, layer_major)
            self.line(x2, y - major_r, x2 + chamfer, y - major_r + chamfer, layer_major)
            self.line(x2, y + minor_r, x2 + chamfer, y + major_r - chamfer, layer_minor, 0.25)
            self.line(x2, y - minor_r, x2 + chamfer, y - major_r + chamfer, layer_minor, 0.25)
        else:
            self.line(x1, y + minor_r, x2, y + minor_r, layer_minor, 0.25)
            self.line(x1, y - minor_r, x2, y - minor_r, layer_minor, 0.25)
        # 螺纹终止线
        self.line(x2, y - major_r, x2, y + major_r, layer_major)

    def thread_triangles(self, x_start, x_end, y, major_r, minor_r, pitch, layer="OUTLINE"):
        """螺纹牙三角形示意（放大图用）"""
        n = int((x_end - x_start) / pitch)
        for i in range(n):
            tx = x_start + i * pitch
            self.line(tx, y + minor_r, tx + pitch / 2, y + major_r, layer, 0.25)
            self.line(tx + pitch / 2, y + major_r, tx + pitch, y + minor_r, layer, 0.25)
            self.line(tx, y - minor_r, tx + pitch / 2, y - major_r, layer, 0.25)
            self.line(tx + pitch / 2, y - major_r, tx + pitch, y - minor_r, layer, 0.25)

    # ══════════════════════════════════════════════════════════════
    #  中心线
    # ══════════════════════════════════════════════════════════════


    def circle_array(self, cx, cy, w, h, cols, rows, r, margin_x=0, margin_y=0, layer="OUTLINE", lw=0.5):
        x1, y1 = cx - w/2, cy - h/2
        x2, y2 = cx + w/2, cy + h/2
        self.rect(cx, cy, w, h, layer, lw)
        if margin_x == 0: margin_x = w / (cols + 1)
        if margin_y == 0: margin_y = h / (rows + 1)
        sx = (w - 2*margin_x) / max(1, cols-1)
        sy = (h - 2*margin_y) / max(1, rows-1)
        for r_i in range(rows):
            for c_i in range(cols):
                rx = x1 + margin_x + c_i * sx
                ry = y2 - margin_y - r_i * sy
                self.circle(rx, ry, r, layer, lw)
        return cols * rows

    def rect_grid(self, cx, cy, w, h, cols, rows, layer="OUTLINE", lw=0.5):
        x1, y1 = cx - w/2, cy - h/2
        x2, y2 = cx + w/2, cy + h/2
        self.rect(cx, cy, w, h, layer, lw)
        for i in range(1, cols):
            xi = x1 + w * i / cols
            self.line(xi, y1, xi, y2, layer, lw)
        for i in range(1, rows):
            yi = y1 + h * i / rows
            self.line(x1, yi, x2, yi, layer, lw)

    def centerline(self, x1, x2, y, extend=15, layer="CENTERLINE"):
        """画水平中心线"""
        self.line(x1 - extend, y, x2 + extend, y, layer, 0.18)

    # ══════════════════════════════════════════════════════════════
    #  图框 & 输出
    # ══════════════════════════════════════════════════════════════

    FRAME_SIZES = {"A3": (420,297), "A2": (594,420), "A1": (841,594)}

    def add_frame(self, fields=None, frame_size="A3"):
        """添加图框+标题栏（支持 A3/A2/A1）"""
        fl = FrameLib(self.doc, self.msp)
        if fields is None:
            fields = {"client":"","project":self.title,"drawing":"",
                      "stamp":"","scale":"1:1","date":"2026.05","designer":"Python"}
        fw, fh = self.FRAME_SIZES.get(frame_size, (420, 297))
        m = 5
        fl.standard_a3_frame(fields, x0=-fw/2+m, y0=-fh/2+m, x1=fw/2-m, y1=fh/2-m)
        return fl

    def save(self, path=None):
        """保存 DXF"""
        if path is None:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "%s.dxf" % self.title.replace(" ", "_"))
        self.doc.saveas(path)
        self._last_dxf = path
        print("  Saved: %s" % path)
        print("  Entities: %d" % len(self.msp))
        return path

    def export_svg(self, path=None, scale=0.8, margin=60):
        """导出 SVG 预览"""
        dxf_path = self._last_dxf or self.save()
        if path is None:
            path = dxf_path.replace(".dxf", ".svg")
        r = DXFRenderer(dxf_path)
        r.to_svg(path, scale=scale, margin=margin)
        print("  SVG: %s" % path)
        return path

    def export_pdf(self, path=None, scale=0.7, margin=50):
        """导出 PDF"""
        dxf_path = self._last_dxf or self.save()
        if path is None:
            path = dxf_path.replace(".dxf", ".pdf")
        r = DXFRenderer(dxf_path)
        r.to_pdf(path, scale=scale, margin=margin)
        print("  PDF: %s" % path)
        return path


    def export_plt(self, path=None):
        """导出 PLT/HPGL 格式"""
        dxf_path = self._last_dxf or self.save()
        if path is None:
            path = dxf_path.replace(".dxf", ".plt")
        pw = {"OUTLINE":2,"HIDDEN":1,"CENTERLINE":1,"DIMENSION":1,"TEXT":1,"THREAD":1,"HATCH":1,"BORDER":2}
        with open(path, "w", encoding="ascii") as f:
            f.write("IN;\nSP1;\n")
            for e in self.msp:
                lyr = e.dxf.layer if hasattr(e.dxf,"layer") else "0"
                pwi = pw.get(lyr, 1)
                f.write("SP" + str(pwi) + ";\n")
                if e.dxftype() == "LINE":
                    f.write("PU" + str(int(e.dxf.start.x)) + "," + str(int(e.dxf.start.y)) + ";\n")
                    f.write("PD" + str(int(e.dxf.end.x)) + "," + str(int(e.dxf.end.y)) + ";\n")
                elif e.dxftype() == "LWPOLYLINE":
                    pts = list(e.get_points())
                    if pts:
                        f.write("PU" + str(int(pts[0][0])) + "," + str(int(pts[0][1])) + ";\n")
                        for p in pts[1:]:
                            f.write("PD" + str(int(p[0])) + "," + str(int(p[1])) + ";\n")
            f.write("SP0;\nIN;\n")
        print("  PLT:  " + path)
        return path