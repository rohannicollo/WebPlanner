# WebPlanner

> My final project is a simple planner web app to help people be organized. I am currently a highschool student, and being able to manage the things i need to do helps a lot, so this the first thing that came to mind while thinking of a final project.

## Files

---

My final project contains 4 pages:
- homepage
- schedules page
- todo page
- deadlines page

People will need to register and login first to access my webapp and save their notes. My webapp contains:
- a templates folder containing all my html files
- a static folder containing my css file
- a functions python file containing some extra functions including the `status` function and `login_required` function from the cs50 finance problem set
- MySQL as a database
- a python app file that contains everything needed for `flask` and the backend side of my web app.


# How my Webapp works

## Database

---

I used MySQL as the database for my app. It has 4 different tables, the user table, schedules table, todo table, and deadlines table. The user tablehas all the nessesarry information about the user. This contains the user's id, username and password hash. The next three tables have pretty simmilar column names, they all have an id, username, note, status in the deadlines and todo table, and date in the deadlines and schedules table.
- user table
- schedules table
- todo table
- deadlines table


## App.py

---

### **Login, logout and register**
My Webapp requires you to login first. The `login`, `logout` and `register` functions are similar to the ones I used in the finance problem set. People are asked for their username and password then checked if the username exists in my database and checks the password hash using the `check_password_hash` function from the werkzeug.security library. The user then gets redirected to the index page.

The logout function simply forgets the `user id` then redirected back to the login page.

The register function will ask the user for three inputs; username, password, and to confirm their password. The function then will check if the username already exists in my database and compare the password and confirm password. The user will be shown with an error if the username already exists or if the the passwords do not match. If all goes well the user's input will then get stored into the database, their passwords will be hashed, and get redirected to the login page.

### **Edit, add, clear and delete buttons and functions**
The three pages will all have these four buttons. All of the buttons has the type submit that submits to a form via `post`, to the url of the respective functions, and the edit and delete buttons will have the `ids` of the respective notes. The `edit` and `delete` functions will then take these ids as arguements and either remove the row with the same `id` or update the row with the same `id` with the user's new inputs to the database. The `clear` function will delete all the rows with the `username` equlas to the user's `username` from the database. And the `add` function will add new rows into the database.

There are to more funtions included in the deadlines and todo pages, `check` and `rmcheck` which changes the status of the picked note.

## Functions.py

---

This contains some extra functions I seperated from the app file. The `status` function that checks the status of a note dfrom the deadlines page. And a `login_required` function from the cs50 finance problem.

## Templates

---

### **Index**
The index is a simple page welcoming the user and a slogan below.

### **Schedules, Todo-list and Deadlines page**
All three pages will show either a sorted by date, a table or list with the user's `notes`, `date`, and `status` with the `username` equals to the user's`username` if accesssed via `get`. The data will be displayed via `for loop` displaying all the values of the arguements passed via `get`.

The deadline page will update the status of all the notes everytime the `get` action is used except for the ones with the "completed" status. The `status` function from the function file takes two arguements, `deadline` and the `date` today. It will then check how long until the deadline or how late our assignment is. The deadlines page will first loop through the notes without the "completed" status then loop through the ones with the status.

## Design

---

The design of my page mainly comes from [mdbootstrap](https://mdbootstrap.com/).


Video Demo: https://youtu.be/tZRM9igG52Y

This was CS50!