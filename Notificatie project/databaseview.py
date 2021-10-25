import PySimpleGUI as sg
import database
import main

def databaseview():
    sg.theme(main.get_theme())
    headings = ['id','email_key', 'conditie_key'	,'notificatie naam',	'e-mail naam', 'conditie naam',	'omschrijving',	'aanmaker',	'startdatum',	'tijd',	'dagen',	'ontvanger']

    data = database.select_all_notifications()

    layout = [[sg.Table(data, headings=headings, size=(50, 30), justification='left', key='-TABLE-')],]
    window = sg.Window("Notificaties", layout, resizable=True, finalize=True, icon='ico_trans.ico')
    window['-TABLE-'].expand(True, True)
    window['-TABLE-'].table_frame.pack(expand=True, fill='both')

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        print(event, values)

def databaselogview(n):
    sg.theme(main.get_theme())
    headings = ['id',	'notificatie_naam',	'datum_tijd',	'status',	'result',	'omschrijving']

    data = database.select_all_logging(n)

    layout = [[sg.Table(data, headings=headings, size=(50, 30), justification='left', key='-TABLE-')],]
    window = sg.Window("Logging", layout, resizable=True, finalize=True, icon='ico_trans.ico')
    window['-TABLE-'].expand(True, True)
    window['-TABLE-'].table_frame.pack(expand=True, fill='both')
    
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        print(event, values)

def databasestatsview(n):
    sg.theme(main.get_theme())
    headings = ['id', 'notificatie_naam', 'ok',	'ok_nv', 'fout']

    data = database.select_statistic(n)

    layout = [[sg.Table(data, headings=headings, size=(50, 30), justification='left', key='-TABLE-')],]
    window = sg.Window("Statistieken", layout, resizable=True, finalize=True, icon='ico_trans.ico')
    window['-TABLE-'].expand(True, True)
    window['-TABLE-'].table_frame.pack(expand=True, fill='both')
    
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        print(event, values)