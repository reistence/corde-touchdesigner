// GLSL TOP "corde" (strings): pixel shader.
//
// Input 0: webcam video.
// uLine  = (ax, ay, bx, by): the two pinch points, 0..1, y up
//          (same convention as vUV, so no conversion needed).
// uState = (both, time in seconds (% 600), number of fixed strings,
//           full absTime.seconds, to compare with t0)
// uCorde = fixed strings, one per element: (ax, ay, bx, by).
// uPizz  = last pluck of each string: (t0, pos, col, dir).
//          Both come from corde_tab -> dat_corde -> sel_geo / sel_pizz
//          (Arrays page, Uniform Array).

#define MAX_CORDE 64

uniform vec4 uLine;
uniform vec4 uState;
uniform vec4 uCorde[MAX_CORDE];
uniform vec4 uPizz[MAX_CORDE];

out vec4 fragColor;

const float PI = 3.14159265;

// Colour of the string while you hold it.
const vec3 COL_LIVE = vec3(1.0, 0.45, 0.95);

// Fixed strings: slightly cool white, with a faint glow.
const vec3 COL_FISSA = vec3(0.92, 0.96, 1.0);
const float PASSO_TACCHE = 14.0;   // spacing between tick marks, px
const float LUNGH_TACCA = 3.5;     // half length of a tick mark, px
const float LUNGH_TESTA = 9.0;     // half length of the "T" caps at the ends, px

// Local frame of a segment: s along the string, lato perpendicular to it.
struct Frame { float s; float lato; float len; };

Frame frameDi(vec2 p, vec2 a, vec2 b) {
	vec2 ab = b - a;
	float len = max(length(ab), 1e-3);
	vec2 dir = ab / len;
	vec2 ap = p - a;
	return Frame(dot(ap, dir), dot(ap, vec2(-dir.y, dir.x)), len);
}

// Distance (in pixels) from a string wobbling between a and b.
// Standing wave: zero at the ends, largest in the middle.
float distCordaViva(vec2 p, vec2 a, vec2 b, float ampiezza, float tempo) {
	Frame f = frameDi(p, a, b);
	float t = clamp(f.s / f.len, 0.0, 1.0);

	// Two out-of-phase harmonics: a lively shimmer, not a clean sine.
	float onda = sin(PI * t) * (
		sin(tempo * 23.0) * 0.7 +
		sin(tempo * 37.0 + t * 9.0) * 0.3
	) * ampiezza;

	float fuori = max(max(-f.s, f.s - f.len), 0.0);   // beyond the endpoints
	return length(vec2(f.lato - onda, fuori));
}

// Pluck.
const float DURATA_PIZZ = 1.6;    // seconds after which the string is still
const float AMPIEZZA_PIZZ = 14.0; // maximum initial displacement, px
const float SMORZ = 3.2;          // damping of the fundamental
const float OMEGA = 42.0;         // oscillation speed (rad/s)

vec3 colorePizzico(float i) {
	if (i < 0.5) return vec3(0.70, 1.00, 0.35);   // lime
	if (i < 1.5) return vec3(1.00, 0.50, 0.85);   // pink
	return vec3(0.45, 0.95, 1.00);                // cyan
}

// Perpendicular displacement of the string at point t (0..1), given the pluck
// age in seconds. Plucked at "pos": harmonics are weighted sin(k*pi*pos)/k²,
// higher ones die out sooner.
float vibrazione(float t, float eta, float pos, float verso) {
	if (eta < 0.0 || eta > DURATA_PIZZ) return 0.0;
	float y = 0.0;
	for (int k = 1; k <= 3; k++) {
		float fk = float(k);
		float peso = sin(fk * PI * pos) / (fk * fk);
		y += peso * sin(fk * PI * t) * cos(fk * OMEGA * eta) * exp(-SMORZ * fk * eta);
	}
	return y * AMPIEZZA_PIZZ * verso;
}

// Sparks.
const int N_SCINTILLE = 14;
const float DURATA_SCINT = 0.8;            // maximum lifetime, s
const vec2 GRAVITA = vec2(0.0, -900.0);    // px/s², y up
const float CODA = 0.025;                  // trail length, s

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

float distSegmento(vec2 p, vec2 a, vec2 b) {
	vec2 ab = b - a;
	float t = clamp(dot(p - a, ab) / max(dot(ab, ab), 1e-6), 0.0, 1.0);
	return length(p - a - ab * t);
}

// Light from one pluck's sparks at pixel p.
// origine: plucked point (px); nrm: string normal; verso: the side the finger
// moved towards; seme: seed, different for every pluck.
float scintille(vec2 p, vec2 origine, vec2 nrm, float verso, float eta, float seme) {
	if (eta < 0.0 || eta > DURATA_SCINT) return 0.0;
	// early out: no spark reaches beyond ~600 px from the origin
	if (length(p - origine) > 600.0) return 0.0;

	float luce = 0.0;
	for (int k = 0; k < N_SCINTILLE; k++) {
		float fk = float(k);
		float h1 = hash(vec2(seme, fk));
		float h2 = hash(vec2(fk, seme + 7.31));
		float h3 = hash(vec2(seme + fk, 3.17));

		float vita = mix(0.35, 1.0, h3) * DURATA_SCINT;
		if (eta > vita) continue;

		float ang = h1 * 2.0 * PI;
		vec2 dir = normalize(vec2(cos(ang), sin(ang)) + nrm * verso * 0.9);
		vec2 v0 = dir * mix(80.0, 320.0, h2);

		vec2 testa = origine + v0 * eta + 0.5 * GRAVITA * eta * eta;
		float e0 = max(eta - CODA, 0.0);
		vec2 coda = origine + v0 * e0 + 0.5 * GRAVITA * e0 * e0;

		float d = distSegmento(p, coda, testa);
		float vivo = 1.0 - eta / vita;
		float brillio = 0.65 + 0.35 * sin(eta * 70.0 + fk * 2.3);
		luce += (smoothstep(1.0, 0.0, d) + exp(-d * 0.7) * 0.3) * vivo * brillio;
	}
	return luce;
}

// Continuous sparks from the live string. Each particle respawns every
// VITA_VIVA seconds (staggered) at a random point on the string and
// falls slowly: a fizzing dust while you hold the string.
const int N_VIVA = 12;
const float VITA_VIVA = 0.5;

float scintilleViva(vec2 p, vec2 a, vec2 b, float ora) {
	vec2 ab = b - a;
	float len = length(ab);
	if (len < 1.0) return 0.0;
	// early out: pixels too far from the string
	if (distSegmento(p, a, b) > 120.0) return 0.0;

	vec2 dirC = ab / len;
	vec2 nrm = vec2(-dirC.y, dirC.x);
	float luce = 0.0;
	for (int k = 0; k < N_VIVA; k++) {
		float fk = float(k);
		float fase = ora / VITA_VIVA + fk / float(N_VIVA);
		float nascita = floor(fase);        // identifies this "life"
		float eta = fract(fase) * VITA_VIVA;

		float h1 = hash(vec2(nascita, fk));
		float h2 = hash(vec2(fk + 0.37, nascita));
		float h3 = hash(vec2(nascita + 5.1, fk + 2.9));

		vec2 origine = mix(a, b, 0.05 + 0.9 * h1);
		vec2 v0 = nrm * (h2 * 2.0 - 1.0) * 90.0 + dirC * (h3 * 2.0 - 1.0) * 40.0;
		vec2 testa = origine + v0 * eta + 0.5 * GRAVITA * 0.35 * eta * eta;

		float d = length(p - testa);
		float vivo = 1.0 - eta / VITA_VIVA;
		luce += (smoothstep(1.3, 0.0, d) + exp(-d * 0.8) * 0.25) * vivo;
	}
	return luce;
}

// Fixed string: line + perpendicular tick marks + "T" caps at the ends.
// "onda" (wave) shifts line and ticks sideways (the caps stay put).
// Returns (distance from the line, distance from ticks and caps).
vec2 distCordaFissa(vec2 p, vec2 a, vec2 b, vec4 pizz, float ora) {
	Frame f = frameDi(p, a, b);
	float t = clamp(f.s / f.len, 0.0, 1.0);
	float onda = vibrazione(t, ora - pizz.x, pizz.y, pizz.w);
	float fuori = max(max(-f.s, f.s - f.len), 0.0);
	float lato = f.lato - onda;
	float linea = length(vec2(lato, fuori));

	// Tick marks: short perpendicular segments, every PASSO_TACCHE pixels.
	float lungo = abs(mod(f.s + PASSO_TACCHE * 0.5, PASSO_TACCHE) - PASSO_TACCHE * 0.5);
	float tacca = length(vec2(lungo + fuori, max(abs(lato) - LUNGH_TACCA, 0.0)));

	// Caps: longer bars at both ends.
	float latoT = max(abs(f.lato) - LUNGH_TESTA, 0.0);
	float testa = min(length(vec2(f.s, latoT)), length(vec2(f.s - f.len, latoT)));

	return vec2(linea, min(tacca, testa));
}

void main() {
	vec2 res = uTDOutputInfo.res.zw;
	vec2 p = vUV.st * res;

	vec3 col = texture(sTD2DInputs[0], vUV.st).rgb;

	// Fixed strings.
	int n = min(int(uState.z + 0.5), MAX_CORDE);
	for (int i = 0; i < n; i++) {
		vec4 c = uCorde[i];
		vec4 pz = uPizz[i];
		vec2 d = distCordaFissa(p, c.xy * res, c.zw * res, pz, uState.w);

		// After a pluck: full colour and glow, then fading back to white.
		float eta = uState.w - pz.x;
		float accesa = (eta >= 0.0 && eta < DURATA_PIZZ * 2.0) ? exp(-eta * 1.4) : 0.0;
		vec3 tinta = mix(COL_FISSA, colorePizzico(pz.z), accesa);

		float linea = smoothstep(1.2 + accesa, 0.2, d.x);
		float segni = smoothstep(1.0, 0.2, d.y) * 0.75;
		float glow = exp(-d.x * mix(0.5, 0.25, accesa)) * mix(0.25, 1.1, accesa);

		col += tinta * (max(linea, segni) + glow);

		// Sparks from the plucked point, white with a hint of colour.
		vec2 a = c.xy * res;
		vec2 b = c.zw * res;
		vec2 dirC = normalize(b - a + 1e-6);
		vec2 nrm = vec2(-dirC.y, dirC.x);
		float sc = scintille(p, mix(a, b, pz.y), nrm, pz.w, eta, pz.x + float(i) * 13.7);
		col += mix(vec3(1.0, 0.97, 0.9), colorePizzico(pz.z), 0.3) * sc;
	}

	// Live string, on top of everything.
	if (uState.x > 0.5) {
		vec2 a = uLine.xy * res;
		vec2 b = uLine.zw * res;
		float d = distCordaViva(p, a, b, 5.0, uState.y);

		float anima = smoothstep(1.8, 0.4, d);          // white core
		float glow = exp(-d * 0.35) * 0.9               // tight halo
		           + exp(-d * 0.06) * 0.35;             // wide halo

		col += COL_LIVE * glow + vec3(anima);
		col += mix(vec3(1.0), COL_LIVE, 0.35) * scintilleViva(p, a, b, uState.y);
	}

	fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
