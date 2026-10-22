# CONTRATO DE REFERENCIAS · EL KITOVU (para Claude)

**Regla única:** no se modela nada sin su imagen canónica al lado. Si un recurso pone ⏳, la imagen todavía no existe: **no lo modeles de memoria, espera.**
Cuando la imagen y la ficha `.md` choquen, manda lo que diga la columna «Manda».

## 1. Estilo global (para todo)
- Calidad y tono: `interfaz/ui_gameplay_aaa_concept_art.jpg` (God of War / Elden Ring: sobrio, realista estilizado, niebla, luz dorada lateral).
- Prohibido: primitivas sueltas (conos, cubos, esferas) como forma final, cilindros con `math.sin`, look de juguete o móvil.

## 2. Tabla de recursos

| Recurso | .glb | Imagen canónica | Manda | Estado |
| :--- | :--- | :--- | :--- | :--- |
| Mzee Shamba | `personajes/mzee_shamba.glb` | `personajes/mzee_shamba_castor_mitico_concept_art.jpg` | **Imagen**: cara, pelaje gris plateado, proporciones, cola de pizarra, sombrero de paja. **Ficha**: gafas redondas de latón + chaleco de pana encima (la imagen no las tiene; Iam las pidió). Quitar las placas de musgo verde brillante de los hombros. | 🟡 usable ya · turnaround ⏳ |
| Maisha | `personajes/maisha.glb` | ⏳ `personajes/maisha_turnaround_sheet.jpg` | Ficha `ref_maisha_mistico.md` | ⏳ |
| Petrino de Giza | `enemigos/petrino_giza.glb` | ⏳ `enemigos/petrino_giza_concept_art.jpg` | Ficha `ref_petrino_giza.md` | ⏳ |
| Casa Granja (ruina) | `entorno/casa_granja.glb` | `construcciones/casa_granja_concept_art.jpg` solo para **forma** | Ficha `ref_casa_granja_ruina.md` para el estado | 🟡 forma sí · estado ⏳ |
| Props huerto (carretilla, pala, espantapájaros, pozo, valla, farol, bancal) | `entorno/*.glb` | ⏳ `construcciones/props_huerto_kitovu_sheet.jpg` | Ficha `ref_props_huerto_kitovu.md` | ⏳ |
| Cráter + Árbol seco | `entorno/crater_kitovu.glb`, `arbol_seco.glb` | ⏳ `construcciones/crater_despertar_concept_art.jpg` | Ficha `ref_crater_despertar.md` | ⏳ |
| Portal de Raíz + Nudo | `entorno/portal_raiz.glb`, `nudo_corrupcion.glb` | ⏳ `construcciones/portal_raiz_concept_art.jpg` | Ficha `ref_portal_raiz.md` | ⏳ |

## 3. Imágenes que NO son referencia (obsoletas)
- `personajes/maisha_concept_art.jpg` (chibi), `maisha_adulto_concept_art.jpg` (mujer), `maisha_ser_mistico_concept_art.jpg` y `maisha_evolucion_upgrades.jpg` (tienen astas; Iam las quitó).
- `personajes/mzee_shamba_concept_art.jpg` (anciano humano).
- `mapeado/kitovu_diorama_concept_art.jpg` y `interfaz/ui_gameplay_concept_art.jpg` (estilo infantil antiguo).

## 4. Los .glb actuales de El Kitovu son BLOCKOUTS
Los `.glb` de Shamba, Petrino y los props que subió Gemini el 2026-10-23 están hechos con primitivas. **Valen solo como medida y posición** (altura, huella en el suelo, dónde va cada cosa en `kitovu_3d.tscn`). No son el aspecto final: sustitúyelos sin miedo manteniendo nombre de archivo, escala y pivote en el suelo.

## 5. Cómo comprobar que tu modelo se parece (obligatorio antes de subir)
1. Pon la imagen canónica como *Image Empty* `REF_` detrás del modelo, en la vista frontal ortográfica (skill `reference-to-3d`, paso 3).
2. Renderiza tus 4 vistas con:
   `blender -b --factory-startup -P herramientas/blender/render_turnaround.py -- --modelo modelos/<ruta>.glb --salida <carpeta>`
   (arreglado el 2026-10-23: la vista 3/4 ya no corta el modelo).
3. Pon tu render y la imagen canónica lado a lado en tu aviso del Diario. Si a simple vista no es el mismo personaje, no se sube.
4. Cuerpos humanos u orgánicos bípedos: parte de la malla base CC0 de `herramientas/blender/recursos/human_base_meshes/` (ver `reconstruir_maisha_base.py`), no de primitivas. La carpeta está en `.gitignore`: si no la tienes en `main`, cópiala de `maisha-revision`.
