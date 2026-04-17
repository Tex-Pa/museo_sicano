from datetime import datetime

class User:
    # ATTENZIONE: __init__ deve avere DUE trattini bassi prima e dopo!
    def __init__(self, nome, cognome, data_nascita, sesso, email, password, 
                 nazionalita, regione, citta, termini_accettati, 
                 telefono=None, codice_operatore=None):
        
        # --- DATI ANAGRAFICI ---
        self.nome = nome
        self.cognome = cognome
        self.data_nascita = data_nascita
        self.sesso = sesso
        self.nazionalita = nazionalita
        self.regione = regione
        self.citta = citta
        
        # --- CREDENZIALI E CONTATTI ---
        self.email = email.lower().strip() 
        self.password = password            
        self.telefono = telefono            
        
        # --- SISTEMA E SICUREZZA ---
        self.codice_operatore = codice_operatore
        self.ruolo = "Utente"               
        self.is_active = False              
        self.termini_accettati = termini_accettati
        
        # --- DATI AUTOMATICI ---
        self.data_registrazione = datetime.now().strftime("%Y-%m-%d %H:%M:%S")