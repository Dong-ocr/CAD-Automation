import ezdxf, math

class HatchFiller:
    """Fill manager for adding solid/pattern hatches"""

    def __init__(self, doc, msp=None):
        self.doc = doc
        self.msp = msp if msp else doc.modelspace()
        self._hatches = []

    def fill_rect(self, cx, cy, w, h, color=7, layer="0"):
        x1, y1 = cx - w/2, cy - h/2
        x2, y2 = cx + w/2, cy + h/2
        return self._solid([(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)], color, layer)

    def fill_circle(self, cx, cy, r, color=7, layer="0"):
        h = self.msp.add_hatch(color=color, dxfattribs={"layer": layer})
        h.set_solid_fill()
        h.paths.add_edge_path().add_arc((cx, cy), r, 0, 360)
        self._hatches.append(h); return h

    def fill_polygon(self, points, color=7, layer="0"):
        pts = list(points)
        if len(pts) < 3: return None
        if pts[0] != pts[-1]: pts.append(pts[0])
        return self._solid(pts, color, layer)

    def pattern_rect(self, cx, cy, w, h, pattern="ANGLE", scale=2, angle=0, color=7, layer="0"):
        x1, y1 = cx - w/2, cy - h/2
        x2, y2 = cx + w/2, cy + h/2
        h = self.msp.add_hatch(color=color, dxfattribs={"layer": layer})
        h.set_pattern_fill(pattern, angle=angle, scale=scale)
        h.paths.add_polyline_path([(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)])
        self._hatches.append(h); return h

    def _solid(self, points, color, layer):
        h = self.msp.add_hatch(color=color, dxfattribs={"layer": layer})
        h.set_solid_fill()
        h.paths.add_polyline_path(points)
        self._hatches.append(h); return h

    def fill_all_of_type(self, msp, block_name, color=2, layer=None, inset=0.3):
        """Add solid fills behind all INSERT refs of a given block name"""
        if layer is None: layer = block_name
        refs = [e for e in msp if e.dxftype() == "INSERT" and e.dxf.name == block_name]
        count = 0
        for ref in refs:
            sx, sy = ref.dxf.xscale or 1.0, ref.dxf.yscale or 1.0
            x, y = ref.dxf.insert.x, ref.dxf.insert.y
            rot = ref.dxf.rotation or 0.0
            w, h = sx - 2*inset, sy - 2*inset
            if w < 0.1 or h < 0.1: continue
            if abs(rot) < 0.01:
                self.fill_rect(x, y, w, h, color=color, layer=layer)
            else:
                rad = math.radians(rot); c = math.cos(rad); s = math.sin(rad)
                hw, hh = w/2, h/2
                corners = [(x+hw*c-hh*s, y+hw*s+hh*c),
                           (x-hw*c-hh*s, y-hw*s+hh*c),
                           (x-hw*c+hh*s, y-hw*s-hh*c),
                           (x+hw*c+hh*s, y+hw*s-hh*c)]
                self.fill_polygon(corners, color=color, layer=layer)
            count += 1
        return count

    @property
    def count(self): return len(self._hatches)

if __name__ == "__main__":
    import ezdxf
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    hf = HatchFiller(doc, msp)
    hf.fill_rect(0, 0, 40, 20, color=2, layer="BUILDING")
    hf.fill_circle(0, -30, 15, color=4, layer="WATER")
    hf.pattern_rect(-30, 10, 20, 15, pattern="GRAVEL", scale=3, color=8, layer="GREEN")
    print("OK -", hf.count, "hatches")
    doc.saveas("C:/Users/王东浩/Documents/CAD自动化制图/test.dxf")
