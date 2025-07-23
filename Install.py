import os
import sys
import subprocess
import shutil
import platform

GITHUB_REPO = "https://github.com/XTCooper11/Gemma3-Local-AI-App.git"
LOCAL_FOLDER = "Gemma3-Local-AI-App"
APP_FOLDER = os.path.join(LOCAL_FOLDER, "App")

def run(cmd):
    print(f"\n> {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f" Command failed: {cmd}")
        sys.exit(1)

def install_ollama():
    print(" Installing Ollama...")
    if shutil.which("ollama"):
        print(" Ollama already installed.")
        return

    url = "https://ollama.com/download/OllamaSetup.exe"
    installer = "OllamaSetup.exe"
    run(f"curl -L {url} -o {installer}")
    run(installer)

def pull_model():
    print("Pulling gemma3 model...")
    run("ollama pull gemma3")

def clone_repo():
    print("Cloning GitHub repo...")
    if os.path.exists(LOCAL_FOLDER):
        print(f"Folder '{LOCAL_FOLDER}' already exists. Skipping clone.")
        return
    run(f"git clone {GITHUB_REPO}")

def create_windows_shortcut():
    try:
        import pythoncom
        from win32com.shell import shell, shellcon
    except ImportError:
        print(" pywin32 is required for shortcut creation. Installing now...")
        run(f"{sys.executable} -m pip install pywin32")
        import pythoncom
        from win32com.shell import shell, shellcon

    desktop = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)
    shortcut_path = os.path.join(desktop, "Gemma3 Local AI App.lnk")

    python_exe = sys.executable
    target_py = os.path.abspath(os.path.join(APP_FOLDER, "main.py"))

    shell_link = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink, None,
        pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)

    shell_link.SetPath(python_exe)
    shell_link.SetArguments(f'"{target_py}"')
    shell_link.SetDescription("Launch Gemma3 Local AI App")

    icon_path = os.path.abspath(os.path.join(APP_FOLDER, "G3.ico"))
    if os.path.exists(icon_path):
        shell_link.SetIconLocation(icon_path, 0)
    else:
        print(" G3.ico icon not found; shortcut will use default icon.")

    persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
    persist_file.Save(shortcut_path, 0)

    print(f" Desktop shortcut created at: {shortcut_path}")

def run_app():
    main_py = os.path.join(APP_FOLDER, "main.py")
    if os.path.exists(main_py):
        run(f'"{sys.executable}" "{main_py}"')
    else:
        print(" main.py not found in App/.")

def main():
    if platform.system() != "Windows":
        print(" This installer is Windows-only.")
        sys.exit(1)

    install_ollama()
    pull_model()
    clone_repo()
    create_windows_shortcut()
    run_app()

if __name__ == "__main__":
    main()
