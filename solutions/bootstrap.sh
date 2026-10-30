#!/bin/sh
# bootstrap (solution): restaure l'environnement de l'atelier en une commande.
# Utilisable tel quel sur une machine fraiche (VM) ou dans le conteneur.
set -eu

PYINFRA_VERSION="3.10.0"
DOTFILES_REPO="https://github.com/TOI/dotfiles"    # <-- adapte

# 1. uv (le userland epingle sa version via mise par la suite)
if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"

# 2. pyinfra, en tant qu'outil (epingle)
uv tool install "pyinfra==$PYINFRA_VERSION"

# 3. ton repo de dotfiles (deploys + configs)
if [ ! -d "$HOME/dotfiles" ]; then
    git clone "$DOTFILES_REPO" "$HOME/dotfiles"
else
    git -C "$HOME/dotfiles" pull --ff-only
fi

# 4. la base (root) puis le userland
SUDO_FLAG=""
if [ "$(id -u)" != "0" ]; then
    SUDO_FLAG="--sudo"
fi
pyinfra @local "$HOME/dotfiles/deploy_base.py" $SUDO_FLAG -y
pyinfra @local "$HOME/dotfiles/deploy_user.py" -y
