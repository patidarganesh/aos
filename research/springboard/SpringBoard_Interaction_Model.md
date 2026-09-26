# SpringBoard Interaction & Hierarchy Model

## 1. System Layers
In SpringBoard, the desktop consists of distinct coordinate spaces and layers:
1. **Wallpaper Layer:** Fixed background, subtle parallax shift ($10-15\text{ px}$) during workspace paging; blurs dynamically during Spotlight or App Library activation.
2. **Icon Grid Layer:** Multi-page grid of app icons and widgets. Snaps with damped harmonic springs.
3. **Floating Dock Layer:** Static bottom shelf holding 4 primary apps. Preserves position during workspace horizontal scrolling. Bounces subtly with overscroll resistance.
4. **Page Indicator Layer:** Dots showing active page; pill expansion during page scrub.
5. **App Library (Rightmost Page):** Categorized collections and list view.
6. **Overlay Surfaces:**
   - Spotlight search (pulled from top/center of workspace).
   - Notification Center / Cover Sheet (pulled from top-left).
   - Control Center (pulled from top-right).

## 2. Icon Physics & Squircle Geometry
* Standard icon shape: Continuous curvature squircle (superellipse):
  $$\left| \frac{x}{a} \right|^n + \left| \frac{y}{b} \right|^n = 1 \quad \text{where } n \approx 4.6$$
* On Android, approximate via rounded rectangle with continuous corner path or vector squircle drawable.
* Touch feedback: Quick scale down to $0.90$ with stiff spring ($T_0 = 0.2\text{ s}, \zeta = 0.95$), returning immediately on release.
