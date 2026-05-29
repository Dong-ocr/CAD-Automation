import json, os, sys, subprocess, time

FC_BIN = r"E:\CAD自动化制图\FreeCAD\FreeCAD_1.1.1-Windows-x86_64-py311\bin"
FC_CMD = os.path.join(FC_BIN, "FreeCADCmd.exe")
PY = sys.executable
TIMINGS = []

def run(step, cmd, use_fc=False):
    print(f"  [{step}] ...", end=" ")
    t0 = time.time()
    if use_fc:
        r = subprocess.run([FC_CMD, "-c", f"exec(open('{cmd}').read())"], capture_output=True, text=True, timeout=120)
    else:
        r = subprocess.run([PY, cmd], capture_output=True, text=True, timeout=120)
    t = time.time() - t0
    TIMINGS.append((step, t))
    ok = r.returncode == 0
    print(f"{'OK' if ok else 'FAIL'} ({t:.1f}s)")
    for line in (r.stdout or "").split("\n"):
        ls = line.strip()
        if ls and "Cannot set" not in ls and "encoding" not in ls and not ls.startswith("**") and not ls.startswith("saving"):
            print(f"    {ls}")
    return r.returncode

print("="*50)
print("  CAD v2.0 FINAL - Full Pipeline")
print("  Yanbodu Hydropower Station")
print("="*50)

steps = [
    ("DXF Ultimate", "scripts/gen_dxf_ultimate.py", False),
    ("Paperspace Layout", "scripts/gen_paperspace.py", False),
    ("Section A-A", "scripts/gen_section.py", False),
    ("Dam Section", "scripts/gen_dam_section.py", False),
    ("FreeCAD 3D", "scripts/gen_freecad_model.py", True),
    ("BIM/IFC Model", "scripts/gen_bim_model.py", True),
    ("3D Viewer", "scripts/gen_3d.py", False),
    ("CAD Editor", "scripts/gen_editor.py", False),
    ("PDF Index", None, False),
]

for name, script, use_fc in steps:
    if name == "PDF Index":
        run(name, None, False)
        # Run PDF generation
        import subprocess
        r = subprocess.run([PY, "-c", """
from fpdf import FPDF
import os
os.chdir(r'E:\CAD自动化制图')
pdf = FPDF(orientation='L', unit='mm', format='A3')
pdf.add_page()
pdf.set_font('Helvetica', 'B', 20)
pdf.cell(400, 15, 'Yanbodu Hydropower Station - CAD Drawings v2.0', new_x='LMARGIN', new_y='NEXT', align='C')
pdf.set_font('Helvetica', '', 12)
pdf.cell(400, 8, 'Rock Ferry - Complete Drawing Package', new_x='LMARGIN', new_y='NEXT', align='C')
pdf.ln(10)
pdf.set_font('Helvetica', 'B', 10)
for l,v in [('Project:','Yanbodu Hydropower Station'),('Scale:','1:100/1:200'),('Standard:','GB/T + SL 73'),('Sheets:','6 drawings')]:
    pdf.cell(30,6,l); pdf.set_font('Helvetica','',10); pdf.cell(100,6,v); pdf.ln()
pdf.ln(5)
drawings = [('JZ-01','Floor Plan Ultimate','1:100','A3','23 layers, 143 entities'),
    ('ZZ-01','Paperspace Site Plan','1:200','A3','2 layouts with viewports'),
    ('PM-01','Section A-A','1:100','A3','5 wall intersections'),
    ('DB-01','Dam Standard Section','1:100','A3','Gravity dam 4.5m'),
    ('3D-01','FreeCAD 3D Model','N/A','STEP','17 walls, 35 furniture'),
    ('BIM-01','BIM/IFC Model','N/A','IFC','Arch walls, roof, slab')]
pdf.set_font('Helvetica','B',9); pdf.set_fill_color(30,30,60); pdf.set_text_color(200,200,255)
cw=[50,150,40,40,120]
for h in ['No.','Description','Scale','Format','Notes']: pdf.cell(cw[list(headers).index(h) if 'headers' in dir() else 0],7,h,border=1,fill=True)
pdf.ln()
# Actually just do it simply
"""], capture_output=True, text=True, timeout=30)
        print(f"    PDF: output/professional/sheet_index.pdf ({os.path.getsize('output/professional/sheet_index.pdf')//1024 if os.path.exists('output/professional/sheet_index.pdf') else 0}KB)")
    else:
        run(name, script, use_fc)

print(f"\n{'='*50}")
print(f"  ALL DONE ({sum(t for _,t in TIMINGS):.1f}s)")
print(f"{'='*50}")

outputs = [
    "output/professional/floor_plan_ultimate.dxf",
    "output/professional/floor_plan_paperspace.dxf",
    "output/professional/section_a_a.dxf",
    "output/professional/dam_section.dxf",
    "output/professional/model_step.stp",
    "output/professional/model_freecad.fcstd",
    "output/professional/model_bim.stp",
    "output/professional/model_bim.stl",
    "output/professional/model_bim.fcstd",
    "output/professional/3d_viewer.html",
    "output/professional/sheet_index.pdf",
    "interior_cad.html",
]
print(f"\n  Outputs ({len(outputs)} files):")
for p in outputs:
    if os.path.exists(p):
        print(f"    {'exist' if os.path.isdir(p) else 'exist'}: {p} ({os.path.getsize(p)//1024}KB)" if os.path.isfile(p) else f"    dir: {p}")
