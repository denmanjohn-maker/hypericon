#!/bin/bash
# Removes every folder and disk icon HyperIcon applied, without needing the app.
# Use this if you deleted HyperIcon before choosing "Restore Original Icons".
#
#   bash restore-icons.sh
#
# It finds themed folders by the marker HyperIcon leaves on them (the
# com.hypericon.applied extended attribute), removes the custom icon, the
# marker, and the ignore lines added to a repository's .git/info/exclude.
# Icons you had set yourself before HyperIcon replaced them can only be put
# back by the app (Restore Original Icons), which holds the backups.
set -uo pipefail

ATTR="com.hypericon.applied"
SUPPORT="$HOME/Library/Application Support/HyperIcon"
count=0

restore_folder() {
  local dir="$1"
  [ -d "$dir" ] || return 0
  xattr -p "$ATTR" "$dir" >/dev/null 2>&1 || return 0
  # Ask Finder's own API to remove the custom icon.
  /usr/bin/osascript -l JavaScript -e 'ObjC.import("AppKit"); function run(argv) { $.NSWorkspace.sharedWorkspace.setIconForFileOptions($(), argv[0], 0); }' "$dir" >/dev/null 2>&1
  rm -f "$dir/Icon"$'\r'
  xattr -d "$ATTR" "$dir" 2>/dev/null
  local exclude="$dir/.git/info/exclude"
  if [ -f "$exclude" ] && grep -q "^# HyperIcon:" "$exclude"; then
    /usr/bin/sed -i '' -e '/^# HyperIcon:/{N;d;}' "$exclude"
  fi
  count=$((count + 1))
  printf 'restored  %s\n' "$dir"
}

echo "Looking for folders themed by HyperIcon under $HOME ..."
while IFS= read -r -d '' dir; do
  restore_folder "$dir"
done < <(find "$HOME" \( -path "$HOME/Library" -o -name node_modules -o -name .git \) -prune -o -type d -xattrname "$ATTR" -print0 2>/dev/null)

# The Applications folder and connected disks (disks that are not connected now keep their icon).
for dir in /Applications /Volumes/*; do
  restore_folder "$dir"
done

echo
echo "Restored $count folders and disks."
if [ -f /System/Volumes/Data/.VolumeIcon.icns ]; then
  echo
  echo "Your startup disk has a custom icon. If HyperIcon set it, remove it with:"
  echo "  sudo rm /System/Volumes/Data/.VolumeIcon.icns"
fi
if [ -d "$SUPPORT" ]; then
  echo "HyperIcon's own data is in: $SUPPORT"
  echo "It is safe to delete once you are happy with the result."
fi
killall Finder >/dev/null 2>&1 || true
