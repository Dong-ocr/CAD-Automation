
# ====================================================================
#  gen_v7_pro.py — 岩泊渡水电站 v7.0 四张专业施工图（全面升级版）
#  特点: 真实蜗壳螺旋线、完整尺寸链、专业图框、施工说明、材料表
# ====================================================================
import sys, os, math
sys.path.insert(0, 'E:/CAD自动化制图')
from cad_toolbox_v7 import HydroProject

# =========================== 项目数据 ===========================
# 高程 (mm)
E_DT  = 83500   # 尾水管底
E_TC  = 95670   # 蜗壳中心
E_TF  = 98500   # 水轮机层
E_GF  = 105000  # 发电机层
E_CR  = 117000  # 吊车轨顶
E_RF  = 124200  # 屋顶

# 尺寸 (mm)
LT  = 94000    # 总长 (安装场20m + 机组段30m + 机组段30m = 80m, 加两端)
LU  = 30000    # 机组段长
LI  = 20000    # 安装场长
SPAN = 17000   # 跨度 (净跨)
LK  = 16500    # 吊车跨度
AXIS_SP = 6000 # 轴间距

# 设备参数
STATOR_OD = 9760  # 定子外径
ROTOR_D   = 7900  # 转子直径
HOOD_OD   = 10600 # 机坑盖板直径
SC_R      = 9270  # 蜗壳最大半径
DT_H      = 10000 # 尾水管高度
DT_W      = 10340 # 尾水管宽度
D1        = 3800  # 水轮机转轮直径

# 立柱
CU_W, CU_D = 600, 800   # 上游柱
CD_W, CD_D = 600, 1000  # 下游柱

# 材料表
MATERIALS = [
    ('C30 混凝土', 'm³', 2850, '主厂房结构'),
    ('C25 混凝土', 'm³', 1260, '蜗壳外围'),
    ('HRB400 钢筋', 't', 320, 'Φ25/Φ22'),
    ('HPB300 钢筋', 't', 85,  'Φ12/Φ10'),
    ('Q355B 钢结构', 't', 180, '吊车梁/屋架'),
    ('SF48.1-44/9760', '台', 3, '发电机'),
    ('HL240-LJ-380', '台', 3, '水轮机'),
    ('250/50t 桥吊', '台', 1, '桥式起重机'),
    ('蜗壳钢板 δ=25mm', 't', 45, ''),
]

# 施工说明
CROSS_NOTES = [
    '本图尺寸单位mm，高程单位m',
    '混凝土强度等级：主厂房C30，蜗壳外围C25',
    '钢筋保护层厚度：梁柱35mm，板20mm',
    '图中高程为黄海高程系统',
    '施工时应与地质、机电专业图纸配合使用',
]
PLAN_NOTES = [
    '本图尺寸单位mm',
    '机组中心线偏差不超过±2mm',
    '安装场地面荷载按30kN/m²设计',
    '图中虚线为下层轮廓投影线',
    '预埋件位置详见埋件布置图',
]

OUT_DIR = 'E:/CAD自动化制图'

def save_final(proj, sname):
    if 'Layout1' in [l.name for l in proj.doc.layouts]:
        proj.doc.layouts.delete('Layout1')
    path = os.path.join(OUT_DIR, f'Yanbodu_{sname}_v7.dxf')
    proj.save(path)
    return path

# ====================================================================
#  1. 主厂房横剖面图 — 1:100
# ====================================================================
def gen_cross_section():
    print('  [1/4] 主厂房横剖面图...')
    proj = HydroProject()
    ux = -(SPAN/2 - 2000)   # 上游柱中心
    dx = SPAN/2 - 3000      # 下游柱中心
    ct = E_CR + 2200        # 屋顶下弦

    # ---- 地面与地基 ----
    proj.line(-SPAN, E_DT-500, SPAN, E_DT-500, '0-建筑', 0.5)
    proj.text('地面', SPAN+2000, E_DT-500-1500, 2.5)

    # ---- 地基轮廓 ----
    fnd_pts = [(-SPAN/2-2000, E_DT-500), (-SPAN/2-2000, E_DT-3000),
               (SPAN/2+2000, E_DT-3000), (SPAN/2+2000, E_DT-500)]
    proj.polyline(fnd_pts, 'FNDN-基础', 0.25)
    proj.hatch_fill(fnd_pts, 'AR-HBONE', 500, color=9, layer='HATCH-填充')

    # ---- 尾水管 ----
    dt_pts = [(0, E_TC)]
    for t in [i/36 for i in range(37)]:
        r = DT_W/2 * (0.3 + 0.7*t)
        dt_pts.append((r, E_DT + DT_H*(1-t)))
    for t in [i/36 for i in range(37)]:
        r = DT_W/2 * (0.3 + 0.7*(1-t))
        dt_pts.append((-r, E_DT + DT_H*t))
    dt_pts.append((0, E_TC))
    proj.polyline(dt_pts, 'S-CONC-混凝土', 0.35)
    proj.hatch_fill(dt_pts, 'ANSI31', 200, color=9, layer='HATCH-填充')
    proj.text('尾水管', DT_W/2+3000, E_DT+DT_H*0.5, 2.5)

    # ---- 蜗壳（真实螺旋线） ----
    sc_pts = []
    n_spiral = 120
    for i in range(n_spiral+1):
        a = math.radians(360*i/n_spiral)
        r_max = SC_R
        r = r_max * max(0.08 + 0.92*(1-i/n_spiral), 0.03)
        sc_pts.append((r*math.cos(a), E_TC + r*math.sin(a)))
    proj.polyline(sc_pts, 'M-HYDR-水力', 0.6)
    # 蜗壳填充
    proj.hatch_fill(sc_pts, 'ANSI32', 300, color=4, layer='HATCH-填充')
    proj.text_c(f'蜗壳 R={SC_R}mm', SC_R*0.4, E_TC+SC_R*0.6, 2.5, 'M-HYDR-水力')

    # ---- 座环 ----
    proj.circle(0, E_TC, D1/2+800, 'M-STRU-结构', 0.5)
    proj.circle(0, E_TC, D1/2, 'M-HYDR-水力', 0.35)
    proj.text_c('座环', 0, E_TC-D1/2-1500, 2.5, 'M-STRU-结构')

    # ---- 水轮机 ----
    proj.circle(0, E_TC, D1/2+200, 'M-EQPM-设备', 0.4)
    proj.text_c('HL240-LJ-380', 0, E_TC-4500, 2.5)
    proj.text_c('水轮机', 0, E_TC+4500, 3.0, 'M-EQPM-设备')

    # ---- 发电机 ----
    gc = E_TF + (E_GF - E_TF) * 0.55
    proj.circle(0, gc, STATOR_OD/2, 'M-EQPM-设备', 0.5)
    proj.circle(0, gc, ROTOR_D/2, 'AXIS-轴线', 0.18)
    st_pts = [(STATOR_OD/2*math.cos(math.radians(360*i/36)),
               gc+STATOR_OD/2*math.sin(math.radians(360*i/36))) for i in range(37)]
    proj.hatch_fill(st_pts, 'ANSI31', 200, color=8, layer='HATCH-填充')
    proj.text_c('SF48.1-44/9760', 0, gc, 3.0)
    proj.text_c('发电机', 0, gc+STATOR_OD/2+1500, 3.0, 'M-EQPM-设备')

    # ---- 机坑盖板 ----
    proj.line(-HOOD_OD/2, E_GF-200, -HOOD_OD/2, E_GF+200, 'M-STRU-结构', 0.35)
    proj.line(HOOD_OD/2, E_GF-200, HOOD_OD/2, E_GF+200, 'M-STRU-结构', 0.35)
    proj.line(-HOOD_OD/2, E_GF, HOOD_OD/2, E_GF, 'M-STRU-结构', 0.35)
    proj.text_c('机坑盖板', HOOD_OD/2+2000, E_GF, 2.5, 'M-STRU-结构')

    # ---- 立柱 ----
    for cx, cw, cd in [(ux, CU_W, CU_D/2), (dx, CD_W, CD_D/2)]:
        proj.rect(cx-cw/2, E_TF, cx+cw/2, ct, 'A-COLM-立柱', 0.5)
        col_pts = [(cx-cw/2,E_TF),(cx+cw/2,E_TF),(cx+cw/2,ct),(cx-cw/2,ct)]
        proj.hatch_solid(col_pts, color=252, layer='HATCH-填充')
    # 柱基
    proj.rect(ux-CU_W/2-500, E_DT-500, ux+CU_W/2+500, E_TF, 'FNDN-基础', 0.25)
    proj.rect(dx-CD_W/2-500, E_DT-500, dx+CD_W/2+500, E_TF, 'FNDN-基础', 0.25)

    # ---- 牛腿 ----
    bracket_h = 1200
    for cx, cw in [(ux, CU_W), (dx, CD_W)]:
        proj.rect(cx-cw/2-300, E_CR-bracket_h, cx+cw/2+300, E_CR, 'A-COLM-立柱', 0.35)
    proj.text_c('牛腿', ux+CU_W/2+1800, E_CR-bracket_h/2, 2.5, 'A-COLM-立柱')

    # ---- 楼层线 ----
    floors = [(E_DT, '尾水管底'), (E_TC, '蜗壳中心'), (E_TF, '水轮机层'),
              (E_GF, '发电机层'), (E_CR, '吊车轨顶'), (E_RF, '屋顶')]
    for el, lbl in floors:
        proj.line(-SPAN, el, SPAN, el, 'A-FLOR-楼面', 0.18)
        proj.text(lbl, -SPAN-3000, el, 2.5, 'A-FLOR-楼面', rot=90)

    # ---- 吊车梁 ----
    proj.rect(-LK/2, E_CR+200, LK/2, E_CR+1000, 'A-OVHD-吊车', 0.35)
    proj.hatch_solid([(-LK/2,E_CR+200),(LK/2,E_CR+200),(LK/2,E_CR+1000),(-LK/2,E_CR+1000)],
                     color=253, layer='HATCH-填充')
    proj.text_c('250/50t 桥式起重机', 0, E_CR+600, 3.0, 'A-OVHD-吊车')
    proj.text_c('桥吊', 0, E_CR-500, 2.5, 'A-OVHD-吊车')

    # ---- 屋架 ----
    proj.rect(-SPAN/2+500, ct-800, SPAN/2-500, ct, 'A-ROOF-屋面', 0.5)
    proj.hatch_solid([(-SPAN/2+500,ct-800),(SPAN/2-500,ct-800),(SPAN/2-500,ct),(-SPAN/2+500,ct)],
                     color=251, layer='HATCH-填充')
    # 屋顶坡
    proj.line(-SPAN/2+500, E_RF, 0, E_RF+2000, 'A-ROOF-屋面', 0.18)
    proj.line(0, E_RF+2000, SPAN/2-500, E_RF, 'A-ROOF-屋面', 0.18)
    # 通风帽
    proj.rect(-3000, E_RF, 3000, E_RF+3000, 'A-ROOF-屋面', 0.35)
    proj.line(-3000, E_RF+3000, -1500, E_RF+3500, 'A-ROOF-屋面', 0.18)
    proj.line(1500, E_RF+3500, 3000, E_RF+3000, 'A-ROOF-屋面', 0.18)
    proj.text_c('通风帽', 0, E_RF+1500, 2.5)

    # ---- 中心线 ----
    proj.axis_line(-SC_R*2, E_TC, SC_R*2, E_TC)
    proj.axis_line(0, E_DT-1000, 0, E_RF+2000)
    proj.text_c('机组中心线', 0, E_RF+3500, 2.5, 'AXIS-轴线')

    # ---- 剖切线 A-A ----
    proj.section_line('A', [(-SPAN-2000, E_TC), (-SPAN/2, E_TC)])
    proj.section_line('A', [(SPAN/2, E_TC), (SPAN+2000, E_TC)])

    # ---- 引线标注 ----
    proj.add_leader(0, gc+STATOR_OD/2+1000, -SPAN/3, gc+STATOR_OD/2+4000,
                    '定子外径 Φ9760', 3.0, 500)
    proj.add_leader(SC_R*0.7, E_TC+SC_R*0.7, SPAN/3+2000, E_TC-3000,
                    '蜗壳最高点', 3.0, 500)
    proj.add_leader(ux, ct+800, -SPAN/2-2000, ct+4000,
                    '上游柱 600×800', 3.0, 500)

    # ---- 尺寸链（竖向） ----
    segs = [(E_DT, E_TF, 'H1=15000'), (E_TF, E_GF, 'H2=6500'),
            (E_GF, E_CR, 'H3=12000'), (E_CR, E_RF, 'H4=7200')]
    proj.dim_chain_v(LK/2+12000, segs, scale=100)
    # 总高
    proj.dim_v(LK/2+10000, E_DT, E_RF, text=f'H={E_RF-E_DT}mm', scale=100)

    # ---- 尺寸链（横向） ----
    h_segs = [(-SPAN/2, ux-CU_W/2, ''), (ux-CU_W/2, ux+CU_W/2, '600'),
              (ux+CU_W/2, dx-CD_W/2, f'B={dx-ux-CU_W/2-CD_W/2}'),
              (dx-CD_W/2, dx+CD_W/2, '600'), (dx+CD_W/2, SPAN/2, '')]
    proj.dim_chain_v(0, h_segs, scale=100)

    # ---- 高程标注 ----
    for el, nm in [(E_DT,'尾水管底'),(E_TC,'蜗壳中心'),(E_TF,'水轮机层'),
                   (E_GF,'发电机层'),(E_CR,'吊车轨顶'),(E_RF,'屋顶')]:
        proj.elevation(-LK/2-16000, el, el/1000, nm, 2.5)

    # ---- 说明 ----
    proj.note_block(-SPAN, E_DT-8000, 20000, CROSS_NOTES, '图纸说明')

    # ---- Paper Space ----
    vc = (0, (E_DT+E_RF)/2)
    layout, pw, ph = proj.create_layout('横剖面', 'A1', 100, vc, border_mm=15, landscape=False)
    proj.title_block(layout, pw-240, 0, 240, 60, {
        'project':'岩泊渡水电站', 'dname':'主厂房横剖面图', 'dno':'YBD-01',
        'scale':'1:100', 'date':'2026.05', 'size':'A1',
        'designer':'张', 'checker':'李', 'auditor':'王',
    })
    proj.material_table(layout, 15, 15, 300, MATERIALS)
    proj.note_block_ps(layout, pw-240, 65, 240, CROSS_NOTES, '图纸说明')
    return save_final(proj, 'Cross_Section')


# ====================================================================
#  2~4. 平面图生成器
# ====================================================================
def gen_plan(sname, title, dno, scale=150):
    names = {
        'Generator_Floor': '发电机层平面图',
        'Turbine_Floor':   '水轮机层平面图',
        'Spiral_Case_Floor': '蜗壳层平面图',
    }
    idx = ['Generator_Floor','Turbine_Floor','Spiral_Case_Floor'].index(sname)
    print(f'  [{idx+2}/4] {title}...')

    proj = HydroProject()

    # ---- 轴线网 ----
    n_ax_x = int(LT // AXIS_SP) + 1
    n_ax_y = int(SPAN // AXIS_SP) + 1
    for i in range(n_ax_x):
        x = -LT/2 + i*AXIS_SP
        proj.axis_line(x, -SPAN/2-2000, x, SPAN/2+2000)
        proj.axis_circle(x, -SPAN/2-2500, chr(65+i) if i<26 else f'A{i}')
    for j in range(n_ax_y):
        y = -SPAN/2 + j*AXIS_SP
        proj.axis_line(-LT/2-2000, y, LT/2+2000, y)
        proj.axis_circle(-LT/2-2500, y, j+1, 450, 3.0)

    # ---- 厂房外墙 ----
    wall_thk = 500
    proj.rect(-LT/2-wall_thk, -SPAN/2-wall_thk,
              LT/2+wall_thk, SPAN/2+wall_thk, 'A-WALL-墙体', 0.5)
    # 外墙填充
    wall_pts = [(-LT/2-wall_thk, -SPAN/2-wall_thk),
                (LT/2+wall_thk, -SPAN/2-wall_thk),
                (LT/2+wall_thk, SPAN/2+wall_thk),
                (-LT/2-wall_thk, SPAN/2+wall_thk)]
    proj.hatch_fill(wall_pts, 'ANSI31', 300, color=9, layer='HATCH-填充')
    # 内墙线
    proj.rect(-LT/2, -SPAN/2, LT/2, SPAN/2, '0-建筑', 0.18)

    # ---- 立柱布置 ----
    col_positions = []
    for i in range(2):  # 上下游
        cy = (-SPAN/2+1000) if i==0 else (SPAN/2-1000)
        col_positions.append((-LT/2+3000, cy))
        col_positions.append((-LT/2+LI-3000, cy))
        col_positions.append((-LT/2+LI+3000, cy))
        col_positions.append((-LT/2+LI+LU-3000, cy))
        col_positions.append((-LT/2+LI+LU+3000, cy))
        col_positions.append((LT/2-3000, cy))

    for cx, cy in col_positions:
        cw, cd = (CU_W, CU_D) if cy < 0 else (CD_W, CD_D)
        proj.rect(cx-cw/2, cy-cd/2, cx+cw/2, cy+cd/2, 'A-COLM-立柱', 0.5)
        col_pts = [(cx-cw/2,cy-cd/2),(cx+cw/2,cy-cd/2),
                   (cx+cw/2,cy+cd/2),(cx-cw/2,cy+cd/2)]
        proj.hatch_solid(col_pts, color=252, layer='HATCH-填充')

    # ---- 机组 ----
    for unit in range(3):
        ucx = -LT/2 + LI + unit*LU + LU/2

        # 蜗壳 (真实螺旋)
        if sname == 'Spiral_Case_Floor':
            sc_pts = []
            n_s = 80
            for i in range(n_s+1):
                a = math.radians(360*i/n_s)
                r = SC_R * max(0.08 + 0.92*(1-i/n_s), 0.03)
                sc_pts.append((ucx+r*math.cos(a), r*math.sin(a)))
            proj.polyline(sc_pts, 'M-HYDR-水力', 0.6)
            proj.hatch_fill(sc_pts, 'ANSI32', 300, color=4, layer='HATCH-填充')
            # 座环
            proj.circle(ucx, 0, D1/2+800, 'M-STRU-结构', 0.4)
            proj.circle(ucx, 0, D1/2, 'M-EQPM-设备', 0.35)
            proj.text_c(f'#{unit+1} 蜗壳 R={SC_R//1000}m', ucx, SC_R+2000, 2.5, 'M-HYDR-水力')

        # 水轮机层特有
        if sname == 'Turbine_Floor':
            proj.circle(ucx, 0, D1/2+1000, 'M-STRU-结构', 0.5)
            proj.circle(ucx, 0, STATOR_OD/2, 'HIDN-隐藏', 0.25)
            td_pts = [(ucx+(D1/2+1000)*math.cos(math.radians(360*i/36)),
                       0+(D1/2+1000)*math.sin(math.radians(360*i/36))) for i in range(37)]
            proj.hatch_fill(td_pts, 'ANSI31', 300, color=8, layer='HATCH-填充')
            proj.text_c(f'#{unit+1} 水轮机坑', ucx, D1/2+2000, 2.5, 'M-STRU-结构')
            # 冷却水管示意
            proj.circle(ucx, 0, D1+3000, 'HIDN-隐藏', 0.13)
            proj.text('冷却水管', ucx+D1+3000+500, 500, 2.0, 'HIDN-隐藏')

        # 发电机层特有
        if sname == 'Generator_Floor':
            proj.circle(ucx, 0, HOOD_OD/2, 'HIDN-隐藏', 0.25)
            proj.rect(ucx-3000, 3000, ucx+3000, 5000, 'HIDN-隐藏', 0.18)
            proj.text_c('吊物孔', ucx, 4000, 2.5)
            proj.text_c('SF48.1-44/9760', ucx, -5000, 2.5, 'M-EQPM-设备')

        # 通用: 定子/转子
        proj.circle(ucx, 0, STATOR_OD/2, 'M-EQPM-设备', 0.5)
        st_pts2 = [(ucx+STATOR_OD/2*math.cos(math.radians(360*i/36)),
                    0+STATOR_OD/2*math.sin(math.radians(360*i/36))) for i in range(37)]
        proj.hatch_fill(st_pts2, 'ANSI31', 200, color=8, layer='HATCH-填充')
        proj.circle(ucx, 0, ROTOR_D/2, 'AXIS-轴线', 0.2)
        proj.text_c(f'#{unit+1} 机组', ucx, 0, 4.0)

    # ---- 安装场 ----
    proj.rect(-LT/2, -SPAN/2, -LT/2+LI, SPAN/2, 'HIDN-隐藏', 0.25)
    proj.hatch_fill([(-LT/2,-SPAN/2),(-LT/2+LI,-SPAN/2),
                     (-LT/2+LI,SPAN/2),(-LT/2,SPAN/2)],
                    'ANSI37', 200, color=9, layer='HATCH-填充')
    proj.text_c('安装场 20m×17m', -LT/2+LI/2, 0, 4.0)

    # ---- 楼梯 ----
    for i in range(2):
        sx = -LT/2 + LI + (i+1)*LU*0.8
        proj.rect(sx, SPAN/2-3000, sx+3500, SPAN/2-1000, '0-建筑', 0.18)
        # 踏步示意
        for j in range(6):
            sy = SPAN/2-3000 + j*300
            proj.line(sx, sy, sx+3500, sy, '0-建筑', 0.13)
        proj.text_c('楼梯', sx+1750, SPAN/2-2000, 2.5)
        # 另一侧
        proj.rect(sx, -SPAN/2+1000, sx+3500, -SPAN/2+3000, '0-建筑', 0.18)
        for j in range(6):
            sy = -SPAN/2+1000 + j*300
            proj.line(sx, sy, sx+3500, sy, '0-建筑', 0.13)
        proj.text_c('楼梯', sx+1750, -SPAN/2+2000, 2.5)

    # ---- 门洞 ----
    door_w = 3000
    for side in [-1, 1]:
        proj.line(side*LT/2, -door_w/2, side*(LT/2+wall_thk+200), -door_w/2, 'A-WALL-墙体', 0.35)
        proj.line(side*LT/2, door_w/2, side*(LT/2+wall_thk+200), door_w/2, 'A-WALL-墙体', 0.35)
        proj.arc(side*LT/2, 0, door_w/2, 90-90*side, 180-90*side, '0-建筑', 0.18)
        proj.text_c('大门', side*LT/2+wall_thk+1500, 0, 2.5)

    # ---- 上下游标注 ----
    proj.text_c('上游侧', 0, -SPAN/2-4500, 3.5)
    proj.text_c('下游侧', 0, SPAN/2+4500, 3.5)

    # ---- 引线标注 ----
    if sname == 'Spiral_Case_Floor':
        proj.add_leader(-LT/2+LI+LU/2, SC_R, -LT/2+LI-5000, SC_R+5000,
                        '蜗壳中心线', 3.0, 500)
        proj.add_leader(-LT/2+LI+LU+LU/2+3000, -SC_R-2000,
                        -LT/2+LI+LU+LU/2+8000, -SC_R-5000,
                        '引水管中心线', 3.0, 500)
    elif sname == 'Turbine_Floor':
        proj.add_leader(-LT/2+LI+LU/2, STATOR_OD/2+2000,
                        -LT/2+LI-5000, STATOR_OD/2+5000,
                        '水轮机座环', 3.0, 500)
        proj.add_leader(-LT/2+LI+LU+LU/2, -STATOR_OD/2-2000,
                        -LT/2+LI+LU+LU/2+5000, -STATOR_OD/2-5000,
                        '应力扩散锥', 3.0, 500)
    elif sname == 'Generator_Floor':
        proj.add_leader(-LT/2+LI+LU/2, HOOD_OD/2+2000,
                        -LT/2+LI-5000, HOOD_OD/2+5000,
                        '发电机机坑盖板', 3.0, 500)
        proj.add_leader(-LT/2+LI+LU+LU/2, STATOR_OD/2+2000,
                        -LT/2+LI+LU+LU, STATOR_OD/2+5000,
                        '出线盒位置', 3.0, 500)

    # ---- 尺寸标注 ----
    # 总长尺寸
    proj.dim_h(-SPAN/2-6000, -LT/2-wall_thk, LT/2+wall_thk,
               text=f'总长 L={LT//1000}m', scale=scale)
    # 分段尺寸
    segs = [(-LT/2, -LT/2+LI, f'安装场 {LI//1000}m'),
            (-LT/2+LI, -LT/2+LI+LU, f'机组段 {LU//1000}m'),
            (-LT/2+LI+LU, LT/2, f'机组段 {LU//1000}m')]
    proj.dim_chain_h(-SPAN/2-10000, segs, scale=scale)
    # 跨度
    proj.dim_v(LT/2+6000, -SPAN/2, SPAN/2, text=f'跨度 {SPAN//1000}m', scale=scale)

    # ---- 高程标注 ----
    if sname == 'Generator_Floor':
        proj.elevation(-LT/2-4000, -SPAN/2-1000, E_GF/1000, '发电机层高程', 2.5)
    elif sname == 'Turbine_Floor':
        proj.elevation(-LT/2-4000, -SPAN/2-1000, E_TF/1000, '水轮机层高程', 2.5)
    elif sname == 'Spiral_Case_Floor':
        proj.elevation(-LT/2-4000, -SPAN/2-1000, E_TC/1000, '蜗壳层高程', 2.5)

    # ---- 说明 ----
    notes = list(PLAN_NOTES)
    if sname == 'Spiral_Case_Floor':
        notes += ['蜗壳采用钢板焊接结构，板厚25mm',
                  '蜗壳外围回填C25混凝土',
                  '蜗壳进口断面尺寸需根据水力学计算确定']
    proj.note_block(-LT/2, -SPAN/2-12000, 22000, notes, '图纸说明')

    # ---- Paper Space ----
    vc = (0, 0)
    layout, pw, ph = proj.create_layout(title, 'A1', scale, vc, border_mm=15, landscape=True)
    proj.title_block(layout, pw-240, 0, 240, 60, {
        'project':'岩泊渡水电站', 'dname':names[sname], 'dno':dno,
        'scale':f'1:{scale}', 'date':'2026.05',
        'designer':'张', 'checker':'李', 'auditor':'王', 'size':'A1',
    })
    if sname == 'Generator_Floor':
        proj.material_table(layout, 15, 15, 300, MATERIALS)
    proj.note_block_ps(layout, pw-240, 65, 240, notes, '图纸说明')
    return save_final(proj, sname)


# ====================================================================
#  主程序
# ====================================================================
if __name__ == '__main__':
    print('=' * 60)
    print('  岩泊渡水电站 施工图 v7.0 专业级')
    print('=' * 60)
    results = []
    results.append(gen_cross_section())
    results.append(gen_plan('Generator_Floor', '发电机层平面图', 'YBD-02', 150))
    results.append(gen_plan('Turbine_Floor',   '水轮机层平面图', 'YBD-03', 150))
    results.append(gen_plan('Spiral_Case_Floor', '蜗壳层平面图', 'YBD-04', 150))
    print()
    print('=' * 60)
    print('  v7.0 四张专业施工图完成!')
    print('=' * 60)
    for path in results:
        if os.path.exists(path):
            print(f'  ✓ {os.path.basename(path)} ({os.path.getsize(path)/1024:.0f} KB)')
    print(f'  文件位置: {OUT_DIR}')
