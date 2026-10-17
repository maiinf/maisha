"""Generador de láminas comparativas Antes / Después para la documentación HD-2D."""
import os
from PIL import Image, ImageDraw

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIR_HD2D = os.path.join(RAIZ, "documentacion", "hd2d")


def montar_par(ruta_izq, ruta_der, salida, zoom_rect=None):
    """Une dos capturas de 640x360 lado a lado (y opcionalmente debajo un recorte ampliado x3)."""
    p_izq = os.path.join(DIR_HD2D, ruta_izq)
    p_der = os.path.join(DIR_HD2D, ruta_der)
    if not (os.path.exists(p_izq) and os.path.exists(p_der)):
        return False
    im_a = Image.open(p_izq).convert("RGBA")
    im_b = Image.open(p_der).convert("RGBA")
    w, h = im_a.size
    alto_extra = 180 if zoom_rect else 0
    lienzo = Image.new("RGBA", (w * 2 + 8, h + alto_extra), (14, 12, 20, 255))
    lienzo.paste(im_a, (0, 0))
    lienzo.paste(im_b, (w + 8, 0))
    draw = ImageDraw.Draw(lienzo)
    # Etiquetas discretas arriba a la izquierda de cada mitad
    draw.rectangle([8, 8, 96, 26], fill=(18, 14, 24, 210), outline=(214, 180, 110, 255))
    draw.text((16, 12), "ANTES", fill=(255, 243, 196, 255))
    draw.rectangle([w + 16, 8, w + 114, 26], fill=(18, 14, 24, 210), outline=(143, 208, 106, 255))
    draw.text((w + 24, 12), "DESPUES", fill=(168, 232, 144, 255))
    if zoom_rect:
        x0, y0, zw, zh = zoom_rect
        rec_a = im_a.crop((x0, y0, x0 + zw, y0 + zh)).resize((w, alto_extra - 8), Image.Resampling.NEAREST)
        rec_b = im_b.crop((x0, y0, x0 + zw, y0 + zh)).resize((w, alto_extra - 8), Image.Resampling.NEAREST)
        lienzo.paste(rec_a, (0, h + 8))
        lienzo.paste(rec_b, (w + 8, h + 8))
    lienzo.save(os.path.join(DIR_HD2D, salida))
    return True
