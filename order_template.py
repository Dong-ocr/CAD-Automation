# ======================================================================
#  order_template.py — 新订单接单模板
#
#  用法：
#    1. 复制此文件为 客户名_作业名.py
#    2. 修改尺寸数据
#    3. 在下方画图区域写你的绘图代码
#    4. python 客户名_作业名.py
#
#  工具箱 API 速查：
#    p.line(x1,y1, x2,y2, layer, lw)
#    p.circle(cx,cy, r, layer, lw)
#    p.arc(cx,cy, r, a1,a2, layer, lw)
#    p.rect(cx,cy, w,h, layer, lw)
#    p.text(text, x,y, height, layer)
#    p.dim_h(x1,x2, y, offset, text)
#    p.dim_v(x, y1,y2, offset, text)
#    p.centerline(x1,x2, y)
#    p.hatch_section(boundary_pts)
#    p.roughness(x,y, ra_value)
#    p.tolerance(x,y, symbol, value, datum)
#    p.thread_ext(x1,x2, y, major_r, minor_r)
#    p.circle_array(cx,cy, w,h, cols,rows, r, margin_x, margin_y)
#    p.add_frame(fields, frame_size='A3')
#    p.save('output.dxf')
#    p.export_pdf('output.pdf')
#    p.export_plt('output.plt')
# ======================================================================

from cad_toolbox import CADProject
import math, os

# ── 配置区：修改这里 ─────────────────────────────────────────────
ORDER_NAME = "订单名称"        # 显示在图框中的项目名称
OUTPUT_FILE = "output"         # 输出文件名（不含后缀）
FRAME_SIZE = "A3"              # 图框尺寸 A3/A2/A1
# ─────────────────────────────────────────────────────────────────

BASE = os.path.dirname(os.path.abspath(__file__))

p = CADProject(ORDER_NAME)
p.setup_layers()

# ═══════════════════════════════════════════════════════════════════
#  绘图区：在这里写你的画图代码
# ═══════════════════════════════════════════════════════════════════

# 示例：画一个矩形带中心线
p.rect(0, 0, 200, 100, "OUTLINE")
p.centerline(-10, 210, 0)
p.centerline(-50, 50, 0, layer="CENTERLINE")
p.text("示例图形", 0, 60, 5, "TITLE")

# ═══════════════════════════════════════════════════════════════════
#  输出
# ═══════════════════════════════════════════════════════════════════

p.add_frame({
    "client": "客户名称",
    "project": ORDER_NAME,
    "drawing": "图名",
    "stamp": "T-001",
    "scale": "1:1",
    "date": "2026.05",
    "designer": "Python",
}, frame_size=FRAME_SIZE)

dxf = os.path.join(BASE, OUTPUT_FILE + ".dxf")
p.save(dxf)
p.export_pdf(dxf.replace(".dxf", ".pdf"))
print("订单生成完成: %s" % OUTPUT_FILE)
