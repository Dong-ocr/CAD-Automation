#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DXF Ultimate - hatches, blocks, proper dimensions, SL 73 layers"""
import json, math, os, ezdxf
from ezdxf import units, colors
from ezdxf.enums import TextEntityAlignment
from ezdxf.math import Vec2

os.makedirs("output/professional", exist_ok=True)
d = json.load(open("demo_project.json","r",encoding="utf-8"))
walls, rooms, furniture, doors = d["w"], d["r"], d["f"], d["d"]

LAYERS = {
    "0":(7,"CONTINUOUS",0.25,"Default"),"A-WALL-OUTER":(1,"CONTINUOUS",0.70,"Outer Wall"),
    "A-WALL-INNER":(6,"CONTINUOUS",0.35,"Inner Wall"),"A-DOOR":(2,"CONTINUOUS",0.25,"Door"),
    "A-WINDOW":(2,"CONTINUOUS",0.18,"Window"),"A-FURN":(5,"CONTINUOUS",0.13,"Furniture"),
    "A-DIM":(3,"CONTINUOUS",0.09,"Dimension"),"A-TEXT":(7,"CONTINUOUS",0.09,"Text"),
    "A-ROOM":(4,"DASHED",0.09,"Room"),"A-TITLE":(7,"CONTINUOUS",0.50,"Title Block"),
    "A-ANNO":(4,"CONTINUOUS",0.09,"Anno"),"A-HATCH":(8,"CONTINUOUS",0.09,"Hatch"),
    "A-COLS":(6,"CENTER",0.35,"Columns"),"A-STAIR":(6,"CONTINUOUS",0.18,"Stair"),
    "H-DAM-BODY":(1,"CONTINUOUS",0.70,"Dam Body"),"H-WATER-LINE":(5,"CONTINUOUS",0.25,"Water"),
    "H-SLUICE":(2,"CONTINUOUS",0.35,"Slip Gate"),"H-PIPE":(4,"DASHED",0.18,"Pipe"),
    "H-EQUIP":(7,"CONTINUOUS",0.13,"Equip"),"H-CONTOUR":(3,"CONTINUOUS",0.09,"Contour"),
    "H-ANNO":(4,"CONTINUOUS",0.09,"H-Anno"),"H-REBAR":(6,"CONTINUOUS",0.18,"Rebar"),
}

def lw(v): return int(v*100)

doc = ezdxf.new(dxfversion="R2010", units=units.MM)
msp = doc.modelspace()

for ln,(ci,lt,lv,desc) in LAYERS.items():
    try:
        l = doc.layers.add(ln); l.color=ci
        l.line_type=lt if lt in doc.linetypes else "CONTINUOUS"; l.lineweight=lw(lv)
    except: pass

for lt,pat in [("DASHED","0.5,-0.25"),("CENTER","1.0,-0.25,0.25,-0.25")]:
    if lt not in doc.linetypes:
        try: doc.linetypes.add(lt, pattern=pat)
        except: pass

# Walls
min_x=min(w["x1"] for w in walls)/10; max_x=max(w["x2"] for w in walls)/10
min_y=min(w["y1"] for w in walls)/10; max_y=max(w["y2"] for w in walls)/10

for w in walls:
    x1,y1,x2,y2 = w["x1"]/10,w["y1"]/10,w["x2"]/10,w["y2"]/10
    layer="A-WALL-OUTER" if w["t"]=="\u5916" else "A-WALL-INNER"
    lwv = 0.70 if w["t"]=="\u5916" else 0.35
    msp.add_line((x1,y1),(x2,y2),dxfattribs={"layer":layer,"lineweight":lw(lwv)})
    t = w.get("thickness",240 if w["t"]=="\u5916" else 150)/10
    dx,dy=x2-x1,y2-y1; ln=math.hypot(dx,dy)
    if ln>0:
        nx,ny=-dy/ln*t,dx/ln*t
        msp.add_line((x1+nx,y1+ny),(x2+nx,y2+ny),dxfattribs={"layer":layer,"lineweight":lw(0.18)})

# Door block
if "DOOR" not in doc.blocks:
    blk = doc.blocks.new("DOOR")
    r = 20
    blk.add_arc((0,0),r,0,90,dxfattribs={"layer":"A-DOOR","lineweight":lw(0.25)})
    blk.add_line((0,0),(0,r),dxfattribs={"layer":"A-DOOR","lineweight":lw(0.25)})
    blk.add_line((0,0),(r,0),dxfattribs={"layer":"A-DOOR","lineweight":lw(0.25)})

for i,dd in enumerate(doors):
    x,y = dd.get("x",i*500+min_x*10)/10, dd.get("y",min_y*10+200)/10
    if "w" in dd: w = dd["w"]/10
    else: w = 80
    ref = msp.add_blockref("DOOR",(x,y),dxfattribs={"layer":"A-DOOR","lineweight":lw(0.25)})
    if w>0:
        ref.set_dxf_attrib("xscale",w/20)
        ref.set_dxf_attrib("yscale",w/20)

# Windows on outer walls
for w in walls:
    t = w.get("thickness",240 if w["t"]=="\u5916" else 150)/10
    x1,y1,x2,y2 = w["x1"]/10,w["y1"]/10,w["x2"]/10,w["y2"]/10
    dx,dy=x2-x1,y2-y1; ln=math.hypot(dx,dy)
    if ln>50 and w["t"]=="\u5916":
        mx,my=(x1+x2)/2,(y1+y2)/2
        nx,ny=-dy/ln*t/2,dx/ln*t/2
        msp.add_line((mx-5,my-5),(mx+5,my+5),dxfattribs={"layer":"A-WINDOW","lineweight":lw(0.18)})

# Rooms
for r in rooms:
    x,y,rw,rd = r["x"]/10,r["y"]/10,r["w"]/10,r["d"]/10
    msp.add_lwpolyline([(x,y),(x+rw,y),(x+rw,y+rd),(x,y+rd),(x,y)],
        dxfattribs={"layer":"A-ROOM","lineweight":lw(0.09)})

# Furniture
for fi in furniture:
    x,y,fw,fd=fi["x"]/10,fi["y"]/10,fi["w"]/10,fi["d"]/10
    col=fi.get("c","#A0A0A0")
    try: ci=colors.rgb2int((int(col[1:3],16),int(col[3:5],16),int(col[5:7],16)))
    except: ci=5
    msp.add_lwpolyline([(x,y),(x+fw,y),(x+fw,y+fd),(x,y+fd),(x,y)],
        dxfattribs={"layer":"A-FURN","color":ci,"lineweight":lw(0.13)})
    msp.add_text(fi["n"],height=30,
        dxfattribs={"layer":"A-TEXT","color":7}
    ).set_placement((x+fw/2,y+fd/2),align=TextEntityAlignment.CENTER)

# Proper dimensions
off = 50
msp.add_line((min_x, max_y+off-10),(max_x, max_y+off-10),dxfattribs={"layer":"A-DIM","color":3,"lineweight":25})
msp.add_line((min_x, max_y),(min_x, max_y+off),dxfattribs={"layer":"A-DIM","color":3,"lineweight":25})
msp.add_line((max_x, max_y),(max_x, max_y+off),dxfattribs={"layer":"A-DIM","color":3,"lineweight":25})
dt=str(int((max_x-min_x)*10))+"mm"
msp.add_text(dt,height=30,dxfattribs={"layer":"A-DIM","color":3}).set_placement(((min_x+max_x)/2,max_y+off-15),align=TextEntityAlignment.CENTER)
msp.add_line((max_x+off-10, min_y),(max_x+off-10, max_y),dxfattribs={"layer":"A-DIM","color":3,"lineweight":25})
msp.add_line((max_x, min_y),(max_x+off, min_y),dxfattribs={"layer":"A-DIM","color":3,"lineweight":25})
msp.add_line((max_x, max_y),(max_x+off, max_y),dxfattribs={"layer":"A-DIM","color":3,"lineweight":25})
dtv=str(int((max_y-min_y)*10))+"mm"
msp.add_text(dtv,height=30,dxfattribs={"layer":"A-DIM","color":3}).set_placement((max_x+off-15,(min_y+max_y)/2),align=TextEntityAlignment.CENTER)

# Title block
tb_x,tb_y = max_x+100,min_y-300
tb_w,tb_h = 1200/10,600/10
msp.add_lwpolyline([(tb_x,tb_y),(tb_x+tb_w,tb_y),(tb_x+tb_w,tb_y+tb_h),
    (tb_x,tb_y+tb_h),(tb_x,tb_y)],dxfattribs={"layer":"A-TITLE","lineweight":lw(0.50)})
items=[("\u9879\u76ee","\u5ca9\u6cca\u6e21\u6c34\u7535\u7ad9"),("\u56fe\u540d","\u5ba4\u5185\u5e73\u9762\u56fe"),
       ("\u6bd4\u4f8b","1:100"),("\u56fe\u53f7","JZ-01"),("\u65e5\u671f","2026-05")]
for i,(lb,v) in enumerate(items):
    yp=tb_y+tb_h-100/10-i*100/10
    msp.add_line((tb_x,yp),(tb_x+tb_w,yp),dxfattribs={"layer":"A-TITLE","lineweight":lw(0.13)})
    msp.add_text(lb+": "+v,height=35,dxfattribs={"layer":"A-TITLE","color":7}
    ).set_placement((tb_x+50,yp-15),align=TextEntityAlignment.LEFT)

# Water level (SL 73)
wl_y=max_y+100/10
msp.add_line((min_x,wl_y),(max_x,wl_y),dxfattribs={"layer":"H-WATER-LINE","lineweight":lw(0.25)})
msp.add_text("WL 185.50m",height=30,dxfattribs={"layer":"H-ANNO","color":5}
).set_placement((max_x,wl_y+10),align=TextEntityAlignment.LEFT)

# Save
out="output/professional/floor_plan_ultimate.dxf"
doc.saveas(out)
print("OK: %s (%d layers, %d entities)" % (out,len(doc.layers),len(msp)))
