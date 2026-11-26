# Script CHOP "pinch": pinch detection with hysteresis.
#
# Input 0: sel_pinch, with the channels
#   h1:pinch_midpoint:distance|x|y  h2:pinch_midpoint:distance|x|y
#   h1:Leftness h1:Rightness        h2:Leftness h2:Rightness
#
# Output:
#   h1:pinch, h2:pinch  -> 1 while that hand is pinching, 0 otherwise
#   both                -> 1 when both hands are pinching
#   ax ay bx by         -> the string endpoints in the last frame where both
#                          hands were present and pinching.
#                          On release (both 1 -> 0) they stay put: this is
#                          where salva_corde reads the string to fix.
#
# A hand that isn't detected comes in as all zeros: we spot it by
# Leftness + Rightness == 0. If it disappears for a few frames we keep its
# state, so a tracking glitch doesn't end the string by accident.

SOGLIA_ON = 0.05    # pinch closes below this distance
SOGLIA_OFF = 0.09   # and opens again above this one
TOLLERANZA = 6      # frames of absence tolerated before releasing

_stato = {
	'h1': {'pinch': 0, 'assente': 0, 'presente': False},
	'h2': {'pinch': 0, 'assente': 0, 'presente': False},
}
_estremi = [0.0, 0.0, 0.0, 0.0]


def _valore(src, nome):
	chan = src[nome]
	return chan.eval() if chan is not None else 0.0


def _aggiorna(src, mano):
	s = _stato[mano]
	s['presente'] = _valore(src, mano + ':Leftness') + _valore(src, mano + ':Rightness') > 0

	if not s['presente']:
		s['assente'] += 1
		if s['assente'] > TOLLERANZA:
			s['pinch'] = 0
		return s['pinch']

	s['assente'] = 0
	d = _valore(src, mano + ':pinch_midpoint:distance')
	if s['pinch'] == 0 and d < SOGLIA_ON:
		s['pinch'] = 1
	elif s['pinch'] == 1 and d > SOGLIA_OFF:
		s['pinch'] = 0
	return s['pinch']


def onSetupParameters(scriptOp):
	return


def onPulse(par):
	return


def onCook(scriptOp):
	scriptOp.clear()
	if not scriptOp.inputs:
		return

	src = scriptOp.inputs[0]
	h1 = _aggiorna(src, 'h1')
	h2 = _aggiorna(src, 'h2')
	both = 1 if (h1 and h2) else 0

	if both and _stato['h1']['presente'] and _stato['h2']['presente']:
		_estremi[:] = [
			_valore(src, 'h1:pinch_midpoint:x'),
			_valore(src, 'h1:pinch_midpoint:y'),
			_valore(src, 'h2:pinch_midpoint:x'),
			_valore(src, 'h2:pinch_midpoint:y'),
		]

	scriptOp.appendChan('h1:pinch')[0] = h1
	scriptOp.appendChan('h2:pinch')[0] = h2
	scriptOp.appendChan('both')[0] = both
	for nome, v in zip(('ax', 'ay', 'bx', 'by'), _estremi):
		scriptOp.appendChan(nome)[0] = v
	return
