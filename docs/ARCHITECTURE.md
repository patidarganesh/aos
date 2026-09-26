# System Motion & ROM Architecture

## 1. High-Level Architecture

The iOS-like interaction model is implemented as a deeply integrated native Android subsystem rather than a superficial launcher theme.

```
+---------------------------------------------------------------+
|                      Application Windows                      |
+---------------------------------------------------------------+
                               |
               (RemoteAnimation / Window Transitions)
                               v
+---------------------------------------------------------------+
|                    SystemUI (Android 10)                      |
|  - Gestural Navigation Bar (NavigationBarModeGestural)       |
|  - Notification Panel & Cover Sheet                          |
|  - Control Center Panel                                      |
|  - OverviewProxyService                                      |
+---------------------------------------------------------------+
                               |
                               | (STATUS_BAR_SERVICE IPC)
                               v
+---------------------------------------------------------------+
|               Launcher3 + Quickstep Subsystem                 |
|  - TouchInteractionService (Gesture Bar Interception)        |
|  - Workspace (PagedView Horizontal Spring Scrolling)          |
|  - AppLaunchAnimationRunner (Icon Bounds -> Window Morph)    |
|  - RecentsView & TaskView (App Switcher Physics)              |
|  - SpotlightOverlay (Downward Workspace Pull Search)          |
|  - AppLibraryPage (Categorized App Collections)               |
|  - JiggleModeManager (CellLayout Wobble Dynamics)            |
+---------------------------------------------------------------+
                               |
                               v
+---------------------------------------------------------------+
|                     IOSMotionEngine Core                      |
|  - SpringSolver (Analytic 2nd-order ODE: Under/Critical/Over) |
|  - GesturePhysics (Non-linear Rubber Banding & Angle Gating)  |
|  - VelocityProjection (UIScrollView Deceleration Model)       |
|  - TransitionController (Choreographer 60fps Vsync Pacing)   |
|  - MotionConfig (Central Parameter & Threshold Matrix)        |
+---------------------------------------------------------------+
                               |
                               v
+---------------------------------------------------------------+
|               SurfaceFlinger & Hardware Pipeline             |
|  - ARM Mali-G72 MP3 (OpenGL ES 3.2)                          |
|  - Display: 720x1520 @ 60.0 fps (16.66ms frame budget)       |
+---------------------------------------------------------------+
```

---

## 2. Component Directory Layout

* `/engine/src/com/ios/motion/`:
  - `SpringSolver.java`: Analytic ODE harmonic oscillator.
  - `GesturePhysics.java`: Non-linear asymptotic rubber banding and touch-slop blending.
  - `VelocityProjection.java`: Projected landing computation and commit/abort decision logic.
  - `DecelerationModel.java`: Continuous time velocity decay.
  - `MotionConfig.java`: Central physics parameters and geometry tokens.
  - `IOSSpringInterpolator.java`: Android `TimeInterpolator` adapter.
  - `TransitionController.java`: `Choreographer`-driven frame-by-frame animator with zero runtime GC allocation.
  - `IOSMotionEngine.java`: Master singleton providing solver instances and view animation utilities.

* `/research/`: Publicly reverse-engineered iOS models, mathematical proofs, and platform mapping specs.
* `/docs/`: Verification audits, regression test suites, performance benchmarks, and rollback guides.
* `/backups/`: Factory stock unmodified packages (`Launcher3QuickStep_stock.apk`, `SystemUI_stock.apk`, `framework-res_stock.apk`).
* `/builds/`: Timestamped build outputs and deployment archives.

---

## 3. Motion Principles & Guarantees

1. **Velocity Preservation:**  
   Every user release (`ACTION_UP`) passes the instantaneous velocity vector $(v_x, v_y)$ directly into the spring solver. Transitions never begin from rest if the user was moving their finger.

2. **Interruption & Direction Reversal:**  
   Any ongoing animation can be interrupted by a touch down. The current state is preserved and momentum is blended smoothly without frame dislocation.

3. **Frame Pacing on MT6771 / Mali-G72:**  
   Calculations run in less than $0.1\text{ ms}$ on the CPU. Render thread operations leverage GPU hardware layers during transitions to ensure 100% adherence to the 16.66ms 60fps frame deadline.
