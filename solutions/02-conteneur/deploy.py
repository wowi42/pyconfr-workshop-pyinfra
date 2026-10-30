"""
ex02 (solution): conteneur jetable.

    pyinfra @docker/archlinux:latest deploy.py -y

Sur Mac ARM (pas d'image archlinux/arm64):
    pyinfra @docker/archlinux:latest --data docker_platform=linux/amd64 deploy.py -y
"""

import io

from pyinfra import host
from pyinfra.facts.server import LinuxName
from pyinfra.operations import apt, files, pacman, server

DESTRUCTIBLE = "/root/env-jetable"

# Les facts se lisent comme des variables: on peut brancher le code dessus,
# y compris le gestionnaire de paquets.
DISTRIB = host.get_fact(LinuxName)

# Le sandbox de pacman (seccomp/syscalls) echoue dans les conteneurs.
# On desactive les deux options dans /etc/pacman.conf. Sans ce bloc,
# pacman.packages echoue dans le conteneur Arch.
if DISTRIB == "Arch Linux":
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

if DISTRIB == "Arch Linux":
    pacman.packages(
        name="Paquets de l'atelier",
        packages=["curl", "git", "openssh", "unzip", "fontconfig", "htop"],
        update=True,
    )
elif DISTRIB in ("Debian", "Ubuntu"):
    apt.update(name="Listes de paquets a jour", cache_time=3600)
    apt.packages(
        name="Paquets de l'atelier",
        packages=["curl", "git", "openssh", "unzip", "fontconfig", "htop"],
        update=True,
    )
else:
    server.shell(
        name="Branche a adapter pour ton OS",
        commands="echo 'ici: brew install ... ou pkg install ...'",
    )

files.directory(path=DESTRUCTIBLE)

files.put(
    name="Laisse une trace",
    src=io.StringIO("je survivrai a la destruction (non)\n"),
    dest=f"{DESTRUCTIBLE}/readme.txt",
)

server.shell(
    name="Verifie le resultat",
    commands=f"ls {DESTRUCTIBLE} && cat {DESTRUCTIBLE}/readme.txt",
)
