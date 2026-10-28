#!/usr/bin/env python3
"""Сборка папки dist/ с четырьмя готовыми документами:
  Быстрый_старт.html (автономный, картинки внутри), Быстрый_старт.pdf,
  Интерактивная_справка.html, Руководство_пользователя_DC2.pdf.
Запуск: python3 tools/build_dist.py   (нужны pandoc, Google Chrome, pymupdf)
"""
import base64, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
DIST.mkdir(exist_ok=True)

# 1. Быстрый старт: встраиваем картинки, печатаем PDF
src = (ROOT / "Быстрый_старт.html").read_text()
def inline(m):
    data = (ROOT / m.group(1)).read_bytes()
    return 'src="data:image/jpeg;base64,' + base64.b64encode(data).decode() + '"'
html = re.sub(r'src="(images/[^"]+\.jpe?g)"', inline, src)
qs_html = DIST / "Быстрый_старт.html"
qs_html.write_text(html)
with tempfile.TemporaryDirectory() as td:
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={td}/chrome",
                    f"--print-to-pdf={DIST / 'Быстрый_старт.pdf'}", f"file://{qs_html}"], check=True, capture_output=True)
print(qs_html, round(qs_html.stat().st_size / 1e6, 2), "MB")

# 2. Интерактивная справка и 3. PDF руководства
subprocess.run([sys.executable, str(ROOT / "tools" / "build_help.py")], check=True)
subprocess.run([sys.executable, str(ROOT / "tools" / "build_manual_pdf.py")], check=True)
for f in sorted(DIST.iterdir()):
    print(f"{f.stat().st_size/1e6:6.2f} MB  {f.name}")
