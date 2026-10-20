extends Node3D
## EL ESPEJO HD-2D: dibuja en 3D la escena 2D que se está jugando, sin cambiar nada del juego.
## El juego sigue siendo 2D por dentro (física, enemigos, zonas, diálogos...); esto solo cambia CÓMO SE VE:
##   - EL SUELO: cerca de Maisha, la capa de suelo (abajo); más lejos, el suelo pintado del mapa
##     (arte/mundos/<mundo>/suelos/<mapa>_suelo.png).
##   - LAS PEÑAS («0» del mapa) se levantan como bloques de roca, con el suelo pintado encima.
##   - CADA DIBUJO del mundo (Sprite2D y AnimatedSprite2D) tiene su gemelo 3D DE PIE (Sprite3D que mira a la cámara),
##     en su sitio del suelo y con SOMBRA real; lo que va pegado al suelo (z por debajo de -4) se tumba en el suelo.
##     Las capas de un mismo personaje (cuerpo, ropa, cetro) se apoyan en el mismo punto del suelo.
##   - LO QUE SE DIBUJA CON CÓDIGO (_draw) va por capas (el «canal» visibility_layer de cada dibujo):
##       · lo del suelo y los efectos (zonas de Giza, hierba, brotes, avisos, golpes...): se pinta en una CAPA DE
##         SUELO (un SubViewport que mira la misma escena 2D) que se tumba sobre el suelo 3D alrededor de Maisha;
##       · lo de pantalla (niebla, hojas, nevada, ventisca, rayos de sol): CAPA DE PANTALLA, delante, como en 2D;
##       · lo que va de pie (llamas, halos, el «!»...: DE_PIE): en una VENTANITA de pie sobre su objeto;
##       · las sombras ovaladas pintadas (sombra.gd): no se ven (ya hay sombras de verdad).
##     Los dibujos pegados al suelo (z por debajo de -4) también van a la capa de suelo.
##   - UNA CÁMARA en perspectiva que sigue a Maisha, el sol (con el reloj del día) y algo de niebla.
## La escena 2D no se oculta: solo deja de pintarse en la pantalla principal (canvas_cull_mask); la interfaz
## (CanvasLayer) sigue igual. Medidas: 16 px = 1 m (una casilla).

const PX := 1.0 / 16.0
const ALTO_PENA := 1.25            # metros que se levanta una peña (lo que mide su pared pintada: unos 20 px)
## Mapas en los que la pared pintada es el doble de alta (gargantas y montaña: pintar_suelo, «cara=2»)
const PARED_DOBLE := ["canada_eco", "paso_piedra", "sendero_olvidado", "ruinas_primer_arbol", "paso_escarcha"]
const SUELO_BAJO := -4             # dibujos con z_index por debajo: se tumban en el suelo
const CAMARA_INCLINACION := -48.0  # grados (mirando hacia abajo)
const CAMARA_DISTANCIA := 50.6     # teleobjetivo de maqueta: mantiene el encuadre sin inclinar las casas en los bordes
const CAMARA_FOV := 18.0
const LEJOS := 30.0                # metros: más allá de esto (del foco), los gemelos no se copian
## Los canales de dibujo (visibility_layer) del mundo; la interfaz se queda en el 1, el de siempre. La pantalla
## principal deja de pintar estos canales y las capas pintan solo el suyo.
const CANAL_SUELO := 1 << 12
const CANAL_GEMELO := 1 << 13
const CANAL_PANTALLA := 1 << 14
const CANAL_NADA := 1 << 15
const CANAL_PIE := 1 << 16
const CANALES_MUNDO := CANAL_SUELO | CANAL_GEMELO | CANAL_PANTALLA | CANAL_NADA | CANAL_PIE
## Los que dibujan con código algo que va DE PIE (llamas, halos, auras de enemigos, avisos, el «!»):
## lo que dibujan ellos (o sus hijos sin script) se ve en una VENTANITA de pie sobre ellos (_ventanas)
const DE_PIE := [
	"brasero.gd", "fogata.gd", "farol.gd", "farol_runico.gd", "eco_perdido.gd", "esencia.gd",
	"recogible.gd", "arco_ruinas.gd", "portal.gd", "aldeano.gd", "taa.gd",
	"bundi.gd", "buibui.gd", "murcielago_eco.gd", "kuvu.gd", "guardian.gd", "mamba.gd",
	"kambare.gd", "konokono.gd", "petrino.gd", "jabali.gd", "mzizi.gd", "cosechadora.gd",
	"tintero.gd", "escriba.gd", "piedra_recuerdo.gd", "cerradura_tinta.gd", "atril.gd",
	"ficha_indice.gd", "altar_corteza.gd", "estatua_quieta.gd", "campanilla.gd"
]
const VENTANA := Vector2i(128, 160)       # píxeles de cada ventanita
const VENTANA_PIE := Vector2(64, 148)     # dónde cae el pie del objeto dentro de la ventanita
const VENTANAS := 16                      # ventanitas para los objetos de pie más cercanos a la cámara
const LADO_CAPA := 768             # píxeles de la capa de suelo (48 m alrededor de Maisha: cubre toda la cámara)
## El suelo cercano: la capa de suelo, con luz (para las sombras de personajes, huellas y Giza)
const SOMBREADOR_CAPA := """
shader_type spatial;
render_mode diffuse_lambert, depth_draw_opaque;
uniform sampler2D capa : filter_nearest;
uniform sampler2D agua : filter_linear;
uniform sampler2D mapa_ao : filter_linear;
uniform vec2 origen = vec2(0.0);
uniform vec2 casillas = vec2(1.0);
uniform float lado = 768.0;
uniform float fuerza_nubes = 0.14;

void vertex() {
	// Terreno plano y estable: cero deformación de vértices para erradicar cualquier oscilación al caminar
}

void fragment() {
	vec2 px = origen + UV * lado;
	vec2 uv_mapa = px / 16.0 / casillas;
	float es_agua = texture(agua, uv_mapa).r;

	// Hueco limpio y estable donde hay agua
	if (es_agua > 0.36) { discard; }

	vec3 c = texture(capa, UV).rgb;
	float ao = texture(mapa_ao, uv_mapa).r;
	c *= mix(1.0, 0.56, ao);
	float orilla_sombra = smoothstep(0.18, 0.36, es_agua);
	c *= mix(1.0, 0.80, orilla_sombra);

	if (fuerza_nubes > 0.005) {
		vec2 p_nube = px * 0.0065 + vec2(TIME * 0.09, TIME * 0.04);
		float n_nube = sin(p_nube.x + sin(p_nube.y * 1.3)) * cos(p_nube.y * 0.9 - sin(p_nube.x * 0.8)) * 0.5 + 0.5;
		c *= 1.0 - smoothstep(0.54, 0.88, n_nube) * fuerza_nubes;
	}

	// Desvanecimiento suave en los bordes de la capa para fundirse invisiblemente con el suelo lejano
	vec2 d_cuadro = min(UV, vec2(1.0) - UV) * lado;
	float f_cuadro = clamp(min(d_cuadro.x, d_cuadro.y) / 36.0, 0.0, 1.0);
	if (f_cuadro < 0.01) { discard; }

	ALBEDO = c;
	ALPHA = smoothstep(0.0, 1.0, f_cuadro);
	ROUGHNESS = 0.96;
	SPECULAR = 0.04;
}
"""
## El suelo lejano (todo el mapa): base plana con desniveles, oclusión perimetral y lecho de fondo continuo
const SOMBREADOR_LEJANO := """
shader_type spatial;
render_mode diffuse_lambert;
uniform sampler2D suelo : filter_nearest, source_color;
uniform sampler2D agua : filter_linear;
uniform sampler2D mapa_ao : filter_linear;
uniform vec2 casillas = vec2(60.0, 60.0);
uniform vec3 tinte_2d = vec3(1.0);
uniform float hundido = 0.0;
uniform float fuerza_nubes = 0.14;
uniform float calma_lago = 0.0;

void vertex() {
	// Terreno plano y estable
}

void fragment() {
	vec2 px = UV * casillas * 16.0;
	float es_agua = texture(agua, UV).r;

	if (hundido < 0.5) {
		// Capa de suelo base del mapa
		if (es_agua > 0.36) { discard; }
		vec3 c = texture(suelo, UV).rgb * tinte_2d;
		float ao = texture(mapa_ao, UV).r;
		c *= mix(1.0, 0.56, ao);
		float orilla_sombra = smoothstep(0.18, 0.36, es_agua);
		c *= mix(1.0, 0.80, orilla_sombra);
		if (fuerza_nubes > 0.005) {
			vec2 p_nube = px * 0.0065 + vec2(TIME * 0.09, TIME * 0.04);
			float n_nube = sin(p_nube.x + sin(p_nube.y * 1.3)) * cos(p_nube.y * 0.9 - sin(p_nube.x * 0.8)) * 0.5 + 0.5;
			c *= 1.0 - smoothstep(0.54, 0.88, n_nube) * fuerza_nubes;
		}
		vec2 d_borde = min(UV * casillas, (vec2(1.0) - UV) * casillas);
		float f_borde = clamp(min(d_borde.x, d_borde.y) / 2.2, 0.0, 1.0);
		c *= mix(0.28, 1.0, smoothstep(0.0, 1.0, f_borde));
		ALBEDO = c;
		ROUGHNESS = 0.96;
		SPECULAR = 0.04;
	} else {
		// Lecho continuo de guijarros/arena: elimina al 100% el vacío negro bajo el agua
		if (es_agua <= 0.10) { discard; }
		vec3 c = texture(suelo, UV).rgb * tinte_2d;
		vec3 color_grava = mix(vec3(0.24, 0.32, 0.28) * tinte_2d, c * 0.68, 0.70);
		ALBEDO = color_grava;
		ROUGHNESS = 0.95;
		SPECULAR = 0.02;
	}
}
"""
## Sombreador de agua cristalina HD-2D: translúcida continua, profundidad real, reflejos suaves, espuma en orillas y refracción
const SOMBREADOR_AGUA := """
shader_type spatial;
render_mode blend_mix, depth_draw_always, diffuse_lambert, specular_schlick_ggx;
uniform sampler2D suelo : filter_nearest, source_color;
uniform sampler2D agua : filter_linear;
uniform sampler2D mapa_ao : filter_linear;
uniform vec2 casillas = vec2(60.0, 60.0);
uniform vec3 tinte_2d = vec3(1.0);
uniform float calma_lago = 0.0;
uniform float fuerza_nubes = 0.14;

void vertex() {
	// Lámina de agua plana y estable
}

void fragment() {
	vec2 px = UV * casillas * 16.0;
	float f_calma = 1.0 - calma_lago * 0.85;
	float temblor = (sin(px.x * 0.37 + px.y * 0.21 + TIME * 0.9) * 0.035 + sin(px.y * 0.53 - px.x * 0.17 - TIME * 0.7) * 0.025) * f_calma;
	float es_agua = texture(agua, UV).r + temblor;

	if (es_agua < 0.14) { discard; }

	// Refracción tenue en las ondas superficiales
	vec2 refraccion = vec2(
		cos(px.x * 0.15 + TIME * 1.2 * f_calma),
		sin(px.y * 0.15 + TIME * 1.2 * f_calma)
	) * 0.003 * f_calma;
	vec3 c_refractado = texture(suelo, UV + refraccion).rgb * tinte_2d;

	// Ondulación superficial multicapa
	float onda1 = sin(px.x * 0.08 + px.y * 0.04 + TIME * 1.4 * f_calma) * sin(px.y * 0.11 - px.x * 0.03 - TIME * 1.0 * f_calma);
	float onda2 = sin(px.x * 0.19 - px.y * 0.15 - TIME * 1.9 * f_calma) * 0.5 + 0.5;

	// Profundidad continua graduada sin saltos bruscos
	float profundidad = smoothstep(0.18, 0.72, es_agua);

	// Gradiente acuático cinemático HD-2D: desde agua somera turquesa cristalina hasta azul profundo
	vec3 agua_orilla = vec3(0.20, 0.55, 0.65) * tinte_2d;
	vec3 agua_profunda = vec3(0.08, 0.26, 0.44) * tinte_2d;
	vec3 c_agua = mix(agua_orilla, agua_profunda, profundidad);
	if (calma_lago > 0.01) {
		c_agua = mix(c_agua, vec3(0.16, 0.38, 0.58) * tinte_2d, calma_lago * 0.5);
	}

	// Destellos de luz y reflejos suaves en las crestas de ola
	c_agua += vec3(0.10, 0.16, 0.20) * tinte_2d * smoothstep(0.65, 0.98, onda1) * f_calma;
	c_agua += vec3(0.05, 0.10, 0.14) * tinte_2d * smoothstep(0.72, 0.95, onda2) * profundidad * f_calma;

	// Franja de espuma blanca orgánica en contacto con la orilla
	float pulso_orilla = sin(px.x * 0.34 + px.y * 0.29 - TIME * 2.3 * f_calma) * 0.5 + 0.5;
	float franja_espuma = smoothstep(0.38, 0.22, es_agua) * smoothstep(0.14, 0.24, es_agua);
	float espuma = smoothstep(0.20, 0.55, franja_espuma + pulso_orilla * 0.18);
	c_agua = mix(c_agua, vec3(0.92, 0.97, 1.0) * tinte_2d, espuma * 0.85);

	// Combinación de color con el lecho visible por refracción
	ALBEDO = mix(c_refractado * 0.75, c_agua, 0.62 + profundidad * 0.30);

	// Transparencia gradual: transparente cerca del borde del cauce para fundir con el lecho
	float alfa = smoothstep(0.14, 0.28, es_agua) * clamp(0.55 + profundidad * 0.40, 0.0, 0.95);
	ALPHA = alfa;

	ROUGHNESS = mix(0.18, 0.04, calma_lago);
	SPECULAR = mix(0.50, 0.85, calma_lago);
}
"""
## Sombreador 3D para los gemelos con mapa de normales (*_n.png):
## Conserva los colores exactos del pixel art al sol, proyecta y recibe sombras 3D suaves y reacciona con volumen
## tanto al sol/luna como a las luces puntuales 3D (OmniLight3D) de faroles, ventanas, braseros y fogatas.
const COMPENSACION_Y := 1.24       # compensación vertical de perspectiva bajo cámara a -48°
const SOMBREADOR_GEMELO := """
shader_type spatial;
render_mode ambient_light_disabled, specular_disabled, cull_disabled;
uniform sampler2D tex_albedo : filter_nearest, source_color;
uniform sampler2D tex_normal : filter_nearest;
uniform vec3 tinte_ambiente = vec3(1.0);
uniform float usa_normal = 1.0;
uniform float volteo_x = 1.0;
uniform float mecido = 0.0;
uniform float curvatura_3d = 0.75;
uniform vec2 hv_frames = vec2(1.0, 1.0);
uniform vec3 pos_maisha = vec3(0.0);

void vertex() {
	if (mecido > 0.001) {
		vec3 wp = (MODEL_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
		float h_copa = clamp(1.0 - UV.y, 0.0, 1.0);
		float peso = h_copa * h_copa;
		float brisa = sin(TIME * 2.15 + wp.x * 0.65 + wp.z * 0.45) * 0.7
			+ sin(TIME * 3.6 - wp.z * 0.8 + wp.x * 0.3) * 0.3;
		VERTEX.x += brisa * mecido * peso;
		vec2 d_m = wp.xz - pos_maisha.xz;
		float dist = length(d_m);
		if (dist < 1.35 && dist > 0.01) {
			float empuje = (1.0 - dist / 1.35);
			VERTEX.x += (d_m.x / dist) * empuje * empuje * min(mecido * 3.2, 0.22) * h_copa;
		}
	}
}

void fragment() {
	vec4 c = texture(tex_albedo, UV);
	if (c.a < 0.5) {
		discard;
	}
	// Bisel volumétrico 3D en tiempo real midiendo el contorno de la silueta del fotograma actual
	vec2 tex_tam = vec2(textureSize(tex_albedo, 0));
	vec2 paso = 1.0 / max(tex_tam, vec2(1.0));
	float a_izq = texture(tex_albedo, UV - vec2(paso.x * 2.2, 0.0)).a * 0.6 + texture(tex_albedo, UV - vec2(paso.x * 4.8, 0.0)).a * 0.4;
	float a_der = texture(tex_albedo, UV + vec2(paso.x * 2.2, 0.0)).a * 0.6 + texture(tex_albedo, UV + vec2(paso.x * 4.8, 0.0)).a * 0.4;
	float a_arr = texture(tex_albedo, UV - vec2(0.0, paso.y * 2.2)).a * 0.6 + texture(tex_albedo, UV - vec2(0.0, paso.y * 4.8)).a * 0.4;
	float a_aba = texture(tex_albedo, UV + vec2(0.0, paso.y * 2.2)).a * 0.6 + texture(tex_albedo, UV + vec2(0.0, paso.y * 4.8)).a * 0.4;
	float bisel_x = (a_der - a_izq) * -0.75;
	float bisel_y = (a_aba - a_arr) * 0.65;
	// Curvatura cilíndrica/cúpula 3D a lo ancho y alto del fotograma para dar cuerpo redondo a estructuras y jefes
	vec2 uv_f = fract(UV * hv_frames);
	float cilindro_x = (uv_f.x - 0.5) * 2.0 * volteo_x * curvatura_3d * 0.42;
	float cupula_y = (0.45 - uv_f.y) * curvatura_3d * 0.28;
	float interior = clamp((a_izq + a_der + a_arr + a_aba) * 0.25, 0.0, 1.0);
	float sombra_borde = mix(0.82, 1.0, smoothstep(0.15, 0.92, interior));
	ALBEDO = c.rgb * sombra_borde;
	ALPHA = c.a;
	ALPHA_SCISSOR_THRESHOLD = 0.5;
	ROUGHNESS = 1.0;
	vec3 nm = vec3(0.0, 0.0, 1.0);
	if (usa_normal > 0.5) {
		nm = texture(tex_normal, UV).rgb * 2.0 - 1.0;
	}
	float nx = nm.x * volteo_x * 0.65 + bisel_x * curvatura_3d + cilindro_x;
	float ny = 0.64 + nm.y * 0.62 + bisel_y * curvatura_3d + cupula_y;
	float nz = max(0.22, 0.72 * nm.z * (1.0 - min(0.45, length(vec2(bisel_x, bisel_y)) * 0.45)));
	NORMAL = normalize(vec3(nx, ny, nz));
}

void light() {
	if (LIGHT_IS_DIRECTIONAL) {
		float relieve = (dot(NORMAL, LIGHT) - 0.50) * (usa_normal > 0.5 ? 0.52 : 0.28);
		float sombra_3d = mix(0.68, 1.0, ATTENUATION);
		DIFFUSE_LIGHT += tinte_ambiente * sombra_3d * clamp(1.0 + relieve, 0.72, 1.26);
	} else {
		float ndl = max(0.28, dot(NORMAL, LIGHT));
		DIFFUSE_LIGHT += LIGHT_COLOR * ATTENUATION * ndl * 0.96;
	}
}
"""
## Flora que se mece con el viento y se aparta suavemente al paso de Maisha (amplitud en metros en la copa)
const FLORA_MECIDA := {
	"arbol_a.png": 0.045,
	"arbol_b.png": 0.045,
	"arbol_alto.png": 0.055,
	"arbol_cobre.png": 0.050,
	"arbol_rojizo.png": 0.050,
	"pino_nevado.png": 0.040,
	"sauce.png": 0.060,
	"matorral.png": 0.085,
	"helecho.png": 0.095,
	"juncos.png": 0.105,
	"junco.png": 0.105,
	"bayas.png": 0.080,
	"trigo.png": 0.110,
	"brote_vida.png": 0.075,
	"campanilla.png": 0.085,
	"espino.png": 0.055,
}
## Tabla de luces 3D por edificio y objeto luminoso (reutiliza Relieve.LUCES + edificios de Maandiko + setas y runas)
const LUCES_3D := {
	"casa_seta.png": [["v", 166, 90], ["v", 196, 96], ["f", 195, 112]],
	"taller.png": [["v", 217, 77], ["v", 238, 77], ["h", 174, 120], ["f", 242, 107]],
	"cocina.png": [["v", 195, 90], ["h", 149, 118]],
	"puesto.png": [["f", 143, 46], ["f", 174, 46], ["f", 203, 46]],
	"gran_arbol.png": [["v", 98, 122], ["v", 88, 186], ["f", 66, 158]],
	"campamento.png": [["f", 52, 28]],
	"palafito.png": [["f", 27, 51], ["v", 47, 52], ["v", 81, 53]],
	"madriguera.png": [["v", 29, 66], ["f", 59, 68], ["f", 85, 68]],
	"horreo.png": [["v", 58, 58]],
	"aprisco.png": [["v", 30, 92], ["f", 75, 85], ["f", 42, 82]],
	"casa_barcas.png": [["v", 55, 50], ["f", 113, 48]],
	"casa_bata.png": [["v", 52, 43], ["f", 10, 51]],
	"casa_juncos.png": [["v", 55, 43], ["v", 127, 43], ["f", 185, 37]],
	"casa_shamba.png": [["v", 40, 96], ["v", 124, 96], ["f", 90, 95], ["h", 152, 28]],
	"casa_granja.png": [["v", 40, 96], ["v", 124, 96], ["f", 90, 95], ["h", 152, 28]],
	"almacen.png": [["v", 52, 42]],
	"cubierta.png": [["f", 54, 34]],
	"farol.png": [["f", 4, 4]],
	"casa_escriba.png": [["v", 20, 48], ["v", 52, 48], ["v", 92, 48], ["v", 124, 48]],
	"casa_kalamu.png": [["v", 26, 65], ["v", 68, 65], ["f", 48, 72]],
	"gran_archivo.png": [["v", 52, 110], ["v", 140, 110], ["f", 96, 124]],
	"taller_taa.png": [["h", 34, 58], ["f", 58, 52]],
	"puesto_tinta.png": [["f", 28, 22], ["f", 84, 22]],
	"seta_luminosa.png": [["m", 12, 6]],
	"seta_luz.png": [["m", 16, 8], ["m", 48, 8]],
	"piedra_eco.png": [["m", 8, 10]],
	"eco.png": [["m", 13, 20]],
	"transbordador.png": [["f", 30, 24]],
	"estela.png": [["m", 33, 18]],
	"grua.png": [["f", 36, 68]],
	"portal.png": [["h", 48, 12]],
	"altar_corteza.png": [["h", 24, 18]],
	"brasero.png": [["f", 11, 8]],
	"maquina.png": [["f", 20, 12]],
	"raiz_gigante.png": [["h", 50, 15]],
	"molino.png": [["v", 48, 115]],
	"atril.png": [["f", 20, 12]],
	"puerta.png": [["m", 52, 44]],
}
const CAMBIAN_AL_RECONSTRUIRSE_3D := ["casa_seta.png", "taller.png", "cocina.png", "puesto.png"]
## Modelos 3D de Blender 4.5 para arquitectura y accesorios:
## Sustituyen al sprite plano por una malla 3D completa (.glb) con aleros, volumen sólido y sombras reales
const MODELOS_BLENDER := {
	"casa_granja.png": {
		"ruta": "res://modelos/entorno/casa_granja.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(4.5, 3.0),
		"solo_reconstruido": false,
	},
	"ruina_casa.png": {
		"ruta": "res://modelos/entorno/kitovu_ruina.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.15),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"casa_seta.png": {
		"ruta": "res://modelos/entorno/casa_pino.glb",
		"ruta_ruina": "res://modelos/entorno/casa_pino_ruina.glb",
		"escala": Vector3(1.12, 1.12, 1.12),
		"offset": Vector3(0.0, 0.0, -0.22),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.0, 2.5),
		"solo_reconstruido": false,
	},
	"taller.png": {
		"ruta": "res://modelos/entorno/forja_corteza.glb",
		"ruta_ruina": "res://modelos/entorno/forja_ruina.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.18),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.2, 2.5),
		"solo_reconstruido": false,
	},
	"gran_arbol.png": {
		"ruta": "res://modelos/entorno/gran_arbol.glb",
		"escala": Vector3(1.22, 1.22, 1.22),
		"offset": Vector3(0.0, 0.0, -0.30),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"pozo.png": {
		"ruta": "res://modelos/entorno/pozo_antiguo.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.10),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"espantapajaros.png": {
		"ruta": "res://modelos/entorno/espantapajaros.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"carro.png": {
		"ruta": "res://modelos/entorno/carro_madera.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.10),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"valla.png": {
		"ruta": "res://modelos/entorno/valla_madera.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"cerca.png": {
		"ruta": "res://modelos/entorno/valla_madera.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"farol.png": {
		"ruta": "res://modelos/entorno/farol_madera.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"farol_apagado.png": {
		"ruta": "res://modelos/entorno/farol_madera.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"cocina.png": {
		"ruta": "res://modelos/entorno/cocina_juncia.glb",
		"ruta_ruina": "res://modelos/entorno/cocina_ruina.glb",
		"escala": Vector3(1.08, 1.08, 1.08),
		"offset": Vector3(0.0, 0.0, -0.18),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.0, 2.2),
		"solo_reconstruido": false,
	},
	"puesto.png": {
		"ruta": "res://modelos/entorno/puesto_tawi.glb",
		"ruta_ruina": "res://modelos/entorno/puesto_ruina.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.12),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.8, 1.8),
		"solo_reconstruido": false,
	},
	"gran_archivo.png": {
		"ruta": "res://modelos/entorno/gran_archivo.glb",
		"escala": Vector3(1.15, 1.15, 1.15),
		"offset": Vector3(0.0, 0.0, -0.35),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(4.2, 3.5),
		"solo_reconstruido": false,
	},
	"taller_taa.png": {
		"ruta": "res://modelos/entorno/taller_taa.glb",
		"escala": Vector3(1.10, 1.10, 1.10),
		"offset": Vector3(0.0, 0.0, -0.20),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.5, 2.5),
		"solo_reconstruido": false,
	},
	"casa_escriba.png": {
		"ruta": "res://modelos/entorno/casa_escriba.glb",
		"escala": Vector3(1.06, 1.06, 1.06),
		"offset": Vector3(0.0, 0.0, -0.18),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.2, 2.2),
		"solo_reconstruido": false,
	},
	"casa_kalamu.png": {
		"ruta": "res://modelos/entorno/casa_kalamu.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.20),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(4.2, 3.2),
		"solo_reconstruido": false,
	},
	"fuente.png": {
		"ruta": "res://modelos/entorno/fuente_plaza.glb",
		"escala": Vector3(1.10, 1.10, 1.10),
		"offset": Vector3(0.0, 0.0, -0.15),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"fuente_plaza.png": {
		"ruta": "res://modelos/entorno/fuente_plaza.glb",
		"escala": Vector3(1.10, 1.10, 1.10),
		"offset": Vector3(0.0, 0.0, -0.15),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"casa_shamba.png": {
		"ruta": "res://modelos/entorno/casa_granja.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(4.5, 3.0),
		"solo_reconstruido": false,
	},
	"casa_juncos.png": {
		"ruta": "res://modelos/entorno/casa_juncos.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.15),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.0, 2.0),
		"solo_reconstruido": false,
	},
	"casa_barcas.png": {
		"ruta": "res://modelos/entorno/casa_barcas.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.20),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(4.2, 3.0),
		"solo_reconstruido": false,
	},
	"casa_bata.png": {
		"ruta": "res://modelos/entorno/casa_bata.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.15),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.8, 1.8),
		"solo_reconstruido": false,
	},
	"palafito.png": {
		"ruta": "res://modelos/entorno/palafito.glb",
		"escala": Vector3(1.08, 1.08, 1.08),
		"offset": Vector3(0.0, 0.0, -0.20),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.0, 2.0),
		"solo_reconstruido": false,
	},
	"casa_nungu.png": {
		"ruta": "res://modelos/entorno/casa_nungu.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.15),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.3, 2.2),
		"solo_reconstruido": false,
	},
	"granero.png": {
		"ruta": "res://modelos/entorno/granero.glb",
		"escala": Vector3(1.10, 1.10, 1.10),
		"offset": Vector3(0.0, 0.0, -0.25),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(3.5, 2.6),
		"solo_reconstruido": false,
	},
	"horreo.png": {
		"ruta": "res://modelos/entorno/horreo.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.15),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.2, 2.2),
		"solo_reconstruido": false,
	},
	"campamento.png": {
		"ruta": "res://modelos/entorno/campamento.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.15),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.4, 2.0),
		"solo_reconstruido": false,
	},
	"puesto_tinta.png": {
		"ruta": "res://modelos/entorno/puesto_tinta.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.12),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.0, 1.6),
		"solo_reconstruido": false,
	},
	"almacen.png": {
		"ruta": "res://modelos/entorno/almacen.glb",
		"escala": Vector3(1.08, 1.08, 1.08),
		"offset": Vector3(0.0, 0.0, -0.20),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(3.2, 2.4),
		"solo_reconstruido": false,
	},
	"aprisco.png": {
		"ruta": "res://modelos/entorno/aprisco.glb",
		"escala": Vector3(1.08, 1.08, 1.08),
		"offset": Vector3(0.0, 0.0, -0.20),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(3.4, 2.6),
		"solo_reconstruido": false,
	},
	"madriguera.png": {
		"ruta": "res://modelos/entorno/madriguera.glb",
		"escala": Vector3(1.06, 1.06, 1.06),
		"offset": Vector3(0.0, 0.0, -0.18),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.6, 2.4),
		"solo_reconstruido": false,
	},
	"torre.png": {
		"ruta": "res://modelos/entorno/torre.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.15),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.8, 1.8),
		"solo_reconstruido": false,
	},
	"monumento.png": {
		"ruta": "res://modelos/entorno/monumento.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.15),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.8, 1.8),
		"solo_reconstruido": false,
	},
	"altar.png": {
		"ruta": "res://modelos/entorno/altar.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.10),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"grua.png": {
		"ruta": "res://modelos/entorno/grua.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.15),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.0, 2.2),
		"solo_reconstruido": false,
	},
	"barca.png": {
		"ruta": "res://modelos/entorno/barca.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"barca_bata.png": {
		"ruta": "res://modelos/entorno/barca.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"estela.png": {
		"ruta": "res://modelos/entorno/estela.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.10),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.5, 1.5),
		"solo_reconstruido": false,
	},
	"menhir.png": {
		"ruta": "res://modelos/entorno/menhir.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.08),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.2, 1.2),
		"solo_reconstruido": false,
	},
	"portal.png": {
		"ruta": "res://modelos/entorno/portal_raiz.glb",
		"escala": Vector3(1.08, 1.08, 1.08),
		"offset": Vector3(0.0, 0.0, -0.25),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.5, 2.5),
		"solo_reconstruido": false,
	},
	"arco_ruinas.png": {
		"ruta": "res://modelos/entorno/arco_ruinas.glb",
		"escala": Vector3(1.10, 1.10, 1.10),
		"offset": Vector3(0.0, 0.0, -0.25),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.8, 2.5),
		"solo_reconstruido": false,
	},
	"altar_corteza.png": {
		"ruta": "res://modelos/entorno/altar_corteza.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.15),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.0, 2.0),
		"solo_reconstruido": false,
	},
	"balsa.png": {
		"ruta": "res://modelos/entorno/balsa.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"brasero.png": {
		"ruta": "res://modelos/entorno/brasero.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"maquina.png": {
		"ruta": "res://modelos/entorno/maquina_campo.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.15),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.2, 1.8),
		"solo_reconstruido": false,
	},
	"raiz_gigante.png": {
		"ruta": "res://modelos/entorno/raiz_gigante.glb",
		"escala": Vector3(1.08, 1.08, 1.08),
		"offset": Vector3(0.0, 0.0, -0.20),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(3.5, 2.0),
		"solo_reconstruido": false,
	},
	"columna.png": {
		"ruta": "res://modelos/entorno/columna.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.2, 1.2),
		"solo_reconstruido": false,
	},
	"muro.png": {
		"ruta": "res://modelos/entorno/muro.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.5, 1.2),
		"solo_reconstruido": false,
	},
	"paca.png": {
		"ruta": "res://modelos/entorno/paca.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"solo_reconstruido": false,
	},
	"molino.png": {
		"ruta": "res://modelos/entorno/molino_campo.glb",
		"escala": Vector3(1.10, 1.10, 1.10),
		"offset": Vector3(0.0, 0.0, -0.25),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(3.5, 2.5),
		"solo_reconstruido": false,
	},
	"atril.png": {
		"ruta": "res://modelos/entorno/atril_biblioteca.glb",
		"escala": Vector3(1.05, 1.05, 1.05),
		"offset": Vector3(0.0, 0.0, -0.10),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.8, 1.5),
		"solo_reconstruido": false,
	},
	"tocon.png": {
		"ruta": "res://modelos/entorno/tocon_bosque.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.5, 1.2),
		"solo_reconstruido": false,
	},
	"poste.png": {
		"ruta": "res://modelos/entorno/poste_amarre.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.2, 1.2),
		"solo_reconstruido": false,
	},
	"arbol_seco.png": {
		"ruta": "res://modelos/entorno/arbol_seco.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(0.8, 0.6),
		"solo_reconstruido": false,
	},
	"eco.png": {
		"ruta": "res://modelos/entorno/piedra_eco.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(0.9, 0.6),
		"solo_reconstruido": false,
	},
	"bloque.png": {
		"ruta": "res://modelos/entorno/bloque_piedra.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.2, 0.8),
		"solo_reconstruido": false,
	},
	"transbordador.png": {
		"ruta": "res://modelos/entorno/transbordador.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(4.5, 2.0),
		"solo_reconstruido": false,
	},
	"cubierta.png": {
		"ruta": "res://modelos/entorno/transbordador.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(4.5, 2.0),
		"solo_reconstruido": false,
	},
	"roca_grande.png": {
		"ruta": "res://modelos/entorno/roca_grande.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.1, 0.8),
		"solo_reconstruido": false,
	},
	"roca_pequena.png": {
		"ruta": "res://modelos/entorno/roca_pequena.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(0.7, 0.5),
		"solo_reconstruido": false,
	},
	"roca_nevada.png": {
		"ruta": "res://modelos/entorno/roca_grande.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.1, 0.8),
		"solo_reconstruido": false,
	},
	"arbol_muerto.png": {
		"ruta": "res://modelos/entorno/arbol_muerto.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(0.9, 0.7),
		"solo_reconstruido": false,
	},
	"seta_luz.png": {
		"ruta": "res://modelos/entorno/seta_luz.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(0.6, 0.5),
		"solo_reconstruido": false,
	},
	"cartel.png": {
		"ruta": "res://modelos/entorno/cartel_madera.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(0.6, 0.5),
		"solo_reconstruido": false,
	},
	"tronco.png": {
		"ruta": "res://modelos/entorno/tronco_caido.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.2, 0.7),
		"solo_reconstruido": false,
	},
	"tronco_podrido.png": {
		"ruta": "res://modelos/entorno/tronco_caido.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.2, 0.7),
		"solo_reconstruido": false,
	},
	"pino_nevado.png": {
		"ruta": "res://modelos/entorno/pino_nevado.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.0, 0.8),
		"solo_reconstruido": false,
	},
	"sauce.png": {
		"ruta": "res://modelos/entorno/sauce_pantano.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.2, 0.9),
		"solo_reconstruido": false,
	},
	"primer_arbol.png": {
		"ruta": "res://modelos/entorno/primer_arbol.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(4.5, 3.5),
		"solo_reconstruido": false,
	},
	"armario.png": {
		"ruta": "res://modelos/entorno/armario_nungu.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.10),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.8, 1.5),
		"solo_reconstruido": false,
	},
	"yunque.png": {
		"ruta": "res://modelos/entorno/yunque_forja.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(0.8, 0.6),
		"solo_reconstruido": false,
	},
	"escalera.png": {
		"ruta": "res://modelos/entorno/escalera_biblioteca.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(1.0, 0.0, -2.1875),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.2, 2.5),
		"solo_reconstruido": false,
	},
	"puerta.png": {
		"ruta": "res://modelos/entorno/puerta_sellada.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(3.5, 2.0),
		"solo_reconstruido": false,
	},
	"estatua.png": {
		"ruta": "res://modelos/entorno/estatua_olvidado.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(0.9, 0.7),
		"solo_reconstruido": false,
	},
	"derrumbe.png": {
		"ruta": "res://modelos/entorno/derrumbe_rocas.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.0, 0.8),
		"solo_reconstruido": false,
	},
	"raiz_tapon.png": {
		"ruta": "res://modelos/entorno/raiz_tapon.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.15),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.4, 1.8),
		"solo_reconstruido": false,
	},
	"nudo_giza.png": {
		"ruta": "res://modelos/entorno/nudo_corrupcion.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.4, 1.2),
		"solo_reconstruido": false,
	},
	"roca_mineral.png": {
		"ruta": "res://modelos/entorno/roca_mineral.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(0.8, 0.6),
		"solo_reconstruido": false,
	},
	"espino.png": {
		"ruta": "res://modelos/enemigos/espino_giza.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.0, 0.8),
		"solo_reconstruido": false,
	},
	"saco.png": {
		"ruta": "res://modelos/entorno/saco_mercancias.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(0.6, 0.6),
		"solo_reconstruido": false,
	},
	"sello_raices.png": {
		"ruta": "res://modelos/entorno/sello_raices.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.22),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(3.0, 2.0),
		"solo_reconstruido": false,
	},
	"crater.png": {
		"ruta": "res://modelos/entorno/crater_kitovu.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.8, 1.2),
		"solo_reconstruido": false,
	},
	"cortina.png": {
		"ruta": "res://modelos/entorno/cortina_micelio.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.10),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(2.5, 1.5),
		"solo_reconstruido": false,
	},
	"espinas.png": {
		"ruta": "res://modelos/entorno/espinas_giza.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(1.2, 1.0),
		"solo_reconstruido": false,
	},
	"raiz_dormida.png": {
		"ruta": "res://modelos/entorno/raiz_dormida.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(3.0, 1.5),
		"solo_reconstruido": false,
	},
	"semilla_dormida.png": {
		"ruta": "res://modelos/entorno/semilla_dormida.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, -0.05),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(0.8, 0.6),
		"solo_reconstruido": false,
	},
	"rescoldo.png": {
		"ruta": "res://modelos/entorno/rescoldo_giza.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(0.9, 0.7),
		"solo_reconstruido": false,
	},
	"chatarra.png": {
		"ruta": "res://modelos/entorno/chatarra_oxidada.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(0.8, 0.6),
		"solo_reconstruido": false,
	},
	"zanahoria.png": {
		"ruta": "res://modelos/entorno/zanahoria_huerto.glb",
		"escala": Vector3(1.0, 1.0, 1.0),
		"offset": Vector3(0.0, 0.0, 0.0),
		"rot_y": 0.0,
		"radio_occlusion": Vector2(0.5, 0.4),
		"solo_reconstruido": false,
	},
}
const TIPOS_LUZ_3D := {
	"v": [4.6, 0.92, Color(1.0, 0.84, 0.55), false],
	"f": [5.6, 1.12, Color(1.0, 0.78, 0.46), false],
	"h": [6.8, 1.35, Color(1.0, 0.64, 0.30), true],
	"m": [4.8, 0.88, Color(0.50, 0.92, 0.82), false],
}
const HONDO_AGUA := 0.28             # metros que baja la lámina de agua sobre el lecho hundido (-0.44m)
const LETRAS_AGUA := "~\\"
## Dibujos de pantalla (por su script): van a la capa de pantalla, con sus hijos
const DE_PANTALLA := ["ambiente.gd", "nevada.gd", "ventisca.gd", "luz_sol.gd"]
## Matiz cinematográfico por zona para el etalonaje HD-2D (conservando la luminancia central al sol)
const BIOMAS_HD2D := {
	"cuna_de_musgo": Color(1.02, 1.01, 0.96),
	"prados_del_eco": Color(1.01, 1.02, 0.97),
	"bosque_cobrizo": Color(1.06, 0.96, 0.88),
	"camino_cobrizo": Color(1.04, 0.97, 0.90),
	"campo_segado": Color(1.04, 0.98, 0.91),
	"cienaga_quieta": Color(0.91, 1.03, 0.96),
	"las_pasarelas": Color(0.94, 1.02, 0.97),
	"lago_espejo": Color(0.94, 0.99, 1.05),
	"gruta_raices": Color(0.88, 0.95, 1.08),
	"cueva_setas": Color(0.95, 0.92, 1.06),
	"sendero_olvidado": Color(0.94, 0.97, 1.05),
	"ruinas_primer_arbol": Color(0.93, 0.95, 1.06),
	"paso_escarcha": Color(0.96, 0.95, 1.05),
	"maandiko": Color(0.97, 0.96, 1.04),
	"estanterias_colgantes": Color(1.03, 0.96, 0.92),
}
const ZONAS_OTONO := ["bosque_cobrizo", "camino_cobrizo", "campo_segado"]
const ZONAS_ESPORAS := ["gruta_raices", "cueva_setas", "cienaga_quieta", "las_pasarelas"]
const NUM_MOTAS_3D := 40
const NUM_POLVO_3D := 10
const NUM_HUMO_3D := 24
const ZONAS_NIEVE := ["sendero_olvidado", "ruinas_primer_arbol", "paso_escarcha", "maandiko"]
## Postprocesado cinematográfico HD-2D:
##   1. Profundidad de campo Tilt-Shift (nítido en la banda de Maisha, desenfoque bokeh suave arriba y abajo).
##   2. Bloom cálido selectivo en luces, llamas, runas y ecos (ignora blancos neutros para no quemar nunca la nieve).
##   3. Etalonaje de color por hora del día y bioma + viñeta suave de maqueta.
const SOMBREADOR_POSTPROCESO := """
shader_type canvas_item;
uniform sampler2D pantalla : hint_screen_texture, filter_linear;
uniform int calidad = 2;
uniform float foco_y = 0.52;
uniform float dia = 1.0;
uniform float calidez = 0.0;
uniform vec3 tinte_bioma = vec3(1.0, 1.0, 1.0);
uniform float es_nieve = 0.0;

vec3 extraer_emision(vec3 s, float d, float nieve) {
	float lum = dot(s, vec3(0.299, 0.587, 0.114));
	float sat = max(s.r, max(s.g, s.b)) - min(s.r, min(s.g, s.b));
	float calido = max(0.0, s.r - s.b * 0.85);
	// En la nieve al sol, los píxeles blancos/lilas tienen baja saturación y poco exceso cálido: no emiten bloom
	float mascara_nieve = mix(1.0, smoothstep(0.18, 0.36, sat + calido * 0.8), nieve * d);
	float relevancia = lum * (0.32 + sat * 0.55 + calido * 0.45);
	float umbral = mix(0.56, 0.68, d) + nieve * d * 0.14;
	return s * smoothstep(umbral, umbral + 0.25, relevancia) * mascara_nieve;
}

void fragment() {
	vec2 uv = SCREEN_UV;
	vec3 base = texture(pantalla, uv).rgb;
	if (calidad <= 0) {
		COLOR = vec4(base, 1.0);
	} else {
		vec2 paso = vec2(1.0 / 640.0, 1.0 / 360.0);
		// 1. Tilt-Shift (efecto maqueta): banda central nítida alrededor de Maisha
		float dist_arriba = max(0.0, foco_y - uv.y);
		float dist_abajo = max(0.0, uv.y - foco_y);
		float desenfoque = smoothstep(0.17, 0.44, dist_arriba) * 1.15 + smoothstep(0.19, 0.45, dist_abajo) * 0.95;
		desenfoque = clamp(desenfoque, 0.0, 1.0);
		vec3 col = base;
		if (desenfoque > 0.01) {
			float r = desenfoque * (calidad >= 2 ? 2.1 : 1.25);
			vec3 acum = base * 1.4;
			float peso_t = 1.4;
			vec2 dirs[8] = vec2[8](
				vec2(-0.707, -0.707), vec2(0.707, -0.707),
				vec2(-0.707, 0.707), vec2(0.707, 0.707),
				vec2(0.0, -1.0), vec2(0.0, 1.0),
				vec2(-1.0, 0.0), vec2(1.0, 0.0)
			);
			int muestras = calidad >= 2 ? 8 : 4;
			for (int i = 0; i < muestras; i++) {
				float escala_r = (i < 4) ? r : r * 0.55;
				vec3 m = texture(pantalla, clamp(uv + dirs[i] * paso * escala_r, vec2(0.001), vec2(0.999))).rgb;
				float p = 1.0 + dot(m, vec3(0.299, 0.587, 0.114)) * 0.35;
				acum += m * p;
				peso_t += p;
			}
			col = mix(base, acum / peso_t, smoothstep(0.0, 0.15, desenfoque));
		}
		// 2. Bloom suave selectivo (llamas, faroles, ventanas, runas y ecos)
		vec3 bloom = extraer_emision(col, dia, es_nieve) * 0.16;
		vec2 pb = paso * 3.0;
		bloom += extraer_emision(texture(pantalla, clamp(uv + vec2(pb.x, 0.0), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.10;
		bloom += extraer_emision(texture(pantalla, clamp(uv - vec2(pb.x, 0.0), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.10;
		bloom += extraer_emision(texture(pantalla, clamp(uv + vec2(0.0, pb.y), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.10;
		bloom += extraer_emision(texture(pantalla, clamp(uv - vec2(0.0, pb.y), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.10;
		if (calidad >= 2) {
			vec2 pd = pb * 1.45;
			bloom += extraer_emision(texture(pantalla, clamp(uv + vec2(pd.x, pd.y), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.05;
			bloom += extraer_emision(texture(pantalla, clamp(uv + vec2(-pd.x, pd.y), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.05;
			bloom += extraer_emision(texture(pantalla, clamp(uv + vec2(pd.x, -pd.y), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.05;
			bloom += extraer_emision(texture(pantalla, clamp(uv + vec2(-pd.x, -pd.y), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.05;
		}
		float fuerza_bloom = mix(0.24, 0.15, dia);
		col += bloom * fuerza_bloom;
		// 3. Etalonaje de color por hora y bioma (preservando el brillo natural sin saturar)
		float noche = 1.0 - dia;
		vec3 sombra_tinte = mix(vec3(0.97, 0.98, 1.01), vec3(0.88, 0.91, 1.05), noche);
		vec3 luz_tinte = mix(vec3(1.0), vec3(1.04, 0.95, 0.86), calidez * 0.45);
		float lum_c = dot(col, vec3(0.299, 0.587, 0.114));
		col *= mix(sombra_tinte, luz_tinte, smoothstep(0.15, 0.75, lum_c));
		col *= mix(vec3(1.0), tinte_bioma, 0.35);
		// 4. Viñeta cinematográfica suave en los bordes
		vec2 d_centro = (uv - vec2(0.5, 0.5)) * vec2(1.12, 1.0);
		float vineta = 1.0 - smoothstep(0.46, 0.92, length(d_centro)) * mix(0.24, 0.14, dia);
		col *= vineta;
		COLOR = vec4(clamp(col, vec3(0.0), vec3(1.0)), 1.0);
	}
}
"""

var escena: Node2D
var region: Node2D
var camara: Camera3D
var sol: DirectionalLight3D
var _entorno: Environment
var _gemelos := {}                 # id del dibujo 2D -> [n, g, ancla, z, mod_base]
var _ids_dinamicos := {}           # id -> true
var _ids_estaticos := {}           # id -> true
var _ultimo_tinte := Color(-1, -1, -1, -1)
var _maisha: Node2D
var _foco := Vector3.ZERO
var _adelanto_camara := Vector3.ZERO
var _fotogramas_camara := 0
var _alto_pena := ALTO_PENA
var _mats_capa: Array[ShaderMaterial] = []
var _plano_agua: MeshInstance3D
var _plano_lecho: MeshInstance3D
var _mascara_agua: ImageTexture
var _mascara_ao: ImageTexture
var _suelos_lejanos: Array[ShaderMaterial] = []
var _mat_penas: StandardMaterial3D
var _tinte := Color.WHITE
var _canales := {}                 # id de cada dibujo -> [dibujo, su canal de antes] (para devolverlo al apagar)
var _capa_suelo: SubViewport
var _plano_capa: MeshInstance3D
var _capa_pantalla: SubViewport
var _ventanas: Array = []          # [SubViewport, Sprite3D] (se reparten entre los objetos de pie más cercanos)
var _de_pie := {}                  # id del objeto de pie (su cuerpo) -> el cuerpo
var _velo_pantalla: CanvasLayer
var _capa_post: CanvasLayer
var _mat_post: ShaderMaterial
var _id_escena := ""
var _tinte_bioma := Color.WHITE
var _es_nieve := 0.0
var _mascara_antes := 0xFFFFFFFF
var _tiempo_luces := 0.0
var _luces_3d: Array[Dictionary] = []      # {"luz": OmniLight3D, "pos": Vector3, "fuerza": float, "fuego": bool, "siempre": bool, "fase": float, "dueno": Node}
var _luces_pt2d := {}                      # id de PointLight2D -> [PointLight2D, OmniLight3D]
var _moduladores_2d: Array[CanvasModulate] = []
var _sh_gemelo: Shader
var _cache_mat_relieve := {}               # clave -> ShaderMaterial
var _malla_motas: MultiMeshInstance3D
var _motas_datos: Array[Dictionary] = []
var _malla_polvo: MultiMeshInstance3D
var _polvo_datos: Array[Dictionary] = []
var _reloj_polvo := 0.0
var _malla_humo: MultiMeshInstance3D
var _humo_datos: Array[Dictionary] = []
var _reloj_humo := 0.0
static var _cache_normales := {}           # ruta -> Texture2D
static var _escenas_blender_cache := {}     # ruta -> PackedScene
var _modelos_blender_instanciados := {}     # id de Node2D -> Node3D (instancia de Blender)


func _ready() -> void:
	region = escena.get_node_or_null("Region")
	_maisha = escena.get_tree().get_first_node_in_group("maisha") as Node2D
	_id_escena = escena.scene_file_path.get_file().get_basename()
	_tinte_bioma = BIOMAS_HD2D.get(_id_escena, Color.WHITE)
	_es_nieve = 1.0 if _id_escena in ZONAS_NIEVE else 0.0
	_sh_gemelo = Shader.new()
	_sh_gemelo.code = SOMBREADOR_GEMELO
	_crear_ambiente()
	_crear_suelo()
	_crear_camara()
	_crear_capas()
	_crear_particulas_3d()
	_crear_postproceso()
	for n in _todos(escena):
		_registrar(n)
	_hornear_ao_suelo()
	# la raíz de la escena, en los canales de las dos capas (si no, se llevaría por delante a todos sus hijos)
	_canales[escena.get_instance_id()] = [escena, escena.visibility_layer]
	escena.visibility_layer = escena.visibility_layer | CANAL_SUELO | CANAL_PANTALLA | CANAL_PIE
	escena.get_tree().node_added.connect(_registrar)
	escena.get_tree().node_removed.connect(_quitar)


func _todos(nodo: Node) -> Array:
	var lista := [nodo]
	for h in nodo.get_children():
		lista.append_array(_todos(h))
	return lista


# --- El ambiente: sol, cielo, niebla -------------------------------------------------------------------------

func _crear_ambiente() -> void:
	_entorno = Environment.new()
	_entorno.background_mode = Environment.BG_COLOR
	_entorno.background_color = RenderingServer.get_default_clear_color()
	_entorno.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	_entorno.ambient_light_color = Color(1, 1, 1)
	_entorno.ambient_light_energy = 0.4     # (medido: con esto y el sol, el suelo al sol sale igual de claro que en 2D)
	_entorno.tonemap_mode = Environment.TONE_MAPPER_LINEAR      # (los colores del pixel art, tal cual)
	_entorno.fog_enabled = false        # (la niebla aclaraba los oscuros: la del juego ya la pinta la capa de pantalla)
	_entorno.glow_enabled = false
	var mundo := WorldEnvironment.new()
	mundo.environment = _entorno
	add_child(mundo)
	sol = DirectionalLight3D.new()
	sol.shadow_enabled = true
	sol.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_2_SPLITS
	sol.directional_shadow_blend_splits = true
	sol.shadow_blur = 1.65
	sol.shadow_opacity = 0.78
	sol.light_energy = 0.27
	sol.light_color = Color(1.0, 0.95, 0.86)
	sol.rotation_degrees = Vector3(-50, -35, 0)          # (desde arriba a la izquierda y algo por detrás: sombras hacia delante y a la derecha, como las pintadas)
	sol.directional_shadow_max_distance = 86.0
	add_child(sol)


# --- El suelo y las peñas -------------------------------------------------------------------------------------

func _textura_suelo() -> Texture2D:
	var mundo := String(region.get("mundo")) if region and region.get("mundo") else "raiz"
	var ruta := "res://arte/mundos/%s/suelos/%s_suelo.png" % [mundo, String(region.get("mapa"))]
	return load(ruta) if region and ResourceLoader.exists(ruta) else null


func _crear_suelo() -> void:
	if region == null:
		return
	var tex := _textura_suelo()
	_alto_pena = ALTO_PENA * (2.0 if String(region.get("mapa")) in PARED_DOBLE else 1.0)
	var filas: PackedStringArray = region.get("_filas")
	var ancho: float = filas[0].length()
	var alto: float = filas.size()
	_mat_penas = StandardMaterial3D.new()
	_mat_penas.albedo_texture = tex
	_mat_penas.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	_mat_penas.vertex_color_use_as_albedo = true
	_mat_penas.roughness = 0.95
	# el suelo: una sola malla del tamaño del mapa con el suelo pintado (con el agujero del agua) y, debajo, el agua
	var plano := PlaneMesh.new()
	plano.size = Vector2(ancho, alto)
	plano.subdivide_width = clampi(int(ancho), 24, 56)
	plano.subdivide_depth = clampi(int(alto), 24, 56)
	var lejano := Shader.new()
	lejano.code = SOMBREADOR_LEJANO
	var shader_agua := Shader.new()
	shader_agua.code = SOMBREADOR_AGUA
	_suelos_lejanos.clear()
	for hundido in [0.0, 1.0, 2.0]:
		var m := ShaderMaterial.new()
		m.shader = shader_agua if is_equal_approx(hundido, 1.0) else lejano
		m.set_shader_parameter("suelo", tex)
		m.set_shader_parameter("casillas", Vector2(ancho, alto))
		if not is_equal_approx(hundido, 1.0):
			m.set_shader_parameter("hundido", hundido)
		_suelos_lejanos.append(m)
		var suelo := MeshInstance3D.new()
		suelo.mesh = plano
		suelo.material_override = m
		var pos_y := 0.0
		if hundido > 1.5:
			pos_y = -HONDO_AGUA - 0.06
			suelo.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		elif hundido > 0.5:
			pos_y = -HONDO_AGUA
			suelo.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		suelo.position = Vector3(ancho / 2.0, pos_y, alto / 2.0)
		add_child(suelo)
	# el agua: una máscara (1 píxel por casilla) para hundirla (la orilla la dibujan los sombreadores, curva y con su
	# sombra)
	var img := Image.create(int(ancho), int(alto), false, Image.FORMAT_L8)
	for y in filas.size():
		for x in filas[y].length():
			if not LETRAS_AGUA.contains(filas[y][x]):
				continue
			img.set_pixel(x, y, Color.WHITE)
	_mascara_agua = ImageTexture.create_from_image(img)
	for m in _suelos_lejanos:
		m.set_shader_parameter("agua", _mascara_agua)
	# las peñas: bloques que se levantan, con el suelo pintado encima y los lados de roca oscura
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var lados := SurfaceTool.new()
	lados.begin(Mesh.PRIMITIVE_TRIANGLES)
	for y in filas.size():
		var x := 0
		var fila := filas[y]
		while x < fila.length():
			if fila[x] != "0":
				x += 1
				continue
			var x0 := x
			while x < fila.length() and fila[x] == "0":
				x += 1
			_bloque(st, lados, x0, x, y, ancho, alto, filas)
	var techo := MeshInstance3D.new()
	techo.mesh = st.commit()
	techo.material_override = _mat_penas
	add_child(techo)
	# las paredes: la del sur, con la pared de roca que ya está pintada en el suelo; las demás, de roca oscura
	var paredes := MeshInstance3D.new()
	paredes.mesh = lados.commit()
	paredes.material_override = _mat_penas
	add_child(paredes)


## Hornea un mapa de oclusión ambiental (AO) de contacto en la base de las peñas, árboles, rocas y edificios
func _hornear_ao_suelo() -> void:
	if region == null:
		return
	var filas: PackedStringArray = region.get("_filas")
	var w := filas[0].length() * 2
	var h := filas.size() * 2
	var img_ao := Image.create(w, h, false, Image.FORMAT_L8)
	# 1. Oclusión suave al pie de las paredes de peña («0»)
	for y in filas.size():
		var fila := filas[y]
		for x in fila.length():
			if fila[x] == "0":
				continue
			var junto_pena := false
			if y > 0 and filas[y - 1][x] == "0":
				junto_pena = true
			elif y + 1 < filas.size() and filas[y + 1][x] == "0":
				junto_pena = true
			elif x > 0 and fila[x - 1] == "0":
				junto_pena = true
			elif x + 1 < fila.length() and fila[x + 1] == "0":
				junto_pena = true
			if junto_pena:
				for dy in 2:
					for dx in 2:
						img_ao.set_pixel(x * 2 + dx, y * 2 + dy, Color(0.58, 0.58, 0.58, 1.0))
	# 2. Oclusión ambiental de contacto bajo edificios, árboles y rocas estáticas
	for par in _gemelos.values():
		var n: Node2D = par[0]
		var g: Sprite3D = par[1]
		var ancla: Node2D = par[2]
		if not is_instance_valid(n) or not is_instance_valid(ancla) or not (ancla is StaticBody2D):
			continue
		var tex: Texture2D = g.texture
		if tex == null:
			continue
		var ancho_px := (g.region_rect.size.x if g.region_enabled else tex.get_width() / float(maxi(g.hframes, 1)))
		var alto_px := (g.region_rect.size.y if g.region_enabled else tex.get_height() / float(maxi(g.vframes, 1)))
		if alto_px <= 14.0:
			continue
		var cx := int(roundf(ancla.global_position.x / 8.0))
		var cy := int(roundf(ancla.global_position.y / 8.0))
		var rx := clampi(int(roundf(ancho_px / 22.0)), 1, 9)
		var ry := clampi(int(roundf(ancho_px / 48.0)), 1, 3)
		for dy in range(-ry, ry + 1):
			var py := cy + dy
			if py < 0 or py >= h:
				continue
			for dx in range(-rx, rx + 1):
				var px := cx + dx
				if px < 0 or px >= w:
					continue
				var d2 := float(dx * dx) / float(maxi(1, rx * rx)) + float(dy * dy) / float(maxi(1, ry * ry))
				if d2 <= 1.0:
					var f := (1.0 - d2) * 0.68
					var prev := img_ao.get_pixel(px, py).r
					if f > prev:
						img_ao.set_pixel(px, py, Color(f, f, f, 1.0))
	_mascara_ao = ImageTexture.create_from_image(img_ao)
	for mat in _mats_capa:
		mat.set_shader_parameter("mapa_ao", _mascara_ao)
	for mat in _suelos_lejanos:
		mat.set_shader_parameter("mapa_ao", _mascara_ao)


## Un tramo de peña de x0 a x1 (casillas) en la fila y: techo con biseles suaves en las aristas y oclusión en el pie
func _bloque(st: SurfaceTool, lados: SurfaceTool, x0: int, x1: int, y: int, ancho: float, alto: float, filas: PackedStringArray) -> void:
	# En el dibujo 2D (vista 3/4) la peña ya está pintada como se vería: su pared del sur ocupa una franja de
	# «h» casillas dentro de la peña, y lo de encima está corrido hacia el norte esa misma altura.
	var h := _alto_pena
	var bh := h * 0.16
	var y_base := -0.10
	var c_techo := Color.WHITE
	var c_bisel := Color(1.05, 1.04, 1.02)
	var c_pared_sup := Color(0.95, 0.95, 0.97)
	var c_pared_pie := Color(0.58, 0.58, 0.64)
	var uv := func(px: float, pz: float) -> Vector2: return Vector2(px / ancho, clampf(pz, 0.0, alto) / alto)
	_cuad(st, Vector3(x0, h, y), Vector3(x1, h, y), Vector3(x1, h, y + 1), Vector3(x0, h, y + 1),
		uv.call(x0, y - h), uv.call(x1, y - h), uv.call(x1, y + 1 - h), uv.call(x0, y + 1 - h), c_techo, c_techo)
	for x in range(x0, x1):
		if y + 1 >= filas.size() or filas[y + 1][x] != "0":
			# Bisel superior sur + pared sur con oclusión en el pie
			_cuad(lados, Vector3(x, h, y + 0.88), Vector3(x + 1, h, y + 0.88), Vector3(x + 1, h - bh, y + 1), Vector3(x, h - bh, y + 1),
				uv.call(x, y + 0.88 - h), uv.call(x + 1, y + 0.88 - h), uv.call(x + 1, y + 1 - h + bh), uv.call(x, y + 1 - h + bh), c_bisel, c_pared_sup)
			_cuad(lados, Vector3(x, h - bh, y + 1), Vector3(x + 1, h - bh, y + 1), Vector3(x + 1, y_base, y + 1), Vector3(x, y_base, y + 1),
				uv.call(x, y + 1 - h + bh), uv.call(x + 1, y + 1 - h + bh), uv.call(x + 1, y + 1), uv.call(x, y + 1), c_pared_sup, c_pared_pie)
		if y == 0 or filas[y - 1][x] != "0":
			_cuad(lados, Vector3(x + 1, h, y), Vector3(x, h, y), Vector3(x, y_base, y), Vector3(x + 1, y_base, y),
				uv.call(x + 1, y - h), uv.call(x, y - h), uv.call(x, y), uv.call(x + 1, y), c_pared_sup, c_pared_pie)
	# los lados este y oeste: con sombreado de pie
	if x0 > 0:
		_cuad(lados, Vector3(x0, h, y), Vector3(x0, h, y + 1), Vector3(x0, y_base, y + 1), Vector3(x0, y_base, y),
			uv.call(x0, y + 1 - h), uv.call(x0 + 1, y + 1 - h), uv.call(x0 + 1, y + 1), uv.call(x0, y + 1), c_pared_sup, c_pared_pie)
	if x1 < filas[y].length():
		_cuad(lados, Vector3(x1, h, y + 1), Vector3(x1, h, y), Vector3(x1, y_base, y), Vector3(x1, y_base, y + 1),
			uv.call(x1 - 1, y + 1 - h), uv.call(x1, y + 1 - h), uv.call(x1, y + 1), uv.call(x1 - 1, y + 1), c_pared_sup, c_pared_pie)


func _cuad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, ua := Vector2.ZERO, ub := Vector2.ZERO, uc := Vector2.ZERO, ud := Vector2.ZERO, col_arriba := Color.WHITE, col_abajo := Color.WHITE) -> void:
	var n := (b - a).cross(c - a).normalized() * -1.0
	for p in [[a, ua, col_arriba], [b, ub, col_arriba], [c, uc, col_abajo], [a, ua, col_arriba], [c, uc, col_abajo], [d, ud, col_abajo]]:
		st.set_normal(n)
		st.set_color(p[2])
		st.set_uv(p[1])
		st.add_vertex(p[0])


# --- Las capas de lo que se dibuja con código -----------------------------------------------------------------

func _crear_capas() -> void:
	var vista := escena.get_viewport()
	# la capa de suelo: mira la escena 2D alrededor de Maisha y se tumba sobre el suelo
	_capa_suelo = SubViewport.new()
	_capa_suelo.size = Vector2i(LADO_CAPA, LADO_CAPA)
	_capa_suelo.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	_capa_suelo.world_2d = vista.world_2d
	_capa_suelo.canvas_cull_mask = CANAL_SUELO
	_capa_suelo.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	add_child(_capa_suelo)
	# (el suelo cercano ES esta capa: el suelo pintado, con el gris de Giza donde lo hay, y todo lo que se dibuja
	# encima; con luz, para que reciba las sombras de verdad)
	var sombreador := Shader.new()
	sombreador.code = SOMBREADOR_CAPA
	var plano := PlaneMesh.new()
	plano.size = Vector2(LADO_CAPA * PX, LADO_CAPA * PX)
	plano.subdivide_width = 36
	plano.subdivide_depth = 36
	var mat := ShaderMaterial.new()
	mat.shader = sombreador
	mat.set_shader_parameter("capa", _capa_suelo.get_texture())
	mat.set_shader_parameter("agua", _mascara_agua)
	mat.set_shader_parameter("casillas", Vector2(_mascara_agua.get_width(), _mascara_agua.get_height()) if _mascara_agua else Vector2.ONE)
	mat.set_shader_parameter("lado", float(LADO_CAPA))
	mat.render_priority = 1
	_mats_capa.append(mat)
	var p := MeshInstance3D.new()
	p.mesh = plano
	p.material_override = mat
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(p)
	_plano_capa = p
	# la capa de pantalla: lo mismo que verían los ojos en 2D, delante del 3D (y detrás de la interfaz)
	_capa_pantalla = SubViewport.new()
	_capa_pantalla.size = vista.get_visible_rect().size
	_capa_pantalla.transparent_bg = true
	_capa_pantalla.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	_capa_pantalla.world_2d = vista.world_2d
	_capa_pantalla.canvas_cull_mask = CANAL_PANTALLA
	_capa_pantalla.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	add_child(_capa_pantalla)
	_velo_pantalla = CanvasLayer.new()
	_velo_pantalla.layer = 5
	var cuadro := TextureRect.new()
	cuadro.texture = _capa_pantalla.get_texture()
	cuadro.set_anchors_preset(Control.PRESET_FULL_RECT)
	cuadro.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cuadro.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_velo_pantalla.add_child(cuadro)
	add_child(_velo_pantalla)
	# las ventanitas de lo que va de pie
	for i in VENTANAS:
		var v := SubViewport.new()
		v.size = VENTANA
		v.transparent_bg = true
		v.world_2d = vista.world_2d
		v.canvas_cull_mask = CANAL_PIE
		v.render_target_update_mode = SubViewport.UPDATE_DISABLED
		v.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
		add_child(v)
		var g := Sprite3D.new()
		g.texture = v.get_texture()
		g.pixel_size = PX
		g.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
		g.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
		g.shaded = false
		g.alpha_cut = SpriteBase3D.ALPHA_CUT_DISABLED
		g.transparent = true
		g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		g.offset = Vector2(VENTANA.x / 2.0 - VENTANA_PIE.x, VENTANA_PIE.y - VENTANA.y / 2.0)
		g.visible = false
		add_child(g)
		_ventanas.append([v, g])
	# la pantalla principal deja de pintar el mundo 2D (sigue vivo y viéndose en las capas); la interfaz, sí
	_mascara_antes = vista.canvas_cull_mask
	vista.canvas_cull_mask = _mascara_antes & ~CANALES_MUNDO


func _crear_particulas_3d() -> void:
	# 1. Motas ambientales 3D con profundidad real (polen dorado, luciérnagas, esporas, hojas cobrizas o copos 3D)
	var mat_m := StandardMaterial3D.new()
	mat_m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat_m.vertex_color_use_as_albedo = true
	mat_m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat_m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	mat_m.billboard_keep_scale = true
	var quad_m := QuadMesh.new()
	var es_hoja := _id_escena in ZONAS_OTONO
	quad_m.size = Vector2(2.2 * PX, 1.5 * PX) if es_hoja else Vector2(1.4 * PX, 1.4 * PX)
	quad_m.material = mat_m
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	mm.mesh = quad_m
	mm.instance_count = NUM_MOTAS_3D
	_malla_motas = MultiMeshInstance3D.new()
	_malla_motas.multimesh = mm
	_malla_motas.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_malla_motas)
	_motas_datos.clear()
	for i in NUM_MOTAS_3D:
		var ox := randf_range(-13.5, 13.5)
		var oz := randf_range(-9.5, 9.5)
		var oy := randf_range(0.35, 3.4)
		_motas_datos.append({
			"ox": ox,
			"oz": oz,
			"oy": oy,
			"vx": randf_range(-0.35, 0.55) if not es_hoja else randf_range(0.35, 0.95),
			"vy": randf_range(-0.55, -0.22) if (_es_nieve > 0.5 or es_hoja) else randf_range(-0.08, 0.14),
			"vz": randf_range(-0.25, 0.35),
			"fase": randf() * TAU,
			"escala": randf_range(0.75, 1.30),
		})
	# 2. Motas de polvo 3D tras los pies de Maisha al correr
	var mat_p := StandardMaterial3D.new()
	mat_p.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat_p.vertex_color_use_as_albedo = true
	mat_p.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat_p.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	mat_p.billboard_keep_scale = true
	var quad_p := QuadMesh.new()
	quad_p.size = Vector2(1.5 * PX, 1.5 * PX)
	quad_p.material = mat_p
	var mm_p := MultiMesh.new()
	mm_p.transform_format = MultiMesh.TRANSFORM_3D
	mm_p.use_colors = true
	mm_p.mesh = quad_p
	mm_p.instance_count = NUM_POLVO_3D
	_malla_polvo = MultiMeshInstance3D.new()
	_malla_polvo.multimesh = mm_p
	_malla_polvo.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_malla_polvo)
	_polvo_datos.clear()
	for i in NUM_POLVO_3D:
		_polvo_datos.append({
			"pos": Vector3(0.0, -10.0, 0.0),
			"vel": Vector3.ZERO,
			"vida": 0.0,
			"max_vida": 0.45,
		})
		mm_p.set_instance_transform(i, Transform3D(Basis(), Vector3(0.0, -10.0, 0.0)))
		mm_p.set_instance_color(i, Color(1, 1, 1, 0))
	# 3. Humo y brasas 3D de chimeneas, calderos y fogatas
	var mat_h := StandardMaterial3D.new()
	mat_h.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat_h.vertex_color_use_as_albedo = true
	mat_h.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat_h.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	mat_h.billboard_keep_scale = true
	var quad_h := QuadMesh.new()
	quad_h.size = Vector2(2.4 * PX, 2.4 * PX)
	quad_h.material = mat_h
	var mm_h := MultiMesh.new()
	mm_h.transform_format = MultiMesh.TRANSFORM_3D
	mm_h.use_colors = true
	mm_h.mesh = quad_h
	mm_h.instance_count = NUM_HUMO_3D
	_malla_humo = MultiMeshInstance3D.new()
	_malla_humo.multimesh = mm_h
	_malla_humo.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_malla_humo)
	_humo_datos.clear()
	for i in NUM_HUMO_3D:
		_humo_datos.append({
			"pos": Vector3(0.0, -20.0, 0.0),
			"vel": Vector3.ZERO,
			"vida": 0.0,
			"max_vida": 1.8,
			"es_chispa": false,
		})
		mm_h.set_instance_transform(i, Transform3D(Basis(), Vector3(0.0, -20.0, 0.0)))
		mm_h.set_instance_color(i, Color(1, 1, 1, 0))


func _actualizar_particulas_3d(delta: float, dia: float, en_penumbra: bool) -> void:
	if _malla_motas and _malla_motas.multimesh:
		var mm := _malla_motas.multimesh
		var es_hoja := _id_escena in ZONAS_OTONO
		var es_espora := _id_escena in ZONAS_ESPORAS
		var noche := 1.0 if en_penumbra else (1.0 - dia)
		var col_base := Color(1.0, 0.94, 0.68, 0.62)
		if _es_nieve > 0.5:
			col_base = Color(0.92, 0.96, 1.0, 0.72)
		elif es_hoja:
			col_base = Color(0.92, 0.52, 0.24, 0.78)
		elif es_espora:
			col_base = Color(0.52, 0.96, 0.84, 0.68)
		elif noche > 0.45:
			col_base = Color(0.76, 0.98, 0.46, 0.76)      # luciérnagas cálidas de noche
		for i in NUM_MOTAS_3D:
			var d: Dictionary = _motas_datos[i]
			var ox := float(d["ox"]) + float(d["vx"]) * delta + sin(_tiempo_luces * 1.4 + float(d["fase"])) * 0.18 * delta
			var oy := float(d["oy"]) + float(d["vy"]) * delta + cos(_tiempo_luces * 1.8 + float(d["fase"])) * 0.12 * delta
			var oz := float(d["oz"]) + float(d["vz"]) * delta
			if ox > 13.5:
				ox -= 27.0
			elif ox < -13.5:
				ox += 27.0
			if oz > 9.5:
				oz -= 19.0
			elif oz < -9.5:
				oz += 19.0
			if oy < 0.22:
				oy = 3.35
			elif oy > 3.45:
				oy = 0.28
			d["ox"] = ox
			d["oy"] = oy
			d["oz"] = oz
			var pos_m := Vector3(_foco.x + ox, oy, _foco.z + oz)
			var pulso := 0.55 + 0.45 * sin(_tiempo_luces * (3.2 if noche > 0.45 else 1.9) + float(d["fase"]))
			var esc := float(d["escala"]) * (0.75 + 0.35 * pulso)
			mm.set_instance_transform(i, Transform3D(Basis().scaled(Vector3(esc, esc, esc)), pos_m))
			mm.set_instance_color(i, Color(col_base.r, col_base.g, col_base.b, col_base.a * pulso))
	if _malla_polvo and _malla_polvo.multimesh:
		var mm_p := _malla_polvo.multimesh
		_reloj_polvo -= delta
		if _maisha and is_instance_valid(_maisha) and _maisha is CharacterBody2D:
			var vel_m := (_maisha as CharacterBody2D).velocity
			if vel_m.length() > 42.0 and _reloj_polvo <= 0.0:
				_reloj_polvo = 0.085
				for i in NUM_POLVO_3D:
					if float(_polvo_datos[i]["vida"]) <= 0.0:
						var base_m := _al_suelo(_maisha.global_position)
						var atras_m := -vel_m.normalized() * PX * 3.0
						_polvo_datos[i]["pos"] = base_m + Vector3(atras_m.x + randf_range(-0.14, 0.14), 0.12, atras_m.y + randf_range(-0.10, 0.16))
						_polvo_datos[i]["vel"] = Vector3(randf_range(-0.22, 0.22), randf_range(0.32, 0.58), randf_range(-0.18, 0.18))
						_polvo_datos[i]["vida"] = 0.42
						_polvo_datos[i]["max_vida"] = 0.42
						break
		var col_polvo := Color(0.88, 0.92, 0.98) if _es_nieve > 0.5 else Color(0.82, 0.74, 0.60) * _tinte
		for i in NUM_POLVO_3D:
			var dp: Dictionary = _polvo_datos[i]
			var vida := float(dp["vida"])
			if vida <= 0.0:
				continue
			vida -= delta
			dp["vida"] = vida
			if vida <= 0.0:
				mm_p.set_instance_color(i, Color(1, 1, 1, 0))
				continue
			var pos_p: Vector3 = dp["pos"] + dp["vel"] * delta
			dp["pos"] = pos_p
			var r_vida := clampf(vida / float(dp["max_vida"]), 0.0, 1.0)
			var esc_p := lerpf(1.35, 0.55, r_vida)
			mm_p.set_instance_transform(i, Transform3D(Basis().scaled(Vector3(esc_p, esc_p, esc_p)), pos_p))
			mm_p.set_instance_color(i, Color(col_polvo.r, col_polvo.g, col_polvo.b, r_vida * 0.58))
	if _malla_humo and _malla_humo.multimesh:
		var mm_h := _malla_humo.multimesh
		_reloj_humo -= delta
		if _reloj_humo <= 0.0:
			_reloj_humo = randf_range(0.14, 0.32)
			var emisores: Array[Vector3] = []
			for dl in _luces_3d:
				if bool(dl.get("fuego", false)):
					var omni_l: OmniLight3D = dl["luz"]
					if is_instance_valid(omni_l) and omni_l.visible:
						emisores.append(dl["pos"])
			if not emisores.is_empty():
				var p_emis: Vector3 = emisores[randi() % emisores.size()]
				for i in NUM_HUMO_3D:
					if float(_humo_datos[i]["vida"]) <= 0.0:
						var es_chispa := randf() < 0.22
						var dura := randf_range(0.6, 1.1) if es_chispa else randf_range(1.6, 2.4)
						_humo_datos[i]["pos"] = p_emis + Vector3(randf_range(-0.12, 0.12), randf_range(0.2, 0.4), randf_range(-0.12, 0.12))
						_humo_datos[i]["vel"] = Vector3(randf_range(0.08, 0.24), randf_range(0.75, 1.25) if es_chispa else randf_range(0.35, 0.65), randf_range(-0.08, 0.08))
						_humo_datos[i]["vida"] = dura
						_humo_datos[i]["max_vida"] = dura
						_humo_datos[i]["es_chispa"] = es_chispa
						break
		for i in NUM_HUMO_3D:
			var dh: Dictionary = _humo_datos[i]
			var vida := float(dh["vida"])
			if vida <= 0.0:
				continue
			vida -= delta
			dh["vida"] = vida
			if vida <= 0.0:
				mm_h.set_instance_color(i, Color(1, 1, 1, 0))
				continue
			var pos_h: Vector3 = dh["pos"] + dh["vel"] * delta
			pos_h.x += sin(vida * 3.0 + i) * 0.08 * delta
			dh["pos"] = pos_h
			var max_v := float(dh["max_vida"])
			var r_vida := clampf(vida / max_v, 0.0, 1.0)
			var es_chispa: bool = dh["es_chispa"]
			if es_chispa:
				var esc_c := lerpf(0.5, 0.9, r_vida)
				mm_h.set_instance_transform(i, Transform3D(Basis().scaled(Vector3(esc_c, esc_c, esc_c)), pos_h))
				mm_h.set_instance_color(i, Color(1.0, 0.68, 0.28, r_vida * 0.95))
			else:
				var esc_h := lerpf(2.2, 0.8, 1.0 - r_vida)
				var alfa_h := sin(r_vida * PI) * 0.38
				mm_h.set_instance_transform(i, Transform3D(Basis().scaled(Vector3(esc_h, esc_h, esc_h)), pos_h))
				mm_h.set_instance_color(i, Color(0.72, 0.74, 0.76, alfa_h))


func _crear_postproceso() -> void:
	_capa_post = CanvasLayer.new()
	_capa_post.layer = 4
	var rect := ColorRect.new()
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sh := Shader.new()
	sh.code = SOMBREADOR_POSTPROCESO
	_mat_post = ShaderMaterial.new()
	_mat_post.shader = sh
	_mat_post.set_shader_parameter("tinte_bioma", Vector3(_tinte_bioma.r, _tinte_bioma.g, _tinte_bioma.b))
	_mat_post.set_shader_parameter("es_nieve", _es_nieve)
	rect.material = _mat_post
	_capa_post.add_child(rect)
	add_child(_capa_post)


func _actualizar_postproceso(dia: float, calido: float) -> void:
	if _mat_post == null:
		return
	var cal_str := String(Estado.extra.get("calidad_hd2d", "alta"))
	var nivel_cal := 2 if cal_str == "alta" else (1 if cal_str == "media" else 0)
	_mat_post.set_shader_parameter("calidad", nivel_cal)
	_capa_post.visible = nivel_cal > 0
	if nivel_cal <= 0:
		return
	_mat_post.set_shader_parameter("dia", dia)
	_mat_post.set_shader_parameter("calidez", calido)
	var fy := 0.52
	if _maisha and is_instance_valid(_maisha) and camara:
		var pos_m := _al_suelo(_maisha.global_position) + Vector3(0.0, 0.8, 0.0)
		if not camara.is_position_behind(pos_m):
			fy = clampf(camara.unproject_position(pos_m).y / 360.0, 0.28, 0.72)
	_mat_post.set_shader_parameter("foco_y", fy)


func _mover_capas() -> void:
	# la capa de suelo, centrada en el foco (a píxeles enteros, para que no tiemble)
	var centro := Vector2(roundf(_foco.x / PX), roundf(_foco.z / PX))
	_capa_suelo.canvas_transform = Transform2D(0.0, -(centro - Vector2(LADO_CAPA, LADO_CAPA) / 2.0))
	_plano_capa.position = Vector3(centro.x * PX, 0.012, centro.y * PX)
	if _plano_agua:
		_plano_agua.position = Vector3(centro.x * PX, -HONDO_AGUA, centro.y * PX)
	if _plano_lecho:
		_plano_lecho.position = Vector3(centro.x * PX, -HONDO_AGUA - 0.06, centro.y * PX)
	for mat in _mats_capa:
		mat.set_shader_parameter("origen", centro - Vector2(LADO_CAPA, LADO_CAPA) / 2.0)
	_capa_pantalla.canvas_transform = escena.get_viewport().canvas_transform
	# las ventanitas: para los objetos de pie más cercanos a la cámara, cada una mirando su trocito de la escena
	var cerca := []
	for id in _de_pie.keys():
		var c_var: Variant = _de_pie[id]
		if not is_instance_valid(c_var):
			_de_pie.erase(id)
			continue
		var c := c_var as Node2D
		var d := _al_suelo(c.global_position).distance_to(_foco)
		if d < LEJOS * 0.7:
			cerca.append([d, c])
	cerca.sort_custom(func(a: Array, b: Array) -> bool: return a[0] < b[0])
	for i in _ventanas.size():
		var v: SubViewport = _ventanas[i][0]
		var g: Sprite3D = _ventanas[i][1]
		if i >= cerca.size():
			g.visible = false
			v.render_target_update_mode = SubViewport.UPDATE_DISABLED
			continue
		v.render_target_update_mode = SubViewport.UPDATE_ALWAYS
		var c: Node2D = cerca[i][1]
		var pie := c.global_position.round()
		v.canvas_transform = Transform2D(0.0, -(pie - VENTANA_PIE))
		g.position = _al_suelo(pie) + Vector3(0, 0, 0.06)        # (un pelín hacia la cámara: por delante de su dibujo)
		g.modulate = _tinte
		g.visible = true


func _exit_tree() -> void:
	# todo como estaba: la escena vuelve a pintarse y cada dibujo a su canal
	if is_instance_valid(escena) and escena.is_inside_tree():
		escena.get_viewport().canvas_cull_mask = _mascara_antes
	else:
		get_viewport().canvas_cull_mask = _mascara_antes
	for par in _canales.values():
		if is_instance_valid(par[0]):
			(par[0] as CanvasItem).visibility_layer = par[1]
	_canales.clear()
	_gemelos.clear()
	_ids_dinamicos.clear()
	_ids_estaticos.clear()
	_de_pie.clear()
	_ventanas.clear()
	_luces_3d.clear()
	_luces_pt2d.clear()
	_moduladores_2d.clear()
	_cache_mat_relieve.clear()
	_modelos_blender_instanciados.clear()


# --- La cámara ------------------------------------------------------------------------------------------------

func _crear_camara() -> void:
	camara = Camera3D.new()
	camara.fov = CAMARA_FOV
	camara.rotation_degrees = Vector3(CAMARA_INCLINACION, 0, 0)
	camara.near = 10.0
	camara.far = 140.0
	add_child(camara)
	camara.current = true
	_fotogramas_camara = 0
	_adelanto_camara = Vector3.ZERO
	if _maisha:
		_foco = _al_suelo(_maisha.global_position)
	_colocar_camara(1.0)


func _colocar_camara(suave: float, delta: float = 0.016) -> void:
	if _maisha and is_instance_valid(_maisha):
		var base := _al_suelo(_maisha.global_position)
		if _fotogramas_camara < 2 or suave >= 0.99:
			_foco = base
			_adelanto_camara = Vector3.ZERO
		else:
			var vel_2d := Vector2.ZERO
			if _maisha is CharacterBody2D:
				vel_2d = (_maisha as CharacterBody2D).velocity
			var meta_adelanto := Vector3(
				clampf(vel_2d.x * PX * 0.14, -1.35, 1.35),
				0.0,
				clampf(vel_2d.y * PX * 0.11, -1.05, 1.05)
			)
			_adelanto_camara = _adelanto_camara.lerp(meta_adelanto, clampf(delta * 4.5, 0.02, 0.35))
			var paso := clampf(1.0 - exp(-9.5 * delta), 0.04, 0.45)
			_foco = _foco.lerp(base + _adelanto_camara, paso)
		_fotogramas_camara += 1
	# encuadre más íntimo durante los diálogos y vuelta suave al terminar
	var nodo_dlg := escena.get_tree().get_first_node_in_group("dialogo") if is_instance_valid(escena) and escena.is_inside_tree() else null
	var en_dialogo := nodo_dlg != null and bool(nodo_dlg.get("hablando"))
	var fov_meta := CAMARA_FOV - 1.4 if en_dialogo else CAMARA_FOV
	camara.fov = lerpf(camara.fov, fov_meta, clampf(delta * 5.0, 0.04, 0.35))
	# sin salirse del mapa (como la cámara 2D): deja un margen de media pantalla a cada lado
	if region:
		var tam: Vector2 = region.get("tam") * PX
		var mx := minf(16.0, tam.x / 2.0)
		_foco.x = clampf(_foco.x, mx, tam.x - mx)
		_foco.z = clampf(_foco.z, minf(7.0, tam.y / 2.0), tam.y - minf(11.0, tam.y / 2.0))
	# sacudida de impacto limpia sincronizada con la cámara 2D
	var sacudida := Vector3.ZERO
	var cam_2d := escena.get_viewport().get_camera_2d() if is_instance_valid(escena) and escena.is_inside_tree() else null
	if cam_2d and cam_2d.offset != Vector2.ZERO:
		sacudida = Vector3(cam_2d.offset.x * PX * 0.85, -cam_2d.offset.y * PX * 0.55, cam_2d.offset.y * PX * 0.65)
	var atras := camara.global_transform.basis.z * CAMARA_DISTANCIA
	camara.global_position = _foco + sacudida + atras


func _al_suelo(p: Vector2) -> Vector3:
	return Vector3(p.x * PX, 0.0, p.y * PX)


# --- Luces 3D reales y relieve con mapas de normales ----------------------------------------------------------

func _textura_normal_de(tex: Texture2D) -> Texture2D:
	if tex == null:
		return null
	var ruta := tex.resource_path
	if ruta == "":
		return null
	if _cache_normales.has(ruta):
		return _cache_normales[ruta]
	var ruta_n := ruta.get_basename() + "_n.png"
	if ResourceLoader.exists(ruta_n):
		var tn: Texture2D = load(ruta_n)
		_cache_normales[ruta] = tn
		return tn
	_cache_normales[ruta] = null
	return null


func _material_relieve(tex: Texture2D, tex_n: Texture2D, flip_h: bool, mecido_amp: float = 0.0, curvatura: float = 0.75, hv: Vector2 = Vector2.ONE) -> ShaderMaterial:
	var clave := "%d_%d_%d_%d_%dx%d" % [
		tex.get_instance_id(),
		1 if flip_h else 0,
		int(roundf(mecido_amp * 1000.0)),
		int(roundf(curvatura * 100.0)),
		int(hv.x),
		int(hv.y)
	]
	if _cache_mat_relieve.has(clave):
		return _cache_mat_relieve[clave]
	var mat := ShaderMaterial.new()
	mat.shader = _sh_gemelo
	mat.set_shader_parameter("tex_albedo", tex)
	if tex_n != null:
		mat.set_shader_parameter("tex_normal", tex_n)
		mat.set_shader_parameter("usa_normal", 1.0)
	else:
		mat.set_shader_parameter("usa_normal", 0.0)
	mat.set_shader_parameter("volteo_x", -1.0 if flip_h else 1.0)
	mat.set_shader_parameter("mecido", mecido_amp)
	mat.set_shader_parameter("curvatura_3d", curvatura)
	mat.set_shader_parameter("hv_frames", hv)
	mat.set_shader_parameter("tinte_ambiente", Vector3(_tinte.r, _tinte.g, _tinte.b))
	_cache_mat_relieve[clave] = mat
	return mat


func _config_volumen_3d(n: Node2D, ancla: Node2D, arch: String, ancho_px: float, alto_px: float) -> Vector2:
	if alto_px <= 14.0 or arch in ["agujero.png", "charco.png", "mancha.png", "setitas.png", "sombra.png"]:
		return Vector2.ZERO
	if n.get_parent() and n.get_parent().name == "Ropa":
		return Vector2.ZERO
	# Desactivado al 100% para edificios, arquitectura y modelos Blender (evita láminas de papel superpuestas)
	if MODELOS_BLENDER.has(arch) or ancla.is_in_group("edificios") or (ancla.get_script() and "granja" in ancla.get_script().resource_path):
		return Vector2.ZERO
	var es_jefe := ancla.is_in_group("jefes") or (n.get_parent() and n.get_parent().is_in_group("jefes"))
	if es_jefe:
		var prof_j := clampf(minf(ancho_px, alto_px) * PX * 0.38, 0.44, 0.86)
		return Vector2(5.0, prof_j)
	if alto_px >= 40.0 or ancho_px >= 42.0:
		var prof_e := clampf(minf(ancho_px, alto_px) * PX * 0.36, 0.48, 0.88)
		return Vector2(5.0, prof_e)
	if alto_px >= 22.0 or ancho_px >= 22.0:
		var prof_m := clampf(minf(ancho_px, alto_px) * PX * 0.32, 0.28, 0.54)
		return Vector2(4.0, prof_m)
	return Vector2(3.0, 0.22)


func _sincronizar_modelo_blender(n: Node2D, g: Sprite3D, ancla: Node2D, arch: String, mod_final: Color) -> bool:
	if not MODELOS_BLENDER.has(arch):
		return false
	if arch == "molino.png":
		if ancla and (ancla.name.to_lower().contains("granja") or (ancla.get_script() and "granja" in ancla.get_script().resource_path)):
			g.visible = false
			return true
	var cfg: Dictionary = MODELOS_BLENDER[arch]
	var ruta_b: String = cfg["ruta"]
	if arch == "farol.png" or arch == "farol_apagado.png":
		var es_runico := false
		if ancla and ancla.get_script() and String(ancla.get_script().resource_path).ends_with("farol_runico.gd"):
			es_runico = true
		elif n is Sprite2D and (n as Sprite2D).texture:
			var path_tex := (n as Sprite2D).texture.resource_path
			if path_tex.contains("sigilia") or path_tex.contains("paso"):
				es_runico = true
		if es_runico:
			ruta_b = "res://modelos/entorno/farol_runico.glb"
	if cfg.has("ruta_ruina"):
		var frame_act := 0
		if n is Sprite2D:
			frame_act = (n as Sprite2D).frame
		elif n is AnimatedSprite2D:
			frame_act = (n as AnimatedSprite2D).frame
		if frame_act < 1:
			ruta_b = cfg["ruta_ruina"]
	elif cfg.get("solo_reconstruido", false):
		var frame_act := 0
		if n is Sprite2D:
			frame_act = (n as Sprite2D).frame
		elif n is AnimatedSprite2D:
			frame_act = (n as AnimatedSprite2D).frame
		if frame_act < 1:
			var id_r := n.get_instance_id()
			if _modelos_blender_instanciados.has(id_r):
				var m_prev = _modelos_blender_instanciados[id_r]
				if is_instance_valid(m_prev):
					m_prev.visible = false
			return false

	var id := n.get_instance_id()
	var m3d: Node3D = _modelos_blender_instanciados.get(id)
	if m3d != null and is_instance_valid(m3d):
		if m3d.get_meta("ruta_origen", "") != ruta_b:
			m3d.queue_free()
			m3d = null
			_modelos_blender_instanciados.erase(id)
	if m3d == null or not is_instance_valid(m3d):
		if not _escenas_blender_cache.has(ruta_b):
			_escenas_blender_cache[ruta_b] = load(ruta_b) if ResourceLoader.exists(ruta_b) else null
		var ps: PackedScene = _escenas_blender_cache[ruta_b]
		if ps:
			m3d = ps.instantiate() as Node3D
			m3d.name = "Blender3D_%s_%d" % [arch.get_basename(), id]
			m3d.set_meta("ruta_origen", ruta_b)
			m3d.set_meta("radio_occlusion", cfg.get("radio_occlusion", Vector2.ZERO))
			_preparar_materiales_modelo(m3d)
			add_child(m3d)
			_modelos_blender_instanciados[id] = m3d
			var esc: Vector3 = cfg.get("escala", Vector3.ONE)
			m3d.scale = esc
			if cfg.get("rot_y", 0.0) != 0.0:
				m3d.rotation.y = deg_to_rad(cfg["rot_y"])
	if m3d and is_instance_valid(m3d):
		var off: Vector3 = cfg.get("offset", Vector3.ZERO)
		var pos_ref := (n as Node2D).global_position if (arch == "escalera.png" or arch == "puerta.png" or arch == "raiz_tapon.png" or arch == "nudo_giza.png" or arch == "sello_raices.png" or arch == "crater.png" or arch == "cortina.png" or arch == "espinas.png" or arch == "raiz_dormida.png" or arch == "semilla_dormida.png" or arch == "zanahoria.png" or arch == "chatarra.png") else (ancla.global_position if ancla and is_instance_valid(ancla) and ancla.global_position != Vector2.ZERO else (n as Node2D).global_position)
		m3d.position = _al_suelo(pos_ref) + off
		m3d.visible = _visible(n)
		if mod_final.a < 0.05:
			m3d.visible = false
		elif mod_final.a < 0.98:
			_aplicar_alfa_a_nodos(m3d, mod_final.a)
		if arch == "puerta.png":
			var frame_act := 0
			if n is Sprite2D:
				frame_act = (n as Sprite2D).frame
			elif n is AnimatedSprite2D:
				frame_act = (n as AnimatedSprite2D).frame
			var abierta := frame_act >= 3
			for hijo in m3d.find_children("*", "Node3D"):
				if hijo.name.begins_with("Sello_") or hijo.name.begins_with("Cancela_") or hijo.name.begins_with("Barrote_"):
					(hijo as Node3D).visible = not abierta
		elif arch == "zanahoria.png":
			var frame_act := 0
			if n is Sprite2D:
				frame_act = (n as Sprite2D).frame
			var cosechada := frame_act >= 1
			for hijo in m3d.find_children("*", "Node3D"):
				if hijo.name.begins_with("Zanahoria_Fruto") or hijo.name.begins_with("Zanahoria_Hojas"):
					(hijo as Node3D).visible = not cosechada
		elif arch == "chatarra.png":
			var frame_act := 0
			if n is Sprite2D:
				frame_act = (n as Sprite2D).frame
			var aplastada := frame_act >= 1
			for hijo in m3d.find_children("*", "Node3D"):
				if hijo.name.begins_with("Chatarra_Superior"):
					(hijo as Node3D).visible = not aplastada
		g.visible = false
		g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		if g.has_meta("capas_fondo"):
			for c_ant in g.get_meta("capas_fondo"):
				if is_instance_valid(c_ant):
					(c_ant as Sprite3D).visible = false
					(c_ant as Node).queue_free()
			g.remove_meta("capas_fondo")
		return true
	return false


func _actualizar_transparencias_edificios() -> void:
	if not _maisha or not is_instance_valid(_maisha):
		return
	var pos_m := _al_suelo(_maisha.global_position)
	for m3d_var in _modelos_blender_instanciados.values():
		if not is_instance_valid(m3d_var):
			continue
		var m3d := m3d_var as Node3D
		if not m3d.visible:
			continue
		var radio_occ: Vector2 = m3d.get_meta("radio_occlusion", Vector2.ZERO)
		if radio_occ == Vector2.ZERO:
			continue
		var d_x := absf(pos_m.x - m3d.position.x)
		var d_z := m3d.position.z - pos_m.z # positivo si Maisha está detrás (al norte del edificio)
		# Rango de oclusión bajo la cámara en perspectiva (-48°):
		var oculta := (d_x < radio_occ.x) and (d_z > 0.15 and d_z < radio_occ.y)
		var meta_a := 0.38 if oculta else 1.0
		var alfa_actual: float = m3d.get_meta("alfa_transparencia", 1.0)
		var nuevo_alfa := lerpf(alfa_actual, meta_a, 0.28)
		if absf(nuevo_alfa - meta_a) < 0.02:
			nuevo_alfa = meta_a
		m3d.set_meta("alfa_transparencia", nuevo_alfa)
		if absf(nuevo_alfa - alfa_actual) > 0.01:
			_aplicar_alfa_a_nodos(m3d, nuevo_alfa)


func _aplicar_alfa_a_nodos(nodo: Node, a: float) -> void:
	if nodo is MeshInstance3D:
		var mi := nodo as MeshInstance3D
		var num_surf := mi.mesh.get_surface_count() if mi.mesh else 0
		for s in num_surf:
			var mat := mi.get_surface_override_material(s)
			if mat is StandardMaterial3D:
				var sm := mat as StandardMaterial3D
				if a < 0.98:
					sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS
					sm.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_ALWAYS
					sm.albedo_color.a = a
				else:
					sm.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED
					sm.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_OPAQUE_ONLY
					sm.albedo_color.a = 1.0
	for h in nodo.get_children():
		_aplicar_alfa_a_nodos(h, a)


func _preparar_materiales_modelo(nodo: Node) -> void:
	if nodo is MeshInstance3D:
		var mi := nodo as MeshInstance3D
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		var num_surf := mi.mesh.get_surface_count() if mi.mesh else 0
		for s in num_surf:
			var mat := mi.get_surface_override_material(s)
			if mat == null and mi.mesh:
				mat = mi.mesh.surface_get_material(s)
			if mat is StandardMaterial3D:
				var sm := mat.duplicate() as StandardMaterial3D
				sm.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
				sm.diffuse_mode = BaseMaterial3D.DIFFUSE_LAMBERT_WRAP
				sm.roughness = 0.85
				sm.metallic_specular = 0.10
				sm.cull_mode = BaseMaterial3D.CULL_BACK
				# Retención ambiental de color: asegura que en sombra las paredes y tejados mantengan sus detalles pixel art
				if sm.albedo_texture != null:
					sm.emission_enabled = true
					sm.emission_texture = sm.albedo_texture
					sm.emission = Color.WHITE
					sm.emission_energy_multiplier = 0.48
				elif not sm.emission_enabled:
					var col_base := sm.albedo_color
					sm.emission_enabled = true
					sm.emission = col_base
					sm.emission_energy_multiplier = 0.48
				mi.set_surface_override_material(s, sm)
	for h in nodo.get_children():
		_preparar_materiales_modelo(h)


func _sincronizar_volumen_3d(n: Node2D, g: Sprite3D, ancla: Node2D, tex: Texture2D, arch: String, ancho_px: float, alto_px: float, mod_final: Color) -> void:
	if _sincronizar_modelo_blender(n, g, ancla, arch, mod_final):
		return
	g.visible = _visible(n)
	var cfg := _config_volumen_3d(n, ancla, arch, ancho_px, alto_px)
	var num_capas := int(cfg.x)
	if num_capas <= 0 or tex == null:
		if g.has_meta("capas_fondo"):
			for c_ant in g.get_meta("capas_fondo"):
				if is_instance_valid(c_ant):
					(c_ant as Sprite3D).visible = false
					(c_ant as Node).queue_free()
			g.remove_meta("capas_fondo")
		return
	var prof_z := cfg.y
	var capas: Array = []
	if g.has_meta("capas_fondo"):
		capas = g.get_meta("capas_fondo")
	else:
		for k in range(1, num_capas + 1):
			var c_sp := Sprite3D.new()
			c_sp.pixel_size = PX
			c_sp.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
			c_sp.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
			c_sp.alpha_scissor_threshold = 0.52
			c_sp.shaded = false
			c_sp.double_sided = true
			c_sp.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
			c_sp.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if (k == num_capas or k == maxi(1, num_capas / 2)) else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			g.add_child(c_sp)
			capas.append(c_sp)
		g.set_meta("capas_fondo", capas)
	var alto_m := maxf(alto_px * PX * COMPENSACION_Y, 0.5)
	var y_base_local := (g.offset.y - (alto_px * 0.5 if g.centered else 0.0)) * PX
	for k in capas.size():
		var c_sp: Sprite3D = capas[k]
		if not is_instance_valid(c_sp):
			continue
		c_sp.visible = g.visible
		var t := float(k + 1) / float(capas.size())
		var dz := prof_z * t
		c_sp.texture = tex
		c_sp.hframes = g.hframes
		c_sp.vframes = g.vframes
		c_sp.frame = g.frame
		c_sp.region_enabled = g.region_enabled
		c_sp.region_rect = g.region_rect
		c_sp.flip_h = g.flip_h
		c_sp.flip_v = g.flip_v
		c_sp.centered = g.centered
		c_sp.offset = g.offset
		c_sp.visibility_range_end = g.visibility_range_end
		var sx := 1.0 + 0.055 * sin(t * PI) - 0.018 * t * t
		var sy := clampf(1.0 - (dz * 0.72) / alto_m, 0.48, 0.96)
		c_sp.scale = Vector3(sx, sy, 1.0)
		c_sp.position = Vector3(0.0, y_base_local * (1.0 - sy), -dz)
		var osc := lerpf(0.78, 0.42, t)
		c_sp.modulate = mod_final * Color(osc * 0.94, osc * 0.96, osc * 1.05, 1.0)


func _actualizar_color_volumen_3d(g: Sprite3D, mod_final: Color) -> void:
	if not g.has_meta("capas_fondo"):
		return
	var capas: Array = g.get_meta("capas_fondo")
	for k in capas.size():
		var c_sp: Sprite3D = capas[k]
		if is_instance_valid(c_sp):
			var t := float(k + 1) / float(capas.size())
			var osc := lerpf(0.78, 0.42, t)
			c_sp.modulate = mod_final * Color(osc * 0.94, osc * 0.96, osc * 1.05, 1.0)


func _crear_omni_3d(color: Color, rango: float, pos_3d: Vector3) -> OmniLight3D:
	var luz := OmniLight3D.new()
	luz.light_color = color
	luz.omni_range = rango
	luz.omni_attenuation = 1.35
	luz.shadow_enabled = false
	luz.light_energy = 0.0
	luz.visible = false
	luz.position = pos_3d
	add_child(luz)
	return luz


func _registrar_luces_sprite(s: Variant, tex: Texture2D) -> void:
	if not is_instance_valid(s) or not (s is Sprite2D) or tex == null:
		return
	var sp := s as Sprite2D
	var arch := tex.resource_path.get_file()
	if not LUCES_3D.has(arch):
		return
	var padre := sp.get_parent()
	if padre and padre.get_script() and String(padre.get_script().resource_path).ends_with("farol_runico.gd"):
		return
	_rehacer_luces_sprite(sp, tex, LUCES_3D[arch])
	if arch in CAMBIAN_AL_RECONSTRUIRSE_3D and not sp.frame_changed.is_connected(_rehacer_luces_sprite):
		sp.frame_changed.connect(_rehacer_luces_sprite.bind(sp, tex, LUCES_3D[arch]))


func _rehacer_luces_sprite(s: Sprite2D, tex: Texture2D, puntos: Array) -> void:
	if not is_instance_valid(s) or tex == null:
		return
	for i in range(_luces_3d.size() - 1, -1, -1):
		if _luces_3d[i]["dueno"] == s:
			var l_ant: OmniLight3D = _luces_3d[i]["luz"]
			if is_instance_valid(l_ant):
				l_ant.queue_free()
			_luces_3d.remove_at(i)
	var ancla := _ancla(s)
	var tam_fotograma := tex.get_size() / Vector2(maxi(1, s.hframes), maxi(1, s.vframes))
	var arch := tex.resource_path.get_file()
	var fotograma := 0 if arch == "farol.png" else s.frame
	var esquina := Vector2(fotograma % maxi(1, s.hframes), fotograma / maxi(1, s.hframes)) * tam_fotograma
	var origen := (-tam_fotograma / 2.0 if s.centered else Vector2.ZERO) + s.offset
	for p in puntos:
		var en_dibujo := Vector2(p[1], p[2])
		if not Rect2(esquina, tam_fotograma).has_point(en_dibujo):
			continue
		var local := origen + (en_dibujo - esquina)
		if s.flip_h:
			local.x = -local.x if s.centered else tam_fotograma.x - local.x
		var global_2d := s.global_position + local
		var x_3d := global_2d.x * PX
		var y_3d := clampf(-(global_2d.y - ancla.global_position.y) * PX, 0.45, 3.6)
		var z_3d := ancla.global_position.y * PX + 0.48
		var tipo := String(p[0])
		var cfg: Array = TIPOS_LUZ_3D.get(tipo, TIPOS_LUZ_3D["v"])
		var pos_3d := Vector3(x_3d, y_3d, z_3d)
		var omni := _crear_omni_3d(cfg[2], float(cfg[0]), pos_3d)
		_luces_3d.append({
			"luz": omni,
			"pos": pos_3d,
			"color": cfg[2],
			"rango": float(cfg[0]),
			"fuerza": float(cfg[1]),
			"fuego": bool(cfg[3]),
			"siempre": tipo == "m",
			"fase": randf() * TAU,
			"dueno": s,
		})


func _luz_en_punto(pos: Vector3) -> Color:
	var r := 0.0
	var g := 0.0
	var b := 0.0
	for d in _luces_3d:
		var omni: OmniLight3D = d["luz"]
		if not is_instance_valid(omni) or not omni.visible:
			continue
		var dist := pos.distance_to(d["pos"])
		var rango: float = d["rango"]
		if dist < rango:
			var f := pow(1.0 - dist / rango, 1.6) * omni.light_energy * 0.12
			var col: Color = d["color"]
			r += col.r * f
			g += col.g * f
			b += col.b * f
	for par_pt in _luces_pt2d.values():
		var omni_pt: OmniLight3D = par_pt[1]
		if not is_instance_valid(omni_pt) or not omni_pt.visible:
			continue
		var dist := pos.distance_to(omni_pt.position)
		if dist < omni_pt.omni_range:
			var f := pow(1.0 - dist / omni_pt.omni_range, 1.6) * omni_pt.light_energy * 0.10
			r += omni_pt.light_color.r * f
			g += omni_pt.light_color.g * f
			b += omni_pt.light_color.b * f
	return Color(r, g, b, 1.0)


# --- Los gemelos de los dibujos -------------------------------------------------------------------------------

func _registrar(n: Node) -> void:
	if not (n is CanvasItem) or not escena.is_ancestor_of(n) or _en_interfaz(n):
		return
	var ci := n as CanvasItem
	if not _canales.has(ci.get_instance_id()):
		_canales[ci.get_instance_id()] = [ci, ci.visibility_layer]
	if n is CanvasModulate:
		if not _moduladores_2d.has(n):
			_moduladores_2d.append(n as CanvasModulate)
	elif n is PointLight2D and not n.has_meta("luz_edificio"):
		var id_pt := n.get_instance_id()
		if not _luces_pt2d.has(id_pt):
			var pt := n as PointLight2D
			var omni := _crear_omni_3d(pt.color, clampf(pt.texture_scale * 6.8, 3.0, 9.5), Vector3.ZERO)
			_luces_pt2d[id_pt] = [pt, omni]
	elif n.get_script() and String(n.get_script().resource_path).ends_with("/fogata.gd"):
		var p_fog := _al_suelo((n as Node2D).global_position) + Vector3(0.0, 0.55, 0.35)
		var cfg_h: Array = TIPOS_LUZ_3D["h"]
		var omni_f := _crear_omni_3d(cfg_h[2], float(cfg_h[0]), p_fog)
		_luces_3d.append({
			"luz": omni_f,
			"pos": p_fog,
			"color": cfg_h[2],
			"rango": float(cfg_h[0]),
			"fuerza": float(cfg_h[1]),
			"fuego": true,
			"siempre": true,
			"fase": randf() * TAU,
			"dueno": n,
		})
	# ¿a qué capa va?
	# Las sombras elípticas (sombra.gd) van al suelo (CANAL_SUELO) para dar oclusión ambiental de contacto bajo pies y bases
	if n.get_script() and String(n.get_script().resource_path).ends_with("sombra.gd"):
		ci.visibility_layer = CANAL_SUELO
		return
	if _de_pantalla(n):
		ci.visibility_layer = CANAL_PANTALLA
		return
	var es_modelo_blender := false
	if n is Sprite2D and (n as Sprite2D).texture:
		var tex_s := (n as Sprite2D).texture
		if tex_s is CanvasTexture:
			tex_s = (tex_s as CanvasTexture).diffuse_texture
		var arch_b := tex_s.resource_path.get_file() if tex_s else ""
		es_modelo_blender = MODELOS_BLENDER.has(arch_b)
	elif n is AnimatedSprite2D and (n as AnimatedSprite2D).sprite_frames:
		var sf := (n as AnimatedSprite2D).sprite_frames
		if sf.has_animation("default") and sf.get_frame_count("default") > 0:
			var tex_b := sf.get_frame_texture("default", 0)
			if tex_b:
				es_modelo_blender = MODELOS_BLENDER.has(tex_b.resource_path.get_file())

	if not (n is Sprite2D or n is AnimatedSprite2D) or (_z(n) < SUELO_BAJO and not es_modelo_blender):
		var dueno := _dueno_de_pie(n)
		if _contenedor(n):
			# un contenedor (no pinta nada): en todos los canales, para que sus hijos se vean en su capa
			ci.visibility_layer = CANAL_SUELO | CANAL_PIE
		else:
			# lo que pinta (con código, o un sprite pegado al suelo): de pie (en su ventanita) o en el suelo
			ci.visibility_layer = CANAL_PIE if dueno and _dibuja(n) else CANAL_SUELO
		if dueno:
			var cuerpo := _ancla(dueno as Node2D)
			_de_pie[cuerpo.get_instance_id()] = cuerpo
		return
	ci.visibility_layer = CANAL_GEMELO
	var id := n.get_instance_id()
	if _gemelos.has(id):
		return
	var g := Sprite3D.new()
	g.pixel_size = PX
	g.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	g.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	g.alpha_scissor_threshold = 0.52
	g.shaded = false                 # (sus colores de pixel art; de noche se oscurecen con «_tinte»)
	g.double_sided = true
	g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	g.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	add_child(g)
	var ancla := _ancla(n as Node2D)
	var z := _z(n)
	var mod_base: Color = (n as CanvasItem).modulate * (n as CanvasItem).self_modulate
	var par := [n, g, ancla, z, mod_base]
	_gemelos[id] = par
	var estatico := false
	if n is Sprite2D:
		var s := n as Sprite2D
		var tex_s := s.texture
		if tex_s is CanvasTexture:
			tex_s = (tex_s as CanvasTexture).diffuse_texture
		_registrar_luces_sprite.call_deferred(s, tex_s)
		var arch := tex_s.resource_path.get_file() if tex_s else ""
		if n.get_script() == null and ancla is StaticBody2D and ancla.get_script() == null:
			if not (arch in ["casa_seta.png", "taller.png", "cocina.png", "puesto.png", "farol.png", "transbordador.png"]):
				estatico = true
			if tex_s:
				var alto_f := (s.region_rect.size.y if s.region_enabled else tex_s.get_height() / float(maxi(s.vframes, 1)))
				if alto_f <= 14.0:
					g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	if estatico:
		g.visibility_range_end = 64.0
		_copiar(n as Node2D, g, ancla, z)
		_ids_estaticos[id] = true
	else:
		_ids_dinamicos[id] = true


## ¿Cuelga de una CanvasLayer (la interfaz: el HUD, los diálogos, la mochila...)? Eso no se toca.
func _en_interfaz(n: Node) -> bool:
	var c: Node = n
	while c and c != escena:
		if c is CanvasLayer:
			return true
		c = c.get_parent()
	return false


## ¿No pinta nada él mismo? (un Node2D, un cuerpo, una forma de choque, una luz... sin _draw)
func _contenedor(n: Node) -> bool:
	if _dibuja(n):
		return false
	return n.get_class() == "Node2D" or n is CollisionObject2D or n is CollisionShape2D or n is CollisionPolygon2D \
		or n is Light2D or n is LightOccluder2D or n is Marker2D or n is RemoteTransform2D or n is CanvasModulate


## ¿Dibuja algo con código? (_draw en su script, o alguien conectado a su señal «draw»)
func _dibuja(n: Node) -> bool:
	return (n.get_script() != null and n.has_method("_draw")) or not n.get_signal_connection_list("draw").is_empty()


## El objeto de pie al que pertenece este dibujo (él mismo o su padre, si es de los DE_PIE), o null
func _dueno_de_pie(n: Node) -> Node:
	for c in [n, n.get_parent()]:
		if c and c != escena and c.get_script():
			var ruta := String(c.get_script().resource_path)
			for nombre in DE_PIE:
				if ruta.ends_with("/" + nombre):
					return c
	return null


## ¿Es un dibujo de pantalla (o cuelga de uno)?
func _de_pantalla(n: Node) -> bool:
	var c: Node = n
	while c and c != escena:
		if c.get_script():
			var ruta := String(c.get_script().resource_path)
			for nombre in DE_PANTALLA:
				if ruta.ends_with(nombre):
					return true
		c = c.get_parent()
	return false


func _quitar(n: Node) -> void:
	var id := n.get_instance_id()
	_canales.erase(id)
	_de_pie.erase(id)
	_ids_dinamicos.erase(id)
	_ids_estaticos.erase(id)
	if _luces_pt2d.has(id):
		if is_instance_valid(_luces_pt2d[id][1]):
			(_luces_pt2d[id][1] as Node).queue_free()
		_luces_pt2d.erase(id)
	if _gemelos.has(id):
		if is_instance_valid(_gemelos[id][1]):
			(_gemelos[id][1] as Node).queue_free()
		_gemelos.erase(id)
	if _modelos_blender_instanciados.has(id):
		if is_instance_valid(_modelos_blender_instanciados[id]):
			(_modelos_blender_instanciados[id] as Node).queue_free()
		_modelos_blender_instanciados.erase(id)


## El z_index de verdad de un dibujo (sumando el de sus padres, si es relativo)
func _z(n: CanvasItem) -> int:
	var z := 0
	var c: Node = n
	while c and c is CanvasItem and c != escena:
		z += (c as CanvasItem).z_index
		if not (c as CanvasItem).z_as_relative:
			break
		c = c.get_parent()
	return z


## El punto del suelo en el que se apoya un dibujo: el de su «cuerpo» (el hijo directo de Entidades, que se
## ordena por altura), o el suyo propio
func _ancla(n: Node2D) -> Node2D:
	var c: Node = n
	while c and c.get_parent() and c.get_parent() != escena:
		var p := c.get_parent()
		if p is CanvasItem and (p as CanvasItem).y_sort_enabled:
			return c as Node2D
		c = p
	return n


## ¿Se ve? (su visibilidad hasta la escena, sin contar la escena, que está oculta)
func _visible(n: CanvasItem) -> bool:
	var c: Node = n
	while c and c != escena:
		if c is CanvasItem and not (c as CanvasItem).visible:
			return false
		c = c.get_parent()
	return true


func _process(delta: float) -> void:
	_tiempo_luces += delta
	# el sol sigue la hora del día (de día, cálido; de noche, frío y flojo), y los dibujos se tiñen igual
	var dia: float = Reloj.luz_dia() if Reloj.has_method("luz_dia") else 1.0
	var calido: float = Reloj.calidez() if Reloj.has_method("calidez") else 0.0
	var mod_2d := Color.WHITE
	var en_penumbra := false
	for i in range(_moduladores_2d.size() - 1, -1, -1):
		var m := _moduladores_2d[i]
		if not is_instance_valid(m):
			_moduladores_2d.remove_at(i)
			continue
		if m.visible:
			mod_2d = m.color
			if m.name != "LuzDelDia":
				en_penumbra = true
				break
	if en_penumbra:
		sol.light_energy = 0.08
		sol.light_color = Color(0.65, 0.62, 0.85)
		_tinte = Color(clampf(mod_2d.r * 2.3, 0.24, 1.0), clampf(mod_2d.g * 2.3, 0.22, 1.0), clampf(mod_2d.b * 2.3, 0.28, 1.0))
	else:
		sol.light_energy = lerpf(0.07, 0.27, dia)
		sol.light_color = Color(0.6, 0.66, 0.95).lerp(Color(1.0, 0.95, 0.86), dia).lerp(Color(1.0, 0.72, 0.45), calido * 0.5)
		_tinte = Color(0.42, 0.46, 0.68).lerp(Color.WHITE, dia).lerp(Color(1.0, 0.88, 0.78), calido * 0.35)
	var tinte_roca := Color(minf(1.0, mod_2d.r * 1.65), minf(1.0, mod_2d.g * 1.65), minf(1.0, mod_2d.b * 1.65)) if en_penumbra else mod_2d
	if _mat_penas:
		_mat_penas.albedo_color = tinte_roca
	var nodo_espejo := get_tree().get_first_node_in_group("espejo_lago")
	var calma_lago := float(nodo_espejo.get("calma")) if nodo_espejo else 0.0
	var f_nubes := (0.15 * dia) if not en_penumbra else 0.0
	for m_cap in _mats_capa:
		m_cap.set_shader_parameter("fuerza_nubes", f_nubes)
		m_cap.set_shader_parameter("calma_lago", calma_lago)
	for m_lej in _suelos_lejanos:
		m_lej.set_shader_parameter("tinte_2d", Vector3(tinte_roca.r, tinte_roca.g, tinte_roca.b))
		m_lej.set_shader_parameter("fuerza_nubes", f_nubes)
		m_lej.set_shader_parameter("calma_lago", calma_lago)
	_colocar_camara(0.12, delta)
	var noche_ef := 1.0 if en_penumbra else (1.0 - dia)
	_actualizar_luces_3d(noche_ef)
	var cambio_tinte := absf(_tinte.r - _ultimo_tinte.r) + absf(_tinte.g - _ultimo_tinte.g) + absf(_tinte.b - _ultimo_tinte.b) > 0.008
	var toca_luces_est := noche_ef > 0.15 and int((_tiempo_luces - delta) * 6.0) != int(_tiempo_luces * 6.0)
	if cambio_tinte or toca_luces_est:
		_ultimo_tinte = _tinte
		var vec_tinte := Vector3(_tinte.r, _tinte.g, _tinte.b)
		for mat_r in _cache_mat_relieve.values():
			(mat_r as ShaderMaterial).set_shader_parameter("tinte_ambiente", vec_tinte)
		var hay_luces_activas := noche_ef > 0.15 and (_luces_3d.size() > 0 or _luces_pt2d.size() > 0)
		for id_e in _ids_estaticos.keys():
			if not _gemelos.has(id_e):
				_ids_estaticos.erase(id_e)
				continue
			var pe: Array = _gemelos[id_e]
			if not is_instance_valid(pe[0]) or not is_instance_valid(pe[1]):
				_ids_estaticos.erase(id_e)
				_gemelos.erase(id_e)
				continue
			var g_e: Sprite3D = pe[1]
			if not hay_luces_activas:
				g_e.modulate = (pe[4] as Color) * _tinte
				_actualizar_color_volumen_3d(g_e, g_e.modulate)
				continue
			if absf(g_e.position.x - _foco.x) > LEJOS or absf(g_e.position.z - _foco.z) > LEJOS:
				continue
			var luz_e := _luz_en_punto(g_e.position)
			var tf_e := Color(minf(1.06, _tinte.r + luz_e.r), minf(1.05, _tinte.g + luz_e.g), minf(1.03, _tinte.b + luz_e.b), 1.0)
			g_e.modulate = (pe[4] as Color) * tf_e
			_actualizar_color_volumen_3d(g_e, g_e.modulate)
	for id in _ids_dinamicos.keys():
		if not _gemelos.has(id):
			_ids_dinamicos.erase(id)
			continue
		var par: Array = _gemelos[id]
		if not is_instance_valid(par[0]) or not is_instance_valid(par[1]):
			if is_instance_valid(par[1]):
				(par[1] as Node).queue_free()
			_ids_dinamicos.erase(id)
			_gemelos.erase(id)
			continue
		var n: Node2D = par[0]
		var g: Sprite3D = par[1]
		var p := n.global_position * PX
		if absf(p.x - _foco.x) > LEJOS or absf(p.y - _foco.z) > LEJOS:
			g.visible = false
			continue
		if par[2] == null or not is_instance_valid(par[2]):
			par[2] = _ancla(n)
		_copiar(n, g, par[2], par[3])
	if _maisha and is_instance_valid(_maisha):
		var pm := _al_suelo(_maisha.global_position)
		for mat_r in _cache_mat_relieve.values():
			(mat_r as ShaderMaterial).set_shader_parameter("pos_maisha", pm)
	_actualizar_transparencias_edificios()
	_mover_capas()
	_actualizar_particulas_3d(delta, dia, en_penumbra)
	_actualizar_postproceso(0.15 if en_penumbra else dia, calido)


func _actualizar_luces_3d(noche: float) -> void:
	var encendidas := smoothstep(0.12, 0.58, noche)
	for i in range(_luces_3d.size() - 1, -1, -1):
		var d: Dictionary = _luces_3d[i]
		var omni: OmniLight3D = d["luz"]
		if not is_instance_valid(omni) or not is_instance_valid(d["dueno"]):
			if is_instance_valid(omni):
				omni.queue_free()
			_luces_3d.remove_at(i)
			continue
		var pos_l: Vector3 = d["pos"]
		if absf(pos_l.x - _foco.x) > LEJOS or absf(pos_l.z - _foco.z) > LEJOS:
			omni.visible = false
			continue
		var factor_hora := maxf(0.45, encendidas) if bool(d["siempre"]) else encendidas
		if factor_hora <= 0.02:
			omni.light_energy = 0.0
			omni.visible = false
			continue
		var vacila := 0.14 * sin(_tiempo_luces * (7.2 if d["fuego"] else 2.2) + float(d["fase"])) \
			+ (0.08 * sin(_tiempo_luces * 13.0 + float(d["fase"]) * 2.0) if d["fuego"] else 0.0)
		omni.light_energy = float(d["fuerza"]) * factor_hora * (1.0 + vacila)
		omni.visible = omni.light_energy > 0.02
	for id_pt in _luces_pt2d.keys():
		var par_pt: Array = _luces_pt2d[id_pt]
		var pt: PointLight2D = par_pt[0]
		var omni_pt: OmniLight3D = par_pt[1]
		if not is_instance_valid(pt) or not is_instance_valid(omni_pt):
			if is_instance_valid(omni_pt):
				omni_pt.queue_free()
			_luces_pt2d.erase(id_pt)
			continue
		if not pt.visible or pt.energy <= 0.02:
			omni_pt.visible = false
			omni_pt.light_energy = 0.0
			continue
		var ancla_pt := _ancla(pt)
		var pos_3d := Vector3(
			pt.global_position.x * PX,
			clampf(-(pt.global_position.y - ancla_pt.global_position.y) * PX + 0.4, 0.45, 3.2),
			ancla_pt.global_position.y * PX + 0.38
		)
		if absf(pos_3d.x - _foco.x) > LEJOS or absf(pos_3d.z - _foco.z) > LEJOS:
			omni_pt.visible = false
			continue
		omni_pt.position = pos_3d
		omni_pt.light_color = pt.color
		omni_pt.omni_range = clampf(pt.texture_scale * 6.8, 3.0, 9.5)
		omni_pt.light_energy = pt.energy * 1.45
		omni_pt.visible = true


func _copiar(n: Node2D, g: Sprite3D, ancla: Node2D, z: int) -> void:
	g.visible = _visible(n)
	if not g.visible:
		return
	var tex: Texture2D = null
	var tex_n: Texture2D = null
	if n is AnimatedSprite2D:
		var a := n as AnimatedSprite2D
		if a.sprite_frames:
			tex = a.sprite_frames.get_frame_texture(a.animation, a.frame)
		g.hframes = 1
		g.vframes = 1
		g.frame = 0
		g.region_enabled = false
	else:
		var s := n as Sprite2D
		tex = s.texture
		g.hframes = s.hframes
		g.vframes = s.vframes
		g.frame = mini(s.frame, s.hframes * s.vframes - 1)
		g.region_enabled = s.region_enabled
		g.region_rect = s.region_rect
	if tex is CanvasTexture:
		tex_n = (tex as CanvasTexture).normal_texture
		tex = (tex as CanvasTexture).diffuse_texture          # (en 3D, el relieve va en SOMBREADOR_GEMELO)
	elif tex != null:
		tex_n = _textura_normal_de(tex)
	g.texture = tex
	var arch_check := tex.resource_path.get_file() if tex else ""
	if arch_check == "molino.png" and ancla and (ancla.name.to_lower().contains("granja") or (ancla.get_script() and "granja" in ancla.get_script().resource_path)):
		g.visible = false
		return
	g.flip_h = n.flip_h
	g.flip_v = n.flip_v
	g.centered = n.centered
	var escala := n.global_scale
	g.scale = Vector3(escala.x, escala.y * COMPENSACION_Y, 1.0)
	# de pie: apoyado en el suelo de su cuerpo; lo que en 2D está más arriba que el cuerpo, en 3D está más alto
	var sube: Vector2 = n.global_position - ancla.global_position
	var o2: Vector2 = n.offset + Vector2(sube.x, sube.y)
	# (en 2D la «y» crece hacia abajo y en 3D hacia arriba: sin centrar, el dibujo va de o2.y a o2.y + alto en 2D,
	# así que en 3D su borde de abajo está en -(o2.y + alto); centrado, se queda donde está, solo cambia el signo)
	var ancho_f := 0.0
	var alto_f := 0.0
	if tex:
		ancho_f = (g.region_rect.size.x if g.region_enabled else tex.get_width() / float(maxi(g.hframes, 1)))
		alto_f = (g.region_rect.size.y if g.region_enabled else tex.get_height() / float(maxi(g.vframes, 1)))
	var alto := alto_f if (not g.centered and tex) else 0.0
	g.offset = Vector2(o2.x, -(o2.y + alto))
	# En jefes por piezas (Cosechadora, Mzizi), separamos las capas con más profundidad Z para que tengan cuerpo mecánico/orgánico real
	var es_jefe_capas := ancla.is_in_group("jefes") and n.get_parent() != ancla
	var paso_indice := 0.026 if es_jefe_capas else 0.0018
	var orden := z * 0.005 + n.get_index() * paso_indice
	g.position = _al_suelo(ancla.global_position) + Vector3(0, 0, orden)
	var luz_p := _luz_en_punto(g.position)
	var tf := Color(minf(1.06, _tinte.r + luz_p.r), minf(1.05, _tinte.g + luz_p.g), minf(1.03, _tinte.b + luz_p.b), 1.0)
	var mod_propio := n.modulate * n.self_modulate
	var mod_final := mod_propio * tf
	g.modulate = mod_final
	var arch := tex.resource_path.get_file() if tex else ""
	if tex and alto_f > 14.0 and not g.region_enabled:
		var amp_mecido := float(FLORA_MECIDA.get(arch, 0.0))
		var es_gran_vol := ancla.is_in_group("jefes") or ancla.is_in_group("edificios") or alto_f >= 32.0 or ancho_f >= 32.0
		var curv := 0.90 if es_gran_vol else 0.65
		var sin_destello := absf(mod_propio.r - 1.0) < 0.08 and absf(mod_propio.g - 1.0) < 0.08 and absf(mod_propio.b - 1.0) < 0.08 and mod_propio.a > 0.96
		if sin_destello:
			g.material_override = _material_relieve(tex, tex_n, g.flip_h, amp_mecido, curv, Vector2(maxi(g.hframes, 1), maxi(g.vframes, 1)))
		else:
			g.material_override = null
	_sincronizar_volumen_3d(n, g, ancla, tex, arch, ancho_f, alto_f, mod_final)


