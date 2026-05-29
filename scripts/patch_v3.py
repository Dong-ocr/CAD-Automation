import os
with open('E:\CAD自动化制图\interior_cad.html', 'r', encoding='utf-8') as f:
    html = f.read()
changes = 0

# 1. Grid/snap toggle
if 'gridVisible' not in html:
    html = html.replace('// ===================== ANIMATION LOOP',
        'let gridVisible=true,snapEnabled=true;\nwindow.toggleGrid=function(){gridVisible=!gridVisible;render2D()};\nwindow.toggleSnap=function(){snapEnabled=!snapEnabled;render2D()};\n// ===================== ANIMATION LOOP')
    html = html.replace('const gs=50;const gsPx=gs*cam.zoom;\n  if(gsPx>4 && gridVisible){',
                        'const gs=50;const gsPx=gs*cam.zoom;\n  if(gsPx>4){')
    html = html.replace('const gs=50;const gsPx=gs*cam.zoom;\n  if(gsPx>4){',
                        'const gs=50;const gsPx=gs*cam.zoom;\n  if(gsPx>4 && gridVisible){')
    changes += 1
    print('+ Grid/snap toggle')

# 2. PNG export
if 'exportPNG' not in html:
    png = '\nwindow.exportPNG=function(){render2D();c2.toBlob(function(b){var a=document.createElement("a");a.download="floorplan.png";a.href=URL.createObjectURL(b);a.click()},"image/png")};\n'
    html = html.replace('window.exportSVG=function(){', png + 'window.exportSVG=function(){')
    html = html.replace('<button class="btn" onclick="exportSVG()"> SVG</button>',
        '<button class="btn" onclick="exportPNG()"> PNG</button>\n      <button class="btn" onclick="exportSVG()"> SVG</button>')
    changes += 1
    print('+ PNG export')

# 3. Copy/paste furniture
if 'clipboardFurniture' not in html:
    html = html.replace('document.addEventListener("keydown", function(e){',
        'var clipboardFurniture=null;\ndocument.addEventListener("keydown", function(e){')
    html = html.replace('case "z": case "Z": e.shiftKey ? redo() : undo(); e.preventDefault(); break;',
        'case "c": if(selected&&selected.userData){clipboardFurniture=Object.assign({},selected.userData);document.getElementById("tool-status").textContent="  Copied: "+clipboardFurniture.name;e.preventDefault()}break;\n      case "v": if(clipboardFurniture){saveState();furniture.push({id:nextId++,name:clipboardFurniture.name,cat:"",x:(clipboardFurniture.x||0)+500,y:(clipboardFurniture.z||clipboardFurniture.y||0)+500,w:clipboardFurniture.w||1000,d:clipboardFurniture.d||800,color:clipboardFurniture.color});render2D();rebuild3D();updateStatus();document.getElementById("tool-status").textContent="  Pasted: "+clipboardFurniture.name;e.preventDefault()}break;\n      case "z": case "Z": e.shiftKey ? redo() : undo(); e.preventDefault(); break;')
    changes += 1
    print('+ Copy/paste')

with open('E:\CAD自动化制图\interior_cad.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Done! {changes} changes, {len(html)} bytes')
