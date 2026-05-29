import urllib.request, json, os, io, zipfile, shutil, tempfile

os.makedirs("reference", exist_ok=True)
os.makedirs("cad_blocks", exist_ok=True)
os.makedirs("standards", exist_ok=True)

def dl(url, path):
    try:
        r = urllib.request.urlopen(url, timeout=15)
        with open(path, "wb") as f: f.write(r.read())
        size = os.path.getsize(path)
        print(f"  OK {path} ({size//1024}KB)")
        return True
    except Exception as e:
        print(f"  FAIL {url}: {e}")
        return False

print("=== 1. CAD Standards ===")
# GB/T 50001-2017 layer standard summary (from public docs)
dl("https://raw.githubusercontent.com/mozman/ezdxf/main/docs/source/tutorials/getting_started.dxf",
   "reference/ezdxf_getting_started.dxf")
dl("https://raw.githubusercontent.com/mozman/ezdxf/main/docs/source/tutorials/add_drawing_content.py",
   "reference/ezdxf_add_content.py")
dl("https://raw.githubusercontent.com/mozman/ezdxf/main/examples/using_aci_palette.py",
   "reference/ezdxf_aci_palette.py")

print("\n=== 2. CAD DXF Blocks from public repos ===")
# Download some real DXF block libraries from open sources
# A sample architectural DXF from open source
sources = [
    ("https://raw.githubusercontent.com/sindresorhus/screenfull/main/readme.md", None),  # placeholder
]

# Actually let's search GitHub for DXF files
search_url = "https://api.github.com/search/repositories?q=dxf+blocks+library&sort=stars&per_page=5"
try:
    r = urllib.request.urlopen(search_url, timeout=10)
    data = json.load(r)
    with open("reference/github_dxf_repos.json", "w", encoding="utf-8") as f:
        json.dump([{"name":i["full_name"],"stars":i["stargazers_count"],"url":i["html_url"],"desc":i["description"]} for i in data["items"]], f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(data['items'])} DXF repo results to reference/github_dxf_repos.json")
except Exception as e:
    print(f"  GitHub search FAIL: {e}")

print("\n=== 3. Three.js resources ===")
# Check if we can get Three.js CDN info
dl("https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js",
   "reference/three.min.js")

print("\n=== 4. GB/T Layer Standards Guide ===")
gb_layers = """
GB/T 50001-2017 房屋建筑制图统一标准 - 图层命名规范参考:

常用图层命名:
- 0               默认图层
- A-WALL          墙体 (Architecture-Wall)
- A-WALL-EXTR     外墙
- A-WALL-INT      内墙  
- A-DOOR          门
- A-WINDOW        窗
- A-FLOR          楼面
- A-ROOF          屋顶
- A-COLUMN        柱
- A-BEAM          梁
- A-STAIR         楼梯
- A-FURN          家具
- A-DIM           尺寸标注
- A-TEXT          文字
- A-HATCH         填充
- S-LABEL         标注
- G-ANNO          通用注释
- A-GLAZ          玻璃幕墙
- S-SLAB          结构板
- S-FOOTING       基础
- M-EQPM          设备

颜色索引 (ACI):
- 1 Red            红    轮廓线
- 2 Yellow         黄    窗口/门
- 3 Green          绿    尺寸标注
- 4 Cyan           青    注释
- 5 Blue           蓝    家具
- 6 Magenta        洋红  设备
- 7 White          白    默认
- 8 Dark Gray      深灰  填充边界
- 9 Light Gray     浅灰  填充

线型:
- CONTINUOUS       实线  默认
- DASHED           虚线  隐藏/内部
- CENTER           点划线 中心线
- PHANTOM          双点划线 边界
- DOT              点    ......

线宽 (mm):
- 0.00 = 默认
- 0.05, 0.09, 0.13 (细线/标注)
- 0.18, 0.25, 0.35 (中等/轮廓)
- 0.50, 0.70, 1.00 (粗线/剖面)
"""
with open("standards/gb_layer_standard.txt", "w", encoding="utf-8") as f:
    f.write(gb_layers)
print("  OK standards/gb_layer_standard.txt")

print("\n=== 5. Checking installed packages ===")
try:
    import ezdxf
    print(f"  ezdxf {ezdxf.__version__}: OK")
    print(f"  DXF version support: {ezdxf.consts.MIN_SUPPORTED_DXF_VERSION} - {ezdxf.consts.MAX_SUPPORTED_DXF_VERSION}")
    print(f"  Entities available: {len(ezdxf.consts.DXF2000)} types (DXF2000)")
except Exception as e:
    print(f"  ezdxf ERROR: {e}")

try:
    import cadquery as cq
    print(f"  cadquery {cq.__version__}: OK")
except Exception as e:
    print(f"  cadquery: {e}")

try:
    import build123d as bd
    print(f"  build123d: OK")
except:
    print(f"  build123d: not available")

print("\n=== Done ===")
