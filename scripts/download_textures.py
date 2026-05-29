import urllib.request, json, os, zipfile, io

out_dir = r"E:\CAD自动化制图\textures"
os.makedirs(out_dir, exist_ok=True)

# Free PBR textures from ambientCG (CC0)
# Using direct download links for a small starter pack
textures = [
    # Wood
    {"name":"wood_oak", "url":"https://ambientcg.com/get?file=Wood037_1K-JPG.zip", "type":"wood"},
    {"name":"wood_floor", "url":"https://ambientcg.com/get?file=WoodFloors002_1K-JPG.zip", "type":"wood"},
    # Stone/Marble
    {"name":"marble_white", "url":"https://ambientcg.com/get?file=Marble003_1K-JPG.zip", "type":"stone"},
    {"name":"concrete", "url":"https://ambientcg.com/get?file=Concrete020_1K-JPG.zip", "type":"stone"},
    # Fabric
    {"name":"fabric_velvet", "url":"https://ambientcg.com/get?file=Fabric013_1K-JPG.zip", "type":"fabric"},
    {"name":"fabric_cotton", "url":"https://ambientcg.com/get?file=Fabric019_1K-JPG.zip", "type":"fabric"},
    # Metal
    {"name":"metal_brushed", "url":"https://ambientcg.com/get?file=Metal032_1K-JPG.zip", "type":"metal"},
    # Tile
    {"name":"tile_ceramic", "url":"https://ambientcg.com/get?file=Tiles065_1K-JPG.zip", "type":"tile"},
    # Ground
    {"name":"leather", "url":"https://ambientcg.com/get?file=Leather008_1K-JPG.zip", "type":"fabric"},
    # Plaster
    {"name":"plaster_wall", "url":"https://ambientcg.com/get?file=Plaster001_1K-JPG.zip", "type":"stone"},
]

print(f"Downloading {len(textures)} PBR textures...")
total = 0
for t in textures:
    dest = os.path.join(out_dir, t["name"])
    if os.path.exists(dest):
        files = [f for f in os.listdir(dest) if f.endswith(".jpg")]
        if files: 
            print(f"  SKIP {t['name']} (already exists, {len(files)} files)")
            total += 1
            continue
    try:
        req = urllib.request.Request(t["url"], headers={"User-Agent": "Codex"})
        data = urllib.request.urlopen(req, timeout=30).read()
        z = zipfile.ZipFile(io.BytesIO(data))
        os.makedirs(dest, exist_ok=True)
        for f in z.namelist():
            if f.endswith(".jpg") or f.endswith(".png"):
                z.extract(f, dest)
                # Rename to flat structure
                src = os.path.join(dest, f)
                ext = f.split(".")[-1]
                base = os.path.basename(f)
                # Keep original names
        files = [f for f in os.listdir(dest) if f.endswith(".jpg") or f.endswith(".png")]
        print(f"  OK {t['name']} ({len(files)} textures)")
        total += 1
    except Exception as e:
        print(f"  FAIL {t['name']}: {e}")

print(f"\nDownloaded {total}/{len(textures)} textures to {out_dir}")
print("Done!")
