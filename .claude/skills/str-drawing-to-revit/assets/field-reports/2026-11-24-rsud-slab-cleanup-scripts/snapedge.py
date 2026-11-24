import sys,math,numpy as np
from corner import parse,write,area
from cap import overlap_in,simplify,valid_loops
BALL=[l.strip().split(';') for l in open('/mnt/user-data/uploads/RSUD CAKUNG/context/exports/beams_now.csv') if l.strip()]
DEL={'ST-BM-L05-135'}
UPD={'ST-BM-L05-322':(67190,11798,71487,11798),'ST-BM-L01-243':(19747,16302,55215,16302),'ST-BM-L01-306':(20993,15073,20993,79475)}
ADD=[['x','ST-BM-L05-323','L2','LANTAI 5','71427','11798','71427','16334','120','L'],['x','ST-BM-L05-324','L1','LANTAI 5','69547','63078','69547','71192','150','L']]
def beams(lv):
    out=[]
    for b in BALL+ADD:
        if b[3]!=lv or b[1] in DEL or b[9]=='A': continue
        x0,y0,x1,y1=UPD.get(b[1],tuple(map(float,b[4:8])))
        w=float(b[8] or 300)
        if abs(y0-y1)<5: out.append(('H',(y0+y1)/2,min(x0,x1),max(x0,x1),w,b[1]))
        elif abs(x0-x1)<5: out.append(('V',(x0+x1)/2,min(y0,y1),max(y0,y1),w,b[1]))
    return out
def snap(regs,lv,log,DMIN=25,DMAX=260):
    BM=beams(lv)
    for k,(t,lps) in enumerate(regs):
        if t in ('O','R,T'): continue
        p=lps[0]; ccw=area(p)>0
        changed=True; guard=0
        while changed and guard<400:
            changed=False; guard+=1; n=len(p)
            for i in range(n):
                a,b=p[i],p[(i+1)%n]
                if abs(a[1]-b[1])<1: ori='H'; c=a[1]; lo,hi=sorted([a[0],b[0]]); dx=b[0]-a[0]; nrm=(-1 if dx>0 else 1) if ccw else (1 if dx>0 else -1)
                elif abs(a[0]-b[0])<1: ori='V'; c=a[0]; lo,hi=sorted([a[1],b[1]]); dy=b[1]-a[1]; nrm=(1 if dy>0 else -1) if ccw else (-1 if dy>0 else 1)
                else: continue
                L=hi-lo
                if L<300: continue
                if ori=='V' and 67350<c<67950: continue   # dilatation joint edges stay on the joint
                # internal boundary? sample just outside the edge
                from matplotlib.path import Path as _P
                sp=[((lo+hi)/2+0*j, c+nrm*120) if ori=='H' else (c+nrm*120,lo+(hi-lo)*j/4) for j in (1,2,3)] if ori=='V' else [(lo+(hi-lo)*j/4, c+nrm*120) for j in (1,2,3)]
                if any(_P(l2[0]).contains_points(np.array(sp)).any() for k2,(t2,l2) in enumerate(regs) if k2!=k and t2!='O'): continue
                cands=[]
                for (o,bc,b0,b1,w,mk) in BM:
                    if o!=ori: continue
                    face=bc+nrm*w/2; dlt=(face-c)*nrm
                    if not (DMIN<=abs(dlt)<=DMAX): continue
                    if abs(bc-c)>w/2+DMAX: continue
                    ov=max(0,min(hi,b1)-max(lo,b0))
                    if ov>0: cands.append((face,ov,mk))
                if not cands: continue
                # group by face (30mm)
                cands.sort(); best=None
                for f0,_,_ in cands:
                    grp=[x for x in cands if abs(x[0]-f0)<=30]; cov=sum(x[1] for x in grp)
                    if best is None or cov>best[1]: best=(np.mean([x[0] for x in grp]),cov,[x[2] for x in grp])
                if best[1]<0.8*L: continue
                nf=round(best[0])
                new=list(p)
                if ori=='H': new[i]=(a[0],nf); new[(i+1)%n]=(b[0],nf)
                else: new[i]=(nf,a[1]); new[(i+1)%n]=(nf,b[1])
                new=simplify(new)
                bx=(lo-300,min(c,nf)-300,hi+300,max(c,nf)+300) if ori=='H' else (min(c,nf)-300,lo-300,max(c,nf)+300,hi+300)
                before=overlap_in(regs,bx); lps[0]=new
                if valid_loops(lps) and overlap_in(regs,bx)<=before and all(abs(area(h))>0 for h in lps[1:]):
                    log.append((k,t,ori,int(c),'->',nf,int(lo),int(hi),best[2][:3])); p=new; changed=True; break
                lps[0]=p
    return log
if __name__=='__main__':
    NM={'LANTAI1':'LANTAI 1','LANTAI2':'LANTAI 2','LANTAI3':'LANTAI 3','LANTAI4':'LANTAI 4','LANTAI5':'LANTAI 5','LANTAI6':'LANTAI 6','ROOFTOP':'ROOFTOP'}
    for lv in [a for a in sys.argv[1:] if a!='-w']:
        fn='/mnt/user-data/outputs/slab_%s.txt'%lv; regs=parse(fn); log=[]
        nreal=len(regs)
        if lv=='LANTAI1':
            import math as _m
            ap=lambda cx,cy,r,a0,a1:[(cx+r*_m.cos(a0+(a1-a0)*i/40),cy+r*_m.sin(a0+(a1-a0)*i/40)) for i in range(41)]
            T1=ap(9123,21074,4000,_m.pi,1.5*_m.pi)+[(16808,17074)]+ap(16808,12078,4996,_m.pi/2,0)+[(21804,11097)]+ap(24308,11097,2504,_m.pi,1.5*_m.pi)+[(59207,8593),(60304,9690),(67600,9690),(67600,11784),(24308,11784),(24308,21074)]
            regs+= [['R,T',[T1]],['R,T',[[(67700,9690),(95600,9690),(95600,11784),(67700,11784)]]]]
        snap(regs,NM[lv],log); regs=regs[:nreal]
        print(lv,len(log)); [print('  ',x) for x in log]
        if '-w' in sys.argv: write(fn,regs)
