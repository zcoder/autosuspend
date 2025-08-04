#!/usr/bin/env python3
"""WOL Tray Indicator

Minimal system‑tray application for Ubuntu 22.04 that shows the power
state of a remote host ("lzwork") and allows the user to wake or sleep
it via existing shell scripts.

* Green icon  – host replies to **arping** (awake)
* Yellow icon – host is silent      (sleeping)

The program relies only on the standard Gtk/AppIndicator stack that is
already present on modern Ubuntu desktops.  No additional Python
packages are required besides *PyGObject* (python3‑gi) which ships with
Ubuntu.

Author: ChatGPT (OpenAI)
Licence: MIT
"""
from __future__ import annotations

import os
import signal
import subprocess
from pathlib import Path
from typing import Final

import gi  # type: ignore

gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import AppIndicator3, GLib, Gtk  # type: ignore

###############################################################################
#                     ─── USER‑CONFIGURABLE CONSTANTS ───                    #
###############################################################################
# Hostname or IPv4 address that we probe with `arping` (must resolve locally)
HOST: Final[str] = "lzwork"
# Full path of the script that sends the Magic Packet (Wake‑on‑LAN)
WAKE_SCRIPT: Final[Path] = Path("/home/zhenka/bin/wake_lzwork")
# Full path of the script that puts the host to sleep
SLEEP_SCRIPT: Final[Path] = Path("/home/zhenka/bin/wake_lzwork__go_sleep")
# Probe interval, seconds
CHECK_INTERVAL: Final[int] = 10

# Icons ───────────────────────────────────────────────────────────────────────
# Two png files (16×16 or 24×24) placed next to this script.  Feel free to
# replace them with your own artwork.
ICON_AWAKE: Final[str] = str(Path(__file__).with_name("icon_green.png"))
ICON_SLEEP: Final[str] = str(Path(__file__).with_name("icon_yellow.png"))

# Fallback to symbolic theme icons if the pngs are missing.
ICON_AWAKE_FALLBACK: Final[str] = "network-transmit-receive"
ICON_SLEEP_FALLBACK: Final[str] = "network-offline"
###############################################################################


class WolIndicator:
    """Single‑icon tray indicator for WOL control."""

    def __init__(self) -> None:
        self.indicator = AppIndicator3.Indicator.new(
            "wol-indicator",
            ICON_SLEEP_FALLBACK,
            AppIndicator3.IndicatorCategory.HARDWARE,
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        # Build dropdown menu
        self._menu = Gtk.Menu()
        self._append_item("Пробудить", self._wake)
        self._append_item("Усыпить", self._sleep)
        self._menu.append(Gtk.SeparatorMenuItem())
        self._append_item("Выход", self._quit)

        self.indicator.set_menu(self._menu)

        # First status update immediately
        self._update_status()
        # Schedule periodic checks
        GLib.timeout_add_seconds(CHECK_INTERVAL, self._update_status)

    # ────────────────────────────── Menu helpers ───────────────────────────
    def _append_item(self, label: str, callback) -> None:
        item = Gtk.MenuItem(label=label)
        item.connect("activate", callback)
        item.show()
        self._menu.append(item)

    # ────────────────────────────── Callbacks ──────────────────────────────
    def _wake(self, _widget) -> None:
        subprocess.Popen([str(WAKE_SCRIPT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _sleep(self, _widget) -> None:
        subprocess.Popen([str(SLEEP_SCRIPT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _quit(self, _widget) -> None:
        Gtk.main_quit()

    # ──────────────────────────── Host detection ───────────────────────────
    @staticmethod
    def _is_host_up() -> bool:
        """Returns *True* when the host replies to a single arping probe."""
        result = subprocess.run(
            ["arping", "-c", "1", "-w", "1", HOST],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0

    def _update_status(self):  # type: ignore[override]  # GLib quirk
        """Timer callback – refreshes the tray icon colour."""
        host_up = self._is_host_up()
        icon_path = ICON_AWAKE if host_up and Path(ICON_AWAKE).exists() else (
            ICON_AWAKE_FALLBACK if host_up else (
                ICON_SLEEP if Path(ICON_SLEEP).exists() else ICON_SLEEP_FALLBACK
            )
        )
        self.indicator.set_icon_full(icon_path, "wol-state")
        # Repeat this timer
        return True


def main() -> None:
    # Ensure our child processes terminate when the GUI closes
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    WolIndicator()
    Gtk.main()


if __name__ == "__main__":
    main()
