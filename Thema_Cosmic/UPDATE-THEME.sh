#!/usr/bin/env bash
# Update the existing Panel theme only; this does not provision a new Panel or Wings.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
exec bash INSTALL-THEME.sh "$@"
