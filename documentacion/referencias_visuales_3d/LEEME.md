# 📐 CATÁLOGO DE REFERENCIAS VISUALES 3D PARA BLENDER

> **Destinatario**: Claude Code (Constructora y Modeladora 3D)  
> **Autor**: Gemini (Supervisora, Mapeado, Música y Concept Artist)  
> **Directriz de Iam**: Maisha evoluciona a un **juego 100% en 3D**. Gemini genera las imágenes conceptuales y especificaciones técnicas; Claude las modela en Blender (`.glb`).

---

## 🧭 CÓMO USAR ESTAS REFERENCIAS AL MODELAR EN BLENDER

1. **Consulta la imagen conceptual de la ficha**: Cada subcarpeta contiene imágenes `.png` con las vistas (frente, perfil, perspectiva) y la guía de colores oficial.
2. **Estilo visual (*Diorama / Cuento Cálido*)**:
   - Modelado estilizado *chibi* / diorama, con bordes redondeados y proporciones acogedoras.
   - Materiales Principled BSDF o sombreador toon con filtrado `NEAREST` en texturas si llevan detalles pintados, o colores base limpios según la paleta indicada.
   - **Cero huecos**: Las construcciones deben ser macizas y cerradas en 360° (con fachada delantera, trasera, laterales y tejados completos).
3. **Pivote y Escala**:
   - Origen/pivote siempre en la base ($z = 0$ o $y = 0$ en el suelo).
   - $1\text{ unidad de Blender} = 1\text{ metro en Godot} \approx 16\text{ píxeles del 2D original}$.
   - Altura estándar de Maisha $\approx 1.0\text{ - }1.1\text{ m}$. Altura de una casa estándar $\approx 2.5\text{ - }3.5\text{ m}$.
4. **Exportación**:
   - Exportar a `modelos/personajes/`, `modelos/entorno/`, `modelos/enemigos/` en formato `.glb`.

---

## 🗂️ ÍNDICE DE MODELOS PRIORITARIOS

| Categoría | Elemento | Estado de Referencia | Ficha Técnica |
| :--- | :--- | :--- | :--- |
| **Personaje** | **Maisha** (Protagonista) | 🟢 Disponible | [ref_maisha.md](personajes/ref_maisha.md) |
| **Personaje** | **Pino** (Explorador seta) | 🟢 Disponible | [ref_pino.md](personajes/ref_pino.md) |
| **Construcción** | **Casa Granja de Shamba** | 🟢 Disponible | [ref_casa_granja.md](construcciones/ref_casa_granja.md) |
| **Mapeado** | **Diorama El Kitovu** | 🟢 Disponible | [ref_mapa_kitovu.md](mapeado/ref_mapa_kitovu.md) |
