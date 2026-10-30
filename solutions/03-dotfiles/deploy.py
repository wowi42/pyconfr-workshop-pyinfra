"""
ex03 (solution): dotfiles versionnes, $HOME en liens symboliques.

    PYCONFR_HOME=$PWD/faux-home pyinfra @local deploy.py
    GIT_NAME="Ton Nom" GIT_EMAIL="toi@example.com" pyinfra @local deploy.py
"""

import os

from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import files, git

HOME = os.environ.get("PYCONFR_HOME") or host.get_fact(Home)
ICI = os.path.dirname(os.path.abspath(__file__))
DOTFILES = f"{ICI}/dotfiles"

LIENS = [
    (f"{HOME}/.vimrc", f"{DOTFILES}/vimrc"),
    (f"{HOME}/.config/starship.toml", f"{DOTFILES}/starship.toml"),
    (f"{HOME}/.config/fish/config.fish", f"{DOTFILES}/fish-config.fish"),
]

for chemin, cible in LIENS:
    files.link(
        name=f"Lien {chemin}",
        path=chemin,
        target=cible,
        force=True,
    )

files.template(
    name="gitconfig personnalise",
    src=f"{DOTFILES}/gitconfig.j2",
    dest=f"{HOME}/.gitconfig",
    nom=os.environ.get("GIT_NAME", "Ada Lovelace"),
    email=os.environ.get("GIT_EMAIL", "ada@example.com"),
)

# Bonus: cloner TON repo de dotfiles (decommente et adapte l'URL).
# git.repo(src="https://github.com/TOI/dotfiles", dest=f"{HOME}/dotfiles")
