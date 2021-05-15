from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from helper import getConnection, disconnect, login_required, gradeItem, hashPassword, getData, getKey
import sqlite3


app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['TEMPLATE_AUTO_RELOAD'] = True
Session(app)

@app.route('/')
def index():

    #Connect to database
    connection = getConnection()
    cursor = connection.cursor()
    user_id = session.get('user_id')
    username = 'Not logged in'

    #Get the username
    if not user_id is None:

        cursor.execute('SELECT username FROM users WHERE id IS ?', (user_id,))
        rows = cursor.fetchall()
        username = rows[0][0]

    #Get data to display on score table
    cursor.execute('SELECT username, score FROM users')
    rows = cursor.fetchall()
    rows.sort( reverse = True, key = getKey )

    disconnect(connection, False)

    return render_template('index.html', username = username, rows = rows)

@app.route('/register', methods=['GET', 'POST'])
def register():

    login_required()

    if not session.get('user_id') is None:
        session.clear()

    if request.method == 'POST':

        #Get credentials
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        #Validate credentials
        if username == '':
            return render_template('register.html', error = 'Blank username')
        if password == '':
            return render_template('register.html', error = 'Blank password')
        if password != confirmation:
            return render_template('register.html', error = "Password and confirmation don't match")

        #Register if not already
        connection = getConnection()
        cursor = connection.cursor()

        #Debug:
        print(f'Username: {username} | Password: {password} | Password hash: {hashPassword(password)}')

        cursor.execute('SELECT * FROM users WHERE username IS ? OR password IS ?', (username, hashPassword(password)) )
        rows = cursor.fetchall()
        if len(rows) > 0:
            return render_template('register.html', error = 'Username or password already exists')
        cursor.execute('INSERT INTO users (username, password, score) VALUES (?, ?, 0)', (username, hashPassword(password)) )

        disconnect(connection, True)

        return redirect('/login')

    else:

        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if not session.get('user_id') is None:
        session.clear()

    if request.method == 'POST':

        #Get credentials
        username = request.form.get('username')
        password = request.form.get('password')

        #Validate credentials
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM users WHERE username IS ? AND password IS ?', (username, hashPassword(password)))

        rows = cursor.fetchall()
        if len(rows) == 0:
            return render_template('login.html', error = 'Username or password invalid')

        session['user_id'] = rows[0][0]

        disconnect(connection, commit=False)

        return redirect('/')

    else:

        return render_template('login.html')

@app.route('/exam', methods=['GET', 'POST'])
def exam():

    #loggedOut is None if logged in, else it holds redirection
    loggedOut = login_required()

    if loggedOut:
        return loggedOut

    if request.method == 'POST':

        items = [

            #Select the corresponding rendering engine.
            {

                'path-tracing': request.form.get('1A'),
                'rasterization': request.form.get('1B')

            },

            #Which characteristics do vertices have? Select all that apply.
            request.form.getlist('vertexCharacteristics'),

            #What is an n-gon?
            request.form.get('n-gon'),

            #Select the corresponding type of light.
            {

                'point': request.form.get('4A'),
                'area': request.form.get('4B'),
                'spot': request.form.get('4C'),
                'sun': request.form.get('4D')

            },

            {

                'vertex-quantity': request.form.get('vertex-quantity'),
                'edge-quantity': request.form.get('edge-quantity')

            },

            #Select the corresponding key combinations to do the following in the 3D viewport
            {

                'ctrl': request.form.get('6A'),
                'mmb': request.form.get('6B'),
                'shift': request.form.get('6C')

            },

            #Select the corresponding Blender features.
            {

                'animation': request.form.get('7A'),
                'simulation': request.form.get('7B'),
                'shading': request.form.get('7C'),
                'sculpting': request.form.get('7D'),
                'rendering': request.form.get('7E'),
                'modelling': request.form.get('7F'),
                'uv': request.form.get('7G')

            },

            #What does IOR stand for?
            request.form.get('acronym'),

            #Outline color
            request.form.get('color'),

            #Which company developed Blender?
            request.form.get('company')

        ]

        for item in items:
            if type(item) is None:
                return render_template('exam.html', error = 'All items must be answered', username = getData('username', session.get('user_id') ))

        #Get score
        score = (

            gradeItem(items[0]) +
            gradeItem(items[1]) +
            gradeItem(items[2], '3C') +
            gradeItem(items[3]) + #Don't forget to grade the fith item
            gradeItem(items[5]) +
            gradeItem(items[6]) +
            gradeItem(items[7], '8B') +
            gradeItem(items[8], '9D') +
            gradeItem(items[9], '10A')

        )

        if int(items[4]['vertex-quantity']) == 2 and int(items[4]['edge-quantity']) == 3:

            print(f'\n 5th item is correct \n')

            score += 1

        score /= 10

        score *= 5

        #Save score if first attempt
        connection = getConnection()
        cursor = connection.cursor()
        user_id = session.get('user_id')
        cursor.execute('SELECT score FROM users WHERE id IS ?', (user_id,))
        rows = cursor.fetchall()
        oldScore = rows[0][0]

        commit = False
        if int(oldScore) == 0:
            cursor.execute('UPDATE users SET score = ? WHERE id IS ?', ( round(score, 2), user_id) )
            commit = True
        disconnect(connection, commit)

        return redirect('/')

    else:

        score = getData('score', session.get('user_id') )

        if int(score) != 0:
            return redirect('/')

        return render_template('exam.html', username = getData('username', session.get('user_id') ) )

@app.route('/logout')
def logOut():

    login_required()

    session.clear()

    return redirect('/')
