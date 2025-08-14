"""
AI Telemedicine Platform - Flask Backend
Main application entry point with CORS and basic routing setup
"""

from flask import Flask, jsonify
from flask_cors import CORS
import logging
import os
from datetime import datetime

# Import blueprints
from api.routes import api_bp
from api.symptom_routes import symptom_bp
from api.mental_health_routes import mental_health_bp
from api.booking_routes import booking_bp
from api.auth_routes import auth_bp
from api.privacy_routes import privacy_bp
from api.integration_routes import integration_bp

# Import configuration
from config.settings import Config

def create_app():
    """Application factory pattern for Flask app creation"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Enable CORS for frontend integration
    # TODO: NOTIFY FRONTEND TEAM - CORS enabled for all origins in development
    CORS(app, origins=["*"], supports_credentials=True)
    
    # Configure logging - temporarily disabled to debug 415 error
    # setup_logging(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(symptom_bp, url_prefix='/api')
    app.register_blueprint(mental_health_bp, url_prefix='/api')
    app.register_blueprint(booking_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(privacy_bp, url_prefix='/api/privacy')
    app.register_blueprint(integration_bp, url_prefix='/api/integration')

    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with API information"""
        return jsonify({
            'message': 'AI Telemedicine Platform Backend',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'test': '/test',
                'api_docs': 'See API_DOCUMENTATION.md'
            },
            'team_integration_status': {
                'backend': 'ready',
                'ai_integration': 'pending_team_lead',
                'frontend_integration': 'ready'
            }
        })

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """System health check endpoint"""
        try:
            # TODO: COORDINATE WITH TEAM - Add Firebase connection check here
            # TODO: REQUEST FROM TEAM LEAD - Add AI service health check when available

            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'services': {
                    'flask': 'running',
                    'firebase': 'development_mode',  # Updated to reflect current state
                    'ai_service': 'mock_responses'  # Updated to reflect current state
                }
            })
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 500

    # Simple test endpoint
    @app.route('/test', methods=['GET'])
    def test_endpoint():
        """Simple test endpoint"""
        return jsonify({'message': 'Test endpoint working', 'status': 'ok'})

    # API test endpoint to debug blueprint issues
    @app.route('/api/test', methods=['GET'])
    def api_test_endpoint():
        """Simple API test endpoint to debug blueprint issues"""
        return jsonify({
            'message': 'API test endpoint working!',
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'success',
            'blueprints_registered': True
        })
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid request data',
            'status_code': 400
        }), 400
    
    # Request logging middleware - temporarily disabled to debug 415 error
    # @app.before_request
    # def log_request_info():
    #     app.logger.info(f"Request: {request.method} {request.url}")
    #     if request.json:
    #         app.logger.debug(f"Request body: {request.json}")

    # @app.after_request
    # def log_response_info(response):
    #     app.logger.info(f"Response: {response.status_code}")
    #     return response
    
    return app

def setup_logging(app):
    """Configure application logging"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure logging level based on environment
    log_level = logging.DEBUG if app.config['DEBUG'] else logging.INFO
    
    # File handler
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)

if __name__ == '__main__':
    app = create_app()
    
    # Development server configuration
    port = int(os.environ.get('PORT', 5000))
    debug = True  # Force debug mode for development
    
    print(f"🚀 AI Telemedicine Backend starting on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📋 Health check available at: http://localhost:{port}/health")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
