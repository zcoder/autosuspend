#!/usr/bin/env bash
#
# install.sh – устанавливает auto_suspend daemon
#   • создаёт симлинки на локальные файлы
#   • перезапускает systemd-юнит
#   • работает повторно (idempotent)
#
# размещайте рядом:
#   auto_suspend
#   auto-suspend.service
#
# usage:
#   sudo ./install.sh            # или: ./install.sh (если уже root)
set -euo pipefail

# ───────────────────────────────────────────────────────────────────────────────
# Константы: куда ставим файлы
TARGET_BIN="/usr/local/bin/auto_suspend"
TARGET_UNIT="/etc/systemd/system/auto-suspend.service"
# ───────────────────────────────────────────────────────────────────────────────

need_root() {
  if [[ $EUID -ne 0 ]]; then
    echo "💡 Требуются root-права – повторите через sudo" >&2
    exit 1
  fi
}

make_symlink() {
  local src="$1" dst="$2"
  ln -sf "$src" "$dst"
  echo "→ $dst → $src"
}

main() {
  need_root

  local here
  here="$(dirname "$(realpath "$0")")"

  # 1. Симлинк скрипта
  make_symlink "$here/auto_suspend" "$TARGET_BIN"
  chmod +x "$TARGET_BIN"

  # 2. Симлинк systemd-юнита
  make_symlink "$here/auto-suspend.service" "$TARGET_UNIT"

  # 3. Активация / перезапуск
  systemctl daemon-reload
  systemctl enable --now auto-suspend.service

  echo "✅ Установка завершена. Логи: journalctl -u auto-suspend.service -f"
}

main "$@"

