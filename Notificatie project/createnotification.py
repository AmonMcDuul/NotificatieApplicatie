import PySimpleGUI as sg
import sys
import main
import os.path
## for scheduled task
import datetime as dt
import win32com.client
from pathlib import Path
## db
import database
import re

def tijd_check(s):
    s = s.replace(' ','')
    r = s.split(',')
    for j in r:
        if len(j) != 5:
            return False
    count = 0
    regex = r"(23:59|2[0-3]:[0-5][0-9]|[0-1][0-9]:[0-5][0-9])"
    matches = re.finditer(regex, s)
    for i in matches:
        count+=1
    if count == len(r):
        return True
    else:
        return False

def get_demo_path():
    demo_path = sg.user_settings_get_entry('-demos folder-', os.path.dirname(__file__))
    return demo_path

def get_file_names(n):
    if n == 1:
        n = '.sql'
    if n == 2:
        n = '.txt'
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

def get_file_list(n):
    return sorted(list(get_file_names(n).keys()))
#####


def create_notification():
    sg.theme(main.get_theme())
    today = dt.date.today()
    thisday = today.strftime("%Y-%m-%d")

    left_col = sg.Col([
            [sg.Text('Maak een notificatie', font='Default 18')],
              [sg.T('Bestandsnaam:', size=(15,1)), sg.Input(key='-NOTIFICATION TEMP NAME-',tooltip='Voer de bestandsnaam in', size=(35,1))],
              [sg.T('Omschrijving:', size=(15,1)), sg.Input(key='-OMSCHR-',tooltip='Voer de omschrijving van de notificatie in', size=(35,1))],
              [sg.T('Geadresseerde:', size=(15,1)), sg.Input(key='-EMAIL TO-',tooltip='Voer het e-mailadres van de ontvanger is. scheidt e-mailadressen met een ; om meerdere ontvangers in te voeren', size=(35,1))],
              [sg.T('Onderwerp:', size=(15,1)), sg.Input(key='-EMAIL SUBJECT-',tooltip='Voer het onderwerp van de e-mail in', size=(35,1))],
            #   [sg.T('Bijlage:', size=(15,1)), sg.Input(key='-EMAIL ADDON-', size=(35,1))],
              [sg.T('Conditie:', size=(15,1)), sg.Combo(get_file_list(1), tooltip='Selecteer de conditie', key='-QUERY-')],
              [sg.T('Email:', size=(15,1)), sg.Combo(get_file_list(2),tooltip='Selecteer de e-mail template', key='-EMAIL-')],
              [sg.T('Bijlage selecteren')],
                [sg.In(tooltip='Selecteer een PDF als bijlage', key='-BIJLAGE-')],
                [sg.FileBrowse(target='-BIJLAGE-', file_types=(("PDF bestand", "*.pdf"),))],    
    ], element_justification='l')

    lef_col_find_re = sg.Col([    
    ], element_justification='l')

    right_col = [
            [sg.CalendarButton('Kies start datum',format='%Y-%m-%d', target='input1', key='-DATE-')],
            [sg.In(default_text=thisday, readonly=True, size=(20,1),tooltip='Selecteer een startdatum. voer de datum met de volgende notatie in: yyyy-mm-dd', key='input1')],
            [sg.T('Tijd:', size=(7,1)), sg.Input(key='-TIJD-', tooltip='Voer de tijd in als: xx:xx . Voer meerdere tijden in gescheiden met een ,  bv: xx:xx,xx:xx', size=(10,1))],
            [sg.Checkbox('Maandag:', default=True, key="Ma")],
            [sg.Checkbox('Dinsdag:', default=True, key="Di")],
            [sg.Checkbox('Woensdag:', default=True, key="Wo")],
            [sg.Checkbox('Donderdag:', default=True, key="Do")],
            [sg.Checkbox('Vrijdag:', default=True, key="Vr")],
            [sg.Checkbox('Zaterdag:', default=False, key="Za")],
            [sg.Checkbox('Zondag:', default=False, key="Zo")],
            [sg.Button('Opslaan')],
    ]

    layout = [sg.vtop([sg.Column([[left_col],[lef_col_find_re]], element_justification='l'), sg.Col(right_col, element_justification='l') ])
              ]

    window = sg.Window('Maak een notificatie', layout, icon='ico_trans.ico')

    while True:  # Event Loop
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            window.close()
            break
        if event == 'Opslaan' and ('@') not in values['-EMAIL TO-'] or (':') not in values['-TIJD-'] or len(values['-NOTIFICATION TEMP NAME-']) == 0\
            or len(values['-OMSCHR-']) == 0 or len(values['-EMAIL SUBJECT-']) == 0 or len(values['input1']) == 0:
            if ('@') not in values['-EMAIL TO-']:
                window['-EMAIL TO-'].Widget.configure(highlightcolor='red', highlightthickness=2)
            else:
                window['-EMAIL TO-'].Widget.configure(highlightcolor='green', highlightthickness=0)
            if (':') not in values['-TIJD-']:
                window['-TIJD-'].Widget.configure(highlightcolor='red', highlightthickness=2)
            else:
                window['-TIJD-'].Widget.configure(highlightcolor='green', highlightthickness=0)
            if len(values['-NOTIFICATION TEMP NAME-']) == 0:
                window['-NOTIFICATION TEMP NAME-'].Widget.configure(highlightcolor='red', highlightthickness=2)
            else:
                window['-NOTIFICATION TEMP NAME-'].Widget.configure(highlightcolor='green', highlightthickness=0)
            if len(values['-OMSCHR-']) == 0:
                window['-OMSCHR-'].Widget.configure(highlightcolor='red', highlightthickness=2)
            else:
                window['-OMSCHR-'].Widget.configure(highlightcolor='green', highlightthickness=0)
            if len(values['-EMAIL SUBJECT-']) == 0:
                window['-EMAIL SUBJECT-'].Widget.configure(highlightcolor='red', highlightthickness=2)
            else:
                window['-EMAIL SUBJECT-'].Widget.configure(highlightcolor='green', highlightthickness=0)
            if len(values['input1']) == 0:
                window['input1'].Widget.configure(highlightcolor='red', highlightthickness=2)
            else:
                window['input1'].Widget.configure(highlightcolor='green', highlightthickness=0)
        if event == 'Opslaan' and ('@') in values['-EMAIL TO-'] and (':') in values['-TIJD-'] and len(values['-NOTIFICATION TEMP NAME-']) > 0\
            and len(values['-OMSCHR-']) > 1 and len(values['-EMAIL SUBJECT-']) > 1 and len(values['input1']) > 1 and len(values['-QUERY-']) > 1 and len(values['-EMAIL-']) > 1:
            notifname = values['-NOTIFICATION TEMP NAME-']
            notifname = notifname.replace(' ', '_')
            omschr = values['-OMSCHR-']
            to = values['-EMAIL TO-']
            subject = values['-EMAIL SUBJECT-']
            query = values['-QUERY-']
            emailtxt = values['-EMAIL-']
            bijlage = values['-BIJLAGE-']
            if len(bijlage) == 0:
                bijlage = 1
            ##scheduler
            datum = values['input1']
            tijd = values['-TIJD-']
            tijd = tijd.replace(' ', '')
            if tijd_check(str(tijd)):
                # day of week # value can be [1, 2, 4, 8, 16, 32, 64]
                days = {'Ma': 2, 'Di': 4, 'Wo': 8, 'Do':16, 'Vr':32, 'Za':64, 'Zo':1}
                dagen = 0
                dagendb = ''
                for dag in days.keys():
                    if values[dag]:
                        dagen += days[dag]
                        dagendb = dagendb + dag + " "
                x = tijd.split(',')
                if database.create_notif(notifname, emailtxt, query, omschr, datum, tijd, dagendb, to):
                    database.create_statistic(notifname)
                    notification_creator(notifname, to, subject, emailtxt, query, bijlage)
                    if len(x) > 1:
                        count = 0
                        for i in x:
                            count+=1
                            naam = notifname + str(count)
                            create_scheduled_task(notifname, naam, datum, i, dagen)
                    else:
                        naam = notifname
                        create_scheduled_task(notifname, naam, datum, tijd, dagen)
                    window.close() 
            else:
                sg.cprint('Tijd(en) zijn niet goed ingevuld.\
                \nBv: 08:00 voor enkele tijd\nBv: 08:00,12:00,16:00 voor meerdere tijden.', c='white on red', end='')
                sg.cprint('')

def notification_creator(notifname, to, subject, emailtxt, query, bijlage):
    # Read in the file
    with open('notiftemplatedb.txt', 'r') as file :
        filedata = file.read()

    # Replace the target string
        filedata = filedata.replace('parameter_email', to)
        filedata = filedata.replace('parameter_subject', subject)
        filedata = filedata.replace('parameter_notification_name', notifname)
        if bijlage == 1:
            filedata = filedata.replace('parameter_bijlage_sturing', 'False')
        else:
            filedata = filedata.replace('parameter_bijlage_sturing', 'True')
            filedata = filedata.replace('parameter_bijlage', bijlage)
            bijlagenaam = Path(bijlage)
            filedata = filedata.replace('parameter_xbijlage_naam', bijlagenaam.stem+'.pdf')

    #Open mailtemplate and insert in notificationtemplate
    with open(main.get_demo_path()+'\\'+emailtxt, 'r') as file :
        maildata = file.read()#.replace('\n', '')
        filedata = filedata.replace('parameter_txt_email', maildata)
    #open query en insert
    with open(main.get_demo_path()+'\\'+query, 'r') as file :
        querydata = file.read().replace('\n', ' ')
        querydata = querydata.replace('\t', ' ')
        querydata = querydata.replace('\xa0', u' ')
        querydata = querydata.replace('Â', '')
        filedata = filedata.replace('parameter_query', querydata)

    # Write the file out again
    with open(main.get_demo_path()+'\\'+notifname + '.py', 'x') as file:
        file.write(filedata)

def create_scheduled_task(notifname, naam, datum, tijd, dagen):
    #Connection to Task Scheduler
    try:
        task = win32com.client.Dispatch('Schedule.Service')
        task.Connect()
        root_folder = task.GetFolder('\\Notificaties')
        newtask = task.NewTask(0)

        # Trigger
        x = datum.split('-')
        tijd = tijd.replace(',', '')
        if len(tijd) < 5:
            return
        y = tijd.split(':')
        set_time=dt.datetime(int(x[0]),int(x[1]),int(x[2]),int(y[0]),int(y[1]),0,500000)
        TASK_TRIGGER_TIME = 1
        TASK_TRIGGER_DAILY = 2
        TASK_TRIGGER_WEEKLY = 3
        trigger = newtask.Triggers.Create(TASK_TRIGGER_WEEKLY)
        trigger.StartBoundary = set_time.isoformat()
        trigger.DaysOfWeek = dagen  # value can be [1, 2, 4, 8, 16, 32, 64]
        trigger.WeeksInterval = 1  # Task runs every week.
        trigger.Enabled = True

        # Action
        TASK_ACTION_EXEC = 0
        action = newtask.Actions.Create(TASK_ACTION_EXEC)
        action.ID = 'DO NOTHING'

        action.Path = r'C:\Program Files (x86)\Python39-32\python.exe'
        action.Arguments = main.get_demo_path() + '\\' + notifname + '.py'

        # Parameters
        newtask.RegistrationInfo.Description = notifname
        newtask.Settings.Enabled = True
        newtask.Settings.StopIfGoingOnBatteries = False

        # Saving
        notifname = naam
        TASK_CREATE_OR_UPDATE = 6
        TASK_LOGON_NONE = 0
        root_folder.RegisterTaskDefinition(
            notifname,  # Joran's notificatie applicatie
            newtask,
            TASK_CREATE_OR_UPDATE,
            '',  # No user
            '',  # No password
            TASK_LOGON_NONE)
    except:
        sg.cprint('Maken scheduled task is niet gelukt.', c='white on red', end='')
        sg.cprint('')