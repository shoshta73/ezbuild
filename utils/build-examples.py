from os import chdir
from pathlib import Path
from subprocess import run

ROOT_DIR = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT_DIR / "examples"


if __name__ == "__main__":
    for example in EXAMPLES_DIR.iterdir():
        if example.is_dir():
            chdir(example)
            print(f"Building {example.name}")
            run(["ezbuild", "build"])
            chdir(ROOT_DIR)
