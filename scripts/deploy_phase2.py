import subprocess
import time
import sys

ADB = r"C:\Users\Ganesh Patidar\AppData\Local\Android\Sdk\platform-tools\adb.exe"

def run(cmd):
    res = subprocess.run([ADB] + cmd, capture_output=True, text=True, errors="replace")
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def main():
    print("1. Pushing Launcher3QuickStep_phase2.apk to device...")
    apk_path = r"c:\mad\builds\Launcher3QuickStep_phase2.apk"
    out, err, code = run(["push", apk_path, "/system/product/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk"])
    print("Push output:", out)
    if code != 0:
        print("Push error:", err)
        sys.exit(1)

    print("2. Setting permissions 644...")
    run(["shell", "chmod", "644", "/system/product/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk"])

    print("3. Restarting Launcher3...")
    run(["shell", "killall", "-9", "com.android.launcher3"])
    time.sleep(2)

    print("4. Starting Launcher activity...")
    out, err, code = run(["shell", "am", "start", "-n", "com.android.launcher3/.Launcher"])
    print("Activity start:", out)
    time.sleep(2)

    print("5. Checking logcat for fatal exceptions...")
    out, err, code = run(["shell", "logcat", "-d", "-s", "AndroidRuntime:E", "FATAL:E"])
    print("Fatal errors:\n", out if out else "None (Clean boot!)")

    print("6. Verifying resumed launcher activity...")
    out, err, code = run(["shell", "dumpsys", "activity", "activities"])
    resumed = [l for l in out.splitlines() if "mResumedActivity" in l]
    for r in resumed:
        print(" ", r.strip())

if __name__ == "__main__":
    main()
