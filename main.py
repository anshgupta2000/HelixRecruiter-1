import os
import sys
from flask import send_file, render_template, Response, jsonify, send_from_directory

# Add the backend directory to the path so we can import properly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app import create_app, socketio

# Create app instance
app = create_app()

# Get the absolute path to the static directory
static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

# Define route for serving the frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # First check if the path is an API route
    if path.startswith('api/'):
        # Let the backend handle API routes
        return app.full_dispatch_request()
    
    # Check if the requested file exists in the static folder
    if path and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    
    # For all other routes, serve the index.html file
    return send_from_directory(static_folder, 'index.html')

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)