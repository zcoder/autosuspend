### Auto-Suspend on Low Load + Wake-on-LAN Reset

The **`auto_suspend`** daemon puts the machine to sleep if the 15-minute load average stays below **`1.5`** for **three hours** straight and **resets the timer** whenever it receives a Wake-on-LAN frame (UDP / 9).

Project layout:

| File                   | Purpose                                     |
| ---------------------- | ------------------------------------------- |
| `auto_suspend`         | Python daemon (load monitor + WoL listener) |
| `auto-suspend.service` | systemd unit                                |
| `install.sh`           | idempotent installer (symlinks + restart)   |
| `firewall.sh`          | minimal WoL setup (ethtool + iptables)      |
| `wakeup.py`            | Python CLI to send WoL                      |
| `wakeup.sh`            | Shell helper (uses `wakeonlan` package)     |

---

### Requirements

* Ubuntu 22.04 (or any systemd distro)
* Python ≥ 3.8, **psutil** package:

  ```bash
  sudo apt install python3-pip
  sudo pip3 install psutil wakeonlan
  ```
* Wake-on-LAN enabled in BIOS/UEFI.

---

### Installation

```bash
git clone https://…/auto-suspend.git
cd auto-suspend
sudo ./install.sh          # creates symlinks, enables + starts systemd unit
```

**Enable WoL and open firewall** (once):

```bash
sudo ./firewall.sh         # sets 'wol g' on eno2 and allows UDP/9
```

> Adjust the interface name inside `firewall.sh` if needed.

---

### Usage

| Task                      | Command                                                    |
| ------------------------- | ---------------------------------------------------------- |
| Tail daemon log           | `journalctl -u auto-suspend.service -f`                    |
| Wake workstation (Python) | `python wakeup.py AA:BB:CC:DD:EE:FF -b 192.168.1.255`      |
| Wake workstation (shell)  | `./wakeup.sh` — edit MAC inside the file                   |
| Change thresholds         | edit constants in `auto_suspend`, then `sudo ./install.sh` |

The daemon logs status every 30 s: current LA and seconds until suspend.

---

### How it works

1. Load checked every 30 s, using **LA 15**.
2. If LA 15 < 1.5 for 3 h **→** `systemctl suspend`.
3. Any valid WoL frame (UDP / 9) resets the idle timer.
4. Unit restarts automatically after resume.

---

### Tweaks

* `LOAD_THRESHOLD` — low-load threshold.
* `TIMEOUT_SEC` — idle duration before suspend.
* To listen on port 7 as well, change `WOL_PORT = 9` to a tuple `(7, 9)` and adjust the loop accordingly (see code comments).

---

### Update

```
git pull
sudo ./install.sh
```

`install.sh` is idempotent and restarts the service.

---

### License

MIT.
