import os
from app import create_app, socketio
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting server on port {port}")
    
    # Run the socketio app
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port,
        debug=True,
        allow_unsafe_werkzeug=True  # For development only
    )
