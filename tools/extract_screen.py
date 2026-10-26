import cv2, numpy as np, sys, os

def find_screen_quad(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = g.shape
    # screen-ish gray range; bezel is darker, floor is brighter
    mask = cv2.inRange(g, 40, 150)
    # also include cyan UI pixels (bright) inside screen
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cyan = cv2.inRange(hsv, (80, 60, 60), (110, 255, 255))
    mask = cv2.bitwise_or(mask, cyan)
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask)
    # choose the largest component whose bbox is reasonably central and tall
    best = None
    for i in range(1, n):
        x, y, bw, bh, area = stats[i]
        if area < 0.05 * h * w: continue
        if best is None or area > stats[best][4]:
            best = i
    if best is None: return None, mask
    comp = (lab == best).astype(np.uint8) * 255
    cnts, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cnts, key=cv2.contourArea)
    peri = cv2.arcLength(c, True)
    for eps in (0.01, 0.02, 0.03, 0.05):
        approx = cv2.approxPolyDP(c, eps * peri, True)
        if len(approx) == 4:
            return approx.reshape(4, 2).astype(np.float32), mask
    rect = cv2.minAreaRect(c)
    return cv2.boxPoints(rect).astype(np.float32), mask

def order_pts(pts):
    s = pts.sum(1); d = np.diff(pts, axis=1).ravel()
    tl = pts[np.argmin(s)]; br = pts[np.argmax(s)]
    tr = pts[np.argmin(d)]; bl = pts[np.argmax(d)]
    return np.array([tl, tr, br, bl], np.float32)

def warp(img, quad, W=600, H=1024):
    q = order_pts(quad)
    dst = np.array([[0,0],[W-1,0],[W-1,H-1],[0,H-1]], np.float32)
    M = cv2.getPerspectiveTransform(q, dst)
    return cv2.warpPerspective(img, M, (W, H), flags=cv2.INTER_AREA)

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    img = cv2.imread(src)
    quad, mask = find_screen_quad(img)
    if quad is None:
        print("no quad", src); sys.exit(1)
    q = order_pts(quad)
    wtop = np.linalg.norm(q[1]-q[0]); hleft = np.linalg.norm(q[3]-q[0])
    print(os.path.basename(src), "quad:", q.astype(int).tolist(), "aspect w/h=%.3f" % (wtop/hleft))
    dbg = img.copy()
    cv2.polylines(dbg, [q.astype(int)], True, (0,0,255), 6)
    cv2.imwrite("dbg/" + os.path.basename(out), cv2.resize(dbg, None, fx=0.3, fy=0.3))
    cv2.imwrite(out, warp(img, quad), [cv2.IMWRITE_JPEG_QUALITY, 90])
