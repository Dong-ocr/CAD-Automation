import os
html = open("E:/CAD自动化制图/interior_cad.html","r",encoding="utf-8").read()
c=0
old = " 图层</button>"
new = ' 网格</button><button class="tool-btn" onclick="toggleSnap()"> 吸附</button><button class="tool-btn" onclick="toggleLayerPanel()"> 图层</button>'
if old in html:
    html = html.replace(old,new); c+=1; print("+ grid/snap buttons")
html = html.replace('if(gsPx>4 and gridVisible and gridVisible){','if(gsPx>4 and gridVisible){')
open("E:/CAD自动化制图/interior_cad.html","w",encoding="utf-8").write(html)
print(f"Done {c} changes, {len(html)} bytes")
