# ex02: la cible devient jetable

Objectif: meme outil, autre connecteur. pyinfra cree un conteneur a partir
d'une image, y installe python3 tout seul, et execute le deploy dedans.
Quand on a fini, on jette. C'est la boucle de travail de l'atelier:
ecris, detruis, restaure, recommence.

## Commandes

    pyinfra @docker/archlinux:latest deploy.py --dry
    pyinfra @docker/archlinux:latest deploy.py -y

Sur Mac ARM (pas d'image archlinux/arm64), forcer la plateforme:

    pyinfra @docker/archlinux:latest --data docker_platform=linux/amd64 deploy.py -y

Detruire:

    docker ps -a                          # trouve le nom du conteneur
    docker rm -f <nom-du-conteneur>

Note: la premiere execution peut builder une image derivee (python3
ajoute). C'est le connecteur qui s'en charge.

ATTENTION: `@docker/<image>` est SANS ETAT. Chaque run recree un conteneur
propre depuis l'image, execute, sauvegarde en image, puis supprime le
conteneur. Ne cherche pas a "continuer" dans le conteneur d'un run
precedent: tout ce qui doit exister a la fin doit etre dans LE deploy.
C'est la propriete qui rend la course finale possible.

## TODO

3 marqueurs `TODO(atelier)` dans `deploy.py`.

## Questions en chemin

1. Le deploy installe unzip et fontconfig. A quoi vont-ils servir en
   ex04? (reponse: polices)
2. Le `if` sur le fact `LinuxName`: que se passe-t-il sur ta machine
   locale? Et dans le conteneur?
3. Le run d'apres: pourquoi tout est re-cree? Que signifie "sans etat"
   pour un outil de test? (indice: c'est la propriete qui rend la course
   finale possible)
