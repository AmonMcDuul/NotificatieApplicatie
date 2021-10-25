import PySimpleGUI as sg
import main
import sys
import os.path
import win32com.client
from sqlite3 import connect
import database

#####
def get_demo_path():
    demo_path = sg.user_settings_get_entry('-demos folder-', os.path.dirname(__file__))
    return demo_path

def get_file_names(n):
    if n == 1:
        n = '.sql'
    if n == 2:
        n = '.txt'
    if n == 3:
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

def get_file_list(n):
    return sorted(list(get_file_names(n).keys()))
#####
def multiple_tasks(n):
    with connect('notification.db') as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT tijd FROM notifications WHERE notification = ?", (n,))
            x = ''
            length = ''
            for i in cursor:
                x = i
            for j in x:
                length = j.split(',')
            return len(length)
        except:
            return 1

#####

def delete_task(name, location="\\Notificaties"):

    if name not in list_tasks(location):
        y = "{0} Niet gevonden in windows task scheduler".format(name)
        sg.cprint(y)
    else:
        # connect to the task scheduler
        task = win32com.client.Dispatch('Schedule.Service')
        task.Connect()
        root_folder = task.GetFolder('\\Notificaties')

        # get the folder to delete the task from
        task_folder = task.GetFolder(location)

        task_folder.DeleteTask(name, 0)

        # Verify deletion
        x = name not in list_tasks(location)
        sg.cprint("{0} is verwijderd uit windows task scheduler".format(name))

#####
def list_tasks(location="\\Notificaties"):
    # Create the task service object
    task = win32com.client.Dispatch('Schedule.Service')
    task.Connect()
    root_folder = task.GetFolder('\\Notificaties')

    # Get the folder to list tasks from
    task_folder = task.GetFolder(location)
    tasks = task_folder.GetTasks(0)

    ret = []
    for task in tasks:
        ret.append(task.Name)

    return ret
#####

def verwijder_scherm():
    sg.theme(main.get_theme())
    create_file_layout = [
        [sg.T('Selecteer de te verwijderen conditie:', size=(35,1))],
        [sg.Combo(get_file_list(1), key='-CONDITIE-')],
        [sg.T('Selecteer de te verwijderen e-mail:', size=(35,1))],
        [sg.Combo(get_file_list(2), key='-EMAIL-')],
        [sg.T('Selecteer de te verwijderen notificatie of mutatie:', size=(35,1))],
        [sg.Combo(get_file_list(3), key='-NOTIFMUT-')],
        [sg.Button('Verwijder', bind_return_key=True)]]
    create_window = sg.Window('Notificatie of mutatie uitvoeren', create_file_layout, element_justification='left', icon='ico_trans.ico')

    while True:
        event, values = create_window.read()
        if event in ('Cancel', sg.WIN_CLOSED):
            break
        if event == 'Verwijder':
            c = main.get_demo_path()+'\\'+values['-CONDITIE-']
            e = main.get_demo_path()+'\\'+values['-EMAIL-']
            nm = main.get_demo_path()+'\\'+values['-NOTIFMUT-']
            str2 = values['-NOTIFMUT-'].split('.', 1)[0]
            if len(values['-CONDITIE-']) > 1:
                if os.path.exists(c):
                    os.remove(c)
                    str1 = values['-CONDITIE-'].split('.', 1)[0]
                    database.delete_condition_mail(str1)
                    sg.cprint('Conditie: ' + values['-CONDITIE-'] + ' is verwijderd')
            if len(values['-EMAIL-']) > 1:
                if os.path.exists(e):
                    os.remove(e)
                    str1 = values['-EMAIL-'].split('.', 1)[0]
                    database.delete_condition_mail(str1)
                    sg.cprint('E-mail: ' + values['-EMAIL-'] + ' is verwijderd')
            if len(values['-NOTIFMUT-']) > 1:
                aantal = multiple_tasks(str2)
                if aantal == 1:
                    delete_task(str2)
                if aantal > 1:
                    for i in range(1, aantal+1):
                        delete_task(str2+str(i))
                if os.path.exists(nm):
                    os.remove(nm)
                    database.delete_notifications(str2)
                    sg.cprint('Notificatie of mutatie: ' + values['-NOTIFMUT-'] + ' is verwijderd')
                    
            break
    create_window.close()
