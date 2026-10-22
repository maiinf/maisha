# 🌾 FICHA TÉCNICA 3D: PROPS Y NARRATIVA AMBIENTAL DE EL KITOVU

- **Ubicación**: El Huerto Asfixiado & Entorno de la Casona (El Kitovu)
- **Modelador Asignado**: Claude Code (Blender `bpy`)
- **Estándar Visual**: *God of War (Wildwoods)* / *The Last of Us* (decadencia orgánica) / *Elden Ring*.
- **Objetivo**: Transmitir mediante narrativa ambiental cómo la Purga de Giza ha ido arrinconando la vida de la granja de Mzee Shamba.

---

## 1. 🛒 LA CARRETILLA DE MADERA VOLCADA (`carro_madera.glb`)
- **Dimensiones**: Longitud $1.45\text{ m}$, anchura $0.75\text{ m}$, altura $0.60\text{ m}$.
- **Geometría y Desgaste**:
  - Estructura de dos varales de roble grisáceo agrietado por la intemperie.
  - Cajón de tablones desiguales unidos por remaches de hierro oxidado, con un lateral roto y astillado.
  - Rueda delantera única de madera maciza con aro exterior de hierro forjado partido y oxidado.
  - En el interior del cajón yacen restos de abono petrificado, tierra reseca y hebras de malas hierbas marchitas.
- **Pose en Escena**: Descansa ladeada contra el suelo (inclinación de 28°), abandonada tras romperse la rueda durante la retirada de Mzee Shamba.

---

## 2. ⛏️ LA PALA DE LABRANZA OXIDADA (`pala_oxidada.glb`)
- **Dimensiones**: Longitud del mango $1.15\text{ m}$, hoja de hierro $0.28\text{ m} \times 0.22\text{ m}$.
- **Detalle Texturas**:
  - Mango de madera de fresno desgastada con sudor y tierra seca en el agarre superior en "T".
  - Hoja de pala triangular de hierro forjado cubierta de costras de óxido marrón-rojizo (#8a3a22) y melladuras en el filo.
- **Pose en Escena**: Clavada a 20 cm de profundidad en un surco seco a medio cavar, con un ángulo de 22°, como si el agricultor la hubiera soltado apresuradamente al avanzar la sombra.

---

## 3. 🌾 EL ESPANTAPÁJAROS DE SOMBRAS (`espantapajaros.glb`)
- **Dimensiones**: Altura total $2.10\text{ m}$, envergadura de brazos $1.60\text{ m}$.
- **Estructura y Materiales**:
  - Cruceta tosca de dos ramas gruesas de abedul descortezadas, atadas en la intersección con cuerda de esparto gruesa.
  - Torso vestido con un saco de cáñamo rústico desgastado, deshilachado en la base y remendado con parches de cuero oscuro cosidos con hilo grueso.
  - Cabeza de calabaza seca cubierta con una capucha de arpillera gris y dos pedazos de carbón vegetal incrustados como ojos ciegos.
  - Sombrero cónico de paja trenzada de campesino con el ala deshilachada y caída sobre un hombro.
- **Función Mecánica**: Sirve como **maniquí tutorial táctico**. Posee colisión y reacciona físicamente con bamboleo y desprendimiento de paja al ser golpeado con el báculo de Maisha o al practicar la esquiva.

---

## 4. 🪨 EL POZO MEGALÍTICO ANTIGUO (`pozo_antiguo.glb`)
- **Dimensiones**:
  - Diámetro exterior del brocal: $1.70\text{ m}$, diámetro interior: $1.15\text{ m}$.
  - Altura del brocal de piedra: $0.90\text{ m}$.
  - Altura total con estructura de polea: $2.35\text{ m}$.
- **Geometría y Elementos**:
  - Brocal formado por 4 grandes sillares curvos de piedra caliza desgastada, con profundas hendiduras talladas por la fricción de la soga durante siglos.
  - Musgo húmedo y líquenes verde oscuro en la base y juntas de mortero antiguo.
  - Dos pilastras laterales de roble oscuro que sostienen un travesaño superior con tejadillo a dos aguas de madera podrida.
  - Eje cilíndrico de madera con manivela de hierro y carrete de soga de cáñamo gastada que cuelga hacia el fondo oscuro del pozo.
  - Cubo de madera de cedro con dos aros de hierro forjado colocado sobre el brocal.

---

## 🎨 PALETA DE MATERIALES COMPARTIDA (HEX)
| Material | Color HEX | Roughness | Metallic | Función |
| :--- | :--- | :--- | :--- | :--- |
| `madera_roble_desgastada` | `#4a443c` | 0.88 | 0.0 | Tablones de carretilla, viga de pozo y estacas |
| `hierro_herrumbre` | `#7a3824` | 0.82 | 0.25 | Aros de rueda, polea y hoja de pala |
| `saco_cañamo_parches` | `#7c7462` | 0.90 | 0.0 | Ropa del espantapájaros |
| `caliza_pozo_musgo` | `#585954` | 0.85 | 0.0 | Sillares de piedra caliza con manchas de liquen |
| `tierra_agrietada_surco` | `#3c352a` | 0.95 | 0.0 | Terreno del huerto asfixiado |
