"""Boceto del Camino Este de Jioni (Valle del Ocaso):
EL JARDÍN DE LOS FAROLES + opciones de jefe MONDO.
Sale en documentacion/boceto_jardin_faroles.png (1200x780)."""
import math
import os
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 780

FONDO = (20, 14, 28)
PANEL = (28, 20, 40)
BORDE = (128, 86, 134)
ORO = (248, 198, 108)
ORO_SUAVE = (212, 162, 88)
CREMA = (248, 236, 206)
TEXTO_SUAVE = (206, 190, 214)
TERRAZA = (166, 106, 94)
TERRAZA_CLARA = (192, 128, 106)
ESTANQUE = (42, 26, 68)
SOMBRA = (46, 22, 76)
MALVA = (196, 128, 246)
CORAL = (232, 118, 106)
AMBAR = (255, 212, 104)
ESMERALDA = (122, 214, 174)


def fuente(tam):
    for ruta in (
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if os.path.exists(ruta):
            try:
                return ImageFont.truetype(ruta, tam)
            except OSError:
                pass
    return ImageFont.load_default()


def etiqueta(d, x, y, txt, f, bg=(24, 15, 34), fg=CREMA, borde=ORO_SUAVE):
    tw = d.textlength(txt, font=f)
    d.rounded_rectangle([x, y, x + tw + 14, y + 22], radius=4, fill=bg, outline=borde)
    d.text((x + 7, y + 3), txt, fill=fg, font=f)


def prisma(d, x, y, col=AMBAR):
    d.polygon([(x, y - 13), (x + 10, y), (x, y + 13), (x - 10, y)], fill=col, outline=CREMA)


def espejo(d, x, y):
    d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(74, 52, 42), outline=ORO, width=2)
    d.line([(x - 6, y - 6), (x + 6, y + 6)], fill=(255, 242, 192), width=2)


def farol(d, x, y):
    d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(94, 56, 36))
    d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=AMBAR, outline=ORO)


def dibujar_mondo_a(d, cx, cy):
    """Opción A: Mondo, el Serval de Mil Reflejos."""
    # Dos reflejos fantasma laterales
    for dx in (-76, 76):
        d.ellipse([cx + dx - 28, cy - 12, cx + dx + 28, cy + 28], fill=(42, 24, 68), outline=MALVA)
        d.polygon([(cx + dx - 16, cy - 10), (cx + dx - 22, cy - 36), (cx + dx - 4, cy - 16)], fill=(54, 30, 86), outline=MALVA)
        d.polygon([(cx + dx + 16, cy - 10), (cx + dx + 22, cy - 36), (cx + dx + 4, cy - 16)], fill=(54, 30, 86), outline=MALVA)
    # Cuerpo central de bronce y cristal
    d.ellipse([cx - 38, cy - 10, cx + 38, cy + 44], fill=(102, 66, 52), outline=ORO, width=2)
    # Cabeza estilizada de serval con orejas altas de cristal
    d.ellipse([cx - 24, cy - 36, cx + 24, cy + 6], fill=(124, 82, 62), outline=ORO, width=2)
    d.polygon([(cx - 18, cy - 28), (cx - 28, cy - 64), (cx - 4, cy - 34)], fill=AMBAR, outline=ORO)
    d.polygon([(cx + 18, cy - 28), (cx + 28, cy - 64), (cx + 4, cy - 34)], fill=AMBAR, outline=ORO)
    # Collar prismático + ojos dorados
    d.polygon([(cx, cy + 2), (cx + 12, cy + 16), (cx, cy + 30), (cx - 12, cy + 16)], fill=(255, 242, 180), outline=CORAL)
    d.ellipse([cx - 12, cy - 20, cx - 4, cy - 12], fill=(255, 244, 178))
    d.ellipse([cx + 4, cy - 20, cx + 12, cy - 12], fill=(255, 244, 178))
    # Cola con prisma
    d.line([(cx + 32, cy + 26), (cx + 58, cy + 14), (cx + 54, cy - 18)], fill=ORO, width=4)
    prisma(d, cx + 54, cy - 24, AMBAR)


def dibujar_mondo_b(d, cx, cy):
    """Opción B: Mondo, el Guardián del Farol Gigante."""
    d.ellipse([cx - 50, cy - 12, cx + 50, cy + 44], fill=(64, 42, 68), outline=ORO, width=2)
    # Jaula de farol en el lomo
    d.rounded_rectangle([cx - 26, cy - 52, cx + 26, cy - 6], radius=6, fill=(255, 206, 98), outline=ORO, width=3)
    d.line([(cx, cy - 52), (cx, cy - 6)], fill=(96, 58, 36), width=2)
    d.line([(cx - 26, cy - 29), (cx + 26, cy - 29)], fill=(96, 58, 36), width=2)
    # Cabeza acorazada a la izquierda
    d.ellipse([cx - 64, cy - 18, cx - 22, cy + 18], fill=(82, 54, 86), outline=ORO, width=2)
    d.polygon([(cx - 56, cy - 14), (cx - 66, cy - 40), (cx - 42, cy - 18)], fill=(98, 66, 96), outline=ORO)
    d.ellipse([cx - 52, cy - 6, cx - 44, cy + 2], fill=CORAL)


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    f_tit = fuente(24)
    f_sub = fuente(15)
    f_lbl = fuente(13)
    f_peq = fuente(12)

    d.rectangle([0, 0, W, 62], fill=(28, 18, 42))
    d.line([(0, 62), (W, 62)], fill=ORO, width=2)
    d.text((24, 12), "VALLE DEL OCASO · CAMINO ESTE: EL JARDÍN DE LOS FAROLES", fill=ORO, font=f_tit)
    d.text((24, 40), "Salida este de Jioni · Mecánica: Espejos + Prismas de Cristal que disipan espejismos + 3 Faroles + Peso del Este", fill=TEXTO_SUAVE, font=f_peq)

    # --- PANEL IZQUIERDO: TRAZADO JUGABLE ---
    d.rounded_rectangle([20, 78, 700, 756], radius=10, fill=PANEL, outline=BORDE, width=2)
    d.text((36, 90), "TRAZADO DE LA ZONA (74 × 54 casillas aprox.)", fill=ORO, font=f_sub)

    d.rounded_rectangle([36, 118, 684, 650], radius=8, fill=ESTANQUE, outline=(96, 62, 108))
    # Canales reflejantes y faroles flotantes
    for fx, fy in ((110, 170), (260, 210), (490, 170), (210, 560), (520, 580)):
        d.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], fill=(255, 198, 92))

    # 1. Entrada desde Jioni (Oeste)
    d.rounded_rectangle([46, 285, 178, 408], radius=10, fill=TERRAZA, outline=ORO, width=2)
    etiqueta(d, 54, 294, "Desde Jioni >", f_lbl, bg=(44, 24, 52), fg=ORO)
    d.text((56, 322), "Pérgola de entrada", fill=CREMA, font=f_peq)
    d.text((56, 338), "1.er Prisma solar", fill=TEXTO_SUAVE, font=f_peq)
    espejo(d, 96, 378)
    prisma(d, 152, 378, AMBAR)

    # 2. Claustro de los Prismas (Centro)
    d.rounded_rectangle([226, 236, 434, 444], radius=12, fill=TERRAZA_CLARA, outline=ORO, width=2)
    etiqueta(d, 242, 246, "CLAUSTRO DE LOS PRISMAS", f_lbl, bg=(42, 24, 50), fg=ORO)
    d.text((242, 276), "· Cadena de 3 espejos + prismas", fill=(36, 20, 42), font=f_peq)
    d.text((242, 294), "· Polillas de papel (apagan faroles)", fill=(36, 20, 42), font=f_peq)
    espejo(d, 260, 356)
    prisma(d, 330, 356, AMBAR)
    espejo(d, 398, 356)
    prisma(d, 330, 414, MALVA)
    # Rayos de luz conectando espejos y prismas
    d.line([(162, 378), (206, 356), (260, 356), (330, 356), (398, 356)], fill=AMBAR, width=3)
    d.line([(330, 356), (330, 414)], fill=MALVA, width=2)

    # Puente Oeste -> Centro
    d.rectangle([178, 336, 226, 370], fill=TERRAZA, outline=ORO)

    # 3. Pabellón del Té (Norte · Secreto + Farol 1)
    d.rounded_rectangle([228, 128, 448, 198], radius=12, fill=TERRAZA, outline=MALVA, width=2)
    etiqueta(d, 240, 136, "PABELLÓN DEL TÉ (SECRETO)", f_lbl, bg=(44, 22, 58), fg=MALVA, borde=MALVA)
    d.text((242, 166), "Celosía ilusoria · Farol + Cristal", fill=CREMA, font=f_peq)
    farol(d, 424, 174)
    d.rectangle([314, 198, 346, 236], fill=SOMBRA, outline=MALVA, width=2)

    # 4. Estanque de Papel (Sur · Farol 2)
    d.rounded_rectangle([216, 492, 466, 620], radius=12, fill=TERRAZA, outline=ORO, width=2)
    etiqueta(d, 232, 502, "ESTANQUE DE LOS REFLEJOS", f_lbl, bg=(42, 24, 50), fg=ORO)
    d.text((232, 532), "· Dos pasarelas gemelas: solo una real", fill=CREMA, font=f_peq)
    d.text((232, 550), "· Un rayo de prisma revela la falsa", fill=TEXTO_SUAVE, font=f_peq)
    d.text((232, 568), "· Farol de la Hora al final del muelle", fill=TEXTO_SUAVE, font=f_peq)
    farol(d, 438, 592)
    d.rectangle([314, 444, 346, 492], fill=TERRAZA_CLARA, outline=ORO)

    # 5. Invernadero de Cristal (Este · Jefe Mondo + Peso del Este + Farol 3)
    d.ellipse([484, 225, 676, 465], fill=TERRAZA_CLARA, outline=CORAL, width=3)
    etiqueta(d, 498, 248, "INVERNADERO · MONDO", f_lbl, bg=(56, 22, 42), fg=CORAL, borde=CORAL)
    d.text((504, 282), "· 4 espejos en las esquinas", fill=(36, 20, 42), font=f_peq)
    d.text((504, 300), "· Ilumina los reflejos para", fill=(36, 20, 42), font=f_peq)
    d.text((504, 318), "  descubrir al Mondo real", fill=(36, 20, 42), font=f_peq)
    espejo(d, 534, 360)
    espejo(d, 626, 360)
    espejo(d, 580, 420)
    farol(d, 580, 446)
    etiqueta(d, 492, 474, "Recompensa: Peso del Este + Farol", f_peq, bg=(46, 24, 44), fg=ORO)

    d.rectangle([434, 328, 484, 362], fill=TERRAZA, outline=CORAL, width=2)

    # Leyenda inferior
    d.rounded_rectangle([36, 664, 684, 742], radius=8, fill=(22, 15, 32), outline=BORDE)
    d.text((48, 672), "REGLAS PROPIAS DEL JARDÍN:", fill=ORO, font=f_lbl)
    d.text((48, 694), "1. Los PRISMAS dividen un rayo de espejo en dos colores: disipan muros ilusorios y delatan reflejos falsos.", fill=CREMA, font=f_peq)
    d.text((48, 714), "2. Las Polillas de Papel acuden a los espejos encendidos: un golpe o Resonancia las ahuyenta.", fill=TEXTO_SUAVE, font=f_peq)

    # --- PANEL DERECHO: OPCIONES DE JEFE MONDO ---
    d.rounded_rectangle([718, 78, 1180, 756], radius=10, fill=PANEL, outline=BORDE, width=2)
    d.text((736, 90), "JEFE DEL CAMINO ESTE · MONDO (2 OPCIONES)", fill=ORO, font=f_sub)

    d.rounded_rectangle([734, 122, 1164, 434], radius=8, fill=(34, 22, 48), outline=ORO, width=2)
    etiqueta(d, 746, 132, "[A] RECOMENDADA: Serval de Mil Reflejos", f_lbl, bg=(56, 36, 28), fg=ORO)
    dibujar_mondo_a(d, 948, 250)
    d.text((748, 338), "· Felino ágil de bronce y orejas de cristal dorado.", fill=CREMA, font=f_peq)
    d.text((748, 358), "· Se divide en 3 copias que saltan entre espejos.", fill=TEXTO_SUAVE, font=f_peq)
    d.text((748, 378), "· Clave: solo el real brilla con el rayo del espejo (los", fill=TEXTO_SUAVE, font=f_peq)
    d.text((748, 398), "  reflejos se esfuman al cruzar la luz) y cae aturdido.", fill=ORO_SUAVE, font=f_peq)

    d.rounded_rectangle([734, 450, 1164, 742], radius=8, fill=(30, 20, 44), outline=MALVA, width=2)
    etiqueta(d, 746, 460, "OPCIÓN B: Guardián del Farol Gigante", f_lbl, bg=(42, 22, 58), fg=MALVA, borde=MALVA)
    dibujar_mondo_b(d, 948, 566)
    d.text((748, 648), "· Serval blindado cargando un farol-jaula a la espalda.", fill=CREMA, font=f_peq)
    d.text((748, 668), "· Apaga el invernadero dejando solo un haz de luz.", fill=TEXTO_SUAVE, font=f_peq)
    d.text((748, 688), "· Clave: usar los espejos para devolverle su propio haz", fill=TEXTO_SUAVE, font=f_peq)
    d.text((748, 708), "  y agrietar la jaula con Carga Sísmica.", fill=MALVA, font=f_peq)

    out = os.path.join(RAIZ, "documentacion", "boceto_jardin_faroles.png")
    img.save(out)
    print("OK:", out)


if __name__ == "__main__":
    main()
