# Execute DAT "pizzico" (pluck). Parameter Frame Start: On.
#
# Every frame, looks at where each index fingertip moved
# (h1/h2:index_finger_tip, from sel_dita). If the path the finger travelled
# between the previous frame and this one crosses a fixed string, the string
# is plucked: writes to corde_tab the time (t0), the point along the
# string (pos), a colour (col) and the direction (dir). The shader does the rest.

ASPETTO = 1280 / 720   # x and y are 0..1 on a 16:9 image
MARGINE = 0.04         # ignored near the endpoints (that's where the pinch is)
PAUSA = 0.15           # minimum seconds between two plucks of the same string
SALTO_MAX = 0.35       # larger moves are tracking jumps
NUM_COLORI = 3

DITI = ('h1:index_finger_tip', 'h2:index_finger_tip')

# Sound: string length -> note. Short = high, long = low.
# A minor pentatonic over three octaves, from A2 (110 Hz).
PENTATONICA = (0, 3, 5, 7, 10)
OTTAVE = 3
NOTA_BASE = 110.0
LUNGH_CORTA = 0.10     # in image-height units (x already corrected)
LUNGH_LUNGA = 1.40


def _nota(lunghezza):
	n_note = len(PENTATONICA) * OTTAVE
	t = (lunghezza - LUNGH_CORTA) / (LUNGH_LUNGA - LUNGH_CORTA)
	t = min(max(t, 0.0), 1.0)
	i = int(round((1.0 - t) * (n_note - 1)))
	ottava, grado = divmod(i, len(PENTATONICA))
	return NOTA_BASE * 2 ** (ottava + PENTATONICA[grado] / 12.0)


def _suona(freq, pos):
	"""Puts the note in this DAT's storage, where the "suono" Script CHOP
	reads it. Each note has an increasing id; only the last 32 are kept."""
	note = list(me.fetch('note', [], search=False))[-31:]
	nuovo_id = note[-1][0] + 1 if note else 1
	note.append((nuovo_id, freq, pos))
	me.store('note', note)

_prima = {}     # finger -> (x, y) in the previous frame
_colore = [0]   # colour of the next pluck, cycles through NUM_COLORI


def _cross(ax, ay, bx, by):
	return ax * by - ay * bx


def _dito(src, nome):
	cx, cy = src[nome + ':x'], src[nome + ':y']
	if cx is None or cy is None:
		return None
	x, y = cx.eval(), cy.eval()
	if x == 0 and y == 0:   # hand not detected
		return None
	return (x * ASPETTO, y)


def _attraversa(p0, p1, a, b):
	"""Does the path p0->p1 cross the segment a->b?
	Returns (position along a->b, direction) or None."""
	rx, ry = b[0] - a[0], b[1] - a[1]
	sx, sy = p1[0] - p0[0], p1[1] - p0[1]
	den = _cross(rx, ry, sx, sy)
	if abs(den) < 1e-9:
		return None
	qx, qy = p0[0] - a[0], p0[1] - a[1]
	t = _cross(qx, qy, sx, sy) / den   # along the string
	u = _cross(qx, qy, rx, ry) / den   # along the finger's movement
	if MARGINE < t < 1 - MARGINE and 0.0 <= u <= 1.0:
		return t, (1 if den > 0 else -1)
	return None


# "Clear all" gesture: two closed fists held for TEMPO_PUGNI seconds.
SOGLIA_PUGNO = 0.6     # minimum Closed_Fist score (0..1)
TEMPO_PUGNI = 0.6
_pugni = {'da': None, 'armato': True}


def pugni_recenti(secondi=1.0):
	"""True if both fists were closed in the last `secondi` seconds. Used by
	salva_corde: closing your fists triggers a pinch, and that "fake" string
	is released when you open your hands, right after the fists."""
	ultimo = op('pizzico').fetch('pugni_ultimo', -1000.0, search=False)
	return 0.0 <= absTime.seconds - ultimo < secondi


def pugni_chiusi():
	"""True if both hands are making a fist."""
	g = op('hand_tracking/gestures')
	if g is None:
		return False
	valori = []
	for mano in ('h1', 'h2'):
		c = g[mano + ':Closed_Fist']
		valori.append(c.eval() if c is not None else 0.0)
	return all(v > SOGLIA_PUGNO for v in valori)


def _controlla_pugni(ora):
	if not pugni_chiusi():
		_pugni['da'] = None
		_pugni['armato'] = True   # re-armed when you open your hands
		return
	op('pizzico').store('pugni_ultimo', ora)
	if _pugni['da'] is None:
		_pugni['da'] = ora
	if _pugni['armato'] and ora - _pugni['da'] >= TEMPO_PUGNI:
		op('salva_corde').module.svuota()
		_pugni['armato'] = False   # only one clear per gesture


def onFrameStart(frame):
	ora = absTime.seconds
	_controlla_pugni(ora)

	tab = op('salva_corde').module.tabella()
	src = op('sel_dita')

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
			# absTime restarts from zero every time the project is opened: a t0
			# "in the future" comes from a previous session and doesn't block the pluck.
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
