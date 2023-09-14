from flask import Flask, render_template, request, url_for
from pymysql import connections
import os
import boto3

customhost = "focsdb.cpkr5ofaey5p.us-east-1.rds.amazonaws.com"
customuser = "admin"
custompass = "admin123"
customdb = "focsDB"
custombucket = "semfocs-bucket"
customregion = "us-east-1"


app = Flask(__name__, static_folder='assets')

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/course/<int:id>')
def course(id):

    if id == 1: #doc
        doc_statement = "SELECT prog_id, prog_name FROM Programme WHERE lvl_id = 1"
        doc_cursor = db_conn.cursor()
        doc_cursor.execute(doc_statement)
        result = doc_cursor.fetchone()

        doc_statement1 = "SELECT lvl_name FROM ProgrammeLevel WHERE lvl_id = 1"
        doc_cursor1 = db_conn.cursor()
        doc_cursor1.execute(doc_statement1)
        result1 = doc_cursor.fetchone()
        
        return render_template('courses.html', prog=result, name=result1)

    elif id == 2:#master
        doc_statement = "SELECT prog_id, prog_name FROM Programme WHERE lvl_id = 2"
        doc_cursor = db_conn.cursor()
        doc_cursor.execute(doc_statement)
        result = doc_cursor.fetchone()

        doc_statement1 = "SELECT lvl_name FROM ProgrammeLevel WHERE lvl_id = 2"
        doc_cursor1 = db_conn.cursor()
        doc_cursor1.execute(doc_statement1)
        result1 = doc_cursor.fetchone()
        
        return render_template('courses.html', prog=result, name=result1)

    elif id == 3: #bachelor
        doc_statement = "SELECT prog_id, prog_name FROM Programme WHERE lvl_id = 3"
        doc_cursor = db_conn.cursor()
        doc_cursor.execute(doc_statement)
        result = doc_cursor.fetchone()

        doc_statement1 = "SELECT lvl_name FROM ProgrammeLevel WHERE lvl_id = 3"
        doc_cursor1 = db_conn.cursor()
        doc_cursor1.execute(doc_statement1)
        result1 = doc_cursor.fetchone()
        
        return render_template('courses.html', prog=result, name=result1)
        
    elif id == 4: #diploma
        doc_statement = "SELECT prog_id, prog_name FROM Programme WHERE lvl_id = 4"
        doc_cursor = db_conn.cursor()
        doc_cursor.execute(doc_statement)
        result = doc_cursor.fetchone()

        doc_statement1 = "SELECT lvl_name FROM ProgrammeLevel WHERE lvl_id = 4"
        doc_cursor1 = db_conn.cursor()
        doc_cursor1.execute(doc_statement1)
        result1 = doc_cursor.fetchone()
        
        return render_template('courses.html', prog=result, name=result1)

    else:
        return render_template('index.html')



        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
