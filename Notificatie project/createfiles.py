import PySimpleGUI as sg
from sqlite3 import connect
import database
import main

def create_sql_window():
    sg.theme(main.get_theme())
    create_file_layout = [
        [sg.Text('Bestandsnaam', size=(15,1)), sg.Input(key='filename', tooltip='Voer de bestandsnaam in')],
        [sg.Text('Omschrijving', size=(15,1)), sg.Input(key='omschrijving', tooltip='Voer een omschrijving in')],
        [sg.Button('Opslaan', bind_return_key=True)]]
    create_window = sg.Window('Maak een conditie', create_file_layout, icon='ico_trans.ico')

    while True:
        event, values = create_window.read()
        if event in ('Cancel', sg.WIN_CLOSED):
            break
        if event == 'Opslaan' and len(values['filename']) == 0 or len(values['omschrijving']) == 0:
            if len(values['filename']) == 0:
                create_window['filename'].Widget.configure(highlightcolor='red', highlightthickness=2)
            else:
                create_window['filename'].Widget.configure(highlightcolor='green', highlightthickness=0)
            if len(values['omschrijving']) == 0:
                create_window['omschrijving'].Widget.configure(highlightcolor='red', highlightthickness=2)
            else:
                create_window['omschrijving'].Widget.configure(highlightcolor='green', highlightthickness=0)            
        if event == 'Opslaan' and len(values['filename']) > 1 and len(values['omschrijving']) > 1:
            if database.create_file(format(values['filename']),format(values['omschrijving'])):
                create_sql(format(values['filename']))
                create_window.close()

### CREATE SQL FILE
def create_sql(n):
    n = n.replace(' ', '_')
    name = (n + ".sql")
    f = open(main.get_demo_path()+'\\'+name, "x")
    editor_program = main.get_editor()
    new_file = main.get_demo_path()+'\\'+name
    main.execute_command_subprocess(f'{editor_program}', f'"{new_file}"')