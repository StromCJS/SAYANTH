#!/usr/bin/env bash
# Downloads the three source fonts into tools/fonts/.
#
# They are NOT committed. Sora and JetBrains Mono could be (both OFL), but
# Clash Display's licence forbids redistributing the font file, so the build
# fetches all three the same way and keeps the repository clean.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p fonts
cd fonts

get() { echo "  $2"; curl -fsSL -o "$2" "$1"; }

echo "fetching fonts..."
get "https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/fonts/variable/JetBrainsMono%5Bwght%5D.ttf" \
    "JetBrainsMono-Var.ttf"
get "https://raw.githubusercontent.com/google/fonts/main/ofl/sora/Sora%5Bwght%5D.ttf" \
    "Sora.ttf"

if [ ! -f ClashDisplay-Variable.ttf ]; then
  echo "  ClashDisplay-Variable.ttf (via fontshare)"
  curl -fsSL -o clash.zip "https://api.fontshare.com/v2/fonts/download/clash-display"
  python -c "import zipfile; z=zipfile.ZipFile('clash.zip'); \
open('ClashDisplay-Variable.ttf','wb').write(z.read('ClashDisplay_Complete/Fonts/TTF/ClashDisplay-Variable.ttf'))"
  rm -f clash.zip
fi

ls -la
echo "done - now run: python build.py"
