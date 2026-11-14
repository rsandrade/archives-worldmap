#!/usr/bin/env bash
# Baixa os assets vendorizados nas versões fixadas abaixo.
# Depois de rodar, atualize os SHA256 em VERSIONS.md (o script imprime os hashes).
set -euo pipefail

BOOTSTRAP="${BOOTSTRAP_VERSION:-5.3.9}"
LEAFLET="${LEAFLET_VERSION:-1.9.4}"
MARKERCLUSTER="${MARKERCLUSTER_VERSION:-1.5.3}"

cd "$(dirname "$0")/.."
V=app/static/vendor

mkdir -p "$V/bootstrap" "$V/leaflet/images" "$V/leaflet-markercluster"

curl -fsSL "https://cdn.jsdelivr.net/npm/bootstrap@${BOOTSTRAP}/dist/css/bootstrap.min.css" -o "$V/bootstrap/bootstrap.min.css"
curl -fsSL "https://cdn.jsdelivr.net/npm/bootstrap@${BOOTSTRAP}/dist/js/bootstrap.min.js"   -o "$V/bootstrap/bootstrap.min.js"
curl -fsSL "https://unpkg.com/leaflet@${LEAFLET}/dist/leaflet.js"  -o "$V/leaflet/leaflet.js"
curl -fsSL "https://unpkg.com/leaflet@${LEAFLET}/dist/leaflet.css" -o "$V/leaflet/leaflet.css"
for img in marker-icon.png marker-icon-2x.png marker-shadow.png layers.png layers-2x.png; do
  curl -fsSL "https://unpkg.com/leaflet@${LEAFLET}/dist/images/${img}" -o "$V/leaflet/images/${img}"
done
curl -fsSL "https://unpkg.com/leaflet.markercluster@${MARKERCLUSTER}/dist/leaflet.markercluster.js" -o "$V/leaflet-markercluster/leaflet.markercluster.js"
curl -fsSL "https://unpkg.com/leaflet.markercluster@${MARKERCLUSTER}/dist/MarkerCluster.css"         -o "$V/leaflet-markercluster/MarkerCluster.css"
curl -fsSL "https://unpkg.com/leaflet.markercluster@${MARKERCLUSTER}/dist/MarkerCluster.Default.css" -o "$V/leaflet-markercluster/MarkerCluster.Default.css"

echo "Versões: bootstrap=${BOOTSTRAP} leaflet=${LEAFLET} markercluster=${MARKERCLUSTER}"
echo "SHA256 (atualizar VERSIONS.md):"
(cd "$V" && find . -type f ! -name 'VERSIONS.md' -print0 | sort -z | xargs -0 sha256sum | sed 's|\./||')
