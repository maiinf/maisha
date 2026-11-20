"""Boceto de JIONI, LA CIUDAD DE LOS FAROLES (el Valle del Ocaso, la ciudad del centro), para decidir con Iam.
Lo pinta Claude porque el de Gemini aún no estaba (mismo estilo que boceto_mirador_ocaso.py).
Enseña:
  1. El trazado: la Escalera del Arco (desde el Mirador), la Plaza de los Doce Faroles, la Torre del Reloj de Arena
     que sujeta el sol con tres cadenas, el Barrio de las Cortinas, el Mercado del Crepúsculo y las cuatro salidas
     (Dunas de Penumbra, Jardín de los Faroles, Calzada de los Obeliscos y la Puerta del Horizonte, sellada).
  2. Las opciones: qué le pasa a la ciudad y quién guía a Maisha en ella.
Sale en documentacion/boceto_jioni.png (1020x760)."""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1020, 760
FONDO = (20, 14, 28)
ABISMO = (34, 18, 48)
TIERRA = (158, 96, 82)
TIERRA_CLARA = (182, 114, 92)
TEJADO = (112, 52, 62)
BORDE_ORO = (248, 194, 104)
BORDE_MALVA = (196, 128, 246)
CREMA = (248, 234, 198)
APAGADO = (74, 52, 70)


def etiqueta(d, x, y, texto, font, bg=(22, 14, 30), fg=CREMA, borde=None):
    tw = d.textlength(texto, font=font)
    d.rectangle([x, y, x + tw + 14, y + 22], fill=bg, outline=borde)
    d.text((x + 7, y + 3), texto, fill=fg, font=font)


def casa(d, x, y, cortina=False):
    d.rectangle([x - 14, y - 10, x + 14, y + 12], fill=(196, 132, 100), outline=(60, 28, 40), width=2)
    d.polygon([(x - 18, y - 10), (x, y - 24), (x + 18, y - 10)], fill=TEJADO, outline=(60, 28, 40))
    if cortina:
        d.rectangle([x - 6, y - 4, x + 6, y + 6], fill=(92, 40, 90))      # cortinas echadas: dentro quieren noche
        d.line([(x, y - 4), (x, y + 6)], fill=(150, 90, 150), width=1)
    else:
        d.rectangle([x - 6, y - 4, x + 6, y + 6], fill=(255, 210, 120))


def flecha(d, p0, p1, col=(255, 214, 118)):
    d.line([p0, p1], fill=col, width=3)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (-0.5, 0.5):
        d.line([p1, (p1[0] - math.cos(ang + s) * 10, p1[1] - math.sin(ang + s) * 10)], fill=col, width=3)


def zorro(d, x, y, ojeras=False, pequeno=False):
    r = 8 if pequeno else 11
    d.ellipse([x - r, y - r, x + r, y + r], fill=(246, 208, 154), outline=(146, 58, 110), width=2)
    for s in (-1, 1):
        d.polygon([(x + s * r * 0.6, y - r * 0.7), (x + s * r * 1.5, y - r * 2.1), (x + s * r * 0.1, y - r)],
                  fill=(246, 208, 154), outline=(74, 34, 52))
    if ojeras:
        for s in (-1, 1):
            d.arc([x + s * 4 - 3, y - 2, x + s * 4 + 3, y + 4], 0, 180, fill=(110, 60, 120), width=2)


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    try:
        ft = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 15)
        fb = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 13)
        fp = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana.ttf", 12)
    except OSError:
        ft = fb = fp = ImageFont.load_default()

    d.text((22, 10), "2. JIONI, LA CIUDAD DE LOS FAROLES — trazado y opciones (boceto de Claude para Iam)", fill=(255, 216, 132), font=ft)
    d.rectangle([20, 40, 1000, 470], fill=ABISMO, outline=(96, 62, 118))

    # el sol, atado: arriba a la derecha, con tres cadenas que bajan a la torre
    sx, sy = 880, 92
    d.ellipse([sx - 34, sy - 34, sx + 34, sy + 34], fill=(255, 214, 120), outline=(255, 160, 70), width=3)
    for k in range(3):
        d.arc([sx - 44 - k * 8, sy - 44 - k * 8, sx + 44 + k * 8, sy + 44 + k * 8], 0, 360, fill=(170, 120, 80), width=1)
    tx, ty = 510, 132
    # la meseta de la ciudad, en terrazas
    d.rounded_rectangle([110, 70, 900, 440], radius=26, fill=TIERRA, outline=(46, 24, 52), width=3)
    d.rounded_rectangle([250, 150, 770, 400], radius=20, fill=TIERRA_CLARA, outline=(60, 30, 48), width=2)

    # la Escalera del Arco (llega del Mirador, por el norte)
    d.rectangle([470, 44, 550, 72], fill=(196, 140, 104), outline=BORDE_ORO, width=2)
    for y in range(48, 72, 6):
        d.line([(474, y), (546, y)], fill=(120, 70, 60), width=1)
    flecha(d, (510, 46), (510, 96))

    for dx in (-10, 0, 10):
        pasos = 16
        for i in range(pasos):
            t0, t1 = i / pasos, (i + 0.6) / pasos
            a = (tx + dx + (sx - tx - dx) * t0, ty - 30 + (sy - ty + 30) * t0 - math.sin(t0 * math.pi) * 30)
            b = (tx + dx + (sx - tx - dx) * t1, ty - 30 + (sy - ty + 30) * t1 - math.sin(t1 * math.pi) * 30)
            d.line([a, b], fill=(150, 150, 170), width=3)

    # la Torre del Reloj de Arena (norte de la plaza): sujeta las cadenas
    d.rectangle([tx - 20, ty - 36, tx + 20, ty + 18], fill=(120, 70, 86), outline=BORDE_ORO, width=2)
    d.polygon([(tx - 12, ty - 26), (tx + 12, ty - 26), (tx, ty - 8)], fill=(255, 220, 150))
    d.polygon([(tx - 12, ty + 10), (tx + 12, ty + 10), (tx, ty - 8)], fill=(230, 170, 110))

    # la Plaza de los Doce Faroles: doce postes en corro, dos encendidos (los del Mirador)
    px, py = 510, 272
    d.ellipse([px - 92, py - 62, px + 92, py + 62], fill=(208, 146, 106), outline=(110, 60, 60), width=2)
    for k in range(12):
        a = -math.pi / 2 + k * math.pi / 6
        x, y = px + math.cos(a) * 78, py + math.sin(a) * 52
        luz = k < 2
        d.line([(x, y + 6), (x, y - 6)], fill=(70, 40, 30), width=3)
        d.ellipse([x - 6, y - 14, x + 6, y - 2], fill=(255, 214, 108) if luz else APAGADO, outline=(60, 30, 20))
    zorro(d, px, py - 4, pequeno=True)          # el guía, en el centro

    # el Barrio de las Cortinas (oeste) y el Mercado del Crepúsculo (este)
    for (x, y) in ((170, 130), (215, 175), (165, 230), (220, 285), (170, 345)):
        casa(d, x, y, cortina=True)
    for (x, y) in ((300, 340), (340, 200)):
        zorro(d, x, y, ojeras=True)
    for (x, y) in ((690, 200), (740, 200), (690, 250)):
        d.rectangle([x - 18, y - 8, x + 18, y + 12], fill=(150, 96, 70), outline=(60, 30, 30), width=2)
        d.polygon([(x - 22, y - 8), (x + 22, y - 8), (x + 16, y - 20), (x - 16, y - 20)], fill=(196, 84, 90), outline=(60, 30, 30))
    zorro(d, 790, 250, ojeras=True)

    # las salidas
    d.rectangle([110, 230, 126, 280], fill=(60, 30, 70), outline=BORDE_ORO, width=2)
    flecha(d, (112, 255), (52, 255))
    d.rectangle([884, 300, 900, 350], fill=(60, 30, 70), outline=BORDE_ORO, width=2)
    flecha(d, (898, 325), (958, 325))
    d.rectangle([800, 424, 850, 440], fill=(60, 30, 70), outline=BORDE_ORO, width=2)
    flecha(d, (830, 438), (880, 462))
    d.rectangle([470, 424, 550, 444], fill=(70, 20, 90), outline=BORDE_MALVA, width=3)
    for dx in (-20, 0, 20):
        d.ellipse([510 + dx - 5, 428, 510 + dx + 5, 440], outline=(255, 214, 108), width=2)   # los tres sellos
    flecha(d, (510, 444), (510, 466), col=BORDE_MALVA)

    etiqueta(d, 568, 46, "Escalera del Arco (llega del Mirador)", fp, bg=(32, 18, 46))
    etiqueta(d, 540, 104, "Torre del Reloj de Arena (ata el sol)", fb, borde=BORDE_ORO)
    etiqueta(d, 404, 180, "Plaza de los Doce Faroles", fb, borde=BORDE_ORO)
    etiqueta(d, 124, 380, "Barrio de las Cortinas", fb, borde=BORDE_MALVA)
    etiqueta(d, 650, 150, "Mercado del Crepúsculo", fb, borde=BORDE_ORO)
    etiqueta(d, 26, 196, "<- Dunas de Penumbra", fp, bg=(32, 18, 46))
    etiqueta(d, 836, 288, "Jardín de los Faroles ->", fp, bg=(32, 18, 46))
    etiqueta(d, 760, 444, "Calzada de los Obeliscos", fp, bg=(32, 18, 46))
    etiqueta(d, 300, 444, "Puerta del Horizonte (sellada)", fb, borde=BORDE_MALVA)

    # las opciones
    d.rectangle([20, 484, 1000, 748], fill=(28, 18, 38), outline=(182, 134, 88))
    d.text((34, 494), "1. ¿Qué le pasa a Jioni?", fill=(255, 218, 132), font=fb)
    op1 = [("A · Los Desvelados (recomendada)", "Sin noche nadie duerme. Los fénec están agotados, con ojeras, y repiten su faena sin parar.",
            "Cada Farol de la Hora colgado en la plaza devuelve una hora de la tarde: alguien, por fin, descansa y ayuda."),
           ("B · Los Detenidos de arena", "El miedo los ha dejado quietos como estatuas de arena (parecido a Mji-Jiwe y Sigilia).",
            "Cada Farol de la Hora despierta a uno.")]
    y = 518
    for t, l1, l2 in op1:
        d.text((44, y), t, fill=CREMA, font=fb)
        d.text((60, y + 18), l1, fill=(230, 214, 190), font=fp)
        d.text((60, y + 34), l2, fill=(230, 214, 190), font=fp)
        y += 58
    d.text((34, 636), "2. ¿Quién guía a Maisha en la ciudad?", fill=(255, 218, 132), font=fb)
    op2 = [("A · Kibatari, aprendiz de Mwanga (recomendada)", "Joven, nunca ha visto la noche (la idea B de Gemini, con otro nombre para no chocar con la ciudad)."),
           ("B · Bibi Saa, la alcaldesa del reloj", "Vieja; fue quien mandó atar el sol, y ahora no sabe cómo desatarlo.")]
    y = 660
    for t, l1 in op2:
        d.text((44, y), t, fill=CREMA, font=fb)
        d.text((60, y + 18), l1, fill=(230, 214, 190), font=fp)
        y += 42

    salida = os.path.join(RAIZ, "documentacion", "boceto_jioni.png")
    img.save(salida)
    print("Boceto:", salida)


if __name__ == "__main__":
    main()
