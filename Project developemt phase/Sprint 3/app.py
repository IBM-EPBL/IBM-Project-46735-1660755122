from flask import Flask, render_template, request, redirect, session ,url_for
import ibm_db
import re

app = Flask(__name__)

hostname = '1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;'
uid = 'vjx02808'
pwd = 'ZheXo0qLEishDDb0'
driver = "{IBM DB2 ODBC DRIVER}"
db_name = 'Bludb'
port = '32286'
protocol = 'TCPIP'
cert = "certi.crt"
dsn = (
    "DATABASE ={0};"
    "HOSTNAME ={1};"
    "PORT ={2};"
    "UID ={3};"
    "SECURITY=SSL;"
    "PROTOCOL={4};"
    "PWD ={6};"
).format(db_name, hostname, port, uid, protocol, cert, pwd)
connection = ibm_db.connect(dsn, "", "") 
app.secret_key = 'a'
  

#HOME--PAGE
@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/")
def add():
    return render_template("home.html")



#SIGN--UP--OR--REGISTER


@app.route("/signup")
def signup():
    return render_template("signup.html")



@app.route('/register', methods =['GET', 'POST'])
def register():
    global user_email
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        query = "SELECT * FROM register WHERE email=?;"
        stmt = ibm_db.prepare(connection, query)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            query = "INSERT INTO register values(?,?,?);"
            stmt = ibm_db.prepare(connection, query)
            ibm_db.bind_param(stmt, 1, username)
            ibm_db.bind_param(stmt, 2, email)
            ibm_db.bind_param(stmt, 3, password)
            ibm_db.execute(stmt)
            session['loggedin'] = True
            session['id'] = email
            user_email = email
            session['email'] = email
            session['username'] = username

            msg = 'You have successfully registered ! Proceed Login Process'
            return render_template('login.html', msg = msg)
    else:
        msg = 'PLEASE FILL OUT OF THE FORM'
        return render_template('register.html', msg=msg)
        
 
        
 #LOGIN--PAGE
    
@app.route("/signin")
def signin():
    return render_template('login.html')
        
@app.route('/login',methods =['GET', 'POST'])
def login():
    global user_email
    msg = ''
    
    if request.method == 'POST' :
        email = request.form['email']
        password = request.form['password']
        sql = "SELECT * FROM register WHERE email =? AND password=?;"
        stmt = ibm_db.prepare(connection, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print (account)
        
        if account:
            session['loggedin'] = True
            session['id'] = account['EMAIL']
            user_email=  account['EMAIL']
            session['email']=account['EMAIL']
            session['username'] = account['USERNAME']
           
            return redirect('/home')
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

#CHANGE FORGOT PASSWORD

@app.route("/forgot")
def forgot():
    return render_template('forgot.html')
        
@app.route("/forgotpw", methods =['GET', 'POST'])
def forgotpw():
    msg = ''
    if request.method == 'POST' :
        email = request.form['email']
        password = request.form['password']
        query = "SELECT * FROM register WHERE email=?;"
        stmt = ibm_db.prepare(connection, query)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            query = "UPDATE register SET password = ? WHERE email = ?;"
            stmt = ibm_db.prepare(connection, query)
            ibm_db.bind_param(stmt, 1, password)
            ibm_db.bind_param(stmt, 2, email)
            ibm_db.execute(stmt)
            msg = 'Successfully changed your password ! Proceed Login Process'
            return render_template('login.html', msg = msg)
    else:
        msg = 'PLEASE FILL OUT THE CORRECT DETAILS'
        return render_template('forgot.html', msg=msg)


#ADDING----DATA


@app.route("/add")
def adding():
    return render_template('add.html')


@app.route('/addexpense',methods=['GET', 'POST'])
def addexpense():
    global user_email
    que = "SELECT * FROM expenses where id = ? ORDER BY 'dates' DESC"
    stm = ibm_db.prepare(connection, que)
    ibm_db.bind_param(stm, 1, session['email'])
    ibm_db.execute(stm) 
    dictionary=ibm_db.fetch_assoc(stm)
    expense=[]
    while dictionary != False:
        exp=(dictionary["ID"],dictionary["DATES"],dictionary["EXPENSENAME"],dictionary["AMOUNT"],dictionary["PAYMODE"],dictionary["CATEGORY"])
        expense.append(exp)
        dictionary = ibm_db.fetch_assoc(stm)
    i=len(expense)+1
    indexes=str(i)
    dates = request.form['date']
    expensename = request.form['expensename']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']
    query = "INSERT INTO expenses VALUES (?,?,?,?,?,?,?);"
    stmt = ibm_db.prepare(connection, query)
    ibm_db.bind_param(stmt, 1, session['email'])
    ibm_db.bind_param(stmt, 2, dates)
    ibm_db.bind_param(stmt, 3, expensename)
    ibm_db.bind_param(stmt, 4, amount)
    ibm_db.bind_param(stmt, 5, paymode)
    ibm_db.bind_param(stmt, 6, category)
    ibm_db.bind_param(stmt, 7, indexes)
    ibm_db.execute(stmt)
    print(dates + " " + expensename + " " + amount + " " + paymode + " " + category)
    
    return redirect("/display")



#DISPLAY---graph 

@app.route("/display")
def display():
    query = "SELECT * FROM expenses where id = ? ORDER BY 'dates' DESC"
    stmt = ibm_db.prepare(connection, query)
    ibm_db.bind_param(stmt, 1, session['email'])
    ibm_db.execute(stmt) 
    dictionary=ibm_db.fetch_assoc(stmt)
    rexpense=[]
    while dictionary != False:
        exp=(dictionary["ID"],dictionary["DATES"],dictionary["EXPENSENAME"],dictionary["AMOUNT"],dictionary["PAYMODE"],dictionary["CATEGORY"],dictionary["IDX"])
        rexpense.append(exp)
        dictionary = ibm_db.fetch_assoc(stmt)
    query = "SELECT MONTH(dates) as DATES, SUM(amount) as AMOUNT FROM expenses WHERE id=? AND YEAR(dates)= YEAR(now()) GROUP BY MONTH(dates);"
    stmt = ibm_db.prepare(connection, query)
    ibm_db.bind_param(stmt, 1,session['email'])
    ibm_db.execute(stmt)
    dictionary=ibm_db.fetch_assoc(stmt)
    texpense=[]
    while dictionary != False:
        exp=(dictionary["DATES"],dictionary["AMOUNT"])
        texpense.append(exp)
        dictionary = ibm_db.fetch_assoc(stmt)
    print(texpense)
      
    query = "SELECT * FROM expenses WHERE id = ? AND YEAR(dates)= YEAR(now());"
    stmt = ibm_db.prepare(connection, query)
    ibm_db.bind_param(stmt, 1,session['email'])
    ibm_db.execute(stmt)
    dictionary=ibm_db.fetch_assoc(stmt)
    expense=[]
    while dictionary != False:
        exp=(dictionary["ID"],dictionary["DATES"],dictionary["EXPENSENAME"],dictionary["AMOUNT"],dictionary["PAYMODE"],dictionary["CATEGORY"],dictionary["IDX"])
        expense.append(exp)
        dictionary = ibm_db.fetch_assoc(stmt)
  
    total=0
    t_food=0
    t_entertainment=0
    t_business=0
    t_rent=0
    t_EMI=0
    t_other=0
 
     
    for x in expense:
          total += x[3]
          if x[5] == "food":
              t_food += x[3]
            
          elif x[5] == "entertainment":
              t_entertainment  += x[3]
        
          elif x[5] == "business":
              t_business  += x[3]
          elif x[5] == "rent":
              t_rent  += x[3]
           
          elif x[5] == "EMI":
              t_EMI  += x[3]
         
          elif x[5] == "other":
              t_other  += x[3]
            
    print(total)
        
    print(t_food)
    print(t_entertainment)
    print(t_business)
    print(t_rent)
    print(t_EMI)
    print(t_other)


     
    return render_template("display.html",rexpense=rexpense, texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
   
    

#delete---the--data

@app.route('/delete/<idx>', methods = ['POST', 'GET' ])
def delete(idx):
    query = "DELETE FROM expenses WHERE id=? and idx=?;"
    stmt = ibm_db.prepare(connection, query)
    ibm_db.bind_param(stmt, 1, session["email"])
    ibm_db.bind_param(stmt, 2, idx)
    ibm_db.execute(stmt)
    print('deleted successfully')    
    return render_template("display.html")
    
 
    
#UPDATE---DATA

@app.route('/edit/<id>', methods = ['POST', 'GET' ])
def edit(id):
    query = "SELECT * FROM expenses WHERE id=? and idx=?;"
    stmt = ibm_db.prepare(connection, query)
    ibm_db.bind_param(stmt, 1, session['email'])
    ibm_db.bind_param(stmt, 2, id)
    ibm_db.execute(stmt)
    dictionary=ibm_db.fetch_assoc(stmt)
    expense=[]
    while dictionary != False:
        exp=(dictionary["ID"],dictionary["DATES"],dictionary["EXPENSENAME"],dictionary["AMOUNT"],dictionary["PAYMODE"],dictionary["CATEGORY"],dictionary["IDX"])
        expense.append(exp)
        dictionary = ibm_db.fetch_assoc(stmt)
    print(expense)
    return render_template('edit.html', expenses = expense[0])




@app.route('/update/<id>', methods = ['POST'])
def update(id):
  if request.method == 'POST' :
      dates = request.form['date']
      expensename = request.form['expensename']
      amount = request.form['amount']
      paymode = request.form['paymode']
      category = request.form['category']
      query = "UPDATE expenses SET dates = ? , expensename = ? , amount = ?, paymode = ?, category = ? WHERE id = ? and idx=?;"
      stmt = ibm_db.prepare(connection, query)
      ibm_db.bind_param(stmt, 1, dates)
      ibm_db.bind_param(stmt, 2, expensename)
      ibm_db.bind_param(stmt, 3, amount)
      ibm_db.bind_param(stmt, 4, paymode)
      ibm_db.bind_param(stmt, 5, category)
      ibm_db.bind_param(stmt, 6, session['email'])
      ibm_db.bind_param(stmt, 7, id)
      ibm_db.execute(stmt)
      
      print('successfully updated')
      return redirect("/display")
     
      


#REPORT

@app.route("/today")
def today():
      query = "SELECT dates, amount FROM expenses  WHERE id = ? AND DATE(dates) = DATE(NOW()); "
      stmt = ibm_db.prepare(connection, query)
      ibm_db.bind_param(stmt, 1, str(session['email']))
      ibm_db.execute(stmt)
      dictionary=ibm_db.fetch_assoc(stmt)
      texpense=[]
      while dictionary != False:
        exp=(dictionary["DATES"],dictionary["AMOUNT"])
        texpense.append(exp)
        dictionary = ibm_db.fetch_assoc(stmt)
      print(texpense)
      
      query = "SELECT * FROM expenses WHERE id = ? AND DATE(dates) = DATE(NOW())"
      stmt = ibm_db.prepare(connection, query)
      ibm_db.bind_param(stmt, 1, session['email'])
      ibm_db.execute(stmt)
      dictionary=ibm_db.fetch_assoc(stmt)
      expense=[]
      while dictionary != False:
            exp=(dictionary["AMOUNT"],dictionary["PAYMODE"],dictionary["CATEGORY"])
            expense.append(exp)
            dictionary = ibm_db.fetch_assoc(stmt)
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += x[0]
          if x[2] == "food":
              t_food += x[0]
            
          elif x[2] == "entertainment":
              t_entertainment  += x[0]
        
          elif x[2] == "business":
              t_business  += x[0]
          elif x[2] == "rent":
              t_rent  += x[0]
           
          elif x[2] == "EMI":
              t_EMI  += x[0]
         
          elif x[2] == "other":
              t_other  += x[0]
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
     

@app.route("/month")
def month():
      query = "SELECT dates, SUM(amount) as AMOUNT FROM expenses WHERE id= ? AND MONTH(dates)= MONTH(now()) GROUP BY dates ORDER BY dates;"
      stmt = ibm_db.prepare(connection, query)
      ibm_db.bind_param(stmt, 1, str(session['email']))
      ibm_db.execute(stmt)
      dictionary=ibm_db.fetch_assoc(stmt)
      texpense=[]
      while dictionary != False:
        exp=(dictionary["DATES"],dictionary["AMOUNT"])
        texpense.append(exp)
        dictionary = ibm_db.fetch_assoc(stmt)
      print(texpense)
      
      query = "SELECT * FROM expenses WHERE id = ? AND MONTH(dates)= MONTH(now());"
      stmt = ibm_db.prepare(connection, query)
      ibm_db.bind_param(stmt, 1, session['email'])
      ibm_db.execute(stmt)
      dictionary=ibm_db.fetch_assoc(stmt)
      expense=[]
      while dictionary != False:
        exp=(dictionary["ID"],dictionary["DATES"],dictionary["EXPENSENAME"],dictionary["AMOUNT"],dictionary["PAYMODE"],dictionary["CATEGORY"],dictionary["IDX"])
        expense.append(exp)
        dictionary = ibm_db.fetch_assoc(stmt)
      
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += x[3]
          if x[5] == "food":
              t_food += x[3]
            
          elif x[5] == "entertainment":
              t_entertainment  += x[3]
        
          elif x[5] == "business":
              t_business  += x[3]
          elif x[5] == "rent":
              t_rent  += x[3]
           
          elif x[5] == "EMI":
              t_EMI  += x[3]
         
          elif x[5] == "other":
              t_other  += x[3]
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("month.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
         
@app.route("/year")
def year():
      query = "SELECT MONTH(dates) as DATES, SUM(amount) as AMOUNT FROM expenses WHERE id=? AND YEAR(dates)= YEAR(now()) GROUP BY MONTH(dates);"
      stmt = ibm_db.prepare(connection, query)
      ibm_db.bind_param(stmt, 1,session['email'])
      ibm_db.execute(stmt)
      dictionary=ibm_db.fetch_assoc(stmt)
      texpense=[]
      while dictionary != False:
        exp=(dictionary["DATES"],dictionary["AMOUNT"])
        texpense.append(exp)
        dictionary = ibm_db.fetch_assoc(stmt)
      print(texpense)
      
      query = "SELECT * FROM expenses WHERE id = ? AND YEAR(dates)= YEAR(now());"
      stmt = ibm_db.prepare(connection, query)
      ibm_db.bind_param(stmt, 1,session['email'])
      ibm_db.execute(stmt)
      dictionary=ibm_db.fetch_assoc(stmt)
      expense=[]
      while dictionary != False:
        exp=(dictionary["ID"],dictionary["DATES"],dictionary["EXPENSENAME"],dictionary["AMOUNT"],dictionary["PAYMODE"],dictionary["CATEGORY"],dictionary["IDX"])
        expense.append(exp)
        dictionary = ibm_db.fetch_assoc(stmt)
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += x[3]
          if x[5] == "food":
              t_food += x[3]
            
          elif x[5] == "entertainment":
              t_entertainment  += x[3]
        
          elif x[5] == "business":
              t_business  += x[3]
          elif x[5] == "rent":
              t_rent  += x[3]
           
          elif x[5] == "EMI":
              t_EMI  += x[3]
         
          elif x[5] == "other":
              t_other  += x[3]
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("year.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )

#log-out

@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('home.html')

             

if __name__ == "__main__":
    app.run(debug=True)