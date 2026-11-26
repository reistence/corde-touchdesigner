#!/bin/zsh
# Converte i .mov ProRes registrati da TouchDesigner in MP4 H.264 leggeri.
#
#   ./comprimi.sh                    tutti i .mov in registrazioni/
#   ./comprimi.sh ~/Desktop/x.mov    file specifici
#   ./comprimi.sh --elimina          come sopra, e cancella il .mov se la
#                                    conversione riesce
#
# Crea <nome>.mp4 accanto all'originale. Salta i file già convertiti.
# Lanciato anche da TD (scripts/registra_fine.py) quando la registrazione
# finisce: in quel caso l'output va in registrazioni/comprimi.log.

set -euo pipefail
cd "$(dirname "$0")"

# TD non eredita il PATH della shell: ffmpeg di Homebrew va aggiunto a mano.
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

elimina=0
if [[ "${1:-}" == "--elimina" ]]; then
	elimina=1
	shift
fi

if (( $# == 0 )); then
	set -- registrazioni/*.mov(N)
fi
if (( $# == 0 )); then
	echo "Nessun .mov in registrazioni/"
	exit 0
fi

for f in "$@"; do
	out="${f:r}.mp4"
	if [[ -e "$out" ]]; then
		echo "salto $f (esiste già $out)"
		continue
	fi
	echo "→ $f"
	tmp="${f:r}.tmp.mp4"
	if ffmpeg -v error -y -i "$f" \
		-c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
		-c:a aac -b:a 192k -movflags +faststart \
		"$tmp"; then
		mv "$tmp" "$out"
		echo "  $(du -h "$f" | cut -f1) → $(du -h "$out" | cut -f1)  $out"
		if (( elimina )); then
			rm "$f"
			echo "  eliminato $f"
		fi
	else
		rm -f "$tmp"
		echo "  ERRORE: $f non convertito, lo lascio com'è"
	fi
done
