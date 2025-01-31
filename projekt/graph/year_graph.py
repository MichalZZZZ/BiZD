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

    query = """
    SELECT Year, TotalTicketsSold 
    FROM AnnualTicketSales
    WHERE TO_NUMBER(Year) BETWEEN :start_year AND :end_year
    ORDER BY TO_NUMBER(Year)
    """

    query2 = """
    SELECT Year, TotalRevenue 
    FROM AnnualTicketSales
    WHERE TO_NUMBER(Year) BETWEEN :start_year AND :end_year
    ORDER BY TO_NUMBER(Year)
    """

    cursor.execute("SELECT MIN(Year), MAX(Year) FROM AnnualTicketSales")
    min_year, max_year = cursor.fetchone()

    print(f"Dostępne lata w bazie danych: {min_year}-{max_year}")

    year_range = input("Podaj przedział lat (YYYY-YYYY): ")
    start_year, end_year = year_range.split('-')

    start_year = int(start_year)
    end_year = int(end_year)

    if start_year < min_year or end_year > max_year:
        print(f"Podany przedział lat wykracza poza dostępne dane. Dostępne lata: {min_year}-{max_year}")
    else:
        cursor.execute(query, start_year=start_year, end_year=end_year)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(rows, columns=columns)

        cursor.execute(query2, start_year=start_year, end_year=end_year)
        rows2 = cursor.fetchall()
        columns2 = [col[0] for col in cursor.description]
        df2 = pd.DataFrame(rows2, columns=columns2)

        if df.empty or df2.empty:
            print(f"Brak danych dla przedziału {start_year}-{end_year}.")
        else:
            fig, axs = plt.subplots(1, 2, figsize=(14, 6))

            axs[0].bar(df['YEAR'], df['TOTALTICKETSSOLD'], color='skyblue')
            axs[0].set_xticks(df['YEAR'])
            axs[0].set_xlabel('Year')
            axs[0].set_ylabel('Total Tickets Sold')
            axs[0].set_title(f'Annual Ticket Sales ({start_year}-{end_year})')
            axs[0].tick_params(axis='x', rotation=45)

            axs[1].plot(df2['YEAR'], df2['TOTALREVENUE'], color='skyblue')
            axs[1].set_xticks(df2['YEAR'])
            axs[1].set_xlabel('Year')
            axs[1].set_ylabel('Total Revenue')
            axs[1].set_title(f'Annual Revenue ({start_year}-{end_year})')
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
