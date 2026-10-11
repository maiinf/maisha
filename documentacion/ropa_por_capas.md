# Ropa por capas de Maisha

Maisha va cambiando de aspecto según las **Artes** que aprende. En lugar de redibujarla entera cada vez, la ropa se dibuja **aparte** y el juego la coloca encima (o detrás) de Maisha en cada fotograma.

**Idea clave:** cada prenda se dibuja **una sola vez por dirección** (abajo, arriba, lado). Al andar o respirar, el juego la mueve sola siguiendo los **puntos de anclaje** (cabeza, cuerpo, brazos, pies).

---

## Las 7 zonas

| Zona | Arte que la usa | Ejemplo |
| --- | --- | --- |
| cabeza | Raíz | Corona de hojas ✅ |
| espalda | Raíz | Capa de musgo ✅ |
| cara | Runa | Antifaz de sigilos |
| torso | Runa | Peto rúnico |
| brazos | Tierra | Brazaletes de piedra |
| piernas | Tierra | Botas de raíz |
| aura | Aliento | Brillo alrededor del cuerpo |
| arma | — | Cetro-rama ✅ (cambia de aspecto en cada mundo) |

Solo se lleva **una prenda por zona**: ponerse otra en la misma zona sustituye a la anterior.
Las grietas de **Giza** irán por encima de todo (se harán con un efecto, no con una prenda).

---

## Los puntos de anclaje

Mira `documentacion/plantilla_anclajes_ropa.png`: muestra cada vista con sus puntos de anclaje en la pose de reposo.

| Anclaje | Vistas | Qué marca (esquina superior izquierda de…) |
| --- | --- | --- |
| `cabeza` | todas | …la cabeza (sin el brote) |
| `cuerpo` | todas | …el cuerpo |
| `brazo_izq`, `brazo_der` | abajo, arriba | …cada brazo |
| `brazo` | lado | …el brazo visible |
| `pie_izq`, `pie_der` | abajo, arriba | …la última fila de cada pierna (la suela) |
| `mano` | todas | la mano que sujeta el cetro (un punto, no una esquina) |
| `piernas` | lado | …el bloque de las dos piernas |

Las posiciones de cada fotograma están en `datos/maisha_anclajes.json` (las genera `herramientas/dibujar_maisha.py`).

---

## Cómo añadir una prenda nueva (paso a paso)

### 1. Dibujarla en Pixelorama

1. Abre `arte/personajes/maisha/maisha_base_frente.png` (24×32) y ponlo en una capa de referencia.
2. Crea una capa nueva y dibuja la prenda encima, con la **paleta de Raíz** y su **propio contorno** (el tono más oscuro de su material).
3. **Nunca tapes el corazón del pecho ni los ojos**: son los rasgos fijos de Maisha.
4. Exporta **solo la prenda** (fondo transparente), recortada a su tamaño, en
   `arte/personajes/maisha/prendas/`, por ejemplo `botas_raiz_abajo.png`.
5. Apunta en qué píxel de la plantilla queda **su esquina superior izquierda**. Por ejemplo: x=6, y=29.
6. Repite con la vista de espalda (`_arriba`) y la de perfil (`_lado`, mirando a la derecha).

### 2. Calcular el desplazamiento

**desplazamiento = posición de la prenda − posición del anclaje**

Ejemplo: unas botas en x=6, y=29 colgadas de `pie_izq` (x=7, y=31) → desplazamiento **[-1, -2]**.

### 3. Añadirla al catálogo `datos/prendas.json`

Copia el bloque de una prenda existente y cambia los datos:

```json
"botas_raiz": {
  "nombre": "Botas de raíz",
  "zona": "piernas",
  "arte": "tierra",
  "piezas": {
    "abajo": [
      {"textura": "res://arte/personajes/maisha/prendas/botas_raiz_izq_abajo.png",
       "ancla": "pie_izq", "desplazamiento": [-1, -2], "delante": true},
      {"textura": "res://arte/personajes/maisha/prendas/botas_raiz_der_abajo.png",
       "ancla": "pie_der", "desplazamiento": [-1, -2], "delante": true}
    ],
    "arriba": [ ... ],
    "lado": [ ... ]
  }
}
```

- **`delante`:** `true` si se dibuja encima de Maisha y `false` si va detrás (como la capa vista de frente).
- Una prenda puede tener **varias piezas** por vista: cada bota se cuelga de su pie y la capa lleva un broche aparte.

### 4. Probarla

Abre el proyecto en Godot y pulsa `⌘ + B`. En la escena de prueba, las teclas **1 a 8** cambian la prenda de cada zona (1 cabeza, 2 cara, 3 espalda, 4 torso, 5 brazos, 6 piernas, 7 aura, 8 arma). Cada pulsación pasa a la siguiente prenda de esa zona y, después de la última, la quita.

> Si el programa `herramientas/dibujar_prendas.py` se vuelve a ejecutar, **solo reescribe las prendas que dibuja él** (corona y capa). Las que añadas tú a mano en `prendas.json` se conservan.

---

## Cómo se usa desde el código

```gdscript
$Maisha/Ropa.poner("corona_hojas")       # ponerse una prenda
$Maisha/Ropa.quitar_zona("cabeza")       # quitarse lo de esa zona
$Maisha/Ropa.alternar("capa_musgo")      # ponérsela o quitársela
$Maisha/Ropa.lleva("capa_musgo")         # ¿la lleva puesta?
```

Más adelante, el **Árbol de la Vida** llamará a `poner()` cada vez que Maisha aprenda un Arte.
