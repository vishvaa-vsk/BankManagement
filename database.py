import mysql.connector as sql

usr_name = input("Enter the username:")
mydb = sql.connect(host="localhost",user="root",password="vishvaa_vsk",autocommit=True)
cursor = mydb.cursor()

try:
    cursor.execute("create database bankmanagement;")
except:
    cursor.execute("use bankmanagement")
    cursor.execute("SET SQL_SAFE_UPDATES = 0;")
try:
    cursor.execute("create table account(Name varchar(30),AccNo varchar(15) primary key,DOB varchar(10),Address longtext,ContactNo bigint,OpeningBal int,Balance int,passwd varchar(15),Email longtext);")
    cursor.execute("CREATE TABLE trans_details (AccNo VARCHAR(16),FOREIGN KEY (AccNo)REFERENCES account (Accno),trans_type VARCHAR(15),trans_date VARCHAR(30),trans_amount INT,bal_after_trans INT);")
    print("Database Setup is created successfully!")
except:
    print("Database is already set")