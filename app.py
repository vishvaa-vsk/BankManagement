from flask import Flask,render_template,request,redirect, url_for,flash
import mysql.connector as sql
import random,json,pickle
import numpy as np 
import os
import nltk , webbrowser
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
from database import user_passwd


os.system("pip install -r requirements.txt")
os.system("python database.py")

mydb = sql.connect(host="localhost",user="root",password=user_passwd,database="bankmanagement",autocommit=True)
cur = mydb.cursor(dictionary=True)
cur.execute("select * from account;")
usersDic = cur.fetchall()
status = False

lemmatizer = WordNetLemmatizer()
intents = json.loads(open("intents.json").read())

words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))
model = load_model("chatbotmodel.h5")

def updateDic():# func which updates dic when new details added!
    global usersDic
    cur.execute("select * from account;")
    usersDic = cur.fetchall()
def updatestatus():
    global status
    status = True
def accnocreate():
    no,pre = random.randint(100000,9999999),"AXB"
    accno = pre+str(no)
    for i in range(len(usersDic)):
        if usersDic[i]["AccNo"]==accno:
            accno = accnocreate()
    return accno
def status_message():
    if status == False:
        flash("Internal server error!")
        flash("You are logged out due to Safety purposes!")

app = Flask(__name__)
app.config['SECRET_KEY'] = "8d4a9c0eae5147a030d36c48989892c8"

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag= [0]*len(words)
    for w in sentence_words:
        for i,word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [(i,r) for i,r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x:x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]] , 'probability':str(r[1])})
    return return_list

def get_response(intents_list , intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
    if tag== "forget-password":
        webbrowser.open(request.url_root+"resetpasswd")
    if tag== "registeration":
        webbrowser.open(request.url_root+"signup")
    return result

@app.route("/get")
def getresponse():
    userText = request.args.get('msg')
    ints = predict_class(userText)
    res = get_response(ints, intents)
    return str(res)

@app.route("/",methods=["GET","POST"])# Login route
def Login():
    if request.method=="POST":
        accno,passwd=request.form["accno"],request.form["passwd"]
        for i in range(len(usersDic)):
            if usersDic[i]["AccNo"]==accno and usersDic[i]["passwd"]==passwd:
                updatestatus()
                return redirect(url_for("home",accno=accno,name=usersDic[i]["Name"]))
        flash("Invalid credentials! or account not Exist!!")
    return render_template("index.html")

@app.route("/signup",methods = ["GET","POST"])
def Signup():
    updateDic()
    accno = accnocreate()
    if request.method=="POST":#checking POST method!
        name,address,DOB,cno,obal,email,passwd,repasswd = request.form['name'],request.form['address'],request.form["dob"],int(request.form["cno"]),request.form["obal"],request.form["email"],request.form["passwd"],request.form["re-passwd"]# Gathering all info
        for i in range(len(usersDic)):
            if name in usersDic[i]["Name"]:
                return render_template("signup.html",data="Already a account exist in this name!")
        if passwd == repasswd:# check new passwd == repasswd
            cur.execute(f"insert into account values('{name}','{accno}','{DOB}','{address}',{cno},{obal},{obal},'{passwd}','{email}');")# change values in DB
            flash("Registered Successfully!!")
        else:
            flash("Password not matched!")#if not signup
        updateDic()
        return render_template("accnoshow.html",name=name,AccNo=accno)
    return render_template("signup.html")

@app.route("/home/<string:accno>/<string:name>",methods=["GET","POST"])# Home page route!
def home(accno="AXBxxxxxxx",name="xxx"):
    if status:# only if user logged in with usrname and passwd
        updatestatus()
        return render_template("home.html",name=name,accno=accno)
    else:
        status_message()
        return redirect(url_for("Login"))

@app.route("/resetpasswd",methods=["GET","POST"])
def resetPassword():
    if request.method=="POST":
        accno,passwd,repasswd,email = request.form["accno"],request.form["passwd"], request.form["re-passwd"], request.form["email"]
        for i in range(len(usersDic)):
            if email in usersDic[i]["Email"]:
                if status:
                    if passwd == repasswd:
                        cur.execute(f"update account set passwd = '{passwd}' where AccNo = '{accno}';")
                        return redirect(url_for("home",accno=accno,name=usersDic[i]["Name"]))
                    else:
                        flash("Password not matched!")
                else:
                    if passwd == repasswd:
                        cur.execute(f"update account set passwd = '{passwd}' where AccNo = '{accno}';")
                        return redirect(url_for("Login"))
                    else:
                        flash("Password not matched!")
            else:
                flash("Incorrect email Id")
        updateDic()
    return render_template("resetpasswd.html")

@app.route("/changeuserdetails/<string:accno>",methods=["GET","POST"])
def changeDetails(accno):
    if status:
        if request.method == "POST":
            name,dob,address,contno,email = request.form["name"],request.form["dob"],request.form["address"],request.form["cno"],request.form["email"]
            try:
                cur.execute(f"update account set Name = '{name}',DOB = '{dob}',Address='{address}',ContactNo = {int(contno)} ,Email='{email}' where AccNo ='{accno}';")
                flash("Details updated successfully!")
            except:
                flash("Error occured! Can't update Details..")
    else:
        status_message()
        return redirect(url_for("Login"))
    return render_template("changedetails.html",accno=accno)

@app.route("/balanceEnquiry/<string:accno>",methods=["GET","POST"])
def balanceEq(accno):
    if status:
        cur.execute(f"select * from account where AccNo = '{accno}';")
        res = cur.fetchall()
        updatestatus()
        return render_template("viewacc.html",datas=res,rep="XXX")
    else:
        status_message()
        redirect(url_for("Login"))
    return render_template("viewacc.html")
@app.route("/accountdetails/<string:accno>",methods=["GET","POST"])
def customerDetails(accno):
    if status:
        cur.execute(f"select * from account where AccNo = '{accno}';")
        result = cur.fetchall()
        updatestatus()
        return render_template("custdetails.html",records=result)
    else:
        status_message()
        redirect(url_for("Login"))

@app.route("/deleteaccount/<string:accno>",methods=['GET','POST'])
def deleteAccount(accno):
    cur.execute("SET SQL_SAFE_UPDATES = 0;")
    cur.execute(f"delete from account where AccNo = '{accno}';")
    global status
    status = False
    flash("Successfully Deleted!!!")
    return redirect(url_for('Login')) 

@app.route("/tranfer/<string:accno>",methods=["GET","POST"])
def transfer(accno):
    if status:
        if request.method == "POST":
            fr,amount,to,passwd = request.form["from"],request.form["amount"],request.form["toaccno"],request.form["passwd"]
            if fr != to and int(amount)!=0 and fr==accno:
                cur.execute(f"select * from account where AccNo = '{accno}';")
                resultf = cur.fetchall()
                for fdata in resultf:
                    if fdata['passwd']==passwd:
                        for i in range(len(usersDic)):
                            if usersDic[i]["AccNo"] == to:
                                balancef = fdata['Balance']-int(amount)
                                cur.execute(f"update account set Balance = {balancef} where AccNo = '{fr}';")
                                cur.execute(f"select * from account where AccNo = '{to}';")
                                resultt = cur.fetchall()
                                for tdata in resultt:
                                    balancet = tdata['Balance']+int(amount)
                                    cur.execute(f"update account set Balance = {balancet} where AccNo = '{to}';")
                                    flash("Transfer Successfull")
                                    break
                    else:
                        flash("Password doesn't matched!")
    else:
        status_message()
        return redirect(url_for("Login"))
    return render_template("transfer.html")
if __name__ == "__main__":
    app.run()
