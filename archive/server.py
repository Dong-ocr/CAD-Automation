import os, sys, json
from socketserver import TCPServer
from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlparse

P = 8780
R = os.path.dirname(os.path.abspath(__file__))
M = {'.html':'text/html; charset=utf-8','.js':'application/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.dxf':'application/dxf'}

def dxf(d):
    L=[]
    def w(c,v):L.extend([str(c),str(v) if not isinstance(v,str) else v])
    w(0,'SECTION');w(2,'HEADER');w(9,'');w(1,'AC1006')
    w(9,'');w(10,'0');w(20,'0');w(30,'0')
    w(0,'ENDSEC')
    w(0,'SECTION');w(2,'TABLES')
    w(0,'TABLE');w(2,'LTYPE');w(70,'4')
    for t,n,ln,p in [('CONTINUOUS','',0,[]),('DASHED','',6,[6,-3]),('CENTER','',16,[8,-2,2,-2]),('DASHDOT','',10,[6,-2,1,-2])]:
        w(0,'LTYPE');w(2,t);w(70,'64');w(3,n);w(72,'65');w(73,str(len(p)//2 if p else 0));w(40,str(ln));w(62,'0')
        for x in p:w(49,str(x))
    w(0,'ENDTAB')
    w(0,'TABLE');w(2,'LAYER');w(70,'9')
    for n,c,l in [('0','7','CONTINUOUS'),('A-WALL','7','CONTINUOUS'),('A-WALL-PART','6','CONTINUOUS'),('A-DOOR','3','CONTINUOUS'),('A-WINDOW','4','CONTINUOUS'),('A-DIM','2','CONTINUOUS'),('A-TEXT','7','CONTINUOUS'),('A-FURN','5','CONTINUOUS'),('A-HATCH','8','CONTINUOUS')]:
        w(0,'LAYER');w(2,n);w(70,'64');w(62,c);w(6,l)
    w(0,'ENDTAB');w(0,'ENDSEC')
    w(0,'SECTION');w(2,'ENTITIES')
    for wd in d.get('walls',[]):
        a='A-WALL' if wd.get('type','')==chr(22806)+chr(22681) else 'A-WALL-PART'
        w(0,'LINE');w(8,a);w(62,'7' if a=='A-WALL' else '6')
        w(10,str(wd['x1']));w(20,str(wd['y1']));w(30,'0')
        w(11,str(wd['x2']));w(21,str(wd['y2']));w(31,'0')
        dx,dy=wd['x2']-wd['x1'],wd['y2']-wd['y1']
        l=(dx*dx+dy*dy)**.5
        if l>0:
            nx,ny=-dy/l*wd.get('thick',200)/2,dx/l*wd.get('thick',200)/2
            w(0,'LINE');w(8,a);w(10,str(wd['x1']+nx));w(20,str(wd['y1']+ny));w(30,'0')
            w(11,str(wd['x2']+nx));w(21,str(wd['y2']+ny));w(31,'0')
    for door in d.get('doors',[]):
        wall=None
        for wd in d.get('walls',[]):
            if wd.get('id')==door.get('wallId'):wall=wd;break
        if not wall:continue
        dx,dy=wall['x2']-wall['x1'],wall['y2']-wall['y1']
        l=(dx*dx+dy*dy)**.5
        if l==0:continue
        r=door.get('pos',0)/l;cx=wall['x1']+dx*r;cy=wall['y1']+dy*r
        w(0,'CIRCLE');w(8,'A-DOOR');w(10,str(cx));w(20,str(cy));w(30,'0');w(40,str(door.get('width',900)))
        w(0,'LINE');w(8,'A-DOOR');w(10,str(cx));w(20,str(cy));w(30,'0')
        w(11,str(cx+dx/l*door.get('width',900)));w(21,str(cy+dy/l*door.get('width',900)));w(31,'0')
    for f in d.get('furniture',[]):
        w(0,'LINE');w(8,'A-FURN');w(62,'5')
        hw,hd=f.get('w',1000)/2,f.get('d',800)/2
        cs=[(f.get('x',0)-hw,f.get('y',0)-hd),(f.get('x',0)+hw,f.get('y',0)-hd),(f.get('x',0)+hw,f.get('y',0)+hd),(f.get('x',0)-hw,f.get('y',0)+hd)]
        for i in range(4):
            w(0,'LINE');w(8,'A-FURN');w(62,'5')
            w(10,str(cs[i][0]));w(20,str(cs[i][1]));w(30,'0')
            w(11,str(cs[(i+1)%4][0]));w(21,str(cs[(i+1)%4][1]));w(31,'0')
    w(0,'ENDSEC');w(0,'EOF')
    return chr(13)+chr(10)+chr(13).join(L)

class H(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=R,**kw)
    def do_GET(self):
        p=urlparse(self.path).path
        try:
            if p=='/api/load_demo':
                dp=os.path.join(R,'demo_project.json')
                if os.path.exists(dp):
                    with open(dp,'r',encoding='utf-8') as f:
                        self.js(json.load(f))
                else:self.js({'error':'no demo'},404)
                return
            if p=='/api/materials':
                mp=os.path.join(R,'materials.json')
                if os.path.exists(mp):
                    md=json.load(open(mp,'r',encoding='utf-8'))
                    for k in list(md.keys()):
                        if isinstance(md[k],str):md[k]={'fallback':md[k],'type':'material'}
                    self.js(md)
                else:self.js({'error':'no'},404)
                return
            if p=='/'or not p:p='/interior_cad.html'
            fp=os.path.normpath(os.path.join(R,p.lstrip('/')))
            if not fp.startswith(R):self.send_error(403);return
            if os.path.isfile(fp):
                e=os.path.splitext(fp)[1].lower()
                with open(fp,'rb') as f:self.raw(f.read(),M.get(e,'application/octet-stream'))
            else:
                fb=os.path.join(R,'interior_cad.html')
                if os.path.isfile(fb):
                    with open(fb,'rb') as f:self.raw(f.read(),'text/html; charset=utf-8')
                else:self.send_error(404)
        except Exception as x:self.send_error(500,str(x))
    def do_POST(self):
        p=urlparse(self.path).path
        try:
            c=int(self.headers.get('Content-Length',0))
            d=json.loads(self.rfile.read(c).decode('utf-8'))
            if p=='/api/export_dxf':
                x=dxf(d)
                self.send_response(200)
                self.send_header('Content-Type','application/dxf')
                self.send_header('Content-Disposition','attachment; filename=plan.dxf')
                self.send_header('Access-Control-Allow-Origin','*')
                self.end_headers();self.wfile.write(x.encode('utf-8'))
            elif p=='/api/save_project':
                n=d.get('name','proj')
                s=''.join(c if c.isalnum() or c in'-_'else'_'for c in n)
                o=os.path.join(R,'projects');os.makedirs(o,exist_ok=True)
                json.dump(d,open(os.path.join(o,s+'.json'),'w',encoding='utf-8'),ensure_ascii=False)
                self.js({'ok':True})
            else:self.js({'error':'?'},404)
        except Exception as x:self.send_error(500,str(x))
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','POST,GET,OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()
    def raw(self,d,m):
        self.send_response(200)
        self.send_header('Content-Type',m);self.send_header('Content-Length',str(len(d)))
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers();self.wfile.write(d)
    def js(self,d,s=200):
        b=json.dumps(d,ensure_ascii=False).encode('utf-8')
        self.send_response(s)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(b)))
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers();self.wfile.write(b)

if __name__=='__main__':
    p=int(sys.argv[1])if len(sys.argv)>1 else P
    s=TCPServer(('',p),H)
    print(' CAD:', 'http://localhost:'+str(p)+'/interior_cad.html', flush=True)
    s.serve_forever()
