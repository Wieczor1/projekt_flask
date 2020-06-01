from datetime import datetime, date
from functools import wraps
from tempfile import mkdtemp

from flask_session import Session
from flask import Flask, render_template, request, redirect, session, flash
import sqlite3

app = Flask(__name__)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
con = sqlite3.connect("db.db")
cur = con.cursor()
# cur.execute(
#     "select Wizyta.id, Wizyta.Data, Lekarz.Surname from Wizyta inner join Lekarz on Wizyta.Lekarz_Id = Lekarz.Id")
# wizyty = cur.fetchall()


# print(wizyty)


# @app.route('/')
# def hello_world():
#     return 'Hello World!'
#
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/login", methods=['GET', 'POST']) #TODO LOGIN INNY
def login():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    # session.clear()
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        cur.execute("select * from Users where username = ? and password = ?", [username, password])
        rows = cur.fetchall()
        # print(rows)
        # print(len(rows))
        # print(rows[0][0])
        if len(rows) != 1:
            flash("Błędne dane")
            return redirect(request.path)
        if len(rows) == 1:
            session["user_id"] = rows[0][0]
            session["access"] = rows[0][3]
        flash("Zalogowano poprawnie")
        return redirect("/wizyta")

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return redirect("/wizyta")


#     con = sqlite3.connect("db.db")
#     cur = con.cursor()
#     if request.method == "POST":
#         username = request.form['username']
#         password = request.form['password']
#         cur.execute("select * from Users where username = ? and password = ?", [username, password])
#         ziomki = cur.fetchall()
#
#         columns = ["Data", "Imię lekarza", "Nazwisko lekarza", "Imię pacjenta", "Nazwisko pacjenta"]
#
#         cur.execute(
#             "select Wizyta.id, Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id")
#         rows = cur.fetchall()
#         # print(ziomki)
#         return render_template("wizyta.html", columns=columns, rows=rows)
#     else:
#         return render_template("login.html")

@app.route('/pacjent', methods=['GET', 'POST'])
@login_required
def pacjent():
    if session["access"] == 3:
        if request.method == "GET":
            session.pop('_flashes', None)
            con = sqlite3.connect("db.db")
            cur = con.cursor()

            columns = ["Imie", "Nazwisko", "Pesel", "Telefon"]
            cur.execute(
                "select id, Name, Surname, Pesel, Telefon from Pacjent")
            rows = cur.fetchall()
            return render_template("pacjent.html", columns=columns, rows=rows)


@app.route('/pacjent_create', methods=['GET', 'POST'])  # TODO logowanie
@login_required
def pacjent_create():
    if session["access"] == 3:
        if request.method == "GET":
            session.pop('_flashes', None)
            return render_template("pacjent_create.html")
        if request.method == "POST":
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            name = request.form["name"]
            surname = request.form["surname"]
            pesel = request.form["pesel"]
            telefon = request.form["telefon"]
            username = request.form["username"]
            password = request.form["password"]
            if not name or not surname or not pesel or not telefon or not username or not password:
                session.pop('_flashes', None)
                flash("Bledne dane!")
                return render_template("pacjent_create.html")
            if not len(pesel) == 11 or not pesel.isdigit():
                session.pop('_flashes', None)
                flash("Pesel musi byc ciagiem 11 cyfr!")
                return render_template("pacjent_create.html")
            if not len(telefon) == 9 or not pesel.isdigit():
                session.pop('_flashes', None)
                flash("Telefon musi byc ciagiem 9 cyfr!")
                return render_template("pacjent_create.html")
            if len(password) <= 4:
                session.pop('_flashes', None)
                flash("Haslo musi miec mala litere, cyfre i byc dluzsze niz 4!")
                return render_template("pacjent_create.html")
            else:
                cur.execute("insert into users(id, username, password, access) values (null, ?, ?, 1) ", [username, password])
                con.commit()
                cur.execute("select id from Users where username = ? and password = ?", [username, password])
                id = cur.fetchall()
                print(id, "id")
                cur.execute("insert into pacjent(name, surname, pesel, telefon, users_id) values (?,?,?,?,?)",
                            [name, surname, pesel, telefon, int(id[0][0])])
                con.commit()

                columns = ["Imie", "Nazwisko", "Pesel", "Telefon"]
                cur.execute(
                    "select id, Name, Surname, Pesel, Telefon from Pacjent")
                session.pop('_flashes', None)
                rows = cur.fetchall()
                return render_template("pacjent.html", columns=columns, rows=rows)


@app.route('/pacjent_update', methods=['GET', 'POST']) #TODO logowanie
@login_required
def pacjent_update():
    if request.method == "GET":
        session.pop('_flashes', None)
        global id
        id = request.args.get("id")
        if not id:
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            columns = ["Imie", "Nazwisko", "Pesel", "Telefon"]
            cur.execute(
                "select id, Name, Surname, Pesel, Telefon from Pacjent")
            rows = cur.fetchall()
            flash("Musisz wpierw zaznaczyc pacjenta!")
            return render_template("pacjent.html", columns=columns, rows=rows)
        # print(id, "id")
        con = sqlite3.connect("db.db")
        cur = con.cursor()
        # cur.execute("select * from Wizyta where Wizyta.id = ?", (id,))
       # wizyta = cur.fetchall()
        cur.execute(
            "select Name, Surname, Pesel, Telefon, Username, Password from pacjent inner join users on pacjent.users_id = users.id where Pacjent.id = ?",
            (id,))
        text = cur.fetchall()
        print(text)
        if not text:
            cur.execute(
                "select Name, Surname, Pesel, Telefon from pacjent where Pacjent.id = ?",
                (id,))
            helper = cur.fetchall()
            text = list(helper[0])
            text.append('')
            text.append('')
            return render_template("pacjent_update.html", text=text)
        return render_template("pacjent_update.html", text=text[0])
    if request.method == "POST":
        name = request.form["name"]
        surname = request.form["surname"]
        pesel = request.form["pesel"]
        telefon = request.form["telefon"]
        username = request.form["username"]
        password = request.form["password"]
        if not name or not surname or not pesel or not telefon or not username or not password:
            session.pop('_flashes', None)
            flash("Bledne dane!")
            return render_template("pacjent_create.html")
        if not len(pesel) == 11 or not pesel.isdigit():
            session.pop('_flashes', None)
            flash("Pesel musi byc ciagiem 11 cyfr!")
            return render_template("pacjent_create.html")
        if not len(telefon) == 9 or not pesel.isdigit():
            session.pop('_flashes', None)
            flash("Telefon musi byc ciagiem 9 cyfr!")
            return render_template("pacjent_create.html")
        if len(password) <= 4:
            session.pop('_flashes', None)
            flash("Haslo musi miec mala litere, cyfre i byc dluzsze niz 4!")
            return render_template("pacjent_create.html")

        con = sqlite3.connect("db.db")
        cur = con.cursor()
        cur.execute("select id from Users where username = ? and password = ?", [username, password])

        ifempty = cur.fetchall()
        if len(ifempty) > 0:
            columns = ["Imie", "Nazwisko", "Pesel", "Telefon"]
            cur.execute(
                "select id, Name, Surname, Pesel, Telefon from Pacjent")
            session.pop('_flashes', None)
            rows = cur.fetchall()
            flash("Istnieje juz taki uzytkownik")
            return render_template("pacjent.html", columns=columns, rows=rows)

        cur.execute("select Users_id from Pacjent where id = ?", id)

        pacjent_user_id = cur.fetchall()

        helper = pacjent_user_id[0][0]
        print(helper)

        cur.execute("select id from Users")
        lekarze = cur.fetchall()
        print(lekarze, "pacjenci")

        if ((helper,) in lekarze):
            print("jestem w ifie")
            cur.execute(
                "update Users set Username=?, Password=? where id =?",
                [username, password, helper])
            con.commit()
        else:
            print("jestem w else")
            cur.execute(
                "insert into Users(id,Username,Password,Access) values (null, ?, ?, 1)",
                [username, password])
            con.commit()
            cur.execute("select * from Users order by id desc limit 1")
            lekarz_user_id = cur.fetchall()
            helper = lekarz_user_id[0][0]
            con.commit()

        cur.execute(
            "update Pacjent set Name=?, Surname = ?, Pesel = ?, Telefon = ?, Users_id = ? where id=?",
            [name, surname, pesel, telefon, helper, id])
        con.commit()

        columns = ["Imie", "Nazwisko", "Pesel", "Telefon"]
        cur.execute(
            "select id, Name, Surname, Pesel, Telefon from Pacjent")
        rows = cur.fetchall()
        session.pop('_flashes', None)
        flash("Zmieniono Pacjenta!")
        return render_template("pacjent.html", columns=columns, rows=rows)


@app.route('/pacjent_delete', methods=['GET', 'POST'])
@login_required
def pacjent_delete():
    if session["access"] == 3:
        if request.method == "GET":
            session.pop('_flashes', None)
            id = request.args.get("id")
            if not id:
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Imie", "Nazwisko", "Pesel", "Telefon"]
                cur.execute(
                    "select id, Name, Surname, Pesel, Telefon from Pacjent")
                rows = cur.fetchall()
                flash("Musisz wpierw zaznaczyc pacjenta!")
                return render_template("pacjent.html", columns=columns, rows=rows)  # TODO usun penisa
            print(id, "id")
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute("select id from Wizyta where Pacjent_id = ?", (id,))
            ifempty = cur.fetchall()
            if len(ifempty) > 0:
                print("wbilem byku")
                columns = ["Imie", "Nazwisko", "Pesel", "Telefon"]
                cur.execute(
                    "select id, Name, Surname, Pesel, Telefon from Pacjent")
                rows = cur.fetchall()
                session.pop('_flashes', None)
                flash("Musisz usunac wpierw wizyty!")
                return render_template("pacjent.html", columns=columns, rows=rows)
            cur.execute("delete from Pacjent where Pacjent.id = ?", (id,))
            con.commit()
            columns = ["Imie", "Nazwisko", "Pesel", "Telefon"]
            cur.execute(
                "select id, Name, Surname, Pesel, Telefon from Pacjent")
            rows = cur.fetchall()
            flash("Usunięto pacjenta")
            return render_template("pacjent.html", columns=columns, rows=rows)


@app.route('/lekarz', methods=['GET', 'POST'])
@login_required
def lekarz():
    if session["access"] == 3:
        if request.method == "GET":
            session.pop('_flashes', None)
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            columns = ["Imie", "Nazwisko", "Pesel", "Telefon", "Pensja"]
            cur.execute(
                "select id, Name, Surname, Pesel, Telefon, Salary from Lekarz")
            rows = cur.fetchall()
            # print(ziomki)
            return render_template("lekarz.html", columns=columns, rows=rows)


@app.route('/lekarz_create', methods=['GET', 'POST'])
@login_required
def lekarz_create():
    if session["access"] == 3:
        session.pop('_flashes', None)
        if request.method == "GET":
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            return render_template("lekarz_create.html")

        if request.method == "POST":
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            name = request.form['name']
            surname = request.form['surname']
            telefon = request.form['telefon']
            pesel = request.form['pesel']
            salary = request.form['salary']
            username = request.form['username']
            password = request.form['password']
            if not name or not surname or not pesel or not telefon or not username or not password:
                session.pop('_flashes', None)
                flash("Bledne dane!")
                return render_template("pacjent_create.html")
            if not len(pesel) == 11 or not pesel.isdigit():
                session.pop('_flashes', None)
                flash("Pesel musi byc ciagiem 11 cyfr!")
                return render_template("pacjent_create.html")
            if not len(telefon) == 9 or not pesel.isdigit():
                session.pop('_flashes', None)
                flash("Telefon musi byc ciagiem 9 cyfr!")
                return render_template("pacjent_create.html")
            if len(password) <= 4:
                session.pop('_flashes', None)
                flash("Haslo musi miec mala litere, cyfre i byc dluzsze niz 4!")
                return render_template("pacjent_create.html")
            if not salary.isdigit():
                session.pop('_flashes', None)
                flash("Pensja musi byc cyfra!")
                return render_template("pacjent_create.html")

            cur.execute("select id from Users where username = ? and password = ?", [username, password])
            ifempty = cur.fetchall()
            if len(ifempty) > 0:
                columns = ["Imie", "Nazwisko", "Pesel", "Telefon", "Pensja"]
                cur.execute(
                    "select id ,Name, Surname, Pesel, Telefon, Salary from Lekarz")
                rows = cur.fetchall()
                session.pop('_flashes', None)
                flash("Istnieje juz taki uzytkownik")
                return render_template("lekarz.html", columns=columns, rows=rows)



            cur.execute("insert into Users(id, Username, Password, Access) values (null, ?,?,2)",
                        [username, password])
            con.commit()

            cur.execute("select id from Users where username = ? and password = ?", [username, password])

            ziomki = cur.fetchall()

            print(ziomki)
            id = ziomki[0][0]
            print(id)
            cur.execute(
                "insert into Lekarz(id, Name, Surname, Pesel, Telefon, Salary, Users_id) values (null, ?,?,?,?,?,?)",
                [name, surname, telefon, pesel, salary, id])
            con.commit()
            columns = ["Imie", "Nazwisko", "Pesel", "Telefon", "Pensja"]
            cur.execute(
                "select id ,Name, Surname, Pesel, Telefon, Salary from Lekarz")
            rows = cur.fetchall()
            flash("Dodano lekarza")
            return render_template("lekarz.html", columns=columns, rows=rows)


@app.route('/lekarz_update', methods=['GET', 'POST'])
@login_required
def lekarz_update():
    if session["access"] == 3:
        if request.method == "GET":
            session.pop('_flashes', None)
            global id
            id = request.args.get("id")
            if not id:
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Imie", "Nazwisko", "Pesel", "Telefon", "Pensja"]
                cur.execute(
                    "select id, Name, Surname, Pesel, Telefon, Salary from Lekarz")
                rows = cur.fetchall()
                flash("Musisz wpierw zaznaczyc lekarza!")
                return render_template("lekarz.html", columns=columns, rows=rows)
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute("select Name, Surname, Pesel, Telefon, Salary, Username, Password from lekarz inner join users on lekarz.users_id = users.id where Lekarz.id=?", (id,))
            text = cur.fetchall()
            if not text:
                cur.execute(
                    "select Name, Surname, Pesel, Telefon, Salary from Lekarz where Lekarz.id = ?",
                    (id,))
                helper = cur.fetchall()
                text = list(helper[0])
                text.append('')
                text.append('')
                return render_template("lekarz_update.html", text=text)
            print(text)
            return render_template("lekarz_update.html", text=text[0])

        if request.method == "POST":
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            name = request.form['name']
            surname = request.form['surname']
            telefon = request.form['telefon']
            pesel = request.form['pesel']
            salary = request.form['salary']
            username = request.form['username']
            password = request.form['password']
            if not name or not surname or not pesel or not telefon or not username or not password:
                session.pop('_flashes', None)
                flash("Bledne dane!")
                return render_template("pacjent_create.html")
            if not len(pesel) == 11 or not pesel.isdigit():
                session.pop('_flashes', None)
                flash("Pesel musi byc ciagiem 11 cyfr!")
                return render_template("pacjent_create.html")
            if not len(telefon) == 9 or not pesel.isdigit():
                session.pop('_flashes', None)
                flash("Telefon musi byc ciagiem 9 cyfr!")
                return render_template("pacjent_create.html")
            if len(password) <= 4:
                session.pop('_flashes', None)
                flash("Haslo musi miec mala litere, cyfre i byc dluzsze niz 4!")
                return render_template("pacjent_create.html")
            if not salary.isdigit():
                session.pop('_flashes', None)
                flash("Pensja musi byc cyfra!")
                return render_template("pacjent_create.html")

            cur.execute("select id from Users where username = ? and password = ?", [username, password])
            ifempty = cur.fetchall()
            if len(ifempty) > 0:
                columns = ["Imie", "Nazwisko", "Pesel", "Telefon", "Pensja"]
                cur.execute(
                    "select id ,Name, Surname, Pesel, Telefon, Salary from Lekarz")
                rows = cur.fetchall()
                session.pop('_flashes', None)
                flash("Istnieje juz taki uzytkownik")
                return render_template("lekarz.html", columns=columns, rows=rows)

            cur.execute("select Users_id from Lekarz where id = ?", (int(id),))

            lekarz_user_id = cur.fetchall()
            helper = lekarz_user_id[0][0]

            cur.execute("select id from Users")
            lekarze = cur.fetchall()
            print(lekarze, "lekarze")

            if ((helper,) in lekarze):
                print("jestem w ifie")
                cur.execute(
                    "update Users set Username=?, Password=? where id =?",
                    [username, password, helper])
                con.commit()
            else:
                print("jestem w else")
                cur.execute(
                    "insert into Users(id,Username,Password,Access) values (null, ?, ?, 2)",
                    [username, password])
                con.commit()
                cur.execute("select * from Users order by id desc limit 1")
                lekarz_user_id = cur.fetchall()
                helper = lekarz_user_id[0][0]
                con.commit()

            cur.execute(
                "update Lekarz set Name=?, Surname = ?, Pesel = ?, Telefon = ?, Salary = ?, Users_id = ? where id=?",
                [name, surname, pesel, telefon, salary, helper, id])
            con.commit()

            columns = ["Imie", "Nazwisko", "Pesel", "Telefon", "Pensja"]
            cur.execute(
                "select id, Name, Surname, Pesel, Telefon, Salary from Lekarz")

            rows = cur.fetchall()
            session.pop('_flashes', None)
            flash("Zmieniono lekarza!")
            return render_template("lekarz.html", columns=columns,
                                   rows=rows)  # TODO usun penis


@app.route('/lekarz_deleteuser', methods=['GET', 'POST'])
@login_required
def lekarz_deleteuser():
    if session["access"] == 3:
        if request.method == "GET":
            session.pop('_flashes', None)
            id = request.args.get("id")
            if not id:
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Imie", "Nazwisko", "Pesel", "Telefon", "Pensja"]
                cur.execute(
                    "select id, Name, Surname, Pesel, Telefon, Salary from Lekarz")
                rows = cur.fetchall()
                flash("Musisz wpierw zaznaczyc lekarza!")
                return render_template("lekarz.html", columns=columns, rows=rows)
            print(id, "id")
            con = sqlite3.connect("db.db")
            cur = con.cursor()

            cur.execute("select Users_id from Lekarz where id = ?", id)

            lekarz_user_id = cur.fetchall()

            helper = lekarz_user_id[0][0]

            print(type(helper))
            print("przed")
            cur.execute("select * from Users")

            lekarze = cur.fetchall()
            print(lekarze)

            print(helper)
            cur.execute("delete from Users where Users.id = ?", (helper,))
            con.commit()
            print("po")
            cur.execute("select * from Users")

            lekarze = cur.fetchall()

            print(lekarze)

            columns = ["Imie", "Nazwisko", "Pesel", "Telefon", "Pensja"]
            cur.execute(
                "select id, Name, Surname, Pesel, Telefon, Salary from Lekarz")
            rows = cur.fetchall()
            flash("Usunieto dane lekarza!")
            return render_template("lekarz.html", columns=columns, rows=rows)  # TODO usun penisa


@app.route('/lekarz_delete', methods=['GET', 'POST'])
@login_required
def lekarz_delete():
    if session["access"] == 3:
        if request.method == "GET":
            session.pop('_flashes', None)
            id = request.args.get("id")
            if not id:
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Imie", "Nazwisko", "Pesel", "Telefon", "Pensja"]
                cur.execute(
                    "select id, Name, Surname, Pesel, Telefon, Salary from Lekarz")
                rows = cur.fetchall()
                flash("Musisz wpierw zaznaczyc lekarza!")
                return render_template("lekarz.html", columns=columns, rows=rows)
            print(id, "id")
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute("select id from Wizyta where Lekarz_id = ?", (id,))
            ifempty = cur.fetchall()
            if len(ifempty) > 0:
                print("wbilem byku")
                columns = ["Imie", "Nazwisko", "Pesel", "Telefon", "Pensja"]
                cur.execute(
                    "select id ,Name, Surname, Pesel, Telefon, Salary from Lekarz")
                rows = cur.fetchall()
                session.pop('_flashes', None)
                flash("Musisz usunac wpierw wizyty!")
                return render_template("lekarz.html", columns=columns, rows=rows)

            cur.execute("delete from Lekarz where Lekarz.id = ?", (id,))
            con.commit()

            columns = ["Imie", "Nazwisko", "Pesel", "Telefon", "Pensja"]
            cur.execute(
                "select id, Name, Surname, Pesel, Telefon, Salary from Lekarz")
            rows = cur.fetchall()
            flash("Usunieto lekarza!")
            return render_template("lekarz.html", columns=columns, rows=rows)  # TODO usun penisa


@app.route('/wizyta', methods=['GET', 'POST'])
@login_required
def wizyta():
    if session["access"] == 3:
        if request.method == "GET":
            session.pop('_flashes', None)
            con = sqlite3.connect("db.db")
            cur = con.cursor()

            columns = ["Data", "Imię lekarza", "Nazwisko lekarza", "Imię pacjenta", "Nazwisko pacjenta"]
            cur.execute(
                "select Wizyta.id,Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id")
            rows = cur.fetchall()
            print(rows)
            # print(ziomki)
            return render_template("wizyta.html", columns=columns, rows=rows)
    if session["access"] == 2:
        if request.method == "GET":
            session.pop('_flashes', None)
            con = sqlite3.connect("db.db")
            cur = con.cursor()

            columns = ["Data", "Imię pacjenta", "Nazwisko pacjenta"]
            cur.execute("select id from Lekarz where Users_id=?",[session['user_id']])
            lekarz_id = cur.fetchall()
            print(lekarz_id, "ID LEKARZA")
            cur.execute(
                "select Wizyta.id,Wizyta.Data,Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.lekarz_Id =?", lekarz_id[0])
            rows = cur.fetchall()
            # print(ziomki)
            return render_template("wizyta.html", columns=columns, rows=rows) #TODO checkboxy jeden zaznaczony, id null w delecie wystrzelic, logut i przyciski przesunac
    if session["access"] == 1:
        if request.method == "GET":
            session.pop('_flashes', None)
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            print(session["user_id"], "id ziomiutka")
            columns = ["Data", "Imię lekarza", "Nazwisko lekarza"]
            cur.execute("select id from Pacjent where Users_id=?",[session['user_id']])
            pacjent_id = cur.fetchall()
            cur.execute(
                "select Wizyta.id,Wizyta.Data,Lekarz.Name, Lekarz.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.pacjent_Id =?", pacjent_id[0])
            rows = cur.fetchall()
            # print(ziomki)
            return render_template("wizyta.html", columns=columns, rows=rows)



@app.route('/wizyta_create', methods=['GET', 'POST'])
@login_required
def wizyta_create():
    if session["access"] == 3:
        if request.method == "GET":
            session.pop('_flashes', None)
            con = sqlite3.connect("db.db")
            cur = con.cursor()

            cur.execute("select Name,Surname from Lekarz")
            helper = cur.fetchall()
            lekarze = [' '.join(lekarz) for lekarz in helper]

            cur.execute("select Name,Surname from Pacjent")
            helper = cur.fetchall()
            pacjenci = [' '.join(pacjent) for pacjent in helper] #TODO pacjent - create wizyta wybierz lekarze

            return render_template("wizyta_create.html", lekarze=lekarze, pacjenci=pacjenci)
        if request.method == "POST":
            data = request.form['data']
            if not data:
                session.pop('_flashes', None)
                flash("Nowa data nie moze byc pusta!")
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Data", "Imię lekarza", "Nazwisko lekarza", "Imię pacjenta", "Nazwisko pacjenta"]
                cur.execute(
                    "select Wizyta.id, Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id")
                rows = cur.fetchall()
                return render_template("wizyta.html", columns=columns, rows=rows)
            # print(data)
            lekarz = request.form['lekarz']

            pacjent = request.form['pacjent']

            now = date(*map(int, data.split('-')))

            if now < datetime.today().date():
                session.pop('_flashes', None)
                flash("Nowa data nie moze byc z przeszlosci!")
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Data", "Imię lekarza", "Nazwisko lekarza", "Imię pacjenta", "Nazwisko pacjenta"]
                cur.execute(
                    "select Wizyta.id, Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id")
                rows = cur.fetchall()
                return render_template("wizyta.html", columns=columns, rows=rows)

            # print(pacjent)
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute("select id from Lekarz where Name = ? and Surname = ?",
                        [lekarz.split(" ")[0], lekarz.split(" ")[1]])
            lekarz = cur.fetchone()

            cur.execute("select id from Pacjent where Name = ? and Surname = ?",
                        [pacjent.split(" ")[0], pacjent.split(" ")[1]])
            pacjent = cur.fetchone()
            # print(isinstance(lekarz[0], "str"))
            # print(lekarz, pacjent)
            cur.execute("insert into Wizyta(id, data,lekarz_id, pacjent_id) values (null, ?,?,?)",
                        [str(data), int(lekarz[0]), int(pacjent[0])])
            con.commit()
            columns = ["Data", "Imię lekarza", "Nazwisko lekarza", "Imię pacjenta", "Nazwisko pacjenta"]
            cur = con.cursor()
            cur.execute(
                "select Wizyta.id, Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id")
            rows = cur.fetchall()
            session.pop('_flashes', None)
            flash("Dodano wizyte!")
            return render_template("wizyta.html", columns=columns, rows=rows)
    if session["access"] == 1:
        if request.method == "GET":
            session.pop('_flashes', None)
            con = sqlite3.connect("db.db")
            cur = con.cursor()

            cur.execute("select Name,Surname from Lekarz")
            helper = cur.fetchall()
            lekarze = [' '.join(lekarz) for lekarz in helper]

            cur.execute("select Name,Surname from Pacjent")
            helper = cur.fetchall()
            pacjenci = [' '.join(pacjent) for pacjent in helper] #TODO pacjent - create wizyta wybierz lekarze

            return render_template("wizyta_create.html", lekarze=lekarze, pacjenci=pacjenci)
        if request.method == "POST":
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            data = request.form['data']
            cur.execute("select id from Pacjent where Users_id=?", [session['user_id']])
            pacjent_id = cur.fetchall()

            if not data:
                session.pop('_flashes', None)
                flash("Nowa data nie moze byc pusta!")

                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Data", "Imię lekarza", "Nazwisko lekarza"]
                cur.execute(
                    "select Wizyta.id,Wizyta.Data,Lekarz.Name, Lekarz.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.pacjent_Id =?",
                    pacjent_id[0])
                rows = cur.fetchall()
                # print(ziomki)
                return render_template("wizyta.html", columns=columns, rows=rows)
            now = date(*map(int, data.split('-')))
            if now < datetime.today().date():
                session.pop('_flashes', None)
                flash("Nowa data nie moze byc z przeszlosci!")

                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Data", "Imię lekarza", "Nazwisko lekarza"]
                cur.execute(
                    "select Wizyta.id,Wizyta.Data,Lekarz.Name, Lekarz.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.pacjent_Id =?",
                    pacjent_id[0])
                rows = cur.fetchall()
                # print(ziomki)
                return render_template("wizyta.html", columns=columns, rows=rows)
            # print(data)
            lekarz = request.form['lekarz']

            # pacjent = request.form['pacjent']
            # print(pacjent)
            print(lekarz, "lekarinio")
            print(pacjent_id, "iddddddddd")
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute("select id from Lekarz where Name = ? and Surname = ?",
                        [lekarz.split(" ")[0], lekarz.split(" ")[1]])
            lekarz = cur.fetchone()
            cur.execute("insert into Wizyta(id, data,lekarz_id, pacjent_id) values (null, ?,?,?)",
                        [str(data), int(lekarz[0]), int(pacjent_id[0][0])])
            con.commit()
            columns = ["Data", "Imię lekarza", "Nazwisko lekarza"]

            cur.execute(
                "select Wizyta.id,Wizyta.Data,Lekarz.Name, Lekarz.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.pacjent_Id =?",
                pacjent_id[0])
            rows = cur.fetchall()
            # print(ziomki)
            flash("Dodano wizyte!")
            return render_template("wizyta.html", columns=columns, rows=rows)


@app.route('/wizyta_update', methods=['GET', 'POST'])
@login_required
def wizyta_update():
    if session["access"] == 3:
        if request.method == "GET":
            session.pop('_flashes', None)
            global id
            id = request.args.get("id")
            print(id, "id")
            if not id:
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Data", "Imię lekarza", "Nazwisko lekarza", "Imię pacjenta", "Nazwisko pacjenta"]
                cur.execute(
                    "select Wizyta.id, Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from "
                    "Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on "
                    "Wizyta.pacjent_id = Pacjent.id")
                rows = cur.fetchall()
                flash("Musisz wpierw zaznaczyc Wizyte")
                return render_template("wizyta.html", columns=columns, rows=rows)
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute("select * from Wizyta where Wizyta.id = ?", (id,))
            # wizyta = cur.fetchall()
            cur.execute("select Name,Surname from Lekarz")
            helper = cur.fetchall()
            lekarze = [' '.join(lekarz) for lekarz in helper]

            cur.execute("select Name,Surname from Pacjent")
            helper = cur.fetchall()
            pacjenci = [' '.join(pacjent) for pacjent in helper]
            return render_template("wizyta_update.html", lekarze=lekarze, pacjenci=pacjenci)
        if request.method == "POST":
            lekarz = request.form['lekarz']
            data = request.form['data']
            if not data:
                session.pop('_flashes', None)
                flash("Nowa data nie moze byc pusta!")
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Data", "Imię lekarza", "Nazwisko lekarza", "Imię pacjenta", "Nazwisko pacjenta"]
                cur.execute(
                    "select Wizyta.id, Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id")
                rows = cur.fetchall()
                return render_template("wizyta.html", columns=columns, rows=rows)
            pacjent = request.form['pacjent']
            now = date(*map(int, data.split('-')))
            if now < datetime.today().date():
                session.pop('_flashes', None)
                flash("Nowa data nie moze byc z przeszlosci!")
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Data", "Imię lekarza", "Nazwisko lekarza", "Imię pacjenta", "Nazwisko pacjenta"]
                cur.execute(
                    "select Wizyta.id, Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id")
                rows = cur.fetchall()
                return render_template("wizyta.html", columns=columns, rows=rows)
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                cur.execute("select id from Lekarz where Name = ? and Surname = ?",
                            [lekarz.split(" ")[0], lekarz.split(" ")[1]])
                lekarz = cur.fetchone()

                cur.execute("select id from Pacjent where Name = ? and Surname = ?",
                            [pacjent.split(" ")[0], pacjent.split(" ")[1]])
                pacjent = cur.fetchone()
                columns = ["Data", "Imię lekarza", "Nazwisko lekarza", "Imię pacjenta", "Nazwisko pacjenta"]

                cur.execute("update Wizyta set Data=?, lekarz_id = ?, pacjent_id = ? where id = ?",
                            [str(data), int(lekarz[0]), int(pacjent[0]), int(id)])
                con.commit()
                cur.execute(
                    "select Wizyta.id, Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id")
                rows = cur.fetchall()
                session.pop('_flashes', None)
                flash("Zmieniono wizytę!")
                return render_template("wizyta.html", columns=columns, rows=rows)  # TODO usun penisa
    if session["access"] == 1:
        if request.method == "GET":
            session.pop('_flashes', None)
            global id3
            id3 = request.args.get("id")
            if not id3:
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Data", "Imię lekarza", "Nazwisko lekarza"]
                cur.execute("select id from Pacjent where Users_id=?", [session['user_id']])
                pacjent_id = cur.fetchall()
                cur.execute(
                    "select Wizyta.id,Wizyta.Data,Lekarz.Name, Lekarz.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.pacjent_Id =?",
                    pacjent_id[0])
                rows = cur.fetchall()
                # print(ziomki)
                flash("Musisz wpierw zaznaczyć wizytę!")
                return render_template("wizyta.html", columns=columns, rows=rows)
            # print(id2, "id")
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute("select * from Wizyta where Wizyta.id = ?", (id3,))
            # wizyta = cur.fetchall()
            cur.execute("select Name,Surname from Lekarz")
            helper = cur.fetchall()
            lekarze = [' '.join(lekarz) for lekarz in helper]

            cur.execute("select Name,Surname from Pacjent")
            helper = cur.fetchall()
            pacjenci = [' '.join(pacjent) for pacjent in helper]
            return render_template("wizyta_update.html", lekarze=lekarze, pacjenci=pacjenci)
        if request.method == "POST":
            # lekarz = request.form['lekarz']
            data = request.form['data']

            if not data:
                session.pop('_flashes', None)
                flash("Nowa data nie moze byc pusta!")
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Data", "Imię lekarza", "Nazwisko lekarza"]
                cur.execute("select id from Pacjent where Users_id=?", [session['user_id']])
                pacjent_id = cur.fetchall()
                cur.execute(
                    "select Wizyta.id,Wizyta.Data,Lekarz.Name, Lekarz.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.pacjent_Id =?",
                    pacjent_id[0])
                rows = cur.fetchall()
                # print(ziomki)
                return render_template("wizyta.html", columns=columns, rows=rows)

            # pacjent = request.form['pacjent']
            now = date(*map(int, data.split('-')))

            if now < datetime.today().date():
                session.pop('_flashes', None)
                flash("Nowa data nie moze byc z przeszlosci!")
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Data", "Imię pacjenta", "Nazwisko pacjenta"]
                cur.execute("select id from Pacjent where Users_id=?", [session['user_id']])
                pacjent_id = cur.fetchall()
                # print(lekarz_id, "ID LEKARZA")
                cur.execute(
                    "select Wizyta.id,Wizyta.Data,Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.pacjent_id =?",
                    pacjent_id[0])
                rows = cur.fetchall()
                # print(ziomki)
                return render_template("wizyta.html", columns=columns, rows=rows)
            # pacjent = request.form['pacjent']
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute("update Wizyta set Data=? where id = ?",
                        [str(data), int(id3)])
            con.commit()
            # cur.execute("select id from Lekarz where Name = ? and Surname = ?",
            #             [lekarz.split(" ")[0], lekarz.split(" ")[1]])
            # lekarz = cur.fetchone()

            # cur.execute("select id from Pacjent where Name = ? and Surname = ?",
            #             [pacjent.split(" ")[0], pacjent.split(" ")[1]])
            # pacjent = cur.fetchone()
            session.pop('_flashes', None)
            columns = ["Data", "Imię lekarza", "Nazwisko lekarza"]
            cur.execute("select id from Pacjent where Users_id=?",[session['user_id']])
            pacjent_id = cur.fetchall()
            cur.execute(
                "select Wizyta.id,Wizyta.Data,Lekarz.Name, Lekarz.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.pacjent_Id =?", pacjent_id[0])
            rows = cur.fetchall()
            # print(ziomki)
            flash("Zmieniono wizytę!")
            return render_template("wizyta.html", columns=columns, rows=rows)
    if session["access"] == 2:
        if request.method == "GET":
            session.pop('_flashes', None)
            global id2
            id2 = request.args.get("id")
            if not id2:
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Data", "Imię pacjenta", "Nazwisko pacjenta"]
                cur.execute("select id from Lekarz where Users_id=?", [session['user_id']])
                lekarz_id = cur.fetchall()
                # print(lekarz_id, "ID LEKARZA")
                cur.execute(
                    "select Wizyta.id,Wizyta.Data,Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.pacjent_id =?",
                    lekarz_id[0])
                rows = cur.fetchall()
                session.pop('_flashes', None)
                flash("Musisz wpierw zaznaczyć wizytę!")
                # print(ziomki)
                return render_template("wizyta.html", columns=columns, rows=rows)
            print(id2, "id")
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute("select * from Wizyta where Wizyta.id = ?", (id2,))
            # wizyta = cur.fetchall()
            cur.execute("select Name,Surname from Lekarz")
            helper = cur.fetchall()
            lekarze = [' '.join(lekarz) for lekarz in helper]

            cur.execute("select Name,Surname from Pacjent")
            helper = cur.fetchall()
            pacjenci = [' '.join(pacjent) for pacjent in helper]
            return render_template("wizyta_update.html", lekarze=lekarze, pacjenci=pacjenci)
        if request.method == "POST":
            # lekarz = request.form['lekarz']
            data = request.form['data']

            if not data:
                session.pop('_flashes', None)
                flash("Nowa data nie moze byc pusta!")
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Data", "Imię pacjenta", "Nazwisko pacjenta"]
                cur.execute("select id from Lekarz where Users_id=?", [session['user_id']])
                lekarz_id = cur.fetchall()
                print(lekarz_id, "ID LEKARZA")
                cur.execute(
                    "select Wizyta.id,Wizyta.Data,Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.lekarz_Id =?",
                    lekarz_id[0])
                rows = cur.fetchall()
                # print(ziomki)
                return render_template("wizyta.html", columns=columns, rows=rows)

            # pacjent = request.form['pacjent']
            now = date(*map(int, data.split('-')))

            if now < datetime.today().date():
                session.pop('_flashes', None)
                flash("Nowa data nie moze byc z przeszlosci!")
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                columns = ["Data", "Imię pacjenta", "Nazwisko pacjenta"]
                cur.execute("select id from Lekarz where Users_id=?", [session['user_id']])
                lekarz_id = cur.fetchall()
                print(lekarz_id, "ID LEKARZA")
                cur.execute(
                    "select Wizyta.id,Wizyta.Data,Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.lekarz_Id =?",
                    lekarz_id[0])
                rows = cur.fetchall()
                # print(ziomki)
                return render_template("wizyta.html", columns=columns, rows=rows)
            # pacjent = request.form['pacjent']
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute("update Wizyta set Data=? where id = ?",
                        [str(data), int(id2)])
            con.commit()
            # cur.execute("select id from Lekarz where Name = ? and Surname = ?",
            #             [lekarz.split(" ")[0], lekarz.split(" ")[1]])
            # lekarz = cur.fetchone()

            # cur.execute("select id from Pacjent where Name = ? and Surname = ?",
            #             [pacjent.split(" ")[0], pacjent.split(" ")[1]])
            # pacjent = cur.fetchone()
            session.pop('_flashes', None)
            flash("Zmieniono wizytę!")
            columns = ["Data", "Imię pacjenta", "Nazwisko pacjenta"]

            cur.execute("select id from Lekarz where Users_id=?", [session['user_id']])
            lekarz_id = cur.fetchall()
            print(lekarz_id, "ID LEKARZA")
            cur.execute(
                "select Wizyta.id,Wizyta.Data,Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.lekarz_Id =?",
                lekarz_id[0])
            rows = cur.fetchall()  # TODO usun penisa
            return render_template("wizyta.html", columns=columns, rows=rows)


@app.route('/pacjent_deleteuser', methods=['GET', 'POST'])
@login_required
def pacjent_deleteuser():
    if request.method == "GET":
        session.pop('_flashes', None)
        id = request.args.get("id")
        if not id:
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            columns = ["Imie", "Nazwisko", "Pesel", "Telefon"]
            cur.execute(
                "select id, Name, Surname, Pesel, Telefon from Pacjent")
            rows = cur.fetchall()
            flash("Musisz wpierw zaznaczyc pacjenta!")
            return render_template("pacjent.html", columns=columns, rows=rows)  # TODO usun penisa
        # print(id, "id")
        print(id, "id")
        con = sqlite3.connect("db.db")
        cur = con.cursor()

        cur.execute("select Users_id from Pacjent where id = ?", id)

        pacjent_user_id = cur.fetchall()

        helper = pacjent_user_id[0][0]

        cur.execute("delete from Users where Users.id = ?", (helper,))
        con.commit()

        columns = ["Imie", "Nazwisko", "Pesel", "Telefon"]
        cur.execute(
            "select id, Name, Surname, Pesel, Telefon from Pacjent")
        rows = cur.fetchall()
        flash("Usunięto dane logowania!")
        return render_template("pacjent.html", columns=columns, rows=rows)  # TODO usun penisa

@app.route('/wizyta_delete', methods=['GET', 'POST'])
@login_required
def wizyta_delete():
        if request.method == "GET":
            session.pop('_flashes', None)
            id = request.args.get("id")
            print(id, "id")
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute("delete from Wizyta where Wizyta.id = ?", (id,))
            con.commit()
            if session['access'] == 3:
                if not id:
                    con = sqlite3.connect("db.db")
                    cur = con.cursor()
                    columns = ["Data", "Imię lekarza", "Nazwisko lekarza", "Imię pacjenta", "Nazwisko pacjenta"]
                    cur = con.cursor()
                    cur.execute(
                        "select Wizyta.id, Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id")
                    rows = cur.fetchall()
                    flash("Musisz wpierw zaznaczyc Wizyte")
                    return render_template("wizyta.html", columns=columns, rows=rows)
                columns = ["Data", "Imię lekarza", "Nazwisko lekarza", "Imię pacjenta", "Nazwisko pacjenta"]
                cur = con.cursor()
                cur.execute(
                    "select Wizyta.id, Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id")
                rows = cur.fetchall()
                flash("Musisz najpierw wybrać wizytę!")
                return render_template("wizyta.html", columns=columns, rows=rows)
            if session['access'] == 2:
                if not id:
                    con = sqlite3.connect("db.db")
                    cur = con.cursor()
                    columns = ["Data", "Imię pacjenta", "Nazwisko pacjenta"]
                    cur.execute("select id from Lekarz where Users_id=?", [session['user_id']])
                    lekarz_id = cur.fetchall()
                    print(lekarz_id, "ID LEKARZA")
                    cur.execute(
                        "select Wizyta.id,Wizyta.Data,Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.lekarz_Id =?",
                        lekarz_id[0])
                    flash("Musisz najpierw wybrać wizytę!")
                    rows = cur.fetchall()
                    return render_template("wizyta.html", columns=columns, rows=rows)
                columns = ["Data", "Imię pacjenta", "Nazwisko pacjenta"]
                cur.execute("select id from Lekarz where Users_id=?", [session['user_id']])
                lekarz_id = cur.fetchall()
                print(lekarz_id, "ID LEKARZA")
                cur.execute(
                    "select Wizyta.id,Wizyta.Data,Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.lekarz_Id =?",
                    lekarz_id[0])
                rows = cur.fetchall()
                # print(ziomki)
                return render_template("wizyta.html", columns=columns, rows=rows)
            if session['access'] == 1:
                    if not id:
                        con = sqlite3.connect("db.db")
                        cur = con.cursor()
                        print(session["user_id"], "id ziomiutka")
                        columns = ["Data", "Imię lekarza", "Nazwisko lekarza"]
                        cur.execute("select id from Pacjent where Users_id=?", [session['user_id']])
                        pacjent_id = cur.fetchall()
                        cur.execute(
                            "select Wizyta.id,Wizyta.Data,Lekarz.Name, Lekarz.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.pacjent_Id =?",
                            pacjent_id[0])
                        rows = cur.fetchall()
                        flash("Musisz najpierw wybrać wizytę!")
                        # print(ziomki)
                        return render_template("wizyta.html", columns=columns, rows=rows)
                    session.pop('_flashes', None)
                    con = sqlite3.connect("db.db")
                    cur = con.cursor()
                    print(session["user_id"], "id ziomiutka")
                    columns = ["Data", "Imię lekarza", "Nazwisko lekarza"]
                    cur.execute("select id from Pacjent where Users_id=?", [session['user_id']])
                    pacjent_id = cur.fetchall()
                    cur.execute(
                        "select Wizyta.id,Wizyta.Data,Lekarz.Name, Lekarz.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id where Wizyta.pacjent_Id =?",
                        pacjent_id[0])
                    rows = cur.fetchall()
                    flash("Usunięto wizytę!")
                    # print(ziomki)
                    return render_template("wizyta.html", columns=columns, rows=rows)


if __name__ == '__main__': #TODO create pacjent ---- wizyta pacjent - create tylko data, zmien wizyte tylko data
    app.run()
