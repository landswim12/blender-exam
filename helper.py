from flask import session, redirect
import sqlite3

def getConnection():

    return sqlite3.connect('app.db', check_same_thread=False)

def disconnect(connection, commit):

    if commit:
        connection.commit()

    connection.close()

def login_required():

    #If there is no user id
    if session.get('user_id') is None:

        #Return redirection
        return redirect('/login')

def gradeItem(item, rightAnswer=''):

    grade = 0

    if type(item) is dict:

        maxGrade = len(item)

        for key in item.keys():

            if key == item[key]:

                grade += 1

        grade /= maxGrade

    elif type(item) is list:

        if len(item) == 1 and item[0] == 'location':

            grade = 1

    elif type(item) is str:

        if item == rightAnswer:

            grade = 1

    return grade

#By Paul Larson of Microsoft Research
def hashPassword(password):

    hash = 0

    for character in password:
        hash = 101 * hash + ord(character)

    hashString = str(hash)

    return hashString[:18]

def getData(query, user_id):

    connection = getConnection()
    cursor = connection.cursor()

    if query == 'username':
        cursor.execute('SELECT username FROM users WHERE id IS ?', (user_id,) )

    elif query == 'score':
        cursor.execute('SELECT score FROM users WHERE id IS ?', (user_id,) )

    else:
        raise ValueError('Invalid query: use "username" or "score"')

    data = cursor.fetchall()[0][0]

    disconnect(connection, False)

    return data

def getKey(e):

    return e[1]
