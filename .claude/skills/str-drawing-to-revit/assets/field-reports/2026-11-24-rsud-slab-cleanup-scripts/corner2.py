from corner import *
def stair(p,i):
    n=len(p); P=[p[(i+j)%n] for j in range(5)]; D=[d(P[j],P[j+1]) for j in range(4)]
    if any(x[0] is None for x in D): return None
    (d1,l1),(d2,l2),(d3,l3),(d4,l4)=D
    if not(d3==d1 and d4==d2 and d1[0]*d2[0]+d1[1]*d2[1]==0 and l2<=900 and l3<=900 and l1>=60 and l4>=60): return None
    Q=(P[3][0],P[1][1]) if d1[1]==0 else (P[1][0],P[3][1])
    new=[]
    for j in range(n):
        if j==(i+1)%n: new.append(Q)
        elif j in ((i+2)%n,(i+3)%n): continue
        else: new.append(p[j])
    xs=sorted([Q[0],P[2][0]]); ys=sorted([Q[1],P[2][1]])
    gi=np.array([(x,y) for x in np.linspace(xs[0]+5,xs[1]-5,7) for y in np.linspace(ys[0]+5,ys[1]-5,7)])
    return new,gi,abs(area(new))-abs(area(p)),P
def covered(gi,regs,k,li):   # points inside region k (excluding hole li) -> conflict test
    t,lps=regs[k]; m=Path(lps[0]).contains_points(gi)
    for j,h in enumerate(lps[1:],1):
        if j!=li: m&=~Path(h).contains_points(gi)
    return m.any()
def clean2(regs):
    log=[]
    # pass 1: outer loops of B/S/D: fill corner steps (add only); S may fill into its parent B hole
    for k,(t,lps) in enumerate(regs):
        if t=='O': continue
        go=True
        while go:
            go=False; p=lps[0]
            for i in range(len(p)):
                r=stair(p,i)
                if not r: continue
                new,gi,da,P=r
                if da<=0: continue
                hits=[kk for kk in range(len(regs)) if kk!=k and covered(gi,regs,kk,-1)]
                if hits and not (t=='R,S' and all(regs[h][0]=='R,B' for h in hits)): continue
                if any(not Path(new).contains_points(np.array(h)).all() for h in lps[1:]): continue
                lps[0]=new; log.append((k,t,'outer',P[2],'fill %.0f'%da)); go=True; break
    # pass 2: B holes: enlarge hole where the region is now an S piece
    S=[ (kk,l) for kk,(tt,l) in enumerate(regs) if tt=='R,S']
    for k,(t,lps) in enumerate(regs):
        if t!='R,B': continue
        for li in range(1,len(lps)):
            go=True
            while go:
                go=False; p=lps[li]
                for i in range(len(p)):
                    r=stair(p,i)
                    if not r: continue
                    new,gi,da,P=r
                    if da<=0: continue   # hole grows
                    # removed B area must lie inside an S piece grown by 25
                    ok=any(Path(l[0]).contains_points(gi,radius=50).all() or Path(l[0]).contains_points(gi,radius=-50).all() for kk,l in S)
                    if not ok: continue
                    lps[li]=new; log.append((k,t,'hole',P[2],'grow %.0f'%da)); go=True; break
    return log
if __name__=='__main__':
    import sys
    for lv in sys.argv[1:]:
        if lv=='-w': continue
        fn='/mnt/user-data/outputs/slab_%s.txt'%lv; regs=parse(fn); lg=clean2(regs)
        print(lv,len(lg)); [print('  ',x) for x in lg]
        if '-w' in sys.argv: write(fn,regs)
def pairs(regs):
    log=[]
    for k,(t,lps) in enumerate(regs):
        if t!='R,B': continue
        go=True
        while go:
            go=False; p=lps[0]
            for i in range(len(p)):
                r=stair(p,i)
                if not r or r[2]<=0: continue
                new,gi,da,P=r
                hits=[kk for kk in range(len(regs)) if kk!=k and covered(gi,regs,kk,-1)]
                if len(hits)!=1 or regs[hits[0]][0]!='R,D': continue
                h=hits[0]; q=regs[h][1][0]; done=False
                for j in range(len(q)):
                    r2=stair(q,j)
                    if not r2 or r2[2]>=0: continue
                    new2,gi2,da2,P2=r2
                    if abs(abs(da2)-da)/da<0.35 and Path(p).contains_points(gi2,radius=60).all() is not None:
                        # removed D rect must lie inside the B-filled rect grown 60
                        xs=sorted([gi[:,0].min()-70,gi[:,0].max()+70]); ys=sorted([gi[:,1].min()-70,gi[:,1].max()+70])
                        if ((gi2[:,0]>=xs[0])&(gi2[:,0]<=xs[1])&(gi2[:,1]>=ys[0])&(gi2[:,1]<=ys[1])).all():
                            lps[0]=new; regs[h][1][0]=new2; log.append((k,h,P[2],'B fill %.0f / D cut %.0f'%(da,da2))); done=True; break
                if done: go=True; break
    return log
if __name__=='__main__':
    for lv in sys.argv[1:]:
        if lv=='-w': continue
        fn='/mnt/user-data/outputs/slab_%s.txt'%lv; regs=parse(fn); clean2(regs); lg=pairs(regs)
        print('pairs',lv,lg)
