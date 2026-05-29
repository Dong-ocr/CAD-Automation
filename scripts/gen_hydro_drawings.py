"""Hydro Dam Engineering Drawing Set - DXF Plan/Elevation/Section"""
import os, math, ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment

os.makedirs("output/hydro", exist_ok=True)

def lw(v): return int(v*100)

# Dam params
H = 45.0; CW = 5.0; BW = 35.0; DL = 120.0
EL_CREST = 185.5; EL_BASE = 140.5; NWL = 183.0
UP_S = 0.05; DOWN_S = 0.78
SW_W = 24; SW_N = 3
SCALE = 150  # 1:150

LAYERS = {
    "DAM-OUTLINE":(1,"CONTINUOUS",0.70,"Dam body"),
    "DAM-CREST":(6,"CONTINUOUS",0.50,"Crest"),
    "DIM":(3,"CONTINUOUS",0.09,"Dimension"),
    "TEXT":(7,"CONTINUOUS",0.09,"Text"),
    "WATER":(5,"CONTINUOUS",0.25,"Water"),
    "HATCH":(8,"CONTINUOUS",0.09,"Hatch"),
    "GRID":(4,"CENTER",0.09,"Grid"),
    "TITLE":(7,"CONTINUOUS",0.50,"Title"),
    "ROCK":(4,"CONTINUOUS",0.13,"Rock"),
    "REBAR":(6,"CONTINUOUS",0.18,"Rebar"),
    "GATE":(2,"CONTINUOUS",0.25,"Gate"),
    "PIPE":(4,"DASHED",0.18,"Pipe"),
    "ANNO":(4,"CONTINUOUS",0.09,"Annotation"),
}

def setup_doc():
    doc = ezdxf.new(dxfversion="R2010", units=units.MM)
    msp = doc.modelspace()
    for ln,(ci,lt,lv,_) in LAYERS.items():
        try:
            l = doc.layers.add(ln); l.color=ci
            l.line_type=lt if lt in doc.linetypes else "CONTINUOUS"; l.lineweight=lw(lv)
        except: pass
    for lt,pat in [("DASHED","0.5,-0.25"),("CENTER","1.0,-0.25,0.25,-0.25")]:
        if lt not in doc.linetypes:
            try: doc.linetypes.add(lt,pattern=pat)
            except: pass
    return doc, msp

# === SHEET 1: DAM SECTION ===
doc1, msp1 = setup_doc()
x0, y0 = 50, 50

# Dam profile
pts = [
    (x0, y0), (x0+BW*10, y0),
    (x0+BW*10 - H*10*DOWN_S, y0+H*10),
    (x0+CW*10 + H*10*UP_S, y0+H*10),
    (x0+H*10*UP_S, y0+H*10*0.3),
    (x0, y0),
]
msp1.add_lwpolyline(pts, dxfattribs={"layer":"DAM-OUTLINE","lineweight":lw(0.70)})

# Crest
msp1.add_line((x0+CW*10+H*10*UP_S, y0+H*10), (x0+BW*10-H*10*DOWN_S, y0+H*10),
    dxfattribs={"layer":"DAM-CREST","lineweight":lw(0.50)})

# Water level
wl_h = (NWL-EL_BASE)/(EL_CREST-EL_BASE)*H*10
msp1.add_line((x0-30, y0+wl_h), (x0, y0+wl_h), dxfattribs={"layer":"WATER","lineweight":lw(0.25)})
msp1.add_text("NWL "+str(NWL)+"m", height=20, dxfattribs={"layer":"WATER","color":5}
).set_placement((x0-35, y0+wl_h+5), align=TextEntityAlignment.RIGHT)

# Rock foundation
for rx in range(int(x0-20), int(x0+BW*10+20), 30):
    msp1.add_line((rx, y0-20), (rx+15, y0-10), dxfattribs={"layer":"ROCK","lineweight":lw(0.09)})
    msp1.add_line((rx, y0-30), (rx+15, y0-20), dxfattribs={"layer":"ROCK","lineweight":lw(0.09)})
msp1.add_line((x0-30, y0), (x0+BW*10+30, y0), dxfattribs={"layer":"ROCK","lineweight":lw(0.25)})

# Foundation line
msp1.add_line((x0, y0), (x0, y0-40), dxfattribs={"layer":"DIM","color":3,"lineweight":lw(0.09)})
msp1.add_text("EL {:.2f}m".format(EL_BASE), height=15, dxfattribs={"layer":"TEXT","color":7}
).set_placement((x0-20, y0-50), align=TextEntityAlignment.CENTER)
msp1.add_text("EL {:.2f}m".format(EL_CREST), height=15, dxfattribs={"layer":"TEXT","color":7}
).set_placement((x0+BW*10-H*10*DOWN_S+20, y0+H*10+5), align=TextEntityAlignment.LEFT)

# Dimensions
# Height
msp1.add_line((x0+BW*10+30, y0), (x0+BW*10+30, y0+H*10), dxfattribs={"layer":"DIM","color":3,"lineweight":lw(0.09)})
msp1.add_text("H={:.1f}m".format(H), height=20, dxfattribs={"layer":"DIM","color":3}
).set_placement((x0+BW*10+50, y0+H*5), align=TextEntityAlignment.CENTER)
# Width
msp1.add_line((x0, y0-60), (x0+BW*10, y0-60), dxfattribs={"layer":"DIM","color":3,"lineweight":lw(0.09)})
msp1.add_text("B={:.1f}m".format(BW), height=20, dxfattribs={"layer":"DIM","color":3}
).set_placement((x0+BW*5, y0-75), align=TextEntityAlignment.CENTER)

# Title
msp1.add_text("坝体标准剖面图", height=35, dxfattribs={"layer":"TEXT","color":7}
).set_placement((x0+BW*5, y0+H*10+40), align=TextEntityAlignment.CENTER)
msp1.add_text("混凝土重力坝  1:"+str(SCALE), height=20, dxfattribs={"layer":"TEXT","color":7}
).set_placement((x0+BW*5, y0+H*10+20), align=TextEntityAlignment.CENTER)

doc1.saveas("output/hydro/dam_section_pro.dxf")
print("Sheet 1: Dam Section (%d layers, %d entities)" % (len(doc1.layers), len(msp1)))

# === SHEET 2: PLAN VIEW ===
doc2, msp2 = setup_doc()
x0, y0 = 50, 100

# Dam footprint
msp2.add_lwpolyline([
    (x0, y0), (x0+BW*10, y0), (x0+BW*10+20, y0+DL*10),
    (x0+20, y0+DL*10), (x0, y0)
], dxfattribs={"layer":"DAM-OUTLINE","lineweight":lw(0.50)})

# Spillway
sw_w = SW_W*10
sw_cx = x0 + BW*5
for i in range(SW_N):
    gx = sw_cx + (i - (SW_N-1)/2) * sw_w/SW_N
    msp2.add_lwpolyline([
        (gx-sw_w/SW_N/2+5, y0+20), (gx+sw_w/SW_N/2-5, y0+20),
        (gx+sw_w/SW_N/2-5, y0+DL*10-20), (gx-sw_w/SW_N/2+5, y0+DL*10-20), (gx-sw_w/SW_N/2+5, y0+20)
    ], dxfattribs={"layer":"GATE","lineweight":lw(0.25)})
    # Gate label
    msp2.add_text("闸门", height=15, dxfattribs={"layer":"GATE","color":2}
    ).set_placement((gx, y0+DL*5), align=TextEntityAlignment.CENTER)

# Crest line (upstream edge)
msp2.add_line((x0+20, y0+DL*10), (x0+BW*10+20, y0+DL*10),
    dxfattribs={"layer":"DAM-CREST","lineweight":lw(0.35)})

# Access road
msp2.add_line((x0+BW*10+30, y0+DL*10), (x0+BW*10+80, y0+DL*10+50),
    dxfattribs={"layer":"DIM","color":3,"lineweight":lw(0.13)})
msp2.add_text("上坝公路", height=15, dxfattribs={"layer":"TEXT","color":7}
).set_placement((x0+BW*10+60, y0+DL*10+30), align=TextEntityAlignment.CENTER)

# Dimensions
msp2.add_line((x0, y0-30), (x0+BW*10, y0-30), dxfattribs={"layer":"DIM","color":3,"lineweight":lw(0.09)})
msp2.add_text("B={:.1f}m".format(BW), height=20, dxfattribs={"layer":"DIM","color":3}
).set_placement((x0+BW*5, y0-45), align=TextEntityAlignment.CENTER)
msp2.add_line((x0-30, y0), (x0-30, y0+DL*10), dxfattribs={"layer":"DIM","color":3,"lineweight":lw(0.09)})
msp2.add_text("L={:.1f}m".format(DL), height=20, dxfattribs={"layer":"DIM","color":3}
).set_placement((x0-50, y0+DL*5), align=TextEntityAlignment.CENTER)

# Title
msp2.add_text("坝顶平面布置图", height=35, dxfattribs={"layer":"TEXT","color":7}
).set_placement((x0+BW*5, y0+DL*10+40), align=TextEntityAlignment.CENTER)
msp2.add_text("1:"+str(SCALE), height=20, dxfattribs={"layer":"TEXT","color":7}
).set_placement((x0+BW*5, y0+DL*10+20), align=TextEntityAlignment.CENTER)

doc2.saveas("output/hydro/dam_plan.dxf")
print("Sheet 2: Dam Plan (%d layers, %d entities)" % (len(doc2.layers), len(msp2)))

# === SHEET 3: DOWNSTREAM ELEVATION ===
doc3, msp3 = setup_doc()
x0, y0 = 50, 50

# Dam face
msp3.add_lwpolyline([
    (x0, y0), (x0+DL*10, y0), (x0+DL*10, y0+H*10),
    (x0, y0+H*10), (x0, y0)
], dxfattribs={"layer":"DAM-OUTLINE","lineweight":lw(0.50)})

# Spillway openings
sw_w = SW_W*10
sw_cx = x0 + DL*5
for i in range(SW_N):
    gx = sw_cx + (i-(SW_N-1)/2) * sw_w/SW_N
    gw = sw_w/SW_N * 0.7
    gh = H*10*0.2
    msp3.add_lwpolyline([
        (gx-gw/2, y0+5), (gx+gw/2, y0+5), (gx+gw/2, y0+gh),
        (gx-gw/2, y0+gh), (gx-gw/2, y0+5)
    ], dxfattribs={"layer":"GATE","lineweight":lw(0.25)})

# Crest
msp3.add_line((x0, y0+H*10), (x0+DL*10, y0+H*10),
    dxfattribs={"layer":"DAM-CREST","lineweight":lw(0.50)})

# Penstock outlets
for i in range(3):
    px = x0 + DL*10 * (0.2 + i*0.3)
    msp3.add_circle((px, y0+H*10*0.1), 15,
        dxfattribs={"layer":"PIPE","lineweight":lw(0.18)})
    msp3.add_text("DN"+str(3500), height=12, dxfattribs={"layer":"PIPE","color":4}
    ).set_placement((px, y0+H*10*0.1-25), align=TextEntityAlignment.CENTER)

# Gallery
msp3.add_line((x0+DL*10*0.15, y0+H*10*0.3), (x0+DL*10*0.85, y0+H*10*0.3),
    dxfattribs={"layer":"HATCH","lineweight":lw(0.13)})
msp3.add_text("排水廊道", height=15, dxfattribs={"layer":"TEXT","color":7}
).set_placement((x0+DL*5, y0+H*10*0.3+10), align=TextEntityAlignment.CENTER)

# Title
msp3.add_text("下游立视图", height=35, dxfattribs={"layer":"TEXT","color":7}
).set_placement((x0+DL*5, y0+H*10+40), align=TextEntityAlignment.CENTER)
msp3.add_text("1:"+str(SCALE), height=20, dxfattribs={"layer":"TEXT","color":7}
).set_placement((x0+DL*5, y0+H*10+20), align=TextEntityAlignment.CENTER)

# Dimensions
msp3.add_line((x0+DL*10+20, y0), (x0+DL*10+20, y0+H*10),
    dxfattribs={"layer":"DIM","color":3,"lineweight":lw(0.09)})
msp3.add_text("H={:.1f}m".format(H), height=20, dxfattribs={"layer":"DIM","color":3}
).set_placement((x0+DL*10+40, y0+H*5), align=TextEntityAlignment.CENTER)

doc3.saveas("output/hydro/dam_elevation.dxf")
print("Sheet 3: Dam Elevation (%d layers, %d entities)" % (len(doc3.layers), len(msp3)))

# === SHEET INDEX ===
print("\\n=== Drawing Set Complete ===")
for f in ["dam_section_pro.dxf", "dam_plan.dxf", "dam_elevation.dxf"]:
    fp = os.path.join("output/hydro", f)
    if os.path.exists(fp):
        print(f"  {f}: {os.path.getsize(fp)//1024}KB")
