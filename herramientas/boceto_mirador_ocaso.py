"""Boceto del trazado y mecánicas de la PRIMERA ZONA del Valle del Ocaso:
EL MIRADOR DEL OCASO (entrada desde el sur del Kitovu hasta Jioni).
Enseña sin texto:
  1. Sombras largas sólidas que hacen de puente sobre grietas de penumbra.
  2. Relojes de Sol que giran el rayo del atardecer (Oeste / Sur / Este) y rotan todas las sombras.
  3. Criaturas de penumbra (Kivuli menor) invulnerables en sombra, vulnerables al darles la luz solar.
  4. Guía fénec (mbweha) junto al Primer Reloj + Puerta del Atardecer hacia Jioni.
Sale en documentacion/boceto_mirador_ocaso.png (1020x700)."""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1020, 700
FONDO = (20, 14, 28)
ABISMO = (28, 16, 44)
TIERRA = (158, 96, 82)
TIERRA_CLARA = (182, 114, 92)
SOMBRA_PUENTE = (48, 24, 78)
SOMBRA_ALT = (68, 36, 102)
BORDE_ORO = (248, 194, 104)
BORDE_MALVA = (196, 128, 246)
CREMA = (248, 234, 198)


def etiqueta(d, x, y, texto, font, bg=(22, 14, 30), fg=CREMA, borde=None):
    tw = d.textlength(texto, font=font)
    r = [x, y, x + tw + 14, y + 22]
    d.rectangle(r, fill=bg, outline=borde)
    d.text((x + 7, y + 3), texto, fill=fg, font=font)
    return r


def obelisco(d, x, y):
    d.polygon([(x - 10, y + 8), (x - 7, y - 16), (x, y - 24), (x + 7, y - 16), (x + 10, y + 8)],
              fill=(78, 46, 86), outline=BORDE_ORO)
    d.ellipse([x - 3, y - 10, x + 3, y - 4], fill=(255, 224, 134))


def reloj_sol(d, x, y):
    d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(64, 36, 68), outline=BORDE_ORO, width=2)
    d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 228, 136))
    for ang in (0, 2.1, 4.2):
        d.line([(x, y), (x + math.cos(ang) * 13, y + math.sin(ang) * 13)], fill=BORDE_ORO, width=2)


def puente_sombra(d, p0, p1, ancho=18, activo=True):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = max(1.0, math.hypot(dx, dy))
    nx, ny = -dy / L * ancho * 0.5, dx / L * ancho * 0.5
    poly = [
        (p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny),
        (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny),
    ]
    if activo:
        d.polygon(poly, fill=SOMBRA_PUENTE, outline=BORDE_ORO)
        d.line([(p0[0] - nx, p0[1] - ny), (p1[0] - nx, p1[1] - ny)], fill=BORDE_MALVA, width=2)
    else:
        d.polygon(poly, fill=SOMBRA_ALT, outline=(172, 128, 212))
        # línea discontinua indicando sombra alternativa al girar el sol
        pasos = int(L / 12)
        for k in range(0, pasos, 2):
            t0, t1 = k / pasos, min(1.0, (k + 1) / pasos)
            a = (p0[0] + dx * t0, p0[1] + dy * t0)
            b = (p0[0] + dx * t1, p0[1] + dy * t1)
            d.line([a, b], fill=(255, 216, 136), width=2)


def flecha(d, p0, p1, col=(255, 214, 118)):
    d.line([p0, p1], fill=col, width=3)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (-0.5, 0.5):
        px = p1[0] - math.cos(ang + s) * 10
        py = p1[1] - math.sin(ang + s) * 10
        d.line([p1, (px, py)], fill=col, width=3)


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    try:
        ft = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 15)
        fb = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 13)
        fp = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana.ttf", 12)
    except OSError:
        ft = fb = fp = ImageFont.load_default()

    d.text((22, 10), "1. EL MIRADOR DEL OCASO — trazado de la primera zona y mecánica de Luz y Sombra (propuesta para Iam)",
           fill=(255, 216, 132), font=ft)

    # Lienzo del abismo crepuscular (980x485)
    d.rectangle([20, 40, 1000, 525], fill=ABISMO, outline=(96, 62, 118))

    # Rayos solares suaves desde el oeste-suroeste indicando la dirección inicial del sol detenido
    for ry in range(70, 510, 62):
        d.line([(26, ry), (82, ry + 18)], fill=(255, 190, 96), width=2)
    d.ellipse([26, 215, 58, 247], fill=(255, 224, 136), outline=(255, 168, 74), width=2)
    d.text((26, 254), "SOL", fill=(255, 220, 132), font=fb)

    # ISLAS / MESETAS DE PIEDRA CREPUSCULAR (separadas por grietas que solo se cruzan por sombras-puente)
    islas = [
        # 1A. Mirador Norte (entrada desde el sur del Kitovu)
        ([370, 56, 610, 152], TIERRA_CLARA),
        # 1B. Balcón Este (primer cruce por sombra fija -> enseña la regla sin texto)
        ([690, 64, 960, 198], TIERRA),
        # 2. Plaza del Primer Reloj de Sol y el guía mbweha (centro)
        ([360, 212, 675, 342], TIERRA_CLARA),
        # 3. Terrazas de Penumbra (oeste: combate con enemigos de sombra + 2º reloj + secreto)
        ([88, 222, 290, 438], TIERRA),
        # Secreto norte-oeste (al girar el reloj del oeste hacia el norte)
        ([102, 74, 276, 154], (142, 82, 106)),
        # 4. El Arco del Atardecer -> bajada a Jioni (sur)
        ([405, 408, 765, 506], TIERRA_CLARA),
    ]
    for r, col in islas:
        d.rounded_rectangle(r, radius=14, fill=col, outline=(46, 24, 52), width=3)
        # filo cálido superior de luz de atardecer
        d.line([(r[0] + 12, r[1] + 2), (r[2] - 12, r[1] + 2)], fill=(238, 154, 96), width=2)

    # SOMBRAS-PUENTE (sólidas = posición actual del sol · discontinuas = al girar el Reloj de Sol)
    # Puente 1 (tutorial natural): obelisco en 1A proyecta sombra fija al este -> 1B
    puente_sombra(d, (592, 106), (702, 106), 22, activo=True)
    # Puente 2: desde 1B baja a la Plaza Central (2) por sombra diagonal
    puente_sombra(d, (726, 186), (654, 232), 22, activo=True)
    # Puente 3A (inicial): desde Plaza (2) hacia el oeste -> Terrazas de Penumbra (3)
    puente_sombra(d, (376, 278), (278, 278), 22, activo=True)
    # Puente 3B (al girar el Primer Reloj de Sol): la sombra del gran obelisco rota al SUR -> Arco del Atardecer (4)
    puente_sombra(d, (518, 326), (518, 418), 24, activo=False)
    # Puente 4 (al girar el 2º Reloj en Terrazas): sombra sube al NORTE -> Islote Secreto (Farol #2)
    puente_sombra(d, (188, 234), (188, 146), 20, activo=False)

    # Obeliscos proyectores
    obelisco(d, 586, 106)
    obelisco(d, 734, 182)
    obelisco(d, 384, 278)
    obelisco(d, 518, 318)
    obelisco(d, 188, 238)

    # Relojes de Sol interactivos (golpe de Cetro / poder del Ocaso gira el ángulo solar)
    reloj_sol(d, 495, 256)
    reloj_sol(d, 206, 366)

    # Guía zorro fénec (mbweha) junto al Primer Reloj de Sol
    gx, gy = 438, 254
    d.ellipse([gx - 11, gy - 11, gx + 11, gy + 11], fill=(246, 208, 154), outline=(146, 58, 110), width=2)
    d.polygon([(gx - 7, gy - 8), (gx - 14, gy - 22), (gx - 1, gy - 11)], fill=(246, 208, 154), outline=(74, 34, 52))
    d.polygon([(gx + 7, gy - 8), (gx + 14, gy - 22), (gx + 1, gy - 11)], fill=(246, 208, 154), outline=(74, 34, 52))

    # Enemigos de Penumbra (Kivuli menor: sombra morada con ojos ámbar -> se aturden al girar el sol y darles luz)
    for ex, ey in [(836, 134), (156, 318), (242, 310), (624, 462)]:
        d.ellipse([ex - 11, ey - 9, ex + 11, ey + 9], fill=(54, 22, 84), outline=(204, 132, 252), width=2)
        d.ellipse([ex - 5, ey - 3, ex - 2, ey], fill=(255, 214, 104))
        d.ellipse([ex + 2, ey - 3, ex + 5, ey], fill=(255, 214, 104))

    # Faroles de la Hora (2 coleccionables en la primera zona: Balcón Este + Islote Secreto)
    for fx, fy in [(914, 114), (188, 108)]:
        d.ellipse([fx - 9, fy - 9, fx + 9, fy + 9], fill=(255, 212, 108))
        d.rectangle([fx - 4, fy - 6, fx + 4, fy + 5], fill=(255, 244, 188), outline=(74, 36, 18))

    # 2 Espejos-Farol de la Puerta del Atardecer (sur -> Jioni)
    for mx, my in [(686, 444), (686, 480)]:
        d.polygon([(mx - 7, my), (mx, my - 9), (mx + 7, my), (mx, my + 9)], fill=(255, 224, 130), outline=(66, 36, 22))
    d.rectangle([718, 434, 756, 492], fill=(44, 22, 62), outline=BORDE_ORO, width=3)

    # Flechas de recorrido principal
    flecha(d, (490, 50), (490, 82))
    flecha(d, (614, 106), (684, 106))
    flecha(d, (790, 166), (754, 190))
    flecha(d, (428, 304), (306, 304))
    flecha(d, (552, 462), (656, 462))

    # Etiquetas claras de las 4 secciones
    etiqueta(d, 376, 60, "1. Entrada (Kitovu) · 1ª sombra", fb, borde=BORDE_ORO)
    etiqueta(d, 706, 70, "1B. Balcón Este (1er Farol)", fb, borde=BORDE_ORO)
    etiqueta(d, 372, 218, "2. Plaza del 1er Reloj de Sol + Guía Mbweha", fb, borde=BORDE_ORO)
    etiqueta(d, 96, 228, "3. Terrazas de Penumbra", fb, borde=BORDE_MALVA)
    etiqueta(d, 104, 412, "2º Reloj: ilumina enemigos", fp, bg=(32, 18, 46))
    etiqueta(d, 106, 78, "Secreto (2º Farol)", fb, borde=(255, 212, 108))
    etiqueta(d, 414, 414, "4. Arco del Atardecer >> bajada a Jioni", fb, borde=BORDE_ORO)
    etiqueta(d, 536, 356, "Al girar el sol -> puente sur", fp, bg=(36, 20, 56), fg=(255, 224, 146))

    # Leyenda inferior (2 columnas con la mecánica paso a paso)
    d.rectangle([20, 540, 1000, 686], fill=(28, 18, 38), outline=(182, 134, 88))
    col1 = [
        (SOMBRA_PUENTE, BORDE_ORO, "Sombra-puente activa: sombra larga de obelisco (se cruza andando)"),
        (SOMBRA_ALT, BORDE_MALVA, "Sombra rotada: activar un Reloj de Sol gira el atardecer y abre rutas"),
        ((64, 36, 68), BORDE_ORO, "Reloj de Sol: golpe o poder cambia el ángulo (Oeste -> Sur -> Este)"),
        ((54, 22, 84), BORDE_MALVA, "Kivuli menor: invulnerable en penumbra; la luz solar lo deja expuesto"),
    ]
    for i, (fill_c, out_c, txt) in enumerate(col1):
        ly = 552 + i * 32
        d.rectangle([34, ly + 2, 52, ly + 18], fill=fill_c, outline=out_c, width=2)
        d.text((62, ly + 2), txt, fill=CREMA, font=fp)

    d.line([(606, 550), (606, 676)], fill=(112, 78, 118), width=1)
    d.text((620, 550), "Flujo jugable (sin tutorial pesado):", fill=(255, 218, 132), font=fb)
    pasos = [
        "1) Cruza la 1ª grieta por sombra fija (aprende la regla).",
        "2) Habla con el guía mbweha junto al Reloj de Sol.",
        "3) Gira el reloj: la sombra rota, ilumina y abre el sur.",
        "4) Enciende los 2 espejos del Arco para bajar a Jioni.",
    ]
    for i, p_txt in enumerate(pasos):
        d.text((620, 574 + i * 25), p_txt, fill=CREMA, font=fp)

    out = os.path.join(RAIZ, "documentacion", "boceto_mirador_ocaso.png")
    img.save(out)
    print("Guardado:", out)


if __name__ == "__main__":
    main()
