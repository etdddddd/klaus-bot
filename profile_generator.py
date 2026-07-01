from __future__ import annotations

import io
import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from theme_art import apply_theme_art

FONTS_DIR = Path(os.environ.get("FONTS_DIR", "C:/Windows/Fonts"))

W = 800
H = 520


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


def _alpha(c, a):
    return (c[0], c[1], c[2], a)


def _circle_mask(s):
    m = Image.new("L", s, 0)
    ImageDraw.Draw(m).ellipse((0, 0, s[0] - 1, s[1] - 1), fill=255)
    return m


def _soft_glow(img, cx, cy, r, color, intensity=1.0):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(r, 0, -2):
        t = i / r
        a = int((1.0 - t) * 40 * intensity)
        if a < 1:
            continue
        d.ellipse((cx - i, cy - i, cx + i, cy + i), fill=_alpha(color, a))
    ov = ov.filter(ImageFilter.GaussianBlur(6))
    return Image.alpha_composite(img, ov)


# ── PARTICLE SYSTEMS ──

def _particles_v2(img, color, count=80, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(count):
        x, y = rng.randint(0, w), rng.randint(0, h)
        sz = rng.choice([1, 1, 2, 2, 3, 3, 4])
        a = rng.randint(20, 90)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).ellipse((x - sz, y - sz, x + sz, y + sz), fill=_alpha(color, a))
        if rng.random() < 0.4 and sz >= 2:
            glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ImageDraw.Draw(glow).ellipse((x - sz * 3, y - sz * 3, x + sz * 3, y + sz * 3), fill=_alpha(color, a // 5))
            glow = glow.filter(ImageFilter.GaussianBlur(4))
            ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


def _sparkles_v2(img, color, count=25, seed=99):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(count):
        x, y = rng.randint(30, w - 30), rng.randint(20, h - 20)
        size = rng.choice([3, 4, 5, 6, 7, 8])
        a = rng.randint(60, 180)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        c = _alpha(color, a)
        s3 = int(size * 0.7)
        d.line((x - size, y, x + size, y), fill=c, width=1)
        d.line((x, y - size, x, y + size), fill=c, width=1)
        d.line((x - s3, y - s3, x + s3, y + s3), fill=c, width=1)
        d.line((x - s3, y + s3, x + s3, y - s3), fill=c, width=1)
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=_alpha(color, min(255, a + 60)))
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((x - size * 2, y - size * 2, x + size * 2, y + size * 2), fill=_alpha(color, a // 5))
        glow = glow.filter(ImageFilter.GaussianBlur(4))
        ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


def _glow_ring(img, cx, cy, r, color, rings=12, spread=3, blur=3):
    for i in range(rings, 0, -1):
        rad = r + i * spread
        a = max(0, int(35 - i * 2.5))
        if a < 1:
            continue
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).ellipse((cx - rad, cy - rad, cx + rad, cy + rad), outline=_alpha(color, a), width=2)
        ov = ov.filter(ImageFilter.GaussianBlur(blur))
        img = Image.alpha_composite(img, ov)
    return img


def _diagonal_stripes(img, color, spacing=80, alpha=8):
    w, h = img.size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for offset in range(-h, w + h, spacing):
        d.line((offset, 0, offset + h, h), fill=_alpha(color, alpha), width=1)
    img = Image.alpha_composite(img, ov)
    return img


def _flowing_waves(img, color, y_base, amplitude=15, wavelength=120, alpha=12):
    w, h = img.size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for layer in range(3):
        pts, off = [], layer * 30
        a = alpha - layer * 3
        if a < 1:
            continue
        for x in range(0, w + 2, 2):
            y = y_base + int(amplitude * math.sin((x + off) * 2 * math.pi / wavelength))
            pts.append((x, y))
        for i in range(len(pts) - 1):
            d.line((pts[i], pts[i + 1]), fill=_alpha(color, a), width=2)
    img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════
# NEW EFFECT TYPES
# ══════════════════════════════════════════

def _effect_aurora(img, colors, intensity=1):
    w, h = img.size
    for band in range(intensity):
        ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        c = colors[band % len(colors)]
        y_center = 80 + band * 120
        for y in range(max(0, y_center - 60), min(h, y_center + 60)):
            t = 1.0 - abs(y - y_center) / 60.0
            a = int(t * 25 * intensity)
            if a < 1:
                continue
            wave_offset = int(20 * math.sin(y * 0.05 + band * 2))
            for x in range(0, w, 3):
                xa = int(15 * math.sin(x * 0.02 + y * 0.01 + band))
                d.point((x + wave_offset + xa, y), fill=_alpha(c, a))
        ov = ov.filter(ImageFilter.GaussianBlur(12))
        img = Image.alpha_composite(img, ov)
    return img


def _effect_embers(img, color, count=120, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(count):
        x, y = rng.randint(0, w), rng.randint(h // 3, h)
        sz = rng.choice([1, 2, 2, 3, 3, 4, 5])
        a = rng.randint(30, 120)
        c = _alpha(color, a)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.ellipse((x - sz, y - sz, x + sz, y + sz), fill=c)
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((x - sz * 4, y - sz * 4, x + sz * 4, y + sz * 4), fill=_alpha(color, a // 4))
        glow = glow.filter(ImageFilter.GaussianBlur(6))
        ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


def _effect_rain(img, color, intensity=1, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    drops = 40 * intensity
    for _ in range(drops):
        x = rng.randint(0, w)
        y = rng.randint(0, h)
        length = rng.randint(10, 30)
        a = rng.randint(15, 45)
        d.line((x, y, x - 2, y + length), fill=_alpha(color, a), width=1)
    img = Image.alpha_composite(img, ov)
    return img


def _effect_neon_pulse(img, color, intensity=1, seed=42):
    w, h = img.size
    for band_y in range(3):
        y = 100 + band_y * 150
        for i in range(8 * intensity):
            a = max(0, int(30 - i * 4))
            if a < 1:
                continue
            ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            ImageDraw.Draw(ov).rectangle((0, y - i, w, y + i), fill=_alpha(color, a))
            ov = ov.filter(ImageFilter.GaussianBlur(8))
            img = Image.alpha_composite(img, ov)
    return img


def _effect_shadow_waves(img, color, intensity=1):
    w, h = img.size
    for layer in range(intensity):
        ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        y_base = 150 + layer * 100
        pts = []
        for x in range(0, w + 2, 3):
            y = y_base + int(30 * math.sin(x * 0.008 + layer * 1.5))
            pts.append((x, y))
        for i in range(len(pts) - 1):
            d.line((pts[i], pts[i + 1]), fill=_alpha(color, 40 - layer * 10), width=30)
        ov = ov.filter(ImageFilter.GaussianBlur(20))
        img = Image.alpha_composite(img, ov)
    return img


def _effect_crystal_shimmer(img, color, count=100, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(count):
        x, y = rng.randint(20, w - 20), rng.randint(20, h - 20)
        size = rng.choice([2, 3, 4, 5, 6])
        a = rng.randint(80, 220)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        c = _alpha(color, a)
        for angle_deg in [0, 60, 120]:
            angle = math.radians(angle_deg)
            ex = x + int(size * math.cos(angle))
            ey = y + int(size * math.sin(angle))
            sx = x - int(size * math.cos(angle))
            sy = y - int(size * math.sin(angle))
            d.line((sx, sy, ex, ey), fill=c, width=1)
        d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=_alpha(color, min(255, a + 40)))
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((x - size * 3, y - size * 3, x + size * 3, y + size * 3), fill=_alpha(color, a // 6))
        glow = glow.filter(ImageFilter.GaussianBlur(5))
        ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


def _effect_nebula(img, colors, intensity=1, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(4 + intensity * 2):
        cx, cy = rng.randint(100, w - 100), rng.randint(50, h - 50)
        r = rng.randint(80, 200) * intensity
        c = rng.choice(colors)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for i in range(r, 0, -3):
            t = i / r
            a = int((1 - t) * 15 * intensity)
            if a < 1:
                continue
            d.ellipse((cx - i, cy - i, cx + i, cy + i), fill=_alpha(c, a))
        ov = ov.filter(ImageFilter.GaussianBlur(25))
        img = Image.alpha_composite(img, ov)
    return img


def _effect_vortex_particles(img, color, count=100, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    cx, cy = w * 0.55, h * 0.5
    for _ in range(count):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(20, 280)
        x = int(cx + dist * math.cos(angle))
        y = int(cy + dist * math.sin(angle) * 0.6)
        if not (0 < x < w and 0 < y < h):
            continue
        sz = rng.choice([1, 2, 2, 3])
        a = int(max(10, 80 - dist * 0.2))
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).ellipse((x - sz, y - sz, x + sz, y + sz), fill=_alpha(color, a))
        img = Image.alpha_composite(img, ov)
    return img


def _effect_falling_petals(img, colors, count=50, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(count):
        x, y = rng.randint(0, w), rng.randint(-20, h)
        c = rng.choice(colors)
        sz = rng.choice([2, 3, 4, 5])
        a = rng.randint(40, 120)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.ellipse((x - sz, y - sz // 2, x + sz, y + sz // 2), fill=_alpha(c, a))
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((x - sz * 3, y - sz * 2, x + sz * 3, y + sz * 2), fill=_alpha(c, a // 6))
        glow = glow.filter(ImageFilter.GaussianBlur(4))
        ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


def _effect_grid_glow(img, color, intensity=1, spacing=50):
    w, h = img.size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for x in range(0, w, spacing):
        d.line((x, 0, x, h), fill=_alpha(color, 4 + intensity * 2), width=1)
    for y in range(0, h, spacing):
        d.line((0, y, w, y), fill=_alpha(color, 4 + intensity * 2), width=1)
    intersections = [(x, y) for x in range(0, w, spacing) for y in range(0, h, spacing)]
    rng = random.Random(hash((color[0], color[1], color[2])))
    for ix, iy in rng.sample(intersections, min(15 * intensity, len(intersections))):
        a = rng.randint(20, 60 * intensity)
        ov2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov2).ellipse((ix - 3, iy - 3, ix + 3, iy + 3), fill=_alpha(color, a))
        ov2 = ov2.filter(ImageFilter.GaussianBlur(2))
        ov = Image.alpha_composite(ov, ov2)
    img = Image.alpha_composite(img, ov)
    return img


def _effect_sacred_geometry(img, color, intensity=1):
    w, h = img.size
    cx, cy = w // 2, h // 2
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for ring in range(3 * intensity):
        r = 60 + ring * 50
        a = max(0, 20 - ring * 4)
        if a < 1:
            break
        c = _alpha(color, a)
        points = []
        n = 6
        for i in range(n + 1):
            angle = 2 * math.pi * i / n + ring * 0.3
            px = cx + int(r * math.cos(angle))
            py = cy + int(r * math.sin(angle))
            points.append((px, py))
        for i in range(n):
            d.line((points[i], points[i + 1]), fill=c, width=1)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=_alpha(color, a // 2), width=1)
    ov = ov.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════
# MAIN GENERATOR
# ══════════════════════════════════════════

def generate_profile(
    username: str = "User",
    koins: int = 0,
    rank_name: str = "INICIANTE",
    rank_position: int = 0,
    wins: int = 0,
    losses: int = 0,
    streak: int = 0,
    commands_used: int = 0,
    achievements_count: int = 0,
    avatar_url: str | None = None,
    avatar: Image.Image | None = None,
    level: int = 1,
    xp_current: int = 0,
    xp_next: int = 100,
    bg_color: str = "#0f0a1a",
    accent_color: str = "#8b5cf6",
    border_color: str = "#d946ef",
    purchased_borders: list[str] | None = None,
    active_border: str = "default",
    effects: dict | None = None,
    theme: str = "padrao",
) -> io.BytesIO:
    bg = _hex(bg_color)
    acc = _hex(accent_color)
    brd = _hex(border_color)
    brt = _bright(brd, 1.5)
    brt2 = _bright(brd, 2.0)

    if effects is None:
        effects = {"particles": 60, "sparkles": 10, "stripes": False, "grid": False, "glow": 1}

    # ── SIMPLIFY: reduce all effects for cleaner look ──
    effects = dict(effects)
    effects["particles"] = max(0, int(effects.get("particles", 60) * 0.3))
    effects["sparkles"] = max(0, int(effects.get("sparkles", 10) * 0.25))
    effects["stripes"] = False
    effects["grid"] = False
    effects["glow"] = min(1, effects.get("glow", 1))
    effects["intensity"] = min(1, effects.get("intensity", 1))

    n_particles = effects.get("particles", 15)
    n_sparkles = effects.get("sparkles", 3)
    do_stripes = effects.get("stripes", False)
    do_grid = effects.get("grid", False)
    glow_level = effects.get("glow", 1)
    effect_type = effects.get("type", "default")
    effect_intensity = effects.get("intensity", 1)

    img = Image.new("RGBA", (W, H), bg + (255,))
    draw = ImageDraw.Draw(img)

    for y in range(H):
        t = y / H
        c1 = _lerp(bg, _dim(brd, 0.2), t * 0.4)
        c2 = _lerp(c1, _dim(acc, 0.15), t * 0.3)
        draw.line((0, y, W, y), fill=c2 + (255,))

    seed = hash((bg_color, border_color)) % 100000

    # ── TYPE-BASED EFFECTS ──
    if effect_type == "aurora":
        img = _effect_aurora(img, [brd, acc], max(1, effect_intensity))
    elif effect_type == "embers":
        img = _effect_embers(img, brt, count=max(5, 15 + effect_intensity * 8), seed=seed)
        img = _effect_embers(img, (255, 100, 30), count=max(3, 8 + effect_intensity * 4), seed=seed + 10)
    elif effect_type == "rain":
        img = _effect_rain(img, brt, max(1, effect_intensity), seed=seed)
    elif effect_type == "neon_pulse":
        img = _effect_neon_pulse(img, brt, max(1, effect_intensity), seed=seed)
    elif effect_type == "shadow_waves":
        img = _effect_shadow_waves(img, _dim(brd, 0.5), max(1, effect_intensity))
    elif effect_type == "crystal":
        img = _effect_crystal_shimmer(img, brt, count=max(5, 10 + effect_intensity * 6), seed=seed)
    elif effect_type == "nebula":
        img = _effect_nebula(img, [brd, acc], max(1, effect_intensity), seed=seed)
    elif effect_type == "vortex":
        img = _effect_vortex_particles(img, brt, count=max(8, 20 + effect_intensity * 8), seed=seed)
    elif effect_type == "petals":
        img = _effect_falling_petals(img, [brd, acc], count=max(5, 8 + effect_intensity * 5), seed=seed)
    elif effect_type == "sacred_geometry":
        img = _effect_sacred_geometry(img, brt, max(1, effect_intensity))
    else:
        if glow_level >= 1:
            img = _soft_glow(img, 400, 260, int(120 * glow_level * 0.3), brd, glow_level * 0.3)

    # ── BASE EFFECTS (always applied, layered on top) ──
    if do_grid:
        img = _effect_grid_glow(img, brd, glow_level)

    if do_stripes:
        img = _diagonal_stripes(img, brd, spacing=90, alpha=7)
        img = _diagonal_stripes(img, acc, spacing=130, alpha=5)

    if glow_level >= 1:
        gi = glow_level * 0.3
        img = _soft_glow(img, 700, 80, int(60 * gi), brd, gi)
        img = _soft_glow(img, 750, 440, int(40 * gi), brd, gi * 0.7)

    if n_particles > 0:
        img = _particles_v2(img, brt2, count=n_particles, seed=seed)
        img = _sparkles_v2(img, brt, count=n_sparkles, seed=seed + 1)

    for cx, cy, r, a in [(720, -40, 100, 8), (750, 440, 60, 6)]:
        img = _soft_glow(img, cx, cy, r, brd, a / 20.0)

    # ── THEMED ART ──
    img = apply_theme_art(img, theme, brd, acc, seed=seed)

    # ── TOP/BOTTOM GLOW LINES ──
    for i in range(3):
        a = int(180 - i * 50) * glow_level // 2
        a = max(0, min(255, a))
        if a < 1:
            break
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ov).rectangle((0, i, W, i + 1), fill=_alpha(brt, a))
        ov = ov.filter(ImageFilter.GaussianBlur(1))
        img = Image.alpha_composite(img, ov)

    for i in range(3):
        a = int(140 - i * 35) * glow_level // 2
        a = max(0, min(255, a))
        if a < 1:
            break
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ov).rectangle((0, H - 1 - i, W, H - i), fill=_alpha(acc, a))
        ov = ov.filter(ImageFilter.GaussianBlur(1))
        img = Image.alpha_composite(img, ov)

    # ── DOWNLOAD AVATAR ──
    if avatar is None and avatar_url:
        try:
            import requests as _req
            resp = _req.get(avatar_url, timeout=10)
            avatar = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        except Exception:
            avatar = Image.new("RGBA", (128, 128), (80, 80, 100, 255))
    if avatar is None:
        avatar = Image.new("RGBA", (128, 128), (80, 80, 100, 255))

    # ── LEFT PANEL ──
    PANEL_W = 270
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    panel_bg = Image.new("RGBA", (PANEL_W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel_bg)
    for x in range(PANEL_W):
        t = x / PANEL_W
        c = _lerp(_dim(bg, 0.3), (0, 0, 0), t * 0.6)
        pd.line((x, 0, x, H), fill=c + (160,))
    ov.paste(panel_bg, (0, 0))
    img = Image.alpha_composite(img, ov)

    for x in range(PANEL_W - 1, PANEL_W + 10):
        dist = x - (PANEL_W - 1)
        a = max(0, int(120 - dist * 12))
        if a < 1:
            break
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ov).line((x, 0, x, H), fill=_alpha(brt, a))
        img = Image.alpha_composite(img, ov)

    ov = Image.new("RGBA", (PANEL_W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for off in range(-H, PANEL_W + H, 60):
        d.line((off, 0, off + H, H), fill=_alpha(brd, 3), width=1)
    panel_ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    panel_ov.paste(ov, (0, 0))
    img = Image.alpha_composite(img, panel_ov)
    draw = ImageDraw.Draw(img)

    # ── AVATAR ──
    av_sz = 140
    av_x = (PANEL_W - av_sz) // 2
    av_y = 40
    av_cx = av_x + av_sz // 2
    av_cy = av_y + av_sz // 2

    img = _glow_ring(img, av_cx, av_cy, av_sz // 2 + 8, brt, rings=6, spread=3, blur=3)

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(3):
        r = av_sz // 2 + 4 + i
        a = max(0, int(160 - i * 40))
        d.ellipse((av_cx - r, av_cy - r, av_cx + r, av_cy + r), outline=_alpha(brt, a), width=2)
    ov = ov.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, ov)

    bw = 4
    bi = Image.new("RGBA", (av_sz + bw * 2, av_sz + bw * 2), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bi)
    for i in range(3):
        bd.ellipse(
            (i, i, av_sz + bw * 2 - 1 - i, av_sz + bw * 2 - 1 - i),
            outline=_alpha(brt, max(0, 255 - i * 40)), width=bw - i
        )
    img.paste(bi, (av_x - bw, av_y - bw), bi)

    av_r = avatar.resize((av_sz, av_sz), Image.Resampling.LANCZOS)
    img.paste(av_r.convert("RGBA"), (av_x, av_y), _circle_mask((av_sz, av_sz)))
    draw = ImageDraw.Draw(img)

    ov = Image.new("RGBA", (av_sz, av_sz), (0, 0, 0, 0))
    ImageDraw.Draw(ov).arc((0, 0, av_sz, av_sz), 200, 340, fill=_alpha(brt, 40), width=2)
    img.paste(ov, (av_x, av_y), ov)
    draw = ImageDraw.Draw(img)

    # ── FONTS ──
    fn_name = _font_bold("segoeuib.ttf", 24)
    fn_small = _font("segoeui.ttf", 13)
    fn_tiny = _font("segoeui.ttf", 11)
    fn_mid = _font_bold("segoeuib.ttf", 16)
    fn_lbl = _font("segoeui.ttf", 12)
    fn_val = _font_bold("segoeuib.ttf", 15)
    fn_big = _font_bold("segoeuib.ttf", 28)

    name = username if len(username) <= 18 else username[:16] + ".."
    bb = draw.textbbox((0, 0), name, font=fn_name)
    tw = bb[2] - bb[0]
    nx = (PANEL_W - tw) // 2
    ny = av_y + av_sz + 20
    draw.text((nx + 1, ny + 1), name, fill=(0, 0, 0, 120), font=fn_name)
    draw.text((nx, ny), name, fill=(255, 255, 255), font=fn_name)

    rk = rank_name if len(rank_name) <= 22 else rank_name[:20] + ".."
    bb = draw.textbbox((0, 0), rk, font=fn_small)
    tw = bb[2] - bb[0]
    badge_pad = 20
    badge_w = tw + badge_pad * 2
    badge_h = 26
    bx = (PANEL_W - badge_w) // 2
    by = ny + 38

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bdg = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bdg)
    bd.rounded_rectangle((0, 0, badge_w, badge_h), radius=badge_h // 2, fill=_alpha(acc, 55))
    bd.rounded_rectangle((0, 0, badge_w, badge_h), radius=badge_h // 2, outline=_alpha(brt, 160), width=1)
    ov.paste(bdg, (bx, by))
    img = Image.alpha_composite(img, ov)
    draw = ImageDraw.Draw(img)
    draw.text((bx + badge_pad, by + 4), rk, fill=_alpha(brt, 245), font=fn_small)

    pos = f"#{rank_position} no ranking"
    bb = draw.textbbox((0, 0), pos, font=fn_tiny)
    tw = bb[2] - bb[0]
    draw.text(((PANEL_W - tw) // 2, by + 34), pos, fill=(160, 150, 190), font=fn_tiny)

    ktext = f"{koins:,}".replace(",", ".")
    bb = draw.textbbox((0, 0), ktext, font=fn_big)
    tw = bb[2] - bb[0]
    kx = (PANEL_W - tw) // 2
    ky = by + 55

    for i in range(4):
        a = max(0, int(40 - i * 10))
        draw.text((kx + i, ky + i), ktext, fill=(0, 0, 0, a), font=fn_big)
    draw.text((kx, ky), ktext, fill=(255, 215, 0), font=fn_big)

    bb = draw.textbbox((0, 0), "Koins", font=fn_tiny)
    tw = bb[2] - bb[0]
    draw.text(((PANEL_W - tw) // 2, ky + 34), "Koins", fill=(180, 160, 120), font=fn_tiny)

    # ── RIGHT PANEL ──
    rx = PANEL_W + 35
    rw = W - PANEL_W - 50

    sy = 28
    draw.text((rx + 1, sy + 1), "Estatisticas", fill=(0, 0, 0, 80), font=fn_mid)
    draw.text((rx, sy), "Estatisticas", fill=(220, 210, 250), font=fn_mid)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.line((rx, sy + 28, rx + rw, sy + 28), fill=_alpha(brt, 50), width=1)
    img = Image.alpha_composite(img, ov)
    draw = ImageDraw.Draw(img)

    stats = [
        ("Koins", f"{koins:,}".replace(",", "."), (255, 215, 0)),
        ("Wins", str(wins), (74, 222, 128)),
        ("Losses", str(losses), (248, 113, 113)),
        ("Win Rate", f"{round((wins / (wins + losses)) * 100) if (wins + losses) > 0 else 0}%", (139, 92, 246)),
        ("Streak", f"{streak} dias", (251, 146, 60)),
        ("Comandos", f"{commands_used:,}".replace(",", "."), (96, 165, 250)),
        ("Conquistas", str(achievements_count), (232, 121, 249)),
    ]

    stat_y = sy + 40
    col_w = rw // 2

    for i, (label, value, dot_color) in enumerate(stats):
        col = i % 2
        row = i // 2
        sx = rx + col * col_w
        sy2 = stat_y + row * 44
        card_w = col_w - 12
        card_h = 38

        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
        cdd = ImageDraw.Draw(cd)
        cdd.rounded_rectangle((0, 0, card_w, card_h), radius=8, fill=(255, 255, 255, 8))
        cdd.rounded_rectangle((0, 0, card_w, card_h), radius=8, outline=(255, 255, 255, 12), width=1)
        ov.paste(cd, (sx, sy2))
        img = Image.alpha_composite(img, ov)
        draw = ImageDraw.Draw(img)

        draw.ellipse((sx + 10, sy2 + 10, sx + 18, sy2 + 18), fill=_alpha(dot_color, 220))
        draw.text((sx + 24, sy2 + 6), label, fill=(150, 140, 180), font=fn_lbl)

        vt = str(value)
        max_vw = card_w - 30
        vb = draw.textbbox((0, 0), vt, font=fn_val)
        vw = vb[2] - vb[0]
        while vw > max_vw and len(vt) > 4:
            vt = vt[:-4] + "..."
            vb = draw.textbbox((0, 0), vt, font=fn_val)
            vw = vb[2] - vb[0]
        draw.text((sx + 10, sy2 + 20), vt, fill=(255, 255, 255), font=fn_val)

    # ── LEVEL BAR ──
    bar_y = stat_y + (len(stats) // 2 + 1) * 44 + 8
    draw.text((rx + 1, bar_y + 1), f"Nivel {level}", fill=(0, 0, 0, 60), font=fn_mid)
    draw.text((rx, bar_y), f"Nivel {level}", fill=(220, 210, 250), font=fn_mid)
    bar_y += 28
    progress = xp_current / xp_next if xp_next > 0 else 0
    bar_h = 18

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = Image.new("RGBA", (rw, bar_h), (0, 0, 0, 0))
    bdd = ImageDraw.Draw(bd)
    bdd.rounded_rectangle((0, 0, rw, bar_h), radius=bar_h // 2, fill=(20, 15, 40, 220))
    bdd.rounded_rectangle((0, 0, rw, bar_h), radius=bar_h // 2, outline=_alpha(brd, 40), width=1)
    ov.paste(bd, (rx, bar_y))
    img = Image.alpha_composite(img, ov)
    draw = ImageDraw.Draw(img)

    if progress > 0:
        fw = max(bar_h, int(rw * min(progress, 1.0)))
        for gi in range(8):
            ga = max(0, int(60 - gi * 8))
            if ga < 1:
                break
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gd = Image.new("RGBA", (fw, bar_h + gi * 2), (0, 0, 0, 0))
            ImageDraw.Draw(gd).rounded_rectangle((0, 0, fw, bar_h + gi * 2), radius=(bar_h + gi * 2) // 2, fill=_alpha(brt, ga))
            ov.paste(gd, (rx, bar_y - gi))
            img = Image.alpha_composite(img, ov)
        draw = ImageDraw.Draw(img)

        fill_ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        fill_bar = Image.new("RGBA", (fw, bar_h), (0, 0, 0, 0))
        fd = ImageDraw.Draw(fill_bar)
        fd.rounded_rectangle((0, 0, fw, bar_h), radius=bar_h // 2, fill=_alpha(brt, 230))
        fill_ov.paste(fill_bar, (rx, bar_y))
        img = Image.alpha_composite(img, fill_ov)
        draw = ImageDraw.Draw(img)

    xp_text = f"{xp_current}/{xp_next} XP"
    bb = draw.textbbox((0, 0), xp_text, font=fn_tiny)
    tw = bb[2] - bb[0]
    draw.text((rx + (rw - tw) // 2, bar_y + 3), xp_text, fill=(255, 255, 255, 200), font=fn_tiny)

    ach_y = bar_y + 30
    if achievements_count > 0:
        draw.text((rx, ach_y), "Conquistas", fill=(210, 200, 240), font=fn_lbl)
        for ai in range(min(achievements_count, 18)):
            x = rx + ai * 18
            if x + 14 > rx + rw:
                break
            c = brt if ai % 3 == 0 else (acc if ai % 3 == 1 else _bright(acc, 1.3))
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            bd = Image.new("RGBA", (14, 14), (0, 0, 0, 0))
            ImageDraw.Draw(bd).rounded_rectangle((0, 0, 13, 13), radius=3, fill=_alpha(c, 140))
            ov.paste(bd, (x, ach_y + 18))
            img = Image.alpha_composite(img, ov)
        draw = ImageDraw.Draw(img)

    fy = H - 30
    ft = "Klaus Bot - Perfil"
    bb = draw.textbbox((0, 0), ft, font=fn_tiny)
    tw = bb[2] - bb[0]
    draw.text(((W - tw) // 2, fy), ft, fill=(70, 60, 100), font=fn_tiny)

    result = Image.new("RGB", img.size, (15, 10, 26))
    result.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)

    buf = io.BytesIO()
    result.save(buf, format="PNG", quality=95)
    buf.seek(0)
    return buf
