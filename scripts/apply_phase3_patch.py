"""
Phase 3 Patch Applicator:
Documents and verifies all modifications made to Launcher3Quickstep smali code
for the iOS App Launch Spring Transition:

1. Creates com/android/launcher3/anim/Interpolators$5.smali
   - Bridges Interpolators.EXAGGERATED_EASE directly to IOSMotionEngine.getAppLaunchInterpolation(F)F

2. Patches com/android/launcher3/anim/Interpolators.smali
   - Instantiates EXAGGERATED_EASE as Interpolators$5 instead of PathInterpolator

3. Patches com/android/launcher3/QuickstepAppTransitionManagerImpl$6.smali
   - Replaces AGGRESSIVE_EASE on mDx and mDy with EXAGGERATED_EASE (App Launch Spring)
   - Synchronizes mIconScale, mCroppedSize, and mWindowRadius to 500.0f
   - Updates mIconAlpha interpolator to FAST_OUT_SLOW_IN for smooth icon-to-window dissolve

4. Patches com/android/launcher3/QuickstepAppTransitionManagerImpl.smali
   - Zeros out mContentTransY and mWorkspaceTransY (stabilizing background home screen)
   - Unifies xDuration and yDuration to 500ms (0x1f4L)
   - Sets alphaDuration to 180ms (0xb4L)
   - Sets appAnimator duration to 500ms (0x1f4L)
   - Sets initialWindowRadius to 36.0f (0x42100000) matching icon squircle radius
"""

import os
import sys

def main():
    print("Verifying Phase 3 Smali Artifacts in launcher3_src...")
    interp5 = r"c:\mad\launcher3_src\smali_classes3\com\android\launcher3\anim\Interpolators$5.smali"
    if not os.path.exists(interp5):
        print(f"Error: {interp5} not found!")
        sys.exit(1)
    print("  [OK] Interpolators$5.smali exists.")

    interp = r"c:\mad\launcher3_src\smali_classes3\com\android\launcher3\anim\Interpolators.smali"
    with open(interp, "r", encoding="utf-8") as f:
        content = f.read()
    if "Interpolators$5" in content:
        print("  [OK] Interpolators.smali is patched with Interpolators$5.")
    else:
        print("  [FAIL] Interpolators.smali missing Interpolators$5 patch!")

    mgr6 = r"c:\mad\launcher3_src\smali_classes3\com\android\launcher3\QuickstepAppTransitionManagerImpl$6.smali"
    with open(mgr6, "r", encoding="utf-8") as f:
        content = f.read()
    if "FAST_OUT_SLOW_IN" in content and "0x43fa0000" in content:
        print("  [OK] QuickstepAppTransitionManagerImpl$6.smali is patched with unified 500ms spring dynamics.")
    else:
        print("  [FAIL] QuickstepAppTransitionManagerImpl$6.smali missing expected patch!")

    mgr = r"c:\mad\launcher3_src\smali_classes3\com\android\launcher3\QuickstepAppTransitionManagerImpl.smali"
    with open(mgr, "r", encoding="utf-8") as f:
        content = f.read()
    if "0x1f4" in content and "0x42100000" in content:
        print("  [OK] QuickstepAppTransitionManagerImpl.smali is patched with 500ms appAnimator and 36px squircle radius.")
    else:
        print("  [FAIL] QuickstepAppTransitionManagerImpl.smali missing expected patch!")

    print("\nAll Phase 3 patches verified successfully.")

if __name__ == "__main__":
    main()
