from flask import Flask, render_template, request, session, url_for, redirect, Markup
import pymysql.cursors
import hashlib
import datetime

app = Flask(__name__)
app.secret_key = 'this is a secret key'

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',  # password for MAMP
                       # password='', # password for XAMP/linux
                       db='reservation_system1',
                       # port=5000,
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    else:
        return render_template('index.html')


def filter(text):
    return (
        text.replace("&", "&amp;").
        replace('"', "&quot;").
        replace("<", "&lt;").
        replace(">", "&gt;")
    )


@app.route('/info')
def info():
    return render_template('info.html')


@app.route('/search')
def search():
    if request.args.get('sourceAirport') is None:
        return redirect(url_for('home'))
    else:
        choice = request.args.get('choice')
        if choice == "oneway":
            sourceAirport = filter(request.args.get('sourceAirport'))
            destAirport = filter(request.args.get('destAirport'))
            date = filter(request.args.get('date'))
            
            cursor = conn.cursor()
            query = "SELECT * FROM flight WHERE departure_airport = %s AND arrival_airport = %s AND departure_time LIKE %s AND departure_time BETWEEN NOW() AND NOW() + INTERVAL 1 YEAR"
            date = '%'+date+'%'
            cursor.execute(query, (sourceAirport, destAirport, date))
            data = cursor.fetchall()
            
            if not data:
                noFlights = "No flights found"
                cursor.close()
                if 'username' not in session:
                    username = "Guest"
                else:
                    username = session["username"]
                return render_template('response.html', noFlights=noFlights, username=username)
            else:
                flights = data
                cursor.close()
                if request.args.get('customer') is not None:
                    return render_template('searchCustomer.html', flights=flights)
                elif request.args.get('agent') is not None:
                    return render_template('searchAgent.html', flights=flights)
                else:
                    return render_template('search.html', flights=flights)
        else:
            sourceAirport = filter(request.args.get('sourceAirport'))
            destAirport = filter(request.args.get('destAirport'))
            date = filter(request.args.get('date'))
            returning = filter(request.args.get('returning'))

            cursor = conn.cursor()

            query = "SELECT * FROM flight WHERE departure_airport = %s AND arrival_airport = %s AND departure_time LIKE %s AND departure_time BETWEEN NOW() AND NOW() + INTERVAL 1 YEAR"
            date = '%'+date+'%'
            cursor.execute(query, (sourceAirport, destAirport, date))
            data = cursor.fetchall()

            # query2 = "SELECT arrival_time FROM flight WHERE departure_airport = %s AND arrival_airport = %s AND departure_time LIKE %s AND departure_time BETWEEN NOW() AND NOW() + INTERVAL 1 YEAR"
            # cursor.execute(query2, (sourceAirport, destAirport, date))
            # temp_time = cursor.fetchone()
            # temp_time = temp_time['arrival_time']

            query1 = "SELECT * FROM flight WHERE departure_airport = %s AND arrival_airport = %s AND departure_time LIKE %s AND departure_time BETWEEN NOW() AND NOW() + INTERVAL 1 YEAR"
            returning = '%'+returning+'%'
            cursor.execute(query1, (destAirport, sourceAirport, returning))
            data2 = cursor.fetchall()
            print("------------------------")
            print(data)
            print(data2)
            print("------------------------")
            
            if not data or not data2:
                noFlights = "No flights found"
                cursor.close()
                if 'username' not in session:
                    username = "Guest"
                else:
                    username = session["username"]
                return render_template('response.html', noFlights=noFlights, username=username)
            else:
                flights = data
                second_flights = data2
                cursor.close()
                if request.args.get('customer') is not None:
                    return render_template('searchRoundCustomer.html', flights=flights, second=second_flights, to=destAirport, backto=sourceAirport)
                elif request.args.get('agent') is not None:
                    return render_template('searchRoundAgent.html', flights=flights, second=second_flights, to=destAirport, backto=sourceAirport)
                else:
                    return render_template('searchRound.html', flights=flights, second=second_flights, to=destAirport, backto=sourceAirport)

@app.route('/bookAndPayAgent')
def bookAndPayAgent():
    return render_template('bookAndPayAgent.html')


@app.route('/bookAndPayCustomer')
def bookAndPayCustomer():
    return render_template('bookAndPayCustomer.html')


@app.route('/purchaseTicket', methods=['GET', 'POST'])
def purchaseTicket():
    if 'username' not in session or request.method == "GET":
        return redirect(url_for('home'))
    else:
        airline = filter(request.form['airline'])
        flightNumber = filter(request.form['flightNumber'])
        role = filter(session['role'])
        print(role)

        cursor = conn.cursor()

        query1 = "SELECT seats FROM airplane NATURAL JOIN flight where airline_name = %s AND flight_num = %s"
        cursor.execute(query1, (airline, flightNumber))
        seats_data = cursor.fetchone()
        seats = seats_data['seats']
        print(seats)
        query2 = "SELECT count(ticket_id) FROM ticket WHERE airline_name = %s AND flight_num = %s AND ticket_id  IN (SELECT ticket_id FROM purchases)"
        cursor.execute(query2, (airline, flightNumber))
        already_bought_data = cursor.fetchone()
        already_bought = already_bought_data['count(ticket_id)']
        print(already_bought)

        query = "SELECT ticket_id FROM ticket WHERE airline_name = %s AND flight_num = %s AND ticket_id NOT IN (SELECT ticket_id FROM purchases)"
        cursor.execute(query, (airline, flightNumber))
        data = cursor.fetchone()

        if not data or already_bought == seats:
            noTickets = "No tickets left for this flight"
            cursor.close()

            return render_template('response.html', noTickets=noTickets, username=session['username'])
        else:

            ticket = data

            if already_bought >= 0.7 * seats and role == 'customer':
                update = "UPDATE ticket SET sold_price = 1.20 * sold_price  WHERE ticket_id =  %s "
                cursor.execute(update, (ticket["ticket_id"]))
                get_sell_price = "SELECT sold_price FROM ticket where ticket_id = %s"
                cursor.execute(get_sell_price, (ticket["ticket_id"]))
                get_sell_price_data = cursor.fetchone()
                sold_price = get_sell_price_data['sold_price']
                conn.commit()
                cursor.close()
                ticketBought = "Successfully purchased ticket"

                return render_template('bookAndPayCustomer.html', ticketID=ticket["ticket_id"], airlineName=airline, flightNum=flightNumber, soldPrice=sold_price, username=session['username'])
            elif already_bought <= 0.7*seats and role == 'customer':
                query3 = "SELECT price FROM flight WHERE airline_name = %s AND flight_num = %s"
                cursor.execute(query3, (airline, flightNumber))
                price_data = cursor.fetchone()
                price = price_data['price']

                return render_template('bookAndPayCustomer.html', ticketID=ticket["ticket_id"], airlineName=airline, flightNum=flightNumber, soldPrice=price, username=session['username'])

            else:
                email = filter(request.form['email'])
                emailQuery = "SELECT * FROM customer WHERE email = %s"
                cursor.execute(emailQuery, (email))
                email = cursor.fetchone()
                if not email:
                    error = "No customer has that email address"
                    return render_template('response.html', error=error, username=session['username'])
                else:
                    if already_bought >= 0.7 * seats:
                        update = "UPDATE ticket SET sold_price = 1.20 * sold_price WHERE ticket_id =  %s"
                        cursor.execute(update, (ticket["ticket_id"]))
                        get_sell_price = "SELECT sold_price FROM ticket where ticket_id = %s"
                        cursor.execute(get_sell_price, (ticket["ticket_id"]))
                        get_sell_price_data = cursor.fetchone()
                        sold_price = get_sell_price_data['sold_price']
                        conn.commit()
                        cursor.close()

                        return render_template('bookAndPayAgent.html', email=email["email"], ticketID=ticket["ticket_id"], airlineName=airline, flightNum=flightNumber, soldPrice=sold_price, username=session['id'])
                    else:
                        query4 = "SELECT price FROM flight WHERE airline_name = %s AND flight_num = %s"
                        cursor.execute(query4, (airline, flightNumber))
                        price_data = cursor.fetchone()
                        price = price_data['price']

                        return render_template('bookAndPayAgent.html', email=email["email"], ticketID=ticket["ticket_id"], airlineName=airline, flightNum=flightNumber, soldPrice=price, username=session['id'])


@app.route('/paymentInsertCustomer', methods=['GET', 'POST'])
def paymentInsertCustomer():
    if 'username' not in session or request.method == "GET":
        return redirect(url_for('home'))
    else:
        airline = filter(request.form['airline'])
        flightNumber = filter(request.form['flightNum'])
        customerEmail = filter(request.form['CustomerEmail'])
        updatedPrice = filter(request.form['updatedPrice'])
        ticketID = filter(request.form['ticketID'])
        cardType = filter(request.form['cardType'])
        cardNumber = filter(request.form['cardNumber'])
        NameonCard = filter(request.form['NameonCard'])
        expDate = filter(request.form['expDate']) + "-01"

        role = filter(session['role'])
        cursor = conn.cursor()
        ins = "INSERT INTO purchases VALUES(%s , %s , NULL , %s , %s, %s, CURRENT_TIMESTAMP(), %s)"
        cursor.execute(ins, (ticketID, customerEmail,
                             cardType, cardNumber, NameonCard, expDate))
        conn.commit()
        cursor.close()
        ticketBought = "Successfully purchased ticket"

        return render_template('response.html', ticketBought=ticketBought, username=session['username'])


@app.route('/paymentInsertAgent', methods=['GET', 'POST'])
def paymentInsertAgent():
    if 'username' not in session or request.method == "GET":
        return redirect(url_for('home'))
    else:
        username = session['username']
        airline = filter(request.form['airline'])
        flightNumber = filter(request.form['flightNum'])
        customerEmail = filter(request.form['CustomerEmail'])
        updatedPrice = filter(request.form['updatedPrice'])
        ticketID = filter(request.form['ticketID'])
        cardType = filter(request.form['cardType'])
        cardNumber = filter(request.form['cardNumber'])
        NameonCard = filter(request.form['NameonCard'])
        expDate = filter(request.form['expDate']) + "-01"
        role = filter(session['role'])
        cursor = conn.cursor()
        ins = "INSERT INTO purchases VALUES(%s , %s , %s , %s , %s, %s, CURRENT_TIMESTAMP(), %s)"
        print(customerEmail)
        cursor.execute(ins, (ticketID, customerEmail, username,
                             cardType, cardNumber, NameonCard, expDate))
        conn.commit()
        cursor.close()
        ticketBought = "Successfully purchased ticket"

        return render_template('response.html', ticketBought=ticketBought, username=session['username'])


@app.route('/status')
def status():
    airline = filter(request.args.get('airline'))
    flightNumber = filter(request.args.get('flightNumber'))

    cursor = conn.cursor()
    query = "SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s"
    cursor.execute(query, (airline, flightNumber))
    data = cursor.fetchone()
    if not data:
        noFlight = "No flight found"
        cursor.close()
        return render_template('status.html', noFlight=noFlight)
    else:
        flight = data
        cursor.close()
        return render_template('status.html', flight=flight)


@app.route('/home')
def home():
    if 'username' in session:
        username = session['username']
        if session['role'] == "customer":
            cursor = conn.cursor()
            query = "SELECT * FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE customer_email = %s AND departure_time BETWEEN NOW() AND NOW() + INTERVAL 1 YEAR"
            query2 = "SELECT * FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE customer_email = %s AND arrival_time BETWEEN NOW() - INTERVAL 1 YEAR AND NOW()"
            cursor.execute(query, (username))
            data_upcoming = cursor.fetchall()
            cursor.execute(query2, (username))
            data_previous = cursor.fetchall()
            cursor.close()
            previousflights = data_previous
            upComingflights = data_upcoming

            return render_template('homeCustomer.html', username=username, upComingflights=upComingflights, previousflights=previousflights)
        elif session['role'] == "staff":
            airline = session['company']
            cursor = conn.cursor()
            query = "SELECT * FROM flight WHERE airline_name = %s AND departure_time BETWEEN NOW() AND NOW() + INTERVAL 30 DAY"

            cursor.execute(query, (airline))
            data = cursor.fetchall()
            cursor.close()
            flights = data
            return render_template('homeStaff.html', username=username, airline=airline, flights=flights)
        elif session['role'] == "agent":
            cursor = conn.cursor()
            agentEmail = session['username']
            query = "SELECT * FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE agent_email = %s AND departure_time BETWEEN NOW() AND NOW() + INTERVAL 1 YEAR"
            query2 = "SELECT * FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE agent_email = %s AND arrival_time BETWEEN NOW() - INTERVAL 1 YEAR AND NOW()"
            cursor.execute(query, (agentEmail))
            data = cursor.fetchall()
            cursor.execute(query2, (username))
            data_previous = cursor.fetchall()
            cursor.close()
            flights = data
            previousflights = data_previous
            return render_template('homeAgent.html', username=username, flights=flights, previousflights = previousflights)
    else:
            return render_template('index.html')


@app.route('/newFlight', methods=['GET', 'POST'])
def newFlight():
    if request.method == "GET" or session.get('role') != "staff":
        return redirect(url_for('home'))
    else:
        airline = filter(request.form["airline"])
        flightNumber = filter(request.form["flightNumber"])
        departureAirport = filter(request.form["departureAirport"])
        departureTime = filter(request.form["departureTime"])
        arrivalAirport = filter(request.form["arrivalAirport"])
        arrivalTime = filter(request.form["arrivalTime"])
        price = filter(request.form["price"])
        status = filter(request.form["status"])
        airplaneID = filter(request.form["airplaneID"])

        cursor = conn.cursor()
        ins = 'INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (airline, flightNumber, departureAirport, departureTime, arrivalAirport, arrivalTime, price, status, airplaneID))
        conn.commit()
        cursor.close()
        newFlight = "Successfully created new flight"
        return render_template('response.html', newFlight=newFlight, username=session['username'])


@app.route('/allFlights')
def allFlights():
    if session.get('role') != "staff":
        return redirect(url_for('home'))
    else:
        airline = session['company']
        cursor = conn.cursor()
        query = 'SELECT * FROM flight WHERE airline_name = %s'
        cursor.execute(query, (airline))
        data = cursor.fetchall()
        flights = data
        cursor.close()
        return render_template('allFlights.html', flights=flights, airline=airline)


@app.route('/allFlightsFiltered')
def allFlightsFiltered():
    if session.get('role') != "staff" or request.args.get('start') is None:
        return redirect(url_for('home'))
    else:
        if request.args.get('date') == "yes":
            start = filter(request.args.get('start'))
            end = filter(request.args.get('end'))
            airline = session['company']

            cursor = conn.cursor()
            query = "SELECT * FROM flight WHERE airline_name = %s AND departure_time BETWEEN %s AND %s"
            cursor.execute(query, (airline, start, end))
            data = cursor.fetchall()
            flights = data
            cursor.close()
            return render_template('allFlightsFiltered.html', flights=flights, airline=airline)
        elif request.args.get('airport') == "yes":
            start = filter(request.args.get('start'))
            end = filter(request.args.get('end'))
            airline = session['company']

            cursor = conn.cursor()
            query = "SELECT * FROM flight WHERE airline_name = %s AND departure_airport = %s AND arrival_airport = %s"
            cursor.execute(query, (airline, start, end))
            data = cursor.fetchall()
            flights = data
            cursor.close()
            return render_template('allFlightsFiltered.html', flights=flights, airline=airline)


@app.route('/flightCustomers')
def flightCustomers():
    if session.get('role') != "staff" or request.args.get('airline') is None:
        return redirect(url_for('home'))
    else:
        airline = request.args.get('airline')
        flightNumber = request.args.get('flightNumber')

        cursor = conn.cursor()
        query = "SELECT * FROM purchases NATURAL JOIN ticket WHERE airline_name = %s AND flight_num = %s"
        cursor.execute(query, (airline, flightNumber))
        data = cursor.fetchall()
        cursor.close()
        return render_template('customers.html', customers=data, airline=airline, flightNumber=flightNumber)


@app.route('/changeStatus')
def changeStatus():
    if session.get('role') != "staff" or request.args.get('flightNumber') is None:
        return redirect(url_for('home'))
    else:
        airline = session['company']
        status = filter(request.args.get('status'))
        flightNumber = filter(request.args.get('flightNumber'))
        cursor = conn.cursor()

        query2 = "SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s"
        cursor.execute(query2, (airline, flightNumber))
        data = cursor.fetchall()

        if data: 

            query = "UPDATE flight SET status = %s WHERE airline_name = %s AND flight_num = %s"
            cursor.execute(query, (status, airline, flightNumber))
            conn.commit()
            cursor.close()
            statusChange = "Flight's status successfully changed."
            return render_template('response.html', statusChange=statusChange, username=session['username'])

        else:
            declareavar = "Flight not found"
            return render_template('response.html', statusChange=declareavar, username=session['username'])




@app.route('/allAirplanes')
def allAirplanes():
    if session.get('role') != "staff":
        return redirect(url_for('home'))
    else:
        airline = session['company']
        cursor = conn.cursor()
        query = "SELECT * FROM airplane WHERE airline_name = %s"
        cursor.execute(query, (airline))
        data = cursor.fetchall()
        cursor.close()
        return render_template('airplanes.html', airline=airline, airplanes=data)


@app.route('/addAirplane', methods=['GET', 'POST'])
def addAirplane():
    if session.get('role') != "staff" or request.method == "GET" or request.form["airplaneID"] is None:
        return redirect(url_for('home'))
    else:
        airline = session['company']
        airplaneID = filter(request.form["airplaneID"])
        seats = filter(request.form["seats"])

        cursor = conn.cursor()
        query = "SELECT * FROM airplane WHERE airline_name = %s AND airplane_id = %s"
        cursor.execute(query, (airline, airplaneID))
        data = cursor.fetchone()
        if(data):
            airplaneExists = "Airplane already exists"
            cursor.close()
            return render_template('response.html', airplaneExists=airplaneExists, username=session['username'])
        else:
            ins = "INSERT INTO airplane VALUES(%s, %s, %s)"
            cursor.execute(ins, (airline, airplaneID, seats))
            query = "SELECT * FROM airplane WHERE airline_name = %s"
            cursor.execute(query, (airline))
            data2 = cursor.fetchall()
            conn.commit()
            cursor.close()
            newAirplane = "Airplane successfully added"
            return render_template('airplanes.html', airplanes = data2, airline = airline )


@app.route('/addAirport', methods=['GET', 'POST'])
def addAirport():
    if session.get('role') != "staff" or request.method == "GET" or request.form["name"] is None:
        return redirect(url_for('home'))
    else:
        name = filter(request.form['name'])
        city = filter(request.form['city'])
        cursor = conn.cursor()
        query = "SELECT * FROM airport WHERE airport_name = %s"
        cursor.execute(query, (name))
        data = cursor.fetchone()
        if(data):
            airportExists = "Airport already exists"
            cursor.close()
            return render_template('response.html', airportExists=airportExists, username=session['username'])
        else:
            ins = "INSERT INTO airport VALUES(%s, %s)"
            cursor.execute(ins, (name, city))
            conn.commit()
            cursor.close()
            newAirport = "Airport successfully added"
            return render_template('response.html', newAirport=newAirport, username=session['username'])

@app.route('/addPhone', methods=['GET', 'POST'])
def addPhone():
    if request.method == "GET":
        return redirect(url_for('home'))
    else:
        username = filter(request.form['username'])
        phone_num = filter(request.form['phone_num'])

        cursor = conn.cursor()
        query = "INSERT INTO phone VALUES (%s, %s)"
        cursor.execute(query, (username, phone_num))
        conn.commit()
        cursor.close()
        newPhone = "Phone number successfully added"
        return render_template('response.html', newAirport = newPhone, username=session['username'])

@app.route('/Agents')
def Agents():
    if session.get('role') != "staff":
        return redirect(url_for('home'))
    else:
        cursor = conn.cursor()
        query1 = "SELECT * FROM booking_agent"
        cursor.execute(query1)
        Agents = cursor.fetchall()
        #query2 = "SELECT COUNT(sold_price) AS count, booking_agent.email, booking_agent.booking_agent_id FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent WHERE purchase_datetime BETWEEN NOW() - INTERVAL 30 DAY AND NOW() GROUP BY booking_agent.email ORDER BY COUNT(sold_price) DESC LIMIT 5"
        query2 = "SELECT COUNT(ticket_id) as Count, agent_email FROM purchases NATURAL JOIN ticket WHERE agent_email IS NOT NULL AND purchase_datetime BETWEEN NOW() - INTERVAL 30 DAY AND NOW() GROUP BY agent_email ORDER BY Count DESC LIMIT 5"
        cursor.execute(query2)
        topFiveMonth = cursor.fetchall()
        #query3 = "SELECT COUNT(sold_price) AS count, booking_agent.email, booking_agent.booking_agent_id FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent WHERE purchase_datetime BETWEEN NOW() - INTERVAL 1 YEAR AND NOW() GROUP BY booking_agent.email ORDER BY COUNT(sold_price) DESC LIMIT 5"
        query3 = "SELECT COUNT(ticket_id) as Count, agent_email FROM purchases NATURAL JOIN ticket WHERE agent_email IS NOT NULL AND purchase_datetime BETWEEN NOW() - INTERVAL 1 YEAR AND NOW() GROUP BY agent_email ORDER BY Count DESC LIMIT 5"
        cursor.execute(query3)
        topFiveYear = cursor.fetchall()
        #query4 = "SELECT SUM(sold_price*.10) AS sum, booking_agent.email, booking_agent.booking_agent_id FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent WHERE purchase_datetime BETWEEN NOW() - INTERVAL 1 YEAR AND NOW() GROUP BY booking_agent.email ORDER BY SUM(sold_price*.10) DESC LIMIT 5"
        query4 = "SELECT SUM(sold_price * .10) AS Sum, agent_email FROM purchases NATURAL JOIN ticket WHERE agent_email IS NOT NULL AND purchase_datetime BETWEEN NOW() - INTERVAL 1 YEAR AND NOW() GROUP BY agent_email ORDER BY Sum DESC LIMIT 5"
        cursor.execute(query4)
        topFiveCom = cursor.fetchall()
        print(topFiveCom)
        cursor.close()
        return render_template('Agents.html', agents=Agents, topFiveMonth=topFiveMonth, topFiveYear=topFiveYear, topFiveCom=topFiveCom)


@app.route('/customerInfo')
def customerInfo():
    if session.get('role') != "staff":
        return redirect(url_for('home'))
    else:
        airline = session['company']
        cursor = conn.cursor()
        query1 = "SELECT COUNT(ticket_id) as count, customer_email FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE airline_name = %s AND purchase_datetime BETWEEN NOW() - INTERVAL 1 YEAR AND NOW() GROUP BY customer_email ORDER BY COUNT(ticket_id) DESC LIMIT 1"
        cursor.execute(query1, (airline))
        customers = cursor.fetchall()
        cursor.close()
        return render_template('customerInfo.html', customers=customers)


@app.route('/flightsTaken')
def flightsTaken():
    if session.get('role') != "staff" or request.args.get('email') is None:
        return redirect(url_for('home'))
    else:
        email = filter(request.args.get('email'))
        airline = session['company']

        cursor = conn.cursor()
        query = "SELECT * FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE customer_email = %s AND airline_name = %s AND departure_time < CURRENT_TIMESTAMP"
        cursor.execute(query, (email, airline))
        flights = cursor.fetchall()
        cursor.close()
        return render_template('flightsTaken.html', flights=flights, email=email)


@app.route('/viewReports')
def viewReports():
    if session.get('role') != "staff":
        return redirect(url_for('home'))
    else:
        airline = session['company']

        cursor = conn.cursor()
        query1 = "SELECT COUNT(ticket_id) as count FROM purchases NATURAL JOIN ticket WHERE airline_name = %s AND purchase_datetime BETWEEN NOW() - INTERVAL 1 YEAR AND NOW()"
        cursor.execute(query1, (airline))
        lastYear = cursor.fetchone()
        
        query2 = "SELECT COUNT(ticket_id) as count FROM purchases NATURAL JOIN ticket WHERE airline_name = %s AND purchase_datetime BETWEEN NOW() - INTERVAL 30 DAY AND NOW()"
        cursor.execute(query2, (airline))
        lastMonth = cursor.fetchone()
        query3 = "SELECT COUNT(ticket_id) as count_month, DATE_FORMAT(purchase_datetime , '%%b %%Y') as datee FROM purchases NATURAL JOIN ticket WHERE airline_name = %s AND purchase_datetime BETWEEN NOW() - INTERVAL 1 YEAR AND NOW() GROUP BY month(purchase_datetime), year(purchase_datetime) ORDER BY datee DESC"
        cursor.execute(query3, (airline))
        count_month = cursor.fetchall()
        query4 = "select DATE_FORMAT(m1, '%b %Y') from ( select (DATE_ADD(CURRENT_DATE, INTERVAL -1 YEAR) - INTERVAL DAYOFMONTH(DATE_ADD(CURRENT_DATE, INTERVAL -1 YEAR))-1 DAY) +INTERVAL m MONTH as m1 from ( select @rownum:=@rownum+1 as m from (select 1 union select 2 union select 3 union select 4) t1, (select 1 union select 2 union select 3 union select 4) t2, (select 1 union select 2 union select 3 union select 4) t3, (select 1 union select 2 union select 3 union select 4) t4, (select @rownum:=-1) t0 ) d1 ) d2 where m1<= CURRENT_DATE order by m1 DESC LIMIT 13"
        cursor.execute(query4)
    
        labels = cursor.fetchall()
        list = {
            k: [d.get(k) for d in labels]
            for k in set().union(*labels)
        }
        print(list["DATE_FORMAT(m1, '%b %Y')"])
        # query3 = "SELECT COUNT(sold_price) FROM purchases AS COUNT NATURAL JOIN ticket WHERE booking_agent_id = %s AND purchase_datetime BETWEEN NOW() - INTERVAL 30 DAY AND NOW()"
        # cursor.execute(query3, (agentID))
        # lastThirtyDays = cursor.fetchone()
        print(count_month)
        lis = {
            k: [d.get(k) for d in count_month]
            for k in set().union(*count_month)
        }
        datalist = [0]*len(list["DATE_FORMAT(m1, '%b %Y')"])
        if len(lis) == 0:
            datalist = datalist
        else:
            for i in range(len(lis["count_month"])):
                for k in range(len(list["DATE_FORMAT(m1, '%b %Y')"])):
                    if lis["datee"][i] == list["DATE_FORMAT(m1, '%b %Y')"][k]:
                        datalist[k] = lis["count_month"][i]
                

        
        
        cursor.close()
        return render_template('viewReports.html', lastYear=lastYear, lastMonth=lastMonth, data = datalist, labels = list["DATE_FORMAT(m1, '%b %Y')"], max = max(datalist))


@app.route('/viewReportsDate')
def viewReportsDate():
    if session.get('role') != "staff" or request.args.get('start') is None:
        return redirect(url_for('home'))
    else:
        airline = session['company']
        start = filter(request.args.get('start'))
        end = filter(request.args.get('end'))
        cursor = conn.cursor()
        query = "SELECT COUNT(ticket_id) as count FROM purchases NATURAL JOIN ticket WHERE airline_name = %s AND purchase_datetime BETWEEN %s AND %s"
        cursor.execute(query, (airline, start, end))
        date = cursor.fetchone()
        query2 = "SELECT COUNT(ticket_id) as count_month , DATE_FORMAT(purchase_datetime , '%%b %%Y') as datee FROM purchases NATURAL JOIN ticket WHERE airline_name = %s AND purchase_datetime BETWEEN %s AND %s GROUP BY month(purchase_datetime), year(purchase_datetime) ORDER BY datee DESC "
        # query2 = "SELECT SUM(sold_price) AS SUM_MONTH , month(purchase_datetime) as MONTH, year(purchase_datetime) as YEAR FROM purchases NATURAL JOIN ticket WHERE customer_email = %s AND purchase_datetime BETWEEN %s AND %s GROUP BY month(purchase_datetime), year(purchase_datetime) ORDER BY month(purchase_datetime), year(purchase_datetime) ASC"
        cursor.execute(query2, (airline, start, end))
        count_month = cursor.fetchall()
        print(count_month)
        query3 = "SELECT abs(datediff(%s, %s)) as 'INTERVAL' "
        cursor.execute(query3 , (start, end))
        interval = cursor.fetchone()
        print(interval['INTERVAL'])
        # # print(interval)
        # # cursor.execute(query2, (username, start, end))
        # # spendingMonthly = cursor.fetchall()
        query4 =  "select DATE_FORMAT(m1, '%%b %%Y') from ( select (DATE_ADD(%s, INTERVAL -%s DAY) - INTERVAL DAYOFMONTH(DATE_ADD(%s, INTERVAL -%s DAY))-1 DAY) +INTERVAL m MONTH as m1 from ( select @rownum:=@rownum+1 as m from (select 1 union select 2 union select 3 union select 4) t1, (select 1 union select 2 union select 3 union select 4) t2, (select 1 union select 2 union select 3 union select 4) t3, (select 1 union select 2 union select 3 union select 4) t4, (select @rownum:=-1) t0 ) d1 ) d2 where m1<= %s  order by m1 DESC "
        cursor.execute(query4 , (end, interval["INTERVAL"], end , interval["INTERVAL"], end))
        labels = cursor.fetchall()
        print(labels)
        list = {
            k: [d.get(k) for d in labels]
            for k in set().union(*labels)
        }
        print(list["DATE_FORMAT(m1, '%b %Y')"])
        # cursor.execute(query3, (start, end))
        lis = {
            k: [d.get(k) for d in count_month]
            for k in set().union(*count_month)
        }
        datalist = [0]*len(list["DATE_FORMAT(m1, '%b %Y')"])
        if len(lis) == 0:
            datalist = datalist
        else:
            for i in range(len(lis["count_month"])):
                for k in range(len(list["DATE_FORMAT(m1, '%b %Y')"])):
                    if lis["datee"][i] == list["DATE_FORMAT(m1, '%b %Y')"][k]:
                        datalist[k] = lis["count_month"][i]
                

        
            
        
        
        cursor.close()
        return render_template('viewReportsDate.html', date=date, start=start, end=end , data = datalist, labels = list["DATE_FORMAT(m1, '%b %Y')"], max = max(datalist))


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/registerCustomer')
def registerCustomer():
    return render_template('registerCustomer.html')


@app.route('/registerAgent')
def registerAgent():
    return render_template('registerAgent.html')


@app.route('/registerStaff')
def registerStaff():
    return render_template('registerStaff.html')


@app.route('/registerCustomerAuth', methods=['GET', 'POST'])
def registerCustomerAuth():
    if request.method == "GET":
        return redirect(url_for('home'))
    else:
        email = filter(request.form['email'])
        name = filter(request.form['name'])
        origPassword = request.form['password'].encode('latin1')
        password = hashlib.md5(origPassword).hexdigest()
        building = filter(request.form['building'])
        street = filter(request.form['street'])
        city = filter(request.form['city'])
        state = filter(request.form['state'])
        phone = filter(request.form['phone'])
        passportNum = filter(request.form['passportNum'])
        passportExp = filter(request.form['passportExp'])
        passportCountry = filter(request.form['passportCountry'])
        dob = filter(request.form['dob'])

        cursor = conn.cursor()
        query = 'SELECT * FROM customer WHERE email = %s'
        cursor.execute(query, (email))
        data = cursor.fetchone()

        if data:
            error = "User already exists"
            cursor.close()
            return render_template('registerCustomer.html', error=error)
        else:
            ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(ins, (email, name, password, building, street, city,
                                 state, phone, passportNum, passportExp, passportCountry, dob))
            conn.commit()
            cursor.close()
            register = "Succesfully registered user"
            return render_template('index.html', register=register)


@app.route('/registerAgentAuth', methods=['GET', 'POST'])
def registerAgentAuth():
    if request.method == "GET":
        return redirect(url_for('home'))
    else:
        email = filter(request.form['email'])
        origPassword = request.form['password'].encode('latin1')
        password = hashlib.md5(origPassword).hexdigest()
        agentID = filter(request.form['agentID'])
        cursor = conn.cursor()
        query = 'SELECT * FROM booking_agent WHERE email = %s'
        cursor.execute(query, (email))
        data = cursor.fetchone()

        if data:
            error = "User already exists"
            cursor.close()
            return render_template('registerAgent.html', error=error)
        else:
            ins = 'INSERT INTO booking_agent VALUES(%s, %s, %s)'
            cursor.execute(ins, (email, password, agentID))
            conn.commit()
            cursor.close()
            register = "Succesfully registered user"
            return render_template('index.html', register=register)


@app.route('/registerStaffAuth', methods=['GET', 'POST'])
def registerStaffAuth():
    if request.method == "GET":
        return redirect(url_for('home'))
    else:
        username = filter(request.form['username'])
        origPassword = request.form['password'].encode('latin1')
        password = hashlib.md5(origPassword).hexdigest()
        firstName = filter(request.form['firstName'])
        lastName = filter(request.form['lastName'])
        dob = filter(request.form['dob'])
        airline = filter(request.form['airline'])
        phone = filter(request.form['phone'])

        cursor = conn.cursor()
        query = 'SELECT * FROM airline_staff WHERE username = %s'
        cursor.execute(query, (username))
        data = cursor.fetchone()

        if data:
            error = "User already exists"
            cursor.close()
            return render_template('registerStaff.html', error=error)
        else:
            tempQuery = 'SELECT * FROM airline WHERE airline_name = %s'
            cursor.execute(tempQuery, (airline))
            data = cursor.fetchone()
            if not data:
                error = "No such airline exists"
                cursor.close()
                return render_template('registerStaff.html', error=error)
            else:
                ins = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
                query1 = 'INSERT INTO phone VALUES (%s, %s)'
                print(phone)
                cursor.execute(ins, (username, password, firstName, lastName, dob, airline))
                cursor.execute(query1, (username, phone))
                conn.commit()
                cursor.close()
                register = "Succesfully registered user"
                return render_template('index.html', register=register)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/loginCustomer')
def loginCustomer():
    return render_template('loginCustomer.html')


@app.route('/loginStaff')
def loginStaff():
    return render_template('loginStaff.html')


@app.route('/loginAgent')
def loginAgent():
    return render_template('loginAgent.html')


@app.route('/loginCustomerAuth', methods=['GET', 'POST'])
def loginCustomerAuth():
    if request.method == "GET":
        return redirect(url_for('home'))
    else:
        email = filter(request.form['email'])
        origPassword = request.form['password'].encode('latin1')
        password = hashlib.md5(origPassword).hexdigest()

        cursor = conn.cursor()
        query = 'SELECT * FROM customer WHERE email = %s AND password = %s'
        cursor.execute(query, (email, password))

        data = cursor.fetchone()
        cursor.close()
        if data:
            session['username'] = email
            session['role'] = "customer"
            return redirect(url_for('home'))
        else:
            error = "Invalid username or password"
            return render_template('loginCustomer.html', error=error)


@app.route('/loginStaffAuth', methods=['GET', 'POST'])
def loginStaffAuth():
    if request.method == "GET":
        return redirect(url_for('home'))
    else:
        username = filter(request.form['username'])
        origPassword = request.form['password'].encode('latin1')
        password = hashlib.md5(origPassword).hexdigest()

        cursor = conn.cursor()
        query = 'SELECT * FROM airline_staff WHERE username = %s AND password = %s'
        cursor.execute(query, (username, password))

        data = cursor.fetchone()
        cursor.close()
        if data:
            session['username'] = username
            session['role'] = "staff"
            session['company'] = data["airline_name"]
            return redirect(url_for('home'))
        else:
            error = "Invalid username or password"
            return render_template('loginStaff.html', error=error)


@app.route('/loginAgentAuth', methods=['GET', 'POST'])
def loginAgentAuth():
    if request.method == "GET":
        return redirect(url_for('home'))
    else:
        email = filter(request.form['email'])
        origPassword = request.form['password'].encode('latin1')
        password = hashlib.md5(origPassword).hexdigest()
        agentID = filter(request.form['id'])

        cursor = conn.cursor()
        query = 'SELECT * FROM booking_agent WHERE email = %s AND password = %s AND booking_agent_id = %s'
        cursor.execute(query, (email, password, agentID))

        data = cursor.fetchone()
        cursor.close()
        if data:
            session['username'] = email
            session['role'] = "agent"
            session['id'] = data["booking_agent_id"]
            return redirect(url_for('home'))
        else:
            error = "Invalid username or password or booking agent ID"
            return render_template('loginAgent.html', error=error)


@app.route('/topCustomers')
def topCustomers():
    if request.method == "POST":
        return redirect(url_for('home'))
    else:
        cursor = conn.cursor()

        email = session['username']

        Booking = "SELECT booking_agent_id FROM booking_agent WHERE email = %s"
        cursor.execute(Booking, (email))
        data = cursor.fetchone()
        BA = data["booking_agent_id"]

        six_months = "SELECT name, sum(ticket.sold_price * 0.1) as val FROM purchases, customer, ticket WHERE agent_email = %s AND customer_email = email AND ticket.ticket_id = purchases.ticket_id AND purchase_datetime BETWEEN NOW() - INTERVAL 1 YEAR AND NOW() GROUP BY customer.name ORDER BY COUNT(customer_email) DESC LIMIT 5"
        last_year = "SELECT name, COUNT(ticket_id) as val FROM purchases, customer WHERE agent_email = %s AND customer_email = email AND purchase_datetime BETWEEN NOW() - INTERVAL 1 YEAR AND NOW() GROUP BY customer.name ORDER BY COUNT(customer_email) DESC LIMIT 5"

        cursor.execute(six_months, (email))
        data6m = cursor.fetchall()

        cursor.execute(last_year, (email))
        data1y = cursor.fetchall()
        print(data1y)
        lis1y = {
            k: [d.get(k) for d in data1y]
            for k in set().union(*data1y)
        }

        lis6m = {
            k: [d.get(k) for d in data6m]
            for k in set().union(*data6m)
        }
        cursor.close()
        print(lis1y['name'])
        return render_template('topCustomers.html', agent=email, BA1y=lis1y["name"], count1y=lis1y['val'], BA6m=lis6m["name"], count6m=lis6m['val'], max1y=max(lis1y['val']), max6m=max(lis6m['val']))


@app.route('/topthreedests', methods=["GET", "POST"])
def topthreedests():
    if request.method == "POST":
        return redirect(url_for('home'))
    else:
        cursor = conn.cursor()

        username = session['username']

        airline = "SELECT airline_name FROM airline_staff WHERE username = %s"
        cursor.execute(airline, (username))
        data = cursor.fetchone()
        airline_name = data["airline_name"]

        last_year = "SELECT airport_city FROM airport, flight NATURAL JOIN ticket NATURAL JOIN purchases NATURAL JOIN airline_staff WHERE airline_name = %s AND airport_name = flight.arrival_airport AND purchase_datetime BETWEEN NOW() - INTERVAL 1 YEAR AND NOW() GROUP BY airport_name ORDER BY COUNT(ticket_id) DESC LIMIT 3"
        three_months = "SELECT airport_city FROM airport, flight NATURAL JOIN ticket NATURAL JOIN purchases NATURAL JOIN airline_staff WHERE airline_name = %s AND airport_name = flight.arrival_airport AND purchase_datetime BETWEEN NOW() - INTERVAL 3 MONTH AND NOW() GROUP BY airport_name ORDER BY COUNT(ticket_id) DESC LIMIT 3"
        cursor.execute(last_year, (airline_name))
        data1y = cursor.fetchall()

        cursor.execute(three_months, (airline_name))
        data3m = cursor.fetchall()

        lis1y = {
            k: [d.get(k) for d in data1y]
            for k in set().union(*data1y)
        }

        lis3m = {
            k: [d.get(k) for d in data3m]
            for k in set().union(*data3m)
        }
        cursor.close()
        if lis3m or lis1y:
            return render_template('topthreedests.html', airports1y=lis1y["airport_city"], airports3m=lis3m['airport_city'])

        else:
            varlk = "No data"
            return render_template('response.html', error=varlk, username = username) 

@app.route('/commission')
def commission():
    if 'username' not in session or session.get('role') != "agent":
        return redirect(url_for('home'))
    else:
        username = session['username']
        agentID = session['id']
        cursor = conn.cursor()
        query1 = "SELECT SUM(sold_price*.10) AS SUM FROM purchases NATURAL JOIN ticket WHERE agent_email = %s AND purchase_datetime BETWEEN NOW() - INTERVAL 30 DAY AND NOW()"
        cursor.execute(query1, (username))
        totalCommission = cursor.fetchone()
        query2 = "SELECT AVG(sold_price*.10) FROM purchases NATURAL JOIN ticket WHERE agent_email = %s AND purchase_datetime BETWEEN NOW() - INTERVAL 30 DAY AND NOW()"
        cursor.execute(query2, (username))
        averageCommission = cursor.fetchone()
        query3 = "SELECT COUNT(sold_price) FROM purchases AS COUNT NATURAL JOIN ticket WHERE agent_email = %s AND purchase_datetime BETWEEN NOW() - INTERVAL 30 DAY AND NOW()"
        cursor.execute(query3, (username))
        lastThirtyDays = cursor.fetchone()

        return render_template("commission.html", username=username, totalCommission=totalCommission["SUM"], averageCommission="{0:.2f}".format(averageCommission["AVG(sold_price*.10)"]), lastThirtyDays=lastThirtyDays["COUNT(sold_price)"])


@app.route('/commissionDetailed')
def commissionDetailed():
    if 'username' not in session or request.args.get('start') is None or session.get('role') != "agent":
        return redirect(url_for('commission'))
    else:
        username = session['username']
        agentID = session['id']
        start = filter(request.args.get('start'))
        end = filter(request.args.get('end'))

        cursor = conn.cursor()
        query1 = "SELECT SUM(sold_price*.10) AS SUM FROM purchases NATURAL JOIN ticket WHERE agent_email = %s AND purchase_datetime BETWEEN %s AND %s"
        cursor.execute(query1, (username, start, end))
        totalCommission = cursor.fetchone()
        if totalCommission["SUM"] is None:
            totalCommission["SUM"] = 0
        query2 = "SELECT COUNT(sold_price) FROM purchases AS COUNT NATURAL JOIN ticket WHERE agent_email = %s AND purchase_datetime BETWEEN %s AND %s"
        cursor.execute(query2, (username, start, end))
        dateRange = cursor.fetchone()
        return render_template("commissionDetailed.html", start=start, end=end, totalCommission=totalCommission["SUM"], dateRange=dateRange["COUNT(sold_price)"])


@app.route('/spending')
def spending():
    if 'username' not in session or session.get('role') != "customer":
        return redirect(url_for('home'))
    else:
        username = session['username']
        # agentID = session['id']
        cursor = conn.cursor()
        query1 = "SELECT SUM(sold_price) AS SUM FROM purchases NATURAL JOIN ticket WHERE customer_email = %s AND purchase_datetime BETWEEN NOW() - INTERVAL 1 YEAR AND NOW()"
        cursor.execute(query1, (username))
        totalSpending = cursor.fetchone()
        query2 = "SELECT SUM(sold_price) AS SUM_MONTH , DATE_FORMAT(purchase_datetime , '%%b %%Y') as datee FROM purchases NATURAL JOIN ticket WHERE customer_email = %s AND purchase_datetime BETWEEN NOW() - INTERVAL 6 MONTH AND NOW() GROUP BY datee ORDER BY datee ASC LIMIT 7"
        query3 = "select DATE_FORMAT(m1, '%b %Y') from ( select (DATE_ADD(CURRENT_DATE, INTERVAL -6 MONTH) - INTERVAL DAYOFMONTH(DATE_ADD(CURRENT_DATE, INTERVAL -6 MONTH))-1 DAY) +INTERVAL m MONTH as m1 from ( select @rownum:=@rownum+1 as m from (select 1 union select 2 union select 3 union select 4) t1, (select 1 union select 2 union select 3 union select 4) t2, (select 1 union select 2 union select 3 union select 4) t3, (select 1 union select 2 union select 3 union select 4) t4, (select @rownum:=-1) t0 ) d1 ) d2 where m1<= CURRENT_DATE order by m1 ASC LIMIT 7"
        
        cursor.execute(query2, (username))
        spendingMonthly = cursor.fetchall()
        cursor.execute(query3)
        labels = cursor.fetchall()
        list = {
            k: [d.get(k) for d in labels]
            for k in set().union(*labels)
        }
        
        lis = {
            k: [d.get(k) for d in spendingMonthly]
            for k in set().union(*spendingMonthly)
        }
        datalist = [0]*len(list["DATE_FORMAT(m1, '%b %Y')"])
        if len(lis) == 0:
            datalist = datalist
        else:
            for i in range(len(lis["SUM_MONTH"])):
                for k in range(len(list["DATE_FORMAT(m1, '%b %Y')"])):
                    if lis["datee"][i] == list["DATE_FORMAT(m1, '%b %Y')"][k]:
                        datalist[k] = lis["SUM_MONTH"][i]
                

        
        
        return render_template("spending.html", username=username, title='Monthly Spending for Last 6 Months', max=max(lis["SUM_MONTH"]), totalSpending=totalSpending["SUM"], data=datalist, labels=list["DATE_FORMAT(m1, '%b %Y')"])


@app.route('/spendingDetailed')
def spendingDetailed():
    if 'username' not in session or request.args.get('start') is None or session.get('role') != "customer":
        return redirect(url_for('spending'))
    else:
        username = session['username']
        # agentID = session['id']
        start = filter(request.args.get('start'))
        end = filter(request.args.get('end'))

        cursor = conn.cursor()
        query1 = "SELECT SUM(sold_price) AS SUM FROM purchases NATURAL JOIN ticket WHERE customer_email = %s AND purchase_datetime BETWEEN %s AND %s"
        cursor.execute(query1, (username, start, end))
        totalSpending = cursor.fetchone()
        if totalSpending["SUM"] is None:
            totalSpending["SUM"] = 0
        query2 = "SELECT SUM(sold_price) AS SUM_MONTH , DATE_FORMAT(purchase_datetime , '%%b %%Y') as datee FROM purchases NATURAL JOIN ticket WHERE customer_email = %s AND purchase_datetime BETWEEN %s AND %s GROUP BY datee ORDER BY datee DESC"
        query3 = "SELECT abs(datediff(%s, %s)) as 'INTERVAL' "
        cursor.execute(query3 , (start, end))
        interval = cursor.fetchone()
        
        cursor.execute(query2, (username, start, end))
        spendingMonthly = cursor.fetchall()
        print(spendingMonthly)

        query4 =  "select DATE_FORMAT(m1, '%%b %%Y') from ( select (DATE_ADD(%s, INTERVAL -%s DAY) - INTERVAL DAYOFMONTH(DATE_ADD(%s, INTERVAL -%s DAY))-1 DAY) +INTERVAL m MONTH as m1 from ( select @rownum:=@rownum+1 as m from (select 1 union select 2 union select 3 union select 4) t1, (select 1 union select 2 union select 3 union select 4) t2, (select 1 union select 2 union select 3 union select 4) t3, (select 1 union select 2 union select 3 union select 4) t4, (select @rownum:=-1) t0 ) d1 ) d2 where m1<= %s  order by m1 ASC "
        cursor.execute(query4 , (end, interval["INTERVAL"], end , interval["INTERVAL"], end))
        labels = cursor.fetchall()
        list = {
            k: [d.get(k) for d in labels]
            for k in set().union(*labels)
        }
        
        lis = {
            k: [d.get(k) for d in spendingMonthly]
            for k in set().union(*spendingMonthly)
        }
        
        datalist = [0]*len(list["DATE_FORMAT(m1, '%b %Y')"])
        if len(lis) == 0:
            datalist = datalist

        else :
            for i in range(len(lis["SUM_MONTH"])):
                for k in range(len(list["DATE_FORMAT(m1, '%b %Y')"])):
                    if lis["datee"][i] == list["DATE_FORMAT(m1, '%b %Y')"][k]:
                        datalist[k] = lis["SUM_MONTH"][i]


                
        
        
        return render_template("spendingDetailed.html", start=start, end=end, max=max(datalist), totalSpending=totalSpending["SUM"], data=datalist, labels=list["DATE_FORMAT(m1, '%b %Y')"])


@app.route('/review')
def review():
    return render_template('review.html')


@app.route('/reviewAuth', methods=['GET', 'POST'])
def reviewAuth():
    if 'username' not in session or session.get('role') != "customer":
        return redirect(url_for('home'))
    else:
        username = session['username']
        rating = filter(request.form['rating'])
        comments = filter(request.form['comments'])
        airline_name = filter(request.form['airlineName'])
        flight_num = filter(request.form['flightNumber'])
        cursor = conn.cursor()
        query2 = "SELECT email, airline_name, flight_num FROM review WHERE email = %s AND airline_name = %s AND flight_num = %s"
        cursor.execute(query2, (username, airline_name, flight_num))
        data2 = cursor.fetchall()
        query = "SELECT * FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE customer_email = %s AND airline_name = %s AND flight_num = %s AND arrival_time BETWEEN NOW() - INTERVAL 1 YEAR AND NOW()"
        cursor.execute(query, (username, airline_name, flight_num))
        data = cursor.fetchall()
        
        if data2:
            error = 'You have already reviewed this flight'
            return render_template('response.html', error=error)
        elif not data:
            error = 'You have not taken this flight yet or such a flight does not exist'
            return render_template('response.html', error=error)

        ins = "INSERT INTO review VALUES(%s ,%s, %s, %s, %s)"
        cursor.execute(ins, (username, airline_name,
                             flight_num, rating, comments))
        conn.commit()
        cursor.close()
        reviewDone = "Your review has been forwarded to the relevant personnel. Thank you for your feedback"

        return render_template("response.html", reviewDone=reviewDone)


@app.route('/viewRatings')
def viewRatings():
    return render_template('viewRatings.html')


@app.route('/viewRatingsAuth', methods=['GET', 'POST'])
def viewRatingsAuth():
    if 'username' not in session or session.get('role') != "staff":
        return redirect(url_for('home'))
    else:
        cursor = conn.cursor()
        username = session['username']
        query = 'SELECT airline_name FROM airline_staff WHERE username = %s'
        cursor.execute(query, (username))
        data = cursor.fetchone()
        airline = data['airline_name']
        flight_num = filter(request.form['flightNumber'])

        query2 = "SELECT email, rating , comments FROM review WHERE airline_name = %s AND flight_num = %s"
        cursor.execute(query2, (airline, flight_num))
        feedbackData = cursor.fetchall()
        print(feedbackData)
        if not feedbackData:
            error = 'This flight has not been rated yet'
            return render_template('response.html', error=error)

        query3 = "SELECT AVG(rating) FROM review where airline_name = %s and flight_num = %s"
        cursor.execute(query3, (airline, flight_num))
        average = cursor.fetchone()

        return render_template("viewRatingsAuth.html", feedbackData=feedbackData, airlineName=airline, flightNum=flight_num, averageRating=average['AVG(rating)'])


@app.route('/revenueChart')
def revenueChart():
    if 'username' not in session or session.get('role') != "staff":
        return redirect(url_for('home'))
    else:
        colors = ["#F7464A", "#46BFBD"]
        labels = ['Indirect Revenue1y', 'Direct Revenue1y']
        labels2 = ['Indirect Revenue1m', 'Direct Revenue1m']
        cursor = conn.cursor()
        username = session['username']
        query = 'SELECT airline_name FROM airline_staff WHERE username = %s'
        cursor.execute(query, (username))
        data = cursor.fetchone()
        airline = data['airline_name']
        # flight_num = filter(request.form['flightNumber'])

        query2 = "SELECT SUM(sold_price) as cusRevenue FROM ticket NATURAL JOIN purchases WHERE airline_name = %s AND agent_email IS NULL AND purchase_datetime BETWEEN NOW() - INTERVAL 1 YEAR AND NOW()"
        cursor.execute(query2, (airline))
        cusRevenuePastyear = cursor.fetchone()
        print(cusRevenuePastyear['cusRevenue'])
        if cusRevenuePastyear['cusRevenue'] == None:
            print('yolo')
            cusRevenuePastyear['cusRevenue'] = 0

        query3 = "SELECT SUM(sold_price) as indirectRev FROM ticket NATURAL JOIN purchases where airline_name = %s and agent_email IS NOT NULL AND purchase_datetime BETWEEN NOW() - INTERVAL 1 YEAR AND NOW()"
        cursor.execute(query3, (airline))
        indirectRevPastyear = cursor.fetchone()
        if indirectRevPastyear['indirectRev'] == None:
            print('yolo')
            indirectRevPastyear['indirectRev'] = 0

        values_Pastyear = [indirectRevPastyear['indirectRev'],
                           cusRevenuePastyear['cusRevenue']]

        query4 = "SELECT SUM(sold_price) as cusRevenue FROM ticket NATURAL JOIN purchases WHERE airline_name = %s AND agent_email IS NULL AND purchase_datetime BETWEEN NOW() - INTERVAL 1 MONTH AND NOW()"
        cursor.execute(query4, (airline))
        cusRevenuePastmonth = cursor.fetchone()
        print(cusRevenuePastmonth['cusRevenue'])
        if cusRevenuePastmonth['cusRevenue'] == None:
            print('yolo')
            cusRevenuePastmonth['cusRevenue'] = 0

        query5 = "SELECT SUM(sold_price) as indirectRev FROM ticket NATURAL JOIN purchases where airline_name = %s and agent_email IS NOT NULL AND purchase_datetime BETWEEN NOW() - INTERVAL 1 MONTH AND NOW()"
        cursor.execute(query5, (airline))
        indirectRevPastmonth = cursor.fetchone()
        if indirectRevPastmonth['indirectRev'] == None:
            print('yolo')
            indirectRevPastmonth['indirectRev'] = 0

        values_Pastmonth = [
            indirectRevPastmonth['indirectRev'], cusRevenuePastmonth['cusRevenue']]

        return render_template("revenueChart.html", max_Pastyear=max(values_Pastyear), title_Pastyear='Comparison of Revenue earned from direct and indirect sales in the Past year',  set_Pastyear=zip(values_Pastyear, labels, colors), max_Pastmonth=max(values_Pastmonth), title_Pastmonth='Comparison of revenue earned from direct and indirect sales in the past month', set_Pastmonth=zip(values_Pastmonth, labels2, colors))


@app.route('/logout')
def logout():
    session.pop('username')
    session.pop('role')
    if 'company' in session:
        session.pop('company')
    if 'id' in session:
        session.pop('id')
    return redirect('/login')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
