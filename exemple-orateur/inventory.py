# inventory.py: groupes de machines de l'orateur.
# Usage: pyinfra -i inventory.py <groupe> <deploy.py>
#
# Chaque variable liste definit un groupe du meme nom.

poste = [
    "@local",
]

# VM fraiche (multipass, virtualbox, cloud...). Adapte l'IP.
vm_neuve = [
    "@ssh:root@192.0.2.10",
]
