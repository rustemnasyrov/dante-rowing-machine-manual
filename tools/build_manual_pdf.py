#!/usr/bin/env python3
"""Сборка PDF руководства: Markdown → HTML (pandoc) → PDF (headless Chrome) → нумерация страниц,
оглавление с номерами страниц и закладки (PyMuPDF).

Запуск из любой папки:  python3 tools/build_manual_pdf.py
Нужны: pandoc, Google Chrome, пакет pymupdf.
"""
import os, re, sys, subprocess, tempfile, urllib.parse
from pathlib import Path
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "Руководство_пользователя_DC2.md"
OUT = ROOT / "dist" / "Руководство_пользователя_DC2.pdf"
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
FOOTER_FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
FOOTER_TEXT = "Панель управления DC2 · Руководство пользователя"

CSS = """
@page { size: A4; margin: 17mm 15mm 20mm 15mm; }
html { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 10.5pt; line-height: 1.42; color: #14202c; }
body { margin: 0; }
h2.sec { page-break-before: always; break-before: page; font-size: 20pt; line-height: 1.2; margin: 0 0 12pt; padding-bottom: 6pt;
         border-bottom: 2px solid #1b6ac9; color: #0d2a4a; }
h3 { font-size: 13.5pt; margin: 18pt 0 6pt; color: #0d2a4a; }
h2, h3 { page-break-after: avoid; break-after: avoid; }
p { margin: 0 0 8pt; }
p, li { orphans: 2; widows: 2; }
ul, ol { margin: 0 0 8pt; padding-left: 20pt; }
li { margin-bottom: 2pt; }
table { border-collapse: collapse; width: 100%; font-size: 9.5pt; line-height: 1.35; margin: 6pt 0 12pt; }
tr { page-break-inside: avoid; break-inside: avoid; }
th { background: #e8f0fa; text-align: left; font-weight: 600; }
th, td { border: 1px solid #c5cfdb; padding: 4pt 6pt; vertical-align: top; }
figure { margin: 10pt 0 12pt; text-align: center; page-break-inside: avoid; break-inside: avoid; }
figcaption { font-size: 9pt; color: #5a6b7c; margin-top: 4pt; }
img { max-width: 100%; display: block; margin: 0 auto; }
img[src*="screens/"] { width: 58mm; border: 1px solid #d5dde6; }
img[src*="annotated/"] { width: 96mm; }
img[src*="ui/"] { width: 100%; max-width: 150mm; }
hr { display: none; }
pre { font: 7.8pt/1.32 Menlo, "DejaVu Sans Mono", monospace; background: #f4f6f9; padding: 7pt 9pt; border-radius: 3pt;
      white-space: pre; margin: 6pt 0 12pt; page-break-inside: avoid; }
code { font-family: Menlo, monospace; font-size: 90%; }
strong { font-weight: 600; }
a { color: #1b6ac9; text-decoration: none; }
.cover { height: 250mm; display: flex; flex-direction: column; align-items: center; text-align: center; page-break-after: always; break-after: page; }
.cover .brand { font-size: 13pt; letter-spacing: 2pt; text-transform: uppercase; color: #1b6ac9; margin-top: 18mm; }
.cover h1 { font-size: 27pt; line-height: 1.2; margin: 8mm 0 3mm; color: #0d2a4a; font-weight: 700; }
.cover .sub { font-size: 16pt; color: #3a4a5c; margin-bottom: 12mm; }
.cover img { width: 68mm; border: 1px solid #d5dde6; box-shadow: 0 6px 18px rgba(0,0,0,.18); }
.cover .ver { margin-top: auto; font-size: 10pt; color: #5a6b7c; line-height: 1.6; }
.toc a { display: flex; align-items: baseline; color: #14202c; }
.toc .d { flex: 1; border-bottom: 1px dotted #9aa7b4; margin: 0 4pt 3pt; }
.toc .l2 { font-weight: 600; margin-top: 7pt; }
.toc .l3 { padding-left: 16pt; font-size: 9.8pt; }
"""


def preprocess(md: str):
    """Возвращает (markdown, headings) где headings = [(level, text, id)]."""
    lines = md.split("\n")
    # заголовок документа и версии
    m_doc = re.search(r"Версия документа:\s*(.+)", md)
    m_fw = re.search(r"Версия прошивки[^:]*:\s*(.+)", md)
    toc_i = next(i for i, l in enumerate(lines) if l.strip() == "## Содержание")
    body = lines[toc_i:]
    # конец блока содержания — первая горизонтальная черта после него
    toc_end = next(i for i, l in enumerate(body) if i > 0 and l.strip() == "---")
    body = body[toc_end + 1:]

    headings, out, ids = [], [], {}
    n = 0
    for l in body:
        m = re.match(r"^(##|###) (.+?)\s*$", l)
        if m:
            n += 1
            hid = f"s{n}"
            text = m.group(2)
            ids[text] = hid
            headings.append((len(m.group(1)) - 1, text, hid))
            cls = " .sec" if m.group(1) == "##" else ""
            l = f"{m.group(1)} {text} {{#{hid}{cls}}}"
        out.append(l)

    def fix_link(m):
        target = urllib.parse.unquote(m.group(2))
        return f"[{m.group(1)}](#{ids.get(target, target)})"
    text = "\n".join(out)
    text = re.sub(r"\[([^\]]+)\]\(#([^)]+)\)", fix_link, text)

    cover = f"""<div class="cover">
<div class="brand">Гребной тренажёр Dante</div>
<h1>Панель управления<br>(дисплейный модуль DC2)</h1>
<div class="sub">Руководство пользователя</div>
<img src="images/screens/main.jpg" alt="">
<div class="ver">Версия документа {m_doc.group(1).strip() if m_doc else ''}<br>Версия прошивки {m_fw.group(1).strip() if m_fw else ''}</div>
</div>
"""
    return cover, text, headings


def toc_html(headings, pages):
    items = ['<h2 class="sec" id="toc">Содержание</h2>', '<nav class="toc">']
    for lvl, text, hid in headings:
        p = pages.get(hid, "")
        items.append(f'<a class="l{lvl+1}" href="#{hid}"><span class="t">{text}</span><span class="d"></span><span class="p">{p}</span></a>')
    items.append("</nav>")
    return "\n".join(items) + "\n"


def render(cover, toc, body, workdir: Path) -> Path:
    md_path = workdir / "manual.md"
    html_path = workdir / "manual.html"
    pdf_path = workdir / "manual.pdf"
    (workdir / "style.css").write_text(CSS)
    md_path.write_text(cover + "\n" + toc + "\n" + body)
    subprocess.run(["pandoc", str(md_path), "-f", "markdown", "-t", "html5", "--standalone", "--wrap=none",
                    "--metadata", "title=Руководство пользователя DC2", "--css", "style.css", "-o", str(html_path)], check=True)
    # pandoc выводит <header><h1 class="title">: убираем, обложка своя
    h = html_path.read_text()
    h = re.sub(r"<header id=\"title-block-header\">.*?</header>", "", h, flags=re.S)
    html_path.write_text(h)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--user-data-dir={workdir / 'chrome'}", f"--print-to-pdf={pdf_path}",
                    f"file://{html_path}"], check=True, capture_output=True)
    return pdf_path


def heading_pages(pdf: Path, headings):
    """Страница каждого заголовка: по внутренним ссылкам из оглавления, иначе по поиску текста."""
    doc = fitz.open(pdf)
    pages = {}
    for pno in range(min(4, len(doc))):
        for lk in doc[pno].get_links():
            if lk.get("nameddest") and "page" in lk:
                pages[lk["nameddest"]] = lk["page"] + 1
    for lvl, text, hid in headings:
        if hid in pages:
            continue
        for pno in range(3, len(doc)):
            if doc[pno].search_for(text):
                pages[hid] = pno + 1
                break
    doc.close()
    return pages


def finish(pdf: Path, headings, pages, out: Path):
    doc = fitz.open(pdf)
    for pno in range(1, len(doc)):  # без обложки
        page = doc[pno]
        w, h = page.rect.width, page.rect.height
        y = h - 11 * 72 / 25.4
        page.insert_text((15 * 72 / 25.4, y), FOOTER_TEXT, fontsize=8, fontname="footer", fontfile=FOOTER_FONT, color=(0.42, 0.47, 0.53))
        num = str(pno + 1)
        tw = len(num) * 5
        page.insert_text((w - 15 * 72 / 25.4 - tw, y), num, fontsize=9, fontname="footer", fontfile=FOOTER_FONT, color=(0.42, 0.47, 0.53))
    toc = [[1, "Содержание", 2]] + [[lvl, text, pages[hid]] for lvl, text, hid in headings if hid in pages]
    doc.set_toc(toc)
    doc.subset_fonts()
    doc.set_metadata({"title": "Панель управления DC2 — руководство пользователя", "author": "Dante", "subject": "Гребной тренажёр Dante"})
    out.parent.mkdir(exist_ok=True)
    doc.save(out, garbage=3, deflate=True)
    doc.close()


def main():
    cover, body, headings = preprocess(MD.read_text())
    with tempfile.TemporaryDirectory() as td:
        wd = Path(td)
        os.symlink(ROOT / "images", wd / "images")
        pages = {}
        for attempt in range(3):
            pdf = render(cover, toc_html(headings, pages), body, wd)
            new = heading_pages(pdf, headings)
            if new == pages:
                break
            pages = new
        missing = [t for _, t, h in headings if h not in pages]
        if missing:
            print("не найдены страницы:", missing, file=sys.stderr)
        finish(pdf, headings, pages, OUT)
    print(OUT, round(OUT.stat().st_size / 1e6, 2), "MB,", len(fitz.open(OUT)), "стр.")


if __name__ == "__main__":
    main()
