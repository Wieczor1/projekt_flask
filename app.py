from datetime import datetime

from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
con = sqlite3.connect("db.db")
cur = con.cursor()
cur.execute("select Wizyta.Data, Lekarz.Surname from Wizyta inner join Lekarz on Wizyta.Lekarz_Id = Lekarz.Id")
wizyty = cur.fetchall()
# print(wizyty)


# @app.route('/')
# def hello_world():
#     return 'Hello World!'
#

@app.route('/', methods=['GET', 'POST'])
def login():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        cur.execute("select * from Users where username = ? and password = ?", [username, password])
        ziomki = cur.fetchall()

        columns = ["Data", "Imię lekarza", "Nazwisko lekarza", "Imię pacjenta", "Nazwisko pacjenta"]

        cur.execute(
            "select Wizyta.id, Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id")
        rows = cur.fetchall()
        # print(ziomki)
        return render_template("wizyta.html", columns=columns, rows=rows)
    else:
        return render_template("login.html")

@app.route('/pacjent', methods=['GET', 'POST'])
def pacjent():
    if request.method == "GET":
        con = sqlite3.connect("db.db")
        cur = con.cursor()

        columns = ["Imie", "Nazwisko", "Pesel", "Telefon"]
        cur.execute(
            "select id, Name, Surname, Pesel, Telefon from Pacjent")
        rows = cur.fetchall()
        return render_template("pacjent.html", columns=columns, rows=rows)

@app.route('/pacjent_create', methods=['GET', 'POST']) #TODO logowanie
def pacjent_create():
    if request.method == "GET":
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
        cur.execute("insert into users(id, username, password, access) values (null, ?, ?, 1) ", [username, password])
        con.commit()
        cur.execute("select id from Users where username = ? and password = ?", [username, password])
        id = cur.fetchall()
        print(id , "id")
        cur.execute("insert into pacjent(name, surname, pesel, telefon, users_id) values (?,?,?,?,?)",[name, surname, pesel, telefon, int(id[0][0])])
        con.commit()

        columns = ["Imie", "Nazwisko", "Pesel", "Telefon"]
        cur.execute(
            "select id, Name, Surname, Pesel, Telefon from Pacjent")
        rows = cur.fetchall()
        return render_template("pacjent.html", columns=columns, rows=rows)


@app.route('/pacjent_update', methods=['GET', 'POST']) #TODO logowanie
def pacjent_update():
    if request.method == "GET":
        global id
        id = request.args.get("id")
        print(id, "id")
        con = sqlite3.connect("db.db")
        cur = con.cursor()
        # cur.execute("select * from Wizyta where Wizyta.id = ?", (id,))
       # wizyta = cur.fetchall()
        return render_template("pacjent_update.html")
    if request.method == "POST":
        name = request.form["name"]
        surname = request.form["surname"]
        pesel = request.form["pesel"]
        telefon = request.form["telefon"]
        username = request.form["username"]
        password = request.form["password"]
        con = sqlite3.connect("db.db")
        cur = con.cursor()

        cur.execute("select Users_id from Pacjent where id = ?", id)

        pacjent_user_id = cur.fetchall()

        helper = pacjent_user_id[0][0]
        print(helper)

        cur.execute(
            "update Pacjent set Name=?, Surname = ?, Pesel = ?, Telefon = ?, Users_id = ? where id=?",
            [name, surname, pesel, telefon, helper, id])
        con.commit()

        columns = ["Imie", "Nazwisko", "Pesel", "Telefon"]
        cur.execute(
            "select id, Name, Surname, Pesel, Telefon from Pacjent")
        rows = cur.fetchall()
        return render_template("pacjent.html", columns=columns, rows=rows)

@app.route('/pacjent_delete', methods=['GET', 'POST'])
def pacjent_delete():
    if request.method == "GET":
        id = request.args.get("id")
        print(id, "id")
        con = sqlite3.connect("db.db")
        cur = con.cursor()
        cur.execute("delete from Pacjent where Pacjent.id = ?", (id,))
        con.commit()
        columns = ["Imie", "Nazwisko", "Pesel", "Telefon"]
        cur.execute(
            "select id, Name, Surname, Pesel, Telefon from Pacjent")
        rows = cur.fetchall()
        return render_template("pacjent.html", columns=columns, rows=rows)



@app.route('/lekarz', methods=['GET', 'POST'])
def lekarz():
    if request.method == "GET":
        con = sqlite3.connect("db.db")
        cur = con.cursor()

        columns = ["Imie", "Nazwisko", "Pesel", "Telefon", "Pensja"]
        cur.execute(
            "select id ,Name, Surname, Pesel, Telefon, Salary from Lekarz")
        rows = cur.fetchall()
        return render_template("lekarz.html", columns=columns, rows=rows)


@app.route('/wizyta', methods=['GET', 'POST'])
def wizyta():
    if request.method == "GET":
        con = sqlite3.connect("db.db")
        cur = con.cursor()

        columns = ["Data", "Imię lekarza", "Nazwisko lekarza", "Imię pacjenta", "Nazwisko pacjenta"]
        cur.execute(
            "select Wizyta.id, Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id")
        rows = cur.fetchall()
        # print(ziomki)
        return render_template("wizyta.html", columns=columns, rows=rows)


@app.route('/wizyta_create', methods=['GET', 'POST'])
def wizyta_create():
    if request.method == "GET":
        con = sqlite3.connect("db.db")
        cur = con.cursor()

        cur.execute("select Name,Surname from Lekarz")
        helper = cur.fetchall()
        lekarze = [' '.join(lekarz) for lekarz in helper]

        cur.execute("select Name,Surname from Pacjent")
        helper = cur.fetchall()
        pacjenci = [' '.join(pacjent) for pacjent in helper]

        return render_template("wizyta_create.html", lekarze=lekarze, pacjenci=pacjenci)
    if request.method == "POST":
        data = request.form['data']
        # print(data)
        lekarz = request.form['lekarz']

        pacjent = request.form['pacjent']
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
        return render_template("wizyta.html", columns=columns, rows=rows)

@app.route('/wizyta_update', methods=['GET', 'POST'])
def wizyta_update():

    if request.method == "GET":
        global id
        id = request.args.get("id")
        print(id, "id")
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
        pacjent = request.form['pacjent']
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
        return render_template("wizyta.html", columns=columns, rows=rows) #TODO usun penisa

@app.route('/wizyta_delete', methods=['GET', 'POST'])
def wizyta_delete():
    if request.method == "GET":
        id = request.args.get("id")
        print(id, "id")
        con = sqlite3.connect("db.db")
        cur = con.cursor()
        cur.execute("delete from Wizyta where Wizyta.id = ?", (id,))
        con.commit()
        columns = ["Data", "Imię lekarza", "Nazwisko lekarza", "Imię pacjenta", "Nazwisko pacjenta"]
        cur = con.cursor()
        cur.execute(
            "select Wizyta.id, Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id")
        rows = cur.fetchall()
        return render_template("wizyta.html", columns=columns, rows=rows)


if __name__ == '__main__':
    app.run()
