import cv2, numpy as np, subprocess, os, sys
from extract_screen import find_screen_quad, warp, order_pts
FF="venv/bin/ffmpeg"; VID="/Users/rust/work/dante-super-sport/doc/media/VID_20261021_175126.mp4"
def frame(t):
    p=f"full/f_{t}.jpg"
    if not os.path.exists(p):
        subprocess.run([FF,"-loglevel","error","-y","-ss",str(t),"-i",VID,"-frames:v","1","-q:v","2",p],check=True)
    return cv2.imread(p)
def good_quad(img):
    q,_=find_screen_quad(img)
    if q is None: return None
    q=order_pts(q)
    w=(np.linalg.norm(q[1]-q[0])+np.linalg.norm(q[2]-q[3]))/2; h=(np.linalg.norm(q[3]-q[0])+np.linalg.norm(q[2]-q[1]))/2
    return q if 0.53<=w/h<=0.60 and h>1100 else None
def status_line(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV); cy=cv2.inRange(hsv,(80,60,60),(110,255,255))
    cy=cv2.morphologyEx(cy,cv2.MORPH_CLOSE,np.ones((1,31),np.uint8))
    for y in range(20,300):
        row=cy[y]>0; runs=np.diff(np.concatenate(([0],row.astype(np.int8),[0])))
        st=np.where(runs==1)[0]; en=np.where(runs==-1)[0]
        if len(st)==0: continue
        L=en-st; i=int(np.argmax(L))
        if L[i]>=470: return (y,int(st[i]),int(en[i])-1)
    return None
def norm(img):
    sl=status_line(img)
    if sl is None: return img
    y,xl,xr=sl; s=596.0/(xr-xl); x0=xl-2/s; y0=y-60/s
    M=np.array([[s,0,-x0*s],[0,s,-y0*s]],np.float32)
    return cv2.warpAffine(img,M,(600,1024),flags=cv2.INTER_AREA,borderValue=(12,14,16))
for t in [int(x) for x in sys.argv[1:]]:
    img=frame(t); q=None
    for dt in (0,-2,2,-4,4,-7,7):
        q=good_quad(frame(t+dt))
        if q is not None: break
    if q is None: print("FAIL",t); continue
    cv2.imwrite(f"cand/c_{t}.jpg",norm(warp(img,q)),[cv2.IMWRITE_JPEG_QUALITY,88]); print("ok",t)
