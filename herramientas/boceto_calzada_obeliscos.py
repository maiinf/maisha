"""Boceto del Camino Sureste de Jioni (Valle del Ocaso):
LA CALZADA DE LOS OBELISCOS + opciones de jefe SAA-MCHANGA.
Sale en documentacion/boceto_calzada_obeliscos.png (1200x780)."""
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
CALZADA = (164, 100, 86)
CALZADA_CLARA = (190, 122, 98)
ABISMO = (28, 16, 46)
SOMBRA = (44, 20, 74)
MALVA = (196, 128, 246)
CORAL = (232, 118, 106)
AMBAR = (255, 214, 108)


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


def obelisco(d, x, y):
    d.polygon([(x - 8, y + 8), (x - 6, y - 14), (x, y - 22), (x + 6, y - 14), (x + 8, y + 8)],
              fill=(86, 52, 92), outline=ORO)
    d.ellipse([x - 3, y - 9, x + 3, y - 3], fill=AMBAR)


def reloj_sol(d, x, y):
    d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(64, 36, 70), outline=ORO, width=2)
    d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 232, 146))


def farol(d, x, y):
    d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(94, 56, 36))
    d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=AMBAR, outline=ORO)


def dibujar_saa_a(d, cx, cy):
    """Opción A: Saa-Mchanga, el Autómata Reloj de Arena."""
    # Aro exterior de engranaje dorado
    d.ellipse([cx - 64, cy - 64, cx + 64, cy + 64], outline=ORO, width=3)
    for ang in range(0, 360, 30):
        r = math.radians(ang)
        d.line([(cx + math.cos(r) * 60, cy + math.sin(r) * 60),
                (cx + math.cos(r) * 72, cy + math.sin(r) * 72)], fill=ORO, width=3)
    # Dos pilares laterales de bronce
    d.rectangle([cx - 42, cy - 52, cx - 32, cy + 52], fill=(104, 72, 54), outline=ORO)
    d.rectangle([cx + 32, cy - 52, cx + 42, cy + 52], fill=(104, 72, 54), outline=ORO)
    d.rectangle([cx - 48, cy - 58, cx + 48, cy - 48], fill=(124, 86, 62), outline=ORO)
    d.rectangle([cx - 48, cy + 48, cx + 48, cy + 58], fill=(124, 86, 62), outline=ORO)
    # Ampollas de cristal: arriba sol dorado, abajo sombra violeta
    d.polygon([(cx - 28, cy - 48), (cx + 28, cy - 48), (cx, cy)], fill=AMBAR, outline=CREMA)
    d.polygon([(cx - 28, cy + 48), (cx + 28, cy + 48), (cx, cy)], fill=(110, 52, 166), outline=CREMA)
    # Ojo central en el cuello del reloj
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(42, 20, 56), outline=ORO, width=2)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 240, 178))


def dibujar_saa_b(d, cx, cy):
    """Opción B: Saa-Mchanga, el Péndulo Doble."""
    # Eje superior
    d.line([(cx - 72, cy - 54), (cx + 72, cy - 54)], fill=ORO, width=4)
    d.ellipse([cx - 12, cy - 66, cx + 12, cy - 42], fill=(92, 62, 52), outline=ORO, width=2)
    # Dos brazos oscilantes (sol a la izquierda, sombra a la derecha)
    d.line([(cx, cy - 54), (cx - 56, cy + 22)], fill=ORO, width=4)
    d.line([(cx, cy - 54), (cx + 56, cy + 22)], fill=MALVA, width=4)
    d.ellipse([cx - 78, cy + 4, cx - 34, cy + 48], fill=AMBAR, outline=CREMA, width=2)
    d.ellipse([cx + 34, cy + 4, cx + 78, cy + 48], fill=(64, 28, 102), outline=MALVA, width=2)
    d.text((cx - 67, cy + 19), "SOL", fill=(48, 28, 22), font=fuente(11))
    d.text((cx + 38, cy + 19), "SOM", fill=CREMA, font=fuente(11))


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    f_tit = fuente(24)
    f_sub = fuente(15)
    f_lbl = fuente(13)
    f_peq = fuente(12)

    d.rectangle([0, 0, W, 62], fill=(28, 18, 42))
    d.line([(0, 62), (W, 62)], fill=ORO, width=2)
    d.text((24, 12), "VALLE DEL OCASO · CAMINO SURESTE: LA CALZADA DE LOS OBELISCOS", fill=ORO, font=f_tit)
    d.text((24, 40), "Salida sureste de Jioni · Mecánica: Sombras encadenadas sobre abismo + Centinelas de sombra + 3 Faroles + Peso del Sur", fill=TEXTO_SUAVE, font=f_peq)

    # --- PANEL IZQUIERDO: TRAZADO JUGABLE ---
    d.rounded_rectangle([20, 78, 700, 756], radius=10, fill=PANEL, outline=BORDE, width=2)
    d.text((36, 90), "TRAZADO DE LA ZONA (72 × 56 casillas aprox.)", fill=ORO, font=f_sub)

    d.rounded_rectangle([36, 118, 684, 650], radius=8, fill=ABISMO, outline=(96, 62, 108))
    # Nubes de atardecer en el abismo
    for cx, cy, rx, ry in ((150, 240, 80, 18), (480, 210, 96, 20), (240, 500, 110, 22), (560, 440, 70, 16)):
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(64, 30, 62))

    # 1. Entrada desde Jioni (Noroeste)
    d.rounded_rectangle([54, 134, 214, 232], radius=10, fill=CALZADA, outline=ORO, width=2)
    etiqueta(d, 64, 142, "v Desde Jioni (SE)", f_lbl, bg=(44, 24, 52), fg=ORO)
    d.text((66, 174), "1.er Obelisco + Reloj", fill=CREMA, font=f_peq)
    obelisco(d, 190, 198)
    reloj_sol(d, 112, 208)

    # 2. Islas-Pilar encadenadas (Centro-Norte)
    d.rounded_rectangle([290, 152, 396, 242], radius=10, fill=CALZADA_CLARA, outline=ORO, width=2)
    obelisco(d, 344, 210)
    d.text((302, 160), "Pilar I", fill=(36, 20, 42), font=f_lbl)

    d.rounded_rectangle([476, 152, 660, 266], radius=10, fill=CALZADA, outline=ORO, width=2)
    etiqueta(d, 486, 160, "BALCÓN DEL MEDIODÍA", f_lbl, bg=(42, 24, 50), fg=MALVA, borde=MALVA)
    d.text((488, 190), "· Secreto + Farol 1", fill=CREMA, font=f_peq)
    d.text((488, 208), "· Reloj de Sol 2", fill=TEXTO_SUAVE, font=f_peq)
    farol(d, 634, 238)
    reloj_sol(d, 524, 242)

    # Sombras horizontales encadenadas (Sol al Oeste)
    d.rectangle([214, 184, 290, 214], fill=SOMBRA, outline=ORO, width=2)
    d.rectangle([396, 184, 476, 214], fill=SOMBRA, outline=ORO, width=2)

    # 3. Tramo de los Centinelas (Centro)
    d.rounded_rectangle([232, 304, 504, 412], radius=12, fill=CALZADA_CLARA, outline=ORO, width=2)
    etiqueta(d, 248, 314, "VIADUCTO DE LOS CENTINELAS", f_lbl, bg=(42, 24, 50), fg=ORO)
    d.text((248, 344), "· 2 Centinelas de Reloj (avanzan en sombra,", fill=(36, 20, 42), font=f_peq)
    d.text((248, 362), "  se detienen al girar el sol sobre ellos)", fill=(36, 20, 42), font=f_peq)
    obelisco(d, 344, 392)
    reloj_sol(d, 444, 384)
    farol(d, 272, 392)
    # Sombra vertical (Sol al Sur) desde Pilar I -> Viaducto
    d.rectangle([328, 242, 360, 304], fill=SOMBRA, outline=MALVA, width=2)

    # 4. Rotonda de los Péndulos (Sur · Jefe Saa-Mchanga + Peso del Sur + Farol 3)
    d.ellipse([212, 466, 512, 636], fill=CALZADA_CLARA, outline=CORAL, width=3)
    etiqueta(d, 252, 480, "ROTONDA · SAA-MCHANGA (JEFE)", f_lbl, bg=(56, 22, 42), fg=CORAL, borde=CORAL)
    d.text((256, 510), "· 4 Obeliscos rodeando al coloso", fill=(36, 20, 42), font=f_peq)
    d.text((256, 528), "· Refúgiate en su sombra ante el barrido", fill=(36, 20, 42), font=f_peq)
    obelisco(d, 268, 574)
    obelisco(d, 456, 574)
    reloj_sol(d, 362, 594)
    farol(d, 362, 622)
    etiqueta(d, 46, 588, "Recompensa: Peso del Sur + Farol", f_peq, bg=(46, 24, 44), fg=ORO)
    # Sombra vertical Viaducto -> Rotonda
    d.rectangle([346, 412, 378, 466], fill=SOMBRA, outline=CORAL, width=2)

    # Leyenda inferior
    d.rounded_rectangle([36, 664, 684, 742], radius=8, fill=(22, 15, 32), outline=BORDE)
    d.text((48, 672), "REGLAS PROPIAS DE LA CALZADA:", fill=ORO, font=f_lbl)
    d.text((48, 694), "1. Varios obeliscos se encadenan sobre el abismo: girar el sol abre un tramo y cierra el anterior.", fill=CREMA, font=f_peq)
    d.text((48, 714), "2. Los Centinelas de Reloj solo se mueven en penumbra; el sol directo los congela como estatuas.", fill=TEXTO_SUAVE, font=f_peq)

    # --- PANEL DERECHO: OPCIONES DE JEFE SAA-MCHANGA ---
    d.rounded_rectangle([718, 78, 1180, 756], radius=10, fill=PANEL, outline=BORDE, width=2)
    d.text((736, 90), "JEFE DEL CAMINO SURESTE · SAA-MCHANGA", fill=ORO, font=f_sub)

    d.rounded_rectangle([734, 122, 1164, 434], radius=8, fill=(34, 22, 48), outline=ORO, width=2)
    etiqueta(d, 746, 132, "[A] RECOMENDADA: Autómata Reloj de Arena", f_lbl, bg=(56, 36, 28), fg=ORO)
    dibujar_saa_a(d, 948, 250)
    d.text((748, 338), "· Coloso de bronce y dos ampollas (sol arriba, sombra abajo).", fill=CREMA, font=f_peq)
    d.text((748, 358), "· Barre la rotonda con rayos solares: cúbrete tras obeliscos.", fill=TEXTO_SUAVE, font=f_peq)
    d.text((748, 378), "· Clave: al vaciarse su arena se inclina; una Carga Sísmica", fill=TEXTO_SUAVE, font=f_peq)
    d.text((748, 398), "  o girar el Reloj lo vuelca y rompe su aro de relojería.", fill=ORO_SUAVE, font=f_peq)

    d.rounded_rectangle([734, 450, 1164, 742], radius=8, fill=(30, 20, 44), outline=MALVA, width=2)
    etiqueta(d, 746, 460, "OPCIÓN B: El Péndulo Doble", f_lbl, bg=(42, 22, 58), fg=MALVA, borde=MALVA)
    dibujar_saa_b(d, 948, 566)
    d.text((748, 648), "· Dos pesas gigantes (Sol y Sombra) oscilan sobre la rotonda.", fill=CREMA, font=f_peq)
    d.text((748, 668), "· Cada oscilación cambia qué mitad del suelo es luz o sombra.", fill=TEXTO_SUAVE, font=f_peq)
    d.text((748, 688), "· Clave: usar Pulso Magnético / Resonancia para desfasar", fill=TEXTO_SUAVE, font=f_peq)
    d.text((748, 708), "  las pesas hasta que choquen entre sí en el centro.", fill=MALVA, font=f_peq)

    out = os.path.join(RAIZ, "documentacion", "boceto_calzada_obeliscos.png")
    img.save(out)
    print("OK:", out)


if __name__ == "__main__":
    main()
