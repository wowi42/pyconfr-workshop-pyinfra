"""
ex02: conteneur jetable.

    pyinfra @docker/archlinux:latest deploy.py --dry
    pyinfra @docker/archlinux:latest deploy.py -y
"""

import io

from pyinfra import host
from pyinfra.facts.server import LinuxName
from pyinfra.operations import apt, files, server

DESTRUCTIBLE = "/root/env-jetable"

# Le sandbox de pacman (seccomp/syscalls) echoue dans les conteneurs Arch.
# On desactive les deux options dans /etc/pacman.conf. Deja fait pour toi:
# sans ce bloc, pacman.packages echoue dans le conteneur.
files.replace(
    name="pacman: sandbox incompatible conteneur",
    path="/etc/pacman.conf",
    text="^#DisableSandboxFilesystem",
    replace="DisableSandboxFilesystem",
)
files.replace(
    name="pacman: sandbox syscalls incompatible conteneur",
    path="/etc/pacman.conf",
    text="^#DisableSandboxSyscalls",
    replace="DisableSandboxSyscalls",
)

# Les facts se lisent comme des variables: on peut brancher le code dessus.
# TODO(atelier): complete la condition pour que la branche pacman ne tourne
# que sur Arch Linux (fact LinuxName), la branche apt sur Debian/Ubuntu,
# et ecris la branche else.
if host.get_fact(LinuxName):
    apt.update(name="Listes de paquets a jour", cache_time=3600)
    apt.packages(
        name="Paquets de l'atelier",
        packages=["curl", "git", "openssh", "unzip", "fontconfig", "htop"],
        update=True,
    )

# TODO(atelier): cree le repertoire DESTRUCTIBLE (files.directory)

files.put(
    name="Laisse une trace",
    src=io.StringIO("je survivrai a la destruction (non)\n"),
    dest=f"{DESTRUCTIBLE}/readme.txt",
)

# TODO(atelier): affiche le contenu de DESTRUCTIBLE (server.shell)
