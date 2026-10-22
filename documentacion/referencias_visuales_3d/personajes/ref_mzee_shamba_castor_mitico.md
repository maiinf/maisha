# 🌾 FICHA DE REFERENCIA 3D: MZEE SHAMBA (EL SABIO Y CULTO CASTOR DE EL KITOVU)

- **Elemento**: Mzee Shamba, Patriarca Agricultor y Sabio Botánico de El Kitovu
- **Archivo Destino**: `modelos/personajes/mzee_shamba.glb`
- **Modelador Asignado**: Claude Code (vía Blender `bpy`)
- **Dirección Creativa Oficial (Feedback Directo de Iam)**:
  - **100% Bípedo y de Media Estatura**: No es un monstruo gigante ni una bestia cuadrúpeda salvaje. Es un venerable anciano castor erguido, de estatura media ($1.45\text{ m}$), de porte culto, tranquilo y afable.
  - **Muy Sabio, Culto y con Gafas**:
    - Lleva unas características **gafas redondas con montura metálica fina** apoyadas sobre el hocico, que le dan un aire erudito de botánico milenario.
    - Es un anciano que lee tratados de agricultura antigua, clasifica semillas raras en pergaminos y custodia la memoria botánica de Asili antes de la decadencia.
    - Habla con calma, educación paternal y ternura hacia Maisha.

---

## 📏 PROPORCIONES Y ANATOMÍA BÍPEDA
- **Estatura y Silueta**: $1.45\text{ m}$ de altura (silueta bípeda de anciano sabio, de unas 4.5 cabezas de proporción estilizada). Ligeramente encorvado de hombros por los años de estudio y labranza, pero con un paso digno y sereno.
- **Rostro y Hocico Erudito**:
  - Hocico noble y canoso con incisivos limpios y cuidados de castor sabio.
  - Gafas redondas con patillas curvas ajustadas tras sus orejas redondas de castor.
  - Bigotes sensoriales blancos y suaves que tiemblan con curiosidad al examinar un brote nuevo.
  - Ojos sabios y bondadosos detrás de los cristales de aumento.
- **Cola de Castor como Tercer Punto de Apoyo**:
  - Cola ancha, aplanada y de textura de cuero escamado suave, que arrastra de forma natural al caminar bípedo y que utiliza como taburete o apoyo al inclinarse a examinar las plantas.
- **Indumentaria de Sabio Campesino Culto**:
  - **Chaleco de paño rústico**: De pana gastada en tonos ocre tostado (#6b4f35) con pequeños bolsillos donde guarda una lupa de mano, tiza y saquitos de semillas raras.
  - **Camisa de algodón crudo**: Color crema (#e0d8c3) con las mangas pulcramente arremangadas hasta los codos.
  - **Pañuelo al cuello**: Pañuelo suave de cuadros apagados (#7a5542).
  - **Pantalones de trabajo y polainas**: Tejido resistente remendado y zapatillas o botas de cuero suave adaptadas a sus patas palmeadas.
  - **Herramienta**: Un bastón de paseo de roble que en la base tiene una pequeña azadilla botánica de latón pulido.

---

## 🎨 PALETA DE MATERIALES (HEX)
| Material | Color HEX | Roughness | Metallic | Emission | Función |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `pelaje_castor_canoso` | `#4a3a2d` | 0.85 | 0.0 | - | Pelaje pardo suave con canas en patillas y hocico |
| `gafas_sabio_laton` | `#9c8144` | 0.30 | 0.8 | - | Montura metálica fina de las gafas |
| `cristal_lentes` | `#c8dce4` | 0.10 | 0.0 | - | Lentes de aumento translúcidas |
| `chaleco_pana_sabio` | `#6b4f35` | 0.80 | 0.0 | - | Chaleco de paño rústico con bolsillos |
| `camisa_algodon_crudo`| `#e0d8c3` | 0.85 | 0.0 | - | Camisa de algodón crudo arremangada |
| `cola_cuero_castor` | `#3b2e24` | 0.70 | 0.0 | - | Cola plana de castor de tacto suave |
| `pañuelo_cuello` | `#7a5542` | 0.85 | 0.0 | - | Pañuelo campesino acogedor |
| `baston_azada_roble` | `#423223` | 0.75 | 0.0 | - | Bastón de paseo y estudio botánico |

---

## 🦴 ESQUELETO Y RIGGING PARA BLENDER
```
root (suelo, y=0.0)
 └─ hips (pelvis bípeda, y=0.65m)
     ├─ spine_01 -> spine_02 -> chest -> neck -> head (y=1.30m)
     │    ├─ jaw (mandíbula inferior)
     │    ├─ glasses_bone (control sutil de acomodarse las gafas)
     │    └─ whiskers_L / whiskers_R
     ├─ shoulder_L -> arm_L -> forearm_L -> hand_L (para sostener pergaminos o libros)
     ├─ shoulder_R -> arm_R -> forearm_R -> hand_R (socket para Bastón)
     ├─ tail_01 -> tail_02 -> tail_paddle (cola de castor bípeda para apoyo)
     └─ thigh_L/R -> calf_L/R -> foot_L/R (patas bípedas plantígradas)
```

---

## 🎬 ANIMACIONES CLAVE
1. `idle_ajustar_gafas`: De pie pacíficamente, se sube las gafas por el hocico con un dedo mientras lee un papel o mira a Maisha.
2. `hablar_culto`: Gesticula con serenidad y elocuencia mientras se apoya en su bastón de botánico.
3. `examinar_brote`: Se agacha apoyando su peso sobre la cola de castor y observa una zanahoria con su lupa de mano.
4. `ofrecer_sopa`: Sostiene con ambas manos un cuenco de sopa humeante con una sonrisa paternal y acogedora.
