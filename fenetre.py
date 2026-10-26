import tkinter as tk
from tkinter import messagebox


# Classe qui représente la fenêtre principale de l'application.
# Elle permet à l'utilisateur de se connecter et d'afficher ses secrets.
class FenetreCoffre:

    # Initialise la fenêtre et les éléments graphiques.
    def __init__(self, coffre):

        self.coffre = coffre

        self.fenetre = tk.Tk()

        self.fenetre.title("Coffre")

        # Champ pour entrer le matricule.
        tk.Label(
            self.fenetre,
            text="Matricule"
        ).pack()

        self.matricule = tk.Entry(
            self.fenetre
        )
        self.matricule.pack()

        # Champ pour entrer le mot de passe, masqué par des astérisques.
        tk.Label(
            self.fenetre,
            text="Mot de passe"
        ).pack()

        self.mdp = tk.Entry(
            self.fenetre,
            show="*"
        )
        self.mdp.pack()

        # Bouton pour tenter la connexion.
        tk.Button(
            self.fenetre,
            text="Se connecter",
            command=self.connecter
        ).pack()

        # Liste qui affichera les secrets de l'utilisateur connecté.
        self.liste = tk.Listbox(
            self.fenetre
        )

        self.liste.pack(
            fill=tk.BOTH,
            expand=True
        )

    # Tente la connexion et affiche les secrets si l'authentification réussit.
    def connecter(self):

        try:

            # Vérifie le matricule et le mot de passe.
            jeton = self.coffre.ouvrir_session(
                self.matricule.get(),
                self.mdp.get()
            )

            print("JETON =", jeton)

            # Efface l'affichage avant de montrer les nouveaux secrets.
            self.liste.delete(0, tk.END)

            # Récupère la liste des secrets de l'utilisateur connecté.
            liste = self.coffre.lister(jeton)

            print("LISTE =", liste)

            # Affiche chaque secret dans la liste graphique.
            for secret in liste:
                self.liste.insert(tk.END, secret)

        except Exception as e:

            print("ERREUR =", e)

            # Affiche un message d'erreur si la connexion ou l'accès échoue.
            messagebox.showerror(
                "Erreur",
                str(e)
            )

    # Lance la boucle principale de la fenêtre Tkinter.
    def mainloop(self):
        self.fenetre.mainloop() 




# Importation de la classe Coffre depuis le fichier coffre.py.
from coffre import Coffre

# Crée une instance du coffre avec la base de données locale.
coffre = Coffre("coffre.db")

# Ouvre la fenêtre principale de l'application.
app = FenetreCoffre(coffre)
app.mainloop()