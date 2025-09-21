import os
from flask_app import app, init_db

# Initialize database on startup
init_db()

# AWS App Runner expects the WSGI application to be named 'application'
application = app

if __name__ == '__main__':
    # Get port from environment variable (AWS App Runner sets this)
    port = int(os.environ.get('PORT', 8080))
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)