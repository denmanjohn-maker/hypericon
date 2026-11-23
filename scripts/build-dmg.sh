#!/bin/bash
# Builds a drag-to-Applications disk image.
# Usage: scripts/build-dmg.sh path/to/HyperIcon.app output.dmg
set -euo pipefail

APP="${1:?path to HyperIcon.app}"
OUT="${2:?output .dmg path}"
STAGING="$(mktemp -d)"
trap 'rm -rf "$STAGING"' EXIT

cp -R "$APP" "$STAGING/"
ln -s /Applications "$STAGING/Applications"
rm -f "$OUT"
hdiutil create -volname "HyperIcon" -srcfolder "$STAGING" -fs HFS+ -format UDZO -ov "$OUT"
echo "Created $OUT"
