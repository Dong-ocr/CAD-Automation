# ======================================================================
#  exam_task2.py — 平面几何图形自动绘制（AutoCAD 作业需求二）
#
#  使用 cad_toolbox.CADProject，不再重复造轮子
#
#  任务要求：
#    1. 矩形阵列组合：200×100 外框 + 5×5 均布圆（直径10mm）
#    2. 对称图形：左右对称键槽，R10 倒角
#    3. 圆弧连接：R30 大弧过渡两个 R10 小圆，粗/细线区分
#
#  输出：exam_task2.dxf + exam_task2.pdf
# ======================================================================

from cad_toolbox import CADProject
import math, os

BASE = os.path.dirname(os.path.abspath(__file__))
p = CADProject("exam_task2")
p.setup_layers()

# ── 任务 1: 矩形阵列组合 ──────────────────────────────────────────

def task1(xo=0, yo=220):
    W, H = 200, 100
    cx, cy = xo + W/2, yo - H/2
    p.rect(cx, cy, W, H, "OUTLINE")
    p.circle_array(cx, cy, W, H, 5, 5, 5, margin_x=25, margin_y=20)
    p.text("任务1: 矩形阵列组合", cx, yo+15, 5, "TITLE")

# ── 任务 2: 对称键槽 ──────────────────────────────────────────────

def task2(xo=0, yo=60):
    W, H = 200, 100
    cx, cy = xo + W/2, yo - H/2
    # 外框
    p.rect(cx, cy, W, H, "OUTLINE")
    # 中心线
    p.centerline(xo, xo+W, cy)
    p.centerline(cy-H/2, cy+H/2, cx, layer="CENTERLINE")
    # 中心竖线（手动）
    p.line(cx, cy-H/2, cx, cy+H/2, "CENTERLINE", 0.18)

    # 键槽参数
    sw, sh = 20, 30  # 槽宽、槽深（左右各一个）
    gap = 40         # 两槽间距

    for side in [-1, 1]:
        sx = cx + side * gap/2
        # 键槽外轮廓（三边）
        p.line(sx - sw/2, cy + sh/2, sx + sw/2, cy + sh/2, "OUTLINE")
        p.line(sx - sw/2, cy - sh/2, sx + sw/2, cy - sh/2, "OUTLINE")
        p.line(sx - sw/2, cy - sh/2, sx - sw/2, cy + sh/2, "OUTLINE", 0.5)
        p.line(sx + sw/2, cy - sh/2, sx + sw/2, cy + sh/2, "OUTLINE", 0.5)
        # R10 倒角（四角圆弧）
        for sy in [-1, 1]:
            r = 10
            acx = sx + sy * (sw/2 - r) if abs(sy) > 0 else sx
            acy = cy + sy * (sh/2 - r)
            # 圆弧
            a1 = 0 if sy == 1 else 180
            a2 = 180 if sy == 1 else 0
            p.arc(acx, acy, r, a1, a2, "OUTLINE")

    # 标注
    p.dim_h(xo, xo+W, cy-H/2-10, text="200")
    p.dim_v(xo, cy-H/2, cy+H/2, offset=5, text="100")
    p.text("任务2: 对称键槽", cx, yo+15, 5, "TITLE")

# ── 任务 3: 圆弧连接 ──────────────────────────────────────────────

def task3(xo=400, yo=60):
    R_SMALL, R_LARGE = 10, 30
    SPACING = 60
    cx = xo + SPACING/2
    cy = yo - R_SMALL - 10
    left_cx, right_cx = xo, xo + SPACING

    # 中心线
    p.centerline(xo-15, xo+SPACING+15, cy)

    # 小圆
    p.circle(left_cx, cy, R_SMALL, "OUTLINE")
    p.circle(right_cx, cy, R_SMALL, "OUTLINE")

    # 大圆弧（相切过渡）
    half_s = SPACING / 2
    center_dist = R_SMALL + R_LARGE
    if center_dist > half_s:
        vert_off = math.sqrt(max(0, center_dist**2 - half_s**2))
        arc_cy = cy - vert_off
        angle_to_left = math.atan2(cy - arc_cy, left_cx - cx)
        angle_to_right = math.atan2(cy - arc_cy, right_cx - cx)
        p.arc(cx, arc_cy, R_LARGE, math.degrees(angle_to_left),
              math.degrees(angle_to_right), "OUTLINE")
        # 辅助线
        p.line(left_cx, cy, cx, arc_cy, "AUX", 0.25)
        p.line(right_cx, cy, cx, arc_cy, "AUX", 0.25)
        p.text("O", cx, arc_cy-8, 3, "DIMENSION")

    # 标注
    p.text("R%d" % R_LARGE, cx+R_LARGE*0.6, cy-15, 3, "DIMENSION")
    p.text("R%d" % R_SMALL, left_cx-R_SMALL-5, cy+R_SMALL+3, 3, "DIMENSION")
    p.text("R%d" % R_SMALL, right_cx+R_SMALL+5, cy+R_SMALL+3, 3, "DIMENSION")
    p.text("任务3: 圆弧连接", cx, yo+15, 5, "TITLE")

# ── 运行 ──────────────────────────────────────────────────────────

task1(50, 220)
task2(50, 60)
task3(400, 60)

# ── 图例 ──────────────────────────────────────────────────────────

lx, ly = 50, -20
p.text("图例", lx, ly, 4, "TITLE")
legends = [("OUTLINE", "轮廓线 (0.5mm)"), ("AUX", "辅助线 (0.25mm)"),
           ("CENTERLINE", "中心线 (红色)"), ("DIMENSION", "尺寸标注 (绿色)")]
for i, (lyr, desc) in enumerate(legends):
    y = ly - 12 - i * 7
    p.rect(lx+2, y, 12, 4, lyr, 0.5)
    p.text(desc, lx+15, y, 2.5, "TEXT")

# ── 图框 + 保存 ──────────────────────────────────────────────────

p.add_frame({"client":"AutoCAD 作业二","project":"平面几何图形自动绘制",
             "drawing":"基础功能测试","stamp":"T-002",
             "scale":"1:1","date":"2026.05","designer":"Python+cad_toolbox"})
dxf = os.path.join(BASE, "exam_task2.dxf")
p.save(dxf)
p.export_pdf(dxf.replace(".dxf", ".pdf"))
print("Done!")
