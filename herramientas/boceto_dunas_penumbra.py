"""Boceto del Camino Oeste de Jioni (Valle del Ocaso):
LAS DUNAS DE PENUMBRA + opciones de jefe KIVULI.
Sale en documentacion/boceto_dunas_penumbra.png (1200x780)."""
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
ARENA = (196, 128, 84)
ARENA_CLARA = (222, 158, 102)
ARENA_MOV = (96, 50, 76)
SOMBRA = (44, 22, 74)
MALVA = (196, 128, 246)
CORAL = (232, 118, 106)
CIAN = (122, 214, 234)


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


def vela_sombra(d, x, y):
    d.polygon([(x - 4, y + 10), (x - 4, y - 14), (x + 12, y - 4), (x - 4, y + 6)], fill=CORAL, outline=ORO)
    d.line([(x - 4, y - 16), (x - 4, y + 12)], fill=ORO, width=2)


def reloj_sol(d, x, y):
    d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(64, 36, 70), outline=ORO, width=2)
    d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 232, 146))


def farol(d, x, y):
    d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(90, 56, 36))
    d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 224, 122), outline=ORO)


def dibujar_kivuli_a(d, cx, cy):
    """Opción A: Kivuli, el Alacrán de Reloj de Arena."""
    # Halo de arena y sombra
    d.ellipse([cx - 88, cy - 34, cx + 88, cy + 56], fill=(38, 18, 60), outline=MALVA)
    # Patas articuladas de obsidiana
    for lado in (-1, 1):
        for dy in (-14, 0, 14):
            pts = [
                (cx + lado * 22, cy + dy),
                (cx + lado * 54, cy + dy - 10),
                (cx + lado * 74, cy + dy + 12),
            ]
            d.line(pts, fill=(84, 54, 112), width=5)
            d.line(pts, fill=MALVA, width=1)
    # Pinzas frontales
    for lado in (-1, 1):
        d.line([(cx + lado * 18, cy - 16), (cx + lado * 52, cy - 42)], fill=(92, 62, 122), width=7)
        d.pieslice([cx + lado * 52 - 18, cy - 60, cx + lado * 52 + 18, cy - 24],
                   20 if lado > 0 else 160, 320 if lado > 0 else 200, fill=(68, 38, 96), outline=ORO)
    # Cuerpo con reloj de arena dorado incrustado en el torso
    d.ellipse([cx - 28, cy - 26, cx + 28, cy + 28], fill=(48, 24, 72), outline=ORO, width=2)
    d.polygon([(cx - 14, cy - 16), (cx + 14, cy - 16), (cx, cy + 1)], fill=(255, 212, 114), outline=ORO)
    d.polygon([(cx - 12, cy + 18), (cx + 12, cy + 18), (cx, cy + 1)], fill=(142, 74, 188), outline=ORO)
    # Cola arqueada con aguijón solar
    cola = [(cx, cy + 24), (cx + 10, cy + 48), (cx + 38, cy + 44), (cx + 50, cy + 14), (cx + 26, cy - 52)]
    d.line(cola, fill=(68, 36, 98), width=11)
    d.line(cola, fill=ORO, width=2)
    d.polygon([(cx + 26, cy - 68), (cx + 18, cy - 48), (cx + 34, cy - 48)], fill=(255, 224, 128), outline=CORAL)
    # Ojos brillantes
    d.ellipse([cx - 12, cy - 22, cx - 5, cy - 16], fill=(255, 232, 148))
    d.ellipse([cx + 5, cy - 22, cx + 12, cy - 16], fill=(255, 232, 148))


def dibujar_kivuli_b(d, cx, cy):
    """Opción B: Kivuli, la Sombra Sin Cuerpo."""
    d.ellipse([cx - 86, cy - 26, cx + 86, cy + 48], fill=(26, 12, 46), outline=MALVA, width=2)
    # Zarcillos de sombra en el suelo
    for ang in range(0, 360, 45):
        r = math.radians(ang)
        d.line([(cx, cy + 8), (cx + math.cos(r) * 78, cy + 8 + math.sin(r) * 34)], fill=(72, 34, 112), width=6)
    # Silueta plana con núcleo luminoso expuesto
    d.polygon([(cx - 46, cy + 16), (cx - 26, cy - 24), (cx, cy - 38), (cx + 26, cy - 24), (cx + 46, cy + 16)],
              fill=(38, 18, 66), outline=MALVA)
    d.ellipse([cx - 18, cy - 12, cx + 18, cy + 18], fill=(255, 210, 112), outline=CREMA, width=2)
    d.ellipse([cx - 8, cy - 4, cx + 8, cy + 10], fill=(255, 246, 200))


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    f_tit = fuente(24)
    f_sub = fuente(15)
    f_lbl = fuente(13)
    f_peq = fuente(12)

    # Cabecera
    d.rectangle([0, 0, W, 62], fill=(28, 18, 42))
    d.line([(0, 62), (W, 62)], fill=ORO, width=2)
    d.text((24, 12), "VALLE DEL OCASO · CAMINO OESTE: LAS DUNAS DE PENUMBRA", fill=ORO, font=f_tit)
    d.text((24, 40), "Salida oeste de Jioni · Ambiente: viento_arena · Mecánica: Velas de Sombra sobre arenas movedizas + 3 Faroles + Peso del Oeste", fill=TEXTO_SUAVE, font=f_peq)

    # --- PANEL IZQUIERDO: TRAZADO JUGABLE (x=20..700, y=78..756) ---
    d.rounded_rectangle([20, 78, 700, 756], radius=10, fill=PANEL, outline=BORDE, width=2)
    d.text((36, 90), "TRAZADO DE LA ZONA (74 × 54 casillas aprox.)", fill=ORO, font=f_sub)

    # Fondo de arenas movedizas / mar de dunas
    d.rounded_rectangle([36, 118, 684, 650], radius=8, fill=ARENA_MOV, outline=(96, 62, 108))
    # Dunas onduladas decorativas
    for yy in range(150, 635, 36):
        pts = [(42 + x, yy + int(math.sin(x * 0.03 + yy) * 6)) for x in range(0, 636, 24)]
        d.line(pts, fill=(116, 64, 92), width=2)

    # 1. Entrada desde Jioni (Este)
    d.rounded_rectangle([545, 285, 676, 405], radius=10, fill=ARENA, outline=ORO, width=2)
    etiqueta(d, 554, 294, "< Desde Jioni", f_lbl, bg=(44, 24, 52), fg=ORO)
    d.text((555, 326), "1.er Reloj de Sol", fill=CREMA, font=f_peq)
    d.text((555, 344), "y Vela de prueba", fill=TEXTO_SUAVE, font=f_peq)
    reloj_sol(d, 608, 380)

    # 2. Duna Central (Meseta de las Velas)
    d.rounded_rectangle([305, 255, 470, 425], radius=12, fill=ARENA_CLARA, outline=ORO, width=2)
    etiqueta(d, 316, 264, "MESETA DE LAS VELAS", f_lbl, bg=(42, 24, 50), fg=ORO)
    d.text((318, 294), "· 2 Velas giratorias", fill=(36, 20, 42), font=f_peq)
    d.text((318, 312), "· 2 Kivuli excavadores", fill=(36, 20, 42), font=f_peq)
    d.text((318, 330), "· Espejo enterrado", fill=(36, 20, 42), font=f_peq)
    vela_sombra(d, 448, 352)
    vela_sombra(d, 388, 368)
    vela_sombra(d, 388, 406)
    reloj_sol(d, 338, 384)

    # Sombra-puente Este -> Centro
    d.rectangle([470, 322, 545, 358], fill=SOMBRA, outline=ORO, width=2)
    d.text((476, 334), "Sombra", fill=CREMA, font=f_peq)

    # 3. Oasis de la Sombra (Norte · Secreto + Farol 1)
    d.rounded_rectangle([310, 128, 466, 208], radius=12, fill=ARENA, outline=MALVA, width=2)
    etiqueta(d, 320, 136, "OASIS SECRETO", f_lbl, bg=(44, 22, 58), fg=MALVA, borde=MALVA)
    d.text((322, 166), "Farol secreto + Cristal", fill=CREMA, font=f_peq)
    farol(d, 444, 184)
    d.rectangle([364, 208, 396, 255], fill=SOMBRA, outline=MALVA, width=2)

    # 4. Cañón de los Espejos (Sur · Farol 2 + atajo)
    d.rounded_rectangle([282, 488, 542, 622], radius=12, fill=ARENA, outline=ORO, width=2)
    etiqueta(d, 298, 498, "CAÑÓN DE LOS ESPEJOS", f_lbl, bg=(42, 24, 50), fg=ORO)
    d.text((298, 528), "· 2 espejos semienterrados (Carga)", fill=CREMA, font=f_peq)
    d.text((298, 546), "· Cruza el rayo solar para abrir paso", fill=TEXTO_SUAVE, font=f_peq)
    d.text((298, 564), "  al Cráter del Alacrán + Farol", fill=TEXTO_SUAVE, font=f_peq)
    farol(d, 514, 594)
    d.rectangle([364, 425, 396, 488], fill=SOMBRA, outline=ORO, width=2)

    # 5. Cráter del Alacrán (Oeste · Jefe Kivuli + Peso del Oeste + Farol 3)
    d.ellipse([48, 225, 248, 465], fill=ARENA_CLARA, outline=CORAL, width=3)
    etiqueta(d, 68, 248, "ARENA DE KIVULI (JEFE)", f_lbl, bg=(56, 22, 42), fg=CORAL, borde=CORAL)
    d.text((70, 282), "· 3 Relojes de Sol en triángulo", fill=(36, 20, 42), font=f_peq)
    d.text((70, 300), "· Gira el sol para sacar a", fill=(36, 20, 42), font=f_peq)
    d.text((70, 318), "  Kivuli de su sombra", fill=(36, 20, 42), font=f_peq)
    reloj_sol(d, 148, 360)
    reloj_sol(d, 96, 412)
    reloj_sol(d, 200, 412)
    farol(d, 148, 444)
    etiqueta(d, 64, 474, "Recompensa: Peso del Oeste + Farol", f_peq, bg=(46, 24, 44), fg=ORO)

    # Puente Centro -> Jefe
    d.rectangle([246, 322, 305, 358], fill=SOMBRA, outline=CORAL, width=2)

    # Leyenda inferior izquierda
    d.rounded_rectangle([36, 664, 684, 742], radius=8, fill=(22, 15, 32), outline=BORDE)
    d.text((48, 672), "REGLAS PROPIAS DE LAS DUNAS:", fill=ORO, font=f_lbl)
    d.text((48, 694), "1. Las arenas movedizas hunden a Maisha salvo sobre la sombra larga de una VELA DE SOMBRA.", fill=CREMA, font=f_peq)
    d.text((48, 714), "2. Golpear una Vela la gira 90°; girar un Reloj cambia el sol y mueve todas las sombras a la vez.", fill=TEXTO_SUAVE, font=f_peq)

    # --- PANEL DERECHO: OPCIONES DE JEFE KIVULI (x=718..1180, y=78..756) ---
    d.rounded_rectangle([718, 78, 1180, 756], radius=10, fill=PANEL, outline=BORDE, width=2)
    d.text((736, 90), "JEFE DEL CAMINO OESTE · KIVULI (2 OPCIONES)", fill=ORO, font=f_sub)

    # Opción A
    d.rounded_rectangle([734, 122, 1164, 434], radius=8, fill=(34, 22, 48), outline=ORO, width=2)
    etiqueta(d, 746, 132, "[A] RECOMENDADA: Alacrán de Reloj de Arena", f_lbl, bg=(56, 36, 28), fg=ORO)
    dibujar_kivuli_a(d, 948, 250)
    d.text((748, 338), "· Obsidiana + vientre de reloj de arena dorado.", fill=CREMA, font=f_peq)
    d.text((748, 358), "· Fase 1: se hunde en su sombra y acecha bajo la arena.", fill=TEXTO_SUAVE, font=f_peq)
    d.text((748, 378), "· Clave: gira el Reloj de Sol para que le dé el rayo de lleno;", fill=TEXTO_SUAVE, font=f_peq)
    d.text((748, 398), "  al deslumbrarse se vuelca y deja el reloj expuesto.", fill=ORO_SUAVE, font=f_peq)

    # Opción B
    d.rounded_rectangle([734, 450, 1164, 742], radius=8, fill=(30, 20, 44), outline=MALVA, width=2)
    etiqueta(d, 746, 460, "OPCIÓN B: La Sombra Sin Cuerpo", f_lbl, bg=(42, 22, 58), fg=MALVA, borde=MALVA)
    dibujar_kivuli_b(d, 948, 566)
    d.text((748, 648), "· Sombra plana gigante que corre por las dunas.", fill=CREMA, font=f_peq)
    d.text((748, 668), "· Absorbe las velas para hacerse más grande.", fill=TEXTO_SUAVE, font=f_peq)
    d.text((748, 688), "· Clave: orientar 2 espejos de bronce hacia el centro", fill=TEXTO_SUAVE, font=f_peq)
    d.text((748, 708), "  para encerrar su núcleo solar y golpearlo.", fill=MALVA, font=f_peq)

    out = os.path.join(RAIZ, "documentacion", "boceto_dunas_penumbra.png")
    img.save(out)
    print("OK:", out)


if __name__ == "__main__":
    main()
