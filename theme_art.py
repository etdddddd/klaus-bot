from __future__ import annotations
import math
import random
from PIL import Image, ImageDraw, ImageFilter


def _alpha(c, a):
    return (c[0], c[1], c[2], a)


def _bright(c, f=1.3):
    return tuple(min(255, int(v * f)) for v in c[:3])


def _dim(c, f=0.5):
    return tuple(max(0, int(v * f)) for v in c[:3])


def _ov(img, fn):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    fn(ov)
    r = Image.alpha_composite(img, ov)
    return r, ImageDraw.Draw(r)


# ══════════════════════════════════════════════
# NATURE / PLANTS
# ══════════════════════════════════════════════

def draw_cacti(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(3, 6)):
        x = rng.randint(50, w - 50)
        bh = rng.randint(40, 100)
        bw = rng.randint(8, 14)
        y = h - rng.randint(10, 40)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.rounded_rectangle((x - bw // 2, y - bh, x + bw // 2, y), radius=bw // 2, fill=_alpha(color, 40))
        arm_h = rng.randint(15, 35)
        arm_w = rng.randint(6, 10)
        if rng.random() > 0.3:
            side = rng.choice([-1, 1])
            ax = x + side * bw
            ay = y - bh // 2 - rng.randint(0, bh // 4)
            d.rounded_rectangle((ax, ay - arm_h, ax + side * arm_w, ay), radius=arm_w // 2, fill=_alpha(color, 35))
            d.rounded_rectangle((ax, ay - arm_h, ax - side * bw // 2, ay - arm_h + arm_w), radius=arm_w // 2, fill=_alpha(color, 35))
        ov = ov.filter(ImageFilter.GaussianBlur(2))
        img = Image.alpha_composite(img, ov)
    return img


def draw_trees(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(2, 5)):
        x = rng.randint(60, w - 60)
        trunk_h = rng.randint(30, 60)
        y = h - rng.randint(10, 30)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.rectangle((x - 3, y - trunk_h, x + 3, y), fill=_alpha(_dim(color, 0.6), 50))
        crown_r = rng.randint(20, 40)
        cy = y - trunk_h - crown_r // 2
        for i in range(3):
            r = crown_r - i * 5
            a = 30 - i * 8
            d.ellipse((x - r, cy - r + i * 3, x + r, cy + r + i * 3), fill=_alpha(color, a))
        ov = ov.filter(ImageFilter.GaussianBlur(2))
        img = Image.alpha_composite(img, ov)
    return img


def draw_leaves(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(15, 30)):
        x, y = rng.randint(0, w), rng.randint(0, h)
        sz = rng.randint(4, 12)
        angle = rng.uniform(0, 360)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        pts = []
        for t in range(0, 360, 30):
            r = sz * (1 + 0.3 * math.cos(math.radians(t * 2)))
            px = x + r * math.cos(math.radians(t + angle))
            py = y + r * math.sin(math.radians(t + angle))
            pts.append((px, py))
        if len(pts) >= 3:
            d.polygon(pts, fill=_alpha(color, rng.randint(15, 35)))
        ov = ov.filter(ImageFilter.GaussianBlur(1))
        img = Image.alpha_composite(img, ov)
    return img


def draw_flowers(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(8, 16)):
        cx = rng.randint(30, w - 30)
        cy = rng.randint(30, h - 30)
        petals = rng.randint(4, 7)
        pr = rng.randint(4, 10)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for p in range(petals):
            angle = 2 * math.pi * p / petals
            px = cx + int(pr * 1.2 * math.cos(angle))
            py = cy + int(pr * 1.2 * math.sin(angle))
            d.ellipse((px - pr, py - pr, px + pr, py + pr), fill=_alpha(color, rng.randint(25, 50)))
        d.ellipse((cx - pr // 2, cy - pr // 2, cx + pr // 2, cy + pr // 2), fill=_alpha(_bright(color, 1.5), 60))
        img = Image.alpha_composite(img, ov)
    return img


def draw_bamboo(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(3, 6)):
        x = rng.randint(40, w - 40)
        segments = rng.randint(4, 8)
        seg_h = rng.randint(15, 25)
        y = h - rng.randint(5, 20)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for s in range(segments):
            sy = y - s * seg_h
            d.rectangle((x - 3, sy - seg_h, x + 3, sy), fill=_alpha(color, 30))
            d.line((x - 4, sy - seg_h, x + 4, sy - seg_h), fill=_alpha(color, 40), width=2)
            if rng.random() > 0.5:
                side = rng.choice([-1, 1])
                lx = x + side * 5
                ly = sy - seg_h // 2
                for leaf in range(2):
                    d.ellipse((lx, ly + leaf * 6 - 3, lx + side * 15, ly + leaf * 6 + 3), fill=_alpha(color, 25))
        ov = ov.filter(ImageFilter.GaussianBlur(1))
        img = Image.alpha_composite(img, ov)
    return img


def draw_grass(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for x in range(0, w, rng.randint(4, 8)):
        blade_h = rng.randint(8, 25)
        y = h - rng.randint(0, 15)
        curve = rng.randint(-5, 5)
        d.line((x, y, x + curve, y - blade_h), fill=_alpha(color, rng.randint(15, 35)), width=1)
    img = Image.alpha_composite(img, ov)
    return img


def draw_mushrooms(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(4, 8)):
        x = rng.randint(40, w - 40)
        y = h - rng.randint(10, 30)
        cap_r = rng.randint(8, 18)
        stem_h = rng.randint(10, 20)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.rectangle((x - 3, y - stem_h, x + 3, y), fill=_alpha(_bright(color, 0.8), 35))
        d.pieslice((x - cap_r, y - stem_h - cap_r, x + cap_r, y - stem_h + cap_r // 2), 180, 360, fill=_alpha(color, 40))
        for _ in range(rng.randint(2, 4)):
            dx = x + rng.randint(-cap_r + 3, cap_r - 3)
            dy = y - stem_h - rng.randint(2, cap_r - 2)
            d.ellipse((dx - 2, dy - 2, dx + 2, dy + 2), fill=_alpha(_bright(color, 1.5), 50))
        img = Image.alpha_composite(img, ov)
    return img


def draw_vine(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(2, 4)):
        start_x = rng.choice([0, w])
        start_y = rng.randint(0, h // 3)
        pts = [(start_x, start_y)]
        cx, cy = start_x, start_y
        for _ in range(rng.randint(8, 15)):
            cx += rng.randint(-30, 30) * (1 if start_x == 0 else -1)
            cy += rng.randint(15, 35)
            pts.append((cx, min(cy, h)))
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for i in range(len(pts) - 1):
            d.line((pts[i], pts[i + 1]), fill=_alpha(color, 25), width=2)
            if rng.random() > 0.5:
                lx, ly = pts[i]
                d.ellipse((lx + rng.randint(-8, 8) - 4, ly - 4, lx + rng.randint(-8, 8) + 4, ly + 4), fill=_alpha(color, 20))
        img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════════
# FIRE / LAVA / VOLCANIC
# ══════════════════════════════════════════════

def draw_flames(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(8, 16)):
        x = rng.randint(20, w - 20)
        base_y = h - rng.randint(0, 20)
        flame_h = rng.randint(20, 80)
        flame_w = rng.randint(6, 18)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        pts = [(x - flame_w, base_y)]
        for t in range(10):
            ty = base_y - flame_h * t / 10
            tx = x + int(flame_w * (1 - t / 10) * math.sin(t * 0.8))
            pts.append((tx, ty))
        pts.append((x + flame_w, base_y))
        if len(pts) >= 3:
            d.polygon(pts, fill=_alpha(color, rng.randint(20, 50)))
            inner = [(x, base_y - flame_h * 0.6)]
            for t in range(8):
                ty = base_y - flame_h * 0.6 * t / 8
                tx = x + int(flame_w * 0.4 * (1 - t / 8) * math.sin(t * 1.2))
                inner.append((tx, ty))
            inner.append((x, base_y - flame_h * 0.2))
            if len(inner) >= 3:
                d.polygon(inner, fill=_alpha(_bright(color, 1.5), rng.randint(15, 35)))
        ov = ov.filter(ImageFilter.GaussianBlur(3))
        img = Image.alpha_composite(img, ov)
    return img


def draw_embers(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(30, 60)):
        x = rng.randint(0, w)
        y = rng.randint(h // 3, h)
        sz = rng.choice([1, 2, 2, 3])
        a = rng.randint(30, 100)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.ellipse((x - sz, y - sz, x + sz, y + sz), fill=_alpha(color, a))
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((x - sz * 4, y - sz * 4, x + sz * 4, y + sz * 4), fill=_alpha(color, a // 5))
        glow = glow.filter(ImageFilter.GaussianBlur(5))
        ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


def draw_lava_cracks(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for _ in range(rng.randint(5, 10)):
        x, y = rng.randint(0, w), rng.randint(h // 2, h)
        for _ in range(rng.randint(3, 6)):
            nx = x + rng.randint(-40, 40)
            ny = y + rng.randint(-20, 20)
            d.line((x, y, nx, ny), fill=_alpha(color, rng.randint(20, 45)), width=rng.randint(1, 3))
            x, y = nx, ny
    ov = ov.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, ov)
    return img


def draw_sparks(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(15, 30)):
        x = rng.randint(20, w - 20)
        y = rng.randint(h // 4, h)
        sz = rng.randint(2, 5)
        a = rng.randint(60, 180)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for angle_deg in [0, 60, 120]:
            angle = math.radians(angle_deg)
            d.line((x - int(sz * math.cos(angle)), y - int(sz * math.sin(angle)),
                     x + int(sz * math.cos(angle)), y + int(sz * math.sin(angle))),
                    fill=_alpha(color, a), width=1)
        d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=_alpha(color, min(255, a + 40)))
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((x - sz * 3, y - sz * 3, x + sz * 3, y + sz * 3), fill=_alpha(color, a // 5))
        glow = glow.filter(ImageFilter.GaussianBlur(3))
        ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


def draw_magma(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(3):
        y_base = h - rng.randint(30, 80)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for y in range(y_base, h):
            t = (y - y_base) / max(1, h - y_base)
            a = int(20 + t * 30)
            d.line((0, y, w, y), fill=_alpha(color, a))
        img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════════
# WATER / OCEAN
# ══════════════════════════════════════════════

def draw_waves(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for layer in range(3):
        y_base = h - 80 + layer * 30
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        pts = []
        for x in range(0, w + 4, 4):
            y = y_base + int(15 * math.sin(x * 0.015 + layer * 2 + rng.random() * 0.5))
            pts.append((x, y))
        for x in range(w, -4, -4):
            pts.append((x, h + 10))
        if len(pts) >= 3:
            d.polygon(pts, fill=_alpha(color, 15 - layer * 3))
        img = Image.alpha_composite(img, ov)
    return img


def draw_bubbles(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(15, 35)):
        x = rng.randint(20, w - 20)
        y = rng.randint(20, h - 20)
        r = rng.randint(3, 12)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.ellipse((x - r, y - r, x + r, y + r), outline=_alpha(color, rng.randint(20, 50)), width=1)
        d.arc((x - r + 2, y - r + 2, x + r - 2, y + r - 2), 200, 320, fill=_alpha(_bright(color, 1.5), rng.randint(30, 60)), width=1)
        img = Image.alpha_composite(img, ov)
    return img


def draw_fish(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(3, 7)):
        x = rng.randint(50, w - 50)
        y = rng.randint(50, h - 50)
        sz = rng.randint(8, 18)
        direction = rng.choice([-1, 1])
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        body_x = x + direction * sz
        d.ellipse((x - sz, y - sz // 2, x + sz, y + sz // 2), fill=_alpha(color, rng.randint(20, 40)))
        tail_x = x - direction * sz
        d.polygon([(tail_x, y), (tail_x - direction * sz, y - sz // 2), (tail_x - direction * sz, y + sz // 2)], fill=_alpha(color, rng.randint(15, 35)))
        d.ellipse((x + direction * sz // 2 - 1, y - 2, x + direction * sz // 2 + 1, y + 2), fill=_alpha(_bright(color, 2), 80))
        img = Image.alpha_composite(img, ov)
    return img


def draw_coral(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(4, 8)):
        x = rng.randint(30, w - 30)
        base_y = h - rng.randint(5, 20)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        branches = rng.randint(3, 6)
        for b in range(branches):
            angle = math.radians(-90 + rng.randint(-40, 40))
            length = rng.randint(15, 40)
            ex = x + int(length * math.cos(angle))
            ey = base_y + int(length * math.sin(angle))
            d.line((x, base_y, ex, ey), fill=_alpha(color, rng.randint(25, 45)), width=rng.randint(2, 4))
            d.ellipse((ex - 3, ey - 3, ex + 3, ey + 3), fill=_alpha(_bright(color, 1.2), 40))
        img = Image.alpha_composite(img, ov)
    return img


def draw_seaweed(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(4, 8)):
        x = rng.randint(30, w - 30)
        base_y = h - rng.randint(5, 15)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        pts = [(x, base_y)]
        cx, cy = x, base_y
        for _ in range(rng.randint(5, 10)):
            cx += rng.randint(-8, 8)
            cy -= rng.randint(8, 15)
            pts.append((cx, cy))
        for i in range(len(pts) - 1):
            d.line((pts[i], pts[i + 1]), fill=_alpha(color, rng.randint(20, 40)), width=rng.randint(2, 4))
        img = Image.alpha_composite(img, ov)
    return img


def draw_shell(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(3, 6)):
        cx = rng.randint(50, w - 50)
        cy = rng.randint(h // 2, h - 30)
        r = rng.randint(8, 16)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for i in range(5):
            ri = r - i * 2
            if ri > 0:
                d.arc((cx - ri, cy - ri, cx + ri, cy + ri), -30, 210, fill=_alpha(color, 30 - i * 4), width=2)
        img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════════
# ICE / SNOW / WINTER
# ══════════════════════════════════════════════

def draw_snowflakes(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(20, 40)):
        x = rng.randint(10, w - 10)
        y = rng.randint(10, h - 10)
        sz = rng.randint(3, 8)
        a = rng.randint(30, 80)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for angle_deg in range(0, 360, 60):
            angle = math.radians(angle_deg)
            ex = x + int(sz * math.cos(angle))
            ey = y + int(sz * math.sin(angle))
            d.line((x, y, ex, ey), fill=_alpha(color, a), width=1)
            for br in range(1, 3):
                bx = x + int(sz * br / 3 * math.cos(angle))
                by = y + int(sz * br / 3 * math.sin(angle))
                for ba in [angle + 0.5, angle - 0.5]:
                    d.line((bx, by, bx + int(3 * math.cos(ba)), by + int(3 * math.sin(ba))), fill=_alpha(color, a - 10), width=1)
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((x - sz * 2, y - sz * 2, x + sz * 2, y + sz * 2), fill=_alpha(color, a // 4))
        glow = glow.filter(ImageFilter.GaussianBlur(3))
        ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


def draw_ice_crystals(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(5, 12)):
        x = rng.randint(20, w - 20)
        y = rng.randint(20, h - 20)
        sz = rng.randint(10, 25)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        points = []
        n = rng.choice([4, 6])
        for i in range(n):
            angle = 2 * math.pi * i / n
            px = x + int(sz * math.cos(angle))
            py = y + int(sz * math.sin(angle))
            points.append((px, py))
        for i in range(n):
            d.line((points[i], points[(i + 1) % n]), fill=_alpha(color, rng.randint(25, 50)), width=1)
            mid_x = (points[i][0] + points[(i + 1) % n][0]) // 2
            mid_y = (points[i][1] + points[(i + 1) % n][1]) // 2
            d.line((x, y, mid_x, mid_y), fill=_alpha(color, rng.randint(15, 30)), width=1)
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((x - sz, y - sz, x + sz, y + sz), fill=_alpha(color, 10))
        glow = glow.filter(ImageFilter.GaussianBlur(8))
        ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


def draw_frost(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for corner in [(0, 0), (w, 0), (0, h), (w, h)]:
        for _ in range(rng.randint(8, 15)):
            cx, cy = corner
            for _ in range(rng.randint(5, 12)):
                nx = cx + rng.randint(-30, 30)
                ny = cy + rng.randint(-30, 30)
                d.line((cx, cy, nx, ny), fill=_alpha(color, rng.randint(10, 25)), width=1)
                if rng.random() > 0.5:
                    cx, cy = nx, ny
    img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════════
# SPACE / COSMIC
# ══════════════════════════════════════════════

def draw_constellation(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    stars = [(rng.randint(20, w - 20), rng.randint(20, h - 20)) for _ in range(rng.randint(15, 30))]
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for sx, sy in stars:
        d.ellipse((sx - 1, sy - 1, sx + 1, sy + 1), fill=_alpha(color, rng.randint(60, 150)))
    for _ in range(rng.randint(5, 10)):
        i, j = rng.sample(range(len(stars)), 2)
        d.line((stars[i], stars[j]), fill=_alpha(color, rng.randint(10, 25)), width=1)
    img = Image.alpha_composite(img, ov)
    return img


def draw_planets(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(1, 3)):
        x = rng.randint(80, w - 80)
        y = rng.randint(40, h - 40)
        r = rng.randint(12, 30)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.ellipse((x - r, y - r, x + r, y + r), fill=_alpha(color, rng.randint(20, 40)))
        d.ellipse((x - r + 3, y - r + 3, x + r - 3, y + r - 3), fill=_alpha(_bright(color, 1.3), 10))
        if rng.random() > 0.4:
            ring_w = r + rng.randint(8, 15)
            ring_h = rng.randint(3, 6)
            d.ellipse((x - ring_w, y - ring_h, x + ring_w, y + ring_h), outline=_alpha(color, 30), width=1)
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((x - r * 2, y - r * 2, x + r * 2, y + r * 2), fill=_alpha(color, 8))
        glow = glow.filter(ImageFilter.GaussianBlur(10))
        ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


def draw_moon_crescent(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(1, 3)):
        x = rng.randint(60, w - 60)
        y = rng.randint(40, h - 80)
        r = rng.randint(15, 30)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.ellipse((x - r, y - r, x + r, y + r), fill=_alpha(color, 35))
        d.ellipse((x - r + 8, y - r - 3, x + r + 8, y + r - 3), fill=_alpha((0, 0, 0), 200))
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((x - r * 2, y - r * 2, x + r * 2, y + r * 2), fill=_alpha(color, 10))
        glow = glow.filter(ImageFilter.GaussianBlur(12))
        ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


def draw_nebula_blobs(img, colors, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(3, 6)):
        cx = rng.randint(100, w - 100)
        cy = rng.randint(50, h - 50)
        r = rng.randint(40, 120)
        c = rng.choice(colors)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        for i in range(r, 0, -3):
            t = i / r
            a = int((1 - t) * 20)
            if a < 1:
                continue
            ImageDraw.Draw(ov).ellipse((cx - i, cy - i, cx + i, cy + i), fill=_alpha(c, a))
        ov = ov.filter(ImageFilter.GaussianBlur(20))
        img = Image.alpha_composite(img, ov)
    return img


def draw_orbit_rings(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    cx, cy = w // 2 + rng.randint(-50, 50), h // 2 + rng.randint(-30, 30)
    for _ in range(rng.randint(2, 4)):
        r = rng.randint(60, 180)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        ring_h = rng.randint(3, 8)
        d.ellipse((cx - r, cy - ring_h, cx + r, cy + ring_h), outline=_alpha(color, rng.randint(15, 30)), width=1)
        planet_angle = rng.uniform(0, 2 * math.pi)
        px = cx + int(r * math.cos(planet_angle))
        py = cy + int(ring_h * math.sin(planet_angle))
        d.ellipse((px - 3, py - 3, px + 3, py + 3), fill=_alpha(color, 60))
        img = Image.alpha_composite(img, ov)
    return img


def draw_black_hole(img, color, seed=42):
    w, h = img.size
    cx, cy = w // 2 + 50, h // 2
    for r in range(80, 0, -2):
        t = r / 80
        a = int(t * 25)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).ellipse((cx - r, cy - r, cx + r, cy + r), fill=_alpha(color, a))
        ov = ov.filter(ImageFilter.GaussianBlur(4))
        img = Image.alpha_composite(img, ov)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse((cx - 15, cy - 15, cx + 15, cy + 15), fill=(0, 0, 0, 200))
    img = Image.alpha_composite(img, ov)
    return img


def draw_aurora_bands(img, colors, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for band in range(rng.randint(2, 4)):
        ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        c = colors[band % len(colors)]
        y_center = rng.randint(50, h - 50)
        for y in range(max(0, y_center - 50), min(h, y_center + 50)):
            t = 1.0 - abs(y - y_center) / 50.0
            a = int(t * 25)
            if a < 1:
                continue
            wave = int(15 * math.sin(y * 0.04 + band * 2))
            for x in range(0, w, 2):
                xa = int(10 * math.sin(x * 0.015 + y * 0.008 + band))
                ov.putpixel((min(w - 1, max(0, x + wave + xa)), y), _alpha(c, a))
        ov = ov.filter(ImageFilter.GaussianBlur(10))
        img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════════
# TECH / CIRCUIT / DIGITAL
# ══════════════════════════════════════════════

def draw_circuit(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    nodes = [(rng.randint(20, w - 20), rng.randint(20, h - 20)) for _ in range(rng.randint(10, 20))]
    for i, (nx, ny) in enumerate(nodes):
        d.rectangle((nx - 2, ny - 2, nx + 2, ny + 2), fill=_alpha(color, rng.randint(30, 60)))
        connections = rng.randint(1, 3)
        for _ in range(connections):
            j = rng.randint(0, len(nodes) - 1)
            if i != j:
                px, py = nodes[j]
                mid_x = nx if rng.random() > 0.5 else px
                mid_y = py if rng.random() > 0.5 else ny
                d.line((nx, ny, mid_x, ny), fill=_alpha(color, rng.randint(10, 25)), width=1)
                d.line((mid_x, ny, mid_x, py), fill=_alpha(color, rng.randint(10, 25)), width=1)
                d.line((mid_x, py, px, py), fill=_alpha(color, rng.randint(10, 25)), width=1)
    img = Image.alpha_composite(img, ov)
    return img


def draw_matrix_rain(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    font_size = rng.randint(8, 12)
    chars = "01アイウエオカキクケコ"
    for col in range(0, w, rng.randint(15, 25)):
        start_y = rng.randint(-50, h)
        length = rng.randint(5, 15)
        for i in range(length):
            y = start_y + i * (font_size + 2)
            if 0 <= y < h:
                a = max(0, 60 - i * 8)
                if a > 0:
                    d.text((col, y), rng.choice(chars), fill=_alpha(color, a))
    img = Image.alpha_composite(img, ov)
    return img


def draw_grid_neon(img, color, spacing=40, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for x in range(0, w, spacing):
        d.line((x, 0, x, h), fill=_alpha(color, rng.randint(5, 12)), width=1)
    for y in range(0, h, spacing):
        d.line((0, y, w, y), fill=_alpha(color, rng.randint(5, 12)), width=1)
    for x in range(0, w, spacing):
        for y in range(0, h, spacing):
            if rng.random() > 0.85:
                d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=_alpha(color, rng.randint(30, 80)))
    img = Image.alpha_composite(img, ov)
    return img


def draw_binary(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for _ in range(rng.randint(40, 80)):
        x = rng.randint(0, w - 10)
        y = rng.randint(0, h - 10)
        a = rng.randint(10, 35)
        d.text((x, y), rng.choice(["0", "1"]), fill=_alpha(color, a))
    img = Image.alpha_composite(img, ov)
    return img


def draw_hexagons(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(5, 12)):
        cx = rng.randint(30, w - 30)
        cy = rng.randint(30, h - 30)
        r = rng.randint(10, 25)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        points = []
        for i in range(6):
            angle = math.pi / 3 * i + math.pi / 6
            points.append((cx + int(r * math.cos(angle)), cy + int(r * math.sin(angle))))
        d.polygon(points, outline=_alpha(color, rng.randint(20, 45)))
        if rng.random() > 0.5:
            d.polygon(points, fill=_alpha(color, rng.randint(5, 12)))
        img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════════
# GEMS / CRYSTALS / MINERALS
# ══════════════════════════════════════════════

def draw_diamonds(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(4, 10)):
        cx = rng.randint(40, w - 40)
        cy = rng.randint(40, h - 40)
        sz = rng.randint(8, 20)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        top = (cx, cy - sz)
        left = (cx - sz, cy)
        right = (cx + sz, cy)
        bottom = (cx, cy + sz * 0.7)
        d.polygon([top, left, right, bottom], outline=_alpha(color, rng.randint(40, 80)))
        d.polygon([top, left, right, bottom], fill=_alpha(color, rng.randint(10, 25)))
        d.line((left, (cx, cy + 2)), fill=_alpha(_bright(color, 1.3), 30), width=1)
        d.line((right, (cx, cy + 2)), fill=_alpha(_bright(color, 1.3), 30), width=1)
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((cx - sz * 2, cy - sz * 2, cx + sz * 2, cy + sz * 2), fill=_alpha(color, 8))
        glow = glow.filter(ImageFilter.GaussianBlur(6))
        ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


def draw_crystals(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(4, 10)):
        x = rng.randint(30, w - 30)
        base_y = h - rng.randint(5, 20)
        height = rng.randint(20, 50)
        width = rng.randint(4, 10)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        top = (x, base_y - height)
        left = (x - width, base_y)
        right = (x + width, base_y)
        d.polygon([top, left, right], fill=_alpha(color, rng.randint(20, 45)))
        d.polygon([top, left, right], outline=_alpha(_bright(color, 1.3), rng.randint(30, 60)))
        mid = ((top[0] + left[0]) // 2, (top[1] + left[1]) // 2)
        d.line((top, mid), fill=_alpha(_bright(color, 1.5), 25), width=1)
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((x - width * 2, base_y - height * 2, x + width * 2, base_y + 5), fill=_alpha(color, 8))
        glow = glow.filter(ImageFilter.GaussianBlur(6))
        ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


def draw_gem_facets(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(3, 7)):
        cx = rng.randint(50, w - 50)
        cy = rng.randint(50, h - 50)
        r = rng.randint(10, 22)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        n = rng.choice([6, 8, 10])
        outer = []
        for i in range(n):
            angle = 2 * math.pi * i / n
            outer.append((cx + int(r * math.cos(angle)), cy + int(r * math.sin(angle))))
        d.polygon(outer, fill=_alpha(color, rng.randint(15, 30)))
        for i in range(n):
            d.line((outer[i], outer[(i + 1) % n]), fill=_alpha(_bright(color, 1.3), rng.randint(25, 50)), width=1)
            d.line((outer[i], (cx, cy)), fill=_alpha(color, rng.randint(8, 15)), width=1)
        d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=_alpha(_bright(color, 2), 60))
        img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════════
# ANIMALS / NATURE CREATURES
# ══════════════════════════════════════════════

def draw_paw_prints(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(4, 10)):
        cx = rng.randint(40, w - 40)
        cy = rng.randint(40, h - 40)
        sz = rng.randint(3, 7)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.ellipse((cx - sz, cy, cx + sz, cy + sz * 2), fill=_alpha(color, rng.randint(20, 40)))
        for dx, dy in [(-sz, -sz // 2), (sz, -sz // 2), (-sz // 2, -sz * 1.5), (sz // 2, -sz * 1.5)]:
            d.ellipse((cx + dx - sz // 2, cy + dy - sz // 2, cx + dx + sz // 2, cy + dy + sz // 2), fill=_alpha(color, rng.randint(15, 35)))
        img = Image.alpha_composite(img, ov)
    return img


def draw_butterflies(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(3, 8)):
        cx = rng.randint(40, w - 40)
        cy = rng.randint(40, h - 40)
        sz = rng.randint(6, 14)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        wing_c = _alpha(color, rng.randint(25, 50))
        d.ellipse((cx - sz * 1.5, cy - sz, cx - 1, cy + sz // 2), fill=wing_c)
        d.ellipse((cx + 1, cy - sz, cx + sz * 1.5, cy + sz // 2), fill=wing_c)
        d.ellipse((cx - sz, cy, cx - 1, cy + sz), fill=_alpha(color, rng.randint(20, 40)))
        d.ellipse((cx + 1, cy, cx + sz, cy + sz), fill=_alpha(color, rng.randint(20, 40)))
        d.line((cx, cy - sz, cx, cy + sz), fill=_alpha(_bright(color, 1.3), 50), width=1)
        img = Image.alpha_composite(img, ov)
    return img


def draw_birds(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(3, 8)):
        cx = rng.randint(30, w - 30)
        cy = rng.randint(20, h // 2)
        sz = rng.randint(4, 10)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        a = rng.randint(25, 50)
        d.line((cx - sz, cy + sz // 2, cx - sz // 3, cy, cx, cy + 2), fill=_alpha(color, a), width=1)
        d.line((cx, cy + 2, cx + sz // 3, cy, cx + sz, cy + sz // 2), fill=_alpha(color, a), width=1)
        img = Image.alpha_composite(img, ov)
    return img


def draw_spider_web(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    cx = rng.randint(w // 4, w * 3 // 4)
    cy = rng.randint(h // 4, h // 2)
    max_r = rng.randint(60, 120)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rings = rng.randint(3, 6)
    spokes = rng.randint(6, 10)
    for i in range(1, rings + 1):
        r = max_r * i / rings
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=_alpha(color, rng.randint(10, 20)), width=1)
    for s in range(spokes):
        angle = 2 * math.pi * s / spokes
        ex = cx + int(max_r * math.cos(angle))
        ey = cy + int(max_r * math.sin(angle))
        d.line((cx, cy, ex, ey), fill=_alpha(color, rng.randint(10, 20)), width=1)
    img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════════
# WEATHER / STORM
# ══════════════════════════════════════════════

def draw_lightning(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(2, 5)):
        x = rng.randint(w // 4, w * 3 // 4)
        y = rng.randint(10, h // 3)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        pts = [(x, y)]
        for _ in range(rng.randint(4, 7)):
            x += rng.randint(-20, 20)
            y += rng.randint(15, 35)
            pts.append((x, y))
        for i in range(len(pts) - 1):
            d.line((pts[i], pts[i + 1]), fill=_alpha(color, rng.randint(40, 90)), width=rng.randint(1, 3))
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        for pt in pts:
            ImageDraw.Draw(glow).ellipse((pt[0] - 8, pt[1] - 8, pt[0] + 8, pt[1] + 8), fill=_alpha(color, 10))
        glow = glow.filter(ImageFilter.GaussianBlur(8))
        ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


def draw_rain_drops(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for _ in range(rng.randint(40, 80)):
        x = rng.randint(0, w)
        y = rng.randint(0, h)
        length = rng.randint(8, 20)
        a = rng.randint(15, 40)
        d.line((x, y, x - 1, y + length), fill=_alpha(color, a), width=1)
    img = Image.alpha_composite(img, ov)
    return img


def draw_tornado_funnel(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    cx = w // 2 + rng.randint(-50, 50)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(20, h, 3):
        t = y / h
        half_w = int(10 + t * 80)
        wobble = int(5 * math.sin(y * 0.05))
        a = int(15 + t * 10)
        d.ellipse((cx + wobble - half_w, y - 2, cx + wobble + half_w, y + 2), fill=_alpha(color, a))
    img = Image.alpha_composite(img, ov)
    return img


def draw_clouds(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(3, 6)):
        cx = rng.randint(50, w - 50)
        cy = rng.randint(20, h // 3)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for _ in range(rng.randint(3, 6)):
            r = rng.randint(15, 35)
            ox = rng.randint(-25, 25)
            oy = rng.randint(-10, 10)
            d.ellipse((cx + ox - r, cy + oy - r // 2, cx + ox + r, cy + oy + r // 2), fill=_alpha(color, rng.randint(10, 25)))
        img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════════
# MYTHOLOGY / MEDIEVAL
# ══════════════════════════════════════════════

def draw_sword(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(1, 3)):
        cx = rng.randint(w // 4, w * 3 // 4)
        cy = rng.randint(h // 4, h * 3 // 4)
        size = rng.randint(20, 45)
        angle = rng.uniform(-0.5, 0.5)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        def rot(px, py):
            return (cx + int(px * cos_a - py * sin_a), cy + int(px * sin_a + py * cos_a))
        d.line((rot(0, -size), rot(0, size)), fill=_alpha(color, rng.randint(30, 60)), width=2)
        d.line((rot(-size // 3, 0), rot(size // 3, 0)), fill=_alpha(color, rng.randint(30, 60)), width=2)
        d.ellipse((rot(0, -size)[0] - 2, rot(0, -size)[1] - 2, rot(0, -size)[0] + 2, rot(0, -size)[1] + 2), fill=_alpha(_bright(color, 1.5), 50))
        img = Image.alpha_composite(img, ov)
    return img


def draw_shield(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(1, 3)):
        cx = rng.randint(w // 4, w * 3 // 4)
        cy = rng.randint(h // 4, h * 3 // 4)
        sz = rng.randint(15, 30)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        top = (cx, cy - sz)
        left = (cx - sz, cy - sz // 2)
        right = (cx + sz, cy - sz // 2)
        bottom = (cx, cy + sz)
        d.polygon([top, left, bottom, right], fill=_alpha(color, rng.randint(15, 30)))
        d.polygon([top, left, bottom, right], outline=_alpha(_bright(color, 1.3), rng.randint(30, 50)))
        d.line((left, right), fill=_alpha(_bright(color, 1.3), 20), width=1)
        d.line((top, bottom), fill=_alpha(_bright(color, 1.3), 20), width=1)
        img = Image.alpha_composite(img, ov)
    return img


def draw_crown(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(1, 2)):
        cx = rng.randint(w // 4, w * 3 // 4)
        cy = rng.randint(h // 4, h * 3 // 4)
        sz = rng.randint(12, 25)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        pts = [
            (cx - sz, cy + sz // 2),
            (cx - sz, cy - sz // 4),
            (cx - sz // 2, cy + sz // 4),
            (cx - sz // 4, cy - sz),
            (cx, cy + sz // 6),
            (cx + sz // 4, cy - sz),
            (cx + sz // 2, cy + sz // 4),
            (cx + sz, cy - sz // 4),
            (cx + sz, cy + sz // 2),
        ]
        d.polygon(pts, fill=_alpha(color, rng.randint(25, 45)))
        d.polygon(pts, outline=_alpha(_bright(color, 1.3), rng.randint(40, 70)))
        for pt in [(cx - sz // 4, cy - sz), (cx, cy + sz // 6), (cx + sz // 4, cy - sz)]:
            d.ellipse((pt[0] - 2, pt[1] - 2, pt[0] + 2, pt[1] + 2), fill=_alpha(_bright(color, 2), 60))
        img = Image.alpha_composite(img, ov)
    return img


def draw_skull(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(2, 5)):
        cx = rng.randint(50, w - 50)
        cy = rng.randint(50, h - 50)
        sz = rng.randint(8, 16)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.ellipse((cx - sz, cy - sz, cx + sz, cy + sz // 2), fill=_alpha(color, rng.randint(15, 30)))
        d.ellipse((cx - sz // 2, cy + sz // 4, cx - sz // 6, cy + sz // 2), fill=(0, 0, 0, 80))
        d.ellipse((cx + sz // 6, cy + sz // 4, cx + sz // 2, cy + sz // 2), fill=(0, 0, 0, 80))
        d.line((cx - 2, cy + sz // 3, cx + 2, cy + sz // 3), fill=_alpha(color, rng.randint(20, 40)), width=1)
        img = Image.alpha_composite(img, ov)
    return img


def draw_ankh(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    cx = rng.randint(w // 4, w * 3 // 4)
    cy = rng.randint(h // 4, h * 3 // 4)
    sz = rng.randint(15, 30)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    r = sz // 3
    d.ellipse((cx - r, cy - sz // 2 - r, cx + r, cy - sz // 2 + r), outline=_alpha(color, 40), width=2)
    d.line((cx, cy - sz // 2 + r, cx, cy + sz), fill=_alpha(color, 40), width=2)
    d.line((cx - sz // 3, cy - sz // 6, cx + sz // 3, cy - sz // 6), fill=_alpha(color, 40), width=2)
    img = Image.alpha_composite(img, ov)
    return img


def draw_rune(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(4, 8)):
        cx = rng.randint(30, w - 30)
        cy = rng.randint(30, h - 30)
        sz = rng.randint(6, 14)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        lines = rng.randint(2, 4)
        for _ in range(lines):
            angle = rng.uniform(0, 2 * math.pi)
            ex = cx + int(sz * math.cos(angle))
            ey = cy + int(sz * math.sin(angle))
            d.line((cx, cy, ex, ey), fill=_alpha(color, rng.randint(25, 50)), width=2)
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((cx - sz * 2, cy - sz * 2, cx + sz * 2, cy + sz * 2), fill=_alpha(color, 8))
        glow = glow.filter(ImageFilter.GaussianBlur(5))
        ov = Image.alpha_composite(ov, glow)
        img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════════
# FOOD / DRINKS
# ══════════════════════════════════════════════

def draw_coffee_cup(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(2, 4)):
        cx = rng.randint(60, w - 60)
        cy = rng.randint(h // 3, h - 40)
        sz = rng.randint(10, 18)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.rounded_rectangle((cx - sz, cy - sz, cx + sz, cy + sz), radius=3, fill=_alpha(color, rng.randint(15, 30)), outline=_alpha(color, 30))
        d.arc((cx + sz - 3, cy - sz // 2, cx + sz + sz // 2, cy + sz // 2), -60, 60, fill=_alpha(color, 25), width=2)
        for s in range(3):
            sy = cy - sz - 5 - s * 6
            d.arc((cx - 5, sy - 4, cx + 5, sy + 4), 180, 360, fill=_alpha(color, 20 - s * 5), width=1)
        img = Image.alpha_composite(img, ov)
    return img


def draw_fruit(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(4, 8)):
        cx = rng.randint(30, w - 30)
        cy = rng.randint(30, h - 30)
        r = rng.randint(6, 14)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=_alpha(color, rng.randint(20, 40)))
        d.ellipse((cx - r + 2, cy - r + 2, cx - r + 6, cy - r + 6), fill=_alpha(_bright(color, 1.5), 30))
        d.line((cx, cy - r, cx + 2, cy - r - 5), fill=_alpha(_dim(color, 0.7), 40), width=1)
        img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════════
# GEOMETRIC / ABSTRACT
# ══════════════════════════════════════════════

def draw_triangles(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(5, 12)):
        cx = rng.randint(20, w - 20)
        cy = rng.randint(20, h - 20)
        sz = rng.randint(8, 25)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        angle = rng.uniform(0, 2 * math.pi)
        pts = []
        for i in range(3):
            a = angle + 2 * math.pi * i / 3
            pts.append((cx + int(sz * math.cos(a)), cy + int(sz * math.sin(a))))
        d.polygon(pts, outline=_alpha(color, rng.randint(20, 45)))
        if rng.random() > 0.5:
            d.polygon(pts, fill=_alpha(color, rng.randint(5, 12)))
        img = Image.alpha_composite(img, ov)
    return img


def draw_circles_sacred(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    cx = w // 2 + rng.randint(-30, 30)
    cy = h // 2 + rng.randint(-20, 20)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(1, rng.randint(3, 6)):
        r = i * rng.randint(20, 40)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=_alpha(color, rng.randint(10, 25)), width=1)
    for i in range(6):
        angle = math.pi / 3 * i
        px = cx + int(rng.randint(30, 60) * math.cos(angle))
        py = cy + int(rng.randint(30, 60) * math.sin(angle))
        d.line((cx, cy, px, py), fill=_alpha(color, 10), width=1)
    img = Image.alpha_composite(img, ov)
    return img


def draw_spiral(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    cx = rng.randint(w // 4, w * 3 // 4)
    cy = rng.randint(h // 4, h * 3 // 4)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    pts = []
    for t in range(0, 720, 5):
        angle = math.radians(t)
        r = t * 0.08
        x = cx + int(r * math.cos(angle))
        y = cy + int(r * math.sin(angle))
        pts.append((x, y))
    for i in range(len(pts) - 1):
        a = max(0, 30 - i // 20)
        if a > 0:
            d.line((pts[i], pts[i + 1]), fill=_alpha(color, a), width=1)
    img = Image.alpha_composite(img, ov)
    return img


def draw_mandala(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    cx = w // 2 + rng.randint(-30, 30)
    cy = h // 2 + rng.randint(-20, 20)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    petals = rng.choice([8, 12, 16])
    for ring in range(1, 4):
        r = ring * rng.randint(15, 25)
        for p in range(petals):
            angle = 2 * math.pi * p / petals + ring * 0.2
            px = cx + int(r * math.cos(angle))
            py = cy + int(r * math.sin(angle))
            pr = rng.randint(3, 8)
            d.ellipse((px - pr, py - pr, px + pr, py + pr), outline=_alpha(color, rng.randint(15, 30)))
            d.line((px, py, cx + int((r - 15) * math.cos(angle)), cy + int((r - 15) * math.sin(angle))), fill=_alpha(color, 10), width=1)
    d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=_alpha(color, 30))
    img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════════
# SNAKE / SERPENT
# ══════════════════════════════════════════════

def draw_snake(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(2, 5)):
        x = rng.randint(30, w - 30)
        y = rng.randint(h // 3, h - 30)
        sz = rng.randint(3, 6)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        pts = [(x, y)]
        cx, cy = x, y
        for _ in range(rng.randint(6, 12)):
            cx += rng.randint(-15, 15)
            cy += rng.randint(-10, 10)
            pts.append((cx, cy))
        for i in range(len(pts) - 1):
            d.line((pts[i], pts[i + 1]), fill=_alpha(color, rng.randint(25, 50)), width=sz)
        d.ellipse((x - sz, y - sz, x + sz, y + sz), fill=_alpha(color, 50))
        img = Image.alpha_composite(img, ov)
    return img


def draw_prism(img, color, seed=42):
    rng = random.Random(seed)
    w, h = img.size
    for _ in range(rng.randint(3, 6)):
        cx = rng.randint(50, w - 50)
        cy = rng.randint(50, h - 50)
        sz = rng.randint(12, 25)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        pts = [(cx, cy - sz), (cx - sz, cy + sz // 2), (cx + sz, cy + sz // 2)]
        d.polygon(pts, outline=_alpha(color, rng.randint(30, 60)))
        rainbow = [(255, 50, 50), (255, 165, 0), (255, 255, 0), (0, 200, 0), (0, 100, 255), (130, 0, 255)]
        for i, rc in enumerate(rainbow):
            y1 = cy - sz + (sz * 1.5) * i / len(rainbow)
            x1 = cx + sz + 5 + i * 4
            d.line((x1, int(y1), x1 + 15, int(y1 + 5)), fill=_alpha(rc, 25), width=1)
        img = Image.alpha_composite(img, ov)
    return img


# ══════════════════════════════════════════════
# THEME MAPPING
# ══════════════════════════════════════════════

THEME_DRAWING_MAP = {
    # CACTI / DESERT
    "cacto": draw_cacti, "mandacaru": draw_cacti, "oasis": draw_cacti,
    "deserto_glacial": draw_cacti, "areia": draw_grass,

    # TREES / FOREST
    "floresta": draw_trees, "floresta_encantada": draw_trees, "floresta_sombria": draw_trees,
    "musgo": draw_grass, "tropical": draw_trees, "bambu": draw_bamboo,
    "aloe": draw_grass, "verde_esmeralda": draw_trees, "jade": draw_trees,
    "peridot": draw_grass, "aventurina": draw_trees,

    # LEAVES / PLANTS
    "madeira": draw_leaves, "ipe": draw_flowers, "primavera": draw_flowers,
    "outono": draw_leaves, "borboleta": draw_butterflies,

    # VINES
    "druida": draw_vine, "elfico": draw_vine, "neve_sakura": draw_flowers,

    # FLOWERS
    "sakura": draw_flowers, "sakura_noite": draw_flowers, "rosa_champagne": draw_flowers,

    # MUSHROOMS
    "feiticeiro": draw_mushrooms, "necromante": draw_mushrooms,

    # FIRE / EMBER
    "fenix": draw_flames, "vulcanico": draw_flames, "lava": draw_lava_cracks,
    "dragao": draw_flames, "dragao_fogo": draw_flames, "infernal": draw_flames,
    "big_bang": draw_sparks, "supernova": draw_sparks, "supernova_v2": draw_sparks,
    "big_crunch": draw_sparks, "entropia": draw_sparks,
    "demonio": draw_flames, "hades": draw_embers, "lua_sangue": draw_embers,
    "crimson": draw_embers, "ember": draw_embers,

    # LAVA / VOLCANIC
    "vulcao": draw_lava_cracks, "quasar": draw_sparks,

    # WATER / OCEAN
    "oceano": draw_waves, "oceano_profundo": draw_bubbles, "oceano_lunar": draw_waves,
    "poseidon": draw_waves, "tsunami": draw_waves, "aquamarina": draw_bubbles,
    "turquesa": draw_bubbles, "turquesa_profunda": draw_bubbles,
    "boto_rosa": draw_fish, "coral": draw_coral, "coral_vibrante": draw_coral,

    # SEA LIFE
    "tartaruga": draw_shell, "arara": draw_birds,

    # SEAWEED
    "algas": draw_seaweed,

    # ICE / SNOW
    "geleira": draw_ice_crystals, "artico": draw_snowflakes, "inverno": draw_snowflakes,
    "geada": draw_frost, "tempestade_gelo": draw_ice_crystals, "neve_sakura": draw_snowflakes,

    # SPACE / COSMIC
    "galaxia": draw_constellation, "estrela": draw_constellation, "lua": draw_moon_crescent,
    "buraco_negro": draw_black_hole, "nebulosa": draw_nebula_blobs,
    "pulsar": draw_sparks, "via_lactea": draw_nebula_blobs, "estrela_negra": draw_constellation,
    "ceu_estrelado": draw_constellation, "luz_estrelas": draw_constellation,
    "cosmico": draw_nebula_blobs, "cosmico_v2": draw_nebula_blobs, "cosmica_infinita": draw_nebula_blobs,
    "wormhole": draw_spiral, "magnetar": draw_orbit_rings,
    "anoes_brancos": draw_planets, "buraco_branco": draw_sparks,
    "meia_noite": draw_moon_crescent,

    # AURORA
    "aurora": draw_aurora_bands, "aurora_boreal": draw_aurora_bands,

    # ORBIT
    "gravitacional": draw_orbit_rings, "cometa": draw_orbit_rings,

    # NEBULA COLORS
    "nebulosa": draw_nebula_blobs,

    # TECH / CIRCUIT
    "cyberpunk": draw_circuit, "holograma": draw_circuit, "cyborg": draw_hexagons,
    "digital": draw_matrix_rain, "matrix": draw_matrix_rain, "glitch": draw_binary,
    "nanotech": draw_hexagons, "quantico": draw_hexagons, "sonico": draw_grid_neon,
    "pixel": draw_grid_neon,

    # CRYSTALS / GEMS
    "cristal": draw_crystals, "quartzo": draw_crystals, "diamante": draw_diamonds,
    "diamante_negro": draw_diamonds, "opala": draw_gem_facets,
    "esmeralda": draw_gem_facets, "rubi_bg": draw_gem_facets, "safira_bg": draw_gem_facets,
    "ametista_bg": draw_gem_facets, "berilo": draw_crystals, "rubelita": draw_gem_facets,
    "alexandrita": draw_gem_facets, "topazio_imperial": draw_gem_facets,
    "granada": draw_gem_facets, "granada_v2": draw_gem_facets,
    "turmalina": draw_gem_facets, "zirconio": draw_crystals,
    "lapis_lazuli": draw_gem_facets, "obsidiana_arcoiris": draw_crystals,
    "cristal_arcoiris": draw_crystals, "perola": draw_bubbles,
    "perola_imperial": draw_bubbles,

    # ANIMALS
    "tartaruga": draw_shell, "coruja_noturna": draw_birds,
    "lobo_guara": draw_paw_prints, "onca": draw_paw_prints,

    # BUTTERFLIES
    "neon_rosa": draw_butterflies, "prisma": draw_butterflies,

    # SPIDER WEB
    "labirinto": draw_spider_web, "cripta": draw_spider_web,

    # WEATHER
    "relampago": draw_lightning, "trovao": draw_lightning, "tempestade": draw_lightning,
    "tempestade_neon": draw_lightning,
    "monsoon": draw_rain_drops, "tornada": draw_tornado_funnel,
    "tufao": draw_tornado_funnel,
    "nevoa_eterna": draw_clouds, "neblina": draw_clouds,

    # SHIELD / WEAPONS
    "samurai": draw_sword, "viking": draw_shield, "ninja": draw_sword,
    "valhalla": draw_sword, "paladino": draw_shield,

    # CROWN
    "royal": draw_crown, "imperial": draw_crown, "supremo": draw_crown,

    # SKULLS
    "necromante": draw_skull, "hades": draw_skull, "cripta": draw_skull,
    "sombras_eternas": draw_skull,

    # ANKH / RUNES
    "egipcio": draw_ankh, "reliquia": draw_ankh, "divino": draw_rune,
    "divino_v2": draw_rune, "ascensao": draw_rune, "ascendente": draw_rune,
    "eterno": draw_rune, "eterno_v2": draw_rune, "infinito": draw_spiral,
    "infinito_v2": draw_spiral, "absoluto": draw_spiral, "ultima": draw_spiral,

    # MYTHOLOGY
    "zeus": draw_lightning, "poseidon": draw_waves, "athena": draw_shield,
    "medusa": draw_snake, "hydra": draw_snake, "mitico": draw_crown,
    "lendario": draw_crown, "tita": draw_sword, "colossal": draw_shield,

    # FOOD
    "cafe": draw_coffee_cup, "cafe_eterno": draw_coffee_cup,
    "cha": draw_coffee_cup, "chocolate": draw_fruit, "chocolate_rubro": draw_fruit,
    "mel": draw_fruit, "frutas_tropicais": draw_fruit, "melancia": draw_fruit,
    "cerveja": draw_coffee_cup, "sake": draw_coffee_cup, "vinho": draw_coffee_cup,
    "vinho_tinto": draw_coffee_cup, "chimarra": draw_coffee_cup,
    "licor_estelar": draw_coffee_cup, "caramelo": draw_fruit, "canela_dourada": draw_sparks,

    # GEOMETRIC
    "fractal": draw_mandala, "paradoxo": draw_spiral, "vortex": draw_spiral,
    "dimensional": draw_spiral, "arcana": draw_mandala,

    # ABSTRACT CIRCLES
    "neon": draw_grid_neon, "neon_v2": draw_grid_neon, "neon_dreams": draw_grid_neon,
    "toxico": draw_grid_neon,

    # METALS
    "ferro": draw_hexagons, "prata": draw_hexagons, "platina": draw_hexagons,
    "niquel": draw_hexagons, "cobre": draw_hexagons, "bronze": draw_hexagons,
    "latao": draw_hexagons, "titanio": draw_hexagons, "cobalto": draw_hexagons,
    "tungstenio": draw_hexagons, "osmio": draw_hexagons, "iridio": draw_hexagons,
    "cromo": draw_hexagons, "mercurio": draw_hexagons, "ouro_liquido": draw_sparks,
    "platina_negra": draw_hexagons, "ouro_rosa": draw_flowers,

    # RETRO / VAPORWAVE
    "retro": draw_grid_neon, "vaporwave": draw_grid_neon, "synthwave": draw_grid_neon,
    "lofi": draw_grid_neon,

    # NOIR / ART DECO
    "noir": draw_rain_drops, "art_deco": draw_triangles, "steampunk": draw_hexagons,

    # DARK / SHADOW
    "abismo": draw_spiral, "eclipse": draw_moon_crescent, "obsidiana": draw_spiral,
    "obsidiana_v2": draw_spiral, "vazio": draw_spiral, "shadow": draw_spiral,
    "void": draw_spiral, "void_border": draw_spiral,
    "carvao": draw_triangles, "turfa": draw_triangles, "pedra": draw_triangles,

    # MUSIC
    "onda_sonora": draw_grid_neon, "resonancia": draw_grid_neon,
    "interferencia": draw_grid_neon, "difracao": draw_prism,
    "polaridade": draw_hexagons,

    # DEFAULT
    "padrao": draw_triangles,
    "agate": draw_crystals,
    "amarelo_solar": draw_sparks,
    "ambra": draw_embers,
    "amethyst": draw_crystals,
    "anjo": draw_constellation,
    "arco_iris": draw_prism,
    "argila": draw_cacti,
    "azul_profundo": draw_waves,
    "blood": draw_lava_cracks,
    "branco_perola": draw_diamonds,
    "carmesim": draw_flames,
    "celestial": draw_constellation,
    "cherry": draw_flowers,
    "chrome": draw_diamonds,
    "cinza_prata": draw_hexagons,
    "citrino": draw_crystals,
    "copper_border": draw_lava_cracks,
    "cosmic": draw_orbit_rings,
    "crimson_border": draw_flames,
    "cromado": draw_hexagons,
    "cyber_goth": draw_circuit,
    "deep_sea": draw_bubbles,
    "default": draw_diamonds,
    "diamond": draw_diamonds,
    "dourado": draw_crown,
    "dragon": draw_flames,
    "emerald": draw_crystals,
    "emerald_border": draw_crystals,
    "esfinge": draw_triangles,
    "esmeralda_colombiana": draw_crystals,
    "espiral": draw_spiral,
    "fantasma": draw_spider_web,
    "feiteiceiro": draw_mandala,
    "fire": draw_flames,
    "frost": draw_frost,
    "galaxy": draw_planets,
    "gold": draw_crown,
    "golden_dust": draw_sparks,
    "granito": draw_hexagons,
    "ice": draw_ice_crystals,
    "jade_border": draw_crystals,
    "jade_imperial": draw_crystals,
    "japones": draw_flowers,
    "lavender": draw_flowers,
    "lila_mistico": draw_mandala,
    "marmore": draw_hexagons,
    "metal": draw_hexagons,
    "moonlight": draw_moon_crescent,
    "neon_cyan": draw_grid_neon,
    "neon_green": draw_grid_neon,
    "neon_pink": draw_grid_neon,
    "neon_purple": draw_grid_neon,
    "neon_yellow": draw_grid_neon,
    "niobio": draw_circuit,
    "obsidian": draw_skull,
    "ocean": draw_waves,
    "piramide": draw_triangles,
    "planicie": draw_grass,
    "platinum": draw_diamonds,
    "portal": draw_spiral,
    "rainbow": draw_prism,
    "roxo_real": draw_crown,
    "rubi_birman": draw_flames,
    "ruby": draw_flames,
    "safira_imperial": draw_crystals,
    "sakura_border": draw_flowers,
    "sangue_sagrado": draw_ankh,
    "sapphire": draw_crystals,
    "seda": draw_butterflies,
    "sinestesia": draw_mandala,
    "sol_nascente": draw_sparks,
    "solar_flare": draw_sparks,
    "terremoto": draw_triangles,
    "topazio": draw_crystals,
    "toxic": draw_hexagons,
    "troia": draw_sword,
    "tucano": draw_birds,
    "vanadio": draw_crystals,
    "veludo": draw_butterflies,
    "verao": draw_sparks,
    "vermelho_sangue": draw_flames,
}


def apply_theme_art(img, theme_key, border_color, accent_color, seed=42):
    draw_fn = THEME_DRAWING_MAP.get(theme_key)
    if draw_fn:
        try:
            img = draw_fn(img, border_color, seed=seed)
            img = draw_fn(img, accent_color, seed=seed + 1000)
        except Exception:
            pass
    return img
