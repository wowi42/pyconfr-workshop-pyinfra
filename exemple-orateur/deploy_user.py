"""
Le userland de la machine de demo. Tout dans $HOME, rien de root ici.

    pyinfra @local deploy_user.py
"""

import io
import os

from pyinfra import host
from pyinfra.facts.files import File
from pyinfra.facts.server import Arch, Home, Os, Users
from pyinfra.operations import files, server

MISE_VERSION = "v2026.10.24"
STARSHIP_VERSION = "v1.27.0"
NERD_FONTS_VERSION = "v3.2.1"

HOME = os.environ.get("PYCONFR_HOME") or host.get_fact(Home)
BIN = f"{HOME}/.local/bin"
CACHE = f"{HOME}/.cache/atelier"
ICI = os.path.dirname(os.path.abspath(__file__))
DOTFILES = f"{ICI}/dotfiles"

OS = host.get_fact(Os)
ARCH = host.get_fact(Arch)

# --- detection du shell ------------------------------------------------------
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

# --- arborescences -----------------------------------------------------------
files.directory(path=BIN)
files.directory(path=CACHE)
files.directory(path=f"{HOME}/.local/share/fonts")
files.directory(path=f"{HOME}/.config/mise")
files.directory(path=f"{HOME}/.config/systemd/user")
files.directory(path=f"{HOME}/.ssh", mode=700)

# --- dotfiles: liens depuis le repo ------------------------------------------
LIENS = [
    (f"{HOME}/.vimrc", f"{DOTFILES}/vimrc"),
    (f"{HOME}/.config/starship.toml", f"{DOTFILES}/starship.toml"),
    (f"{HOME}/.config/fish/config.fish", f"{DOTFILES}/fish-config.fish"),
    (f"{HOME}/.config/mise/config.toml", f"{ICI}/config/mise.toml"),
]
for chemin, cible in LIENS:
    files.link(name=f"Lien {chemin}", path=chemin, target=cible, force=True)

files.template(
    name="gitconfig",
    src=f"{DOTFILES}/gitconfig.j2",
    dest=f"{HOME}/.gitconfig",
    nom=os.environ.get("GIT_NAME", "Ada Lovelace"),
    email=os.environ.get("GIT_EMAIL", "ada@example.com"),
)

# --- binaires epingles --------------------------------------------------------
if host.get_fact(File, path=f"{BIN}/mise") is None:
    server.shell(
        name=f"Installe mise {MISE_VERSION}",
        # Pipe a eviter: si curl echoue, sh recoit un script vide et
        # reussit quand meme (le exit code vient de la derniere commande).
        # On telecharge d'abord, on execute ensuite.
        commands="export HOME={0} XDG_CONFIG_HOME={0}/.config XDG_DATA_HOME={0}/.local/share; curl -fsSL https://mise.run -o {2}/mise-install.sh && MISE_VERSION={1} sh {2}/mise-install.sh".format(
            HOME, MISE_VERSION, CACHE
        ),
    )

CIBLE_STARSHIP = {
    ("Linux", "aarch64"): "starship-aarch64-unknown-linux-musl",
    ("Darwin", "arm64"): "starship-aarch64-apple-darwin",
    ("Linux", "x86_64"): "starship-x86_64-unknown-linux-musl",
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

# --- activation shell ----------------------------------------------------------
files.directory(name="Repertoire du rc", path=os.path.dirname(RC))
if host.get_fact(File, path=RC) is None:
    files.put(name="Cree le rc", src=io.StringIO(""), dest=RC)
for ligne in (LIGNE_PATH, LIGNE_MISE, LIGNE_STARSHIP):
    files.line(path=RC, line=ligne, ensure_newline=True)

# --- polices --------------------------------------------------------------------
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
        dest=f"{HOME}/.local/share/fonts",
        remote_src=True,
        creates=f"{HOME}/.local/share/fonts/JetBrainsMonoNerdFont-Regular.ttf",
    )
    server.shell(
        name="Recharge le cache des polices",
        commands="fc-cache -f {0}/.local/share/fonts".format(HOME),
    )

# --- cle SSH ---------------------------------------------------------------------
CLE = f"{HOME}/.ssh/id_ed25519"
if host.get_fact(File, path=CLE) is None:
    server.shell(
        name="Cree la cle ed25519 (mettre une passphrase en vraie vie)",
        commands="ssh-keygen -t ed25519 -f {0} -N '' -C 'pyconfr-demo'".format(CLE),
    )

# --- outils via mise ---------------------------------------------------------------
server.shell(
    name="Installe les outils (mise install)",
    commands="export HOME={0} XDG_CONFIG_HOME={0}/.config XDG_DATA_HOME={0}/.local/share; {1}/mise trust {0}/.config/mise/config.toml && {1}/mise install".format(
        HOME, BIN
    ),
)

# --- service utilisateur (vraie machine uniquement, pas le conteneur) ---------------
UNIT = """[Unit]
Description=Demo service user pyinfra

[Service]
ExecStart=/bin/sh -c 'while true; do echo pyinfra-ok; sleep 60; done'

[Install]
WantedBy=default.target
"""
files.put(
    name="Unit systemd user",
    src=io.StringIO(UNIT),
    dest=f"{HOME}/.config/systemd/user/pyconfr-demo.service",
)
if host.get_fact(Directory, path="/run/systemd/system") and not os.environ.get(
    "PYCONFR_HOME"
):
    server.shell(
        name="Active le service user",
        commands="systemctl --user daemon-reload && systemctl --user enable --now pyconfr-demo.service",
    )
