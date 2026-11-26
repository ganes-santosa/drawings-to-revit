import numpy as np,cv2,sys,math
sys.path.insert(0,'/home/claude/slab')
from corner import parse
R=25;X0=-12000;Y0=-12000;W=int(150000/R);H=int(110000/R)
def P(x,y): return (int(round((x-X0)/R)),int(round(H-(y-Y0)/R)))
def mask(fn,extra=[]):
    m=np.zeros((H,W),np.uint8)
    regs=parse(fn)
    for t,lps in regs:
        cv2.fillPoly(m,[np.array([P(*q) for q in lps[0]],np.int32)],1)   # holes are S/D pieces -> slab anyway; O -> opening (counts as inside)
    for poly in extra: cv2.fillPoly(m,[np.array([P(*q) for q in poly],np.int32)],1)
    return m
def arcpts(cx,cy,r,a0,a1,n=40): return [(cx+r*math.cos(a0+(a1-a0)*i/n),cy+r*math.sin(a0+(a1-a0)*i/n)) for i in range(n+1)]
T1=arcpts(9123,21074,4000,math.pi,1.5*math.pi)+[(16808,17074)]+arcpts(16808,12078,4996,math.pi/2,0)+[(21804,11097)]+arcpts(24308,11097,2504,math.pi,1.5*math.pi)+[(59207,8593),(60304,9690),(67600,9690),(67600,11784),(24308,11784),(24308,21074)]
T2=[(67700,9690),(95600,9690),(95600,11784),(67700,11784)]
LV={'LANTAI 1':('LANTAI1',[T1,T2]),'LANTAI 2':('LANTAI2',[]),'LANTAI 3':('LANTAI3',[]),'LANTAI 4':('LANTAI4',[]),'LANTAI 5':('LANTAI5',[[(67700,15500),(87000,15500),(87000,45600),(67700,45600)]]),'LANTAI 6':('LANTAI6',[]),'ROOFTOP':('ROOFTOP',[])}
B=[l.strip().split(';') for l in open('/mnt/user-data/uploads/RSUD CAKUNG/context/exports/beams_now.csv') if l.strip()]
out=[]
for lv,(fn,ex) in LV.items():
    m=mask('/mnt/user-data/outputs/slab_%s.txt'%fn,ex)
    dist=cv2.distanceTransform((1-m).astype(np.uint8),cv2.DIST_L2,5)*R
    for b in B:
        if b[3]!=lv: continue
        x0,y0,x1,y1=map(float,b[4:8]); w=float(b[8] or 300)
        L=math.hypot(x1-x0,y1-y0); n=max(2,int(L/50))
        worst=0; outlen=0
        for i in range(n+1):
            x=x0+(x1-x0)*i/n; y=y0+(y1-y0)*i/n
            px,py=P(x,y)
            if 0<=px<W and 0<=py<H:
                dd=dist[py,px]; worst=max(worst,dd)
                if dd>w/2+60: outlen+=L/n
        if worst>w/2+100: out.append((lv,b[1],b[2],b[9],int(x0),int(y0),int(x1),int(y1),int(worst),int(outlen)))
for o in out: print(o)
print(len(out))
