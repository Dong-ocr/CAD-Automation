import urllib.request, json, os

out = "E:\\CAD自动化制图\\scripts\\interia_study"
os.makedirs(out, exist_ok=True)

files = ["scene.js", "app.js", "index.html", "styles.css"]
for f in files:
    url = f"https://api.github.com/repos/HAJJIRI-OUSSAMA/interia-3d/contents/{f}"
    req = urllib.request.Request(url, headers={"User-Agent": "Codex"})
    try:
        data = json.load(urllib.request.urlopen(req, timeout=10))
        # GitHub API returns content as base64 when it''s a file
        import base64
        content = base64.b64decode(data["content"]).decode("utf-8")
        dest = os.path.join(out, f)
        with open(dest, "w", encoding="utf-8") as fp:
            fp.write(content)
        print(f"Downloaded {f} ({len(content)} bytes)")
    except Exception as e:
        print(f"Error downloading {f}: {e}")
