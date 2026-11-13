"""Boceto de EL CORAZÓN DEL METEORITO (jefe final de Asterhaul / Mundo 3), para decidir con Iam antes de
que Claude lo construya. Tres propuestas en la arena del Santuario Estelar con Maisha al lado:
  A · La Semilla Estelar Encadenada (⭐ recomendada): núcleo poliédrico de ámbar vivo e iridio flotando
      entre tres aros concéntricos de hierro meteórico y grietas de luz estelar; cada aro cede ante un poder
      del Arte de la Tierra hasta despertar el alma dormida en su centro.
  B · El Coloso de Magma y Basalto: busto titánico forjado del cráter con dos puños flotantes de gravedad.
  C · El Ojo Cósmico de Plasma: esfera incandescente rodeada de anillos orbitales que dispara haces en cruz.
Sale en documentacion/boceto_corazon_meteorito.png (600×256)."""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from pintor import Lienzo, rampa  # noqa: E402
import cinematicas as ci  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 600, 256
COSMOS = ["#080612", "#100c20", "#1a1432", "#282046"]
BASALTO = ["#14121c", "#242030", "#3a344c", "#544c6c", "#746a90"]
HIERRO = ["#1e2430", "#343e52", "#52627e", "#7a8eb0", "#b0c4e2"]
AMBAR = ["#4a1e04", "#8a4208", "#cc6c10", "#f4a428", "#ffd460", "#fff0a8"]
MAGMA = ["#380a08", "#7a160c", "#be3212", "#f26420", "#ffad48"]
CRISTAL = ["#14364a", "#266484", "#449cc4", "#80d8f2", "#d8f8ff"]
LUZ = (-0.55, -0.65, 0.52)


def santuario(lz, x0):
    x1 = x0 + 200
    zona = (lz.x >= x0) * (lz.x < x1)
    # Bóveda estelar detrás del cráter
    fondo = zona * (lz.y < 146)
    lz.pintar(fondo, rampa(COSMOS, np.clip(lz.y / 146.0, 0, 1)))
    # Estrellas tenues en el cielo del cráter
    estrellas = fondo * ((np.sin(lz.x * 1.7 + lz.y * 2.3) * np.cos(lz.x * 0.9 - lz.y * 1.1)) > 0.96)
    lz.pintar(estrellas, CRISTAL[-1], 0.7)
    # Plataforma del Santuario
    suelo = zona * (lz.y >= 146)
    lz.pintar(suelo, rampa(BASALTO[:4], np.clip((lz.y - 146) / 110.0, 0, 1)))
    anillo = suelo * (np.abs(np.hypot(lz.x - (x0 + 100), (lz.y - 190) * 1.65) - 66) < 2.2)
    lz.pintar(anillo, AMBAR[4], 0.65)
    lz.sumar_luz(lz.desenfocar(anillo, 5), "#f4a428", 0.30)


def idea_semilla_encadenada(lz, x0):
    cx, cy = x0 + 108, 108
    lz.pintar(lz.elipse(cx, 182, 40, 10), "#06040e", 0.65)
    # Tres aros concéntricos de hierro meteórico y luz dorada
    for r, col, inclinacion in [(44, HIERRO, 0.52), (34, BASALTO[1:], 1.2), (24, AMBAR[2:], 0.85)]:
        d_el = np.hypot((lz.x - cx) * 1.0, (lz.y - cy) / inclinacion)
        aro = (np.abs(d_el - r) < 3.2) * (lz.x >= x0) * (lz.x < x0 + 200)
        lz.sombrear(aro, col, 3, LUZ)
    # Semilla central poliédrica de ámbar e iridio vivo
    nube_nucleo = lz.poligono([
        (cx, cy - 26), (cx + 18, cy - 10), (cx + 14, cy + 16),
        (cx, cy + 28), (cx - 14, cy + 16), (cx - 18, cy - 10),
    ])
    lz.sombrear(nube_nucleo, AMBAR, 8, LUZ)
    # Grietas estelares luminosas dentro de la semilla
    corazon = lz.elipse(cx, cy, 8, 12)
    lz.pintar(corazon, AMBAR[-1], 0.9)
    lz.sumar_luz(lz.desenfocar(corazon, 10), "#ffd460", 0.7)
    # Dos cadenitas laterales ancladas al altar
    for sx in (-1, 1):
        cad = (np.abs((lz.y - (cy + 30)) - (lz.x - (cx + sx * 24)) * sx * 0.9) < 2.0) * (lz.y >= cy + 24) * (lz.y <= 176)
        lz.sombrear(cad, HIERRO, 2, LUZ)


def idea_coloso_magma(lz, x0):
    cx, cy = x0 + 108, 118
    lz.pintar(lz.elipse(cx, 184, 48, 11), "#06040e", 0.65)
    # Hombros y torso masivo de basalto y magma
    torso = lz.poligono([(cx - 34, cy + 36), (cx - 28, cy - 18), (cx + 28, cy - 18), (cx + 34, cy + 36)])
    lz.sombrear(torso, BASALTO, 8, LUZ)
    nucleo_m = lz.elipse(cx, cy + 6, 13, 14)
    lz.sombrear(nucleo_m, MAGMA, 6, LUZ)
    lz.sumar_luz(lz.desenfocar(nucleo_m, 7), "#f26420", 0.55)
    # Cabeza con corona de roca rota
    cabeza = lz.poligono([(cx - 14, cy - 20), (cx - 18, cy - 42), (cx, cy - 48), (cx + 18, cy - 42), (cx + 14, cy - 20)])
    lz.sombrear(cabeza, BASALTO[1:], 6, LUZ)
    lz.pintar(lz.elipse(cx - 5, cy - 30, 3, 2), MAGMA[-1])
    lz.pintar(lz.elipse(cx + 5, cy - 30, 3, 2), MAGMA[-1])
    # Dos puños flotantes gravitatorios
    for px in (cx - 52, cx + 52):
        puno = lz.elipse(px, cy + 20, 14, 15)
        lz.sombrear(puno, BASALTO, 6, LUZ)
        lz.pintar(lz.elipse(px, cy + 20, 5, 5), MAGMA[3], 0.8)


def idea_ojo_plasma(lz, x0):
    cx, cy = x0 + 108, 108
    lz.pintar(lz.elipse(cx, 182, 34, 9), "#06040e", 0.6)
    # Anillos orbitales de cristal y plasma
    for ang, col in ((0.45, CRISTAL), (-0.45, AMBAR[2:])):
        dx = (lz.x - cx) * np.cos(ang) - (lz.y - cy) * np.sin(ang)
        dy = (lz.x - cx) * np.sin(ang) + (lz.y - cy) * np.cos(ang)
        aro = (np.abs(np.hypot(dx * 0.7, dy * 1.45) - 34) < 3.0) * (lz.x >= x0) * (lz.x < x0 + 200)
        lz.sombrear(aro, col, 3, LUZ)
    # Esfera central luminosa con gran iris cósmico
    esfera = lz.elipse(cx, cy, 24, 24)
    lz.sombrear(esfera, MAGMA, 8, LUZ)
    iris = lz.elipse(cx, cy, 10, 14)
    lz.sombrear(iris, CRISTAL, 5, LUZ)
    pupila = lz.elipse(cx, cy, 3, 9)
    lz.pintar(pupila, "#080612")
    lz.sumar_luz(lz.desenfocar(esfera, 9), "#ffad48", 0.6)


def main():
    lz = Lienzo(W, H, semilla=880)
    for i, fn in enumerate((idea_semilla_encadenada, idea_coloso_magma, idea_ojo_plasma)):
        x0 = i * 200
        santuario(lz, x0)
        fn(lz, x0)
        ci.maisha_luz(lz, x0 + 24, 218, e=1.0)

    for x in (199, 200, 399, 400):
        lz.pintar((np.abs(lz.x - x) < 0.8) * 1.0, AMBAR[4])

    os.makedirs(os.path.join(RAIZ, "documentacion"), exist_ok=True)
    salida = os.path.join(RAIZ, "documentacion", "boceto_corazon_meteorito.png")
    lz.guardar(salida)

    im = Image.open(salida).convert("RGB")
    d = ImageDraw.Draw(im)
    try:
        fb = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 10)
    except OSError:
        fb = ImageFont.load_default()

    titulos = [
        "A · Semilla Estelar (Rec.)",
        "B · Coloso de Magma",
        "C · Ojo de Plasma",
    ]
    for i, tit in enumerate(titulos):
        d.rectangle((i * 200 + 4, 236, i * 200 + 196, 252), fill=(14, 12, 22))
        d.text((i * 200 + 10, 238), tit, font=fb, fill=(255, 240, 168) if i == 0 else (216, 248, 255))

    im.save(salida)
    print("boceto del Corazón guardado en:", salida)


if __name__ == "__main__":
    main()
