import urllib.request, json

url = "https://api.github.com/repos/HAJJIRI-OUSSAMA/interia-3d/contents"
req = urllib.request.Request(url, headers={"User-Agent": "Codex"})
data = json.load(urllib.request.urlopen(req, timeout=10))
for item in data:
    print(f'{item["type"]:8s} {item["name"]}')
