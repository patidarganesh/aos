import subprocess
import time
import re
import json

ADB = r"C:\Users\Ganesh Patidar\AppData\Local\Android\Sdk\platform-tools\adb.exe"

def run(cmd):
    res = subprocess.run([ADB] + cmd, capture_output=True, text=True, errors="replace")
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def parse_gfxinfo(output):
    stats = {}
    m = re.search(r"Total frames rendered:\s+(\d+)", output)
    if m: stats["total_frames"] = int(m.group(1))
    m = re.search(r"Janky frames:\s+(\d+)\s+\(([\d\.]+)%\)", output)
    if m:
        stats["jank_count"] = int(m.group(1))
        stats["jank_pct"] = float(m.group(2))
    m = re.search(r"50th percentile:\s+(\d+)ms", output)
    if m: stats["p50"] = int(m.group(1))
    m = re.search(r"90th percentile:\s+(\d+)ms", output)
    if m: stats["p90"] = int(m.group(1))
    m = re.search(r"95th percentile:\s+(\d+)ms", output)
    if m: stats["p95"] = int(m.group(1))
    m = re.search(r"99th percentile:\s+(\d+)ms", output)
    if m: stats["p99"] = int(m.group(1))
    m = re.search(r"Number Missed Vsync:\s+(\d+)", output)
    if m: stats["missed_vsync"] = int(m.group(1))
    m = re.search(r"Number Slow UI thread:\s+(\d+)", output)
    if m: stats["slow_ui"] = int(m.group(1))
    return stats

def compute_aggregate(trials):
    valid_trials = [t for t in trials if t.get("total_frames", 0) > 0]
    total_frames = sum(t.get("total_frames", 0) for t in valid_trials)
    total_jank = sum(t.get("jank_count", 0) for t in valid_trials)
    jank_pct = (total_jank / total_frames * 100.0) if total_frames > 0 else 0.0
    p50_mean = sum(t.get("p50", 0) for t in valid_trials) / len(valid_trials) if valid_trials else 0
    p90_mean = sum(t.get("p90", 0) for t in valid_trials) / len(valid_trials) if valid_trials else 0
    p95_mean = sum(t.get("p95", 0) for t in valid_trials) / len(valid_trials) if valid_trials else 0
    p99_mean = sum(t.get("p99", 0) for t in valid_trials) / len(valid_trials) if valid_trials else 0
    return {
        "trials_count": len(valid_trials),
        "total_frames": total_frames,
        "total_jank": total_jank,
        "jank_pct": round(jank_pct, 2),
        "p50_mean": round(p50_mean, 2),
        "p90_mean": round(p90_mean, 2),
        "p95_mean": round(p95_mean, 2),
        "p99_mean": round(p99_mean, 2),
    }

def main():
    print("=== TESTING PHASE 4: APP EXIT & SWIPE-TO-HOME TRANSITIONS ===")

    # Ensure device is on home
    run(["shell", "input", "keyevent", "KEYCODE_HOME"])
    time.sleep(1.0)

    # 1. Warmup run
    print("[*] Performing warmup transition...")
    run(["shell", "input", "tap", "360", "1351"])
    time.sleep(1.2)
    run(["shell", "input", "keyevent", "KEYCODE_HOME"])
    time.sleep(0.8)

    apps = [
        ("Gallery", 360, 1351),
        ("Messaging", 227, 1351),
        ("Gallery", 360, 1351),
        ("Messaging", 227, 1351),
        ("Gallery", 360, 1351),
        ("Messaging", 227, 1351),
        ("Gallery", 360, 1351),
        ("Messaging", 227, 1351),
        ("Gallery", 360, 1351),
        ("Messaging", 227, 1351),
    ]

    # --- PART A: PROGRAMMATIC APP EXIT (QuickstepAppTransitionManagerImpl) ---
    print("\n--- Part A: Programmatic App Exit (10 Trials) ---")
    programmatic_trials = []
    for i, (name, x, y) in enumerate(apps, 1):
        run(["shell", "input", "tap", str(x), str(y)])
        time.sleep(1.2)
        run(["shell", "dumpsys", "gfxinfo", "com.android.launcher3", "reset"])
        time.sleep(0.05)
        run(["shell", "input", "keyevent", "KEYCODE_HOME"])
        time.sleep(0.8)
        out, _, _ = run(["shell", "dumpsys", "gfxinfo", "com.android.launcher3"])
        stats = parse_gfxinfo(out)
        stats["target"] = name
        stats["mode"] = "programmatic"
        stats["trial"] = i
        programmatic_trials.append(stats)
        print(f"  Trial {i:2d}/10: {name:9s} | frames={stats.get('total_frames', 0):2d} | jank={stats.get('jank_pct', 0.0):5.2f}% | P50={stats.get('p50', 0):2d}ms | P90={stats.get('p90', 0):2d}ms | P95={stats.get('p95', 0):2d}ms")

    prog_agg = compute_aggregate(programmatic_trials)
    print(f"Programmatic Exit: P50={prog_agg['p50_mean']}ms | P90={prog_agg['p90_mean']}ms | P95={prog_agg['p95_mean']}ms | Jank={prog_agg['jank_pct']}%")

    # --- PART B: GESTURE SWIPE-TO-HOME (WindowTransformSwipeHandler) ---
    print("\n--- Part B: Gesture Swipe-to-Home (10 Trials) ---")
    gesture_trials = []
    for i, (name, x, y) in enumerate(apps, 1):
        run(["shell", "input", "tap", str(x), str(y)])
        time.sleep(1.2)
        run(["shell", "dumpsys", "gfxinfo", "com.android.launcher3", "reset"])
        time.sleep(0.05)
        # Fluid upward swipe from bottom bar
        run(["shell", "input", "swipe", "360", "1510", "360", "950", "160"])
        time.sleep(0.8)
        out, _, _ = run(["shell", "dumpsys", "gfxinfo", "com.android.launcher3"])
        stats = parse_gfxinfo(out)
        stats["target"] = name
        stats["mode"] = "gesture"
        stats["trial"] = i
        gesture_trials.append(stats)
        print(f"  Trial {i:2d}/10: {name:9s} | frames={stats.get('total_frames', 0):2d} | jank={stats.get('jank_pct', 0.0):5.2f}% | P50={stats.get('p50', 0):2d}ms | P90={stats.get('p90', 0):2d}ms | P95={stats.get('p95', 0):2d}ms")
        run(["shell", "input", "keyevent", "KEYCODE_HOME"])
        time.sleep(0.5)

    gest_agg = compute_aggregate(gesture_trials)
    print(f"Gesture Swipe Exit: P50={gest_agg['p50_mean']}ms | P90={gest_agg['p90_mean']}ms | P95={gest_agg['p95_mean']}ms | Jank={gest_agg['jank_pct']}%")

    # Combined aggregate
    all_trials = programmatic_trials + gesture_trials
    overall_agg = compute_aggregate(all_trials)

    # Check for crashes in logcat
    crash_out, _, _ = run(["shell", "logcat", "-d", "-t", "100", "*:E"])
    crashes = [line for line in crash_out.splitlines() if "FATAL" in line or "AndroidRuntime" in line]
    overall_agg["crashes"] = len(crashes)

    print("\n" + "="*58)
    print("=== PHASE 4 APP EXIT 20-TRIAL BENCHMARK SUMMARY ===")
    print("="*58)
    print(f"Programmatic Exit (N=10): P50={prog_agg['p50_mean']:.2f}ms, P90={prog_agg['p90_mean']:.2f}ms, P95={prog_agg['p95_mean']:.2f}ms, Jank={prog_agg['jank_pct']:.2f}%")
    print(f"Gesture Swipe Exit (N=10): P50={gest_agg['p50_mean']:.2f}ms, P90={gest_agg['p90_mean']:.2f}ms, P95={gest_agg['p95_mean']:.2f}ms, Jank={gest_agg['jank_pct']:.2f}%")
    print(f"Overall Total Frames:     {overall_agg['total_frames']}")
    print(f"Overall Total Jank:       {overall_agg['total_jank']} ({overall_agg['jank_pct']:.2f}%)")
    print(f"Overall P50 Mean:         {overall_agg['p50_mean']:.2f} ms [Target: < 8.0 ms]")
    print(f"Overall P90 Mean:         {overall_agg['p90_mean']:.2f} ms [Target: < 12.0 ms]")
    print(f"Overall P95 Mean:         {overall_agg['p95_mean']:.2f} ms [Target: < 14.0 ms]")
    print(f"Fatal Exceptions Detected: {len(crashes)}")

    results = {
        "programmatic_trials": programmatic_trials,
        "gesture_trials": gesture_trials,
        "programmatic_aggregate": prog_agg,
        "gesture_aggregate": gest_agg,
        "overall_aggregate": overall_agg
    }
    with open("c:/mad/phase4_exit_test_data.json", "w") as f:
        json.dump(results, f, indent=2)
    print("[+] Test data written to c:/mad/phase4_exit_test_data.json")

    return 0

if __name__ == "__main__":
    main()
