import json, base64, os
d = json.load(open("hotspots.json")); tours = json.load(open("tours.json"))
SRC = "/Users/rust/work/dante-super-sport/doc/images/screens"
for s in d["screens"]:
    if s["id"] == "hrm": s["video"] = "media/VID_20261021_180009.mp4"; s["t"] = 0
imgs = {}
for s in d["screens"]:
    b = open(f"{SRC}/{s['img']}", "rb").read()
    imgs[s["img"]] = "data:image/jpeg;base64," + base64.b64encode(b).decode()
t = open("help_template.html").read()
t = t.replace("__DATA__", json.dumps(d, ensure_ascii=False)).replace("__IMAGES__", json.dumps(imgs)).replace("__TOURS__", json.dumps(tours, ensure_ascii=False))
out = "/Users/rust/work/dante-super-sport/doc/Интерактивная_справка.html"
open(out, "w").write(t)
print(out, round(os.path.getsize(out)/1e6, 2), "MB")
