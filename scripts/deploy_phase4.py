import subprocess
import sys
import os
import time

def run(cmd, desc):
    print(f"[*] {desc}...")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] FAILED: {desc}")
        print("STDERR:\n", res.stderr)
        print("STDOUT:\n", res.stdout)
        sys.exit(1)
    print(f"[+] DONE: {desc}")
    if res.stdout.strip():
        print("    ", res.stdout.strip()[:200])
    return res

def main():
    root = r"c:\mad"
    build_dir = os.path.join(root, "builds")
    os.makedirs(build_dir, exist_ok=True)

    unaligned_apk = os.path.join(root, "Launcher3QuickStep_phase4.apk")
    aligned_apk = os.path.join(build_dir, "Launcher3QuickStep_phase4_aligned.apk")
    src_dir = os.path.join(root, "launcher3_src")
    apktool_jar = os.path.join(root, "apktool.jar")
    sdk_tools = r"C:\Users\Ganesh Patidar\AppData\Local\Android\Sdk\build-tools\37.0.0"
    zipalign = os.path.join(sdk_tools, "zipalign.exe")
    apksigner = os.path.join(sdk_tools, "apksigner.bat")
    pk8 = os.path.join(root, r"keys\platform.pk8")
    pem = os.path.join(root, r"keys\platform.x509.pem")

    # 1. Compile apktool
    run(f'java -jar "{apktool_jar}" b -f -o "{unaligned_apk}" "{src_dir}"', "Building APK with apktool")

    # 2. Zipalign
    run(f'"{zipalign}" -f -p 4 "{unaligned_apk}" "{aligned_apk}"', "Zipaligning APK")

    # 3. Sign
    run(f'"{apksigner}" sign --key "{pk8}" --cert "{pem}" "{aligned_apk}"', "Signing APK with platform key")

    # 4. Verify device connection
    res = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
    print(res.stdout)
    if "PF4PFQT8HUD6XG5L" not in res.stdout:
        print("[!] Target device PF4PFQT8HUD6XG5L not connected!")
        sys.exit(1)

    # 5. Push APK
    run(f'adb push "{aligned_apk}" /system/product/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk', "Pushing APK to system")
    run('adb shell chmod 644 /system/product/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk', "Setting permissions")

    # 6. Restart Launcher
    run('adb shell killall -9 com.android.launcher3', "Restarting Launcher3 process")
    time.sleep(2)

    # 7. Check if launcher is alive
    res = subprocess.run("adb shell pidof com.android.launcher3", shell=True, capture_output=True, text=True)
    pid = res.stdout.strip()
    if pid:
        print(f"[+] Launcher3 running with PID: {pid}")
    else:
        print("[!] Launcher3 process not found! Checking logcat for crash...")
        crash = subprocess.run('adb logcat -d -t 50 *:E', shell=True, capture_output=True, text=True)
        print(crash.stdout)
        sys.exit(1)

    print("\n[SUCCESS] Phase 4 APK deployed and verified on device!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
