from flask import Flask, render_template, request, jsonify
from datetime import datetime
import qrcode
import io
import base64

app = Flask(__name__)

# Store attendance in memory
attendance_data = []

# Store QR codes for events
qr_codes = {}

@app.route('/')
def home():
    """Admin page to generate QR codes for events"""
    return render_template('admin.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    """Generate QR code for a specific event"""
    event_name = request.form.get('event_name')
    if not event_name:
        return "Event name is required", 400

    # URL for the attendance form
    form_url = request.url_root + f'form?event={event_name}'

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(form_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64 for display
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_image = base64.b64encode(buffer.getvalue()).decode()

    # Save QR code in memory
    qr_codes[event_name] = qr_image

    return render_template('qr_display.html', qr_image=qr_image, event_name=event_name, form_url=form_url)

@app.route('/form')
def attendance_form():
    """Show attendance form after scanning QR"""
    event = request.args.get('event', '')
    return render_template('form.html', event=event)

@app.route('/submit', methods=['POST'])
def submit():
    """Handle attendance form submission"""
    record = {
        'first_name': request.form.get('first_name'),
        'last_name': request.form.get('last_name'),
        'student_id': request.form.get('student_id'),
        'event': request.form.get('event'),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    attendance_data.append(record)
    return render_template('success.html', record=record)

@app.route('/view_data')
def view_data():
    """View attendance data with QR codes"""
    # Create a mapping of event -> QR code base64
    event_qr_map = {}
    for record in attendance_data:
        event = record['event']
        if event in qr_codes:
            event_qr_map[event] = qr_codes[event]

    return render_template('data.html', records=attendance_data, qr_codes=event_qr_map)

@app.route('/api/attendance', methods=['GET'])
def get_attendance_data():
    """API endpoint to get data as JSON"""
    return jsonify(attendance_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
