# 🐊 FICHA DE REFERENCIA 3D: MAMBA (EL LEVIATÁN FLUVIAL DE HERRUMBRE)

- **Elemento**: Mamba, Cocodrilo de Herrumbre / Gran Bestia Fluvial Ancestral Corrompida por Giza
- **Archivo Destino**: `modelos/enemigos/mamba.glb`
- **Modelador Asignado**: Claude Code (vía Blender `bpy`)
- **Naturaleza del Personaje**: **Jefe Fluvial / Coloso Anfibio de Hierro Pantanoso y Madera Sumergida**.
  - En la historia original del juego, Mamba bloquea la dársena de Embarcadero Junco y acecha flotando como si fuera un viejo tronco nudoso antes de embestir la plataforma de amarre.
  - En la dirección de fantasía sombría AAA (inspiración: *God of War*, *Shadow of the Colossus*, *Elden Ring*), Mamba es una criatura fluvial prehistórica y titánica cuyo lomo está fusionado con costras de hierro de turbera oxidada, raíces negras anegadas y minerales afilados. Su fauce contiene colmillos irregulares de sílex negro y de sus branquias y heridas rezuma la niebla violeta corrosiva de Giza.
- **Papel Narrativo**: 100% idéntico al guion original. Debe ser vencido en la dársena esquivando sus embestidas contra los cuatro postes de amarre para que sus mandíbulas queden atascadas y permitan a Maisha purificarlo con el Cetro de Raíz, liberando a Bata y el transbordador.

---

## 📏 PROPORCIONES Y ANATOMÍA MÍSTICA
- **Escala y Masa**: Coloso reptiliano anfibio de $4.80\text{ m}$ de longitud total, silueta baja, ancha y pesada ($1.10\text{ m}$ de altura a la cruz).
- **Coraza Dorsal de Herrumbre y Madera**:
  - Escamas que han mutado en placas imbricadas de hierro de pantano oxidado (tonos ocre herrumbre `#6e3b24` y grafito oxidado `#36302c`) con crestas afiladas.
  - Musgo negro de aguas estancadas y algas podridas adheridas a los costados.
- **Fauces Ciclópeas y Dientes de Sílex**:
  - Mandíbulas masivas capaces de astillar pilotes de roble. Dientes desiguales como lascas de sílex negro y basalto afilado.
  - El interior de la boca y la garganta emiten un resplandor violeta tenue y humeante (infección de Giza, `#8830b8`).
- **Ojos Ciegos de Ceniza**:
  - Ojos lechosos velados por la corrupción de Giza, con una pupila vertical casi imperceptible que brilla con hostilidad fría.
- **Cola de Azote Fluvial**:
  - Cola poderosa con doble quilla dorsal dentada que utiliza como remo y ariete destructivo para azotar el agua o las plataformas.

---

## 🎨 PALETA DE MATERIALES (HEX)
| Material | Color HEX | Roughness | Metallic | Emission | Función |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `placas_herrumbre` | `#5c321d` | 0.85 | 0.4 | - | Placas de hierro de turbera oxidadas |
| `vientre_cieno` | `#2d2b27` | 0.70 | 0.0 | - | Piel correosa y húmeda del vientre |
| `dientes_silex` | `#232526` | 0.35 | 0.1 | - | Dientes minerales cortantes |
| `ojo_corrompido` | `#c8b8d4` | 0.15 | 0.0 | 0.5 | Ojo nublado con velo místico |
| `fauces_giza_glow`| `#7a2da8` | 0.25 | 0.0 | 1.4 | Resplandor de la corrupción en la garganta |
| `musgo_cenagoso` | `#232a1c` | 0.90 | 0.0 | - | Sedimento y algas negras adheridas |

---

## 🦴 ESQUELETO Y RIGGING PARA BLENDER
```
root (nivel de flotación, y=0.0)
 └─ spine_center (centro de masa animal, y=-0.10m)
     ├─ spine_01 -> spine_02 -> neck -> head (y=0.20m)
     │    ├─ jaw_lower (gran mandíbula inferior articulada)
     │    └─ throat_corrupt_glow
     ├─ shoulder_L/R -> arm_L/R -> forearm_L/R -> claw_front_L/R (patas robustas con garras)
     ├─ spine_hip -> tail_01 -> tail_02 -> tail_03 -> tail_tip (cola articulada para coletazo)
     └─ hip_L/R -> leg_L/R -> shin_L/R -> claw_back_L/R
```

---

## 🎬 ANIMACIONES CLAVE
1. `flotar_tronco`: Flota inmóvil en el agua con solo los ojos y el lomo acorazado asomando como un viejo tronco a la deriva.
2. `embestir_salto`: Se arquea violentamente y se propulsa fuera del agua con las fauces abiertas para morder la plataforma.
3. `atascar_poste`: Impacta contra un poste de amarre de madera, quedando aturdido y atrapado durante 4 segundos para recibir daño.
4. `coletazo_fase2`: Gira enérgicamente 180° sobre su eje barriendo la plataforma con su pesada cola dentada.
5. `purificacion_vencido`: Al ser purificado por Maisha, la herrumbre y el brillo violeta se disuelven en agua cristalina, y Mamba se sumerge pacíficamente en las profundidades.
