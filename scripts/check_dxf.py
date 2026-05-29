import FreeCAD, importDXF, os
dxf = "E:/CAD自动化制图/output/professional/floor_plan_ultimate.dxf"
doc = FreeCAD.newDocument("DXFCheck")
importDXF.insert(dxf, doc.Name)
print("=== DXF 验证 ===")
print(f"版本: {FreeCAD.Version()[0]}.{FreeCAD.Version()[1]}.{FreeCAD.Version()[2]}")
stats = {"lines":0, "polylines":0, "texts":0}
for o in doc.Objects:
    if hasattr(o, "Length"):
        if hasattr(o, "Points"): stats["polylines"] += 1
        else: stats["lines"] += 1
    if hasattr(o, "Text") and o.Text: stats["texts"] += 1
print(f"线段: {stats['lines']}  多段线: {stats['polylines']}  文本: {stats['texts']}")
print(f"总对象: {len(doc.Objects)}")
FreeCAD.closeDocument(doc.Name)
print("=== OK ===")
