# Rebuild ta machine en une commande

Atelier PyConFR: encoder toute sa machine en pyinfra, du systeme de base
jusqu'au prompt. Pur Python, versionne, rejouable. Le jour ou le disque
meurt, tu es la seule personne calme de la piece.

Disque mort, laptop perdu, nouvelle machine: combien de temps pour retrouver
TON environnement? Cet atelier repond: le temps d'un `git clone` et d'une
commande.

## Prerequis (a faire AVANT la session)

- Un laptop Linux (ou une VM), ou macOS avec Docker Desktop.
- Python 3.10+, git, curl, [uv](https://docs.astral.sh/uv/).
- Docker rootless (Linux) ou Docker Desktop (macOS). podman marche aussi
  avec le socket docker.
- Verifier: `sh kit/preflight.sh`. Zero ligne MANQUE.

## Installation (10 min, faites ensemble au debut)

Prerequis: [uv](https://docs.astral.sh/uv/) installe. Puis:

    uv venv .venv
    . .venv/bin/activate
    uv pip install -r requirements.txt
    pyinfra --version

## Principe

Deux phases, deux deploys:

1. **La base (root)**: paquets systeme, docker, creation de l'utilisateur.
   Une fois par machine, rarement.
2. **Le userland**: shell, prompt, outils, polices, configs, cles.
   Tout vit dans `$HOME`. C'est la partie que tu versions et que tu
   restaures chaque jour sans y penser.

Pour s'entrainer sans risque: des conteneurs jetables. Le connecteur
`@docker` est sans etat: chaque run repart d'un conteneur neuf, ce qui
rend l'entrainement sans consequence. On ecrit, on detruit, on restaure,
on recommence.

## Deroule (2h)

| Horaire | Module | Contenu |
|---|---|---|
| 00:00 | Accueil | preflight, install, sondage: "combien de temps pour retrouver ton env?" |
| 00:10 | Demo orateur | destruction d'un conteneur, restauration en une commande |
| 00:15 | [ex01](exercices/01-hello/) | pyinfra @local: dry run, operations, idempotence |
| 00:30 | [ex02](exercices/02-conteneur/) | @docker: conteneur jetable, facts, conditions |
| 00:50 | [ex00](exercices/00-base/) | la base en root: paquets, user, docker (guidé) |
| 01:05 | [ex03](exercices/03-dotfiles/) | dotfiles: symlinks, templates, git |
| 01:20 | [ex04](exercices/04-userland/) | userland: mise, starship, detection de shell, secrets |
| 01:40 | bootstrap | ecrire SON script de restauration en une commande |
| 01:50 | LA COURSE | detruire son environnement, le restaurer, chrono |
| 02:10 | Debrief | retours, questions, suite possible |

Si le groupe avance vite: fusionner ex02 et ex03, et doubler le temps de la
course. Si le groupe est lent: ex00 devient une demo commentee de 5 min par
l'orateur.

## Les exercices

Chaque `exercices/NN-*/deploy.py` contient des marqueurs `TODO(atelier)`.
Les versions completes et commentees sont dans `solutions/`. Elles ont ete
testees. Regarder la solution avant d'essayer, c'est se priver du sprint.

## La course (finale)

Consignes dans [exercices/05-course/](exercices/05-course/). En resume:
une seule commande relance [restore.py](solutions/course/restore.py),
qui recree tout depuis zero (le connecteur @docker est sans etat) et se
verifie dans le meme run. Le plus rapide gagne, le plus complet aussi.

## Regles de securite de l'atelier

1. Jamais de secret dans ce repo: ni cle, ni token, ni mot de passe,
   meme "juste un instant".
2. Les exercices 01, 03, 04 touchent uniquement `$HOME` (ou un faux home
   passe via `PYCONFR_HOME`). Le seul exercice root est ex00, et il vise
   une machine jetable.
3. Les vrais secrets passent par des variables d'environnement (voir ex03)
   ou par sops/age (pointe en fin d'ex04).
4. Cles SSH: une passphrase en vraie vie. L'atelier les genere sans
   passphrase pour rester scriptable, elles sont jetables.
5. `.env` est dans le `.gitignore`. Verifie `git status` avant chaque
   commit.

## Structure du repo

    kit/                 preflight.sh + triche.md (aide-memoire)
    exercices/           les 5 modules, avec TODO
    solutions/           versions completes testees + course/restore.py
                         (le deploy complet de la course) + bootstrap.sh
    exemple-orateur/     les deploys de la demo, utilisables comme base

## Apres l'atelier

Prends 30 minutes pour remplacer le contenu des exercices par TES configs
(reelles dotfiles, TON liste d'outils, TON shell). Puis pousse tout dans un
repo prive. C'est ca, l'exercice final.
