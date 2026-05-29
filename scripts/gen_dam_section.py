"""Dam/Hydraulic professional section view - SL 73 standard"""
import json, math, os, ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment

os.makedirs("output/professional", exist_ok=True)
d = json.load(open("demo_project.json","r",encoding="utf-8"))
walls = d["w"]

LAYERS = {
    "S-DAM-BODY":(1,"CONTINUOUS",0.70,"Dam body"),
    "S-DAM-CREST":(6,"CONTINUOUS",0.50,"Crest"),
    "S-REBAR":(6,"CONTINUOUS",0.18,"Rebar"),
    "S-FOUNDATION":(8,"DASHED",0.25,"Foundation"),
    "S-WATER":(5,"CONTINUOUS",0.25,"Water level"),
    "S-GROUT":(4,"DASHED",0.18,"Grout curtain"),
    "S-DRAIN":(4,"DASHED",0.13,"Drain hole"),
    "S-DIM":(3,"CONTINUOUS",0.09,"Dimension"),
    "S-TEXT":(7,"CONTINUOUS",0.09,"Text/Anno"),
    "S-GRID":(4,"CENTER",0.09,"Grid"),
    "S-TITLE":(7,"CONTINUOUS",0.50,"Title block"),
    "S-HATCH":(8,"CONTINUOUS",0.09,"Hatch"),
    "S-ROCK":(4,"CONTINUOUS",0.13,"Rock foundation"),
}
def lw(v): return int(v*100)

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

# === Dam Section Parameters (Gravity Dam type) ===
SCALE = 100  # mm per unit
H = 4500 / SCALE       # Dam height 45m
W_CROWN = 500 / SCALE   # Crown width 5m
W_BASE = 3500 / SCALE   # Base width 35m (varies with height)
UP_SLOPE = 0.05        # Upstream slope
DOWN_SLOPE = 0.78       # Downstream slope (concrete gravity dam typical)
EL_CREST = 185.5        # Crest elevation
EL_BASE = 140.0         # Foundation elevation
NWL = 183.0             # Normal water level

x0 = 200  # Left margin

# === Dam Body Outline ===
up_x = x0 + W_CROWN
down_x = up_x + (H - 0) * DOWN_SLOPE

pts_dam = [
    (x0, 0),                          # Heel
    (x0 + W_BASE, 0),                 # Toe
    (down_x, H),                       # Downstream crest
    (up_x, H),                         # Upstream crest
    (up_x - (H) * UP_SLOPE, H * 0.3), # Upstream slope point
    (x0, 0),                          # Close
]
msp.add_lwpolyline(pts_dam, dxfattribs={"layer":"S-DAM-BODY","lineweight":lw(0.70)})

# === Crest detail ===
msp.add_line((x0, H), (up_x, H), dxfattribs={"layer":"S-DAM-CREST","lineweight":lw(0.50)})
msp.add_line((x0, H), (x0, H+50/SCALE), dxfattribs={"layer":"S-DAM-CREST","lineweight":lw(0.35)})
msp.add_line((up_x, H), (up_x, H+50/SCALE), dxfattribs={"layer":"S-DAM-CREST","lineweight":lw(0.35)})

# === Foundation Rock ===
rock_pts = [
    (x0-100, -50/SCALE), (x0+W_BASE+200, -50/SCALE),
    (x0+W_BASE+200, -100/SCALE), (x0-100, -100/SCALE), (x0-100, -50/SCALE),
]
msp.add_lwpolyline(rock_pts, dxfattribs={"layer":"S-ROCK","lineweight":lw(0.13)})
# Rock hatch pattern
for rx in range(int(x0-80), int(x0+W_BASE+180), int(30)):
    msp.add_line((rx, -55/SCALE), (rx+15, -45/SCALE), dxfattribs={"layer":"S-ROCK","lineweight":lw(0.09)})
    msp.add_line((rx, -65/SCALE), (rx+15, -55/SCALE), dxfattribs={"layer":"S-ROCK","lineweight":lw(0.09)})
    msp.add_line((rx, -70/SCALE), (rx+15, -60/SCALE), dxfattribs={"layer":"S-ROCK","lineweight":lw(0.09)})

# === Foundation Line ===
msp.add_line((x0-100, 0), (x0+W_BASE+200, 0),
    dxfattribs={"layer":"S-FOUNDATION","lineweight":lw(0.25)})

# === Water Level ===
wl_y = (NWL - EL_BASE) / (EL_CREST - EL_BASE) * H
msp.add_line((x0-200, wl_y), (x0, wl_y),
    dxfattribs={"layer":"S-WATER","lineweight":lw(0.25)})
# Water wave
for wx in range(int(x0-200), int(x0), int(20)):
    msp.add_line((wx, wl_y-2), (wx+10, wl_y+2),
        dxfattribs={"layer":"S-WATER","lineweight":lw(0.09)})
    msp.add_line((wx+10, wl_y+2), (wx+20, wl_y-2),
        dxfattribs={"layer":"S-WATER","lineweight":lw(0.09)})

# === Grout Curtain ===
gx = x0 + 100/SCALE
msp.add_line((gx, -30/SCALE), (gx, -H*0.3),
    dxfattribs={"layer":"S-GROUT","lineweight":lw(0.18)})
msp.add_line((gx-5, -45/SCALE), (gx+5, -35/SCALE),
    dxfattribs={"layer":"S-GROUT","lineweight":lw(0.13)})
msp.add_line((gx-5, -H*0.3+5), (gx+5, -H*0.3-5),
    dxfattribs={"layer":"S-GROUT","lineweight":lw(0.13)})

# === Drain Holes ===
for i, dy in enumerate([H*0.2, H*0.4, H*0.6]):
    msp.add_circle((x0+200/SCALE, dy), 10,
        dxfattribs={"layer":"S-DRAIN","lineweight":lw(0.13)})
    msp.add_line((x0+200/SCALE, dy+15), (x0+200/SCALE, 0),
        dxfattribs={"layer":"S-DRAIN","lineweight":lw(0.09)})

# === Rebar indication ===
for rx in range(int(x0+100), int(x0+W_BASE-100), int(200)):
    msp.add_line((rx, 10), (rx+20, 10),
        dxfattribs={"layer":"S-REBAR","lineweight":lw(0.18)})
    msp.add_circle((rx+10, 10), 3,
        dxfattribs={"layer":"S-REBAR","lineweight":lw(0.13)})

# === Dimensions ===
# Height dim
dim_x = x0 + W_BASE + 100
msp.add_line((dim_x, 0), (dim_x, H), dxfattribs={"layer":"S-DIM","color":3,"lineweight":lw(0.09)})
msp.add_line((x0+W_BASE, 0), (dim_x, 0), dxfattribs={"layer":"S-DIM","color":3,"lineweight":lw(0.09)})
msp.add_line((x0+W_BASE, H), (dim_x, H), dxfattribs={"layer":"S-DIM","color":3,"lineweight":lw(0.09)})
msp.add_text("H="+"{:.1f}m".format(H*SCALE/1000), height=25,
    dxfattribs={"layer":"S-DIM","color":3}
).set_placement((dim_x+30, H/2), align=TextEntityAlignment.CENTER)

# Width dim
dim_y = -80/SCALE
msp.add_line((x0, dim_y), (x0+W_BASE, dim_y),
    dxfattribs={"layer":"S-DIM","color":3,"lineweight":lw(0.09)})
msp.add_line((x0, dim_y-10), (x0, dim_y+10),
    dxfattribs={"layer":"S-DIM","color":3,"lineweight":lw(0.09)})
msp.add_line((x0+W_BASE, dim_y-10), (x0+W_BASE, dim_y+10),
    dxfattribs={"layer":"S-DIM","color":3,"lineweight":lw(0.09)})
msp.add_text("B={:.1f}m".format(W_BASE*SCALE/1000), height=25,
    dxfattribs={"layer":"S-DIM","color":3}
).set_placement((x0+W_BASE/2, dim_y-15), align=TextEntityAlignment.CENTER)

# === Elevation Labels ===
msp.add_text("EL {:.2f}m".format(EL_CREST), height=20,
    dxfattribs={"layer":"S-TEXT","color":7}
).set_placement((up_x+30, H+20), align=TextEntityAlignment.LEFT)
msp.add_text("EL {:.2f}m".format(EL_BASE), height=20,
    dxfattribs={"layer":"S-TEXT","color":7}
).set_placement((x0+W_BASE+30, -30), align=TextEntityAlignment.LEFT)
msp.add_text("NWL {:.2f}m".format(NWL), height=20,
    dxfattribs={"layer":"S-WATER","color":5}
).set_placement((x0-180, wl_y+10), align=TextEntityAlignment.RIGHT)

# === Section title ===
title_x = (x0 + x0 + W_BASE) / 2
msp.add_text("坝体标准剖面图  1:"+str(SCALE), height=35,
    dxfattribs={"layer":"S-TEXT","color":7}
).set_placement((title_x, H+100), align=TextEntityAlignment.CENTER)
msp.add_text("岩泊渡水电站 - 混凝土重力坝", height=25,
    dxfattribs={"layer":"S-TEXT","color":7}
).set_placement((title_x, H+80), align=TextEntityAlignment.CENTER)

# === Title block ===
tb_x = x0 + W_BASE + 200
tb_y = -80
msp.add_lwpolyline([(tb_x,tb_y),(tb_x+200,tb_y),(tb_x+200,tb_y+120),(tb_x,tb_y+120),(tb_x,tb_y)],
    dxfattribs={"layer":"S-TITLE","lineweight":lw(0.35)})
items=[("坝型","重力坝"),("坝高","{:.1f}m".format(H*SCALE/1000)),("坝顶宽","{}m".format(int(W_CROWN*SCALE/1000)))]
for i,(lb,v) in enumerate(items):
    yp=tb_y+120-20-i*35
    msp.add_line((tb_x,yp),(tb_x+200,yp),dxfattribs={"layer":"S-TITLE","lineweight":lw(0.13)})
    msp.add_text(lb+": "+v,height=15,dxfattribs={"layer":"S-TITLE","color":7}
    ).set_placement((tb_x+5,yp-10),align=TextEntityAlignment.LEFT)

# Save
out="output/professional/dam_section.dxf"
doc.saveas(out)
print("OK: %s (%d entities)" % (out, len(msp)))
print("Dam: H=%.1fm, B=%.1fm, NWL=%.2f" % (H*SCALE/1000, W_BASE*SCALE/1000, NWL))
