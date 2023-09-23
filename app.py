from curses import flash
from flask import Flask, render_template, request, url_for, session, jsonify
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_session import Session
from pymysql import connections
import os
import boto3
import socket
from io import BytesIO
import pdfplumber
from flask import send_file
from werkzeug.utils import secure_filename

customhost = "focsdb.cpkr5ofaey5p.us-east-1.rds.amazonaws.com"
customuser = "admin"
custompass = "admin123"
customdb = "focsDB"
custombucket = "semfocs-bucket"
customregion = "us-east-1"

app = Flask(__name__, static_folder='assets')
app.secret_key = 'focs_assignment'
csrf = CSRFProtect(app)

#Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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
    ip_address = request.remote_addr
    session['address'] = ip_address
    return render_template('index.html')

@app.route("/staffs", methods=['GET', 'POST'])
def staffs():
    return render_template('staff.html')

#------Enroll--------------
@app.route("/enroll", methods=['GET', 'POST'])
def enroll():
    doc_statement = "SELECT id, name FROM Campus"
    doc_cursor = db_conn.cursor()
    doc_cursor.execute(doc_statement)
    result = doc_cursor.fetchall()
    doc_cursor.close()

    statement = "SELECT id, full_name FROM Subject"
    cursor = db_conn.cursor()
    cursor.execute(statement)
    subj = cursor.fetchall()
    cursor.close()

    grad_statement = "SELECT value, name FROM Grade"
    grad_cursor = db_conn.cursor()
    grad_cursor.execute(grad_statement)
    grad = grad_cursor.fetchall()
    grad_cursor.close()

    count_st = "SELECT COUNT(*) FROM Grade"
    st_cursor = db_conn.cursor()
    st_cursor.execute(count_st)
    st = st_cursor.fetchone()
    st_cursor.close()

    return render_template('enroll.html', campus=result, subject=subj, grade = grad, totalSubj = st)

@app.route("/getSubjectWithCampus", methods=['GET'])
def getSubjectWithCampus():
    campus_id = request.args.get('campus_id') 
    
    statement = (
        "SELECT Programme.prog_id, Programme.prog_name "
        "FROM Programme "
        "INNER JOIN CampusList ON Programme.prog_id = CampusList.prog_id "
        "WHERE CampusList.cam_id = %s AND Programme.lvl_id = 4"
    )

    cursor = db_conn.cursor()
    cursor.execute(statement, (campus_id))
    result = cursor.fetchall()
    cursor.close()

    result = [{'prog_id': row[0], 'prog_name': row[1]} for row in result]

    return jsonify(result)

@app.route("/enrollDiploma", methods=['POST'])
@csrf.exempt
def enrollDiploma():
        
    # Retrieve data from the form
    full_name = request.form.get('name')
    mykad_no = request.form.get('ic')
    gender = request.form.get('gender')
    address = request.form.get('address')
    state = request.form.get('state')
    city = request.form.get('city')
    post_code = request.form.get('postCode')
    phone_no = request.form.get('phoneNo')
    email = request.form.get('email')
    campus = request.form.get('campus')
    program = request.form.get('program')
    front_ic_file = request.files.get('frontIc')
    back_ic_file = request.files.get('backIc')
    qualification = request.form.get('qualification')
    result_year = request.form.get('resultYear')
    type_of_result = request.form.get('typeOfResult')
    acknowledge = request.form.get('acknowledge')

    # Retrieve subject and grade data (loop through the fields)
    subjects = []
    grades = []

    count_st = "SELECT COUNT(*) FROM Grade"
    st_cursor = db_conn.cursor()
    st_cursor.execute(count_st)
    st = st_cursor.fetchone()
    st_cursor.close()
    
    for i in range(1, st[0]):  # Assuming there are 10 subject and grade pairs
        subject = request.form.get(f'subject{i}')
        grade = request.form.get(f'grade{i}')
        if subject and grade:
            subjects.append(subject)
            grades.append(grade)

    #--Start to check the qualification (Compalsory Subject)-----------------------------------------------------
    cc_statement = "SELECT sub_id, grade FROM Compulsory_subject WHERE prog_id = %s"
    cc_cursor = db_conn.cursor()
    cc_cursor.execute(cc_statement, program)
    compulsory_subjects = st_cursor.fetchall()
    cc_cursor.close()

    # Create a dictionary to store the required grades for each compulsory subject.
    compulsory_subjects_dict = {sub_id: grade for sub_id, grade in compulsory_subjects}

    # Initialize a list to store subjects and grades that don't meet the requirements.
    mismatched_subjects = []

    # Iterate through the user-submitted subjects and grades and check if they match the requirements.
    for subject, user_grade in zip(subjects, grades):
        # Check if the subject is compulsory for the selected program.
        if subject in compulsory_subjects_dict:
            required_grade = compulsory_subjects_dict[subject]  # Get the required grade
            if user_grade > required_grade:
                mismatched_subjects.append((subject, user_grade, required_grade))

    #--Start to check the qualification (Credit Check)-----------------------------------------------------
    credit_statement = "SELECT number_credit FROM Credit WHERE prog_id = %s"
    credit_cursor = db_conn.cursor()
    credit_cursor.execute(credit_statement, program)
    number_of_credit = credit_cursor.fetchone()
    credit_cursor.close()
    
    credit_number = 0
    
    for user_grade in grades:
        if user_grade <= '7':
            credit_number += 1

    if(credit_number < number_of_credit[0]):
        return render_template("enrollFail.html", mismatched = mismatched_subjects, user_credit = credit_number, grade=grades, subject=subjects)
    else:
        return render_template("enrollSuccess.html")

    

    
#---------------------------------------------------

@app.route('/displayStaff', methods=['GET'])
def displayStaff():
   
   #Get All Internship
    staff_statement = """SELECT s.staff_id, s.staff_name, s.position,s.img FROM Staff s INNER JOIN Department d WHERE s.depart_id = d.depart_id"""
    cursor = db_conn.cursor()
    cursor.execute(staff_statement)
    result = cursor.fetchall()
    cursor.close()

     #Get Industry involve
    indus_statement = "SELECT depart_name FROM Department"
    cursor = db_conn.cursor()
    cursor.execute(indus_statement)
    depart = cursor.fetchall()
    cursor.close()



    return render_template('staff.html', staff = result, department = depart)



@app.route('/displayStaff/staffDetails/<string:staff_id>')
def staffDetails(staff_id):

    #Get Internship details
    details_statement = """SELECT s.staff_id, s.staff_name, s.position, s.study_level, s.email, s.specialization, s.areaInterest, s.img FROM Staff s INNER JOIN Department d WHERE s.depart_id = d.depart_id AND staff_id = %s"""
    cursor = db_conn.cursor()
    cursor.execute(details_statement, (staff_id))
    details = cursor.fetchone()
    cursor.close()
    
    return render_template('teachers-singel.html', staff = details)


@app.route('/courses/<int:id>')
def courses(id):

    if id == 1: #doc
        doc_statement = "SELECT prog_id, prog_name, prog_duration FROM Programme WHERE lvl_id = 1"
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
        doc_statement = "SELECT prog_id, prog_name, prog_duration FROM Programme WHERE lvl_id = 2"
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
        doc_statement = "SELECT prog_id, prog_name, prog_duration FROM Programme WHERE lvl_id = 3"
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
        doc_statement = "SELECT prog_id, prog_name, prog_duration FROM Programme WHERE lvl_id = 4"
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
    try:
        # Get programme
        statement = "SELECT * FROM Programme WHERE prog_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(statement, (id))
        prog = cursor.fetchone()
        cursor.close()

        # Get level
        statement = "SELECT * FROM ProgrammeLevel WHERE lvl_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(statement, (prog[1]))
        lvl = cursor.fetchone()
        cursor.close()

        # Get all outline
        outline_statement = "SELECT * FROM Outline WHERE prog_id = %s"
        outline_cursor = db_conn.cursor()
        outline_cursor.execute(outline_statement, (id))
        out = outline_cursor.fetchall()
        outline_cursor.close()

        # Get all career
        career_statement = "SELECT * FROM Career WHERE prog_id = %s"
        career_cursor = db_conn.cursor()
        career_cursor.execute(career_statement, (id))
        care = career_cursor.fetchall()
        career_cursor.close()

        # Get progression
        if prog[1] == 4:
            progress_statement = """
                SELECT Progression.future, Programme.prog_name
                FROM Programme
                INNER JOIN Progression ON Programme.prog_id = Progression.future
                WHERE Progression.current = %s
            """
            progress_cursor = db_conn.cursor()
            progress_cursor.execute(progress_statement, (id,))
            gress = progress_cursor.fetchall()
            progress_cursor.close()

            # Debug: Print progression results
            print("Progression Results:", gress)

            return render_template('courses-singel.html', programme=prog, outline=out, career=care, progress=gress, level=lvl)

        return render_template('courses-singel.html', programme=prog, outline=out, career=care, level=lvl)

    except Exception as e:
        # Handle exceptions, print the error message, and return an error page if needed
        print("Error:", str(e))
        return render_template('error.html', error_message=str(e))

@app.route('/compare', methods=['GET', 'POST'])
def compare_prog():
    if request.method == 'POST' or request.method == 'GET':
        #Get the Programme Level
        cursor = db_conn.cursor()      
        cursor.execute('SELECT * FROM ProgrammeLevel')
        programme_levels = cursor.fetchall()
        
        # Get the selected program level from the form
        selected_programme_level = request.form.get('programme_level') or request.args.get('programme_level')
        selected_programme_level1 = request.form.get('programme_level') or request.args.get('programme_level')
        session['compare_level'] = selected_programme_level
        
        
        # If a programme level is selected, fetch the list of programme for that level
        if selected_programme_level:
            cursor.execute('SELECT * FROM Programme WHERE lvl_id = %s', (selected_programme_level,))
            programmes = cursor.fetchall()
        else:
            programmes = []

        # If a programme level1 is selected, fetch the list of programme for that level
        if selected_programme_level1:
            cursor.execute('SELECT * FROM Programme WHERE lvl_id = %s', (selected_programme_level1,))
            programmes1 = cursor.fetchall()
        else:
            programmes1 = []
            
        # Get the selected programme from the form
        selected_programme = request.form.get('programme') or request.args.get('programme')
        selected_programme1 = request.form.get('programme1') or request.args.get('programme1')
        session['compare_prog'] = selected_programme 
        session['compare_prog1'] = selected_programme1
        
        #If a programme is selected, fetch the details of programmes out
        if selected_programme:
            cursor.execute('SELECT * FROM Programme WHERE prog_id = %s', (selected_programme,))
            programme_details = cursor.fetchall()
        else:
            programme_details = []

        #If a programme1 is selected, fetch the details of programmes out
        if selected_programme1:
            cursor.execute('SELECT * FROM Programme WHERE prog_id = %s', (selected_programme1,))
            programme_details1 = cursor.fetchall()
        else:
            programme_details1 = []
        cursor.close()
        
        return render_template('compare.html', programme_levels=programme_levels, programmes=programmes, programmes1=programmes1, programme_details=programme_details, programme_details1=programme_details1)
    return render_template('compare.html', programme_levels=None, programmes=None, programmes1=None, programme_details=None, programme_details1=None)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')

    # Execute a SQL query to search for the data
    cursor = db_conn.cursor()
    cursor.execute("SELECT prog_id, prog_name, prog_duration FROM Programme WHERE prog_name LIKE %s", ('%' + query + '%',) )
    results = cursor.fetchall()
    cursor.close()

    return render_template('search_result.html', results=results)

        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
