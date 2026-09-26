# UIKit UISpringTimingParameters & Velocity Projection

## 1. Parameterization Model
iOS 10+ and SwiftUI parameterize springs not by raw mass/stiffness/damping, but by intuitive perceptual attributes:
* **Response ($T_0$ / `response`):** Duration of one complete undamped cycle in seconds ($T_0 = 2\pi / \omega_0$). Represents the stiffness/speed of the spring.
* **Damping Ratio ($\zeta$ / `dampingRatio`):**
  - $\zeta = 1.0$: Critically damped (no bounce)
  - $\zeta = 0.8$: Minimal bounce (standard app dismiss / sheet dismiss)
  - $\zeta = 0.5$: Moderate bounce (playful UI, toggle bounce)
  - $\zeta = 0.0$: Pure undamped harmonic oscillation

## 2. Converting Perceptual Parameters to Physical Constants
Assuming unit mass $m = 1.0$:
$$\omega_0 = \frac{2\pi}{T_0}$$
$$k = \omega_0^2 = \left( \frac{2\pi}{T_0} \right)^2$$
$$c = 2 \zeta \sqrt{k m} = 2 \zeta \omega_0 = \frac{4\pi \zeta}{T_0}$$

### Standard iOS Motion Presets:
1. **App Exit / Home Gesture:**
   - $T_0 = 0.45\text{ s}$
   - $\zeta = 0.82$
   - $k \approx 195.0\text{ N/m}$
   - $c \approx 22.9\text{ Ns/m}$
2. **App Launch Transition:**
   - $T_0 = 0.50\text{ s}$
   - $\zeta = 0.86$
   - $k \approx 158.0\text{ N/m}$
   - $c \approx 21.6\text{ Ns/m}$
3. **Workspace Page Snapping:**
   - $T_0 = 0.38\text{ s}$
   - $\zeta = 0.88$
   - $k \approx 273.0\text{ N/m}$
   - $c \approx 29.1\text{ Ns/m}$
4. **Spotlight Pull / Dismiss:**
   - $T_0 = 0.40\text{ s}$
   - $\zeta = 0.85$

## 3. Gesture Velocity Projection & Deceleration
When a gesture ends at position $x_0$ with velocity $v_0$, iOS projects the final landing target using exponential deceleration:
$$d_{projected} = \frac{v_0}{1 - d_{rate}} \cdot \text{factor}$$
Where $d_{rate} \approx 0.996$ (UIScrollView deceleration rate).
Continuous form:
$$x(t) = x_0 + \frac{v_0}{\lambda} (1 - e^{-\lambda t})$$
$$\text{Projected resting position: } x_{\infty} = x_0 + \frac{v_0}{\lambda}$$
Where $\lambda \approx 4.0\text{ s}^{-1}$.

If $x_{\infty}$ crosses a page threshold or dismiss threshold, the transition commits to the target page/state; otherwise, it springs back to the origin.

## 4. Velocity Preservation across Handoffs
Crucial principle: **Never reset velocity to zero on state transitions.**
When user lifts finger, the current `VelocityTracker` velocity ($v_x, v_y$) must be injected directly as the initial velocity $v_0$ into the spring solver.
