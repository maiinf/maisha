"""Boceto del mapa de EL NÚCLEO DE LA ESTRELLA (clímax final de Asterhaul, desde el centro de Mji-Jiwe),
para decidir con Iam antes de que Claude lo construya. Es un plano de diseño con el Pozo de las 3 Cadenas
(y los 12 Yunques de Memoria), las 3 Cámaras de Prueba que combinan Carga Sísmica, Pulso Magnético y
Resonancia de Ámbar, la Cámara del Corazón (jefe final: El Corazón del Meteorito) y el clímax con Mauti.
Sale en documentacion/boceto_nucleo_estrella.png (1000×700)."""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 700
X0, Y0, X1, Y1 = 20, 44, 980, 524
FONDO = (14, 12, 22)
CREMA = (245, 236, 218)
ROCA = (32, 28, 42)
LOSA = (64, 56, 82)
AMBAR = (255, 198, 68)
AMBAR_LUZ = (255, 235, 150)
MAGMA = (232, 92, 42)
CRISTAL = (120, 224, 245)
HIERRO = (130, 148, 174)


def fuentes():
    try:
        return (
            ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 12),
            ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana.ttf", 11),
            ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 15),
        )
    except OSError:
        f = ImageFont.load_default()
        return f, f, f


def flecha_doble(d, x0, y0, x1, y1, col):
    d.line([(x0, y0), (x1, y1)], fill=col, width=2)
    ang = math.atan2(y1 - y0, x1 - x0)
    for da in (-2.5, 2.5):
        d.line([(x1, y1), (x1 + 6 * math.cos(ang + da), y1 + 6 * math.sin(ang + da))], fill=col, width=2)
        d.line([(x0, y0), (x0 - 6 * math.cos(ang + da), y0 - 6 * math.sin(ang + da))], fill=col, width=2)


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    fb, fp, ft = fuentes()

    # Fondo del cráter profundo con vetas de ámbar y magma
    d.rectangle([X0, Y0, X1, Y1], fill=ROCA, outline=LOSA, width=2)
    # Abismo estelar / magma en los lados exteriores
    d.rectangle([X0 + 8, Y0 + 8, 220, Y1 - 8], fill=(18, 14, 28))
    d.rectangle([780, Y0 + 8, X1 - 8, Y1 - 8], fill=(18, 14, 28))

    # 1. Entrada Sur · Sello de las 3 Cadenas y los 12 Yunques (desde Mji-Jiwe)
    d.rectangle([420, 456, 580, 524], fill=LOSA, outline=CREMA, width=1)
    d.text((434, 474), "SELLO DE MJI-JIWE\n(3 Cadenas + 12 Yunques)", fill=CREMA, font=fp, align="center")
    # 3 cadenas rotas a ambos lados de la entrada
    for dx in (426, 500, 574):
        d.line([(dx, 456), (dx, 444)], fill=AMBAR, width=3)

    # 2. Atrio Estelar con Mauti esperando al borde
    d.rectangle([380, 388, 620, 448], fill=LOSA, outline=AMBAR, width=1)
    d.text((400, 409), "ATRIO DE LA ESTRELLA", fill=AMBAR_LUZ, font=fb)
    d.ellipse([562, 405, 584, 427], fill=(210, 175, 240), outline=CREMA, width=2)
    d.text((589, 410), "Mauti", fill=(220, 190, 250), font=fb)

    # Tres pasillos / Cámaras de Prueba convergentes (o en secuencia en espiral)
    # Cámara 1 (Izquierda · Sísmica)
    d.rectangle([100, 240, 310, 376], fill=LOSA, outline=AMBAR, width=2)
    d.text((120, 248), "CÁMARA 1 · SÍSMICA", fill=AMBAR, font=fb)
    d.text((116, 272), "• Muros de corteza agrietada\n• Contrapesos de vagoneta\n• Kaa-Jiwe acorazados", fill=CREMA, font=fp)
    d.rectangle([280, 356, 380, 420], fill=(48, 44, 64), outline=AMBAR, width=1)
    flecha_doble(d, 380, 412, 310, 360, AMBAR)

    # Cámara 2 (Centro · Magnética)
    d.rectangle([370, 240, 630, 360], fill=LOSA, outline=HIERRO, width=2)
    d.text((408, 248), "CÁMARA 2 · MAGNÉTICA", fill=(180, 205, 235), font=fb)
    # Foso de magma
    d.rectangle([384, 298, 616, 340], fill=(95, 32, 20), outline=MAGMA, width=1)
    # Bloque móvil de hierro meteórico
    d.rectangle([472, 302, 528, 336], fill=HIERRO, outline=CREMA, width=2)
    d.text((484, 312), "Hierro", fill=FONDO, font=fp)
    d.text((386, 272), "Pulso Magnético + Puentes-Grúa + Kovu", fill=CREMA, font=fp)
    flecha_doble(d, 310, 300, 370, 300, HIERRO)

    # Cámara 3 (Derecha · Resonancia de Ámbar)
    d.rectangle([690, 240, 900, 376], fill=LOSA, outline=CRISTAL, width=2)
    d.text((706, 248), "CÁMARA 3 · RESONANCIA", fill=CRISTAL, font=fb)
    d.text((704, 272), "• Puentes de cristal astral\n• 3 Monolitos-Diapasón\n• Popo sónicos en el vacío", fill=CREMA, font=fp)
    d.polygon([(630, 294), (690, 294), (690, 322), (630, 322)], fill=(50, 110, 140), outline=CRISTAL, width=1)
    flecha_doble(d, 630, 308, 690, 308, CRISTAL)

    # Convergencia hacia el Santuario del Corazón (puente central hacia el norte)
    d.polygon([(440, 178), (560, 178), (574, 240), (426, 240)], fill=(54, 48, 72), outline=AMBAR_LUZ, width=2)
    d.text((452, 202), "PUERTA TRIPLE", fill=AMBAR_LUZ, font=fb)
    flecha_doble(d, 740, 240, 574, 210, CRISTAL)

    # 3. Cámara Final · El Corazón del Meteorito (Norte)
    d.ellipse([250, 54, 750, 184], fill=(42, 34, 58), outline=AMBAR_LUZ, width=3)
    # Anillos gravitatorios y la Semilla Estelar mayor
    d.ellipse([444, 76, 556, 158], fill=(64, 46, 28), outline=MAGMA, width=2)
    d.ellipse([468, 92, 532, 142], fill=(220, 155, 42), outline=AMBAR_LUZ, width=2)
    d.text((366, 58), "SANTUARIO · EL CORAZÓN DEL METEORITO", fill=AMBAR_LUZ, font=fb)
    d.text((344, 160), "3 Fases (Sísmica > Magnético > Ámbar) + Verdad estelar", fill=CREMA, font=fp)

    # Monolito / Diapasón en la arena final
    for ax, ay in [(345, 118), (655, 118)]:
        d.rectangle([ax - 8, ay - 14, ax + 8, ay + 14], fill=(24, 26, 36), outline=CRISTAL, width=2)

    # Banner superior
    d.text((30, 12), "ASTERHAUL · EL NÚCLEO DE LA ESTRELLA (Mazmorra Final del Cráter)", fill=CREMA, font=ft)
    d.text((666, 14), "Mundo 3 · Los 3 Poderes de la Tierra", fill=AMBAR, font=fb)

    # Leyenda inferior en dos columnas
    y_leg = 536
    d.rectangle([20, y_leg, 980, 686], fill=(22, 20, 34), outline=LOSA, width=1)
    d.text((36, y_leg + 8), "ARQUITECTURA DEL CLÍMAX DE ASTERHAUL (MUNDO 3):", fill=AMBAR, font=fb)

    col1 = [
        "1. Apertura: las 3 Cadenas rotas + 12 Yunques\n    abren el pozo central de Mji-Jiwe.",
        "2. Senda en espiral: 3 Cámaras sucesivas combinan\n    Carga Sísmica, Pulso Magnético y Resonancia.",
        "3. Mauti espera junto al atrio antes del santuario\n    para sostener la luz al acercarse al núcleo.",
    ]
    col2 = [
        "4. Jefe final (3 fases): cada aro del meteorito cede\n    con un poder de la Tierra y golpes del Cetro.",
        "5. Revelación: el núcleo guarda la semilla mayor\n    caída siglos antes; Mauti ayuda a calmarla.",
        "6. Cierre: el Cetro del Nexo despierta completo,\n    Asterhaul sana y abre el 4.º y último mundo.",
    ]
    for i, linea in enumerate(col1):
        d.text((36, y_leg + 32 + i * 38), linea, fill=CREMA, font=fp)
    for i, linea in enumerate(col2):
        d.text((514, y_leg + 32 + i * 38), linea, fill=CREMA, font=fp)

    os.makedirs(os.path.join(RAIZ, "documentacion"), exist_ok=True)
    salida = os.path.join(RAIZ, "documentacion", "boceto_nucleo_estrella.png")
    img.save(salida)
    print("boceto guardado en:", salida)


if __name__ == "__main__":
    main()
