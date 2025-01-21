from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

#ik wil graag tables hebben die data bewaren voor login en projecten, zodat ik deze kan gebruiken voor de dergelijke systemen
def init_db():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''') # create table users for login system
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    image TEXT,
                    tags TEXT NOT NULL
                )''') # create table projects for my projects
    conn.commit()
    conn.close()

#app.route hiermee geef ik aan welke paginas gebruikt worden aan de python code en de html pages van toepassing
@app.route('/')
def index():
    return redirect(url_for('login'))# send user to the login page, since the app.route is nothing

@app.route('/login', methods=['GET', 'POST'])# method get and post are added since I want to use buttons for submitting data and I want to receive data from my database
#login pagina maken ik heb een gebruikersnaam en wachtwoord nodig, deze controleer ik met mijn database. als er geen corrensponderende gebruiker is geef ik dat weer door een error message. is het wel goed dan word je doorgestuurd naar de about page
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('app.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()  # Fetch user from database
        conn.close()

        if user is None:  # No user found
            flash('Invalid username. Please try again.', 'error')
            return redirect(url_for('login'))

        # Check password 
        if user[2] == password:  # Assuming `user[2]` is the password, this how it is stored in the database
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('about'))  # Redirect to about page
        else:
            flash('Invalid password. Please try again.', 'error')
            return redirect(url_for('login'))# send error message and redirect to login page

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])# method get and post are added since I want to use buttons for submitting data and I want to receive data from my database
#registreer gebruikers door de ingevulde data te inserten in de database, stel de gebruikersnaam wordt al gebruikt(om copies te voorkomen) geef een error message
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('app.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('Registration successful. Please log in.')# send message
            return redirect(url_for('login'))# redirect to the login page
        except sqlite3.IntegrityError:
            flash('Username already exists')# send error message
        conn.close()

    return render_template('register.html')

@app.route('/about')# about pagina
def about():
    return render_template('about.html')

@app.route('/contact')# contact pagina
def contact():
    return render_template('contact.html')

@app.route('/projects', methods=['GET', 'POST'])# method get and post are added since I need data from the database
#laat in de projects pagina mijn projecten zien vanuit de database, waarom de database? als ik het via html er in typ kan het aangepast worden door injecties, verder wil ik mijn projecten sorteerbaar maken met tags
def projects():
    #stel iemand probeert een shortcut via de paths in de browser dan wordt hij teruggestuurd om alsnog in te loggen
    if 'username' not in session: #check the user data
        flash('Please log in first')
        return redirect(url_for('login'))# return to login page

    conn = sqlite3.connect('app.db')# connect to the database
    c = conn.cursor()

    selected_tags = [] # watch for tags to sort
    if request.method == 'POST':  # Handle form submission
        selected_tags = request.form.getlist('tags')

    if selected_tags:
        # SQL query to filter projects by tags
        query = "SELECT * FROM projects WHERE " + " OR ".join(["tags LIKE ?"] * len(selected_tags))
        c.execute(query, [f"%{tag}%" for tag in selected_tags])
    else:
        # Default: show all projects
        c.execute("SELECT * FROM projects")

    projects = c.fetchall()
    conn.close()

    return render_template('projects.html', projects=projects, selected_tags=selected_tags)



@app.route('/logout') #logout page
def logout():
    session.pop('username', None)
    flash('Logged out successfully')
    return redirect(url_for('login'))# return to login page

#project data toevoegen aan database de enige manier om data toe te voegen doen op deze manier, zodat gebruikers niet zelf hun data kunnen toevoegen
def insert_sample_projects():
    conn = sqlite3.connect('app.db')# connect to database
    c = conn.cursor()
    c.execute('DELETE FROM projects')# empty database
    projects = [
        ("3D Printen onderdelen luchtdruk boot", "Bij dit project kregen we de taak als groep om een bootje te maken dat zichzelf kon voortstuwen met luchtdruk, tijdens dit project heb ik de rol van projectleider op me genomen, maar ook ben ik bezig geweest met het ontwerp van de versheidene onderdelen die ge 3d print moesten worden zoals bijvoorbeeld het stuur. Wij hadden als groep 8 weken de tijd gekregen om dit project tot een mooi einde te brengen ik heb ervoor gezorgd dat we als groep bepaalde deadlines gingen halen die ik zelf had opgesteld als tussenstops om te kijken hoe ver we daadwerkelijk waren in het project, ook heb ik meetings opgesteld om te zien waar we aan toe waren die week dit werdt op prijs gesteld door mijn groepsgenoten en dit zorgde voor een soepel verloop.", "img/3dontwerpboot.jpeg", "3dprinting"),
        ("Robotarm ontwerp", "In dit project zijn we aan de slag gegaan met het maken van een robotarm die medisch appratuur kan herkennen en oppakken, mijn taak hierin was het ontwerpen van de 3d onderdelen zoals de gripper en houders voor motoren, ik heb gebruik gemaakt van krachtberekeningen om te kunnen bepalen hoe groot de grippers uiteindelijk moesten worden om de tandwielen te behuizen ook heb ik gekeken naar de grip strength die nodig was om apparatuur te kunnen grijpen", "img/robotarm.jpeg", "physics,3dprinting"),
        ("Atractie behuizing", "Dit project had een kermissatractie als centrale bron, ons project was het maken van een behuizing voor de balken die zouden roteren, hiervoor hebben we veel berekeningen gedaan en ook een beetje 3dontwerp we zijn voornamelijk bezig geweest me het berekenen van dynamische krachten en doorbuigingen", "img/behuizing.jpeg", "physics"),
        ("Management Luchtdruk boot", "Bij dit project kregen we de taak als groep om een bootje te maken dat zichzelf kon voortstuwen met luchtdruk, tijdens dit project heb ik de rol van projectleider op me genomen. Wij hadden als groep 8 weken de tijd gekregen om dit project tot een mooi einde te brengen ik heb ervoor gezorgd dat we als groep bepaalde deadlines gingen halen die ik zelf had opgesteld als tussenstops om te kijken hoe ver we daadwerkelijk waren in het project, ook heb ik meetings opgesteld om te zien waar we aan toe waren die week dit werdt op prijs gesteld door mijn groepsgenoten en dit zorgde voor een soepel verloop en een leuk eindresultaat.","img/bootluchtdruk.jpeg", "management")
    ]
    c.executemany('INSERT INTO projects (title, description, image, tags) VALUES (?, ?, ?, ?)', projects)# add data to database
    conn.commit()
    conn.close()



if __name__ == '__main__':
    init_db()
    insert_sample_projects()
    app.run(debug=True)
# values van de SQL zijn allemaal ? dit voorkomt SQL injecties hierdoor kan er moeilijk ongewenst data worden aangepast