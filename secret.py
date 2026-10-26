from abc import ABC, abstractmethod
from datetime import datetime

# Classe abstraite pour les secrets
class Secret(ABC):
    def __init__(self, idSecret, typeSecret, dateDepot):
        self.__idSecret = idSecret
        self.__typeSecret = typeSecret
        self.__dateDepot = dateDepot

    def get_id_secret(self):
        return self.__idSecret

    @abstractmethod
    def type_affiche(self):
        pass

    def apercu(self):
        return f"Type de secret : {self.__typeSecret}, Date de dépôt : {self.__dateDepot}"


# Sous-classes concrètes pour les types de secrets
class MotDePasse(Secret):
    def __init__(self, idSecret, typeSecret, dateDepot, valeur):
        super().__init__(idSecret, typeSecret, dateDepot)
        self.__valeur = valeur

    def type_affiche(self):
        return "Mot de passe"

    def consulter(self):
        return self.__valeur

    def modifier(self, nouvelle_valeur):
        self.__valeur = nouvelle_valeur


class CleAPI(Secret):
    def __init__(self, idSecret, typeSecret, dateDepot, valeur):
        super().__init__(idSecret, typeSecret, dateDepot)
        self.__valeur = valeur

    def type_affiche(self):
        return "Clé API"

    def consulter(self):
        return self.__valeur

    def modifier(self, nouvelle_valeur):
        self.__valeur = nouvelle_valeur


class NoteSecurisee(Secret):
    def __init__(self, idSecret, typeSecret, dateDepot, contenu):
        super().__init__(idSecret, typeSecret, dateDepot)
        self.__contenu = contenu

    def type_affiche(self):
        return "Note sécurisée"

    def consulter(self):
        return self.__contenu

    def modifier(self, nouveau_contenu):
        self.__contenu = nouveau_contenu


# Classe Utilisateur
class Utilisateur:
    def __init__(self, id, nom, email, mdp, role):
        self.id = id
        self.nom = nom
        self.email = email
        self.mdp = mdp
        self.role = role
        self.essais = 0

    def get_id(self):
        return self.id

    def seConnecter(self, mdp):
        if mdp == self.mdp:
            self.essais = 0
            return True
        else:
            self.essais += 1
            if self.essais >= 3:
                pass
            return False

    def seDeconnecter(self):
        self.essais = 0


# Classe Consultant
class Consultant(Utilisateur):
    def __init__(self, id, nom, email, mdp, matricule):
        super().__init__(id, nom, email, mdp, "consultant")
        self.matricule = matricule

    def deposerSecret(self, secret):
        pass

    def consulterSecret(self, idSecret):
        pass

    def modifierSecret(self, idSecret, nouveau_secret):
        pass

    def supprimerSecret(self, idSecret):
        pass


# Classe RespoSec
class RespoSec(Utilisateur):
    def __init__(self, id, nom, email, mdp, niveauAcces):
        super().__init__(id, nom, email, mdp, "responsable")
        self.niveauAcces = niveauAcces

    def consulterOperation(self, idOperation):
        pass

    def rechercherTrace(self, typeTrace):
        pass


# Classe CoffreFort
class CoffreFort:
    def __init__(self):
        self.utilisateurs = {}
        self.secrets = {}
        self.operations = []

    def ajouterSecret(self, utilisateur, secret):
        if utilisateur.get_id() not in self.utilisateurs:
            self.utilisateurs[utilisateur.get_id()] = utilisateur

        self.secrets[secret.get_id_secret()] = secret

        operation = Operation(
            len(self.operations) + 1,
            "Ajout",
            utilisateur.get_id(),
            secret.get_id_secret()
        )

        self.operations.append(operation)
        TraceAudit.enregistrer(operation)

    def retirerSecret(self, utilisateur, idSecret):
        if utilisateur.get_id() in self.utilisateurs and idSecret in self.secrets:

            del self.secrets[idSecret]

            operation = Operation(
                len(self.operations) + 1,
                "Retrait",
                utilisateur.get_id(),
                idSecret
            )

            self.operations.append(operation)
            TraceAudit.enregistrer(operation)

    def listerSecret(self, utilisateur):
        return list(self.secrets.values())


# Classe Operation
class Operation:
    def __init__(self, idOperation, typeOperation, idUtilisateur, idSecret=None):
        self.idOperation = idOperation
        self.typeOperation = typeOperation
        self.idUtilisateur = idUtilisateur
        self.idSecret = idSecret
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Classe TraceAudit
class TraceAudit:
    @staticmethod
    def enregistrer(operation):
        pass

    @staticmethod
    def afficher():
        pass


# Fonctions d'affichage (hors classes métier)
def afficher_message(message):
    print(message)


def afficher_secret(secret):
    print(secret.apercu())