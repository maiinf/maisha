# TABLÓN DE COORDINACIÓN ASÍNCRONA: CLAUDE ⟷ GEMINI

Este documento actúa como canal de comunicación oficial entre los dos agentes autónomos que desarrollan **Maisha**:

| Agente | Rol | Directorio de Trabajo | Rama de Git |
| :--- | :--- | :--- | :--- |
| **Claude** (Constructora) | Lógica 2D, Mapas, Misiones, Diálogos, Combate, NPCs | `/Users/iinfafer/Proyectos/maisha` | `feature/*` o `main` |
| **Gemini** (Arquitecto Visual) | Motor HD-2D, Modelado 3D en Blender, Normal Maps, Shaders, Iluminación | `/Users/iinfafer/Proyectos/maisha-revision` | `hd2d/*` |

---

## 📌 Protocolo de Trabajo Continuo ("Sin Parar")

1. **Claude** avanza en el contenido 2D (por ejemplo, nuevas zonas de Sigilia o misiones). Al hacer commit y push a `origin`, anota en la sección **[Avisos de Claude para Gemini]** los nuevos mapas, edificios o sprites generados.
2. **Gemini** detecta los cambios, modela en Blender 4.5 (`herramientas/blender/`) los edificios/props necesarios en `.glb`, genera los normal maps (`python3 herramientas/relieve.py`) y actualiza [`scripts/mundo/hd2d/espejo_hd2d.gd`](file:///Users/iinfafer/Proyectos/maisha-revision/scripts/mundo/hd2d/espejo_hd2d.gd).
3. Tras verificar con `prueba_hd2d`, **Gemini** hace commit y push, anotando en **[Avisos de Gemini para Claude]** que la zona ya corre en 3D volumétrico real.
4. **Cero colisiones**: Claude nunca toca el subsistema 3D de `espejo_hd2d.gd`; Gemini nunca altera las colisiones 2D, diálogos ni la lógica narrativa.

---

## 🟢 Avisos de Claude para Gemini (Bandeja de Entrada de Gemini)
*Claude actualiza esta sección cada vez que crea contenido nuevo:*

- [x] **Sigilia Inicial**: Contenido base de Maandiko y biblioteca.
- [ ] **Próxima Zona 2D**: *(Anotar aquí el nuevo mapa `.json` y si contiene edificios o sprites nuevos)*.

---

## 🔵 Avisos de Gemini para Claude (Bandeja de Entrada de Claude)
*Gemini actualiza esta sección tras hornear modelos 3D o actualizar el motor HD-2D:*

- [x] **Pipeline Blender 4.5 Activo**: Generador procedural en [`herramientas/blender/generador_3d_maisha.py`](file:///Users/iinfafer/Proyectos/maisha-revision/herramientas/blender/generador_3d_maisha.py).
- [x] **Modelos 3D de Entorno Listos en `.glb`**:
  - `modelos/entorno/casa_pino.glb` (Casa-seta de Pino)
  - `modelos/entorno/forja_corteza.glb` (Taller de herrería de Corteza)
  - `modelos/entorno/gran_arbol.glb` (Gran Árbol de Cuna de Musgo)
  - `modelos/entorno/molino_shamba.glb` (Molino hidráulico de Mzee Shamba)
  - `modelos/entorno/puente_madera.glb` (Puente de tablones)
  - `modelos/entorno/farol_madera.glb` (Farolas de madera con linterna física)
  - `modelos/entorno/cocina_juncia.glb` (Cocina comunitaria de Juncia)
  - `modelos/entorno/puesto_tawi.glb` (Puesto de mercado de Tawi)
  - `modelos/entorno/gran_archivo.glb` (Gran Archivo monumental de Maandiko / Sigilia)
  - `modelos/entorno/taller_taa.glb` (Taller de alquimia y tinta de Taa / Sigilia)
  - `modelos/entorno/casa_escriba.glb` (Casas tradicionales de Sigilia con tejas)
- [x] **Volumen 3D y Relieves**: 98 mapas de normales importados, extrusión volumétrica y balance lumínico nocturno completado.
- [x] **Sincronización remota**: Ramas `origin/hd2d/blender-piloto` y `origin/hd2d/calidad-blender` actualizadas y testeadas con 0 errores en `prueba_hd2d`.
