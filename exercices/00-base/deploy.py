"""
ex00: la base, en root. Machine fraiche = paquets + user + docker.

Conteneur (on y est deja root):
    pyinfra @docker/archlinux:latest deploy.py -y

Vraie machine:
    pyinfra @local deploy.py --sudo
"""

import os

from pyinfra import host
from pyinfra.operations import apt, server

# Dans un conteneur, on est root: inutile de sudo. Ailleurs, toutes les
# operations root passent _sudo=True (ou le flag --sudo en CLI).
# TODO(atelier): trouve un fact qui detecte qu'on est dans un conteneur
# (indice: kit/triche.md, facts File). Stocke le resultat dans EN_CONTENEUR.
EN_CONTENEUR = False
SUDO = {} if EN_CONTENEUR else {"_sudo": True}

USER = os.environ.get("ATELIER_USER", "atelier")

# TODO(atelier): detecte la distribution (fact LinuxName) et installe les
# paquets de base curl/git/sudo avec le bon gestionnaire:
#   Arch Linux   -> pacman.packages(..., update=True)
#   Debian/Ubuntu-> apt.update(..., cache_time=3600) puis apt.packages(...)
# Stocke aussi le groupe admin: "wheel" sur Arch, "sudo" ailleurs.

# Conteneur Arch: le sandbox de pacman echoue (seccomp). On le desactive
# via files.replace sur /etc/pacman.conf. Deja fait pour toi, lis-le.
if EN_CONTENEUR:
    pass  # TODO(atelier): files.replace de ^#DisableSandboxFilesystem et
          # ^#DisableSandboxSyscalls vers la version sans '#'

apt.packages(
    name="Installe les paquets de base",
    packages=["curl", "git", "sudo"],
    update=True,
    **SUDO,
)

# TODO(atelier): cree l'utilisateur principal:
#   user=USER, home=/home/USER, shell=/bin/bash,
#   groups=[GROUPE_ADMIN], append=True
# (indice: server.user)

# Docker: sur une machine avec systemd (VM, physique), on installe docker,
# on ajoute l'utilisateur au groupe docker et on active le service.
# Dans un conteneur simple, ce bloc doit etre Saute: trouve le fact qui
# detecte la presence de systemd (indice: /run/systemd/system est un
# repertoire sur les machines systemd).
# TODO(atelier): ecris ce if/else:
#   - branche "vraie machine": paquet docker (nom different selon la
#     distribution!), puis server.user(groups=[GROUPE_ADMIN, "docker"],
#     append=True) pour ajouter l'utilisateur au groupe (pas de usermod),
#     puis systemd.service(service="docker", running=True, enabled=True)
#   - branche conteneur: files.put de /root/NEXT-STEPS.txt
# Imports utiles: pyinfra.operations.{apt,pacman,systemd,files},
# pyinfra.facts.files.Directory, io.
