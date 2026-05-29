#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CAD block library generator - reusable blocks for DXF"""
import os, math, ezdxf
from ezdxf import units

OUT = "cad_blocks"
os.makedirs(OUT, exist_ok=True)

BLOCK_WIDTH = 200  # 200mm as base unit

def make_block(name, desc, draw_fn):
    doc = ezdxf.new(dxfversion="R2010", units=units.MM)
    msp = doc.modelspace()
    if name not in doc.blocks:
        blk = doc.blocks.new(name)
        draw_fn(blk, doc)
    doc.saveas(os.path.join(OUT, f"{name}.dxf"))
    print(f"  {name}.dxf - {desc}")
    return name

# ==== Block definitions ====
def door_single(blk, doc):
    r = BLOCK_WIDTH
    lay = {"layer":"0","lineweight":25}
    blk.add_arc((0,0),r,0,90,dxfattribs=lay)
    blk.add_line((0,0),(0,r),dxfattribs=lay)
    blk.add_line((0,0),(r,0),dxfattribs=lay)

def door_double(blk, doc):
    r = BLOCK_WIDTH
    lay = {"layer":"0","lineweight":25}
    blk.add_arc((0,0),r,0,90,dxfattribs=lay)
    blk.add_arc((r,0),r,90,180,dxfattribs=lay)
    blk.add_line((0,0),(0,r),dxfattribs=lay)
    blk.add_line((r,0),(r,r),dxfattribs=lay)
    blk.add_line((0,0),(r,0),dxfattribs=lay)

def window(blk, doc):
    lay = {"layer":"0","lineweight":25}
    blk.add_line((0,0),(BLOCK_WIDTH,0),dxfattribs=lay)
    blk.add_line((0,30),(BLOCK_WIDTH,30),dxfattribs=lay)
    blk.add_line((0,0),(0,30),dxfattribs=lay)
    blk.add_line((BLOCK_WIDTH,0),(BLOCK_WIDTH,30),dxfattribs=lay)
    blk.add_line((BLOCK_WIDTH/3,0),(BLOCK_WIDTH/3,30),dxfattribs={"layer":"0","lineweight":13})
    blk.add_line((BLOCK_WIDTH*2/3,0),(BLOCK_WIDTH*2/3,30),dxfattribs={"layer":"0","lineweight":13})

def staircase(blk, doc):
    lay = {"layer":"0","lineweight":13}
    for i in range(10):
        y = i * 25
        blk.add_line((0,y),(BLOCK_WIDTH-25,y),dxfattribs=lay)
    blk.add_line((BLOCK_WIDTH-25,0),(BLOCK_WIDTH-25,250),dxfattribs=lay)
    # Arrow
    blk.add_line((BLOCK_WIDTH-50,125),(BLOCK_WIDTH-25,125),dxfattribs=lay)
    blk.add_line((BLOCK_WIDTH-50,115),(BLOCK_WIDTH-50,135),dxfattribs=lay)

def column(blk, doc):
    lay = {"layer":"0","lineweight":35}
    s = BLOCK_WIDTH/2
    blk.add_lwpolyline([(-s,-s),(s,-s),(s,s),(-s,s),(-s,-s)],dxfattribs=lay)
    blk.add_lwpolyline([(-s*0.7,-s*0.7),(s*0.7,-s*0.7),(s*0.7,s*0.7),(-s*0.7,s*0.7),(-s*0.7,-s*0.7)],
        dxfattribs={"layer":"0","lineweight":13})

def toilet(blk, doc):
    r = BLOCK_WIDTH*0.4; gap = 30
    blk.add_circle((0,0),r,dxfattribs={"layer":"0","lineweight":13})
    blk.add_line((0,-r),(0,-r-gap),dxfattribs={"layer":"0","lineweight":13})
    blk.add_line((-r*0.6,-r-gap),(r*0.6,-r-gap),dxfattribs={"layer":"0","lineweight":13})

def sink(blk, doc):
    w = BLOCK_WIDTH*0.8; d = BLOCK_WIDTH*0.5; r = BLOCK_WIDTH*0.15
    blk.add_lwpolyline([(0,0),(w,0),(w,d),(0,d),(0,0)],dxfattribs={"layer":"0","lineweight":13})
    blk.add_circle((w/2,d/2),r,dxfattribs={"layer":"0","lineweight":13})
    blk.add_circle((w/2-w*0.25,d/2),r,dxfattribs={"layer":"0","lineweight":13})
    blk.add_line((w/2-w*0.1,d/2-r-10),(w/2+w*0.1,d/2+r+10),dxfattribs={"layer":"0","lineweight":13})

def bed_double(blk, doc):
    w = BLOCK_WIDTH*2; d = BLOCK_WIDTH*1.5
    blk.add_lwpolyline([(0,0),(w,0),(w,d),(0,d),(0,0)],dxfattribs={"layer":"0","lineweight":13})
    # Pillow
    blk.add_lwpolyline([(10,d-50),(w-10,d-50),(w-10,d-10),(10,d-10),(10,d-50)],
        dxfattribs={"layer":"0","lineweight":13})

def desk(blk, doc):
    w = BLOCK_WIDTH*1.2; d = BLOCK_WIDTH*0.6
    blk.add_lwpolyline([(0,0),(w,0),(w,d),(0,d),(0,0)],dxfattribs={"layer":"0","lineweight":13})
    blk.add_line((0,d/3),(w,d/3),dxfattribs={"layer":"0","lineweight":9})

def chair(blk, doc):
    s = BLOCK_WIDTH*0.4
    blk.add_lwpolyline([(0,0),(s,0),(s,s),(0,s),(0,0)],dxfattribs={"layer":"0","lineweight":13})
    blk.add_circle((s/2,s/2),s*0.2,dxfattribs={"layer":"0","lineweight":13})

def table_round(blk, doc):
    r = BLOCK_WIDTH*0.6
    blk.add_circle((0,0),r,dxfattribs={"layer":"0","lineweight":13})
    blk.add_circle((0,0),r*0.08,dxfattribs={"layer":"0","lineweight":13})

# === SL 73 hydraulic symbols ===
def dam_section(blk, doc):
    pts = [(0,0),(300,0),(200,150),(100,150),(0,0)]
    blk.add_lwpolyline(pts,dxfattribs={"layer":"0","lineweight":35})
    # Upstream face
    blk.add_line((0,0),(0,-50),dxfattribs={"layer":"0","lineweight":25})

def sluice_gate(blk, doc):
    w,h = BLOCK_WIDTH*2, BLOCK_WIDTH
    blk.add_lwpolyline([(0,0),(w,0),(w,h),(0,h),(0,0)],dxfattribs={"layer":"0","lineweight":35})
    blk.add_line((w*0.1,0),(w*0.1,h),dxfattribs={"layer":"0","lineweight":25})
    blk.add_line((w*0.9,0),(w*0.9,h),dxfattribs={"layer":"0","lineweight":25})
    # Gate leaf
    blk.add_line((w*0.15,h*0.3),(w*0.85,h*0.3),dxfattribs={"layer":"0","lineweight":25})
    blk.add_line((w*0.15,h*0.7),(w*0.85,h*0.7),dxfattribs={"layer":"0","lineweight":25})

def pipe_cross(blk, doc):
    r = BLOCK_WIDTH*0.3
    blk.add_circle((0,0),r,dxfattribs={"layer":"0","lineweight":13})
    blk.add_line((-r*1.5,0),(r*1.5,0),dxfattribs={"layer":"0","lineweight":13})
    blk.add_line((0,-r*1.5),(0,r*1.5),dxfattribs={"layer":"0","lineweight":13})

def valve(blk, doc):
    s = BLOCK_WIDTH*0.4
    blk.add_line((-s,0),(s,0),dxfattribs={"layer":"0","lineweight":13})
    blk.add_line((0,-s),(0,s),dxfattribs={"layer":"0","lineweight":13})
    blk.add_circle((0,0),s*0.3,dxfattribs={"layer":"0","lineweight":13})

def pump(blk, doc):
    r = BLOCK_WIDTH*0.35
    blk.add_circle((0,0),r,dxfattribs={"layer":"0","lineweight":25})
    blk.add_line((0,0),(0,r*0.7),dxfattribs={"layer":"0","lineweight":13})
    blk.add_line((-r*0.5,0),(r*0.5,0),dxfattribs={"layer":"0","lineweight":13})
    blk.add_text("P",height=r*0.6,dxfattribs={"layer":"0"}).set_placement((0,0))

# === Generate all blocks ===
blocks = [
    ("DOOR-SINGLE", "Single door", door_single),
    ("DOOR-DOUBLE", "Double door", door_double),
    ("WINDOW", "Window", window),
    ("STAIRCASE", "Staircase", staircase),
    ("COLUMN", "Column", column),
    ("TOILET", "Toilet", toilet),
    ("SINK", "Sink", sink),
    ("BED-DOUBLE", "Double bed", bed_double),
    ("DESK", "Desk", desk),
    ("CHAIR", "Chair", chair),
    ("TABLE-ROUND", "Round table", table_round),
    ("DAM-SECTION", "Dam section (SL 73)", dam_section),
    ("SLUICE-GATE", "Sluice gate (SL 73)", sluice_gate),
    ("PIPE-CROSS", "Pipe crossing (SL 73)", pipe_cross),
    ("VALVE", "Valve (SL 73)", valve),
    ("PUMP", "Pump (SL 73)", pump),
]

print("Generating CAD block library...")
for name, desc, fn in blocks:
    make_block(name, desc, fn)

# Generate block index
with open(os.path.join(OUT, "block_index.json"), "w", encoding="utf-8") as f:
    import json
    idx = [{"name":n,"desc":d,"file":f"{n}.dxf","cat":"sl73" if "SL 73" in d else "aec"} for n,d,_ in blocks]
    json.dump(idx, f, ensure_ascii=False, indent=2)

print(f"\nDone: {len(blocks)} blocks in {OUT}/")
