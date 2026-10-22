# 📜 CONTRATO OFICIAL DE PRODUCCIÓN 3D: EL KITOVU (Para Claude)

**Directiva de Iam (2026-10-23):**
> "Termina lo que ya has empezado YA, con eso podré pedir a mi otro agente que empiece a modelar, y por favor que las imágenes y diseños cumplan mis requisitos acuérdate."

Este documento es el **contrato visual definitivo**. Claude debe seguir las imágenes de referencia y las directivas de Iam punto por punto para cada activo de El Kitovu.

---

## 1. Estándar Visual y Tono del Juego (God of War / Zelda TotK / Elden Ring)
- **Imagen de Tono y Calidad Maestra**: [`documentacion/referencias_visuales_3d/interfaz/ui_gameplay_aaa_concept_art.jpg`](file:///C:/Users/iamin/Proyectos/maisha-revision/documentacion/referencias_visuales_3d/interfaz/ui_gameplay_aaa_concept_art.jpg).
- **Estilo**: Fantasía oscura/mítica seria, sobria y prestigiosa. Iluminación atmosférica lateral, niebla volumétrica baja, texturas táctiles ricas (madera vieja, pizarra húmeda, cuero curtido, bronce envejecido, resplandores ámbar y violeta).
- **PROHIBIDO**: Estilo infantil, colores chillones, personajes chibi o dibujos animados.
- **PROHIBIDO PARA HUMANOS/ORGÁNICOS**: Modelar figuras mediante cilindros matemáticos procedimentales en bucle (`math.sin`). Toda figura humana u orgánica debe esculpirse o construirse sobre mallas base profesionales.

---

## 2. Hoja de Ruta de Modelado de El Kitovu (100% Desbloqueado)

| Activo | Archivo .glb | Referencia Visual Canónica | Requisitos Estrictos de Iam (Prioridad Absoluta) | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **Mzee Shamba** | `modelos/personajes/mzee_shamba.glb` | [`personajes/mzee_shamba_castor_mitico_concept_art.jpg`](file:///C:/Users/iamin/Proyectos/maisha-revision/documentacion/referencias_visuales_3d/personajes/mzee_shamba_castor_mitico_concept_art.jpg) | 1. **100% Bípedo y 1.45 m de altura** (no cuadrúpedo ni monstruo).<br/>2. **Muy sabio, culto y con gafas redondas de latón** apoyadas en el hocico.<br/>3. Rostro noble canoso de castor, incisivos de ámbar fósil pulido, barba con espigas.<br/>4. Chaleco rústico de pana ocre, camisa crema de algodón arremangada.<br/>5. Gran cola plana de pizarra que arrastra y usa como tercer punto de apoyo.<br/>6. Bastón botánico de roble con azadilla en la base.<br/>*(Nota: En la imagen de referencia tiene hombreras de musgo verde brillante; Iam prefiere chaleco rústico y sombrero de paja campesino)*. | 🟢 **LISTO** (Prioridad 1) |
| **Maisha** | `modelos/personajes/maisha.glb` | Ropa/Atuendo: [`personajes/maisha_ser_mistico_concept_art.jpg`](file:///C:/Users/iamin/Proyectos/maisha-revision/documentacion/referencias_visuales_3d/personajes/maisha_ser_mistico_concept_art.jpg)<br/>Rostro/Atmósfera: [`interfaz/ui_gameplay_aaa_concept_art.jpg`](file:///C:/Users/iamin/Proyectos/maisha-revision/documentacion/referencias_visuales_3d/interfaz/ui_gameplay_aaa_concept_art.jpg) | 1. **Ser místico andrógino/humanoide maduro** (1.70 m, esbelto y ágil).<br/>2. **SIN CUERNOS NI ASTAS** (cabello orgánico suave oscuro).<br/>3. **Tatuajes Mnemotécnicos en brazos y pecho**: oscuros al inicio, se iluminan en oro Asili conforme recupera la memoria.<br/>4. Túnica de lino arena (#eae3d2), capa asimétrica de viaje color musgo, cinturón con bolsas de semillas.<br/>5. Corazón de Asili incrustado en el esternón con resplandor cálido.<br/>6. Cetro de Raíz de madera retorcida con semilla de esmeralda.<br/>7. **Malla Base Oficial**: Usar `GEO-body_male_stylized` de `human_base_meshes_bundle.blend` (ver [`reconstruir_maisha_base.py`](file:///C:/Users/iamin/Proyectos/maisha-revision/herramientas/blender/reconstruir_maisha_base.py)). | 🟢 **LISTO** (Prioridad 1) |
| **Petrino de Giza** | `modelos/enemigos/petrino_giza.glb` | Placas de piedra: [`personajes/bata_castor_mitico_concept_art.jpg`](file:///C:/Users/iamin/Proyectos/maisha-revision/documentacion/referencias_visuales_3d/personajes/bata_castor_mitico_concept_art.jpg)<br/>Ficha: [`enemigos/ref_petrino_giza.md`](file:///C:/Users/iamin/Proyectos/maisha-revision/documentacion/referencias_visuales_3d/enemigos/ref_petrino_giza.md) | 1. Bestia cuadrúpeda pesada ($1.85\text{ m}$ largo, $1.15\text{ m}$ a la cruz).<br/>2. Cuerpo de basalto volcánico oscuro con textura porosa.<br/>3. **Coraza dorsal de 5 lajas superpuestas de pizarra cortante** (inspiradas en el blindaje pétreo de Bata).<br/>4. Colmillos toscos de pedernal/sílex afilados.<br/>5. Cuencas de ojos hendidas con **resplandor violeta frío de corrupción de Giza**. | 🟢 **LISTO** |
| **Casa Granja de Shamba** | `modelos/entorno/casa_granja.glb` | [`construcciones/casa_granja_concept_art.jpg`](file:///C:/Users/iamin/Proyectos/maisha-revision/documentacion/referencias_visuales_3d/construcciones/casa_granja_concept_art.jpg)<br/>Ruina: [`construcciones/ref_casa_granja_ruina.md`](file:///C:/Users/iamin/Proyectos/maisha-revision/documentacion/referencias_visuales_3d/construcciones/ref_casa_granja_ruina.md) | 1. Casona de troncos de cedro sobre zócalo de piedras de río.<br/>2. Rueda hidráulica de molino de madera girando sobre canaleta con agua.<br/>3. Chimenea de piedra caliza con chimenea y marcador de humo.<br/>4. Porche de madera con farol encendido.<br/>5. Versión inicial dañada por la ceniza de Giza antes de la purificación. | 🟢 **LISTO** |
| **Props del Huerto Asfixiado** | `modelos/entorno/carro_madera.glb`<br/>`pala_oxidada.glb`<br/>`espantapajaros.glb`<br/>`pozo_antiguo.glb` | [`construcciones/casa_granja_concept_art.jpg`](file:///C:/Users/iamin/Proyectos/maisha-revision/documentacion/referencias_visuales_3d/construcciones/casa_granja_concept_art.jpg)<br/>Ficha: [`construcciones/ref_props_huerto_kitovu.md`](file:///C:/Users/iamin/Proyectos/maisha-revision/documentacion/referencias_visuales_3d/construcciones/ref_props_huerto_kitovu.md) | **Narrativa ambiental de huerto abandonado por la Purga de Giza (Requisitos clave de Iam):**<br/>1. **Carretilla volcada**: Inclinada 28° contra el suelo con rueda de hierro forjado rota y abono reseco.<br/>2. **Pala oxidada**: Clavada en ángulo en un surco seco, abandonada apresuradamente.<br/>3. **Espantapájaros de sombras**: Maniquí de entrenamiento de $2.10\text{ m}$ con cabeza de arpillera y sombrero de paja.<br/>4. **Pozo antiguo**: Brocal circular de caliza con líquenes, tejadillo de cedro y cubo.<br/>5. **Valla, farol y bancales**: Vallas de madera desgastada y brotes marchitos. | 🟢 **LISTO** |
| **Cráter del Despertar & Árbol Seco** | `modelos/entorno/crater_kitovu.glb`<br/>`arbol_seco.glb` | Ficha: [`construcciones/ref_crater_despertar.md`](file:///C:/Users/iamin/Proyectos/maisha-revision/documentacion/referencias_visuales_3d/construcciones/ref_crater_despertar.md) | 1. Cráter elíptico de $3.4\text{ m} \times 3.0\text{ m}$ con lajas de pizarra levantadas por el impacto.<br/>2. **Glifos rúnicos en espiral grabados en el lecho**: idénticos a los tatuajes de Maisha, brillan con pulso ámbar al despertar.<br/>3. **Árbol seco**: Roble milenario petrificado de $4.6\text{ m}$ con ramas desnudas como garras hacia el cielo. | 🟢 **LISTO** |
| **Portal de Raíz & Nudo de Giza** | `modelos/entorno/portal_raiz.glb`<br/>`nudo_corrupcion.glb` | Ficha: [`construcciones/ref_portal_raiz.md`](file:///C:/Users/iamin/Proyectos/maisha-revision/documentacion/referencias_visuales_3d/construcciones/ref_portal_raiz.md) | 1. **Portal**: Arco colosal de $4.80\text{ m}$ de altura formado por dos raíces vivas entrelazadas en ojiva.<br/>2. **Nudo**: Bulbo central de $1.60\text{ m}$ con barrera de zarcillos negros espinosos y **agujas de cuarzo violeta de Giza**. | 🟢 **LISTO** |

---

## 3. Guía de Ejecución Rápida para Claude
1. **Modelar en Blender**: Escribir o ejecutar los scripts en `herramientas/blender/` (o modelar directamente en Blender 5.2.3).
2. **Exportar a `.glb`**: Ubicarlos en `modelos/personajes/`, `modelos/enemigos/` o `modelos/entorno/` manteniendo los nombres exactos de archivo.
3. **Generar las 4 Vistas Turnaround**:
   ```bash
   blender -b --factory-startup -P herramientas/blender/render_turnaround.py -- --modelo modelos/<ruta>.glb --salida <carpeta_vistas>
   ```
4. **Validación en Godot**: Pasar `prueba_kitovu_3d.gd`:
   ```bash
   Godot_v4.7.2-stable_win64_console.exe --headless -s pruebas/prueba_kitovu_3d.gd
   ```
