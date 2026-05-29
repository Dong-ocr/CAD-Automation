
# ====================================================================
#  cad_toolbox_v7.py — 岩泊渡水电站 专业施工图工具箱 v7.0
#  功能: 图层管理、尺寸标注、引线标注、剖切符号、图框标题栏、
#        材料表、施工说明、高程符号、轴线网格、填充图案
# ====================================================================
import ezdxf, math, os
from ezdxf.enums import TextEntityAlignment
from ezdxf.math import Vec2
from ezdxf import units
from ezdxf.tools.standards import setup_dimstyle
import ezdxf.zoom as zoom

# =========================== 国标图层配置 ===========================
GB_LAYERS = {
    '0-建筑':        (7, 'CONTINUOUS'),
    'S-CONC-混凝土':  (8, 'CONTINUOUS'),
    'S-REIN-钢筋':    (5, 'CONTINUOUS'),
    'M-EQPM-设备':    (7, 'CONTINUOUS'),
    'M-HYDR-水力':    (4, 'CONTINUOUS'),
    'M-STRU-结构':    (3, 'CONTINUOUS'),
    'A-WALL-墙体':    (7, 'CONTINUOUS'),
    'A-COLM-立柱':    (6, 'CONTINUOUS'),
    'A-OVHD-吊车':    (5, 'DASHED2'),
    'A-ROOF-屋面':    (7, 'CONTINUOUS'),
    'A-FLOR-楼面':    (4, 'CONTINUOUS'),
    'DIM-尺寸':      (3, 'CONTINUOUS'),
    'TEXT-文字':      (7, 'CONTINUOUS'),
    'HATCH-填充':     (8, 'CONTINUOUS'),
    'SYMB-符号':      (6, 'CONTINUOUS'),
    'AXIS-轴线':      (1, 'CENTER2'),
    'HIDN-隐藏':      (5, 'DASHED2'),
    'BORD-图框':      (7, 'CONTINUOUS'),
    'TBLK-标题栏':    (2, 'CONTINUOUS'),
    'LEAD-引线':      (4, 'CONTINUOUS'),
    'NOTE-说明':      (7, 'CONTINUOUS'),
    'VIEWPORTS':     (7, 'CONTINUOUS'),
    'FNDN-基础':      (3, 'CONTINUOUS'),
    'FILL-回填':      (8, 'CONTINUOUS'),
}

PAPER_SIZES = {
    'A0': (841, 1189), 'A1': (594, 841), 'A2': (420, 594),
    'A3': (297, 420), 'A4': (210, 297),
}

class HydroProject:
    def __init__(self, name='岩泊渡水电站'):
        self.name = name
        self.doc = ezdxf.new('R2010', units=units.MM, setup=True)
        self.msp = self.doc.modelspace()
        self._setup_all()
        
    def _setup_all(self):
        self._setup_layers()
        self._setup_dimstyles()
        self._setup_styles()
        self._create_blocks()
        
    def _setup_styles(self):
        for name, font in [('HZ','simsun.ttc'),('TXT','txt'),('COMPLEX','complex')]:
            if name not in self.doc.styles:
                s = self.doc.styles.new(name, dxfattribs={'font': font, 'height': 0})
                if name == 'HZ':
                    s.dxf.width = 0.7
                    
    def _setup_layers(self):
        for name, (c, lt) in GB_LAYERS.items():
            if name not in self.doc.layers:
                try:
                    self.doc.layers.new(name, dxfattribs={'color': c, 'linetype': lt})
                except:
                    pass
        if 'VIEWPORTS' in self.doc.layers:
            self.doc.layers.get('VIEWPORTS').off()
            
    def _setup_dimstyles(self):
        for scale in [50, 100, 150, 200]:
            name = f'GB_DIM_{scale}'
            ds = setup_dimstyle(self.doc, fmt=f'EZ_M_{scale}_H25_CM', name=name)
            if ds:
                ds.dxf.dimtsz = 1.0
                ds.dxf.dimtad = 1
                ds.dxf.dimtix = 0
                ds.dxf.dimclrd = 3
                ds.dxf.dimclre = 3
                ds.dxf.dimclrt = 7
                ds.dxf.dimdec = 0
                ds.dxf.dimzin = 8
                ds.dxf.dimdsep = ord('.')
                ds.dxf.dimtxsty = 'HZ'

    def _create_blocks(self):
        blk = self.doc.blocks
        # 1. 标高符号
        if '标高' not in blk:
            b = blk.new(name='标高')
            b.add_line((-6, 0), (6, 0), dxfattribs={'layer': 'SYMB-符号'})
            b.add_line((6, 0), (0, -5), dxfattribs={'layer': 'SYMB-符号'})
            b.add_line((0, -5), (-6, 0), dxfattribs={'layer': 'SYMB-符号'})
        # 2. 轴线编号
        if '轴号' not in blk:
            b = blk.new(name='轴号')
            b.add_circle((0, 0), 4.5, dxfattribs={'layer': 'AXIS-轴线'})
            b.add_text('', height=3.0, dxfattribs={'layer': 'TEXT-文字', 'style': 'HZ'})
            
    # ====================== 基本绘图方法 ======================
    def line(self, x1, y1, x2, y2, layer='0-建筑', lw=0.18):
        self.msp.add_line((x1, y1), (x2, y2),
            dxfattribs={'layer': layer, 'lineweight': int(lw*100)})
    
    def circle(self, x, y, r, layer='0-建筑', lw=0.18):
        self.msp.add_circle((x, y), r,
            dxfattribs={'layer': layer, 'lineweight': int(lw*100)})
    
    def arc(self, x, y, r, sa, ea, layer='0-建筑', lw=0.18):
        self.msp.add_arc((x, y), r, start_angle=sa, end_angle=ea,
            dxfattribs={'layer': layer, 'lineweight': int(lw*100)})
    
    def rect(self, x1, y1, x2, y2, layer='0-建筑', lw=0.18):
        if x1 > x2: x1, x2 = x2, x1
        if y1 > y2: y1, y2 = y2, y1
        self.msp.add_lwpolyline([(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)],
            dxfattribs={'layer': layer, 'lineweight': int(lw*100)})
    
    def polyline(self, pts, layer='0-建筑', lw=0.18, closed=False):
        if len(pts) < 2: return
        self.msp.add_lwpolyline(pts,
            dxfattribs={'layer': layer, 'lineweight': int(lw*100), 'closed': 1 if closed else 0})
    
    def text(self, txt, x, y, h=2.5, layer='TEXT-文字', rot=0):
        self.msp.add_text(txt, height=h, rotation=rot,
            dxfattribs={'layer': layer, 'style': 'HZ'}
            ).set_placement((x, y), align=TextEntityAlignment.LEFT)
    
    def text_c(self, txt, x, y, h=2.5, layer='TEXT-文字'):
        self.msp.add_text(txt, height=h,
            dxfattribs={'layer': layer, 'style': 'HZ'}
            ).set_placement((x, y), align=TextEntityAlignment.CENTER)
    
    def text_r(self, txt, x, y, h=2.5, layer='TEXT-文字'):
        self.msp.add_text(txt, height=h,
            dxfattribs={'layer': layer, 'style': 'HZ'}
            ).set_placement((x, y), align=TextEntityAlignment.RIGHT)
    
    # ====================== 轴线系统 ======================
    def axis_line(self, x1, y1, x2, y2):
        self.line(x1, y1, x2, y2, 'AXIS-轴线', 0.13)
    
    def axis_circle(self, x, y, label, r=450, h=3.0):
        self.circle(x, y, r, 'AXIS-轴线', 0.18)
        self.text_c(str(label), x, y-1.5, h, 'TEXT-文字')
    
    def axis_grid(self, ox, oy, nx, ny, dx, dy, start_no=1):
        for i in range(nx):
            x = ox + i*dx
            self.axis_line(x, oy, x, oy+(ny-1)*dy)
            self.axis_circle(x, oy-1500, chr(64+start_no+i) if start_no+i<27 else f'{start_no+i}', 450, 3.0)
        for j in range(ny):
            y = oy + j*dy
            self.axis_line(ox, y, ox+(nx-1)*dx, y)
            self.axis_circle(ox-1500, y, j+1, 450, 3.0)
    
    # ====================== 填充 ======================
    def hatch_solid(self, pts, color=253, layer='HATCH-填充'):
        if len(pts) < 3: return
        hatch = self.msp.add_hatch(color=color, dxfattribs={'layer': layer})
        hatch.paths.add_polyline_path(pts, is_closed=True)
    
    def hatch_fill(self, pts, pattern='ANSI31', scale=100, color=8, layer='HATCH-填充'):
        if len(pts) < 3: return
        hatch = self.msp.add_hatch(color=color, dxfattribs={'layer': layer})
        hatch.paths.add_polyline_path(pts, is_closed=True)
        hatch.set_pattern_fill(pattern, scale=scale)
    
    def hatch_rect(self, x1, y1, x2, y2, pattern='ANSI31', scale=100, color=8, layer='HATCH-填充'):
        if x1 > x2: x1, x2 = x2, x1
        if y1 > y2: y1, y2 = y2, y1
        pts = [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]
        self.hatch_fill(pts, pattern, scale, color, layer)
    
    # ====================== 高程 ======================
    def elevation(self, x, y, elev, label='', h=2.5):
        self.msp.add_blockref('标高', (x, y), dxfattribs={'layer': 'SYMB-符号'})
        self.text(f'{elev:.3f}', x+8, y-2, h, 'TEXT-文字')
        if label:
            self.text(label, x+8, y+2, h, 'TEXT-文字')
    
    # ====================== 尺寸标注 ======================
    def dim_h(self, y, x1, x2, text='', scale=100):
        if abs(x2-x1) < 1: return
        ds = f'GB_DIM_{scale}'
        dim = self.msp.add_linear_dim(base=(x1, y), p1=(x1, y), p2=(x2, y), dimstyle=ds)
        if text:
            dim.set_text_format(text)
        dim.render()
    
    def dim_v(self, x, y1, y2, text='', scale=100):
        if abs(y2-y1) < 1: return
        ds = f'GB_DIM_{scale}'
        dim = self.msp.add_linear_dim(base=(x, y1), p1=(x, y1), p2=(x, y2), dimstyle=ds)
        if text:
            dim.set_text_format(text)
        dim.render()
    
    def dim_chain_h(self, y, segments, scale=100):
        for x1, x2, label in segments:
            if abs(x2-x1) > 1:
                ds = f'GB_DIM_{scale}'
                dim = self.msp.add_linear_dim(base=(x1, y), p1=(x1, y), p2=(x2, y), dimstyle=ds)
                if label:
                    dim.set_text_format(f'<> {label}')
                dim.render()
                    
    def dim_chain_v(self, x, segments, scale=100):
        for y1, y2, label in segments:
            if abs(y2-y1) > 1:
                ds = f'GB_DIM_{scale}'
                dim = self.msp.add_linear_dim(base=(x, y1), p1=(x, y1), p2=(x, y2), dimstyle=ds)
                if label:
                    dim.set_text_format(f'<> {label}')
                dim.render()
    
    # ====================== 引线标注 ======================
    def add_leader(self, x1, y1, x2, y2, text, h=3.0, gap=400):
        self.msp.add_line((x1, y1), (x2, y2),
            dxfattribs={'layer': 'LEAD-引线', 'lineweight': 25})
        self.text(text, x2+gap if x2>x1 else x2-gap*3, y2-1.5, h, 'NOTE-说明')
        if gap > 0:
            txt_w = len(text) * h * 0.6
            self.line(x2+gap-50, y2-2, x2+gap+txt_w, y2-2, 'LEAD-引线', 0.15)
    
    # ====================== 剖切符号 ======================
    def section_line(self, label, pts):
        if len(pts) < 2: return
        self.msp.add_lwpolyline(pts, dxfattribs={'layer': 'SYMB-符号', 'lineweight': 60})
        x1, y1 = pts[0]
        x2, y2 = pts[1]
        a = math.degrees(math.atan2(y2-y1, x2-x1))
        self.text_c(label, x1-2000, y1-2000, 4.0, 'SYMB-符号')
        xn, yn = pts[-1]
        xm, ym = pts[-2]
        self.text_c(label, xn-2000, yn-2000, 4.0, 'SYMB-符号')
    
    # ====================== 图纸说明 ======================
    def note_block(self, x, y, w, notes, title='图纸说明'):
        n = len(notes) + 1
        rh = 6.0
        h = n * rh + 4
        self.rect(x, y, x+w, y+h, 'NOTE-说明', 0.35)
        self.line(x, y+h-rh, x+w, y+h-rh, 'NOTE-说明', 0.18)
        self.text_c(title, x+w/2, y+h-rh+1, 3.5, 'NOTE-说明')
        for i, note in enumerate(notes):
            ty = y + h - (i+1)*rh - rh
            self.text(f'{i+1}. {note}', x+3, ty+1, 2.5, 'NOTE-说明')
    
    # ====================== Paper Space 布局 ======================
    def create_layout(self, name, paper_size, scale, view_center, border_mm=15, landscape=False):
        pw, ph = PAPER_SIZES[paper_size]
        if landscape: pw, ph = ph, pw
        layout = self.doc.layouts.new(name)
        layout.page_setup(size=(pw,ph), margins=(border_mm,border_mm,border_mm,border_mm), units='mm')
        for vp in list(layout.query('VIEWPORT')):
            layout.delete_entity(vp)
        vp_w = pw - 2*border_mm
        vp_h = ph - 2*border_mm
        view_h = vp_h * scale
        vp = layout.add_viewport(center=(pw/2,ph/2), size=(vp_w,vp_h),
            view_center_point=view_center, view_height=view_h, status=2)
        vp.dxf.layer = 'VIEWPORTS'
        layout.add_lwpolyline([(0,0),(pw,0),(pw,ph),(0,ph),(0,0)],
            dxfattribs={'layer': 'BORD-图框', 'lineweight': 70})
        layout.add_lwpolyline([(10,10),(pw-10,10),(pw-10,ph-10),(10,ph-10),(10,10)],
            dxfattribs={'layer': 'BORD-图框', 'lineweight': 35})
        return layout, pw, ph
    
    def title_block(self, layout, x, y, w, h, data):
        # 主体
        self._tblk_frame(layout, x, y, w, h)
        # 左半: 项目信息
        rows = [
            ('工程项目', data.get('project','')),
            ('子项名称', data.get('subname','')),
            ('图纸名称', data.get('dname','')),
            ('图号',     data.get('dno','')),
            ('比例',     data.get('scale','')),
            ('阶段',     data.get('stage','施工图')),
            ('日期',     data.get('date','2026.05')),
            ('图幅',     data.get('size','')),
            ('第 张',    data.get('sheets','共 张')),
        ]
        left_w = int(w * 0.65)
        rh = h / len(rows)
        for i, (label, value) in enumerate(rows):
            yy = y + i*rh
            self._tblk_cell(layout, x, yy, left_w, rh, f'{label}: {value}')
        # 右半: 会签栏
        rx = x + left_w
        rw = w - left_w
        sign = [
            ('设计', data.get('designer','')),
            ('制图', data.get('drafter','')),
            ('校对', data.get('checker','')),
            ('审核', data.get('auditor','')),
            ('批准', data.get('approver','')),
            ('审定', data.get('reviewer','')),
            ('专业', data.get('major','水工')),
        ]
        srh = h / len(sign)
        self._tblk_cell(layout, rx, y+h-srh, rw, srh, '会 签')
        for i, (label, value) in enumerate(sign):
            yy = y + i*srh
            self._tblk_cell(layout, rx, yy, rw, srh, f'{label}: {value}')
    
    def _tblk_frame(self, layout, x, y, w, h):
        layout.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)],
            dxfattribs={'layer': 'TBLK-标题栏', 'lineweight': 25})
    
    def _tblk_cell(self, layout, x, y, w, h, text):
        layout.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)],
            dxfattribs={'layer': 'TBLK-标题栏', 'lineweight': 15})
        layout.add_text(text, height=2.5,
            dxfattribs={'layer': 'TEXT-文字', 'style': 'HZ'}
            ).set_placement((x+2, y+1), align=TextEntityAlignment.LEFT)
    
    def material_table(self, layout, x, y, w, materials, scale_mm_per_unit=1):
        headers = ['序号', '名称', '规格/型号', '单位', '数量', '备注']
        cw = [8, 40, 28, 12, 14, 20]
        rh = 6.0
        n = len(materials) + 1
        th = n * rh
        self._tblk_frame(layout, x, y, w, th)
        cx = x
        for hi, (hdr, cw_) in enumerate(zip(headers, cw)):
            layout.add_lwpolyline([(cx,y+th-rh),(cx+cw_,y+th-rh),(cx+cw_,y+th),(cx,y+th),(cx,y+th-rh)],
                dxfattribs={'layer': 'TBLK-标题栏', 'lineweight': 15})
            layout.add_text(hdr, height=2.5,
                dxfattribs={'layer': 'TEXT-文字', 'style': 'HZ'}
                ).set_placement((cx+1, y+th-rh+1), align=TextEntityAlignment.LEFT)
            cx += cw_
        for ri, mat in enumerate(materials):
            ry = y + th - (ri+1)*rh
            cx = x
            for ci, val in enumerate([ri+1, *mat]):
                layout.add_text(str(val), height=2.0,
                    dxfattribs={'layer': 'TEXT-文字', 'style': 'HZ'}
                    ).set_placement((cx+1, ry+1), align=TextEntityAlignment.LEFT)
                cx += cw[ci]
    
    def note_block_ps(self, layout, x, y, w, notes, title='图纸说明'):
        n = len(notes)
        rh = 6.0
        h = (n+1)*rh + 4
        self._tblk_frame(layout, x, y, w, h)
        layout.add_lwpolyline([(x,y+h-rh),(x+w,y+h-rh)],
            dxfattribs={'layer': 'NOTE-说明', 'lineweight': 15})
        layout.add_text(title, height=3.5,
            dxfattribs={'layer': 'TEXT-文字', 'style': 'HZ'}
            ).set_placement((x+w/2, y+h-rh+1), align=TextEntityAlignment.CENTER)
        for i, note in enumerate(notes):
            ty = y + h - (i+1)*rh - rh
            layout.add_text(f'{i+1}. {note}', height=2.5,
                dxfattribs={'layer': 'TEXT-文字', 'style': 'HZ'}
                ).set_placement((x+3, ty+1), align=TextEntityAlignment.LEFT)
    
    # ====================== 输出 ======================
    def save(self, path):
        zoom.extents(self.msp, factor=1.1)
        self.doc.saveas(path)
        return path
