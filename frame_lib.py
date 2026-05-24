from ezdxf.enums import TextEntityAlignment

FRAME_SIZES = {
    "A3": (420, 297),
    "A2": (594, 420),
    "A1": (841, 594),
}

class FrameLib:
    """Professional title block and frame system

    Supports A3 / A2 / A1 with proportional title blocks.
    """

    def __init__(self, doc, msp=None):
        self.doc = doc
        self.msp = msp if msp else doc.modelspace()

    def draw_frame(self, x0, y0, x1, y1, layer="BORDER"):
        """Draw outer border"""
        self.msp.add_lwpolyline(
            [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)],
            dxfattribs={"layer": layer}
        )

    def draw_title_block(self, x, y, w, h, layer="BORDER"):
        """Draw title block outline at bottom-right"""
        y0, y1 = y, y + h
        self.msp.add_lwpolyline(
            [(x, y0), (x + w, y0), (x + w, y1), (x, y1), (x, y0)],
            dxfattribs={"layer": layer}
        )
        mid_y = y0 + h * 0.35
        self.msp.add_line((x, mid_y), (x + w, mid_y), dxfattribs={"layer": layer})
        col_w = w / 4
        for i in range(1, 4):
            vx = x + i * col_w
            self.msp.add_line((vx, mid_y), (vx, y1), dxfattribs={"layer": layer})
        return {"x": x, "y": y, "w": w, "h": h, "mid_y": mid_y, "col_w": col_w}

    def fill_title_block(self, tb, fields, layer_text="TITLE"):
        """Fill title block with data"""
        x, y0, w, h = tb["x"], tb["y"], tb["w"], tb["h"]
        mid_y, col_w = tb["mid_y"], tb["col_w"]

        labels = ["建设单位", "工程名称", "图名", "图号"]
        for i, lbl in enumerate(labels):
            lx = x + i * col_w + col_w / 2
            self._text(lbl, lx, y0 + h * 0.17, 2.5, layer_text)

        if "client" in fields:
            self._text(fields["client"], x + col_w / 2, y0 + h * 0.68, 3.0, layer_text)
        if "project" in fields:
            self._text(fields["project"], x + col_w + col_w / 2, y0 + h * 0.68, 3.0, layer_text)
        if "drawing" in fields:
            self._text(fields["drawing"], x + 2 * col_w + col_w / 2, y0 + h * 0.68, 3.0, layer_text)
        if "stamp" in fields:
            self._text(fields["stamp"], x + 3 * col_w + col_w / 2, y0 + h * 0.68, 3.0, layer_text)

        bottom_info = []
        if "scale" in fields:
            bottom_info.append(("比例", fields["scale"]))
        if "date" in fields:
            bottom_info.append(("日期", fields["date"]))
        if "designer" in fields:
            bottom_info.append(("设计", fields["designer"]))
        if "checker" in fields:
            bottom_info.append(("审核", fields["checker"]))

        info_y = y0 - 4
        info_x = x + w - 20
        for lbl, val in reversed(bottom_info):
            self._text("%s: %s" % (lbl, val), info_x, info_y, 2.5, layer_text)
            info_y -= 4

    def _text(self, text, x, y, h, layer):
        te = self.msp.add_text(str(text), height=h, dxfattribs={"layer": layer})
        te.set_placement((x, y), align=TextEntityAlignment.MIDDLE_CENTER)

    def calc_title_block_size(self, frame_w, frame_h):
        """Calculate title block size proportional to frame"""
        # A3 baseline: frame ~400x280, title block 135x45
        ratio_w = frame_w / 400.0
        ratio_h = frame_h / 280.0
        ratio = min(ratio_w, ratio_h)
        return max(90, min(200, 135 * ratio)), max(30, min(60, 45 * ratio))

    def standard_a3_frame(self, fields, x0=-345, y0=-265, x1=345, y1=265):
        """Quick setup: draw frame + title block + fill"""
        self.draw_frame(x0, y0, x1, y1)
        fw = x1 - x0
        fh = y1 - y0
        tb_w, tb_h = self.calc_title_block_size(fw, fh)
        tb = self.draw_title_block(x1 - tb_w - 5, y0 + 5, tb_w, tb_h)
        self.fill_title_block(tb, fields)
        return tb
