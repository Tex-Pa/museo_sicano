import sqlite3

# --- 1. FUNZIONE PER CREARE IL DATABASE ---
def crea_tabella_utenti():
    try:
        # Il timeout di 10 secondi aiuta a prevenire il "database is locked"
        with sqlite3.connect('museo_sicano.db', timeout=10) as conn:
            cursor = conn.cursor()
            
            # Creiamo la tabella (se non esiste già)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS utenti (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    cognome TEXT,
                    data_nascita TEXT,
                    email TEXT UNIQUE,
                    password TEXT,
                    nazionalita TEXT,
                    regione TEXT,
                    citta TEXT,
                    ruolo TEXT,
                    termini_accettati BOOLEAN
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"Errore durante la creazione della tabella: {e}")

# --- 2. FUNZIONE PER SALVARE L'UTENTE ---
def salva_nuovo_utente(utente_oggetto):
    try:
        # Usando 'with', la connessione si chiude AUTOMATICAMENTE anche in caso di errore
        with sqlite3.connect('museo_sicano.db', timeout=10) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO utenti (
                    nome, cognome, data_nascita, email, password, 
                    nazionalita, regione, citta, ruolo, termini_accettati
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                utente_oggetto.nome,
                utente_oggetto.cognome,
                utente_oggetto.data_nascita,
                utente_oggetto.email,
                utente_oggetto.password,
                utente_oggetto.nazionalita,
                utente_oggetto.regione,
                utente_oggetto.citta,
                utente_oggetto.ruolo,
                utente_oggetto.termini_accettati
            ))
            
            conn.commit()
            print(f"--- DATABASE: Utente {utente_oggetto.email} salvato correttamente! ---")
            
    except sqlite3.IntegrityError:
        print(f"ERRORE: L'email {utente_oggetto.email} è già presente nel database!")
    except sqlite3.Error as e:
        print(f"ERRORE DATABASE: {e}")

def login_utente(email, password_da_controllare):
    try:
        with sqlite3.connect('museo_sicano.db', timeout=10) as conn:
            # Questa riga serve per poter usare i nomi delle colonne (es. utente['nome'])
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            
            # Cerchiamo l'utente per email
            cursor.execute("SELECT * FROM utenti WHERE email = ?", (email.lower().strip(),))
            utente = cursor.fetchone()
            
            if utente:
                # Controlliamo se la password nel database coincide con quella inserita
                if utente['password'] == password_da_controllare:
                    return utente 
            return None
    except sqlite3.Error as e:
        print(f"Errore durante il login: {e}")
        return None
    
def crea_tabella_codici():
    import sqlite3
    with sqlite3.connect('museo_sicano.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS codici_attivazione (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codice TEXT UNIQUE NOT NULL,
                ruolo_destinato TEXT NOT NULL, -- 'Operatore' o 'Amministratore'
                usato_da TEXT,                 -- Email dell'utente che lo usa
                stato TEXT DEFAULT 'Attivo'    -- 'Attivo' o 'Esaurito'
            )
        ''')
        conn.commit()

def elimina_scheda_db(id_scheda):
    import sqlite3
    try:
        with sqlite3.connect('museo_sicano.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM schede WHERE id = ?', (id_scheda,))
            conn.commit()
            return True
    except Exception as e:
        print(f"Errore eliminazione: {e}")
        return False

def aggiorna_scheda_db(id_scheda, dati):
    import sqlite3
    try:
        with sqlite3.connect('museo_sicano.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE schede SET 
                titolo=?, categoria=?, descrizione=?, epoca_risalenza=?, materiale_tecnica=?
                WHERE id = ?
            ''', (dati['titolo'], dati['categoria'], dati['descrizione'], 
                  dati['epoca'], dati['materiale'], id_scheda))
            conn.commit()
            return True
    except Exception as e:
        print(f"Errore aggiornamento: {e}")
        return False