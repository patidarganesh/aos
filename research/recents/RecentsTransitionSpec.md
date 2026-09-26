# Recents & Quickstep Gesture Transition Specification

## 1. Overview
In modern iOS, the App Switcher / Recents is reached via an upward swipe from the bottom gesture bar combined with a slight hold or deceleration pause.

## 2. Gesture States & Thresholds
1. **Swipe Up Start:**
   - Finger touches bottom $20\text{ dp}$ zone.
   - App window scales down proportionally to vertical displacement: $\text{scale} = 1.0 - 0.35 \cdot (\Delta y / H)$.
   - Corner radius transitions from screen curvature ($28\text{ dp}$) to card curvature ($20\text{ dp}$).
2. **Hold / Deceleration Detection:**
   - If user pauses ($|v_y| < 150\text{ px/s}$) for $> 80\text{ ms}$, or passes $\Delta y > 0.30 \cdot H$ with slow velocity:
     * System delivers subtle haptic tap (`HapticFeedbackConstants.CONTEXT_CLICK`).
     * Transition enters App Switcher state.
     * Previous app cards slide into view from left with spring damping ($T_0 = 0.42\text{ s}, \zeta = 0.84$).
3. **Card Swiping in Switcher:**
   - Horizontal paging with momentum and spring snapping to card centers.
   - Flick up on a card throws it out of the switcher with velocity preservation to dismiss/kill.
