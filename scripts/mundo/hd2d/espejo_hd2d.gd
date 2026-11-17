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
const PARED_DOBLE := ["canada_eco", "paso_piedra", "sendero_olvidado", "ruinas_primer_arbol", "paso_escarcha", "maandiko", "canal_tinta"]
## Mapas con altura de pared propia en casillas (p. ej. Sección Prohibida: estanterías de 24 px = 1,5 casillas)
const ALTO_MAPA := {
	"seccion_prohibida": 1.5,
	"desfiladero_meteorito": 1.625,
	"mji_jiwe": 0.75,
	"galerias_ambar": 1.625,
	"fundicion_escoria": 1.625,
}
## Mapas en los que «0» no es peña sino cielo o vacío (no se levantan bloques de roca)
const SIN_PENAS := ["observatorio_aurora", "aguja_caida"]
const SUELO_BAJO := -4             # dibujos con z_index <= SUELO_BAJO: se tumban en el suelo
const PLATAFORMAS := ["barcaza.gd", "penasco.gd"] # plataformas elevadas sobre vacío o escoria
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
	"recogible.gd", "arco_ruinas.gd", "portal.gd", "aldeano.gd", "taa.gd", "vecino.gd", "escriba.gd",
	"bobina.gd", "saa.gd", "grimorio_tinta.gd", "rasgos_maisha.gd", "kimya.gd", "roca_mineral.gd", "escarcha.gd",
	"piedra_recuerdo.gd", "primer_arbol.gd", "buibui.gd", "guardian.gd", "kambare.gd", "mamba.gd",
	"cangrejo.gd", "rescoldo.gd", "espinas_paso.gd", "gallina_perdida.gd", "barca_bata.gd", "chispa_golpe.gd",
	"nyundo.gd", "popo.gd", "pluma_cuchilla.gd"]
const VENTANA := Vector2i(320, 288)       # píxeles de cada ventanita (cubre tenazas de Nyundo y ondas de Popo)
const VENTANA_PIE := Vector2(160, 176)     # dónde cae el pie del objeto dentro de la ventanita
const VENTANAS := 14                      # como mucho, las de los 14 objetos de pie más cerca de la cámara
const LADO_CAPA := 1024            # píxeles de la capa de suelo (64 m alrededor de Maisha)
## El suelo cercano: la capa de suelo, con luz (para las sombras)
## Con «hundido» = 0 es el suelo, con un agujero donde hay agua o escoria; con 1, el agua o la escoria fundida.
## «agua» es la máscara del mapa (1 píxel por casilla).
const SOMBREADOR_CAPA := """
shader_type spatial;
render_mode diffuse_lambert, specular_disabled;
uniform sampler2D capa : filter_nearest;
uniform sampler2D agua : filter_linear;
uniform vec2 origen = vec2(0.0);
uniform vec2 casillas = vec2(1.0);
uniform float lado = 1024.0;
uniform float hundido = 0.0;
uniform float hay_agua = 1.0;
uniform float es_escoria = 0.0;
void fragment() {
	vec3 c = texture(capa, UV).rgb;
	vec3 emision = vec3(0.0);
	if (hay_agua > 0.5) {
		vec2 px = origen + UV * lado;
		// (la máscara, suavizada y con un temblor, para que la orilla sea curva como la pintada y no en escalones)
		float temblor = sin(px.x * 0.37 + px.y * 0.21) * 0.06 + sin(px.y * 0.53 - px.x * 0.17) * 0.05;
		float es_agua = texture(agua, px / 16.0 / casillas).r + temblor;
		if (hundido < 0.5 && es_agua > 0.5) { discard; }
		if (hundido > 0.5 && es_agua <= 0.5) { discard; }
		if (hundido > 0.5) {
			float orilla = smoothstep(0.5, 0.72, es_agua);
			if (es_escoria > 0.5) {
				float pulso = 0.5 + 0.5 * sin(px.x * 0.05 + TIME * 1.1) * cos(px.y * 0.06 - TIME * 0.8);
				c = c * (1.0 + 0.14 * pulso) + vec3(0.14, 0.04, 0.0) * smoothstep(0.5, 1.0, pulso);
				c *= mix(0.62, 1.0, orilla);
				emision = c * 0.15 * orilla;
			} else {
				float brillo = sin(px.x * 0.07 + TIME * 1.3) * sin(px.y * 0.11 - TIME * 0.9);
				c = mix(c, vec3(0.08, 0.16, 0.24), 0.22) + vec3(0.05, 0.07, 0.08) * smoothstep(0.75, 1.0, brillo);
				// junto a la orilla, la sombra del borde (se nota que el agua está más abajo)
				c *= mix(0.55, 1.0, orilla);
			}
		}
	} else if (hundido > 0.5) {
		discard;
	}
	ALBEDO = c;
	EMISSION = emision;
	ROUGHNESS = 1.0;
}
"""
## Ventanita de pie (Rasgos / efectos con código): deshace el alfa premultiplicado del SubViewport para no oscurecer brillos
const SOMBREADOR_PIE := """
shader_type spatial;
render_mode unshaded, depth_draw_never, cull_disabled, blend_mix;
uniform sampler2D ventana : filter_nearest;
void vertex() {
	vec3 cam_z = normalize(vec3(INV_VIEW_MATRIX[2].x, 0.0, INV_VIEW_MATRIX[2].z));
	vec3 cam_x = normalize(cross(vec3(0.0, 1.0, 0.0), cam_z));
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(
		vec4(cam_x, 0.0),
		vec4(0.0, 1.0, 0.0, 0.0),
		vec4(cam_z, 0.0),
		MODEL_MATRIX[3]
	);
}
void fragment() {
	vec4 c = texture(ventana, UV);
	if (c.a <= 0.002) { discard; }
	ALBEDO = clamp(c.rgb / c.a, 0.0, 1.0);
	ALPHA = c.a;
}
"""
## El suelo lejano (todo el mapa): igual, pero con el suelo pintado y la máscara a la medida del mapa
const SOMBREADOR_LEJANO := """
shader_type spatial;
render_mode diffuse_lambert, specular_disabled;
uniform sampler2D suelo : filter_nearest, source_color;
uniform sampler2D agua : filter_linear;
uniform float hundido = 0.0;
uniform float es_escoria = 0.0;
uniform vec4 tinte : source_color = vec4(1.0);
void fragment() {
	float es_agua = texture(agua, UV).r;
	if (hundido < 0.5 && es_agua > 0.5) { discard; }
	if (hundido > 0.5 && es_agua <= 0.5) { discard; }
	vec3 c = texture(suelo, UV).rgb * tinte.rgb;
	vec3 emision = vec3(0.0);
	if (hundido > 0.5) {
		float orilla = smoothstep(0.5, 0.72, es_agua);
		if (es_escoria > 0.5) {
			c = c * 1.08 * mix(0.62, 1.0, orilla);
			emision = c * 0.14 * orilla;
		} else {
			c = mix(c, vec3(0.08, 0.16, 0.24) * tinte.rgb, 0.22) * mix(0.55, 1.0, orilla);
		}
	}
	ALBEDO = c;
	EMISSION = emision;
	ROUGHNESS = 1.0;
}
"""
const HONDO_AGUA := 0.35             # metros que baja el agua
const LETRAS_AGUA := "~\\"
## Dibujos de pantalla (por su script): van a la capa de pantalla, con sus hijos
const DE_PANTALLA := ["ambiente.gd", "nevada.gd", "ventisca.gd", "luz_sol.gd"]
const EDIFICIOS := preload("res://scripts/mundo/hd2d/edificios_hd2d.gd")

var escena: Node2D
var region: Node2D
var camara: Camera3D
var sol: DirectionalLight3D
var _gemelos := {}                 # id del dibujo 2D -> [nodo, gemelo 3D, ancla, z, edificio]
var _edificios: EDIFICIOS = EDIFICIOS.new()
var _maisha: Node2D
var _foco := Vector3.ZERO
var _alto_pena := ALTO_PENA
var _mats_capa: Array[ShaderMaterial] = []
var _plano_agua: MeshInstance3D
var _mascara_agua: ImageTexture
var _es_escoria := false
var _suelos_lejanos: Array[ShaderMaterial] = []
var _mat_penas: StandardMaterial3D
var _entorno: Environment
var _fondo_base := Color.BLACK
var _mod_escena := Color.WHITE
var _moduladores: Array[CanvasModulate] = []
var _luces_2d: Array[PointLight2D] = []
var _luz_muros: OmniLight3D
var _canales := {}                 # id de cada dibujo -> [dibujo, su canal de antes] (para devolverlo al apagar)
var _capa_suelo: SubViewport
var _plano_capa: MeshInstance3D
var _capa_pantalla: SubViewport
var _ventanas: Array = []          # [SubViewport, MeshInstance3D] (se reparten entre los objetos de pie más cercanos)
var _de_pie := {}                  # id del objeto de pie (su cuerpo) -> el cuerpo
var _velo_pantalla: CanvasLayer
var _mascara_antes := 0xFFFFFFFF
var _motas_mm: MultiMesh
var _motas_datos: Array = []
var _motas_t := 0.0


func _ready() -> void:
	region = escena.get_node_or_null("Region")
	_maisha = escena.get_tree().get_first_node_in_group("maisha") as Node2D
	_crear_ambiente()
	_crear_suelo()
	_crear_camara()
	_crear_capas()
	_crear_motas()
	for n in _todos(escena):
		_registrar(n)
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
	var entorno := Environment.new()
	entorno.background_mode = Environment.BG_COLOR
	_fondo_base = Color.BLACK if region == null else RenderingServer.get_default_clear_color()
	entorno.background_color = _fondo_base
	_entorno = entorno
	entorno.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	entorno.ambient_light_color = Color(1, 1, 1)
	entorno.ambient_light_energy = 0.4     # (medido: con esto y el sol, el suelo al sol sale igual de claro que en 2D)
	entorno.tonemap_mode = Environment.TONE_MAPPER_LINEAR      # (los colores del pixel art, tal cual)
	entorno.fog_enabled = false        # (la niebla aclaraba los oscuros: la del juego ya la pinta la capa de pantalla)
	entorno.glow_enabled = false
	var mundo := WorldEnvironment.new()
	mundo.environment = entorno
	add_child(mundo)
	sol = DirectionalLight3D.new()
	sol.shadow_enabled = true
	sol.light_energy = 0.27
	sol.light_color = Color(1.0, 0.95, 0.86)
	sol.rotation_degrees = Vector3(-50, -35, 0)          # (desde arriba a la izquierda y algo por detrás: sombras hacia delante y a la derecha, como las pintadas)
	sol.directional_shadow_max_distance = 60.0
	add_child(sol)
	# (en cuevas o de noche, un resplandor suave alrededor de Maisha solo sobre los muros para que la roca cercana se distinga)
	_luz_muros = OmniLight3D.new()
	_luz_muros.light_cull_mask = 2
	_luz_muros.omni_range = 7.5
	_luz_muros.omni_attenuation = 1.6
	_luz_muros.light_color = Color(1.0, 0.9, 0.72)
	_luz_muros.light_energy = 0.65
	_luz_muros.visible = false
	add_child(_luz_muros)


# --- El suelo y las peñas -------------------------------------------------------------------------------------

func _textura_suelo() -> Texture2D:
	var mundo := String(region.get("mundo")) if region and region.get("mundo") else "raiz"
	var ruta := "res://arte/mundos/%s/suelos/%s_suelo.png" % [mundo, String(region.get("mapa"))]
	return load(ruta) if region and ResourceLoader.exists(ruta) else null


func _crear_suelo() -> void:
	if region == null:
		return
	var tex := _textura_suelo()
	var mapa_n := String(region.get("mapa"))
	_es_escoria = mapa_n == "fundicion_escoria"
	_alto_pena = float(ALTO_MAPA.get(mapa_n, ALTO_PENA * (2.0 if mapa_n in PARED_DOBLE else 1.0)))
	var filas: PackedStringArray = region.get("_filas")
	var ancho: float = filas[0].length()
	var alto: float = filas.size()
	var mat := StandardMaterial3D.new()
	mat.albedo_texture = tex
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	mat.roughness = 1.0
	_mat_penas = mat
	# el suelo: una sola malla del tamaño del mapa con el suelo pintado (con el agujero del agua o escoria) y, debajo, lo hundido
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
		m.set_shader_parameter("es_escoria", 1.0 if _es_escoria else 0.0)
		_suelos_lejanos.append(m)
		var suelo := MeshInstance3D.new()
		suelo.mesh = plano
		suelo.material_override = m
		suelo.position = Vector3(ancho / 2.0, -HONDO_AGUA if hundido > 0.5 else 0.0, alto / 2.0)
		add_child(suelo)
	# el agua / escoria fundida: una máscara (1 píxel por casilla) para hundirla
	var img := Image.create(int(ancho), int(alto), false, Image.FORMAT_L8)
	for y in filas.size():
		for x in filas[y].length():
			var c := filas[y][x]
			var hundir := (c == "≈" or (c == "=" and y >= 32 and y <= 46 and x >= 36 and x <= 48)) if _es_escoria else LETRAS_AGUA.contains(c)
			if not hundir:
				continue
			img.set_pixel(x, y, Color.WHITE)
	_mascara_agua = ImageTexture.create_from_image(img)
	for m in _suelos_lejanos:
		m.set_shader_parameter("agua", _mascara_agua)
	# las peñas: bloques que se levantan, con el suelo pintado encima y los lados de roca oscura
	# (salvo en mapas como observatorio_aurora o aguja_caida donde «0» es el cielo o el vacío)
	if not String(region.get("mapa")) in SIN_PENAS:
		var st := SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		var lados := SurfaceTool.new()
		lados.begin(Mesh.PRIMITIVE_TRIANGLES)
		for y in filas.size():
			var x := 0
			var fila := filas[y]
			while x < fila.length():
				if not _es_pena(filas, x, y):
					x += 1
					continue
				var x0 := x
				while x < fila.length() and _es_pena(filas, x, y):
					x += 1
				_bloque(st, lados, x0, x, y, ancho, alto, filas)
		var techo := MeshInstance3D.new()
		techo.mesh = st.commit()
		techo.material_override = mat
		techo.layers = 2
		add_child(techo)
		# las paredes: la del sur, con la pared de roca que ya está pintada en el suelo; las demás, de roca oscura
		var paredes := MeshInstance3D.new()
		paredes.mesh = lados.commit()
		paredes.material_override = mat
		paredes.layers = 2
		add_child(paredes)


func _es_pena(filas: PackedStringArray, x: int, y: int) -> bool:
	if y < 0 or y >= filas.size() or x < 0 or x >= filas[y].length():
		return false
	if _es_escoria and x >= 59 and y >= 34 and y <= 48:
		return false
	return filas[y][x] == "0"


## Un tramo de peña de x0 a x1 (casillas) en la fila y: techo con el suelo pintado y paredes donde no hay peña al lado
func _bloque(st: SurfaceTool, lados: SurfaceTool, x0: int, x1: int, y: int, ancho: float, alto: float, filas: PackedStringArray) -> void:
	# En el dibujo 2D (vista 3/4) la peña ya está pintada como se vería: su pared del sur ocupa una franja de
	# «h» casillas dentro de la peña, y lo de encima está corrido hacia el norte esa misma altura. Por eso, en 3D:
	# el techo (a «h» de alto) toma el dibujo de «h» casillas más al norte, y la pared del sur, la franja pintada.
	var h := _alto_pena
	var uv := func(px: float, pz: float) -> Vector2: return Vector2(px / ancho, clampf(pz, 0.0, alto) / alto)
	var z_top := float(y) - h
	var z_bot := float(y + 1) - h
	if z_bot <= 0.0:
		# Cerca del borde norte: refleja hacia dentro para conservar la escala 1:1 sin estirar la fila 0
		z_top = clampf(-z_top, 0.0, alto)
		z_bot = clampf(-z_bot, 0.0, alto)
	elif z_top < 0.0:
		z_top = 0.0
	_cuad(st, Vector3(x0, h, y), Vector3(x1, h, y), Vector3(x1, h, y + 1), Vector3(x0, h, y + 1),
		uv.call(x0, z_top), uv.call(x1, z_top), uv.call(x1, z_bot), uv.call(x0, z_bot))
	for x in range(x0, x1):
		if y + 1 >= filas.size() or not _es_pena(filas, x, y + 1):
			_cuad(lados, Vector3(x, h, y + 1), Vector3(x + 1, h, y + 1), Vector3(x + 1, 0, y + 1), Vector3(x, 0, y + 1),
				uv.call(x, y + 1 - h), uv.call(x + 1, y + 1 - h), uv.call(x + 1, y + 1), uv.call(x, y + 1))
		if y == 0 or not _es_pena(filas, x, y - 1):
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
	var hay_agua := _mascara_agua != null
	var agua_tex: Texture2D = _mascara_agua if hay_agua else ImageTexture.create_from_image(Image.create(1, 1, false, Image.FORMAT_L8))
	var capas_hundido: Array = [0.0, 1.0] if hay_agua else [0.0]
	for hundido: float in capas_hundido:
		var mat := ShaderMaterial.new()
		mat.shader = sombreador
		mat.set_shader_parameter("capa", _capa_suelo.get_texture())
		mat.set_shader_parameter("agua", agua_tex)
		mat.set_shader_parameter("casillas", Vector2(_mascara_agua.get_width(), _mascara_agua.get_height()) if hay_agua else Vector2.ONE)
		mat.set_shader_parameter("lado", float(LADO_CAPA))
		mat.set_shader_parameter("hundido", hundido)
		mat.set_shader_parameter("hay_agua", 1.0 if hay_agua else 0.0)
		mat.set_shader_parameter("es_escoria", 1.0 if _es_escoria else 0.0)
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
	# las ventanitas de lo que va de pie (malla doblada: la mitad superior de pie y el borde inferior a ras del suelo)
	var sombreador_pie := Shader.new()
	sombreador_pie.code = SOMBREADOR_PIE
	var malla_pie := _malla_pie()
	for i in VENTANAS:
		var v := SubViewport.new()
		v.size = VENTANA
		v.transparent_bg = true
		v.world_2d = vista.world_2d
		v.canvas_cull_mask = CANAL_PIE
		v.render_target_update_mode = SubViewport.UPDATE_DISABLED
		v.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
		add_child(v)
		var g := MeshInstance3D.new()
		g.mesh = malla_pie
		var mat_pie := ShaderMaterial.new()
		mat_pie.shader = sombreador_pie
		mat_pie.set_shader_parameter("ventana", v.get_texture())
		g.material_override = mat_pie
		g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		g.visible = false
		add_child(g)
		_ventanas.append([v, g])
	# la pantalla principal deja de pintar el mundo 2D (sigue vivo y viéndose en las capas); la interfaz, sí
	if vista.has_meta("_hd2d_mascara_antes"):
		_mascara_antes = int(vista.get_meta("_hd2d_mascara_antes"))
	else:
		_mascara_antes = vista.canvas_cull_mask
		vista.set_meta("_hd2d_mascara_antes", _mascara_antes)
	vista.canvas_cull_mask = _mascara_antes & ~CANALES_MUNDO


func _malla_pie() -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var x_l := -VENTANA_PIE.x * PX
	var x_r := (VENTANA.x - VENTANA_PIE.x) * PX
	var y_pie := 0.02
	var y_top := y_pie + VENTANA_PIE.y * PX
	var z_bot := (VENTANA.y - VENTANA_PIE.y) * PX
	var v_pie := VENTANA_PIE.y / float(VENTANA.y)
	_cuad(st, Vector3(x_l, y_top, 0.0), Vector3(x_r, y_top, 0.0), Vector3(x_r, y_pie, 0.0), Vector3(x_l, y_pie, 0.0),
		Vector2(0.0, 0.0), Vector2(1.0, 0.0), Vector2(1.0, v_pie), Vector2(0.0, v_pie))
	_cuad(st, Vector3(x_l, y_pie, 0.0), Vector3(x_r, y_pie, 0.0), Vector3(x_r, y_pie, z_bot), Vector3(x_l, y_pie, z_bot),
		Vector2(0.0, v_pie), Vector2(1.0, v_pie), Vector2(1.0, 1.0), Vector2(0.0, 1.0))
	return st.commit()


func _mover_capas() -> void:
	# la capa de suelo, centrada en el foco (a píxeles enteros, para que no tiemble)
	var centro := Vector2(roundf(_foco.x / PX), roundf(_foco.z / PX))
	_capa_suelo.canvas_transform = Transform2D(0.0, -(centro - Vector2(LADO_CAPA, LADO_CAPA) / 2.0))
	_plano_capa.position = Vector3(centro.x * PX, 0.005, centro.y * PX)
	if _plano_agua:
		_plano_agua.position = Vector3(centro.x * PX, -HONDO_AGUA + 0.005, centro.y * PX)
	for mat in _mats_capa:
		mat.set_shader_parameter("origen", centro - Vector2(LADO_CAPA, LADO_CAPA) / 2.0)
	_capa_pantalla.canvas_transform = escena.get_viewport().canvas_transform
	# las ventanitas: para los objetos de pie más cercanos a la cámara, cada una mirando su trocito de la escena
	var cerca := []
	for id in _de_pie.keys():
		# (comprobarlo antes de guardarlo en una variable Node2D: guardar uno ya borrado da error y corta la función)
		if not is_instance_valid(_de_pie[id]):
			_de_pie.erase(id)
			continue
		var c: Node2D = _de_pie[id]
		var d := _al_suelo(c.global_position).distance_to(_foco)
		if d < LEJOS * 0.7:
			cerca.append([d, c])
	cerca.sort_custom(func(a: Array, b: Array) -> bool: return a[0] < b[0])
	for i in _ventanas.size():
		var v: SubViewport = _ventanas[i][0]
		var g: MeshInstance3D = _ventanas[i][1]
		if i >= cerca.size():
			g.visible = false
			v.render_target_update_mode = SubViewport.UPDATE_DISABLED
			continue
		v.render_target_update_mode = SubViewport.UPDATE_ALWAYS
		var c: Node2D = cerca[i][1]
		var pie := c.global_position.round()
		v.canvas_transform = Transform2D(0.0, -(pie - VENTANA_PIE))
		g.position = _al_suelo(pie) + Vector3(0, 0, 0.06)        # (un pelín hacia la cámara: por delante de su dibujo)
		g.visible = true


func _exit_tree() -> void:
	# todo como estaba: solo restauramos la máscara si no queda otro espejo activo (evita carrera al pulsar H rápido)
	var otro_activo := false
	for h in get_tree().root.get_children():
		if h != self and not h.is_queued_for_deletion() and h.get_script() == get_script():
			otro_activo = true
			break
	if not otro_activo:
		var v := escena.get_viewport() if is_instance_valid(escena) and escena.is_inside_tree() else get_viewport()
		if v:
			v.canvas_cull_mask = _mascara_antes
			v.remove_meta("_hd2d_mascara_antes")
	for par in _canales.values():
		if is_instance_valid(par[0]):
			(par[0] as CanvasItem).visibility_layer = par[1]
	_edificios.limpiar()


# --- La cámara ------------------------------------------------------------------------------------------------

func _objetivo_camara() -> Vector2:
	if region == null and is_instance_valid(escena):
		var cam := escena.get_viewport().get_camera_2d()
		if cam and (not is_instance_valid(_maisha) or not _maisha.is_ancestor_of(cam)):
			return cam.get_screen_center_position() + Impacto.encuadre
	if is_instance_valid(_maisha):
		return _maisha.global_position + Impacto.encuadre
	return Vector2.ZERO


func _crear_camara() -> void:
	camara = Camera3D.new()
	camara.fov = CAMARA_FOV
	camara.rotation_degrees = Vector3(CAMARA_INCLINACION, 0, 0)
	add_child(camara)
	camara.current = true
	_foco = _al_suelo(_objetivo_camara())
	_colocar_camara(1.0)


func _colocar_camara(suave: float) -> void:
	var objetivo := _objetivo_camara()
	if objetivo != Vector2.ZERO or is_instance_valid(_maisha):
		_foco = _foco.lerp(_al_suelo(objetivo), suave)
	# sin salirse del mapa (como la cámara 2D): cubre la proyección completa (-33° norte ~ 14.5m, -63° sur ~ 9m)
	if region:
		var tam: Vector2 = region.get("tam") * PX
		var mx := 15.0
		_foco.x = tam.x / 2.0 if mx * 2.0 >= tam.x else clampf(_foco.x, mx, tam.x - mx)
		var z_min := 14.5
		var z_max := tam.y - 9.0
		_foco.z = tam.y / 2.0 if z_min >= z_max else clampf(_foco.z, z_min, z_max)
	var atras := camara.global_transform.basis.z * CAMARA_DISTANCIA
	camara.global_position = _foco + atras


func _al_suelo(p: Vector2) -> Vector3:
	return Vector3(p.x * PX, 0.0, p.y * PX)


# --- Los gemelos de los dibujos -------------------------------------------------------------------------------

func _registrar(n: Node) -> void:
	if n is CanvasModulate:
		var cm := n as CanvasModulate
		if escena.is_ancestor_of(cm) and not _moduladores.has(cm):
			_moduladores.append(cm)
	elif n is PointLight2D:
		var luz := n as PointLight2D
		if escena.is_ancestor_of(luz) and not _luces_2d.has(luz):
			_luces_2d.append(luz)
	if not (n is CanvasItem) or not escena.is_ancestor_of(n) or _en_interfaz(n):
		return
	var ci := n as CanvasItem
	if not _canales.has(ci.get_instance_id()):
		_canales[ci.get_instance_id()] = [ci, ci.visibility_layer]
	# ¿a qué capa va?
	if n.get_script() and String(n.get_script().resource_path).ends_with("sombra.gd"):
		ci.visibility_layer = CANAL_NADA
		return
	if _de_pantalla(n):
		ci.visibility_layer = CANAL_PANTALLA
		return
	var plat := (n is Sprite2D or n is AnimatedSprite2D) and _es_plataforma(n)
	var plano_suelo := n is Sprite2D and (n as Sprite2D).texture != null and String((n as Sprite2D).texture.resource_path).ends_with("/placa.png")
	if not plat and (plano_suelo or not (n is Sprite2D or n is AnimatedSprite2D) or _z(n) <= SUELO_BAJO):
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
	if _gemelos.has(n.get_instance_id()):
		return
	var edif := "__plataforma__" if plat else _edificios.nombre_catalogo(n as Node2D)
	var g: GeometryInstance3D
	if plat:
		g = _crear_plataforma_gemelo()
	elif edif != "":
		g = _edificios.crear_gemelo()
	else:
		g = _crear_sprite_gemelo()
	add_child(g)
	# (lo que no cambia: el cuerpo en el que se apoya y su orden de dibujo; se calcula una vez)
	_gemelos[n.get_instance_id()] = [n, g, null, _z(n), edif]


func _es_plataforma(n: Node) -> bool:
	var p := n.get_parent()
	if p == null or p.get_script() == null:
		return false
	var s: Script = p.get_script()
	while s:
		var ruta := String(s.resource_path)
		for nombre in PLATAFORMAS:
			if ruta.ends_with("/" + nombre):
				return true
		s = s.get_base_script()
	return false


func _crear_plataforma_gemelo() -> MeshInstance3D:
	var g := MeshInstance3D.new()
	var plano := PlaneMesh.new()
	plano.size = Vector2.ONE
	g.mesh = plano
	var mat := StandardMaterial3D.new()
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	mat.alpha_scissor_threshold = 0.5
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	mat.roughness = 1.0
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	g.material_override = mat
	g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	return g


func _crear_sprite_gemelo() -> Sprite3D:
	var g := Sprite3D.new()
	g.pixel_size = PX
	g.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	g.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	g.shaded = false                 # (sus colores de pixel art; de noche se oscurecen con «_tinte»)
	g.double_sided = true
	g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	g.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	return g


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
	var candidatos: Array[Node] = [n]
	# Un hijo «top_level» (rastros o capas en el suelo) vive en el mundo, no sobre el cuerpo del padre
	if not (n is Node2D and (n as Node2D).top_level):
		candidatos.append(n.get_parent())
	for c in candidatos:
		if c and c != escena and c.get_script():
			var s: Script = c.get_script()
			while s:
				var ruta := String(s.resource_path)
				for nombre in DE_PIE:
					if ruta.ends_with("/" + nombre):
						return c
				s = s.get_base_script()
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
	if n is CanvasModulate:
		_moduladores.erase(n)
	elif n is PointLight2D:
		_luces_2d.erase(n)
	var id := n.get_instance_id()
	_canales.erase(id)
	if _gemelos.has(id):
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


func _process(_delta: float) -> void:
	for id in _gemelos.keys():
		var par: Array = _gemelos[id]
		var n: Node2D = par[0]
		var g: GeometryInstance3D = par[1]
		if not is_instance_valid(n):
			g.queue_free()
			_gemelos.erase(id)
			continue
		# (solo los que están cerca de la cámara: los demás, ocultos y sin copiar; así no pesa en los mapas grandes)
		var p := n.global_position * PX
		if absf(p.x - _foco.x) > LEJOS or absf(p.y - _foco.z) > LEJOS:
			g.visible = false
			continue
		if par[2] == null or not is_instance_valid(par[2]):
			par[2] = _ancla(n)
		var edif := String(par[4])
		if edif == "__plataforma__":
			_copiar_plataforma(n, g as MeshInstance3D)
		elif edif != "":
			_edificios.copiar(n, g as MeshInstance3D, par[2], par[3], _visible(n), _al_suelo(par[2].global_position), _tinte_sprite(n))
		else:
			_copiar(n, g as Sprite3D, par[2], par[3])
	_colocar_camara(0.12)
	_mover_capas()
	_actualizar_motas(_delta)
	# La capa 2D del suelo y las ventanitas ya reciben LuzDelDia / Penumbra; aquí igualamos el suelo lejano, las peñas y los gemelos
	var mod := Color.WHITE
	for i in range(_moduladores.size() - 1, -1, -1):
		var cm: CanvasModulate = _moduladores[i]
		if not is_instance_valid(cm):
			_moduladores.remove_at(i)
			continue
		if cm.is_visible_in_tree():
			mod *= cm.color
	_mod_escena = mod
	if _entorno:
		_entorno.background_color = _fondo_base * mod
	for m in _suelos_lejanos:
		m.set_shader_parameter("tinte", mod)
	if _mat_penas:
		_mat_penas.albedo_color = mod
	if _luz_muros:
		var oscuro := clampf((0.8 - mod.get_luminance()) * 1.4, 0.0, 1.0)
		_luz_muros.visible = oscuro > 0.05 and is_instance_valid(_maisha)
		if _luz_muros.visible:
			_luz_muros.light_energy = 0.75 * oscuro
			_luz_muros.global_position = _al_suelo(_maisha.global_position) + Vector3(0.0, 1.4, 0.2)


func _tinte_sprite(n: Node2D) -> Color:
	if n.material is CanvasItemMaterial and (n.material as CanvasItemMaterial).light_mode == CanvasItemMaterial.LIGHT_MODE_UNSHADED:
		return Color.WHITE
	if _mod_escena.r >= 0.99 and _mod_escena.g >= 0.99 and _mod_escena.b >= 0.99:
		return Color.WHITE
	var luz := _mod_escena
	for i in range(_luces_2d.size() - 1, -1, -1):
		var l: PointLight2D = _luces_2d[i]
		if not is_instance_valid(l):
			_luces_2d.remove_at(i)
			continue
		if not l.enabled or not l.is_visible_in_tree() or l.texture == null:
			continue
		var radio := l.texture.get_width() * 0.5 * l.texture_scale
		if radio <= 1.0:
			continue
		var d := n.global_position.distance_to(l.global_position)
		if d >= radio:
			continue
		var f := clampf(1.0 - d / radio, 0.0, 1.0)
		f = f * f * (3.0 - 2.0 * f) * l.energy
		luz += l.color * f
	return Color(minf(luz.r, 1.0), minf(luz.g, 1.0), minf(luz.b, 1.0), 1.0)


func _alfa_efectiva(n: Node2D) -> float:
	var a := n.self_modulate.a
	var c: Node = n
	while c and c != escena:
		if c is CanvasItem:
			a *= (c as CanvasItem).modulate.a
		c = c.get_parent()
	return a


func _copiar_plataforma(n: Node2D, g: MeshInstance3D) -> void:
	g.visible = _visible(n)
	if not g.visible:
		return
	var tex: Texture2D = null
	var region_rect := Rect2()
	var usar_region := false
	var cols := 1
	var filas_f := 1
	var offset_sprite := Vector2.ZERO
	var centrado := true
	if n is AnimatedSprite2D:
		var a := n as AnimatedSprite2D
		offset_sprite = a.offset
		centrado = a.centered
		if a.sprite_frames:
			tex = a.sprite_frames.get_frame_texture(a.animation, a.frame)
	else:
		var s := n as Sprite2D
		tex = s.texture
		offset_sprite = s.offset
		centrado = s.centered
		usar_region = s.region_enabled
		region_rect = s.region_rect
		cols = maxi(s.hframes, 1)
		filas_f = maxi(s.vframes, 1)
	if tex is CanvasTexture:
		tex = (tex as CanvasTexture).diffuse_texture
	if tex == null:
		g.visible = false
		return
	var mat := g.material_override as StandardMaterial3D
	if mat.albedo_texture != tex:
		mat.albedo_texture = tex
	var mod := n.modulate * n.self_modulate * _tinte_sprite(n)
	var alfa := _alfa_efectiva(n)
	mat.albedo_color = Color(mod.r, mod.g, mod.b, alfa)
	var tam := region_rect.size if usar_region else Vector2(tex.get_width() / float(cols), tex.get_height() / float(filas_f))
	var escala := n.global_scale.abs()
	var plano := g.mesh as PlaneMesh
	var mundo_tam := Vector2(tam.x * escala.x * PX, tam.y * escala.y * PX)
	if not plano.size.is_equal_approx(mundo_tam):
		plano.size = mundo_tam
	var desplazamiento: Vector2 = (offset_sprite - (tam * 0.5 if centrado else Vector2.ZERO)) * escala
	var centro: Vector2 = n.global_position + desplazamiento + Vector2(tam.x * escala.x, tam.y * escala.y) * 0.5
	g.position = Vector3(centro.x * PX, 0.015, centro.y * PX)
	g.rotation = Vector3(0.0, -n.global_rotation, 0.0)


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
		tex = (tex as CanvasTexture).diffuse_texture          # (en 3D, sin el relieve 2D)
	g.texture = tex
	g.flip_h = n.flip_h
	g.flip_v = n.flip_v
	g.centered = n.centered
	var rgb := n.modulate * n.self_modulate * _tinte_sprite(n)
	var alfa := _alfa_efectiva(n)
	g.modulate = Color(rgb.r, rgb.g, rgb.b, alfa)
	g.transparent = true
	g.alpha_cut = SpriteBase3D.ALPHA_CUT_DISABLED if alfa < 0.99 else SpriteBase3D.ALPHA_CUT_DISCARD
	var escala := n.global_scale
	g.scale = Vector3(escala.x, escala.y, 1.0)
	var rot := n.global_rotation
	if absf(rot) > 0.001:
		g.billboard = BaseMaterial3D.BILLBOARD_DISABLED
		g.rotation = Vector3(0.0, 0.0, -rot)
	else:
		g.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
		g.rotation = Vector3.ZERO
	# de pie: apoyado en el suelo de su cuerpo; lo que en 2D está más arriba que el cuerpo, en 3D está más alto
	var sube: Vector2 = n.global_position - ancla.global_position
	# (en 2D la «y» crece hacia abajo y en 3D hacia arriba: sin centrar, el dibujo va de offset.y a offset.y + alto en 2D,
	# así que en 3D su borde de abajo está en -(offset.y + alto); centrado, se queda donde está, solo cambia el signo)
	var alto := 0.0
	if not g.centered and tex:
		alto = (g.region_rect.size.y if g.region_enabled else tex.get_height() / float(maxi(g.vframes, 1)))
	g.offset = Vector2(n.offset.x, -(n.offset.y + alto))
	# si gira hacia abajo (p. ej. un tentáculo hacia el sur), lo alzamos lo justo para que no se hunda bajo el suelo
	var alza := (1.0 - cos(rot)) * maxf(0.0, -(n.offset.y + (alto * 0.5 if not g.centered else 0.0)))
	# (las capas de un mismo cuerpo, un pelín hacia la cámara según su orden de dibujo, para que no parpadeen)
	var orden := z * 0.008 + _orden_en_ancla(n, ancla)
	g.position = _al_suelo(ancla.global_position) + Vector3(sube.x * PX, (-sube.y + alza) * PX, orden)


## Orden de dibujo de `n` respecto a `ancla`: respeta grupos hermanos como RopaDetras < Sprite < Ropa.
static func _orden_en_ancla(n: Node, ancla: Node) -> float:
	if n == ancla:
		return 0.0
	var pasos: Array[int] = []
	var cur := n
	while cur != null and cur != ancla:
		pasos.append(cur.get_index())
		cur = cur.get_parent()
	if cur != ancla:
		return float(n.get_index()) * 0.0015
	var peso := 0.0015
	var total := 0.0
	for i in range(pasos.size() - 1, -1, -1):
		var paso := pasos[i] + (0 if i == pasos.size() - 1 else 1)
		total += float(paso) * peso
		peso *= 0.12
	return total


## Partículas atmosféricas suaves por bioma en HD-2D (esporas, nieve fina, motas doradas o polvo mineral)
func _crear_motas() -> void:
	if region == null:
		return
	var mapa := String(region.get("mapa"))
	var mundo := String(region.get("mundo")) if region.get("mundo") else "raiz"
	var col_a := Color("f0e088")
	var col_b := Color("b4e070")
	var vel_y := 0.25
	if mapa in ["paso_escarcha", "sendero_olvidado", "ruinas_primer_arbol"]:
		col_a = Color("eef4ff")
		col_b = Color("b6cde8")
		vel_y = -0.35
	elif mapa == "observatorio_aurora":
		col_a = Color("9ce8ff")
		col_b = Color("ffe690")
		vel_y = 0.22
	elif mundo == "sigilia":
		col_a = Color("edd694")
		col_b = Color("b6a6dc")
		vel_y = 0.18
	elif mundo == "asterhaul":
		col_a = Color("ffcb72")
		col_b = Color("d88450")
		vel_y = 0.30
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	mat.vertex_color_use_as_albedo = true
	mat.no_depth_test = false
	var quad := QuadMesh.new()
	quad.size = Vector2(0.085, 0.085)
	quad.material = mat
	_motas_mm = MultiMesh.new()
	_motas_mm.transform_format = MultiMesh.TRANSFORM_3D
	_motas_mm.use_colors = true
	_motas_mm.mesh = quad
	_motas_mm.instance_count = 34
	var inst := MultiMeshInstance3D.new()
	inst.multimesh = _motas_mm
	inst.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	inst.extra_cull_margin = 40.0
	add_child(inst)
	var rng := RandomNumberGenerator.new()
	rng.seed = 20261114
	for i in 34:
		var c := col_a.lerp(col_b, rng.randf())
		_motas_datos.append({
			"off": Vector3(rng.randf_range(-13.0, 13.0), rng.randf_range(0.35, 3.6), rng.randf_range(-10.0, 10.0)),
			"vy": vel_y * rng.randf_range(0.6, 1.3),
			"vx": rng.randf_range(-0.35, 0.35),
			"fase": rng.randf() * TAU,
			"col": c,
		})
	_actualizar_motas(0.0)


func _actualizar_motas(delta: float) -> void:
	if _motas_mm == null or _motas_datos.is_empty():
		return
	_motas_t += delta
	for i in _motas_datos.size():
		var d: Dictionary = _motas_datos[i]
		var off: Vector3 = d["off"]
		var fase: float = float(d["fase"])
		var y := fposmod(off.y + _motas_t * float(d["vy"]), 3.4) + 0.3
		var x := wrapf(off.x + _motas_t * float(d["vx"]) + sin(_motas_t * 0.9 + fase) * 0.45, -13.0, 13.0)
		var z := wrapf(off.z + cos(_motas_t * 0.7 + fase) * 0.35, -10.0, 10.0)
		var pulso := 0.25 + 0.45 * (0.5 + 0.5 * sin(_motas_t * 1.8 + fase))
		var alt_a := clampf(minf(y - 0.3, 3.7 - y) * 1.4, 0.0, 1.0)
		var col: Color = d["col"]
		_motas_mm.set_instance_transform(i, Transform3D(Basis(), _foco + Vector3(x, y, z)))
		_motas_mm.set_instance_color(i, Color(col.r, col.g, col.b, pulso * alt_a))
