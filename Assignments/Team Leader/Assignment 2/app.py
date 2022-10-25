from flask import Flask, render_template, request, redirect, url_for
import ibm_db

app = Flask(__name__)

try:
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;PROTOCOL=TCPIP;UID=vjx02808;PWD=ZheXo0qLEishDDb0;", "", "")
    print("connected")
except:
    print("failed")

def insert_values(conn, email, username, rollno, pwd):
    sql = "INSERT into user values ('{}', '{}','{}', '{}')".format(email, username, rollno, pwd)
    stmt = ibm_db.exec_immediate(conn, sql)
    print("Number of affected rows: ", ibm_db.num_rows(stmt))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signin")
def render_signin(accountok=True):
    if accountok == True:
        return render_template('login.html', message = "")
    else:
        return render_template('login.html', message = "Username/Password is wrong")

@app.route("/login", methods = ['POST', 'GET'])
def checkLogin():
    if request.method == 'POST':
        mail = request.form.get('email',False)
        pwd = request.form.get('password',False)
        sql = "SELECT * from userdetails where email = '{}'".format(mail)
        
        stmt = ibm_db.exec_immediate(conn, sql)
        dict = ibm_db.fetch_assoc(stmt)
        if dict == False:
            return render_signin(False)
        if (mail == dict['email'].strip() and pwd == dict['password'].strip()):
            return render_template("welcome.html", user=dict['username'])
        else:
            return render_signin(False)
    return render_signin(True)

@app.route("/register", methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('username')
        roll = request.form.get('rollno')
        pwd = request.form.get('password')
        insert_values(conn, email, name, roll, pwd)
        return redirect(url_for('checkLogin'))
    return render_template("register.html")


if __name__ == '__main__':
    app.debug = True
    app.run()