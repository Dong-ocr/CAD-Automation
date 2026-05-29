import FreeCAD, Part, Mesh, math, os, sys, traceback
from FreeCAD import Base, Vector
V = Vector

C = {
    "glass": (0.50, 0.75, 0.95, 0.40), "glass_dark": (0.30, 0.50, 0.70, 0.50),
    "wall_w": (0.92, 0.92, 0.90, 0.00), "wall_g": (0.75, 0.80, 0.75, 0.00),
    "roof_wood": (0.55, 0.35, 0.20, 0.00), "roof_green": (0.20, 0.60, 0.25, 0.00),
    "deck": (0.50, 0.40, 0.30, 0.00), "pool": (0.10, 0.50, 0.80, 0.30),
    "steel": (0.55, 0.55, 0.60, 0.00), "terrain": (0.35, 0.55, 0.25, 0.00),
    "road": (0.30, 0.30, 0.30, 0.00), "car_body": (0.80, 0.15, 0.15, 0.00),
    "light_warm": (1.00, 0.85, 0.50, 0.00), "red": (0.70, 0.15, 0.15, 0.00),
}

def sc(o, name):
    try:
        v = o.ViewObject
        if v:
            rgb = C.get(name, (0.8,0.8,0.8,0))
            v.ShapeColor = (rgb[0], rgb[1], rgb[2])
            if len(rgb)>3 and rgb[3]>0: v.Transparency = int(rgb[3]*100)
    except: pass

def bb(l,w,h,p=(0,0,0),n="B",c=None):
    b = doc.addObject("Part::Box",n); b.Length,b.Width,b.Height = l,w,h
    b.Placement = Base.Placement(V(*p),Base.Rotation())
    if c: sc(b,c); return b

def cc(r,h,p=(0,0,0),n="C",c=None):
    o = doc.addObject("Part::Cylinder",n); o.Radius,o.Height = r,h
    o.Placement = Base.Placement(V(*p),Base.Rotation())
    if c: sc(o,c); return o

def sp(r,p=(0,0,0),n="S",c=None):
    o = doc.addObject("Part::Sphere",n); o.Radius = r
    o.Placement = Base.Placement(V(*p),Base.Rotation())
    if c: sc(o,c); return o

doc = FreeCAD.newDocument("CliffVilla")
doc.Label = "Cliff Villa - Modern Organic Architecture"

sys.stderr.write("Terrain...\n")
bb(60000,50000,2000,(-30000,-25000,-2000),"Terrain","terrain")
bb(60000,5000,15000,(-30000,-5000,-2000),"Cliff","terrain")
for i in range(20):
    rx=-20000+math.sin(i*1.7)*25000; ry=-5000+math.cos(i*2.3)*4000
    rz=-2000+math.sin(i*3.1)*3000
    r=sp(800+math.sin(i*5.7)*400,(rx,ry,rz),f"Rock{i}","terrain")

sys.stderr.write("Main building...\n")
bb(18000,14000,400,(-9000,-7000,0),"Slab1")
for i in range(7):
    a=-0.8+i*0.25; cx=4000*math.cos(a); cy=4000*math.sin(a)+3000
    g=bb(200,3200,3200,(cx-100,cy-1600,0),f"GW{i}","glass")
    g.Placement.Rotation=Base.Rotation(V(0,0,1),-math.degrees(a))
    g.Placement.Base=V(cx,cy,0)

for cx2,cy2 in [(-4000,-2000),(4000,-2000),(-4000,2000),(4000,2000),(-2000,-3000),(2000,-3000)]:
    cc(200,3200,(cx2-200,cy2-200,0),"Col","steel")

sys.stderr.write("Deck & pool...\n")
bb(16000,6000,200,(-8000,7000,3200),"Deck","deck")
bb(8000,4000,1800,(-5000,8000,-1800),"PoolBase")
bb(7600,3600,200,(-4800,8200,0),"PoolWater","pool")
bb(8000,200,150,(-5000,8000,0),"PoolEdge")

sys.stderr.write("Windows & facade...\n")
for i,(gx,gw) in enumerate([(-7000,2000),(-3500,3000),(0,3000),(3500,3000),(6500,2000)]):
    bb(gw,50,2800,(gx,6975,200),f"Win{i}","glass")
for i in range(12):
    bb(50,200,3200,(-7000+i*1200,-7100,0),f"Lou{i}","roof_wood")

sys.stderr.write("Interior...\n")
s=bb(3000,1000,700,(-2000,-3000,400),"Sofa"); sc(s,"red")
bb(1500,800,300,(-500,-2600,700),"TeaTable","roof_wood")
bb(2400,1000,750,(-1000,2000,400),"DTable","roof_wood")
for j,(dx,dy) in enumerate([(-900,0),(900,0),(0,-600),(0,600)]):
    bb(500,500,800,(-1000+dx-250,2000+dy-250,400),f"Chair{j}","roof_wood")
bb(2000,300,2800,(6000,-4000,200),"Shelf")
cc(80,2000,(4920,-2000,0),"Lamp","light_warm")
p=bb(1500,600,1000,(4000,1000,400),"Piano"); sc(p,"wall_w")

sys.stderr.write("Landscape...\n")
for tx2,ty2 in [(-12000,5000),(-13000,8000),(10000,6000),(11000,-2000),(-8000,-10000),(8000,-8000),(12000,10000)]:
    cc(80,2000,(tx2-80,ty2-80,0),"Trunk","roof_wood")
    cc(600,2000,(tx2-600,ty2-600,2000),"Crown","roof_green")

sys.stderr.write("Car...\n")
bb(4500,1800,800,(6000,-12000,200),"CarBody","car_body")
bw=bb(2500,1500,300,(6500,-11500,1000),"CarRoof","glass_dark")
for wx2,wy2 in [(6300,-12300),(6300,-10900),(10200,-12300),(10200,-10900)]:
    cc(300,200,(wx2-300,wy2-100,0),"Wheel")
    cc(350,180,(wx2-350,wy2-90,-10),"Tire","road")

doc.recompute()
sys.stderr.write(f"Done! Objects: {len(doc.Objects)}\n")
d="E:/CAD自动化制图/output/professional"
os.makedirs(d,exist_ok=True)
doc.saveAs(os.path.join(d,"cliff_villa.fcstd"))
sys.stderr.write("FCStd saved\n")
try:
    sh=[o.Shape for o in doc.Objects if hasattr(o,"Shape") and o.Shape and not o.Shape.isNull()]
    if sh:
        co=Part.makeCompound(sh)
        co.exportStep(os.path.join(d,"cliff_villa.step"))
        sys.stderr.write("STEP saved\n")
        me=Mesh.Mesh(co.tessellate(100))
        me.write(os.path.join(d,"cliff_villa.stl"))
        sys.stderr.write("STL saved\n")
except Exception as e:
    sys.stderr.write(f"Export: {e}\n")
sys.stderr.write("ALL DONE\n")
