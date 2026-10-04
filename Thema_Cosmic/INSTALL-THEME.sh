#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
PANEL_DIR="${PANEL_DIR:-/var/www/pterodactyl}"
if [[ $EUID -ne 0 ]]; then echo 'Gunakan sudo bash INSTALL-THEME.sh'; exit 1; fi
python3 theme/install-theme.py --panel "$PANEL_DIR" "$@"
(cd -- "$PANEL_DIR" && php artisan route:clear && php artisan view:clear)
echo 'Selesai. Refresh browser (hapus cache jika perlu).'
