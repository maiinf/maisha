# Ideas de la IA revisora (a futuro)

Aquí van las ideas que **no** son una mejora de lo ya hecho. No se implementan sin que Iam las apruebe.

| Idea | Por qué | Esfuerzo (S/M/L) | Qué tocaría |
| --- | --- | --- | --- |
| **Audio dinámico por capas (stems reactivos)** | Las piezas generadas proceduralmente ya tienen pistas aisladas (melodía, bajo, kalimba, percusión). Reproducirlas en buses independientes permite transiciones fluidas: la percusión entra al cruzar una zona corrupta y se desvanece al purgarla, sin reiniciar la pista. | M | `scripts/globales/sonido.gd`, `herramientas/sintetizador.py` |
| **Modo Cuaderno de Campo (bocetos con filtro de tinta)** | El diario ya tiene una estética maravillosa de papel y tinta. Permitir congelar el juego en puntos panorámicos para estampar un boceto a pluma en una página del diario refuerza el tono contemplativo del viaje de Maisha. | M | `scripts/interfaz/mochila.gd`, shaders en `shaders/` |
| **Efectos climáticos atmosféricos ligeros por bioma** | Llovizna tenue en el Lago Kimya, hojas cobrizas meciéndose en el Bosque Cobrizo y motas de polen en Cuna de Musgo. Usando `GPUParticles2D` o mallas fijas para cero coste de CPU. | S | `scripts/mundo/ambiente.gd`, `arte/efectos/` |
| **Accesibilidad sensorial y señales visuales de combate** | Indicador visual sutil en pantalla para el chisporroteo de la mecha de las semillas y el clinc del escudo, pensado para jugar sin sonido o con baja audición, junto con paleta de alto contraste para daltónicos. | S | `scripts/interfaz/`, `scripts/globales/impacto.gd` |
| **Coliseo de Rescoldos (rematch de jefes con desafíos)** | Aprovechando que los rescoldos de Giza ya reviven el eco de los jefes para el rango de oro, crear una pequeña gruta en el Nexo donde retar a jefes con condiciones especiales (sin daño, tiempo límite) para desbloquear tintes rúnicos de ropa. | L | `scripts/mundo/`, `scripts/interfaz/tienda_tawi.gd`, `Estado` |
