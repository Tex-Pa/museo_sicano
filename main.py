import os
import random
import string
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

# Import dai tuoi moduli personalizzati
from models.users import User
from logic.auth_users import cifra_password, controlla_ruolo
from database.manager_users import crea_tabella_utenti, salva_nuovo_utente
from logic.login_manager import autentica_e_indirizza, controllo_permessi

# Import dal nuovo gestore schede
from database.manager_schede import (
    crea_tabella_schede, 
    salva_nuova_scheda, 
    ottieni_tutte_le_schede, 
    approva_scheda_db
)

app = Flask(__name__)
app.secret_key = "chiave_segreta_museo_sicano"

# --- CONFIGURAZIONE UPLOAD IMMAGINI ---
UPLOAD_FOLDER = 'static/uploads/schede'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- INIZIALIZZAZIONE DATABASE ---
crea_tabella_utenti()
crea_tabella_schede()

def inizializza_tabella_codici():
    with sqlite3.connect('museo_sicano.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS codici_attivazione (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codice TEXT UNIQUE NOT NULL,
                ruolo_destinato TEXT NOT NULL,
                usato_da TEXT,
                stato TEXT DEFAULT 'Attivo'
            )
        ''')
inizializza_tabella_codici()

# --- ROTTE DI AUTENTICAZIONE ---

@app.route('/')
def home():
    return render_template('registrazione.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password_cifrata = cifra_password(password)
        utente = autentica_e_indirizza(email, password_cifrata)
        
        if utente:
            session['utente_email'] = utente.get('email') 
            session['utente_nome'] = utente.get('nome')
            session['utente_cognome'] = utente.get('cognome', '') 
            session['utente_ruolo'] = utente.get('ruolo')
            return redirect(url_for('dashboard_ritorno'))
        else:
            return "Email o Password errati. <a href='/login'>Riprova</a>"
    return render_template('login.html')

@app.route('/registra', methods=['POST'])
def registra():
    nome = request.form.get('nome')
    cognome = request.form.get('cognome')
    email = request.form.get('email')
    password_scelta = request.form.get('password')
    codice_inserito = request.form.get('codice_op')
    
    password_sicura = cifra_password(password_scelta)
    ruolo_assegnato = controlla_ruolo(codice_inserito, email)
    
    nuovo_utente = User(
        nome=nome, cognome=cognome, data_nascita=request.form.get('nascita'),
        sesso="N/D", email=email, password=password_sicura,
        nazionalita=request.form.get('nazionalita'), regione=request.form.get('regione'),
        citta=request.form.get('citta'), termini_accettati=True
    )
    nuovo_utente.ruolo = ruolo_assegnato
    
    salva_nuovo_utente(nuovo_utente)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- ROTTE GESTIONE SCHEDE (OPERATORE/ADMIN) ---

@app.route('/nuova_scheda')
def visualizza_modulo_scheda():
    if 'utente_email' not in session:
        return redirect(url_for('login'))
    return render_template('crea_scheda.html')

@app.route('/salva-scheda', methods=['POST'])
def salva_scheda_elaborata():
    if 'utente_email' not in session:
        return redirect(url_for('login'))

    file = request.files.get('foto')
    filename = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    dati_scheda = {
        'titolo': request.form.get('titolo'),
        'categoria': request.form.get('categoria'),
        'descrizione': request.form.get('descrizione'),
        'luogo_ritrovamento': request.form.get('luogo_ritrovamento'),
        'autore_email': session.get('utente_email'),
        'codice_museo': request.form.get('codice_museo'),
        'codice_soprintendenza': request.form.get('codice_soprintendenza'),
        'codice_iccd': request.form.get('codice_iccd'),
        'ente_custode': request.form.get('ente_custode'),
        'collocazione_attuale': request.form.get('collocazione_attuale'),
        'epoca_risalenza': request.form.get('epoca_risalenza'),
        'materiale_tecnica': request.form.get('materiale_tecnica'),
        'dimensioni': request.form.get('dimensioni'),
        'stato_conservazione': request.form.get('stato_conservazione'),
        'coordinate_gps': request.form.get('coordinate_gps'),
        'note_storiche': request.form.get('note_storiche'),
        'foto_path': filename
    }

    if salva_nuova_scheda(dati_scheda):
        return "Scheda salvata con successo! <a href='/dashboard'>Torna alla Dashboard</a>"
    else:
        return "Errore nel salvataggio della scheda."

# --- ROTTE CONSULTAZIONE E APPROVAZIONE ---

@app.route('/archivio')
def archivio_completo():
    if 'utente_email' not in session:
        return redirect(url_for('login'))
    
    tutte_le_schede = ottieni_tutte_le_schede()
    ruolo = str(session.get('utente_ruolo', 'Abitante')).strip()

    if ruolo in ['Amministratore', 'Operatore']:
        return render_template('archivio.html', schede=tutte_le_schede)
    else:
        approvate = [s for s in tutte_le_schede if str(s.get('stato_approvazione', '')).strip().lower() == 'approvata']
        return render_template('archivio.html', schede=approvate)

@app.route('/approva/<int:id>')
def approva_scheda(id):
    if session.get('utente_ruolo') != 'Amministratore':
        return "Accesso negato.", 403
    
    if approva_scheda_db(id):
        return redirect(url_for('archivio_completo'))
    else:
        return "Errore durante l'approvazione.", 500

@app.route('/scheda/<int:id>')
def visualizza_scheda(id):
    try:
        with sqlite3.connect('museo_sicano.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM schede WHERE id = ?', (id,))
            scheda = cursor.fetchone()
            
            if scheda:
                if str(scheda['stato_approvazione']).strip().lower() != 'approvata' and session.get('utente_ruolo') == 'Abitante':
                    return "Accesso negato: scheda in fase di revisione.", 403
                return render_template('dettaglio_scheda.html', s=scheda)
            return "Scheda non trovata", 404
    except Exception as e:
        return f"Errore: {e}", 500

@app.route('/dashboard')
def dashboard_ritorno():
    if 'utente_email' not in session:
        return redirect(url_for('login'))
    
    ruolo = str(session.get('utente_ruolo', 'Abitante')).strip()
    utente = {'nome': session.get('utente_nome'), 'cognome': session.get('utente_cognome'), 'ruolo': ruolo}
    
    permessi = controllo_permessi(ruolo)
    tutte_le_schede = ottieni_tutte_le_schede()

    if ruolo not in ['Amministratore', 'Operatore']:
        schede_visibili = [s for s in tutte_le_schede if str(s.get('stato_approvazione', '')).strip().lower() == 'approvata']
    else:
        schede_visibili = tutte_le_schede
    
    return render_template('dashboard.html', utente=utente, permessi=permessi, schede=schede_visibili)

# --- GESTIONE CODICI ATTIVAZIONE ---

@app.route('/gestione_codici')
def gestione_codici_pagina():
    if session.get('utente_ruolo') != 'Amministratore':
        return "Accesso negato", 403
    return render_template('gestione_codici.html') # Puoi usare una stringa HTML o un file dedicato

@app.route('/genera_codice/<ruolo>')
def genera_nuovo_codice(ruolo):
    if session.get('utente_ruolo') != 'Amministratore':
        return "Accesso negato", 403
    
    nuovo_codice = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    try:
        with sqlite3.connect('museo_sicano.db') as conn:
            conn.execute('INSERT INTO codici_attivazione (codice, ruolo_destinato, stato) VALUES (?, ?, "Attivo")', 
                         (nuovo_codice, ruolo))
            conn.commit()
        return f"Codice Generato: {nuovo_codice} per ruolo {ruolo}. <a href='/gestione_codici'>Indietro</a>"
    except Exception as e:
        return f"Errore: {e}"

# --- FUNZIONALITÀ ADMIN: MODIFICA ED ELIMINA ---

@app.route('/elimina_scheda/<int:id>')
def elimina_scheda(id):
    if session.get('utente_ruolo') != 'Amministratore':
        return "Accesso negato", 403
    
    try:
        with sqlite3.connect('museo_sicano.db') as conn:
            conn.execute('DELETE FROM schede WHERE id = ?', (id,))
            conn.commit()
        return redirect(url_for('archivio_completo'))
    except Exception as e:
        return f"Errore durante l'eliminazione: {e}"

@app.route('/modifica_scheda/<int:id>', methods=['GET', 'POST'])
def modifica_scheda(id):
    if session.get('utente_ruolo') != 'Amministratore':
        return "Accesso negato", 403

    if request.method == 'POST':
        # Recuperiamo tutti i campi principali dal form
        titolo = request.form.get('titolo')
        categoria = request.form.get('categoria')
        descrizione = request.form.get('descrizione')
        luogo = request.form.get('luogo_ritrovamento')
        epoca = request.form.get('epoca_risalenza')
        materiale = request.form.get('materiale_tecnica')

        try:
            with sqlite3.connect('museo_sicano.db') as conn:
                conn.execute('''
                    UPDATE schede 
                    SET titolo=?, categoria=?, descrizione=?, luogo_ritrovamento=?, epoca_risalenza=?, materiale_tecnica=?
                    WHERE id = ?
                ''', (titolo, categoria, descrizione, luogo, epoca, materiale, id))
                conn.commit()
            return redirect(url_for('archivio_completo'))
        except Exception as e:
            return f"Errore durante l'aggiornamento: {e}"

    # Caricamento dati per il form (GET)
    with sqlite3.connect('museo_sicano.db') as conn:
        conn.row_factory = sqlite3.Row
        scheda = conn.execute('SELECT * FROM schede WHERE id = ?', (id,)).fetchone()
    
    if not scheda:
        return "Scheda non trovata", 404
        
    return render_template('modifica_scheda.html', s=scheda)

if __name__ == "__main__":
    app.run(debug=True)