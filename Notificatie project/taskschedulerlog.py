import win32com.client
import win32timezone
import PySimpleGUI as sg
import main
import datetime

def schedulerview():
    sg.theme(main.get_theme())
    headings = ['Naam', 'Status', 'Volgende_run', 'Laatste_run', 'Resultaat']

    data = get_task_log()
    if len(data) == 0:
        data = [('','','','','')]

    layout = [[sg.Table(data, auto_size_columns=True, headings=headings, size=(40, 30), justification='left', key='-TABLE-')],]
    window = sg.Window("Title", layout, resizable=True, finalize=True, icon='ico_trans.ico')
    window['-TABLE-'].expand(True, True)
    window['-TABLE-'].table_frame.pack(expand=True, fill='both')

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        print(event, values)

def get_task_log():
    TASK_STATE = {0: 'Unknown',
                1: 'Disabled',
                2: 'Queued',
                3: 'Ready',
                4: 'Running'}

    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    folders = [scheduler.GetFolder('\\Notificaties')]
    while folders:
        folder = folders.pop(0)
        folders += list(folder.GetFolders(0))
        lijst = []
        for task in folder.GetTasks(0):
            naam = task.Path.split('\\')
            x = naam[2],TASK_STATE[task.State],str(task.NextRunTime.strftime("%d-%m-%Y %H:%M")),str(task.LastRunTime.strftime("%d-%m-%Y %H:%M")),task.LastTaskResult
            lijst.append(x)
            # print('Path       : %s' % task.Path)
            # print('State      : %s' % TASK_STATE[task.State])
            # print('Last Run   : %s' % task.LastRunTime)
            # print('Last Result: %s\n' % task.LastTaskResult)
        return lijst