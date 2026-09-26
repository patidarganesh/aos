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

def main():
    print("=== TESTING PHASE 3: APP LAUNCH SPRING TRANSITIONS ===")
    
    # Return to home first
    run(["shell", "input", "keyevent", "KEYCODE_HOME"])
    time.sleep(1.5)
    
    # Test targets: Gallery (360, 1351), Messaging (227, 1351), Aurora Store (360, 403)
    targets = [
        ("Gallery", 360, 1351),
        ("Messaging", 227, 1351),
        ("Aurora Store", 360, 403),
        ("Gallery", 360, 1351),
        ("Messaging", 227, 1351),
        ("Aurora Store", 360, 403),
        ("Gallery", 360, 1351),
        ("Messaging", 227, 1351),
        ("Gallery", 360, 1351),
        ("Messaging", 227, 1351),
    ]
    
    trials = []
    
    for i, (name, x, y) in enumerate(targets, 1):
        # Reset gfxinfo
        run(["shell", "dumpsys", "gfxinfo", "com.android.launcher3", "reset"])
        time.sleep(0.2)
        
        # Tap the app icon to trigger the launch transition
        print(f"Trial {i:2d}/10: Launching {name} from ({x}, {y})...")
        run(["shell", "input", "tap", str(x), str(y)])
        
        # Wait for spring transition to complete (500ms + buffer)
        time.sleep(1.2)
        
        # Collect gfxinfo for the launch animation
        out, _, _ = run(["shell", "dumpsys", "gfxinfo", "com.android.launcher3"])
        stats = parse_gfxinfo(out)
        stats["target"] = name
        stats["trial"] = i
        trials.append(stats)
        print(f"  Result: frames={stats.get('total_frames', 0)}, jank={stats.get('jank_pct', 0.0)}%, P50={stats.get('p50', 0)}ms, P90={stats.get('p90', 0)}ms, P95={stats.get('p95', 0)}ms")
        
        # Return home for next trial
        run(["shell", "input", "keyevent", "KEYCODE_HOME"])
        time.sleep(1.0)
        
    # Aggregate statistics
    total_frames = sum(t.get("total_frames", 0) for t in trials)
    total_jank = sum(t.get("jank_count", 0) for t in trials)
    jank_pct = (total_jank / total_frames * 100.0) if total_frames > 0 else 0.0
    p50_mean = sum(t.get("p50", 0) for t in trials) / len(trials)
    p90_mean = sum(t.get("p90", 0) for t in trials) / len(trials)
    p95_mean = sum(t.get("p95", 0) for t in trials) / len(trials)
    p99_mean = sum(t.get("p99", 0) for t in trials) / len(trials)
    
    print("\n=== PHASE 3 APP LAUNCH 10-TRIAL AGGREGATE ===")
    print(f"Total Frames Rendered: {total_frames}")
    print(f"Total Janky Frames:    {total_jank} ({jank_pct:.2f}%) [Target: < 1.0%]")
    print(f"P50 Mean Frame Time:   {p50_mean:.2f} ms [Target: < 8.0 ms]")
    print(f"P90 Mean Frame Time:   {p90_mean:.2f} ms [Target: < 12.0 ms]")
    print(f"P95 Mean Frame Time:   {p95_mean:.2f} ms [Target: < 14.0 ms]")
    print(f"P99 Mean Frame Time:   {p99_mean:.2f} ms [Target: < 16.67 ms]")
    
    # Save full trial data
    with open("c:/mad/phase3_launch_test_data.json", "w") as f:
        json.dump({"trials": trials, "aggregate": {
            "total_frames": total_frames,
            "total_jank": total_jank,
            "jank_pct": jank_pct,
            "p50_mean": p50_mean,
            "p90_mean": p90_mean,
            "p95_mean": p95_mean,
            "p99_mean": p99_mean
        }}, f, indent=2)
    print("Saved results to c:/mad/phase3_launch_test_data.json")

if __name__ == "__main__":
    main()
