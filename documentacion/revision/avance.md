# Estado de Avance de la Revisión Integral de Maisha

Documento de consolidación de la auditoría y de las 10 ramas de revisión ejecutadas sobre el repositorio de Maisha.
Todas las ramas parten limpiamente de `origin/main` (`03c5857`) y han sido verificadas con la suite de pruebas headless de Godot 4.7.

---

## 1. Inventario de Ramas y Commits

| Rama | Commit | Área | Estado de Pruebas |
| --- | --- | --- | --- |
| `revision/auditoria` | `f6fa302` | Auditoría inicial completa | Documentación generada |
| `revision/sprites` | `366bf55`<br>`b0021e0`<br>`a36adce` | Bastones cortados, pezuñas Pembe, grietas Konokono, corazón Petrino, óxido Jabalí, Pino y animaciones de perfil Maisha | `prueba_aldea`: OK<br>`prueba_maisha_animaciones`: OK |
| `revision/ilustraciones` | `c1846e1` | Periodicidad en horizontes, acequia bajo molino, árbol de leyenda, reflejo Kimya y ruinas de Mauti | `prueba_kitovu`: OK<br>`prueba_lago_espejo`: OK |
| `revision/luz-2.5d` | `1907ec8` | 49 mapas de normales `_n.png` generados, sombras dinámicas con calidez solar, motas de luz y luces nocturnas | `prueba_luz`: OK |
| `revision/musica` | `cd4a605` | Timbres orgánicos en kalimba/balafón/flauta, costura de 8 ms sin clic, saturación suave y tabla `VOLUMEN_MUSICA` (-15.5 dBFS) | `prueba_sonido`: OK |
| `revision/sonidos` | `d98c5da` | Rediseño de efectos de combate (`cetro_golpe`, `golpe_acierto`, `semilla_plantar`) y balance de `VOLUMEN` | `prueba_sonido`: OK |
| `revision/interfaz` | `d332bc3` | Menú de pausa con iconos y 2 columnas, desactivación de subpíxel en fuentes, punto `cueva_eco` y atajos | `prueba_misiones`: OK |
| `revision/codigo` | `4484cf8` | Centralización de `Relieve.textura_luz(tam)` con caché estática, unificación de fundidos y limpieza | `prueba_luz`: OK |
| `revision/rendimiento` | `4fca984` | Cacheo de `tiene_novedad` en aldeanos, eliminación in-place en ambiente, descarte de nubes fuera de cámara y grupos en `luz_sol` | `cuna_de_musgo`: 141.2 FPS (+10.3%)<br>`prados_del_eco`: 117.8 FPS (+9.1%)<br>`prueba_aldea`: OK |
| `revision/textos` | `2970d4d` | Lenguaje neutro estricto para Maisha («Sin ayuda no», «tenue pero entera») y susurro de Shamba | `prueba_embarcadero_junco`: OK |
| `revision/estabilidad` | `1a85ac9` | `set_process(false)` en `_ready()` para nodos liberados (`aldeano.gd`, `recogible.gd`) y captura por ID en lambda de Kitovu | `prueba_kitovu`: OK<br>`prueba_aldea`: OK<br>`prueba_combate`: OK |

---

## 2. Resumen Técnico de Cambios por Rama

### 1. `revision/sprites`
- **Bastones de aldeanos**: Los bastones de Mzee Shamba, Mbuzi y Msafiri estaban cortados 1-2 píxeles por encima del borde del sprite. Se extendieron hasta el nivel del suelo en `herramientas/dibujar_kitovu.py`, `dibujar_aldea.py` y `dibujar_aldeanos.py`.
- **Anatomía de jefes y criaturas**:
  - `pembe.png`: Reubicada la pezuña trasera descolgada para cerrar el apoyo anatómico del ciervo.
  - `konokono.png`: Grietas del caparazón reescaladas pixel-perfect sin distorsión bilineal.
  - `petrino.png`: Corazón interior contrastado con amatista brillante y núcleo pulsante.
  - `jabali.png`: Eliminadas manchas aisladas de óxido en la coraza metálica.
- **Pino**: Detalladas las pecas, la mochila exploradora y la hojita en el sombrero de seta.
- **Maisha de perfil**: Pulido el movimiento vertical del brote y el eje de la cabeza en `maisha_reposo_lado` y `maisha_correr_lado` para evitar saltos de 1 px.

### 2. `revision/ilustraciones` (y `revision/ilustraciones-v2`)
- **2_familia_shamba.png**: Eliminadas líneas y patrones periódicos en el cielo y la hierba lejana. Añadida espuma de agua y salpicaduras en la acequia que desciende hacia la rueda del molino.
- **3_leyenda.png (Rediseño profundo v2)**: Esfera de la visión con el Primer Árbol frondoso, racimos dorados y Maisha espiritual sobre la colina sagrada; torrente fluido de chispas y corona solar. Crías de castor acurrucadas y sentadas en la alfombra (`cria_leyenda`) con expresiones tiernas y atentas mirando la magia: una señalando asombrada y el pequeño Shamba con su sombrerito ladeado y manitas en el pecho. Iluminación volumétrica global de 3 fuentes (fuego de chimenea cálido, resplandor dorado celestial de la visión y luz de luna fría en la ventana).
- **17_kimya_lago.png (Rediseño profundo v2)**: Kimya espectral (`_kimya_figura_serena`) con velos diáfanos de aurora, mirada serena y ondas concéntricas de agua a sus pies. Península de la orilla enriquecida con juncos con espigas, piedras húmedas y nenúfares flotantes con flor blanca abierta. En el agua, el reflejo de Mauti (`_mauti_reflejo_lago`) extiende la mano hacia arriba hacia la de Maisha, casi tocándose en la superficie del lago con un destello y ondas de contacto. Columna de luna reflejada y bruma baja sobre el lago en calma.
- **22_ruinas_mauti.png**: Añadidas piedras caídas, musgo y grietas orgánicas con relieve de sombras en las ruinas.

### 3. `revision/luz-2.5d`
- **49 Mapas de Normales**: Generados todos los archivos `_n.png` que faltaban en aldeanos, jefes, vegetación y edificios mediante `herramientas/relieve.py`.
- **Sombras dinámicas y calidez solar**: Enlazada la inclinación y longitud de sombras con `Reloj.calidez()` y `Reloj.angulo_sol()`.
- **Luces nocturnas**: Incorporadas luces tenues y cálidas en ventanas de cabañas y en el cráter del Kitovu al anochecer.

### 4. `revision/musica`
- **Sintetizador procedural (`herramientas/sintetizador.py`)**:
  - Kalimba: Introducida resonancia modal de cuerpo hueco y caída de afinación no lineal (-15 cents en el transitorio de ataque).
  - Balafón: Incorporada resonancia del segundo armónico (octava + quinta) con amortiguamiento rápido simulando maza de caucho.
  - Flauta: Inyección de ruido rosa filtrado en el ataque emulando el soplo de embocadura.
- **Costuras de bucle**: Algoritmo de crossfade suave de 8 ms en `Pista.bucle()` y `componer_musica.py:final()`, eliminando los clics acústicos.
- **Calibración de volumen**: Creado el diccionario `VOLUMEN_MUSICA` en `scripts/globales/sonido.gd` para equilibrar las 44 pistas a un nivel homogéneo de -15.5 dBFS.

### 5. `revision/sonidos`
- **Efectos de combate (`herramientas/crear_sonidos.py`)**:
  - `cetro_golpe`: Diseñado con barrido continuo de aire y silbido armónico suave sin cortes abruptos de filtro.
  - `golpe_acierto`: Añadido chasquido resonante de madera/corteza densa con componente agudo para dar peso al impacto.
  - `semilla_plantar`: Integrado crujido terroso de hojarasca y reverb muy corta de tierra húmeda.
- **Balance general**: Rugidos y victorias de jefes atenuados en `VOLUMEN` a -2.0 dB para preservar la presencia de la música.

### 6. `revision/interfaz`
- **Menú de pausa (`scripts/interfaz/menu_pausa.gd`)**:
  - Objetos en dos columnas ordenadas con icono oficial de `arte/interfaz/objetos.png`.
  - Prevención de desbordamiento de `CAJA_INFO`.
- **Nitidez tipográfica**: Desactivado el posicionamiento subpíxel (`SUBPIXEL_POSITIONING_DISABLED`) en `objetivo.gd` y `mochila.gd` para garantizar píxeles nítidos a resolución 640×360.
- **Mapa y atajos**: Añadido punto cardinal de `cueva_eco` en `PUNTO_RAIZ` y soporte para `keycode` además de `physical_keycode`.

### 7. `revision/codigo`
- **Texturas radiales de luz (`scripts/mundo/relieve.gd`)**:
  - Creado método estático `Relieve.textura_luz(tam: int)` con diccionario de caché estática `_cache_luz`.
  - Reutilizada en `Relieve.destello()`, `brasero.gd`, `oscuridad.gd` y `seta_luz.gd`, eliminando la instanciación de texturas duplicadas.
- **Limpieza arquitectónica**:
  - Unificada la llamada a `hud.fundido()` en `zona_corrupta.gd`.
  - Limpieza de librerías no utilizadas en `componer_musica.py`.

### 8. `revision/rendimiento`
- **Aldeanos (`scripts/mundo/aldea/aldeano.gd`)**:
  - Eliminado el recálculo constante de `CHARLA.tiene_novedad()` y búsqueda de Maisha en cada fotograma. Ahora se evalúa en `_al_poner_marca()` o mediante temporizador de 0.5 s.
  - `queue_redraw()` solo se ejecuta cuando el estado de novedad o distancia de Maisha cambia.
- **Ambiente (`scripts/mundo/ambiente.gd`)**:
  - Reemplazados 5 `.filter()` sucesivos por iteración inversa in-place para eliminar partículas muertas.
  - Descarte anticipado (culling) de nubes fuera del viewport antes del cálculo de polígonos.
  - Uso de `draw_set_transform()` para evitar alocación de `PackedVector2Array` por fotograma.
- **Resultados de benchmarking medidos en Godot**:
  - Escena `cuna_de_musgo`: De 7.81 ms (128.0 FPS) a 7.08 ms (141.2 FPS) -> **+10.3% de rendimiento**.
  - Escena `prados_del_eco`: De 9.20 ms (108.7 FPS) a 8.49 ms (117.8 FPS) -> **+9.1% de rendimiento**.

### 9. `revision/textos`
- **Lenguaje neutro estricto**:
  - En `datos/dialogos/raiz.json` (`embarcadero_darsena_sola`): Corregido `"No. Sola no."` por `"No. Sin ayuda no."`.
  - En `primer_arbol_final`: Corregido `"Debajo hay una luz lila, cansada pero entera"` por `"Debajo hay una luz lila, tenue pero entera"`.
  - En `scripts/mundo/interiores/casa_shamba.gd`: Corregido `"(Duerme, pequeño brote...)"` por `"(Duerme, brotecito...)"`, unificando el trato con el diálogo de Bibi.

### 10. `revision/estabilidad`
- **Acceso nulo por destrucción en inicialización (`aldeano.gd`, `recogible.gd`)**:
  - Cuando un aldeano o recogible no cumple las marcas de activación y llama a `queue_free()` en `_ready()`, se invoca inmediatamente `set_process(false)`.
  - Añadida guarda preventiva `if _sprite == null or not is_instance_valid(_sprite): return` al comienzo de `_process()`.
- **Captura de nodos liberados en corrutinas (`kitovu.gd`)**:
  - En la lección de siembra de semillas («¡Sal de la cruz!»), se sustituyó la captura del objeto `semilla` por el identificador primitivo `id_semilla := semilla.get_instance_id()`.
  - La condición de parada valida `is_instance_id_valid(id_semilla)`, eliminando el error de depuración de GDScript `Lambda capture at index 0 was freed`.
