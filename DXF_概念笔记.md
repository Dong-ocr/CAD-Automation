# CAD 实体（Entities）概念笔记

## 什么是实体（Entity）？

在 DXF 中，**实体**是图纸中最基本的"几何积木"。每一个具体的图形元素都是一个实体。

常见实体类型：
- `LINE` —— 直线段
- `CIRCLE` —— 圆
- `ARC` —— 圆弧
- `TEXT` —— 文字
- `INSERT` —— 块引用（插入已定义的块）
- `LWPOLYLINE` —— 轻量多段线
- `DIMENSION` —— 尺寸标注

## ezdxf 中的对应 API

| 实体类型 | ezdxf API | 参数示例 |
|---------|-----------|---------|
| 直线 | `msp.add_line(start, end)` | `(0,0), (100,0)` |
| 圆 | `msp.add_circle(center, radius)` | `(0,0), 50` |
| 圆弧 | `msp.add_arc(center, radius, start_angle, end_angle)` | `(0,0), 50, 0, 180` |
| 文字 | `msp.add_text(text, height, dxfattribs)` | `"Hello", 10` |
| 多段线 | `msp.add_lwpolyline(points)` | `[(0,0), (10,0), (10,10)]` |

## 图层（Layer）

图层是组织实体的逻辑容器。每个实体必须属于一个图层（默认在 "0" 层）。

### 为什么使用图层？

| 场景 | 不用图层 | 用图层 |
|------|---------|-------|
| 修改颜色 | 逐条修改实体 | 改图层颜色，所有实体自动变化 |
| 打印控制 | 无法批量控制 | 关闭图层打印即可 |
| 冻结/锁定 | 无法锁定部分图元 | 冻结图层，整层不可见 |
| 专业规范 | 不符合行业标准 | 符合 GB / ISO 图层标准 |

### ezdxf 中操作图层

```python
# 创建图层
doc.layers.new("MY_LAYER", dxfattribs={
    "color": 2,                  # ACI 颜色
    "linetype": "CONTINUOUS",    # 线型
})

# 绘制时指定图层
msp.add_circle((0,0), 50, dxfattribs={"layer": "MY_LAYER"})
```

## 线型（Linetype）

线型定义实体的外观模式（实线、虚线、点划线等）。

### 内置线型
AutoCAD / DXF 标准内置线型：

| 线型名 | 外观 | 用途 |
|--------|------|------|
| `CONTINUOUS` | 实线（———） | 轮廓线、可见边 |
| `DASHED` | 虚线（- - -） | 隐藏边、不可见轮廓 |
| `CENTER` | 点划线（—·—·—） | 中心线、对称轴 |
| `DASHDOT` | 双点划线（—··—··） | 假想线、极限位置 |
| `PHANTOM` | 长点划线 | 相邻零件轮廓 |

### ezdxf 示例

```python
# 注册虚线线型
doc.linetypes.new("DASHED", pattern="DASHED")

# 在图层中使用
doc.layers.new("HIDDEN_LINE", dxfattribs={
    "color": 1,
    "linetype": "DASHED",
})
```

## 颜色（Color）

DXF 使用 **ACI（AutoCAD Color Index）** 颜色系统，共 255 种索引色。

### 常用颜色速查

| ACI | 颜色 | ezdxf 常量 | 典型用途 |
|-----|------|------------|---------|
| 1 | 红 | `colors.RED` | 螺栓孔、中心线 |
| 2 | 黄 | `colors.YELLOW` | 轮廓线、主要图元 |
| 3 | 绿 | `colors.GREEN` | 尺寸标注、注释 |
| 4 | 青 | `colors.CYAN` | 中心线、辅助线 |
| 5 | 蓝 | `colors.BLUE` | 标注、文字 |
| 6 | 品红 | `colors.MAGENTA` | 特殊标记 |
| 7 | 白/黑 | `colors.WHITE` | 默认颜色 |

### 使用方式

```python
from ezdxf import colors

# 方式一：用 ezdxf 常量
dxfattribs={"color": colors.RED}

# 方式二：直接用 ACI 数值
dxfattribs={"color": 1}
```

## 块（Block）

块是一组实体的"打包集合"，定义后可以像"零件"一样反复插入。

### 核心概念

```
                  块定义（Block Definition）
                  ┌──────────────────────┐
                  │  螺栓块 "BOLT_M20"   │
                  │  ○ Circle (头部)     │
                  │  □ Rectangle (垫片)  │
                  └──────────────────────┘
                         ↓ 插入引用
              ┌──────────┼──────────┐
              ↓          ↓          ↓
         块引用1      块引用2      块引用3
         (x=0,0)     (x=10,0)    (x=20,0)
```

### 为什么用块？

- **节省空间**：同一块插入 100 次，文件只存一份几何定义
- **统一修改**：修改块定义，所有引用自动更新
- **参数化**：支持缩放、旋转、属性文字

### ezdxf 中的块操作

```python
# 1. 定义块
block = doc.blocks.new("BOLT_M20")
block.add_circle((0, 0), 5)     # 螺栓头部
block.add_circle((0, 0), 3)     # 螺纹部分

# 2. 插入块引用
msp.add_blockref("BOLT_M20", insert=(100, 200))
msp.add_blockref("BOLT_M20", insert=(200, 200), scale=0.5, rotation=45)
```

## 模型空间 vs 图纸空间

| 概念 | 说明 | ezdxf 获取方式 |
|------|------|---------------|
| **模型空间** | 真正的绘图区域，1:1 绘制所有几何 | `msp = doc.modelspace()` |
| **图纸空间** | 排版布局，可设置图框、比例、多个视图 | `blk = doc.blocks.new("Layout1")` |

**初学者只需关注模型空间**，所有图元都画在模型空间即可。

## 总结速查

```python
import ezdxf
from ezdxf import colors

# 1. 新建文档
doc = ezdxf.new("R2010")

# 2. 获取模型空间
msp = doc.modelspace()

# 3. 创建图层
doc.layers.new("OUTLINE", dxfattribs={"color": colors.YELLOW})
doc.layers.new("CENTER",  dxfattribs={"color": colors.CYAN, "linetype": "CENTER"})

# 4. 绘制实体
msp.add_line((0,0), (100,0),     dxfattribs={"layer": "OUTLINE"})
msp.add_circle((50,50), 30,      dxfattribs={"layer": "OUTLINE"})
msp.add_text("Hello", height=10, dxfattribs={"layer": "CENTER"})

# 5. 保存
doc.saveas("output.dxf")
```
