"""Boceto del clímax final del Valle del Ocaso (y del juego):
EL HORIZONTE INMÓVIL + JUA-GIZA, EL SOL ENCADENADO (Opción A aprobada por Iam).
Sale en documentacion/boceto_horizonte_inmovil.png (1200x780)."""
import math
import os
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 780

FONDO = (18, 12, 28)
PANEL = (26, 18, 40)
BORDE = (132, 90, 140)
ORO = (248, 200, 112)
ORO_SUAVE = (214, 166, 92)
CREMA = (248, 236, 208)
TEXTO_SUAVE = (208, 192, 218)
CALZADA = (164, 102, 88)
CALZADA_CLARA = (192, 126, 100)
ABISMO = (26, 14, 46)
SOMBRA = (44, 20, 76)
MALVA = (196, 130, 246)
CORAL = (234, 122, 108)
NOCHE = (20, 28, 58)
ESTRELLA = (255, 246, 204)


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


def dibujar_jua_giza(d, cx, cy):
    """Jua-Giza, el Sol Encadenado (Opción A aprobada por Iam)."""
    # Halo de atardecer y grietas de Giza
    d.ellipse([cx - 92, cy - 92, cx + 92, cy + 92], fill=(44, 20, 56), outline=MALVA)
    # 3 anillos de relojería cruzados
    d.ellipse([cx - 82, cy - 38, cx + 82, cy + 38], outline=ORO, width=3)
    d.ellipse([cx - 38, cy - 82, cx + 38, cy + 82], outline=ORO_SUAVE, width=2)
    d.ellipse([cx - 66, cy - 66, cx + 66, cy + 66], outline=CORAL, width=2)
    # 3 cadenas con pesos (Oeste, Este, Sur)
    for dx, dy, lbl in ((-112, 22, "P1"), (112, 22, "P2"), (0, 102, "P3")):
        d.line([(cx + dx * 0.45, cy + dy * 0.45), (cx + dx, cy + dy)], fill=ORO, width=3)
        d.rounded_rectangle([cx + dx - 14, cy + dy - 10, cx + dx + 14, cy + dy + 12],
                            radius=4, fill=(72, 46, 84), outline=ORO, width=2)
        d.text((cx + dx - 8, cy + dy - 6), lbl, fill=ORO, font=fuente(11))
    # Disco solar central agrietado de púrpura
    d.ellipse([cx - 44, cy - 44, cx + 44, cy + 44], fill=(248, 178, 84), outline=CREMA, width=2)
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=(255, 224, 134))
    # Grietas violetas de Giza (miedo a la noche)
    d.line([(cx - 32, cy - 18), (cx - 8, cy - 4), (cx - 18, cy + 22)], fill=(76, 26, 118), width=4)
    d.line([(cx + 28, cy - 12), (cx + 6, cy + 4), (cx + 22, cy + 26)], fill=(76, 26, 118), width=4)
    # Ojo sereno en el centro
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(42, 18, 62), outline=ORO, width=2)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=ESTRELLA)


def dibujar_primera_noche(d, x0, y0, x1, y1):
    """Miniatura del epílogo: la Primera Noche sobre el Valle del Ocaso."""
    d.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=NOCHE, outline=ORO_SUAVE, width=2)
    # Estrellas
    for sx, sy, r in (
        (x0 + 36, y0 + 28, 2), (x0 + 92, y0 + 20, 1), (x0 + 148, y0 + 34, 2),
        (x0 + 216, y0 + 22, 2), (x0 + 288, y0 + 30, 1), (x0 + 340, y0 + 24, 2),
        (x0 + 70, y0 + 44, 1), (x0 + 186, y0 + 40, 1), (x0 + 312, y0 + 42, 2),
    ):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=ESTRELLA)
    # Luna creciente cálida
    mx, my = x1 - 52, y0 + 34
    d.ellipse([mx - 14, my - 14, mx + 14, my + 14], fill=ESTRELLA)
    d.ellipse([mx - 7, my - 16, mx + 18, my + 12], fill=NOCHE)
    # Horizonte con silueta de Jioni y 12 farolillos encendidos
    d.rectangle([x0 + 2, y1 - 36, x1 - 2, y1 - 2], fill=(28, 20, 44))
    for i in range(12):
        fx = x0 + 26 + i * ((x1 - x0 - 52) / 11.0)
        fy = y1 - 24 - (4 if i % 2 else 0)
        d.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], fill=(96, 64, 34))
        d.ellipse([fx - 2, fy - 2, fx + 2, fy + 2], fill=ORO)
    d.text((x0 + 14, y0 + 56), "EPÍLOGO · LA PRIMERA NOCHE", fill=ORO, font=fuente(13))
    d.text((x0 + 14, y0 + 76), "El sol descansa, Giza se disuelve y Jioni duerme en paz.", fill=CREMA, font=fuente(12))


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    f_tit = fuente(24)
    f_sub = fuente(15)
    f_lbl = fuente(13)
    f_peq = fuente(12)

    d.rectangle([0, 0, W, 62], fill=(28, 18, 42))
    d.line([(0, 62), (W, 62)], fill=ORO, width=2)
    d.text((24, 12), "VALLE DEL OCASO · CLÍMAX FINAL: EL HORIZONTE INMÓVIL", fill=ORO, font=f_tit)
    d.text((24, 40), "Tras la Puerta del Horizonte (3 Pesas: Oeste, Este, Sur) · Jefe final: Jua-Giza, el Sol Encadenado · Cierre del juego", fill=TEXTO_SUAVE, font=f_peq)

    # --- PANEL IZQUIERDO: TRAZADO DEL HORIZONTE INMÓVIL ---
    d.rounded_rectangle([20, 78, 690, 756], radius=10, fill=PANEL, outline=BORDE, width=2)
    d.text((36, 90), "TRAZADO DE LA ESCENA FINAL (66 × 58 casillas aprox.)", fill=ORO, font=f_sub)

    d.rounded_rectangle([36, 118, 674, 646], radius=8, fill=ABISMO, outline=(96, 62, 108))
    # Gradiente sutil de horizonte ardiente al sur
    for band in range(6):
        yy = 490 + band * 26
        col = (64 + band * 16, 26 + band * 10, 66 - band * 4)
        d.rectangle([38, yy, 672, min(644, yy + 26)], fill=col)

    # 1. Umbral del Crepúsculo (Norte, desde Jioni)
    d.rounded_rectangle([244, 130, 466, 212], radius=10, fill=CALZADA, outline=ORO, width=2)
    etiqueta(d, 258, 138, "v Desde la Puerta del Horizonte", f_lbl, bg=(44, 24, 52), fg=ORO)
    d.text((260, 168), "· Mauti espera a Maisha junto al borde", fill=CREMA, font=f_peq)
    d.text((260, 186), "· Los 3 Pesos encajan en el pedestal", fill=TEXTO_SUAVE, font=f_peq)

    # 2. Pasarela de los Tres Ecos (breve repaso poético)
    d.rectangle([332, 212, 378, 250], fill=SOMBRA, outline=ORO, width=2)
    d.rounded_rectangle([118, 250, 592, 344], radius=12, fill=CALZADA_CLARA, outline=ORO, width=2)
    etiqueta(d, 134, 258, "PASARELA DE LOS TRES PESOS (Repaso final antes del Sol)", f_lbl, bg=(42, 24, 50), fg=ORO)
    d.text((136, 288), "1. Oeste: Vela + Sombra    2. Centro: Espejo + Prisma    3. Este: Reloj + Obelisco", fill=(34, 18, 40), font=f_peq)
    d.text((136, 308), "Cada paso enciende un pilar dorado y calma el puente hacia el Sol Encadenado.", fill=(48, 26, 52), font=f_peq)

    # 3. Gran Altar del Sol Encadenado (Sur)
    d.rectangle([330, 344, 380, 388], fill=SOMBRA, outline=CORAL, width=2)
    d.ellipse([110, 384, 600, 624], fill=CALZADA_CLARA, outline=ORO, width=3)
    etiqueta(d, 208, 400, "ALTAR DEL SOL ENCADENADO · JUA-GIZA", f_lbl, bg=(56, 22, 42), fg=ORO, borde=ORO)
    # 3 estaciones alrededor del altar
    for px, py, txt in (
        (160, 502, "Cadena Oeste\n(Vela + Carga)"),
        (548, 502, "Cadena Este\n(Espejos + Luz)"),
        (355, 588, "Cadena Sur · Mauti + Maisha"),
    ):
        d.ellipse([px - 14, py - 14, px + 14, py + 14], fill=(56, 32, 68), outline=ORO, width=2)
    d.text((126, 522), "Pesa Oeste", fill=(36, 20, 42), font=f_peq)
    d.text((514, 522), "Pesa Este", fill=(36, 20, 42), font=f_peq)
    d.text((294, 558), "Pesa Sur + Reloj de Sol", fill=(36, 20, 42), font=f_peq)
    # Sol en el centro de la arena
    d.ellipse([325, 452, 385, 512], fill=(248, 188, 92), outline=CORAL, width=3)
    d.text((336, 474), "SOL", fill=(48, 22, 46), font=f_lbl)

    # Nota narrativa inferior izquierda
    d.rounded_rectangle([36, 660, 674, 742], radius=8, fill=(22, 15, 32), outline=BORDE)
    d.text((48, 668), "CLÍMAX NARRATIVO (OJO: GÉNERO NEUTRO PARA MAISHA Y MAUTI):", fill=ORO, font=f_lbl)
    d.text((48, 690), "· Giza no es un monstruo externo: nació del miedo de los habitantes a que el día terminara.", fill=CREMA, font=f_peq)
    d.text((48, 710), "· No se destruye al Sol: Maisha y Mauti sueltan las 3 cadenas para que la noche llegue sin miedo.", fill=TEXTO_SUAVE, font=f_peq)

    # --- PANEL DERECHO: JUA-GIZA Y SUS 3 FASES + EPÍLOGO ---
    d.rounded_rectangle([708, 78, 1180, 756], radius=10, fill=PANEL, outline=BORDE, width=2)
    d.text((726, 90), "JEFE FINAL · JUA-GIZA (OPCIÓN A APROBADA)", fill=ORO, font=f_sub)

    d.rounded_rectangle([724, 122, 1164, 378], radius=8, fill=(34, 22, 48), outline=ORO, width=2)
    dibujar_jua_giza(d, 944, 242)

    d.rounded_rectangle([724, 392, 1164, 594], radius=8, fill=(30, 20, 44), outline=MALVA, width=2)
    etiqueta(d, 738, 402, "3 FASES DE COMBATE (12 de vida / 3 cadenas)", f_lbl, bg=(46, 24, 56), fg=ORO)
    d.text((738, 434), "1. CADENA DEL OESTE (Sombra): cúbrete tras el obelisco ante la", fill=CREMA, font=f_peq)
    d.text((748, 452), "llamarada solar y rompe el contrapeso con Carga Sísmica.", fill=TEXTO_SUAVE, font=f_peq)
    d.text((738, 476), "2. CADENA DEL ESTE (Luz): orienta los 2 espejos del borde hacia", fill=CREMA, font=f_peq)
    d.text((748, 494), "Jua-Giza para disipar el velo de Giza y golpear el broche.", fill=TEXTO_SUAVE, font=f_peq)
    d.text((738, 518), "3. CADENA DEL SUR (Calma): olas de penumbra y rayos cruzados;", fill=CREMA, font=f_peq)
    d.text((748, 536), "al soltar la 3.ª cadena, Mauti llega y calman el núcleo a la par", fill=TEXTO_SUAVE, font=f_peq)
    d.text((748, 554), "con el Cetro del Nexo (sin matar: el sol por fin baja).", fill=ORO_SUAVE, font=f_peq)

    dibujar_primera_noche(d, 724, 608, 1164, 742)

    out = os.path.join(RAIZ, "documentacion", "boceto_horizonte_inmovil.png")
    img.save(out)
    print("OK:", out)


if __name__ == "__main__":
    main()
