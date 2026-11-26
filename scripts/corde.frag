// GLSL TOP "corde" — pixel shader.
//
// Ingresso 0: video della webcam.
// uLine  = (ax, ay, bx, by): i due punti di pinch, 0..1, y verso l'alto
//          (stessa convenzione di vUV, quindi niente conversioni).
// uState = (both, tempo in secondi (% 600), numero di corde fissate,
//           absTime.seconds pieno, per confrontarlo con t0)
// uCorde = corde fissate, una per elemento: (ax, ay, bx, by).
// uPizz  = pizzico di ciascuna corda: (t0, pos, col, dir).
//          Entrambi arrivano da corde_tab -> dat_corde -> sel_geo / sel_pizz
//          (pagina Arrays, Uniform Array).

#define MAX_CORDE 64

uniform vec4 uLine;
uniform vec4 uState;
uniform vec4 uCorde[MAX_CORDE];
uniform vec4 uPizz[MAX_CORDE];

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

// Pizzico.
const float DURATA_PIZZ = 1.6;    // secondi oltre i quali la corda è ferma
const float AMPIEZZA_PIZZ = 14.0; // spostamento iniziale massimo, px
const float SMORZ = 3.2;          // smorzamento della fondamentale
const float OMEGA = 42.0;         // velocità di oscillazione (rad/s)

vec3 colorePizzico(float i) {
	if (i < 0.5) return vec3(0.70, 1.00, 0.35);   // lime
	if (i < 1.5) return vec3(1.00, 0.50, 0.85);   // rosa
	return vec3(0.45, 0.95, 1.00);                // ciano
}

// Spostamento perpendicolare della corda nel punto t (0..1), età del pizzico
// in secondi. Corda pizzicata in "pos": le armoniche pesano sin(k*pi*pos)/k²,
// quelle alte si smorzano prima.
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

// Corda fissata: linea + tacche perpendicolari + "T" agli estremi.
// "onda" sposta linea e tacche perpendicolarmente (le teste restano ferme).
// Ritorna (distanza dalla linea, distanza da tacche e teste).
vec2 distCordaFissa(vec2 p, vec2 a, vec2 b, vec4 pizz, float ora) {
	Frame f = frameDi(p, a, b);
	float t = clamp(f.s / f.len, 0.0, 1.0);
	float onda = vibrazione(t, ora - pizz.x, pizz.y, pizz.w);
	float fuori = max(max(-f.s, f.s - f.len), 0.0);
	float lato = f.lato - onda;
	float linea = length(vec2(lato, fuori));

	// Tacche: segmenti corti perpendicolari, ogni PASSO_TACCHE pixel.
	float lungo = abs(mod(f.s + PASSO_TACCHE * 0.5, PASSO_TACCHE) - PASSO_TACCHE * 0.5);
	float tacca = length(vec2(lungo + fuori, max(abs(lato) - LUNGH_TACCA, 0.0)));

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
		vec4 pz = uPizz[i];
		vec2 d = distCordaFissa(p, c.xy * res, c.zw * res, pz, uState.w);

		// Dopo il pizzico: colore e glow pieni, poi sfumano verso il bianco.
		float eta = uState.w - pz.x;
		float accesa = (eta >= 0.0 && eta < DURATA_PIZZ * 2.0) ? exp(-eta * 1.4) : 0.0;
		vec3 tinta = mix(COL_FISSA, colorePizzico(pz.z), accesa);

		float linea = smoothstep(1.2 + accesa, 0.2, d.x);
		float segni = smoothstep(1.0, 0.2, d.y) * 0.75;
		float glow = exp(-d.x * mix(0.5, 0.25, accesa)) * mix(0.25, 1.1, accesa);

		col += tinta * (max(linea, segni) + glow);
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
