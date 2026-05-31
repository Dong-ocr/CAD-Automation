import os
wp = r"E:\CAD自动化制图"
web = os.path.join(wp, "web")
idx = os.path.join(web, "index.html")
html = open(idx, "r", encoding="utf-8").read()

# Add ultra card styling
if ".card.ultra" not in html:
    # Find the style section end
    style_end = html.index("</style>")
    css = "\n.card.ultra{border-color:rgba(96,165,250,0.3);background:linear-gradient(135deg,rgba(96,165,250,0.08),rgba(0,0,0,0.2))}\n.card.ultra .icn{color:#60a5fa;text-shadow:0 0 20px rgba(96,165,250,0.3)}"
    html2 = html[:style_end] + css + html[style_end:]
    with open(idx, "w", encoding="utf-8") as f:
        f.write(html2)
    print("Added ultra CSS")
else:
    print("Already has ultra CSS")
