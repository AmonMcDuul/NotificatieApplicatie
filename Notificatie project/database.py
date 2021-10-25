from sqlite3 import connect
import PySimpleGUI as sg

def active_user():
    with connect('notification.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE active = 1")
        results = ''
        for row in cursor:
            results = row[0]
    return results 

def create_file(filename, omschrijving):
    filename = filename.replace(' ','_')
    activeuser = active_user()
    with connect('notification.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conditie_emails WHERE file_name = ?", (filename,))
        check = len(cursor.fetchall())
        # add to database if not existing, otherwise alert user
        if check == 0:
            cursor.execute("INSERT INTO conditie_emails VALUES(NULL, ?, ?, ?)", (filename, omschrijving, activeuser))
            sg.popup('Filename {} is aangemaakt'.format(filename))
            return True
        else:
            sg.popup_error('Filename {} bestaat al. Voer een andere naam in'.format(filename))
            return False

def create_notif(notification_name, email_name, condition_name, omschrijving, datum, tijd, dagen, ontvanger):
    activeuser = active_user()
    with connect('notification.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notifications WHERE notification = ?", (notification_name,))
        check = len(cursor.fetchall())
        # add to database if not existing, otherwise alert user
        if check == 0:
            cursor.execute("SELECT id FROM conditie_emails WHERE file_name = ?", (email_name[:-4],))
            email_id = ''
            for row in cursor:
                email_id = row[0]
            cursor.execute("SELECT id FROM conditie_emails WHERE file_name = ?", (condition_name[:-4],))
            conditie_id = ''
            for row in cursor:
                conditie_id = row[0]
            cursor.execute("INSERT INTO notifications VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (email_id, conditie_id, notification_name, email_name[:-4], condition_name[:-4], omschrijving, activeuser, datum, tijd, dagen, ontvanger))
            sg.popup('Filename {} is aangemaakt'.format(notification_name))
            return True
        else:
            sg.popup_error('Filename {} bestaat al. Voer een andere naam in'.format(notification_name))
            return False

def create_mutation(notification_name, condition_name, omschrijving, datum):
    activeuser = active_user()
    notification_name
    with connect('notification.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notifications WHERE notification = ?", (notification_name,))
        check = len(cursor.fetchall())
        if check == 0:
            cursor.execute("SELECT id FROM conditie_emails WHERE file_name = ?", (condition_name[:-4],))
            conditie_id = ''
            for row in cursor:
                conditie_id = row[0]
            cursor.execute("INSERT INTO notifications VALUES(NULL, NULL, ?, ?, NULL, ?, ?, ?, ?, NULL, NULL, NULL)", (conditie_id, notification_name, condition_name[:-4], omschrijving, activeuser, datum))
            sg.popup('Filename {} is aangemaakt'.format(notification_name))
            return True
        else:
            sg.popup_error('Filename {} bestaat al. Voer een andere naam in'.format(notification_name))
            return False

def create_statistic(notification_name):
    with connect('notification.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM statistiek WHERE notification_name = ?", (notification_name,))
        check = len(cursor.fetchall())
        # add to database if not existing, otherwise alert user
        if check == 0:
            cursor.execute("INSERT INTO statistiek VALUES(NULL, ?, 0, 0, 0)", (notification_name,))
            return True
        else:
            sg.popup_error('Filename {} bestaat al. Voer een andere naam in'.format(notification_name))
            return False

def delete_notifications(n):
    with connect('notification.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notifications WHERE notification = ?", (n,))
        cursor.execute("DELETE FROM statistiek WHERE notification_name = ?", (n,))

def delete_condition_mail(n):
    with connect('notification.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conditie_emails WHERE file_name = ?", (n,))

def select_all_notifications():
    with connect('notification.db') as conn:
        cursor = conn.cursor()
        cursor.execute("select * from notifications order by notification asc")
        row = cursor.fetchone()
        if row == None:
            lijst = [('','','','','','','','','','','','')]
            return lijst
        lijst = []
        lijst.append(row)
        for i in cursor:     
            lijst.append(i)
        return lijst

def select_all_logging(n):
    with connect('notification.db') as conn:
        cursor = conn.cursor()
        if len(n) < 1:
            cursor.execute("select * from logging order by date_time desc")
        else:
            cursor.execute("select * from logging where notification_name = ? order by date_time desc", (n[:-3],))
        row = cursor.fetchone()
        if row == None:
            lijst = [('','','','','','')]
            return lijst
        lijst = []
        lijst.append(row)
        for i in cursor:
            lijst.append(i)
        return lijst

def select_statistic(n):
    with connect('notification.db') as conn:
        cursor = conn.cursor()
        if len(n) < 1:
            cursor.execute("SELECT *FROM statistiek")
        else:
            cursor.execute("SELECT * FROM statistiek WHERE notification_name = ?", (n[:-3],))
        row = cursor.fetchone()
        if row == None:
            lijst = [('','','','','')]
            return lijst
        lijst = []
        lijst.append(row)
        for i in cursor:
            lijst.append(i)
        return lijst

def get_file_description(n):
    str1 = "" 
    str1 = str1.join(n)
    sep = '.'
    str2 = str1.split(sep, 1)[0]
    if str2.startswith('MUT_'):
        with connect('notification.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT notification, condition_name, omschrijving, gebruiker FROM notifications WHERE notification = ?", (str2,))
            for i in cursor:
                sg.cprint(' Naam mutatie: ''\n',i[0],'\n','\n', 'Naam conditie: ''\n',i[1],'\n','\n', 'Omschrijving: ''\n',i[2],'\n','\n', 'Aanmaker: ''\n',i[3],'\n')        
    elif len(str1.split(sep, 1)[1]) == 2:
        with connect('notification.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT notification, email_name, condition_name, omschrijving, gebruiker, startdatum, tijd, dagen, ontvanger FROM notifications WHERE notification = ?", (str2,))
            for i in cursor:
                sg.cprint(' Naam notificatie: ''\n',i[0],'\n','\n', 'Naam email: ''\n',i[1],'\n','\n', 'Naam conditie: ''\n',i[2],'\n','\n', 'Omschrijving: ''\n',i[3],'\n','\n', 'Aanmaker: ''\n',i[4],'\n','\n', 'Startdatum: ''\n',i[5],'\n','\n', 'Tijd: ''\n',i[6],'\n','\n', 'Dagen: ''\n',i[7],'\n','\n', 'Ontvanger: ''\n',i[8],'\n','\n' )
    else:
        with connect('notification.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_name, omschrijving, gebruiker FROM conditie_emails WHERE file_name = ?", (str2,))
            for i in cursor:
                sg.cprint(' Naam bestand: ''\n',i[0],'\n','\n','Omschrijving: ','\n',i[1],'\n','\n','Aangemaakt door:','\n',i[2],'\n','\n')