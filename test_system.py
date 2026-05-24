# ======================================================================
#  test_system.py — 一键系统验证脚本
#
#  验证所有核心功能是否正常工作，输出结果摘要
#
#  用法：
#    python test_system.py
# ======================================================================

import os, sys, tempfile, traceback

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

PASS = 0
FAIL = 0
ERRORS = []

def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print("  [PASS] %s" % name)
    else:
        FAIL += 1
        msg = "[FAIL] %s" % name
        if detail: msg += " -- " + detail
        print("  " + msg)
        ERRORS.append((name, detail))

def section(title):
    print()
    print("=" * 55)
    print("  " + title)
    print("=" * 55)


# ═══════════════════════════════════════════════════════════════════════
#  1. 导入测试
# ═══════════════════════════════════════════════════════════════════════

section("1. 模块导入")

try:
    from cad_toolbox import CADProject
    check("cad_toolbox.CADProject import", True)
except Exception as e:
    check("cad_toolbox.CADProject import", False, str(e))

try:
    from library import BlockLibrary
    check("library.BlockLibrary import", True)
except Exception as e:
    check("library.BlockLibrary import", False, str(e))

try:
    from hatch_lib import HatchFiller
    check("hatch_lib.HatchFiller import", True)
except Exception as e:
    check("hatch_lib.HatchFiller import", False, str(e))

try:
    from dim_lib import DimLib
    check("dim_lib.DimLib import", True)
except Exception as e:
    check("dim_lib.DimLib import", False, str(e))

try:
    from frame_lib import FrameLib, FRAME_SIZES
    check("frame_lib.FrameLib import", True)
    check("frame_lib.FRAME_SIZES defined", True)
except Exception as e:
    check("frame_lib.FrameLib import", False, str(e))

try:
    from render import DXFRenderer
    check("render.DXFRenderer import", True)
except Exception as e:
    check("render.DXFRenderer import", False, str(e))


# ═══════════════════════════════════════════════════════════════════════
#  2. cad_toolbox 基础功能
# ═══════════════════════════════════════════════════════════════════════

section("2. cad_toolbox 基础绘图")

tmp = os.path.join(BASE, "_test_output.dxf")
try:
    p = CADProject("Test")
    p.setup_layers()

    # Basic primitives
    p.line(0, 0, 100, 0)
    p.circle(50, 50, 20)
    p.arc(50, 50, 15, 0, 90)
    p.rect(50, -30, 80, 40)
    p.text("Hello", 50, -60, 3)
    p.polyline([(0, -80), (20, -80), (20, -100)])
    p.centerline(0, 100, 120)

    # New: circle_array
    n = p.circle_array(200, 50, 100, 50, 5, 5, 5, margin_x=10, margin_y=8)
    check("circle_array returns %d circles" % n, n == 25)

    # New: rect_grid
    p.rect_grid(200, -30, 60, 40, 3, 3)

    # Dimensions
    p.dim_h(0, 100, -15)
    p.dim_v(0, 0, 50, offset=-15)

    # Markings
    p.roughness(50, 80, 3.2)
    p.tolerance(200, 80, "圆圆", "0.02", "A-B")
    p.tolerance_leader(200, 76, 200, 70)

    # Thread
    p.thread_ext(100, 160, 120, 12, 10, chamfer=2)
    p.thread_triangles(100, 160, 120, 12, 10, 3)

    # Hatch
    p.hatch_section([(20, 150), (80, 150), (80, 180), (20, 180)])
    p.hatch_solid([(20, -50), (40, -50), (40, -35), (20, -35)])

    # Frame
    p.add_frame(frame_size="A3")

    # Save
    path = p.save(tmp)
    check("save() returns path", path == tmp)

    # Verify file exists
    check("DXF file exists", os.path.exists(tmp))

    # _last_dxf caching
    check("_last_dxf set", p._last_dxf == tmp)

    # Export SVG
    svg_path = p.export_svg(tmp.replace(".dxf", ".svg"))
    check("SVG export works", os.path.exists(svg_path))

    # Export PDF
    pdf_path = p.export_pdf(tmp.replace(".dxf", ".pdf"))
    check("PDF export works", os.path.exists(pdf_path))

    # Export PLT (new)
    plt_path = p.export_plt(tmp.replace(".dxf", ".plt"))
    check("PLT export works", os.path.exists(plt_path))
    if os.path.exists(plt_path):
        with open(plt_path) as f:
            plt_content = f.read()
        check("PLT has HPGL commands", "IN;" in plt_content and "SP" in plt_content)

except Exception as e:
    check("CADProject full test", False, str(e))
    traceback.print_exc()


# ═══════════════════════════════════════════════════════════════════════
#  3. FRAME_SIZES 支持
# ═══════════════════════════════════════════════════════════════════════

section("3. 图框尺寸")

try:
    p2 = CADProject("FrameTest")
    p2.setup_layers()
    p2.add_frame(frame_size="A3")
    check("A3 frame", True)
    # Check FRAME_SIZES dict
    check("FRAME_SIZES has A3/A2/A1",
          p2.FRAME_SIZES["A3"] == (420, 297) and
          p2.FRAME_SIZES["A2"] == (594, 420) and
          p2.FRAME_SIZES["A1"] == (841, 594))
except Exception as e:
    check("Frame size support", False, str(e))


# ═══════════════════════════════════════════════════════════════════════
#  4. run.py & batch
# ═══════════════════════════════════════════════════════════════════════

section("4. run.py & batch")

try:
    from run import gen_shaft_dxf
    part = {"name": "TestShaft", "d1": 25, "l1": 30, "d2": 30, "l2": 30,
            "d3": 20, "l3": 20, "d4": 28, "l4": 20, "key_w": 8,
            "key_d": 3.5, "thread": "M20"}
    result = gen_shaft_dxf(part, BASE)
    check("gen_shaft_dxf returns path", result and os.path.exists(result))
    check("gen_shaft_dxf filename correct", "TestShaft.dxf" in result)
except Exception as e:
    check("gen_shaft_dxf", False, str(e))
    traceback.print_exc()


# ═══════════════════════════════════════════════════════════════════════
#  5. 清理
# ═══════════════════════════════════════════════════════════════════════

section("5. 清理测试文件")

for f in ["_test_output.dxf", "_test_output.svg", "_test_output.pdf", "_test_output.plt",
          "TestShaft.dxf"]:
    fp = os.path.join(BASE, f)
    if os.path.exists(fp):
        try:
            os.remove(fp)
            check("Cleaned: %s" % f, True)
        except:
            check("Clean: %s" % f, False, "cannot remove")

# Clean temp scripts
for f in ["_do_patch.py", "_check.py", "_check2.py", "_fix_plt.py", "_add_plt.py",
          "_patch_toolbox.py", ".cad_toolbox.b64", "_patch.p64"]:
    fp = os.path.join(BASE, f)
    if os.path.exists(fp):
        try:
            os.remove(fp)
        except:
            pass


# ═══════════════════════════════════════════════════════════════════════
#  结果汇总
# ═══════════════════════════════════════════════════════════════════════

print()
print("=" * 55)
print("  TEST RESULTS")
print("=" * 55)
print("  PASS: %d" % PASS)
print("  FAIL: %d" % FAIL)
print("  Total: %d" % (PASS + FAIL))
print()

if FAIL > 0:
    print("  Failed tests:")
    for name, detail in ERRORS:
        print("    - %s: %s" % (name, detail))
    sys.exit(1)
else:
    print("  All tests passed!")
    print()
    print("  System is ready for production use.")
    sys.exit(0)
