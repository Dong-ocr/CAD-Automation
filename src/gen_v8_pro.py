# ====================================================================
#  gen_v8_pro.py — 岩泊渡水电站 v8 四张专业施工图（全面升级版）
#  特点: 完整尺寸引擎 · MultiLeader · 齿轮绘制 · SVG预览 ·
#        蜗壳螺旋线 · DXF 审计 · 3D 导出 (可选)
# ====================================================================
import sys, os, math
sys.path.insert(0, "E:/CAD自动化制图/src")
from cad_toolbox_v8 import HydroProjectV8

# =========================== 项目数据 ===========================
E_DT  = 83500   # 尾水管底
E_TC  = 95670   # 蜗壳中心
E_TF  = 98500   # 水轮机层
E_GF  = 105000  # 发电机层
E_CR  = 117000  # 吊车轨顶
E_RF  = 124200  # 屋顶

LT  = 94000
LU  = 30000
LI  = 20000
SPAN = 17000
LK  = 16500
AXIS_SP = 6000

STATOR_OD = 9760
ROTOR_D   = 7900
HOOD_OD   = 10600
SC_R      = 9270
DT_H      = 10000
DT_W      = 10340
D1        = 3800

CU_W, CU_D = 600, 800
CD_W, CD_D = 600, 1000

# =========================== 1. 剖面图 ===========================
def draw_cross_section(proj):
    ox, oy = 0, 82000
    s = 100  # scale
    print("  [剖面图] 绘制结构...", end=" ")

    # 屋顶
    proj.rect(ox, oy + (E_RF - E_GF), ox + LT, oy + (E_RF - E_GF) + 3000, "A-ROOF-屋面", 0.35)
    # 发电机层楼板
    proj.line(ox, oy + (E_GF - E_DT), ox + LT, oy + (E_GF - E_DT), "A-FLOR-楼面", 0.35)
    # 水轮机层楼板
    proj.line(ox, oy + (E_TF - E_DT), ox + LT, oy + (E_TF - E_DT), "A-FLOR-楼面", 0.35)
    # 蜗壳中心线
    proj.line(ox, oy + (E_TC - E_DT), ox + LT, oy + (E_TC - E_DT), "AXIS-轴线", 0.18)
    # 尾水管底
    proj.line(ox, oy + 0, ox + LT, oy + 0, "S-FNDN-基础", 0.50)
    # 立柱
    for cx in [5000, 11000, 41000, 47000, 53000]:
        proj.rect(cx - CU_W / 2, oy, cx + CU_W / 2, oy + (E_GF - E_DT), "A-COLM-立柱", 0.25)
    for cx in [3500, 50000]:
        proj.rect(cx - CD_W / 2, oy, cx + CD_W / 2, oy + (E_RF - E_DT) + 3000, "A-COLM-立柱", 0.35)
    # 吊车
    proj.line(2000, oy + (E_CR - E_DT), LT - 2000, oy + (E_CR - E_DT), "A-OVHD-吊车", 0.25)
    # 水轮机
    cx_t = 47000
    proj.circle(cx_t, oy + (E_TC - E_DT), D1 / 2, "M-HYDR-水力", 0.35)

    print("尺寸标注...", end=" ")
    # 高程标注
    for label, ey in [("尾水管底", E_DT), ("蜗壳中心", E_TC),
                       ("水轮机层", E_TF), ("发电机层", E_GF),
                       ("吊车轨顶", E_CR), ("屋顶", E_RF)]:
        y = oy + (ey - E_DT)
        proj.dim_v(ox - 1500, oy, y, f"{ey//1000}.{ey%1000//10:02d}m", s)
    # 水平总尺寸
    proj.dim_h(oy - 3000, ox, ox + LT, f"总长{LT//1000}.{LT%1000//10:02d}m", s)
    proj.dim_chain_h(oy - 4500, [
        (ox, ox + LI, f"{LI//1000}m"),
        (ox + LI, ox + LI + LU, f"{LU//1000}m"),
        (ox + LI + LU, ox + LI + 2 * LU, f"{LU//1000}m"),
    ], s)

    print("填充...", end=" ")
    proj.hatch_rect(ox + 100, oy, ox + LT - 100, oy + 500, "ANSI31", 50, 8, "HATCH-填充")

    notes = [
        "本图高程以 m 计，其余尺寸以 mm 计",
        "混凝土强度等级 C30，抗渗等级 W8",
        "尾水管底板高程 83.500m，机组安装高程 95.670m",
    ]
    proj.note_block(ox + LU, oy + (E_GF - E_DT) + 1000, 18000, notes)
    print("完成")

# =========================== 2. 发电机层 ===========================
def draw_generator_floor(proj):
    ox, oy = 3000, 3000
    s = 100
    print("  [发电机层] 绘制结构...", end=" ")

    proj.rect(ox, oy, ox + SPAN, oy + LI + 2 * LU, "A-WALL-墙体", 0.35)
    for i in range(4):
        y = oy + LI + i * LU
        if i > 0:
            proj.line(ox, y, ox + SPAN, y, "AXIS-轴线", 0.15)

    cx, cy = ox + SPAN / 2, oy + LI + LU / 2
    # 发电机风罩
    proj.circle(cx, cy, HOOD_OD / 2, "M-EQPM-设备", 0.35)
    proj.circle(cx, cy, STATOR_OD / 2, "M-EQPM-设备", 0.25)
    proj.circle(cx, cy, ROTOR_D / 2, "M-EQPM-设备", 0.18)

    # v8 新特性：齿轮绘制
    proj.draw_gear(cx, cy, 20, 1500, "M-STRU-金属结构")

    print("立柱...", end=" ")
    for dx, dy in [(-7700, -4500), (-7700, 4500), (7700, -4500), (7700, 4500),
                   (-7700, -14500), (-7700, 14500), (7700, -14500), (7700, 14500)]:
        proj.rect(SPAN / 2 + dx - CU_W / 2, LI + LU / 2 + dy - CU_D / 2,
                  SPAN / 2 + dx + CU_W / 2, LI + LU / 2 + dy + CU_D / 2,
                  "A-COLM-立柱", 0.25)

    print("轴线网格...", end=" ")
    proj.axis_grid(ox, oy, 3, 3, SPAN / 2, LI / 2)

    print("尺寸...", end=" ")
    proj.dim_h(oy - 2000, ox, ox + SPAN, f"跨度{SPAN//1000}.{SPAN%1000//10:02d}m", s)
    proj.dim_v(ox - 2000, oy, oy + LI + 2 * LU, f"总长{(LI+2*LU)//1000}m", s)
    proj.dim_radius(cx, cy, cx + HOOD_OD / 2 + 1000, cy + 1000,
                    f"R{HOOD_OD//10//100:.1f}m", s)
    proj.dim_diameter(cx, cy, STATOR_OD / 2 + 2000,
                      f"\\U+00D8{STATOR_OD//1000}.{STATOR_OD%1000//10:02d}m", s)

    print("填充...", end=" ")
    proj.hatch_solid([(ox + 50, oy + 50), (SPAN - 50, oy + 50),
                       (SPAN - 50, oy + LI - 50), (ox + 50, oy + LI - 50)],
                      253, "HATCH-填充")

    # v8 新特性：MultiLeader
    proj.add_leader_v8(cx + HOOD_OD / 2 + 500, cy + 500,
                        cx + HOOD_OD / 2 + 2000, cy + 2000,
                        "发电机风罩 \\U+00D810600", 2.5, 300)

    notes = [
        "发电机层高程 105.000m",
        "定子外径 9760，转子直径 7900",
        "风罩内径 10600，壁厚 300",
    ]
    proj.note_block(ox + 500, oy + LI + LU + 2000, 14000, notes)
    print("完成")

# =========================== 3. 水轮机层 ===========================
def draw_turbine_floor(proj):
    ox, oy = 3000, 3000
    s = 100
    print("  [水轮机层] 绘制结构...", end=" ")

    proj.rect(ox, oy, ox + SPAN, oy + LI + 2 * LU, "A-WALL-墙体", 0.35)
    cx, cy = ox + SPAN / 2, oy + LI + LU / 2
    proj.circle(cx, cy, HOOD_OD / 2, "M-HYDR-水力", 0.35)
    proj.circle(cx, cy, D1 / 2, "M-HYDR-水力", 0.50)

    # v8 新特性：蜗壳螺旋线
    proj.spiral_case(cx, cy, SC_R, 2.5, 200, "M-HYDR-水力")

    print("尺寸...", end=" ")
    proj.dim_radius(cx, cy, cx + SC_R, cy, f"R{SC_R//10//100:.1f}m", s)
    proj.dim_radius(cx, cy, cx, cy + SC_R, f"R{SC_R//10//100:.1f}m", s)
    proj.dim_diameter(cx, cy, HOOD_OD / 2, f"\\U+00D8{HOOD_OD//1000}.{HOOD_OD%1000//10:02d}m", s)
    proj.dim_h(oy - 2000, ox, ox + SPAN, f"跨度{SPAN//1000}m", s)

    # 尾水管
    dt_x = cx - DT_W / 2
    proj.rect(dt_x, oy - DT_H, dt_x + DT_W, oy, "S-FNDN-基础", 0.25)

    print("填充...", end=" ")
    proj.hatch_rect(dt_x + 50, oy - DT_H + 50, dt_x + DT_W - 50, oy - 50,
                     "ANSI31", 30, 8, "HATCH-填充")

    notes = [
        "水轮机层高程 98.500m",
        "转轮直径 3800，蜗壳最大半径 9270",
        "尾水管高度 10000，出口宽度 10340",
    ]
    proj.note_block(ox + 500, oy + LI + LU + 2000, 14000, notes)
    print("完成")

# =========================== 4. 蜗壳层 ===========================
def draw_spiral_case_floor(proj):
    ox, oy = 3000, 3000
    s = 100
    print("  [蜗壳层] 绘制结构...", end=" ")

    proj.rect(ox, oy, ox + SPAN, oy + LI + 2 * LU, "S-CONC-混凝土", 0.35)
    cx, cy = ox + SPAN / 2, oy + LI + LU / 2

    # 座环
    proj.circle(cx, cy, D1, "M-STRU-金属结构", 0.50)
    proj.circle(cx, cy, D1 * 0.7, "M-STRU-金属结构", 0.35)

    # 蜗壳螺旋线
    proj.spiral_case(cx, cy, SC_R, 2.0, 150, "M-HYDR-水力")

    print("尺寸...", end=" ")
    proj.dim_radius(cx, cy, cx + SC_R, cy - 500, f"R{SC_R//10//100:.1f}m", s)
    proj.dim_diameter(cx, cy, D1, f"座环\\U+00D8{D1//1000}.{D1%1000//10:02d}m", s)

    # 混凝土填充
    proj.hatch_rect(ox + 100, oy + 100, ox + SPAN - 100, oy + LI - 100,
                     "AR-CONC", 30, 8, "HATCH-填充")

    notes = [
        "蜗壳中心高程 95.670m",
        "座环外径 7600，蜗壳包角 345°",
        "蜗壳最大平面半径 9270",
    ]
    proj.note_block(ox + 500, oy + LI + LU + 2000, 14000, notes)
    print("完成")

# =========================== v8 存储测试 ===========================
def test_v8_features(proj):
    """演示 v8 新特性"""
    print()
    print("=" * 60)
    print("v8 新特性演示")
    print("=" * 60)

    # 1. 路径操作
    print("  [1/5] 路径操作 (fillet/chamfer/gear)...")
    pts = [(0, 0), (1000, 0), (1000, 800), (0, 800)]
    filleted = proj.path_fillet(pts, 100)
    print(f"       fillet: {len(filleted)} 点")

    # 2. 齿轮
    print("  [2/5] 齿轮绘制...")
    proj.draw_gear(0, 0, 16, 500, "M-STRU-金属结构")

    # 3. UCS 变换
    print("  [3/5] UCS 变换测试...")
    ucs = proj.with_ucs((2000, 0), 30)
    wcs_pts = proj.points_to_wcs([(0, 0), (100, 0), (0, 100)], ucs)
    print(f"       UCS → WCS: {[f'({p[0]:.0f},{p[1]:.0f})' for p in wcs_pts]}")

    # 4. 构造几何
    print("  [4/5] 构造几何...")
    pt = proj.construction_intersection((0, 0, 100, 100), (0, 100, 100, 0))
    print(f"       交点: {pt}")

    # 5. DXF 审计
    print("  [5/5] DXF 审计...")
    errors = proj.validate()
    if not errors:
        print("       [OK] 审计通过")


# =========================== 主程序 ===========================
def main():
    print("=" * 60)
    print("岩泊渡水电站施工图生成 v8 (全面升级版)")
    print("=" * 60)
    print()
    print("[1/4] 创建项目...")
    proj = HydroProjectV8("岩泊渡水电站", "v8-全面升级版").setup_all()
    print("      项目初始化完成")

    print()
    print("[2/4] 生成图纸...")
    draw_cross_section(proj)
    draw_generator_floor(proj)
    draw_turbine_floor(proj)
    draw_spiral_case_floor(proj)

    print()
    print("[3/4] 演示 v8 新特性...")
    test_v8_features(proj)

    print()
    print("[4/4] 保存文件...")
    proj.save("E:/CAD自动化制图/output/dxf/Yanbodu_v8_complete.dxf")

    print()
    print("=" * 60)
    print("生成完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
