# Exemple orateur: la machine de la demo

Deux deploys, deux rythmes:

- `deploy_base.py` (root): rarement. Machine fraiche: paquets, docker,
  utilisateur. Lance avec `--sudo` en local ou contre une VM en `@ssh`.
- `deploy_user.py` (userland): tout le reste, quotidien, tout dans
  `$HOME`. C'est lui qui est versionne et rejoue chaque semaine.

## Usage

    pyinfra -i inventory.py vm_neuve deploy_base.py -y   # la base, sur la VM
    pyinfra -i inventory.py poste deploy_user.py -y      # le userland, chez toi

Ou directement sans inventaire:

    pyinfra @local deploy_user.py

La demo d'ouverture: `docker rm -f` du conteneur de test, puis
`./solutions/bootstrap.sh` (ou son equivalent perso) et tout revient.

Ce dossier est une BASE: remplace les listes par les tiennes. Ne pousse
jamais de secret ici (ni cle, ni token, ni mot de passe). Voir les regles
dans le README racine.
