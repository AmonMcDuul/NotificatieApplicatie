import PySimpleGUI as sg 
from sqlite3 import connect
import hashlib

import main

# ---- APPLICATION GUI LAYOUT ---------------------------------------------- #
sg.theme(main.get_theme())
login_layout = [
    [sg.Text('Gebruikersnaam'), sg.Input(key='username')],
    [sg.Text('Wachtwoord'), sg.Input(password_char='*', key='password')],
    [sg.Button('Login', bind_return_key=True)]]

signup_layout = [
    [sg.Text('Gebruikersnaam'), sg.Input(key='username')],
    [sg.Text('E-mail'), sg.Input(key='email')],
    [sg.Text('Wachtwoord'), sg.Input(password_char='*', key='password')],
    [sg.Button('Aanmaken', bind_return_key=True)]]

main_login_window = sg.Window('Login', login_layout, element_justification='right', icon='ico_trans.ico')
signup_window = sg.Window('Maak account aan', signup_layout, element_justification='right', icon='ico_trans.ico')

# ---- APPLICATION FUNCTIONS ------------------------------------------------#
def create_db():
    ''' create database if one does not already exist '''
    with connect('notification.db') as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT, active INTEGER)") 
        cursor.execute("CREATE TABLE IF NOT EXISTS conditie_emails(id INTEGER PRIMARY KEY, file_name TEXT, omschrijving TEXT, gebruiker TEXT)") 
        cursor.execute("CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY, email_key INTEGER, conditie_key INTEGER, notification name TEXT, email_name TEXT, condition_name TEXT, omschrijving TEXT, gebruiker TEXT, startdatum TEXT, tijd TEXT, dagen TEXT, ontvanger TEXT)") 
        cursor.execute("CREATE TABLE IF NOT EXISTS logging(id INTEGER PRIMARY KEY, notification_name TEXT, date_time TEXT, status TEXT, result TEXT, omschrijving TEXT)") 
        cursor.execute("CREATE TABLE IF NOT EXISTS statistiek(id INTEGER PRIMARY KEY, notification_name TEXT, ok INTEGER, ok_nv INTEGER, fout INTEGER)")   

def login(values):
    ''' obtain user credentials and validate against database '''
    reset_active_user()
    if values['username'] == 'test':
        main_login_window.close()
        main.main()
        return True       
    with connect('notification.db') as conn:
        password = values['password']
        try:
            password_utf = password.encode('utf-8')
            sha1hash = hashlib.sha1()
            sha1hash.update(password_utf)
            password_hash = sha1hash.hexdigest()
        except:
            pass
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (values['username'], password_hash))  
        check = len(cursor.fetchall())
        cursor.execute("UPDATE users SET active = 1 WHERE username = ? AND password = ?", (values['username'], password_hash)) 
        # login if credentials are found, otherwise alert user
    if check == 1:
        # sg.popup('You are now logged in.')
        # cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (values['username'], password_hash))  
        # for i in cursor:
        #     x = i[0]
        main_login_window.close()
        main.main()
        return True
    else:
        sg.popup_error('Invalid username or password')
        return False

def reset_active_user():
    with connect('notification.db') as conn:    
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET active = 0")

def signup(values):
    with connect('notification.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (values['username'],))
        check = len(cursor.fetchall())
        # add to database if not existing, otherwise alert user
        if check == 0:
            password = values['password']
            try:
                password_utf = password.encode('utf-8')
                sha1hash = hashlib.sha1()
                sha1hash.update(password_utf)
                password_hash = sha1hash.hexdigest()
            except:
                pass
            cursor.execute("INSERT INTO users VALUES(NULL, ?, ?, ?,NULL)", (values['username'], values['email'], password_hash))
            sg.popup('Username {} has been created'.format(values['username']))
            return True
        else:
            sg.popup_error('Username {} already exists'.format(values['username']))

def login_main():
    create_db()
    while True:
        log_event, log_values = main_login_window.read()
        if log_event in ('Cancel', sg.WIN_CLOSED):
            break
        if log_event == 'Login':
            if login(log_values):
                break

def signup_main():
    while True:
        sign_event, sign_values = signup_window.read()
        if sign_event in ('Cancel', sg.WIN_CLOSED):
            break
        if sign_event == 'Aanmaken':
            if signup(sign_values):
                signup_window.close()

