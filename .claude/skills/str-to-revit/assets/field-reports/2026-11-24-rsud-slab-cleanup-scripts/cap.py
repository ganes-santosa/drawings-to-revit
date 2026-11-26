from corner import *
import cv2
R=10.0
def simplify(p):
    q=[]
    for v in p:
        if q and abs(q[-1][0]-v[0])<1 and abs(q[-1][1]-v[1])<1: continue
        q.append(v)
    if len(q)>1 and abs(q[0][0]-q[-1][0])<1 and abs(q[0][1]-q[-1][1])<1: q.pop()
    ch=True
    while ch and len(q)>3:
        ch=False
        for i in range(len(q)):
            a,b,c=q[i-1],q[i],q[(i+1)%len(q)]
            if (abs(a[0]-b[0])<1 and abs(b[0]-c[0])<1) or (abs(a[1]-b[1])<1 and abs(b[1]-c[1])<1):
                q.pop(i); ch=True; break
    return q
OUTER=[True]
def caps(p):
    n=len(p); res=[]
    for i in range(n):
        P=[p[(i+j)%n] for j in range(4)]
        D=[d(P[j],P[j+1]) for j in range(3)]
        if any(x[0] is None for x in D): continue
        (db,lb),(dc,lc),(dd,ld)=D
        if db!=(-dd[0],-dd[1]) or db[0]*dc[0]+db[1]*dc[1]!=0: continue
        m=min(lb,ld)
        if (lc<=900 and max(lb,ld)<=1000) or (lc<=120 and OUTER[0]):
            sx,sy=-db[0]*m,-db[1]*m
            P2=(P[1][0]+sx,P[1][1]+sy); P3=(P[2][0]+sx,P[2][1]+sy)
            new=list(p); new[(i+1)%n]=P2; new[(i+2)%n]=P3
            res.append((i,simplify(new),P,lc,m))
    return res
def polymask(lps,shape,org):
    m=np.zeros(shape,np.uint8)
    f=lambda q:[(int(round((x-org[0])/R)),int(round((y-org[1])/R))) for x,y in q]
    cv2.fillPoly(m,[np.array(f(lps[0]),np.int32)],1)
    for h in lps[1:]: cv2.fillPoly(m,[np.array(f(h),np.int32)],0)
    return m
def overlap_in(regs,box):
    x0,y0,x1,y1=box; org=(x0-100,y0-100); shape=(int((y1-y0+200)/R)+1,int((x1-x0+200)/R)+1)
    acc=np.zeros(shape,np.int16)
    for t,lps in regs:
        if t=='O': continue
        xs=[q[0] for q in lps[0]]; ys=[q[1] for q in lps[0]]
        if max(xs)<x0-100 or min(xs)>x1+100 or max(ys)<y0-100 or min(ys)>y1+100: continue
        acc+=polymask(lps,shape,org)
    return int((acc>1).sum())
def box(P,pad=50):
    xs=[q[0] for q in P]; ys=[q[1] for q in P]; return (min(xs)-pad,min(ys)-pad,max(xs)+pad,max(ys)+pad)
def run(regs,log):
    changed=True; it=0
    while changed and it<200:
        changed=False; it+=1
        for k,(t,lps) in enumerate(regs):
            if t=='O': continue
            for li in range(len(lps)):
                OUTER[0]=(li==0)
                for (i,new,P,lc,m) in caps(lps[li]):
                    bx=box(P); before=overlap_in(regs,bx)
                    old=lps[li]; lps[li]=new
                    if valid_loops(lps) and overlap_in(regs,bx)<=before:
                        log.append((k,t,li,P[1],P[2],int(lc),int(m))); changed=True; break
                    # try pair: collapse a cap in another piece in the same box
                    ok=False
                    for k2,(t2,l2) in enumerate(regs):
                        if k2==k or t2=='O': continue
                        for lj in range(len(l2)):
                            for (i2,new2,P2,lc2,m2) in caps(l2[lj]):
                                b2=box(P2)
                                if b2[0]>bx[2] or b2[2]<bx[0] or b2[1]>bx[3] or b2[3]<bx[1]: continue
                                o2=l2[lj]; l2[lj]=new2
                                if valid_loops(l2) and overlap_in(regs,(min(bx[0],b2[0]),min(bx[1],b2[1]),max(bx[2],b2[2]),max(bx[3],b2[3])))<=before:
                                    log.append((k,t,li,P[1],P[2],int(lc),int(m),'pair',k2,t2)); ok=True; break
                                l2[lj]=o2
                            if ok: break
                        if ok: break
                    if ok: changed=True; break
                    lps[li]=old
                if changed: break
            if changed: break
def valid_loops(lps):
    for p in lps:
        if len(p)<4: return False
        n=len(p)
        segs=[(p[i],p[(i+1)%n]) for i in range(n)]
        for a in range(n):
            for b in range(a+2,n):
                if a==0 and b==n-1: continue
                (p1,p2),(p3,p4)=segs[a],segs[b]
                if inter(p1,p2,p3,p4): return False
    return True
def inter(a,b,c,d_):
    def o(p,q,r): v=(q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]); return 0 if abs(v)<1e-6 else (1 if v>0 else -1)
    o1,o2,o3,o4=o(a,b,c),o(a,b,d_),o(c,d_,a),o(c,d_,b)
    if o1!=o2 and o3!=o4 and 0 not in (o1,o2,o3,o4): return True
    def on(p,q,r): return min(p[0],r[0])-0.5<=q[0]<=max(p[0],r[0])+0.5 and min(p[1],r[1])-0.5<=q[1]<=max(p[1],r[1])+0.5
    if o1==0 and on(a,c,b): return True
    if o2==0 and on(a,d_,b): return True
    if o3==0 and on(c,a,d_): return True
    if o4==0 and on(c,b,d_): return True
    return False
if __name__=='__main__':
    import sys
    for lv in [a for a in sys.argv[1:] if a!='-w']:
        fn='/mnt/user-data/outputs/slab_%s.txt'%lv; regs=parse(fn)
        for t,lps in regs:
            for i in range(len(lps)): lps[i]=simplify(lps[i])
        log=[]; run(regs,log); print(lv,len(log)); [print('  ',x) for x in log]
        if '-w' in sys.argv: write(fn,regs)
