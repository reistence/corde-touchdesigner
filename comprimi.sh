#!/bin/zsh
# Converte i .mov ProRes registrati da TouchDesigner in MP4 H.264 leggeri.
#
#   ./comprimi.sh                    tutti i .mov in registrazioni/
#   ./comprimi.sh ~/Desktop/x.mov    file specifici
#
# Crea <nome>.mp4 accanto all'originale e non tocca il .mov.
# Salta i file già convertiti.

set -euo pipefail
cd "$(dirname "$0")"

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
	ffmpeg -v error -stats -i "$f" \
		-c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
		-c:a aac -b:a 192k -movflags +faststart \
		"$out"
	echo "  $(du -h "$f" | cut -f1) → $(du -h "$out" | cut -f1)  $out"
done
