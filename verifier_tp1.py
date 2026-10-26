"""
420-PR2-AG — TP1 — Script de vérification

Usage :  python3 verifier_tp1.py coffre.py

Le fichier passé en argument doit exposer la classe Coffre et les quatre
exceptions du contrat. Le script n'inspecte jamais le code source : il ne
teste que des comportements observables.

Trois familles vérifiées :
  A. Conformité au contrat        (le reste n'est testable que si A passe)
  B. Injection SQL                 A03
  C. Stockage des authentifiants   A02
  D. Contrôle d'accès              A01
"""

import importlib.util
import os
import sys
import tempfile
import traceback

CHARGES = [
    "' OR '1'='1",
    "x' OR 1=1 --",
    "'; DROP TABLE compte; --",
    "\" OR \"\"=\"",
    "' UNION SELECT 1,2,3,4,5 --",
]

resultats = []


def verifier(famille, nom, condition, detail=""):
    resultats.append((famille, nom, bool(condition), detail))


def charger(chemin):
    spec = importlib.util.spec_from_file_location("remise", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(chemin_module):
    m = charger(chemin_module)

    for nom in ("Coffre", "ErreurCoffre", "AuthentificationEchouee",
                "AccesRefuse", "DonneeInvalide"):
        verifier("A", f"la classe {nom} est exposée", hasattr(m, nom))
    if not all(hasattr(m, n) for n in ("Coffre", "ErreurCoffre")):
        return afficher()

    Coffre = m.Coffre
    ErreurCoffre = m.ErreurCoffre
    AccesRefuse = getattr(m, "AccesRefuse", ErreurCoffre)
    AuthEchouee = getattr(m, "AuthentificationEchouee", ErreurCoffre)

    bd = tempfile.mktemp(suffix=".db")
    MDP_A = "MotDePasseAna1"
    MDP_B = "MotDePasseLuis1"
    VALEUR = "ValeurUltraSecrete2026"

    c = Coffre(bd)

    # ---------------------------------------------------------------- A
    try:
        c.creer_compte("2026001", MDP_A, "consultant")
        c.creer_compte("2026002", MDP_B, "consultant")
        c.creer_compte("2026003", "MotDePasseResp1", "responsable")
        verifier("A", "creer_compte accepte trois comptes valides", True)
    except Exception as e:
        verifier("A", "creer_compte accepte trois comptes valides", False, repr(e))
        return afficher()

    try:
        sa = c.ouvrir_session("2026001", MDP_A)
        sb = c.ouvrir_session("2026002", MDP_B)
        sr = c.ouvrir_session("2026003", "MotDePasseResp1")
        verifier("A", "ouvrir_session retourne un identifiant", bool(sa) and sa != sb)
    except Exception as e:
        verifier("A", "ouvrir_session retourne un identifiant", False, repr(e))
        return afficher()

    try:
        id_a = c.ajouter_secret(sa, "motdepasse", "Courriel client", VALEUR)
        c.ajouter_secret(sb, "cleapi", "Clé de test", "cle-de-luis")
        verifier("A", "ajouter_secret retourne un identifiant", id_a is not None)
    except Exception as e:
        verifier("A", "ajouter_secret retourne un identifiant", False, repr(e))
        return afficher()

    try:
        apercus = c.lister(sa)
        verifier("A", "lister retourne les secrets du propriétaire", len(apercus) == 1,
                 f"obtenu : {apercus}")
        verifier("C", "lister ne divulgue aucune valeur",
                 all(VALEUR not in str(a) for a in apercus), f"obtenu : {apercus}")
    except Exception as e:
        verifier("A", "lister retourne les secrets du propriétaire", False, repr(e))

    try:
        verifier("A", "reveler retourne la valeur au propriétaire",
                 c.reveler(sa, id_a) == VALEUR)
    except Exception as e:
        verifier("A", "reveler retourne la valeur au propriétaire", False, repr(e))

    try:
        verifier("A", "journal accessible au responsable", len(c.journal(sr)) > 0)
    except Exception as e:
        verifier("A", "journal accessible au responsable", False, repr(e))

    # ---------------------------------------------------------------- B
    for charge in CHARGES:
        try:
            c.ouvrir_session(charge, charge)
            ok, detail = False, "une session a été ouverte"
        except ErreurCoffre:
            ok, detail = True, ""
        except Exception as e:
            ok, detail = False, f"exception hors hiérarchie : {type(e).__name__}"
        verifier("B", f"ouvrir_session résiste à  {charge}", ok, detail)

    for charge in CHARGES[:3]:
        try:
            c.ajouter_secret(sa, "motdepasse", charge, "valeur")
            ok, detail = True, ""
        except ErreurCoffre:
            ok, detail = True, ""
        except Exception as e:
            ok, detail = False, f"exception hors hiérarchie : {type(e).__name__}"
        verifier("B", f"ajouter_secret résiste à  {charge[:22]}", ok, detail)

    for charge in ("1 OR 1=1", "1; DROP TABLE secret", "' OR '1'='1"):
        try:
            c.reveler(sa, charge)
            ok, detail = False, "une valeur a été retournée"
        except ErreurCoffre:
            ok, detail = True, ""
        except Exception as e:
            ok, detail = False, f"exception hors hiérarchie : {type(e).__name__}"
        verifier("B", f"reveler résiste à  {charge}", ok, detail)

    try:
        c.lister(sa)
        verifier("B", "les tables existent toujours après les charges utiles", True)
    except Exception as e:
        verifier("B", "les tables existent toujours après les charges utiles", False, repr(e))

    # ---------------------------------------------------------------- C
    c.creer_compte("2026004", MDP_A, "consultant")   # même mot de passe que 2026001
    try:
        c.fermer()
    except Exception:
        pass

    with open(bd, "rb") as f:
        octets = f.read()

    verifier("C", "le mot de passe maître n'est pas lisible dans la base",
             MDP_A.encode() not in octets)
    verifier("C", "la valeur du secret n'est pas lisible dans la base",
             VALEUR.encode() not in octets)

    import sqlite3
    con = sqlite3.connect(bd)
    try:
        lignes = con.execute(
            "SELECT matricule, sel, empreinte FROM compte "
            "WHERE matricule IN ('2026001','2026004')").fetchall()
        sels = {bytes(l[1]) for l in lignes}
        emp = {bytes(l[2]) for l in lignes}
        verifier("C", "deux comptes ont des sels distincts", len(sels) == 2)
        verifier("C", "deux mots de passe identiques donnent des empreintes distinctes",
                 len(emp) == 2)
    except Exception as e:
        verifier("C", "la table compte expose matricule, sel et empreinte", False, repr(e))
    con.close()

    # ---------------------------------------------------------------- D
    c2 = Coffre(bd)
    sa = c2.ouvrir_session("2026001", MDP_A)
    sb = c2.ouvrir_session("2026002", MDP_B)
    sr = c2.ouvrir_session("2026003", "MotDePasseResp1")

    try:
        c2.reveler(sb, id_a)
        verifier("D", "un consultant ne révèle pas le secret d'un autre", False,
                 "la valeur a été retournée")
    except AccesRefuse:
        verifier("D", "un consultant ne révèle pas le secret d'un autre", True)
    except ErreurCoffre:
        verifier("D", "un consultant ne révèle pas le secret d'un autre", True,
                 "refusé, mais pas par AccesRefuse")

    try:
        verifier("D", "lister ne montre que ses propres secrets",
                 all(str(id_a) not in a or "Courriel" not in a for a in c2.lister(sb)))
    except Exception as e:
        verifier("D", "lister ne montre que ses propres secrets", False, repr(e))

    try:
        c2.journal(sa)
        verifier("D", "un consultant n'accède pas au journal", False,
                 "le journal a été retourné")
    except AccesRefuse:
        verifier("D", "un consultant n'accède pas au journal", True)
    except ErreurCoffre:
        verifier("D", "un consultant n'accède pas au journal", True,
                 "refusé, mais pas par AccesRefuse")

    try:
        c2.reveler("jeton-de-session-invente", id_a)
        verifier("D", "une session inventée est refusée", False, "la valeur a été retournée")
    except ErreurCoffre:
        verifier("D", "une session inventée est refusée", True)
    except Exception as e:
        verifier("D", "une session inventée est refusée", False,
                 f"exception hors hiérarchie : {type(e).__name__}")

    for i in range(4):
        try:
            c2.ouvrir_session("2026002", "MauvaisMotDePasse9")
        except ErreurCoffre:
            pass
    try:
        c2.ouvrir_session("2026002", MDP_B)
        verifier("D", "le compte se bloque après 3 tentatives échouées", False,
                 "la session s'est ouverte malgré le blocage")
    except ErreurCoffre:
        verifier("D", "le compte se bloque après 3 tentatives échouées", True)

    try:
        verifier("D", "le responsable conserve l'accès au journal", len(c2.journal(sr)) > 0)
    except Exception as e:
        verifier("D", "le responsable conserve l'accès au journal", False, repr(e))

    c2.fermer()
    os.unlink(bd)
    afficher()


def afficher():
    titres = {"A": "A — Conformité au contrat", "B": "B — Injection SQL (A03)",
              "C": "C — Stockage des authentifiants (A02)",
              "D": "D — Contrôle d'accès (A01)"}
    total = reussis = 0
    for fam in ("A", "B", "C", "D"):
        lignes = [r for r in resultats if r[0] == fam]
        if not lignes:
            continue
        print(f"\n{titres[fam]}")
        for _, nom, ok, detail in lignes:
            total += 1
            reussis += ok
            marque = "RÉUSSI " if ok else "ÉCHOUÉ "
            print(f"  {marque} {nom}")
            if not ok and detail:
                print(f"           {detail}")
    print(f"\n{reussis} / {total} vérifications réussies")
    return 0 if reussis == total else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    try:
        sys.exit(main(sys.argv[1]) or 0)
    except Exception:
        traceback.print_exc()
        print("\nLe module n'a pas pu être chargé ou exécuté.")
        sys.exit(2)

