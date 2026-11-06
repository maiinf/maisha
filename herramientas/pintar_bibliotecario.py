"""EL BIBLIOTECARIO HUECO (jefe de Las Estanterías Colgantes, Sigilia).
Opción A aprobada por Iam: El abrigo vacío.
La toga morada del viejo bibliotecario armiño que flota en la sala de lectura; en la capucha, solo dos
ojos de tinta brillante. 3 libros encantados le dan vueltas haciendo de escudo protector.

Uso:
    python3 herramientas/pintar_bibliotecario.py

Genera en arte/mundos/sigilia/estanterias/:
  bibliotecario.png   7 × 80×80  fotogramas del jefe:
                      0 y 1 flotando en reposo (ondea) · 2 alzar el puntero (canaliza) · 3 dispara tinta ·
                      4 aturdido (escudo roto, cae al suelo) · 5 golpeado (blanco) · 6 derrotado (desinflado)
  libro_escudo.png    4 × 24×24  el libro encantado que orbita en escudo (bate páginas como alas)
  proyectil_tinta.png 16×16      gota de tinta afilada que dispara
"""
import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "sigilia", "estanterias")
LUZ = (-0.6, -0.6, 0.55)

TELA = ["#120c1e", "#221638", "#382454", "#523678", "#704c9e", "#946cd0"]
ORO = ["#3a2408", "#6a4614", "#a07020", "#d4a034", "#f0cc60", "#fff0b0"]
TINTA = ["#040208", "#0a0614", "#140e24", "#24183e", "#3a2660"]
PAPEL = ["#8a7a60", "#b8a888", "#dccfb0", "#f4ecd8"]
GOLPEADO = ["#4a3a60", "#7a6298", "#b098d8", "#e0d4fc", "#ffffff"]


def bibliotecario_frame(f):
    W, H = 80, 80
    lz = Lienzo(W, H, s=4, semilla=9500 + f)
    cx = 40

    # Desplazamientos y transformaciones según el fotograma
    baja = 0
    alzar_puntero = False
    dispara = False
    aturdido = False
    golpeado = (f == 5)
    derrotado = (f == 6)

    paleta_tela = GOLPEADO if golpeado else TELA

    if f == 0:
        baja = 0
    elif f == 1:
        baja = -3
    elif f == 2:
        baja = -1
        alzar_puntero = True
    elif f == 3:
        baja = -2
        dispara = True
    elif f == 4:
        baja = 10
        aturdido = True
    elif f == 5:
        baja = 2
    elif f == 6:
        baja = 18
        derrotado = True

    y_centro = 40 + baja

    if derrotado:
        # Toga desparramada en el suelo, vacía
        suelo = lz.elipse(cx, 68, 26, 8)
        lz.sombrear(suelo, paleta_tela, 4, LUZ)
        # Capucha caída arrugada
        capucha_caida = lz.elipse(cx - 6, 64, 12, 7)
        lz.sombrear(capucha_caida, paleta_tela, 3, LUZ)
        # Manga y puntero en el suelo
        lz.sombrear(lz.poligono([(cx + 8, 66), (cx + 26, 68), (cx + 24, 72), (cx + 6, 70)]), paleta_tela, 2, LUZ)
        puntero = lz.trazo([(cx + 18, 70), (cx + 34, 69)], 1.2, 0.4)
        lz.sombrear(puntero, ORO, 1, LUZ)
        # Destello tenue donde quedará la ficha
        lz.sumar_luz(lz.desenfocar(lz.circulo(cx - 4, 64, 5), 3), "#f0cc60", 0.4)
        return lz.sprite(contorno=0.5)

    # 1. Sombra en el suelo (más difusa cuanto más alto flote)
    dist_suelo = 72 - (y_centro + 24)
    radio_sombra_x = max(12, 22 - dist_suelo * 0.3)
    radio_sombra_y = max(3, 5 - dist_suelo * 0.1)
    opacidad_sombra = max(0.2, 0.55 - dist_suelo * 0.01)
    lz.pintar(lz.desenfocar(lz.elipse(cx, 73, radio_sombra_x, radio_sombra_y), 2), "#000000", opacidad_sombra)

    # 2. Toga principal
    y_hombros = y_centro - 14
    y_borde = y_centro + 25

    if aturdido:
        # Toga flácida casi desinflada
        pts_toga = [
            (cx - 14, y_hombros + 4), (cx + 14, y_hombros + 4),
            (cx + 24, y_borde), (cx + 12, y_borde - 2), (cx, y_borde + 2),
            (cx - 12, y_borde - 2), (cx - 24, y_borde)
        ]
    else:
        ondulacion = 2 if f == 1 else -2
        pts_toga = [
            (cx - 15, y_hombros), (cx + 15, y_hombros),
            (cx + 26 + (3 if dispara else 0), y_borde - 3),
            (cx + 14, y_borde + ondulacion),
            (cx + 2, y_borde - 2),
            (cx - 12, y_borde + ondulacion),
            (cx - 26, y_borde - 2)
        ]

    toga = lz.poligono(pts_toga)
    lz.sombrear(toga, paleta_tela, 8, LUZ, textura=(np.sin((lz.x - cx) * 0.5 + lz.y * 0.1) > 0.5) * 1.0, fuerza_tex=0.2)

    # Cenefa dorada inferior
    borde_dorado = toga * (lz.distancia(toga) < 2.0) * (lz.y > y_borde - 6)
    lz.pintar(borde_dorado, ORO[3], 0.9)

    # 3. Mangas flotantes
    # Manga izquierda (en reposo)
    manga_izq = lz.poligono([
        (cx - 13, y_hombros + 4), (cx - 28, y_centro + 4),
        (cx - 32, y_centro + 14), (cx - 22, y_centro + 13),
        (cx - 11, y_hombros + 16)
    ])
    lz.sombrear(manga_izq, paleta_tela, 5, LUZ)
    lz.pintar(lz.elipse(cx - 27, y_centro + 14, 4, 2), TINTA[0])

    # Manga derecha (sostiene el puntero de oro)
    if alzar_puntero:
        manga_der = lz.poligono([
            (cx + 12, y_hombros + 2), (cx + 28, y_centro - 10),
            (cx + 34, y_centro - 2), (cx + 24, y_centro + 2),
            (cx + 10, y_hombros + 16)
        ])
        lz.sombrear(manga_der, paleta_tela, 5, LUZ)
        lz.pintar(lz.elipse(cx + 30, y_centro - 4, 4, 2), TINTA[0])
        # Puntero apuntando al cielo/diagonal
        puntero = lz.trazo([(cx + 29, y_centro - 4), (cx + 46, y_centro - 24)], 1.8, 0.4)
        lz.sombrear(puntero, ORO, 1.2, LUZ)
        # Destello en la punta
        lz.sumar_luz(lz.desenfocar(lz.circulo(cx + 46, y_centro - 24, 4), 2), "#fff0b0", 0.8)
    elif dispara:
        manga_der = lz.poligono([
            (cx + 12, y_hombros + 4), (cx + 32, y_centro),
            (cx + 36, y_centro + 8), (cx + 24, y_centro + 10),
            (cx + 10, y_hombros + 16)
        ])
        lz.sombrear(manga_der, paleta_tela, 5, LUZ)
        lz.pintar(lz.elipse(cx + 31, y_centro + 8, 4, 2), TINTA[0])
        # Puntero disparando horizontal
        puntero = lz.trazo([(cx + 30, y_centro + 8), (cx + 52, y_centro + 6)], 1.8, 0.4)
        lz.sombrear(puntero, ORO, 1.2, LUZ)
        # Rayo de tinta que sale
        destello = lz.circulo(cx + 52, y_centro + 6, 3.5)
        lz.pintar(destello, TINTA[4])
        lz.sumar_luz(lz.desenfocar(destello, 3), "#a855f7", 0.9)
    else:
        # Manga en reposo sosteniendo el puntero hacia abajo
        manga_der = lz.poligono([
            (cx + 13, y_hombros + 4), (cx + 28, y_centro + 4),
            (cx + 32, y_centro + 14), (cx + 22, y_centro + 13),
            (cx + 11, y_hombros + 16)
        ])
        lz.sombrear(manga_der, paleta_tela, 5, LUZ)
        lz.pintar(lz.elipse(cx + 27, y_centro + 14, 4, 2), TINTA[0])
        if not aturdido:
            puntero = lz.trazo([(cx + 28, y_centro + 14), (cx + 38, y_centro - 4)], 1.6, 0.4)
            lz.sombrear(puntero, ORO, 1.2, LUZ)

    # 4. Capucha
    y_capucha = y_hombros - 5
    capucha = lz.elipse(cx, y_capucha, 15, 16)
    lz.sombrear(capucha, paleta_tela, 8, LUZ)

    # Orejitas de armiño de tela en la capucha
    for dx in (-10, 10):
        oreja = lz.elipse(cx + dx, y_capucha - 14, 4, 5.5)
        lz.sombrear(oreja, paleta_tela, 3, LUZ)

    # Hueco negro en el interior de la capucha
    hueco = lz.elipse(cx, y_capucha + 1, 9, 10)
    lz.pintar(hueco, TINTA[0])

    # Ojos de tinta brillante
    if not aturdido:
        for dx in (-4, 4):
            ojo = lz.elipse(cx + dx, y_capucha + (0 if not alzar_puntero else -1), 1.4, 2.2)
            lz.sumar_luz(lz.desenfocar(ojo, 2.5), "#a855f7", 0.7)
            lz.pintar(ojo, "#f3e8ff")
    else:
        # Ojos bizcos / intermitentes apagados
        ojo1 = lz.elipse(cx - 3, y_capucha + 2, 1.0, 1.0)
        ojo2 = lz.elipse(cx + 4, y_capucha + 3, 1.0, 1.0)
        lz.pintar(ojo1 + ojo2, "#8a6af0", 0.5)

    return lz.sprite(contorno=0.5)


def libro_escudo(f):
    W, H = 24, 24
    lz = Lienzo(W, H, s=6, semilla=9600 + f)
    cx, cy = 12, 12

    # f va de 0 a 3: ciclo de aleteo de las páginas
    angulo_ala = [0, 2, 4, 2][f]
    colores_tomo = ["#5a1828", "#241848", "#183824", "#482810"][f % 4]

    # Cubierta dura del libro
    cubierta = lz.poligono([
        (cx - 8, cy + 2 + angulo_ala),
        (cx, cy - 2 - angulo_ala * 0.5),
        (cx + 8, cy + 2 + angulo_ala),
        (cx, cy + 6 + angulo_ala * 0.5)
    ])
    lz.sombrear(cubierta, [TINTA[0], colores_tomo, ORO[3]], 2, LUZ)

    # Hojas blancas de papel abiertas
    hojas = lz.poligono([
        (cx - 7, cy + 1 + angulo_ala),
        (cx, cy - 3 - angulo_ala * 0.5),
        (cx + 7, cy + 1 + angulo_ala),
        (cx, cy + 4 + angulo_ala * 0.5)
    ])
    lz.sombrear(hojas, PAPEL, 1.5, LUZ)

    # Lomo de cuero y runa dorada
    lomo = lz.trazo([(cx, cy - 3 - angulo_ala * 0.5), (cx, cy + 5 + angulo_ala * 0.5)], 0.8)
    lz.pintar(lomo, ORO[4])

    # Destello mágico de protección alrededor
    lz.sumar_luz(lz.desenfocar(hojas, 3), "#c084fc", 0.3)

    return lz.sprite(contorno=0.5)


def proyectil_tinta():
    W, H = 16, 16
    lz = Lienzo(W, H, s=6, semilla=9700)
    cx, cy = 8, 8

    gota = lz.poligono([(cx + 6, cy), (cx - 2, cy - 4), (cx - 6, cy), (cx - 2, cy + 4)])
    lz.sombrear(gota, TINTA, 2, LUZ)
    brillo = lz.circulo(cx + 2, cy - 1, 1.2)
    lz.pintar(brillo, "#e9d5ff")
    lz.sumar_luz(lz.desenfocar(gota, 2), "#a855f7", 0.5)

    return lz.sprite(contorno=0.4)


def main():
    os.makedirs(SALIDA, exist_ok=True)

    # 1. Bibliotecario (7 fotogramas de 80x80)
    frames_biblio = [bibliotecario_frame(f) for f in range(7)]
    tira_biblio = np.concatenate(frames_biblio, axis=1)
    Image.fromarray(tira_biblio, "RGBA").save(os.path.join(SALIDA, "bibliotecario.png"))

    # 2. Libro escudo (4 fotogramas de 24x24)
    frames_libro = [libro_escudo(f) for f in range(4)]
    tira_libro = np.concatenate(frames_libro, axis=1)
    Image.fromarray(tira_libro, "RGBA").save(os.path.join(SALIDA, "libro_escudo.png"))

    # 3. Proyectil tinta (16x16)
    Image.fromarray(proyectil_tinta(), "RGBA").save(os.path.join(SALIDA, "proyectil_tinta.png"))

    print("Bibliotecario Hueco pintado exitosamente en:", SALIDA)


if __name__ == "__main__":
    main()
