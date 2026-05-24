import os
import subprocess
import sys

OUTPUT_NAME = "WinOperation"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
ENTRY_POINT = os.path.join(BASE_DIR, "src", "main.py")

# (source_dir_relative, dest_dir) — mapped into the PyInstaller bundle
DATA_DIRS = [
    ("templates", "templates"),
    ("static", "static"),
]


def main():
    print("=" * 60)
    print(f"  {OUTPUT_NAME} - Build Script")
    print("=" * 60)

    if not os.path.exists(ENTRY_POINT):
        print(f"\nError: Entry point not found: {ENTRY_POINT}")
        sys.exit(1)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--icon", os.path.join(BASE_DIR, "static", "logo.ico"),
        "--name", OUTPUT_NAME,
        "--distpath", DIST_DIR,
        "--paths", os.path.join(BASE_DIR, "src"),
    ]

    for src_rel, dst in DATA_DIRS:
        src_abs = os.path.join(BASE_DIR, src_rel)
        cmd.extend(["--add-data", f"{src_abs}{os.pathsep}{dst}"])

    # Modules that PyInstaller's static analysis may miss
    cmd.extend(["--hidden-import", "bcrypt"])

    # Ensure all submodules are bundled for Flask and its extensions
    for pkg in ("flask", "flask_sqlalchemy"):
        cmd.extend(["--collect-all", pkg])

    cmd.append(ENTRY_POINT)

    print(f"\nRunning PyInstaller...\n")
    print(" ".join(cmd))
    print()

    result = subprocess.run(cmd, cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"\nBuild failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    exe_path = os.path.join(DIST_DIR, f"{OUTPUT_NAME}.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\nBuild successful!")
        print(f"  Output: {exe_path}")
        print(f"  Size:   {size_mb:.1f} MB")
    else:
        print(f"\nBuild completed but EXE not found at {exe_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
