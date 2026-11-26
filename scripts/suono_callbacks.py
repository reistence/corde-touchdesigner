# Script CHOP "suono" — sintesi del pizzico.
#
# Ingresso 0: un Audio Oscillator muto (Amplitude 0) a 44.1 kHz. Fa da
# "metronomo": a ogni frame porta il numero giusto di campioni audio
# (~735 a 60 fps). Lo copiamo e sostituiamo i valori con il nostro suono.
#
# Le note arrivano da pizzico.py, nello storage dell'Execute DAT "pizzico":
#   [(id, freq, pos), ...]   con id crescente
# Qui le leggiamo soltanto (scrivere durante il cook creerebbe un loop di
# dipendenze) e ricordiamo l'ultimo id suonato.
#
# Ogni nota è una somma di armoniche smorzate. Il peso dell'armonica k è
# sin(k*pi*pos)/k, come nella vibrazione dello shader: pizzicata al centro
# è più morbida, vicino a un estremo più brillante.

import math
import numpy as np

MAX_VOCI = 8           # oltre, la voce più vecchia viene tolta
DURATA = 2.5           # secondi dopo i quali una voce è spenta
ARMONICHE = 6
SMORZ = 2.2            # smorzamento della fondamentale (1/s)
ATTACCO = 0.004        # rampa iniziale contro il click, s
VOLUME = 0.35

_voci = []             # ognuna: {'freq', 'pesi', 't'}
_ultimo_id = [None]    # None = non ancora sincronizzato con la coda


def _nuova_voce(freq, pos, rate):
	pesi = []
	for k in range(1, ARMONICHE + 1):
		if freq * k > rate * 0.45:      # niente armoniche sopra Nyquist
			break
		pesi.append(abs(math.sin(k * math.pi * pos)) / k)
	somma = sum(pesi) or 1.0
	return {'freq': freq, 'pesi': [p / somma for p in pesi], 't': 0.0}


def _leggi_note(rate):
	sorgente = op('pizzico')
	note = sorgente.fetch('note', [], search=False) if sorgente else []
	if _ultimo_id[0] is None:
		# appena (ri)caricato: non risuonare le note vecchie
		_ultimo_id[0] = note[-1][0] if note else 0
		return
	for nid, freq, pos in note:
		if nid > _ultimo_id[0]:
			_voci.append(_nuova_voce(freq, pos, rate))
			_ultimo_id[0] = nid
	del _voci[:-MAX_VOCI]


def onSetupParameters(scriptOp):
	return


def onPulse(par):
	return


def onCook(scriptOp):
	scriptOp.clear()
	if not scriptOp.inputs:
		return

	scriptOp.copy(scriptOp.inputs[0])   # stessa lunghezza e rate dell'audio in ingresso
	n = scriptOp.numSamples
	rate = scriptOp.rate
	if n <= 0:
		return

	_leggi_note(rate)

	out = np.zeros(n, dtype=np.float64)
	passo = np.arange(n, dtype=np.float64) / rate

	for v in _voci:
		t = v['t'] + passo
		attacco = np.clip(t / ATTACCO, 0.0, 1.0)
		suono = np.zeros(n)
		for k, peso in enumerate(v['pesi'], start=1):
			# le armoniche alte si spengono prima
			suono += peso * np.sin(2.0 * math.pi * v['freq'] * k * t) * np.exp(-SMORZ * (0.6 + 0.4 * k) * t)
		out += suono * attacco
		v['t'] += n / rate

	_voci[:] = [v for v in _voci if v['t'] < DURATA]

	# limitatore morbido: tanti pizzichi insieme non distorcono
	out = np.tanh(out * VOLUME * 1.5)

	valori = out.astype(np.float32).tolist()
	for c in scriptOp.chans():
		c.vals = valori
	return
