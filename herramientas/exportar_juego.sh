#!/usr/bin/env bash
# Exporta y empaqueta Maisha v1.0.0 en modo Release (solo HD-2D) para macOS (.app / .dmg) y Windows (.exe / .zip)
# Uso: ./herramientas/exportar_juego.sh [macos|windows|paquetes|todo]
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
GODOT="${GODOT:-/Applications/Godot.app/Contents/MacOS/Godot}"
VERSION="${VERSION:-1.0.0}"
OBJETIVO="${1:-todo}"

mkdir -p "$RAIZ/exportaciones/macos" "$RAIZ/exportaciones/windows"

exportar_macos() {
  echo "==> Exportando macOS (Universal .app)..."
  rm -rf "$RAIZ/exportaciones/macos/Maisha.app"
  "$GODOT" --headless --path "$RAIZ" --export-release "macOS" "$RAIZ/exportaciones/macos/Maisha.app"
  du -sh "$RAIZ/exportaciones/macos/Maisha.app"
}

exportar_windows() {
  echo "==> Exportando Windows Desktop (x86_64 .exe autocontenido)..."
  rm -rf "$RAIZ/exportaciones/windows/Maisha.exe" "$RAIZ/exportaciones/windows/Maisha.pck"
  "$GODOT" --headless --path "$RAIZ" --export-release "Windows Desktop" "$RAIZ/exportaciones/windows/Maisha.exe"
  du -sh "$RAIZ/exportaciones/windows/Maisha.exe"
}

empaquetar() {
  local guia="$RAIZ/documentacion/LEEME_JUGADOR.txt"
  local dmg="$RAIZ/exportaciones/Maisha-${VERSION}-macOS.dmg"
  local zip_win="$RAIZ/exportaciones/Maisha-${VERSION}-Windows.zip"
  local tmp_dmg
  local tmp_win
  tmp_dmg="$(mktemp -d /tmp/maisha_dmg_XXXXXX)"
  tmp_win="$(mktemp -d /tmp/maisha_win_XXXXXX)"
  trap 'rm -rf "$tmp_dmg" "$tmp_win"' RETURN

  if [ -d "$RAIZ/exportaciones/macos/Maisha.app" ]; then
    echo "==> Creando instalador macOS (.dmg)..."
    cp -R "$RAIZ/exportaciones/macos/Maisha.app" "$tmp_dmg/Maisha.app"
    ln -s /Applications "$tmp_dmg/Aplicaciones"
    cp "$guia" "$tmp_dmg/LEEME_JUGADOR.txt"
    rm -f "$dmg"
    hdiutil create -volname "Maisha ${VERSION}" -srcfolder "$tmp_dmg" -ov -format UDZO "$dmg"
    hdiutil verify "$dmg"
    du -sh "$dmg"
  fi

  if [ -f "$RAIZ/exportaciones/windows/Maisha.exe" ]; then
    echo "==> Creando paquete Windows (.zip)..."
    local carpeta="Maisha-${VERSION}-Windows"
    mkdir -p "$tmp_win/$carpeta"
    cp "$RAIZ/exportaciones/windows/Maisha.exe" "$tmp_win/$carpeta/Maisha.exe"
    cp "$guia" "$tmp_win/$carpeta/LEEME_JUGADOR.txt"
    rm -f "$zip_win"
    (cd "$tmp_win" && zip -q -r -9 "$zip_win" "$carpeta")
    unzip -t "$zip_win" >/dev/null
    du -sh "$zip_win"
  fi

  (
    cd "$RAIZ/exportaciones"
    shasum -a 256 "Maisha-${VERSION}-macOS.dmg" "Maisha-${VERSION}-Windows.zip" > SHA256SUMS.txt
  )
  echo "==> Checksums SHA-256:"
  cat "$RAIZ/exportaciones/SHA256SUMS.txt"
}

case "$OBJETIVO" in
  macos) exportar_macos ;;
  windows) exportar_windows ;;
  paquetes) empaquetar ;;
  todo) exportar_macos; exportar_windows; empaquetar ;;
  *) echo "Uso: $0 [macos|windows|paquetes|todo]" >&2; exit 1 ;;
esac

echo "==> Exportación completada en $RAIZ/exportaciones/"
