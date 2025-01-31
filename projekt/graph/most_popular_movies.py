import oracledb
import pandas as pd
import matplotlib.pyplot as plt

username = 'ziolkowskim'
password = 'michal1'
hostname = '213.184.8.44'
port = '1521'
sid = 'orcl'

dsn = oracledb.makedsn(hostname, port, sid)
try:

    connection = oracledb.connect(user=username, password=password, dsn=dsn)
    cursor = connection.cursor()

    query = "SELECT Title, TicketsSold FROM TopMovies"
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    df2 = pd.DataFrame(rows, columns=columns)

    plt.figure(figsize=(12, 6))
    plt.bar(df2['TITLE'], df2['TICKETSSOLD'], color='skyblue')
    plt.xlabel('Title')
    plt.ylabel('Tickets Sold')
    plt.title('Top Movies')
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.show()

except Exception as e:
    print("Wystąpił błąd:", e)

finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
        print("Połączenie z bazą zostało zamknięte.")