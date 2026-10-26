"""Вырезание экранов панели из фотографий media/IMG_*.jpg (3000×4000).
1) грубо: чёрная рамка корпуса -> её «дырка» = экран (несколько порогов яркости);
2) точно: в расширенной области ищутся 4 границы экран/рамка по перепаду яркости,
   линии подгоняются робастно, углы = пересечения; 3) перспективное выравнивание в 600×1024.
Запуск из папки scratch-пайплайна (нужны extract_screen.py); результат в photo_out/.
"""
import cv2, numpy as np, glob, os
from extract_screen import warp, order_pts
from grab import norm
from PIL import Image, ImageOps
def load(f):
    im=ImageOps.exif_transpose(Image.open(f)).convert('RGB'); return cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR)
def quad_from_mask(m):
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE); c=max(cnts,key=cv2.contourArea)
    peri=cv2.arcLength(c,True)
    for eps in (0.01,0.02,0.03,0.05):
        a=cv2.approxPolyDP(c,eps*peri,True)
        if len(a)==4: return a.reshape(4,2).astype(np.float32)
    return cv2.boxPoints(cv2.minAreaRect(c)).astype(np.float32)
def ok(q,img):
    if q is None: return False
    q=order_pts(q); w=np.linalg.norm(q[1]-q[0]); h=np.linalg.norm(q[3]-q[0])
    return 0.535<=w/h<=0.57 and h>0.3*img.shape[0]
def hole_quad(g,T):
    bez=(g<T).astype(np.uint8)*255
    bez=cv2.morphologyEx(bez,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
    n,lab,st,_=cv2.connectedComponentsWithStats(bez)
    if n<2: return None
    big=max(range(1,n),key=lambda i:st[i][4]); comp=(lab==big).astype(np.uint8)*255
    ff=comp.copy(); h,w=comp.shape; cv2.floodFill(ff,np.zeros((h+2,w+2),np.uint8),(0,0),255)
    holes=cv2.bitwise_and(cv2.bitwise_not(ff),cv2.bitwise_not(comp))
    n2,lab2,st2,_=cv2.connectedComponentsWithStats(holes)
    if n2<2: return None
    hole=max(range(1,n2),key=lambda i:st2[i][4])
    return quad_from_mask((lab2==hole).astype(np.uint8)*255)
def find(img):
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    small=cv2.resize(g,None,fx=0.25,fy=0.25,interpolation=cv2.INTER_AREA)
    for T in (45,40,35,30,25,20,50,55,60):
        q=hole_quad(small,T)
        if ok(q,small): return q*4,T
    return None,None
def warp_to(img,q,W,H):
    q=order_pts(q); dst=np.array([[0,0],[W-1,0],[W-1,H-1],[0,H-1]],np.float32)
    M=cv2.getPerspectiveTransform(q,dst); return cv2.warpPerspective(img,M,(W,H),flags=cv2.INTER_AREA), M
def expand(q,f=0.08):
    q=order_pts(q); c=q.mean(0); return c+(q-c)*(1+f)
def edge_points(g,T,axis,side,run=25,start_frac=0.16):
    """Scan outwards starting a little inside the expected edge (the warp has an 8% margin)."""
    pts=[]
    n=g.shape[axis]
    for i in range(int(n*0.1),int(n*0.9),3):
        line=g[i,:] if axis==0 else g[:,i]
        L=len(line); c=int(L*start_frac)
        seg=line[L-1-c:] if side==1 else line[:c+1][::-1]
        dark=(seg<T).astype(np.int8)
        cs=np.convolve(dark,np.ones(run,dtype=np.int8),'valid')
        hit=np.where(cs==run)[0]
        if len(hit)==0: continue
        j=int(hit[0])
        pos=(L-1-c)+j if side==1 else c-j
        pts.append((pos,i) if axis==0 else (i,pos))
    return np.array(pts,np.float32)
def fit(pts):
    vx,vy,x0,y0=cv2.fitLine(pts,cv2.DIST_HUBER,0,0.01,0.01).ravel(); return (x0,y0,vx,vy)
def inter(l1,l2):
    x1,y1,a1,b1=l1; x2,y2,a2,b2=l2
    A=np.array([[a1,-a2],[b1,-b2]],float); t=np.linalg.solve(A,[x2-x1,y2-y1]); return (x1+a1*t[0], y1+b1*t[0])
def refine(img,q):
    W,H=720,1230
    big,M=warp_to(img,expand(q),W,H)
    g=cv2.cvtColor(big,cv2.COLOR_BGR2GRAY); g=cv2.GaussianBlur(g,(7,7),0)
    inner=np.median(g[int(H*0.2):int(H*0.8),int(W*0.2):int(W*0.8)])
    border=np.median(np.concatenate([g[:15].ravel(),g[-15:].ravel(),g[:,:15].ravel(),g[:,-15:].ravel()]))
    T=border+0.3*(inner-border)
    L=fit(edge_points(g,T,0,0)); R=fit(edge_points(g,T,0,1)); Tp=fit(edge_points(g,T,1,0)); B=fit(edge_points(g,T,1,1))
    corners=np.array([inter(L,Tp),inter(R,Tp),inter(R,B),inter(L,B)],np.float32)
    Minv=np.linalg.inv(M)
    src=cv2.perspectiveTransform(corners.reshape(-1,1,2),Minv).reshape(4,2)
    return src,(inner,border)
if __name__=="__main__":
    for f in sorted(glob.glob("/Users/rust/work/dante-super-sport/doc/media/IMG_*.jpg")):
        name=os.path.basename(f)[:-4]; img=load(f); q,T=find(img)
        if q is None: print("FAIL",name); continue
        q2,_=refine(img,q); out,_=warp_to(img,q2,600,1024)
        cv2.imwrite(f"photo_out/{name}.jpg",out,[cv2.IMWRITE_JPEG_QUALITY,90]); print("ok",name)
