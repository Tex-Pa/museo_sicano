import sqlite3

def crea_tabella_schede():
    with sqlite3.connect('museo_sicano.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schede (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titolo TEXT, categoria TEXT, descrizione TEXT, luogo_ritrovamento TEXT,
                autore_email TEXT, codice_museo TEXT, codice_soprintendenza TEXT,
                codice_iccd TEXT, ente_custode TEXT, collocazione_attuale TEXT,
                epoca_risalenza TEXT, materiale_tecnica TEXT, dimensioni TEXT,
                stato_conservazione TEXT, coordinate_gps TEXT, foto_path TEXT,
                note_storiche TEXT, stato_approvazione TEXT DEFAULT 'In attesa'
            )
        ''')

def salva_nuova_scheda(dati):
    import sqlite3
    with sqlite3.connect('museo_sicano.db') as conn:
        cursor = conn.cursor()
        # Abbiamo aggiunto 'stato_approvazione' alla lista delle colonne
        # e un '?' in più nei VALUES
        query = '''INSERT INTO schede (
                        titolo, categoria, descrizione, luogo_ritrovamento, 
                        autore_email, foto_path, stato_approvazione
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)'''
        
        # Inseriamo 'In attesa' come valore predefinito
        valori = (
            dati['titolo'], 
            dati['categoria'], 
            dati['descrizione'], 
            dati['luogo_ritrovamento'], 
            dati['autore_email'], 
            dati['foto_path'],
            'In attesa'  # <-- Questo è fondamentale!
        )
        
        cursor.execute(query, valori)
        conn.commit()
    return True

def ottieni_tutte_le_schede():
    import sqlite3
    with sqlite3.connect('museo_sicano.db') as conn:
        # Questa riga è FONDAMENTALE per poter usare s['stato_approvazione']
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM schede")
        rows = cursor.fetchall()
        # Trasformiamo in una lista di dizionari vera e propria
        return [dict(ix) for ix in rows]

def approva_scheda_db(id_scheda):
    with sqlite3.connect('museo_sicano.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE schede SET stato_approvazione = 'Approvata' WHERE id = ?", (id_scheda,))
        conn.commit()
    return True