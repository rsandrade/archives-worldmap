#!/usr/bin/env bash
# Verifica se os assets vendorizados batem com os SHA256 de VERSIONS.md.
set -euo pipefail

cd "$(dirname "$0")/.."
V=app/static/vendor

grep -E '^[0-9a-f]{64}  ' "$V/VERSIONS.md" | (cd "$V" && sha256sum -c --quiet -) \
  && echo "vendor OK: $(grep -cE '^[0-9a-f]{64}  ' "$V/VERSIONS.md") arquivos conferidos"
