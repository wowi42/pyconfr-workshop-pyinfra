"""
La course: UN deploy complet qui restaure tout, d'un seul coup.

    GIT_NAME="Ton Nom" GIT_EMAIL="toi@example.com" \
        pyinfra @docker/archlinux:latest restore.py -y

Pourquoi un seul fichier: le connecteur @docker est SANS ETAT. Chaque run
recree un conteneur propre depuis l'image, execute, sauvegarde, supprime.
Tout ce qui doit exister a la fin doit donc etre cree DANS CE RUN:
systeme d'abord, userland ensuite, verification a la fin.

Sur Mac ARM (pas d'image archlinux/arm64), forcer l'emulation x86:

    pyinfra @docker/archlinux:latest --data docker_platform=linux/amd64 restore.py -y

Sur une vraie machine (@local), l'etat persiste: le deploy devient
rejouable, la verification confirme a chaque fois.
"""

import io
import os

from pyinfra import host
from pyinfra.facts.files import File
from pyinfra.facts.server import Arch, Home, LinuxName, Os, Users
from pyinfra.operations import apt, files, pacman, server

MISE_VERSION = "v2026.10.24"
STARSHIP_VERSION = "v1.27.0"
NERD_FONTS_VERSION = "v3.2.1"

HOME = os.environ.get("PYCONFR_HOME") or host.get_fact(Home)
BIN = f"{HOME}/.local/bin"
FONTS = f"{HOME}/.local/share/fonts"
CACHE = f"{HOME}/.cache/atelier"
ICI = os.path.dirname(os.path.abspath(__file__))
DOTFILES = f"{ICI}/dotfiles"

OS = host.get_fact(Os)
ARCH = host.get_fact(Arch)
DISTRIB = host.get_fact(LinuxName)

EN_CONTENEUR = host.get_fact(File, path="/.dockerenv") is not None
SUDO = {} if EN_CONTENEUR else {"_sudo": True}

# --- 1. systeme (root): uniquement ce qu'on ne peut pas faire en userland ---
# Detection de la distribution: une seule base de code, plusieurs OS.
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
        name="Paquets necessaires au userland",
        packages=["curl", "git", "openssh", "unzip", "fontconfig"],
        update=True,
        **SUDO,
    )
elif DISTRIB in ("Debian", "Ubuntu"):
    apt.update(name="Listes a jour", cache_time=3600, **SUDO)
    apt.packages(
        name="Paquets necessaires au userland",
        packages=["curl", "git", "openssh", "unzip", "fontconfig"],
        update=True,
        **SUDO,
    )
else:
    server.shell(
        name="Distribution non gereee par l'atelier",
        commands="echo 'ajoute ta famille de paquets ici' ",
    )

# --- 2. dotfiles -------------------------------------------------------------
# Sur une vraie machine: liens vers le repo clone (editable, versionne).
# Dans le conteneur jetable: le repo n'existe pas, on pousse les fichiers.
# Meme source, deux transports: c'est un classique.
FICHIERS = [
    (f"{DOTFILES}/vimrc", f"{HOME}/.vimrc"),
    (f"{DOTFILES}/starship.toml", f"{HOME}/.config/starship.toml"),
    (f"{DOTFILES}/fish-config.fish", f"{HOME}/.config/fish/config.fish"),
    (f"{ICI}/config/mise.toml", f"{HOME}/.config/mise/config.toml"),
]
for src, dest in FICHIERS:
    if EN_CONTENEUR:
        files.put(name=f"Pousse {dest}", src=src, dest=dest)
    else:
        files.link(name=f"Lien {dest}", path=dest, target=src, force=True)

files.template(
    name="gitconfig",
    src=f"{DOTFILES}/gitconfig.j2",
    dest=f"{HOME}/.gitconfig",
    nom=os.environ.get("GIT_NAME", "Ada Lovelace"),
    email=os.environ.get("GIT_EMAIL", "ada@example.com"),
)

# --- 3. detection du shell ----------------------------------------------------
users = host.get_fact(Users)
trouve = next((n for n, d in users.items() if d["home"] == HOME), None)
SHELL = os.environ.get("PYCONFR_SHELL") or (
    users[trouve]["shell"] if trouve else "/bin/sh"
)
BASE_SHELL = os.path.basename(SHELL)

if BASE_SHELL == "fish":
    RC = f"{HOME}/.config/fish/config.fish"
    LIGNE_PATH = "fish_add_path -g ~/.local/bin ~/.local/share/mise/shims"
    LIGNE_MISE = "mise activate fish | source"
    LIGNE_STARSHIP = "starship init fish | source"
else:
    RC = {"bash": f"{HOME}/.bashrc", "zsh": f"{HOME}/.zshrc"}.get(
        BASE_SHELL, f"{HOME}/.profile"
    )
    LIGNE_PATH = 'export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$PATH"'
    LIGNE_MISE = 'eval "$(mise activate {0})"'.format(BASE_SHELL)
    LIGNE_STARSHIP = 'eval "$(starship init {0})"'.format(BASE_SHELL)

# --- 4. userland ----------------------------------------------------------------
files.directory(path=BIN)
files.directory(path=CACHE)
files.directory(path=FONTS)
files.directory(path=f"{HOME}/.config/mise")
files.directory(path=f"{HOME}/.ssh", mode=700)

if host.get_fact(File, path=f"{BIN}/mise") is None:
    server.shell(
        name=f"Installe mise {MISE_VERSION}",
        # telecharge puis execute: curl|sh masquerait un echec de curl.
        commands="export HOME={0} XDG_CONFIG_HOME={0}/.config XDG_DATA_HOME={0}/.local/share; curl -fsSL https://mise.run -o {1}/mise-install.sh && MISE_VERSION={2} sh {1}/mise-install.sh".format(
            HOME, CACHE, MISE_VERSION
        ),
    )

CIBLE_STARSHIP = {
    ("Linux", "aarch64"): "starship-aarch64-unknown-linux-musl",
    ("Linux", "x86_64"): "starship-x86_64-unknown-linux-musl",
    ("Darwin", "arm64"): "starship-aarch64-apple-darwin",
    ("Darwin", "aarch64"): "starship-aarch64-apple-darwin",
    ("Darwin", "x86_64"): "starship-x86_64-apple-darwin",
}.get((OS, ARCH))
if CIBLE_STARSHIP and host.get_fact(File, path=f"{BIN}/starship") is None:
    archive = f"{CACHE}/{CIBLE_STARSHIP}.tar.gz"
    files.download(
        name=f"Telecharge starship {STARSHIP_VERSION}",
        src="https://github.com/starship/starship/releases/download/{0}/{1}.tar.gz".format(
            STARSHIP_VERSION, CIBLE_STARSHIP
        ),
        dest=archive,
    )
    files.unarchive(
        name="Extrait starship",
        src=archive,
        dest=BIN,
        remote_src=True,
        creates=f"{BIN}/starship",
    )

files.directory(name="Repertoire du rc", path=os.path.dirname(RC))
if host.get_fact(File, path=RC) is None:
    files.put(name="Cree le rc", src=io.StringIO(""), dest=RC)
for ligne in (LIGNE_PATH, LIGNE_MISE, LIGNE_STARSHIP):
    files.line(path=RC, line=ligne, ensure_newline=True)

if OS == "Linux":
    ZIP = f"{CACHE}/JetBrainsMono.zip"
    files.download(
        name="Telecharge JetBrainsMono NF",
        src="https://github.com/ryanoasis/nerd-fonts/releases/download/{0}/JetBrainsMono.zip".format(
            NERD_FONTS_VERSION
        ),
        dest=ZIP,
    )
    files.unarchive(
        name="Extrait les polices",
        src=ZIP,
        dest=FONTS,
        remote_src=True,
        creates=f"{FONTS}/JetBrainsMonoNerdFont-Regular.ttf",
    )
    server.shell(
        name="Recharge le cache des polices",
        commands="fc-cache -f {0}".format(FONTS),
    )

CLE = f"{HOME}/.ssh/id_ed25519"
if host.get_fact(File, path=CLE) is None:
    server.shell(
        name="Cree la cle ed25519 (jetable: sans passphrase)",
        commands="ssh-keygen -t ed25519 -f {0} -N '' -C 'atelier-pyconfr'".format(CLE),
    )

server.shell(
    name="Installe les outils (mise install)",
    commands="export HOME={0} XDG_CONFIG_HOME={0}/.config XDG_DATA_HOME={0}/.local/share; {1}/mise trust {0}/.config/mise/config.toml && {1}/mise install".format(
        HOME, BIN
    ),
)

# --- 5. verification (meme run: c'est le dernier etat du conteneur) -------------
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
    commands='test "$(stat -c %a {0}/.ssh 2>/dev/null || stat -f %A {0}/.ssh)" = 700'.format(
        HOME
    ),
)
