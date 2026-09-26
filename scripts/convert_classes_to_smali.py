import subprocess
import os
import shutil
import zipfile

def convert():
    sdk_tools = r"C:\Users\Ganesh Patidar\AppData\Local\Android\Sdk\build-tools\37.0.0"
    jar = r"C:\Users\Ganesh Patidar\AppData\Local\Android\Sdk\platforms\android-34\android.jar"
    d8 = os.path.join(sdk_tools, "d8.bat")
    
    # 1. Compile engine Java files
    engine_bin = r"c:\mad\engine\bin"
    os.makedirs(engine_bin, exist_ok=True)
    
    src_dir = r"c:\mad\engine\src\com\ios\motion"
    src_files = [os.path.join(src_dir, f) for f in os.listdir(src_dir) if f.endswith('.java')]
    
    cmd = ["javac", "-source", "8", "-target", "8", "-Xlint:-options", "-bootclasspath", jar, "-d", engine_bin] + src_files
    print("Compiling engine sources...")
    subprocess.check_call(cmd)
    
    # 2. Dex with d8
    dex_dir = r"c:\mad\engine\dex"
    if os.path.exists(dex_dir):
        shutil.rmtree(dex_dir)
    os.makedirs(dex_dir)
    
    class_files = []
    for root, dirs, files in os.walk(engine_bin):
        for f in files:
            if f.endswith('.class') and not f.startswith('Test'):
                class_files.append(os.path.join(root, f))
                
    print(f"Dexing {len(class_files)} class files with D8...")
    d8_cmd = [d8, "--min-api", "26", "--output", dex_dir] + class_files
    subprocess.check_call(d8_cmd, shell=True)
    
    # 3. Create dummy zip/apk containing classes.dex
    dummy_apk = r"c:\mad\engine\dummy.apk"
    with zipfile.ZipFile(dummy_apk, "w") as z:
        z.write(os.path.join(dex_dir, "classes.dex"), "classes.dex")
        
    # 4. Decompile dummy.apk with apktool to get pure smali
    smali_out = r"c:\mad\engine\smali_out"
    if os.path.exists(smali_out):
        shutil.rmtree(smali_out)
        
    print("Decompiling classes.dex into smali via apktool...")
    apktool_cmd = ["java", "-jar", r"c:\mad\apktool.jar", "d", "-r", "-f", "-o", smali_out, dummy_apk]
    subprocess.check_call(apktool_cmd)
    
    print("Smali files generated successfully in:", smali_out)
    
    # 5. Copy generated smali files to launcher3_src/smali_classes3/com/ios/motion
    target_dest = r"c:\mad\launcher3_src\smali_classes3\com\ios\motion"
    if os.path.exists(target_dest):
        shutil.rmtree(target_dest)
        
    src_smali_dir = os.path.join(smali_out, "smali", "com", "ios", "motion")
    if os.path.exists(src_smali_dir):
        shutil.copytree(src_smali_dir, target_dest)
        print("Copied com.ios.motion smali classes to Launcher3:", target_dest)
        for f in os.listdir(target_dest):
            print("  -", f)

if __name__ == "__main__":
    convert()
