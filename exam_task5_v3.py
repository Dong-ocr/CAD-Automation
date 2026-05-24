# ======================================================================
#  exam_task5_v3.py — 阶梯轴零件图（使用 cad_toolbox）
#
#  轴段数据驱动，修改 SEG 即可适配不同尺寸的轴
# ======================================================================

from cad_toolbox import CADProject
import math, os

BASE = os.path.dirname(os.path.abspath(__file__))
p = CADProject("阶梯轴零件图")
p.setup_layers()

# ── 轴段数据 ──
SEG = [("M20",20,20,"M"), ("phi25",30,25,""), ("phi30slot",30,30,"K"),
       ("phi20",20,20,""), ("phi28",20,28,"")]
x, SEGS = 0, []
for nm, ln, d, nt in SEG:
    SEGS.append({"n":nm,"x1":x,"x2":x+ln,"ln":ln,"d":d,"r":d/2,"nt":nt})
    x += ln
TOTAL_L = x  # 120
KW, KD = 8, 3.5  # 键槽

# ── 主视图 ──
OX, AY = 50, 200
p.centerline(OX, OX+TOTAL_L, AY)

for s in SEGS:
    r, x1, x2 = s["r"], OX+s["x1"], OX+s["x2"]
    if s["nt"] == "M":
        p.thread_ext(x1, x2, AY, r, r-1.5, "OUTLINE", "THREAD", 2)
    else:
        p.line(x1, AY+r, x2, AY+r, "OUTLINE")
        p.line(x1, AY-r, x2, AY-r, "OUTLINE")
    # 轴肩
    if s["x1"] > 0:
        pr = [p2 for p2 in SEGS if abs(p2["x2"]-s["x1"])<0.1]
        if pr and abs(pr[0]["r"]-r)>0.01:
            prr = pr[0]["r"]
            p.line(x1, AY+min(prr,r), x1, AY+max(prr,r))
            p.line(x1, AY-max(prr,r), x1, AY-min(prr,r))

p.line(OX, AY, OX, AY+SEGS[0]["r"], "OUTLINE")
p.line(OX+TOTAL_L, AY, OX+TOTAL_L, AY+SEGS[-1]["r"], "OUTLINE")
p.line(OX, AY, OX, AY-SEGS[0]["r"], "OUTLINE")
p.line(OX+TOTAL_L, AY, OX+TOTAL_L, AY-SEGS[-1]["r"], "OUTLINE")

# 键槽
ks = [s for s in SEGS if s["nt"]=="K"]
if ks:
    s = ks[0]
    kx1 = OX+s["x1"]+(s["ln"]-KW)/2; kx2 = kx1+KW; ky = AY+s["r"]-KD
    p.line(kx1, ky, kx2, ky, "HIDDEN")
    p.line(kx1, ky, kx1, AY+s["r"], "HIDDEN")
    p.line(kx2, ky, kx2, AY+s["r"], "HIDDEN")

# 剖面线
boundary = []
for s in SEGS:
    if s["nt"] == "M": continue
    x1, x2 = OX+s["x1"], OX+s["x2"]
    boundary.append((x1, AY+s["r"]-0.5))
    if s["nt"] == "K":
        kx1 = x1+(s["ln"]-KW)/2; kx2 = kx1+KW
        ky = AY+s["r"]-KD+0.5
        boundary += [(kx1, AY+s["r"]-0.5), (kx1, ky), (kx2, ky), (kx2, AY+s["r"]-0.5)]
    boundary.append((x2, AY+s["r"]-0.5))
xs2 = [pt[0] for pt in boundary]
boundary += [(max(xs2), AY), (min(xs2), AY)]
p.hatch_section(boundary)

# 标注
for s in SEGS:
    xm = OX+(s["x1"]+s["x2"])/2
    p.text("M20x2.5" if s["nt"]=="M" else ("phi%d"%s["d"]), xm, AY+s["r"]+10, 2.5, "DIMENSION")
    p.text("M20" if s["nt"]=="M" else ("phi%d"%s["d"]), xm, AY+30, 2.5, "TEXT")
    p.roughness(xm, AY+s["r"]+14, 1.6 if s["nt"]=="K" else 3.2)
p.dim_h(OX, OX+TOTAL_L, AY-SEGS[-1]["r"]-8, text="L=%d"%TOTAL_L)
if ks:
    s = ks[0]; xm = OX+(s["x1"]+s["x2"])/2
    p.text("键槽 %dx%s" % (KW, KD), xm, AY-s["r"]-18, 2.5, "DIMENSION")
    p.dim_h(xm-KW/2, xm+KW/2, AY-s["r"]-8, text=str(KW))
    tx = xm
    p.tolerance(tx-25, AY+s["r"]+22, "圆圆", "0.02", "A-B")
    p.tolerance_leader(tx-25, AY+s["r"]+17, tx-25, AY+s["r"])
p.text("C1", OX+3, AY+5, 2, "DIMENSION"); p.text("C1", OX+3, AY-5, 2, "DIMENSION")

# ── 螺纹局部放大 3x ──
OX2, BY = 50, 70; sc = 3
s = SEGS[0]; rm, ri = s["r"]*sc, (s["r"]-1.5)*sc; ln2= s["ln"]*sc
p.centerline(OX2, OX2+ln2, BY)
p.thread_ext(OX2, OX2+ln2, BY, rm, ri, "OUTLINE", "THREAD")
p.thread_triangles(OX2, OX2+ln2, BY, rm, ri, 2.5*sc, "OUTLINE")
p.text("M20 螺纹 3:1", OX2+ln2/2, BY+rm+12, 4, "TITLE")
ccx = 50+SEGS[0]["x1"]+SEGS[0]["ln"]/2; ccy = 200
p.circle(ccx, ccy, 12, "AUX", 0.25)
p.line(ccx-12, ccy+3, OX2, BY+rm+3, "AUX", 0.25)
p.line(ccx+12, ccy+3, OX2+ln2, BY+rm+3, "AUX", 0.25)

# ── 斜二测 ──
OX3, CY = 380, 120; SC = 1.5; A45 = math.radians(45); SY = 0.5
def pr(x,y,z):
    return (OX3+x*SC+z*SC*SY*math.cos(A45), CY+y*SC+z*SC*SY*math.sin(A45))
for s in SEGS:
    r, x1, x2 = s["r"], s["x1"], s["x2"]
    p.line(*pr(x1,0,-r), *pr(x2,0,-r)); p.line(*pr(x1,0,r), *pr(x2,0,r), "HIDDEN", 0.25)
    p.line(*pr(x1,r,0), *pr(x2,r,0)); p.line(*pr(x1,-r,0), *pr(x2,-r,0))
for seg, is_l in [(SEGS[0],True),(SEGS[-1],False)]:
    r = seg["r"]; xp = seg["x1"] if is_l else seg["x2"]
    pts = [pr(xp, r*math.sin(math.radians(a)), r*math.cos(math.radians(a))) for a in range(0,360,10)]
    p.polyline(pts, "OUTLINE")
p.text("斜二测图 1:1", OX3+TOTAL_L*SC/2, CY+max(s["r"] for s in SEGS)*SC+15, 4, "TITLE")

# ── 技术要求 ──
notes = ["技术要求","","1. 材料：45号钢","","2. 调质处理 HB 220-250","",
         "3. 未注倒角 C1","","4. 未注表面粗糙度 Ra 3.2","",
         "5. 圆柱度公差 0.02mm","","6. 去毛刺、锐角倒钝",""]
y = -50
for n in notes:
    if n: p.text(n, 60, y, 5 if n=="技术要求" else 2.5, "TITLE" if n=="技术要求" else "TEXT")
    y -= 5

# ── 图框 + 保存 ──
p.add_frame({"client":"机械制图作业","project":"阶梯轴零件图",
             "drawing":"轴套类零件","stamp":"T-005","scale":"1:1",
             "date":"2026.05","designer":"Python+cad_toolbox"})
dxf = os.path.join(BASE, "exam_task5.dxf")
p.save(dxf)
p.export_pdf(dxf.replace(".dxf", ".pdf"))
print("Done!")
