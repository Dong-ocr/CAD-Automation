# ezdxf 常用 API 速查手册

## 零、环境搭建（专业开发流程）

### 推荐：使用虚拟环境

虚拟环境（Virtual Environment）是 Python 开发的**行业标配**，可以防止不同项目的库版本冲突。

```bash
# 在项目文件夹下运行
python -m venv venv

# 激活环境 (Windows)
.\venv\Scripts\activate

# 激活环境 (macOS / Linux)
source venv/bin/activate

# 激活后，命令行前面会出现 (venv) 提示
# 然后再安装库
pip install ezdxf
```

### 验证安装

```bash
python -c "import ezdxf; print(ezdxf.__version__)"
```

---

## 一、文档操作

| 操作 | API | 说明 |
|------|-----|------|
| 新建文档 | `ezdxf.new("R2010")` | 创建 DXF，R2010 兼容性最佳 |
| 打开已有 | `ezdxf.read("file.dxf")` | 读取并解析已有 DXF 文件 |
| 保存文档 | `doc.saveas("file.dxf")` | 保存到文件 |
| 获取模型空间 | `doc.modelspace()` | 获取主绘图区域 |

## 二、实体创建（模型空间）

| 实体 | API | 备注 |
|------|-----|------|
| 直线 | `msp.add_line(start, end, dxfattribs)` | start/end: (x,y) |
| 圆 | `msp.add_circle(center, radius, dxfattribs)` | center: (x,y) |
| 圆弧 | `msp.add_arc(center, radius, start_angle, end_angle, dxfattribs)` | 角度单位：度 |
| 文字 | `msp.add_text(text, height, dxfattribs)` | 需指定 dxfattribs |
| 多段线 | `msp.add_lwpolyline(points, dxfattribs)` | points: [(x,y), ...] |
| 块引用 | `msp.add_blockref(name, insert, dxfattribs)` | 插入已定义的块 |

## 三、图层管理

```python
# 创建图层
doc.layers.new("LAYER_NAME", dxfattribs={
    "color": 2,              # ACI 颜色
    "linetype": "CONTINUOUS", # 线型
})

# 获取已有图层
layer = doc.layers.get("LAYER_NAME")

# 修改图层属性
layer.color = 3
layer.is_off = True    # 关闭图层（隐藏）
layer.is_locked = True # 锁定图层
```

## 四、线型注册

```python
# 标准线型已内置，可直接使用
# 如需自定义：
doc.linetypes.new("MY_DASH", pattern="DASHED")

# 在图层中使用
doc.layers.new("HIDDEN", dxfattribs={
    "linetype": "MY_DASH",
})
```

## 五、颜色常量（ezdxf.colors）

```python
from ezdxf import colors

colors.RED      # 1  红
colors.YELLOW   # 2  黄
colors.GREEN    # 3  绿
colors.CYAN     # 4  青
colors.BLUE     # 5  蓝
colors.MAGENTA  # 6  品红
colors.WHITE    # 7  白/黑
```

## 六、块（Block）操作

```python
# 1. 定义块
block = doc.blocks.new("BOLT_M20")
block.add_circle((0, 0), 5, dxfattribs={"color": 2})
block.add_circle((0, 0), 3, dxfattribs={"color": 1})

# 2. 插入块引用
msp.add_blockref("BOLT_M20", insert=(100, 200))
msp.add_blockref("BOLT_M20", insert=(200, 200), scale=0.5, rotation=45)

# 3. 块支持属性（Attribute）
#    用于给块添加可变文字标签
block.add_attrib(tag="PART_NO", text="M20x80", insert=(0, -10), height=3)
```

## 七、常用 dxfattribs 属性

```python
dxfattribs = {
    "layer": "LAYER_NAME",  # 图层
    "color": 2,             # 颜色（ACI）
    "linetype": "CENTER",   # 线型
    "lineweight": 35,       # 线宽（1/100 mm，35 ≈ 0.35mm）
}
```

## 八、完整最小模板

```python
import ezdxf
from ezdxf import colors

doc = ezdxf.new("R2010")
msp = doc.modelspace()

doc.layers.new("MY_LAYER", dxfattribs={"color": colors.YELLOW})

msp.add_line((0,0), (100,0), dxfattribs={"layer": "MY_LAYER"})
msp.add_circle((50,50), 30, dxfattribs={"layer": "MY_LAYER"})

doc.saveas("output.dxf")
```

## 九、进阶学习路径

1. **官方文档**：https://ezdxf.readthedocs.io/
2. **GitHub 仓库**：https://github.com/mozman/ezdxf
3. **关键词搜索**：`ezdxf add_lwpolyline`、`ezdxf block attribute`、`ezdxf dimension`
