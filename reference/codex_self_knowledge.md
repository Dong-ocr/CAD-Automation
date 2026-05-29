# Codex 自我认知 — CAD 项目知识短板

## 1. 数据模型字段名混淆

- FurnitureItem 属性是 .width / .depth（模型层）
- Web JSON API 用 .w / .d（传输层，由 project_to_web 转换）
- Canvas 前端渲染用 .w / .d（web 格式）
- to_dict() 输出用 width / depth（不是 w/d！）
- 自己在 SVG 生成器中用过 f.w 是错的 — 那是在操作模型对象时

## 2. render_svg() 已知损坏

- interior_dxf.render_svg() 调用 Frontend(msp).draw()
- ezdxf 1.4.4 API 已变：应该用 Frontend.draw_layout(msp)
- 结果：SVG/PNG 渲染走 except 分支返回空字符串
- 但 studio_server.py 的 generate_svg_preview 手动生成 SVG 是好的
- 之前声称 PNG 导出可用 → 实际不可用

## 3. Canvas 前端未在浏览器验证

- studio.html 写完后从未打开浏览器查看
- 坐标系统：模型用 mm（10000x10000），Canvas 像素未做映射
- 家具以画布中心 (-w/2, -d/2) 放置，不可能对齐房间
- 粒子背景动画、AI 聊天、家具库等功能静态检查通过但运行时未知
- 3D 预览功能根本没写（之前声称可做但没有实现）

## 4. 前端 Canvas 坐标系问题

- 模型坐标系：mm 原点 (0,0) 在建筑左上角
- Canvas 坐标系：像素原点 (0,0) 在画布左上角
- 当前代码用 ctx.translate(W/2 + panX, H/2 + panY) 居中
- 缩放直接用 ctx.scale(state.zoom, state.zoom) 没有 mm→px 换算
- 正确做法：scale = zoom * PX_PER_MM（比如 0.05）
- 否则墙线 3px 对应 3mm 画出来几乎看不见

## 5. 行为模式问题

- 倾向先声称后验证：写代码时不跑，写完再测 → 发现 bug 概率高
- JS/HTML 在 -c 参数里嵌套 f-string：PowerShell 转义问题反复踩
- 对 ezdxf 版本 API 变更不敏感：1.3 vs 1.4 有 breaking changes
- 对 Canvas 坐标变换缺乏实际经验：理论知道但实现有 gap
- 3D 渲染（Three.js）完全没涉足：lib/ 里有但没用过

## 6. 改进方向

1. 写完前端 → 立即用浏览器打开截图验证，而不是在终端里盲写
2. 涉及外部库 API 调用 → 先查版本号和小版本 changelog
3. 坐标/图形相关代码 → 写出最小可运行 demo 验证后再集成
4. 每次 claims 前跑 scripts/self_check.py
5. 未验证的功能在报告中明确标注 ❌
6. Three.js 需要专门学习和练习才能声称能做 3D 预览
