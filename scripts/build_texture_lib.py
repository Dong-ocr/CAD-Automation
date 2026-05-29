import json, os

# Build texture library index
tex_dir = r"E:\CAD自动化制图\textures"
lib = {}

for folder in os.listdir(tex_dir):
    folder_path = os.path.join(tex_dir, folder)
    if not os.path.isdir(folder_path): continue
    files = os.listdir(folder_path)
    entry = {"name": folder, "path": f"textures/{folder}/", "maps": {}}
    for f in files:
        f_lower = f.lower()
        if "color" in f_lower or (f.endswith(".png") and "normal" not in f_lower and "roughness" not in f_lower and "displacement" not in f_lower and "ambient" not in f_lower and "metalness" not in f_lower and "opacity" not in f_lower):
            entry["maps"]["color"] = f"textures/{folder}/{f}"
        elif "roughness" in f_lower:
            entry["maps"]["roughness"] = f"textures/{folder}/{f}"
        elif "normalgl" in f_lower or "normal_gl" in f_lower:
            entry["maps"]["normal"] = f"textures/{folder}/{f}"
        elif "normaldx" in f_lower:
            entry["maps"]["normalDX"] = f"textures/{folder}/{f}"
        elif "displacement" in f_lower:
            entry["maps"]["displacement"] = f"textures/{folder}/{f}"
        elif "metalness" in f_lower:
            entry["maps"]["metalness"] = f"textures/{folder}/{f}"
        elif "ambientocclusion" in f_lower:
            entry["maps"]["ao"] = f"textures/{folder}/{f}"
        elif "opacity" in f_lower:
            entry["maps"]["opacity"] = f"textures/{folder}/{f}"
    lib[folder] = entry

# Also add fallback color for each
color_map = {
    "wood_oak": "#C4A882", "marble_white": "#E0D8D0", "concrete": "#A0A0A0",
    "fabric_velvet": "#7B6B8A", "fabric_cotton": "#F0EDE8", "metal_brushed": "#A0A0A0",
    "tile_ceramic": "#E8E0D0", "leather": "#8B5E3C", "plaster_wall": "#F0EBE5",
}
for k in lib:
    lib[k]["fallbackColor"] = color_map.get(k, "#cccccc")

with open(r"E:\CAD自动化制图\textures\texture_library.json", "w", encoding="utf-8") as f:
    json.dump(lib, f, ensure_ascii=False, indent=2)

print(f"Texture library: {len(lib)} entries")
for name, entry in lib.items():
    maps = list(entry["maps"].keys())
    print(f"  {name}: {maps}")
