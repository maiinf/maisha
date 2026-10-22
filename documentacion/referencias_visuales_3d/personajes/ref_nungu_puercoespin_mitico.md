# 🪨 FICHA DE REFERENCIA 3D: NUNGU (EL ERUDITO LITOMÍSTICO DE LAS CAVERNAS)

- **Elemento**: Nungu, Científico y Sabio Eremita de las Cavernas Profundas
- **Archivo Destino**: `modelos/personajes/nungu.glb`
- **Modelador Asignado**: Claude Code (vía Blender `bpy`)
- **Naturaleza del Personaje**: **Puercoespín Místico de Cristal y Bambú Resonante (Litho-Erinaceus)**.
  - En la historia original del juego, Nungu es el científico miope con gafas que investiga por qué la piedra violeta subterránea no es mineral inerte, sino una infección viva que *crece* hacia el norte (la corrupción de Giza).
  - En la dirección de arte de fantasía sombría AAA (inspiración: *God of War*, *Elden Ring*, *The Dark Crystal*), Nungu no es un roedor de caricatura, sino un ser subterráneo arcano y fascinante, un eremita cuyas espinas son agujas de cuarzo ahumado y finas cañas minerales huecas que resuenan con las vibraciones telúricas.
- **Papel Narrativo**: 100% idéntico al guion original. Atrapado en la caverna de Kuvu bajo el influjo de las esporas de la colmena hasta que Maisha corta las cortinas de micelio; al liberarse, entrega a Maisha su cuaderno de investigación sobre la piedra violeta.

---

## 📏 PROPORCIONES Y ANATOMÍA MÍSTICA
- **Estatura y Silueta**: $1.20\text{ m}$ de altura (silueta bípeda compacta, baja y encorvada, de unas 3.5 cabezas de proporción).
- **Púas Resonantes de Cuarzo y Caña Mineral**:
  - En su lomo se erigen centenares de púas largas y afiladas compuestas de cuarzo ahumado translúcido y cañas de silicato huecas.
  - Cuando el viento subterráneo sopla o la corrupción de Giza se agita cerca, sus púas emiten un zumbido armónico sutil como un conjunto de diapasones.
  - Entre las púas lleva incrustados pequeños fragmentos de cristal violeta extraídos para sus ensayos alquímicos.
- **Rostro y Gafas de Investigador**:
  - Hocico curtido con pelo áspero en tonos pizarra y ceniza.
  - Lleva ajustadas al hocico unas aparatosas gafas de campo con montura de latón oscuro remachado y múltiples lentes circulares de cuarzo pulido que puede girar para examinar muestras diminutas.
- **Mandil y Utillaje de Campo**:
  - Mandil de cuero crudo curtido reforzado con remaches de bronce, repleto de bolsillos con frascos de vidrio sellados con cera, cinceles diminutos de geólogo y lupas.
  - A la cintura cuelga su **Cuaderno de Campo**, un libro grueso encuadernado en corteza petrificada con esquinas de hierro, repleto de bocetos y anotaciones sobre la propagación de la piedra violeta.

---

## 🎨 PALETA DE MATERIALES (HEX)
| Material | Color HEX | Roughness | Metallic | Emission | Función |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `pelaje_ceniza` | `#383535` | 0.85 | 0.0 | - | Pelaje oscuro de caverna |
| `puas_cuarzo_ahumado` | `#5c5663` | 0.20 | 0.1 | 0.3 | Cristales de cuarzo y cañas minerales translúcidas |
| `cristal_violeta_muestra`| `#8a38b8` | 0.15 | 0.0 | 1.3 | Muestras de la infección de Giza incrustadas |
| `gafas_laton_oscuro` | `#6e5a32` | 0.35 | 0.8 | - | Montura metálica de las lentes |
| `lentes_cuarzo_vidrio` | `#c4d5db` | 0.10 | 0.0 | - | Lentes de aumento |
| `mandil_cuero_gastado` | `#4a3a2a` | 0.80 | 0.0 | - | Cuero de trabajo de geólogo |
| `cuaderno_corteza` | `#2f231b` | 0.90 | 0.0 | - | Cuaderno de notas de campo |

---

## 🦴 ESQUELETO Y RIGGING PARA BLENDER
```
root (suelo, y=0.0)
 └─ hips (centro de masa bajo, y=0.50m)
     ├─ spine_01 -> spine_02 -> chest -> neck -> head (y=1.05m)
     │    ├─ jaw
     │    ├─ glasses_rig (ajuste de lentes)
     │    ├─ quills_fan_01/02/03 (huesos para erizar las púas cristalinas al alertarse)
     ├─ shoulder_L/R -> arm_L/R -> forearm_L/R -> hand_L/R (con garras de excavación)
     └─ thigh_L/R -> calf_L/R -> foot_L/R
```

---

## 🎬 ANIMACIONES CLAVE
1. `idle_examinar`: Ajusta con una garra una de las lentes de sus gafas mientras observa una esquirla de roca violeta.
2. `erizar_puas`: Al sentir una perturbación de Giza, arquea la espalda y sus púas de cristal se abren en abanico emitiendo un tintineo resonante.
3. `escribir_cuaderno`: Apunta con rapidez notas de campo con un trozo de tiza o carbón en su cuaderno de corteza.
4. `entregar_cuaderno`: Extiende con ambas manos el cuaderno hacia Maisha con alivio y urgencia.
