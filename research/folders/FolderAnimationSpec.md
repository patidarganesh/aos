# Folder Open / Close Animation Specification

## 1. Folder Open Transition
When a folder icon is tapped:
1. **Source Geometry:** Folder icon frame $(x_0, y_0, w_0, h_0)$ with 9 mini icon previews ($3\times 3$).
2. **Target Geometry:** Expanded folder card centered on screen $(x_c, y_c, W_f, H_f)$, corner radius $28\text{ dp}$.
3. **Motion Curves:**
   - Background dim / blur alpha fades in from $0.0 \to 1.0$ ($T_0 = 0.35\text{ s}, \zeta = 0.90$).
   - Surrounding workspace icons scale down to $0.94$ with subtle radial defocus.
   - Folder container expands from source frame to target frame using spring ($T_0 = 0.42\text{ s}, \zeta = 0.82$).
   - The 9 mini icons smoothly interpolate their bounds and spacing into full-size icons.

## 2. Folder Close Transition
Triggered by tapping outside the card or swiping down on folder:
* Card collapses back into exact source icon bounds.
* Spring parameters: $T_0 = 0.38\text{ s}, \zeta = 0.86$.
* Surrounding icons spring back to $1.0$ scale.
