import json, os, textwrap, time

# ====== Generate the optimized interior_cad.html ======

# Materials data (with fallback colors, no texture paths - loaded progressively)
materials = {
    "墙面": "#F0EBE5",
    "橡木": "#C4A882",
    "大理石": "#E0D8D0",
    "混凝土": "#A0A0A0",
    "瓷砖": "#E8E0D0",
    "金属": "#A0A0A0",
    "皮革": "#8B5E3C",
    "天鹅绒": "#7B6B8A",
    "纯棉": "#F0EDE8",
    "地板深色": "#6B4226",
    "地板浅色": "#DEB887",
    "地毯": "#8B7D6B",
    "玻璃": "#ADD8E6",
    "白色": "#F5F5F5",
    "黑色": "#2C2C2C",
    "红色": "#8B0000",
    "蓝色": "#00008B",
    "绿色": "#006400",
}

# Furniture library
furniture_lib = {
    "双人床": {"w": 2000, "d": 1800, "color": "#D2B48C", "height": 450},
    "单人床": {"w": 1200, "d": 2000, "color": "#D2B48C", "height": 450},
    "沙发": {"w": 2200, "d": 850, "color": "#8B4513", "height": 800},
    "L型沙发": {"w": 2800, "d": 1600, "color": "#8B4513", "height": 800},
    "茶几": {"w": 1200, "d": 600, "color": "#D2691E", "height": 450},
    "餐桌": {"w": 1400, "d": 800, "color": "#DEB887", "height": 750},
    "餐椅": {"w": 480, "d": 520, "color": "#C4A882", "height": 450},
    "衣柜": {"w": 1800, "d": 600, "color": "#C4A882", "height": 2000},
    "书桌": {"w": 1200, "d": 600, "color": "#8B7355", "height": 750},
    "电视柜": {"w": 1800, "d": 400, "color": "#3C3C3C", "height": 500},
    "冰箱": {"w": 900, "d": 800, "color": "#C0C0C0", "height": 1800},
    "洗衣机": {"w": 600, "d": 600, "color": "#E0E0E0", "height": 850},
    "马桶": {"w": 400, "d": 700, "color": "#F5F5F5", "height": 400},
    "洗手盆": {"w": 600, "d": 500, "color": "#FFFFFF", "height": 800},
    "淋浴房": {"w": 900, "d": 900, "color": "#D0E0F0", "height": 2000},
    "灶台": {"w": 800, "d": 600, "color": "#2C2C2C", "height": 850},
    "水槽": {"w": 800, "d": 600, "color": "#A0A0A0", "height": 850},
    "钢琴": {"w": 1500, "d": 600, "color": "#1A1A1A", "height": 1200},
    "书架": {"w": 800, "d": 400, "color": "#8B7355", "height": 1800},
    "鞋柜": {"w": 800, "d": 350, "color": "#C4A882", "height": 1000},
}

# Room templates
room_templates = {
    "客厅": {"min_area": 15, "max_area": 50, "furniture": ["沙发", "茶几", "电视柜"]},
    "主卧": {"min_area": 12, "max_area": 30, "furniture": ["双人床", "衣柜", "书桌"]},
    "次卧": {"min_area": 8, "max_area": 20, "furniture": ["单人床", "衣柜", "书桌"]},
    "厨房": {"min_area": 5, "max_area": 15, "furniture": ["灶台", "水槽", "冰箱"]},
    "卫生间": {"min_area": 3, "max_area": 10, "furniture": ["马桶", "洗手盆", "淋浴房"]},
    "餐厅": {"min_area": 8, "max_area": 25, "furniture": ["餐桌", "餐椅"]},
    "书房": {"min_area": 6, "max_area": 20, "furniture": ["书桌", "书架"]},
    "阳台": {"min_area": 3, "max_area": 15, "furniture": []},
    "衣帽间": {"min_area": 4, "max_area": 15, "furniture": ["衣柜"]},
    "储物间": {"min_area": 2, "max_area": 10, "furniture": []},
}

print("Generating interior_cad.html...")
