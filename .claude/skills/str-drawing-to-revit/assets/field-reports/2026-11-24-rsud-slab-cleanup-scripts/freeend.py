import math,numpy as np
B=[l.strip().split(';') for l in open('/mnt/user-data/uploads/RSUD CAKUNG/context/exports/beams_now.csv') if l.strip()]
def segd(px,py,x0,y0,x1,y1):
    dx,dy=x1-x0,y1-y0; L2=dx*dx+dy*dy
    t=0 if L2==0 else max(0,min(1,((px-x0)*dx+(py-y0)*dy)/L2))
    return math.hypot(px-(x0+t*dx),py-(y0+t*dy))
import sys
lvs=sys.argv[1:]
for lv in lvs:
    bl=[b for b in B if b[3]==lv]
    for b in bl:
        x0,y0,x1,y1=map(float,b[4:8])
        for (px,py) in ((x0,y0),(x1,y1)):
            near=[o for o in bl if o is not b and segd(px,py,*map(float,o[4:8]))<float(o[8] or 300)/2+260]
            if not near: print(lv,b[1],b[2],int(px),int(py))
