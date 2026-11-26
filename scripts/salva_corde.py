# CHOP Execute DAT "salva_corde".
#
# Parameters: CHOPs = pinch, Channels = both, On to Off = On (the rest Off).
# When both goes from 1 to 0 (release) it appends a row to corde_tab
# with the endpoints held by pinch (ax ay bx by).
#
# corde_tab columns:
#   ax ay bx by   endpoints, 0..1, y up
#   t0            absTime.seconds of the last pluck (-1000 = never)
#   pos           where it was plucked, 0..1 along the string
#   col           pluck colour index (0 lime, 1 pink, 2 cyan)
#   dir           pluck direction, +1 or -1
#
# To clear the table: hold two closed fists for about half a second
# (pizzico.py), or from the Textport:
#   mod.salva_corde.svuota()

LUNGHEZZA_MIN = 0.05   # shorter strings are discarded (accidental pinches)
MAX_CORDE = 64         # must match MAX_CORDE in corde.frag

GEOMETRIA = ['ax', 'ay', 'bx', 'by']
PIZZICO = ['t0', 'pos', 'col', 'dir']
PIZZICO_DEFAULT = ['-1000', '0.5', '0', '1']
INTESTAZIONE = GEOMETRIA + PIZZICO


def tabella():
	"""corde_tab with the right header. Migrates the old 4-column version."""
	tab = op('corde_tab')
	intestazione = [c.val for c in tab.row(0)] if tab.numRows else []

	if intestazione == INTESTAZIONE:
		return tab

	if intestazione == GEOMETRIA:
		# old geometry-only table: add the pluck columns
		for nome, default in zip(PIZZICO, PIZZICO_DEFAULT):
			tab.appendCol([nome] + [default] * (tab.numRows - 1))
		return tab

	tab.clear()
	tab.appendRow(INTESTAZIONE)
	return tab


def svuota():
	tab = op('corde_tab')
	tab.clear()
	tab.appendRow(INTESTAZIONE)


def onOnToOff(channel, sampleIndex, val, prev):
	p = op('pinch')
	ax, ay, bx, by = (p[n].eval() for n in GEOMETRIA)

	if ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5 < LUNGHEZZA_MIN:
		return

	# Closing your fists brings thumb and index together and triggers a pinch:
	# that's not a string, it's the clear-all gesture.
	if op('pizzico').module.pugni_recenti(1.0):
		return

	tab = tabella()
	if tab.numRows - 1 >= MAX_CORDE:
		tab.deleteRow(1)   # the oldest one
	tab.appendRow(['{:.5f}'.format(v) for v in (ax, ay, bx, by)] + PIZZICO_DEFAULT)
	return


def onOffToOn(channel, sampleIndex, val, prev):
	return


def whileOn(channel, sampleIndex, val, prev):
	return


def whileOff(channel, sampleIndex, val, prev):
	return


def onValueChange(channel, sampleIndex, val, prev):
	return
