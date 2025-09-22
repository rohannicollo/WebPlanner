from sre_constants import SUCCESS
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from jinja2 import Environment, FileSystemLoader
from datetime import date, datetime
from flask_mysqldb import MySQL
import yaml

from functions import login_required, status

# Configure application
app = Flask(__name__)

# Configure templates
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

# Connect to MySQL
db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# GLobal variable for name
user = ''


@app.route('/login', methods=["GET", "POST"])
def login():
    #log the user in

    #Forget any user id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':

        # Get username and password
        username = request.form.get('username')
        password = request.form.get('password')

        # Query database for username
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, password, username FROM users WHERE username = %s', [username])
        rows = cursor.fetchall()
        cursor.close()

        # Ensure username exists and password is correct
        if rows == None or not check_password_hash(rows[0][1], password):
            error = 'Invalid Username/Password'
            return render_template('login.html', error=error)

        # Remember which user has logged in
        session['user_id'] = rows[0][0]
        global user
        user = rows[0][2]

        # Redirect user to home page
        return redirect('/')

    else:
        return render_template('login.html')


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    global user
    user = ''
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == 'GET':
        return render_template('register.html')

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == 'POST':

        # Get inputs
        username = request.form.get('username')
        password = request.form.get('password')

        # Check password
        if password != request.form.get('confirmpass'):

            # Return 'Password mismatch' then reconfirm Password
            error = 'Password Mismatch'
            return render_template('register.html', error=error)

        # SQL Query to check if username in database
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT username FROM users WHERE username = %s', [username])
        row = cursor.fetchone()
        cursor.close()

        # If in database, return 'Username already taken' then request another username
        if row != None:
            error2 = 'Username already exists'
            return render_template('register.html', error2=error2)

        # Hash password then Add user to database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", [(username), (generate_password_hash(password))])
        mysql.connection.commit()
        cursor.close()


        # Redirect user to login form
        return redirect("/login")


@app.route('/', methods=["GET", "POST"])
@login_required
def index():
    if request.method == 'GET':
        name = user
        return render_template('index.html', name=name)


@app.route('/todo-list', methods=["GET", "POST"])
@login_required
def todoList():
    # Add Todo-list

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == 'GET':

        # SqlQuery to return table with list
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT todo_id, note, status FROM todo WHERE username = %s", [user])
        rows = cursor.fetchall()
        cursor.close()

        # Return Template
        return render_template('todo-list.html', todos=rows)

    # User reached route via POST (as by submitting a form via POST)
    else:

        # Get user input
        todo = request.form.get('todo')

        # Insert todo to SQL table
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO todo (note, username, status) VALUES(%s, %s, %s)', [(todo), (user), False])
        mysql.connection.commit()
        cursor.close()

        return redirect('/todo-list')

@app.route('/todo-list/delete/<int:todo_id>', methods=["POST"])
@login_required
def todo_delete(todo_id):
    # Delete todo
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM todo WHERE todo_id = %s", [todo_id])
    mysql.connection.commit()
    cursor.close()
    return redirect('/todo-list')

@app.route('/todo-list/edit/<int:todo_id>', methods=["POST"])
@login_required
def todo_edit(todo_id):
    # Edit todo

    # Get new inputs
    new_note = request.form.get('new-note')

    # Update database
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE todo SET note = %s WHERE todo_id = %s", [new_note, todo_id])
    mysql.connection.commit()
    cursor.close()
    return redirect('/todo-list')

@app.route('/todo-list/check/<int:todo_id>', methods=["POST"])
@login_required
def todo_check(todo_id):
    # Check todo

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE todo SET status = %s WHERE todo_id = %s", [True, todo_id])
    mysql.connection.commit()
    cursor.close()
    return redirect('/todo-list')

@app.route('/todo-list/rmcheck/<int:todo_id>', methods=["POST"])
@login_required
def todo_rmcheck(todo_id):
    # Remove Check

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE todo SET status = %s WHERE todo_id = %s", [False, todo_id])
    mysql.connection.commit()
    cursor.close()
    return redirect('/todo-list')

@app.route('/todo-list/clear', methods=["POST"])
@login_required
def todo_clear():
    # Clear deadlines

    # Remove From database
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM todo WHERE username = %s", [user])
    mysql.connection.commit()
    cursor.close()
    return redirect('/todo-list')


@app.route('/schedule', methods=["GET", "POST"])
@login_required
def schedules():
    # Add Schedules

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == 'GET':

        # SqlQuery to return table with list
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT date, note, sched_id FROM schedules WHERE username = %s", [user])
        rows = cursor.fetchall()
        cursor.close()

        # Sort by dates
        rows = sorted(rows, key=lambda x: x[0])

        # Return Template
        return render_template('schedule.html', schedules=rows)

    # User reached route via POST (as by submitting a form via POST)
    else:

        # Get user input
        note = request.form.get('note')
        date = request.form.get('date')
        date = datetime.strptime(date, '%Y-%m-%d').date()

        # Insert schedule to SQL table
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO schedules (note, date, username) VALUES(%s, %s, %s)', [(note), (date), (user)])
        mysql.connection.commit()
        cursor.close()

        return redirect('/schedule')

@app.route('/schedule/delete/<int:sched_id>', methods=["POST"])
@login_required
def sched_delete(sched_id):
    # Delete schedule
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM schedules WHERE sched_id = %s", [sched_id])
    mysql.connection.commit()
    cursor.close()
    return redirect('/schedule')


@app.route('/schedule/edit/<int:sched_id>', methods=["GET", "POST"])
@login_required
def sched_edit(sched_id):
    # Edit schedule

    # Get new inputs
    new_note = request.form.get('new-note')
    new_date = request.form.get('new-date')

    # Update database
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE schedules SET note = %s, date = %s WHERE sched_id = %s", [new_note, new_date, sched_id])
    mysql.connection.commit()
    cursor.close()
    return redirect('/schedule')

@app.route('/schedule/clear', methods=["POST"])
@login_required
def sched_clear():
    # Clear schedules

    # Remove From database
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM schedules WHERE username = %s", [user])
    mysql.connection.commit()
    cursor.close()
    return redirect('/schedule')


@app.route('/deadlines', methods=["GET", "POST"])
@login_required
def deadlines():
    # Add Deadlines

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == 'GET':

        # SqlQuery to return table with list
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT dl_id, note, date, status FROM deadlines WHERE username = %s", [user])
        rows = cursor.fetchall()
        cursor.close()

        # Update Status and Sort by date
        for row in rows:
            if row[3] != 'Completed':
                today = date.today()
                tmp = list(row)
                tmp[3] = status(today, row[2])
                row = tuple(tmp)
        rows = sorted(rows, key=lambda x: x[2])

        # Return Template
        return render_template('deadlines.html', deadlines=rows)

    # User reached route via POST (as by submitting a form via POST)
    else:

        # Get user input
        note = request.form.get('note')
        deadline = request.form.get('deadline')
        deadline = datetime.strptime(deadline, '%Y-%m-%d').date()

        # Set status
        today = date.today()
        dlstatus = status(today, deadline)

        # Insert deadline to SQL table
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO deadlines (note, date, status, username) VALUES(%s, %s, %s, %s)', (note, deadline, dlstatus, user))
        mysql.connection.commit()
        cursor.close()

        return redirect('/deadlines')

@app.route('/deadlines/delete/<int:dl_id>', methods=["POST"])
@login_required
def dl_delete(dl_id):
    # Delete deadline
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM deadlines WHERE dl_id = %s", [dl_id])
    mysql.connection.commit()
    cursor.close()
    return redirect('/deadlines')

@app.route('/deadlines/edit/<int:dl_id>', methods=["POST"])
@login_required
def dl_edit(dl_id):
    # Edit deadline

    # Get new inputs
    new_note = request.form.get('new-note')
    new_date = request.form.get('new-date')

    # Update database
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE deadlines SET note = %s, date = %s WHERE dl_id = %s", [new_note, new_date, dl_id])
    mysql.connection.commit()
    cursor.close()
    return redirect('/deadlines')

@app.route('/deadlines/check/<int:dl_id>', methods=["POST"])
@login_required
def dl_check(dl_id):
    # Check deadline

    # Update Database
    completed = 'Completed'
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE deadlines SET status = %s WHERE dl_id = %s", [completed, dl_id])
    mysql.connection.commit()
    cursor.close()
    return redirect('/deadlines')

@app.route('/deadlines/rmcheck/<int:dl_id>', methods=["POST"])
@login_required
def dl_rmcheck(dl_id):
    # Remove check

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT date FROM deadlines WHERE dl_id = %s", [dl_id])
    check = cursor.fetchall()
    mysql.connection.commit()
    cursor.close()

    # If already completed
    today = date.today()
    old_status = status(today, check[0][0])
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE deadlines SET status = %s WHERE dl_id = %s", [old_status, dl_id])
    mysql.connection.commit()
    cursor.close()
    print("hello")
    return redirect('/deadlines')

@app.route('/deadlines/clear', methods=["POST"])
@login_required
def dl_clear():
    # Clear deadlines

    # Remove From database
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM deadlines WHERE username = %s", [user])
    mysql.connection.commit()
    cursor.close()
    return redirect('/deadlines')



if __name__ == '__main__':
    app.run(debug=True)