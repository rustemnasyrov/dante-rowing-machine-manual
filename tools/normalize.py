import cv2, numpy as np, glob, os, json
SRC = "final_screens"; OUT = "/Users/rust/work/dante-super-sport/doc/images/screens"
def status_line(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cy = cv2.inRange(hsv, (80, 60, 60), (110, 255, 255))
    cy = cv2.morphologyEx(cy, cv2.MORPH_CLOSE, np.ones((1, 31), np.uint8))
    best = None
    for y in range(20, 300):
        row = cy[y] > 0
        # longest contiguous run
        runs = np.diff(np.concatenate(([0], row.astype(np.int8), [0])))
        starts = np.where(runs == 1)[0]; ends = np.where(runs == -1)[0]
        if len(starts) == 0: continue
        lens = ends - starts; i = int(np.argmax(lens))
        if lens[i] >= 470:
            # refine: pick the longest run within next 8 rows
            best = (y, int(starts[i]), int(ends[i]) - 1)
            break
    return best
report = {}
for f in sorted(glob.glob(f"{SRC}/*.jpg")):
    img = cv2.imread(f); name = os.path.basename(f)
    sl = status_line(img)
    if sl is None:
        print("no line", name); cv2.imwrite(f"{OUT}/{name}", img); continue
    y, xl, xr = sl
    s = 596.0 / (xr - xl)
    x0 = xl - 2 / s; y0 = y - 60 / s
    w = 600 / s; h = 1024 / s
    # affine: map (x0,y0)->(0,0), scale s
    M = np.array([[s, 0, -x0 * s], [0, s, -y0 * s]], np.float32)
    out = cv2.warpAffine(img, M, (600, 1024), flags=cv2.INTER_AREA, borderValue=(12, 14, 16))
    cv2.imwrite(f"{OUT}/{name}", out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    report[name] = (y, xl, xr, round(s, 3))
print(json.dumps(report))
