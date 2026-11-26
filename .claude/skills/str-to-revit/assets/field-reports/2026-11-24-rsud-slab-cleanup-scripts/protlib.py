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
