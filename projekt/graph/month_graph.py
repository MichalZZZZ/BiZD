import oracledb
import pandas as pd
import matplotlib.pyplot as plt

username = 'ziolkowskim'
password = 'michal1'
hostname = '213.184.8.44'
port = '1521'
sid = 'orcl'

list_of_months = ['styczeń', 'luty', 'marzec', 'kwiecień', 'maj', 'czerwiec', 'lipiec', 'sierpień', 'wrzesień', 'październik', 'listopad', 'grudzień']

dsn = oracledb.makedsn(hostname, port, sid)
try:
    year = input("Podaj rok (YYYY): ")

    connection = oracledb.connect(user=username, password=password, dsn=dsn)
    cursor = connection.cursor()

    query = """
    SELECT YearMonth, TotalTicketsSold 
    FROM MonthlyTicketSales
    WHERE SUBSTR(YearMonth, 1, 4) = :year
    """
    cursor.execute(query, year=year)
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(rows, columns=columns)


    query2 = """
    SELECT YearMonth, TotalRevenue 
    FROM MonthlyTicketSales
    WHERE SUBSTR(YearMonth, 1, 4) = :year
    """
    cursor.execute(query2, year=year)
    rows2 = cursor.fetchall()
    columns2 = [col[0] for col in cursor.description]
    df2 = pd.DataFrame(rows2, columns=columns2)

    if df.empty or df2.empty:
        print(f"Brak danych dla roku {year}.")
    else:
        fig, axs = plt.subplots(1, 2, figsize=(14, 6))

        axs[0].bar(list_of_months, df['TOTALTICKETSSOLD'], color='skyblue')
        axs[0].set_xlabel('Month')
        axs[0].set_ylabel('Total Tickets Sold')
        axs[0].set_title(f'Monthly Ticket Sales for {year}')
        axs[0].tick_params(axis='x', rotation=45)

        axs[1].plot(list_of_months, df2['TOTALREVENUE'], color='skyblue')
        axs[1].set_xlabel('Month')
        axs[1].set_ylabel('Total Revenue')
        axs[1].set_title(f'Monthly Revenue for {year}')
        axs[1].tick_params(axis='x', rotation=45)

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
