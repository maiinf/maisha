"""
ICONO DE LA APLICACIÓN MAISHA (macOS .icns, Windows .ico y PNG 512×512).
Uso: python3 herramientas/dibujar_icono_app.py
"""
import math
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFilter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "arte", "interfaz")


def _dibujar_icono(tam: int = 512) -> Image.Image:
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    # Máscara redondeada estilo macOS (margen 24 px en 512)
    m = int(tam * 0.048)
    r = int(tam * 0.21)
    mascara = Image.new("L", (tam, tam), 0)
    ImageDraw.Draw(mascara).rounded_rectangle([m, m, tam - m, tam - m], radius=r, fill=255)

    # Fondo degradado: cielo índigo de la Primera Noche -> violeta crepúsculo -> horizonte dorado
    fondo = Image.new("RGBA", (tam, tam), (0, 0, 0, 255))
    px = fondo.load()
    c_top = (22, 24, 58)
    c_mid = (72, 34, 88)
    c_hor = (228, 128, 72)
    c_bot = (56, 78, 44)
    for y in range(tam):
        u = y / float(tam - 1)
        if u < 0.48:
            t = u / 0.48
            col = tuple(int(c_top[i] + (c_mid[i] - c_top[i]) * t) for i in range(3))
        elif u < 0.74:
            t = (u - 0.48) / 0.26
            col = tuple(int(c_mid[i] + (c_hor[i] - c_mid[i]) * t) for i in range(3))
        else:
            t = (u - 0.74) / 0.26
            col = tuple(int(c_hor[i] + (c_bot[i] - c_hor[i]) * t) for i in range(3))
        for x in range(tam):
            px[x, y] = col + (255,)

    d = ImageDraw.Draw(fondo)

    # Sol naciente/poniente suave en el centro-bajo
    aura = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    da = ImageDraw.Draw(aura)
    cx, cy = tam // 2, int(tam * 0.62)
    for rad, al in ((185, 36), (138, 64), (96, 110), (62, 160)):
        da.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(255, 214, 118, al))
    aura = aura.filter(ImageFilter.GaussianBlur(14))
    fondo.alpha_composite(aura)

    # Colina verde de Raíz / Kitovu al pie
    d = ImageDraw.Draw(fondo)
    d.ellipse([-60, int(tam * 0.73), tam + 60, int(tam * 1.18)], fill=(54, 86, 46, 255), outline=(144, 186, 86, 255), width=4)
    d.ellipse([-20, int(tam * 0.79), tam + 20, int(tam * 1.16)], fill=(40, 64, 38, 255))

    # Estrellas en el cielo nocturno superior
    for sx, sy, sr in (
        (0.20, 0.20, 4), (0.31, 0.15, 3), (0.43, 0.22, 3), (0.58, 0.16, 4),
        (0.68, 0.35, 3), (0.24, 0.34, 3), (0.82, 0.37, 3), (0.16, 0.44, 2),
        (0.64, 0.30, 2), (0.36, 0.29, 2),
    ):
        x0, y0 = int(sx * tam), int(sy * tam)
        d.ellipse([x0 - sr, y0 - sr, x0 + sr, y0 + sr], fill=(255, 246, 206, 235))

    # Luna creciente fina en la esquina superior derecha
    lx, ly = int(tam * 0.76), int(tam * 0.22)
    lr = int(tam * 0.068)
    luna = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    dl = ImageDraw.Draw(luna)
    dl.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], fill=(255, 244, 198, 255))
    dl.ellipse([lx - int(lr * 0.35), ly - int(lr * 1.05), lx + int(lr * 1.35), ly + int(lr * 0.75)], fill=(0, 0, 0, 0))
    fondo.alpha_composite(luna)

    # Sprite pixel-art auténtico de Maisha (maisha_reposo_abajo.png, fotograma 0) escalado nítido
    hoja = Image.open(os.path.join(RAIZ, "arte", "personajes", "maisha", "maisha_reposo_abajo.png")).convert("RGBA")
    fw = hoja.width // 4
    maisha = hoja.crop((0, 0, fw, hoja.height))
    escala = 10  # 24x32 -> 240x320 píxeles nítidos
    maisha_g = maisha.resize((maisha.width * escala, maisha.height * escala), Image.NEAREST)
    # Sombra suave a sus pies
    sombra = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).ellipse([cx - 88, int(tam * 0.77), cx + 88, int(tam * 0.85)], fill=(18, 12, 28, 130))
    sombra = sombra.filter(ImageFilter.GaussianBlur(8))
    fondo.alpha_composite(sombra)
    mx = (tam - maisha_g.width) // 2
    my = int(tam * 0.19)
    fondo.alpha_composite(maisha_g, (mx, my))

    # Aplicar máscara redondeada
    img.paste(fondo, (0, 0), mascara)

    # Doble marco dorado elegante
    di = ImageDraw.Draw(img)
    di.rounded_rectangle([m, m, tam - m, tam - m], radius=r, outline=(242, 202, 114, 255), width=10)
    di.rounded_rectangle([m + 10, m + 10, tam - m - 10, tam - m - 10], radius=max(8, r - 10), outline=(92, 58, 34, 220), width=4)
    return img


def _guardar_icns(img512: Image.Image, destino_icns: str) -> None:
    tmp = tempfile.mkdtemp(prefix="maisha_icon_")
    iconset = os.path.join(tmp, "Maisha.iconset")
    os.makedirs(iconset, exist_ok=True)
    try:
        pares = [
            (16, "icon_16x16.png"), (32, "icon_16x16@2x.png"),
            (32, "icon_32x32.png"), (64, "icon_32x32@2x.png"),
            (128, "icon_128x128.png"), (256, "icon_128x128@2x.png"),
            (256, "icon_256x256.png"), (512, "icon_256x256@2x.png"),
            (512, "icon_512x512.png"), (1024, "icon_512x512@2x.png"),
        ]
        for sz, nom in pares:
            im = img512.resize((sz, sz), Image.LANCZOS)
            im.save(os.path.join(iconset, nom))
        subprocess.run(["iconutil", "-c", "icns", iconset, "-o", destino_icns], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    os.makedirs(SALIDA, exist_ok=True)
    img512 = _dibujar_icono(512)
    ruta_png = os.path.join(SALIDA, "icono_app.png")
    ruta_ico = os.path.join(SALIDA, "icono_app.ico")
    ruta_icns = os.path.join(SALIDA, "icono_app.icns")
    img512.save(ruta_png)
    img512.save(ruta_ico, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    _guardar_icns(img512, ruta_icns)
    print("OK:", ruta_png, ruta_ico, ruta_icns)


if __name__ == "__main__":
    main()
