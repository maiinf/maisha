# 🏚️ FICHA TÉCNICA 3D: CASA GRANJA EN RUINA (ESTADO INICIAL / PRE-PURGA)

- **Elemento**: Casa Granja de Mzee Shamba en estado de degradación por la ceniza de Giza.
- **Archivo Destino**: `modelos/entorno/casa_granja_ruina.glb` (o `kitovu_ruina.glb`)
- **Modelador Asignado**: Claude Code (Blender `bpy`)
- **Propósito**: Tono por estados (la granja comienza sombría, desgastada y con daños por la petrificación, y al purificarse el nudo se restaura al estado vivo).

---

## 📏 MODIFICACIONES RESPECTO AL ESTADO VIVO (`casa_granja.glb`)

1. **Tejado a Dos Aguas**:
   - Falda izquierda con 3 tablones caídos o partidos, dejando al descubierto vigas secundarias de madera ennegrecida.
   - Ceniza gris acumulada en las canales del tejado.
   - La chimenea de piedra caliza no emite humo en este estado; la boca está tapada por telarañas y hollín cuarteado.
2. **Rueda del Molino Hidráulico**:
   - La rueda está **bloqueada/atascada**: dos de sus aspas de madera están partidas por un zarcillo petrificado seco.
   - La canaleta de madera superior está agrietada y no conduce agua limpia, solo un goteo turbio.
3. **Muros de Troncos y Zócalo**:
   - Troncos de cedro con manchas de humedad podrida y corteza agrisada por la ceniza.
   - El zócalo de pizarra tiene musgo seco y quebradizo en lugar de líquenes vivos.
4. **Porche y Ventanas**:
   - Las ventanas están apagadas (sin emisión dorada en `luz_ventana`, con cristales sucios y opacos).
   - El farol del porche está apagado, con el cristal roto.
   - Los escalones de madera tienen una tabla partida.

---

## 🎨 PALETA DE MATERIALES (HEX)
| Material | Color HEX | Roughness | Metallic | Emission | Notas |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `madera_troncos_ceniza` | `#5a483a` | 0.90 | 0.0 | - | Madera apagada y sin vida |
| `madera_tejado_roto` | `#6b4b38` | 0.88 | 0.0 | - | Tablones quebrados |
| `piedra_zocalo_seco` | `#45484d` | 0.92 | 0.0 | - | Pizarra gris cenicienta |
| `ventana_apagada` | `#282a2e` | 0.60 | 0.1 | 0.0 | Sin luz interior |
| `rueda_atascada` | `#35281e` | 0.85 | 0.0 | - | Madera oscura con grietas |
