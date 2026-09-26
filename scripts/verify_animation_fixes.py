import subprocess
import time
import os
import sys
import glob
from PIL import Image

ADB = r"C:\Users\Ganesh Patidar\AppData\Local\Android\Sdk\platform-tools\adb.exe"

def adb(args):
    cmd = [ADB] + args
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def main():
    print("[*] Waiting for ADB device PF4PFQT8HUD6XG5L to be online...")
    device_ready = False
    for attempt in range(15):
        out, _, _ = adb(["devices"])
        if "PF4PFQT8HUD6XG5L\tdevice" in out:
            print(f"[+] Device online and ready on attempt {attempt+1}")
            device_ready = True
            break
        time.sleep(1)

    if not device_ready:
        print("[!] Device not ready after 15 seconds! Output:\n" + out)
        return 1

    print("[*] Waking screen and going to HOME...")
    adb(["shell", "input", "keyevent", "KEYCODE_WAKEUP"])
    adb(["shell", "input", "keyevent", "KEYCODE_HOME"])
    time.sleep(1)

    print("[*] Force-stopping target apps to test true cold start...")
    adb(["shell", "am", "force-stop", "com.android.settings"])
    adb(["shell", "am", "force-stop", "org.lineageos.jelly"])
    time.sleep(1)

    # Reset gfxinfo
    adb(["shell", "dumpsys", "gfxinfo", "com.android.launcher3", "reset"])

    print("[*] Starting screen recording on device for 6 seconds...")
    rec_proc = subprocess.Popen([ADB, "shell", "screenrecord", "--time-limit", "6", "/sdcard/anim_fix_test.mp4"])
    time.sleep(1.0) # wait for recorder to initialize

    print("[*] Action 1: Cold launch Settings...")
    adb(["shell", "am", "start", "-a", "android.settings.SETTINGS"])
    time.sleep(1.5)

    print("[*] Action 2: Swipe up to Home...")
    adb(["shell", "input", "swipe", "360", "1500", "360", "750", "160"])
    time.sleep(1.5)

    print("[*] Waiting for recording to finalize...")
    rec_proc.wait(timeout=10)
    time.sleep(1.0)

    print("[*] Pulling recording...")
    root = r"c:\mad"
    video_path = os.path.join(root, "anim_fix_test.mp4")
    if os.path.exists(video_path):
        os.remove(video_path)
    adb(["pull", "/sdcard/anim_fix_test.mp4", video_path])

    if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
        print("[!] Video file failed to pull or is empty!")
        return 1

    print(f"[+] Recording saved: {video_path} ({os.path.getsize(video_path)} bytes)")

    # Extract frames
    frames_dir = os.path.join(root, "frames_fixed")
    os.makedirs(frames_dir, exist_ok=True)
    for f in glob.glob(os.path.join(frames_dir, "*.png")):
        os.remove(f)

    print("[*] Extracting frames with ffmpeg...")
    subprocess.run(f'ffmpeg -y -i "{video_path}" -vf "fps=60" "{frames_dir}/f_%04d.png"', shell=True, capture_output=True)

    frame_files = sorted(glob.glob(os.path.join(frames_dir, "f_*.png")))
    print(f"[+] Extracted {len(frame_files)} frames.")

    if not frame_files:
        print("[!] No frames extracted!")
        return 1

    # Analyze frames for:
    # 1. Pitch black void (mean brightness < 5)
    # 2. White flash (mean brightness > 240)
    print("\n[*] Analyzing frame luminance and detecting glitches...")
    black_void_frames = []
    white_flash_frames = []

    stats = []
    for i, fpath in enumerate(frame_files):
        img = Image.open(fpath).convert("L") # Grayscale
        # resize for fast analysis
        small = img.resize((72, 152))
        pixels = list(small.getdata())
        avg_lum = sum(pixels) / len(pixels)
        min_lum = min(pixels)
        max_lum = max(pixels)
        stats.append((i+1, avg_lum, min_lum, max_lum))

        if avg_lum < 5.0 and max_lum < 15:
            black_void_frames.append(i+1)
        if avg_lum > 235.0:
            white_flash_frames.append(i+1)

    print("\n=== FRAME-BY-FRAME GLITCH AUDIT RESULTS ===")
    print(f"Total Frames Analyzed: {len(frame_files)}")
    print(f"Black Void Frames Detected: {len(black_void_frames)} {black_void_frames}")
    print(f"White Flash Frames Detected: {len(white_flash_frames)} {white_flash_frames}")

    # Inspect the launch transition window (frames 40-90)
    print("\nLaunch Transition Window Luminance (Frames 45 to 80):")
    for fnum, avg, mi, ma in stats[44:80]:
        bar = "#" * int(avg / 4)
        print(f"  Frame {fnum:03d}: avg={avg:5.1f} (min={mi:3d}, max={ma:3d}) | {bar}")

    # Dumpsys gfxinfo
    out, _, _ = adb(["shell", "dumpsys", "gfxinfo", "com.android.launcher3"])
    print("\n=== LAUNCHER GFXINFO PROFILE ===")
    for line in out.splitlines():
        if any(k in line for k in ["Total frames rendered", "Janky frames", "50th percentile", "90th percentile", "95th percentile", "99th percentile"]):
            print(f"  {line.strip()}")

    if not black_void_frames and not white_flash_frames:
        print("\n[VERIFICATION PASSED] 0 Black Voids. 0 White Flashes. Full Continuous Animation!")
        return 0
    else:
        print("\n[!] Residual frame artifacts detected.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
