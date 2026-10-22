shader_type spatial;
render_mode blend_mix, depth_draw_always, cull_back, diffuse_burley, specular_schlick_ggx;

uniform vec4 color_superficie : source_color = vec4(0.28, 0.68, 0.84, 0.80);
uniform vec4 color_profundo : source_color = vec4(0.12, 0.38, 0.58, 0.95);
uniform vec4 color_espuma : source_color = vec4(0.92, 0.98, 1.0, 0.90);
uniform float velocidad_ola : hint_range(0.0, 5.0) = 0.8;
uniform float escala_ola : hint_range(0.1, 10.0) = 2.4;
uniform float distancia_espuma : hint_range(0.01, 1.0) = 0.12;

uniform sampler2D depth_texture : hint_depth_texture, filter_linear_mipmap;


void vertex() {
	float ola = sin(VERTEX.x * escala_ola + TIME * velocidad_ola) * cos(VERTEX.z * escala_ola * 0.8 + TIME * velocidad_ola * 1.2) * 0.02;
	VERTEX.y += ola;
}


void fragment() {
	float depth = texture(depth_texture, SCREEN_UV).r;
	vec3 ndc = vec3(SCREEN_UV * 2.0 - 1.0, depth);
	vec4 view = INV_PROJECTION_MATRIX * vec4(ndc, 1.0);
	view.xyz /= view.w;
	float linear_depth = -view.z;
	float profundidad_agua = linear_depth - VERTEX.z;

	float f_prof = clamp(profundidad_agua * 1.5, 0.0, 1.0);
	vec4 col_base = mix(color_superficie, color_profundo, f_prof);

	float f_espuma = 1.0 - smoothstep(0.0, distancia_espuma, profundidad_agua);
	vec4 col_final = mix(col_base, color_espuma, f_espuma * 0.85);

	ALBEDO = col_final.rgb;
	ALPHA = col_final.a;
	ROUGHNESS = 0.12;
	SPECULAR = 0.65;
}
