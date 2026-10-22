# 🐗 FICHA TÉCNICA 3D: PETRINO DE GIZA (LA BESTIA PÉTREA CENICIENTA)

- **Elemento**: Petrino de Giza (Enemigo Bestia de Choque del Prólogo)
- **Archivo Destino**: `modelos/enemigos/petrino_giza.glb`
- **Escena en Godot**: `escenas/enemigos/petrino_3d.tscn`
- **Modelador Asignado**: Claude Code (Blender `bpy`)
- **Estándar Visual**: *God of War* / *Shadow of the Colossus* / *Elden Ring*. Criatura cuadrúpeda masiva de roca viva corrompida por la petrificación.

---

## 📏 PROPORCIONES Y SILUETA (1:1 BLENDER)
- **Dimensiones Generales**:
  - Longitud total (hocico a anca): $1.85\text{ m}$
  - Altura a la cruz (hombros): $1.15\text{ m}$
  - Anchura de pecho: $0.85\text{ m}$
  - Masa percibida: Bestia tosca, baja y densa de piedra granítica andante.
- **Anatomía**:
  - **Cabeza y Fauces**: Cráneo macizo en forma de cuña de pedernal. Mandíbula con dos colmillos toscos de cuarzo ferroso afilados por el roce contra la roca. No tiene ojos orgánicos: cuencas hundidas de donde emana un sutil resplandor violeta/ceniza de Giza.
  - **Lomo y Coraza**: Placas superpuestas de lajas de pizarra y basalto que forman un caparazón espinoso protector sobre el lomo y los hombros.
  - **Patas y Pezuñas**: Patas cortas y anchas de piedra porosa con garras macizas de sílex para impulsarse al cargar.
  - **Grietas de Corrupción**: Hendiduras profundas en el pecho y flancos por donde late la ceniza de Giza.

---

## 🎨 PALETA DE MATERIALES (HEX)
| Material | Color HEX | Roughness | Metallic | Emission | Función |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `roca_basalto_cuerpo` | `#252528` | 0.92 | 0.0 | - | Cuerpo principal de piedra volcánica oscura |
| `pizarra_coraza_lomo` | `#3c3b42` | 0.85 | 0.05 | - | Placas superpuestas afiladas del lomo |
| `colmillos_silex` | `#6a6258` | 0.45 | 0.1 | - | Colmillos desgastados de pedernal |
| `vetas_giza_violacea`| `#7a288e` | 0.60 | 0.0 | `#9b30b0` (1.8) | Grietas de corrupción que emiten luz tenue |
| `musgo_seco_grietas` | `#353826` | 0.95 | 0.0 | - | Restos de liquen muerto en las juntas |

---

## 🦴 JERARQUÍA DE NODOS / ESQUELETO
```
root (suelo, y=0.0)
 └─ Petrino_Body (MeshInstance3D)
     ├─ Pelvis (y=0.75m)
     │   ├─ Spine_01 -> Spine_02 -> Chest (y=1.05m)
     │   │   ├─ Neck -> Head (y=0.95m)
     │   │   │   └─ Jaw_Tusk (colmillos)
     │   │   ├─ Shoulder_L/R -> LegFront_L/R -> FootFront_L/R
     │   └─ LegBack_L/R -> FootBack_L/R
     └─ Shards_Break (nodos vacíos para fragmentos de rotura al morir)
```

---

## 💥 COMPORTAMIENTO Y FEEDBACK MECÁNICO
1. **Embestida Rectilínea**: Arremete con la cabeza gacha levantando polvo de ceniza.
2. **Aturdimiento por Choque**: Si el jugador rueda hacia un lado y el Petrino colisiona contra un árbol o la pared de la casona, queda aturdido durante 2.5 segundos con chispas de piedra.
3. **Muerte por Fractura**: Al vaciar su barra de guardia, se fragmenta en trozos de roca sólida que caen al suelo con sonido mineral contundente.
