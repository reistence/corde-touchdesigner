# Execute DAT "pizzico" — parametro Frame Start: On.
#
# A ogni frame guarda dove si è mossa la punta di ciascun indice
# (h1/h2:index_finger_tip, da sel_dita). Se il tratto percorso dal dito
# tra il frame precedente e questo attraversa una corda fissata, la corda
# è pizzicata: scrive in corde_tab il momento (t0), il punto lungo la
# corda (pos), un colore (col) e il verso (dir). Lo shader fa il resto.

ASPETTO = 1280 / 720   # x e y sono 0..1 su un'immagine 16:9
MARGINE = 0.04         # vicino agli estremi non conta (lì c'è il pinch)
PAUSA = 0.15           # secondi minimi tra due pizzichi della stessa corda
SALTO_MAX = 0.35       # spostamenti più grandi sono salti del tracking
NUM_COLORI = 3

DITI = ('h1:index_finger_tip', 'h2:index_finger_tip')

# Suono: lunghezza della corda -> nota. Corta = acuta, lunga = grave.
# Pentatonica minore di La su tre ottave, da La2 (110 Hz).
PENTATONICA = (0, 3, 5, 7, 10)
OTTAVE = 3
NOTA_BASE = 110.0
LUNGH_CORTA = 0.10     # in unità d'altezza dell'immagine (x già corretta)
LUNGH_LUNGA = 1.40


def _nota(lunghezza):
	n_note = len(PENTATONICA) * OTTAVE
	t = (lunghezza - LUNGH_CORTA) / (LUNGH_LUNGA - LUNGH_CORTA)
	t = min(max(t, 0.0), 1.0)
	i = int(round((1.0 - t) * (n_note - 1)))
	ottava, grado = divmod(i, len(PENTATONICA))
	return NOTA_BASE * 2 ** (ottava + PENTATONICA[grado] / 12.0)


def _suona(freq, pos):
	"""Mette la nota nello storage di questo DAT; la legge lo Script CHOP
	"suono". Ogni nota ha un id crescente, teniamo solo le ultime 32."""
	note = list(me.fetch('note', [], search=False))[-31:]
	nuovo_id = note[-1][0] + 1 if note else 1
	note.append((nuovo_id, freq, pos))
	me.store('note', note)

_prima = {}     # dito -> (x, y) al frame precedente
_colore = [0]   # colore del prossimo pizzico, gira tra i NUM_COLORI


def _cross(ax, ay, bx, by):
	return ax * by - ay * bx


def _dito(src, nome):
	cx, cy = src[nome + ':x'], src[nome + ':y']
	if cx is None or cy is None:
		return None
	x, y = cx.eval(), cy.eval()
	if x == 0 and y == 0:   # mano non rilevata
		return None
	return (x * ASPETTO, y)


def _attraversa(p0, p1, a, b):
	"""Il tratto p0->p1 incrocia il segmento a->b?
	Ritorna (posizione lungo a->b, verso) oppure None."""
	rx, ry = b[0] - a[0], b[1] - a[1]
	sx, sy = p1[0] - p0[0], p1[1] - p0[1]
	den = _cross(rx, ry, sx, sy)
	if abs(den) < 1e-9:
		return None
	qx, qy = p0[0] - a[0], p0[1] - a[1]
	t = _cross(qx, qy, sx, sy) / den   # lungo la corda
	u = _cross(qx, qy, rx, ry) / den   # lungo il movimento del dito
	if MARGINE < t < 1 - MARGINE and 0.0 <= u <= 1.0:
		return t, (1 if den > 0 else -1)
	return None


def onFrameStart(frame):
	tab = op('salva_corde').module.tabella()
	src = op('sel_dita')
	ora = absTime.seconds

	for nome in DITI:
		p1 = _dito(src, nome)
		p0 = _prima.get(nome)
		if p1 is None:
			_prima.pop(nome, None)
			continue
		_prima[nome] = p1
		if p0 is None:
			continue
		if ((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2) ** 0.5 > SALTO_MAX:
			continue

		for r in range(1, tab.numRows):
			# absTime riparte da zero a ogni apertura del progetto: un t0 "nel
			# futuro" viene da una sessione precedente e non blocca il pizzico.
			if 0.0 <= ora - float(tab[r, 't0'].val) < PAUSA:
				continue
			a = (float(tab[r, 'ax'].val) * ASPETTO, float(tab[r, 'ay'].val))
			b = (float(tab[r, 'bx'].val) * ASPETTO, float(tab[r, 'by'].val))
			colpo = _attraversa(p0, p1, a, b)
			if colpo is None:
				continue
			pos, verso = colpo
			tab[r, 't0'] = '{:.3f}'.format(ora)
			tab[r, 'pos'] = '{:.3f}'.format(pos)
			tab[r, 'col'] = _colore[0]
			tab[r, 'dir'] = verso
			_colore[0] = (_colore[0] + 1) % NUM_COLORI
			lunghezza = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
			_suona(_nota(lunghezza), pos)
	return
