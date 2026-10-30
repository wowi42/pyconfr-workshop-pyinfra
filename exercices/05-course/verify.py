"""
ex05: verification post-restauration. Une erreur = un point perdu.

Mode faux home (filesystem persistant, donc verifiable en run separe):

    PYCONFR_HOME=$PWD/faux-home pyinfra @local verify.py -y

Pour le conteneur sans etat, la verification est la section finale de
restore.py (solutions/course), executee dans le meme run.
"""

import os

from pyinfra.operations import server

HOME = os.environ.get("PYCONFR_HOME") or "/root"

CHECKS = [
    ".local/bin/mise",
    ".local/bin/starship",
    ".config/mise/config.toml",
    ".config/starship.toml",
    ".gitconfig",
    ".vimrc",
    ".ssh/id_ed25519",
    ".local/share/fonts",
]

for c in CHECKS:
    server.shell(name=f"check {c}", commands="test -e {0}/{1}".format(HOME, c))

server.shell(
    name="check identite git",
    commands="grep -q email {0}/.gitconfig".format(HOME),
)
server.shell(
    name="check polices installees",
    commands='test -n "$(ls {0}/.local/share/fonts)"'.format(HOME),
)
server.shell(
    name="check droits .ssh en 700",
    commands='test "$(stat -c %a {0}/.ssh 2>/dev/null || stat -f %A {0}/.ssh)" = 700'.format(HOME),
)
