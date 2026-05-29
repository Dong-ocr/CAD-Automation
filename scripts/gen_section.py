"""Section view generator from 3D model data"""
import json, math, os, ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment

os.makedirs("output/professional", exist_ok=True)
d = json.load(open("demo_project.json","r",encoding="utf-8"))
walls = d["w"]

LAYERS = {
    "S-OUTLINE":(1,"CONTINUOUS",0.50,"Section outline"),
    "S-HATCH":(8,"CONTINUOUS",0.09,"Section hatch"),
    "S-DIM":(3,"CONTINUOUS",0.09,"Section dim"),
    "S-TEXT":(7,"CONTINUOUS",0.09,"Section text"),
    "S-GRID":(4,"CONTINUOUS",0.09,"Grid lines"),
    "S-TITLE":(7,"CONTINUOUS",0.50,"Title block"),
}
def lw(v): return int(v*100)

doc = ezdxf.new(dxfversion="R2010", units=units.MM)
msp = doc.modelspace()

for ln,(ci,lt,lv,_) in LAYERS.items():
    try:
        l = doc.layers.add(ln); l.color=ci
        l.line_type=lt if lt in doc.linetypes else "CONTINUOUS"; l.lineweight=lw(lv)
    except: pass

# === Section A-A: Cut through the middle of the building ===
cut_y = (min(w["y1"] for w in walls) + max(w["y2"] for w in walls)) / 2
all_x = [w["x1"] for w in walls] + [w["x2"] for w in walls]
min_x, max_x = min(all_x), max(all_x)

# Collect wall intersections with section plane
sections = []
for w in walls:
    x1,y1,x2,y2 = w["x1"],w["y1"],w["x2"],w["y2"]
    t = w.get("thickness",240 if w["t"]=="\u5916" else 150)
    h = 2800  # floor height
    
    # Check if this wall crosses the cut line
    if (y1 <= cut_y <= y2) or (y2 <= cut_y <= y1):
        # Interpolate cut position
        if y2 != y1:
            ratio = (cut_y - y1) / (y2 - y1)
            cut_x = x1 + ratio * (x2 - x1)
            sections.append({
                "x": cut_x,
                "thickness": t,
                "height": h,
                "type": w["t"]
            })

# Sort by x position
sections.sort(key=lambda s: s["x"])

# Draw section outline
base_y = 0  # ground level
floor_h = 200  # floor slab

# Scale factor: 1/10 to convert mm to drawing units
scale = 10

# Draw floor
floor_top = 0
# Find leftmost and rightmost points
if sections:
    left_x = min(s["x"] for s in sections)
    right_x = max(s["x"] for s in sections)
    margin = 500
    
    # Floor slab
    msp.add_lwpolyline([
        ((left_x-margin)/scale, floor_top-floor_h/scale),
        ((right_x+margin)/scale, floor_top-floor_h/scale),
        ((right_x+margin)/scale, floor_top/scale),
        ((left_x-margin)/scale, floor_top/scale),
        ((left_x-margin)/scale, floor_top-floor_h/scale),
    ], dxfattribs={"layer":"S-HATCH","lineweight":lw(0.13)})
    
    # Draw each wall section
    for s in sections:
        x = s["x"] / scale
        t = s["thickness"] / scale
        h = s["height"] / scale
        
        # Wall solid fill (represented as outline + hatch)
        msp.add_lwpolyline([
            (x - t/2, floor_top/scale),
            (x + t/2, floor_top/scale),
            (x + t/2, (floor_top+h)/scale),
            (x - t/2, (floor_top+h)/scale),
            (x - t/2, floor_top/scale),
        ], dxfattribs={"layer":"S-OUTLINE","lineweight":lw(0.35)})
        
        # Floor connection
        msp.add_line((x-t/2, floor_top/scale), (x-t/2, (floor_top-floor_h)/scale),
                     dxfattribs={"layer":"S-OUTLINE","lineweight":lw(0.25)})
        msp.add_line((x+t/2, floor_top/scale), (x+t/2, (floor_top-floor_h)/scale),
                     dxfattribs={"layer":"S-OUTLINE","lineweight":lw(0.25)})

# Grid lines
grid_spacing = 1000 / scale
for i, gx in enumerate(range(int((left_x-margin)/scale), int((right_x+margin)/scale+grid_spacing), int(grid_spacing))):
    msp.add_line((gx, (floor_top-floor_h-500)/scale), (gx, (floor_top+3200)/scale),
                 dxfattribs={"layer":"S-GRID","lineweight":lw(0.09)})
    msp.add_text(str(i+1), height=30, dxfattribs={"layer":"S-TEXT","color":7}
    ).set_placement((gx, (floor_top-floor_h-800)/scale), align=TextEntityAlignment.CENTER)

# Section label
mid_x = (left_x + right_x) / 2 / scale
msp.add_text("A-A 剖面图  1:"+str(int(scale)), height=40,
    dxfattribs={"layer":"S-TEXT","color":7}
).set_placement((mid_x, (floor_top+3400)/scale), align=TextEntityAlignment.CENTER)

# Height dimension
max_h = max(s["height"] for s in sections) / scale + floor_top/scale
msp.add_line(((right_x+margin)/scale+50, floor_top/scale),
             ((right_x+margin)/scale+50, max_h),
             dxfattribs={"layer":"S-DIM","color":3,"lineweight":lw(0.09)})
msp.add_text("H="+str(int(max_h*scale))+"mm", height=25,
    dxfattribs={"layer":"S-DIM","color":3}
).set_placement(((right_x+margin)/scale+80, (floor_top/scale+max_h)/2), align=TextEntityAlignment.CENTER)

# Title block
tb_x = (right_x+margin)/scale + 200
tb_y = floor_top/scale - floor_h/scale - 200
msp.add_lwpolyline([(tb_x,tb_y),(tb_x+300,tb_y),(tb_x+300,tb_y+200),(tb_x,tb_y+200),(tb_x,tb_y)],
                   dxfattribs={"layer":"S-TITLE","lineweight":lw(0.35)})
items = [("剖面","A-A"),("比例","1:"+str(int(scale))),("图号","PM-01")]
for i,(lb,v) in enumerate(items):
    yp = tb_y+200-30-i*60
    msp.add_line((tb_x,yp),(tb_x+300,yp),dxfattribs={"layer":"S-TITLE","lineweight":lw(0.13)})
    msp.add_text(lb+": "+v,height=25,dxfattribs={"layer":"S-TITLE","color":7}
    ).set_placement((tb_x+10,yp-15),align=TextEntityAlignment.LEFT)

out = "output/professional/section_a_a.dxf"
doc.saveas(out)
print("OK: %s (%d entities)" % (out, len(msp)))
print("Section through Y=%.0fmm, %d walls intersected" % (cut_y/10, len(sections)))
