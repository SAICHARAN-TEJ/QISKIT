import sys
import os

# Change to webapp directory
os.chdir(os.path.join(os.path.dirname(__file__), 'webapp'))

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))

# Import and run Flask
from app import app

if __name__ == '__main__':
    print("Starting QuantumRes web server at http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)