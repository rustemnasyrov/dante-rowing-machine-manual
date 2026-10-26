"""Выравнивание экрана «Выйти из тренировки» (кадр 464 с видео), у которого левый край
экрана обрезан границей кадра. Гомография подбирается по элементам интерфейса:
правый конец строки состояния, кнопки СТАТИСТИКА и ЛИДЕР, горизонтальность/вертикальность
рамки всплывающего окна. Нужны full/f_464.jpg, feat.py и grab.py из рабочей папки пайплайна.
"""
import cv2, numpy as np, json
from scipy.optimize import least_squares
from feat import cyan
from grab import norm
f=cv2.imread('full/f_464.jpg'); cy=cyan(f)>0
def ymean(x,y0,y1,w=3):
    ys=[y for y in range(y0,y1) if cy[y,x-w:x+w+1].any()]; return float(np.mean(ys))
def xmean(y,x0,x1,w=3):
    xs=[x for x in range(x0,x1) if cy[y-w:y+w+1,x].any()]; return float(np.mean(xs))
st_l=(60,ymean(60,310,335)); st_r=(740,ymean(740,308,330))
top=[(100,ymean(100,452,475)),(650,ymean(650,452,475))]
bot=[(100,ymean(100,1044,1066)),(650,ymean(650,1044,1066))]
left=[(xmean(600,25,60),600),(xmean(950,25,60),950)]
right=[(xmean(600,690,725),600),(xmean(950,690,725),950)]
print('status',st_l,st_r,'top',top,'bot',bot,'left',left,'right',right)
P_src=[(760,st_r[1]-0.3),(768,1557.5),(542,1559.5)]; P_dst=[(599,60),(588,985),(420,982.4)]
def apply(h,p):
    H=np.append(h,1).reshape(3,3); v=H@np.array([p[0],p[1],1.0]); return v[0]/v[2],v[1]/v[2]
def resid(h):
    r=[]
    for s,d in zip(P_src,P_dst):
        x,y=apply(h,s); r+=[x-d[0],y-d[1]]
    r.append(apply(h,st_l)[1]-60)
    for pair in (top,bot):
        r.append(apply(h,pair[0])[1]-apply(h,pair[1])[1])
    for pair in (left,right):
        r.append(apply(h,pair[0])[0]-apply(h,pair[1])[0])
    return r
H0,_=cv2.findHomography(np.float32(P_src+[st_l]),np.float32(P_dst+[(2,60)]))
h0=(H0/H0[2,2]).ravel()[:8]
sol=least_squares(resid,h0,xtol=1e-12,ftol=1e-12)
print('residuals',np.round(sol.fun,2))
H=np.append(sol.x,1).reshape(3,3)
print('popup rect in ref:',apply(sol.x,left[0]),apply(sol.x,top[0]),apply(sol.x,right[0]),apply(sol.x,bot[0]))
out=cv2.warpPerspective(f,H,(600,1024),flags=cv2.INTER_AREA,borderValue=(12,14,16))
out=norm(out)
cv2.imwrite('cand/exit_fixed.jpg',out,[cv2.IMWRITE_JPEG_QUALITY,88])
old=cv2.imread('/Users/rust/work/dante-super-sport/doc/images/screens/exit_dialog.jpg')
# overlay hotspots on new
d=json.load(open('/Users/rust/work/dante-super-sport/doc/tools/hotspots.json'))
s=[s for s in d['screens'] if s['id']=='exit_dialog'][0]
ov=out.copy()
for hs in s['hotspots']:
    x,y,w,h=hs['rect']; cv2.rectangle(ov,(x,y),(x+w,y+h),(0,0,255),2); cv2.putText(ov,hs['id'],(x,y-4),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1)
cv2.imwrite('exit_cmp.png',np.hstack([old,ov]))
