# Home Screen & Jiggle Mode Physics

## 1. Paging & Scroll Dynamics
* Workspace pages scroll horizontally with 1:1 finger tracking.
* Spring-snapping to discrete pages with initial gesture velocity injection:
  $$x(t) = x_{page} + (x_0 - x_{page}) \cdot e^{-\zeta \omega_0 t} (\cos(\omega_d t) + \frac{v_0 + \zeta \omega_0 (x_0 - x_{page})}{\omega_d} \sin(\omega_d t))$$
  Parameters: Response $T_0 = 0.38\text{ s}$, Damping $\zeta = 0.88$.
* Overscroll rubber banding at leftmost (Today View / Page 0) and rightmost (App Library).

## 2. Jiggle (Edit) Mode Dynamics
* Trigger: Long-press on empty workspace ($500\text{ ms}$) or long-press on icon followed by edit menu.
* Transition: All icons scale down to $0.92$ and begin oscillating slightly out of phase.
* Jiggle Motion Model:
  $$\theta_i(t) = A_i \cdot \sin(2\pi f t + \phi_i)$$
  $$x_i(t) = X_i \cdot \sin(2\pi f t + \phi_i + \pi/4)$$
  - Frequency $f \approx 9.5\text{ Hz}$
  - Angular amplitude $A \approx 1.8^\circ$ to $2.4^\circ$
  - Translational amplitude $X \approx 0.8\text{ px}$ to $1.2\text{ px}$
  - Phase offset $\phi_i = (col \cdot 0.35 + row \cdot 0.5) \pmod{2\pi}$ gives pseudo-random organic flutter.
* Minus badges ("-") appear with spring pop-in ($T_0 = 0.25\text{ s}, \zeta = 0.70$).
* Done button in top right slides down with spring settling.
