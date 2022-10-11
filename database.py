import mysql.connector as sql
user_passwd = input("Enter the root password: ")
mydb = sql.connect(host="localhost",user="root",password=user_passwd,autocommit=True)
cursor = mydb.cursor()
cursor.execute("create database bankmanagement;")
cursor.execute("create table account(Name varchar(15),AccNo varchar(15) primary key,DOB varchar(15),Address longtext,ContactNo bigint,OpeningBal int,Balance int,passwd varchar(15),Email longtext);")
cursor.execute("SET SQL_SAFE_UPDATES = 0;")