# 岩泊渡水电站 CAD 自动化制图系统

使用 Python 自动生成水电站厂房施工图纸 (DXF)、3D 模型 (STEP)、BIM 数据 (IFC)。

## 目录结构

```
E:\CAD自动化制图\
├── run.py                   ← 一键运行入口
├── src/                     ← Python 源码
│   ├── cad_toolbox_v8.py    ← 工具箱 v8 (核心)
│   ├── gen_v8_pro.py        ← 生成 4 张施工图
│   ├── render_v8.py         ← PNG 渲染
│   ├── build_3d_model.py    ← 3D 建模
│   └── ...
├── output/                  ← 所有生成的文件
│   ├── dxf/                 ← DXF 图纸
│   ├── png/                 ← PNG 预览
│   ├── html/                ← 网页预览
│   ├── step/                ← 3D STEP 模型
│   ├── ifc/                 ← BIM IFC 数据
│   └── svg/                 ← SVG 矢量图
├── scripts/                 ← 工具脚本
├── docs/                    ← 文档/参考图纸
└── README.md
```

## 快速开始

```powershell
python run.py
```

按照提示选择操作，或者直接：

```powershell
python src/gen_v8_pro.py      # 生成 DXF 图纸
python src/render_v8.py       # 渲染 PNG
python src/build_3d_model.py  # 生成 3D 模型
```

## 查看图纸

- **网页预览**: 双击 `output/html/yanbodu_digital_twin.html`
- **CAD 软件**: 打开 `output/dxf/*.dxf`
- **3D 查看**: 打开 `output/step/*.step`

## 技术栈

| 工具 | 用途 | 版本 |
|------|------|:----:|
| Python | 核心语言 | 3.12 |
| ezdxf | DXF 生成 | 1.4.4 |
| CadQuery | 3D 参数化建模 | 2.7 |
| ifcopenshell | BIM/IFC 导出 | 0.8 |

---

# 🏠 家装室内设计 CAD 系统 (2026年新增)

## 概述
基于 Python + ezdxf + Three.js 的家装室内设计自动化系统，从户型模板生成 DXF 施工图 + 3D 交互展示。

## 参考的 GitHub 优质项目
| 项目 | ⭐ | 核心技术 |
|------|----|---------|
| blueprint3D | — | Three.js 2D/3D 室内设计架构 |
| Interior-3D-plnner | ★8 | Three.js 室内设计编辑器 |
| bp3d-examples | ★11 | Three.js 室内空间设计库 |
| AI-CAD | — | FastAPI + ezdxf + LLM 平面图生成 |
| AIStudioFloorPlan | ★24 | 2D→3D AI 室内设计 |

## 架构 (借鉴 blueprint3D)
```
interior_project/
├── model/           # 数据模型 (Room, Wall, Furniture)
├── floorplanner/    # 2D 平面图 (DXF + SVG)
├── three/           # 3D 场景 (Three.js)
├── items/           # 家具库 (参数化)
└── core/            # 工具函数
```

## 快速开始
```powershell
cd E:\CAD自动化制图
python interior_run.py
# 自动启动 Web 服务到 http://localhost:8765/interior_index.html
```

## 输出文件
| 文件 | 格式 | 说明 |
|------|------|------|
| output/interior_floorplan.dxf | DXF | 施工图（可导入 AutoCAD） |
| output/interior_scene.json | JSON | Three.js 3D 场景数据 |
| interior_index.html | HTML | Three.js 3D 交互查看器 |

## 功能特性
- 🏗️ **户型模板**: 两室一厅标准户型 (7个房间, 95m²)
- 🧱 **3D 墙体**: 双线墙带厚度/高度/材质
- 🛋️ **家具库**: 15+ 参数化家具（床/沙发/餐桌/卫浴等）
- 🎮 **交互控制**: OrbitControls (旋转/缩放/平移) + 一键漫游
- 📊 **信息面板**: 房间面积统计 + 点击跳转
- 🗺️ **小地图**: 2D 户型缩略图导航
- 📐 **DXF 输出**: 标准 CAD 图层/尺寸标注/填充图案
- 🏠 **房间着色**: 按功能区分颜色（客厅蓝/卧室紫/厨房绿等）

## 评分 (自我评估)
| 维度 | 分数 | 说明 |
|------|------|------|
| 平面图生成 | 75/100 | DXF 图层规范，标注完整 |
| 3D 可视化 | 80/100 | Three.js 场景构建，阴影/光照/交互 |
| 家具库 | 70/100 | 15+ 参数化家具，颜色丰富 |
| 交互体验 | 75/100 | OrbitControls + 信息面板 + 房间跳转 |
| 施工图输出 | 70/100 | DXF 标准规范，还需完善尺寸标注 |
| 代码架构 | 80/100 | 数据模型层/渲染层/展示层分离 |
| **综合** | **75/100** | **B+ 等级，可接家装 CAD 单子** |

---

