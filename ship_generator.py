from __future__ import annotations

import io
import math
import os
import random
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS_DIR = Path(os.environ.get("FONTS_DIR", "C:/Windows/Fonts"))

W = 800
H = 400


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONTS_DIR / name, FONTS_DIR / "segoeui.ttf", FONTS_DIR / "arial.ttf",
              Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def _font_bold(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONTS_DIR / name, FONTS_DIR / "segoeuib.ttf", FONTS_DIR / "arialbd.ttf",
              Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")]:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return _font(name, size)


def _hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(min(len(a), len(b))))


def _bright(c, f=1.4):
    return tuple(min(255, int(v * f)) for v in c[:3])


def _dim(c, f=0.3):
    return tuple(max(0, int(v * f)) for v in c[:3])


def _draw_circle_mask(size: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 1, size - 1), fill=255)
    return mask


def _download_avatar(url: str, size: int = 256) -> Image.Image:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("RGBA")
        img = img.resize((size, size), Image.LANCZOS)
        return img
    except Exception:
        img = Image.new("RGBA", (size, size), (139, 92, 246, 255))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, size - 1, size - 1), fill=(139, 92, 246, 255))
        return img


def _draw_heart(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int, color: tuple) -> None:
    s = size / 30
    points = []
    for i in range(360):
        t = math.radians(i)
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        px = cx + x * s
        py = cy + y * s
        points.append((px, py))
    draw.polygon(points, fill=color)


def _draw_heart_outline(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int, color: tuple, width: int = 2) -> None:
    s = size / 30
    points = []
    for i in range(360):
        t = math.radians(i)
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        px = cx + x * s
        py = cy + y * s
        points.append((px, py))
    draw.polygon(points, outline=color, width=width)


def generate_ship(
    avatar1_url: str,
    avatar2_url: str,
    name1: str,
    name2: str,
    compat: int,
    ship_name: str,
    name_factor: float,
    id_factor: float,
    random_factor: float,
) -> io.BytesIO:
    """Generate a Loritta-style ship image."""

    if compat >= 80:
        bg_colors = [(255, 20, 80), (180, 30, 120)]
        heart_color = (255, 50, 100)
        accent = (255, 100, 150)
        glow_color = (255, 50, 100, 40)
    elif compat >= 60:
        bg_colors = [(220, 50, 180), (150, 30, 200)]
        heart_color = (236, 72, 153)
        accent = (217, 70, 239)
        glow_color = (236, 72, 153, 40)
    elif compat >= 40:
        bg_colors = [(100, 80, 200), (60, 50, 150)]
        heart_color = (139, 92, 246)
        accent = (99, 102, 241)
        glow_color = (139, 92, 246, 40)
    elif compat >= 20:
        bg_colors = [(60, 60, 120), (40, 40, 90)]
        heart_color = (99, 102, 241)
        accent = (79, 70, 229)
        glow_color = (99, 102, 241, 30)
    else:
        bg_colors = [(50, 50, 60), (30, 30, 40)]
        heart_color = (107, 114, 128)
        accent = (75, 85, 99)
        glow_color = (107, 114, 128, 30)

    img = Image.new("RGBA", (W, H), bg_colors[0])
    draw = ImageDraw.Draw(img)

    for y in range(H):
        t = y / H
        c = _lerp(bg_colors[0], bg_colors[1], t)
        draw.line([(0, y), (W, y)], fill=c)

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((W // 2 - 200, H // 2 - 200, W // 2 + 200, H // 2 + 200), fill=glow_color)
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    for _ in range(30):
        x = random.randint(0, W)
        y = random.randint(0, H)
        s = random.randint(1, 3)
        a = random.randint(30, 80)
        draw.ellipse((x, y, x + s, y + s), fill=(255, 255, 255, a))

    av1 = _download_avatar(avatar1_url, 200)
    av2 = _download_avatar(avatar2_url, 200)

    mask = _draw_circle_mask(200)
    border = 4

    av1_x, av1_y = 100, H // 2 - 100
    av2_x, av2_y = W - 300, H // 2 - 100

    draw.ellipse(
        (av1_x - border, av1_y - border, av1_x + 200 + border, av1_y + 200 + border),
        fill=(255, 255, 255, 200),
    )
    img.paste(av1, (av1_x, av1_y), mask)

    draw.ellipse(
        (av2_x - border, av2_y - border, av2_x + 200 + border, av2_y + 200 + border),
        fill=(255, 255, 255, 200),
    )
    img.paste(av2, (av2_x, av2_y), mask)

    heart_size = 80
    _draw_heart(draw, W // 2, H // 2, heart_size, heart_color)
    _draw_heart_outline(draw, W // 2, H // 2, heart_size + 6, (255, 255, 255, 180), 2)

    font_name = _font_bold("segoeuib.ttf", 28)
    font_compat = _font_bold("segoeuib.ttf", 48)
    font_bar = _font("segoeui.ttf", 18)
    font_factors = _font("segoeui.ttf", 16)
    font_ship = _font_bold("segoeuib.ttf", 24)

    name1_bbox = draw.textbbox((0, 0), name1, font=font_name)
    name1_w = name1_bbox[2] - name1_bbox[0]
    draw.text(((av1_x + 100) - name1_w // 2, av1_y + 210), name1, fill=(255, 255, 255), font=font_name)

    name2_bbox = draw.textbbox((0, 0), name2, font=font_name)
    name2_w = name2_bbox[2] - name2_bbox[0]
    draw.text(((av2_x + 100) - name2_w // 2, av2_y + 210), name2, fill=(255, 255, 255), font=font_name)

    ship_bbox = draw.textbbox((0, 0), ship_name, font=font_ship)
    ship_w = ship_bbox[2] - ship_bbox[0]
    draw.text(((W // 2) - ship_w // 2, 25), ship_name, fill=accent, font=font_ship)

    compat_text = f"{compat}%"
    compat_bbox = draw.textbbox((0, 0), compat_text, font=font_compat)
    compat_w = compat_bbox[2] - compat_bbox[0]
    draw.text(((W // 2) - compat_w // 2, H - 120), compat_text, fill=(255, 255, 255), font=font_compat)

    bar_x = W // 2 - 150
    bar_y = H - 60
    bar_w = 300
    bar_h = 16

    draw.rounded_rectangle(
        (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
        radius=bar_h // 2,
        fill=(255, 255, 255, 30),
    )

    fill_w = int(bar_w * compat / 100)
    if fill_w > 0:
        for x in range(fill_w):
            t = x / bar_w
            c = _lerp(heart_color, accent, t)
            draw.rounded_rectangle(
                (bar_x, bar_y, bar_x + x + 1, bar_y + bar_h),
                radius=bar_h // 2,
                fill=c,
            )

    factor_y = H - 35
    factors_text = f"Nomes: {int(name_factor * 25)}/25  •  IDs: {int(id_factor * 25)}/25  •  Destino: {int(random_factor * 50)}/50"
    fac_bbox = draw.textbbox((0, 0), factors_text, font=font_factors)
    fac_w = fac_bbox[2] - fac_bbox[0]
    draw.text(((W // 2) - fac_w // 2, factor_y), factors_text, fill=(200, 200, 200), font=font_factors)

    if compat == 100:
        for _ in range(15):
            hx = random.randint(50, W - 50)
            hy = random.randint(10, H - 10)
            hs = random.randint(8, 18)
            _draw_heart(draw, hx, hy, hs, (255, 200, 200, random.randint(80, 160)))
    elif compat >= 80:
        for _ in range(8):
            hx = random.randint(50, W - 50)
            hy = random.randint(10, H - 10)
            hs = random.randint(6, 12)
            _draw_heart(draw, hx, hy, hs, (255, 180, 200, random.randint(60, 120)))

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf
