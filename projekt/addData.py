import oracledb
import json
import re
import datetime

username = 'ziolkowskim'
password = 'michal1'
hostname = '213.184.8.44'
port = '1521'
sid = 'orcl'

dsn = oracledb.makedsn(hostname, port, sid)

def load_data_from_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def validate_phone_stationary(phone):
    pattern = r'^\d{2}-\d{2}-\d{3}$'
    return bool(re.match(pattern, phone)) and phone.replace("-", "").isdigit()

def validate_phone_mobile(phone):
    pattern = r'^\d{3}-\d{3}-\d{3}$'
    return bool(re.match(pattern, phone)) and phone.replace("-", "").isdigit()

def validate_datetime(datetime_str):
    pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
    return bool(re.match(pattern, datetime_str))

def validate_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

def validate_start_end_time(start_time, end_time):
    return start_time < end_time

def validate_ticket_buy_date(buy_date):
    now = datetime.datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    now_timestamp = datetime.datetime.strptime(now_str, '%Y-%m-%d %H:%M:%S')
    buy_date = datetime.datetime.strptime(buy_date, '%Y-%m-%d %H:%M:%S')
    return buy_date > now_timestamp


def insert_data():
    try:
        connection = oracledb.connect(user=username, password=password, dsn=dsn)
        cursor = connection.cursor()

        cinemas = load_data_from_json('projekt/json/cinemas.json')

        auditoriums = load_data_from_json('projekt/json/auditoriums.json')

        movies = load_data_from_json('projekt/json/movies.json')

        showtimes = load_data_from_json('projekt/json/showtimes.json')

        customers = load_data_from_json('projekt/json/customers.json')

        tickets = load_data_from_json('projekt/json/tickets2.json')
        # tickets = load_data_from_json('projekt/json/tickets.json')

        for cinema in cinemas:
            if not validate_phone_stationary(cinema['Phone']):
                print(f"Błąd: Niepoprawny numer telefonu w kinie {cinema['CinemaID']}: {cinema['Phone']}")
                return
        
        for customer in customers:
            if not validate_phone_mobile(customer['Phone']):
                print(f"Błąd: Niepoprawny numer telefonu w kliencie {customer['CustomerID']}: {customer['Phone']}")
                return
            if not validate_email(customer['Email']):
                print(f"Błąd: Niepoprawny email w kliencie {customer['CustomerID']}: {customer['Email']}")
                return

        for showtime in showtimes:
            if not validate_datetime(showtime['StartTime']):
                print(f"Błąd: Niepoprawny format StartTime w showtime {showtime['ShowtimeID']}: {showtime['StartTime']}")
                return
            if not validate_datetime(showtime['EndTime']):
                print(f"Błąd: Niepoprawny format EndTime w showtime {showtime['ShowtimeID']}: {showtime['EndTime']}")
                return
            if not validate_start_end_time(showtime['StartTime'], showtime['EndTime']):
                print(f"Błąd: StartTime musi być mniejszy od EndTime w showtime {showtime['ShowtimeID']}")
                return
            
        for ticket in tickets:
            if not validate_datetime(ticket['DateBuy']):
                print(f"Błąd: Niepoprawny format DateBuy w bilecie {ticket['TicketID']}: {ticket['DateBuy']}")
                return
            # if not validate_ticket_buy_date(ticket['DateBuy']):
            #     print(f"Błąd: Data zakupu biletu nie może być późniejsza niż obecna data w bilecie {ticket['TicketID']}")
            #     return
            

        now = datetime.datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        now_timestamp = datetime.datetime.strptime(now_str, '%Y-%m-%d %H:%M:%S')


        cursor.executemany("INSERT INTO Cinema (CinemaID, Name, Location, Phone) VALUES (:CinemaID, :Name, :Location, :Phone)", cinemas)
        for cinema in cinemas:
            cinema['AddedDate'] = now_timestamp
        cursor.executemany("INSERT INTO ArchivesAddedCinema (CinemaID, Name, Location, Phone, AddedDate) VALUES (:CinemaID, :Name, :Location, :Phone, :AddedDate)", cinemas)


        cursor.executemany("INSERT INTO Movie (MovieID, Title, Genre, Duration, Rating) VALUES (:MovieID, :Title, :Genre, :Duration, :Rating)", movies)
        for movie in movies:
            movie['AddedDate'] = now_timestamp
        cursor.executemany("INSERT INTO ArchivesAddedMovie (MovieID, Title, Genre, Duration, Rating, AddedDate) VALUES (:MovieID, :Title, :Genre, :Duration, :Rating, :AddedDate)", movies)


        cursor.executemany("INSERT INTO Customer (CustomerID, Name, Email, Phone) VALUES (:CustomerID, :Name, :Email, :Phone)", customers)
        for customer in customers:
            customer['AddedDate'] = now_timestamp
        cursor.executemany("INSERT INTO ArchivesAddedCustomer (CustomerID, Name, Email, Phone, AddedDate) VALUES (:CustomerID, :Name, :Email, :Phone, :AddedDate)", customers)


        cursor.executemany("INSERT INTO Auditorium (AuditoriumID, CinemaID, Name, Capacity)VALUES (:AuditoriumID, :CinemaID, :Name, :Capacity)", auditoriums)
        cursor.execute("SELECT CinemaID, Name FROM Cinema")
        cinema_mapping = {row[0]: row[1] for row in cursor.fetchall()}
        for auditorium in auditoriums:
            auditorium['AddedDate'] = now_timestamp
            cinema_id = auditorium.pop('CinemaID')
            auditorium['CinemaName'] = cinema_mapping.get(cinema_id)
        cursor.executemany("INSERT INTO ArchivesAddedAuditorium (AuditoriumID, CinemaName, Name, Capacity, AddedDate)VALUES (:AuditoriumID, :CinemaName, :Name, :Capacity, :AddedDate)", auditoriums)


        cursor.executemany("INSERT INTO Showtime (ShowtimeID, MovieID, AuditoriumID, StartTime, EndTime)VALUES (:ShowtimeID, :MovieID, :AuditoriumID, TO_TIMESTAMP(:StartTime, 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP(:EndTime, 'YYYY-MM-DD HH24:MI:SS'))", showtimes)
        cursor.execute("SELECT MovieID, Title FROM Movie")
        movie_mapping = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute("SELECT AuditoriumID, Name FROM Auditorium")
        auditorium_mapping = {row[0]: row[1] for row in cursor.fetchall()}
        for showtime in showtimes:
            showtime['AddedDate'] = now_timestamp
            movie_id = showtime.pop('MovieID')
            showtime['MovieName'] = movie_mapping.get(movie_id)
            auditorium_id = showtime.pop('AuditoriumID')
            showtime['AuditoriumName'] = auditorium_mapping.get(auditorium_id)
        cursor.executemany("INSERT INTO ArchivesAddedShowtime (ShowtimeID, MovieName, AuditoriumName, StartTime, EndTime, AddedDate)VALUES (:ShowtimeID, :MovieName, :AuditoriumName, TO_TIMESTAMP(:StartTime, 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP(:EndTime, 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP(:AddedDate, 'YYYY-MM-DD HH24:MI:SS'))", showtimes)


        cursor.executemany("INSERT INTO Ticket (TicketID, ShowtimeID, CustomerID, SeatNumbers, Price, CountPerson, Sum, DateBuy) VALUES (:TicketID, :ShowtimeID, :CustomerID, :SeatNumbers, :Price, :CountPerson, :Sum, :DateBuy)", tickets)
        cursor.execute("""SELECT s.ShowtimeID, s.MovieID, m.Title
        FROM Showtime s
        JOIN Movie m ON s.MovieID = m.MovieID""")
        cursor.execute("SELECT MovieID, Title FROM Movie")
        movie_mapping = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute("SELECT CustomerID, Name FROM Customer")
        customer_mapping = {row[0]: row[1] for row in cursor.fetchall()}
        for ticket in tickets:
            ticket['AddedDate'] = now_timestamp
            showtime_id = ticket.pop('ShowtimeID')
            ticket['ShowtimeMovieName'] = movie_mapping.get(showtime_id)
            customer_id = ticket.pop('CustomerID')
            ticket['CustomerName'] = customer_mapping.get(customer_id)

        cursor.executemany("INSERT INTO ArchivesAddedTicket (TicketID, SeatNumbers, Price, CountPerson, Sum, DateBuy, AddedDate, ShowtimeMovieName, CustomerName) VALUES (:TicketID, :SeatNumbers, :Price, :CountPerson, :Sum, :DateBuy, :AddedDate, :ShowtimeMovieName, :CustomerName)", tickets)


        connection.commit()

        print("Dane zostały pomyślnie dodane do bazy.")

    except oracledb.DatabaseError as e:
        print(f"Błąd: {e}")
        if connection:
            connection.rollback()

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

insert_data()
