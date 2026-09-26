# SystemUI Motion Specification (Control Center & Notification Shade)

## 1. Top-Edge Gestures Disambiguation
* **Notification Shade / Cover Sheet:** Triggered by swipe down from top edge where $x < 0.65 \cdot W$.
  - Cards translate vertically with spring drag ($1:1$ tracking).
  - Background blurs/dims progressively.
  - Release with downward velocity $> 500\text{ px/s}$ springs open ($T_0 = 0.44\text{ s}, \zeta = 0.84$).
* **Control Center:** Triggered by swipe down from top-right corner where $x \ge 0.65 \cdot W$.
  - Control modules (Network 2x2, Media 2x2, Orientation/DoNotDisturb, Brightness/Volume sliders) cascade in with micro-stagger ($\Delta t = 8\text{ ms}$).
  - Module expansion: Long-press on a module (e.g. Brightness or Connectivity) springs open an expanded overlay with rounded corners and rubber band bounce at limits.

## 2. Continuous Slider Physics (Brightness & Volume)
* Slider pill expands slightly in width (+10%) upon touch down.
* When dragged past $0\%$ or $100\%$, displacement follows rubber band physics:
  $$\Delta y_{resist} = \left( 1 - \frac{1}{\frac{|\Delta y| \cdot 0.4}{H_{slider}} + 1} \right) \cdot H_{slider}$$
* Upon touch release, pill snaps back to bounds with spring ($T_0 = 0.28\text{ s}, \zeta = 0.75$).
