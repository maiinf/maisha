# PROMPT MAESTRO NOCTURNO: EVOLUCIÓN 3D / HD-2D, OBSIDIAN Y BLENDER (MODO AUTÓNOMO CONTINUO)

Copia y pega este bloque en el chat de la IA (recomendado ejecutar con el comando `/goal`):

```markdown
/goal Eres el agente principal de desarrollo de **Maisha** y vas a trabajar de forma 100 % autónoma durante toda la noche en la evolución tridimensional del juego. No te detengas hasta completar todas las fases descritas.

### 1. CONTEXTO CRÍTICO DEL PROYECTO
- **Repositorio**: `/Users/iinfafer/Proyectos/maisha` (Godot 4.7, macOS x86_64).
- **Estado de git**: Ya se completaron y subieron a GitHub (`origin`) la auditoría y las 10 ramas de revisión (`revision/sprites`, `revision/ilustraciones`, `revision/luz-2.5d`, `revision/musica`, `revision/sonidos`, `revision/interfaz`, `revision/codigo`, `revision/rendimiento`, `revision/textos`, `revision/estabilidad`).
- **Rama de trabajo**: Trabaja en `experimento/prototipo-visual` (o `experimento/modelado-3d`). NUNCA toques `main` directamente ni interfieras con el contenido de Sigilia (`scripts/mundo/sigilia/`, `arte/mundos/sigilia/`).
- **Prototipo actual**: En `escenas/experimento/prototipo_hd2d.tscn` ya existe un prototipo funcional en espacio 3D con Maisha, Pino (diálogo), Petrinos (combate con cetro y semillas), sombras direccionales dinámicas, desniveles de terreno y música ambiental.

---

### 2. FASE 1: CONEXIÓN CON OBSIDIAN Y DOCUMENTACIÓN DE DISEÑO
1. **Bóveda de Obsidian**: El repositorio local `/Users/iinfafer/Proyectos/maisha` ya contiene la configuración de Obsidian en `.obsidian/`.
2. **Lectura obligatoria del GDD**:
   - Lee el Game Design Document oficial en `/Users/iinfafer/Downloads/Maisha — Game Design Document.md`.
   - Lee `CLAUDE.md`, `LEEME.md`, `documentacion/decisiones.md` y `documentacion/plan_hd2d.md`.
3. **Sincronización**: Registra cada modelo, escala y decisión 3D en `documentacion/decisiones.md` y en una nota de Obsidian en `documentacion/modelos_3d.md`.

---

### 3. FASE 2: CONEXIÓN Y AUTOMATIZACIÓN DE BLENDER
1. **Instalación desatendida de Blender**:
   - Comprueba si existe `/Applications/Blender.app`.
   - Si no está instalado, descarga mediante terminal la versión oficial de Blender 4.x para macOS x86_64 (Intel), monta el `.dmg` y cópialo a `/Applications/Blender.app`:
     ```bash
     curl -L -o /tmp/blender.dmg https://download.blender.org/release/Blender4.2/blender-4.2.3-macos-x64.dmg
     hdiutil attach /tmp/blender.dmg
     cp -R /Volumes/Blender/Blender.app /Applications/
     hdiutil detach /Volumes/Blender
     rm -f /tmp/blender.dmg
     ```
2. **Conexión con Godot 4**:
   - Configura la ruta de Blender en `project.godot` para que Godot importe automáticamente archivos `.blend`:
     ```ini
     [filesystem]
     import/blender/blender_path="/Applications/Blender.app"
     ```
3. **Flujo de modelado procedural con Python (`bpy`)**:
   - Crea scripts en `herramientas/blender/` que utilicen `/Applications/Blender.app/Contents/MacOS/Blender -b -P script.py` para generar modelos `.blend` y exportar escenas `.gltf` de forma automatizada y reproducible.

---

### 4. FASE 3: MODELADO 3D COMPLETO (PERSONAJES, CRIATURAS Y BIOMAS)
Modela los elementos fundamentales de Maisha con estilo estilizado (borde suave, texturas limpias, paleta cálida de Raíz y Giza):

1. **Personajes principales y aldeanos** (en `modelos/personajes/`):
   - **Maisha**: Modelo 3D estilizado (cuerpo suave de brote, cabeza redondeada, ojos expresivos, cetro de madera con gemas y capas de ropa intercambiables).
   - **Mzee Shamba**: Castor anciano con bastón largo, peto de trabajo y gafas.
   - **Pino**: Explorador con sombrero de seta, mochila y correa.
   - **Corteza**: Herrero con delantal de cuero, gafas protectoras y martillo.
   - **Bibi**, **Juncia**, **Tawi**.
2. **Enemigos y criaturas** (en `modelos/enemigos/`):
   - **Petrino de Giza**: Criatura esférica de roca sedimentaria con vetas amatistas y núcleo pulsante.
   - **Mzizi**: Raíz colosal de piedra con ojos violetas y corteza agrietada.
   - **Pembe**: Ciervo de hierro y raíces con cornamenta de ramas metálicas.
   - **Konokono**: Caracola de óxido con caparazón de piedra espiral.
3. **Escenarios y arquitectura modular** (en `modelos/entorno/`):
   - **Cuna de Musgo**: Gran Árbol central, Casa Seta de Pino, Taller de forja de Corteza, Puesto de Tawi, Cocina de Juncia y farolillos de madera.
   - **El Kitovu**: Cabaña de madera de Mzee Shamba, rueda de molino de agua, pozo antiguo, puente de madera y cerca de estacas.
   - **Kits modulares de terreno**: Losas de camino, bloques de riscos, desniveles de hierba, escaleras talladas y canal de agua.

---

### 5. FASE 4: INTEGRACIÓN EN GODOT 4 Y ESCENAS 3D JUGABLES
1. **Adaptador de regiones (`scripts/mundo/region_3d.gd`)**:
   - Construye el sistema que traduce los mapas `.json` de Raíz en terrenos 3D utilizando los modelos importados de Blender.
2. **Escena completa de Cuna de Musgo 3D**:
   - En `escenas/mundo/3d/cuna_de_musgo_3d.tscn`, monta la aldea completa con iluminación por sol direccional, sombras suaves, faroles con luz cálida física, agua viva en la acequia y navegación 3D.
3. **Verificación y commits**:
   - Ejecuta `/Applications/Godot.app/Contents/MacOS/Godot --headless --path . res://escenas/mundo/3d/cuna_de_musgo_3d.tscn` para garantizar 0 errores.
   - Realiza commits pequeños y descriptivos en la rama con autoría clara.
   - Deja un informe final detallado en `documentacion/informe_noche_3d.md`.
```
