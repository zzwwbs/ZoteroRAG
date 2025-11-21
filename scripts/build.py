"""PyInstaller build orchestrator for cross-platform artifacts."""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT / "build"
DIST_DIR = ROOT / "dist"
SRC_DIR = ROOT / "src"

TARGETS = {
    "windows": {"name": "ZoteroRAG-Windows", "windowed": True, "extension": ".exe"},
    "macos": {"name": "ZoteroRAG-macOS", "windowed": True, "extension": ".app"},
    "linux": {"name": "ZoteroRAG-Linux", "windowed": False, "extension": ""},
}


def build_target(target: str) -> None:
    """Invoke PyInstaller for a single target configuration."""

    config = TARGETS[target]
    dist_target = DIST_DIR / target
    work_target = BUILD_DIR / target
    dist_target.mkdir(parents=True, exist_ok=True)
    work_target.mkdir(parents=True, exist_ok=True)

    assets_dir = SRC_DIR / "zoterorag" / "ui" / "assets"
    datas = []
    if assets_dir.exists():
        datas.append(f"{assets_dir}{os.pathsep}zoterorag/ui/assets")

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

    if datas:
        for data in datas:
            command.extend(["--add-data", data])

    command.append(str(SRC_DIR / "zoterorag" / "__main__.py"))

    subprocess.run(command, check=True)

    if target == "macos":
        create_dmg_placeholder(dist_target, config["name"])


def create_dmg_placeholder(dist_target: Path, app_name: str) -> None:
    """Create a placeholder DMG step (hook for future code-sign/notarization)."""
    app_path = next(dist_target.glob(f"{app_name}*{TARGETS['macos']['extension']}"), None)
    dmg_path = dist_target / f"{app_name}.dmg"
    if app_path and not dmg_path.exists():
        dmg_path.write_text("DMG packaging placeholder - integrate hdiutil and codesign here.")


def main() -> int:
    """CLI entry point to build one or more platform executables."""

    parser = argparse.ArgumentParser(
        description="Build platform-specific Zotero RAG executables via PyInstaller."
    )
    parser.add_argument(
        "--target",
        choices=list(TARGETS),
        nargs="+",
        default=[current_platform_target()],
        help="Which platform target(s) to build.",
    )
    args = parser.parse_args()

    for target in args.target:
        build_target(target)

    return 0


def current_platform_target() -> str:
    system = platform.system().lower()
    if system.startswith("win"):
        return "windows"
    if system.startswith("darwin"):
        return "macos"
    return "linux"


if __name__ == "__main__":
    raise SystemExit(main())
