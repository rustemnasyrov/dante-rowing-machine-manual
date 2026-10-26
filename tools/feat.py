import cv2, numpy as np, sys
def cyan(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV); return cv2.inRange(hsv,(80,60,60),(110,255,255))
def status_line_right(img, ymin, ymax, minlen):
    cy=cv2.morphologyEx(cyan(img),cv2.MORPH_CLOSE,np.ones((1,31),np.uint8))
    best=None
    for y in range(ymin,ymax):
        row=cy[y]>0; runs=np.diff(np.concatenate(([0],row.astype(np.int8),[0])))
        st=np.where(runs==1)[0]; en=np.where(runs==-1)[0]
        if len(st)==0: continue
        L=en-st; i=int(np.argmax(L))
        if L[i]>=minlen:
            if best is None or L[i]>best[2]: best=(y,int(en[i])-1,L[i],int(st[i]))
    return best  # y, xright, len, xleft
def buttons(img, ymin, ymax):
    m=cyan(img)[ymin:ymax]; m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(m)
    comps=[st[i] for i in range(1,n) if st[i][4]>300]
    comps.sort(key=lambda s:s[0])
    L=comps[0]; R=comps[-1]
    return (int(L[0]), ymin+int(L[1]+L[3]/2)), (int(R[0]+R[2]-1), ymin+int(R[1]+R[3]/2))
def clock_left(img, ymin, ymax):
    m=cyan(img)[ymin:ymax]; m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(m)
    comps=[st[i] for i in range(1,n) if st[i][4]>80]
    comps.sort(key=lambda s:s[0]); c=comps[0]
    return (int(c[0]), ymin+int(c[1]+c[3]/2))
if __name__=="__main__":
    ref=cv2.imread('/Users/rust/work/dante-super-sport/doc/images/screens/active_workout.jpg')
    print('ref status',status_line_right(ref,40,80,400))
    print('ref buttons',buttons(ref,945,1015))
    print('ref clock',clock_left(ref,15,55))
    f=cv2.imread('full/f_464.jpg')
    print('f status',status_line_right(f,250,380,500))
    print('f buttons',buttons(f,1500,1640))
    print('f clock',clock_left(f,240,310))
