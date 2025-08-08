import os
import platform

if platform.system() == "Windows":
    dll_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "runtime", "win_x64"))
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(dll_path)
    else:
        os.environ["PATH"] = dll_path + os.pathsep + os.environ["PATH"]
