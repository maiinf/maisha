"""Boceto del mapa de LA AGUJA CAÍDA (camino del norte de Asterhaul), para decidir con Iam
antes de que Claude la construya. Es un plano de diseño con las terrazas de viento astral,
la afinadora Pigo, la Estela de la Resonancia de Ámbar, los monolitos-diapasón, puentes de cristal
y el Nido de la Cima (Kipanga Astral, 3.ª Cadena del Cráter).
Sale en documentacion/boceto_aguja_caida.png (1000×700)."""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 700
X0, Y0, X1, Y1 = 20, 44, 980, 524
FONDO = (16, 18, 26)
CREMA = (245, 236, 218)
ROCA = (34, 38, 52)
LOSA = (68, 76, 102)
CRISTAL = (120, 224, 245)
CRISTAL_LUZ = (200, 250, 255)
AMBAR = (255, 198, 68)
AMBAR_LUZ = (255, 232, 130)
OBSIDIANA = (24, 26, 36)
VIENTO = (90, 140, 180)


def fuentes():
    try:
        return (
            ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 13),
            ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana.ttf", 13),
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

    # Fondo de roca basáltica con precipicio y cielo astral
    d.rectangle([X0, Y0, X1, Y1], fill=ROCA, outline=LOSA, width=2)

    # El gran abismo de viento astral al oeste y este
    d.polygon([(X0, Y0), (X0 + 160, Y0), (X0 + 110, Y1), (X0, Y1)], fill=(12, 14, 20))
    d.polygon([(X1 - 160, Y0), (X1, Y0), (X1, Y1), (X1 - 110, Y1)], fill=(12, 14, 20))

    # Senderos y terrazas de basalto tallado (Ruta de la Aguja)
    # Entrada Sur (desde Mji-Jiwe)
    d.rectangle([430, 440, 570, 524], fill=LOSA, outline=CREMA, width=1)
    # Terraza 1 · Base de la Aguja y Pigo
    d.rectangle([320, 340, 680, 440], fill=LOSA, outline=CREMA, width=1)
    # Puente de Cristal 1 (activado por Diapasón)
    d.rectangle([460, 290, 540, 340], fill=CRISTAL, outline=CRISTAL_LUZ, width=1)
    # Terraza 2 · Desfiladero de las Ráfagas (Cresta de los Diapasones)
    d.polygon([(260, 200), (740, 200), (660, 290), (340, 290)], fill=LOSA, outline=CREMA, width=1)
    # Plataformas flotantes laterales (Resonancia de Ámbar)
    d.rectangle([180, 220, 240, 270], fill=LOSA, outline=AMBAR, width=2)
    d.rectangle([760, 220, 820, 270], fill=LOSA, outline=AMBAR, width=2)
    flecha_doble(d, 240, 245, 260, 245, CRISTAL)
    flecha_doble(d, 740, 245, 760, 245, CRISTAL)
    # Puente de Cristal 2 hacia la cima
    d.polygon([(470, 140), (530, 140), (550, 200), (450, 200)], fill=CRISTAL, outline=CRISTAL_LUZ, width=1)
    # Cima · El Nido de Kipanga Astral (la punta de la Aguja clavada)
    d.polygon([(360, 54), (640, 54), (590, 140), (410, 140)], fill=(44, 48, 66), outline=AMBAR, width=2)

    # Monolitos-Diapasón (resonantes con el Cetro)
    diasones = [(360, 370), (640, 370), (410, 240), (590, 240), (210, 245), (790, 245), (440, 90), (560, 90)]
    for dx, dy in diasones:
        d.rectangle([dx - 8, dy - 18, dx + 8, dy + 18], fill=OBSIDIANA, outline=AMBAR, width=2)
        d.line([(dx - 5, dy - 24), (dx - 5, dy - 18)], fill=AMBAR_LUZ, width=2)
        d.line([(dx + 5, dy - 24), (dx + 5, dy - 18)], fill=AMBAR_LUZ, width=2)
        # Ondas de sonido
        d.arc([dx - 18, dy - 28, dx + 18, dy - 8], 200, 340, fill=AMBAR_LUZ, width=1)

    # Puntos clave y elementos interactivos
    # Entrada
    d.text((450, 475), "ENTRADA SUR\n(desde Mji-Jiwe)", fill=CREMA, font=fp, align="center")
    # Pigo
    d.ellipse([485, 385, 515, 415], fill=(220, 180, 120), outline=CREMA, width=2)
    d.text((525, 392), "PIGO (afinadora en gris)", fill=AMBAR, font=fb)
    # Estela de la Resonancia
    d.rectangle([485, 350, 515, 370], fill=(80, 140, 180), outline=CRISTAL, width=1)
    d.text((450, 332), "Estela de la Resonancia", fill=CRISTAL, font=fp)

    # Enemigos Popo de Obsidiana (murciélagos resonantes)
    for px, py in [(300, 230), (680, 230), (500, 170)]:
        d.polygon([(px - 10, py), (px, py - 8), (px + 10, py), (px, py + 8)], fill=OBSIDIANA, outline=CRISTAL_LUZ, width=1)
        d.text((px - 14, py + 10), "Popo", fill=CREMA, font=fp)

    # Jefe Kipanga Astral y la 3.ª Cadena
    d.ellipse([475, 70, 525, 120], fill=OBSIDIANA, outline=AMBAR, width=2)
    d.text((440, 58), "KIPANGA ASTRAL (Jefe)", fill=AMBAR, font=fb)
    d.text((435, 122), "3.ª CADENA DEL CRÁTER", fill=CRISTAL_LUZ, font=fp)
    d.line([(450, 95), (380, 95)], fill=(160, 160, 180), width=3)
    d.line([(550, 95), (620, 95)], fill=(160, 160, 180), width=3)

    # Título superior
    d.text((30, 12), "ASTERHAUL · LA AGUJA CAÍDA (Ruta Norte a la Cumbre)", fill=CREMA, font=ft)
    d.text((700, 14), "Mundo 3 · Poder: Resonancia de Ámbar", fill=AMBAR, font=fb)

    # Leyenda inferior en dos columnas
    y_leg = 538
    d.rectangle([20, y_leg, 980, 686], fill=(24, 28, 40), outline=LOSA, width=1)
    d.text((36, y_leg + 8), "MECÁNICAS Y SECRETOS DE LA AGUJA CAÍDA:", fill=AMBAR, font=fb)

    col1 = [
        "1. Entrada: tras vencer a Kifaru y Nyundo, las 2 primeras cadenas se aflojan.",
        "2. Pigo enseña la Resonancia de Ámbar al recuperar su Esquirla en la Cresta.",
        "3. Resonancia de Ámbar: vibrar diapasón proyecta puentes de cristal y rocas.",
        "4. Popo de Obsidiana: aturde con ondas sónicas si no desvías el eco con diapasón.",
    ]
    col2 = [
        "5. Cresta de los Diapasones: coordinar 3 diapasones para alinear el puente.",
        "6. Cima del Nido: Kipanga Astral anida sobre la punta clavada de la estrella.",
        "7. Victoria: suelta la 3.ª Cadena y abre el Núcleo de la Estrella en Mji-Jiwe.",
        "8. 12 Esquirlas completadas: despiertan a los 12 artesanos y forjan el Cetro.",
    ]
    for i, linea in enumerate(col1):
        d.text((36, y_leg + 32 + i * 26), linea, fill=CREMA, font=fp)
    for i, linea in enumerate(col2):
        d.text((510, y_leg + 32 + i * 26), linea, fill=CREMA, font=fp)

    os.makedirs(os.path.join(RAIZ, "documentacion"), exist_ok=True)
    salida = os.path.join(RAIZ, "documentacion", "boceto_aguja_caida.png")
    img.save(salida)
    print("boceto guardado en:", salida)


if __name__ == "__main__":
    main()
