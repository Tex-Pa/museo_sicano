from database.manager_users import login_utente

def autentica_e_indirizza(email, password):
    """
    Controlla le credenziali e restituisce i dati dell'utente 
    se corretti, altrimenti restituisce None.
    """
    # 1. Chiediamo al database se l'utente esiste
    utente_trovato = login_utente(email, password)
    
    if utente_trovato:
        # Trasformiamo i dati del database in un dizionario Python facile da usare
        dati_sessione = {
            "nome": utente_trovato["nome"],
            "ruolo": utente_trovato["ruolo"],
            "email": utente_trovato["email"]
        }
        return dati_sessione
    
    return None

def controllo_permessi(ruolo):
    """
    Restituisce cosa può fare l'utente in base al ruolo.
    """
    permessi = {
        "visualizza_info": True,  # Tutti possono vedere le info
        "crea_schede": False,
        "approva_schede": False,
        "gestisci_codici": False
    }
    
    if ruolo == "Amministratore":
        permessi["crea_schede"] = True
        permessi["approva_schede"] = True
        permessi["gestisci_codici"] = True
    elif ruolo == "Operatore":
        permessi["crea_schede"] = True
        
    return permessi