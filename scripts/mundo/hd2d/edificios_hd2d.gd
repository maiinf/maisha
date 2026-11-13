extends RefCounted
## EDIFICIOS 3D VOLUMÉTRICOS EN HD-2D
## Convierte cada edificio / estructura del catálogo en una malla 3D con volumen real:
## muros laterales texturados con su propio material a escala 1:1 de píxel, tejados
## inclinados a dos/cuatro aguas, cúpulas y torres cilíndricas, fachadas nítidas pixel a
## pixel y sombras 3D reales sin depender de .glb externos y respetando cambios de frame
## (ruina <-> reconstruido), tintes de noche/iluminación y transparencias (Gran Árbol).

const PX := 1.0 / 16.0

const SOMBREADOR := """
shader_type spatial;
render_mode diffuse_lambert, specular_disabled, cull_disabled;
uniform sampler2D textura : filter_nearest, source_color;
uniform vec4 tinte : source_color = vec4(1.0);
uniform vec4 uv_marco = vec4(0.0, 0.0, 1.0, 1.0);

void fragment() {
	vec2 uv = uv_marco.xy + UV * uv_marco.zw;
	vec4 c = texture(textura, uv);
	if (c.a < 0.5) { discard; }
	if (tinte.a < 0.99) {
		ivec2 p = ivec2(FRAGCOORD.xy) & ivec2(3);
		int idx = p.x + p.y * 4;
		float bayer = float(
			(idx == 0) ? 0 : (idx == 1) ? 8 : (idx == 2) ? 2 : (idx == 3) ? 10 :
			(idx == 4) ? 12 : (idx == 5) ? 4 : (idx == 6) ? 14 : (idx == 7) ? 6 :
			(idx == 8) ? 3 : (idx == 9) ? 11 : (idx == 10) ? 1 : (idx == 11) ? 9 :
			(idx == 12) ? 15 : (idx == 13) ? 7 : (idx == 14) ? 13 : 5
		) / 16.0;
		if (tinte.a <= bayer) { discard; }
	}
	ALBEDO = c.rgb * tinte.rgb * COLOR.rgb;
	ROUGHNESS = 1.0;
}
"""

## Catálogo de geometría 3D por nombre de archivo PNG.
const CATALOGO := {
	"casa_granja.png": {
		"tipo": "hip", "x0": 26, "x1": 170, "y_alero": 76, "y_pico": 8,
		"rx0": 60, "rx1": 134, "eave_x0": 14, "eave_x1": 180, "fondo": 4.0, "alero_z": 0.20,
		"techo_rect": [46, 76, 44, 68],
		"extras": [["caja", 136, 154, 0, 38, -2.1, -1.2], ["frente_z", 86, 114, 24, 52, -0.35]],
	},
	"ruina_casa.png": {
		"tipo": "hip", "x0": 4, "x1": 56, "y_alero": 28, "y_pico": 18,
		"rx0": 14, "rx1": 46, "eave_x0": 2, "eave_x1": 58, "fondo": 2.6, "alero_z": 0.10,
	},
	"taller.png": {
		"tipo": "hip", "x0": 22, "x1": 124, "y_alero": 64, "y_pico": 38,
		"rx0": 46, "rx1": 102, "eave_x0": 16, "eave_x1": 130, "fondo": 3.8, "alero_z": 0.18,
		"extras": [["caja", 14, 34, 20, 144, -1.8, -0.6], ["frente_z", 12, 54, 0, 26, -1.2]],
	},
	"cocina.png": {
		"tipo": "domo", "x0": 22, "x1": 98, "y_alero": 72, "y_pico": 26,
		"fondo": 3.4, "cono": true, "crest_x0": 52, "crest_x1": 74, "crest_y": 28,
	},
	"casa_seta.png": {
		"tipo": "domo", "x0": 32, "x1": 88, "cap_x0": 6, "cap_x1": 114,
		"y_alero": 80, "y_pico": 26, "fondo": 3.8, "cono": false,
		"crest_x0": 44, "crest_x1": 76, "crest_y": 26,
	},
	"puesto.png": {
		"tipo": "puesto", "x0": 12, "x1": 104, "y_mostrador": 72,
		"y_alero": 40, "y_pico": 22, "fondo": 2.4,
	},
	"gran_arbol.png": {
		"tipo": "arbol", "x0": 48, "x1": 128, "y_copa": 112, "y_pico": 2, "fondo": 4.8,
	},
	"granero.png": {
		"tipo": "gable", "x0": 22, "x1": 101, "y_alero": 64, "y_pico": 25, "cx": 62,
		"eave_x0": 18, "eave_x1": 104, "fondo": 4.0, "alero_z": 0.18, "crest_x0": 50, "crest_x1": 74, "crest_y": 26,
	},
	"campo/molino.png": {
		"tipo": "domo", "x0": 26, "x1": 70, "cap_x0": 24, "cap_x1": 72,
		"y_alero": 56, "y_pico": 36, "fondo": 3.0, "cono": false,
		"extras": [["frente_z", 0, 96, 16, 88, 0.18]],
	},
	"casa_bata.png": {
		"tipo": "hip", "x0": 8, "x1": 96, "y_alero": 52, "y_pico": 4,
		"rx0": 42, "rx1": 56, "eave_x0": 2, "eave_x1": 98, "fondo": 3.4, "alero_z": 0.18,
	},
	"sello_raices.png": {
		"tipo": "sello", "y_alero": 52, "y_pico": 4, "fondo": 3.4, "alero_z": 0.24,
	},
	"almacen.png": {
		"tipo": "hip", "x0": 12, "x1": 118, "y_alero": 54, "y_pico": 8,
		"rx0": 24, "rx1": 102, "eave_x0": 2, "eave_x1": 128, "fondo": 4.0, "alero_z": 0.20,
		"extras": [["frente_z", 54, 74, 2, 16, -0.3]],
	},
	"casa_juncos.png": {
		"tipo": "hip", "x0": 8, "x1": 94, "y_alero": 52, "y_pico": 4,
		"rx0": 40, "rx1": 58, "eave_x0": 2, "eave_x1": 98, "fondo": 3.4, "alero_z": 0.18,
	},
	"casa_barcas.png": {
		"tipo": "hip", "x0": 12, "x1": 114, "y_alero": 56, "y_pico": 18,
		"rx0": 38, "rx1": 90, "eave_x0": 8, "eave_x1": 120, "fondo": 3.8, "alero_z": 0.20,
		"extras": [["frente_z", 50, 74, 4, 22, -0.8]],
	},
	"aprisco.png": {
		"tipo": "hip", "x0": 14, "x1": 80, "y_alero": 74, "y_pico": 42,
		"rx0": 34, "rx1": 62, "eave_x0": 8, "eave_x1": 86, "fondo": 3.4, "alero_z": 0.18,
		"extras": [["caja", 20, 34, 28, 72, -1.5, -0.7], ["frente_z", 18, 46, 0, 30, -1.1]],
	},
	"horreo.png": {
		"tipo": "hip", "x0": 20, "x1": 90, "y_alero": 52, "y_pico": 18,
		"rx0": 46, "rx1": 66, "eave_x0": 12, "eave_x1": 98, "fondo": 3.6, "alero_z": 0.18,
		"extras": [["frente_z", 44, 68, 4, 22, -1.6]],
	},
	"madriguera.png": {
		"tipo": "domo", "x0": 12, "x1": 116, "cap_x0": 12, "cap_x1": 116,
		"y_alero": 68, "y_pico": 24, "fondo": 4.0, "cono": false,
		"extras": [["caja", 72, 84, 6, 30, -2.0, -1.2], ["frente_z", 70, 94, 0, 18, -1.6]],
	},
	"palafito.png": {
		"tipo": "hip", "x0": 26, "x1": 98, "y_alero": 54, "y_pico": 22,
		"rx0": 46, "rx1": 74, "eave_x0": 20, "eave_x1": 106, "fondo": 3.4, "alero_z": 0.18,
		"extras": [["frente_z", 44, 70, 14, 30, -1.5]],
	},
	"campamento.png": {
		"tipo": "domo", "x0": 8, "x1": 82, "cap_x0": 6, "cap_x1": 84,
		"y_alero": 72, "y_pico": 20, "fondo": 3.2, "cono": true, "crest_x0": 28, "crest_x1": 56, "crest_y": 24,
	},
	"casa_nungu.png": {
		"tipo": "hip", "x0": 24, "x1": 152, "y_alero": 68, "y_pico": 30,
		"rx0": 52, "rx1": 124, "eave_x0": 12, "eave_x1": 164, "fondo": 4.4, "alero_z": 0.22,
		"extras": [["caja", 38, 50, 14, 34, -2.1, -1.3], ["domo_extra", 114, 146, 34, 6, -2.2, 24]],
	},
	"gran_archivo.png": {
		"tipo": "hip", "x0": 32, "x1": 159, "y_alero": 74, "y_pico": 74,
		"rx0": 28, "rx1": 163, "eave_x0": 26, "eave_x1": 165, "fondo": 4.8, "alero_z": 0.20, "cerrar_techo": true,
		"pared_rect": [112, 126, 98, 144],
		"extras": [["caja", 54, 137, 52, 74, -3.9, -0.9], ["domo_extra", 52, 139, 54, 14, -2.4, 52], ["frente_z", 86, 108, 0, 16, -2.4]],
	},
	"casa_kalamu.png": {
		"tipo": "gable", "x0": 6, "x1": 66, "y_alero": 48, "y_pico": 18, "cx": 38,
		"eave_x0": 4, "eave_x1": 68, "fondo": 3.4, "alero_z": 0.18,
		"extras": [["caja", 64, 86, 32, 103, -2.8, -0.3], ["cono_extra", 60, 88, 34, 2, -1.55]],
	},
	"casa_escriba.png": {
		"tipo": "gable", "x0": 10, "x1": 61, "y_alero": 46, "y_pico": 16, "cx": 36,
		"eave_x0": 5, "eave_x1": 67, "fondo": 3.2, "alero_z": 0.18, "crest_x0": 26, "crest_x1": 46, "crest_y": 17,
	},
	"taller_taa.png": {
		"tipo": "gable", "x0": 10, "x1": 69, "y_alero": 46, "y_pico": 18, "cx": 40,
		"eave_x0": 6, "eave_x1": 74, "fondo": 3.2, "alero_z": 0.18,
	},
	"puesto_tinta.png": {
		"tipo": "puesto", "x0": 5, "x1": 50, "y_mostrador": 32,
		"y_alero": 19, "y_pico": 11, "fondo": 1.8,
	},
	"cupula_nyota.png": {
		"tipo": "hip", "x0": 20, "x1": 89, "y_alero": 54, "y_pico": 50,
		"rx0": 17, "rx1": 91, "eave_x0": 17, "eave_x1": 91, "fondo": 4.0, "alero_z": 0.14, "cerrar_techo": true,
		"pared_rect": [24, 52, 92, 106],
		"extras": [["domo_extra", 18, 90, 52, 16, -2.0], ["frente_z", 58, 92, 4, 34, -1.1], ["frente_z", 40, 56, 0, 16, -2.0]],
	},
	"torre.png": {
		"tipo": "domo", "x0": 8, "x1": 34, "cap_x0": 6, "cap_x1": 36,
		"y_alero": 28, "y_pico": 12, "fondo": 1.8, "cono": true,
	},
	"pozo.png": {
		"tipo": "domo", "x0": 4, "x1": 26, "cap_x0": 2, "cap_x1": 28,
		"y_alero": 10, "y_pico": 2, "fondo": 1.4, "cono": true,
		"extras": [["frente_z", 0, 30, 0, 38, 0.12]],
	},
	"monumento.png": {
		"tipo": "domo", "x0": 10, "x1": 34, "cap_x0": 16, "cap_x1": 28,
		"y_alero": 46, "y_pico": 6, "fondo": 1.6, "cono": true,
	},
	"fuente.png": {
		"tipo": "bloques",
		"partes": [
			["cil", 7, 57, 35, 48, 0.25, -1.95, true, [10, 26, 40, 46], [16, 48, 36, 42]],
			["cil", 29, 35, 16, 38, -0.67, -1.03, false, [29, 34, 18, 34]],
			["capa", 20, 48, 4, 38, -0.85, 1.0],
		],
	},
	"seccion/sello.png": {
		"tipo": "bloques", "frente_z": 0.04,
		"partes": [
			["caja", 0, 6, 4, 47, 0.02, -0.68, true, [0, 5, 8, 44]],
			["caja", 58, 64, 4, 47, 0.02, -0.68, true, [58, 63, 8, 44]],
		],
	},
	"pedestal.png": {
		"tipo": "bloques", "frente_z": 0.04,
		"partes": [
			["caja", 5, 19, 8, 15, 0.01, -0.62, true, [6, 18, 9, 13]],
			["caja", 8, 16, 15, 30, -0.06, -0.46, false, [8, 15, 16, 29]],
			["caja", 4, 20, 30, 35, 0.02, -0.72, true, [5, 19, 31, 34]],
		],
	},
	"seccion/atril.png": {
		"tipo": "bloques", "frente_z": 0.04,
		"partes": [
			["caja", 3, 13, 6, 13, 0.01, -0.45, true, [4, 12, 6, 12]],
			["caja", 6, 10, 13, 27, -0.10, -0.34, false, [4, 12, 6, 12]],
			["caja", 3, 13, 27, 30, 0.02, -0.52, true, [4, 12, 6, 12]],
		],
	},
	"estanterias/atril.png": {
		"tipo": "bloques", "frente_z": 0.04,
		"partes": [
			["caja", 7, 33, 13, 25, 0.01, -0.82, true, [10, 30, 15, 23]],
			["caja", 18, 23, 25, 38, -0.15, -0.55, false, [18, 22, 27, 37]],
			["caja", 13, 27, 38, 44, 0.02, -0.82, true, [14, 26, 39, 43]],
		],
	},
	"altar.png": {
		"tipo": "bloques", "frente_z": 0.04,
		"partes": [
			["caja", 9, 25, 20, 30, -0.02, -0.92, true, [10, 23, 21, 29]],
			["caja", 6, 28, 30, 35, 0.02, -1.08, true, [7, 27, 31, 34]],
		],
	},
	"menhir.png": {
		"tipo": "bloques", "frente_z": 0.04,
		"partes": [
			["caja", 5, 13, 12, 34, 0.01, -0.65, true, [5, 12, 16, 32]],
			["capa", 3, 15, 2, 14, -0.22, 0.88],
			["capa", 3, 15, 2, 14, -0.44, 0.76],
		],
	},
	"arco_ruinas.png": {
		"tipo": "bloques", "frente_z": 0.04,
		"partes": [
			["caja", 16, 29, 24, 83, 0.02, -1.10, true, [17, 28, 36, 76]],
			["caja", 83, 97, 34, 83, 0.02, -1.10, true, [84, 96, 40, 76]],
			["capa", 16, 94, 0, 32, -0.28, 0.88],
			["capa", 16, 94, 0, 32, -0.56, 0.78],
			["capa", 16, 94, 0, 32, -0.84, 0.68],
		],
	},
	"estatua.png": {
		"tipo": "bloques", "frente_z": 0.04,
		"partes": [
			["caja", 6, 25, 35, 39, 0.02, -0.78, true, [8, 22, 35, 39]],
			["caja", 36, 55, 35, 39, 0.02, -0.78, true, [38, 52, 35, 39]],
			["caja", 66, 85, 35, 39, 0.02, -0.78, true, [68, 82, 35, 39]],
			["capa", 4, 89, 1, 36, -0.22, 0.88],
			["capa", 4, 89, 1, 36, -0.44, 0.78],
			["capa", 4, 89, 1, 36, -0.66, 0.70],
		],
	},
	"muro.png": {
		"tipo": "bloques",
		"partes": [
			["caja", 0, 24, 1, 12, 0.02, -0.68, true, [2, 22, 3, 10], [2, 22, 3, 8]],
		],
	},
	"columna.png": {
		"tipo": "bloques",
		"partes": [
			["cil", 1, 11, 3, 30, 0.02, -0.60, true, [2, 9, 8, 26], [2, 9, 8, 16]],
		],
	},
}

var _shader: Shader
var _mallas := {}                     # "ruta|frame" -> ArrayMesh (se libera al destruir el espejo)


func limpiar() -> void:
	_mallas.clear()
	_shader = null


func _nombre_catalogo(tex: Texture2D) -> String:
	if tex == null:
		return ""
	var ruta := tex.resource_path
	for clave: String in ["campo/molino.png", "seccion/atril.png", "estanterias/atril.png", "seccion/sello.png"]:
		if ruta.ends_with(clave):
			return clave
	var archivo := ruta.get_file()
	return archivo if CATALOGO.has(archivo) else ""


func nombre_catalogo(n: Node2D) -> String:
	if not (n is Sprite2D):
		return ""
	return _nombre_catalogo(_textura_base((n as Sprite2D).texture))


func crear_gemelo() -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	var mat := ShaderMaterial.new()
	if _shader == null:
		_shader = Shader.new()
		_shader.code = SOMBREADOR
	mat.shader = _shader
	mi.material_override = mat
	return mi


func copiar(n: Node2D, mi: MeshInstance3D, ancla: Node2D, z: int, visible: bool, pos_suelo: Vector3, tinte: Color) -> void:
	mi.visible = visible
	if not visible:
		return
	var s := n as Sprite2D
	var tex := _textura_base(s.texture)
	if tex == null:
		mi.visible = false
		return
	var archivo := _nombre_catalogo(tex)
	if archivo.is_empty():
		mi.visible = false
		return
	var hf := maxi(s.hframes, 1)
	var vf := maxi(s.vframes, 1)
	var marco := mini(s.frame, hf * vf - 1)
	var fw := float(tex.get_width()) / float(hf)
	var fh := float(tex.get_height()) / float(vf)
	var clave := "%s|%d" % [tex.resource_path, marco]
	if not _mallas.has(clave):
		_mallas[clave] = _construir_malla(tex, archivo, marco, hf, int(fw), int(fh))
	mi.mesh = _mallas[clave]
	var col := marco % hf
	var fila := marco / hf
	var mat := mi.material_override as ShaderMaterial
	mat.set_shader_parameter("textura", tex)
	mat.set_shader_parameter("tinte", n.modulate * n.self_modulate * tinte)
	var flip := -1.0 if s.flip_h else 1.0
	var u0 := (float(col) + (1.0 if s.flip_h else 0.0)) / float(hf)
	mat.set_shader_parameter("uv_marco", Vector4(u0, float(fila) / float(vf), flip / float(hf), 1.0 / float(vf)))
	var escala := n.global_scale
	mi.scale = Vector3(escala.x, escala.y, maxf(escala.x, 1.0))
	mi.rotation = Vector3(0.0, 0.0, -n.global_rotation) if absf(n.global_rotation) > 0.001 else Vector3.ZERO
	var sube: Vector2 = n.global_position - ancla.global_position
	var dx_origen := (s.offset.x if s.centered else s.offset.x + fw * 0.5)
	var dy_origen := (s.offset.y + fh * 0.5 if s.centered else s.offset.y + fh)
	var orden := z * 0.004 + n.get_index() * 0.0015
	mi.position = pos_suelo + Vector3((sube.x + dx_origen) * PX, (-sube.y - dy_origen) * PX, orden)


static func _textura_base(tex: Texture2D) -> Texture2D:
	if tex is CanvasTexture:
		return (tex as CanvasTexture).diffuse_texture
	return tex


static func _p(px: float, py: float, z: float, fw: int, fh: int) -> Vector3:
	return Vector3((px - float(fw) * 0.5) * PX, (float(fh) - py) * PX, z)


static func _uv(px: float, py: float, fw: int, fh: int) -> Vector2:
	return Vector2(clampf(px / float(fw), 0.0, 1.0), clampf(py / float(fh), 0.0, 1.0))


static func _quad(st: SurfaceTool, p0: Vector3, p1: Vector3, p2: Vector3, p3: Vector3,
		u0: Vector2, u1: Vector2, u2: Vector2, u3: Vector2, col: Color) -> void:
	var n := (p1 - p0).cross(p3 - p0)
	n = n.normalized() if n.length_squared() >= 1e-8 else Vector3.UP
	st.set_color(col)
	st.set_normal(n)
	for pair in [[p0, u0], [p1, u1], [p2, u2], [p0, u0], [p2, u2], [p3, u3]]:
		st.set_uv(pair[1])
		st.add_vertex(pair[0])


static func _tri(st: SurfaceTool, p0: Vector3, p1: Vector3, p2: Vector3,
		u0: Vector2, u1: Vector2, u2: Vector2, col: Color) -> void:
	var n := (p1 - p0).cross(p2 - p0)
	n = n.normalized() if n.length_squared() >= 1e-8 else Vector3.UP
	st.set_color(col)
	st.set_normal(n)
	for pair in [[p0, u0], [p1, u1], [p2, u2]]:
		st.set_uv(pair[1])
		st.add_vertex(pair[0])


## Subdivide un quad en azulejos espejados (ping-pong) a escala 1:1 de píxel para no estirar la textura
static func _quad_tiling(st: SurfaceTool, p0: Vector3, p1: Vector3, p2: Vector3, p3: Vector3,
		m: Rect2, fw: int, fh: int, col: Color) -> void:
	var sw := maxf(m.size.x * float(fw), 4.0)
	var sh := maxf(m.size.y * float(fh), 4.0)
	var nx := clampi(roundi((p0.distance_to(p1) / PX) / sw), 1, 10)
	var ny := clampi(roundi((p0.distance_to(p3) / PX) / sh), 1, 10)
	var u0 := m.position.x
	var u1 := m.end.x
	var v0 := m.position.y
	var v1 := m.end.y
	for ix in nx:
		var sx0 := float(ix) / float(nx)
		var sx1 := float(ix + 1) / float(nx)
		var ua := u0 if (ix % 2 == 0) else u1
		var ub := u1 if (ix % 2 == 0) else u0
		for iy in ny:
			var sy0 := float(iy) / float(ny)
			var sy1 := float(iy + 1) / float(ny)
			var va := v1 if (iy % 2 == 0) else v0
			var vb := v0 if (iy % 2 == 0) else v1
			var q0 := p0.lerp(p1, sx0).lerp(p3.lerp(p2, sx0), sy0)
			var q1 := p0.lerp(p1, sx1).lerp(p3.lerp(p2, sx1), sy0)
			var q2 := p0.lerp(p1, sx1).lerp(p3.lerp(p2, sx1), sy1)
			var q3 := p0.lerp(p1, sx0).lerp(p3.lerp(p2, sx0), sy1)
			_quad(st, q0, q1, q2, q3, Vector2(ua, va), Vector2(ub, va), Vector2(ub, vb), Vector2(ua, vb), col)


## Triángulo texturado con azulejos 1:1 (subdivide en franjas horizontales y azulejos horizontales)
static func _tri_tiling(st: SurfaceTool, p0: Vector3, p1: Vector3, apex: Vector3,
		m: Rect2, fw: int, fh: int, col: Color) -> void:
	var n_filas := clampi(roundi((p0.distance_to(apex) / PX) / maxf(m.size.y * float(fh), 6.0)), 2, 6)
	var sw := maxf(m.size.x * float(fw), 4.0)
	var u0 := m.position.x
	var u1 := m.end.x
	var v0 := m.position.y
	var v1 := m.end.y
	for r in n_filas:
		var t0 := float(r) / float(n_filas)
		var t1 := float(r + 1) / float(n_filas)
		var l0 := p0.lerp(apex, t0)
		var r0 := p1.lerp(apex, t0)
		var l1 := p0.lerp(apex, t1)
		var r1 := p1.lerp(apex, t1)
		var va := v1 if (r % 2 == 0) else v0
		var vb := v0 if (r % 2 == 0) else v1
		if r == n_filas - 1:
			_tri(st, l0, r0, apex, Vector2(u0, va), Vector2(u1, va), Vector2((u0 + u1) * 0.5, vb), col)
		else:
			var nx := clampi(roundi((l0.distance_to(r0) / PX) / sw), 1, 8)
			for ix in nx:
				var sx0 := float(ix) / float(nx)
				var sx1 := float(ix + 1) / float(nx)
				var ua := u0 if (ix % 2 == 0) else u1
				var ub := u1 if (ix % 2 == 0) else u0
				_quad(st, l0.lerp(r0, sx0), l0.lerp(r0, sx1), l1.lerp(r1, sx1), l1.lerp(r1, sx0),
					Vector2(ua, va), Vector2(ub, va), Vector2(ub, vb), Vector2(ua, vb), col)


static func _caja_texturada(st: SurfaceTool, x0: float, x1: float, y_top: float, y_bot: float,
		z_frente: float, z_fondo: float, fw: int, fh: int, m_pared: Rect2, m_top: Rect2,
		frente_original := true) -> void:
	var bl_f := _p(x0, y_bot, z_frente, fw, fh)
	var br_f := _p(x1, y_bot, z_frente, fw, fh)
	var tr_f := _p(x1, y_top, z_frente, fw, fh)
	var tl_f := _p(x0, y_top, z_frente, fw, fh)
	var bl_b := _p(x0, y_bot, z_fondo, fw, fh)
	var br_b := _p(x1, y_bot, z_fondo, fw, fh)
	var tr_b := _p(x1, y_top, z_fondo, fw, fh)
	var tl_b := _p(x0, y_top, z_fondo, fw, fh)
	if frente_original:
		_quad(st, bl_f, br_f, tr_f, tl_f,
			_uv(x0, y_bot, fw, fh), _uv(x1, y_bot, fw, fh), _uv(x1, y_top, fw, fh), _uv(x0, y_top, fw, fh), Color(1.0, 1.0, 1.0))
	else:
		_quad_tiling(st, bl_f, br_f, tr_f, tl_f, m_pared, fw, fh, Color(0.95, 0.95, 0.95))
	_quad_tiling(st, bl_b, bl_f, tl_f, tl_b, m_pared, fw, fh, Color(0.88, 0.89, 0.92))
	_quad_tiling(st, br_f, br_b, tr_b, tr_f, m_pared, fw, fh, Color(0.70, 0.72, 0.78))
	_quad_tiling(st, br_b, bl_b, tl_b, tr_b, m_pared, fw, fh, Color(0.68, 0.70, 0.76))
	if m_top.size.x > 0.0:
		_quad_tiling(st, tl_f, tr_f, tr_b, tl_b, m_top, fw, fh, Color(0.92, 0.91, 0.89))


## Busca una muestra 100% opaca (idealmente ~12x14 px) dentro del rectángulo de píxeles dado
static func _muestra(img: Image, xoff: int, col_i: int, fw: int, fh: int,
		rx0: int, rx1: int, ry0: int, ry1: int) -> Rect2:
	var x0 := clampi(mini(rx0, rx1), 1, maxi(2, fw - 4))
	var x1 := clampi(maxi(rx0, rx1), mini(x0 + 3, fw - 1), fw - 2)
	var y0 := clampi(mini(ry0, ry1), 1, maxi(2, fh - 4))
	var y1 := clampi(maxi(ry0, ry1), mini(y0 + 3, fh - 1), fh - 2)
	var mejor := Rect2(float(x0) / fw, float(y0) / fh, clampf(8.0 / fw, 0.02, 0.2), clampf(10.0 / fh, 0.02, 0.2))
	if img == null:
		return mejor
	var mejor_score := -1e9
	var w_muestra := mini(12, maxi(4, x1 - x0))
	var h_muestra := mini(14, maxi(4, y1 - y0))
	var step_x := maxi(1, (x1 - x0) / 6)
	var step_y := maxi(1, (y1 - y0) / 5)
	for sx in range(x0, maxi(x0 + 1, x1 - w_muestra + 1), step_x):
		for sy in range(y0, maxi(y0 + 1, y1 - h_muestra + 1), step_y):
			var opacos := 0
			var total := 0
			var lum_luz := 0.0
			for dx in w_muestra:
				for dy in h_muestra:
					var px_x := xoff + sx + dx
					var px_y := col_i * fh + sy + dy
					if px_x < 0 or px_y < 0 or px_x >= img.get_width() or px_y >= img.get_height():
						continue
					var c := img.get_pixel(px_x, px_y)
					total += 1
					if c.a >= 0.85:
						opacos += 1
						if c.r > 0.85 and c.g > 0.72 and c.b < 0.45:
							lum_luz += 2.0
						elif c.get_luminance() < 0.07:
							lum_luz += 0.6
			if total == 0 or opacos < total:
				continue
			var score := float(opacos) * 10.0 - lum_luz * 4.0
			if score > mejor_score:
				mejor_score = score
				mejor = Rect2(float(sx) / fw, float(sy) / fh, float(w_muestra) / fw, float(h_muestra) / fh)
	return mejor


static func _fila_opaca(img: Image, xoff: int, y_off: int, fw: int, y: int, hint_x0: int, hint_x1: int) -> Vector2i:
	if img == null or y < 0 or y_off + y >= img.get_height():
		return Vector2i(hint_x0, hint_x1)
	var ax0 := fw
	var ax1 := -1
	var lo := maxi(0, hint_x0 - 8)
	var hi := mini(fw - 1, hint_x1 + 8)
	for x in range(lo, hi + 1):
		if img.get_pixel(xoff + x, y_off + y).a > 0.65:
			if x < ax0: ax0 = x
			if x > ax1: ax1 = x
	if ax1 <= ax0 + 2:
		return Vector2i(hint_x0, hint_x1)
	return Vector2i(ax0, ax1)


func _construir_malla(tex: Texture2D, archivo: String, marco: int, hf: int, fw: int, fh: int) -> ArrayMesh:
	var cfg: Dictionary = CATALOGO.get(archivo, {})
	var img := tex.get_image()
	var col_i := marco / hf
	var row_i := marco % hf
	var xoff := row_i * fw
	var yoff := col_i * fh

	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)

	match String(cfg.get("tipo", "frente")):
		"sello":
			_construir_sello(st, cfg, fw, fh)
		"hip":
			_construir_hip(st, img, cfg, xoff, yoff, fw, fh)
		"gable":
			_construir_gable(st, img, cfg, xoff, yoff, fw, fh)
		"domo":
			_construir_domo(st, img, cfg, xoff, yoff, fw, fh)
		"puesto":
			_construir_puesto(st, img, cfg, xoff, yoff, fw, fh)
		"arbol":
			_construir_arbol(st, img, cfg, xoff, yoff, fw, fh)
		"bloques":
			_construir_bloques(st, img, cfg, xoff, yoff, fw, fh)

	return st.commit()


static func _construir_bloques(st: SurfaceTool, img: Image, cfg: Dictionary, xoff: int, yoff: int, fw: int, fh: int) -> void:
	var tiene_frente := cfg.has("frente_z")
	if tiene_frente:
		var fz := float(cfg["frente_z"])
		_quad(st,
			_p(0, fh, fz, fw, fh), _p(fw, fh, fz, fw, fh),
			_p(fw, 0, fz, fw, fh), _p(0, 0, fz, fw, fh),
			_uv(0, fh, fw, fh), _uv(fw, fh, fw, fh), _uv(fw, 0, fw, fh), _uv(0, 0, fw, fh), Color.WHITE)
	var col_i := yoff / fh
	var partes: Array = cfg.get("partes", [])
	for parte_v: Variant in partes:
		var p := parte_v as Array
		var kind := String(p[0])
		if kind == "capa":
			var x0 := float(p[1]); var x1 := float(p[2]); var y0 := float(p[3]); var y1 := float(p[4])
			var z := float(p[5]); var s := float(p[6])
			_quad(st,
				_p(x0, y1, z, fw, fh), _p(x1, y1, z, fw, fh), _p(x1, y0, z, fw, fh), _p(x0, y0, z, fw, fh),
				_uv(x0, y1, fw, fh), _uv(x1, y1, fw, fh), _uv(x1, y0, fw, fh), _uv(x0, y0, fw, fh), Color(s, s, s))
			continue
		var x0 := float(p[1]); var x1 := float(p[2]); var y0 := float(p[3]); var y1 := float(p[4])
		var zf := float(p[5]); var zb := float(p[6]); var con_top := bool(p[7])
		var mr: Array = p[8] if p.size() > 8 else [int(x0) + 1, int(x1) - 1, int(y0) + 2, int(y1) - 2]
		var m_pared := _muestra(img, xoff, col_i, fw, fh, int(mr[0]), int(mr[1]), int(mr[2]), int(mr[3]))
		var m_top := Rect2()
		if con_top:
			if p.size() > 9:
				var tr_rect: Array = p[9]
				m_top = _muestra(img, xoff, col_i, fw, fh, int(tr_rect[0]), int(tr_rect[1]), int(tr_rect[2]), int(tr_rect[3]))
			else:
				m_top = m_pared
		if kind == "caja":
			_caja_texturada(st, x0, x1, y0, y1, zf, zb, fw, fh, m_pared, m_top, not tiene_frente)
		elif kind == "cil":
			var cx_m := ((x0 + x1) * 0.5 - float(fw) * 0.5) * PX
			var rx := maxf((x1 - x0) * 0.5 * PX, 0.12)
			var rz := maxf((zf - zb) * 0.5, 0.12)
			var zc := (zf + zb) * 0.5
			var y_bot_m := (float(fh) - y1) * PX
			var y_top_m := (float(fh) - y0) * PX
			var segs := 12
			var centro := Vector3(cx_m, y_top_m, zc)
			for i in segs:
				var a0 := -PI + TAU * float(i) / float(segs)
				var a1 := -PI + TAU * float(i + 1) / float(segs)
				var b0 := Vector3(cx_m + sin(a0) * rx, y_bot_m, zc + cos(a0) * rz)
				var b1 := Vector3(cx_m + sin(a1) * rx, y_bot_m, zc + cos(a1) * rz)
				var t1 := Vector3(b1.x, y_top_m, b1.z)
				var t0 := Vector3(b0.x, y_top_m, b0.z)
				var am := (a0 + a1) * 0.5
				var sombra := 0.76 + 0.24 * clampf(cos(am), 0.0, 1.0)
				if cos(am) >= 0.0:
					var px_s0 := lerpf(x0, x1, (sin(a0) + 1.0) * 0.5)
					var px_s1 := lerpf(x0, x1, (sin(a1) + 1.0) * 0.5)
					_quad(st, b0, b1, t1, t0,
						_uv(px_s0, y1, fw, fh), _uv(px_s1, y1, fw, fh),
						_uv(px_s1, y0, fw, fh), _uv(px_s0, y0, fw, fh),
						Color(sombra, sombra, sombra))
				else:
					_quad_tiling(st, b0, b1, t1, t0, m_pared, fw, fh, Color(sombra * 0.9, sombra * 0.92, sombra * 0.96))
				if con_top:
					_tri_tiling(st, t0, t1, centro, m_top, fw, fh, Color(0.92, 0.92, 0.94))


static func _construir_sello(st: SurfaceTool, cfg: Dictionary, fw: int, fh: int) -> void:
	# Sigue exactamente el perfil pared + tejado de casa_bata por delante (+0.05 m)
	var y_alero := float(cfg["y_alero"])
	var y_pico := float(cfg["y_pico"])
	var fondo := float(cfg["fondo"])
	var oh_z := float(cfg["alero_z"])
	var y_alero_m := (float(fh) - y_alero) * PX
	var y_pico_m := y_alero_m + (y_alero - y_pico) * PX * 0.74
	var z_pico := -fondo * 0.48 + 0.05
	_quad(st,
		_p(0, fh, 0.06, fw, fh), _p(fw, fh, 0.06, fw, fh),
		_p(fw, y_alero, 0.06, fw, fh), _p(0, y_alero, 0.06, fw, fh),
		_uv(0, fh, fw, fh), _uv(fw, fh, fw, fh), _uv(fw, y_alero, fw, fh), _uv(0, y_alero, fw, fh), Color.WHITE)
	_quad(st,
		Vector3(-fw * 0.5 * PX, y_alero_m, oh_z), Vector3(fw * 0.5 * PX, y_alero_m, oh_z),
		Vector3(fw * 0.5 * PX, y_pico_m, z_pico), Vector3(-fw * 0.5 * PX, y_pico_m, z_pico),
		_uv(0, y_alero, fw, fh), _uv(fw, y_alero, fw, fh), _uv(fw, y_pico, fw, fh), _uv(0, y_pico, fw, fh), Color.WHITE)


static func _construir_hip(st: SurfaceTool, img: Image, cfg: Dictionary, xoff: int, yoff: int, fw: int, fh: int) -> void:
	var x0 := float(cfg["x0"])
	var x1 := float(cfg["x1"])
	var y_alero := float(cfg["y_alero"])
	var y_pico := float(cfg["y_pico"])
	var rx0 := float(cfg.get("rx0", lerpf(x0, x1, 0.25)))
	var rx1 := float(cfg.get("rx1", lerpf(x0, x1, 0.75)))
	var ex0 := float(cfg.get("eave_x0", x0))
	var ex1 := float(cfg.get("eave_x1", x1))
	var fondo := float(cfg.get("fondo", 3.6))
	var oh_z := float(cfg.get("alero_z", 0.20))

	# Fachada inferior completa (0..fw, y_alero..fh) para conservar porche, corral, barriles intactos
	_quad(st,
		_p(0, fh, 0.02, fw, fh), _p(fw, fh, 0.02, fw, fh),
		_p(fw, y_alero, 0.02, fw, fh), _p(0, y_alero, 0.02, fw, fh),
		_uv(0, fh, fw, fh), _uv(fw, fh, fw, fh), _uv(fw, y_alero, fw, fh), _uv(0, y_alero, fw, fh), Color.WHITE)

	var rect_pared: Array = cfg.get("pared_rect", [])
	var m_pared := _muestra(img, xoff, yoff / fh, fw, fh, int(rect_pared[0]), int(rect_pared[1]), int(rect_pared[2]), int(rect_pared[3])) if rect_pared.size() == 4 else _muestra(img, xoff, yoff / fh, fw, fh, int(x0) + 2, int(x0) + 18, int(y_alero) + 4, fh - 6)
	var rect_techo: Array = cfg.get("techo_rect", [])
	var m_techo := _muestra(img, xoff, yoff / fh, fw, fh, int(rect_techo[0]), int(rect_techo[1]), int(rect_techo[2]), int(rect_techo[3])) if rect_techo.size() == 4 else _muestra(img, xoff, yoff / fh, fw, fh, int(rx0), int(rx1), int(lerpf(y_pico, y_alero, 0.35)), int(y_alero) - 3)
	var m_tapa := m_techo if bool(cfg.get("cerrar_techo", false)) else Rect2()
	if bool(cfg.get("cerrar_techo", false)):
		m_tapa = m_pared if rect_pared.size() == 4 else _muestra(img, xoff, yoff / fh, fw, fh, int(x0) + 8, int(x1) - 8, int(y_alero) + 6, fh - 16)
	_caja_texturada(st, x0, x1, y_alero, fh, 0.0, -fondo, fw, fh, m_pared, m_tapa, false)

	var y_alero_m := _p(0, y_alero, 0.0, fw, fh).y
	var y_pico_m := y_alero_m + (y_alero - y_pico) * PX * 0.74
	var z_frente := oh_z
	var z_pico := -fondo * 0.48
	var z_atras := -fondo - oh_z * 0.75

	# Alero inferior
	_quad_tiling(st,
		_p(ex0, y_alero, 0.0, fw, fh), _p(ex1, y_alero, 0.0, fw, fh),
		_p(ex1, y_alero, z_frente, fw, fh), _p(ex0, y_alero, z_frente, fw, fh),
		m_techo, fw, fh, Color(0.55, 0.54, 0.56))

	if y_alero - y_pico > 6.0:
		var pasos := 5
		for k in pasos:
			var t0 := float(k) / float(pasos)
			var t1 := float(k + 1) / float(pasos)
			var py0 := lerpf(y_alero, y_pico, t0)
			var py1 := lerpf(y_alero, y_pico, t1)
			var lx0 := lerpf(ex0, rx0, t0)
			var lx1 := lerpf(ex0, rx0, t1)
			var px0 := lerpf(ex1, rx1, t0)
			var px1 := lerpf(ex1, rx1, t1)
			var span0 := _fila_opaca(img, xoff, yoff, fw, int(py0), int(lx0), int(px0))
			var span1 := _fila_opaca(img, xoff, yoff, fw, int(py1), int(lx1), int(px1))
			lx0 = clampf(float(span0.x), minf(ex0, rx0), maxf(lx0 + 4.0, rx0))
			px0 = clampf(float(span0.y), minf(px0 - 4.0, rx1), maxf(ex1, rx1))
			lx1 = clampf(float(span1.x), minf(ex0, rx0), maxf(lx1 + 4.0, rx0))
			px1 = clampf(float(span1.y), minf(px1 - 4.0, rx1), maxf(ex1, rx1))
			var wy0 := lerpf(y_alero_m, y_pico_m, t0)
			var wy1 := lerpf(y_alero_m, y_pico_m, t1)
			var wz0 := lerpf(z_frente, z_pico, t0)
			var wz1 := lerpf(z_frente, z_pico, t1)
			var bl := Vector3((lx0 - fw * 0.5) * PX, wy0, wz0)
			var br := Vector3((px0 - fw * 0.5) * PX, wy0, wz0)
			var tr := Vector3((px1 - fw * 0.5) * PX, wy1, wz1)
			var tl := Vector3((lx1 - fw * 0.5) * PX, wy1, wz1)
			_quad(st, bl, br, tr, tl,
				_uv(lx0, py0, fw, fh), _uv(px0, py0, fw, fh), _uv(px1, py1, fw, fh), _uv(lx1, py1, fw, fh),
				Color(1.02, 1.01, 0.99))

		var b_tl := Vector3((rx0 - fw * 0.5) * PX, y_pico_m, z_pico)
		var b_tr := Vector3((rx1 - fw * 0.5) * PX, y_pico_m, z_pico)
		var b_bl := Vector3((ex0 - fw * 0.5) * PX, y_alero_m, z_atras)
		var b_br := Vector3((ex1 - fw * 0.5) * PX, y_alero_m, z_atras)
		_quad_tiling(st, b_br, b_bl, b_tl, b_tr, m_techo, fw, fh, Color(0.76, 0.78, 0.84))

		# Limas / faldones laterales triangulares con azulejos 1:1 de píxel (cero estiramiento)
		var f_bl := Vector3((ex0 - fw * 0.5) * PX, y_alero_m, z_frente)
		var f_br := Vector3((ex1 - fw * 0.5) * PX, y_alero_m, z_frente)
		_tri_tiling(st, b_bl, f_bl, b_tl, m_techo, fw, fh, Color(0.90, 0.90, 0.93))
		_tri_tiling(st, f_br, b_br, b_tr, m_techo, fw, fh, Color(0.72, 0.74, 0.80))
		_quad_tiling(st, _p(x0, y_alero, -fondo, fw, fh), _p(x1, y_alero, -fondo, fw, fh), b_tr, b_tl, m_pared, fw, fh, Color(0.68, 0.70, 0.75))

	_aplicar_extras(st, img, cfg, xoff, yoff, fw, fh, m_techo)


static func _construir_gable(st: SurfaceTool, img: Image, cfg: Dictionary, xoff: int, yoff: int, fw: int, fh: int) -> void:
	var x0 := float(cfg["x0"])
	var x1 := float(cfg["x1"])
	var ex0 := float(cfg.get("eave_x0", x0))
	var ex1 := float(cfg.get("eave_x1", x1))
	var cx := float(cfg.get("cx", (x0 + x1) * 0.5))
	var y_alero := float(cfg["y_alero"])
	var y_pico := float(cfg["y_pico"])
	var fondo := float(cfg.get("fondo", 3.4))
	var oh_z := float(cfg.get("alero_z", 0.18))

	var m_pared := _muestra(img, xoff, yoff / fh, fw, fh, int(x0) + 2, int(x0) + 18, int(y_alero) + 4, fh - 6)
	var m_techo_i := _muestra(img, xoff, yoff / fh, fw, fh, int(ex0) + 2, int(cx) - 4, int(lerpf(y_pico, y_alero, 0.5)), int(y_alero))
	var m_techo_d := _muestra(img, xoff, yoff / fh, fw, fh, int(cx) + 4, int(ex1) - 2, int(lerpf(y_pico, y_alero, 0.5)), int(y_alero))

	_quad(st,
		_p(0, fh, 0.02, fw, fh), _p(fw, fh, 0.02, fw, fh),
		_p(fw, y_alero, 0.02, fw, fh), _p(0, y_alero, 0.02, fw, fh),
		_uv(0, fh, fw, fh), _uv(fw, fh, fw, fh), _uv(fw, y_alero, fw, fh), _uv(0, y_alero, fw, fh), Color.WHITE)
	_tri(st,
		_p(ex0, y_alero, 0.02, fw, fh), _p(ex1, y_alero, 0.02, fw, fh), _p(cx, y_pico, 0.02, fw, fh),
		_uv(ex0, y_alero, fw, fh), _uv(ex1, y_alero, fw, fh), _uv(cx, y_pico, fw, fh), Color.WHITE)

	if cfg.has("crest_y"):
		var cy := float(cfg["crest_y"])
		var cx0 := float(cfg.get("crest_x0", cx - 16.0))
		var cx1 := float(cfg.get("crest_x1", cx + 16.0))
		_quad(st,
			_p(cx0, cy, -fondo * 0.4, fw, fh), _p(cx1, cy, -fondo * 0.4, fw, fh),
			_p(cx1, 0, -fondo * 0.4, fw, fh), _p(cx0, 0, -fondo * 0.4, fw, fh),
			_uv(cx0, cy, fw, fh), _uv(cx1, cy, fw, fh), _uv(cx1, 0, fw, fh), _uv(cx0, 0, fw, fh), Color.WHITE)

	_caja_texturada(st, x0, x1, y_alero, fh, 0.0, -fondo, fw, fh, m_pared, Rect2(), false)
	_tri_tiling(st, _p(x1, y_alero, -fondo, fw, fh), _p(x0, y_alero, -fondo, fw, fh), _p(cx, y_pico, -fondo, fw, fh),
		m_pared, fw, fh, Color(0.68, 0.70, 0.76))

	var zf := oh_z
	var zb := -fondo - oh_z
	_quad_tiling(st, _p(ex0, y_alero, zb, fw, fh), _p(ex0, y_alero, zf, fw, fh), _p(cx, y_pico, zf, fw, fh), _p(cx, y_pico, zb, fw, fh),
		m_techo_i, fw, fh, Color(0.96, 0.96, 0.98))
	_quad_tiling(st, _p(cx, y_pico, zb, fw, fh), _p(cx, y_pico, zf, fw, fh), _p(ex1, y_alero, zf, fw, fh), _p(ex1, y_alero, zb, fw, fh),
		m_techo_d, fw, fh, Color(0.76, 0.78, 0.84))

	_aplicar_extras(st, img, cfg, xoff, yoff, fw, fh, m_techo_i)


static func _construir_domo(st: SurfaceTool, img: Image, cfg: Dictionary, xoff: int, yoff: int, fw: int, fh: int) -> void:
	var x0 := float(cfg["x0"])
	var x1 := float(cfg["x1"])
	var cap_x0 := float(cfg.get("cap_x0", x0))
	var cap_x1 := float(cfg.get("cap_x1", x1))
	var y_alero := float(cfg["y_alero"])
	var y_pico := float(cfg["y_pico"])
	var fondo := float(cfg.get("fondo", 3.2))
	var cono := bool(cfg.get("cono", false))

	var cx_m := ((x0 + x1) * 0.5 - fw * 0.5) * PX
	var rx := maxf((x1 - x0) * 0.5 * PX, 0.4)
	var rz := fondo * 0.5
	var zc := -rz
	var m_pared := _muestra(img, xoff, yoff / fh, fw, fh, int(x0) + 3, int(x0) + 18, int(y_alero) + 4, fh - 6)
	var m_techo := _muestra(img, xoff, yoff / fh, fw, fh, int(cap_x0) + 4, int(cap_x1) - 4, int(lerpf(y_pico, y_alero, 0.45)), int(y_alero) - 2)

	# Solo elementos del suelo/caldero por debajo de y_alero para no duplicar la cúpula
	_quad(st,
		_p(0, fh, 0.02, fw, fh), _p(fw, fh, 0.02, fw, fh),
		_p(fw, y_alero, 0.02, fw, fh), _p(0, y_alero, 0.02, fw, fh),
		_uv(0, fh, fw, fh), _uv(fw, fh, fw, fh), _uv(fw, y_alero, fw, fh), _uv(0, y_alero, fw, fh), Color.WHITE)

	var segs := 12
	var y_alero_m := (float(fh) - y_alero) * PX
	for i in segs:
		var a0 := -PI + TAU * float(i) / float(segs)
		var a1 := -PI + TAU * float(i + 1) / float(segs)
		var b0 := Vector3(cx_m + sin(a0) * rx, 0.0, zc + cos(a0) * rz)
		var b1 := Vector3(cx_m + sin(a1) * rx, 0.0, zc + cos(a1) * rz)
		var t1 := Vector3(b1.x, y_alero_m, b1.z)
		var t0 := Vector3(b0.x, y_alero_m, b0.z)
		var sombra := 0.72 + 0.28 * clampf(cos((a0 + a1) * 0.5), 0.0, 1.0)
		if cos((a0 + a1) * 0.5) >= 0.0:
			var px_s0 := lerpf(x0, x1, (sin(a0) + 1.0) * 0.5)
			var px_s1 := lerpf(x0, x1, (sin(a1) + 1.0) * 0.5)
			_quad(st, b0, b1, t1, t0,
				_uv(px_s0, fh, fw, fh), _uv(px_s1, fh, fw, fh), _uv(px_s1, y_alero, fw, fh), _uv(px_s0, y_alero, fw, fh),
				Color(sombra, sombra, sombra))
		else:
			_quad_tiling(st, b0, b1, t1, t0, m_pared, fw, fh, Color(sombra * 0.9, sombra * 0.92, sombra * 0.96))

	var cap_rx := maxf((cap_x1 - cap_x0) * 0.5 * PX, rx)
	var cap_rz := maxf(rz * (cap_rx / maxf(rx, 0.1)), rz)
	var cap_h := maxf((y_alero - y_pico) * PX * 0.85, 0.5)
	var anillos := 3
	for r in anillos:
		var t0 := float(r) / float(anillos)
		var t1 := float(r + 1) / float(anillos)
		var rad0 := (1.0 - t0) if cono else cos(t0 * PI * 0.5)
		var rad1 := (1.0 - t1) if cono else cos(t1 * PI * 0.5)
		var h0 := y_alero_m + cap_h * (t0 if cono else sin(t0 * PI * 0.5))
		var h1 := y_alero_m + cap_h * (t1 if cono else sin(t1 * PI * 0.5))
		var py0 := lerpf(y_alero, y_pico, t0)
		var py1 := lerpf(y_alero, y_pico, t1)
		for i in segs:
			var a0 := -PI + TAU * float(i) / float(segs)
			var a1 := -PI + TAU * float(i + 1) / float(segs)
			var p00 := Vector3(cx_m + sin(a0) * cap_rx * rad0, h0, zc + cos(a0) * cap_rz * rad0)
			var p10 := Vector3(cx_m + sin(a1) * cap_rx * rad0, h0, zc + cos(a1) * cap_rz * rad0)
			var p11 := Vector3(cx_m + sin(a1) * cap_rx * rad1, h1, zc + cos(a1) * cap_rz * rad1)
			var p01 := Vector3(cx_m + sin(a0) * cap_rx * rad1, h1, zc + cos(a0) * cap_rz * rad1)
			var am := (a0 + a1) * 0.5
			var sombra := 0.78 + 0.24 * clampf(0.4 + 0.6 * cos(am) - 0.15 * sin(am), 0.0, 1.0)
			if cos(am) >= 0.0:
				_quad(st, p00, p10, p11, p01,
					_uv(lerpf(cap_x0, cap_x1, (sin(a0) * rad0 + 1.0) * 0.5), py0, fw, fh),
					_uv(lerpf(cap_x0, cap_x1, (sin(a1) * rad0 + 1.0) * 0.5), py0, fw, fh),
					_uv(lerpf(cap_x0, cap_x1, (sin(a1) * rad1 + 1.0) * 0.5), py1, fw, fh),
					_uv(lerpf(cap_x0, cap_x1, (sin(a0) * rad1 + 1.0) * 0.5), py1, fw, fh),
					Color(sombra, sombra, sombra))
			else:
				_quad_tiling(st, p00, p10, p11, p01, m_techo, fw, fh, Color(sombra * 0.9, sombra * 0.92, sombra * 0.96))

	if cfg.has("crest_y"):
		var cy := float(cfg["crest_y"])
		var cx0 := float(cfg.get("crest_x0", 0.0))
		var cx1 := float(cfg.get("crest_x1", float(fw)))
		_quad(st,
			_p(cx0, cy, zc, fw, fh), _p(cx1, cy, zc, fw, fh), _p(cx1, 0, zc, fw, fh), _p(cx0, 0, zc, fw, fh),
			_uv(cx0, cy, fw, fh), _uv(cx1, cy, fw, fh), _uv(cx1, 0, fw, fh), _uv(cx0, 0, fw, fh), Color.WHITE)

	_aplicar_extras(st, img, cfg, xoff, yoff, fw, fh, m_techo)


static func _construir_puesto(st: SurfaceTool, img: Image, cfg: Dictionary, xoff: int, yoff: int, fw: int, fh: int) -> void:
	var x0 := float(cfg["x0"])
	var x1 := float(cfg["x1"])
	var y_mos := float(cfg["y_mostrador"])
	var y_alero := float(cfg["y_alero"])
	var y_pico := float(cfg["y_pico"])
	var fondo := float(cfg.get("fondo", 2.2))

	var m_madera := _muestra(img, xoff, yoff / fh, fw, fh, int(x0) + 4, int(x1) - 4, int(y_mos) + 4, fh - 4)
	var m_toldo := _muestra(img, xoff, yoff / fh, fw, fh, int(x0) + 4, int(x1) - 4, int(y_pico) + 2, int(y_alero) - 2)

	_quad(st,
		_p(0, fh, 0.02, fw, fh), _p(fw, fh, 0.02, fw, fh),
		_p(fw, y_pico, 0.02, fw, fh), _p(0, y_pico, 0.02, fw, fh),
		_uv(0, fh, fw, fh), _uv(fw, fh, fw, fh), _uv(fw, y_pico, fw, fh), _uv(0, y_pico, fw, fh), Color.WHITE)
	_caja_texturada(st, x0, x1, y_mos, fh, 0.0, -fondo * 0.65, fw, fh, m_madera, m_madera, false)

	var pw := 3.5
	for px in [x0, x1 - pw]:
		_caja_texturada(st, px, px + pw, y_alero, y_mos, -fondo * 0.65, -fondo * 0.9, fw, fh, m_madera, Rect2(), false)

	var y_alero_m := _p(0, y_alero, 0.0, fw, fh).y
	var y_pico_m := y_alero_m + (y_alero - y_pico) * PX * 0.72
	var fl := Vector3((x0 - 2.0 - fw * 0.5) * PX, y_alero_m, 0.25)
	var fr := Vector3((x1 + 2.0 - fw * 0.5) * PX, y_alero_m, 0.25)
	var bl := Vector3((x0 - 2.0 - fw * 0.5) * PX, y_pico_m, -fondo)
	var br := Vector3((x1 + 2.0 - fw * 0.5) * PX, y_pico_m, -fondo)
	_quad(st, fl, fr, br, bl,
		_uv(x0, y_alero, fw, fh), _uv(x1, y_alero, fw, fh), _uv(x1, y_pico, fw, fh), _uv(x0, y_pico, fw, fh), Color.WHITE)
	var bl_bot := Vector3(bl.x, y_alero_m, bl.z)
	var br_bot := Vector3(br.x, y_alero_m, br.z)
	_tri_tiling(st, bl_bot, fl, bl, m_toldo, fw, fh, Color(0.86, 0.86, 0.88))
	_tri_tiling(st, fr, br_bot, br, m_toldo, fw, fh, Color(0.72, 0.74, 0.78))


static func _construir_arbol(st: SurfaceTool, img: Image, cfg: Dictionary, xoff: int, yoff: int, fw: int, fh: int) -> void:
	var x0 := float(cfg["x0"])
	var x1 := float(cfg["x1"])
	var y_copa := float(cfg["y_copa"])
	var fondo := float(cfg.get("fondo", 4.8))
	var m_corteza := _muestra(img, xoff, yoff / fh, fw, fh, int(x0) + 4, int(x0) + 20, int(y_copa) + 10, fh - 16)
	var m_hojas := _muestra(img, xoff, yoff / fh, fw, fh, 40, 130, 18, 70)

	var rx := (x1 - x0) * 0.45 * PX
	var rz := fondo * 0.45
	var zc := -rz
	var y_copa_m := (float(fh) - y_copa) * PX
	var segs := 10
	for i in segs:
		var a0 := -PI + TAU * float(i) / float(segs)
		var a1 := -PI + TAU * float(i + 1) / float(segs)
		var p_x0 := sin(a0) * rx
		var p_z0 := zc + cos(a0) * rz
		var p_x1 := sin(a1) * rx
		var p_z1 := zc + cos(a1) * rz
		var b0 := Vector3(p_x0, 0.0, p_z0)
		var b1 := Vector3(p_x1, 0.0, p_z1)
		var t1 := Vector3(p_x1 * 0.85, y_copa_m, p_z1 * 0.85)
		var t0 := Vector3(p_x0 * 0.85, y_copa_m, p_z0 * 0.85)
		if cos((a0 + a1) * 0.5) >= 0.0:
			_quad(st, b0, b1, t1, t0,
				_uv(lerpf(x0, x1, (sin(a0) + 1.0) * 0.5), fh, fw, fh),
				_uv(lerpf(x0, x1, (sin(a1) + 1.0) * 0.5), fh, fw, fh),
				_uv(lerpf(x0, x1, (sin(a1) + 1.0) * 0.5), y_copa, fw, fh),
				_uv(lerpf(x0, x1, (sin(a0) + 1.0) * 0.5), y_copa, fw, fh), Color.WHITE)
		else:
			_quad_tiling(st, b0, b1, t1, t0, m_corteza, fw, fh, Color(0.75, 0.74, 0.76))

	for z_off: float in [0.05, -fondo * 0.48, -fondo * 0.92]:
		var s := 1.0 if z_off > -1.0 else (0.94 if z_off > -3.0 else 0.86)
		var y_base := float(fh) if z_off > 0.0 else y_copa + 18.0
		var shade := Color(1.0, 1.0, 1.0) if z_off > -1.0 else Color(0.84, 0.88, 0.84)
		_quad(st,
			_p(0, y_base, z_off, fw, fh) * s + Vector3(0, (1.0 - s) * y_copa_m, 0),
			_p(fw, y_base, z_off, fw, fh) * s + Vector3(0, (1.0 - s) * y_copa_m, 0),
			_p(fw, 0, z_off, fw, fh) * s + Vector3(0, (1.0 - s) * y_copa_m, 0),
			_p(0, 0, z_off, fw, fh) * s + Vector3(0, (1.0 - s) * y_copa_m, 0),
			_uv(0, y_base, fw, fh), _uv(fw, y_base, fw, fh), _uv(fw, 0, fw, fh), _uv(0, 0, fw, fh), shade)

	var w_h := float(fw) * 0.42 * PX
	var h_c := y_copa_m + 3.8
	_quad_tiling(st, Vector3(-w_h, h_c, 0.1), Vector3(w_h, h_c, 0.1), Vector3(w_h, h_c, -fondo * 0.9), Vector3(-w_h, h_c, -fondo * 0.9),
		m_hojas, fw, fh, Color(0.96, 1.0, 0.92))


static func _aplicar_extras(st: SurfaceTool, img: Image, cfg: Dictionary, xoff: int, yoff: int, fw: int, fh: int, m_techo: Rect2) -> void:
	for e in cfg.get("extras", []):
		var kind := String(e[0])
		if kind == "caja":
			var cx0 := float(e[1]); var cx1 := float(e[2]); var cy0 := float(e[3]); var cy1 := float(e[4])
			var cz0 := float(e[5]); var cz1 := float(e[6])
			var mc := _muestra(img, xoff, yoff / fh, fw, fh, int(cx0) + 1, int(cx1) - 1, int(cy0) + 2, int(cy1) - 2)
			_caja_texturada(st, cx0, cx1, cy0, cy1, cz1, cz0, fw, fh, mc, mc, true)
		elif kind == "frente_z":
			var fx0 := float(e[1]); var fx1 := float(e[2]); var fy0 := float(e[3]); var fy1 := float(e[4]); var fz := float(e[5])
			_quad(st,
				_p(fx0, fy1, fz, fw, fh), _p(fx1, fy1, fz, fw, fh), _p(fx1, fy0, fz, fw, fh), _p(fx0, fy0, fz, fw, fh),
				_uv(fx0, fy1, fw, fh), _uv(fx1, fy1, fw, fh), _uv(fx1, fy0, fw, fh), _uv(fx0, fy0, fw, fh), Color.WHITE)
		elif kind in ["domo_extra", "cono_extra"]:
			var cx_m := ((float(e[1]) + float(e[2])) * 0.5 - fw * 0.5) * PX
			var rx := maxf((float(e[2]) - float(e[1])) * 0.5 * PX, 0.3)
			var zc := float(e[5])
			var rz := minf(rx, absf(zc) * 0.85)
			var y_alero := float(e[3])
			var y_pico := float(e[4])
			var y_alero_m := (float(fh) - y_alero) * PX
			var cap_h := maxf((y_alero - y_pico) * PX * 0.85, 0.4)
			var mc := _muestra(img, xoff, yoff / fh, fw, fh, int(e[1]) + 3, int(e[2]) - 3, int(y_pico) + 3, int(y_alero) - 1)
			var cono := kind == "cono_extra"
			var segs := 10
			var anillos := 3
			for r in anillos:
				var t0 := float(r) / float(anillos)
				var t1 := float(r + 1) / float(anillos)
				var rad0 := (1.0 - t0) if cono else cos(t0 * PI * 0.5)
				var rad1 := (1.0 - t1) if cono else cos(t1 * PI * 0.5)
				var h0 := y_alero_m + cap_h * (t0 if cono else sin(t0 * PI * 0.5))
				var h1 := y_alero_m + cap_h * (t1 if cono else sin(t1 * PI * 0.5))
				var py0 := lerpf(y_alero, y_pico, t0)
				var py1 := lerpf(y_alero, y_pico, t1)
				for i in segs:
					var a0 := -PI + TAU * float(i) / float(segs)
					var a1 := -PI + TAU * float(i + 1) / float(segs)
					var p00 := Vector3(cx_m + sin(a0) * rx * rad0, h0, zc + cos(a0) * rz * rad0)
					var p10 := Vector3(cx_m + sin(a1) * rx * rad0, h0, zc + cos(a1) * rz * rad0)
					var p11 := Vector3(cx_m + sin(a1) * rx * rad1, h1, zc + cos(a1) * rz * rad1)
					var p01 := Vector3(cx_m + sin(a0) * rx * rad1, h1, zc + cos(a0) * rz * rad1)
					if cos((a0 + a1) * 0.5) >= 0.0:
						_quad(st, p00, p10, p11, p01,
							_uv(lerpf(float(e[1]), float(e[2]), (sin(a0) * rad0 + 1.0) * 0.5), py0, fw, fh),
							_uv(lerpf(float(e[1]), float(e[2]), (sin(a1) * rad0 + 1.0) * 0.5), py0, fw, fh),
							_uv(lerpf(float(e[1]), float(e[2]), (sin(a1) * rad1 + 1.0) * 0.5), py1, fw, fh),
							_uv(lerpf(float(e[1]), float(e[2]), (sin(a0) * rad1 + 1.0) * 0.5), py1, fw, fh), Color.WHITE)
					else:
						_quad_tiling(st, p00, p10, p11, p01, mc if mc.size.x > 0.0 else m_techo, fw, fh, Color(0.76, 0.78, 0.82))
