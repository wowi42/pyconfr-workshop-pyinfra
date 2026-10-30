"""
ex03: dotfiles versionnes, $HOME en liens symboliques.

    PYCONFR_HOME=$PWD/faux-home pyinfra @local deploy.py --dry
    GIT_NAME="Ton Nom" GIT_EMAIL="toi@example.com" pyinfra @local deploy.py
"""

import os

from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import files, git

HOME = os.environ.get("PYCONFR_HOME") or host.get_fact(Home)
ICI = os.path.dirname(os.path.abspath(__file__))
DOTFILES = f"{ICI}/dotfiles"

# La table des liens: chemin dans $HOME -> cible dans le repo.
LIENS = [
    (f"{HOME}/.vimrc", f"{DOTFILES}/vimrc"),
    (f"{HOME}/.config/starship.toml", f"{DOTFILES}/starship.toml"),
    (f"{HOME}/.config/fish/config.fish", f"{DOTFILES}/fish-config.fish"),
]

# TODO(atelier): boucle sur LIENS avec files.link
# (path=chemin, target=cible, force=True, create_remote_dir se gere tout seul)

# TODO(atelier): files.template du gitconfig: src=dotfiles/gitconfig.j2,
# dest=~/.gitconfig, variables nom et email lues dans l'environnement
# (os.environ.get("GIT_NAME", "Ada Lovelace"), idem GIT_EMAIL).

# Bonus: cloner TON repo de dotfiles et relier depuis la.
# git.repo(src="https://github.com/TOI/dotfiles", dest=f"{HOME}/dotfiles")
