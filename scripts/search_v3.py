import urllib.request, json

queries = [
    "javascript canvas arc wall drawing",
    "hatch pattern fill canvas javascript",
    "cad dimension arrow style javascript",
    "floor plan wall join cleanup algorithm",
    "three.js extrude shape wall arc",
    "canvas polygon hatch fill pattern",
]

for q in queries:
    q_enc = q.replace(" ", "%20")
    url = f"https://api.github.com/search/repositories?q={q_enc}&sort=stars&per_page=3"
    req = urllib.request.Request(url, headers={"User-Agent": "Codex"})
    try:
        data = json.load(urllib.request.urlopen(req, timeout=10))
        print(f"===== {q} =====")
        for r in data.get("items", []):
            s = r["stargazers_count"]
            desc = (r["description"] or "")[:100]
            print(f'{r["full_name"]} \u2605{s}')
            print(f'  {desc}')
        print()
    except Exception as e:
        print(f"  Error: {q} -> {e}")
