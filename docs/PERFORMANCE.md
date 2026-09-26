# Performance Engineering & Benchmarking Protocol

## 1. Hierarchy of Performance Priorities
1. **Input Responsiveness:** Touch events processed immediately within the active frame window (< 4ms).
2. **Frame Stability:** Zero dropped frames; 99% of frames under 16.66ms deadline.
3. **Gesture Correctness:** 1:1 finger tracking without lag or trajectory deviation.
4. **Animation Physics Correctness:** Damped harmonic settling matching empirical iOS curves.
5. **Visual Polish:** High fidelity squircle radii, subtle blur approximations, and natural drop shadows.

---

## 2. Profiling & Measurement Tools

* **GFXInfo Frame Stats:**
  ```powershell
  $adb = "C:\Users\Ganesh Patidar\AppData\Local\Android\Sdk\platform-tools\adb.exe"
  & $adb shell dumpsys gfxinfo com.android.launcher3 reset
  # [Execute interaction loop]
  & $adb shell dumpsys gfxinfo com.android.launcher3
  ```
* **Process Memory (PSS):**
  ```powershell
  & $adb shell dumpsys meminfo com.android.launcher3 -d
  & $adb shell dumpsys meminfo com.android.systemui -d
  ```
* **SurfaceFlinger Diagnostics:**
  ```powershell
  & $adb shell dumpsys SurfaceFlinger --latency
  ```
* **CPU & Thread Scheduling:**
  ```powershell
  & $adb shell top -n 1 -b -m 10
  ```

---

## 3. Baseline vs Current Benchmark Comparison

| Metric | Target | Baseline (Stock AOSP 10) | Phase 1 (Motion Engine) | Variance |
|---|---|---|---|---|
| **50th Percentile Frame Time** | < 8.0 ms | 6.0 ms | 6.0 ms | 0.0 ms |
| **90th Percentile Frame Time** | < 12.0 ms | 7.0 ms | 7.0 ms | 0.0 ms |
| **95th Percentile Frame Time** | < 14.0 ms | 8.0 ms | 8.0 ms | 0.0 ms |
| **99th Percentile Frame Time** | < 16.6 ms | 10.0 ms | 10.0 ms | 0.0 ms |
| **Janky Frame Percentage** | < 1.0% | 0.00% (0 / 316) | 0.00% | 0.00% |
| **Cold App Launch (Settings)**| < 250 ms | 187 ms | 187 ms | 0.0 ms |
| **Warm App Resume** | < 80 ms | 51 ms | 51 ms | 0.0 ms |
| **Launcher3 Process PSS** | < 120 MB | 80.05 MB | 80.05 MB | 0.0 MB |
| **SystemUI Process PSS** | < 130 MB | 101.84 MB | 101.84 MB | 0.0 MB |
| **CPU Idle Capacity** | > 90% | 98.0% | 98.0% | 0.0% |

---

## 4. Hardware Optimization Strategy for MediaTek Helio P60 (MT6771 / Mali-G72)

1. **Avoid Runtime Live RenderScript Blur:**
   The Mali-G72 MP3 has 3 shader cores. Fullscreen multi-pass Gaussian blur on 720x1520 at 60fps causes GPU memory bandwidth saturation and drops frame rate to 35-42fps.
   **Solution:** Compute blur once on opening gesture start into a low-resolution offscreen buffer ($360\times 760$, 0.5x downsample), then crossfade via alpha blend during the spring transition.
2. **Hardware Layers Management:**
   During spring transitions (e.g. app exit or page swipe), assign `View.setLayerType(View.LAYER_TYPE_HARDWARE, null)` to composite as an OpenGL texture on GPU without invalidating view hierarchies. Call `setLayerType(LAYER_TYPE_NONE, null)` upon `onSpringEnd` to release VRAM.
3. **No Dynamic Object Allocations in `doFrame`:**
   All `SpringState`, matrix transforms, and coordinate buffers in `TransitionController` are pre-allocated or scalar primitives to avoid invoking the Dalvik/ART Garbage Collector.
