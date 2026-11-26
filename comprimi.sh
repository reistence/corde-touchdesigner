#!/bin/zsh
# Converts ProRes .mov files recorded by TouchDesigner into lightweight H.264 MP4s.
#
#   ./comprimi.sh                    every .mov in registrazioni/
#   ./comprimi.sh path/to/x.mov      specific files
#   ./comprimi.sh --elimina          same as above, and deletes each .mov
#                                    once its conversion succeeds
#
# Writes <name>.mp4 next to the original. Skips files already converted.
# Also run by TD (scripts/registra_fine.py) when a recording stops:
# in that case the output goes to registrazioni/comprimi.log.

set -euo pipefail
cd "$(dirname "$0")"

# TD doesn't inherit the shell's PATH: add Homebrew's ffmpeg by hand.
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
	echo "No .mov files in registrazioni/"
	exit 0
fi

for f in "$@"; do
	out="${f:r}.mp4"
	if [[ -e "$out" ]]; then
		echo "skipping $f ($out already exists)"
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
			echo "  deleted $f"
		fi
	else
		rm -f "$tmp"
		echo "  ERROR: $f not converted, leaving it as is"
	fi
done
