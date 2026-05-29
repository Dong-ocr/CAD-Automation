import urllib.request, json

queries = [
    "pdf export canvas javascript",
    "three.js room environment outdoor trees",
    "floor plan image trace overlay canvas",
    "wall split algorithm computational geometry",
    "javascript CAD polygon boolean operations",
    "canvas image upload drag resize javascript",
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
