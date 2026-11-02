"""Ajusta o projeto Android gerado pelo Capacitor: código nativo, permissões, ícones e versão."""
import glob, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "android", "app")
MAIN = os.path.join(APP, "src", "main")
PKG = "br.julio.painelmotorhome"
build_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1

# 1) código Java (substitui a MainActivity gerada)
java_dir = os.path.join(MAIN, "java", *PKG.split("."))
os.makedirs(java_dir, exist_ok=True)
for f in glob.glob(os.path.join(MAIN, "java", "**", "MainActivity.java"), recursive=True):
    os.remove(f)
for f in glob.glob(os.path.join(ROOT, "native", "java", "*.java")):
    shutil.copy(f, java_dir)

# 2) recursos: remove o splash padrão (png) e copia ícones/cores/splash próprios
for f in glob.glob(os.path.join(MAIN, "res", "drawable*", "splash.png")):
    os.remove(f)
for src in glob.glob(os.path.join(ROOT, "native", "res", "**", "*"), recursive=True):
    if os.path.isfile(src):
        dst = os.path.join(MAIN, "res", os.path.relpath(src, os.path.join(ROOT, "native", "res")))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)

# 3) manifesto: permissões e serviço em primeiro plano
mf = os.path.join(MAIN, "AndroidManifest.xml")
m = open(mf, encoding="utf-8").read()
perms = ["FOREGROUND_SERVICE", "FOREGROUND_SERVICE_CONNECTED_DEVICE", "WAKE_LOCK", "POST_NOTIFICATIONS",
         "REQUEST_IGNORE_BATTERY_OPTIMIZATIONS", "VIBRATE", "BLUETOOTH_SCAN", "BLUETOOTH_CONNECT",
         "ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION"]
add = "".join(f'    <uses-permission android:name="android.permission.{p}" />\n' for p in perms if f"permission.{p}\"" not in m)
m = m.replace("</manifest>", add + "</manifest>")
if "MonitorService" not in m:
    m = m.replace("</application>", '        <service android:name=".MonitorService" android:exported="false" android:foregroundServiceType="connectedDevice" />\n    </application>')
open(mf, "w", encoding="utf-8").write(m)

# 4) versão do app = número do build
bg = os.path.join(APP, "build.gradle")
g = open(bg, encoding="utf-8").read()
g = re.sub(r"versionCode \d+", f"versionCode {build_no}", g)
g = re.sub(r'versionName "[^"]*"', f'versionName "1.{build_no}"', g)
open(bg, "w", encoding="utf-8").write(g)
print(f"Projeto Android ajustado (build {build_no}).")
