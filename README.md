# CAD 自动化制图系统 — AI全能助手

## 项目概述
一个集CAD制图、3D可视化、FreeCAD建模和Web展示于一体的综合性CAD自动化系统。

## 功能矩阵

### 1. 3D可视化 (Three.js)
| 页面 | 功能 |
|------|------|
| web/index.html | 门户入口，链接所有页面 |
| web/cliff_villa_ultra.html | 旗舰版 — Bloom光晕 · 动态海洋 · 下雨 · 飞行模式 · 夜间模式 · 点击交互 |
| web/cliff_villa_3d.html | 悬崖别墅标准版 |
| web/apartment_3d.html | 室内户型3D查看器 |
| web/dxf_viewer.html | DXF文件在线查看器 |
| web/showcase.html | 终极作品展 (669KB Canvas 2D) |

### 2. CAD导出引擎
| 模块 | 功能 |
|------|------|
| src/interior_models.py | 22件家具模板 + 户型数据模型 |
| src/interior_dxf.py | DXF/SVG/PNG导出 (12国标图层) |
| scripts/cliff_villa_macro.py | FreeCAD悬崖别墅宏 (91对象) |
| scripts/freecad_apartment_macro.py | FreeCAD户型宏 |

### 3. Python后端
- src/cad_toolbox_v8.py — 水电站CAD工具集
- src/gen_v8_pro.py — 施工图生成
- src/build_3d_model.py — 3D建模

## 技术栈
- **3D渲染**: Three.js + OrbitControls + UnrealBloomPass
- **CAD引擎**: FreeCAD 1.1.1 + ezdxf 1.4.4
- **格式支持**: DXF · STEP · STL · FCStd · IGS · BREP · SVG · PNG
- **部署**: GitHub Pages (dong-ocr.github.io/CAD-Automation)

## 快速启动
`ash
# 本地启动
start_cad.bat     # 启动Web服务器
stop_cad.bat      # 停止服务器
打开FreeCAD.bat   # 启动FreeCAD
`

## GitHub Pages
访问: https://dong-ocr.github.io/CAD-Automation/
