import hashlib
import sqlite3

# --- 1. FUNZIONE PER PROTEGGERE LA PASSWORD ---
def cifra_password(password_chiara):
    """
    Trasforma la password in un hash SHA-256 a 64 caratteri.
    """
    if not password_chiara:
        return ""
    hash_object = hashlib.sha256(password_chiara.encode())
    return hash_object.hexdigest()

# --- 2. NUOVA FUNZIONE PER DECIDERE IL RUOLO (DINAMICA) ---
def controlla_ruolo(codice_inserito, email_utente=None):
    """
    Controlla se il codice inserito esiste nella tabella 'codici_attivazione'
    ed è ancora in stato 'Attivo'. Se valido, lo 'brucia' assegnandolo all'utente.
    """
    # Se l'utente non ha inserito alcun codice, è un semplice Abitante
    if not codice_inserito:
        return "Abitante"

    try:
        # Ci colleghiamo al database per cercare il codice
        with sqlite3.connect('museo_sicano.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Cerchiamo il codice nel database
            cursor.execute('''
                SELECT * FROM codici_attivazione 
                WHERE codice = ? AND stato = 'Attivo'
            ''', (codice_inserito,))
            
            riga = cursor.fetchone()

            if riga:
                # Il codice è valido! Recuperiamo il ruolo destinato (es. 'Operatore')
                ruolo_trovato = riga['ruolo_destinato']
                
                # AGGIORNAMENTO: Segniamo il codice come 'Esaurito' e lo leghiamo all'email
                cursor.execute('''
                    UPDATE codici_attivazione 
                    SET stato = 'Esaurito', usato_da = ? 
                    WHERE codice = ?
                ''', (email_utente, codice_inserito))
                
                conn.commit()
                print(f"DEBUG: Codice {codice_inserito} usato con successo da {email_utente}")
                return ruolo_trovato
            
            else:
                # Codice non trovato o già usato
                print(f"DEBUG: Tentativo fallito con codice errato o esaurito: {codice_inserito}")
                return "Abitante"

    except Exception as e:
        print(f"ERRORE critico durante il controllo ruolo: {e}")
        return "Abitante"