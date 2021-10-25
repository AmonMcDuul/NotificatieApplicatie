from sqlite3 import connect
import datetime as dt
import dateutil.relativedelta

thisday = dt.datetime.today().strftime("%Y-%m-%d")
d = dt.datetime.strptime(thisday, "%Y-%m-%d")
d2 = d - dateutil.relativedelta.relativedelta(months=2)

with connect('notification.db') as conn:
    cursor = conn.cursor()
    cursor.execute("select * from logging where date_time < ?", (d2,))
    lijst = []
    for i in cursor:
        lijst.append(i)
    print(lijst)