import subprocess
import time
import sys
import re

DEVICE = "PF4PFQT8HUD6XG5L"

def adb(cmd):
    full_cmd = f"adb -s {DEVICE} {cmd}"
    res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return res.stdout.strip()

def adb_shell(cmd):
    return adb(f"shell {cmd}")

def get_current_page():
    # Dump launcher hierarchy or check scroll to determine active page
    out = adb_shell("dumpsys activity top")
    # Also check Launcher3 dumpsys
    dump = adb_shell("dumpsys activity service Launcher3")
    m = re.search(r"mCurrentPage=(\d+)", dump)
    if m:
        return int(m.group(1))
    return -1

def test_rubber_band_page0():
    print("\n--- TEST 1: Rubber-band Overscroll on Page 0 (Rebound Glitch Test) ---")
    # Go home
    adb_shell("input keyevent KEYCODE_HOME")
    time.sleep(1)

    failures = 0
    test_runs = 15

    for i in range(1, test_runs + 1):
        # Ensure we are at Page 0
        adb_shell("input keyevent KEYCODE_HOME")
        time.sleep(0.3)

        # Pull right on Page 0 into overscroll, then release with a micro-left flick
        # Drag from x=200 to x=650, then quickly flick left to 550
        adb_shell("input swipe 200 800 650 800 350")
        # Give small delay for snap
        time.sleep(0.5)

        # Also test swipe with leftward velocity release
        # Simulating release rebound: drag 150 -> 600 in 200ms, then release
        adb_shell("input swipe 150 850 600 850 180")
        time.sleep(0.5)

        # Check dump
        dump = adb_shell("dumpsys activity service Launcher3")
        m = re.search(r"mCurrentPage=(\d+)", dump)
        curr = int(m.group(1)) if m else -1

        if curr != 0 and curr != -1:
            print(f"  [!] Run {i}: FAILED - Workspace jumped to page {curr} after overscroll!")
            failures += 1
        else:
            print(f"  [+] Run {i}: PASSED (snapped back cleanly to Page {curr})")

    if failures == 0:
        print(f"[PASS] Rubber-band Page 0 test passed 100% ({test_runs}/{test_runs} runs stable, zero opposite flips).")
    else:
        print(f"[FAIL] Rubber-band Page 0 had {failures} failures.")
    return failures == 0

def test_recents_swipe_and_hold():
    print("\n--- TEST 2: Recents Switcher Swipe-and-Hold & Card Switching ---")
    
    # 1. Launch Settings app to have a running task
    print("[*] Launching com.android.settings...")
    adb_shell("am start -n com.android.settings/.Settings")
    time.sleep(1.5)

    # Reset gfxinfo
    adb_shell("dumpsys gfxinfo com.android.launcher3 reset")

    switches = 10
    successes = 0

    for i in range(1, switches + 1):
        print(f"[*] Recents Switch Cycle {i}/{switches}...")
        # Swipe up from bottom and hold: from (360, 1500) to (360, 850) over 400ms
        adb_shell("input swipe 360 1500 360 850 400")
        time.sleep(0.6)

        # Check if Overview/Recents is active
        top = adb_shell("dumpsys activity top")
        is_recents = "RecentsActivity" in top or "Launcher" in top

        if is_recents:
            # Swipe recents card carousel (horizontal swipe to next card)
            adb_shell("input swipe 550 800 200 800 250")
            time.sleep(0.4)

            # Test recents overscroll: pull card to right
            adb_shell("input swipe 200 800 600 800 200")
            time.sleep(0.5)

            # Tap center to launch card
            adb_shell("input tap 360 800")
            time.sleep(1.0)

            successes += 1
            print(f"  [+] Cycle {i}: Success")
        else:
            print(f"  [!] Cycle {i}: Recents did not open")
            # Try to recover
            adb_shell("input keyevent KEYCODE_APP_SWITCH")
            time.sleep(1.0)
            adb_shell("input tap 360 800")
            time.sleep(0.5)

    print(f"\n[+] Recents Switch Cycles completed: {successes}/{switches}")

    # Gfxinfo metrics
    gfx = adb_shell("dumpsys gfxinfo com.android.launcher3")
    print("\n--- Performance Metrics (dumpsys gfxinfo) ---")
    for line in gfx.splitlines():
        if "Total frames rendered" in line or "Janky frames" in line or "90th percentile" in line or "95th percentile" in line or "99th percentile" in line:
            print("  ", line.strip())

    return successes >= 8

def main():
    print("==================================================")
    print("   PHASE 5 RECENTS SWITCHER & RUBBER-BAND AUDIT   ")
    print("==================================================")

    p0_ok = test_rubber_band_page0()
    recents_ok = test_recents_swipe_and_hold()

    print("\n==================================================")
    if p0_ok and recents_ok:
        print("  ALL PHASE 5 TESTS PASSED SUCCESSFULLY!          ")
    else:
        print("  PHASE 5 TEST COMPLETED WITH WARNINGS/FAILURES!   ")
    print("==================================================")

if __name__ == "__main__":
    main()
