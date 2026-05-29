import os

with open(r"E:\CAD自动化制图\interior_cad.html", "r", encoding="utf-8") as f:
    html = f.read()

# Add texture loader and material presets right after Three.js import and before "CAD DATA MODEL" section
texture_loader_code = """
// ===================== PBR 材质系统 =====================
const texLoader = new THREE.TextureLoader();
const TEXTURE_LIB = {
  "橡木":{color:"./textures/wood_oak/Wood037_1K-JPG_Color.jpg",roughness:"./textures/wood_oak/Wood037_1K-JPG_Roughness.jpg",normal:"./textures/wood_oak/Wood037_1K-JPG_NormalGL.jpg",fallback:"#C4A882"},
  "大理石":{color:"./textures/marble_white/Marble003_1K-JPG_Color.jpg",roughness:"./textures/marble_white/Marble003_1K-JPG_Roughness.jpg",normal:"./textures/marble_white/Marble003_1K-JPG_NormalGL.jpg",fallback:"#E0D8D0"},
  "混凝土":{color:"./textures/concrete/Concrete020_1K-JPG_Color.jpg",roughness:"./textures/concrete/Concrete020_1K-JPG_Roughness.jpg",normal:"./textures/concrete/Concrete020_1K-JPG_NormalGL.jpg",fallback:"#A0A0A0"},
  "天鹅绒":{color:"./textures/fabric_velvet/Fabric013_1K-JPG_Color.jpg",roughness:"./textures/fabric_velvet/Fabric013_1K-JPG_Roughness.jpg",normal:"./textures/fabric_velvet/Fabric013_1K-JPG_NormalGL.jpg",fallback:"#7B6B8A"},
  "纯棉":{color:"./textures/fabric_cotton/Fabric019_1K-JPG_Color.jpg",roughness:"./textures/fabric_cotton/Fabric019_1K-JPG_Roughness.jpg",normal:"./textures/fabric_cotton/Fabric019_1K-JPG_NormalGL.jpg",opacity:"./textures/fabric_cotton/Fabric019_1K-JPG_Opacity.jpg",fallback:"#F0EDE8"},
  "金属":{color:"./textures/metal_brushed/Metal032_1K-JPG_Color.jpg",roughness:"./textures/metal_brushed/Metal032_1K-JPG_Roughness.jpg",normal:"./textures/metal_brushed/Metal032_1K-JPG_NormalGL.jpg",metalness:"./textures/metal_brushed/Metal032_1K-JPG_Metalness.jpg",fallback:"#A0A0A0"},
  "瓷砖":{color:"./textures/tile_ceramic/Tiles065_1K-JPG_Color.jpg",roughness:"./textures/tile_ceramic/Tiles065_1K-JPG_Roughness.jpg",normal:"./textures/tile_ceramic/Tiles065_1K-JPG_NormalGL.jpg",fallback:"#E8E0D0"},
  "皮革":{color:"./textures/leather/Leather008_1K-JPG_Color.jpg",roughness:"./textures/leather/Leather008_1K-JPG_Roughness.jpg",normal:"./textures/leather/Leather008_1K-JPG_NormalGL.jpg",fallback:"#8B5E3C"},
  "墙面":{color:"./textures/plaster_wall/Plaster001_1K-JPG_Color.jpg",roughness:"./textures/plaster_wall/Plaster001_1K-JPG_Roughness.jpg",normal:"./textures/plaster_wall/Plaster001_1K-JPG_NormalGL.jpg",fallback:"#F0EBE5"},
};

const textureCache = {};

function loadPBRMaterial(texName, opts = {}){
  const lib = TEXTURE_LIB[texName];
  if(!lib) return new THREE.MeshStandardMaterial({color:opts.color||"#cccccc",roughness:0.6});
  
  const mat = new THREE.MeshStandardMaterial({
    color: opts.color || undefined,
    roughness: opts.roughness !== undefined ? opts.roughness : 0.6,
    metalness: opts.metalness || 0,
    map: texLoader.load(lib.color),
    roughnessMap: texLoader.load(lib.roughness),
    normalMap: texLoader.load(lib.normal),
  });
  
  if(lib.metalness) mat.metalnessMap = texLoader.load(lib.metalness);
  if(lib.opacity) {
    mat.alphaMap = texLoader.load(lib.opacity);
    mat.transparent = true;
  }
  
  return mat;
}
"""

# Insert after the Three.js import section (find "// ===================== CAD DATA MODEL")
html = html.replace("// ===================== CAD DATA MODEL", texture_loader_code + "\n// ===================== CAD DATA MODEL")

# Update rebuild3D to use PBR materials
old_build = """  const wMat=new THREE.MeshStandardMaterial({color:"#F0EBE5",roughness:0.9});"""
new_build = """  const wMat=loadPBRMaterial("墙面");"""
html = html.replace(old_build, new_build)

# Update floor material
old_floor = """const floorMat3=new THREE.MeshStandardMaterial({color:"#E8E0D6",roughness:0.8});"""
new_floor = """const floorMat3=loadPBRMaterial("橡木",{roughness:0.7});"""
html = html.replace(old_floor, new_floor)

# Add texture selector to the 3D toolbar
toolbar_marker = '<button class="btn3d" onclick="snapshot()"> 截图</button>'
new_toolbar = '<button class="btn3d" onclick="snapshot()"> 截图</button><span style="width:4px"></span><select onchange="changeFloorTexture(this.value)" style="background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.1);border-radius:3px;color:#fff;font-size:10px;padding:2px 4px;cursor:pointer"><option>橡木</option><option>大理石</option><option>混凝土</option><option>瓷砖</option><option>金属</option></select>'
html = html.replace(toolbar_marker, new_toolbar)

# Add changeFloorTexture function
script_end = "console.log("
html = html.replace(script_end, """window.changeFloorTexture=function(name){
  if(!floor3)return;
  const newMat=loadPBRMaterial(name,{roughness:0.7});
  floor3.material.dispose();
  floor3.material=newMat;
  floor3.material.needsUpdate=true;
};
""" + script_end)

with open(r"E:\CAD自动化制图\interior_cad.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Updated: {len(html)} bytes")
print("PBR textures integrated!")
