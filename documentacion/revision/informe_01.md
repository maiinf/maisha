# Informe de Auditoría 01 · Maisha (Fase A)

Fecha: 16 de octubre de 2026  
Área revisada: **Sprites y arte del mundo** (`arte/`, `herramientas/`)

---

## Hallazgos de la auditoría

| # | Área | Qué he visto | Por qué importa | Propuesta | Esfuerzo (S/M/L) | Impacto (1-5) |
|---|---|---|---|---|---|---|
| 1 | Sprites / Aldeanos | En el fotograma 4 del gesto de Shamba, Bibi, Bata, Mbuzi y Msafiri, el bastón, cayado o pértiga tiene un hueco cortado de 2 píxeles antes del suelo, dejando la base flotando desconectada (`alza_derecha` en `dibujar_aldeanos.py`). | Es un fallo visible cada vez que Maisha se acerca a hablar o interactuar con los personajes centrales. Resta acabado visual. | Corregir `alza_derecha` en `herramientas/dibujar_aldeanos.py` para desplazar toda la columna del bastón sin truncar la base y regenerar los sprites. | S | 4 |
| 2 | Sprites / Enemigos | Píxeles huérfanos/flotantes en animaciones: `pembe.png` tiene restos de píxeles desconectados en el suelo en el fotograma 3; `konokono.png` tiene un píxel morado flotante bajo el caparazón en el fotograma 6. | Basura visual durante los combates que distrae y produce parpadeos extraños a resolución 640×360. | Limpiar los restos en los programas generadores y regenerar los fotogramas limpios. | S | 3 |
| 3 | Sprites / Enemigos | Los primeros enemigos (`jabali.png` y `petrino.png`) presentan sombreado plano en bloque y siluetas muy rígidas en comparación con enemigos modernos (`mamba`, `anguila`, `kuvu`, `guardian`). | Son el primer contacto del jugador con el combate en el Kitovu y Raíz; desentonan con la dirección artística actual. | Rediseñar el acabado de relieve rocoso en Petrino y las cerdas/placas de óxido en el Jabalí usando `pintor.py`. | M | 4 |
| 4 | Arte del mundo / Monumentos | El Gran Árbol hueco (`gran_arbol.png` en Cuna de Musgo) sigue generado con el código original (`dibujar_aldea.py`), con hojas de sellos circulares repetitivos y una muesca cuadrada cortada en la raíz derecha. | Es el edificio central y el alma de la aldea. Las casas de alrededor se rehicieron con gran detalle el 14-10, pero el Gran Árbol quedó con la calidad antigua. | Repintar el Gran Árbol con `pintor.py` (follaje orgánico, corteza con relieve y raíces integradas) y actualizar su mapa de normales (`_n.png`). | M | 5 |
| 5 | Arte del mundo / Vegetación | Los árboles básicos (`arbol_a.png` y `arbol_b.png` en `arte/mundos/raiz/objetos/`) tienen un tronco cilíndrico liso y recto sin vetas de madera ni raíces en el suelo. | Aparecen repetidos por todo Raíz. Su simplicidad choca con la vegetación detallada de los caminos (`arbol_cobre.png`, etc.). | Mejorar el tronco y la base en `pintar_prados.py` para añadir textura de corteza y garras de raíz que arraiguen en la hierba. | S | 3 |
| 6 | Sprites / Aldeanos | Pino (`pino_anim.png`), el niño-seta de Cuna de Musgo, tiene un aspecto muy liso y plástico, con brazos y piernas esquemáticos. | Habita la `casa_seta.png` (que tiene un detalle altísimo); al salir o interactuar, el contraste de calidad con su entorno es excesivo. | Añadir matices y textura de micelio, pliegues y sombreado suave en `dibujar_aldeanos.py`. | S | 3 |
