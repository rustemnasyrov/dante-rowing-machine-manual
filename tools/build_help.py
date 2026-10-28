import json, base64, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open("hotspots.json")); tours = json.load(open("tours.json"))
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images", "screens")
imgs = {}
for s in d["screens"]:
    b = open(f"{SRC}/{s['img']}", "rb").read()
    imgs[s["img"]] = "data:image/jpeg;base64," + base64.b64encode(b).decode()
t = open("help_template.html").read()
t = t.replace("__DATA__", json.dumps(d, ensure_ascii=False)).replace("__IMAGES__", json.dumps(imgs)).replace("__TOURS__", json.dumps(tours, ensure_ascii=False))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist", "Интерактивная_справка.html")
out = os.path.normpath(out); open(out, "w").write(t)
print(out, round(os.path.getsize(out)/1e6, 2), "MB")
