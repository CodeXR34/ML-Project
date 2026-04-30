# sitecustomize.py
# Ensures the project-local site-packages (one level up) are always on sys.path
# regardless of which directory Python is launched from.
import sys, os

_packages = r"C:\Users\shivam\OneDrive\Documents\shivam proj\Lib\site-packages"
if _packages not in sys.path:
    sys.path.insert(1, _packages)
