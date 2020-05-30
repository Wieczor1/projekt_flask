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
            "select Wizyta.Data, Lekarz.Name, Lekarz.Surname, Pacjent.Name, Pacjent.Surname from Wizyta inner join Lekarz on  Wizyta.lekarz_Id = Lekarz.id inner join Pacjent on Wizyta.pacjent_id = Pacjent.id")
        rows = cur.fetchall()
        # print(ziomki)
        return render_template("wizyta.html", columns=columns, rows=rows)
    else:
        return render_template("login.html")


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


@app.route('/wizyta_update/<id>/', methods=['GET', 'POST'])
def wizyta_update(id):
    if request.method == "GET":
        con = sqlite3.connect("db.db")
        cur = con.cursor()
        cur.execute("select * from Wizyta where id = ?", id)
        print(cur.fetchall())

        return


if __name__ == '__main__':
    app.run()
