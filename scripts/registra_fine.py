# Parameter Execute DAT "registra_fine".
#
# Parametri: OPs = registra, Parameters = record, Value Change = On.
# Quando Record torna su Off, lancia comprimi.sh --elimina in background:
# il .mov ProRes diventa un .mp4 H.264 leggero e l'originale viene cancellato.
# L'output dello script finisce in registrazioni/comprimi.log.

import os
import subprocess

ATTESA = 2   # secondi: lascia a TD il tempo di chiudere il file .mov


def onValueChange(par, prev):
	if par.name != 'record' or not prev or par.eval():
		return

	radice = project.folder
	script = os.path.join(radice, 'comprimi.sh')
	log = os.path.join(radice, 'registrazioni', 'comprimi.log')
	comando = 'sleep {} && "{}" --elimina'.format(ATTESA, script)

	with open(log, 'a') as out:
		subprocess.Popen(
			['/bin/zsh', '-c', comando],
			cwd=radice, stdout=out, stderr=subprocess.STDOUT,
			start_new_session=True,
		)
	return


def onPulse(par):
	return


def onExpressionChange(par, val, prev):
	return


def onExportChange(par, val, prev):
	return


def onEnableChange(par, val, prev):
	return


def onModeChange(par, val, prev):
	return
