"""Simple orchestration script that builds platform-specific executables via PyInstaller."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT / "build"
DIST_DIR = ROOT / "dist"

TARGETS = {
    "windows": {"name": "ZoteroRAG-Windows", "windowed": True},
    "macos": {"name": "ZoteroRAG-macOS", "windowed": True},
    "linux": {"name": "ZoteroRAG-Linux", "windowed": False},
}


def build_target(target: str) -> None:
    """Invoke PyInstaller for a single target configuration."""

    config = TARGETS[target]
    dist_target = DIST_DIR / target
    work_target = BUILD_DIR / target
    dist_target.mkdir(parents=True, exist_ok=True)
    work_target.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        config["name"],
        "--distpath",
        str(dist_target),
        "--workpath",
        str(work_target),
        "--specpath",
        str(work_target),
        "--onefile",
        "--noconfirm",
        "--clean",
    ]

    if config.get("windowed"):
        command.append("--windowed")

    command.append(str(ROOT / "main.py"))

    subprocess.run(command, check=True)


def main() -> int:
    """CLI entry point to build one or more platform executables."""

    parser = argparse.ArgumentParser(
        description="Build platform-specific Zotero RAG executables via PyInstaller."
    )
    parser.add_argument(
        "--target",
        choices=list(TARGETS),
        nargs="+",
        default=list(TARGETS),
        help="Which platform target(s) to build.",
    )
    args = parser.parse_args()

    for target in args.target:
        build_target(target)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
