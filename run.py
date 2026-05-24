# ======================================================================
#  run.py — 统一命令行入口 v2
#
#  用法：
#    python run.py campus          # 生成校园总平面
#    python run.py shaft           # 生成阶梯轴零件图
#    python run.py geometry        # 生成几何图形作业
#    python run.py excel           # 从 Excel 生成
#    python run.py batch --csv parts.csv  # 批量生成阶梯轴
#    python run.py list            # 列出可用模板
# ======================================================================

import os, sys, csv, argparse

BASE = os.path.dirname(os.path.abspath(__file__))

def ensure_import(name):
    """Dynamic import helper for scripts in the same directory"""
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, os.path.join(BASE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def cmd_campus(args):
    """生成校园总平面图"""
    print("Running: campus map...")
    exec(open(os.path.join(BASE, "campus_pro.py")).read())

def cmd_shaft(args):
    """生成阶梯轴零件图"""
    print("Running: stepped shaft drawing...")
    # Import and run the shaft generator
    shaft_mod = ensure_import("exam_task5_v3")
    # The module runs on import; that's fine for now

def gen_shaft_dxf(part, output_dir):
    """Generate a shaft DXF from a part dict

    Args:
        part: dict with keys d1,l1,d2,l2,d3,l3,d4,l4,key_w,key_d,thread
        output_dir: output directory
    Returns:
        path to generated DXF file
    """
    from cad_toolbox import CADProject
    import math

    name = part.get("name", "shaft")
    segs_data = [
        (part.get("d1", 25), part.get("l1", 30)),
        (part.get("d2", 30), part.get("l2", 30)),
        (part.get("d3", 20), part.get("l3", 20)),
        (part.get("d4", 28), part.get("l4", 20)),
    ]
    key_w = int(part.get("key_w", 8))
    key_d = float(part.get("key_d", 3.5))
    thread_label = part.get("thread", "M20")

    # Parse thread info
    import re
    tm = re.match(r"M(\d+)", thread_label)
    thread_d = int(tm.group(1)) if tm else 20

    p = CADProject(name)
    p.setup_layers()

    # Build segments
    x, SEGS = 0, []
    for di, li in segs_data:
        d, ln = int(di), int(li)
        nt = ""
        if abs(d - thread_d) < 2: nt = "M"
        if nt == "" and key_w > 0:
            nt = "K"
        SEGS.append({"d": d, "ln": ln, "r": d/2.0, "x1": x, "x2": x+ln, "nt": nt})
        x += ln

    OX, AY = 50, 150
    p.centerline(OX, OX+x, AY)

    for s in SEGS:
        r, x1, x2 = s["r"], OX+s["x1"], OX+s["x2"]
        if s["nt"] == "M":
            p.thread_ext(x1, x2, AY, r, r-1.5, "OUTLINE", "THREAD", 2)
        else:
            p.line(x1, AY+r, x2, AY+r, "OUTLINE")
            p.line(x1, AY-r, x2, AY-r, "OUTLINE")
        if s["x1"] > 0:
            pr = [p2 for p2 in SEGS if abs(p2["x2"]-s["x1"]) < 0.1]
            if pr and abs(pr[0]["r"]-r) > 0.01:
                prr = pr[0]["r"]
                p.line(x1, AY+min(prr,r), x1, AY+max(prr,r))
                p.line(x1, AY-min(prr,r), x1, AY-max(prr,r))

    # End faces
    p.line(OX, AY, OX, AY+SEGS[0]["r"], "OUTLINE")
    p.line(OX+x, AY, OX+x, AY+SEGS[-1]["r"], "OUTLINE")
    p.line(OX, AY, OX, AY-SEGS[0]["r"], "OUTLINE")
    p.line(OX+x, AY, OX+x, AY-SEGS[-1]["r"], "OUTLINE")

    # Keyway
    ks = [s for s in SEGS if s["nt"] == "K"]
    if ks:
        s = ks[0]
        kx1 = OX+s["x1"]+(s["ln"]-key_w)/2
        kx2 = kx1+key_w
        ky = AY+s["r"]-key_d
        p.line(kx1, ky, kx2, ky, "HIDDEN")
        p.line(kx1, ky, kx1, AY+s["r"], "HIDDEN")
        p.line(kx2, ky, kx2, AY+s["r"], "HIDDEN")

    # Section hatch
    boundary = []
    for s in SEGS:
        if s["nt"] == "M": continue
        x1, x2 = OX+s["x1"], OX+s["x2"]
        boundary.append((x1, AY+s["r"]-0.5))
        if s["nt"] == "K":
            kx1 = x1+(s["ln"]-key_w)/2
            kx2 = kx1+key_w
            ky = AY+s["r"]-key_d+0.5
            boundary += [(kx1, AY+s["r"]-0.5), (kx1, ky), (kx2, ky), (kx2, AY+s["r"]-0.5)]
        boundary.append((x2, AY+s["r"]-0.5))
    xs2 = [pt[0] for pt in boundary]
    boundary += [(max(xs2), AY), (min(xs2), AY)]
    p.hatch_section(boundary)

    # Dimensions
    for s in SEGS:
        xm = OX+(s["x1"]+s["x2"])/2
        label = thread_label if s["nt"]=="M" else ("phi%d" % s["d"])
        p.text(label, xm, AY+s["r"]+10, 2.5, "DIMENSION")
        p.roughness(xm, AY+s["r"]+14, 1.6 if s["nt"]=="K" else 3.2)
    p.dim_h(OX, OX+x, AY-SEGS[-1]["r"]-8, text="L=%d" % x)

    if ks:
        s = ks[0]
        xm = OX+(s["x1"]+s["x2"])/2
        p.text("键槽 %dx%s" % (key_w, key_d), xm, AY-s["r"]-18, 2.5, "DIMENSION")
        p.dim_h(xm-key_w/2, xm+key_w/2, AY-s["r"]-8, text=str(key_w))

    # Tech notes
    notes = ["技术要求", "", "1. 材料：45号钢", "", "2. 调质处理 HB 220-250",
             "", "3. 未注倒角 C1", "", "4. 去毛刺、锐角倒钝"]
    y = -50
    for n in notes:
        if n: p.text(n, 60, y, 5 if n=="技术要求" else 2.5, "TITLE" if n=="技术要求" else "TEXT")
        y -= 5

    p.add_frame({"client":"批量生成","project":name,"drawing":"阶梯轴","stamp":"BATCH",
                 "scale":"1:1","date":"2026.05","designer":"Python"})
    dxf_path = os.path.join(output_dir, "%s.dxf" % name)
    p.save(dxf_path)
    do_pdf = "args" in dir() and hasattr(args, "pdf") and args.pdf
    if do_pdf:
        p.export_pdf(dxf_path.replace(".dxf", ".pdf"))
    return dxf_path


def cmd_batch(args):
    """批量生成：读取 CSV，每行一个阶梯轴"""
    csv_path = args.csv
    if not os.path.exists(csv_path):
        print("Error: CSV file not found:", csv_path)
        return
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        parts = list(reader)
    print("Batch: %d parts loaded from %s" % (len(parts), csv_path))
    for i, part in enumerate(parts):
        name = part.get("name", "part_%02d" % i)
        print("  [%d/%d] %s..." % (i + 1, len(parts), name))
        gen_shaft_dxf(part, BASE)
    print("Batch done: %d files" % len(parts))


def cmd_geometry(args):
    """生成几何图形作业"""
    print("Running: geometry task...")
    exec(open(os.path.join(BASE, "exam_task2.py")).read())


def cmd_excel(args):
    """从 Excel 生成"""
    from dxf_excel import excel_to_dxf
    excel_to_dxf(
        excel_path=args.excel,
        output_pdf=args.pdf,
        output_svg=args.svg,
        frame_size=args.frame,
    )


def cmd_shaft_from_args(args):
    """Generate shaft with custom params"""
    cmd_shaft(args)


def cmd_list(args):
    """列出所有可用模板"""
    templates = {
        "campus":   "校园总平面图 (campus_pro.py)",
        "shaft":    "阶梯轴零件图 (exam_task5_v3.py)",
        "geometry": "几何图形作业 (exam_task2.py)",
        "excel":    "从 Excel 文件生成 (--excel path.xlsx)",
        "batch":    "批量生成阶梯轴 (--csv parts.csv)",
    }
    print("=" * 50)
    print("  Available Templates")
    print("=" * 50)
    for name, desc in templates.items():
        print("  python run.py %-12s - %s" % (name, desc))


def main():
    parser = argparse.ArgumentParser(description="CAD Drawing Generator v2")
    parser.add_argument("command", nargs="?", default="list",
                        help="Command: campus/shaft/geometry/excel/batch/list")
    parser.add_argument("--csv", help="CSV file for batch processing")
    parser.add_argument("--excel", help="Excel file for data-driven generation")
    parser.add_argument("--pdf", help="Output PDF path (flag for batch)", action="store_true")
    parser.add_argument("--svg", help="Output SVG path", default=None)
    parser.add_argument("--frame", choices=["A3", "A2", "A1"], default="A3",
                        help="Frame size")

    args = parser.parse_args()
    commands = {
        "campus": cmd_campus, "shaft": cmd_shaft,
        "geometry": cmd_geometry, "excel": cmd_excel,
        "batch": cmd_batch, "list": cmd_list,
    }
    if args.command in commands:
        commands[args.command](args)
    else:
        print("Unknown command:", args.command)
        cmd_list(args)

if __name__ == "__main__":
    main()
