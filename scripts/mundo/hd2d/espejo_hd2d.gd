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
const CAMARA_DISTANCIA := 30.0     # metros hasta Maisha (se ve más o menos lo mismo que en 2D)
const CAMARA_FOV := 30.0
const LEJOS := 30.0                # metros: más allá de esto (de la cámara), los gemelos no se copian
## Los canales de dibujo (visibility_layer) del mundo; la interfaz se queda en el 1, el de siempre. La pantalla
## principal deja de pintar estos canales y las capas pintan solo el suyo.
const CANAL_SUELO := 1 << 12
const CANAL_GEMELO := 1 << 13
const CANAL_PANTALLA := 1 << 14
const CANAL_NADA := 1 << 15
const CANAL_PIE := 1 << 16
const CANALES_MUNDO := CANAL_SUELO | CANAL_GEMELO | CANAL_PANTALLA | CANAL_NADA | CANAL_PIE
## Los que dibujan con código algo que va DE PIE (llamas, halos, el «!» de los aldeanos, la niebla de un arco):
## lo que dibujan ellos (o sus hijos sin script) se ve en una VENTANITA de pie sobre ellos (_ventanas)
const DE_PIE := ["brasero.gd", "fogata.gd", "farol.gd", "farol_runico.gd", "eco_perdido.gd", "esencia.gd",
	"recogible.gd", "arco_ruinas.gd", "portal.gd", "aldeano.gd", "taa.gd"]
const VENTANA := Vector2i(128, 160)       # píxeles de cada ventanita
const VENTANA_PIE := Vector2(64, 148)     # dónde cae el pie del objeto dentro de la ventanita
const VENTANAS := 10                      # como mucho, las de los 10 objetos de pie más cerca de la cámara
const LADO_CAPA := 768             # píxeles de la capa de suelo (48 m alrededor de Maisha: cubre toda la cámara)
## El suelo cercano: la capa de suelo, con luz (para las sombras)
## Con «hundido» = 0 es el suelo, con un agujero donde hay agua; con 1, el agua (más abajo, algo más oscura y azul,
## con un brillo que se mueve). «agua» es la máscara del mapa (1 píxel por casilla).
const SOMBREADOR_CAPA := """
shader_type spatial;
render_mode diffuse_lambert, specular_disabled;
uniform sampler2D capa : filter_nearest;
uniform sampler2D agua : filter_linear;
uniform sampler2D mapa_ao : filter_linear;
uniform vec2 origen = vec2(0.0);
uniform vec2 casillas = vec2(1.0);
uniform float lado = 1024.0;
uniform float hundido = 0.0;
void fragment() {
	vec2 px = origen + UV * lado;
	vec2 uv_mapa = px / 16.0 / casillas;
	// (la máscara, suavizada y con un temblor, para que la orilla sea curva como la pintada y no en escalones)
	float temblor = sin(px.x * 0.37 + px.y * 0.21) * 0.06 + sin(px.y * 0.53 - px.x * 0.17) * 0.05;
	float es_agua = texture(agua, uv_mapa).r + temblor;
	if (hundido < 0.5 && es_agua > 0.5) { discard; }
	if (hundido > 0.5 && es_agua <= 0.5) { discard; }
	vec3 c = texture(capa, UV).rgb;
	if (hundido > 0.5) {
		float brillo = sin(px.x * 0.07 + TIME * 1.3) * sin(px.y * 0.11 - TIME * 0.9);
		c = mix(c, vec3(0.08, 0.16, 0.24), 0.22) + vec3(0.05, 0.07, 0.08) * smoothstep(0.75, 1.0, brillo);
		// junto a la orilla, la sombra del borde (se nota que el agua está más abajo)
		c *= mix(0.55, 1.0, smoothstep(0.5, 0.72, es_agua));
	} else {
		float ao = texture(mapa_ao, uv_mapa).r;
		c *= mix(1.0, 0.56, ao);
	}
	ALBEDO = c;
	ROUGHNESS = 1.0;
}
"""
## El suelo lejano (todo el mapa): igual, pero con el suelo pintado, la oclusión ambiental y el tinte de penumbra/noche
const SOMBREADOR_LEJANO := """
shader_type spatial;
render_mode diffuse_lambert, specular_disabled;
uniform sampler2D suelo : filter_nearest, source_color;
uniform sampler2D agua : filter_linear;
uniform sampler2D mapa_ao : filter_linear;
uniform vec3 tinte_2d = vec3(1.0);
uniform float hundido = 0.0;
void fragment() {
	float es_agua = texture(agua, UV).r;
	if (hundido < 0.5 && es_agua > 0.5) { discard; }
	if (hundido > 0.5 && es_agua <= 0.5) { discard; }
	vec3 c = texture(suelo, UV).rgb * tinte_2d;
	if (hundido > 0.5) {
		c = mix(c, vec3(0.08, 0.16, 0.24) * tinte_2d, 0.22) * mix(0.55, 1.0, smoothstep(0.5, 0.72, es_agua));
	} else {
		float ao = texture(mapa_ao, UV).r;
		c *= mix(1.0, 0.56, ao);
	}
	ALBEDO = c;
	ROUGHNESS = 1.0;
}
"""
## Sombreador 3D para los gemelos con mapa de normales (*_n.png):
## Conserva los colores exactos del pixel art al sol, proyecta y recibe sombras 3D suaves y reacciona con volumen
## tanto al sol/luna como a las luces puntuales 3D (OmniLight3D) de faroles, ventanas, braseros y fogatas.
const SOMBREADOR_GEMELO := """
shader_type spatial;
render_mode ambient_light_disabled, specular_disabled, cull_disabled;
uniform sampler2D tex_albedo : filter_nearest, source_color;
uniform sampler2D tex_normal : filter_nearest;
uniform vec3 tinte_ambiente = vec3(1.0);
uniform float usa_normal = 1.0;
uniform float volteo_x = 1.0;

void fragment() {
	vec4 c = texture(tex_albedo, UV);
	if (c.a < 0.5) {
		discard;
	}
	ALBEDO = c.rgb;
	ALPHA = c.a;
	ALPHA_SCISSOR_THRESHOLD = 0.5;
	ROUGHNESS = 1.0;
	vec3 n_vista = normalize(vec3(0.0, 0.68, 0.73));
	if (usa_normal > 0.5) {
		vec3 nm = texture(tex_normal, UV).rgb * 2.0 - 1.0;
		n_vista = normalize(vec3(nm.x * volteo_x * 0.58, 0.68 + nm.y * 0.58, max(0.25, 0.73 * nm.z)));
	}
	NORMAL = n_vista;
}

void light() {
	if (LIGHT_IS_DIRECTIONAL) {
		float relieve = (dot(NORMAL, LIGHT) - 0.50) * (usa_normal > 0.5 ? 0.38 : 0.10);
		float sombra_3d = mix(0.70, 1.0, ATTENUATION);
		DIFFUSE_LIGHT += tinte_ambiente * sombra_3d * clamp(1.0 + relieve, 0.76, 1.24);
	} else {
		float ndl = max(0.28, dot(NORMAL, LIGHT));
		DIFFUSE_LIGHT += LIGHT_COLOR * ATTENUATION * ndl * 0.95;
	}
}
"""
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
	"casa_shamba.png": [["v", 40, 96], ["v", 124, 96], ["f", 90, 95]],
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
	"estela.png": [["m", 33, 18]],
}
const CAMBIAN_AL_RECONSTRUIRSE_3D := ["casa_seta.png", "taller.png", "cocina.png", "puesto.png"]
const TIPOS_LUZ_3D := {
	"v": [5.2, 2.15, Color(1.0, 0.76, 0.38), false],
	"f": [6.8, 2.35, Color(1.0, 0.72, 0.35), false],
	"h": [8.2, 2.65, Color(1.0, 0.56, 0.22), true],
	"m": [5.4, 1.85, Color(0.45, 0.95, 0.85), false],
}
const HONDO_AGUA := 0.35             # metros que baja el agua
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
	float relevancia = lum * (0.42 + sat * 0.95 + calido * 0.75);
	float umbral = mix(0.36, 0.64, d) + nieve * d * 0.14;
	return s * smoothstep(umbral, umbral + 0.28, relevancia) * mascara_nieve;
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
		vec3 bloom = extraer_emision(col, dia, es_nieve) * 0.20;
		vec2 pb = paso * 3.2;
		bloom += extraer_emision(texture(pantalla, clamp(uv + vec2(pb.x, 0.0), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.13;
		bloom += extraer_emision(texture(pantalla, clamp(uv - vec2(pb.x, 0.0), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.13;
		bloom += extraer_emision(texture(pantalla, clamp(uv + vec2(0.0, pb.y), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.13;
		bloom += extraer_emision(texture(pantalla, clamp(uv - vec2(0.0, pb.y), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.13;
		if (calidad >= 2) {
			vec2 pd = pb * 1.45;
			bloom += extraer_emision(texture(pantalla, clamp(uv + vec2(pd.x, pd.y), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.07;
			bloom += extraer_emision(texture(pantalla, clamp(uv + vec2(-pd.x, pd.y), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.07;
			bloom += extraer_emision(texture(pantalla, clamp(uv + vec2(pd.x, -pd.y), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.07;
			bloom += extraer_emision(texture(pantalla, clamp(uv + vec2(-pd.x, -pd.y), vec2(0.001), vec2(0.999))).rgb, dia, es_nieve) * 0.07;
		}
		float fuerza_bloom = mix(0.46, 0.24, dia);
		col += bloom * fuerza_bloom;
		// 3. Etalonaje de color por hora y bioma (preservando el brillo central al sol)
		float noche = 1.0 - dia;
		vec3 sombra_tinte = mix(vec3(0.96, 0.97, 1.02), vec3(0.82, 0.88, 1.12), noche);
		vec3 luz_tinte = mix(vec3(1.0), vec3(1.08, 0.94, 0.82), calidez * 0.65);
		float lum_c = dot(col, vec3(0.299, 0.587, 0.114));
		col *= mix(sombra_tinte, luz_tinte, smoothstep(0.15, 0.75, lum_c));
		col *= mix(vec3(1.0), tinte_bioma, 0.45);
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
var _alto_pena := ALTO_PENA
var _mats_capa: Array[ShaderMaterial] = []
var _plano_agua: MeshInstance3D
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
static var _cache_normales := {}           # ruta -> Texture2D


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
	sol.directional_shadow_max_distance = 60.0
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
	_mat_penas.roughness = 1.0
	# el suelo: una sola malla del tamaño del mapa con el suelo pintado (con el agujero del agua) y, debajo, el agua
	var plano := PlaneMesh.new()
	plano.size = Vector2(ancho, alto)
	var lejano := Shader.new()
	lejano.code = SOMBREADOR_LEJANO
	_suelos_lejanos.clear()
	for hundido in [0.0, 1.0]:
		var m := ShaderMaterial.new()
		m.shader = lejano
		m.set_shader_parameter("suelo", tex)
		m.set_shader_parameter("hundido", hundido)
		_suelos_lejanos.append(m)
		var suelo := MeshInstance3D.new()
		suelo.mesh = plano
		suelo.material_override = m
		suelo.position = Vector3(ancho / 2.0, -HONDO_AGUA if hundido > 0.5 else 0.0, alto / 2.0)
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
						img_ao.set_pixel(x * 2 + dx, y * 2 + dy, Color(0.52, 0.52, 0.52, 1.0))
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


## Un tramo de peña de x0 a x1 (casillas) en la fila y: techo con el suelo pintado y paredes donde no hay peña al lado
func _bloque(st: SurfaceTool, lados: SurfaceTool, x0: int, x1: int, y: int, ancho: float, alto: float, filas: PackedStringArray) -> void:
	# En el dibujo 2D (vista 3/4) la peña ya está pintada como se vería: su pared del sur ocupa una franja de
	# «h» casillas dentro de la peña, y lo de encima está corrido hacia el norte esa misma altura. Por eso, en 3D:
	# el techo (a «h» de alto) toma el dibujo de «h» casillas más al norte, y la pared del sur, la franja pintada.
	var h := _alto_pena
	var uv := func(px: float, pz: float) -> Vector2: return Vector2(px / ancho, clampf(pz, 0.0, alto) / alto)
	_cuad(st, Vector3(x0, h, y), Vector3(x1, h, y), Vector3(x1, h, y + 1), Vector3(x0, h, y + 1),
		uv.call(x0, y - h), uv.call(x1, y - h), uv.call(x1, y + 1 - h), uv.call(x0, y + 1 - h))
	for x in range(x0, x1):
		if y + 1 >= filas.size() or filas[y + 1][x] != "0":
			_cuad(lados, Vector3(x, h, y + 1), Vector3(x + 1, h, y + 1), Vector3(x + 1, 0, y + 1), Vector3(x, 0, y + 1),
				uv.call(x, y + 1 - h), uv.call(x + 1, y + 1 - h), uv.call(x + 1, y + 1), uv.call(x, y + 1))
		if y == 0 or filas[y - 1][x] != "0":
			_cuad(lados, Vector3(x + 1, h, y), Vector3(x, h, y), Vector3(x, 0, y), Vector3(x + 1, 0, y),
				uv.call(x + 1, y - h), uv.call(x, y - h), uv.call(x, y), uv.call(x + 1, y))
	# los lados este y oeste: la pared pintada de la casilla de la esquina, estirada (se ven poco)
	if x0 > 0:
		_cuad(lados, Vector3(x0, h, y), Vector3(x0, h, y + 1), Vector3(x0, 0, y + 1), Vector3(x0, 0, y),
			uv.call(x0, y + 1 - h), uv.call(x0 + 1, y + 1 - h), uv.call(x0 + 1, y + 1), uv.call(x0, y + 1))
	if x1 < filas[y].length():
		_cuad(lados, Vector3(x1, h, y + 1), Vector3(x1, h, y), Vector3(x1, 0, y), Vector3(x1, 0, y + 1),
			uv.call(x1 - 1, y + 1 - h), uv.call(x1, y + 1 - h), uv.call(x1, y + 1), uv.call(x1 - 1, y + 1))


func _cuad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, ua := Vector2.ZERO, ub := Vector2.ZERO, uc := Vector2.ZERO, ud := Vector2.ZERO) -> void:
	var n := (b - a).cross(c - a).normalized() * -1.0
	for p in [[a, ua], [b, ub], [c, uc], [a, ua], [c, uc], [d, ud]]:
		st.set_normal(n)
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
	for hundido in [0.0, 1.0]:
		var mat := ShaderMaterial.new()
		mat.shader = sombreador
		mat.set_shader_parameter("capa", _capa_suelo.get_texture())
		mat.set_shader_parameter("agua", _mascara_agua)
		mat.set_shader_parameter("casillas", Vector2(_mascara_agua.get_width(), _mascara_agua.get_height()) if _mascara_agua else Vector2.ONE)
		mat.set_shader_parameter("lado", float(LADO_CAPA))
		mat.set_shader_parameter("hundido", hundido)
		_mats_capa.append(mat)
		var p := MeshInstance3D.new()
		p.mesh = plano
		p.material_override = mat
		p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(p)
		if hundido > 0.5:
			_plano_agua = p
		else:
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
	_plano_capa.position = Vector3(centro.x * PX, 0.005, centro.y * PX)
	_plano_agua.position = Vector3(centro.x * PX, -HONDO_AGUA, centro.y * PX)
	for mat in _mats_capa:
		mat.set_shader_parameter("origen", centro - Vector2(LADO_CAPA, LADO_CAPA) / 2.0)
	_capa_pantalla.canvas_transform = escena.get_viewport().canvas_transform
	# las ventanitas: para los objetos de pie más cercanos a la cámara, cada una mirando su trocito de la escena
	var cerca := []
	for id in _de_pie.keys():
		var c: Node2D = _de_pie[id]
		if not is_instance_valid(c):
			_de_pie.erase(id)
			continue
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


# --- La cámara ------------------------------------------------------------------------------------------------

func _crear_camara() -> void:
	camara = Camera3D.new()
	camara.fov = CAMARA_FOV
	camara.rotation_degrees = Vector3(CAMARA_INCLINACION, 0, 0)
	add_child(camara)
	camara.current = true
	if _maisha:
		_foco = _al_suelo(_maisha.global_position)
	_colocar_camara(1.0)


func _colocar_camara(suave: float) -> void:
	if _maisha and is_instance_valid(_maisha):
		_foco = _foco.lerp(_al_suelo(_maisha.global_position), suave)
	# sin salirse del mapa (como la cámara 2D): deja un margen de media pantalla a cada lado
	if region:
		var tam: Vector2 = region.get("tam") * PX
		var mx := minf(16.0, tam.x / 2.0)
		_foco.x = clampf(_foco.x, mx, tam.x - mx)
		_foco.z = clampf(_foco.z, minf(7.0, tam.y / 2.0), tam.y - minf(11.0, tam.y / 2.0))
	var atras := camara.global_transform.basis.z * CAMARA_DISTANCIA
	camara.global_position = _foco + atras


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


func _material_relieve(tex: Texture2D, tex_n: Texture2D, flip_h: bool) -> ShaderMaterial:
	var clave := "%d_%d" % [tex.get_instance_id(), 1 if flip_h else 0]
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
	mat.set_shader_parameter("tinte_ambiente", Vector3(_tinte.r, _tinte.g, _tinte.b))
	_cache_mat_relieve[clave] = mat
	return mat


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


func _registrar_luces_sprite(s: Sprite2D, tex: Texture2D) -> void:
	if tex == null:
		return
	var arch := tex.resource_path.get_file()
	if not LUCES_3D.has(arch):
		return
	var padre := s.get_parent()
	if padre and padre.get_script() and String(padre.get_script().resource_path).ends_with("farol_runico.gd"):
		return
	_rehacer_luces_sprite(s, tex, LUCES_3D[arch])
	if arch in CAMBIAN_AL_RECONSTRUIRSE_3D and not s.frame_changed.is_connected(_rehacer_luces_sprite):
		s.frame_changed.connect(_rehacer_luces_sprite.bind(s, tex, LUCES_3D[arch]))


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
			var f := pow(1.0 - dist / rango, 1.6) * omni.light_energy * 0.28
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
			var f := pow(1.0 - dist / omni_pt.omni_range, 1.6) * omni_pt.light_energy * 0.24
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
	if not (n is Sprite2D or n is AnimatedSprite2D) or _z(n) < SUELO_BAJO:
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
		var tex_n: Texture2D = null
		if tex_s is CanvasTexture:
			tex_n = (tex_s as CanvasTexture).normal_texture
			tex_s = (tex_s as CanvasTexture).diffuse_texture
		else:
			tex_n = _textura_normal_de(tex_s)
		_registrar_luces_sprite.call_deferred(s, tex_s)
		var arch := tex_s.resource_path.get_file() if tex_s else ""
		if n.get_script() == null and ancla is StaticBody2D and ancla.get_script() == null:
			if not (arch in ["casa_seta.png", "taller.png", "cocina.png", "puesto.png", "farol.png", "transbordador.png"]):
				estatico = true
			if tex_s:
				var alto_f := (s.region_rect.size.y if s.region_enabled else tex_s.get_height() / float(maxi(s.vframes, 1)))
				if alto_f <= 14.0:
					g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				elif tex_n != null and s.hframes == 1 and s.vframes == 1 and not s.region_enabled:
					g.material_override = _material_relieve(tex_s, tex_n, s.flip_h)
		elif tex_n != null and s.hframes == 1 and s.vframes == 1 and not s.region_enabled and ancla is StaticBody2D:
			g.material_override = _material_relieve(tex_s, tex_n, s.flip_h)
	if estatico:
		g.visibility_range_end = 38.0
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
	for m_lej in _suelos_lejanos:
		m_lej.set_shader_parameter("tinte_2d", Vector3(tinte_roca.r, tinte_roca.g, tinte_roca.b))
	_colocar_camara(0.12)
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
				continue
			if absf(g_e.position.x - _foco.x) > LEJOS or absf(g_e.position.z - _foco.z) > LEJOS:
				continue
			var luz_e := _luz_en_punto(g_e.position)
			var tf_e := Color(minf(1.3, _tinte.r + luz_e.r), minf(1.25, _tinte.g + luz_e.g), minf(1.2, _tinte.b + luz_e.b), 1.0)
			g_e.modulate = (pe[4] as Color) * tf_e
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
	_mover_capas()
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
		tex = (tex as CanvasTexture).diffuse_texture          # (en 3D, el relieve va en SOMBREADOR_GEMELO)
	g.texture = tex
	g.flip_h = n.flip_h
	g.flip_v = n.flip_v
	g.centered = n.centered
	var escala := n.global_scale
	g.scale = Vector3(escala.x, escala.y, 1.0)
	# de pie: apoyado en el suelo de su cuerpo; lo que en 2D está más arriba que el cuerpo, en 3D está más alto
	var sube: Vector2 = n.global_position - ancla.global_position
	var o2: Vector2 = n.offset + Vector2(sube.x, sube.y)
	# (en 2D la «y» crece hacia abajo y en 3D hacia arriba: sin centrar, el dibujo va de o2.y a o2.y + alto en 2D,
	# así que en 3D su borde de abajo está en -(o2.y + alto); centrado, se queda donde está, solo cambia el signo)
	var alto := 0.0
	if not g.centered and tex:
		alto = (g.region_rect.size.y if g.region_enabled else tex.get_height() / float(maxi(g.vframes, 1)))
	g.offset = Vector2(o2.x, -(o2.y + alto))
	# (las capas de un mismo cuerpo, un pelín hacia la cámara según su orden de dibujo, para que no parpadeen)
	var orden := z * 0.004 + n.get_index() * 0.0015
	g.position = _al_suelo(ancla.global_position) + Vector3(0, 0, orden)
	var luz_p := _luz_en_punto(g.position)
	var tf := Color(minf(1.3, _tinte.r + luz_p.r), minf(1.25, _tinte.g + luz_p.g), minf(1.2, _tinte.b + luz_p.b), 1.0)
	g.modulate = n.modulate * n.self_modulate * tf

