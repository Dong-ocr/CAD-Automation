#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FreeCAD 立体图生成宏 — 在 FreeCAD GUI 中运行
使用方法:
  1. 双击打开 FreeCAD
  2. File → Open → output/professional/apartment_interior.fcstd
  3. Macro → Macros → 选择本文件 → Execute
  4. 自动生成 A4 图纸: 正视图 + 俯视图 + 右视图 + 等轴测立体图
  5. 导出 PDF + SVG
"""

import FreeCAD, os, Part, math

# ====== 配置 ======
DOC_PATH = FreeCAD.ActiveDocument.FileName if FreeCAD.ActiveDocument else ""
OUTPUT_DIR = os.path.dirname(DOC_PATH) if DOC_PATH else "E:/CAD自动化制图/output/professional"

def build_techdraw():
    """在 FreeCAD GUI 中创建 TechDraw 工程图"""
    doc = FreeCAD.ActiveDocument
    if not doc:
        print("❌ 请先打开一个文档")
        return

    # 构建整体 Shape
    shapes = [o.Shape for o in doc.Objects if hasattr(o,"Shape") and o.Shape and not o.Shape.isNull()]
    if not shapes:
        print("❌ 文档中没有有效 Shape")
        return
    comp = Part.makeCompound(shapes)

    # 添加 Compound 对象
    whole = doc.addObject("Part::Feature", "WholeModel")
    whole.Shape = comp

    # 找 A4 模板
    td_dir = os.path.join(FreeCAD.getResourceDir(), "Mod", "TechDraw", "Templates")
    tmpl_path = os.path.join(td_dir, "Default_Template_A4_Landscape.svg")
    if not os.path.exists(tmpl_path):
        print("⚠️ 未找到模板")

    # 创建页面
    page = doc.addObject("TechDraw::DrawPage", "DrawingPage")
    page.Label = "两室一厅 - 工程图"

    # 加载模板 (需在 GUI 中通过 Template 属性设置)
    # 在 FreeCAD GUI 中，可以通过模板对话框加载
    # 这里自动创建视图

    # 创建视图
    views = []
    view_configs = [
        ("FrontView",  "正视图", (0,-1,0), (1,0,0), 120, 160),
        ("TopView",    "俯视图", (0,0,-1), (1,0,0), 120, 60),
        ("SideView",   "右视图", (1,0,0),  (0,1,0), 220, 160),
        ("AxoView",    "立体图(等轴测)", (-1,-1,1), (1,0,0), 250, 100),
    ]
    for name, label, direction, xdir, x, y in view_configs:
        v = doc.addObject("TechDraw::DrawViewPart", name)
        v.Label = label
        v.Source = [whole]
        v.Direction = direction
        v.XDirection = xdir
        page.addView(v)
        v.X = x
        v.Y = y
        v.Scale = 0.015
        views.append(v)

    doc.recompute()
    print(f"✅ 已创建 {len(views)} 个视图")

    # 导出
    try:
        import TechDraw
        pdf_path = os.path.join(OUTPUT_DIR, "apartment_techdraw.pdf")
        TechDraw.exportPageToPdf(page, pdf_path)
        print(f"✅ PDF: {pdf_path}")
    except Exception as e:
        print(f"⚠️ PDF 导出: {e}")

    print(f"\n🎉 完成！请手动设置模板:")
    print(f"   在树中选择 DrawingPage → 属性 Template → 选择 {tmpl_path}")
    print(f"   然后重新导出 PDF")

if __name__ == "__main__":
    build_techdraw()
