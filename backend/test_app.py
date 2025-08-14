#!/usr/bin/env python3
"""
Minimal test Flask app to debug the 415 error
"""

from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Test app working'
    })

@app.route('/test', methods=['GET'])
def test():
    """Simple test endpoint"""
    return jsonify({'message': 'Hello World', 'status': 'ok'})

if __name__ == '__main__':
    print("🧪 Starting minimal test Flask app on port 5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
