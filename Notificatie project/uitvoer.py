import PySimpleGUI as sg
import main
import sys
import os.path

#####
def get_demo_path():
    demo_path = sg.user_settings_get_entry('-demos folder-', os.path.dirname(__file__))
    return demo_path

def get_file_names(n):
    if n == 1:
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

def uitvoer_scherm():
    sg.theme(main.get_theme())
    create_file_layout = [
        [sg.T('Selecteer de uit te voeren notificatie of mutatie:', size=(35,1))],
        [sg.Combo(get_file_list(1), key='-UITVOER-')],
        [sg.CB('Wait for Runs to Complete', default=False, enable_events=True, k='-WAIT-', visible=False)],
        [sg.Button('Uitvoeren', bind_return_key=True)]]
    create_window = sg.Window('Notificatie of mutatie uitvoeren', create_file_layout, element_justification='left', icon='ico_trans.ico')

    while True:
        event, values = create_window.read()
        if event in ('Cancel', sg.WIN_CLOSED):
            break
        if event == 'Uitvoeren':
            file_to_run = main.get_demo_path()+'\\'+values['-UITVOER-']
            main.execute_py_file_with_pipe_output(f'{file_to_run}')
            sg.cprint(file_to_run,text_color='white', background_color='purple')
            sg.cprint('Notificatie of mutatie wordt uitgevoerd.\nControleer logging voor resultaat')
            break
    create_window.close()