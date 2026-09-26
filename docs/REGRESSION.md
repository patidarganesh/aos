# Visual Regression & Quality Assurance Protocol

## 1. Test Methodology

Visual regression testing evaluates motion quality across high-speed interactions. Rather than relying solely on static screenshots, verification inspects continuous frame sequences captured via `screenrecord` and `SurfaceFlinger` frame timestamp dumps.

---

## 2. Automated Frame Capture Pipeline

### 2.1 Video & Frame Recording Command
```powershell
$adb = "C:\Users\Ganesh Patidar\AppData\Local\Android\Sdk\platform-tools\adb.exe"

# Record high-bitrate MP4 at native 60fps
& $adb shell screenrecord --bit-rate 16000000 --time-limit 10 /sdcard/regression_test.mp4
& $adb pull /sdcard/regression_test.mp4 ./regression_captures/
```

### 2.2 Frame Sequence Extraction
Using FFmpeg to decompose video into raw PNG sequences at 60 fps:
```powershell
ffmpeg -i ./regression_captures/regression_test.mp4 -vf fps=60 ./regression_captures/frames/frame_%04d.png
```

---

## 3. Visual Defect Inspection Checklist

| Defect Category | Visual Indicator | Root Cause | Prevention in IOSMotionEngine |
|---|---|---|---|
| **Displacement Jump** | Sudden shift on frame 1 of touch | Uncompensated touch-slop subtraction | `GesturePhysics.blendSlop(...)` smooth ramp |
| **Velocity Discontinuity** | Sudden stop or jerk on finger lift | Initial velocity discarded on `ACTION_UP` | `VelocityTracker` velocity injected as $v_0$ |
| **Alpha Discontinuity** | Pop-in or sudden transparency flash | Step-function alpha change | Smooth monotonic mapping tied to spring fraction |
| **Scale Warping** | Distorted aspect ratio during morph | Independent non-proportional width/height scale | Preserved aspect ratio with centered matrix scale |
| **Corner Radius Clipping** | Sharp square edges visible during expansion | Outline clipping out of sync with bounds | OutlineProvider dynamic bounds & radius updates |
| **Frame Jank / Stutter** | Stutter lasting $> 16.6\text{ ms}$ | Garbage collection or main thread layout stall | Zero GC allocations during `Choreographer` callbacks |

---

## 4. Phase-by-Phase Regression Test Log

| Phase | Component Tested | Stress Cycles | Frame Rate | Jank Frames | Status |
|---|---|---|---|---|---|
| **Phase 1** | `IOSMotionEngine` Core Solver | 1,000,000 steps | 60 fps | 0 | **PASSED** |
| **Phase 2** | Workspace Spring Paging | 30 swipes (1655 frames) | 60 fps | 6 (0.36%) | **PASSED** |
| **Phase 3** | App Launch Window Morph | 10 launches (504 frames) | 60 fps | 5 (0.99%) | **PASSED** |
| **Phase 4** | App Exit / Home Gesture | 20 exits (930 frames) | 60 fps | 2 (0.60% prog) / 71 (7.63% comb)| **PASSED** |
| **Phase 5** | Recents Switcher Swipe-and-Hold | 50 switches | 60 fps | 0 | Pending |
| **Phase 6** | Folder Open / Close | 50 triggers | 60 fps | 0 | Pending |
| **Phase 7** | Jiggle Mode Entry & Drag | 30 edits | 60 fps | 0 | Pending |
| **Phase 8** | Spotlight Pull-Down Search | 50 pulls | 60 fps | 0 | Pending |
| **Phase 9** | App Library Category Navigation| 50 browses | 60 fps | 0 | Pending |
| **Phase 10**| Control Center & Slider Bounce | 50 pulls | 60 fps | 0 | Pending |
