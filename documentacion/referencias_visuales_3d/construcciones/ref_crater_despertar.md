# 🕳️ FICHA TÉCNICA 3D: EL CRÁTER DEL DESPERTAR & EL ÁRBOL SECO

- **Ubicación**: Zona de Inicio del Prólogo Tutorial (El Kitovu)
- **Modelador Asignado**: Claude Code (Blender `bpy`)
- **Estándar Visual**: *God of War* / *Elden Ring* (impacto cósmico sagrado) / *Zelda: Tears of the Kingdom*.

---

## 1. 🕳️ EL CRÁTER DEL IMPACTO (`crater_kitovu.glb`)
- **Dimensiones**:
  - Diámetro del labio exterior: $3.40\text{ m} \times 3.00\text{ m}$ (elipse de impacto).
  - Profundidad central: $0.45\text{ m}$.
- **Geometría y Morfología**:
  - La caída de la chispa cósmica de Asili ha hundido la roca madre en un cuenco gradual.
  - El reborde exterior está formado por lajas de pizarra fracturadas levantadas hacia arriba por la energía del choque.
  - La superficie interior presenta tierra calcinada vidriada y agrietada en patrones radiales.
- **Simbología Rúnica & Vetas de Ámbar**:
  - En el fondo del cráter están grabados **glifos ancestrales en espiral**, idénticos a los tatuajes del antebrazo de Maisha.
  - Entre las grietas asoman vetas de ámbar translúcido que emiten un tenue pulso de calor dorado (`#d89b38`).
- **Mecánica Diegética**:
  - Al abrir los ojos Maisha al iniciar el juego, la luz de estos glifos parpadea suavemente y activa los tatuajes de sus brazos en sincronía: es la tierra misma reconociendo el despertar de la Vida.

---

## 2. 🌲 EL ÁRBOL SECO ANCESTRAL (`arbol_seco.glb`)
- **Dimensiones**:
  - Altura total: $4.60\text{ m}$.
  - Diámetro del tronco en la base: $0.70\text{ m}$, diámetro a media altura: $0.45\text{ m}$.
  - Envergadura de la copa desnuda: $3.20\text{ m}$.
- **Geometría y Silueta**:
  - Un roble milenario completamente petrificado por la ceniza de Giza.
  - Tronco nudoso y retorcido con una espiral en sentido horario, con profundas fisuras en la corteza de las que se desprenden motas de ceniza gris.
  - Se bifurca en tres grandes ramas maestras descortezadas que se alzan hacia el cielo como garras suplicantes, sin una sola hoja verde.
  - En la base, dos raíces gruesas sobresalen del suelo y abrazan el borde rocoso del cráter de impacto.
- **Materiales**:
  - Corteza petrificada gris carbón (`#2e2c2a`) con tacto de piedra calcinada y parches de ceniza blancuzca (`#8c8a85`) en los recovecos superiores.

---

## 🎨 PALETA DE MATERIALES (HEX)
| Material | Color HEX | Roughness | Metallic | Emission | Función |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `roca_calcinada_crater` | `#22201e` | 0.90 | 0.0 | - | Roca fracturada del lecho del cráter |
| `glifos_ambar_crater` | `#d89b38` | 0.40 | 0.1 | `#e8aa42` (1.4) | Simbología en espiral grabada en el suelo |
| `madera_petrificada_seco` | `#2e2c2a` | 0.95 | 0.0 | - | Tronco y ramas del árbol seco |
| `ceniza_incrustada` | `#8c8a85` | 0.98 | 0.0 | - | Polvo de ceniza en hendiduras |
