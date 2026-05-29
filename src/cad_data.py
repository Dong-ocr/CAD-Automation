"""
cad_data.py — 水电站 CAD 数据模型 (类型安全 · 数据驱动)
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum


class Layer(Enum):
    """国标图层枚举 (GB/T 50001-2017)"""
    BUILDING = "0-建筑"
    CONCRETE = "S-CONC-混凝土"
    REBAR = "S-REIN-钢筋"
    EQUIPMENT = "M-EQPM-设备"
    HYDRAULIC = "M-HYDR-水力"
    WALL = "A-WALL-墙体"
    COLUMN = "A-COLM-立柱"
    CRANE = "A-OVHD-吊车"
    FLOOR = "A-FLOR-楼面"
    ROOF = "A-ROOF-屋面"
    DIM = "DIM-尺寸"
    TEXT = "TEXT-文字"
    HATCH = "HATCH-填充"
    SYMBOL = "SYMB-符号"
    AXIS = "AXIS-轴线"
    HIDDEN = "HIDN-隐藏"
    BORDER = "BORD-图框"
    TITLE = "TBLK-标题栏"
    LEADER = "LEAD-引线"
    NOTE = "NOTE-说明"


class HatchPattern(Enum):
    """常用填充图案"""
    CONCRETE = "ANSI31"
    STEEL = "ANSI32" 
    EARTH = "AR-SAND"
    GRAVEL = "GRAVEL"
    BRICK = "BRICK"
    CONCRETE_DOT = "AR-CONC"


@dataclass
class Point:
    x: float = 0.0
    y: float = 0.0

    def tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass
class Line:
    p1: Point
    p2: Point
    layer: str = Layer.BUILDING.value
    lineweight: float = 0.18


@dataclass
class Rect:
    x1: float = 0
    y1: float = 0
    x2: float = 1000
    y2: float = 1000
    layer: str = Layer.BUILDING.value
    lineweight: float = 0.18


@dataclass
class Circle:
    x: float = 0
    y: float = 0
    radius: float = 100
    layer: str = Layer.BUILDING.value
    lineweight: float = 0.18


@dataclass
class Dimension:
    """尺寸标注"""
    type: str = "linear"  # linear, radius, diameter, angular
    x1: float = 0
    y1: float = 0
    x2: float = 0
    y2: float = 0
    base: float = 0  # 尺寸线位置
    text: str = ""
    scale: int = 100


@dataclass
class TextLabel:
    text: str = ""
    x: float = 0
    y: float = 0
    height: float = 2.5
    layer: str = Layer.TEXT.value
    align: str = "left"  # left, center, right


@dataclass
class Hatch:
    points: List[Point] = field(default_factory=list)
    pattern: str = HatchPattern.CONCRETE.value
    scale: float = 100
    color: int = 8
    layer: str = Layer.HATCH.value


# ===== 厂房数据模型 =====

@dataclass
class PowerhouseData:
    """水电站厂房核心数据"""
    # 高程 (mm)
    el_dt_bottom: float = 83500    # 尾水管底
    el_spiral_center: float = 95670  # 蜗壳中心
    el_turbine_floor: float = 98500  # 水轮机层
    el_gen_floor: float = 105000    # 发电机层
    el_crane_rail: float = 117000   # 吊车轨顶
    el_roof: float = 124200         # 屋顶

    # 尺寸 (mm)
    total_length: float = 94000     # 总长
    unit_length: float = 30000      # 机组段长
    install_length: float = 20000   # 安装场长
    span: float = 17000             # 跨度
    crane_span: float = 16500       # 吊车跨度

    # 设备 (mm)
    stator_od: float = 9760         # 定子外径
    rotor_diameter: float = 7900    # 转子直径
    hood_od: float = 10600          # 机坑盖板直径
    sc_max_radius: float = 9270     # 蜗壳最大半径
    dt_height: float = 10000        # 尾水管高度
    dt_width: float = 10340         # 尾水管宽度
    runner_diameter: float = 3800   # 转轮直径

    # 立柱 (mm)
    col_up_w: float = 600
    col_up_d: float = 800
    col_dw_w: float = 600
    col_dw_d: float = 1000

    def validate(self) -> List[str]:
        """数据校验，返回错误列表"""
        errors = []
        if self.total_length <= 0: errors.append("总长必须 > 0")
        if self.span <= 0: errors.append("跨度必须 > 0")
        if self.el_roof <= self.el_dt_bottom: errors.append("屋顶高程必须高于尾水管底")
        if self.stator_od <= 0: errors.append("定子外径必须 > 0")
        return errors
