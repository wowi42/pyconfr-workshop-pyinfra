# Aide-memoire pyinfra

## Lancer

    pyinfra @local deploy.py --dry    # preview: montre tout, n'execute rien
    pyinfra @local deploy.py          # execute (demande confirmation, -y pour zapper)
    pyinfra @docker/archlinux:latest deploy.py -y
    pyinfra @ssh:user@machine deploy.py
    pyinfra @local deploy.py --limit un-groupe     # filtre de l'inventaire

Toujours `--dry` d'abord. Toujours.

## Connecteurs

| Connecteur | Cible | Remarque |
|---|---|---|
| `@local` | la machine courante | pour tester en vrai |
| `@docker/<image>` | conteneur neuf a CHAQUE run | sans etat: parfait pour tester une restauration |
| `@docker/<image>` + `--data docker_platform=linux/amd64` | force la plateforme | utile sur Mac ARM (pas d'image archlinux/arm64) |
| `@docker/<id-conteneur>` | conteneur existant | avec etat, laisse tourner |
| `@ssh:user@hote` | machine distante | besoin de python3 cote cible |
| `@docker/<image>/pull_always` | force le re-pull | utile si l'image a change |

## Operations courantes

| Operation | Role | Idempotente? |
|---|---|---|
| `apt.packages(...)` / `apt.update(...)` | paquets Debian/Ubuntu | oui |
| `pacman.packages(...)` / `pacman.update(...)` | paquets Arch Linux | oui |
| `server.shell(commands=...)` | n'importe quelle commande | non: rejouee a chaque run |
| `server.user(user=..., shell=..., groups=..., append=True)` | comptes utilisateurs | oui |
| `files.directory(path=..., mode=...)` | repertoires | oui |
| `files.put(src=... ou src=io.StringIO(...), dest=...)` | fichier statique | oui |
| `files.template(src=..., dest=..., **variables)` | fichier jinja2 | oui |
| `files.link(path=..., target=..., force=True)` | symlinks | oui |
| `files.line(path=..., line=...)` | ligne presente dans un fichier | oui |
| `files.download(src=..., dest=...)` | telechargement (curl/wget distants) | oui |
| `files.unarchive(src=..., dest=..., remote_src=True, creates=...)` | extrait une archive distante | oui (avec `creates`) |
| `git.repo(src=..., dest=...)` | clone/pull | oui |
| `systemd.service(service=..., running=True, enabled=True)` | services | oui |

`server.shell` est la soupape de secours: pratique, mais rejouee a chaque
execution. Si une operation files.* fait le travail, prends-la.

## Facts courants (lecture seule de l'etat reel)

    host.get_fact(Os)                 # "Linux" / "Darwin" / ...
    host.get_fact(Arch)               # "aarch64" / "x86_64" / "arm64"
    host.get_fact(Hostname)
    host.get_fact(Home)               # $HOME de l'utilisateur courant cible
    host.get_fact(Users)["atelier"]["shell"]   # shell d'un utilisateur
    host.get_fact(File, path="...")   # None si absent, sinon metadonnees
    host.get_fact(Directory, path="...")       # pareil pour les repertoires
    host.get_fact(LinuxName)          # "Debian" / "Ubuntu" / ...

Les facts se lisent au moment ou le deploy est charge: tu peux faire des
`if` dessus pour brancher ton code.

## Regles de survie

1. Le deploy s'execute de haut en bas, dans l'ordre du fichier.
2. Tout ce qui touche a `$HOME` est userland. Rien au-dela.
3. Dans un conteneur on est root: pas de `_sudo`. Ailleurs: `_sudo=True`
   (ou le flag `--sudo` en CLI).
4. `--dry` avant chaque vrai run. Vraiment.
5. Un deploy doit pouvoir etre rejoue: 2e run = "No change" partout
   (sauf server.shell).
6. `curl ... | sh` masque les erreurs de curl (code de sortie = derniere
   commande du pipe). Telecharge puis execute: `curl -o f.sh && sh f.sh`.
7. Secrets: jamais dans le repo. Variables d'environnement ou sops/age.
