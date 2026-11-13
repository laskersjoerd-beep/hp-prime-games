HELLRAY - a Doom-style first-person shooter for the HP Prime
=============================================================
Original raycasting engine, levels and pixel art, written in Python
(hpprime module). Two levels, imps that throw fireballs, heavy brutes,
doors, health/ammo pickups, shotgun, minimap.

CONTROLS
  Up / 8        move forward          Down / 5   move back
  Left / Right  turn                  4 / 6      strafe left / right
  Enter or 0    fire shotgun          Space      open door / press exit switch
  Menu          toggle minimap        + / -      more / less detail (speed)
  Esc           quit

GOAL
  Find the blinking green EXIT switch on each level and press Space on it.
  Gold-striped grey walls are doors (Space to open).

INSTALL (same as the CubeGame example)
  Keep the folder name "HELLRAY.hpappdir" exactly as it is.
  1. Start the HP Prime Virtual Calculator or connect your HP Prime.
  2. Open HP Connectivity Kit.
  3. Drag "HELLRAY.hpappdir" onto the calculator's "Application Library".
  4. On the calculator press Apps, tap "HELLRAY".
  Requires firmware with Python support (2020 or newer).

PERFORMANCE
  Default is 64 ray columns. On a G1 press "-" for 40 columns if it feels
  slow; on a G2 press "+" for 80/107/160 for a sharper image.

ALTERNATIVE (if the app launcher doesn't work on your firmware)
  Open the Python app, create a new file and paste main.py into it.
