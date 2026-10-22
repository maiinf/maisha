#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_referencias_visuales_3d.py
Genera las hojas de referencia visuales (Model Sheets y Concept Art técnico)
para que Claude las utilice al modelar en Blender.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_REFS = os.path.join(BASE_DIR, "documentacion", "referencias_visuales_3d")
DIR_PERSONAJES = os.path.join(DIR_REFS, "personajes")
DIR_CONSTRUCCIONES = os.path.join(DIR_REFS, "construcciones")
DIR_MAPEADO = os.path.join(DIR_REFS, "mapeado")

for d in [DIR_PERSONAJES, DIR_CONSTRUCCIONES, DIR_MAPEADO]:
    os.makedirs(d, exist_ok=True)

# -----------------------------------------------------------------------------
# UTILIDADES DE DIBUJO DE FICHAS TÉCNICAS
# -----------------------------------------------------------------------------

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def crear_lienzo_ficha(ancho=1000, alto=700, titulo="FICHA DE MODELADO 3D", subtitulo=""):
    im = Image.new("RGBA", (ancho, alto), hex_to_rgb("#16181f"))
    draw = ImageDraw.Draw(im)

    # Rejilla suave de fondo
    grid_col = hex_to_rgb("#1e222d")
    for x in range(0, ancho, 25):
        draw.line([(x, 0), (x, alto)], fill=grid_col, width=1)
    for y in range(0, alto, 25):
        draw.line([(0, y), (ancho, y)], fill=grid_col, width=1)

    # Cabecera superior
    draw.rectangle([(0, 0), (ancho, 55)], fill=hex_to_rgb("#232838"))
    draw.line([(0, 55), (ancho, 55)], fill=hex_to_rgb("#4a5578"), width=2)
    
    # Textos de cabecera
    draw.text((25, 12), titulo, fill=hex_to_rgb("#f5f6fa"))
    if subtitulo:
        draw.text((25, 32), subtitulo, fill=hex_to_rgb("#9baacf"))

    # Pie de página
    draw.line([(0, alto - 30), (ancho, alto - 30)], fill=hex_to_rgb("#2d3345"), width=1)
    draw.text((25, alto - 22), "MAISHA 3D · Pipeline de Referencia Visual Gemini -> Blender Claude", fill=hex_to_rgb("#636e88"))
    draw.text((ancho - 280, alto - 22), "Godot 4.7 · Blender 5.2 · Escala: 1m = 1 Blender Unit", fill=hex_to_rgb("#636e88"))

    return im, draw

def dibujar_paleta(draw, x_base, y_base, colores, titulo="PALETA DE MATERIALES"):
    draw.text((x_base, y_base), titulo, fill=hex_to_rgb("#e0e6ed"))
    y = y_base + 22
    for hex_c, nombre, desc in colores:
        rgb = hex_to_rgb(hex_c)
        draw.rectangle([(x_base, y), (x_base + 32, y + 20)], fill=rgb, outline=hex_to_rgb("#ffffff"), width=1)
        draw.text((x_base + 40, y + 2), f"{nombre} ({hex_c})", fill=hex_to_rgb("#ffffff"))
        draw.text((x_base + 240, y + 2), desc, fill=hex_to_rgb("#8f9cb5"))
        y += 28
    return y

def dibujar_caja_info(draw, x0, y0, x1, y1, titulo, lineas):
    draw.rectangle([(x0, y0), (x1, y1)], fill=hex_to_rgb("#1a1e2b"), outline=hex_to_rgb("#3a435e"), width=1)
    draw.rectangle([(x0, y0), (x1, y0 + 26)], fill=hex_to_rgb("#23293b"))
    draw.text((x0 + 10, y0 + 6), titulo, fill=hex_to_rgb("#ffcc00"))
    y = y0 + 34
    for linea in lineas:
        draw.text((x0 + 10, y), linea, fill=hex_to_rgb("#cbd5e1"))
        y += 18

# -----------------------------------------------------------------------------
# 1. REFERENCIA VISUAL: MAISHA (PROTAGONISTA)
# -----------------------------------------------------------------------------

def generar_referencia_maisha():
    im, draw = crear_lienzo_ficha(
        1050, 720,
        "PERSONAJE: MAISHA (ESPÍRITU DE LA VIDA)",
        "Modelo objetivo: modelos/personajes/maisha.glb · Estilo: Chibi / Diorama Cuento"
    )

    # Vista Frontal
    cx_f, cy_f = 240, 260
    # Sombra en suelo
    draw.ellipse([(cx_f - 70, cy_f + 160), (cx_f + 70, cy_f + 185)], fill=hex_to_rgb("#0d0f14"))
    
    # 1. Cuerpo cónico (torso)
    draw.polygon([
        (cx_f - 35, cy_f + 80), (cx_f + 35, cy_f + 80),
        (cx_f + 50, cy_f + 140), (cx_f - 50, cy_f + 140)
    ], fill=hex_to_rgb("#f5efe6"), outline=hex_to_rgb("#d6cbbe"), width=2)

    # 2. Piernas
    draw.rectangle([(cx_f - 30, cy_f + 140), (cx_f - 12, cy_f + 170)], fill=hex_to_rgb("#4a3e35"))
    draw.rectangle([(cx_f + 12, cy_f + 140), (cx_f + 30, cy_f + 170)], fill=hex_to_rgb("#4a3e35"))

    # 3. Cabeza esférica chibi (grande, dulce)
    draw.ellipse([(cx_f - 65, cy_f - 40), (cx_f + 65, cy_f + 80)], fill=hex_to_rgb("#f5efe6"), outline=hex_to_rgb("#d6cbbe"), width=2)

    # 4. Ojos ovalados y expresivos
    draw.ellipse([(cx_f - 32, cy_f + 10), (cx_f - 14, cy_f + 38)], fill=hex_to_rgb("#18161a"))
    draw.ellipse([(cx_f + 14, cy_f + 10), (cx_f + 32, cy_f + 38)], fill=hex_to_rgb("#18161a"))
    # Brillos blancos en los ojos
    draw.ellipse([(cx_f - 26, cy_f + 14), (cx_f - 20, cy_f + 22)], fill=(255, 255, 255))
    draw.ellipse([(cx_f + 20, cy_f + 14), (cx_f + 26, cy_f + 22)], fill=(255, 255, 255))

    # 5. Mejillas ruborizadas
    draw.ellipse([(cx_f - 46, cy_f + 34), (cx_f - 26, cy_f + 46)], fill=hex_to_rgb("#e89999"))
    draw.ellipse([(cx_f + 26, cy_f + 34), (cx_f + 46, cy_f + 46)], fill=hex_to_rgb("#e89999"))

    # 6. Brote en la cabeza (tallo + 2 hojas vivas)
    draw.line([(cx_f, cy_f - 40), (cx_f - 4, cy_f - 75)], fill=hex_to_rgb("#4c8a38"), width=5)
    draw.ellipse([(cx_f - 32, cy_f - 95), (cx_f - 4, cy_f - 70)], fill=hex_to_rgb("#66b34a"), outline=hex_to_rgb("#3a6e29"), width=1)
    draw.ellipse([(cx_f - 2, cy_f - 92), (cx_f + 28, cy_f - 68)], fill=hex_to_rgb("#7ed95c"), outline=hex_to_rgb("#3a6e29"), width=1)

    # 7. Corazón de Asili (en el pecho, brillante)
    draw.polygon([
        (cx_f, cy_f + 95), (cx_f + 12, cy_f + 107),
        (cx_f, cy_f + 122), (cx_f - 12, cy_f + 107)
    ], fill=hex_to_rgb("#f5c842"), outline=hex_to_rgb("#b38612"), width=2)

    # 8. Brazos
    draw.line([(cx_f - 35, cy_f + 90), (cx_f - 60, cy_f + 120)], fill=hex_to_rgb("#f5efe6"), width=10)
    draw.line([(cx_f + 35, cy_f + 90), (cx_f + 60, cy_f + 115)], fill=hex_to_rgb("#f5efe6"), width=10)

    # 9. Cetro de Raíz (en mano derecha de Maisha)
    draw.line([(cx_f + 65, cy_f + 45), (cx_f + 65, cy_f + 175)], fill=hex_to_rgb("#6b492b"), width=5)
    draw.ellipse([(cx_f + 56, cy_f + 32), (cx_f + 74, cy_f + 50)], fill=hex_to_rgb("#41c4a0"), outline=hex_to_rgb("#1a6953"), width=2)

    draw.text((cx_f - 35, cy_f + 195), "VISTA FRONTAL", fill=hex_to_rgb("#8aa2c8"))

    # Vista Lateral (Perfil)
    cx_l, cy_l = 510, 260
    draw.ellipse([(cx_l - 60, cy_l + 160), (cx_l + 60, cy_l + 185)], fill=hex_to_rgb("#0d0f14"))
    
    # Torso de perfil
    draw.polygon([
        (cx_l - 25, cy_l + 80), (cx_l + 30, cy_l + 80),
        (cx_l + 35, cy_l + 140), (cx_l - 30, cy_l + 140)
    ], fill=hex_to_rgb("#ede6dc"), outline=hex_to_rgb("#d6cbbe"), width=2)
    draw.rectangle([(cx_l - 10, cy_l + 140), (cx_l + 10, cy_l + 170)], fill=hex_to_rgb("#4a3e35"))

    # Cabeza de perfil
    draw.ellipse([(cx_l - 55, cy_l - 40), (cx_l + 55, cy_l + 80)], fill=hex_to_rgb("#f5efe6"), outline=hex_to_rgb("#d6cbbe"), width=2)
    draw.ellipse([(cx_l - 45, cy_l + 12), (cx_l - 30, cy_l + 38)], fill=hex_to_rgb("#18161a"))
    draw.ellipse([(cx_l - 42, cy_l + 16), (cx_l - 36, cy_l + 24)], fill=(255, 255, 255))
    draw.ellipse([(cx_l - 50, cy_l + 34), (cx_l - 32, cy_l + 46)], fill=hex_to_rgb("#e89999"))

    # Brote lateral
    draw.line([(cx_l, cy_l - 40), (cx_l - 10, cy_l - 75)], fill=hex_to_rgb("#4c8a38"), width=5)
    draw.ellipse([(cx_l - 30, cy_l - 92), (cx_l + 10, cy_l - 70)], fill=hex_to_rgb("#66b34a"), outline=hex_to_rgb("#3a6e29"), width=1)

    # Brazo y gema de Asili en pecho
    draw.polygon([(cx_l - 30, cy_l + 102), (cx_l - 20, cy_l + 110), (cx_l - 30, cy_l + 120)], fill=hex_to_rgb("#f5c842"))
    draw.line([(cx_l, cy_l + 90), (cx_l - 20, cy_l + 125)], fill=hex_to_rgb("#f5efe6"), width=10)

    draw.text((cx_l - 30, cy_l + 195), "VISTA PERFIL", fill=hex_to_rgb("#8aa2c8"))

    # Cajas de especificaciones
    dibujar_caja_info(
        draw, 680, 75, 1020, 310,
        "GUÍA DE MODELADO BLENDER",
        [
            "• Escala: Altura total 1.05m (cabeza r=0.38m).",
            "• Geometría: Malla estilizada 'low/mid-poly'.",
            "• Sombras suaves: 'Shade Smooth' con bordes limpios.",
            "• Ojos: Malla incrustada o textura pintada NEAREST.",
            "• Cetro: Accesorio independiente emparentado",
            "  al hueso 'hand_R' (Hand_R).",
            "• Brote: Tallo flexible con 2 hojas para animar",
            "  leve balanceo con el viento y saltos."
        ]
    )

    dibujar_caja_info(
        draw, 680, 330, 1020, 480,
        "ESTRUCTURA DE ARMATURE (RIG)",
        [
            "root (suelo)",
            " └─ hips (pelvis) [0.45m]",
            "     ├─ spine -> chest -> neck -> head [0.95m]",
            "     │    └─ sprout (brote) [1.25m]",
            "     ├─ arm_L / arm_R -> hand_R (cetro)",
            "     └─ leg_L / leg_R -> foot_L / foot_R"
        ]
    )

    # Paleta de Colores
    paleta_maisha = [
        ("#f5efe6", "Cuerpo Maisha", "Piel marfil suave, BSDF Roughness 0.6"),
        ("#4a3e35", "Extremidades", "Marrón corteza suave para pies/sombra"),
        ("#66b34a", "Brote Verde", "Hojas vivas, color orgánico fresco"),
        ("#f5c842", "Corazón Asili", "Oro cálido, Emisión 0.8 en combates"),
        ("#41c4a0", "Gema Cetro", "Esmeralda vida, Emisión 1.2 mágica"),
        ("#6b492b", "Madera Cetro", "Vara de roble antiguo tallado"),
        ("#18161a", "Ojos Negros", "Expresivos con brillo especular"),
        ("#e89999", "Rubor", "Mejillas tiernas / calidez infantil")
    ]
    dibujar_paleta(draw, 40, 490, paleta_maisha, "PALETA OFICIAL DE MATERIALES")

    out_path = os.path.join(DIR_PERSONAJES, "ref_maisha.png")
    im.save(out_path)
    print(f"Generado: {out_path}")

# -----------------------------------------------------------------------------
# 2. REFERENCIA VISUAL: CASA GRANJA DE MZEE SHAMBA (EL KITOVU)
# -----------------------------------------------------------------------------

def generar_referencia_casa_granja():
    im, draw = crear_lienzo_ficha(
        1050, 720,
        "CONSTRUCCIÓN: CASA GRANJA DE MZEE SHAMBA (EL KITOVU)",
        "Modelo objetivo: modelos/entorno/casa_granja.glb · Estilo: Arquitectura 360° Sólida"
    )

    cx, cy = 340, 290
    draw.ellipse([(cx - 220, cy + 130), (cx + 220, cy + 220)], fill=hex_to_rgb("#0d0f14"))

    # 1. Zócalo de mampostería de piedra
    draw.polygon([
        (cx - 150, cy + 100), (cx + 10, cy + 160),
        (cx + 160, cy + 90), (cx, cy + 30)
    ], fill=hex_to_rgb("#5e636b"), outline=hex_to_rgb("#3d4147"), width=2)

    # 2. Muros de troncos horizontales
    draw.polygon([
        (cx - 150, cy + 100), (cx + 10, cy + 160),
        (cx + 10, cy + 30), (cx - 150, cy - 30)
    ], fill=hex_to_rgb("#855430"), outline=hex_to_rgb("#4a2c14"), width=2)
    draw.polygon([
        (cx + 10, cy + 160), (cx + 160, cy + 90),
        (cx + 160, cy - 40), (cx + 10, cy + 30)
    ], fill=hex_to_rgb("#663f22"), outline=hex_to_rgb("#3d2412"), width=2)

    # Puerta frontal de madera
    draw.polygon([
        (cx - 70, cy + 130), (cx - 30, cy + 145),
        (cx - 30, cy + 70), (cx - 70, cy + 55)
    ], fill=hex_to_rgb("#452b17"), outline=hex_to_rgb("#f5c842"), width=1)

    # Ventana con luz cálida interior
    draw.polygon([
        (cx + 50, cy + 100), (cx + 110, cy + 70),
        (cx + 110, cy + 25), (cx + 50, cy + 55)
    ], fill=hex_to_rgb("#ffcc33"), outline=hex_to_rgb("#331e0f"), width=2)

    # 3. Tejado a dos aguas de madera de cedro
    draw.polygon([
        (cx - 170, cy - 20), (cx + 20, cy + 50),
        (cx - 60, cy - 120)
    ], fill=hex_to_rgb("#ab5e35"), outline=hex_to_rgb("#572c14"), width=2)
    draw.polygon([
        (cx + 20, cy + 50), (cx + 180, cy - 30),
        (cx + 90, cy - 180), (cx - 60, cy - 120)
    ], fill=hex_to_rgb("#8c4623"), outline=hex_to_rgb("#421d09"), width=2)

    # 4. Chimenea de piedra caliza con boca y humo
    draw.polygon([
        (cx + 80, cy - 140), (cx + 120, cy - 120),
        (cx + 120, cy - 50), (cx + 80, cy - 70)
    ], fill=hex_to_rgb("#828894"), outline=hex_to_rgb("#444952"), width=2)
    draw.ellipse([(cx + 95, cy - 170), (cx + 125, cy - 145)], fill=hex_to_rgb("#d9e0eb"))
    draw.ellipse([(cx + 115, cy - 205), (cx + 155, cy - 170)], fill=hex_to_rgb("#e8eef7"))

    # 5. Rueda de molino de agua hidráulica en el lateral izquierdo
    rx, ry = cx - 180, cy + 90
    draw.ellipse([(rx - 35, ry - 35), (rx + 35, ry + 35)], fill=hex_to_rgb("#4a301c"), outline=hex_to_rgb("#29170a"), width=2)
    draw.line([(rx - 35, ry), (rx + 35, ry)], fill=hex_to_rgb("#8c5a32"), width=3)
    draw.line([(rx, ry - 35), (rx, ry + 35)], fill=hex_to_rgb("#8c5a32"), width=3)
    # Canaleta de agua que alimenta la rueda
    draw.polygon([
        (rx - 20, ry - 45), (rx + 40, ry - 45),
        (rx + 50, ry - 35), (rx - 10, ry - 35)
    ], fill=hex_to_rgb("#52a3c7"))

    draw.text((cx - 80, cy + 185), "PERSPECTIVA DIORAMA 3D", fill=hex_to_rgb("#8aa2c8"))

    # Especificaciones técnicas
    dibujar_caja_info(
        draw, 680, 75, 1020, 310,
        "ESPECIFICACIONES DE MODELADO",
        [
            "• Dimensiones: 5.0m frente × 4.2m fondo × 4.8m alto.",
            "• Geometría sólida 360°: Pared trasera completa",
            "  con ventana auxiliar y leñera de troncos.",
            "• Rueda de molino: Malla separada para animar",
            "  rotación continua en eje X/Y.",
            "• Ventanas: Material con emisión cálida",
            "  (Roughness 0.2, Emission strength 1.5).",
            "• Chimenea: Boca abierta superior preparada para",
            "  emisor de partículas de humo de Godot."
        ]
    )

    dibujar_caja_info(
        draw, 680, 330, 1020, 480,
        "ELEMENTOS AUXILIARES DE LA FINCA",
        [
            "• Pozo antiguo de piedra con manivela (pozo_antiguo.glb).",
            "• Espantapájaros de paja con camisa remendada.",
            "• Carro de madera volcado junto al pajar.",
            "• Valla rústica de estacas unidas con cuerda.",
            "• Canal de acequia con fondo de grava y agua viva."
        ]
    )

    paleta_granja = [
        ("#855430", "Troncos Fachada", "Madera rústica de pino envejecido"),
        ("#ab5e35", "Tejado Cedro", "Tablones solapados, impermeable"),
        ("#5e636b", "Piedra Zócalo", "Mampostería de río gris con musgo"),
        ("#828894", "Chimenea Caliza", "Sillares resistentes al fuego"),
        ("#ffcc33", "Luz de Hogar", "Ventana iluminada por fuego interior"),
        ("#4a301c", "Rueda Molino", "Madera mojada oscurecida por agua"),
        ("#52a3c7", "Agua Acequia", "Corriente cristalina en canaleta")
    ]
    dibujar_paleta(draw, 40, 490, paleta_granja, "PALETA DE MATERIALES GRANJA")

    out_path = os.path.join(DIR_CONSTRUCCIONES, "ref_casa_granja.png")
    im.save(out_path)
    print(f"Generado: {out_path}")

# -----------------------------------------------------------------------------
# 3. REFERENCIA VISUAL: DIORAMA EL KITOVU (MAPA Y ENTORNO 3D)
# -----------------------------------------------------------------------------

def generar_referencia_mapa_kitovu():
    im, draw = crear_lienzo_ficha(
        1050, 720,
        "MAPEADO 3D: DIORAMA TUTORIAL 'EL KITOVU'",
        "Escena objetivo: escenas/mundo_3d/kitovu_3d.tscn · Estilo: Maqueta Viva / Cuento"
    )

    cx, cy = 340, 280

    # Base de tierra / roca del diorama
    draw.polygon([
        (cx - 240, cy + 40), (cx, cy + 150),
        (cx + 240, cy + 40), (cx, cy - 70)
    ], fill=hex_to_rgb("#4a7a38"), outline=hex_to_rgb("#2c4a20"), width=2)

    # Grosor vertical del bloque de terreno
    draw.polygon([
        (cx - 240, cy + 40), (cx, cy + 150),
        (cx, cy + 200), (cx - 240, cy + 90)
    ], fill=hex_to_rgb("#5c4632"), outline=hex_to_rgb("#382717"), width=2)
    draw.polygon([
        (cx, cy + 150), (cx + 240, cy + 40),
        (cx + 240, cy + 90), (cx, cy + 200)
    ], fill=hex_to_rgb("#473423"), outline=hex_to_rgb("#2e1f13"), width=2)

    # Río / Acequia curvada que atraviesa el terreno
    draw.polygon([
        (cx - 140, cy - 30), (cx - 80, cy + 10),
        (cx - 40, cy + 70), (cx - 10, cy + 145),
        (cx + 25, cy + 140), (cx, cy + 60),
        (cx - 40, cy), (cx - 110, cy - 40)
    ], fill=hex_to_rgb("#3d98bd"))

    # Huerto vallado con zanahorias
    draw.polygon([
        (cx + 40, cy + 30), (cx + 120, cy + 70),
        (cx + 170, cy + 40), (cx + 90, cy)
    ], fill=hex_to_rgb("#69482b"), outline=hex_to_rgb("#856238"), width=1)
    for zx, zy in [(cx + 70, cy + 35), (cx + 100, cy + 50), (cx + 130, cy + 45), (cx + 110, cy + 25)]:
        draw.ellipse([(zx - 3, zy - 5), (zx + 3, zy + 1)], fill=hex_to_rgb("#5da348"))

    # Mancha de la casona
    draw.rectangle([(cx - 70, cy - 50), (cx + 10, cy + 10)], fill=hex_to_rgb("#855430"), outline=hex_to_rgb("#ab5e35"), width=2)
    draw.text((cx - 50, cy - 25), "[GRANJA]", fill=(255, 255, 255))

    # Sendero de tierra suave
    draw.polygon([
        (cx - 50, cy + 10), (cx + 10, cy + 25),
        (cx + 40, cy + 100), (cx + 10, cy + 110)
    ], fill=hex_to_rgb("#a3885d"))

    draw.text((cx - 90, cy + 220), "ESQUEMA DIORAMA EL KITOVU", fill=hex_to_rgb("#8aa2c8"))

    # Especificaciones de Mapeado
    dibujar_caja_info(
        draw, 680, 75, 1020, 310,
        "ESTRUCTURA DEL MAPA 3D (GODOT 4)",
        [
            "• Terreno modular: Bloques de césped de 2×2m con",
            "  desniveles suaves (altura 0.5m y 1.0m).",
            "• Agua viva: Plano de agua con profundidad, espuma",
            "  en orillas y lecho de piedras.",
            "• Shaders: Cel-shading suave, sombreado de",
            "  hierba que reacciona a los pasos de Maisha.",
            "• Iluminación: Luz de sol cálida (35° inclinación),",
            "  niebla suave de horizonte y tilt-shift de maqueta."
        ]
    )

    dibujar_caja_info(
        draw, 680, 330, 1020, 480,
        "REPARTO DE TRABAJO (CLAUDE & GEMINI)",
        [
            "1. Claude modela en Blender: casa_granja.glb,",
            "   pozo_antiguo.glb, espantapajaros.glb, vallas.",
            "2. Gemini ensambla el mapa 3D en Godot:",
            "   Coloca las mallas, ajusta colisiones 3D,",
            "   materiales de terreno y compone la música.",
            "3. Claude conecta la lógica de Mzee Shamba,",
            "   diálogos y primera misión en la escena 3D."
        ]
    )

    paleta_kitovu = [
        ("#4a7a38", "Césped Kitovu", "Verde cálido de pradera viva"),
        ("#3d98bd", "Agua Acequia", "Agua pura con reflejos celestes"),
        ("#a3885d", "Sendero Tierra", "Tierra compacta pisada por aldeanos"),
        ("#69482b", "Tierra de Huerto", "Suelo fértil húmedo para zanahorias"),
        ("#5c4632", "Roca Basal", "Corte geológico del diorama en corte")
    ]
    dibujar_paleta(draw, 40, 490, paleta_kitovu, "PALETA DE ENTORNO KITOVU")

    out_path = os.path.join(DIR_MAPEADO, "ref_mapa_kitovu.png")
    im.save(out_path)
    print(f"Generado: {out_path}")

# -----------------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------------------------------------------------------

def main():
    print("Iniciando generación de hojas de referencia visuales 3D...")
    generar_referencia_maisha()
    generar_referencia_casa_granja()
    generar_referencia_mapa_kitovu()
    print("Todas las hojas de referencia visuales han sido generadas con éxito.")

if __name__ == "__main__":
    main()
