import os, sys
FC_BIN = r"E:\CAD自动化制图\FreeCAD\FreeCAD_1.1.1-Windows-x86_64-py311\bin"
for p in [os.path.join(FC_BIN,"..","Lib"), os.path.join(FC_BIN,"..","Mod")]:
    if p not in sys.path: sys.path.append(p)
import FreeCAD, TechDraw, TechDrawGui
os.makedirs("output/professional", exist_ok=True)

# Find templates
tdir = os.path.join(FC_BIN, "..", "data", "Mod", "TechDraw", "Templates", "ISO")
tdir_zh = os.path.join(tdir, "localized", "zh-CN", "landscape")
if os.path.isdir(tdir_zh): tdir = tdir_zh

templates = [f for f in os.listdir(tdir) if "A3" in f and "Landscape" in f]
print("Templates found:", templates)
if not templates:
    # Try broader search
    tdir = os.path.join(FC_BIN, "..", "data", "Mod", "TechDraw", "Templates")
    for root, dirs, files in os.walk(tdir):
        for f in files:
            if "A3" in f and "Landscape" in f:
                templates.append(os.path.join(root,f))
                if len(templates) >= 1: break
        if templates: break
    tdir = os.path.dirname(templates[0]) if templates else tdir

if not templates:
    print("No A3 template found!")
    sys.exit(1)

template_path = os.path.join(tdir, templates[0]) if not os.path.isabs(templates[0]) else templates[0]
print("Using template:", template_path)

# Load model
fcstd = "output/professional/model_freecad.fcstd"
doc = FreeCAD.openDocument(fcstd)
print("Loaded:", fcstd)

# Create page
page = doc.addObject("TechDraw::DrawPage", "Page")
tpl = doc.addObject("TechDraw::DrawSVGTemplate", "Template")
tpl.Template = template_path
page.Template = tpl

# Get main shape
shapes = [o for o in doc.Objects if hasattr(o,"Shape") and not o.Shape.isNull() and o.Shape.Volume > 0]
if shapes:
    main = shapes[0]
    print("Main shape:", main.Label)
    
    # Top view
    top = doc.addObject("TechDraw::DrawViewPart","TopView")
    page.addView(top)
    top.Source = main
    top.Direction = (0,0,1)
    top.X = 210; top.Y = 148
    top.Scale = 0.05
    
    # Front view
    front = doc.addObject("TechDraw::DrawViewPart","FrontView")
    page.addView(front)
    front.Source = main
    front.Direction = (0,-1,0)
    front.X = 210; front.Y = 80
    front.Scale = 0.05
    
    doc.recompute()
    
    pdf_path = "output/professional/techdraw_sheet.pdf"
    try:
        TechDrawGui.exportPageAsPdf(page, pdf_path)
        print("PDF:", pdf_path, os.path.getsize(pdf_path)//1024, "KB")
    except Exception as e:
        print("PDF export error:", e)

doc.saveAs("output/professional/techdraw_source.fcstd")
print("Done")
