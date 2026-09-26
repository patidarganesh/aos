# Fluid Gesture Handling & Rubber Banding Physics

## 1. Rubber Banding (Resistive Overscroll)
When dragging beyond scroll boundaries (e.g. workspace leftmost/rightmost, top of notification shade, volume slider limits), displacement follows a non-linear resistive curve.

### Mathematical Formulation
$$x_{resist} = \left( 1.0 - \frac{1.0}{\frac{x_{raw} \cdot c}{d} + 1.0} \right) \cdot d$$
Where:
* $x_{raw}$ = raw gesture displacement past boundary
* $d$ = dimension of view (screen width or height, e.g. 720 or 1520)
* $c$ = coefficient of resistance (typically $c = 0.55$)

### Derivative (Instantaneous Resistance)
$$\frac{dx_{resist}}{dx_{raw}} = \frac{c}{\left( \frac{x_{raw} \cdot c}{d} + 1.0 \right)^2}$$
As displacement increases, the perceived resistance approaches infinity, asymptotically capping displacement at $d$.

## 2. Gesture Cancellation & Redirection
When user changes direction mid-gesture:
1. Position tracks finger 1:1 without smoothing lag (`touch_slop` must only gate gesture start, then be subtracted or blended to prevent sudden jump).
2. Velocity is smoothed over a short sliding window (last 3-4 touch samples) to avoid noise spikes.
3. If an animation is already in progress and a touch occurs, the animation is interrupted immediately:
   - Current interpolated position becomes gesture starting point.
   - Any residual momentum is either absorbed or blended with new touch vector.

## 3. Directional Disambiguation
To separate Spotlight pull-down from horizontal page swipe:
* Angle threshold:
  - If $|\Delta y| > 1.5 \cdot |\Delta x|$ and $y_{touch} < \text{screen\_height} \cdot 0.8$, engage Spotlight drag.
  - If $|\Delta x| > |\Delta y|$, engage Workspace horizontal paging.
* Touch lock: Once a gesture commits past $8\text{ dp}$ in one direction, lock the alternate axis until finger release (`ACTION_UP`).
