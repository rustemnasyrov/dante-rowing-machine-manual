"""Вырезает элементы интерфейса из images/screens/*.jpg (600×1024) и собирает
наборные иллюстрации для раздела 4 руководства в images/ui/.
Запуск из папки doc:  python3 tools/crop_ui.py
"""
from PIL import Image, ImageDraw, ImageFont
import os
S = "images/screens/"; O = "images/ui/"; os.makedirs(O, exist_ok=True)
BG = (12, 14, 16); FG = (205, 212, 220); PAD = 8
FONT = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 22)

def crop(img, rect, pad=PAD):
    x, y, w, h = rect
    im = Image.open(S + img)
    return im.crop((max(0, x - pad), max(0, y - pad), min(600, x + w + pad), min(1024, y + h + pad)))

def sheet(name, items, scale=1.0, gap=36, maxw=None):
    """items: [(caption, PIL image)] -> одна горизонтальная картинка с подписями."""
    ims = []
    for cap, im in items:
        if scale != 1.0:
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        ims.append((cap, im))
    H = max(im.height for _, im in ims)
    widths = [max(im.width, FONT.getlength(cap) + 10) for cap, im in ims]
    W = int(sum(widths) + gap * (len(ims) + 1))
    out = Image.new("RGB", (W, H + 70), BG); d = ImageDraw.Draw(out)
    x = gap
    for (cap, im), w in zip(ims, widths):
        cx = x + (w - im.width) / 2
        out.paste(im, (int(cx), int(20 + (H - im.height) / 2)))
        tw = FONT.getlength(cap)
        d.text((x + (w - tw) / 2, H + 32), cap, fill=FG, font=FONT)
        x += w + gap
    out.save(O + name + ".jpg", quality=92)
    print(name, out.size)

# 4.1 Навигация
sheet("nav_buttons", [
    ("МЕНЮ — в главное меню", crop("options.jpg", [8, 958, 150, 56])),
    ("НАЗАД — к списку", crop("workout_info.jpg", [8, 958, 150, 56])),
    ("Крестик — закрыть окно", crop("time_popup.jpg", [515, 200, 50, 50])),
    ("Старт тренировки", crop("fast_start.jpg", [180, 958, 192, 56])),
])
# 4.2 Кнопки действий
sheet("action_buttons", [
    ("ИЗМЕНИТЬ", crop("options.jpg", [372, 338, 220, 56])),
    ("ПОДРОБНЕЕ", crop("history.jpg", [365, 205, 215, 52])),
    ("СОХРАНИТЬ", crop("splits_popup.jpg", [255, 815, 290, 60])),
    ("ЗАБЫТЬ", crop("wifi_list.jpg", [160, 835, 255, 52])),
])
# 4.3 Поразрядные стрелки
sheet("digits", [
    ("Дистанция: по стрелке на каждый разряд", crop("splits_popup.jpg", [140, 350, 340, 130])),
    ("Минуты : секунды", crop("program_create.jpg", [70, 655, 260, 125])),
])
# 4.4 Переключатель категории
sheet("category_switch", [
    ("Цель интервала: ВРЕМЯ / ДИСТАНЦИЯ / ГРЕБКИ", crop("program_create.jpg", [90, 540, 240, 80])),
    ("Такой же значок: МУЖЧИНА / ЖЕНЩИНА", crop("athlete.jpg", [160, 145, 230, 60])),
])
# 4.5 Включаемые параметры
sheet("toggles", [
    ("ЛИДЕР включён — виден темп", crop("splits_popup.jpg", [150, 645, 275, 130])),
    ("ЛИДЕР выключен — оранжевый крестик", crop("program_create_leader_off.jpg", [325, 735, 260, 125])),
    ("ТЕМП выключен", crop("program_create_tempo_off.jpg", [70, 830, 240, 120])),
])
# 4.6 Стрелки ◀ ▶
sheet("steppers", [
    ("Номер интервала в программе", crop("program_create.jpg", [155, 435, 200, 70])),
    ("Возраст, рост, вес спортсмена", crop("athlete.jpg", [210, 600, 200, 80])),
])
# 4.7 Ползунки
sheet("slider", [
    ("Перетащите бегунок или коснитесь шкалы в нужном месте", crop("options.jpg", [20, 140, 560, 45])),
])
# 4.8 Списки и страницы
sheet("lists", [
    ("Строка списка с кнопкой ПОДРОБНЕЕ", crop("history.jpg", [25, 165, 555, 100])),
    ("Страница 1 из 13, листание", crop("history.jpg", [320, 950, 170, 56])),
    ("Слоты программ, прокрутка ▲ ▼", crop("program_create.jpg", [5, 145, 65, 215])),
])
