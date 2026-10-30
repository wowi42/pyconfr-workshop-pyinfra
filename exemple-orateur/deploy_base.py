"""
La base de la machine de demo (root). Lance rarement: machine neuve.

    pyinfra -i inventory.py vm_neuve deploy_base.py -y
    pyinfra @local deploy_base.py --sudo
"""

import io
import os

from pyinfra import host
from pyinfra.facts.files import Directory, File
from pyinfra.facts.server import LinuxName
from pyinfra.operations import apt, files, pacman, server, systemd

EN_CONTENEUR = host.get_fact(File, path="/.dockerenv") is not None
SUDO = {} if EN_CONTENEUR else {"_sudo": True}

# Sur une vraie machine fraiche: True (docker + groupe + service).
# Dans les conteneurs de l'atelier: False, docker est trop lourd a installer.
INSTALLER_DOCKER = False

USER = os.environ.get("DEMO_USER", "atelier")
DISTRIB = host.get_fact(LinuxName)

if DISTRIB == "Arch Linux":
    pacman.packages(
        name="Paquets de base",
        packages=["curl", "git", "openssh", "sudo", "unzip", "fontconfig", "htop"],
        update=True,
        **SUDO,
    )
    GROUPE_ADMIN = "wheel"
elif DISTRIB in ("Debian", "Ubuntu"):
    apt.update(name="Listes de paquets a jour", cache_time=3600, **SUDO)
    apt.packages(
        name="Paquets de base",
        packages=["curl", "git", "openssh", "sudo", "unzip", "fontconfig", "htop"],
        update=True,
        **SUDO,
    )
    GROUPE_ADMIN = "sudo"
else:
    raise SystemExit(f"Distribution non supportee: {DISTRIB}")

server.user(
    name=f"Utilisateur {USER}",
    user=USER,
    home=f"/home/{USER}",
    shell="/bin/bash",
    groups=[GROUPE_ADMIN] + (["docker"] if INSTALLER_DOCKER else []),
    append=True,
    **SUDO,
)

if host.get_fact(Directory, path="/run/systemd/system") and INSTALLER_DOCKER:
    if DISTRIB == "Arch Linux":
        pacman.packages(name="Docker", packages=["docker"], **SUDO)
    else:
        apt.packages(name="Docker", packages=["docker.io"], **SUDO)
    server.user(
        name=f"{USER} dans le groupe docker",
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
elif not host.get_fact(Directory, path="/run/systemd/system"):
    files.put(
        name="Note pour la vraie vie",
        src=io.StringIO(
            "machine systemd: installer docker, groupe docker, service actif\n"
        ),
        dest="/root/NEXT-STEPS.txt",
    )
