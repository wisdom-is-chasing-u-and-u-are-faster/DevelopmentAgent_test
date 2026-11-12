"""
Enterprise Fitness Challenge Platform
Backend Service Entrypoint (Python / Flask)
"""

import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from app.routes.challenges import challenges_bp
from app.routes.leaderboard import leaderboard_bp
from app.routes.social import social_bp
from app.routes.users import users_bp
from app.routes.privacy import privacy_bp
from app.routes.telemetry import telemetry_bp

def create_app():
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
    app = Flask(__name__, static_folder=static_dir, static_url_path="")
    CORS(app)

    # Register blueprints
    app.register_blueprint(challenges_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(privacy_bp)
    app.register_blueprint(telemetry_bp)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "service": "fitness-challenge-platform",
            "version": "1.0.0",
            "timestamp": "2026-06-10T12:00:00Z"
        }), 200

    @app.route("/", methods=["GET"])
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "type": "about:blank",
            "title": "Bad Request",
            "status": 400,
            "detail": str(error)
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "type": "about:blank",
            "title": "Not Found",
            "status": 404,
            "detail": "Resource not found"
        }), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An internal server error occurred"
        }), 500

    return app

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8080))
    app = create_app()
    app.run(host=host, port=port, debug=False)
