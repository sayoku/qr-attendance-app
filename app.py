from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime
import qrcode
import io
import base64

app = Flask(__name__)

attendance_data = []

@app.route('/')
def home():
    #Admin page to generate QR code for events
    return render_template('admin.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    #Generate QR code for a specific event
    event_name = request.form.get('event_name')
    
    #Create the URL that the QR code will point to
    form_url = request.url_root + f'form?event={event_name}'
    
    #Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(form_url)
    qr.make(fit=True)
    
    #Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    #Convert to base64 for display
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_image = base64.b64encode(buffer.getvalue()).decode()
    
    return render_template('qr_display.html', 
        qr_image=qr_image, 
        event_name=event_name,
        form_url=form_url)

@app.route('/form')
def attendance_record():
    #Show attendance form after QR
    event = request.args.get('event', '')
    return render_template('form.html', event=event)

@app.route('/submit', methods=['POST'])
def submit():
    #Handle form submission
    attendance_record = {
    'first_name' : request.form.get('first_name'),
    'last_name' : request.form.get('last_name'),
    'student_id' : request.form.get('student_id'),
    'event' : request.form.get('event'),
    #'qr_data' : request.form.get('qr_data'),
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    #Store data in memory
    attendance_data.append(attendance_record)
    return render_template('success.html', record=attendance_record)

@app.route('/view_data')
def view_data():
    #View data for testing
    return render_template('data.html', records=attendance_data)

@app.route('/api/attendance', methods=['GET'])
def get_attendance_data():
    #API endpoint to get data as JSON
    return jsonify(attendance_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)