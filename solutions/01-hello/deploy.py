"""
ex01 (solution): premier deploy, local, isole dans ~/pyconfr-test.
"""

import io
import os

from pyinfra import host
from pyinfra.facts.server import Arch, Hostname, Os
from pyinfra.operations import files, server

HOME = os.environ.get("PYCONFR_HOME") or os.path.expanduser("~")
TEST = f"{HOME}/pyconfr-test"

print(f"Hote: {host.get_fact(Hostname)} / {host.get_fact(Os)} / {host.get_fact(Arch)}")

files.directory(name="Repertoire de test", path=TEST)

files.put(
    name="Un fichier de config",
    src=io.StringIO("export PYCONFR=2026\n"),
    dest=f"{TEST}/config.env",
)

files.link(
    name="Lien symbolique vers config.env",
    path=f"{TEST}/config-lien",
    target=f"{TEST}/config.env",
)

files.line(
    name="Ajoute une ligne dans notes.txt",
    path=f"{TEST}/notes.txt",
    line="premier deploy pyinfra",
    ensure_newline=True,
)

server.shell(
    name="Montre le resultat",
    commands=f"ls -la {TEST} && cat {TEST}/notes.txt",
)
