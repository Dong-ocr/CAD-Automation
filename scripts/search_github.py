import urllib.request, json, os
queries = ["dxf+python+library","freecad+python+automation","cad+blocks+library","chinese+cad+standard"]
results = {}
for q in queries:
    url = "https://api.github.com/search/repositories?q="+q+"&sort=stars&per_page=5"
    try:
        r = urllib.request.urlopen(url, timeout=10)
        data = json.load(r)
        results[q] = [{"name":i["full_name"],"stars":i["stargazers_count"],"url":i["html_url"],"desc":i["description"]} for i in data["items"]]
    except Exception as e:
        results[q] = [{"error":str(e)}]
os.makedirs("reference", exist_ok=True)
json.dump(results, open("reference/github_cad_resources.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
for q,items in results.items():
    print(q+":")
    for i in items[:3]: print("  "+str(i.get("stars","?"))+"\u2605 "+i.get("name","?")+" | "+str(i.get("desc","N/A"))[:60])
