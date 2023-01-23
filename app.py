from flask import Flask,render_template,request,redirect, url_for,flash,session
import mysql.connector as sql
import random
from datetime import timedelta ,datetime


mydb = sql.connect(host="localhost",user="root",password="vishvaa_vsk",autocommit=True,database="bankmanagement")
cur = mydb.cursor(dictionary=True)

cur.execute("select * from account;")
usersDic = cur.fetchall()

def updateDic():# func which updates dic when new details added!
    global usersDic
    cur.execute("select * from account;")
    usersDic = cur.fetchall()

def accnocreate():
    no,pre = random.randint(100000,9999999),"AXB"
    accno = pre+str(no)
    for i in range(len(usersDic)):
        if usersDic[i]["AccNo"]==accno:
            accno = accnocreate()
    return accno

app = Flask(__name__)
app.secret_key = "8d4a9c0eae5147a030d36c48989892c8"
app.permanent_session_lifetime = timedelta(minutes=3)

@app.route("/",methods=["GET","POST"])# Login route
def Login():
    if request.method=="POST":
        session.permanent=True
        accno,passwd=request.form["accno"],request.form["passwd"]
        for i in range(len(usersDic)):
            if usersDic[i]["AccNo"]==accno and usersDic[i]["passwd"]==passwd:
                session["Accno"]=accno
                session["username"] = usersDic[i]["Name"]
                return redirect(url_for("home"))
            flash("Invalid credentials! or account not Exist!!")
    return render_template("index.html")

@app.route("/logout")
def Logout():
    session.pop('Accno', None)
    session.pop('username',None)
    return redirect(url_for('Login'))

@app.route("/signup",methods = ["GET","POST"])
def Signup():
    updateDic()
    accno = accnocreate()
    if request.method=="POST":#checking POST method!
        name,address,DOB,cno,obal,email,passwd,repasswd,acc_type = request.form['name'],request.form['address'],request.form["dob"],int(request.form["cno"]),2000,request.form["email"],request.form["passwd"],request.form["re-passwd"],request.form["acc-type"]# Gathering all info
        for i in range(len(usersDic)):
            if name in usersDic[i]["Name"]:
                return render_template("signup.html",data="Already a account exist in this name!")
        if passwd == repasswd:# check new passwd == repasswd
            cur.execute(f"insert into account values('{name}','{accno}','{DOB}','{address}',{cno},{obal},{obal},'{passwd}','{email}','{acc_type}');")# change values in DB
            flash("Registered Successfully!!")
            updateDic()
            return render_template("accnoshow.html",name=name,AccNo=accno)
        else:
            flash("Password not matched!")#if not signup
    return render_template("signup.html")

@app.route("/home",methods=["GET","POST"])# Home page route!
def home():
    if "Accno" and "username" in session:
        name = session["username"]
        accno = session["Accno"]
        return render_template("home.html",name=name,accno=accno)
    else:
        return redirect(url_for("Login"))

@app.route("/resetpasswd",methods=["GET","POST"])
def resetPassword():
    updateDic()
    if request.method=="POST":
        accno,passwd,repasswd,email = request.form["accno"],request.form["passwd"], request.form["re-passwd"], request.form["email"]
        for i in range(len(usersDic)):
            if email in usersDic[i]["Email"]:
                if passwd == repasswd:
                    cur.execute(f"update account set passwd = '{passwd}' where AccNo = '{accno}';")
                    return redirect(url_for("home",accno=accno,name=usersDic[i]["Name"]))
                else:
                    flash("Password not matched!")
            else:
                flash("Incorrect email Id")
    updateDic()
    return render_template("resetpasswd.html")

@app.route("/changeuserdetails",methods=["GET","POST"])
def changeDetails():
    if "Accno" in session:
        accno=session["Accno"] 
        if request.method == "POST":
            name,dob,address,contno,email = request.form["name"],request.form["dob"],request.form["address"],request.form["cno"],request.form["email"]
            try:
                cur.execute(f"update account set Name = '{name}',DOB = '{dob}',Address='{address}',ContactNo = {int(contno)} ,Email='{email}' where AccNo ='{accno}';")
                flash("Details updated successfully!")
            except:
                flash("Error occured! Can't update Details..")
    else:
        return redirect(url_for("Login"))
    return render_template("changedetails.html",accno=accno)

@app.route("/balanceEnquiry",methods=["GET","POST"])
def balanceEq():
    if "Accno" in session:
        accno = session["Accno"]
        cur.execute(f"select * from account where AccNo = '{accno}';")
        res = cur.fetchall()
        return render_template("viewacc.html",datas=res,rep="XXX")
    else:
        redirect(url_for("Login"))
    return render_template("viewacc.html")

@app.route("/accountdetails",methods=["GET","POST"])
def customerDetails():
    if "Accno" in session:
        accno = session["Accno"]
        cur.execute(f"select * from account where AccNo = '{accno}';")
        result = cur.fetchall()
        return render_template("custdetails.html",records=result)
    else:
        redirect(url_for("Login"))
    return render_template("custdetails.html")

@app.route("/deleteaccount",methods=['GET','POST'])
def deleteAccount():
    accno = session["Accno"]
    cur.execute("SET SQL_SAFE_UPDATES = 0;")
    cur.execute(f"delete from account where AccNo = '{accno}';")
    flash("Successfully Deleted!!!")
    return redirect(url_for('Login')) 

@app.route("/transfer",methods=["GET","POST"])
def transfer():
    now = datetime.now()
    if "Accno" in session:
        accno = session["Accno"]
        if request.method == "POST":
            fr,amount,to,passwd,trans_type = request.form["from"],request.form["amount"],request.form["to"],request.form["passwd"],request.form["trans-type"]
            if fr != to and int(amount)!=0 and fr==accno:
                cur.execute(f"select * from account where AccNo = '{accno}';")
                resultf = cur.fetchall()
                for fdata in resultf:
                    if fdata['passwd']==passwd:
                        for i in range(len(usersDic)):
                            if usersDic[i]["AccNo"] == to:
                                if int(amount)>=100:
                                    if int(amount) < fdata["Balance"]:
                                        cur.execute(f"select * from account where AccNo = '{to}';")
                                        result_to = cur.fetchall()
                                        from_balance = fdata["Balance"]
                                        for tdata in result_to:
                                            to_balance = tdata["Balance"]
                                        if fdata["Balance"] <= 0:
                                            cur.execute(f"update account set Balance = 0 where AccNo='{fr}'")
                                        if tdata["Balance"] <= 0:
                                            cur.execute(f"update account set Balance = 0 where AccNo='{to}'")
                                        new_from_balance=from_balance-int(amount)
                                        new_to_balance=to_balance+int(amount)

                                        cur.execute(f"update account set Balance = {new_from_balance} where AccNo = '{fr}'")
                                        cur.execute(f"update account set Balance = {new_to_balance} where AccNo = '{to}'")
                                        flash("Transfer Successfull")
                                        updateDic()

                                        cur.execute(f"select Balance where AccNo = '{fr}'")
                                        balance_fr=cur.fetchone()
                                        cur.execute(f"select Balance where AccNo = '{to}'")
                                        balance_to=cur.fetchone()
                                        cur.execute(f"insert into trans_details values('{fr}','{trans_type}','{str(now.strftime('%d-%m-%Y %H:%M:%S'))}','{amount}',{balance_fr})")
                                        cur.execute(f"insert into trans_details values('{to}','{trans_type}','{str(now.strftime('%d-%m-%Y %H:%M:%S'))}','{amount}',{balance_to})")

                                    else:
                                        flash("Insufficient Balance in your account")
                                else:
                                    flash("Transfer amount should be significantly greater than ₹100!")
                    else:
                        flash("Password doesn't matched!")
    else:
        return redirect(url_for("Login"))
    return render_template("transfer.html",accno=accno)

@app.route("/history",methods=["POST","GET"])
def trans_history():
    if "Accno" in session:
        accno = session["Accno"]
        name = session["username"]
        cur.execute(f"select * from trans_details where AccNo='{accno}';")
        result = cur.fetchall()
        return render_template("history.html",details=result,name=name)
    return render_template("history.html")
if __name__ == "__main__":
    app.run(debug=True)
