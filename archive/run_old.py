"""岩泊渡水电站 CAD 自动化 — 一键运行入口"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def cmd(name, module):
    print(f"\n{'='*50}")
    print(f"  [{name}]")
    print(f"{'='*50}")
    import importlib
    mod = importlib.import_module(module)
    if hasattr(mod, "main"):
        mod.main()
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("  岩泊渡水电站 · CAD 自动化制图系统")
    print("  Yanbodu Hydropower Station")
    print("=" * 50)
    
    actions = {
        "1": ("生成施工图纸 (DXF)", "gen_v8_pro"),
        "2": ("渲染 PNG 预览", "render_v8"),
        "3": ("构建 3D 模型", "build_3d_model"),
        "4": ("全部执行 (1→2→3)", "all"),
    }
    
    print()
    for k, (desc, _) in actions.items():
        print(f"  [{k}] {desc}")
    print()
    
    try:
        choice = input("  请选择 [1-4]: ").strip()
    except (EOFError, KeyboardInterrupt):
        choice = "1"
    
    if choice == "4":
        cmd("生成施工图纸", "gen_v8_pro")
        cmd("渲染 PNG 预览", "render_v8")
        cmd("构建 3D 模型", "build_3d_model")
    elif choice in actions:
        cmd(actions[choice][0], actions[choice][1])
    else:
        cmd(actions["1"][0], actions["1"][1])
    
    print()
    print("完成! 查看 output/ 目录下的生成文件。")
    print("网页预览: output/html/yanbodu_digital_twin.html")
