"""Boceto de Jioni parte 2:
EL MERCADO DEL CREPÚSCULO (tienda de Kikombe con 4 artículos + precios) y opciones de cierre del diario.
Sale en documentacion/boceto_mercado_crepusculo.png (1200x780)."""
import os
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 780

FONDO = (20, 14, 28)
PANEL = (28, 20, 40)
BORDE = (128, 86, 134)
ORO = (248, 200, 112)
ORO_SUAVE = (214, 166, 92)
CREMA = (248, 236, 208)
TEXTO_SUAVE = (208, 192, 218)
MALVA = (196, 130, 246)
CORAL = (234, 122, 108)
AMBAR = (255, 214, 108)
CIAN = (124, 212, 234)


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


def icono_articulo(d, cx, cy, tipo):
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(42, 26, 56), outline=ORO, width=2)
    if tipo == "reloj":
        d.ellipse([cx - 14, cy - 12, cx + 14, cy + 16], fill=(186, 134, 62), outline=CREMA, width=2)
        d.ellipse([cx - 10, cy - 8, cx + 10, cy + 12], fill=(248, 234, 196))
        d.line([(cx, cy + 2), (cx, cy - 5)], fill=(54, 30, 26), width=2)
        d.line([(cx, cy + 2), (cx + 6, cy + 4)], fill=(54, 30, 26), width=2)
        d.rectangle([cx - 4, cy - 18, cx + 4, cy - 12], fill=ORO)
    elif tipo == "lente":
        d.polygon([(cx, cy - 16), (cx + 14, cy + 2), (cx, cy + 18), (cx - 14, cy + 2)], fill=MALVA, outline=CREMA)
        d.polygon([(cx, cy - 10), (cx + 8, cy + 2), (cx, cy + 12), (cx - 8, cy + 2)], fill=AMBAR)
    elif tipo == "botas":
        d.rounded_rectangle([cx - 16, cy - 6, cx - 2, cy + 14], radius=3, fill=(168, 98, 66), outline=ORO)
        d.rounded_rectangle([cx + 2, cy - 6, cx + 16, cy + 14], radius=3, fill=(168, 98, 66), outline=ORO)
        d.line([(cx - 16, cy + 12), (cx - 2, cy + 12)], fill=AMBAR, width=3)
        d.line([(cx + 2, cy + 12), (cx + 16, cy + 12)], fill=AMBAR, width=3)
    elif tipo == "capa":
        d.polygon([(cx - 10, cy - 14), (cx + 10, cy - 14), (cx + 18, cy + 16), (cx - 18, cy + 16)],
                  fill=(34, 38, 86), outline=ORO)
        d.ellipse([cx + 6, cy + 2, cx + 14, cy + 10], fill=AMBAR, outline=CREMA)


def dibujar_interior_puesto(d, x0, y0, x1, y1):
    """Vista del puesto de Kikombe por dentro (estilo tienda_tawi.gd / tienda_chuma)."""
    d.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=(44, 24, 52), outline=ORO, width=2)
    # Toldo a rayas arriba
    ancho = x1 - x0 - 16
    franjas = 8
    fw = ancho / franjas
    for i in range(franjas):
        col = (224, 182, 128) if i % 2 == 0 else (178, 86, 78)
        d.rectangle([x0 + 8 + i * fw, y0 + 8, x0 + 8 + (i + 1) * fw, y0 + 44], fill=col)
    # Faroles colgantes
    for fx in (x0 + 70, x0 + 210, x1 - 70):
        d.line([(fx, y0 + 44), (fx, y0 + 54)], fill=ORO, width=2)
        d.ellipse([fx - 10, y0 + 52, fx + 10, y0 + 76], fill=AMBAR, outline=CREMA, width=2)
    # Estantes con jarras de té y relojes
    d.rectangle([x0 + 36, y0 + 114, x1 - 36, y0 + 124], fill=(104, 64, 46), outline=ORO_SUAVE)
    for jx, jcol in ((x0 + 68, AMBAR), (x0 + 112, CORAL), (x0 + 156, MALVA), (x1 - 112, CIAN), (x1 - 68, AMBAR)):
        d.ellipse([jx - 11, y0 + 92, jx + 11, y0 + 114], fill=jcol, outline=CREMA)
    # Kikombe (fénec descansado, sonriendo tras el mostrador)
    kx, ky = (x0 + x1) // 2, y0 + 162
    d.polygon([(kx - 16, ky - 14), (kx - 36, ky - 46), (kx - 4, ky - 22)], fill=(214, 152, 102), outline=ORO)
    d.polygon([(kx + 16, ky - 14), (kx + 36, ky - 46), (kx + 4, ky - 22)], fill=(214, 152, 102), outline=ORO)
    d.ellipse([kx - 22, ky - 24, kx + 22, ky + 14], fill=(226, 168, 118), outline=ORO)
    d.ellipse([kx - 10, ky - 10, kx - 5, ky - 5], fill=(32, 18, 36))
    d.ellipse([kx + 5, ky - 10, kx + 10, ky - 5], fill=(32, 18, 36))
    # Mostrador de madera tallada
    d.rectangle([x0 + 24, y0 + 178, x1 - 24, y1 - 14], fill=(116, 72, 48), outline=ORO, width=2)
    d.text((x0 + 40, y0 + 190), "Mostrador de Kikombe · Té tibio, lentes, botas y la Capa del Farolillero", fill=CREMA, font=fuente(12))


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    f_tit = fuente(24)
    f_sub = fuente(15)
    f_lbl = fuente(13)
    f_peq = fuente(12)

    d.rectangle([0, 0, W, 62], fill=(28, 18, 42))
    d.line([(0, 62), (W, 62)], fill=ORO, width=2)
    d.text((24, 12), "JIONI (PARTE 2) · EL MERCADO DEL CREPÚSCULO (TIENDA DE KIKOMBE)", fill=ORO, font=f_tit)
    d.text((24, 40), "Se abre al colgar el 1.er Farol (Kikombe descansa y abre su puesto en el Mercado del Crepúsculo) · 4 artículos en Cristales", fill=TEXTO_SUAVE, font=f_peq)

    # --- PANEL IZQUIERDO: LOS 4 ARTÍCULOS ---
    d.rounded_rectangle([20, 78, 660, 756], radius=10, fill=PANEL, outline=BORDE, width=2)
    d.text((36, 90), "CATÁLOGO DEL MERCADO DEL CREPÚSCULO (4 ARTÍCULOS)", fill=ORO, font=f_sub)

    articulos = [
        ("reloj", "1. Reloj de bolsillo de latón", "5 Cristales",
         "· Afinado por los relojeros de Jioni para el sol detenido.",
         "· Efecto: +15 % recarga de Aliento y las sombras-puente brillan",
         "  con halo dorado extra en el borde para leer los saltos."),
        ("lente", "2. Lente de prisma del Jardín", "6 Cristales",
         "· Tallada con esquirla de cristal del Claustro.",
         "· Efecto: la Resonancia y el Pulso ganan +25 % de alcance y",
         "  los Faroles de la Hora escondidos destellan desde lejos."),
        ("botas", "3. Botas de arena firme", "7 Cristales",
         "· Suela ancha cosida por los fénec de las Dunas.",
         "· Efecto: +10 % velocidad al correr y un margen de +0,4 s",
         "  antes de hundirse en arena movediza o agua del Estanque."),
        ("capa", "4. Capa del Farolillero (Prenda)", "9 Cristales",
         "· Capa azul noche con ribete dorado y farolillo a la cintura.",
         "· Efecto: prenda cosmética + luz cálida alrededor de Maisha",
         "  en zonas oscuras y en el Horizonte Inmóvil."),
    ]
    for idx, (tipo, nom, precio, l1, l2, l3) in enumerate(articulos):
        y0 = 124 + idx * 154
        y1 = y0 + 140
        d.rounded_rectangle([36, y0, 644, y1], radius=8, fill=(34, 24, 50), outline=ORO_SUAVE, width=2)
        icono_articulo(d, 80, y0 + 70, tipo)
        d.text((122, y0 + 14), nom, fill=ORO, font=f_sub)
        etiqueta(d, 524, y0 + 12, precio, f_lbl, bg=(52, 34, 28), fg=AMBAR)
        d.text((122, y0 + 46), l1, fill=CREMA, font=f_peq)
        d.text((122, y0 + 70), l2, fill=TEXTO_SUAVE, font=f_peq)
        d.text((122, y0 + 90), l3, fill=ORO_SUAVE, font=f_peq)

    # --- PANEL DERECHO: INTERIOR DEL PUESTO + OPCIÓN PARA IAM ---
    d.rounded_rectangle([678, 78, 1180, 756], radius=10, fill=PANEL, outline=BORDE, width=2)
    d.text((696, 90), "INTERIOR DEL PUESTO DE KIKOMBE (TIENDA)", fill=ORO, font=f_sub)

    dibujar_interior_puesto(d, 696, 124, 1162, 354)

    # Propuesta A/B para cerrar Jioni parte 2 con Iam
    d.rounded_rectangle([696, 374, 1162, 558], radius=8, fill=(34, 22, 48), outline=ORO, width=2)
    etiqueta(d, 710, 386, "[A] RECOMENDADA: Tienda + Regalo de los 12 Faroles", f_lbl, bg=(56, 36, 28), fg=ORO)
    d.text((710, 420), "· Kikombe abre esta tienda al descansar (1.er Farol).", fill=CREMA, font=f_peq)
    d.text((710, 442), "· Al colgar los 12 Faroles de la Hora en la Plaza, los 6 vecinos", fill=TEXTO_SUAVE, font=f_peq)
    d.text((710, 462), "  descansan y Kibatari entrega la Bendición del Crepúsculo", fill=TEXTO_SUAVE, font=f_peq)
    d.text((710, 482), "  (+1 hoja de Vida máxima y aura cálida para el combate final).", fill=ORO_SUAVE, font=f_peq)
    d.text((710, 512), "· Ventaja: sin inflar el árbol con otra rama nueva; directo", fill=CREMA, font=f_peq)
    d.text((710, 530), "  hacia El Horizonte Inmóvil y el final del juego.", fill=CREMA, font=f_peq)

    d.rounded_rectangle([696, 574, 1162, 740], radius=8, fill=(30, 20, 44), outline=MALVA, width=2)
    etiqueta(d, 710, 586, "OPCIÓN B: Añadir 6.ª rama del diario (Arte del Ocaso)", f_lbl, bg=(42, 22, 58), fg=MALVA, borde=MALVA)
    d.text((710, 620), "· Además de la tienda de Kikombe, Mwanga despierta una", fill=CREMA, font=f_peq)
    d.text((710, 642), "  6.ª rama en el diario (3 o 6 niveles ligados al sol/sombra).", fill=TEXTO_SUAVE, font=f_peq)
    d.text((710, 666), "· Requiere ampliar arbol_vida.gd, artes.json y prendas nuevas.", fill=TEXTO_SUAVE, font=f_peq)
    d.text((710, 694), "  (Tú eliges con Claude si prefieres A para ir ya al final o B.)", fill=MALVA, font=f_peq)

    out = os.path.join(RAIZ, "documentacion", "boceto_mercado_crepusculo.png")
    img.save(out)
    print("OK:", out)


if __name__ == "__main__":
    main()
