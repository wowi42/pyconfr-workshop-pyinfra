# ex04: le userland complet

Objectif: tout ce qui fait TON environnement, sans droits admin, tout dans
`$HOME`: gestionnaire de versions (mise), prompt (starship), outils CLI,
polices, activation shell, cles SSH. Versions epinglees partout.

## Commandes

Faux home:

    PYCONFR_HOME=$PWD/faux-home pyinfra @local deploy.py --dry
    PYCONFR_HOME=$PWD/faux-home pyinfra @local deploy.py

Conteneur: `@docker/<image>` est sans etat (chaque run recree un conteneur
propre), curl, unzip et fontconfig installes par ex02 n'y survivent pas.
Ex04 n'y s'execute donc que via le deploy complet de la course
([restore.py](../solutions/course/restore.py)), systeme et userland dans le
meme run. En standalone, reste sur le faux home.

Demo de la detection de shell sur un faux home:

    PYCONFR_HOME=$PWD/faux-home PYCONFR_SHELL=fish pyinfra @local deploy.py

## TODO

3 marqueurs `TODO(atelier)` dans `deploy.py`: arborescences, starship,
polices.

## Questions en chemin

1. Comment le deploy sait-il quel fichier rc ecrire (bashrc, zshrc,
   config.fish)? Ouvre `~/.bashrc` (conteneur) ou `.profile` (faux home)
   et verifie les lignes ajoutees.
2. Pourquoi epingler MISE_VERSION et STARSHIP_VERSION? Que risque le
   script si starship sort une version cassee demain?
3. Les polices sont dans `~/.local/share/fonts`, pas dans
   `/usr/share/fonts`. Qui peut les lire? Qui peut les installer?
4. Où est la cle privee? Quels droits? Pourquoi `.ssh` en 700?

## Rappel securite

- L'atelier genere les cles SSH sans passphrase pour rester scriptable.
  En vraie vie: `ssh-keygen` interactif, avec passphrase.
- Les vrais secrets (tokens, mots de passe) n'ont rien a faire ici.
  Patterns possibles: variables d'environnement (ex03), ou sops/age pour
  chiffrer des fichiers de config avant de les versionner.

## Nettoyage

    rm -rf faux-home
    docker rm -f <nom-du-conteneur>
