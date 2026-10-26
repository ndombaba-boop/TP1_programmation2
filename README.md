TP1 - Coffre-fort numérique


Description du projet
Ce projet consiste à développer un coffre-fort numérique permettant :

la création de comptes utilisateurs ;
l'authentification des utilisateurs ;
l'ajout de secrets ;
la consultation des secrets ;
la révélation d'un secret précis ;
la consultation d'un journal d'audit.
Le projet est développé en Python selon les principes de la programmation orientée objet.

Structure du projet
coffre.py
Contient :

la classe Coffre
les exceptions personnalisées :
ErreurCoffre
AuthentificationEchouee
AccesRefuse
DonneeInvalide
Cette classe représente le cœur du système.

secret.py
Contient :

la classe abstraite Secret
la classe MotDePasse
la classe CleAPI
la classe NoteSecurisee
la classe Utilisateur
menu_console.py
Interface en ligne de commande permettant :

de créer un compte ;
de se connecter ;
d'ajouter un secret ;
de consulter ses secrets ;
de révéler un secret ;
de consulter le journal ;
de fermer une session.
fenetre.py
Interface graphique réalisée avec Tkinter.

Elle permet :

la connexion d'un utilisateur ;
l'affichage des secrets associés.
Choix de conception
Utilisation d'une classe abstraite Secret.
Utilisation de l'héritage pour les différents types de secrets.
Encapsulation des données sensibles avec des attributs privés.
Séparation entre :
la logique métier ;
l'interface console ;
l'interface graphique.
Les mots de passe sont stockés sous forme d'empreintes (hash) avec un sel aléatoire.

Le compte est bloqué après trois tentatives d'authentification échouées.

Exécution
Interface console
python menu_console.py
Interface graphique
python fenetre.py
Utilisation de l'intelligence artificielle
Microsoft Copilot a été utilisé comme outil d'assistance pour :

l'explication de certaines consignes ;
la révision de portions de code ;
l'identification d'erreurs ;
l'aide à la conception orientée objet.
Toutes les décisions finales, les adaptations et les tests ont été réalisés .

Remarque
Le projet a été développé dans le cadre du cours Programmation .