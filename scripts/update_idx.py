import os, re
wp = r"E:\CAD自动化制图"
web = os.path.join(wp, "web")
idx = os.path.join(web, "index.html")
html = open(idx, "r", encoding="utf-8").read()

# Add ultra card after cliff_villa_3d card
if "cliff_villa_ultra" not in html:
    # Find cliff_villa_3d card end
    target = "cliff_villa_3d.html"
    pos = html.index(target)
    # Find the enclosing </a>
    end_a = html.index("</a>", pos) + 4
    card = '\n  <a href="cliff_villa_ultra.html" class="card ultra">\n    <div class="icn">&#8734;</div>\n    <div class="ttl">CLIFF VILLA ULTRA</div>\n    <div class="dsc">Bloom &#183; Ocean &#183; Rain &#183; Fly</div>\n  </a>'
    html2 = html[:end_a] + card + html[end_a:]
    with open(idx, "w", encoding="utf-8") as f:
        f.write(html2)
    print("Updated index.html")
else:
    print("Already has ultra card")
