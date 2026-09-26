import subprocess
import time
import json

ADB = r"C:\Users\Ganesh Patidar\AppData\Local\Android\Sdk\platform-tools\adb.exe"

def run_adb(cmd):
    res = subprocess.run([ADB, "shell"] + cmd, capture_output=True, text=True, errors="replace")
    return res.stdout.strip()

def run_test():
    print("1. Resetting gfxinfo for com.android.launcher3...")
    run_adb(["dumpsys", "gfxinfo", "com.android.launcher3", "reset"])
    time.sleep(1)

    print("2. Performing 30 horizontal workspace page swipes and overscrolls...")
    for i in range(15):
        # Fling left
        run_adb(["input", "swipe", "620", "800", "100", "800", "120"])
        time.sleep(0.35)
        # Fling right
        run_adb(["input", "swipe", "100", "800", "620", "800", "120"])
        time.sleep(0.35)

    # Overscroll pull past boundary
    for i in range(5):
        run_adb(["input", "swipe", "200", "800", "650", "800", "200"])
        time.sleep(0.3)

    print("3. Collecting gfxinfo performance data...")
    gfxinfo = run_adb(["dumpsys", "gfxinfo", "com.android.launcher3"])
    
    print("4. Checking active activity state...")
    activities = run_adb(["dumpsys", "activity", "activities"])
    resumed = [l.strip() for l in activities.splitlines() if "mResumedActivity" in l]

    lines = gfxinfo.splitlines()
    summary = []
    for l in lines:
        if any(k in l for k in ["Total frames", "Janky frames", "50th percentile", "90th percentile", "95th percentile", "99th percentile", "Number Missed Vsync", "Number Slow UI thread"]):
            summary.append(l.strip())

    result = {
        "resumed_activity": resumed,
        "gfxinfo_summary": summary,
        "passed": any("com.android.launcher3" in r for r in resumed)
    }

    with open("phase2_stress_result.json", "w") as f:
        json.dump(result, f, indent=2)

    print("\n=== PHASE 2 STRESS TEST RESULTS ===")
    for s in summary:
        print(" ", s)
    for r in resumed:
        print("  Resumed:", r)
    print("  Status: " + ("PASS" if result["passed"] else "FAIL"))

if __name__ == "__main__":
    run_test()
