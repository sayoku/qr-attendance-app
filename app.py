from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>QR Attendance App</h1><p>Coming soon!</p>"

if __name__ == '__main__':
    app.run(debug=True)