"""Boceto del BIBLIOTECARIO HUECO (jefe de Las Estanterías Colgantes), para decidir con Iam antes de construirlo.
Tres ideas, cada una en la sala de lectura (estanterías moradas, el atril con el libro enorme) y con Maisha al lado
para ver el tamaño:
  A · El abrigo vacío: la toga del viejo bibliotecario armiño, que flota sin nadie dentro; en la capucha, solo dos
      gotas de tinta. Los libros le dan vueltas alrededor.
  B · El gigante de libros: un armiño enorme hecho de libros apilados, con el pecho hueco y una vela dentro.
  C · La sombra del atril: una sombra de tinta con forma de armiño que sale del libro enorme del atril.
Sale en documentacion/boceto_bibliotecario.png (600×256)."""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from pintor import Lienzo, rampa  # noqa: E402
import cinematicas as ci  # noqa: E402

W, H = 600, 256
MORADO = ["#120c1e", "#1e1430", "#2e1e46", "#42295e", "#5a3a78", "#7a5296", "#a07ab4"]
ORO = ["#3a2408", "#6a4614", "#a07020", "#d4a034", "#f0cc60", "#fff0b0"]
TINTA = ["#05040a", "#0e0a1a", "#1c1430", "#2e2248", "#4a3a6e"]
PAPEL = ["#8a7a60", "#b8a888", "#dccfb0", "#f4ecd8"]
TELA = ["#1a1030", "#2a1a4a", "#3e2a66", "#584088", "#7a62a8"]
LUZ = (-0.6, -0.6, 0.55)


def sala(lz, x0, rng):
    """El fondo de un panel: estanterías con libros, parqué y una alfombra morada con cenefa dorada."""
    x1 = x0 + 200
    zona = (lz.x >= x0) * (lz.x < x1)
    lz.pintar(zona * (lz.y < 150), MORADO[1])
    for fila in range(5):
        yb = 18 + fila * 26
        lz.sombrear(zona * (np.abs(lz.y - yb - 22) < 2), ORO[:4], 2, LUZ)
        x = x0 + 2
        while x < x1 - 4:
            ancho = rng.integers(3, 7)
            alto = rng.integers(14, 21)
            col = ["#5a2a3a", "#2a3a5a", "#3a5a3a", "#6a4a2a", "#4a2a5a"][rng.integers(5)]
            lomo = lz.poligono([(x, yb + 20), (x, yb + 20 - alto), (x + ancho, yb + 20 - alto), (x + ancho, yb + 20)])
            lz.sombrear(lomo, ["#140c18", col, "#c8b090"], 2, LUZ, fuerza_tex=0.1)
            lz.pintar(lomo * (np.abs(lz.y - (yb + 20 - alto * 0.6)) < 0.6), ORO[4], 0.7)
            x += ancho + 1
    suelo = zona * (lz.y >= 150)
    lz.pintar(suelo, rampa(["#2a1810", "#4a2c1a", "#6a4024"], np.clip((lz.y - 150) / 110 + ((lz.x % 14) < 1) * 0.3, 0, 1)))
    alfombra = suelo * (np.abs(lz.x - x0 - 100) < 70) * (lz.y > 170)
    lz.pintar(alfombra, "#3a1a4a")
    lz.pintar(alfombra * ((np.abs(lz.x - x0 - 100) > 64) + (np.abs(lz.y - 174) < 2) > 0), ORO[3])
    # la luz de las velas, cálida, desde arriba
    lz.sumar_luz(lz.desenfocar(zona * lz.elipse(x0 + 100, 60, 90, 60), 30), "#f0a040", 0.15)


def libro_volando(lz, x, y, ang, col):
    abierto = lz.poligono([(x - 6, y), (x, y - 2 + ang), (x + 6, y), (x, y + 3 + ang)])
    lz.sombrear(abierto, ["#140c18", col, "#e8d8b0"], 2, LUZ)
    lz.pintar(lz.trazo([(x, y - 2 + ang), (x, y + 3 + ang)], 0.4), PAPEL[3])


def idea_abrigo(lz, x0, rng):
    cx = x0 + 100
    # la toga: ancha abajo, deshilachada, flotando (no toca el suelo)
    toga = lz.poligono([(cx - 18, 70), (cx + 18, 70), (cx + 34, 182), (cx + 20, 176), (cx + 8, 186), (cx - 6, 178),
                        (cx - 20, 188), (cx - 34, 180)])
    lz.sombrear(toga, TELA, 16, LUZ, textura=(np.sin((lz.x - cx) * 0.6 + lz.y * 0.05) > 0.6) * 1.0, fuerza_tex=0.2)
    # cenefa dorada con runas
    lz.pintar(toga * (lz.distancia(toga) < 2.2) * (lz.y > 120), ORO[3], 0.9)
    # mangas largas, con una pluma enorme en una
    for lado in (-1, 1):
        manga = lz.poligono([(cx + lado * 16, 80), (cx + lado * 40, 118), (cx + lado * 46, 132), (cx + lado * 32, 132),
                             (cx + lado * 14, 104)])
        lz.sombrear(manga, TELA, 8, LUZ)
        lz.pintar(lz.elipse(cx + lado * 39, 132, 6, 3), TINTA[0])
    pluma = lz.trazo([(cx + 40, 132), (cx + 58, 92)], 2.4, 0.4)
    lz.sombrear(pluma, PAPEL, 2, LUZ)
    # la capucha: dentro, nada; solo oscuridad y dos gotas de tinta que brillan
    capucha = lz.elipse(cx, 66, 20, 22)
    lz.sombrear(capucha, TELA, 12, LUZ)
    hueco = lz.elipse(cx, 70, 12, 14)
    lz.pintar(hueco, TINTA[0])
    for dx in (-5, 5):
        ojo = lz.elipse(cx + dx, 70, 1.6, 2.6)
        lz.sumar_luz(lz.desenfocar(ojo, 3), "#8a6af0", 0.7)
        lz.pintar(ojo, "#c8b8ff")
    # las orejas de armiño, vacías, de tela
    for dx in (-12, 12):
        lz.sombrear(lz.elipse(cx + dx, 46, 5, 7), TELA, 4, LUZ)
    # libros que le dan vueltas
    for k in range(7):
        a = k / 7 * np.pi * 2
        libro_volando(lz, cx + np.cos(a) * 62, 110 + np.sin(a) * 26, np.sin(a) * 2,
                      ["#5a2a3a", "#2a3a5a", "#3a5a3a", "#6a4a2a"][k % 4])
    lz.pintar(lz.desenfocar(lz.elipse(cx, 212, 30, 4), 2), "#0a0610", 0.5)


def idea_gigante(lz, x0, rng):
    cx = x0 + 100
    cuerpo = np.zeros((lz.H, lz.W))
    # pilas de libros: piernas, tronco, brazos y cabeza (cada libro, un ladrillo)
    def pila(xc, ya, yb, ancho):
        y = yb
        while y > ya:
            alto = rng.integers(4, 7)
            dx = rng.uniform(-2, 2)
            libro = lz.poligono([(xc - ancho + dx, y), (xc - ancho + dx, y - alto), (xc + ancho + dx, y - alto),
                                 (xc + ancho + dx, y)])
            col = ["#5a2a3a", "#2a3a5a", "#3a5a3a", "#6a4a2a", "#4a2a5a"][rng.integers(5)]
            lz.sombrear(libro, ["#140c18", col, "#c8b090"], 3, LUZ)
            lz.pintar(libro * (lz.x > xc + ancho + dx - 2), PAPEL[2], 0.8)
            y -= alto
            nonlocal cuerpo
            cuerpo = np.maximum(cuerpo, libro)
    pila(cx - 16, 150, 206, 9)
    pila(cx + 16, 150, 206, 9)
    pila(cx, 84, 152, 26)
    pila(cx - 40, 96, 156, 7)
    pila(cx + 40, 96, 156, 7)
    pila(cx, 44, 86, 15)
    # el pecho hueco: un agujero con una vela dentro
    hueco = lz.elipse(cx, 118, 11, 14)
    lz.pintar(hueco, TINTA[1])
    ci.llamas(lz, cx, 124, 4, 10, semilla=5)
    lz.sumar_luz(lz.desenfocar(hueco, 8), "#f0a040", 0.6)
    lz.pintar(lz.poligono([(cx - 2, 132), (cx - 2, 124), (cx + 2, 124), (cx + 2, 132)]), "#e8dcc0")
    # cara: orejas de armiño de pergamino, ojos de tinta y unas lentes
    for dx in (-10, 10):
        lz.sombrear(lz.elipse(cx + dx, 40, 5, 7), PAPEL, 3, LUZ)
    for dx in (-6, 6):
        lz.pintar(lz.trazo([(cx + dx - 4, 62), (cx + dx + 4, 62)], 0.5) + lz.circulo(cx + dx, 64, 4.2) * (lz.distancia(lz.circulo(cx + dx, 64, 4.2)) < 1), ORO[4])
        lz.pintar(lz.elipse(cx + dx, 64, 1.6, 2.2), "#c8b8ff")
    lz.pintar(lz.desenfocar(lz.elipse(cx, 212, 40, 5), 2), "#0a0610", 0.5)


def idea_sombra(lz, x0, rng):
    cx = x0 + 100
    # el atril con el libro enorme abierto
    pie = lz.poligono([(cx - 6, 206), (cx - 4, 160), (cx + 4, 160), (cx + 6, 206)])
    lz.sombrear(pie, ["#2a2030", "#5a4a5e", "#8a7a8e"], 4, LUZ)
    tapa = lz.poligono([(cx - 40, 160), (cx, 150), (cx + 40, 160), (cx, 170)])
    lz.sombrear(tapa, PAPEL, 6, LUZ)
    lz.pintar(lz.trazo([(cx, 150), (cx, 170)], 0.6), "#5a4a3a")
    # la sombra de tinta sale del libro: cuerpo de armiño largo, que se deshace en chorros
    sombra = lz.poligono([(cx - 10, 156), (cx - 22, 110), (cx - 16, 70), (cx + 16, 70), (cx + 24, 112), (cx + 10, 156)])
    sombra = np.maximum(sombra, lz.elipse(cx, 58, 17, 15))
    for dx in (-11, 11):
        sombra = np.maximum(sombra, lz.elipse(cx + dx, 42, 5, 8))
    for lado in (-1, 1):
        brazo = lz.trazo(lz.curva((cx + lado * 16, 84), (cx + lado * 46, 92), (cx + lado * 60, 70), n=30), 6, 1.5)
        sombra = np.maximum(sombra, brazo)
    sombra = sombra * (lz.ruido(6, 3, semilla=40) > 0.25 - (lz.y < 150) * 1.0)
    lz.sombrear(sombra, TINTA, 10, LUZ)
    lz.pintar(sombra * (lz.distancia(sombra) < 1.4), "#6a4ab0", 0.6)
    for dx in (-6, 6):
        ojo = lz.elipse(cx + dx, 58, 2.2, 1.4)
        lz.sumar_luz(lz.desenfocar(ojo, 4), "#8a6af0", 0.8)
        lz.pintar(ojo, "#e8e0ff")
    # chorros de tinta que caen del libro y charcos en la alfombra
    for dx in (-30, -12, 20, 34):
        lz.pintar(lz.trazo([(cx + dx, 162), (cx + dx + rng.uniform(-2, 2), 196)], 1.4, 0.6), TINTA[1])
        lz.sombrear(lz.elipse(cx + dx, 200, 9, 3), TINTA, 3, LUZ)
    # páginas arrancadas que vuelan
    for k in range(9):
        px, py = cx + rng.uniform(-80, 80), rng.uniform(30, 140)
        hoja = lz.poligono([(px - 3, py - 2), (px + 3, py - 2.6), (px + 2.6, py + 2), (px - 3, py + 2.4)])
        lz.sombrear(hoja, PAPEL, 1.2, LUZ)


def boceto():
    lz = Lienzo(W, H, semilla=700)
    rng = np.random.default_rng(701)
    for i, idea in enumerate((idea_abrigo, idea_gigante, idea_sombra)):
        sala(lz, i * 200, rng)
        idea(lz, i * 200, rng)
        ci.maisha_luz(lz, i * 200 + 30, 214, e=1.0)
    for x in (199, 200, 399, 400):
        lz.pintar((np.abs(lz.x - x) < 0.6) * 1.0, "#05040a")
    return lz


if __name__ == "__main__":
    salida = os.path.join(os.path.dirname(__file__), "..", "documentacion", "boceto_bibliotecario.png")
    boceto().guardar(salida)
    img = Image.open(salida).convert("RGB")
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 10)
    except OSError:
        f = ImageFont.load_default()
    for i, nombre in enumerate(("A · El abrigo vacío", "B · El gigante de libros", "C · La sombra del atril")):
        d.rectangle((i * 200 + 4, 236, i * 200 + 196, 252), fill=(10, 6, 18))
        d.text((i * 200 + 10, 238), nombre, font=f, fill=(240, 220, 160))
    img.save(salida)
    print("hecho", os.path.abspath(salida))
