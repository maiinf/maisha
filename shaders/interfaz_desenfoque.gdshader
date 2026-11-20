shader_type canvas_item;

uniform sampler2D pantalla : hint_screen_texture, filter_linear;
uniform float fuerza : hint_range(0.0, 1.0) = 1.0;
uniform float calidez : hint_range(0.0, 1.0) = 0.25;
uniform vec4 tinte_noche : source_color = vec4(0.05, 0.04, 0.09, 1.0);

void fragment() {
	vec2 px = SCREEN_PIXEL_SIZE * (1.8 * fuerza);
	vec3 acc = texture(pantalla, SCREEN_UV).rgb * 0.20;
	acc += texture(pantalla, SCREEN_UV + vec2(px.x, 0.0)).rgb * 0.12;
	acc += texture(pantalla, SCREEN_UV - vec2(px.x, 0.0)).rgb * 0.12;
	acc += texture(pantalla, SCREEN_UV + vec2(0.0, px.y)).rgb * 0.12;
	acc += texture(pantalla, SCREEN_UV - vec2(0.0, px.y)).rgb * 0.12;
	vec2 d1 = px * 1.45;
	acc += texture(pantalla, SCREEN_UV + vec2(d1.x, d1.y)).rgb * 0.08;
	acc += texture(pantalla, SCREEN_UV + vec2(-d1.x, d1.y)).rgb * 0.08;
	acc += texture(pantalla, SCREEN_UV + vec2(d1.x, -d1.y)).rgb * 0.08;
	acc += texture(pantalla, SCREEN_UV + vec2(-d1.x, -d1.y)).rgb * 0.08;

	float luma = dot(acc, vec3(0.299, 0.587, 0.114));
	vec3 desat = mix(acc, vec3(luma), 0.38 * fuerza);

	vec2 uv_c = UV - vec2(0.5);
	float dist = length(uv_c * vec2(1.15, 0.95));
	float vineta = smoothstep(0.18, 0.78, dist);

	vec3 base = mix(desat, tinte_noche.rgb, (0.58 + 0.24 * vineta) * fuerza);
	vec3 ambar = vec3(0.18, 0.11, 0.05) * calidez * (1.0 - vineta * 0.7) * fuerza;
	base += ambar;

	COLOR = vec4(base, clamp(fuerza * 0.98, 0.0, 1.0));
}
