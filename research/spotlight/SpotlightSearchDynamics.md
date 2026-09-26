# Spotlight Search Interaction & Motion Dynamics

## 1. Trigger Gesture
* Downward swipe on any empty area of the workspace.
* Angle restriction: $|\Delta y| > 1.5 \cdot |\Delta x|$, starting in upper 75% of screen.
* Disambiguation:
  - Scrolling begins only after passing $8\text{ dp}$ slop.
  - Does NOT trigger if pulling down from very top status bar edge (which opens Notification Shade / Cover Sheet).

## 2. Interactive Pull Progress
As finger moves down by $y$:
* Progress factor: $p = \min(1.0, y / 180\text{ dp})$.
* Search bar translates down from $y = -50\text{ dp}$ to resting position $y = 80\text{ dp}$.
* Workspace icons scale down: $s = 1.0 - 0.08 \cdot p$ (down to $0.92$).
* Backdrop blur / dim alpha: $\alpha = 0.6 \cdot p$.
* On release:
  - If $p > 0.4$ or $v_y > 400\text{ px/s}$: spring open to $p=1.0$, automatically trigger soft keyboard.
  - If cancelled ($p \le 0.4$ and $v_y \le 0$): spring close back to $p=0.0$.
  - Spring parameters: $T_0 = 0.40\text{ s}, \zeta = 0.85$.
