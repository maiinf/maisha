# Catálogo de Modelos 3D y Activos Blender — Maisha

> Sincronizado automáticamente con la bóveda de Obsidian y el Game Design Document oficial de Maisha.
> Pipeline: Blender 4.5.15 LTS (Darwin x86_64) $\rightarrow$ Godot 4.7 (GL Compatibility).

---

## 1. Identidad Visual y Paleta 3D

Los materiales utilizan **Principled BSDF** estilizado (rugosidad media, sin ruido fotorrealista, sombras suaves y canales emisivos vibrantes para la vida y la corrupción).

| Clave | Hex Base | Propósito | Emisión |
| :--- | :--- | :--- | :--- |
| `Mat_Maisha_Cuerpo` | `#FFE08A` | Tono dorado cálido principal del espíritu de Maisha | — |
| `Mat_Maisha_Sombra` | `#E8B860` | Sombra y extremidades | — |
| `Mat_Brote_Verde` | `#6FCF4F` | Brote de la cabeza y vegetación viva | `#86EFAC` (0.3) |
| `Mat_Corazon_Asili` | `#DF9022` | Corazón de Asili en el pecho y mechas vivas | `#FFF8E8` (2.2) |
| `Mat_Ojos_Negros` | `#140E18` | Ojos de obsidiana con brillo especular | — |
| `Mat_Rubor` | `#DE6771` | Expresión tímida en mejillas | — |
| `Mat_Cetro_Madera` | `#7A4A2A` | Madera orgánica del Cetro de Raíz | — |
| `Mat_Cetro_Gema` | `#FFAA00` | Núcleo de luz del cetro | `#FFDD00` (3.0) |
| `Mat_Petrino_Roca` | `#525649` | Roca sedimentaria de Raíz / Giza | — |
| `Mat_Petrino_Amatista` | `#7C3AED` | Cristales y vetas de corrupción | `#C084FC` (2.8) |
| `Mat_Arbol_Corteza` | `#452B1F` | Madera ancestral del Gran Árbol | — |
| `Mat_Musgo_Hojas` | `#365314` | Manto de musgo y copas de hojas | — |
| `Mat_Farol_Luz` | `#FDE047` | Farolillos de papel y madera de Cuna de Musgo | `#FEF08A` (4.0) |

---

## 2. Inventario de Modelos Generados

### Personajes (`modelos/personajes/`)
- **`maisha.glb` / `maisha.blend`**:
  - Proporción chibi estilizada (cabeza $\approx 45\%$ de altura total, cuerpo suave, ojos de obsidiana, rubor, brote con 2 hojas en la cabeza, corazón de Asili emitiendo luz cálida en el pecho y Cetro de Raíz empuñado en la mano derecha).
  - Altura: $\approx 1.45\text{ m}$.
- **`pino.glb` / `pino.blend`**:
  - Explorador con sombrero de seta roja y lunares crema, peto de trabajo verde y mochila de viaje de cuero con saco enrollado.
  - Altura: $\approx 1.30\text{ m}$.
- **`mzee_shamba.glb` / `mzee_shamba.blend`**:
  - Castor anciano agricultor con peto de faena, hocico con dientes, cola plana y bastón largo de madera.
  - Altura: $\approx 1.50\text{ m}$.
- **`corteza.glb` / `corteza.blend`**:
  - Herrero de complexión fuerte con delantal de cuero oscuro, gafas protectoras metálicas en la frente y martillo pesado de forja.
  - Altura: $\approx 1.55\text{ m}$.

### Criaturas y Corrupción (`modelos/enemigos/`)
- **`petrino_giza.glb` / `petrino_giza.blend`**:
  - Esfera facetada de roca sedimentaria con núcleo central de amatista pura y 3 fragmentos de piedra orbitando suspendidos.
  - Diámetro: $\approx 1.0\text{ m}$.
- **`mzizi_raiz.glb` / `mzizi_raiz.blend`**:
  - Minijefe / tocón colosal petrificado con cuatro raíces arqueadas ancladas al suelo y dos ojos violetas brillantes de Giza.
  - Dimensiones: $1.8\times 1.8\times 1.2\text{ m}$.
- **`babosa_oxido.glb` / `babosa_oxido.blend`**:
  - Enemigo errante de Raíz. Cuerpo blando, caparazón de hierro oxidado y dos antenas que emiten luz ámbar tenue.
- **`corazon_giza.glb` / `corazon_giza.blend`**:
  - Núcleo de combate de las zonas corruptas. Cinco espinas de piedra negra que envuelven un cristal octaédrico violeta pulsante.

### Arquitectura de Cuna de Musgo (`modelos/entorno/`)
- **`gran_arbol.glb` / `gran_arbol.blend`**:
  - Árbol colosal ancestral ($4.8\text{ m}$ de tronco, copas de musgo hasta $6.0\text{ m}$) con portal hueco tallado en la base que conduce al Claro de Calma.
- **`casa_pino.glb` / `casa_pino.blend`**:
  - Vivienda con paredes de tablones de madera, tejado de hongo carmesí y farolillo colgante en la entrada.
- **`forja_corteza.glb` / `forja_corteza.blend`**:
  - Taller abierto con horno de piedra volcánica, chimenea y yunque de hierro montado sobre tocón.
- **`molino_shamba.glb` / `molino_shamba.blend`**:
  - Cabaña de tablones con techo a dos aguas y gran rueda de molino de agua lateral.
- **`puente_madera.glb` / `puente_madera.blend`**:
  - Puente arqueado de 7 tablones de madera con 6 postes y pasamanos rústicos.
- **`farol_madera.glb` / `farol_madera.blend`**:
  - Poste alto con brazo voladizo y esfera de farol con luz cálida omnidireccional.

### Terreno Modular y Props (`modelos/entorno/` y `modelos/objetos/`)
- **`bloque_hierba.glb`**: Bloque cúbico de $1\times 1\times 0.5\text{ m}$ con cubierta de musgo.
- **`bloque_risco.glb`**: Bloque rocoso de desnivel de $1\times 1\times 1.0\text{ m}$.
- **`bloque_canal_agua.glb`**: Bloque de acequia con lámina de agua translúcida.
- **`bloque_camino.glb`**: Cuatro losas de piedra para plazas y senderos.
- **`semilla_explosiva.glb`**: Cápsula de vida con mecha incandescente.
- **`cetro_raiz.glb`**: Vara tallada con gema superior de luz.

---

## 3. Automatización y Regeneración

Todos los modelos se generan de forma determinista mediante el script Python:
```bash
/Applications/Blender.app/Contents/MacOS/Blender -b -P herramientas/blender/generador_3d_maisha.py
```
Cualquier ajuste de proporciones, colores o geometría se puede realizar directamente en el código o abriendo los archivos `.blend` individuales en la interfaz de Blender.
