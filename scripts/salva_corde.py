# CHOP Execute DAT "salva_corde".
#
# Parametri: CHOPs = pinch, Channels = both, On to Off = On (il resto Off).
# Quando both passa da 1 a 0 (rilascio) aggiunge una riga a corde_tab
# con gli estremi tenuti da pinch (ax ay bx by).
#
# Colonne di corde_tab:
#   ax ay bx by   estremi, 0..1, y verso l'alto
#   t0            absTime.seconds dell'ultimo pizzico (-1000 = mai)
#   pos           dove è stata pizzicata, 0..1 lungo la corda
#   col           indice colore del pizzico (0 lime, 1 rosa, 2 ciano)
#   dir           verso del pizzico, +1 o -1
#
# Per svuotare la tabella dalla Textport:
#   mod.salva_corde.svuota()

LUNGHEZZA_MIN = 0.05   # corde più corte vengono scartate (pinch accidentali)
MAX_CORDE = 64         # deve coincidere con MAX_CORDE in corde.frag

GEOMETRIA = ['ax', 'ay', 'bx', 'by']
PIZZICO = ['t0', 'pos', 'col', 'dir']
PIZZICO_DEFAULT = ['-1000', '0.5', '0', '1']
INTESTAZIONE = GEOMETRIA + PIZZICO


def tabella():
	"""corde_tab con l'intestazione giusta. Migra la versione a 4 colonne."""
	tab = op('corde_tab')
	intestazione = [c.val for c in tab.row(0)] if tab.numRows else []

	if intestazione == INTESTAZIONE:
		return tab

	if intestazione == GEOMETRIA:
		# tabella della tappa 4: aggiungo le colonne del pizzico
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

	tab = tabella()
	if tab.numRows - 1 >= MAX_CORDE:
		tab.deleteRow(1)   # la più vecchia
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
