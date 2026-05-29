#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""FreeCAD parametric 3D modeling from demo_project.json"""
import json, os, sys, math

FC_BIN = r"E:\CAD自动化制图\FreeCAD\FreeCAD_1.1.1-Windows-x86_64-py311\bin"
for p in [os.path.join(FC_BIN, '..', 'Lib'), os.path.join(FC_BIN, '..', 'Mod')]:
    if p not in sys.path: sys.path.append(p)

import FreeCAD
import Part
from FreeCAD import Base, Vector

DATA = json.load(open('demo_project.json', 'r', encoding='utf-8'))
walls, rooms, furniture = DATA['w'], DATA['r'], DATA['f']

doc = FreeCAD.newDocument('YanboduHydro')
doc.Label = u'\u5ca9\u6cca\u6e21\u6c34\u7535\u7ad9 - \u5ba4\u5185\u6a21\u578b'

wg = doc.addObject('App::DocumentObjectGroup', 'Walls')
wg.Label = u'\u5899\u4f53'
for i,w in enumerate(walls):
    x1,y1,x2,y2 = w['x1'],w['y1'],w['x2'],w['y2']
    t = w.get('thickness', 240 if w['t']==u'\u5916' else 150)
    h = 2800
    dx,dy = x2-x1,y2-y1; l=math.hypot(dx,dy)
    if l<1: continue
    nx,ny = -dy/l*t/2, dx/l*t/2
    pts = [Vector(x1-nx,y1-ny,0), Vector(x2-nx,y2-ny,0),
           Vector(x2+nx,y2+ny,0), Vector(x1+nx,y1+ny,0), Vector(x1-nx,y1-ny,0)]
    wire = Part.makePolygon(pts)
    solid = Part.Face(wire).extrude(Vector(0,0,h))
    wo = doc.addObject('Part::Feature', 'Wall_'+str(i+1))
    wo.Label = w['t'] + u'\u5899_' + str(i+1)
    wo.Shape = solid
    wg.addObject(wo)

ax = [w['x1'] for w in walls]+[w['x2'] for w in walls]
ay = [w['y1'] for w in walls]+[w['y2'] for w in walls]
floor = doc.addObject('Part::Box', 'Floor')
floor.Label = u'\u697c\u677f'
floor.Length = (max(ax)-min(ax))+600
floor.Width = (max(ay)-min(ay))+600
floor.Height = 200
floor.Placement = Base.Placement(Vector(min(ax)-300,min(ay)-300,-200),Base.Rotation())

fg = doc.addObject('App::DocumentObjectGroup', 'Furniture')
fg.Label = u'\u5bb6\u5177'
for i,f in enumerate(furniture):
    b = doc.addObject('Part::Box', 'Furn_'+str(i+1))
    b.Label = f['n']
    b.Length = f['w']; b.Width = f['d']; b.Height = f.get('h',500)
    b.Placement = Base.Placement(Vector(f['x'],f['y'],0),Base.Rotation())
    fg.addObject(b)

os.makedirs('output/professional', exist_ok=True)
shapes = [o.Shape for o in doc.Objects if hasattr(o,'Shape') and not o.Shape.isNull()]
if shapes:
    Part.makeCompound(shapes).exportStep('output/professional/model_step.stp')
doc.saveAs('output/professional/model_freecad.fcstd')
nw = len([o for o in doc.Objects if 'Wall' in o.Name])
nf = len([o for o in doc.Objects if 'Furn' in o.Name])
print('OK: %d walls, %d furn, %d total objects' % (nw, nf, len(doc.Objects)))
print('STEP: output/professional/model_step.stp')
print('FCStd: output/professional/model_freecad.fcstd')
