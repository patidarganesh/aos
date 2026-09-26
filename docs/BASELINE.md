# Baseline Hardware, OS, & Performance Audit

**Audit Date:** 2026-09-26  
**Audited Device:** Realme 3 (Model: Phh-Treble vanilla / Realme 3 `RMX1821/RMX1825`)  
**Android Version:** 10 (Release: 10, Build ID: `QQ3A.200805.001`, Security Patch: 2020-08-05)  
**Flavor / Target:** `treble_arm64_bvS-userdebug` (AOSP 10 / LineageOS 17.1 Treble base, tag: `android-10.0.0_r41`)  

---

## 1. System & Hardware Specifications

| Component | Specification / Detected Value | Source / Confirmation Command |
|---|---|---|
| **Device Model** | Realme 3 (`phhgsi_arm64_ab`) | `ro.product.model`, `ro.product.device` |
| **Manufacturer** | Realme (`ro.product.manufacturer`) | `getprop ro.product.manufacturer` |
| **SoC / Platform** | MediaTek MT6771 (Helio P60, 4x Cortex-A73 @ 2.0GHz + 4x Cortex-A53 @ 2.0GHz) | `ro.board.platform`, `/proc/cpuinfo` |
| **GPU** | ARM Mali-G72 MP3, OpenGL ES 3.2 v1.r20p0-01rel0 | `dumpsys SurfaceFlinger` (GLES vendor string) |
| **Display Resolution**| 720 x 1520 px (19:9 ratio, waterdrop notch) | `wm size`, `DisplayDeviceInfo` |
| **Display Density** | 320 dpi (xhdpi, 2.0x scale factor) | `wm density` |
| **Refresh Rate** | 60.0 fps (vsync period: 16.666 ms, deadline: 9.366 ms) | `dumpsys display` |
| **Total System RAM** | 3,829,428 kB (~4.0 GB physical LPDDR4X) | `/proc/meminfo` |
| **Available RAM** | 2,566,844 kB (~2.5 GB free/cached at baseline) | `/proc/meminfo` |
| **System Partition** | 4.5 GB total (1.5 GB used, 2.9 GB available, 36% used) | `df -h /system` |
| **Data Partition** | 50.0 GB total (1.4 GB used, 48.0 GB available, 3% used) | `df -h /data` |

---

## 2. ROM Component Identification

### 2.1 Launcher3 Implementation
* **Package:** `com.android.launcher3`
* **APK Location:** `/system/product/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk`
* **Version Code:** 29
* **Version Name:** 10
* **Target SDK:** 29 (Android 10 Q)
* **Architecture:** Launcher3 with Quickstep integration (`Launcher3QuickStep`).

### 2.2 Quickstep Implementation
* **Service:** `com.android.launcher3/com.android.quickstep.TouchInteractionService`
* **Intent Filter:** `android.intent.action.QUICKSTEP_SERVICE`
* **Permission:** `android.permission.STATUS_BAR_SERVICE`
* **Navigation Overlay Enabled:** `com.android.internal.systemui.navbar.gestural` (full gesture navigation mode active).
* **Overview Provider:** Integrated in Launcher3 (`TouchInteractionService`), bound directly to SystemUI's `OverviewProxyService`.

### 2.3 SystemUI Implementation
* **Package:** `com.android.systemui`
* **APK Location:** `/system/product/priv-app/SystemUI/SystemUI.apk`
* **Process:** `com.android.systemui`
* **System Overlays:** Treble navbar and falselocks overlays (`me.phh.treble.overlay.systemui.falselocks`).

### 2.4 Framework Animation & Window-Management Components
* **Framework Resources:** `/system/framework/framework-res.apk`
* **Window Animation Scale:** `1.0`
* **Transition Animation Scale:** `1.0`
* **Animator Duration Scale:** `1.0`
* **Window Manager:** `com.android.server.wm.WindowManagerService`
* **Recents Animation:** `com.android.server.wm.RecentsAnimation` (Android 10 remote transition model).

---

## 3. Build System & Compilation Target

* **Build System:** Android Open Source Project (AOSP / Soong / Kati build system)
* **Lunch Target:** `treble_arm64_bvS-userdebug`
* **Clean Build Command (Reference):**
  ```bash
  source build/envsetup.sh
  lunch treble_arm64_bvS-userdebug
  make -j$(nproc) systemimage
  ```
* **Host Modular Build Pipeline:**
  - AAPT / AAPT2: Android SDK Build-Tools 37.0.0 (`aapt.exe`)
  - Java Compiler: JDK 8/11/17 (`javac.exe`)
  - D8 Dexer: Android SDK Build-Tools 37.0.0 (`d8.bat`)
  - Zipalign: `zipalign.exe`
  - Apksigner: `apksigner.bat`

---

## 4. Baseline Performance Measurements

Measurements captured from untouched baseline system on device `PF4PFQT8HUD6XG5L`:

### 4.1 Boot Performance
* **Boot Start (`boot_progress_start`):** 83,391 ms
* **Preload End (`boot_progress_preload_end`):** 86,717 ms (~3.32s preload)
* **Package Manager Ready (`boot_progress_pms_ready`):** 88,163 ms
* **Activity Manager Ready (`boot_progress_ams_ready`):** 89,285 ms
* **Screen Enabled (`boot_progress_enable_screen`):** 90,651 ms (7.26 seconds from init)
* **Framework Boot Completed (`framework_boot_completed`):** 92,802 ms (9.41 seconds from init)

### 4.2 App & Launcher Startup Times
* **Stock Settings Cold Launch:**
  - `TotalTime`: **187 ms**
  - `WaitTime`: **189 ms**
* **Stock Settings Hot / Warm Resume:**
  - `TotalTime`: **51 ms**
  - `WaitTime`: **62 ms**
* **Launcher3 Resume Time (from App Exit):** **35 ms – 71 ms**

### 4.3 Rendering & Frame Pacing (`dumpsys gfxinfo com.android.launcher3`)
* **Total Frames Sampled:** 316 frames (during continuous workspace swipe interaction)
* **Janky Frames:** **0 (0.00%)**
* **50th Percentile Frame Time:** **6 ms** (target: < 16.66 ms)
* **90th Percentile Frame Time:** **7 ms**
* **95th Percentile Frame Time:** **8 ms**
* **99th Percentile Frame Time:** **10 ms**
* **Missed Vsync:** 0
* **Slow UI Thread:** 0
* **Slow Bitmap Uploads:** 0
* **Slow Draw Commands:** 0
* **High Input Latency Events:** 2 frames

### 4.4 Process Memory Footprint (PSS)
* **Launcher3 (`com.android.launcher3`):**
  - Native Heap: ~20.4 MB
  - Dalvik Heap: ~2.8 MB
  - Total PSS: **80.05 MB** (peaks at ~108 MB under full icon caching)
* **SystemUI (`com.android.systemui`):**
  - Native Heap: ~36.8 MB
  - Dalvik Heap: ~5.7 MB
  - Total PSS: **101.84 MB**

### 4.5 CPU Utilization
* **Idle System Load:** ~98% CPU Idle (784% idle out of 800% capacity on 8-core CPU)
* **Top Active Processes at Baseline:** `mtkfusionrild` (6.4%), `system_server` (~2-3%).

### 4.6 Known Existing Bugs / Baseline Quirks
1. MTK RIL background CPU spikes occasionally on GSI images if vendor RIL interface misreports SIM status.
2. Treble GSI default navbar gesture has wide back margins that can conflict with edge swipes unless tuned.
3. Stock Launcher3 on Android 10 uses fixed linear/cubic Bezier curves (`pathInterpolator`) with hardcoded durations rather than true damped harmonic spring models.

---

## 5. Audit Conclusion & Compliance Status
The test device and ROM are fully audited, functional, and backed up in `/backups/stock/`. Baseline metrics are established as the benchmark for all future phases.
