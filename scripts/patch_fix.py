import os
with open("E:/CAD自动化制图/interior_cad.html","r",encoding="utf-8") as f:
    html = f.read()
c=0

# Fix 1: Add missing adjustBgOpacity function
if "adjustBgOpacity" not in html:
    html = html.replace(
        'window.adjustBgOpacity',
        'window.adjustBgOpacity'
    )
    # Find the loadBgImage function and add opacity control
    old_img = 'window.loadBgImage=function(){'
    new_img = 'window.loadBgImage=function(){\n  bgImageOpacity=0.3;\n'
    html = html.replace(old_img, new_img)
    c+=1
    print("+ Fixed bg opacity init")

# Add opacity buttons in header
if 'adjustBgOpacity(-0.1)' not in html:
    html = html.replace(
        'onclick="loadBgImage()"> 图片</button>',
        'onclick="loadBgImage()"> 图片</button>\n      <button class="btn" onclick="adjustBgOpacity(-0.1)"> 透明-</button>\n      <button class="btn" onclick="adjustBgOpacity(0.1)"> 透明+</button>'
    )
    c+=1
    print("+ Opacity buttons")

# Fix 2: Scale bar - make it render after rooms
old_scale_marker = 'ctx.textAlign = "center";\n    ctx.fillText(r.name'
if 'ctx.textAlign = "center";' in html:
    # Find the correct location - the room label section
    parts = html.split('ctx.textAlign = "center";')
    for i, p in enumerate(parts):
        if 'ctx.fillText(r.name' in p and i < len(parts)-1:
            scale_insert = '\n  // Scale bar\n  var sbLen=2000;var sbPx=sbLen*cam.zoom;var sbX=20,sbY=c2.height-30;\n  ctx.fillStyle="rgba(255,255,255,0.6)";\n  ctx.fillRect(sbX,sbY,sbPx,3);\n  ctx.fillRect(sbX,sbY-3,1,6);ctx.fillRect(sbX+sbPx,sbY-3,1,6);\n  ctx.fillStyle="rgba(255,255,255,0.5)";\n  ctx.font="9px sans-serif";ctx.textAlign="center";\n  ctx.fillText((sbLen/1000)+"m",sbX+sbPx/2,sbY-6);'
            # Find where the room labels end and insert after
            label_marker = 'ctx.fillText(r.name+" "+r.area+"m2",cx.x,cx.y);'
            if label_marker in parts[i]:
                parts[i] = parts[i].replace(label_marker, label_marker + scale_insert)
                html = 'ctx.textAlign = "center";'.join(parts)
                c+=1
                print("+ Scale bar fixed")
            break

with open("E:/CAD自动化制图/interior_cad.html","w",encoding="utf-8") as f:
    f.write(html)
print(f"Done! {c} fixes, {len(html)} bytes")
