import PySimpleGUI as sg
import main
import database

def create_mail():
    sg.theme(main.get_theme())
    layout = [[sg.Text('Maak een e-mail', font='Default 18')],
              [sg.T('Bestandsnaam:', size=(15,1)), sg.Input(key='-EMAIL TEMP NAME-',tooltip='Voer de bestandsnaam in', size=(35,1))],
              [sg.T('Naam notificatie:', size=(15,1)), sg.Input(key='-EMAIL NOTIF NAME-',tooltip='Voer de naam van de notificatie in. Deze komt in de e-mail te staan als de naam van de notificatie', size=(35,1))],
              [sg.T('Onderwerp notificatie:', size=(15,1)), sg.Multiline(key='-EMAIL NOTIF SUBJECT-',tooltip='Voer het onderwerp van de notificatie in', size=(60,2))],
              [sg.T('Reden van notificatie:', size=(15,1)), sg.Multiline(key='-EMAIL NOTIF REASON-',tooltip='Voer de reden van de notificatie in', size=(60,2))],
              [sg.T('Actie gebruiker:', size=(15,1)), sg.Multiline(key='-EMAIL NOTIF ACTION-',tooltip='Voer de te verwachte actie van de ontvanger van de notificatie in', size=(60,2))],
              [sg.Button('Opslaan')]]

    window = sg.Window('Maak een e-mail', layout, icon='ico_trans.ico')

    while True:  # Event Loop
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        if event == 'Opslaan' and len(values['-EMAIL TEMP NAME-']) == 0 or len(values['-EMAIL NOTIF NAME-']) == 0 or len(values['-EMAIL NOTIF SUBJECT-']) == 0\
             or len(values['-EMAIL NOTIF REASON-']) == 0 or len(values['-EMAIL NOTIF ACTION-']) == 0:
            if len(values['-EMAIL TEMP NAME-']) == 0:
                window['-EMAIL TEMP NAME-'].Widget.configure(highlightcolor='red', highlightthickness=2)
            else:
                window['-EMAIL TEMP NAME-'].Widget.configure(highlightcolor='green', highlightthickness=0)
            if len(values['-EMAIL NOTIF NAME-']) == 0:
                window['-EMAIL NOTIF NAME-'].Widget.configure(highlightcolor='red', highlightthickness=2)
            else:
                window['-EMAIL NOTIF NAME-'].Widget.configure(highlightcolor='green', highlightthickness=0)
            if len(values['-EMAIL NOTIF SUBJECT-']) == 0:
                window['-EMAIL NOTIF SUBJECT-'].Widget.configure(highlightcolor='red', highlightthickness=2)
            else:
                window['-EMAIL NOTIF SUBJECT-'].Widget.configure(highlightcolor='green', highlightthickness=0)
            if len(values['-EMAIL NOTIF REASON-']) == 0:
                window['-EMAIL NOTIF REASON-'].Widget.configure(highlightcolor='red', highlightthickness=2)
            else:
                window['-EMAIL NOTIF REASON-'].Widget.configure(highlightcolor='green', highlightthickness=0)
            if len(values['-EMAIL NOTIF ACTION-']) == 0:
                window['-EMAIL NOTIF ACTION-'].Widget.configure(highlightbackground='red', highlightthickness=2)
            else:
                window['-EMAIL NOTIF ACTION-'].Widget.configure(highlightcolor='green', highlightthickness=0)
        if event == 'Opslaan' and len(values['-EMAIL TEMP NAME-']) > 1 and len(values['-EMAIL NOTIF NAME-']) > 1 and len(values['-EMAIL NOTIF SUBJECT-']) > 1\
             and len(values['-EMAIL NOTIF REASON-']) > 1 and len(values['-EMAIL NOTIF ACTION-']) > 1:
            tempname = values['-EMAIL TEMP NAME-']
            namenot = values['-EMAIL NOTIF NAME-']
            subjectnot = values['-EMAIL NOTIF SUBJECT-']
            reasonnot = values['-EMAIL NOTIF REASON-']
            actionnot = values['-EMAIL NOTIF ACTION-']
            if database.create_file(tempname,subjectnot):
                mail_creator(tempname, namenot, subjectnot,reasonnot,actionnot)
                window.close() 

def mail_creator(tempname, namenot, subjectnot,reasonnot,actionnot):
    tempname = tempname.replace(' ', '_')
    subjectnot = subjectnot.replace('\n', '<br />')
    reasonnot = reasonnot.replace('\n', '<br />')
    actionnot = actionnot.replace('\n', '<br />')
    # Read in the file
    with open('nieuwemailtemplate.txt', 'r') as file :
        filedata = file.read()
    # Replace the target string
        # filedata = filedata.replace('parameter_email', to)
        # filedata = filedata.replace('parameter_subject', subject)
        filedata = filedata.replace('parameter_notif_naam', namenot)
        filedata = filedata.replace('parameter_notif_subject', subjectnot)
        filedata = filedata.replace('parameter_notif_reason', reasonnot)
        filedata = filedata.replace('parameter_notif_action', actionnot)

    # Write the file out again
    with open(main.get_demo_path()+'\\'+tempname + '.txt', 'x') as file:
        file.write(filedata)