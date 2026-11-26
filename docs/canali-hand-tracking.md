# hand_tracking.tox channels (v0.6.1)

Read from the tox with `toeexpand`. Hand index N = 1..Maxhands (default 2).

## normalized_data (CHOP)
Per hand: `hN:<joint>:x|y|z` for the 21 joints, plus `hN:Leftness`, `hN:Rightness`.
x, y in 0..1; y is already flipped (`1 - y`, 0 = bottom).

Joints (MediaPipe index → name):
0 wrist · 1 thumb_cmc · 2 thumb_mcp · 3 thumb_ip · **4 thumb_tip** ·
5 index_finger_mcp · 6 index_finger_pip · 7 index_finger_dip · **8 index_finger_tip** ·
9–12 middle_finger_mcp/pip/dip/tip · 13–16 ring_finger_* · 17–20 pinky_*

## helpers (CHOP)
`hN:pinch_midpoint:x|y|z|rotation|distance` (midpoint and 3D distance between index tip and thumb tip), `h1h2:distance`, `hN:Leftness|Rightness`.

## gestures (CHOP)
`hN:None|Closed_Fist|Open_Palm|Pointing_Up|Thumb_Down|Thumb_Up|Victory|ILoveYou`

## Useful parameters
- hand_tracking: `Maxhands`, `Lockhandedness` (left hand always in h1, right in h2), `Settleframes`.
- MediaPipe: `Wflip` (Horizontal Flip).
