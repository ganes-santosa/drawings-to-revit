from protlib import *
import sys
out=[]
for lv,(fn,ex) in LV.items():
    m=mask('/mnt/user-data/outputs/slab_%s.txt'%fn,ex)
    dist=cv2.distanceTransform((1-m).astype(np.uint8),cv2.DIST_L2,5)*R
    for b in B:
        if b[3]!=lv or b[9]=='A': continue
        x0,y0,x1,y1=map(float,b[4:8]); w=float(b[8] or 300); L=math.hypot(x1-x0,y1-y0)
        if L<300: continue
        ux,uy=(x1-x0)/L,(y1-y0)/L
        for sgn in (1,-1):
            nx,ny=-uy*sgn*(w/2-15),ux*sgn*(w/2-15)
            n=int(L/50); vals=[]
            for i in range(n+1):
                t=i/n; x=x0+(x1-x0)*t+nx; y=y0+(y1-y0)*t+ny; px,py=P(x,y)
                vals.append(dist[py,px] if 0<=px<W and 0<=py<H else 9e9)
            vals=np.array(vals); o=(vals>40)&(vals<1200)   # face outside by 40..1200 (near the slab: protrusion, not forecourt)
            # longest run
            run=0;best=0;bmax=0
            for k,v in enumerate(o):
                run=run+1 if v else 0; best=max(best,run)
            if best*50>=900: out.append((lv,b[1],b[2],int(x0),int(y0),int(x1),int(y1),'face',sgn,'out_len',best*50,'max',int(vals[o].max())))
for o in out: print(o)
print(len(out))
