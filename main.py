from flask import Flask, send_from_directory, render_template, jsonify, request
import os
import subprocess
import signal
import sys
import logging
import time
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, static_folder='static')

# Setup app config
app.secret_key = os.environ.get("SESSION_SECRET", "helix-dev-secret-key")

# Variable to store backend server process
backend_process = None

def start_backend_server():
    """Start the backend server process"""
    global backend_process
    try:
        # Kill any existing backend process
        if backend_process:
            try:
                os.killpg(os.getpgid(backend_process.pid), signal.SIGTERM)
            except:
                pass
        
        # Start backend server
        cmd = ["python", "backend/run.py"]
        backend_process = subprocess.Popen(
            cmd, 
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        logger.info("Backend server started successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to start backend server: {e}")
        return False

def monitor_backend():
    """Monitor the backend server and restart if needed"""
    while True:
        if backend_process and backend_process.poll() is not None:
            logger.warning("Backend server crashed, restarting...")
            start_backend_server()
        time.sleep(5)

@app.route('/')
def index():
    """Serve static HTML"""
    return send_from_directory('static', 'index.html')

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_api(path):
    """Proxy API requests to the backend server"""
    import requests
    try:
        # Forward the request to the backend server
        url = f"http://localhost:8000/api/{path}"
        
        # Get the method and data
        method = request.method
        data = request.get_json() if request.is_json else {}
        
        # Forward the request
        if method == 'GET':
            resp = requests.get(url, params=request.args)
        elif method == 'POST':
            resp = requests.post(url, json=data)
        elif method == 'PUT':
            resp = requests.put(url, json=data)
        elif method == 'DELETE':
            resp = requests.delete(url)
        else:
            return jsonify({"error": "Method not supported"}), 405
        
        # Return the response from the backend
        return jsonify(resp.json()), resp.status_code
        
    except Exception as e:
        logger.error(f"Error forwarding request to backend: {str(e)}")
        return jsonify({"error": "Failed to forward request to backend"}), 500

@app.route('/socket.io/')
def proxy_socket():
    """Handle Socket.IO connections"""
    import requests
    try:
        # This is just a placeholder - real Socket.IO connections use
        # WebSockets and can't be simply proxied in this way
        return jsonify({"message": "Socket.IO endpoint"}), 200
    except Exception as e:
        logger.error(f"Error handling Socket.IO connection: {str(e)}")
        return jsonify({"error": "Socket.IO connection failed"}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # Start backend server
    start_backend_server()
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_backend)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Run app
    app.run(host="0.0.0.0", port=5000, debug=True)