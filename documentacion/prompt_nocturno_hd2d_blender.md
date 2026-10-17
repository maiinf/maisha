# PROMPT MAESTRO NOCTURNO: ARQUITECTURA 3D SÓLIDA, AGUA LIMPIA Y EVOLUCIÓN HD-2D CONTINUA

Copia y pega el siguiente bloque completo en el chat para iniciar el trabajo autónomo nocturno:

```markdown
/goal Eres el Agente Principal de Calidad Visual y Arquitectura 3D de **Maisha**. Vas a trabajar de forma 100 % autónoma e ininterrumpida durante toda la noche en resolver los problemas visuales detectados, modelar la arquitectura sólida en Blender y llevar el juego a un nivel HD-2D cinematográfico sin detenerte hasta completar todas las fases.

---

### 1. CONTEXTO Y ENTORNO DE TRABAJO
- **Tu copia de trabajo**: `/Users/iinfafer/Proyectos/maisha-revision` (Godot 4.7, macOS x86_64, Blender 4.5 en `/Applications/Blender.app`).
- **Bóveda de Obsidian y repositorio principal**: `/Users/iinfafer/Proyectos/maisha` (donde trabaja Claude y donde se sincroniza Obsidian con `.obsidian/`).
- **Ramas activas**: Trabaja en `hd2d/calidad-blender` y sincroniza en `hd2d/blender-piloto`. Nunca hagas push a `main`.
- **Regla de oro de convivencia**: Nunca toques colisiones 2D, scripts de misiones ni diálogos de Sigilia o Raíz. El juego en 2D con la tecla H apagada debe seguir funcionando idéntico al 100%.

---

### 2. FASE 1: CASAS Y ESTRUCTURAS 3D SÓLIDAS DE VERDAD (360° SIN EFECTO PAPEL)
**Problema actual**: Al caminar detrás o por los lados de las casas (como la granja del Kitovu o las casas de la aldea), se percibe que son planos sin fondo ni pared trasera.
**Solución requerida**:
1. **Modelado 3D en Blender de todas las casas del juego** (`herramientas/blender/generador_3d_maisha.py`):
   - **El Kitovu (Tutorial)**: Modelar `casa_granja.glb` (casona de troncos completa en 360°, con porche frontal, buhardilla, tejado a dos aguas de madera, chimenea de piedra, paredes traseras y laterales cerradas, y rueda de molino de agua). Modelar también `pozo_antiguo.glb`, `espantapajaros.glb` y `carro_madera.glb`.
   - **Cuna de Musgo**: Modelar tanto la versión reconstruida como la versión en ruinas de cada casa (`casa_pino_ruina.glb`, `forja_ruina.glb`, `cocina_juncia.glb`, `puesto_tawi.glb`), de modo que incluso antes de reconstruirse tengan volumen tridimensional de escombros y mampostería real por los cuatro costados.
   - **Sigilia (Maandiko)**: Asegurar geometría sólida trasera y lateral para `gran_archivo.glb`, `taller_taa.glb`, `casa_escriba.glb` y la fuente central de la plaza (`fuente_plaza.glb`).
2. **Integración en el Espejo HD-2D (`scripts/mundo/hd2d/espejo_hd2d.gd`)**:
   - Mapear todas estas estructuras en `MODELOS_BLENDER`.
   - Garantizar que al caminar Maisha por detrás de cualquier casa, la cámara de perspectiva oculte o muestre a Maisha naturalmente tras el volumen real del tejado y la pared trasera sólida.
   - Configurar oclusión ambiental de contacto horneada en la base de cada casa para que asienten firmemente sobre el terreno.

---

### 3. FASE 2: ERRADICACIÓN DE BUGS VISUALES EN EL AGUA Y ARTEFACTOS NEGROS
**Problema actual**: En el mundo tutorial (El Kitovu) y zonas con agua aparecen parches negros, huecos y parpadeos en los bordes de acequias y estanques.
**Causa técnica**:
- El sombreador de suelo en `espejo_hd2d.gd` ejecuta `discard` simultáneo cuando `temblor` oscila con el tiempo, dejando al descubierto el vacío negro del fondo.
- Los bordes del mapa aplican un oscurecimiento agresivo `c *= mix(0.28, 1.0, f_borde)` que ensucia los canales de agua perimetrales.
- El lecho del río carece de fondo sólido bajo el agua hundida (`_plano_agua`).
**Solución requerida**:
1. **Lecho de fondo sólido (Fondo de río/estanque)**:
   - Crear una malla de lecho con arena, guijarros y lodo (`_plano_fondo_agua`) situada bajo el agua translúcida para que bajo ningún concepto se vea el vacío negro.
2. **Sombreador de agua cristalina y viva**:
   - Eliminar el `discard` dual inestable; el agua debe ser una superficie translúcida continua con profundidad real (`depth_fade`), espuma en contacto con las orillas (`franja_espuma`), reflejos suaves del entorno y refracción tenue.
   - Eliminar los tintes negros de los bordes sobre el agua.
3. **Validación en Kitovu y Ciénaga**:
   - Comprobar que la acequia de Mzee Shamba, el estanque de pesca y el lago reflejen la luz limpiamente de día, atardecer y noche.

---

### 4. FASE 3: CALIDAD DE ESTRUCTURAS, ILUMINACIÓN Y DETALLES HD-2D
1. **Texturas y acabados pixel art**:
   - Asignar a cada modelo 3D de Blender texturas de pixel art limpias generadas con la paleta oficial de Raíz y Sigilia (filtro `NEAREST` sin degradados borrosos), manteniendo coherencia estilística absoluta con los sprites.
2. **Iluminación física cálida**:
   - Cada farol de poste y linterna de pared debe tener su fuente de luz puntual suave (`OmniLight3D`) de tono ámbar acogedor.
   - Chimeneas y calderos con partículas sutiles de humo y brasas tridimensionales.
3. **Cercas, vallas y desniveles**:
   - Modelar `valla_madera.glb` y sustituir las vallas planas por estacas tridimensionales unidas por travesaños.

---

### 5. FASE 4: USO ACTIVO DE OBSIDIAN Y DOCUMENTACIÓN
1. **Bóveda oficial de Obsidian**:
   - Mantener las notas en `/Users/iinfafer/Proyectos/maisha/documentacion/` con formato Obsidian: enlaces bidireccionales `[[...]]`, etiquetas `#maisha #hd2d #blender`, tablas comparativas y diagramas Mermaid.
2. **Actualización continua de notas**:
   - `documentacion/modelos_3d.md`: Catálogo exhaustivo de cada modelo `.glb`, dimensiones, materiales y capturas.
   - `documentacion/decisiones.md`: Registro formal de cada decisión arquitectónica.
   - `documentacion/COORDINACION.md`: Tablón con avisos para Claude detallando qué zonas ya cuentan con 3D sólido.

---

### 6. FASE 5: VERIFICACIÓN, PRUEBAS Y COMMITS CONTINUOS
1. **Ejecución de pruebas automatizadas**:
   - Tras cada bloque de mejoras, ejecutar:
     ```bash
     /Applications/Godot.app/Contents/MacOS/Godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_hd2d
     ```
   - Garantizar 0 errores en `prueba_hd2d` y ampliar las aserciones para verificar la presencia de los nuevos modelos 3D y la ausencia de fallos en el agua.
2. **Generación de capturas de validación visual**:
   - Capturar el antes y después de El Kitovu (granja y agua) y Cuna de Musgo en `documentacion/hd2d/`.
3. **Commits y sincronización**:
   - Realizar commits pequeños, limpios y descriptivos en español.
   - Empujar (`git push`) a `origin/hd2d/blender-piloto` y `origin/hd2d/calidad-blender`.
   - Ejecutar `git fetch origin` en `/Users/iinfafer/Proyectos/maisha` para que Claude y Obsidian reciban las actualizaciones de inmediato.
   - No detenerse hasta haber completado todas las fases y dejar el HD-2D impecable.
```
