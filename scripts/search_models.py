import urllib.request, json, os, zipfile, io

out = "E:/CAD自动化制图/models"
os.makedirs(out, exist_ok=True)

# Free CC0 3D models from PolyHaven / Sketchfab (glTF format)
models = [
    # Simple furniture models from GitHub - using GLTF sample models
    {"name":"sofa", "url":"https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/main/2.0/DamagedHelmet/glTF/DamagedHelmet.gltf", "type":"test"},
]

# Actually, let me look for real furniture models
# Search for furniture GLTF files on GitHub
url = "https://api.github.com/search/repositories?q=furniture+glTF+3d+model&sort=stars&per_page=10"
req = urllib.request.Request(url, headers={"User-Agent": "Codex"})
try:
    data = json.load(urllib.request.urlopen(req, timeout=10))
    print("=== Furniture 3D Model Repos ===")
    for r in data.get("items", []):
        desc = (r["description"] or "")[:80]
        print(f'{r["full_name"]} \u2605{r["stargazers_count"]}')
        print(f'  {desc}')
except Exception as e:
    print(f"Search error: {e}")

# Also search for low-poly furniture
print()
url2 = "https://api.github.com/search/repositories?q=low+poly+furniture+3d&sort=stars&per_page=5"
req2 = urllib.request.Request(url2, headers={"User-Agent": "Codex"})
try:
    data2 = json.load(urllib.request.urlopen(req2, timeout=10))
    print("=== Low Poly Furniture ===")
    for r in data2.get("items", []):
        desc = (r["description"] or "")[:80]
        print(f'{r["full_name"]} \u2605{r["stargazers_count"]}')
        print(f'  {desc}')
except Exception as e:
    print(f"Search error: {e}")
