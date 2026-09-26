# App Launch & Exit Transition Mechanics

## 1. App Launch Geometry & Timing
When an app icon is tapped:
1. **Target View:** The icon view located at $(x_{icon}, y_{icon})$ with size $(w_{icon}, h_{icon})$ and corner radius $r_{icon} \approx 18\text{ dp}$.
2. **Screen Bounds:** $(0, 0, W, H)$ with display corner radius $r_{screen} \approx 28\text{ dp}$ (matching device bezel).
3. **Geometry Interpolation:**
   $$\text{scaleX}(t) = \frac{w_{icon}}{W} + (1 - \frac{w_{icon}}{W}) \cdot f_{spring}(t)$$
   $$\text{scaleY}(t) = \frac{h_{icon}}{H} + (1 - \frac{h_{icon}}{H}) \cdot f_{spring}(t)$$
   $$\text{transX}(t) = (x_{icon} + \frac{w_{icon}}{2} - \frac{W}{2}) \cdot (1 - f_{spring}(t))$$
   $$\text{transY}(t) = (y_{icon} + \frac{h_{icon}}{2} - \frac{H}{2}) \cdot (1 - f_{spring}(t))$$
   $$\text{cornerRadius}(t) = r_{icon} + (r_{screen} - r_{icon}) \cdot f_{spring}(t)$$
4. **Surrounding Icons:** Subtle scale down to $0.94$ with slight focal dispersion outward from tapped icon center.

## 2. App Exit / Home Gesture Mechanics
Interactive swipe up from bottom edge:
1. **Touch Phase:**
   - App window follows finger position.
   - Scale decreases proportionally to vertical drag distance:
     $$\text{scale}(y) = 1.0 - \left( \frac{\Delta y}{H} \right) \cdot 0.45$$
   - Corner radius rapidly transitions from $r_{screen}$ toward $r_{icon}$.
   - Launcher icons behind window scale up from $0.92$ to $1.00$ with inverse alpha blend.
2. **Release Phase (`ACTION_UP`):**
   - Sample velocity $(v_x, v_y)$.
   - If release velocity $v_y < -500\text{ px/s}$ (fast swipe up) or displacement $> 0.25 \cdot H$, commit to home.
   - Target frame is exact bounding box of original app icon on home screen.
   - If velocity/displacement insufficient, spring back to fullscreen ($1.0$ scale, $0$ translation).
   - Dynamic spring parameters: Response $T_0 = 0.45\text{ s}$, Damping Ratio $\zeta = 0.82$, injecting $(v_x, v_y)$.
