import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment
from library import BlockLibrary
from hatch_lib import HatchFiller
from dim_lib import DimLib
from frame_lib import FrameLib

doc = ezdxf.new("R2010")
msp = doc.modelspace()

# Layers
LAYERS = {
    "GROUND":(7,1),"ROAD":(7,1),"BUILDING":(2,1),"DORMITORY":(30,1),
    "SPORT_FIELD":(3,1),"GREEN":(3,1),"WATER":(4,1),"PLAZA":(8,1),
    "TEXT":(7,1),"TITLE":(2,1),"BORDER":(7,1),"LEGEND":(7,1),
    "AXIS":(6,1),"DIMENSION":(3,1),"FILL":(8,1),
}
for n,(c,lt) in LAYERS.items():
    doc.layers.new(n, dxfattribs={"color":c,"linetype":"CONTINUOUS" if lt==1 else lt})

# Init modules
blib = BlockLibrary(doc)
hf = HatchFiller(doc, msp)
dl = DimLib(doc, msp)
fl = FrameLib(doc, msp)
AL = TextEntityAlignment.MIDDLE_CENTER
def txt(s,x,y,h,l): te=msp.add_text(s,height=h,dxfattribs={"layer":l}); te.set_placement((x,y),align=AL)
def ln(x1,y1,x2,y2,l): msp.add_line((x1,y1),(x2,y2),dxfattribs={"layer":l})
def cc(cx,cy,r,l): msp.add_circle((cx,cy),r,dxfattribs={"layer":l})
def rx(x1,y1,x2,y2,l): msp.add_lwpolyline([(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)],dxfattribs={"layer":l})

# 1. Roads
R="ROAD"
for a,b in [((-300,-210),(300,-210)),((-300,210),(300,210)),((-300,-210),(-300,210)),((300,-210),(300,210)),
  ((-300,-50),(300,-50)),((-300,70),(300,70)),((0,-255),(0,210)),((-300,140),(-100,140)),
  ((-300,180),(-100,180)),((-100,140),(-100,210)),((100,70),(300,70)),((100,200),(300,200)),
  ((100,70),(100,200)),((200,70),(200,200)),((-100,-150),(100,-150)),((-100,-100),(100,-100))]:
    ln(a[0],a[1],b[0],b[1],R)

# 2. South gate
ln(-15,-260,-15,-245,"BUILDING"); ln(15,-260,15,-245,"BUILDING")
txt("宝鸡文理学院",0,-248,8,"TITLE"); txt("高新校区",0,-236,5,"TEXT")
rx(-25,-228,25,-212,"PLAZA")
blib.insert("GATE",0,-258,scale=5,layer="BUILDING")
blib.insert("FLAG_POLE",0,-235,scale=3.5,layer="BUILDING")

# 3-14. Buildings
bldgs = [("行政办公楼",0,-185,80,24),("图 书 馆",0,-20,100,44),
  ("教学A楼",-155,-20,64,34),("教学B楼",155,-20,64,34),
  ("教学C楼",-155,45,64,34),("教学D楼",155,45,64,34),
  ("实验楼A",-80,108,54,28),("实验楼B",80,108,54,28),
  ("实验楼C",-80,158,54,24),("实验楼D",80,158,54,24),
  ("体育馆",-190,110,54,38),
  ("食 堂",-230,120,44,20),("民族餐厅",-230,160,44,20),
  ("校医院",260,-80,44,20),("后勤中心",260,-130,44,20),
  ("学生活动中心",260,-180,44,20)]
for lbl,x,y,w,h in bldgs:
    blib.insert("BUILDING",x,y,scale=(w,h),layer="BUILDING")
    txt(lbl,x,y,5 if lbl=="图 书 馆" else 3.5,"TEXT")
txt("Library",0,-10,3.5,"TEXT")

# Dormitories
for nm,dx,dy in [("公寓1号",-220,-10),("公寓2号",-260,-10),("公寓3号",-220,30),
  ("公寓4号",-260,30),("公寓5号",-220,68),("公寓6号",-260,68),
  ("研究生公寓",-260,-80),("留学生公寓",-260,-120)]:
    blib.insert("DORMITORY",dx,dy,scale=(40,18),layer="DORMITORY")
    txt(nm,dx,dy,3.5,"TEXT")

# Plaza
rx(-40,-149,40,-121,"PLAZA"); cc(0,-135,5,"WATER")
txt("中心广场",0,-125,4,"TEXT")

# Sports
blib.insert("SPORT_FIELD",220,135,scale=(140,78),layer="SPORT_FIELD")
txt("田径场",220,135,5,"TEXT"); txt("Track & Field",220,125,3,"TEXT")
for i in range(4):
    bx=220+(i-1.5)*22
    blib.insert("SPORT_FIELD",bx,55,scale=(18,11),layer="SPORT_FIELD")
    txt("篮球",bx,55,2.5,"TEXT")
blib.insert("SPORT_FIELD",220,25,scale=(60,24),layer="SPORT_FIELD")
txt("网球场",220,25,4,"TEXT")
blib.insert("BASKETBALL_COURT",150,120,scale=0.6,layer="SPORT_FIELD")
blib.insert("TENNIS_COURT",150,175,scale=0.6,layer="SPORT_FIELD")

# Lake
for cx,cy,r in [(-160,-110,32),(-140,-100,22),(-170,-100,18),(-160,-110,5)]:
    cc(cx,cy,r,"WATER" if r>5 else "BUILDING")
txt("人工湖",-160,-110,4,"TEXT")
blib.insert("PAVILION",-160,-140,scale=3,layer="BUILDING")

# Green belts
for r in [(-100,-245,-30,-235),(30,-245,100,-235),(-55,-55,-5,-45),(5,-55,55,-45),(-295,-205,-285,205),(285,-205,295,205)]:
    rx(r[0],r[1],r[2],r[3],"GREEN")

# Trees
for tx,ty in [(-50,-225),(50,-225),(-50,-210),(50,-210),(-130,-155),(130,-155),(-130,-140),(130,-140),(-250,-100),(-250,-130),(250,-100),(250,-130)]:
    blib.insert("TREE",tx,ty,scale=2,layer="GREEN")

# Lamps & amenities
blib.insert("STREET_LAMP",-280,-50,scale=2,layer="GROUND")
blib.insert("STREET_LAMP",280,-50,scale=2,layer="GROUND")
blib.insert("FLOWER_BED",0,-135,scale=1.5,layer="GREEN")
blib.insert("BENCH",20,-140,rotation=90,layer="PLAZA")
blib.insert("BENCH",-20,-140,rotation=90,layer="PLAZA")
blib.insert("PARKING",130,-210,layer="PLAZA")
blib.insert("PARKING",-130,-210,layer="PLAZA")
txt("停车场",130,-210,3.5,"TEXT"); txt("停车场",-130,-210,3.5,"TEXT")

# North arrow
blib.insert("NORTH_ARROW",-310,230,scale=10)

# Road label
txt("-> 高新大道",0,-275,4,"TEXT"); txt("高新大道",0,-288,5,"TITLE")

# ===== HATCH =====
print("Hatch...")
n = hf.fill_all_of_type(msp, "BUILDING", color=2, layer="FILL")
n += hf.fill_all_of_type(msp, "DORMITORY", color=30, layer="FILL")
hf.fill_circle(-160,-110,30,color=4,layer="WATER")
hf.fill_circle(-140,-100,20,color=4,layer="WATER")
hf.fill_circle(-170,-100,16,color=4,layer="WATER")
for r in [(-100,-245,-30,-235),(30,-245,100,-235),(-55,-55,-5,-45),(5,-55,55,-45)]:
    cx=(r[0]+r[2])/2; cy=(r[1]+r[3])/2; w=r[2]-r[0]; h=r[3]-r[1]
    hf.pattern_rect(cx,cy,w,h,pattern="GRAVEL",scale=2,color=3,layer="GREEN")
print("  Hatches:", hf.count)

# ===== DIMENSION =====
print("Dim...")
dl.horizontal(-300,300,-265,offset=12,layer="DIMENSION")
dl.vertical(-350,-250,250,offset=12,layer="DIMENSION")
dl.horizontal(-187,-123,108,offset=8,layer="DIMENSION")
dl.vertical(-187,94,122,offset=8,layer="DIMENSION")

# Axis
dl.axis_grid(
    xs=[-300,-200,-100,0,100,200,300],
    ys=[-200,-100,0,100,200],
    labels_x=["1","2","3","4","5","6","7"],
    labels_y=["A","B","C","D","E"],
    size=3,layer_axis="AXIS",layer_dim="DIMENSION"
)

# ===== FRAME & TITLE BLOCK =====
print("Frame...")
fl.standard_a3_frame({
    "client":"宝鸡文理学院","project":"高新校区总平面图",
    "drawing":"总平面布置图","stamp":"T-001",
    "scale":"1:2000","date":"2026.05","designer":"AutoCAD",
}, x0=-355,y0=-295,x1=355,y1=295)

# ===== LEGEND =====
lx,ly=230,-250; txt("图 例",lx,ly+5,5,"LEGEND")
for i,(bn,desc) in enumerate([("BUILDING","建筑物"),("DORMITORY","学生公寓"),
  ("SPORT_FIELD","运动场地"),("TREE","绿化"),("WATER","水体"),("PARKING","停车场"),("ROAD","道路")]):
    blib.insert("LEGEND_ITEM",lx+5,ly-2-i*7,scale=(0.4,0.4),attrs={"LABEL":desc},layer="LEGEND")

# ===== SAVE =====
OUTPUT="C:/Users/王东浩/Documents/CAD自动化制图/bjwlxy_campus.dxf"
doc.saveas(OUTPUT)
print()
print("="*50)
print("  Professional campus map generated!")
print("  Blocks:", blib.count_refs())
print("  Hatches:", hf.count)
print("  Total entities:", len(msp))
print("="*50)
