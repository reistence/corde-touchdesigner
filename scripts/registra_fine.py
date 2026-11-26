# Parameter Execute DAT "registra_fine".
#
# Parameters: OPs = registra, Parameters = record, Value Change = On.
# When Record goes back to Off, runs comprimi.sh --elimina in the background:
# the ProRes .mov becomes a lightweight H.264 .mp4 and the original is deleted.
# The script's output goes to registrazioni/comprimi.log.

import os
import subprocess

ATTESA = 2   # seconds: gives TD time to close the .mov file


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
