import sys
def blocks(lv):
    f='/mnt/user-data/outputs/slab_%s.txt'%lv;regs=[];cur=None
    for s in open(f).read().split('\n'):
        if s.startswith('R,'): cur=[s[2:],[]];regs.append(cur)
        elif s=='L': cur[1].append([])
        elif s=='O': cur=['O',[[]]];regs.append(cur)
        else: cur[1][-1].append(tuple(map(float,s.split(','))))
    return regs
if __name__=='__main__':
    for lv in sys.argv[1:]:
        out=[]
        for t,loops in blocks(lv):
            for li,p in enumerate(loops):
                n=len(p)
                for i in range(n):
                    a,b=p[i],p[(i+1)%n]; L=abs(a[0]-b[0])+abs(a[1]-b[1])
                    if L<400: out.append((t,li,int(a[0]),int(a[1]),int(b[0]),int(b[1]),int(L)))
        print(lv,len(out)); 
        for o in out[:40]: print('  ',o)
