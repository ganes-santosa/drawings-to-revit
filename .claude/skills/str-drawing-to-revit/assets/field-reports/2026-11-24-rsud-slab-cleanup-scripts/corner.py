import sys,numpy as np
from matplotlib.path import Path
def parse(fn):
    regs=[];cur=None
    for s in open(fn).read().split('\n'):
        if s.startswith('R,'): cur=[s,[]];regs.append(cur)
        elif s=='O': cur=['O',[[]]];regs.append(cur)
        elif s=='L': cur[1].append([])
        elif s.strip(): cur[1][-1].append(tuple(map(float,s.split(','))))
    return regs
def write(fn,regs):
    out=[]
    for t,lps in regs:
        out.append(t)
        if t=='O': out+=['%g,%g'%p for p in lps[0]]
        else:
            for lp in lps: out.append('L'); out+=['%g,%g'%p for p in lp]
    open(fn,'w').write('\n'.join(out))
def area(p): return 0.5*sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))
def d(a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; L=abs(dx)+abs(dy)
    return (np.sign(dx),np.sign(dy)) if (abs(dx)<1 or abs(dy)<1) else None, L
def inside_any(pts,regs,skip):
    for k,(t,lps) in enumerate(regs):
        if k==skip: continue
        outer=Path(lps[0]); m=outer.contains_points(pts)
        for h in lps[1:]: m&=~Path(h).contains_points(pts)
        if m.any(): return True
    return False
def clean(regs,MAX=900):
    log=[]
    for k,(t,lps) in enumerate(regs):
        if t=='O': continue
        changed=True
        while changed:
            changed=False; p=lps[0]; n=len(p)
            if n<6: break
            for i in range(n):
                P=[p[(i+j)%n] for j in range(5)]
                D=[d(P[j],P[j+1]) for j in range(4)]
                if any(x[0] is None for x in D): continue
                (d1,l1),(d2,l2),(d3,l3),(d4,l4)=D
                if not(d3==d1 and d4==d2 and d1[0]*d2[0]+d1[1]*d2[1]==0): continue
                if l2>MAX or l3>MAX or l1<l3 or l4<l2: continue
                Q=(P[3][0],P[1][1]) if d1[1]==0 else (P[1][0],P[3][1])
                new=[q for q in p]; idx=[(i+1)%n,(i+2)%n,(i+3)%n]
                new2=[]
                for j in range(n):
                    if j==idx[0]: new2.append(Q)
                    elif j in idx[1:]: continue
                    else: new2.append(p[j])
                xs=sorted([Q[0],P[2][0]]); ys=sorted([Q[1],P[2][1]])
                g=np.array([(x,y) for x in np.linspace(xs[0]-40,xs[1]+40,9) for y in np.linspace(ys[0]-40,ys[1]+40,9)])
                gi=np.array([(x,y) for x in np.linspace(xs[0]+5,xs[1]-5,7) for y in np.linspace(ys[0]+5,ys[1]-5,7)])
                if inside_any(gi if abs(area(new2))>abs(area(p)) else g,regs,k): continue
                # holes must stay inside
                if any(not Path(new2).contains_points(np.array(h)).all() for h in lps[1:]): continue
                log.append((t,P[1],P[2],P[3],'->',Q,'add' if abs(area(new2))>abs(area(p)) else 'cut'))
                lps[0]=new2; changed=True; break
    return log
if __name__=='__main__':
    for lv in sys.argv[1:]:
        fn='/mnt/user-data/outputs/slab_%s.txt'%lv; regs=parse(fn); lg=clean(regs)
        print(lv,len(lg))
        for l in lg[:60]: print('  ',l)
        if '--w' in sys.argv[0:0]: pass
