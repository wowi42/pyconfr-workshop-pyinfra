# ex00: la base, en root

Objectif: preparer une machine fraiche. Paquets systeme, utilisateur
principal, docker. C'est la seule partie avec des droits admin, et on la
lance rarement (machine neuve, gros changement de config systeme).

## Dans l'atelier

On cible un conteneur Ubuntu. On y est deja root, le deploy le detecte
tout seul (fact `/.dockerenv`) et ne passe pas par sudo:

    pyinfra @docker/archlinux:latest deploy.py --dry
    pyinfra @docker/archlinux:latest deploy.py -y

## Sur une vraie machine fraiche (VM, pret pour la course finale)

Copier le deploy sur la machine (ou la viser en SSH), puis:

Sur Mac ARM (pas d'image archlinux/arm64), ajouter la plateforme:

    pyinfra @docker/archlinux:latest --data docker_platform=linux/amd64 deploy.py -y

    pyinfra @local deploy.py --sudo

Le flag `--sudo` sert a toutes les operations; dans le conteneur il n'est
pas necessaire et le deploy s'en passe grace au fact `/.dockerenv`.

## Questions en chemin

1. Pourquoi `apt.update` avant `apt.packages`? Que fait `cache_time`?
2. Que se passe-t-il dans un conteneur simple (sans systemd) pour la
   partie docker? Comment le deploy le sait-il?
3. Le 2e run est-il idempotent? Teste.

## TODO

5 marqueurs `TODO(atelier)` dans `deploy.py` (dont le contournement du
sandbox pacman en conteneur).

## Nettoyage

    docker ps -a
    docker rm -f <nom-du-conteneur>
