# AI CAD 自动化制图系统

## 项目路径
`E:\CAD自动化制图\`

## 目录结构
```
E:\CAD自动化制图\
├── AGENTS.md             项目文档（本文件）
├── README.md
├── src/                  核心 Python 模块
│   ├── interior_models.py    数据模型 + 22 件家具模板
│   ├── interior_dxf.py       DXF 导出引擎 (10 图层)
│   ├── cad_toolbox_v8.py     水电站 CAD 工具集
│   ├── gen_v8_pro.py         水电站施工图生成
│   └── build_3d_model.py     3D 建模
├── scripts/              生成/修补/工具脚本 (59 个)
│   └── self_check.py         自检脚本
├── web/                  前端页面
│   ├── showcase.html         终极作品展 V3 (687KB)
│   ├── studio.html           设计工作室 (31KB)
│   ├── interior_cad.html     室内 CAD 界面
│   ├── interior_pro.html     专业版界面
│   ├── interior_index.html   室内首页
│   ├── index.html            总入口
│   └── cad_web_template.html v2 模板
├── archive/              历史/备份代码
├── cad_blocks/           DXF 图块库 (17 个)
├── docs/                 文档 & 水电站成品图
├── reference/            参考 & 自检知识
├── standards/            制图标准 (国标/SL73/CTB)
├── FreeCAD/              FreeCAD 1.1.1 安装
├── lib/                  Three.js 库 (1.3MB)
├── textures/             PBR 材质贴图 (9 类)
├── output/               历次输出 (DXF/PNG/SVG)
├── static/               静态资源
├── models/               3D 模型文件
└── projects/             项目文件
```

## 当前运行的服务器
| 文件 | 用途 | 端口 |
|------|------|------|
| `studio_server.py` | 新系统 (4种模板 + AI + DXF/PNG导出) | :8765 |
| `cad_web_app_v2.py` | v2 系统 (AI + 真实 CAD) | 同端口 (择一运行) |

## 启动方式
```
start_cad.bat     — 启动服务器
stop_cad.bat      — 停止服务器
打开FreeCAD.bat   — 启动 FreeCAD
```

## 关键 API
- `interior_models.create_apartment_template_fixed()` → InteriorProject
- `interior_dxf.render_dxf(proj, path)` → DXF 导出
- `interior_dxf.render_svg(proj, path)` → PNG/SVG 渲染（当前损坏，见 reference/codex_self_knowledge.md）
- InteriorProject 支持：rooms, walls, openings, furniture, to_json/from_json

## 已知问题
- render_svg() 中 ezdxf 1.4.4 API 变化：Frontend.draw() → draw_layout()
- 详请见 reference/codex_self_knowledge.md

## 腾讯云服务器
- IP: 118.24.164.12
- SSH: ssh -i "C:\Users\王东浩\.ssh\id_ed25519" ubuntu@118.24.164.12
- 待部署
