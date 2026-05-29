import json, os, math, ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment

os.makedirs("output/professional", exist_ok=True)
d = json.load(open("demo_project.json","r",encoding="utf-8"))
walls, rooms, furniture = d["w"], d["r"], d["f"]

LAYERS = {
    "0":(7,"CONTINUOUS",0.25), "A-WALL-OUTER":(1,"CONTINUOUS",0.70),
    "A-WALL-INNER":(6,"CONTINUOUS",0.35), "A-DOOR":(2,"CONTINUOUS",0.25),
    "A-FURN":(5,"CONTINUOUS",0.13), "A-DIM":(3,"CONTINUOUS",0.09),
    "A-TEXT":(7,"CONTINUOUS",0.09), "A-ROOM":(4,"CONTINUOUS",0.09),
    "A-TITLE":(7,"CONTINUOUS",0.50), "A-ANNO":(4,"CONTINUOUS",0.09),
    "A-COLS":(6,"CENTER",0.35), "H-WATER-LINE":(5,"CONTINUOUS",0.25),
    "H-ANNO":(4,"CONTINUOUS",0.09), "A-VP":(7,"CONTINUOUS",0.09),
}

def lw(v): return int(v*100)

# ========== MODEL SPACE ==========
doc = ezdxf.new(dxfversion="R2010", units=units.MM)
msp = doc.modelspace()

for ln,(ci,lt,lv) in LAYERS.items():
    try:
        l = doc.layers.add(ln); l.color=ci
        l.line_type=lt if lt in doc.linetypes else "CONTINUOUS"; l.lineweight=lw(lv)
    except: pass

for lt,pat in [("DASHED","0.5,-0.25"),("CENTER","1.0,-0.25,0.25,-0.25")]:
    if lt not in doc.linetypes:
        try: doc.linetypes.add(lt,pattern=pat)
        except: pass

min_x=min(w["x1"] for w in walls)/10; max_x=max(w["x2"] for w in walls)/10
min_y=min(w["y1"] for w in walls)/10; max_y=max(w["y2"] for w in walls)/10

# Walls
for w in walls:
    x1,y1,x2,y2 = w["x1"]/10,w["y1"]/10,w["x2"]/10,w["y2"]/10
    layer = "A-WALL-OUTER" if w["t"]=="\u5916" else "A-WALL-INNER"
    lwv = 0.70 if w["t"]=="\u5916" else 0.35
    msp.add_line((x1,y1),(x2,y2),dxfattribs={"layer":layer,"lineweight":lw(lwv)})
    t = w.get("thickness",240 if w["t"]=="\u5916" else 150)/10
    dx,dy=x2-x1,y2-y1; ln=math.hypot(dx,dy)
    if ln>0:
        nx,ny=-dy/ln*t,dx/ln*t
        msp.add_line((x1+nx,y1+ny),(x2+nx,y2+ny),dxfattribs={"layer":layer,"lineweight":lw(0.18)})

# Rooms
for r in rooms:
    x,y,rw,rd = r["x"]/10,r["y"]/10,r["w"]/10,r["d"]/10
    msp.add_lwpolyline([(x,y),(x+rw,y),(x+rw,y+rd),(x,y+rd),(x,y)],
        dxfattribs={"layer":"A-ROOM","lineweight":lw(0.09)})

# Furniture
for fi in furniture:
    x,y,fw,fd = fi["x"]/10,fi["y"]/10,fi["w"]/10,fi["d"]/10
    msp.add_lwpolyline([(x,y),(x+fw,y),(x+fw,y+fd),(x,y+fd),(x,y)],
        dxfattribs={"layer":"A-FURN","color":5,"lineweight":lw(0.13)})
    msp.add_text(fi["n"],height=30,dxfattribs={"layer":"A-TEXT","color":7}
    ).set_placement((x+fw/2,y+fd/2),align=TextEntityAlignment.CENTER)

# Dims
off = 50
msp.add_line((min_x,max_y+off-10),(max_x,max_y+off-10),dxfattribs={"layer":"A-DIM","color":3,"lineweight":lw(0.09)})
msp.add_line((min_x,max_y),(min_x,max_y+off),dxfattribs={"layer":"A-DIM","color":3,"lineweight":lw(0.09)})
msp.add_line((max_x,max_y),(max_x,max_y+off),dxfattribs={"layer":"A-DIM","color":3,"lineweight":lw(0.09)})
msp.add_text(str(int((max_x-min_x)*10))+"mm",height=30,
    dxfattribs={"layer":"A-DIM","color":3}
).set_placement(((min_x+max_x)/2,max_y+off-15),align=TextEntityAlignment.CENTER)
msp.add_line((max_x+off-10,min_y),(max_x+off-10,max_y),dxfattribs={"layer":"A-DIM","color":3,"lineweight":lw(0.09)})
msp.add_line((max_x,min_y),(max_x+off,min_y),dxfattribs={"layer":"A-DIM","color":3,"lineweight":lw(0.09)})
msp.add_line((max_x,max_y),(max_x+off,max_y),dxfattribs={"layer":"A-DIM","color":3,"lineweight":lw(0.09)})
msp.add_text(str(int((max_y-min_y)*10))+"mm",height=30,
    dxfattribs={"layer":"A-DIM","color":3}
).set_placement((max_x+off-15,(min_y+max_y)/2),align=TextEntityAlignment.CENTER)

# Model space border (A3 extents)
border_margin = 100
msp.add_lwpolyline([
    (min_x-border_margin,min_y-border_margin),
    (max_x+border_margin,min_y-border_margin),
    (max_x+border_margin,max_y+border_margin+off),
    (min_x-border_margin,max_y+border_margin+off),
    (min_x-border_margin,min_y-border_margin)
],dxfattribs={"layer":"0","lineweight":lw(0.09)})

print("Model space: %d entities" % len(msp))

# ========== PAPER SPACE LAYOUT ==========
# A3: 420x297mm
paper_w, paper_h = 420, 297
margin = 10  # printable margin

# Create layout
layout = doc.layouts.new("A3-平面布置图")
layout.page_setup(size=(paper_w,paper_h), margins=(margin,margin,margin,margin), units="mm")

# Viewport - in DXF, we add a viewport entity to the layout block
# The viewport shows a portion of modelspace at a scale
vp_width = paper_w - 2*margin - 80  # leave room for title block
vp_height = paper_h - 2*margin
vp_x = margin
vp_y = margin

# Calculate scale to fit model content
model_w = (max_x - min_x + 2*border_margin) / 10 # convert to mm (1 unit = 10mm in our DXF)
model_h = (max_y - min_y + border_margin*2 + off) / 10
scale_factor = min(vp_width/model_w, vp_height/model_h) * 0.85  # 85% fill

# Viewport center in model coordinates
center_x = (min_x + max_x) / 2
center_y = (min_y + max_y + off/2) / 2
vp_center_x = vp_x + vp_width/2
vp_center_y = vp_y + vp_height/2

# Add viewport entity - in Paperspace
vp = layout.add_viewport(
    center=(vp_center_x, vp_center_y),
    size=(vp_width-2, vp_height-2),
    view_center_point=(center_x, center_y),
    view_height=model_h * scale_factor,
    dxfattribs={"layer":"A-VP"}
)
# vp_id auto

# Layout title block (bottom-right)
tb_w = 180
tb_h = 60
tb_x = paper_w - margin - tb_w
tb_y = margin

# Title block lines
layout.add_lwpolyline([
    (tb_x, tb_y), (tb_x+tb_w, tb_y),
    (tb_x+tb_w, tb_y+tb_h), (tb_x, tb_y+tb_h), (tb_x, tb_y)
], dxfattribs={"layer":"A-TITLE","lineweight":lw(0.50)})

items = [
    ("项目","岩泊渡水电站"),
    ("图纸","室内平面布置图"),
    ("比例","1:"+str(int(1/scale_factor))),
    ("图号","JZ-01"),
]
for i,(lb,v) in enumerate(items):
    yp = tb_y+tb_h-15-i*14
    layout.add_line((tb_x+5,yp),(tb_x+tb_w-5,yp),dxfattribs={"layer":"A-TITLE","lineweight":lw(0.13)})
    layout.add_text(lb+": "+v,height=4,dxfattribs={"layer":"A-TITLE","color":7}
    ).set_placement((tb_x+8,yp-4),align=TextEntityAlignment.LEFT)

# Paper border
layout.add_lwpolyline([
    (margin, margin), (paper_w-margin, margin),
    (paper_w-margin, paper_h-margin), (margin, paper_h-margin), (margin, margin)
], dxfattribs={"layer":"A-TITLE","lineweight":lw(0.35)})

# Sheet info
layout.add_text("A3 1:"+str(int(1/scale_factor))+"  mm",height=3,
    dxfattribs={"layer":"A-TEXT","color":7}
).set_placement((margin+5, paper_h-margin-8),align=TextEntityAlignment.LEFT)

# ========== SECONDARY LAYOUT: Site Plan ==========
layout2 = doc.layouts.new("A3-枢纽布置图")
layout2.page_setup(size=(paper_w,paper_h), margins=(margin,margin,margin,margin), units="mm")

# Wider view for site plan
scale2 = scale_factor * 0.5  # zoom out more
vp2 = layout2.add_viewport(
    center=(vp_center_x, vp_center_y),
    size=(vp_width-2, vp_height-2),
    view_center_point=(center_x, center_y),
    view_height=model_h * scale2,
    dxfattribs={"layer":"A-VP"}
)
# vp_id auto

# Same title block
for i,(lb,v) in enumerate([("项目","岩泊渡水电站"),("图纸","枢纽总布置图"),("比例","1:"+str(int(1/scale2))),("图号","ZZ-01")]):
    yp = tb_y+tb_h-15-i*14
    layout2.add_line((tb_x+5,yp),(tb_x+tb_w-5,yp),dxfattribs={"layer":"A-TITLE","lineweight":lw(0.13)})
    layout2.add_text(lb+": "+v,height=4,dxfattribs={"layer":"A-TITLE","color":7}
    ).set_placement((tb_x+8,yp-4),align=TextEntityAlignment.LEFT)

layout2.add_lwpolyline([
    (margin, margin), (paper_w-margin, margin),
    (paper_w-margin, paper_h-margin), (margin, paper_h-margin), (margin, margin)
], dxfattribs={"layer":"A-TITLE","lineweight":lw(0.35)})

print("Layouts: %s, %s" % (layout.name, layout2.name))

# Save
out_path = "output/professional/floor_plan_paperspace.dxf"
doc.saveas(out_path)
print("Saved: %s (%d layers, %d layouts)" % (out_path, len(doc.layers), len(doc.layouts)))
