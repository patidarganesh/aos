# QuartzCore CASpringAnimation Mathematical Model

## 1. Overview & Behavioral Representation
`CASpringAnimation` is CoreAnimation's implementation of a damped harmonic oscillator. It governs nearly all fluid, organic physical motion throughout iOS (SpringBoard transitions, dialog bounds, sheet presentations).

## 2. Mathematical Differential Equation
The motion follows the classical second-order ordinary differential equation:
$$m \frac{d^2x}{dt^2} + c \frac{dx}{dt} + k x = 0$$

Where:
* $m$ = `mass` (typically $1.0\text{ kg}$)
* $k$ = `stiffness` (spring constant, typically $100.0\text{ N/m}$ to $1000.0\text{ N/m}$)
* $c$ = `damping` (viscous friction coefficient)
* $x(t)$ = displacement from target equilibrium ($x = p(t) - p_{target}$)

### 2.1 Derived Quantities
* **Undamped Angular Frequency:**
  $$\omega_0 = \sqrt{\frac{k}{m}}$$
* **Critical Damping Coefficient:**
  $$c_c = 2\sqrt{km} = 2 m \omega_0$$
* **Damping Ratio ($\zeta$):**
  $$\zeta = \frac{c}{c_c} = \frac{c}{2\sqrt{km}}$$

## 3. Analytic Solutions Based on Damping Ratio $\zeta$

### Case 1: Underdamped ($\zeta < 1$) — Typical for iOS Springs
The spring oscillates with decaying amplitude:
$$\omega_d = \omega_0 \sqrt{1 - \zeta^2}$$
$$x(t) = e^{-\zeta \omega_0 t} \left( C_1 \cos(\omega_d t) + C_2 \sin(\omega_d t) \right)$$

Given initial conditions at $t=0$: $x(0) = x_0$ (initial displacement), $x'(0) = v_0$ (initial gesture velocity):
$$C_1 = x_0$$
$$C_2 = \frac{v_0 + \zeta \omega_0 x_0}{\omega_d}$$

Velocity at time $t$:
$$v(t) = x'(t) = -\zeta \omega_0 x(t) + e^{-\zeta \omega_0 t} \left( -C_1 \omega_d \sin(\omega_d t) + C_2 \omega_d \cos(\omega_d t) \right)$$

### Case 2: Critically Damped ($\zeta = 1$) — Swift Non-Oscillating Settling
Reaches equilibrium fastest without overshoot:
$$x(t) = e^{-\omega_0 t} \left( C_1 + C_2 t \right)$$
$$C_1 = x_0$$
$$C_2 = v_0 + \omega_0 x_0$$

### Case 3: Overdamped ($\zeta > 1$) — Sluggish Settling
No oscillation, slower return:
$$\omega_* = \omega_0 \sqrt{\zeta^2 - 1}$$
$$x(t) = e^{-\zeta \omega_0 t} \left( C_1 e^{\omega_* t} + C_2 e^{-\omega_* t} \right)$$

## 4. Settling Duration Calculation
The animation completes when both displacement and velocity fall below perceptible thresholds:
$$|x(t_{settle})| < \epsilon_{pos} \quad \text{and} \quad |v(t_{settle})| < \epsilon_{vel}$$
For display units (pixels), $\epsilon_{pos} = 0.5\text{ px}$, $\epsilon_{vel} = 1.0\text{ px/s}$.
Analytic approximation for underdamped envelope:
$$t_{settle} \approx \frac{\ln(x_0 / \epsilon)}{\zeta \omega_0}$$

## 5. Android Implementation Strategy
* Implement analytic spring solver in pure Java (`IOSSpringSolver`).
* Feed time $t$ in seconds driven by `Choreographer.postFrameCallback` or custom `ValueAnimator`.
* Support velocity injection from Android's `VelocityTracker`.
