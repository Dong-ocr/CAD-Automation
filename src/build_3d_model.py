"""岩泊渡水电站 3D 模型生成 (cadquery)"""
import sys, os, math
sys.path.insert(0, "E:/CAD自动化制图")
import cadquery as cq

# ================================ 尺寸数据 ================================
# 总体 (mm)
LEN_TOTAL   = 94000   # 总长
LEN_INSTALL = 20000   # 安装场
LEN_UNIT    = 30000   # 机组段
SPAN        = 17000   # 跨度
HEIGHT      = 40700   # 尾水管底到屋顶

# 高程 (mm)
EL_DT  = 0       # 尾水管底 (基准)
EL_TC  = 12170   # 蜗壳中心
EL_TF  = 15000   # 水轮机层
EL_GF  = 21500   # 发电机层
EL_CR  = 33500   # 吊车轨顶
EL_RF  = 40700   # 屋顶

# 设备 (mm)
STATOR_OD = 9760
ROTOR_D   = 7900
HOOD_OD   = 10600
SC_MAX_R  = 9270
D1        = 3800   # 转轮直径

# 立柱 (mm)
COL_W, COL_D = 600, 800

# ================================ 模型构建 ================================
def build_powerhouse():
    """构建水电站厂房 3D 模型"""
    result = cq.Assembly()
    
    # ---- 1. 底板 (尾水管底) ----
    base = cq.Workplane("XY").box(LEN_TOTAL, SPAN, 500)
    result.add(base, name="底板", color=cq.Color(0.5, 0.5, 0.5, 1))
    
    # ---- 2. 墙体 ----
    wall_thick = 400
    wall_h = EL_RF - 500
    # 2a. 上游墙 (长边)
    wall_front = (cq.Workplane("XY")
        .box(LEN_TOTAL, wall_thick, wall_h)
        .translate((0, -SPAN/2 + wall_thick/2, wall_h/2 + 500)))
    result.add(wall_front, name="上游墙", color=cq.Color(0.7, 0.7, 0.7, 1))
    
    # 2b. 下游墙
    wall_back = (cq.Workplane("XY")
        .box(LEN_TOTAL, wall_thick, wall_h)
        .translate((0, SPAN/2 - wall_thick/2, wall_h/2 + 500)))
    result.add(wall_back, name="下游墙", color=cq.Color(0.7, 0.7, 0.7, 1))
    
    # 2c. 左端墙
    wall_left = (cq.Workplane("XY")
        .box(wall_thick, SPAN - wall_thick*2, wall_h)
        .translate((-LEN_TOTAL/2 + wall_thick/2, 0, wall_h/2 + 500)))
    result.add(wall_left, name="左端墙", color=cq.Color(0.7, 0.7, 0.7, 1))
    
    # 2d. 右端墙
    wall_right = (cq.Workplane("XY")
        .box(wall_thick, SPAN - wall_thick*2, wall_h)
        .translate((LEN_TOTAL/2 - wall_thick/2, 0, wall_h/2 + 500)))
    result.add(wall_right, name="右端墙", color=cq.Color(0.7, 0.7, 0.7, 1))
    
    # ---- 3. 楼板 ----
    slab_thick = 500
    # 3a. 发电机层楼板
    gf_slab = (cq.Workplane("XY")
        .box(LEN_TOTAL - wall_thick*2, SPAN - wall_thick*2, slab_thick)
        .translate((0, 0, EL_GF + slab_thick/2)))
    result.add(gf_slab, name="发电机层楼板", color=cq.Color(0.6, 0.6, 0.6, 1))
    
    # 3b. 水轮机层楼板
    tf_slab = (cq.Workplane("XY")
        .box(LEN_TOTAL - wall_thick*2, SPAN - wall_thick*2, slab_thick)
        .translate((0, 0, EL_TF + slab_thick/2)))
    result.add(tf_slab, name="水轮机层楼板", color=cq.Color(0.6, 0.6, 0.6, 1))
    
    # ---- 4. 立柱 ----
    col_positions = [
        (-LEN_TOTAL/4, -SPAN/4),
        (-LEN_TOTAL/4,  SPAN/4),
        ( LEN_TOTAL/4, -SPAN/4),
        ( LEN_TOTAL/4,  SPAN/4),
    ]
    for i, (cx, cy) in enumerate(col_positions):
        col = (cq.Workplane("XY")
            .box(COL_W, COL_D, EL_GF - 500)
            .translate((cx, cy, (EL_GF - 500)/2 + 500)))
        result.add(col, name=f"立柱_{i+1}", color=cq.Color(0.4, 0.4, 0.8, 1))
    
    # ---- 5. 屋顶 ----
    roof_thick = 300
    roof = (cq.Workplane("XY")
        .box(LEN_TOTAL, SPAN, roof_thick)
        .translate((0, 0, EL_RF + roof_thick/2)))
    result.add(roof, name="屋顶", color=cq.Color(0.5, 0.5, 0.5, 1))
    
    # ---- 6. 吊车梁 ----
    crane_h = 800
    crane_l = SPAN - 2000
    # 吊车轨道 (- 沿长度方向)
    for dx in [-LEN_TOTAL/4, LEN_TOTAL/4]:
        crane_beam = (cq.Workplane("XY")
            .box(400, crane_l, crane_h)
            .translate((dx, 0, EL_CR + crane_h/2)))
        result.add(crane_beam, name=f"吊车梁_{dx}", color=cq.Color(0.8, 0.6, 0.2, 1))
    
    # 吊车 (简化)
    crane_body = (cq.Workplane("XY")
        .box(1500, 1000, 500)
        .translate((0, 0, EL_CR + crane_h + 250)))
    result.add(crane_body, name="吊车", color=cq.Color(0.9, 0.7, 0.0, 1))
    
    # ---- 7. 发电机(简化) ----
    gen = (cq.Workplane("XY")
        .cylinder(HOOD_OD/2, 2000)
        .translate((0, 0, EL_GF + 1000)))
    result.add(gen, name="发电机", color=cq.Color(0.2, 0.6, 0.8, 1))
    
    # 定子
    stator = (cq.Workplane("XY")
        .cylinder(STATOR_OD/2, 1500)
        .translate((0, 0, EL_GF + 750)))
    result.add(stator, name="定子", color=cq.Color(0.3, 0.7, 0.3, 1))
    
    # ---- 8. 水轮机(简化) ----
    turbine = (cq.Workplane("XY")
        .cylinder(D1/2, 1500)
        .translate((0, 0, EL_TC)))
    result.add(turbine, name="水轮机", color=cq.Color(0.8, 0.3, 0.3, 1))
    
    # 蜗壳螺旋线 (用圆环近似)
    spiral = (cq.Workplane("XY")
        .cylinder(SC_MAX_R, 300)
        .translate((0, 0, EL_TC - 150)))
    # 挖空中间
    spiral_cut = cq.Workplane("XY").cylinder(D1 * 0.8, 500)
    spiral = spiral.cut(spiral_cut.translate((0, 0, EL_TC - 250)))
    result.add(spiral, name="蜗壳", color=cq.Color(0.6, 0.3, 0.6, 1))
    
    # ---- 9. 安装场 ----
    install_floor = (cq.Workplane("XY")
        .box(LEN_INSTALL - wall_thick*2, SPAN - wall_thick*2, 300)
        .translate((-LEN_TOTAL/2 + LEN_INSTALL/2, 0, EL_GF + 150)))
    result.add(install_floor, name="安装场", color=cq.Color(0.7, 0.7, 0.3, 1))
    
    return result


# ================================ 导出 ================================
if __name__ == "__main__":
    print("构建厂房 3D 模型...")
    model = build_powerhouse()
    
    # 导出 STEP
    step_path = "E:/CAD自动化制图/output/step/yanbodu_3d_powerhouse.step"
    cq.exporters.export(model.toCompound(), step_path, exportType="STEP")
    print(f"  STEP: {step_path}")
    
    # 导出 SVG 预览
    svg_path = "E:/CAD自动化制图/output/svg/yanbodu_3d_preview.svg"
    cq.exporters.export(model.toCompound(), svg_path, exportType="SVG")
    print(f"  SVG:  {svg_path}")
    
    print("完成!")
