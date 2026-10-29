import hashlib
import os
import sqlite3
from datetime import datetime


# Exception de base pour toutes les erreurs liées au coffre.
class ErreurCoffre(Exception):
    pass


# Exception levée lorsque l'authentification échoue.
class AuthentificationEchouee(ErreurCoffre):
    pass


# Exception levée lorsqu'un utilisateur tente d'accéder à une donnée sans autorisation.
class AccesRefuse(ErreurCoffre):
    pass


# Exception levée lorsqu'une donnée reçue ou demandée est invalide.
class DonneeInvalide(ErreurCoffre):
    pass


# Classe principale qui gère les comptes, les secrets et les opérations dans la base SQLite.
class Coffre:
    # Initialise la connexion à la base de données et crée les tables nécessaires.
    def __init__(self, bd):
        self.bd = bd
        self.conn = sqlite3.connect(bd)
        self.cursor = self.conn.cursor()
        self.__init_db()

    # Crée les tables de la base SQLite si elles n'existent pas.
    def __init_db(self):
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS compte (
                matricule TEXT PRIMARY KEY,
                role TEXT,
                sel BLOB,
                empreinte BLOB,
                tentatives INTEGER DEFAULT 0,
                bloque INTEGER DEFAULT 0           
            )
            ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS secret (
                idSecret INTEGER PRIMARY KEY,
                typeSecret TEXT,
                dateDepot TEXT,
                valeur BLOB,
                idUtilisateur TEXT,
                FOREIGN KEY (idUtilisateur) REFERENCES compte(matricule)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS operation (
                idOperation INTEGER PRIMARY KEY,
                typeOperation TEXT,
                idUtilisateur TEXT,
                idSecret TEXT,
                date TEXT
            )
        ''')

        self.conn.commit()

    # Crée un nouveau compte avec un matricule, un mot de passe et un rôle.
    def creer_compte(self, matricule, mdp, role):
        if self.cursor.execute(
            'SELECT * FROM compte WHERE matricule = ?',
            (matricule,)
        ).fetchone():

            raise DonneeInvalide(
                f"Compte déjà existant pour le matricule {matricule}"
            )

        sel = os.urandom(16)

        empreinte = hashlib.pbkdf2_hmac(
            'sha256',
            mdp.encode(),
            sel,
            100000
        )

        self.cursor.execute(
            'INSERT INTO compte (matricule, role, sel, empreinte) VALUES (?, ?, ?, ?)',
            (matricule, role, sel, empreinte)
        )

        self.conn.commit()

    # Ouvre une session si le matricule et le mot de passe sont corrects.
    # Si le compte est bloqué ou si le mot de passe est faux, une erreur est levée.
    def ouvrir_session(self, matricule, mdp):

        compte = self.cursor.execute(
            '''
            SELECT matricule, role, sel, empreinte,
                tentatives, bloque
            FROM compte
            WHERE matricule = ?
            ''',
            (matricule,)
        ).fetchone()

        if not compte:
            raise AuthentificationEchouee(
                "Mot de passe incorrect"
            )

        if compte[5] == 1:
            raise AuthentificationEchouee(
                "Compte bloqué après 3 tentatives."
            )

        if not self.__verifier_mdp(compte, mdp):

            tentatives = compte[4] + 1

            bloque = 1 if tentatives >= 3 else 0

            self.cursor.execute(
                '''
                UPDATE compte
                SET tentatives = ?, bloque = ?
                WHERE matricule = ?
                ''',
                (
                    tentatives,
                    bloque,
                    matricule
                )
            )

            self.conn.commit()

            raise AuthentificationEchouee(
                "Mot de passe incorrect"
            )

        self.cursor.execute(
            '''
            UPDATE compte
            SET tentatives = 0
            WHERE matricule = ?
            ''',
            (matricule,)
        )

        self.conn.commit()

        return {
            "matricule": compte[0],
            "role": compte[1]
        }

    # Vérifie si le mot de passe saisi correspond à l'empreinte enregistrée.
    def __verifier_mdp(self, compte, mdp):

        return hashlib.pbkdf2_hmac(
            'sha256',
            mdp.encode(),
            compte[2],
            100000
        ) == compte[3]

    # ----------- CORRECTION -----------

    # Ajoute un secret pour un utilisateur et enregistre cette action dans le journal.
    def ajouter_secret(self, session, typeSecret, dateDepot, valeur):

        self.cursor.execute(
            '''
            INSERT INTO secret
            (typeSecret, dateDepot, valeur, idUtilisateur)
            VALUES (?, ?, ?, ?)
            ''',
            (
                typeSecret,
                dateDepot,
                valeur.encode().hex(),
                session["matricule"]
            )
        )

        idSecret = self.cursor.lastrowid

        self.cursor.execute(
            '''
            INSERT INTO operation
            (typeOperation, idUtilisateur, idSecret, date)
            VALUES (?, ?, ?, ?)
            ''',
            (
                "Ajout",
                session["matricule"],
                idSecret,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        self.conn.commit()

        return idSecret

    # ----------- FIN CORRECTION -----------

    # Supprime un secret existant seulement s'il appartient bien à l'utilisateur indiqué.
    def retirer_secret(self, session, idSecret):

        matricule = session["matricule"]

        secret = self.cursor.execute(
            '''
            SELECT idSecret
            FROM secret
            WHERE idSecret = ?
            AND idUtilisateur = ?
            ''',
            (idSecret, matricule)
        ).fetchone()

        if not secret:
            raise DonneeInvalide(
                f"Secret non trouvé avec l'ID {idSecret}"
            )

        self.cursor.execute(
            'DELETE FROM secret WHERE idSecret = ?',
            (idSecret,)
        )

        self.cursor.execute(
            'DELETE FROM operation WHERE idSecret = ?',
            (idSecret,)
        )

        self.conn.commit()

    # Affiche la liste des secrets d'un utilisateur sans révéler leurs valeurs.
    def lister(self, session):

        matricule = session["matricule"]

        secrets = self.cursor.execute(
            '''
            SELECT idSecret, typeSecret, dateDepot
            FROM secret
            WHERE idUtilisateur = ?
            ''',
            (matricule,)
        ).fetchall()

        return [
            f"ID: {s[0]}, Type: {s[1]}, Date: {s[2]}"
            for s in secrets
        ]

    # Récupère la valeur d'un secret uniquement si l'utilisateur a bien accès à ce secret.
    def reveler(self, session, idSecret):

        if not isinstance(session, dict):
            raise AccesRefuse("Accès refusé")


        matricule = session["matricule"]

        secret = self.cursor.execute(
            '''
            SELECT valeur
            FROM secret
            WHERE idSecret = ?
            AND idUtilisateur = ?
            ''',
            (idSecret, matricule)
        ).fetchone()

        if not secret:
            raise AccesRefuse("Accès refusé")

        return bytes.fromhex(secret[0]).decode()

    # Affiche le journal des actions effectuées par un utilisateur.
    def journal(self, session):

        if session["role"] != "responsable":
            raise AccesRefuse("Accès refusé")

        operations = self.cursor.execute(
            '''
            SELECT typeOperation, date
            FROM operation
            '''
        ).fetchall()

        return [
            f"Type: {o[0]}, Date: {o[1]}"
            for o in operations
        ]

    # Ferme proprement la connexion à la base SQLite.
    def fermer(self):
        self.conn.close()

