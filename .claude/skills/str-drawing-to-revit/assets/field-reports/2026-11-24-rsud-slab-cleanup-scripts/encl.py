from prot import *
import math
res=[]
for lv,(fn,ex) in LV.items():
    sl=mask('/mnt/user-data/outputs/slab_%s.txt'%fn,ex)
    bm=np.zeros((H,W),np.uint8)
    for b in B:
        if b[3]!=lv: continue
        x0,y0,x1,y1=map(float,b[4:8]); w=float(b[8] or 300)
        L=math.hypot(x1-x0,y1-y0)
        if L<1: continue
        ux,uy=(x1-x0)/L,(y1-y0)/L; nx,ny=-uy*w/2,ux*w/2
        poly=[(x0+nx,y0+ny),(x1+nx,y1+ny),(x1-nx,y1-ny),(x0-nx,y0-ny)]
        cv2.fillPoly(bm,[np.array([P(*q) for q in poly],np.int32)],1)
    bm=cv2.dilate(bm,np.ones((5,5),np.uint8))  # close 100mm gaps
    n,lab,st,cen=cv2.connectedComponentsWithStats((1-bm).astype(np.uint8),connectivity=4)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))
    for i in range(1,n):
        if i in border: continue
        comp=lab==i; a=comp.sum()*R*R/1e6
        if a<1.0: continue
        free=(comp&(sl==0)).sum()*R*R/1e6
        if free>1.0 and free/a>0.5:
            x,y,w,h=st[i,:4]; res.append((lv,round(free,1),round(a,1),int(X0+x*R),int(X0+(x+w)*R),int(Y0+(H-y-h)*R),int(Y0+(H-y)*R)))
for r in res: print(r)
