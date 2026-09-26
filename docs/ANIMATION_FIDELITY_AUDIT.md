# Animation Fidelity Audit & Motion Glitch Resolution

## 1. Executive Summary

During hands-on testing prior to Phase 5, critical visual motion fidelity defects were identified:
1. **Perception of "Fake" Motion & Stuck Frames**: Transitions appeared artificial and frozen mid-flight rather than continuous.
2. **Cold Start Pop-In & Skipped Frames**: On first app launch, the transition icon failed to render initially, suddenly popping into visibility mid-flight or skipping the opening animation entirely.
3. **Black Void Flickering on App Launch**: A jarring black flicker appeared between the launcher workspace and the expanding app window.
4. **Premature Animation Truncation**: Windows abruptly snapped to final bounds before completing the iOS harmonic spring settling curve.
5. **Swipe-to-Home White Flash**: Swiping to home intermittently flashed a bright white frame before restoring the home screen.

A deep frame-by-frame analysis of native 60fps recordings (`launch_test.mp4`) and disassembly of Launcher3/Quickstep bytecode isolated the exact architectural root causes in AOSP and resolved them.

---

## 2. Root Cause Analysis & Bytecode Solutions

### Defect 1: The 10% Shape Reveal Freeze ("Fake Feeling" & "Stuck Frames")
* **Location**: [`FloatingIconView.smali:L3420-L3435`](file:///c:/mad/launcher3_src/smali_classes3/com/android/launcher3/views/FloatingIconView.smali#L3420)
* **Root Cause**:
  When `isOpening` was `true`, AOSP set `toMax = 10.0f` (`0x41200000`). The reveal progress was computed as:
  $$\text{shapeRevealProgress} = \text{boundToRange}\left(\text{mapToRange}(\text{progress}, 0, 1.0, 0, 10.0), 0, 1.0\right)$$
  Because the scale multiplier was $10.0\times$, `shapeRevealProgress` reached $1.0$ when $\text{progress} = 0.10$—just **50ms into a 500ms transition**.
  For the remaining **450ms (90% of the transition)**, the icon's outline and squircle morphing was completely frozen at $1.0$, while only the translation and scale continued. This produced an artificial, disjointed feeling where the icon morphed almost instantly and then froze.
* **Resolution**:
  Changed `toMax` from `10.0f` (`0x41200000`) to `1.0f` (`0x3f800000`). The icon outline morphs continuously across the entire 500ms harmonic curve from squircle icon to full-screen rounded window, matching authentic iOS physics.

---

### Defect 2: Cold-Start Asynchronous Pop-In & Skipped Frames
* **Location**: [`FloatingIconView.smali:L480-L515`](file:///c:/mad/launcher3_src/smali_classes3/com/android/launcher3/views/FloatingIconView.smali#L480), [`L3120-L3135`](file:///c:/mad/launcher3_src/smali_classes3/com/android/launcher3/views/FloatingIconView.smali#L3120)
* **Root Cause**:
  On a cold app launch, `FloatingIconView.fetchIcon()` dispatched icon loading to `MODEL_EXECUTOR` (a background thread) and set `FloatingIconView.setVisibility(View.INVISIBLE)` (`0x4`).
  Because `ValueAnimator.start()` runs immediately on the UI thread, `mIconLoadResult.isIconLoaded` was guaranteed to be `false` at `onAnimationStart()`, preventing the view from being made visible.
  Between 50ms and 150ms later, when the background thread finished, `onIconLoaded` ran on the UI thread and abruptly flipped visibility to `VISIBLE` (`0x0`), causing an aggressive pop-in mid-animation. If the app took longer to respond or disk I/O stalled, the animation completed while the icon was invisible, appearing completely skipped.
* **Resolution**:
  In `FloatingIconView.checkIconResult()`:
  - If `originalView instanceof BubbleTextView`, the pre-decoded static icon drawable is retrieved synchronously via `((BubbleTextView) originalView).getIcon()`.
  - `setIcon(originalView, drawable, null, 0)` is called immediately on frame 0.
  - `setVisibility(View.VISIBLE)` (`0x0`) is set synchronously before the animator starts.
  - When `MODEL_EXECUTOR` finishes loading the full adaptive icon, `onIconLoaded` seamlessly hot-swaps to the multi-layer drawable without visual interruption.
  - In `onAnimationStart()`, `setVisibility(View.VISIBLE)` is made unconditional.

---

### Defect 3: Black Void Flash on Launch
* **Location**: [`QuickstepAppTransitionManagerImpl.smali:L1003-L1030`](file:///c:/mad/launcher3_src/smali_classes3/com/android/launcher3/QuickstepAppTransitionManagerImpl.smali#L1003), [`L1104-L1109`](file:///c:/mad/launcher3_src/smali_classes3/com/android/launcher3/QuickstepAppTransitionManagerImpl.smali#L1104)
* **Root Cause**:
  During app launch, `getLauncherContentAnimator()` animated `mDragLayerAlpha` from $1.0 \to 0.0$ over 217ms via `:array_0`. Simultaneously, the opening app window alpha started at $0.0$ (`1.0 - mIconAlpha`).
  Between $t = 50\text{ms}$ and $150\text{ms}$, both the launcher DragLayer and the app window were semi-transparent. The user could see through to SurfaceFlinger's pitch-black root layer (confirmed at frames 40–43 with RGB $(0, 0, 0)$), producing a jarring black flash.
* **Resolution**:
  Modified `:array_0` to `[1.0f, 1.0f]`, keeping `mDragLayerAlpha` pinned to $1.0\text{f}$. In iOS, the home screen wallpaper and icons remain visible beneath the expanding app window until covered by the opaque window surface.

---

### Defect 4: RemoteAnimationAdapter Leash Premature Teardown
* **Location**: [`QuickstepAppTransitionManagerImpl.smali:L38`](file:///c:/mad/launcher3_src/smali_classes3/com/android/launcher3/QuickstepAppTransitionManagerImpl.smali#L38), [`L2097`](file:///c:/mad/launcher3_src/smali_classes3/com/android/launcher3/QuickstepAppTransitionManagerImpl.smali#L2097)
* **Root Cause**:
  `APP_LAUNCH_DURATION` passed to WindowManager's `RemoteAnimationAdapterCompat` was hardcoded to **450ms (`0x1c2L`)**, while `appAnimator` ran for **500ms (`0x1f4L`)**.
  At $t = 450\text{ms}$, WindowManager terminated the remote animation leash and released the app window, abruptly snapping the window to fullscreen and clipping the final 50ms of harmonic settling.
* **Resolution**:
  Updated `APP_LAUNCH_DURATION` and the adapter parameter to **500ms (`0x1f4L`)**, ensuring 100% synchronization between WindowManager and the launcher animation runner.

---

### Defect 5: Swipe-to-Home White Screenshot Flash
* **Location**: [`WindowTransformSwipeHandler.smali:L3830-L3855`](file:///c:/mad/launcher3_src/smali_classes3/com/android/quickstep/WindowTransformSwipeHandler.smali#L3830)
* **Root Cause**:
  In `switchToScreenshot()`, AOSP executed `screenshotTask(mRunningTaskId)` synchronously on the UI thread over Binder to SurfaceFlinger before checking `mGestureEndTarget`.
  When returning home (`mGestureEndTarget == HOME`), the screenshot thumbnail was immediately discarded (`taskView = null`), but the synchronous Binder transaction stalled the UI thread and caused SurfaceFlinger to composite a 1-frame blank surface (confirmed at frame 114 with RGB $(244, 244, 244)$ across the window bounds).
* **Resolution**:
  Reordered execution to check `mGestureEndTarget == HOME` before invoking `screenshotTask()`. When swiping to home, the screenshot capture is completely bypassed, eliminating the UI thread stall and white flash.

---

## 3. Bytecode Verification Matrix

| Component | Target Location | Before | After | Verified |
|---|---|---|---|---|
| **DragLayer Alpha** | `QuickstepAppTransitionManagerImpl.smali:1104` | `[1.0f, 0.0f]` | `[1.0f, 1.0f]` | YES |
| **Adapter Duration** | `QuickstepAppTransitionManagerImpl.smali:2097` | `450ms (0x1c2)` | `500ms (0x1f4)` | YES |
| **Constant Duration** | `QuickstepAppTransitionManagerImpl.smali:38` | `450ms (0x1c2L)` | `500ms (0x1f4L)` | YES |
| **Shape Reveal toMax** | `FloatingIconView.smali:3422` | `10.0f (0x41200000)` | `1.0f (0x3f800000)` | YES |
| **Synchronous Fallback** | `FloatingIconView.smali:506` | Worker thread only | `BubbleTextView.getIcon()` frame 0 | YES |
| **Visible on Start** | `FloatingIconView.smali:3120` | Conditional on loaded | Unconditional `VISIBLE` | YES |
| **Bypass Screenshot** | `WindowTransformSwipeHandler.smali:3832` | Always called | Bypassed if `HOME` | YES |

---

## 4. Automation & Deployment Artifacts

* Patch Script: [`scripts/apply_animation_fidelity_patch.py`](file:///c:/mad/scripts/apply_animation_fidelity_patch.py)
* Verification Script: [`scripts/verify_animation_fixes.py`](file:///c:/mad/scripts/verify_animation_fixes.py)
* Deployment Script: [`scripts/deploy_phase4.py`](file:///c:/mad/scripts/deploy_phase4.py)
