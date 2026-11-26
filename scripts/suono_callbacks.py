# Script CHOP "suono" (sound): pluck synthesis.
#
# Input 0: a silent Audio Oscillator (Amplitude 0) at 44.1 kHz. It acts as a
# clock: every frame it brings the right number of audio samples
# (~735 at 60 fps). We copy it and replace the values with our sound.
#
# Notes come from pizzico.py, in the storage of the "pizzico" Execute DAT:
#   [(id, freq, pos), ...]   with increasing id
# Here we only read them (writing during the cook would create a dependency
# loop) and remember the last id played.
#
# Each note is a sum of damped harmonics. Harmonic k is weighted by
# sin(k*pi*pos)/k, like the vibration in the shader: plucked in the middle
# it sounds softer, near an end brighter.

import math
import numpy as np

MAX_VOCI = 8           # beyond this, the oldest voice is dropped
DURATA = 2.5           # seconds after which a voice is silent
ARMONICHE = 6
SMORZ = 2.2            # damping of the fundamental (1/s)
ATTACCO = 0.004        # initial ramp against clicks, s
VOLUME = 0.35

_voci = []             # each one: {'freq', 'pesi', 't'}
_ultimo_id = [None]    # None = not yet synced with the queue


def _nuova_voce(freq, pos, rate):
	pesi = []
	for k in range(1, ARMONICHE + 1):
		if freq * k > rate * 0.45:      # no harmonics above Nyquist
			break
		pesi.append(abs(math.sin(k * math.pi * pos)) / k)
	somma = sum(pesi) or 1.0
	return {'freq': freq, 'pesi': [p / somma for p in pesi], 't': 0.0}


def _leggi_note(rate):
	sorgente = op('pizzico')
	note = sorgente.fetch('note', [], search=False) if sorgente else []
	if _ultimo_id[0] is None:
		# just (re)loaded: don't replay old notes
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

	scriptOp.copy(scriptOp.inputs[0])   # same length and rate as the input audio
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
			# higher harmonics die out sooner
			suono += peso * np.sin(2.0 * math.pi * v['freq'] * k * t) * np.exp(-SMORZ * (0.6 + 0.4 * k) * t)
		out += suono * attacco
		v['t'] += n / rate

	_voci[:] = [v for v in _voci if v['t'] < DURATA]

	# soft limiter: many plucks at once don't distort
	out = np.tanh(out * VOLUME * 1.5)

	valori = out.astype(np.float32).tolist()
	for c in scriptOp.chans():
		c.vals = valori
	return
