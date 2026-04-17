import sqlite3

def promuovi_ad_amministratore(email_utente):
    try:
        # Ci colleghiamo al database
        conn = sqlite3.connect('museo_sicano.db')
        cursor = conn.cursor()
        
        # Aggiorniamo il ruolo per l'email specificata
        cursor.execute("""
            UPDATE utenti 
            SET ruolo = 'Amministratore' 
            WHERE email = ?
        """, (email_utente.lower().strip(),))
        
        # Verifichiamo se l'utente esisteva davvero
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Successo! L'utente {email_utente} ora è un Amministratore.")
        else:
            print(f"❌ Errore: Nessun utente trovato con l'email {email_utente}.")
            
        conn.close()
    except Exception as e:
        print(f"⚠️ Si è verificato un errore: {e}")

if __name__ == "__main__":
    email = input("Inserisci l'email dell'utente da promuovere: ")
    promuovi_ad_amministratore(email)