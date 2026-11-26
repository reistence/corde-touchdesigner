# Corde luminose in aria — TouchDesigner

Strumento a corde disegnato in aria con le mani davanti alla webcam.

## Struttura

```
corde.toe            progetto TD (MediaPipe e hand_tracking come External .tox da vendor/)
scripts/             script Python dei DAT, versionati come testo
docs/                note tecniche
vendor/              release di mediapipe-touchdesigner (ignorata da git)
```

## Tappe

1. [x] Webcam e mani tracciate a schermo — [docs/tappa-1.md](docs/tappa-1.md)
2. [x] Pinch con isteresi (punto 4 ↔ 8)
3. [x] Corda viva tra i due pinch, con glow
4. [x] Corde fissate al rilascio (tabella + ridisegno)
5. [x] Pizzico: vibrazione smorzata, scintille, suono

## Rete in TD

```
MediaPipe ─hands→ hand_tracking ─┬→ sel_dita  (punte di pollice e indice) ──→ pizzico (Execute DAT)
          └video────────────┐    ├→ sel_pinch → pinch (Script CHOP, isteresi) → salva_corde (CHOP Execute)
                            │    └→ sel_punti (punti di pinch, corda viva)              ↓
                            │                                         corde_tab (Table DAT)
                            │                                               ↓
                            │                          dat_corde → sel_geo / sel_pizz
                            ↓                                               ↓
                          corde (GLSL TOP, scripts/corde.frag) ←────────────┘

clock_audio (Audio Oscillator, ampiezza 0) → suono (Script CHOP) → audio_out
```

Tutti gli script sono DAT sincronizzati con i file in `scripts/` (Sync to File): si modificano dall'editor e TD li ricarica.

Per svuotare le corde, nella Textport: `mod.salva_corde.svuota()`
