import PySimpleGUI as sg
import sys
import main
import os.path
from sqlite3 import connect
import databaseview
import taskschedulerlog
import csv
import datetime as dt
import dateutil.relativedelta

def get_demo_path():
    demo_path = sg.user_settings_get_entry('-demos folder-', os.path.dirname(__file__))
    return demo_path

def get_file_names():
    n = '.py'
    demo_path = get_demo_path()
    demo_files_dict = {}
    for dirname, dirnames, filenames in os.walk(demo_path):
        for filename in filenames:
            if filename.endswith(n):
                fname_full = os.path.join(dirname, filename)
                if filename not in demo_files_dict.keys():
                    demo_files_dict[filename] = fname_full
                else:
                    # Allow up to 100 dupicated names. After that, give up
                    for i in range(1, 100):
                        new_filename = f'{filename}_{i}'
                        if new_filename not in demo_files_dict:
                            demo_files_dict[new_filename] = fname_full
                            break
    return demo_files_dict

def get_file_list():
    return sorted(list(get_file_names().keys()))

### FUNCTIONS
def get_logging(n, win, i):
    with connect('notification.db') as conn:
        sg.cprint_set_output_destination(win, '-LOGSCREEN-')
        if i == 3:
            status = 'FOUT'
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM logging WHERE status = ? order by date_time desc", (status,))
            for i in cursor:
                sg.cprint(i[1],' - ', i[2],' - ', i[3],' - ', i[5])
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM logging WHERE notification_name = ? order by date_time desc", (n[:-3],))
            # if i == 1:
            #     for i in cursor:
            #         sg.cprint(i[1],' - ', i[2],' - ', i[3],' - ', i[5])
            if i == 2:
                for i in cursor:
                    sg.cprint(i[1],' - ', i[2],' \n ', i[4], '\n')

def get_statistiek(n, win):
    try:
        with connect('notification.db') as conn:
            sg.cprint_set_output_destination(win, '-LOGSCREEN-')
            cursor = conn.cursor()
            if len(n) < 1:
                cursor.execute("SELECT sum(ok), sum(ok_nv), sum(fout) FROM statistiek")
                n = 'Alle bestanden.py'
            else:
                cursor.execute("SELECT ok, ok_nv, fout FROM statistiek WHERE notification_name = ?", (n[:-3],))
            res = cursor.fetchone() 
            totaal = res[0]+res[1]+res[2]
            sg.cprint(n[:-3],'\nGoed verstuurd:   ',res[0],'\nFout verstuurd:    ',res[2],'\nGoed afgehandeld maar niet verzonden: ',res[1],'\nTotaal:    ',totaal)
    except:
        return False

def export_logging_csv(win):
    # field names 
    sg.cprint_set_output_destination(win, '-LOGSCREEN-')
    fields = ['id', 'naam', 'datum_tijd', 'status', 'resultaat', 'omschrijving'] 
    with connect('notification.db') as conn:
        # data rows of csv file 
        cursor = conn.cursor()
        cursor.execute("select * from logging")
        row = cursor.fetchone()
        if row == None:
            lijst = [('','','','','','')]
            return lijst
        lijst = []
        lijst.append(row)
        for i in cursor:     
            lijst.append(i)

        thisday = dt.datetime.today().strftime("%Y-%m-%d")
        name = 'Logging_export_'+thisday
        with open(main.get_demo_path()+'\\'+name, 'w') as f:
            # using csv.writer method from CSV package
            write = csv.writer(f)
            write.writerow(fields)
            write.writerows(lijst)
        sg.cprint('CSV bestand gemaakt: ', main.get_demo_path()+'\\'+name)

def delete_logging_older(win):
    sg.cprint_set_output_destination(win, '-LOGSCREEN-')
    thisday = dt.datetime.today().strftime("%Y-%m-%d")
    d = dt.datetime.strptime(thisday, "%Y-%m-%d")
    d2 = d - dateutil.relativedelta.relativedelta(months=2)
    with connect('notification.db') as conn:
        cursor = conn.cursor()
        cursor.execute("delete from logging where date_time < ?", (d2,))
        sg.cprint('Logging > 2 maanden verwijderd')

def delete_scherm(win):
    sg.theme(main.get_theme())
    create_file_layout = [
        [sg.T('Weet je zeker dat je de logging > 2 maanden wilt verwijderen?', size=(44,1))],
        [sg.Button('Export logging naar csv', tooltip='Exporteer de logging naar een csv bestand'), sg.Button('Verwijder',tooltip='Verwijder de logging ouder dan 2 maanden')]]
    create_window = sg.Window('Logging verwijderen', create_file_layout, element_justification='left', icon='ico_trans.ico')

    while True:
        event, values = create_window.read()
        if event in ('Cancel', sg.WIN_CLOSED):
            break
        if event == 'Verwijder':
            delete_logging_older(win)
            break
        if event == 'Export logging naar csv':
            export_logging_csv(win)
            break
    create_window.close()

def LoggingScreen():
    sg.theme(main.get_theme())
####
    left_col = sg.Col([
        [sg.Text('Logging', font='Default 18')],
              [sg.T('Notificatie of mutatie:', size=(15,1)), sg.Combo(get_file_list(),key='-NOTIF-')],
              [sg.T('Logging',  font='_ 16')],
              [sg.Button('Statistiek',tooltip='Toon de statistieken van alle notificaties of van de gekozen notificatie'),\
                    sg.Button('Inhoud notificatie',tooltip='Toon de inhoud van de gekozen notificatie'),\
                    sg.Button('Fout verstuurd',tooltip='Toon alle fout verstuurde notificaties. Data komt uit de logging tabel')],  
    ], element_justification='l')

    lef_col_tabl = sg.Col([
        [sg.T('Database tabellen',  font='_ 16')],
        [sg.Button('Notificaties tabel',tooltip='Toon alle notificaties'), sg.Button('Logging tabel',tooltip='Toon alle logging of de logging van een gekozen notificatie')], 
        [sg.Button('Statistiek tabel',tooltip='Toon alle statistieken of de statistieken van een gekozen notificatie'), sg.Button('Scheduler log',tooltip='Toon de log data van Windows Task Scheduler')],    
    ], element_justification='l')

    lef_col_tabl2 = sg.Col([
        [sg.T('Export logging',  font='_ 16')],
        [sg.Button('Exporteer logging',tooltip='Exporteer de logging data naar een csv bestand'), sg.Button('Verwijder logging', tooltip='Verwijder de logging ouder dan 2 maanden')],    
    ], element_justification='l')

    right_col = [
        [sg.Multiline(size=(75, 21), write_only=True, key='-LOGSCREEN-', reroute_stdout=True, echo_stdout_stderr=True)],
    ]

    layout = [sg.vtop([sg.Column([[left_col],[lef_col_tabl],[lef_col_tabl2]], element_justification='l'), sg.Col(right_col, element_justification='c') ])
              ]

    window = sg.Window('Logging', layout, icon='ico_trans.ico')
    
####

    while True:  # Event Loop
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            window.close()
            break
        if event == 'Statistiek':
            window['-LOGSCREEN-'].update('')
            win = window
            get_statistiek((values['-NOTIF-']), win)
        if event == 'Inhoud notificatie':
            window['-LOGSCREEN-'].update('')
            win = window
            get_logging((values['-NOTIF-']), win, 2)
        if event == 'Fout verstuurd':
            window['-LOGSCREEN-'].update('')
            win = window
            get_logging((values['-NOTIF-']), win, 3)
        if event == 'Notificaties tabel':
            databaseview.databaseview()
        if event == 'Logging tabel':
            databaseview.databaselogview(values['-NOTIF-'])
        if event == 'Scheduler log':
            taskschedulerlog.schedulerview()
        if event == 'Statistiek tabel':
            databaseview.databasestatsview(values['-NOTIF-'])
        if event == 'Exporteer logging':
            win = window
            export_logging_csv(win)
        if event == 'Verwijder logging':
            win = window
            delete_scherm(win)
    window.close()