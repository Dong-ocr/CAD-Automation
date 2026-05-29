import os

# Get existing interior_cad.html
with open(r"E:\CAD自动化制图\interior_cad.html", "r", encoding="utf-8") as f:
    html = f.read()

# Find insertion point (before </body>)
# Add modal dialog before </body>
modal = """
<!-- ===================== 参数化户型生成对话框 ===================== -->
<div id="gen-modal" style="display:none;position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.6);backdrop-filter:blur(4px);display:none;align-items:center;justify-content:center">
<div style="background:#1e1e3a;border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:24px;width:420px;max-height:80vh;overflow-y:auto">
  <h3 style="margin-bottom:16px"> 参数化户型生成</h3>
  
  <label style="font-size:11px;color:rgba(255,255,255,0.5);display:block;margin-top:8px">整体尺寸 (mm)</label>
  <div style="display:flex;gap:8px">
    <input id="gw" value="10000" style="flex:1;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:4px;padding:6px 8px;color:#fff;font-size:13px"> <span style="color:rgba(255,255,255,0.3);line-height:32px">×</span>
    <input id="gd" value="8000" style="flex:1;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:4px;padding:6px 8px;color:#fff;font-size:13px">
  </div>

  <label style="font-size:11px;color:rgba(255,255,255,0.5);display:block;margin-top:12px">房间配置</label>
  <div id="room-configs">
    <div class="room-row" style="display:flex;gap:4px;margin-bottom:4px">
      <input value="客厅" style="width:70px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);border-radius:3px;padding:4px 6px;color:#fff;font-size:11px">
      <input value="25" style="width:50px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);border-radius:3px;padding:4px 6px;color:#fff;font-size:11px" placeholder="m2">
      <select style="flex:1;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);border-radius:3px;padding:4px 6px;color:#fff;font-size:11px">
        <option>客厅</option><option>卧室</option><option>厨房</option><option>卫生间</option><option>餐厅</option><option>书房</option><option>阳台</option>
      </select>
    </div>
  </div>
  <button onclick="addRoomRow()" style="background:transparent;border:1px dashed rgba(255,255,255,0.2);border-radius:3px;padding:3px 10px;color:rgba(255,255,255,0.5);cursor:pointer;font-size:11px;margin-top:4px">+ 添加房间</button>

  <div style="margin-top:16px;display:flex;gap:8px;justify-content:flex-end">
    <button onclick="closeGenModal()" style="padding:6px 16px;border:1px solid rgba(255,255,255,0.15);border-radius:4px;background:transparent;color:#fff;cursor:pointer;font-size:12px">取消</button>
    <button onclick="generatePlan()" style="padding:6px 16px;border:none;border-radius:4px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;cursor:pointer;font-size:12px"> 生成布局</button>
  </div>
</div>
</div>

<script>
// ===================== 参数化户型生成器 =====================
// 基于递归二分切割算法

function addRoomRow(name, area, type) {
  const cont = document.getElementById("room-configs");
  const div = document.createElement("div");
  div.className = "room-row";
  div.style.cssText = "display:flex;gap:4px;margin-bottom:4px";
  div.innerHTML = [
    '<input value="'+(name||"房间")+'" style="width:70px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);border-radius:3px;padding:4px 6px;color:#fff;font-size:11px">',
    '<input value="'+(area||"10")+'" style="width:50px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);border-radius:3px;padding:4px 6px;color:#fff;font-size:11px" placeholder="m2">',
    '<select style="flex:1;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);border-radius:3px;padding:4px 6px;color:#fff;font-size:11px">',
    '<option>客厅</option><option>卧室</option><option>厨房</option><option>卫生间</option><option>餐厅</option><option>书房</option><option>阳台</option></select>',
    '<button onclick="this.parentElement.remove()" style="background:transparent;border:none;color:#e74c3c;cursor:pointer;font-size:14px">×</button>',
  ].join("");
  if(type) div.querySelector("select").value = type;
  cont.appendChild(div);
}

// 初始房间配置
addRoomRow("客厅", 25, "客厅");
addRoomRow("主卧", 18, "卧室");
addRoomRow("次卧", 14, "卧室");
addRoomRow("厨房", 8, "厨房");
addRoomRow("卫生间", 5, "卫生间");
addRoomRow("餐厅", 12, "餐厅");

window.openGenModal = function() {
  document.getElementById("gen-modal").style.display = "flex";
};
window.closeGenModal = function() {
  document.getElementById("gen-modal").style.display = "none";
};

window.generatePlan = function() {
  const totalW = parseFloat(document.getElementById("gw").value) || 10000;
  const totalD = parseFloat(document.getElementById("gd").value) || 8000;

  // Read room configs
  const rows = document.querySelectorAll("#room-configs .room-row");
  const rooms_config = [];
  let totalTarget = 0;
  for(const row of rows){
    const inputs = row.querySelectorAll("input");
    const sel = row.querySelector("select");
    if(!inputs[0]||!inputs[1])continue;
    const name = inputs[0].value;
    const area = parseFloat(inputs[1].value) || 10;
    const type = sel ? sel.value : "房间";
    rooms_config.push({name, area, type});
    totalTarget += area;
  }

  if(rooms_config.length < 2) { alert("至少需要2个房间"); return; }

  // Scale areas to fit total
  const totalArea = (totalW * totalD) / 1e6;
  const scale = totalArea / totalTarget;
  rooms_config.forEach(r => r.targetArea = r.area * scale);

  // Layout algorithm: grid-based slicing
  // Sort rooms by area (descending)
  rooms_config.sort((a,b) => b.targetArea - a.targetArea);

  // Start with whole space
  const spaces = [{x:0, y:0, w:totalW, d:totalD, rooms: [...rooms_config]}];

  const final_rooms = [];

  function splitSpace(space, room) {
    const rArea = room.targetArea * 1e6;
    const currentArea = space.w * space.d;
    if(currentArea <= rArea * 1.2) {
      // Room fits
      final_rooms.push({name: room.name, type: room.type, x: space.x, y: space.y, w: space.w, d: space.d});
      return [];
    }
    // Need to split - allocate portion for this room
    const ratio = rArea / currentArea;
    // Decide split direction (wider side splits)
    if(space.w >= space.d) {
      // Vertical split
      const roomW = space.w * Math.sqrt(ratio);
      final_rooms.push({name: room.name, type: room.type, x: space.x, y: space.y, w: Math.max(roomW, 1500), d: space.d});
      return [{x: space.x + Math.max(roomW, 1500), y: space.y, w: space.w - Math.max(roomW, 1500), d: space.d}];
    } else {
      // Horizontal split
      const roomD = space.d * Math.sqrt(ratio);
      final_rooms.push({name: room.name, type: room.type, x: space.x, y: space.y, w: space.w, d: Math.max(roomD, 1500)});
      return [{x: space.x, y: space.y + Math.max(roomD, 1500), w: space.w, d: space.d - Math.max(roomD, 1500)}];
    }
  }

  let remaining = rooms_config.slice();
  let currentSpaces = [{x:0, y:0, w:totalW, d:totalD}];

  for(const room of remaining) {
    if(currentSpaces.length === 0) break;
    // Find the best space for this room
    const space = currentSpaces.shift();
    const newSpaces = splitSpace(space, room);
    currentSpaces.push(...newSpaces);
  }

  // Remaining space becomes hallway
  for(const s of currentSpaces) {
    if(s.w > 800 && s.d > 800) {
      final_rooms.push({name: "过道", type: "过道", x: s.x, y: s.y, w: s.w, d: s.d});
    }
  }

  // Generate walls from rooms
  const newWalls = [];
  const newRooms = [];
  const newDoors = [];
  const newWindows = [];

  const colors = {"客厅":"#667eea","卧室":"#f093fb","厨房":"#43e97b","卫生间":"#fa709a","餐厅":"#764ba2","书房":"#4facfe","阳台":"#84fab0","过道":"#a8a8a8"};

  for(const r of final_rooms) {
    // Room polygon
    const corners = [
      {x: r.x, y: r.y},
      {x: r.x + r.w, y: r.y},
      {x: r.x + r.w, y: r.y + r.d},
      {x: r.x, y: r.y + r.d},
    ];
    const area_m2 = (r.w * r.d) / 1e6;
    newRooms.push({
      id: nextId++, name: r.name, type: r.type,
      corners: corners,
      color: colors[r.type] || "#888888",
      area: Math.round(area_m2 * 10) / 10
    });

    // Walls (only exterior - interior shared walls handled by adjacency)
    const ws = [
      {x1:r.x,y1:r.y,x2:r.x+r.w,y2:r.y},
      {x1:r.x+r.w,y1:r.y,x2:r.x+r.w,y2:r.y+r.d},
      {x1:r.x+r.w,y1:r.y+r.d,x2:r.x,y2:r.y+r.d},
      {x1:r.x,y1:r.y+r.d,x2:r.x,y2:r.y},
    ];
    for(const w of ws) {
      // Check if wall already exists (within tolerance)
      let found = false;
      for(const ew of newWalls) {
        const d1 = Math.hypot(ew.x1-w.x1, ew.y1-w.y1) + Math.hypot(ew.x2-w.x2, ew.y2-w.y2);
        const d2 = Math.hypot(ew.x1-w.x2, ew.y1-w.y2) + Math.hypot(ew.x2-w.x1, ew.y2-w.y1);
        if(d1 < 50 || d2 < 50) { found = true; break; }
      }
      if(!found) {
        const dx = w.x2-w.x1, dy = w.y2-w.y1;
        const len = Math.hypot(dx, dy);
        if(len > 100) {
          newWalls.push({id: nextId++, x1:w.x1, y1:w.y1, x2:w.x2, y2:w.y2,
            thick: (w.x1===0||w.x1===totalW||w.y1===0||w.y1===totalD||w.x2===0||w.x2===totalW||w.y2===0||w.y2===totalD) ? 240 : 150,
            type: (w.x1===0||w.x1===totalW||w.y1===0||w.y1===totalD||w.x2===0||w.x2===totalW||w.y2===0||w.y2===totalD) ? "外墙" : "内墙"
          });
        }
      }
    }
  }

  // Add doors (one per room, on the longest wall)
  for(const r of final_rooms) {
    const ws = [
      {x1:r.x,y1:r.y,x2:r.x+r.w,y2:r.y, side:"top"},
      {x1:r.x+r.w,y1:r.y,x2:r.x+r.w,y2:r.y+r.d, side:"right"},
      {x1:r.x+r.w,y1:r.y+r.d,x2:r.x,y2:r.y+r.d, side:"bottom"},
      {x1:r.x,y1:r.y+r.d,x2:r.x,y2:r.y, side:"left"},
    ];
    // Find the wall that connects to another room or is exterior
    for(const w of ws) {
      const dx = w.x2-w.x1, dy = w.y2-w.y1;
      const len = Math.hypot(dx, dy);
      if(len > 2000) {
        const pos = len * 0.3;
        // Find matching wall
        let wallId = null;
        for(const nw of newWalls) {
          const d1 = Math.hypot(nw.x1-w.x1, nw.y1-w.y1) + Math.hypot(nw.x2-w.x2, nw.y2-w.y2);
          const d2 = Math.hypot(nw.x1-w.x2, nw.y1-w.y2) + Math.hypot(nw.x2-w.x1, nw.y2-w.y1);
          if(d1 < 50 || d2 < 50) { wallId = nw.id; break; }
        }
        if(wallId && len > 1500) {
          newDoors.push({id: nextId++, wallId, pos, width: 900});
          break;
        }
      }
    }
  }

  // Clear and load
  if(!confirm("将清空当前绘图并加载生成户型，确定？")) return;

  walls.length = 0; doors.length = 0; windows.length = 0;
  rooms.length = 0; dims.length = 0; furniture.length = 0;

  newWalls.forEach(w => walls.push(w));
  newDoors.forEach(d => doors.push(d));
  newRooms.forEach(r => rooms.push(r));

  saveState();
  closeGenModal();
  render2D();
  rebuild3D();
  updateStatus();
  zoomFit();
  document.getElementById("tool-status").textContent = ` 户型已生成: ${rooms.length}个房间`;

  // Add furniture suggestions
  for(const r of final_rooms) {
    if(r.type === "卧室") {
      furniture.push({id:nextId++,name:"双人床",cat:"",x:r.x+r.w*0.3,y:r.y+r.d*0.4,w:2000,d:1800,color:"#D2B48C"});
      furniture.push({id:nextId++,name:"衣柜",cat:"",x:r.x+r.w*0.8,y:r.y+r.d*0.2,w:1800,d:600,color:"#C4A882"});
    } else if(r.type === "客厅") {
      furniture.push({id:nextId++,name:"沙发",cat:"",x:r.x+r.w*0.3,y:r.y+r.d*0.7,w:2200,d:850,color:"#8B4513"});
      furniture.push({id:nextId++,name:"茶几",cat:"",x:r.x+r.w*0.5,y:r.y+r.d*0.5,w:1200,d:600,color:"#D2691E"});
      furniture.push({id:nextId++,name:"电视柜",cat:"",x:r.x+r.w*0.5,y:r.y+r.d*0.15,w:1800,d:400,color:"#3C3C3C"});
    } else if(r.type === "餐厅") {
      furniture.push({id:nextId++,name:"餐桌",cat:"",x:r.x+r.w*0.5,y:r.y+r.d*0.5,w:1400,d:800,color:"#DEB887"});
      furniture.push({id:nextId++,name:"餐椅",cat:"",x:r.x+r.w*0.35,y:r.y+r.d*0.65,w:480,d:520,color:"#C4A882"});
      furniture.push({id:nextId++,name:"餐椅",cat:"",x:r.x+r.w*0.65,y:r.y+r.d*0.65,w:480,d:520,color:"#C4A882"});
    } else if(r.type === "厨房") {
      furniture.push({id:nextId++,name:"冰箱",cat:"",x:r.x+r.w*0.85,y:r.y+r.d*0.5,w:900,d:800,color:"#C0C0C0"});
    } else if(r.type === "卫生间") {
      furniture.push({id:nextId++,name:"马桶",cat:"",x:r.x+r.w*0.3,y:r.y+r.d*0.3,w:400,d:700,color:"#F5F5F5"});
      furniture.push({id:nextId++,name:"洗手盆",cat:"",x:r.x+r.w*0.7,y:r.y+r.d*0.7,w:600,d:500,color:"#FFFFFF"});
    }
  }
  saveState();
  render2D();
  rebuild3D();
  updateStatus();
};

// Add generate button to header
document.addEventListener("DOMContentLoaded", function() {
  const header = document.getElementById("header");
  if(header) {
    const genBtn = document.createElement("button");
    genBtn.className = "btn btn-p";
    genBtn.innerHTML = " 生成";
    genBtn.onclick = window.openGenModal;
    const exportBtn = header.querySelector('[onclick="exportDXF()"]');
    if(exportBtn) header.insertBefore(genBtn, exportBtn);
    else header.appendChild(genBtn);
  }
});
</script>
"""

# Insert before closing body tag
html = html.replace("</body>", modal + "\n</body>")

with open(r"E:\CAD自动化制图\interior_cad.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Updated: {len(html)} bytes")
print("Parametric generator added!")
