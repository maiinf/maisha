"""Lámina de personajes y opciones de diseño del VALLE DEL OCASO para decidir con Iam:
  - Arriba: El guía zorro fénec (mbweha) -> Opción A (Mwanga, viejo farolillero) vs Opción B (Jioni, aprendiz)
  - Abajo:  El jefe final en El Horizonte Inmóvil (donde nace Giza) -> Opción A (Jua-Giza, El Sol Encadenado)
            vs Opción B (Mzee-Jua, El Relojero del Ocaso)
Sale en documentacion/boceto_personajes_ocaso.png (1060x700)."""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1060, 700
FONDO = (20, 14, 28)
PANEL = (32, 22, 44)
PANEL_REC = (40, 26, 52)
ORO = (248, 204, 116)
MALVA = (196, 132, 248)
CREMA = (248, 236, 204)
SUAVE = (212, 198, 222)


def dibujar_fenec_viejo(d, cx, cy):
    """Opción A: Mwanga, viejo zorro fénec farolillero (orejas enormes, bufanda púrpura, gafas de latón, vara con farol)."""
    # Halo suave de su farol
    d.ellipse([cx + 16, cy - 42, cx + 76, cy + 18], fill=(92, 62, 42))
    d.ellipse([cx + 28, cy - 30, cx + 64, cy + 6], fill=(156, 108, 52))
    # Sombra en suelo
    d.ellipse([cx - 28, cy + 44, cx + 28, cy + 56], fill=(18, 10, 26))
    # Cola esponjosa de fénec asomando a la izquierda
    d.ellipse([cx - 46, cy + 10, cx - 10, cy + 36], fill=(236, 196, 144), outline=(88, 52, 42), width=2)
    d.ellipse([cx - 46, cy + 14, cx - 32, cy + 28], fill=(124, 72, 68))  # punta oscura
    # Túnica / abrigo de farolillero crepuscular
    d.polygon([(cx - 22, cy + 46), (cx - 16, cy - 4), (cx + 16, cy - 4), (cx + 24, cy + 46)],
              fill=(94, 48, 86), outline=(44, 22, 46))
    d.rectangle([cx - 8, cy + 2, cx + 8, cy + 44], fill=(214, 174, 122))  # pecho crema
    # Bufanda larga morada-ámbar
    d.rounded_rectangle([cx - 22, cy - 10, cx + 22, cy + 6], radius=6, fill=(168, 68, 114), outline=ORO, width=2)
    d.polygon([(cx - 16, cy + 6), (cx - 6, cy + 6), (cx - 12, cy + 28), (cx - 22, cy + 24)], fill=(152, 56, 104))
    # OREJAS ENORMES DE FÉNEC (seña de identidad)
    d.polygon([(cx - 14, cy - 24), (cx - 52, cy - 68), (cx - 2, cy - 36)], fill=(244, 206, 156), outline=(84, 52, 44))
    d.polygon([(cx + 14, cy - 24), (cx + 52, cy - 68), (cx + 2, cy - 36)], fill=(244, 206, 156), outline=(84, 52, 44))
    d.polygon([(cx - 14, cy - 26), (cx - 42, cy - 58), (cx - 6, cy - 34)], fill=(208, 128, 126))
    d.polygon([(cx + 14, cy - 26), (cx + 42, cy - 58), (cx + 6, cy - 34)], fill=(208, 128, 126))
    # Cabeza triangular-suave de fénec
    d.ellipse([cx - 20, cy - 40, cx + 20, cy - 6], fill=(248, 214, 166), outline=(84, 52, 44), width=2)
    d.polygon([(cx - 10, cy - 16), (cx + 10, cy - 16), (cx, cy - 6)], fill=(255, 236, 206))
    d.ellipse([cx - 3, cy - 11, cx + 3, cy - 7], fill=(56, 30, 34))  # nariz
    # Ojos amables + gafas de latón subidas en la frente
    d.ellipse([cx - 11, cy - 24, cx - 5, cy - 18], fill=(38, 22, 28))
    d.ellipse([cx + 5, cy - 24, cx + 11, cy - 18], fill=(38, 22, 28))
    d.ellipse([cx - 14, cy - 38, cx - 2, cy - 27], fill=(116, 162, 184), outline=ORO, width=2)
    d.ellipse([cx + 2, cy - 38, cx + 14, cy - 27], fill=(116, 162, 184), outline=ORO, width=2)
    # Vara larga con farol de ámbar encendido
    d.line([(cx + 34, cy + 48), (cx + 34, cy - 34)], fill=(122, 78, 48), width=4)
    d.arc([cx + 32, cy - 42, cx + 52, cy - 22], 180, 360, fill=ORO, width=3)
    d.rectangle([cx + 38, cy - 24, cx + 54, cy - 4], fill=(255, 234, 152), outline=(146, 92, 42), width=2)
    d.ellipse([cx + 43, cy - 18, cx + 49, cy - 10], fill=(255, 250, 224))


def dibujar_fenec_aprendiz(d, cx, cy):
    """Opción B: Jioni, joven aprendiz de sombras (capa corta crepuscular, orejas alerta, linterna al cinto)."""
    d.ellipse([cx - 24, cy + 44, cx + 24, cy + 54], fill=(18, 10, 26))
    # Cola viva hacia la derecha
    d.ellipse([cx + 12, cy + 12, cx + 46, cy + 34], fill=(242, 198, 146), outline=(88, 52, 42), width=2)
    # Capa corta de atardecer abierta al viento
    d.polygon([(cx - 32, cy + 28), (cx - 16, cy - 6), (cx + 16, cy - 6), (cx + 30, cy + 26), (cx, cy + 16)],
              fill=(186, 86, 84), outline=ORO)
    # Cuerpo ágil y pantalones de viajero
    d.rectangle([cx - 12, cy - 2, cx + 12, cy + 32], fill=(64, 38, 76), outline=(38, 22, 48))
    d.rectangle([cx - 10, cy + 32, cx - 2, cy + 46], fill=(238, 198, 148))
    d.rectangle([cx + 2, cy + 32, cx + 10, cy + 46], fill=(238, 198, 148))
    # Linterna de mano colgada en la cintura
    d.ellipse([cx - 28, cy + 10, cx - 6, cy + 32], fill=(166, 114, 52))
    d.rectangle([cx - 22, cy + 16, cx - 12, cy + 28], fill=(255, 236, 156), outline=(120, 74, 34), width=2)
    # Orejas grandes y muy erguidas
    d.polygon([(cx - 12, cy - 24), (cx - 46, cy - 68), (cx - 2, cy - 36)], fill=(248, 212, 162), outline=(84, 52, 44))
    d.polygon([(cx + 12, cy - 24), (cx + 46, cy - 68), (cx + 2, cy - 36)], fill=(248, 212, 162), outline=(84, 52, 44))
    d.polygon([(cx - 12, cy - 26), (cx - 38, cy - 58), (cx - 5, cy - 34)], fill=(214, 132, 126))
    d.polygon([(cx + 12, cy - 26), (cx + 38, cy - 58), (cx + 5, cy - 34)], fill=(214, 132, 126))
    # Cabeza juvenil y ojos brillantes curiosos
    d.ellipse([cx - 18, cy - 38, cx + 18, cy - 6], fill=(252, 220, 174), outline=(84, 52, 44), width=2)
    d.ellipse([cx - 10, cy - 25, cx - 4, cy - 17], fill=(38, 22, 28))
    d.ellipse([cx + 4, cy - 25, cx + 10, cy - 17], fill=(38, 22, 28))
    d.ellipse([cx - 8, cy - 24, cx - 6, cy - 22], fill=(255, 255, 255))
    d.ellipse([cx + 6, cy - 24, cx + 8, cy - 22], fill=(255, 255, 255))
    d.ellipse([cx - 3, cy - 12, cx + 3, cy - 8], fill=(56, 30, 34))


def dibujar_jefe_sol_encadenado(d, cx, cy):
    """Opción A (recomendada): Jua-Giza, El Sol Encadenado (La Primera Sombra).
    Disco solar agrietado de bronce y luz atrapado en anillos de reloj detenidos y un manto vivo de sombras largas."""
    # Halo crepuscular y manto de sombras largas desplegándose hacia abajo
    d.ellipse([cx - 72, cy - 58, cx + 72, cy + 56], fill=(54, 24, 72))
    # Manto de sombras vivas (brazos/colas de penumbra violeta con filos dorados)
    for dx, dy in [(-68, 42), (-36, 56), (0, 62), (36, 56), (68, 42)]:
        d.polygon([(cx, cy + 6), (cx + dx - 10, cy + dy), (cx + dx + 10, cy + dy)],
                  fill=(28, 12, 46), outline=MALVA)
    # Anillos de reloj detenido girando en diagonal alrededor del sol
    d.ellipse([cx - 58, cy - 50, cx + 58, cy + 50], outline=ORO, width=3)
    d.ellipse([cx - 46, cy - 24, cx + 46, cy + 24], outline=(206, 134, 248), width=2)
    # 12 marcas de hora alrededor del aro exterior
    for k in range(12):
        ang = k * math.tau / 12.0
        p0 = (cx + math.cos(ang) * 53, cy + math.sin(ang) * 45)
        p1 = (cx + math.cos(ang) * 61, cy + math.sin(ang) * 52)
        d.line([p0, p1], fill=ORO, width=2)
    # Núcleo: disco solar agrietado por la primera veta violeta de Giza
    d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(246, 186, 86), outline=(255, 232, 162), width=3)
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(255, 224, 138))
    # Grieta violeta central (la primera herida de Giza) y dos ojos tristes de eclipse
    d.line([(cx - 18, cy - 22), (cx - 4, cy - 2), (cx + 6, cy + 6), (cx + 20, cy + 22)], fill=(122, 40, 178), width=4)
    d.line([(cx - 18, cy - 22), (cx - 4, cy - 2), (cx + 6, cy + 6), (cx + 20, cy + 22)], fill=(216, 146, 255), width=2)
    d.ellipse([cx - 13, cy - 7, cx - 5, cy + 1], fill=(32, 14, 48))
    d.ellipse([cx + 5, cy - 7, cx + 13, cy + 1], fill=(32, 14, 48))
    # Cadenas / pesos de reloj colgando abajo (lo que Maisha y Mauti sueltan al final)
    for px in (-38, 38):
        d.line([(cx + px, cy + 12), (cx + px, cy + 52)], fill=(184, 152, 108), width=2)
        d.polygon([(cx + px, cy + 44), (cx + px - 7, cy + 56), (cx + px + 7, cy + 56)], fill=(118, 86, 62), outline=ORO)


def dibujar_jefe_relojero(d, cx, cy):
    """Opción B: Mzee-Jua, El Relojero del Ocaso (silueta alta de antiguo guardián fénec con corona de agujas y péndulo)."""
    d.ellipse([cx - 48, cy + 46, cx + 48, cy + 58], fill=(18, 10, 26))
    # Capa enorme de cielo morado estrellado
    d.polygon([(cx - 54, cy + 50), (cx - 24, cy - 26), (cx + 24, cy - 26), (cx + 54, cy + 50)],
              fill=(54, 24, 78), outline=ORO)
    # Silueta alta central con pecho de esfera de reloj
    d.rectangle([cx - 18, cy - 24, cx + 18, cy + 44], fill=(32, 16, 48), outline=MALVA, width=2)
    d.ellipse([cx - 12, cy - 8, cx + 12, cy + 16], fill=(246, 198, 110), outline=(66, 32, 54), width=2)
    d.line([(cx, cy + 4), (cx + 8, cy - 2)], fill=(44, 22, 34), width=2)
    # Cabeza con orejas de sombra + corona de agujas solares
    d.polygon([(cx - 10, cy - 32), (cx - 32, cy - 64), (cx - 2, cy - 42)], fill=(44, 20, 62), outline=ORO)
    d.polygon([(cx + 10, cy - 32), (cx + 32, cy - 64), (cx + 2, cy - 42)], fill=(44, 20, 62), outline=ORO)
    d.ellipse([cx - 16, cy - 46, cx + 16, cy - 18], fill=(38, 18, 56), outline=ORO, width=2)
    d.ellipse([cx - 8, cy - 35, cx - 3, cy - 30], fill=(255, 220, 120))
    d.ellipse([cx + 3, cy - 35, cx + 8, cy - 30], fill=(255, 220, 120))
    # Péndulo gigante en la mano derecha
    d.line([(cx + 22, cy - 16), (cx + 58, cy + 36)], fill=ORO, width=3)
    d.ellipse([cx + 46, cy + 24, cx + 70, cy + 48], fill=(246, 184, 86), outline=(255, 236, 174), width=2)


def envolver(d, texto, max_w, font):
    palabras = texto.split()
    lineas, actual = [], ""
    for p in palabras:
        prueba = p if not actual else actual + " " + p
        if d.textlength(prueba, font=font) > max_w and actual:
            lineas.append(actual)
            actual = p
        else:
            actual = prueba
    if actual:
        lineas.append(actual)
    return lineas


def tarjeta(d, rect, titulo, subtitulo, lineas, dibujar_fn, recomendado, fb, fp):
    x0, y0, x1, y1 = rect
    bg = PANEL_REC if recomendado else PANEL
    out = ORO if recomendado else (136, 98, 152)
    d.rounded_rectangle(rect, radius=10, fill=bg, outline=out, width=2)
    # Vitrina del personaje a la izquierda
    vx, vy = x0 + 96, y0 + 138
    d.rounded_rectangle([x0 + 14, y0 + 48, x0 + 180, y1 - 14], radius=8, fill=(22, 14, 34), outline=(92, 62, 114))
    dibujar_fn(d, vx, vy)
    # Cabecera
    d.text((x0 + 16, y0 + 12), titulo, fill=ORO if recomendado else CREMA, font=fb)
    if recomendado:
        badge = "RECOMENDADA"
        bw = d.textlength(badge, font=fp) + 14
        d.rounded_rectangle([x1 - bw - 12, y0 + 10, x1 - 12, y0 + 30], radius=5, fill=(104, 64, 24), outline=ORO)
        d.text((x1 - bw - 5, y0 + 13), badge, fill=(255, 236, 172), font=fp)
    # Texto descriptivo a la derecha de la vitrina
    tx = x0 + 194
    max_w = x1 - tx - 14
    d.text((tx, y0 + 50), subtitulo, fill=MALVA, font=fb)
    yy = y0 + 76
    for ln in lineas:
        for sub in envolver(d, ln, max_w, fp):
            d.text((tx, yy), sub, fill=CREMA, font=fp)
            yy += 18
        yy += 6


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    try:
        ft = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 16)
        fs = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 14)
        fb = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 13)
        fp = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana.ttf", 12)
    except OSError:
        ft = fs = fb = fp = ImageFont.load_default()

    d.text((22, 12), "EL VALLE DEL OCASO — Guía Mbweha y Jefe Final (Opciones para decidir con Iam)", fill=ORO, font=ft)

    # Sección 1: El guía zorro fénec (mbweha)
    d.text((24, 46), "1. EL GUÍA ZORRO FÉNEC (MBWEHA) — espera en El Mirador del Ocaso y enseña Luz y Sombra",
           fill=(255, 224, 162), font=fs)
    tarjeta(
        d, [22, 72, 520, 338],
        "OPCIÓN A · Mwanga, el Viejo Farolillero",
        "Tranquilo, cálido y lleno de memoria",
        [
            "• Fue quien encendió el último farol antes de que detuvieran el sol.",
            "• Orejas altísimas que oyen el paso del tiempo, gafas de latón y vara con farol de ámbar.",
            "• Contraste emotivo: entiende el miedo de su pueblo, pero echa de menos las estrellas.",
        ],
        dibujar_fenec_viejo, True, fb, fp
    )
    tarjeta(
        d, [540, 72, 1038, 338],
        "OPCIÓN B · Jioni, el Joven Aprendiz",
        "Ágil, curioso y sin miedo a la noche",
        [
            "• Nunca ha visto la noche de verdad: nació ya en el atardecer eterno.",
            "• Capa corta crepuscular y linterna de mano atada a la cintura.",
            "• Acompaña a Maisha saltando por las sombras-puente y guía hacia la ciudad.",
        ],
        dibujar_fenec_aprendiz, False, fb, fp
    )

    # Sección 2: El Jefe Final en El Horizonte Inmóvil (donde nace Giza)
    d.text((24, 360), "2. EL JEFE FINAL EN EL HORIZONTE INMÓVIL (DONDE NACE GIZA) — cierre de la historia",
           fill=(228, 174, 255), font=fs)
    tarjeta(
        d, [22, 386, 520, 678],
        "OPCIÓN A · Jua-Giza, El Sol Encadenado",
        "La Primera Sombra · origen de Giza",
        [
            "• Un disco solar agrietado envuelto en aros de reloj detenidos y un manto vivo de sombras.",
            "• Combate final de Luz y Sombra: rota el atardecer en la arena creando puentes de sombra y rayos solares.",
            "• Clímax emotivo: Maisha y Mauti no lo destruyen; sueltan los pesos del reloj para que llegue la primera noche estrellada.",
        ],
        dibujar_jefe_sol_encadenado, True, fb, fp
    )
    tarjeta(
        d, [540, 386, 1038, 678],
        "OPCIÓN B · Mzee-Jua, el Relojero del Ocaso",
        "El antiguo guardián fénec que paró el sol",
        [
            "• El patriarca que encadenó el atardecer por terror a perder a los suyos, convertido en silueta colosal.",
            "• Barre la arena con su péndulo gigante y cambia la hora de golpe.",
            "• Al caer su máscara de sombra, recuerda que el descanso de la noche trae un nuevo día.",
        ],
        dibujar_jefe_relojero, False, fb, fp
    )

    out = os.path.join(RAIZ, "documentacion", "boceto_personajes_ocaso.png")
    img.save(out)
    print("Guardado:", out)


if __name__ == "__main__":
    main()
