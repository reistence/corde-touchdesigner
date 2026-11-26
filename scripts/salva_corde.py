# CHOP Execute DAT "salva_corde".
#
# Parametri: CHOPs = pinch, Channels = both, On to Off = On (il resto Off).
# Quando both passa da 1 a 0 (rilascio) aggiunge una riga a corde_tab
# con gli estremi tenuti da pinch (ax ay bx by).
#
# Per svuotare la tabella dalla Textport:
#   mod.salva_corde.svuota()

LUNGHEZZA_MIN = 0.05   # corde più corte vengono scartate (pinch accidentali)
MAX_CORDE = 64         # deve coincidere con MAX_CORDE in corde.frag

INTESTAZIONE = ['ax', 'ay', 'bx', 'by']


def _tabella():
	tab = op('corde_tab')
	if tab.numRows == 0 or [c.val for c in tab.row(0)] != INTESTAZIONE:
		tab.clear()
		tab.appendRow(INTESTAZIONE)
	return tab


def svuota():
	tab = op('corde_tab')
	tab.clear()
	tab.appendRow(INTESTAZIONE)


def onOnToOff(channel, sampleIndex, val, prev):
	p = op('pinch')
	ax, ay, bx, by = (p[n].eval() for n in INTESTAZIONE)

	if ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5 < LUNGHEZZA_MIN:
		return

	tab = _tabella()
	if tab.numRows - 1 >= MAX_CORDE:
		tab.deleteRow(1)   # la più vecchia
	tab.appendRow(['{:.5f}'.format(v) for v in (ax, ay, bx, by)])
	return


def onOffToOn(channel, sampleIndex, val, prev):
	return


def whileOn(channel, sampleIndex, val, prev):
	return


def whileOff(channel, sampleIndex, val, prev):
	return


def onValueChange(channel, sampleIndex, val, prev):
	return
