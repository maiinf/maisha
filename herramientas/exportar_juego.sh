#!/usr/bin/env bash
# Exporta Maisha v1.0.0 en modo Release (solo HD-2D) para macOS (.app) y Windows Desktop (.exe)
# Uso: ./herramientas/exportar_juego.sh [macos|windows|todo]
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
GODOT="${GODOT:-/Applications/Godot.app/Contents/MacOS/Godot}"
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

case "$OBJETIVO" in
  macos) exportar_macos ;;
  windows) exportar_windows ;;
  todo) exportar_macos; exportar_windows ;;
  *) echo "Uso: $0 [macos|windows|todo]" >&2; exit 1 ;;
esac

echo "==> Exportación completada en $RAIZ/exportaciones/"
