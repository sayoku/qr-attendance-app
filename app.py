from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

attendance_data = []

@app.route('/')
def home():
    #Main page 
    return render_template('scanner.html')

@app.route('/form')
def attendanceForm():
    #Show attendance form after QR
    qr_data = request.args.get('qr_data', '')
    return render_template('form.html', qr_data=qr_data)

@app.route('/submit', methods=['POST'])
def submit():
    #Handle form submission
    attendance_record = {
    'first_name' : request.form.get('first_name'),
    'last_dot_num' : request.form.get('last_dot_num'),
    'event' : request.form.get('event'),
    'qr_data' : request.form.get('qr_data'),
    'timestamp': datetime.now()
    }
    
#Store data in memory
attendance_data.append(attendance_record)
#return render_template('success.html', record=attendance_record)

@app.route('/view_data')
def view_data():
    #View data for testing
    return render_template('data.html', record=attendance_record)

@app.route('/api/attendance', methods=['GET'])
def get_attendance_data():
    #API endpoint to get data as JSON
    return jsonify(attendance_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)