# CAD 自动化制图系统

基于 Python + ezdxf 的 CAD 自动出图工具。**无需安装 AutoCAD**，直接生成 DXF/PDF/SVG/PLT 文件。

## 快速开始

`ash
# 安装依赖
pip install ezdxf matplotlib svgwrite openpyxl

# 生成示例图纸
python exam_task2.py           # 几何图形作业
python exam_task5_v3.py        # 阶梯轴零件图
python run.py campus           # 校园总平面图
`

## 文件结构

| 文件 | 用途 |
|------|------|
| cad_toolbox.py | **核心工具箱** - 所有绘图功能统一入口 |
| un.py | **命令行入口** - 一行命令出图 |
| order_template.py | **接单模板** - 新订单从此开始 |
| exam_task2.py | 几何图形作业（模板，可直接改参数复用） |
| exam_task5_v3.py | 阶梯轴零件图（模板，可直接改参数复用） |
| atch_parts.csv | 批量零件尺寸表 |
| library.py | 块库（建筑/树木/车位/指北针等） |
| hatch_lib.py | 填充系统 |
| dim_lib.py | 尺寸标注系统 |
| rame_lib.py | 图框/标题栏 |
| ender.py | DXF → SVG/PDF 渲染引擎 |
| dxf_excel.py | Excel 数据驱动生成 |
| 	est_system.py | **一键自检** - 接单前跑一遍 |

## 命令速查

`ash
python run.py list             # 查看所有可用模板
python run.py shaft            # 生成阶梯轴零件图
python run.py geometry         # 生成几何图形作业
python run.py batch --csv batch_parts.csv   # 批量生成阶梯轴
python run.py excel --excel 图块数据模板.xlsx  # 从 Excel 生成
python test_system.py          # 一键自检
`

## 接单流程

`
收到作业需求
    │
    ├─ 几何作图题 → 改 exam_task2.py 参数
    ├─ 机械零件图 → 改 exam_task5_v3.py 参数
    ├─ 批量生成   → 填 batch_parts.csv
    │               python run.py batch
    └─ 全新题型   → 复制 order_template.py
                    修改尺寸数据 + 绘图代码
    │
    ▼
python xxx.py  →  输出 DXF + PDF
    │
    ▼
交付 PDF 给客户
`

## 工具箱 API

`python
from cad_toolbox import CADProject

p = CADProject("项目名")
p.setup_layers()

# 基本图元
p.line(x1, y1, x2, y2, layer="OUTLINE", lw=0.5)
p.circle(cx, cy, r, layer="OUTLINE", lw=0.5)
p.arc(cx, cy, r, a1, a2, layer="OUTLINE", lw=0.5)
p.rect(cx, cy, w, h, layer="OUTLINE", lw=0.5)
p.text(text, x, y, height=2.5, layer="TEXT")

# 高级功能
p.circle_array(cx, cy, w, h, cols, rows, r)  # 圆阵列
p.dim_h(x1, x2, y, text="100")               # 水平标注
p.roughness(x, y, ra=3.2)                     # 粗糙度
p.tolerance(x, y, "圆圆", "0.02", "A-B")    # 形位公差
p.thread_ext(x1, x2, y, major_r, minor_r)    # 螺纹
p.hatch_section(boundary_pts)                 # 剖面线

# 图框 + 输出
p.add_frame(frame_size="A3")
p.save("output.dxf")
p.export_pdf("output.pdf")
p.export_svg("output.svg")
p.export_plt("output.plt")
`

## 预览

生成的 PDF 可直接发给客户确认，无需对方安装 AutoCAD。

## 依赖

- ezdxf >= 1.4
- matplotlib（用于 PDF 导出）
- svgwrite（用于 SVG 导出）
- openpyxl（用于 Excel 数据驱动）
