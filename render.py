# ======================================================================
#  render.py — DXF → SVG/PDF/PNG 渲染引擎
#  用于专业展示和交付给客户
# ======================================================================

import ezdxf, math, os
from ezdxf import colors

# ── Renderer ──────────────────────────────────────────────────────────
class DXFRenderer:
    """DXF multipage renderer to SVG/PDF/PNG"""

    ACI_COLORS = {
        1: "#ff4444", 2: "#ffdd44", 3: "#44dd44", 4: "#44dddd",
        5: "#4444ff", 6: "#ff44ff", 7: "#ffffff", 8: "#888888",
        9: "#cccccc", 30: "#ff9944",
    }

    def __init__(self, dxf_path):
        self.doc = ezdxf.readfile(dxf_path)
        self.msp = self.doc.modelspace()

    def get_color(self, entity, default="#ffffff"):
        c = entity.dxf.color if hasattr(entity.dxf, "color") else None
        if not c or c == 256:
            lyr = entity.dxf.layer
            if lyr in self.doc.layers:
                c = self.doc.layers.get(lyr).dxf.color or 7
            else:
                c = 7
        return self.ACI_COLORS.get(c, default)

    def get_bounds(self):
        xs, ys = [], []
        for e in self.msp.query("LINE LWPOLYLINE CIRCLE TEXT INSERT HATCH"):
            if e.dxftype() == "LINE":
                xs += [e.dxf.start.x, e.dxf.end.x]; ys += [e.dxf.start.y, e.dxf.end.y]
            elif e.dxftype() == "LWPOLYLINE":
                for p in e.get_points(): xs.append(p[0]); ys.append(p[1])
            elif e.dxftype() == "CIRCLE":
                xs += [e.dxf.center.x - e.dxf.radius, e.dxf.center.x + e.dxf.radius]
                ys += [e.dxf.center.y - e.dxf.radius, e.dxf.center.y + e.dxf.radius]
            elif e.dxftype() in ("TEXT",):
                xs.append(e.dxf.insert.x); ys.append(e.dxf.insert.y)
            elif e.dxftype() == "INSERT":
                xs.append(e.dxf.insert.x); ys.append(e.dxf.insert.y)
        if not xs:
            return -350, 350, -300, 300
        return min(xs), max(xs), min(ys), max(ys)

    def to_svg(self, svg_path, scale=0.8, margin=80):
        """Render DXF to SVG with full hatch support"""
        import svgwrite
        x_min, x_max, y_min, y_max = self.get_bounds()
        w, h = x_max - x_min, y_max - y_min
        if w < 1: w, h = 700, 550
        cw = int(w * scale + 2 * margin)
        ch = int(h * scale + 2 * margin)
        dwg = svgwrite.Drawing(svg_path, size=(cw, ch))
        dwg.add(dwg.rect(insert=(0, 0), size=(cw, ch), fill="#1a1a2e"))

        def d2s(x, y):
            return (x - x_min) * scale + margin, (y_max - y) * scale + margin
        def dl(l):
            return l * scale

        # Collect hatch areas first (draw behind lines)
        hatch_polygons = []
        for e in self.msp:
            if e.dxftype() != "HATCH":
                continue
            col = self.get_color(e)
            try:
                for path in e.paths.paths:
                    pts = [(v[0], v[1]) for v in path.vertices]
                    if len(pts) >= 3:
                        sp = [d2s(p[0], p[1]) for p in pts]
                        hatch_polygons.append((sp, col))
            except:
                pass

        # Draw hatch fills
        for sp, col in hatch_polygons:
            dwg.add(dwg.polygon(sp, fill=col, fill_opacity="0.35", stroke="none"))

        # Draw entities
        for e in self.msp:
            col = self.get_color(e)
            if e.dxftype() == "LINE":
                x1, y1 = d2s(e.dxf.start.x, e.dxf.start.y)
                x2, y2 = d2s(e.dxf.end.x, e.dxf.end.y)
                dwg.add(dwg.line((x1, y1), (x2, y2), stroke=col, stroke_width=1))
            elif e.dxftype() == "LWPOLYLINE":
                pts = [(p[0], p[1]) for p in e.get_points()]
                if len(pts) >= 2:
                    sp = [d2s(p[0], p[1]) for p in pts]
                    dwg.add(dwg.polyline(sp, fill="none", stroke=col, stroke_width=1))
            elif e.dxftype() == "CIRCLE":
                cx, cy = d2s(e.dxf.center.x, e.dxf.center.y)
                r = dl(e.dxf.radius)
                if r > 0.5:
                    dwg.add(dwg.circle(center=(cx, cy), r=r, fill="none", stroke=col, stroke_width=1))
            elif e.dxftype() == "TEXT":
                x, y = d2s(e.dxf.insert.x, e.dxf.insert.y)
                h = dl(e.dxf.height)
                fs = max(8, min(h * 0.7, 24))
                dwg.add(dwg.text(e.dxf.text, insert=(x, y), fill=col,
                                font_size=fs, font_family="Noto Sans SC",
                                text_anchor="middle"))
            elif e.dxftype() == "INSERT":
                self._render_block(e, dwg, d2s, dl, col)

        dwg.save()
        return svg_path

    def _render_block(self, ref, dwg, d2s, dl, parent_color):
        """Render block reference entities"""
        try:
            block = self.doc.blocks.get(ref.dxf.name)
        except:
            return
        sx, sy = ref.dxf.xscale or 1.0, ref.dxf.yscale or 1.0
        rot = math.radians(ref.dxf.rotation or 0.0)
        ix, iy = ref.dxf.insert.x, ref.dxf.insert.y
        c, s = math.cos(rot), math.sin(rot)

        def tr(x, y):
            return (x * sx * c - y * sy * s + ix, x * sx * s + y * sy * c + iy)

        for be in block:
            bc = self.get_color(be, parent_color)
            if be.dxftype() == "LINE":
                p1 = tr(be.dxf.start.x, be.dxf.start.y)
                p2 = tr(be.dxf.end.x, be.dxf.end.y)
                dwg.add(dwg.line(d2s(*p1), d2s(*p2), stroke=bc, stroke_width=1))
            elif be.dxftype() == "LWPOLYLINE":
                pts = [tr(p[0], p[1]) for p in be.get_points()]
                if len(pts) >= 2:
                    sp = [d2s(p[0], p[1]) for p in pts]
                    dwg.add(dwg.polyline(sp, fill="none", stroke=bc, stroke_width=1))
            elif be.dxftype() == "CIRCLE":
                ct = tr(be.dxf.center.x, be.dxf.center.y)
                r = dl(be.dxf.radius * sx)
                if r > 0.5:
                    dwg.add(dwg.circle(center=d2s(*ct), r=r, fill="none", stroke=bc, stroke_width=1))

    def to_pdf(self, pdf_path, scale=0.7, margin=60):
        """Render DXF to PDF via matplotlib"""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon, Circle, FancyBboxPatch
        from matplotlib.lines import Line2D
        import matplotlib.patches as mpatches

        x_min, x_max, y_min, y_max = self.get_bounds()
        w, h = x_max - x_min, y_max - y_min

        fig, ax = plt.subplots(1, 1, figsize=(11.7, 8.3))  # A4
        ax.set_facecolor("#1a1a2e")
        fig.patch.set_facecolor("#1a1a2e")
        ax.set_xlim(x_min - 20, x_max + 20)
        ax.set_ylim(y_min - 20, y_max + 20)
        ax.set_aspect("equal")
        ax.axis("off")

        acic = {
            1: "#ff4444", 2: "#ffdd44", 3: "#44dd44", 4: "#44dddd",
            5: "#4444ff", 6: "#ff44ff", 7: "white", 8: "#888888",
            30: "#ff9944",
        }

        def gc(e, d="white"):
            c = e.dxf.color if hasattr(e.dxf, "color") else None
            if not c or c == 256:
                lyr = e.dxf.layer
                if lyr in self.doc.layers:
                    c = self.doc.layers.get(lyr).dxf.color or 7
                else:
                    c = 7
            return acic.get(c, d)

        # Draw hatches first
        for e in self.msp:
            if e.dxftype() != "HATCH":
                continue
            col = gc(e)
            try:
                for path in e.paths.paths:
                    pts = [(v[0], v[1]) for v in path.vertices]
                    if len(pts) >= 3:
                        ax.add_patch(Polygon(pts, facecolor=col, alpha=0.3, edgecolor="none"))
            except:
                pass

        # Draw block fills (for rotated buildings)
        for e in self.msp:
            if e.dxftype() != "INSERT":
                continue
            col = gc(e)
            try:
                block = self.doc.blocks.get(e.dxf.name)
            except:
                continue
            # Only fill if the block has LWPOLYLINE (rect outlines)
            if not any(be.dxftype() == "LWPOLYLINE" for be in block):
                continue
            sx = e.dxf.xscale or 1.0
            sy = e.dxf.yscale or 1.0
            rot = e.dxf.rotation or 0.0
            ix, iy = e.dxf.insert.x, e.dxf.insert.y
            rad = math.radians(rot)
            hw, hh = sx / 2 - 0.3, sy / 2 - 0.3
            c, s = math.cos(rad), math.sin(rad)
            corners = [
                (ix + hw * c - hh * s, iy + hw * s + hh * c),
                (ix - hw * c - hh * s, iy - hw * s + hh * c),
                (ix - hw * c + hh * s, iy - hw * s - hh * c),
                (ix + hw * c + hh * s, iy + hw * s - hh * c),
            ]
            ax.add_patch(Polygon(corners, facecolor=col, alpha=0.25, edgecolor="none"))

        # Draw entities
        for e in self.msp:
            if e.dxftype() == "HATCH":
                continue
            col = gc(e)
            if e.dxftype() == "LINE":
                ax.add_line(Line2D([e.dxf.start.x, e.dxf.end.x],
                                  [e.dxf.start.y, e.dxf.end.y],
                                  color=col, linewidth=0.5))
            elif e.dxftype() == "LWPOLYLINE":
                pts = [(p[0], p[1]) for p in e.get_points()]
                if len(pts) >= 2:
                    xs = [p[0] for p in pts]
                    ys = [p[1] for p in pts]
                    ax.add_line(Line2D(xs, ys, color=col, linewidth=0.5))
            elif e.dxftype() == "CIRCLE":
                ax.add_patch(Circle((e.dxf.center.x, e.dxf.center.y),
                                   e.dxf.radius, fill=False, color=col, linewidth=0.5))
            elif e.dxftype() == "TEXT":
                ax.text(e.dxf.insert.x, e.dxf.insert.y, e.dxf.text,
                       color=col, fontsize=e.dxf.height * 0.4,
                       ha="center", va="center",
                       fontfamily="Noto Sans SC")
            elif e.dxftype() == "INSERT":
                try:
                    block = self.doc.blocks.get(e.dxf.name)
                except:
                    continue
                sx = e.dxf.xscale or 1.0
                sy = e.dxf.yscale or 1.0
                rot = math.radians(e.dxf.rotation or 0.0)
                ix, iy = e.dxf.insert.x, e.dxf.insert.y
                c, s = math.cos(rot), math.sin(rot)
                for be in block:
                    if be.dxftype() in ("ATTDEF", "ATTRIB"):
                        continue
                    bc = gc(be)
                    if be.dxftype() == "LINE":
                        p1 = (be.dxf.start.x * sx * c - be.dxf.start.y * sy * s + ix,
                              be.dxf.start.x * sx * s + be.dxf.start.y * sy * c + iy)
                        p2 = (be.dxf.end.x * sx * c - be.dxf.end.y * sy * s + ix,
                              be.dxf.end.x * sx * s + be.dxf.end.y * sy * c + iy)
                        ax.add_line(Line2D([p1[0], p2[0]], [p1[1], p2[1]],
                                          color=bc, linewidth=0.5))
                    elif be.dxftype() == "LWPOLYLINE":
                        pts = [(p[0], p[1]) for p in be.get_points()]
                        if len(pts) >= 2:
                            tpts = [(p[0] * sx * c - p[1] * sy * s + ix,
                                     p[0] * sx * s + p[1] * sy * c + iy) for p in pts]
                            ax.add_line(Line2D([p[0] for p in tpts], [p[1] for p in tpts],
                                              color=bc, linewidth=0.5))
                    elif be.dxftype() == "CIRCLE":
                        ctr = be.dxf.center
                        ct = (ctr.x * sx * c - ctr.y * sy * s + ix,
                              ctr.x * sx * s + ctr.y * sy * c + iy)
                        r = be.dxf.radius * sx
                        ax.add_patch(Circle(ct, r, fill=False, color=bc, linewidth=0.5))

        plt.tight_layout(pad=0)
        fig.savefig(pdf_path, dpi=200, facecolor="#1a1a2e", edgecolor="none")
        plt.close(fig)
        return pdf_path
