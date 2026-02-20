# Gérer son travail sur GitHub

## 1. Créer une branche pour sa tâche
Le travail sur la branche doit être limitée et doit concerner un seul thème. Ainsi, il est plus facile de faire des revues de code et de corriger les erreurs. De plus, cela facilite la fusion de la branche dans la branche principale (main) une fois que le travail est terminé.

### Le naming
1) Pour une fonctionnalité : `feature/nom-de-la-fonctionnalité`
2) Pour une correction de bug : `fix/description-du-bug`
3) Pour la documentation : `doc/description-de-la-documentation`
4) Pour les tests : `test/description-des-tests`

## 2. Faire des commits réguliers
Il est important de faire des commits réguliers pour suivre l'évolution de votre travail et faciliter la collaboration avec les autres membres de l'équipe. Chaque commit doit être accompagné d'un message clair et descriptif qui explique les changements apportés.

## 3. Pousser les changements sur GitHub
Une fois que vous avez fait des commits, vous devez pousser vos changements sur GitHub pour les partager avec les autres membres de l'équipe. Utilisez la commande `git push` pour envoyer vos changements vers la branche correspondante sur GitHub.

## 4. Créer une Pull Request (PR)
Une fois que vous avez poussé vos changements sur GitHub, vous pouvez créer une Pull Request (PR) pour demander à ce que vos changements soient fusionnés dans la branche principale (main). Une fois la PR créée et prise en compte, une CI/CD se lancera. Cette CI/CD exécutera les tests automatisés pour vérifier que les changements n'introduisent pas de bugs ou de régressions. Si les tests passent avec succès, la PR peut être fusionnée dans la branche principale (main). Si les tests échouent, vous devrez corriger les erreurs et pousser à nouveau vos changements pour que la CI/CD puisse les vérifier à nouveau.