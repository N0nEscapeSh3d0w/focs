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

@app.route('/courses/<int:id>')
def courses(id):

    if id == 1: #doc
        doc_statement = "SELECT prog_id, prog_name FROM Programme WHERE lvl_id = 1"
        doc_cursor = db_conn.cursor()
        doc_cursor.execute(doc_statement)
        result = doc_cursor.fetchall()
        doc_cursor.close()

        doc_statement1 = "SELECT * FROM ProgrammeLevel WHERE lvl_id = 1"
        doc_cursor1 = db_conn.cursor()
        doc_cursor1.execute(doc_statement1)
        lvl = doc_cursor1.fetchone()
        doc_cursor1.close()
        
        return render_template('courses.html', prog=result, name=lvl)

    elif id == 2:#master
        doc_statement = "SELECT prog_id, prog_name FROM Programme WHERE lvl_id = 2"
        doc_cursor = db_conn.cursor()
        doc_cursor.execute(doc_statement)
        result = doc_cursor.fetchall()
        doc_cursor.close()

        doc_statement1 = "SELECT * FROM ProgrammeLevel WHERE lvl_id = 2"
        doc_cursor1 = db_conn.cursor()
        doc_cursor1.execute(doc_statement1)
        lvl = doc_cursor1.fetchone()
        doc_cursor1.close()
        
        return render_template('courses.html', prog=result, name=lvl)

    elif id == 3: #bachelor
        doc_statement = "SELECT prog_id, prog_name FROM Programme WHERE lvl_id = 3"
        doc_cursor = db_conn.cursor()
        doc_cursor.execute(doc_statement)
        result = doc_cursor.fetchall()
        doc_cursor.close()

        doc_statement1 = "SELECT * FROM ProgrammeLevel WHERE lvl_id = 3"
        doc_cursor1 = db_conn.cursor()
        doc_cursor1.execute(doc_statement1)
        lvl = doc_cursor1.fetchone()
        doc_cursor1.close()
        
        return render_template('courses.html', prog=result, name=lvl)
        
    elif id == 4: #diploma
        doc_statement = "SELECT prog_id, prog_name FROM Programme WHERE lvl_id = 4"
        doc_cursor = db_conn.cursor()
        doc_cursor.execute(doc_statement)
        result = doc_cursor.fetchall()
        doc_cursor.close()

        doc_statement1 = "SELECT * FROM ProgrammeLevel WHERE lvl_id = 4"
        doc_cursor1 = db_conn.cursor()
        doc_cursor1.execute(doc_statement1)
        lvl = doc_cursor1.fetchone()
        doc_cursor1.close()
        
        return render_template('courses.html', prog=result, name=lvl)

    else:
        return render_template('index.html')



@app.route('/courses-singel/<int:id>')
def coursesSingel(id):

    #get programme
    statement = "SELECT * FROM Programme WHERE prog_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (id))
    prog = cursor.fetchone()
    cursor.close()

    #get all outline
    outline_statement = "SELECT * FROM Outline WHERE prog_id = %s"
    outline_cursor = db_conn.cursor()
    outline_cursor.execute(outline_statement, (id))
    out = outline_cursor.fetchall()
    outline_cursor.close()

    #get all carrer
    career_statement = "SELECT * FROM Outline WHERE prog_id = %s"
    career_cursor = db_conn.cursor()
    career_cursor.execute(career_statement, (id))
    care = career_cursor.fetchall()
    career_cursor.close()

    #get progession
    if prog[1] == "4":
        progress_statement = "SELECT Progression.future, Programme.prog_name FROM Programme INNER JOIN Progression ON Programme.prog_id = Progression.current WHERE Progression.current = %s"
        progress_cursor = db_conn.cursor()
        progress_cursor.execute(progress_statement, (id))
        progr = progress_cursor.fetchall()
        progress_cursor.close()

        
    return render_template('courses-singel.html', programme=prog, outline=out, career=care, progress=progr)



        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
