# Crash Safety & Emergency Rollback Procedures

## 1. Golden Backups Directory
All original, untouched system components pulled prior to any modification are safely archived in:
`/backups/stock/`

* `Launcher3QuickStep_stock.apk` (Size: 9,216,627 bytes)
* `SystemUI_stock.apk` (Size: 20,831,562 bytes)
* `framework-res_stock.apk` (Size: 47,026,520 bytes)

---

## 2. Automated Single-Command Restore

If any component enters a boot loop, crash loop, or rendering stall:

Run the rollback script from PowerShell:
```powershell
$adb = "C:\Users\Ganesh Patidar\AppData\Local\Android\Sdk\platform-tools\adb.exe"

& $adb root
& $adb remount

# Restore stock Launcher3
& $adb push c:\mad\backups\stock\Launcher3QuickStep_stock.apk /system/product/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk
& $adb shell chmod 644 /system/product/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk

# Restore stock SystemUI
& $adb push c:\mad\backups\stock\SystemUI_stock.apk /system/product/priv-app/SystemUI/SystemUI.apk
& $adb shell chmod 644 /system/product/priv-app/SystemUI/SystemUI.apk

# Restart services
& $adb shell "killall -9 com.android.launcher3; killall -9 com.android.systemui"
```

---

## 3. Git Revision Rollback

Before every major modification, changes are committed to Git with descriptive tags:

To view known-good commits:
```bash
git log --oneline -n 10
```

To revert to the last known-good state:
```bash
git checkout <known_good_commit_hash>
```
And redeploy using the procedure in `/docs/BUILD.md`.

---

## 4. Crash Detection Watchdog

A logcat monitoring loop is provided to detect FATAL crashes automatically:
```powershell
$adb = "C:\Users\Ganesh Patidar\AppData\Local\Android\Sdk\platform-tools\adb.exe"
& $adb logcat -v time *:E | Select-String -Pattern "FATAL EXCEPTION", "AndroidRuntime"
```
If repeated crashes occur within 10 seconds of launch, the automatic rollback procedure above is invoked immediately.
