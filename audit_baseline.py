import subprocess
import json
import re
import time

ADB = r"C:\Users\Ganesh Patidar\AppData\Local\Android\Sdk\platform-tools\adb.exe"

def run_adb(cmd):
    full_cmd = [ADB, "shell"] + cmd
    res = subprocess.run(full_cmd, capture_output=True, text=True, errors="replace")
    return res.stdout.strip()

def collect_metrics():
    print("Collecting device information...")
    metrics = {}
    
    # 1. Device identity
    metrics["model"] = run_adb(["getprop", "ro.product.model"])
    metrics["manufacturer"] = run_adb(["getprop", "ro.product.manufacturer"])
    metrics["device"] = run_adb(["getprop", "ro.product.device"])
    metrics["board"] = run_adb(["getprop", "ro.board.platform"])
    metrics["hardware"] = run_adb(["getprop", "ro.hardware"])
    metrics["build_flavor"] = run_adb(["getprop", "ro.build.flavor"])
    metrics["build_id"] = run_adb(["getprop", "ro.build.display.id"])
    metrics["android_version"] = run_adb(["getprop", "ro.build.version.release"])
    metrics["security_patch"] = run_adb(["getprop", "ro.build.version.security_patch"])
    metrics["fingerprint"] = run_adb(["getprop", "ro.build.fingerprint"])

    # 2. Display
    metrics["wm_size"] = run_adb(["wm", "size"])
    metrics["wm_density"] = run_adb(["wm", "density"])
    
    # 3. Memory & Storage
    metrics["meminfo_raw"] = run_adb(["cat", "/proc/meminfo"]).splitlines()[:5]
    metrics["storage"] = run_adb(["df", "-h", "/system", "/data"])

    # 4. GPU & SurfaceFlinger
    metrics["gpu_info"] = run_adb(["dumpsys", "SurfaceFlinger"]).splitlines()
    gpu_lines = [l for l in metrics["gpu_info"] if any(k in l for k in ["GLES", "OpenGL", "Mali", "Adreno"])]
    metrics["gpu_vendor_renderer"] = gpu_lines

    # 5. Animation scales
    metrics["window_animation_scale"] = run_adb(["settings", "get", "global", "window_animation_scale"])
    metrics["transition_animation_scale"] = run_adb(["settings", "get", "global", "transition_animation_scale"])
    metrics["animator_duration_scale"] = run_adb(["settings", "get", "global", "animator_duration_scale"])

    # 6. Current Launcher & SystemUI
    metrics["launcher_pkg"] = run_adb(["pm", "path", "com.android.launcher3"])
    metrics["systemui_pkg"] = run_adb(["pm", "path", "com.android.systemui"])
    metrics["launcher_version"] = run_adb(["dumpsys", "package", "com.android.launcher3"]).splitlines()
    metrics["launcher_version_filtered"] = [l for l in metrics["launcher_version"] if any(k in l for k in ["versionName", "versionCode", "targetSdk"])]

    # 7. Boot time & Uptime
    metrics["uptime"] = run_adb(["uptime"])
    metrics["proc_uptime"] = run_adb(["cat", "/proc/uptime"])

    # 8. App Launch Benchmark (Stock Settings app)
    print("Benchmarking Settings app cold/warm launch...")
    run_adb(["am", "force-stop", "com.android.settings"])
    time.sleep(1)
    # Cold launch
    cold_launch = run_adb(["am", "start", "-W", "-n", "com.android.settings/.Settings"])
    time.sleep(1)
    # Return to home
    run_adb(["input", "keyevent", "KEYCODE_HOME"])
    time.sleep(1)
    # Warm launch
    warm_launch = run_adb(["am", "start", "-W", "-n", "com.android.settings/.Settings"])
    time.sleep(1)
    run_adb(["input", "keyevent", "KEYCODE_HOME"])

    metrics["app_launch_cold"] = cold_launch
    metrics["app_launch_warm"] = warm_launch

    # 9. GFXInfo Jank & Frame Stats for Launcher3
    print("Benchmarking Launcher3 frame pacing...")
    run_adb(["dumpsys", "gfxinfo", "com.android.launcher3", "reset"])
    # Simulate swipe gestures on launcher
    for _ in range(5):
        run_adb(["input", "swipe", "600", "800", "100", "800", "150"])
        time.sleep(0.3)
        run_adb(["input", "swipe", "100", "800", "600", "800", "150"])
        time.sleep(0.3)
    gfxinfo_launcher = run_adb(["dumpsys", "gfxinfo", "com.android.launcher3"])
    metrics["gfxinfo_launcher"] = gfxinfo_launcher

    # 10. Process Memory (PSS / RSS)
    metrics["meminfo_launcher"] = run_adb(["dumpsys", "meminfo", "com.android.launcher3", "-d"])
    metrics["meminfo_systemui"] = run_adb(["dumpsys", "meminfo", "com.android.systemui", "-d"])

    # 11. CPU usage
    metrics["top_cpu"] = run_adb(["top", "-n", "1", "-b", "-m", "10"])

    return metrics

if __name__ == "__main__":
    data = collect_metrics()
    with open("baseline_raw_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Baseline raw data successfully collected and saved to baseline_raw_data.json")
