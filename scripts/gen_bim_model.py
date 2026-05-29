import json, os, sys, math

FC_BIN = r"E:\CAD自动化制图\FreeCAD\FreeCAD_1.1.1-Windows-x86_64-py311\bin"
for p in [os.path.join(FC_BIN, "..", "Lib"), os.path.join(FC_BIN, "..", "Mod")]:
    if p not in sys.path: sys.path.append(p)

import FreeCAD, Part, Arch, Draft, Mesh
from FreeCAD import Base, Vector

DATA = json.load(open("demo_project.json","r",encoding="utf-8"))
walls, rooms, furniture = DATA["w"], DATA["r"], DATA["f"]

doc = FreeCAD.newDocument("YanboduBIM")
doc.Label = "岩泊渡水电站 - BIM模型"
os.makedirs("output/professional", exist_ok=True)

ax = [w["x1"] for w in walls] + [w["x2"] for w in walls]
ay = [w["y1"] for w in walls] + [w["y2"] for w in walls]

# Site
site = doc.addObject("Part::Box","Site")
site.Label="场地"
site.Length=(max(ax)-min(ax))+2000; site.Width=(max(ay)-min(ay))+2000; site.Height=300
site.Placement=Base.Placement(Vector(min(ax)-1000,min(ay)-1000,-300),Base.Rotation())

# Arch Walls
for i,w in enumerate(walls):
    x1,y1,x2,y2 = w["x1"],w["y1"],w["x2"],w["y2"]
    t = w.get("thickness",240 if w["t"]=="\u5916" else 150)
    line = Draft.makeLine(Vector(x1,y1,0),Vector(x2,y2,0))
    aw = Arch.makeWall(line, width=t, height=2800)
    aw.Label = w["t"]+"\u5899_"+str(i+1)

print("Walls:", len([o for o in doc.Objects if "Wall" in o.Name or "\u5899" in o.Label]))

# Slab
pts=[Vector(min(ax)-500,min(ay)-500,0),Vector(max(ax)+500,min(ay)-500,0),
     Vector(max(ax)+500,max(ay)+500,0),Vector(min(ax)-500,max(ay)+500,0)]
wire=Draft.makeWire(pts,closed=True)
slab=Arch.makeStructure(wire,height=200)
slab.Label="\u7ed3\u6784\u697c\u677f"

# Roof (flat)
rpts=[Vector(min(ax)-500,min(ay)-500,2800),Vector(max(ax)+500,min(ay)-500,2800),
      Vector(max(ax)+500,max(ay)+500,2800),Vector(min(ax)-500,max(ay)+500,2800)]
rw=Draft.makeWire(rpts,closed=True)
roof=Arch.makeRoof(rw)
roof.Label="\u5c4b\u9876"

# Furniture as Arch Equipment
for i,fi in enumerate(furniture):
    box=doc.addObject("Part::Box","Furn_"+str(i+1))
    box.Label=fi["n"]; box.Length=fi["w"]; box.Width=fi["d"]; box.Height=fi.get("h",500)
    box.Placement=Base.Placement(Vector(fi["x"],fi["y"],0),Base.Rotation())

# Export IFC
try:
    Arch.exportIFC(doc.Objects, "output/professional/model_bim.ifc")
    print("IFC exported")
except Exception as e:
    print("IFC err:", e)

# Export STEP
shapes=[o for o in doc.Objects if hasattr(o,"Shape") and not o.Shape.isNull()]
if shapes:
    try:
        Part.makeCompound([o.Shape for o in shapes]).exportStep("output/professional/model_bim.stp")
        print("STEP exported")
    except: pass

# Export STL
try:
    m=Mesh.Mesh()
    for o in doc.Objects:
        if hasattr(o,"Shape") and not o.Shape.isNull():
            try: m.addMesh(o.Shape.tessellate(50))
            except: pass
    m.write("output/professional/model_bim.stl")
    print("STL exported")
except: pass

doc.saveAs("output/professional/model_bim.fcstd")
nw=len([o for o in doc.Objects if o.Name.startswith("Wall") or o.Name.startswith("Box")])
print("BIM OK: %d objects" % len(doc.Objects))
