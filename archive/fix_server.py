import json, os
c = open('server.py', 'r', encoding='utf-8').read()
idx = c.find('# API: material library')
end = c.find('return', idx) + len('return')
new_api = """        if path == "/api/materials":
            mat_path = "materials.json"
            if os.path.exists(mat_path):
                md = json.load(open(mat_path, "r", encoding="utf-8"))
                for k in list(md.keys()):
                    if isinstance(md[k], str):
                        md[k] = {"fallback": md[k], "type": "material"}
                self._json_response(md)
            else:
                self._json_response({"error": "no materials"}, 404)
            return"""
c = c[:idx] + new_api + c[end:]
c = c.replace('import os, json,', 'import os, sys, json,')
open('server.py', 'w', encoding='utf-8').write(c)
print('OK: server.py updated')
