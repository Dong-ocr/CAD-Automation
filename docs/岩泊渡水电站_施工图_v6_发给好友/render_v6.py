import sys, os
sys.path.insert(0, "E:/CAD自动化制图")

FILES = [
    "Yanbodu_Cross_Section_v6.dxf",
    "Yanbodu_Generator_Floor_v6.dxf",
    "Yanbodu_Turbine_Floor_v6.dxf",
    "Yanbodu_Spiral_Case_Floor_v6.dxf",
]

def render(fpath, opath):
    print(f"  {os.path.basename(fpath)}...")
    import ezdxf
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import Configuration
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    
    doc = ezdxf.readfile(fpath)
    msp = doc.modelspace()
    
    fig = plt.figure(figsize=(16, 12), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("white")
    ax.set_aspect("equal")
    ax.axis("off")
    
    ctx = RenderContext(doc)
    cfg = Configuration(hatch_policy=1, lineweight_scaling=1.0, color_policy=1)
    Frontend(ctx, MatplotlibBackend(ax), cfg).draw_layout(msp)
    ax.autoscale_view()
    
    plt.savefig(opath, dpi=150, bbox_inches="tight", pad_inches=0.3,
                facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"    -> {os.path.basename(opath)} ({os.path.getsize(opath)/1024:.0f} KB)")

if __name__ == "__main__":
    print("Rendering v6 previews...")
    for f in FILES:
        fp = f"E:/CAD自动化制图/{f}"
        op = fp.replace(".dxf", ".png")
        if os.path.exists(fp):
            render(fp, op)
    print("Done!")
