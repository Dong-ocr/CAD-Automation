from ezdxf.addons.dimlines import LinearDimension
from ezdxf.addons import dimstyles
from ezdxf.enums import TextEntityAlignment
import math

class DimLib:
    """Dimension and annotation system"""

    def __init__(self, doc, msp=None):
        self.doc = doc
        self.msp = msp if msp else doc.modelspace()
        self._setup_style()

    def _setup_style(self):
        dimstyles.setup(self.doc)
        style = self.doc.dimstyles.get("Standard")
        style.dxf.dimtxt = 2.5
        style.dxf.dimtsz = 1.0
        style.dxf.dimtad = 1
        style.dxf.dimasz = 1.5

    def linear(self, p1, p2, offset, angle=0, layer="DIMENSION", roundval=None):
        """Add horizontal/vertical linear dimension

        Args:
            p1, p2: measurement points (x,y)
            offset: distance from the measured line
            angle: 0 = horizontal dim, 90 = vertical dim
            layer: target layer
            roundval: rounding precision (e.g. 0 for integer)
        """
        pos = (p1[0], p1[1] + offset) if angle == 0 else (p1[0] + offset, p1[1])
        dim = LinearDimension(
            pos=pos,
            measure_points=[p1, p2],
            angle=angle,
            dimstyle="Standard",
            layer=layer,
            roundval=roundval,
        )
        dim.render(self.msp)
        return dim

    def horizontal(self, x1, x2, y, offset=8, layer="DIMENSION", roundval=None):
        """Horizontal dimension between two x positions at height y"""
        return self.linear((x1, y), (x2, y), offset, angle=0, layer=layer, roundval=roundval)

    def vertical(self, x, y1, y2, offset=8, layer="DIMENSION", roundval=None):
        """Vertical dimension between two y positions at x position"""
        return self.linear((x, y1), (x, y2), offset, angle=90, layer=layer, roundval=roundval)

    def axis_label(self, x, y, label, size=3, layer="TEXT"):
        """Add axis label with circle"""
        te = self.msp.add_text(str(label), height=size, dxfattribs={"layer": layer})
        te.set_placement((x, y), align=TextEntityAlignment.MIDDLE_CENTER)
        self.msp.add_circle((x, y), size * 0.6, dxfattribs={"layer": layer})

    def axis_line(self, x, y_start, y_end, layer="DIMENSION"):
        """Vertical axis extension line"""
        self.msp.add_line((x, y_start), (x, y_end), dxfattribs={"layer": layer})

    def axis_grid(self, xs, ys, labels_x=None, labels_y=None, size=3, layer_axis="AXIS", layer_dim="DIMENSION"):
        """Full axis grid with labels"""
        count = 0
        if labels_x:
            for i, x in enumerate(xs):
                lbl = labels_x[i] if i < len(labels_x) else str(i+1)
                self.axis_line(x, min(ys), max(ys), layer_axis)
                self.axis_label(x, min(ys) - size*1.5, lbl, size, layer_dim)
                count += 1
        if labels_y:
            for i, y in enumerate(ys):
                lbl = labels_y[i] if i < len(labels_y) else str(i+1)
                self.axis_line(min(xs), y, max(xs), layer_axis)
                self.axis_label(min(xs) - size*1.5, y, lbl, size, layer_dim)
                count += 1
        return count
