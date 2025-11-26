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
        "--add-data=images/icon.ico;images/icon.ico",
        "--noconfirm",
        "main.py",
    ]
)

shutil.make_archive(
    os.path.join("dist", f"{name}-{sys.platform}"), "zip", os.path.join("dist", name)
)
shutil.rmtree(os.path.join("dist", name))
