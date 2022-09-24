from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

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
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/emp/", methods=['POST'])
def Emp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    education = request.form['education']
    location = request.form['location']
    emp_image_file = request.form['emp_image_file'] 
    
    check_in = ''
    insert_sql = "INSERT INTO employee VALUES (%d, %s, %s, %s, %s, %s)"
    emp_id ="SELECT COUNT(emp_id) form employee"
    cursor = db_conn.cursor()
    
    if emp_image_file.filename == "":
        return "Please select a file"
    
    try:
        cursor.execute(insert_sql, (emp_id+1, first_name, last_name, education, location, check_in))
        db_conn.commit()
        emp_name = "" + first_name +" " + last_name
        
        # Upload image file to S3 
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')
        
        try:
            print("Data inserted in MySQL RDS... uploading image to S3... ")
            s3.Bucket(custombucket).put_object(Key = emp_image_file_name_in_s3, Body = emp_image_file)
            bucket_location = boto3.client('S3').get_bucket_location(Bucket=customBucket) 
            s3_location = (bucket_location['LocationConstraint'])
            
            if s3_location is None:
                s3_location = ''
                
            else: 
                s3_location = '-' + s3_location 
                
            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(s3_location, custombucket, emp_image_file_name_in_s3)

      except Exception as e:
            return str(e)
    
    finally:
        cursor.close()
        
    print("all modification done... ")
    return render_template('AddEmpOutput.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
