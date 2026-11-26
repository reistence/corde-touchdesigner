# Corde luminose in aria — TouchDesigner

Strumento a corde disegnato in aria con le mani davanti alla webcam.

## Struttura

```
corde.toe            progetto TD (da creare alla tappa 1)
scripts/             script Python dei DAT, versionati come testo
docs/                note tecniche
vendor/              release di mediapipe-touchdesigner (ignorata da git)
```

## Tappe

1. [x] Webcam e mani tracciate a schermo — [docs/tappa-1.md](docs/tappa-1.md)
2. [x] Pinch con isteresi (punto 4 ↔ 8)
3. [x] Corda viva tra i due pinch, con glow
4. [x] Corde fissate al rilascio (tabella + ridisegno)
5. [ ] Pizzico: vibrazione smorzata, scintille, suono
