# ex01: hello pyinfra

Objectif: premier contact. Un deploy local, isole dans `~/pyconfr-test`,
avec preview seche (`--dry`) et verification de l'idempotence.

## Commandes

    pyinfra @local deploy.py --dry    # lis tout ce qui SERA fait
    pyinfra @local deploy.py          # le fait vraiment
    pyinfra @local deploy.py          # relance: "No change" attendu partout

Pour travailler dans un faux home au lieu du vrai:

    PYCONFR_HOME=$PWD/faux-home pyinfra @local deploy.py

## TODO

2 marqueurs `TODO(atelier)` dans `deploy.py`.

## Questions en chemin

1. Quelle operation n'est PAS idempotente, et pourquoi?
2. Que se passe-t-il si tu relances? Pourquoi c'est la propriete la plus
   importante du repo?
3. Dans la sortie `--dry`, identifie les facts qui ont ete lus pour
   decider du "change / no change".

## Nettoyage

    rm -rf ~/pyconfr-test
