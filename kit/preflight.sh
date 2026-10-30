#!/bin/sh
# A lancer AVANT l'atelier. Objectif: zero ligne MANQUE.
ok() { printf 'OK     %s\n' "$1"; }
ko() { printf 'MANQUE %s\n' "$1"; }

command -v python3 >/dev/null 2>&1 && ok "python3 ($(python3 -V 2>&1 | cut -d' ' -f2))" || ko "python3"
command -v git >/dev/null 2>&1 && ok git || ko git
command -v curl >/dev/null 2>&1 && ok curl || ko curl

if docker info >/dev/null 2>&1; then
    ok "docker ($(docker info --format '{{.ServerVersion}}' 2>/dev/null))"
else
    ko "docker (daemon lance? droits rootless configures?)"
fi

command -v uv >/dev/null 2>&1 && ok "uv ($(uv --version 2>/dev/null | cut -d' ' -f2))" || ko "uv"
command -v podman >/dev/null 2>&1 && ok "podman (alternative a docker)" || true

echo "-> corrige chaque ligne MANQUE avant le debut de l'atelier"
