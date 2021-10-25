import PySimpleGUI as sg
from sqlite3 import connect
import database
import main
import sys
import os.path
import datetime as dt

#####
def get_demo_path():
    demo_path = sg.user_settings_get_entry('-demos folder-', os.path.dirname(__file__))
    return demo_path

def get_file_names(n):
    if n == 1:
        n = '.sql'
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

def mutation_creator(mutatienaam, conditie, omschr):
    mutatienaam = mutatienaam.replace(' ', '_')
    # Read in the file
    with open('mutationtemplate.txt', 'r') as file :
        filedata = file.read()
    # Replace the target string
        filedata = filedata.replace('parameter_mutation_name', mutatienaam)
        filedata = filedata.replace('parameter_omschrijving', omschr)
    #open query en insert
    with open(main.get_demo_path()+'\\'+conditie, 'r') as file :
        querydata = file.read().replace('\n', ' ')
        querydata = querydata.replace('\t', ' ')
        querydata = querydata.replace('\xa0', u' ')
        querydata = querydata.replace('Â', '')
        filedata = filedata.replace('parameter_query', querydata)

    # Write the file out again
    with open(main.get_demo_path()+'\\'+mutatienaam + '.py', 'x') as file:
        file.write(filedata)


def create_mutation():
    sg.theme(main.get_theme())
    create_file_layout = [
        [sg.Text('Mutatie naam', size=(15,1)), sg.Input(key='filename', tooltip='Voer de bestandsnaam in')],
        [sg.Text('Omschrijving', size=(15,1)), sg.Input(key='omschrijving', tooltip='Voer de omschrijving van de mutatie in')],
        [sg.T('Conditie:', size=(15,1)), sg.Combo(get_file_list(1),key='-QUERY-', tooltip='Selecteer de conditie van de mutatie')],
        [sg.Button('Opslaan', bind_return_key=True)]]
    create_window = sg.Window('Maak een mutatie', create_file_layout, icon='ico_trans.ico')

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
        if event == 'Opslaan' and len(values['filename']) > 1 and len(values['omschrijving']) > 1 and len(values['-QUERY-']) > 1:
            thisday = dt.datetime.today().strftime("%Y-%m-%d")
            mutname = 'MUT_'+values['filename']
            if database.create_mutation(mutname, values['-QUERY-'], values['omschrijving'], thisday):
                database.create_statistic(mutname)
                mutation_creator(mutname, values['-QUERY-'], values['omschrijving'])
                sg.cprint('Mutatie gemaakt')
                create_window.close()