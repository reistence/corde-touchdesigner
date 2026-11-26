// GLSL TOP "corde" — pixel shader.
//
// Ingresso 0: video della webcam.
// uLine  = (ax, ay, bx, by): i due punti di pinch, 0..1, y verso l'alto
//          (stessa convenzione di vUV, quindi niente conversioni).
// uState = (both, tempo in secondi, numero di corde fissate, -)
// uCorde = corde fissate, una per elemento: (ax, ay, bx, by).
//          Arriva da corde_tab -> dat_corde (pagina Arrays, Uniform Array).

#define MAX_CORDE 64

uniform vec4 uLine;
uniform vec4 uState;
uniform vec4 uCorde[MAX_CORDE];

out vec4 fragColor;

const float PI = 3.14159265;

// Colore della corda mentre la tieni.
const vec3 COL_LIVE = vec3(1.0, 0.45, 0.95);

// Corde fissate: bianco leggermente freddo, con un glow appena accennato.
const vec3 COL_FISSA = vec3(0.92, 0.96, 1.0);
const float PASSO_TACCHE = 14.0;   // distanza tra le tacche, px
const float LUNGH_TACCA = 3.5;     // mezza lunghezza di una tacca, px
const float LUNGH_TESTA = 9.0;     // mezza lunghezza della "T" agli estremi, px

// Sistema di riferimento di un segmento: s lungo la corda, lato perpendicolare.
struct Frame { float s; float lato; float len; };

Frame frameDi(vec2 p, vec2 a, vec2 b) {
	vec2 ab = b - a;
	float len = max(length(ab), 1e-3);
	vec2 dir = ab / len;
	vec2 ap = p - a;
	return Frame(dot(ap, dir), dot(ap, vec2(-dir.y, dir.x)), len);
}

// Distanza (in pixel) da una corda che ondeggia tra a e b.
// L'onda è stazionaria: zero agli estremi, massima al centro.
float distCordaViva(vec2 p, vec2 a, vec2 b, float ampiezza, float tempo) {
	Frame f = frameDi(p, a, b);
	float t = clamp(f.s / f.len, 0.0, 1.0);

	// Due armoniche sfasate: un tremolio vivo, non una sinusoide pulita.
	float onda = sin(PI * t) * (
		sin(tempo * 23.0) * 0.7 +
		sin(tempo * 37.0 + t * 9.0) * 0.3
	) * ampiezza;

	float fuori = max(max(-f.s, f.s - f.len), 0.0);   // oltre gli estremi
	return length(vec2(f.lato - onda, fuori));
}

// Corda fissata: linea + tacche perpendicolari + "T" agli estremi.
// Ritorna (distanza dalla linea, distanza da tacche e teste).
vec2 distCordaFissa(vec2 p, vec2 a, vec2 b) {
	Frame f = frameDi(p, a, b);
	float fuori = max(max(-f.s, f.s - f.len), 0.0);
	float linea = length(vec2(f.lato, fuori));

	// Tacche: segmenti corti perpendicolari, ogni PASSO_TACCHE pixel.
	float lungo = abs(mod(f.s + PASSO_TACCHE * 0.5, PASSO_TACCHE) - PASSO_TACCHE * 0.5);
	float tacca = length(vec2(lungo + fuori, max(abs(f.lato) - LUNGH_TACCA, 0.0)));

	// Teste: barrette più lunghe ai due estremi.
	float latoT = max(abs(f.lato) - LUNGH_TESTA, 0.0);
	float testa = min(length(vec2(f.s, latoT)), length(vec2(f.s - f.len, latoT)));

	return vec2(linea, min(tacca, testa));
}

void main() {
	vec2 res = uTDOutputInfo.res.zw;
	vec2 p = vUV.st * res;

	vec3 col = texture(sTD2DInputs[0], vUV.st).rgb;

	// Corde fissate.
	int n = min(int(uState.z + 0.5), MAX_CORDE);
	for (int i = 0; i < n; i++) {
		vec4 c = uCorde[i];
		vec2 d = distCordaFissa(p, c.xy * res, c.zw * res);

		float linea = smoothstep(1.2, 0.2, d.x);
		float segni = smoothstep(1.0, 0.2, d.y) * 0.75;
		float glow = exp(-d.x * 0.5) * 0.25;

		col += COL_FISSA * (max(linea, segni) + glow);
	}

	// Corda viva, sopra a tutto.
	if (uState.x > 0.5) {
		vec2 a = uLine.xy * res;
		vec2 b = uLine.zw * res;
		float d = distCordaViva(p, a, b, 5.0, uState.y);

		float anima = smoothstep(1.8, 0.4, d);          // filo centrale bianco
		float glow = exp(-d * 0.35) * 0.9               // alone stretto
		           + exp(-d * 0.06) * 0.35;             // alone largo

		col += COL_LIVE * glow + vec3(anima);
	}

	fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
