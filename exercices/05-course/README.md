# ex05: LA COURSE

Objectif: prouver que ca marche. Chaque participant detruit son
environnement de test et le reconstruit en une seule commande. Chronometre.

## Le point cle appris en ex02

`@docker/<image>` est SANS ETAT: chaque run recree un conteneur propre,
execute, sauvegarde en image, supprime. Donc "detruire" est gratuit: le
run suivant repart de zero. Et tout ce qui doit exister a la fin doit etre
cree dans LE MEME run. C'est pour ca que la restauration tient en un seul
deploy: [solutions/course/restore.py](../solutions/course/restore.py).

## Scenario

1. **Detruire** (le "desastre"): rien a faire, le conteneur suivant sera
   neuf. Pour le spectacle: `docker rm -f <ton-conteneur>` quand meme.
2. **Restaurer** en une commande:

       GIT_NAME="Ton Nom" GIT_EMAIL="toi@example.com" \
           pyinfra @docker/archlinux:latest restore.py -y

Sur Mac ARM: `@docker/archlinux:latest --data docker_platform=linux/amd64`.

   (avec TON restore.py: le cours, enrichi de tes sections.)
3. **Verifier**: la verification est la derniere section de restore.py,
   elle tourne dans le meme run. `verify.py` reste utile pour le mode
   faux home (`@local`), lui persistant:

       PYCONFR_HOME=$PWD/faux-home pyinfra @local verify.py -y

Une erreur de check = erreur visible, points perdus.

## Barème

| Points | Critere |
|---|---|
| 1 | chaque check final qui passe (11 max) |
| 1 | restauration en une seule commande |
| 1 | versions epinglees dans le deploy (pas de latest) |
| 1 | aucun secret dans le repo (`git status` propre, pas de .env ajoute) |
| 1 | bonus creatif: service systemd --user, README de restauration, dry-run dans le bootstrap |

Classement: score d'abord, chrono en cas d'egalite. Le plus rapide gagne,
le plus complet aussi.

## bootstrap.sh attendu (contenu minimal)

- installer python + pyinfra (epingle)
- cloner/pull ton repo dotfiles
- lancer la base (root) si besoin, puis le userland
- etre relancable sans casse (`set -eu` gere)

Reference: [solutions/bootstrap.sh](../solutions/bootstrap.sh).
