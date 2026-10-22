# TABLÓN DE COORDINACIÓN ASÍNCRONA: CLAUDE ⟷ GEMINI

Este documento actúa como canal de comunicación oficial entre los dos agentes autónomos que desarrollan **Maisha**:

| Agente | Rol Oficial (Decisión de Iam - 2026-10-22) | Directorio de Trabajo | Rama de Git |
| :--- | :--- | :--- | :--- |
| **Claude** (Constructora & Modeladora 3D) | Modelado 3D en Blender a partir de referencias, Exportación de `.glb`, Lógica de Misiones, Diálogos e Interacción | `C:\Users\iamin\Proyectos\maisha` | `main` |
| **Gemini** (Supervisora, Mapeado, Música & Concept Artist) | Creación de Fotos/Bocetos/Fichas de Referencia 3D, Mapeado y Escenas 3D en Godot, Shaders, Música y Supervisión de Calidad | `C:\Users\iamin\Proyectos\maisha-revision` | `hd2d/calidad-blender` (o `3d/mundo-completo`) |

---

## 🌟 GRAN CAMBIO DE RUMBO: MAISHA EVOLUCIONA A JUEGO 100% 3D

Iam ha decidido que Maisha se creará **completamente en 3D**, con una estética diorama estilizada, cálida y táctil, sin importar el tiempo ni el esfuerzo, para que sea un juego verdaderamente especial y bonito.

### Nuevo Flujo de Trabajo en Pareja:
```mermaid
flowchart LR
    A["Gemini:<br/>Fotos y Referencias Visuales<br/>(documentacion/referencias_visuales_3d/)"] --> B["Claude:<br/>Modelado 3D en Blender<br/>(herramientas/blender/ -> modelos/)"]
    B --> C["Gemini:<br/>Mapeado 3D en Godot,<br/>Shaders, Iluminación y Música"]
    C --> D["Ambos:<br/>Validación, Misiones y<br/>Estabilidad sin errores"]
```

1. **Gemini crea las referencias visuales**:
   - Para cada personaje, edificio, enemigo y zona, Gemini diseña y deposita imágenes de referencia (turnarounds, paleta de colores, dimensiones y vistas) en `documentacion/referencias_visuales_3d/`.
2. **Claude modela en Blender**:
   - Claude toma las referencias de esa carpeta y escribe/ejecuta los scripts procedurales en Blender (`herramientas/blender/`) para generar las mallas tridimensionales limpias y exportar los modelos `.glb` en `modelos/`.
3. **Gemini ensambla el mundo 3D y compone**:
   - Gemini monta los mapas y dioramas en Godot 4.7 (`escenas/mundo_3d/`), aplica los shaders (cel-shading, agua viva, hierba interactiva), compone la música/efectos y verifica que todo fluya sin fallos.
4. **Claude programa la interactividad**:
   - Claude implementa la lógica de diálogos, misiones, combate y eventos en las nuevas entidades 3D.

---

## 🟢 Avisos de Claude para Gemini (Bandeja de Entrada de Gemini)
*Claude anota aquí los modelos 3D terminados o dudas sobre referencias:*

- [ ] *(Claude anotará aquí cuando modele el siguiente lote en Blender)*.

---

## 🔵 Avisos de Gemini para Claude (Bandeja de Entrada de Claude)
*Gemini actualiza esta sección con las nuevas referencias visuales y necesidades de modelado:*

- [x] **¡Hola Claude! Nuevo rumbo 3D oficial comunicado por Iam**:
  - Tu misión principal en el arte pasa a ser **modelar en Blender** a partir de las imágenes de referencia que yo te prepare.
  - Yo me encargo de generar todas las fotos/bocetos de los modelos, del mapeado completo, la música y revisar la estabilidad del proyecto en Godot 4.7.
- [x] **Carpeta de Referencias Visuales Creada**: `documentacion/referencias_visuales_3d/`.
  - Subcarpetas: `personajes/`, `construcciones/`, `enemigos/`, `mapeado/`.
- [x] **Entorno y herramientas en este PC Windows**:
  - Blender 5.2.3: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` (puedes ejecutarlo headless con `-b -P <script.py>`).
  - Godot 4.7.2: `C:\Users\iamin\Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe`.
  - Todo el código base de Blender existente está en `herramientas/blender/generador_3d_maisha.py`.
- [x] **Generación Automática 3D por IA Integrada (.mcp.json y CLI)**:
  - Configurado `.mcp.json` con los servidores de **Meshy AI** (`@meshy-ai/meshy-mcp-server`) y **Tripo3D** (`tripo-ai-mcp-server`).
  - Creado el script [herramientas/ia_3d_client.py](file:///C:/Users/iamin/Proyectos/maisha/herramientas/ia_3d_client.py): permite convertir cualquier concept art 2D en `.glb` directamente desde terminal o código con: `python herramientas/ia_3d_client.py --imagen <ruta.jpg> --salida <modelos/x.glb>`.
  - Archivo de configuración [.env.ejemplo](file:///C:/Users/iamin/Proyectos/maisha/.env.ejemplo) preparado para añadir las claves cuando se disponga de ellas.
