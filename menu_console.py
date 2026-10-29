from coffre import Coffre


# Classe qui gère le menu principal de l'application en console.
# Elle permet de créer un compte, de se connecter et de quitter le programme.
class MenuConsole:

    # Initialise le menu avec l'objet coffre utilisé pour les opérations.
    def __init__(self, coffre):
        self.coffre = coffre

    # Affiche le menu principal et traite les choix de l'utilisateur.
    def demarrer(self):

        while True:

            print("\n=== COFFRE FORT ===")
            print("1. Créer un compte")
            print("2. Se connecter")
            print("3. Quitter")

            choix = input("> ")

            try:

                # Crée un nouveau compte utilisateur.
                if choix == "1":

                    matricule = input("Matricule : ")
                    motdepasse = input("Mot de passe : ")
                    role = input("Rôle (consultant/responsable) : ")

                    self.coffre.creer_compte(
                        matricule,
                        motdepasse,
                        role
                    )

                    print("Compte créé avec succès.")

                # Ouvre une session si les identifiants sont corrects.
                elif choix == "2":

                    matricule = input("Matricule : ")
                    motdepasse = input("Mot de passe : ")

                    session = self.coffre.ouvrir_session(
                        matricule,
                        motdepasse
                    )

                    print(f"\nConnexion réussie : {session['matricule']}")
                    print(f"Rôle : {session['role']}")

                    self.menu_session(session)

                # Ferme la base de données et quitte le programme.
                elif choix == "3":

                    self.coffre.fermer()
                    break

                # Affiche un message si le choix n'est pas reconnu.
                else:

                    print("Choix invalide.")

            except Exception as e:

                print("Erreur :", e)

    # Affiche le menu de session après une connexion réussie.
    def menu_session(self, session):

        while True:

            print("\n=== SESSION OUVERTE ===")
            print("1. Ajouter un secret")
            print("2. Lister mes secrets")
            print("3. Révéler un secret")
            print("4. Consulter le journal")
            print("5. Fermer la session")

            choix = input("> ")

            try:

                # Ajoute un secret selon son type choisi par l'utilisateur.
                if choix == "1":

                    print("\nType de secret")
                    print("1. Mot de passe")
                    print("2. Clé API")
                    print("3. Note sécurisée")

                    type_choix = input("> ")

                    if type_choix == "1":
                        type_secret = "MotDePasse"

                    elif type_choix == "2":
                        type_secret = "CleAPI"

                    elif type_choix == "3":
                        type_secret = "NoteSecurisee"

                    else:
                        print("Type invalide.")
                        continue

                    valeur = input("Valeur du secret : ")

                    identifiant = self.coffre.ajouter_secret(
                        session,
                        type_secret,
                        "2026-10-25",
                        valeur
                    )

                    print(
                        f"Secret ajouté (ID {identifiant})"
                    )

                # Affiche les secrets enregistrés pour l'utilisateur connecté.
                elif choix == "2":

                    secrets = self.coffre.lister(
                        session
                    )

                    print("\n=== MES SECRETS ===")

                    if not secrets:

                        print(
                            "Aucun secret enregistré."
                        )

                    else:

                        for secret in secrets:
                            print(secret)

                # Affiche le contenu d'un secret sélectionné par son identifiant.
                elif choix == "3":

                    id_secret = int(
                        input("ID du secret : ")
                    )

                    valeur = self.coffre.reveler(
                        session,
                        id_secret
                    )

                    print("\n=== SECRET ===")
                    print(valeur)

                # Affiche le journal des actions si l'utilisateur est responsable.
                elif choix == "4":

                    journal = self.coffre.journal(
                        session
                    )

                    print("\n=== JOURNAL ===")

                    for ligne in journal:
                        print(ligne)

                # Ferme la session active et retourne au menu principal.
                elif choix == "5":

                    print("Session fermée.")
                    return

                # Affiche un message si le choix est invalide.
                else:

                    print("Choix invalide.")

            except Exception as e:

                print("Erreur :", e)


# Crée une instance du coffre pour la base de données locale.
coffre = Coffre("coffre.db")

# Démarre le menu de l'application en console.
menu = MenuConsole(coffre)
menu.demarrer()