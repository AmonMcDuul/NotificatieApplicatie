import os.path
import subprocess
import sys
import mmap, re
import warnings
import PySimpleGUI as sg
##import andere klassen
import login
import createfiles
import createmail
import createnotification
import createmutation
import loggingview
import uitvoer
import verwijder
import database
from sqlite3 import connect

### LAYOUT
#pyinstaller --hiddenimport win32timezone -w -F --onefile -i"ico_trans.ico" main.py

# --------------------------------- Create the window ---------------------------------
def make_window():
    theme = get_theme()
    if not theme:
        theme = sg.OFFICIAL_PYSIMPLEGUI_THEME
    sg.theme(theme)

    filter_tooltip = "Zoek naar bestanden"
    find_re_tooltip = "Zoek naar tekst in de bestanden"

    left_col = sg.Col([
        [sg.Listbox(values=get_file_list(0), select_mode=sg.SELECT_MODE_SINGLE,enable_events=True, size=(80, 20), key='-DEMO LIST-')],
        [sg.Button('Maak conditie'), sg.Button('Maak e-mail'), sg.Button('Maak notificatie'), sg.Button('Maak mutatie')], 
        [sg.B('Logging'), sg.Button('Uitvoeren'), sg.B('Wijzigen'), sg.B('Verwijderen'), sg.B('Vernieuwen')], 
    ], element_justification='l')

    lef_col_find_re = sg.pin(sg.Col([
        [sg.Text('Vind in tekst:', tooltip=find_re_tooltip), sg.Input(size=(25, 1),key='-FIND RE-', tooltip=find_re_tooltip),sg.B('Zoek')]], k='-RE COL-'))

    right_col = [
        [sg.Multiline(size=(40, 21), write_only=True, key=ML_KEY, reroute_stdout=True, echo_stdout_stderr=True)],
        [sg.B('Instellingen'), sg.Button('Exit')],
        [sg.T('Notificatie Applicatie - Joran Schols - 2021 - Versie 1.0' , font='Default 8', pad=(0,0))],
    ]

    options_at_bottom = sg.pin(sg.Column([[sg.CB('Verbose', enable_events=True, k='-VERBOSE-', visible=False),
                         sg.CB('Show only first match in file', default=True, enable_events=True, k='-FIRST MATCH ONLY-', visible=False),
                         sg.CB('Find ignore case', default=True, enable_events=True, k='-IGNORE CASE-', visible=False),
                         sg.CB('Wait for Runs to Complete', default=False, enable_events=True, k='-WAIT-', visible=False)
                                           ]],
                                         pad=(0,0), k='-OPTIONS BOTTOM-'))
                                         
    ###
    choose_source_files = [[sg.Button('Condities'), sg.Button('E-mails'), sg.Button('Notificaties'), sg.Button('Mutaties')],
            [sg.Text('Zoek:', tooltip=filter_tooltip), sg.Input(size=(25, 1), enable_events=True, key='-FILTER-', tooltip=filter_tooltip),
         sg.T(size=(15,1), k='-FILTER NUMBER-')],    
    ]
    ###

    # ----- Full layout -----

    layout = [sg.vtop([sg.Col(choose_source_files, element_justification='l') ]),
              sg.vtop([sg.Column([[left_col],[lef_col_find_re]], element_justification='l'), sg.Col(right_col, element_justification='c') ]),
              [options_at_bottom]
              ]

    # --------------------------------- Create Window ---------------------------------
    window = sg.Window('Notificatie applicatie', layout, finalize=True, icon='ico_trans.ico')
    
    if not advanced_mode():
        window['-RE COL-'].update(visible=False)
        window['-OPTIONS BOTTOM-'].update(visible=False)

    sg.cprint_set_output_destination(window, ML_KEY)
    return window

### SETTINGS WINDOW

def settings_window():
    try:
        global_editor = sg.pysimplegui_user_settings.get('-editor program-')
    except:
        global_editor = ''
    try:    # in case running with old version of PySimpleGUI that doesn't have a global PSG settings path
        global_theme = sg.theme_global()
    except:
        global_theme = ''

    layout = [[sg.T('Instellingen', font='DEFAULT 25')],
              [sg.T('Map met bronbestanden',  font='_ 16')],
               [sg.Combo(sorted(sg.user_settings_get_entry('-folder names-', [])), default_value=sg.user_settings_get_entry('-demos folder-', get_demo_path()), size=(50, 1), key='-FOLDERNAME-'),
               sg.FolderBrowse('Browse', target='-FOLDERNAME-')],
              [sg.T('Tekst editor',  font='_ 16')],
                [ sg.In(sg.user_settings_get_entry('-editor program-', ''),k='-EDITOR PROGRAM-'), sg.FileBrowse()],
              [sg.T('Thema',  font='_ 16')],
              [sg.Combo(['']+sg.theme_list(),sg.user_settings_get_entry('-theme-', ''), readonly=True,  k='-THEME-')],
              [sg.CB('Geavanceerd zoeken', default=advanced_mode() ,k='-ADVANCED MODE-')],
              [sg.Button('Aanmelden', size=(8,1))],
              [sg.B('Ok', bind_return_key=True)],
              ]

    window = sg.Window('Instellingen', layout,icon='ico_trans.ico')

    settings_changed = False

    while True:
        event, values = window.read()
        if event in ('Cancel', sg.WIN_CLOSED):
            break
        if event == 'Ok':
            sg.user_settings_set_entry('-demos folder-', values['-FOLDERNAME-'])
            sg.user_settings_set_entry('-editor program-', values['-EDITOR PROGRAM-'])
            sg.user_settings_set_entry('-theme-', values['-THEME-'])
            sg.user_settings_set_entry('-folder names-', list(set(sg.user_settings_get_entry('-folder names-', []) + [values['-FOLDERNAME-'], ])))
            sg.user_settings_set_entry('-advanced mode-', values['-ADVANCED MODE-'])
            settings_changed = True
            break
        if event == 'Aanmelden':
            login.signup_main()

    window.close()
    return settings_changed

ML_KEY = '-ML-'

### MAIN RUNNING PROGRAM

def login_screen():
    login.login_main()

def main():
    find_in_file.file_list_dict = None
    old_typed_value = None
    file_list_dict = get_file_list_dict(0)
    file_list = get_file_list(0)
    window = make_window()
    window['-FILTER NUMBER-'].update(f'{len(file_list)} bestanden')
    counter = 0

    while True:    
        event, values = window.read()
        counter += 1
        sg.cprint_set_output_destination(window, '-ML-')
        if event in (sg.WINDOW_CLOSED, 'Exit'):
            break
    ### selected file
        if event == '-DEMO LIST-' and len(values['-DEMO LIST-']):
            window['-ML-'].update('')
            database.get_file_description((values['-DEMO LIST-']))
    ###
        if event == 'Wijzigen':
            editor_program = get_editor()
            for file in values['-DEMO LIST-']:
                if find_in_file.file_list_dict is not None:
                    full_filename, line = window_choose_line_to_edit(file, find_in_file.file_list_dict[file][0], find_in_file.file_list_dict[file][1])
                else:
                    full_filename, line = get_file_list_dict(0)[file], 1
                if line is not None:
                    sg.cprint(f'Wijzigen bestand via: {editor_program}', text_color='white', background_color='red', end='')
                    sg.cprint('')
                    sg.cprint(f'{full_filename}', c='white on purple')
                    # if line != 1:
                    if using_local_editor():
                        execute_command_subprocess(editor_program, full_filename)
                    else:
                        try:
                            sg.execute_editor(full_filename, line_number=int(line))
                        except:
                            execute_command_subprocess(editor_program, full_filename)
                    # else:
                    #     sg.execute_editor(full_filename)
                else:
                    sg.cprint('Wijzigen geannuleerd')
        #### Verwijder knop
        if event == 'Verwijderen':
            verwijder.verwijder_scherm()

        ### Views querys emails notificaties mutaties
        elif event == 'Condities':
            file_list_dict = get_file_list_dict(1)
            file_list = get_file_list(1)
            window['-DEMO LIST-'].update(file_list)
            window['-FILTER NUMBER-'].update(f'{len(file_list)} bestanden')
        elif event == 'E-mails':
            file_list_dict = get_file_list_dict(2)
            file_list = get_file_list(2)
            window['-DEMO LIST-'].update(file_list)
            window['-FILTER NUMBER-'].update(f'{len(file_list)} bestanden')
        elif event == 'Notificaties':
            file_list_dict = get_file_list_dict(3)
            file_list = get_file_list(3)
            window['-DEMO LIST-'].update(file_list)
            window['-FILTER NUMBER-'].update(f'{len(file_list)} bestanden')
        elif event == 'Mutaties':
            file_list_dict = get_file_list_dict(4)
            file_list = get_file_list(4)
            window['-DEMO LIST-'].update(file_list)
            window['-FILTER NUMBER-'].update(f'{len(file_list)} bestanden')

        ### CREATE FILE
        elif event == 'Maak conditie':
            sg.cprint('Maak conditie aan....', c='white on green', end='')
            sg.cprint('')
            createfiles.create_sql_window()                        
        ### CREATE MAIL
        elif event == 'Maak e-mail':
            sg.cprint('Maak e-mail aan....', c='white on green', end='')
            sg.cprint('')
            createmail.create_mail()  
        ###
        elif event == 'Maak notificatie':
            sg.cprint('Maak notificatie aan....', c='white on green', end='')
            sg.cprint('')
            createnotification.create_notification()  
        ###
        elif event == 'Maak mutatie':
            sg.cprint('Maak mutatie aan....', c='white on green', end='')
            sg.cprint('')
            createmutation.create_mutation()  
        ###
        elif event == 'Logging':
            sg.cprint('Logging en statistieken', c='white on green', end='')
            sg.cprint('')
            loggingview.LoggingScreen()
        
        elif event == 'Uitvoeren':
            sg.cprint('Uitvoeren....', c='white on green', end='')
            sg.cprint('')
            uitvoer.uitvoer_scherm()

        elif event == '-FILTER-':
            new_list = [i for i in file_list if values['-FILTER-'].lower() in i.lower()]
            window['-DEMO LIST-'].update(new_list)
            window['-FILTER NUMBER-'].update(f'{len(new_list)} files')
            window['-FIND RE-'].update('')

        elif event == 'Zoek':
            window['-ML-'].update('')
            file_list = find_in_file(values['-FIND RE-'], get_file_list_dict(0), regex=True, verbose=values['-VERBOSE-'],window=window)
            window['-DEMO LIST-'].update(sorted(file_list))
            window['-FILTER NUMBER-'].update('')
            window['-FILTER-'].update('')
            sg.cprint('String in bestanden gevonden')

        elif event == 'Instellingen':
            if settings_window() is True:
                window.close()
                window = make_window()
                file_list_dict = get_file_list_dict(0)
                file_list = get_file_list(0)
                window['-FILTER NUMBER-'].update(f'{len(file_list)} bestanden')
        elif event == 'Vernieuwen':
            file_list = get_file_list(0)
            window['-FILTER-'].update('')
            window['-FILTER NUMBER-'].update(f'{len(file_list)} bestanden')
            window['-DEMO LIST-'].update(file_list)
            window['-ML-'].update('')
        elif event == '-FOLDERNAME-':
            sg.user_settings_set_entry('-demos folder-', values['-FOLDERNAME-'])
            file_list_dict = get_file_list_dict(0)
            file_list = get_file_list(0)
            window['-DEMO LIST-'].update(values=file_list)
            window['-FILTER NUMBER-'].update(f'{len(file_list)} bestanden')
            window['-ML-'].update('')
            window['-FILTER-'].update('')

    window.close()

###

def running_linux():
    return sys.platform.startswith('linux')

def running_windows():
    return sys.platform.startswith('win')

def get_file_list_dict(n):
    """
    Returns dictionary of files
    Key is short filename
    Value is the full filename and path

    :return: Dictionary of demo files
    :rtype: Dict[str:str]
    """
    x = 0
    if n == 1:
        n = '.sql'
    if n == 2:
        n = '.txt'
    if n == 3:
        n = '.py'
        x = 1
    if n == 4:
        n = '.py'
        x = 2
    if n == 0:
        n = ('.sql','.txt','.py')
    demo_path = get_demo_path()
    demo_files_dict = {}
    if x == 1:
        for dirname, dirnames, filenames in os.walk(demo_path):
            for filename in filenames:
                if filename.endswith(n) and not filename.startswith('MUT_'):
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
    if x == 2:
        for dirname, dirnames, filenames in os.walk(demo_path):
            for filename in filenames:
                if filename.endswith(n) and filename.startswith('MUT_'):
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
    if x == 0:
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
    return sorted(list(get_file_list_dict(n).keys()))


def get_demo_path():
    demo_path = sg.user_settings_get_entry('-demos folder-', os.path.dirname('C:/NotificatieShiszls/Nieuwemap'))
    return demo_path


def get_global_editor():
    try:    # in case running with old version of PySimpleGUI that doesn't have a global PSG settings path
        global_editor = sg.pysimplegui_user_settings.get('-editor program-')
    except:
        global_editor = ''
    return global_editor


def get_editor():
    try:    # in case running with old version of PySimpleGUI that doesn't have a global PSG settings path
        global_editor = sg.pysimplegui_user_settings.get('-editor program-')
    except:
        global_editor = ''
    user_editor = sg.user_settings_get_entry('-editor program-', '')
    if user_editor == '':
        user_editor = global_editor

    return user_editor

def using_local_editor():
    user_editor = sg.user_settings_get_entry('-editor program-', None)
    return get_editor() ==  user_editor


def advanced_mode():
    return sg.user_settings_get_entry('-advanced mode-', False)


def get_theme():
    # First get the current global theme for PySimpleGUI to use if none has been set for this program
    try:
        global_theme = sg.theme_global()
    except:
        global_theme = sg.theme()
    # Get theme from user settings for this program.  Use global theme if no entry found
    user_theme = sg.user_settings_get_entry('-theme-', '')
    if user_theme == '':
        user_theme = global_theme
    return user_theme

# We handle our code properly. But in case the user types in a flag, the flags are now in the middle of a regex. Ignore this warning.

warnings.filterwarnings("ignore", category=DeprecationWarning)

# New function
def get_line_number(file_path, string):
    lmn = 0
    with open(file_path) as f:
        for num, line in enumerate(f, 1):
            if string.strip() == line.strip():
                lmn = num
    return lmn

def find_in_file(string, demo_files_dict, regex=False, verbose=False, window=None, ignore_case=True, show_first_match=True):
    file_list = []
    num_files = 0

    matched_dict = {}
    for file in demo_files_dict:
        try:
            full_filename = demo_files_dict[file]
            if not demo_files_dict == get_file_list_dict(0):
                full_filename = full_filename[0]
            matches = None

            with open(full_filename, 'rb', 0) as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as s:
                if (regex):
                    window.refresh()
                    matches = re.finditer(bytes("^.*(" + string + ").*$", 'utf-8'), s, re.MULTILINE)
                    if matches:
                        for match in matches:
                            if match is not None:
                                if file not in file_list:
                                    file_list.append(file)
                                    num_files += 1
                                if verbose:
                                    sg.cprint(f"{file}:", c = 'white on green')
                                    sg.cprint(f"{match.group(0).decode('utf-8')}\n")
                else:
                    window.refresh()
                    matches = None
                    if (ignore_case):
                        if (show_first_match):
                            matches = re.search(br'(?i)^' + bytes(".*("+re.escape(string.lower()) + ").*$", 'utf-8'), s, re.MULTILINE)
                        else:
                            matches = re.finditer(br'(?i)^' + bytes(".*("+re.escape(string.lower()) + ").*$", 'utf-8'), s, re.MULTILINE)
                    else:
                        if (show_first_match):
                            matches = re.search(br'^' + bytes(".*("+re.escape(string) + ").*$", 'utf-8'), s, re.MULTILINE)
                        else:
                            matches = re.finditer(br'^' + bytes(".*("+re.escape(string) + ").*$", 'utf-8'), s, re.MULTILINE)
                    if matches:
                        if show_first_match:
                            file_list.append(file)
                            num_files += 1
                            match_array = []
                            match_array.append(matches.group(0).decode('utf-8'))
                            matched_dict[full_filename] = match_array
                        else:
                            # We need to do this because strings are "falsy" in Python, but empty matches still return True...
                            append_file = False
                            match_array = []
                            for match_ in matches:
                                match_str = match_.group(0).decode('utf-8')
                                if match_str:
                                    match_array.append(match_str)
                                    if append_file == False:
                                        append_file = True
                            if append_file:
                                file_list.append(file)
                                num_files += 1
                                matched_dict[full_filename] = match_array

                # del matches
        except ValueError:
            del matches
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(f'{file}', e, file=sys.stderr)

    # Format of the matches dictionary
    # Filename, [num1, num2, num3]
    file_lines_dict = {}
    list_of_matches = []
    if not regex:
        for key in matched_dict:
            head, tail = os.path.split(key)
            # Tails. Don't wanna put Washington in places he doesn't want to be.
            file_array_old = [key]
            file_array_new = []

            if (verbose):
                sg.cprint(f"{tail}:", c='white on green')
            try:
                for _match in matched_dict[key]:
                    line_num_match = get_line_number(key, _match)
                    file_array_new.append(line_num_match)
                    if (verbose):
                        sg.cprint(f"Line: {line_num_match} ", c='white on purple', end='')
                        sg.cprint(f"{_match.strip()}\n")
                    # Make a list of the matches found in this file to add to the dictionry
                    list_of_matches.append(_match.strip())
                file_array_old.append(file_array_new)
                file_lines_dict[tail] = file_array_old
            except:
                pass

        find_in_file.file_list_dict = file_lines_dict

    file_list = list(set(file_list))
    return file_list


def window_choose_line_to_edit(filename, full_filename,  line_num_list):
    # sg.popup('matches previously found for this file:', filename, line_num_list)
    if len(line_num_list) == 1:
        return full_filename, line_num_list[0]
    layout = [[sg.T(f'Choose line from {filename}', font='_ 14')]]
    for line in sorted(set(line_num_list)):
        layout += [[sg.Text(f'Line {line}', key=('-T-', line), enable_events=True)]]
    layout += [[sg.B('Cancel')]]

    window = sg.Window('Open Editor', layout)

    line_chosen = line_num_list[0]
    while True:
        event, values = window.read()
        if event in ('Cancel', sg.WIN_CLOSED):
            line_chosen = None
            break
        # At this point we know a line was chosen
        line_chosen = event[1]
        break

    window.close()
    return full_filename, line_chosen

### EXTRA SHIZZ MCDIZZZ
def execute_py_file_with_pipe_output(pyfile, parms=None, cwd=None, interpreter_command=None, wait=False, pipe_output=False):
    print(pyfile)
    if pyfile[0] != '"' and ' ' in pyfile:
        pyfile = '"'+pyfile+'"'
    try:
        if interpreter_command is not None:
            python_program = interpreter_command
        else:
            python_program = sg.pysimplegui_user_settings.get('-python command-', '')
    except:
        python_program = ''

    if python_program == '':
        python_program = 'python' if sys.platform.startswith('win') else 'python3'
    if parms is not None and python_program:
        sp = execute_command_subprocess_with_pipe_output(python_program, pyfile, parms, wait=wait, cwd=cwd, pipe_output=pipe_output)
    elif python_program:
        sp = execute_command_subprocess_with_pipe_output(python_program, pyfile, wait=wait, cwd=cwd, pipe_output=pipe_output)
    else:
        print('execute_py_file - No interpreter has been configured')
        sp = None
    return sp


def execute_command_subprocess_with_pipe_output(command, *args, wait=False, cwd=None, pipe_output=False):
    try:
        if args is not None:
            expanded_args = ' '.join(args)
            # print('executing subprocess command:',command, 'args:',expanded_args)
            if command[0] != '"' and ' ' in command:
                command = '"'+command+'"'
            # print('calling popen with:', command +' '+ expanded_args)
            # sp = subprocess.Popen(command +' '+ expanded_args, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=cwd)
            if pipe_output:
                sp = subprocess.Popen(command +' '+ expanded_args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
            else:
                sp = subprocess.Popen(command +' '+ expanded_args, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=cwd)
        else:
            sp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        if wait:
            out, err = sp.communicate()
            if out:
                print(out.decode("utf-8"))
            if err:
                print(err.decode("utf-8"))
    except Exception as e:
        print('** Error executing subprocess **', 'Command:', command)
        print('error:', e)
        sp = None
    return sp

# Normally you want to use the PySimpleGUI version of these functions
try:
    execute_py_file = sg.execute_py_file
except:
    execute_py_file = execute_py_file_with_pipe_output

try:
    execute_command_subprocess = sg.execute_command_subprocess
except:
    execute_command_subprocess = execute_command_subprocess_with_pipe_output


### __MAIN__

if __name__ == '__main__':
    try:
        version = sg.version
        version_parts = version.split('.')
        major_version, minor_version = int(version_parts[0]), int(version_parts[1])
        if major_version < 4 or minor_version < 32:
            sg.popup('Warning - Your PySimpleGUI version is less then 4.35.0',
                     'As a result, you will not be able to use the EDIT features of this program',
                     'Please upgrade to at least 4.35.0',
                     f'You are currently running version:',
                     sg.version,
                     background_color='red', text_color='white')
    except Exception as e:
        print(f'** Warning Exception parsing version: {version} **  ', f'{e}')
    login_screen()
    # main()