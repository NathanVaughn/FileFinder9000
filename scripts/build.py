import os
import shutil
import subprocess
import sys

name = "FileFinder9000"

subprocess.run(
    [
        "pyinstaller",
        f"--name={name}",
        # "--onefile",
        "--noconsole",
        "--icon=images/icon.ico",
        f"--add-data=images/icon.ico{os.pathsep}images/icon.ico",
        "--noconfirm",
        "main.py",
    ]
)

shutil.make_archive(
    os.path.join("dist", f"{name}-{sys.platform}"), "zip", os.path.join("dist", name)
)
shutil.rmtree(os.path.join("dist", name))
