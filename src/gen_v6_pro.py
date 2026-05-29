# ======================================================================
#  gen_v6_pro.py — 岩泊渡水电站 v6.1 四张专业级施工图
#  基于参考图: 引线标注、剖切转折、多链尺寸、说明区
# ======================================================================
import sys, os, math
sys.path.insert(0, "E:/CAD自动化制图")
from cad_toolbox_v6 import HydroProject

# =========================== 项目数据 ===========================
E_DT = 83500; E_TC = 95670; E_TF = 98500
E_GF = 105000; E_CR = 117000; E_RF = 124200
LT = 94000; LU = 20000; LI = 30000; SPAN = 17000; LK = 16500
CU_W, CU_D = 600, 800; CD_W, CD_D = 600, 1000
STATOR_OD = 9760; ROTOR_D = 7900; HOOD_OD = 10600; SC_R = 9270
DT_H = 10000; DT_W = 10340; D1 = 3800; AXIS_SP = 6000

MATERIALS = [
    ("C30 混凝土", "m\u00b3", 2850, "主厂房结构"),
    ("C25 混凝土", "m\u00b3", 1260, "蜗壳外围"),
    ("HRB400 钢筋", "t", 320, "\u03a625/\u03a622"),
    ("HPB300 钢筋", "t", 85, "\u03a612/\u03a610"),
    ("Q355B 钢结构", "t", 180, "吊车梁/屋架"),
    ("SF48.1-44/9760", "\u53f0", 3, "发电机"),
    ("HL240-LJ-380", "\u53f0", 3, "水轮机"),
    ("250/50t 桥吊", "\u53f0", 1, "桥式起重机"),
    ("蜗壳钢板 \u03b4=25mm", "t", 45, ""),
]

CROSS_NOTES = [
    "1. 本图尺寸单位mm，高程单位m",
    "2. 混凝土强度等级：主厂房C30，蜗壳外围C25",
    "3. 钢筋保护层厚度：梁柱35mm，板20mm",
    "4. 图中高程为黄海高程系统",
    "5. 施工时应与地质、机电专业图纸配合使用",
]

PLAN_NOTES = [
    "1. 本图尺寸单位mm",
    "2. 机组中心线偏差不超过\u00b12mm",
    "3. 安装场地面荷载按30kN/m\u00b2设计",
    "4. 图中虚线为下层轮廓投影线",
    "5. 预埋件位置详见埋件布置图",
]


OUT_DIR = "E:/CAD自动化制图"

def save_final(proj, sname):
    """保存并清理默认布局"""
    if "Layout1" in [l.name for l in proj.doc.layouts]:
        proj.doc.layouts.delete("Layout1")
    path = os.path.join(OUT_DIR, f"Yanbodu_{sname}_v6.dxf")
    proj.save(path)
    return path


def gen_cross_section():
    """主厂房横剖面图 — A1 1:100 (专业升级版)"""
    print("  [1/4] 主厂房横剖面图...")
    proj = HydroProject()
    ux = -(SPAN/2 - 2000)
    dx = SPAN/2 - 3000
    ct = E_CR + 2200
    
    # 地面线
    proj.line(-LT/3, E_DT-500, LT/3, E_DT-500, "0-建筑", 0.5)
    proj.text("地面", 40000, E_DT-500-2000, 2.5)
    
    # 尾水管
    dt_pts = [(0,E_TC),(-DT_W/2*0.6,E_DT+DT_H*0.5),(-DT_W/2,E_DT),
              (-DT_W/2*0.3,E_DT+DT_H*0.2),(0,E_TC-500),
              (DT_W/2*0.3,E_DT+DT_H*0.2),(DT_W/2,E_DT),
              (DT_W/2*0.6,E_DT+DT_H*0.5),(0,E_TC)]
    proj.polyline(dt_pts, "HIDN-隐藏", 0.25)
    proj.text("尾水管", DT_W/2+3000, E_DT+DT_H*0.5, 2.5)
    
    # 蜗壳
    sc_pts = []
    for i in range(73):
        a = math.radians(360*i/72)
        r = SC_R * max(0.15 + 0.85*(1-i/72), 0.04)
        sc_pts.append((r*math.cos(a), E_TC + r*math.sin(a)))
    proj.polyline(sc_pts, "M-HYDR-水力", 0.5)
    proj.text(f"\u8717\u58f3 R={SC_R}mm", SC_R*0.5, E_TC+SC_R*0.6, 2.5)
    
    # 中心线
    proj.axis_line(-SC_R*2, E_TC, SC_R*2, E_TC)
    proj.axis_line(0, E_DT-1000, 0, ct+1000)
    
    # 发电机
    gc = E_TF + (E_GF - E_TF) * 0.55
    proj.circle(0, gc, STATOR_OD/2, "M-EQPM-设备", 0.5)
    proj.circle(0, gc, ROTOR_D/2, "AXIS-轴线", 0.2)
    st_pts = [(STATOR_OD/2*math.cos(math.radians(360*i/36)),
               gc+STATOR_OD/2*math.sin(math.radians(360*i/36))) for i in range(37)]
    proj.hatch_fill(st_pts, "ANSI31", 100, color=8)
    proj.text_c("SF48.1-44/9760", 0, gc, 3.0)
    proj.text_c("\u53d1\u7535\u673a", 0, gc+3000, 2.5)
    
    # 水轮机
    proj.circle(0, E_TC, D1/2, "M-HYDR-水力", 0.5)
    proj.text_c("HL240-LJ-380", 0, E_TC-3000, 2.5)
    
    # 立柱
    for cx, cw, cd in [(ux,CU_W,CU_D/2),(dx,CD_W,CD_D/2)]:
        proj.rect(cx-cw/2, E_TF, cx+cw/2, ct, "A-COLM-立柱", 0.5)
        proj.hatch_solid([(cx-cw/2,E_TF),(cx+cw/2,E_TF),(cx+cw/2,ct),(cx-cw/2,ct)],253)
    
    # 牛腿
    proj.rect(ux-CU_W/2-300, E_CR-1000, ux+CU_W/2+300, E_CR, "A-COLM-立柱", 0.35)
    proj.rect(dx-CD_W/2-300, E_CR-1000, dx+CD_W/2+300, E_CR, "A-COLM-立柱", 0.35)
    
    # 楼层线
    for el, lbl in [(E_DT,"\u5c3e\u6c34\u7ba1\u5e95"),(E_TF,"\u6c34\u8f6e\u673a\u5c42"),
                     (E_GF,"\u53d1\u7535\u673a\u5c42"),(E_CR,"\u540a\u8f66\u8f68\u9876"),
                     (E_RF,"\u5c4b\u9876")]:
        proj.line(-SPAN, el, SPAN, el, "A-FLOR-楼面", 0.18)
        proj.text(lbl, -SPAN-3000, el, 2.5, rot=90)
    
    # 吊车梁
    proj.rect(-LK/2, E_CR+200, LK/2, E_CR+1000, "A-OVHD-吊车", 0.35)
    proj.text_c("250/50t \u6865\u5f0f\u8d77\u91cd\u673a", 0, E_CR+600, 3.0)
    proj.line(0, E_CR+200, 0, E_CR-500, "HIDN-隐藏", 0.2)
    
    # 屋面
    proj.rect(-SPAN/2+500, E_CR+2200, SPAN/2-500, E_RF, "A-ROOF-屋面", 0.5)
    proj.line(-SPAN/2+500, E_RF, 0, E_RF+1500, "A-ROOF-屋面", 0.18)
    proj.line(0, E_RF+1500, SPAN/2-500, E_RF, "A-ROOF-屋面", 0.18)
    proj.rect(-3000, E_RF, 3000, E_RF+3000, "A-ROOF-屋面", 0.35)
    proj.text_c("\u901a\u98ce\u5e3d", 0, E_RF+1500, 2.5)
    
    # 剖切线 A-A
    proj.add_section_line_turn("A", [(-SPAN-2000, E_TC), (-SPAN/2, E_TC)])
    
    # 引线标注
    proj.add_leader(0, gc+STATOR_OD/2+1000, -SPAN/3, gc+STATOR_OD/2+4000, 
                    "\u5b9a\u5b50\u5916\u5f84\u03a69760", 3.0, 500)
    proj.add_leader(SC_R, E_TC, SPAN/3, E_TC-3000, 
                    "\u8717\u58f3\u4e2d\u5fc3\u9ad8\u7a0b\u03bd95670", 3.0, 500)
    
    # 多链尺寸
    segs = [(E_DT, E_TF, "H1=15000"), (E_TF, E_GF, "H2=6500"), 
            (E_GF, E_CR, "H3=12000"), (E_CR, E_RF, "H4=7200")]
    proj.add_multi_dim_v(LK/2+12000, segs, scale=100)
    
    # 总高尺寸
    proj.dim_v(LK/2+10000, E_DT, E_RF, text=f"H={E_RF-E_DT}mm", scale=100)
    
    # 高程
    for el, nm in [(E_DT,"\u5c3e\u6c34\u7ba1\u5e95"),(E_TC,"\u8717\u58f3\u4e2d\u5fc3"),
                    (E_TF,"\u6c34\u8f6e\u673a\u5c42"),(E_GF,"\u53d1\u7535\u673a\u5c42"),
                    (E_CR,"\u540a\u8f66\u8f68\u9876"),(E_RF,"\u5c4b\u9876")]:
        proj.elevation(LK/2+6000, el, el)
    
    # 图纸说明 (Model Space)
    proj.add_note_block(-SPAN/2-2000, E_DT-3000, 12000, CROSS_NOTES, "\u56fe\u7eb8\u8bf4\u660e")
    
    # Paper Space
    vc = (0, (E_DT+E_RF)/2)
    layout, pw, ph = proj.create_layout("\u6a2a\u5265\u9762\u56fe", "A1", 100, vc, border_mm=15, landscape=True)
    proj.add_title_block(layout, pw-240, 0, 240, 60, {
        "project":"\u5ca9\u6cca\u6e21\u6c34\u7535\u7ad9", "dname":"\u4e3b\u5382\u623f\u6a2a\u5265\u9762\u56fe",
        "dno":"YBD-01","scale":"1:100","date":"2026.05",
        "designer":"\u5f20","checker":"\u674e","auditor":"\u738b","size":"A1",
    })
    proj.add_material_table(layout, 15, 15, 180, MATERIALS)
    
    return save_final(proj, "Cross_Section")


def gen_plan(sname, title, dno, scale=150):
    """生成平面图"""
    print(f"  [{'234'[['Generator_Floor','Turbine_Floor','Spiral_Case_Floor'].index(sname)]}/4] {title}...")
    proj = HydroProject()
    n_ax = LT // AXIS_SP + 1
    
    # 轴线
    for i in range(n_ax):
        x = -LT/2 + i*AXIS_SP
        proj.axis_line(x, -SPAN/2-2000, x, SPAN/2+2000)
        proj.axis_circle(x, -SPAN/2-2000, f"{i+1}")
    
    # 厂方外轮廓
    proj.rect(-LT/2, -SPAN/2, LT/2, SPAN/2, "0-建筑", 0.5)
    
    # 立柱定位
    for i in range(2):
        for j in range(2):
            cx = -LT/2 + LI + i*(LT-LI) + ([-2000,23000][j] if i==0 else [-3000,22000][j])
            cy = -SPAN/2 + 1000 + j*15000
            cw, cd = (CU_W, CU_D) if i == 0 else (CD_W, CD_D)
            proj.rect(cx-cw/2, cy-cd/2, cx+cw/2, cy+cd/2, "A-COLM-立柱", 0.35)
            proj.hatch_solid([(cx-cw/2,cy-cd/2),(cx+cw/2,cy-cd/2),
                              (cx+cw/2,cy+cd/2),(cx-cw/2,cy+cd/2)],253)
    
    # 机组
    for unit in range(3):
        ucx = -LT/2 + LI + unit*LU
        
        if sname == "Spiral_Case_Floor":
            sc_pts = []
            for i in range(49):
                a = math.radians(360*i/48)
                r = SC_R * max(0.15+0.85*(1-i/48),0.04)
                sc_pts.append((ucx+r*math.cos(a), r*math.sin(a)))
            proj.polyline(sc_pts, "M-HYDR-水力", 0.5)
            proj.hatch_fill(sc_pts, "ANSI31", 150, color=8)
            proj.text_c(f"\u8717\u58f3 R={SC_R//1000}m", ucx, SPAN/2-3000, 2.5)
        
        if sname == "Turbine_Floor":
            proj.circle(ucx, 0, D1/2+1000, "M-STRU-结构", 0.5)
            proj.circle(ucx, 0, STATOR_OD/2, "HIDN-隐藏", 0.25)
            td_pts = [(ucx+(D1/2+1000)*math.cos(math.radians(360*i/36)),
                        0+(D1/2+1000)*math.sin(math.radians(360*i/36))) for i in range(37)]
            proj.hatch_fill(td_pts, "ANSI31", 150, color=8)
        
        proj.circle(ucx, 0, STATOR_OD/2, "M-EQPM-设备", 0.5)
        proj.circle(ucx, 0, ROTOR_D/2, "AXIS-轴线", 0.2)
        proj.text_c(f"#{unit+1} \u673a\u7ec4", ucx, 0, 4.0)
        
        if sname == "Generator_Floor":
            proj.circle(ucx, 0, HOOD_OD/2, "HIDN-隐藏", 0.25)
            proj.rect(ucx-3000, 3000, ucx+3000, 5000, "HIDN-隐藏", 0.18)
            proj.text_c("\u540a\u7269\u5b54", ucx, 4000, 2.5)
            proj.text_c("SF48.1-44/9760", ucx, -5000, 2.5)
        
        if unit == 0:
            proj.rect(-LT/2, -SPAN/2, -LT/2+LI, SPAN/2, "HIDN-隐藏", 0.25)
            proj.text_c("\u5b89\u88c5\u573a 30m\u00d717m", -LT/2+LI/2, 0, 3.5)
    
    # 楼梯
    for i in range(2):
        sx = -LT/2 + LI + i*LU*1.5
        proj.rect(sx, SPAN/2-3000, sx+3000, SPAN/2-1500, "0-建筑", 0.18)
        proj.text_c("\u697c\u68af", sx+1500, SPAN/2-2250, 2.5)
    
    # 上下游标注
    proj.text_c("\u4e0a\u6e38\u4fa7", 0, -SPAN/2-4000, 3.5)
    proj.text_c("\u4e0b\u6e38\u4fa7", 0, SPAN/2+4000, 3.5)
    
    # 引线标注 (各层特有)
    if sname == "Spiral_Case_Floor":
        proj.add_leader(-LT/2+LI+2000, SC_R, -LT/2+LI-5000, SC_R+4000,
                        "\u8717\u58f3\u4e2d\u5fc3\u7ebf", 3.0, 500)
        proj.add_leader(-LT/2+LI+LU+3000, -SC_R-2000, -LT/2+LI+LU+8000, -SC_R-5000,
                        "\u5f15\u6c34\u7ba1\u4e2d\u5fc3\u7ebf", 3.0, 500)
    elif sname == "Turbine_Floor":
        proj.add_leader(-LT/2+LI, STATOR_OD/2+2000, -LT/2+LI-5000, STATOR_OD/2+5000,
                        "\u6c34\u8f6e\u673a\u5ea7\u73af", 3.0, 500)
    elif sname == "Generator_Floor":
        proj.add_leader(-LT/2+LI+LU, HOOD_OD/2+2000, -LT/2+LI+LU-5000, HOOD_OD/2+5000,
                        "\u53d1\u7535\u673a\u7a74\u76d6", 3.0, 500)
    
    # 多链尺寸 (总长 + 分段)
    proj.dim_h(-SPAN/2-6000, -LT/2, LT/2, text=f"\u603b\u957f L={LT//1000}m", scale=scale)
    # 安装场 + 机组段
    segs = [(-LT/2, -LT/2+LI, f"L={LI//1000}m"), 
            (-LT/2+LI, -LT/2+LI+LU, f"L={LU//1000}m"),
            (-LT/2+LI+LU, LT/2, f"L={LU//1000}m")]
    proj.add_multi_dim_h(-SPAN/2-10000, segs, scale=scale)
    
    # 跨度尺寸
    proj.dim_v(LT/2+5000, -SPAN/2, SPAN/2, text=f"\u8de8\u5ea6 {SPAN//1000}m", scale=scale)
    
    # 图纸说明
    notes = PLAN_NOTES
    if sname == "Spiral_Case_Floor":
        notes = notes + ["6. \u8717\u58f3\u91c7\u7528\u94a2\u677f\u710a\u63a5\u7ed3\u6784\uff0c\u677f\u539a25mm",
                          "7. \u8717\u58f3\u5916\u56f4\u586b\u5145C25\u6df7\u51dd\u571f"]
    proj.add_note_block(-LT/2, -SPAN/2-8000, 20000, notes, "\u56fe\u7eb8\u8bf4\u660e")
    
    # Paper Space
    vc = (0, 0)
    layout, pw, ph = proj.create_layout(title, "A1", scale, vc, border_mm=15, landscape=True)
    
    names = {"Generator_Floor":"\u53d1\u7535\u673a\u5c42\u5e73\u9762\u56fe",
             "Turbine_Floor":"\u6c34\u8f6e\u673a\u5c42\u5e73\u9762\u56fe",
             "Spiral_Case_Floor":"\u8717\u58f3\u5c42\u5e73\u9762\u56fe"}
    
    proj.add_title_block(layout, pw-240, 0, 240, 60, {
        "project":"\u5ca9\u6cca\u6e21\u6c34\u7535\u7ad9", "dname":names[sname],
        "dno":dno,"scale":f"1:{scale}","date":"2026.05",
        "designer":"\u5f20","checker":"\u674e","auditor":"\u738b","size":"A1",
    })
    
    if sname == "Generator_Floor":
        proj.add_material_table(layout, 15, 15, 180, MATERIALS)
    
    # Paper Space 图纸说明
    proj.add_drawing_note_ps(layout, pw-240, 65, 240, PLAN_NOTES, "\u56fe\u7eb8\u8bf4\u660e")
    
    return save_final(proj, sname)


if __name__ == "__main__":
    print("=" * 60)
    print("  \u5ca9\u6cca\u6e21\u6c34\u7535\u7ad9 \u65bd\u5de5\u56fe v6.1 \u4e13\u4e1a\u7ea7")
    print("=" * 60)
    
    results = []
    results.append(gen_cross_section())
    results.append(gen_plan("Generator_Floor", "\u53d1\u7535\u673a\u5c42\u5e73\u9762\u56fe", "YBD-02", 150))
    results.append(gen_plan("Turbine_Floor",   "\u6c34\u8f6e\u673a\u5c42\u5e73\u9762\u56fe", "YBD-03", 150))
    results.append(gen_plan("Spiral_Case_Floor", "\u8717\u58f3\u5c42\u5e73\u9762\u56fe", "YBD-04", 150))
    
    print("\n" + "=" * 60)
    print("  v6.1 \u56db\u5f20\u4e13\u4e1a\u7ea7\u65bd\u5de5\u56fe\u5b8c\u6210!")
    print("=" * 60)
    for path in results:
        if os.path.exists(path):
            print(f"  \u2713 {os.path.basename(path)} ({os.path.getsize(path)/1024:.0f} KB)")
    print("  \u6587\u4ef6\u4f4d\u7f6e: E:\\CAD\u81ea\u52a8\u5316\u5236\u56fe\\")
