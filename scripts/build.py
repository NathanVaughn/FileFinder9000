import os
import shutil
import subprocess
import sys
import platform

name = "FileFinder9000"

if platform.system() == "Linux":
    # sudo apt-get install python3-tk
    # for linux to run
    icon_ext = "xbm"
elif platform.system() == "Darwin":
    icon_ext = "icns"
else:
    icon_ext = "ico"

subprocess.run(
    [
        "pyinstaller",
        f"--name={name}",
        # "--onefile",
        "--noconsole",
        f"--icon=images/icon.{icon_ext}",
        f"--add-data=images/{os.pathsep}images/",
        "--noconfirm",
        "main.py",
    ]
)

shutil.make_archive(
    os.path.join("dist", f"{name}-{sys.platform}"), "zip", os.path.join("dist", name)
)
shutil.rmtree(os.path.join("dist", name))


