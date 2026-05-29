import urllib.request, json

# 搜索交互式CAD编辑器/室内设计相关项目
queries = [
    "interactive floor plan editor canvas",
    "three.js furniture gltf model",
    "web-based CAD editor open source",
    "drag drop furniture planner javascript",
    "floor plan editor javascript canvas",
    "parametric room layout generator",
    "three.js interior designer drag drop",
]

for q in queries:
    q_enc = q.replace(" ", "%20")
    url = f"https://api.github.com/search/repositories?q={q_enc}&sort=stars&per_page=5"
    req = urllib.request.Request(url, headers={"User-Agent": "Codex"})
    try:
        data = json.load(urllib.request.urlopen(req, timeout=10))
        print(f"===== {q} =====")
        for r in data.get("items", []):
            s = r["stargazers_count"]
            desc = (r["description"] or "")[:100]
            print(f'{r["full_name"]} \u2b50{s}')
            print(f'  {desc}')
        print()
    except Exception as e:
        print(f"Error: {e}")
