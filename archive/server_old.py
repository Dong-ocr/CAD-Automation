import os, json, socketserver, http.server, urllib.parse, threading

# ==================== DXF Generator ====================
def generate_dxf(data):
    """Generate proper ASCII DXF R12 from CAD data"""
    lines = []
    def w(code, val):
        lines.append(str(code))
        lines.append(str(val) if not isinstance(val, str) else val)

    # Header
    w(0, "SECTION"); w(2, "HEADER")
    w(9, "$ACADVER"); w(1, "AC1006")  # R12
    w(9, "$INSBASE"); w(10, "0"); w(20, "0"); w(30, "0")
    w(9, "$EXTMIN"); w(10, "-10000"); w(20, "-10000"); w(30, "0")
    w(9, "$EXTMAX"); w(10, "20000"); w(20, "20000"); w(30, "0")
    w(0, "ENDSEC")

    # Tables
    w(0, "SECTION"); w(2, "TABLES")
    # Line types
    w(0, "TABLE"); w(2, "LTYPE"); w(70, "4")
    for lt in [
        ("CONTINUOUS", "Solid line", 0, []),
        ("DASHED", "Dashed __ __ ", 6, [6, -3]),
        ("CENTER", "Center ____ _ ____ _", 16, [8, -2, 2, -2]),
        ("DASHDOT", "Dash dot __ . __ .", 10, [6, -2, 1, -2]),
    ]:
        w(0, "LTYPE"); w(2, lt[0]); w(70, "64"); w(3, lt[1]); w(72, "65"); w(73, str(len(lt[3])//2 if lt[3] else 0))
        w(40, str(lt[2])); w(62, "0")
        for i, p in enumerate(lt[3]):
            w(49, str(p))
    w(0, "ENDTAB")
    # Layers
    w(0, "TABLE"); w(2, "LAYER"); w(70, "8")
    layers = [
        ("0", "7", "CONTINUOUS"), ("A-WALL", "7", "CONTINUOUS"),
        ("A-WALL-PART", "6", "CONTINUOUS"), ("A-DOOR", "3", "CONTINUOUS"),
        ("A-WINDOW", "4", "CONTINUOUS"), ("A-DIM", "2", "CONTINUOUS"),
        ("A-TEXT", "7", "CONTINUOUS"), ("A-FURN", "5", "CONTINUOUS"),
        ("A-HATCH", "8", "CONTINUOUS"),
    ]
    for name, color, ltype in layers:
        w(0, "LAYER"); w(2, name); w(70, "64"); w(62, color); w(6, ltype)
    w(0, "ENDTAB")
    # Dimension style
    w(0, "TABLE"); w(2, "DIMSTYLE"); w(70, "1")
    w(0, "DIMSTYLE"); w(2, "GB-STANDARD"); w(70, "64")
    w(3, "GB-Standard"); w(4, ""); w(40, "1.0"); w(41, "50.0")
    w(42, "200.0"); w(43, "500.0"); w(44, "250.0"); w(45, "0.0")
    w(140, "200.0"); w(141, "100.0"); w(0, "ENDTAB")
    w(0, "ENDSEC")

    # Entities
    w(0, "SECTION"); w(2, "ENTITIES")

    walls = data.get("walls", [])
    doors = data.get("doors", [])
    windows_data = data.get("windows", [])
    rooms = data.get("rooms", [])
    furniture = data.get("furniture", [])

    for w_data in walls:
        layer = "A-WALL" if w_data.get("type") == "外墙" else "A-WALL-PART"
        w(0, "LINE"); w(8, layer); w(62, "7" if layer == "A-WALL" else "6")
        w(10, str(w_data["x1"])); w(20, str(w_data["y1"])); w(30, "0")
        w(11, str(w_data["x2"])); w(21, str(w_data["y2"])); w(31, "0")
        # Second line for thickness
        dx = w_data["x2"] - w_data["x1"]
        dy = w_data["y2"] - w_data["y1"]
        length = (dx*dx + dy*dy) ** 0.5
        if length > 0:
            nx, ny = -dy/length * w_data.get("thick", 200) / 2, dx/length * w_data.get("thick", 200) / 2
            w(0, "LINE"); w(8, layer)
            w(10, str(w_data["x1"] + nx)); w(20, str(w_data["y1"] + ny)); w(30, "0")
            w(11, str(w_data["x2"] + nx)); w(21, str(w_data["y2"] + ny)); w(31, "0")

    for d in doors:
        wall = None
        for w_data in walls:
            if w_data.get("id") == d.get("wallId"):
                wall = w_data; break
        if not wall: continue
        dx = wall["x2"] - wall["x1"]
        dy = wall["y2"] - wall["y1"]
        length = (dx*dx + dy*dy) ** 0.5
        if length == 0: continue
        ratio = d.get("pos", 0) / length
        cx = wall["x1"] + dx * ratio
        cy = wall["y1"] + dy * ratio
        w(0, "CIRCLE"); w(8, "A-DOOR"); w(10, str(cx)); w(20, str(cy)); w(30, "0"); w(40, str(d.get("width", 900)))
        w(0, "LINE"); w(8, "A-DOOR")
        w(10, str(cx)); w(20, str(cy)); w(30, "0")
        w(11, str(cx + dx/length * d.get("width", 900))); w(21, str(cy + dy/length * d.get("width", 900))); w(31, "0")

    for room in rooms:
        w(0, "TEXT"); w(8, "A-TEXT"); w(62, "7")
        w(10, str(room.get("center", {}).get("x", 0))); w(20, str(room.get("center", {}).get("y", 0))); w(30, "0")
        w(40, "300"); w(1, f"{room.get('name', 'Room')} {room.get('area', 0)}m2")
        w(7, "宋体"); w(72, "1"); w(73, "1")

    for f in furniture:
        w(0, "LINE"); w(8, "A-FURN"); w(62, "5")
        hw, hd = f.get("w", 1000)/2, f.get("d", 800)/2
        corners = [(f.get("x",0)-hw, f.get("y",0)-hd), (f.get("x",0)+hw, f.get("y",0)-hd),
                   (f.get("x",0)+hw, f.get("y",0)+hd), (f.get("x",0)-hw, f.get("y",0)+hd)]
        for i in range(4):
            w(0, "LINE"); w(8, "A-FURN"); w(62, "5")
            w(10, str(corners[i][0])); w(20, str(corners[i][1])); w(30, "0")
            w(11, str(corners[(i+1)%4][0])); w(21, str(corners[(i+1)%4][1])); w(31, "0")

    w(0, "ENDSEC")
    w(0, "EOF")
    return "\r\n".join(lines)

# ==================== Combined HTTP Server ====================
class CADHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/export_dxf":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len)
            data = json.loads(body.decode("utf-8"))
            dxf = generate_dxf(data)
            self.send_response(200)
            self.send_header("Content-Type", "application/dxf")
            self.send_header("Content-Disposition", "attachment; filename=floorplan.dxf")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(dxf.encode("utf-8"))
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8780
    server = socketserver.TCPServer(("", port), CADHandler)
    print(f" CAD Server running on http://localhost:{port}")
    print(f"   Static: http://localhost:{port}/interior_cad.html")
    print(f"   DXF POST: http://localhost:{port}/api/export_dxf")
    server.serve_forever()
