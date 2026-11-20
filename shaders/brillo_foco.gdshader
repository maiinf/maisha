shader_type canvas_item;

uniform vec4 color_brillo : source_color = vec4(0.96, 0.87, 0.60, 1.0);
uniform float intensidad : hint_range(0.0, 1.0) = 0.65;
uniform float velocidad : hint_range(0.1, 4.0) = 1.4;

void fragment() {
	vec4 tex = texture(TEXTURE, UV) * COLOR;
	float diag = fract((UV.x * 0.65 + UV.y * 0.35) - TIME * velocidad * 0.25);
	float barrido = smoothstep(0.42, 0.50, diag) * (1.0 - smoothstep(0.50, 0.58, diag));
	float pulso = 0.5 + 0.5 * sin(TIME * velocidad * 2.2);
	vec3 rgb = tex.rgb + color_brillo.rgb * (barrido * 0.35 + pulso * 0.08) * intensidad;
	COLOR = vec4(rgb, tex.a);
}
