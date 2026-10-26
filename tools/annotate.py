import json, cv2, numpy as np, os, glob
from PIL import Image, ImageDraw, ImageFont
d = json.load(open("hotspots.json"))
SRC = "/Users/rust/work/dante-super-sport/doc/images/screens"
font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
def draw_numbered(screen, out, scale=1.0):
    im = Image.open(f"{SRC}/{screen['img']}").convert("RGB")
    dr = ImageDraw.Draw(im, "RGBA")
    f = ImageFont.truetype(font_path, 26)
    for h in screen["hotspots"]:
        x, y, w, hh = h["rect"]
        dr.rectangle([x, y, x+w, y+hh], outline=(255, 170, 0, 230), width=3)
        if "num" in h:
            cx, cy = x + 18, y + 18
            dr.ellipse([cx-18, cy-18, cx+18, cy+18], fill=(255, 140, 0, 255), outline=(0,0,0,255), width=2)
            t = str(h["num"]); tw = dr.textlength(t, font=f)
            dr.text((cx - tw/2, cy - 16), t, font=f, fill=(0,0,0,255))
    im.save(out, quality=90)
def draw_debug(screen, out):
    im = Image.open(f"{SRC}/{screen['img']}").convert("RGB")
    dr = ImageDraw.Draw(im, "RGBA")
    f = ImageFont.truetype(font_path, 16)
    for h in screen["hotspots"]:
        x, y, w, hh = h["rect"]
        dr.rectangle([x, y, x+w, y+hh], outline=(255, 60, 60, 255), width=2, fill=(255,60,60,40))
        dr.text((x+3, y+2), h["id"], font=f, fill=(255,255,0,255))
    im.save(out, quality=85)
for s in d["screens"]:
    draw_debug(s, f"dbg_hotspots/{s['id']}.jpg")
aw = next(s for s in d["screens"] if s["id"] == "active_workout")
draw_numbered(aw, "/Users/rust/work/dante-super-sport/doc/images/annotated/active_workout.jpg")
# contact sheets of debug overlays
files = [f"dbg_hotspots/{s['id']}.jpg" for s in d["screens"]]
th = [cv2.resize(cv2.imread(f), (400, 683)) for f in files]
cols = 6
for i in range(0, len(th), cols*2):
    chunk = th[i:i+cols*2]
    while len(chunk) % cols: chunk.append(np.zeros_like(th[0]))
    rows = [np.hstack(chunk[j:j+cols]) for j in range(0, len(chunk), cols)]
    cv2.imwrite(f"dbg_sheet_{i//(cols*2)}.jpg", np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
print("ok")
