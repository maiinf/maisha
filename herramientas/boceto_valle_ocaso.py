"""Boceto de atmósfera del VALLE DEL OCASO (mundo 4, el último):
atardecer eterno (cielo malva-ámbar-púrpura con el sol detenido a ras de horizonte),
Jioni (la Ciudad de los Faroles de los zorros fénec mbweha), obeliscos proyectando
sombras largas que hacen de puente y Maisha con el Cetro del Nexo despierto.
Sale en documentacion/boceto_valle_ocaso.png (760x320)."""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 760, 320


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def main():
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    rgb = np.zeros((H, W, 3), dtype=float)

    # Cielo de atardecer eterno: índigo/púrpura arriba -> malva -> coral -> ámbar dorado en el horizonte
    paradas = [
        (0.00, (24, 14, 48)),
        (0.28, (64, 28, 86)),
        (0.48, (132, 48, 96)),
        (0.62, (214, 96, 78)),
        (0.74, (248, 174, 86)),
        (0.80, (255, 224, 140)),
    ]
    t_cielo = np.clip(ys / (H * 0.78), 0.0, 1.0)
    for (p0, c0), (p1, c1) in zip(paradas, paradas[1:]):
        m = (t_cielo >= p0) & (t_cielo <= p1)
        f = np.where(m, (t_cielo - p0) / max(1e-5, p1 - p0), 0.0)[..., None]
        rgb = np.where(m[..., None], np.array(c0) * (1.0 - f) + np.array(c1) * f, rgb)

    # El Sol Detenido a ras de horizonte (centro-derecha, gigante y cálido)
    sx, sy = 518.0, 176.0
    d_sol = np.hypot(xs - sx, ys - sy)
    halo1 = np.exp(-((d_sol / 145.0) ** 2))
    halo2 = np.exp(-((d_sol / 56.0) ** 2))
    rgb += halo1[..., None] * np.array([62.0, 34.0, 18.0])
    rgb += halo2[..., None] * np.array([95.0, 68.0, 35.0])
    # Disco solar con anillos sutiles de reloj detenido
    en_sol = d_sol < 42.0
    rgb[en_sol] = np.array([255.0, 236.0, 172.0])
    borde_sol = (d_sol >= 40.5) & (d_sol < 43.0)
    rgb[borde_sol] = np.array([255.0, 198.0, 96.0])

    # Estrellas tímidas asomando solo en la franja más alta (la noche que no consigue bajar)
    rng = random.Random(42)
    for _ in range(55):
        ex = rng.randint(10, W - 10)
        ey = rng.randint(8, 88)
        br = rng.uniform(0.45, 0.95) * (1.0 - ey / 96.0)
        rgb[ey, ex] = np.clip(rgb[ey, ex] + np.array([255, 240, 210]) * br, 0, 255)

    # Cordilleras escalonadas del Valle del Ocaso (3 planos de profundidad)
    def silueta(x_arr, base, amp1, f1, ph1, amp2, f2, ph2):
        return base - amp1 * np.sin(x_arr * f1 + ph1) - amp2 * np.abs(np.cos(x_arr * f2 + ph2))

    # Plano lejano (malva translúcido)
    m1 = ys > silueta(xs, 192, 18, 0.011, 0.4, 22, 0.025, 1.2)
    rgb[m1] = np.array([94, 42, 78])
    # Plano medio (púrpura sombra con filo cálido arriba)
    h2 = silueta(xs, 212, 16, 0.015, 2.1, 18, 0.032, 0.3)
    m2 = ys > h2
    rgb[m2] = np.array([58, 26, 62])
    filo2 = (ys > h2) & (ys <= h2 + 2.5)
    rgb[filo2] = np.array([232, 138, 84])

    # Suelo del primer plano: arena crepuscular de dunas doradas/malva y barranco de sombra
    h_suelo = 232 + 9 * np.sin(xs * 0.016 + 0.8) + 4 * np.cos(xs * 0.04)
    en_suelo = ys >= h_suelo
    t_s = np.clip((ys - 224.0) / 96.0, 0.0, 1.0)
    col_suelo = np.array([154, 86, 72]) * (1.0 - t_s[..., None]) + np.array([58, 28, 56]) * t_s[..., None]
    # Grano de arena sutil
    grano = (np.sin(xs * 1.9 + ys * 0.7) * np.cos(xs * 0.8 - ys * 1.4)) * 8.0
    rgb = np.where(en_suelo[..., None], np.clip(col_suelo + grano[..., None], 0, 255), rgb)

    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")

    # Anillos de reloj detenido alrededor del sol (sutiles, en bronce/oro)
    for r_aro, a_aro in [(52, 95), (66, 55)]:
        d.ellipse([sx - r_aro, sy - r_aro, sx + r_aro, sy + r_aro], outline=(245, 198, 118, a_aro), width=2)
    for k in range(12):
        ang = k * math.tau / 12.0
        p0 = (sx + math.cos(ang) * 48, sy + math.sin(ang) * 48)
        p1 = (sx + math.cos(ang) * 56, sy + math.sin(ang) * 56)
        d.line([p0, p1], fill=(255, 214, 130, 120), width=2)

    # JIONI, LA CIUDAD DE LOS FAROLES (silueta en terrazas a la derecha-centro bajo el sol)
    terrazas = [
        (360, 196, 650, 232, (46, 22, 54, 255)),
        (395, 178, 620, 212, (62, 28, 66, 255)),
        (445, 162, 578, 194, (78, 34, 72, 255)),
    ]
    for x0, y0, x1, y1, col in terrazas:
        d.rectangle([x0, y0, x1, y1], fill=col)
        d.line([(x0, y0), (x1, y0)], fill=(238, 152, 88, 220), width=2)

    # Torres con cúpulas de adobe/latón y arcos con faroles colgantes
    torres = [
        (382, 162, 28, 44), (422, 148, 32, 50), (464, 138, 26, 46),
        (502, 124, 34, 62), (552, 144, 30, 48), (594, 158, 28, 46), (630, 170, 24, 42)
    ]
    for tx, ty, tw, th in torres:
        d.rectangle([tx, ty, tx + tw, ty + th], fill=(42, 20, 52, 255))
        d.pieslice([tx - 2, ty - tw // 2, tx + tw + 2, ty + tw // 2], 180, 360, fill=(68, 32, 74, 255))
        d.arc([tx - 2, ty - tw // 2, tx + tw + 2, ty + tw // 2], 200, 340, fill=(246, 178, 96, 210), width=2)
        # Ventanitas cálidas
        for vy in range(ty + 8, ty + th - 10, 12):
            d.rectangle([tx + tw // 2 - 3, vy, tx + tw // 2 + 3, vy + 6], fill=(255, 220, 128, 240))
        # Aguja + farolito en la punta
        d.line([(tx + tw // 2, ty - tw // 2), (tx + tw // 2, ty - tw // 2 - 10)], fill=(230, 180, 100, 220), width=2)
        d.ellipse([tx + tw // 2 - 3, ty - tw // 2 - 13, tx + tw // 2 + 3, ty - tw // 2 - 7], fill=(255, 234, 150, 255))

    # Gran Reloj Solar central de Jioni (arco dorado sobre la torre central)
    d.arc([496, 102, 542, 148], 180, 360, fill=(255, 216, 126, 240), width=3)
    d.line([(519, 102), (519, 126)], fill=(255, 228, 156, 255), width=2)

    # Guirnaldas de faroles entre terrazas
    for fx in range(374, 646, 22):
        fy = 198 + int(6 * math.sin(fx * 0.08))
        d.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], fill=(255, 190, 92, 65))
        d.ellipse([fx - 2, fy - 2, fx + 2, fy + 2], fill=(255, 232, 150, 240))

    # Grieta / abismo de penumbra en primer plano que se cruza por una SOMBRA LARGA SÓLIDA
    abismo = [(240, 244), (362, 238), (430, 320), (195, 320)]
    d.polygon(abismo, fill=(18, 9, 30, 255))
    d.line([(240, 244), (195, 320)], fill=(122, 62, 92, 200), width=2)
    d.line([(362, 238), (430, 320)], fill=(224, 134, 84, 200), width=2)

    # Obelisco de piedra en el borde derecho proyectando una SOMBRA LARGA SÓLIDA sobre el abismo
    obx, oby = 382, 242
    d.polygon([(obx - 10, oby + 4), (obx - 6, oby - 58), (obx, oby - 70), (obx + 6, oby - 58), (obx + 10, oby + 4)],
              fill=(54, 30, 62, 255))
    d.line([(obx + 6, oby - 58), (obx + 10, oby + 4)], fill=(248, 180, 102, 230), width=2)
    # Runas doradas del reloj en el obelisco
    for ry in range(oby - 46, oby - 6, 12):
        d.ellipse([obx - 2, ry - 2, obx + 2, ry + 2], fill=(255, 218, 124, 220))

    # LA SOMBRA-PUENTE larga hacia la izquierda (sólida, malva profundo con borde luminoso)
    puente_sombra = [(obx - 10, oby + 4), (obx + 6, oby + 12), (222, 286), (206, 272)]
    d.polygon(puente_sombra, fill=(36, 18, 58, 245))
    d.line([(obx - 10, oby + 4), (206, 272)], fill=(240, 186, 104, 215), width=2)
    d.line([(obx + 6, oby + 12), (222, 286)], fill=(176, 118, 224, 190), width=2)
    # Brillos suaves en el puente de sombra (indican que se puede pisar)
    for k in range(1, 6):
        px = obx - 2 - k * 28
        py = oby + 8 + k * 12
        d.ellipse([px - 4, py - 2, px + 4, py + 2], fill=(220, 176, 255, 110))

    # Farol alto de los zorros fénec en primer plano a la izquierda
    lx, ly = 86, 258
    d.line([(lx, ly), (lx, ly - 52)], fill=(46, 26, 44, 255), width=3)
    d.arc([lx - 2, ly - 60, lx + 20, ly - 40], 180, 360, fill=(214, 166, 92, 240), width=2)
    # Halo del farol
    d.ellipse([lx + 4, ly - 58, lx + 34, ly - 28], fill=(255, 200, 96, 55))
    d.ellipse([lx + 11, ly - 51, lx + 27, ly - 35], fill=(255, 220, 120, 110))
    d.rectangle([lx + 15, ly - 48, lx + 23, ly - 38], fill=(255, 242, 180, 255), outline=(140, 88, 38, 255))

    # Maisha en primer plano a la izquierda con el Cetro del Nexo despierto (brote + cristal azul-oro)
    mx, my = 152, 264
    d.ellipse([mx - 14, my + 8, mx + 14, my + 16], fill=(22, 10, 34, 170))
    # Halo cálido alrededor de Maisha
    d.ellipse([mx - 24, my - 30, mx + 24, my + 16], fill=(255, 212, 124, 38))
    # Cuerpo y capa
    d.rectangle([mx - 8, my - 6, mx + 8, my + 10], fill=(238, 208, 146, 255))
    d.polygon([(mx - 10, my - 4), (mx + 2, my - 4), (mx - 13, my + 9), (mx - 6, my + 9)], fill=(122, 68, 128, 255))
    # Cabeza redonda característica de Maisha
    d.ellipse([mx - 11, my - 24, mx + 11, my - 3], fill=(250, 224, 162, 255))
    d.rectangle([mx + 3, my - 15, mx + 5, my - 11], fill=(38, 22, 28, 255))
    # Brote verde en la cabeza
    d.line([(mx, my - 24), (mx, my - 32)], fill=(76, 172, 68, 255), width=2)
    d.ellipse([mx - 8, my - 35, mx, my - 29], fill=(104, 212, 82, 255))
    d.ellipse([mx, my - 36, mx + 9, my - 30], fill=(134, 230, 96, 255))
    # Cetro del Nexo despierto en la mano derecha
    d.line([(mx + 12, my + 10), (mx + 16, my - 18)], fill=(208, 198, 186, 255), width=3)
    d.ellipse([mx + 10, my - 26, mx + 22, my - 14], fill=(120, 216, 255, 110))
    d.polygon([(mx + 16, my - 24), (mx + 20, my - 19), (mx + 16, my - 14), (mx + 12, my - 19)], fill=(170, 238, 255, 255))

    # Zorro fénec (mbweha) en silueta cercana junto al obelisco recibiendo a Maisha
    fx, fy = 424, 240
    d.ellipse([fx - 9, fy + 6, fx + 9, fy + 12], fill=(24, 10, 36, 150))
    # Cuerpo con bufanda crepuscular
    d.rectangle([fx - 5, fy - 4, fx + 5, fy + 8], fill=(228, 186, 134, 255))
    d.rectangle([fx - 6, fy - 5, fx + 6, fy - 1], fill=(144, 58, 108, 255))
    # Cabeza y OREJAS ENORMES de fénec
    d.ellipse([fx - 6, fy - 16, fx + 6, fy - 5], fill=(244, 206, 154, 255))
    d.polygon([(fx - 5, fy - 13), (fx - 15, fy - 27), (fx - 1, fy - 16)], fill=(238, 194, 140, 255))
    d.polygon([(fx + 5, fy - 13), (fx + 15, fy - 27), (fx + 1, fy - 16)], fill=(238, 194, 140, 255))
    d.polygon([(fx - 5, fy - 14), (fx - 12, fy - 24), (fx - 2, fy - 16)], fill=(196, 118, 116, 255))
    d.polygon([(fx + 5, fy - 14), (fx + 12, fy - 24), (fx + 2, fy - 16)], fill=(196, 118, 116, 255))
    # Farol en su vara
    d.line([(fx - 9, fy + 8), (fx - 9, fy - 18)], fill=(116, 74, 48, 255), width=2)
    d.ellipse([fx - 14, fy - 20, fx - 4, fy - 10], fill=(255, 224, 120, 140))
    d.rectangle([fx - 11, fy - 17, fx - 7, fy - 12], fill=(255, 244, 196, 255))

    # Motas de luz del atardecer flotando en el aire
    for _ in range(38):
        px = rng.randint(20, W - 20)
        py = rng.randint(110, H - 18)
        r = rng.choice([1, 2])
        d.ellipse([px - r, py - r, px + r, py + r], fill=(255, 220, 138, rng.randint(70, 175)))

    out = os.path.join(RAIZ, "documentacion", "boceto_valle_ocaso.png")
    img.convert("RGB").save(out)
    print("Guardado:", out)


if __name__ == "__main__":
    main()
