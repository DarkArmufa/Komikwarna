#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ "${1:-}" == "--preview" ]]; then
  exec python3 installer/server.py
fi
if [[ $EUID -ne 0 ]]; then
  echo 'Jalankan launcher sekali dengan: sudo bash START-INSTALLER.sh'
  exit 1
fi
command -v python3 >/dev/null || { echo 'Python 3.12 bawaan Ubuntu 24.04 diperlukan.'; exit 1; }
exec python3 installer/server.py --live
