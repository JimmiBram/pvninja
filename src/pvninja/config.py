"""
Centralised configuration loader for PVNINJA.

Usage
-----
from pvninja.config import PVNinjaConfig
cfg = PVNinjaConfig.load()         # autodetect
print(cfg.broker, cfg.db_dsn)

# or write a fresh file with sensible defaults
cfg.save()                         # ~/.config/pvninja/config.json  (Linux)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel


class PVNinjaConfig(BaseModel):
    # ---------- your settings ----------
    broker: str
    port: int
    username: str
    password: str
    db_dsn: str  # e.g. "postgresql://user:pass@localhost:5432/dbname"
    # -----------------------------------

    # filename to look for
    FILENAME: ClassVar[str] = "config.json"

    # ---- internals ---------------------------------------------------------
    @classmethod
    def _candidate_paths(cls) -> list[Path]:
        """
        Ordered list of places we look for the JSON file.
        Environment variable 'PVNINJA_CONFIG' beats everything.
        """
        # 1. explicit override
        if (override := os.getenv("PVNINJA_CONFIG")):
            return [Path(override).expanduser()]

        paths: list[Path] = []

        # 2. per‑user config dir (platform specific)
        home = Path.home()
        if sys.platform.startswith("win"):
            appdata = Path(os.getenv("APPDATA", home / "AppData" / "Roaming"))
            paths.append(appdata / "PVNINJA" / cls.FILENAME)
        elif sys.platform == "darwin":
            paths.append(
                home / "Library" / "Application Support" / "PVNINJA" / cls.FILENAME
            )
        else:  # POSIX/Linux
            xdg = Path(os.getenv("XDG_CONFIG_HOME", home / ".config"))
            paths.append(xdg / "pvninja" / cls.FILENAME)

        # 3. project root (two levels up from this file => src/ -> project/)
        project_root = Path(__file__).resolve().parents[2]
        paths.append(project_root / cls.FILENAME)

        return paths

    # -----------------------------------------------------------------------

    @classmethod
    def load(cls) -> "PVNinjaConfig":
        """
        Locate the first existing config file and return a validated PVNinjaConfig.
        """
        for path in cls._candidate_paths():
            if path.is_file():
                with path.open(encoding="utf-8") as fp:
                    data = json.load(fp)
                return cls.model_validate(data)

        raise FileNotFoundError(
            "No PVNINJA config.json found in user config dir or project root."
        )

    # convenience helper -----------------------------------------------------
    def save(self, path: Path | None = None) -> None:
        """
        Write the current config to *path* (or the first candidate path).
        Creates parent directories as needed.
        """
        if path is None:
            # top‑priority candidate (env‑override OR per‑user dir)
            path = self._candidate_paths()[0]

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fp:
            json.dump(self.model_dump(), fp, indent=2)
        print(f"[PVNINJA] Wrote configuration to {path}")
