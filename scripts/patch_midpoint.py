import os
with open("E:/CAD自动化制图/interior_cad.html","r",encoding="utf-8") as f:
    html = f.read()
c=0

# 1. Add snapToMidpoint function
sm_func = 'window.snapToMidpoint=function(p,dist){if(!snapEnabled)return null;for(var w=0;w<walls.length;w++){var mx=(walls[w].x1+walls[w].x2)/2,my=(walls[w].y1+walls[w].y2)/2;if(Math.hypot(p.x-mx,p.y-my)*cam.zoom<dist)return{x:mx,y:my}}return null};\n'

# Find a good insertion point - before the grid/snap section
marker = "var gridVisible=true,snapEnabled=true;"
if marker in html:
    if "snapToMidpoint" not in html:
        html = html.replace(marker, sm_func + marker)
        c+=1

# 2. Patch snap chain in wall drawing - find the actual chain
old_chain = "snapToEndpoint(wp,15/cam.zoom)||snapToGrid(wp)"
new_chain = "snapToEndpoint(wp,15/cam.zoom)||snapToMidpoint(wp,15/cam.zoom)||snapToGrid(wp)"
html = html.replace(old_chain, new_chain)
c+=1

# 3. Also in handle drag
old_handle = "snapToEndpoint(wp,15/cam.zoom)||snapToGrid(wp)"
# Already replaced above, but check if there's another variant
old_handle2 = "snapToEndpoint(wp,15/cam.zoom)||snapToGrid(wp)"
html = html.replace(old_handle2, new_chain)

with open("E:/CAD自动化制图/interior_cad.html","w",encoding="utf-8") as f:
    f.write(html)
print(f"Done! {c} changes")
