# Corde — air strings in TouchDesigner

A string instrument you draw in the air with your hands, in front of a webcam.

Pinch with both hands to stretch a glowing string between them. Let go and it stays where you left it. Swipe a finger across a string to pluck it: it vibrates, changes colour, throws sparks and plays a note whose pitch depends on its length.

Built in TouchDesigner (free Non-Commercial license is enough) with hand tracking from [mediapipe-touchdesigner](https://github.com/torinmb/mediapipe-touchdesigner). No Python install needed.

## How to play

| Gesture | What happens |
|---|---|
| Pinch thumb and index on **both** hands | A live string appears between the two pinch points, with glow and sparks |
| Release the pinch | The string is fixed in place: thin white line, tick marks along its length, a "T" cap at each end |
| Move an index fingertip **through** a fixed string | Pluck: damped vibration, colour (lime, pink or cyan), falling sparks, and a note |
| Hold **two closed fists** for ~0.6 s | Clear all strings |

Short strings play high notes, long strings low ones, on an A minor pentatonic scale across three octaves (from A2, 110 Hz). Where you pluck changes the timbre: near the middle is softer, near an end is brighter.

## Requirements

- TouchDesigner, Non-Commercial license or higher (developed on macOS, Apple Silicon)
- A webcam
- A release of [mediapipe-touchdesigner](https://github.com/torinmb/mediapipe-touchdesigner/releases) (developed with v0.6.1)
- Optional: [ffmpeg](https://ffmpeg.org/) (`brew install ffmpeg`) to compress recordings

## Setup

1. Download the latest mediapipe-touchdesigner release zip (the release asset, not "Source code") and unzip it into `vendor/mediapipe/`, so that `vendor/mediapipe/toxes/MediaPipe.tox` exists. The folder is git-ignored.
2. Open `corde.toe`. `MediaPipe` and `hand_tracking` are loaded as external `.tox` files from `vendor/`.
3. On macOS, allow camera access when asked. If the prompt doesn't appear: System Settings → Privacy & Security → Camera → enable TouchDesigner, then restart it.
4. Select the `MediaPipe` component, press `P`, and pick your webcam. Keep **Horizontal Flip** on (mirror view) and only hand tracking enabled.

The output is rendered by the `corde` GLSL TOP at 1280×720 and shown full screen through the `finestra` Window COMP.

## Project layout

```
corde.toe        TouchDesigner project
scripts/         Python and GLSL code used by the DATs, kept as text files
comprimi.sh      converts ProRes recordings to H.264 MP4
docs/            development notes (Italian)
vendor/          mediapipe-touchdesigner release (git-ignored)
registrazioni/   recordings (git-ignored)
```

Every script in `scripts/` is a DAT synced to its file (*Sync to File*), so you can edit it in your own editor and TouchDesigner reloads it.

| File | Operator | Role |
|---|---|---|
| `pinch_callbacks.py` | Script CHOP `pinch` | Pinch detection with hysteresis (on below 0.05, off above 0.09), tolerates short tracking dropouts |
| `salva_corde.py` | CHOP Execute `salva_corde` | On release, appends the string endpoints to `corde_tab` (max 64 strings, very short ones discarded) |
| `pizzico.py` | Execute DAT `pizzico` | Every frame, checks whether a fingertip's path crossed a string; picks the note; handles the clear gesture |
| `suono_callbacks.py` | Script CHOP `suono` | 44.1 kHz synth: each note is a sum of damped harmonics, up to 8 voices |
| `corde.frag` | GLSL TOP `corde` | Draws the live string, fixed strings, vibration and sparks over the webcam image |
| `registra_fine.py` | Parameter Execute `registra_fine` | When recording stops, runs `comprimi.sh` in the background |

## Network

```
MediaPipe ─hands→ hand_tracking ─┬→ sel_dita  (thumb and index tips) ──→ pizzico (Execute DAT)
          └video────────────┐    ├→ sel_pinch → pinch (Script CHOP, hysteresis) → salva_corde (CHOP Execute)
                            │    └→ sel_punti (pinch points, live string)              ↓
                            │                                         corde_tab (Table DAT)
                            │                                               ↓
                            │                          dat_corde → sel_geo / sel_pizz
                            ↓                                               ↓
                          corde (GLSL TOP, scripts/corde.frag) ←────────────┘

clock_audio (Audio Oscillator, amplitude 0) → suono (Script CHOP) → audio_out
```

`corde_tab` is the single source of truth for fixed strings: one row per string with its endpoints (`ax ay bx by`, 0–1, y up) and the state of its last pluck (`t0 pos col dir`). The shader receives it as two uniform arrays.

Operator and variable names are in Italian: *corda* = string, *pizzico* = pluck, *suono* = sound, *tacche* = tick marks, *scintille* = sparks.

## Tips

- To clear strings from the Textport: `mod.salva_corde.svuota()`
- Tuning constants (thresholds, scale, colours, spark amount) are at the top of each file in `scripts/`.
- Recordings saved to `registrazioni/` as ProRes `.mov` are converted to MP4 automatically when recording stops. To convert by hand:

  ```sh
  ./comprimi.sh                 # every .mov in registrazioni/
  ./comprimi.sh path/to/x.mov   # specific files
  ./comprimi.sh --elimina       # also delete each .mov after a successful conversion
  ```

## Credits

Hand tracking: [mediapipe-touchdesigner](https://github.com/torinmb/mediapipe-touchdesigner) by Torin Blankensmith, built on Google [MediaPipe](https://ai.google.dev/edge/mediapipe).
