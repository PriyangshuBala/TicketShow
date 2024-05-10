from operator import or_
from flask import Flask, abort, flash, jsonify, render_template, request, redirect, url_for, session, make_response
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
import sqlite3



app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///database.sqlite3"
app.config["SECRET_KEY"]="I am Priyangshu Bala"
db = SQLAlchemy(app)
app.app_context().push()


class Accounts(db.Model):
    acctype = db.Column(db.String,nullable=False)
    username = db.Column(db.Integer, primary_key=True,autoincrement=True)    
    password = db.Column(db.String(100), nullable=False)
    pno = db.Column(db.String(10))
    code = db.relationship('Shows', backref='Shows', lazy=True)

    def is_admin(self):
        return self.type=='admin'
    def is_user(self):
        return self.type=='user'
    def get_id(self):
        return self.id 
    def is_authenticated(self):
        return True 
    def is_active(self):
        return True

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venue_name = db.Column(db.String(100), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    shows = db.relationship('Shows', backref='Venue', lazy=True)

class Shows(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_name = db.Column(db.String(100), nullable=False)
    show_rating = db.Column(db.String(100), nullable=False)
    show_tags = db.Column(db.String(100), nullable=False)
    show_price = db.Column(db.Integer, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    username = db.Column(db.Integer, db.ForeignKey('accounts.username'), nullable=False)
    show_tickets = db.Column(db.Integer)

    
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('shows.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.username'), nullable=False)
    num_tickets = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    venue_name = db.Column(db.String)
    


@app.route("/")
def startpage():
    return render_template('welcomepage.html')

@app.route("/admilog", methods = ['GET','POST'])
def admilog():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password =  request.form['password']

        with sqlite3.connect("database.sqlite3") as users:
            cursor = users.cursor()
            cursor.execute("SELECT * FROM Accounts WHERE acctype = 'admin' ")
            acc= cursor.fetchone()

            if acc:
                session['loggedin'] = True
                print(acc)
                session['id'] = acc[0]
                session['username'] = acc[4]
                msg = 'Welcome!!'
                
                bestVenue={}
                conn = sqlite3.connect('database.sqlite3')
                cursor = conn.cursor()
                cursor.execute('SELECT venue_name,venue_img FROM Venue ORDER BY RANDOM() LIMIT 5')
                rows = cursor.fetchall()
                for row in rows:
                    bestVenue=dict(rows)
                cursor.close()
                conn.close()

                bestShows={}
                # home html er paashe, bestShows=topFour
                conn = sqlite3.connect('database.sqlite3')
                cursor = conn.cursor()
                cursor.execute('SELECT show_name,show_url FROM Shows ORDER BY RANDOM() LIMIT 5')
                rows = cursor.fetchall()
                for row in rows:
                    bestShows=dict(rows)
                cursor.close()
                conn.close()

                return render_template('adhome.html',bestVenue=bestVenue,bestShows=bestShows, msg = msg)
            else:
                msg = 'Incorrect Id/Password! Please Try Again'
    return render_template('admilog.html')

@app.route("/newusacc", methods = ['GET','POST'])
def newusacc():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        acctype = "user"
        pno = request.form['pno']
        conn = sqlite3.connect('database.sqlite3')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Accounts (username, password,acctype,pno) VALUES (?,?,?,?)", (username, password,acctype,pno))
        conn.commit()
        conn.close()
        return redirect(url_for('ushome'))
    return render_template('newusacc.html')

@app.route("/newadacc", methods = ['GET','POST'])
def newadacc():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        acctype = "admin"
        conn = sqlite3.connect('database.sqlite3')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Accounts (username, password,acctype) VALUES (?,?, ?)", (username, password,acctype))
        conn.commit()
        conn.close()
        return redirect(url_for('adhome'))
    return render_template('newadacc.html')



@app.route("/uslog", methods=['GET', 'POST'])
def uslog():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("database.sqlite3") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Accounts WHERE username=? AND password=? AND acctype='user'", (username, password))
            account = cursor.fetchone()

            if account:
                session['loggedin'] = True
                session['id'] = account[4]
                session['username'] = account[0]
                msg = 'Welcome!'

                bestShows = {}
                cursor.execute('SELECT show_name,show_url FROM Shows ORDER BY RANDOM() LIMIT 5')
                rows = cursor.fetchall()
                for row in rows:
                    bestShows = dict(rows)

                bestVenue = {}
                cursor.execute('SELECT venue_name,venue_img FROM Venue ORDER BY RANDOM() LIMIT 5')
                rows = cursor.fetchall()
                for row in rows:
                    bestVenue = dict(rows)

                return render_template('ushome.html', bestShows=bestShows, bestVenue=bestVenue, msg=msg)
            else:
                msg = 'Incorrect username or password!'
    return render_template('uslog.html', msg=msg)

@app.route("/ushome")
def ushome():
    # topFour google theke
    bestShows={}
    # home html er paashe, bestShows=topFour
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT show_name,show_url FROM Shows ORDER BY RANDOM() LIMIT 5')
    rows = cursor.fetchall()
    for row in rows:
        bestShows=dict(rows)
    cursor.close()
    conn.close()
 
    bestVenue={}
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT venue_name,venue_img FROM Venue ORDER BY RANDOM() LIMIT 5')
    rows = cursor.fetchall()
    for row in rows:
        bestVenue=dict(rows)
    cursor.close()
    conn.close()
    return render_template('ushome.html',bestShows = bestShows,bestVenue=bestVenue)

@app.route("/adhome")
def adhome():
    # topFour google theke
    bestShows={}
    # home html er paashe, bestShows=topFour
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT show_name,show_url FROM Shows ORDER BY RANDOM() LIMIT 5')
    rows = cursor.fetchall()
    for row in rows:
        bestShows=dict(rows)
    cursor.close()
    conn.close()
 
    bestVenue={}
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT venue_name,venue_img FROM Venue ORDER BY RANDOM() LIMIT 5')
    rows = cursor.fetchall()
    for row in rows:
        bestVenue=dict(rows)
    cursor.close()
    conn.close()
    return render_template('adhome.html',bestShows = bestShows,bestVenue=bestVenue)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/adabout")
def adabout():
    return render_template('adabout.html')

@app.route("/help")
def help():
    return render_template('help.html')

@app.route("/profile")
def profile():
    if 'loggedin' in session:
        conn = sqlite3.connect('database.sqlite3')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Accounts WHERE id = ?", (session['id'],))
        account = cursor.fetchone()
        cursor.close()
        conn.close()

        bestBook={}
        conn = sqlite3.connect('database.sqlite3')
        cursor = conn.cursor()
        cursor.execute('SELECT movie_name,show_time FROM Booking order by id DESC')
        rows = cursor.fetchall()
        for row in rows:
            bestBook=dict(rows)
        cursor.close()
        conn.close()

        return render_template('profile.html', account=account,bestBook=bestBook)
    
    return redirect(url_for('uslog'))


@app.route("/logout")
def logout():
    # remove session data
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    
    # redirect to login page
    response = make_response(redirect(url_for('startpage')))
    
    # Set the cache-control header to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


@app.route('/edit_venue/<string:venue_name>', methods=['GET', 'POST'])
def edit_venue(venue_name):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()

    # Get the Venue to edit
    cursor.execute('SELECT * FROM Venue WHERE venue_name = ?', (venue_name,))
    venue = cursor.fetchone()
    
    if request.method == 'POST':
        # Update the venue in the database with the new values from the form
        new_venue_name = request.form['venue_name']
        venue_address = request.form['venue_address']
        venue_opentime = request.form['venue_opentime']
        venue_img = request.form['venue_img']
        venue_code = request.form['venue_code']
        
        cursor.execute('UPDATE Venue SET venue_name = ?, venue_address = ?, venue_opentime = ?, venue_img = ?, venue_code = ? WHERE venue_name = ?', (new_venue_name, venue_address, venue_opentime, venue_img, venue_code, venue_name))
        conn.commit()
        
        flash('Venue updated successfully', 'success')
        return redirect(url_for('edit_venue', venue_name=new_venue_name))
    
    cursor.execute('SELECT s.show_name, s.show_tickets, s.show_url FROM Shows s JOIN Venue v ON s.venue_id = v.venue_code WHERE v.venue_name = ?', (venue_name,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('edit_venue.html', venue=venue, rows=rows)





@app.route('/edit_show/<string:show_name>', methods=['GET', 'POST'])
def edit_show(show_name):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()

    # Get the show to edit
    cursor.execute('SELECT * FROM Shows WHERE show_name = ?', (show_name,))
    show = cursor.fetchone()

    if request.method == 'POST':
        # Update the show in the database with the new values from the form
        new_show_name = request.form['show_name']
        show_price = request.form['show_price']
        show_rating = request.form['show_rating']
        show_url = request.form['show_url']
        show_code = request.form['show_code']
        
        cursor.execute('UPDATE Shows SET show_name = ?, show_price = ?, show_rating = ?, show_url = ?, show_code = ? WHERE show_name = ?', (new_show_name, show_price, show_rating, show_url, show_code, show_name))
        conn.commit()

        flash('Show updated successfully', 'success')
        return redirect(url_for('edit_show', show_name=new_show_name))

    cursor.execute('SELECT v.venue_name, v.venue_img from Venue v Join Shows s ON s.venue_id = v.venue_code WHERE s.show_name = ?', (show_name,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('edit_show.html', show=show, rows=rows)


@app.route('/add_venue', methods=['GET', 'POST'])
def add_venue():
    if request.method == 'POST':
        venue_name = request.form['venue_name']
        venue_address = request.form['venue_address']
        venue_opentime = request.form['venue_opentime']
        venue_img = request.form['venue_img']
        venue_code = request.form['venue_code']

        conn = sqlite3.connect('database.sqlite3')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Venue (venue_name, venue_code, venue_address, venue_opentime, venue_img) VALUES (?, ?, ?, ?, ?)',
                    (venue_name,venue_code,venue_address,venue_opentime,venue_img))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Venue added successfully")
        return redirect(url_for('add_venue'))

    return render_template('add_venue.html')


@app.route('/add_show', methods=['GET', 'POST'])
def add_show():
    venues = []  # Define venues as an empty list
    if request.method == 'POST':
        # Extract movie information from the form
        show_name = request.form['show_name']
        show_price = request.form['show_price']
        show_rating = request.form['show_rating']
        show_url = request.form['show_url']
        show_code = request.form['show_code']
        venue_id = request.form['venue_id']
        show_tickets = "200"

        # Connect to the database and insert the new movie
       
        conn = sqlite3.connect('database.sqlite3')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Shows (show_name, show_price, show_rating, show_url, show_code, venue_id, show_tickets) VALUES (?, ?, ?, ?, ?,?,?)',
                       (show_name,show_price, show_rating, show_url, show_code, venue_id,show_tickets))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Movie added successfully', 'success')
        return redirect(url_for('add_show'))
    if request.method == 'GET':
        conn = sqlite3.connect('database.sqlite3')
        cursor = conn.cursor()
        cursor.execute('Select venue_name,venue_code from Venue')
        venues=cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template('add_show.html',venues=venues)



@app.route('/booking/<string:show_name>', methods=['GET', 'POST'])
def booking(show_name):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Shows WHERE show_name = ?', (show_name,))
    Show = cursor.fetchone()
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        show_time = request.form['show_time']
        ticket_count = int(request.form['ticket_count'])
        venue_name = request.form['venue_name']
        cursor.execute('SELECT show_tickets FROM Shows WHERE show_name = ?', (show_name,))
        limi = cursor.fetchone()[0]
        left = limi - ticket_count
        if left < 0:
            flash("Not enough tickets available")
            cursor.close()
            conn.close()
            return redirect(url_for('booking', show_name=show_name))
        cursor.execute('INSERT INTO Booking (movie_name, show_time, ticket_count, venue_name) VALUES (?, ?, ?, ?)',
                       (movie_name, show_time, ticket_count, venue_name))
        cursor.execute('UPDATE Shows SET show_tickets = ? WHERE show_name = ?', (left, show_name))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Booking Successful")
        return redirect(url_for('booking', show_name=show_name))
    if request.method == 'GET':
        conn = sqlite3.connect('database.sqlite3')
        cursor = conn.cursor()
        cursor.execute(
            'Select v.venue_name, v.venue_code from Venue v JOIN Shows s ON v.venue_code = s.venue_id WHERE s.show_name = ?',
            (show_name,))
        venues = cursor.fetchall()
        cursor.execute('SELECT show_tickets FROM Shows WHERE show_name=?',(show_name,))
        tcount=cursor.fetchone()[0]
        cursor.close()
        conn.close()

    return render_template('book.html', Show=Show, venues=venues, tcount=tcount)






@app.route('/deleteve/<string:venue_name>', methods=['POST', 'GET'])
def deleteve(venue_name):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()

    if request.method == 'POST':
        cursor.execute('DELETE FROM Venue WHERE venue_name = ?', (venue_name,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Venue successfully deleted')
        return redirect(url_for('adhome'))
    else:
        Venue = cursor.execute('SELECT * FROM Venue WHERE venue_name = ?', (venue_name,)).fetchone()
        cursor.close()
        conn.close()
        return render_template('deleteve.html', Venue=Venue)

@app.route('/deletesh/<string:show_name>', methods=['POST', 'GET'])
def deletesh(show_name):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()

    if request.method == 'POST':
        cursor.execute('DELETE FROM Shows WHERE show_name = ?', (show_name,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Venue successfully deleted')
        return redirect(url_for('adhome'))
    else:
        show = cursor.execute('SELECT * FROM Shows WHERE show_name = ?', (show_name,)).fetchone()
        cursor.close()
        conn.close()
        return render_template('deletesh.html', show=show)

@app.route('/search')
def search():
    search_query = request.args.get('query')
    # Establish a connection to the SQLite3 database
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    # Query the database for venues and shows matching the search query
    if search_query:
        venue_query = f"SELECT 'venue' as type , venue_name, venue_address, venue_img FROM Venue WHERE venue_name LIKE '%{search_query}%'"
        show_query = f"SELECT 'show' as  type , show_name, show_rating, show_price, show_url FROM Shows WHERE show_name LIKE '%{search_query}%'"
    else:
        venue_query = "SELECT 'venue' as type , venue_name, venue_address, venue_img FROM Venue"
        show_query = "SELECT 'show' as type, show_name, show_rating, show_price,show_url FROM Shows"
    c.execute(venue_query)
    venues = c.fetchall()
    c.execute(show_query)
    shows = c.fetchall()
    # Close the database connection
    conn.close()
    # Combine the results and pass them to the template
    results = venues + shows
    return render_template('search.html', results=results)

@app.route('/ussearch')
def ussearch():
    search_query = request.args.get('query')
    # Establish a connection to the SQLite3 database
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    # Query the database for venues and shows matching the search query
    if search_query:
        venue_query = f"SELECT 'venue' as type , venue_name, venue_address, venue_img FROM Venue WHERE venue_name LIKE '%{search_query}%'"
        show_query = f"SELECT 'show' as  type , show_name, show_rating, show_price, show_url FROM Shows WHERE show_name LIKE '%{search_query}%'"
    else:
        venue_query = "SELECT 'venue' as type , venue_name, venue_address, venue_img FROM Venue"
        show_query = "SELECT 'show' as type, show_name, show_rating, show_price,show_url FROM Shows"
    c.execute(venue_query)
    venues = c.fetchall()
    c.execute(show_query)
    shows = c.fetchall()
    # Close the database connection
    conn.close()
    # Combine the results and pass them to the template
    results = venues + shows
    return render_template('ussearch.html', results=results)

@app.route('/usvenue/<string:venue_name>', methods=['GET', 'POST'])
def usvenue(venue_name):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Venue WHERE venue_name = ?', (venue_name,))
    Venue = cursor.fetchone()
    cursor.close()
    conn.close()

    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT s.show_name, s.show_tickets, s.show_url FROM Shows s JOIN Venue v ON s.venue_id = v.venue_code WHERE v.venue_name = ?', (venue_name,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('usvenue.html', Venue=Venue, rows=rows)

@app.route('/venshow/<string:show_name>', methods=['GET', 'POST'])
def venshow(show_name):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    # Get the show to edit
    cursor.execute('SELECT * FROM Shows WHERE show_name = ?', (show_name,))
    Show = cursor.fetchone()
    cursor.close()
    conn.close()

    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT v.venue_name, v.venue_img from Venue v Join Shows s ON s.venue_id = v.venue_code WHERE s.show_name = ?',(show_name,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()


    return render_template('venshow.html', Show=Show, rows = rows)




















if __name__ == '__main__':
    app.run(debug=True)