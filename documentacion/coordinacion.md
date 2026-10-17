# Coordinación entre las dos IAs

Cada IA apunta aquí lo que está tocando **antes** de editarlo y lo borra al terminar.

| Quién | Qué toca | Desde | Rama |
| --- | --- | --- | --- |
| Constructora | Sigilia: Maandiko, la Ciudad-Archivo (`scripts/mundo/sigilia/`, `datos/mapas/maandiko*`, `arte/mundos/sigilia/`, `datos/dialogos/sigilia.json`) | 2026-10-16 | `main` |
| **IA de calidad visual** | **HD-2D**: todo lo visual 3D (`scripts/mundo/hd2d/`, `herramientas/hd2d/`): postprocesado, luces, terreno, sprites, cámara, partículas. Ver `documentacion/prompt_maestro_hd2d.md` | 2026-10-17 | `hd2d/calidad-*` |

## Notas de una IA a la otra

- **Constructora → IA de calidad visual (2026-10-17)**: por decisión de Iam, **el HD-2D pasa a ser tuyo** (`scripts/mundo/hd2d/`). Yo **dejo de tocarlo** y sigo solo con Sigilia (`estanterias_colgantes`, `maandiko`, `paso_escarcha`). Trabaja en **tu propia copia del repositorio** (`~/Proyectos/maisha-hd2d`). Lo hecho y lo que falta está en `documentacion/prompt_maestro_hd2d.md` y en la sección «HD-2D» del LEEME. Si necesitas cambiar `escena_mundo.gd` o `region.gd`, apúntalo aquí antes.

- **Iam (2026-10-16): el juego irá a HD-2D** (los sprites de pixel art en un mundo 3D, como el prototipo `experimento/prototipo-visual`), **no a 3D completo con modelos**. Lo construye la constructora. La revisora vuelve a revisar y pulir lo hecho, sin tocar lo de HD-2D ni Sigilia.

- **Constructora → revisora (2026-10-16)**: he revisado y unido a `main` tus 12 ramas (ver «Revisión de la IA revisora» en `decisiones.md`). Por favor, trabaja desde ahora en **tu propia copia** del repositorio (`~/Proyectos/maisha-revision`), no en `/Users/iinfafer/Proyectos/maisha`: al cambiar de rama aquí, un commit mío cayó en tu rama `revision/bastones-aldeanos`.
- **Constructora → revisora**: en `revision/luz-2.5d` usabas el nombre de escena `paso_de_la_escarcha` (no existe: es `paso_escarcha`, y es de Sigilia). Lo he quitado; el color de las escenas de Sigilia lo ajusta la constructora.
- **Constructora → revisora**: cambiaste los instrumentos de `sintetizador.py`, pero solo se regeneraron 4 pistas de música; las demás siguen con el sonido viejo. Si quieres que todas cambien, regenéralas todas y vuelve a medir `VOLUMEN_MUSICA` con las pistas nuevas.
