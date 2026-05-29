import numpy as np
import os, re

def read_stl_ascii(filename):
    """Read ASCII STL file"""
    with open(filename, "r") as f:
        text = f.read()
    
    # Parse vertex coordinates
    vert_pattern = re.compile(r"vertex\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)")
    matches = vert_pattern.findall(text)
    
    if not matches:
        raise ValueError("No vertices found in STL file")
    
    vertices = np.array([(float(x), float(y), float(z)) for x, y, z in matches])
    n_verts = len(vertices)
    faces = np.arange(n_verts).reshape(-1, 3)
    
    return vertices, faces

def project_ortho(vertices, direction):
    """Orthographic projection"""
    d = np.array(direction, dtype=float)
    d = d / np.linalg.norm(d)
    if abs(d[0]) < 0.9:
        u = np.cross(d, [1,0,0])
    else:
        u = np.cross(d, [0,1,0])
    u = u / np.linalg.norm(u)
    v = np.cross(d, u)
    v = v / np.linalg.norm(v)
    proj = np.column_stack([np.dot(vertices, u), np.dot(vertices, v)])
    return proj

def render_view(vertices, faces, direction, title, output_path, color="#4488aa"):
    """Render to SVG"""
    proj = project_ortho(vertices, direction)
    margin = 50
    min_p, max_p = proj.min(axis=0), proj.max(axis=0)
    size = max_p - min_p
    if size[0] == 0 or size[1] == 0:
        return
    scale = min(700 / size[0], 500 / size[1]) * 0.8
    proj_s = (proj - min_p) * scale + np.array([margin, margin])
    cw = int(max_p[0] - min_p[0]) * scale + 2*margin + 100
    ch = int(max_p[1] - min_p[1]) * scale + 2*margin + 100
    
    # Sort faces by depth
    v = vertices
    centers = v[faces].mean(axis=1)
    depth = np.dot(centers, np.array(direction))
    order = np.argsort(-depth)
    
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cw} {ch}" width="{cw}" height="{ch}">']
    svg.append(f'<rect width="100%" height="100%" fill="#f8f9fa"/>')
    svg.append(f'<text x="{cw/2}" y="30" text-anchor="middle" font-size="18" font-family="Microsoft YaHei" fill="#333">{title}</text>')
    
    for i in order[:50000]:  # limit to avoid huge files
        f = faces[i]
        pts = proj_s[f]
        ps = " ".join([f"{p[0]:.1f},{p[1]:.1f}" for p in pts])
        svg.append(f'<polygon points="{ps}" fill="{color}" stroke="#2c5f8a" stroke-width="0.3" fill-opacity="0.85"/>')
    
    svg.append("</svg>")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"  {title}: {output_path}")

stl_path = "E:/CAD自动化制图/output/professional/apartment_interior.stl"
out_dir = "E:/CAD自动化制图/output/professional"
print("Reading STL...")
verts, faces = read_stl_ascii(stl_path)
print(f"  Vertices: {len(verts)}, Faces: {len(faces)}")
center = verts.mean(axis=0)
verts = verts - center

views = [
    ( 0, -1, 0, "正视图 (Front)"),
    ( 0, 0,-1, "俯视图 (Top)"),
    ( 1, 0, 0, "右视图 (Right)"),
    (-1,-1, 1, "立体图 (Isometric)"),
]
for dx, dy, dz, title in views:
    name = title.split("(")[-1].strip(")").lower()
    render_view(verts, faces, (dx, dy, dz), title, os.path.join(out_dir, f"view_{name}.svg"))
print("Done!")
