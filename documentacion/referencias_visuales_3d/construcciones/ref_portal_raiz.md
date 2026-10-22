# 🚪 FICHA TÉCNICA 3D: EL PORTAL DE RAÍZ & EL NUDO DE CORRUPCIÓN

- **Ubicación**: Límite Este del Desfiladero (Salida de El Kitovu hacia Cuna de Musgo)
- **Modelador Asignado**: Claude Code (Blender `bpy`)
- **Estándar Visual**: *God of War* / *Zelda: Tears of the Kingdom* / *Shadow of the Colossus*.

---

## 1. 🌿 EL MONUMENTAL PORTAL DE RAÍZ (`portal_raiz.glb`)
- **Dimensiones**:
  - Altura total del arco: $4.80\text{ m}$.
  - Anchura libre de paso interior: $2.80\text{ m}$.
  - Profundidad del umbral: $1.40\text{ m}$.
- **Geometría y Morfología**:
  - Dos raíces colosales vivas de roble milenario de $0.75\text{ m}$ de diámetro nacen de ambos lados del desfiladero rocoso.
  - Ascienden retorciéndose con fuerza sobre sí mismas y se entrelazan en la cúspide formando un arco ojival natural.
  - La superficie de la madera viva tiene musgo terciopelo verde oscuro en las zonas húmedas y vetas de savia dorada latente en sus surcos.
  - Pequeños brotes tiernos con hojas verdes vivas asoman en las uniones de las ramas entrelazadas.
- **Transición Atmosférica**:
  - A través del vano del portal no se ve un cielo plano, sino un túnel de raíces descendente sumergido en una densa bruma dorada y esporas flotantes, indicando el camino hacia la Cuna de Musgo.

---

## 2. 🪨 EL NUDO DE CORRUPCIÓN DE GIZA (`nudo_corrupcion.glb`)
- **Dimensiones**:
  - Diámetro del bulbo central: $1.60\text{ m}$.
  - Envergadura de zarcillos espinosos: $3.20\text{ m}$ (sellando de lado a lado el sendero).
- **Geometría y Detalle**:
  - Un corazón vegetal podrido y petrificado por la sombra de Giza.
  - Zarcillos retorcidos de madera negra carbonizada que brotan del suelo y forman una barrera impenetrable de pinchos y espinas.
  - En la parte central brotan agujas minerales y cristales afilados de cuarzo violeta oscuro que pulsan con una luz corrupta siniestra.
  - El suelo a 3 metros alrededor del nudo está marchito y desprovisto de hierba, convertido en ceniza gris cuarteada.
- **Interacción y Purificación**:
  - Posee colisión que impide el paso al portal.
  - Al recibir el pulso telúrico del Corazón de Asili o el golpe de báculo consagrado, las espinas minerales se quiebran en esquirlas, los zarcillos negros se deshacen en ceniza y una onda de choque dorada barre el suelo restaurando el césped y abriendo el Portal de Raíz.

---

## 🎨 PALETA DE MATERIALES (HEX)
| Material | Color HEX | Roughness | Metallic | Emission | Función |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `madera_raiz_portal` | `#453324` | 0.85 | 0.0 | - | Madera viva del arco de raíces |
| `musgo_fresco_portal` | `#2d4822` | 0.90 | 0.0 | - | Manchas de musgo en la base del portal |
| `savia_dorada_raiz` | `#dfa838` | 0.40 | 0.1 | `#f5be42` (1.5) | Vetas de energía en la madera viva |
| `madera_corrupta_nudo` | `#1c181d` | 0.95 | 0.0 | - | Madera negra petrificada del nudo |
| `cristal_giza_violeta` | `#4a1856` | 0.25 | 0.1 | `#7b2292` (2.2) | Agujas minerales de corrupción |
