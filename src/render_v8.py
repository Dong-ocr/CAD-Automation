"""render_v8.py — v8 图纸 PNG 渲染"""
import sys, os
sys.path.insert(0, "E:/CAD自动化制图/src")

DXF_DIR = "E:/CAD自动化制图/output/dxf"
PNG_DIR = "E:/CAD自动化制图/output/png"

FILES = ["Yanbodu_v8_complete.dxf"]

def render(fpath, opath, dpi=200):
    import ezdxf
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import Configuration
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    doc = ezdxf.readfile(fpath)
    msp = doc.modelspace()
    fig = plt.figure(figsize=(16, 12), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("white")
    ax.set_aspect("equal")
    ax.axis("off")
    ctx = RenderContext(doc)
    cfg = Configuration(hatch_policy=1, lineweight_scaling=1.0, color_policy=1)
    Frontend(ctx, MatplotlibBackend(ax), cfg).draw_layout(msp)
    ax.autoscale_view()
    plt.savefig(opath, dpi=dpi, bbox_inches="tight", pad_inches=0.3,
                facecolor="white", edgecolor="none")
    plt.close(fig)
    size_kb = os.path.getsize(opath) / 1024
    print(f"  -> {os.path.basename(opath)} ({size_kb:.0f} KB)")

if __name__ == "__main__":
    print("Rendering v8 preview...")
    os.makedirs(PNG_DIR, exist_ok=True)
    for f in FILES:
        fp = os.path.join(DXF_DIR, f)
        op = os.path.join(PNG_DIR, f.replace(".dxf", ".png"))
        if os.path.exists(fp):
            render(fp, op)
    print("Done!")
