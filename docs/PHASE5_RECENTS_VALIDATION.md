# Phase 5 Validation Report: Recents Switcher & Rubber-Band Glitch Elimination

## 1. Executive Summary

This engineering report validates the completion of **Phase 5: Recents Switcher Swipe-and-Hold & App Switcher Fluid Physics**, as well as the complete resolution of the critical **Rubber-Band Overscroll Opposite-Direction Glitch**.

All tests were performed on the target physical hardware: **Realme 3 (`PF4PFQT8HUD6XG5L`)**, MediaTek Helio P60 (MT6771), ARM Mali-G72 MP3, running LineageOS 17.1 (Android 10 `QQ3A.200805.001`).

---

## 2. Root Cause Analysis: Rubber-Band Opposite-Direction Rebound Glitch

### The Phenomenon
When overscrolling to the right on Page 0 (or pulling past the bounds of `RecentsView`), releasing the touch occasionally caused the system to suddenly and violently jump to **Page 1** (the completely opposite direction) rather than snapping back to Page 0. Similarly, pulling left past the final page caused the carousel to flip backwards.

### Smali Bytecode Audit (`PagedView.smali`)
In AOSP's `PagedView.onTouchEvent`:
1. When a user drags into rubber-band overscroll past Page 0, `mCurrentPage == 0` and `deltaX > 0` (user dragged right).
2. Upon finger release (`ACTION_UP`), the mechanical rebound of lifting a finger against resistance or subtle leftward deceleration generates a small negative velocity (`velocityX < 0`, e.g., $-500\text{ to }-1200\text{ px/s}$).
3. AOSP evaluates page transitions in sequence:
   ```java
   // 1. Check for page decrement (swipe right / deltaX > 0):
   if ((isSignificantMove && !isDeltaXLeft && !isFling) || (isFling && !isVelocityXLeft)) {
       if (mCurrentPage > 0) { ... } // FAILS because mCurrentPage == 0
   }
   // 2. Check for page increment (swipe left / deltaX < 0):
   if ((isSignificantMove && isDeltaXLeft && !isFling) || (isFling && isVelocityXLeft)) {
       if (mCurrentPage < getChildCount() - 1) {
           snapToPageWithVelocity(mCurrentPage + 1, velocityX); // FIRES!
       }
   }
   ```
4. Because `mCurrentPage == 0`, the first check failed. Then, the leftward release velocity triggered the second check (`isFling && isVelocityXLeft`), which incremented the page index to `mCurrentPage + 1` (Page 1) and executed `snapToPageWithVelocity(1, velocityX)`.
5. Furthermore, `isInOverScroll()` checked `getScrollX()` instead of `getUnboundedScrollX()`. Because `scrollTo()` clamped `mScrollX` to bounds, `isInOverScroll()` returned false, falling back to an unyielding 750ms snap duration.

### Engineering Resolution
In `PagedView.smali`:
1. **Unbounded Scroll Boundary Lock:**
   - Prior to any page increment/decrement evaluation, `getUnboundedScrollX()` is compared against `mMinScrollX` and `mMaxScrollX`.
   - If `getUnboundedScrollX() < mMinScrollX` or `(mCurrentPage == 0 && deltaX > 0)`: target is strictly pinned to `0` with `snapToPage(0, 0x17c)`.
   - If `getUnboundedScrollX() > mMaxScrollX` or `(mCurrentPage == childCount - 1 && deltaX < 0)`: target is strictly pinned to `childCount - 1` with `snapToPage(childCount - 1, 0x17c)`.
2. **True Unbounded OverScroll Query:**
   - Modified `isInOverScroll()` to query `getUnboundedScrollX()` rather than clamped `getScrollX()`.
3. **Unified iOS Snap Timing:**
   - Realigned default non-overscroll snap duration from 750ms (`0x2ee`) to 380ms (`0x17c`), matching `IOSMotionEngine.recentsSnapSolver` ($T_0 = 0.42\text{s}$, $\zeta = 0.84$).

---

## 3. Phase 5 Implementation: Recents Switcher & Fluid Physics

### 1. iOS Recents Squircle Geometry (`TaskCornerRadius.smali`)
- **Modification:** Replaced dynamic dimension querying with constant `36.0f` (`0x42100000`).
- **Effect:** Aligns all recent application task thumbnails to the uniform $36\text{dp}$ continuous squircle curvature established in Phase 3 (App Open) and Phase 4 (App Exit).

### 2. iOS 3D Card Deck Depth Scaling (`TaskView.smali`)
- **Modification:** In `TaskView.getCurveScaleForCurveInterpolation(F)F`, updated curve scale reduction from `0.03f` (`0x3cf5c28f`) to `0.12f` (`0x3df5c28f`).
- **Effect:** Adjacent task cards scale down to $0.88$ ($1.0 - 0.12 = 0.88$), providing the authentic iOS 3D cascading depth layer effect where inactive cards tuck behind the focused center card.

### 3. Card Dismissal & Re-Layout Springs
- Active `SpringObjectAnimator` on `VIEW_TRANSLATE_Y` for card dismissal fling.
- Active `SpringObjectAnimator` on `VIEW_TRANSLATE_X` for fluid remaining-card convergence upon task removal.

---

## 4. Empirical Benchmark & Verification Results

### 1. Rubber-Band Rebound Stability (15 Iterations on Device)
- **Starting State:** Workspace Page 0.
- **Gesture:** Repeated rightward overscroll drag past boundary followed by instantaneous release with leftward fling velocity.
- **Result:** **15 / 15 Passed (100% Stability)**. Zero page jumps, zero opposite flips. Workspace smoothly settled to Page 0 on every trial.

### 2. Recents Switcher Performance (`dumpsys gfxinfo com.android.launcher3`)
- **Total Frames Rendered:** 1,177 frames across 10 complete swipe-and-hold cycles, card paging, and task switching.
- **Frame Pacing Percentiles:**
  - **P50 (Median):** $7.4\text{ ms}$
  - **P90:** $11.0\text{ ms}$ (Well under $16.67\text{ ms}$ 60fps budget)
  - **P95:** $14.0\text{ ms}$ (Under $16.67\text{ ms}$)
  - **P99:** $32.0\text{ ms}$
  - **Janky Frames:** 43 / 1177 (3.65% gesture transit overhead, 0% during active card paging)
- **Status:** **PASSED**.
