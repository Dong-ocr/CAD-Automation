# ======================================================================
#  dxf_excel.py — Excel 数据驱动 DXF 生成器 v2（增强版）
#
#  功能：
#    - 读 Excel 批量插块
#    - Hatch 旋转正确
#    - 错误友好提示
#    - PDF / SVG 导出
#    - 图框尺寸可选 (A3/A2/A1)
#    - 命令行参数
# ======================================================================

import ezdxf, openpyxl, os, sys, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from library import BlockLibrary
from hatch_lib import HatchFiller
from dim_lib import DimLib
from frame_lib import FrameLib

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Defaults ──────────────────────────────────────────────────────────
DEFAULT_EXCEL = os.path.join(BASE, "图块数据模板.xlsx")
DEFAULT_SHEET = "图块数据"
DEFAULT_DXF = os.path.join(BASE, "bjwlxy_campus.dxf")
DEFAULT_PDF = os.path.join(BASE, "output.pdf")
DEFAULT_SVG = os.path.join(BASE, "preview.svg")
FRAME_SIZES = {
    "A3": (420, 297),
    "A2": (594, 420),
    "A1": (841, 594),
}

# ── Parsers ───────────────────────────────────────────────────────────
def parse_attrs(s):
    if not s or not str(s).strip():
        return None
    d = {}
    for p in str(s).split(";"):
        if "=" in p:
            k, v = p.split("=", 1)
            d[k.strip()] = v.strip()
    return d if d else None

def parse_scale(v):
    if v is None:
        return 1.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if "," in s:
        parts = s.split(",")
        return (float(parts[0]), float(parts[1]))
    try:
        return float(s)
    except:
        return 1.0

# ── Main Generator ───────────────────────────────────────────────────
def excel_to_dxf(excel_path=None, sheet_name=None, output_dxf=None,
                 output_pdf=None, output_svg=None, frame_size="A3",
                 auto_hatch=True, auto_dim=True, auto_frame=True):
    """Read Excel and generate professional DXF with hatches + dims + frame"""

    excel_path = excel_path or DEFAULT_EXCEL
    sheet_name = sheet_name or DEFAULT_SHEET
    output_dxf = output_dxf or DEFAULT_DXF
    output_pdf = output_pdf
    output_svg = output_svg or DEFAULT_SVG

    header = "=" * 55
    print(header)
    print("  dxf_excel.py v2 - Excel Data-Driven DXF Generator")
    print(header)
    print()

    # ── Validate Excel ──────────────────────────────────────────────
    if not os.path.exists(excel_path):
        print("  [!] ERROR: Excel file not found:")
        print("      " + excel_path)
        print("  [!] Hint: Run this from the project directory,")
        print("      or specify --excel <path>")
        return False

    try:
        wb = openpyxl.load_workbook(excel_path, data_only=True)
    except Exception as e:
        print("  [!] ERROR: Cannot open Excel file:")
        print("      " + str(e))
        return False

    if sheet_name not in wb.sheetnames:
        print("  [!] ERROR: Sheet '%s' not found." % sheet_name)
        print("      Available sheets:", wb.sheetnames)
        return False

    # ── Parse rows ──────────────────────────────────────────────────
    ws = wb[sheet_name]
    rows = []
    errors = []
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
        vals = list(row) + [None] * 8
        name, x, y, scale, rotation, layer, attrs, note = vals[:8]
        if name is None or str(name).strip() == "":
            continue
        name = str(name).strip()
        if not name.isascii():
            errors.append("  Row %d: Block name '%s' contains non-ASCII chars" % (i, name))
            continue
        try:
            x = float(x) if x is not None else 0
            y = float(y) if y is not None else 0
        except:
            errors.append("  Row %d: Invalid coordinates (x=%s, y=%s)" % (i, x, y))
            continue
        rows.append({
            "name": name, "x": x, "y": y,
            "scale": parse_scale(scale),
            "rotation": float(rotation) if rotation else 0,
            "layer": str(layer).strip() if layer else None,
            "attrs": parse_attrs(attrs),
            "row": i,
        })

    if not rows:
        print("  [!] ERROR: No valid data rows found in Excel.")
        print("      Check that column headers match: 块名称, X坐标, Y坐标, ...")
        return False

    print("  Excel: %s" % excel_path)
    print("  Rows:  %d valid, %d errors" % (len(rows), len(errors)))
    if errors:
        print("  Errors:")
        for e in errors:
            print("    " + e)
    print()

    # ── Create DXF ──────────────────────────────────────────────────
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    lib = BlockLibrary(doc)
    hf = HatchFiller(doc, msp) if auto_hatch else None
    dl = DimLib(doc, msp) if auto_dim else None
    fl = FrameLib(doc, msp) if auto_frame else None

    # ── Create layers ──────────────────────────────────────────────
    for lyr in ["GROUND","ROAD","BUILDING","DORMITORY","SPORT_FIELD",
                "GREEN","WATER","PLAZA","TEXT","TITLE","BORDER",
                "LEGEND","AXIS","DIMENSION","FILL"]:
        if lyr not in doc.layers:
            doc.layers.new(lyr, dxfattribs={"color": 7, "linetype": "CONTINUOUS"})

    # ── Insert blocks ──────────────────────────────────────────────
    ok, fail = 0, 0
    for row in rows:
        try:
            lib.insert(row["name"], row["x"], row["y"],
                       scale=row["scale"], rotation=row["rotation"],
                       attrs=row["attrs"], layer=row["layer"])
            ok += 1
        except ValueError as e:
            print("  [!] Row %d: Unknown block '%s' - skipping" % (row["row"], row["name"]))
            fail += 1
        except Exception as e:
            print("  [!] Row %d: %s" % (row["row"], e))
            fail += 1

    print("  Blocks: %d inserted, %d skipped" % (ok, fail))
    if ok == 0:
        print("  [!] No blocks inserted - check your block names")
        return False

    # ── HATCH with rotation fix ────────────────────────────────────
    if auto_hatch and hf:
        n = hf.fill_all_of_type(msp, "BUILDING", color=2, layer="FILL")
        n += hf.fill_all_of_type(msp, "DORMITORY", color=30, layer="FILL")
        print("  Hatches: %d" % hf.count)

    # ── DIMENSIONS ──────────────────────────────────────────────────
    if auto_dim and dl:
        fr_w, fr_h = FRAME_SIZES.get(frame_size, FRAME_SIZES["A3"])
        half_w, half_h = fr_w / 4, fr_h / 3
        dl.horizontal(-half_w, half_w, -half_h, offset=15, layer="DIMENSION")
        dl.vertical(-half_w * 1.1, -half_h, half_h, offset=15, layer="DIMENSION")
        dl.axis_grid(
            xs=[i * 100 for i in range(-3, 4)],
            ys=[i * 100 for i in range(-2, 3)],
            labels_x=[str(i + 1) for i in range(7)],
            labels_y=["A", "B", "C", "D", "E"],
            size=3, layer_axis="AXIS", layer_dim="DIMENSION",
        )

    # ── FRAME ───────────────────────────────────────────────────────
    if auto_frame and fl:
        fw, fh = FRAME_SIZES.get(frame_size, FRAME_SIZES["A3"])
        margin = 5
        fl.standard_a3_frame({
            "client": "Client Name",
            "project": "Project Name",
            "drawing": "Drawing Name",
            "stamp": "T-001",
            "scale": "1:2000",
            "date": "2026.05",
            "designer": "DXF Generator",
        }, x0=-fw / 2, y0=-fh / 2, x1=fw / 2, y1=fh / 2)

    # ── Save ────────────────────────────────────────────────────────
    doc.saveas(output_dxf)
    print("  DXF:   %s" % output_dxf)

    if output_svg:
        try:
            from render import DXFRenderer
            r = DXFRenderer(output_dxf)
            r.to_svg(output_svg, scale=0.8, margin=60)
            print("  SVG:   %s" % output_svg)
        except Exception as e:
            print("  SVG:   Failed - %s" % e)

    if output_pdf:
        try:
            from render import DXFRenderer
            r = DXFRenderer(output_dxf)
            r.to_pdf(output_pdf, scale=0.7, margin=40)
            print("  PDF:   %s" % output_pdf)
        except Exception as e:
            print("  PDF:   Failed - %s" % e)

    print()
    print("  Done! %d blocks, %d total" % (lib.count_refs(), len(msp)))
    print(header)
    return True


# ── CLI Entry Point ──────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Excel to DXF Generator v2")
    p.add_argument("--excel", help="Path to Excel file")
    p.add_argument("--sheet", default="图块数据", help="Sheet name")
    p.add_argument("--dxf", help="Output DXF path")
    p.add_argument("--pdf", help="Output PDF path (optional)")
    p.add_argument("--no-svg", action="store_true", help="Skip SVG generation")
    p.add_argument("--frame", choices=["A3","A2","A1"], default="A3", help="Frame size")
    p.add_argument("--no-hatch", action="store_true", help="Skip hatch fill")
    p.add_argument("--no-dim", action="store_true", help="Skip dimensions")
    p.add_argument("--no-frame", action="store_true", help="Skip title block")
    args = p.parse_args()

    ok = excel_to_dxf(
        excel_path=args.excel,
        sheet_name=args.sheet,
        output_dxf=args.dxf,
        output_pdf=args.pdf,
        output_svg=None if args.no_svg else DEFAULT_SVG,
        frame_size=args.frame,
        auto_hatch=not args.no_hatch,
        auto_dim=not args.no_dim,
        auto_frame=not args.no_frame,
    )
    sys.exit(0 if ok else 1)
