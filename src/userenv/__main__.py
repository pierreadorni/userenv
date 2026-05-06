import sys
import os
from pathlib import Path

# path to the current script
script_path = Path(__file__).resolve()

base = script_path.parent.parent
lib = base / "lib"

# add the lib directory to the system path
for folder in lib.glob("python*/site-packages"):
    sys.path.insert(0, str(folder))

if __name__ == "__main__":
    from userenv.cli import app

    app()
