import os, json, sys, http.server, urllib.parse, threading, subprocess, tempfile, shutil

wp = r"E:\CAD自动化制图"
sys.path.insert(0, os.path.join(wp, "src"))
web_dir = os.path.join(wp, "web")
output_dir = os.path.join(wp, "output", "orders")

os.makedirs(output_dir, exist_ok=True)

PORT = 8766

class HydroAPIHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Hydraulic CAD Generator API v1.0")
        elif self.path == "/status":
            self._json_response({"status": "ok", "version": "1.0", "engine": "HydroProjectV8"})
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            params = json.loads(body)
            
            if self.path == "/api/generate":
                result = self._generate(params)
                self._json_response(result)
            elif self.path == "/api/preview":
                result = self._preview(params)
                self._json_response(result)
            else:
                self._json_response({"error": "unknown endpoint"}, 404)
        except Exception as e:
            self._json_response({"error": str(e)}, 500)
    
    def _generate(self, params):
        """Generate CAD files based on params"""
        from cad_toolbox_v8 import HydroProjectV8
        from gen_v8_pro import draw_cross_section, draw_generator_floor, draw_turbine_floor, draw_spiral_case_floor
        
        name = params.get("name", "水电站")
        order_id = params.get("order_id", f"order_{int(__import__('time').time())}")
        drawings = params.get("drawings", ["section", "generator", "turbine", "spiral"])
        
        proj = HydroProjectV8(name, "v8")
        proj.setup_all()
        
        out_dir = os.path.join(output_dir, order_id)
        os.makedirs(out_dir, exist_ok=True)
        
        results = []
        drawing_map = {
            "section": ("剖面图", draw_cross_section),
            "generator": ("发电机层", draw_generator_floor),
            "turbine": ("水轮机层", draw_turbine_floor),
            "spiral": ("蜗壳层", draw_spiral_case_floor),
        }
        
        for key in drawings:
            if key in drawing_map:
                cname, fn = drawing_map[key]
                try:
                    fn(proj)
                    dxf_name = f"{order_id}_{cname}.dxf"
                    dxf_path = os.path.join(out_dir, dxf_name)
                    proj.save(dxf_path)
                    results.append({
                        "name": cname,
                        "file": dxf_name,
                        "size": os.path.getsize(dxf_path),
                        "status": "ok"
                    })
                except Exception as e:
                    results.append({"name": cname, "error": str(e), "status": "error"})
        
        # Save combined project
        combined = os.path.join(out_dir, f"{order_id}_全图.dxf")
        proj.save(combined)
        
        return {
            "order_id": order_id,
            "project": name,
            "drawings": results,
            "status": "completed",
            "download_url": f"/api/download/{order_id}"
        }
    
    def _preview(self, params):
        """Generate SVG preview"""
        from cad_toolbox_v8 import HydroProjectV8
        from gen_v8_pro import draw_cross_section
        
        proj = HydroProjectV8(params.get("name", "预览"), "v8")
        proj.setup_all()
        draw_cross_section(proj)
        
        svg_path = os.path.join(output_dir, "preview.svg")
        proj.export_svg(svg_path)
        
        return {"preview_url": "/api/file/preview.svg", "status": "ok"}
    
    def _json_response(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

def run_server():
    server = http.server.HTTPServer(("0.0.0.0", PORT), HydroAPIHandler)
    print(f"Hydraulic CAD API Server running on http://localhost:{PORT}")
    print(f"  POST /api/generate  - 生成图纸")
    print(f"  POST /api/preview   - 生成预览")
    print(f"  GET  /status        - 状态检查")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
