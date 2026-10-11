shader_type canvas_item;
// CORRUPCIÓN DE GIZA sobre el suelo y los objetos del mundo (no sobre Maisha ni los enemigos).
//
// - corrupcion_base: el gris general de la región (1 = todo gris). Baja al purgar zonas.
// - Cada zona corrupta (hasta 8) es gris en su interior y su borde se apaga por escalones,
//   para que se vea pixel art y no un degradado suave.
// - Al purgar una zona, una ola devuelve el color desde su centro y, dentro de ella,
//   el color vuelve del todo aunque la región siga gris alrededor.
// Lo controla scripts/combate/gestor_corrupcion.gd

const int MAX_ZONAS = 8;
uniform int num_zonas = 0;
uniform vec2 centros[MAX_ZONAS];
uniform vec2 radios[MAX_ZONAS];        // semiejes del umbral (píxeles)
uniform float bordes[MAX_ZONAS];       // anchura del borde de aviso (píxeles)
uniform float purgas[MAX_ZONAS];       // radio de la ola de purga (1.0 = el umbral); purgada: 100 + radio con color
uniform float formas[64];              // forma natural de cada zona: 8 valores (4 amplitudes y 4 fases, armónicos 2-5)
uniform float corrupcion_base = 0.0;
uniform float fuerza_borde = 0.8;

varying vec2 pos_mundo;

void vertex() {
	pos_mundo = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

// cuánto se aleja el borde de la zona i en la dirección «v» (1.0 = elipse perfecta)
float factor(int i, vec2 v) {
	float a = atan(v.y, v.x);
	float f = 1.0;
	for (int k = 0; k < 4; k++) {
		f += formas[i * 8 + k] * sin(float(k + 2) * a + formas[i * 8 + 4 + k]);
	}
	return f;
}

float azar(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	vec4 c = COLOR;   // en Godot 4, COLOR ya trae el color de la textura
	vec2 celda = floor(pos_mundo / 2.0) * 2.0;           // bloques de 2x2 píxeles
	float t = corrupcion_base;
	bool salvada = false;
	float cerca_color = 1.0;     // 0 = junto a una zona purgada (el gris se va apagando en escalones)
	for (int i = 0; i < MAX_ZONAS; i++) {
		if (i >= num_zonas) {
			break;
		}
		vec2 d = celda - centros[i];
		vec2 n1 = d / radios[i];
		float r1 = length(n1) / factor(i, n1);                      // 1.0 = umbral (con su forma natural)
		if (purgas[i] > 50.0) {
			float radio = purgas[i] - 100.0;
			if (r1 < radio) {
				salvada = true;                                     // dentro de una zona ya purgada
			} else {
				// borde suave: el color se va perdiendo poco a poco al alejarse
				float fuera = (r1 - radio) / 0.35;
				fuera += (azar(celda + vec2(float(i) * 17.0)) - 0.5) * 0.35;
				cerca_color = min(cerca_color, clamp(floor(clamp(fuera, 0.0, 1.0) * 4.0 + 0.5) / 4.0, 0.0, 1.0));
			}
			continue;
		}
		if (r1 < purgas[i]) {
			salvada = true;                                         // la ola de purga va pasando
			continue;
		}
		vec2 n2 = d / (radios[i] + vec2(bordes[i]));
		float r2 = length(n2) / factor(i, n2);                      // 1.0 = fin del borde
		float tz = 0.0;
		if (r1 <= 1.0) {
			tz = 1.0;
		} else if (r2 < 1.0) {
			float r2_umbral = r2 / r1;
			tz = clamp((1.0 - r2) / (1.0 - r2_umbral), 0.0, 1.0) * fuerza_borde;
			tz += (azar(celda + vec2(float(i) * 31.0)) - 0.5) * 0.3;
			tz = clamp(floor(tz * 4.0 + 0.5) / 4.0, 0.0, 1.0);    // 4 escalones
		}
		t = max(t, tz);
	}
	if (salvada) {
		t = 0.0;
	}
	t *= cerca_color;
	float l = dot(c.rgb, vec3(0.3, 0.59, 0.11));
	vec3 pizarra = vec3(l * 0.55 + 0.06, l * 0.56 + 0.065, l * 0.58 + 0.078);   // gris oscuro con un matiz frío casi invisible
	COLOR = vec4(mix(c.rgb, pizarra, t), c.a);
}
