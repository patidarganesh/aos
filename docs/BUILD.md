# Build and Deployment Guide

## 1. Prerequisites & Environment

* **Target Device:** Realme 3 (`phhgsi_arm64_ab` / `mt6771`)
* **Host Platform:** Windows 10/11 with PowerShell & Python 3.10+
* **Android SDK:**
  - Build Tools: 37.0.0 (`C:\Users\Ganesh Patidar\AppData\Local\Android\Sdk\build-tools\37.0.0`)
  - Platform Jar: Android 34 (`android.jar`)
  - Platform Tools: `adb.exe`
* **Java:** JDK 8/11/17 (`javac.exe`)
* **Device Access:** Rooted via Magisk / `su` over ADB.

---

## 2. Motion Engine Compilation

To compile and verify the core motion engine:
```powershell
$jar = "C:\Users\Ganesh Patidar\AppData\Local\Android\Sdk\platforms\android-34\android.jar"
$src = Get-ChildItem -Path "c:\mad\engine\src\com\ios\motion\*.java" | Select-Object -ExpandProperty FullName

# 1. Compile Java Bytecode
javac -source 8 -target 8 -Xlint:-options -bootclasspath $jar -d c:\mad\engine\bin $src

# 2. Run Mathematics & Verification Suite
java -ea -cp c:\mad\engine\bin com.ios.motion.TestMotionEngine
```

---

## 3. Modular System Component Packaging

Each modified system component (Launcher3, SystemUI, or System Overlay) is processed through the modular build pipeline:

1. **AAPT Resource Compilation:**
   ```powershell
   & $aapt package -f -M AndroidManifest.xml -S res -I $jar -F unaligned.apk
   ```
2. **Java Compilation:**
   ```powershell
   & javac -source 8 -target 8 -Xlint:-options -bootclasspath $jar -d bin $srcFiles
   ```
3. **D8 Dexing:**
   ```powershell
   & $d8 --lib $jar --output bin/classes.dex bin/**/*.class
   ```
4. **Zipalign & Signing:**
   ```powershell
   & $zipalign -f -p 4 bin/unaligned.apk bin/aligned.apk
   & $apksigner sign --ks debug.keystore --ks-pass pass:android bin/aligned.apk
   ```

---

## 4. Device Deployment & Hot-Reload

To deploy components to the rooted device:

```powershell
# Remount system partition as writable
adb root
adb remount

# For Launcher3 Quickstep:
adb push bin/aligned.apk /system/product/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk
adb shell chmod 644 /system/product/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk
adb shell killall com.android.launcher3

# For SystemUI:
adb push bin/aligned_sysui.apk /system/product/priv-app/SystemUI/SystemUI.apk
adb shell chmod 644 /system/product/priv-app/SystemUI/SystemUI.apk
adb shell killall com.android.systemui
```
