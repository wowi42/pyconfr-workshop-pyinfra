# ex03: dotfiles

Objectif: tes configs vivent dans un repo, `$HOME` ne contient que des
liens. Un changement de machine = un `git clone` + un deploy.

## Commandes

Faux home (recommande pour l'atelier):

    PYCONFR_HOME=$PWD/faux-home pyinfra @local deploy.py --dry
    PYCONFR_HOME=$PWD/faux-home pyinfra @local deploy.py

Ton vrai home, quand tu es pret:

    pyinfra @local deploy.py

Identite git injectee par l'environnement (pas de secret dans le repo):

    GIT_NAME="Ton Nom" GIT_EMAIL="toi@example.com" pyinfra @local deploy.py

## TODO

2 marqueurs `TODO(atelier)` dans `deploy.py`: la boucle de liens et le
template gitconfig (le bonus `git.repo` reste en commentaire).

## Questions en chemin

1. Pourquoi des liens symboliques plutot que des copies? (indice: que
   vois-tu quand tu edites ~/.vimrc?)
2. Où sont passes le nom et l'email dans le gitconfig? Que se passe-t-il
   sans les variables d'environnement?
3. `force=True` sur les liens: quand est-ce indispensable?

## Nettoyage

    rm -rf faux-home
