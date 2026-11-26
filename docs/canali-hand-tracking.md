# Canali di hand_tracking.tox (v0.6.1)

Letti dal tox con `toeexpand`. Indici N = 1..Maxhands (default 2).

## normalized_data (CHOP)
Per mano: `hN:<joint>:x|y|z` per i 21 joint, più `hN:Leftness`, `hN:Rightness`.
x, y in 0..1; y è già invertita (`1 - y`, 0 = basso).

Joint (indice MediaPipe → nome):
0 wrist · 1 thumb_cmc · 2 thumb_mcp · 3 thumb_ip · **4 thumb_tip** ·
5 index_finger_mcp · 6 index_finger_pip · 7 index_finger_dip · **8 index_finger_tip** ·
9–12 middle_finger_mcp/pip/dip/tip · 13–16 ring_finger_* · 17–20 pinky_*

## helpers (CHOP)
`hN:pinch_midpoint:x|y|z|rotation|distance` (punto medio e distanza 3D tra index tip e thumb tip), `h1h2:distance`, `hN:Leftness|Rightness`.

## gestures (CHOP)
`hN:None|Closed_Fist|Open_Palm|Pointing_Up|Thumb_Down|Thumb_Up|Victory|ILoveYou`

## Parametri utili
- hand_tracking: `Maxhands`, `Lockhandedness` (mano sinistra sempre in h1, destra in h2), `Settleframes`.
- MediaPipe: `Wflip` (Horizontal Flip).
