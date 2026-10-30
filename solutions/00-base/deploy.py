"""
ex00 (solution): la base, en root.

Conteneur (on y est deja root):
    pyinfra @docker/archlinux:latest deploy.py -y

Vraie machine:
    pyinfra @local deploy.py --sudo
"""

import io
import os

from pyinfra import host
from pyinfra.facts.files import Directory, File
from pyinfra.facts.server import LinuxName
from pyinfra.operations import apt, files, pacman, server, systemd

EN_CONTENEUR = host.get_fact(File, path="/.dockerenv") is not None
SUDO = {} if EN_CONTENEUR else {"_sudo": True}

USER = os.environ.get("ATELIER_USER", "atelier")
DISTRIB = host.get_fact(LinuxName)

# Paquets et groupe "sudo" equivalents selon la distribution.
if DISTRIB == "Arch Linux":
    if EN_CONTENEUR:
        # Le sandbox seccomp/syscalls de pacman echoue dans les conteneurs.
        files.replace(
            name="pacman: sandbox incompatible conteneur",
            path="/etc/pacman.conf",
            text="^#DisableSandboxFilesystem",
            replace="DisableSandboxFilesystem",
            **SUDO,
        )
        files.replace(
            name="pacman: sandbox syscalls incompatible conteneur",
            path="/etc/pacman.conf",
            text="^#DisableSandboxSyscalls",
            replace="DisableSandboxSyscalls",
            **SUDO,
        )
    pacman.packages(
        name="Paquets de base",
        packages=["curl", "git", "openssh", "sudo"],
        update=True,
        **SUDO,
    )
    GROUPE_ADMIN = "wheel"
elif DISTRIB in ("Debian", "Ubuntu"):
    apt.update(name="Listes de paquets a jour", cache_time=3600, **SUDO)
    apt.packages(
        name="Paquets de base",
        packages=["curl", "git", "openssh", "sudo"],
        update=True,
        **SUDO,
    )
    GROUPE_ADMIN = "sudo"
else:
    raise SystemExit(f"Distribution non supportee par l'exercice: {DISTRIB}")

server.user(
    name=f"Cree l'utilisateur {USER}",
    user=USER,
    home=f"/home/{USER}",
    shell="/bin/bash",
    groups=[GROUPE_ADMIN],
    append=True,
    **SUDO,
)

if host.get_fact(Directory, path="/run/systemd/system"):
    # Machine systemd (VM, physique): docker pour tout le monde.
    if DISTRIB == "Arch Linux":
        PAQUET_DOCKER = "docker"
    else:
        PAQUET_DOCKER = "docker.io"
    if DISTRIB == "Arch Linux":
        pacman.packages(name="Installe docker", packages=[PAQUET_DOCKER], **SUDO)
    else:
        apt.packages(name="Installe docker", packages=[PAQUET_DOCKER], **SUDO)
    # server.user avec append ajoute aux groupes existants: inutile d'appeler
    # usermod a la main.
    server.user(
        name=f"Ajoute {USER} au groupe docker",
        user=USER,
        groups=[GROUPE_ADMIN, "docker"],
        append=True,
        **SUDO,
    )
    systemd.service(
        name="Docker actif au boot",
        service="docker",
        running=True,
        enabled=True,
        **SUDO,
    )
else:
    # Conteneur simple: pas de systemd, on note la suite pour la vraie vie.
    files.put(
        name="Note pour la vraie vie",
        src=io.StringIO(
            "vraie machine: installer docker, ajouter l'utilisateur au "
            "groupe docker, activer le service\n"
        ),
        dest="/root/NEXT-STEPS.txt",
    )
