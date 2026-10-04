#!/usr/bin/env bash
set -euo pipefail
EXPECTED_SHA256='d7d36fca8bc74d67cd86e9104f3805fdf563a4e219236014865fa0f94d74832f'
if [[ ! -t 0 ]]; then
  echo 'License key wajib dimasukkan dari terminal interaktif.' >&2
  exit 41
fi
printf 'Masukkan LICENSE KEY: '
IFS= read -r -s LICENSE_KEY
printf '\n'
ACTUAL_SHA256="$(printf '%s' "$LICENSE_KEY" | sha256sum | awk '{print $1}')"
unset LICENSE_KEY
if [[ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]]; then
  echo 'License key salah. Proses dibatalkan.' >&2
  exit 42
fi
echo 'License valid.'
