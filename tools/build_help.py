import json, base64, os, io
from PIL import Image
os.chdir(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open("hotspots.json")); tours = json.load(open("tours.json"))
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images", "screens")
imgs = {}
for s in d["screens"]:
    # в справке экран показывается не шире 440 px: уменьшаем до 480×819 и сжимаем, чтобы файл быстрее грузился
    im = Image.open(f"{SRC}/{s['img']}").convert("RGB").resize((480, 819), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=70, optimize=True, progressive=True)
    imgs[s["img"]] = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
t = open("help_template.html").read()
t = t.replace("__DATA__", json.dumps(d, ensure_ascii=False)).replace("__IMAGES__", json.dumps(imgs)).replace("__TOURS__", json.dumps(tours, ensure_ascii=False))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist", "Интерактивная_справка.html")
out = os.path.normpath(out); open(out, "w").write(t)
print(out, round(os.path.getsize(out)/1e6, 2), "MB")
