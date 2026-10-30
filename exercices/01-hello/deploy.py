"""
ex01: premier deploy, local, isole dans ~/pyconfr-test.

    pyinfra @local deploy.py --dry
    pyinfra @local deploy.py
"""

import os

from pyinfra import host
from pyinfra.facts.server import Arch, Hostname, Os
from pyinfra.operations import files, server

HOME = os.environ.get("PYCONFR_HOME") or os.path.expanduser("~")
TEST = f"{HOME}/pyconfr-test"

print(f"Hote: {host.get_fact(Hostname)} / {host.get_fact(Os)} / {host.get_fact(Arch)}")

files.directory(name="Repertoire de test", path=TEST)

# TODO(atelier): ecris un fichier {TEST}/config.env contenant
#   export PYCONFR=2026
# (indice: files.put avec src=io.StringIO(...), pense a importer io)

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

# TODO(atelier): affiche le resultat (ls -la {TEST} + cat notes.txt)
# avec server.shell
