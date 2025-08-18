from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import pandas as pd
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
        'feedback': request.form.get('feedback'),
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


# Add these imports to the top of your Flask app
from flask import send_file
import pandas as pd
import io
from datetime import datetime

# Add this new route to your Flask app
@app.route('/export_to_excel', methods=['POST'])
def export_to_excel():
    """Export data to Excel file"""
    try:
        data = request.get_json()
        export_data = data.get('data', [])
        filename = data.get('filename', 'attendance_export.xlsx')

        if not export_data:
            return jsonify({'error': 'No data to export'}), 400

        # Convert data to pandas DataFrame
        if len(export_data) > 1:  # Has headers and data
            df = pd.DataFrame(export_data[1:], columns=export_data[0])
        else:
            return jsonify({'error': 'No data rows to export'}), 400

        # Create Excel file in memory
        output = io.BytesIO()
        
        # Use ExcelWriter for more control over formatting
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Attendance Data', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Attendance Data']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Style the header row
            from openpyxl.styles import Font, PatternFill
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            
            for cell in worksheet[1]:  # First row (header)
                cell.font = header_font
                cell.fill = header_fill

        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as error:
        print(f'Excel export error: {error}')
        return jsonify({'error': f'Export failed: {str(error)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 