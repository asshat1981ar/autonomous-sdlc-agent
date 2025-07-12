import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.agent import db
from src.routes.user import user_bp
from src.routes.collaboration import collaboration_bp
from src.routes.recommendations import recommendations_bp
from src.routes.bridges import bridges_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Load secret key from environment variable for security
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(collaboration_bp, url_prefix='/api')
app.register_blueprint(recommendations_bp, url_prefix='/api')
app.register_blueprint(bridges_bp, url_prefix='/api')

# Configure database URI with cross-platform path joining

# Constants
HTTP_NOT_FOUND = 404

db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

try:
    db.init_app(app)
    with app.app_context():
        db.create_all()
except Exception as e:
    logger.info(f"Error initializing database: {e}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve with enhanced functionality."""
    static_folder_path = app.static_folder
    if not static_folder_path:
        return "Static folder not configured", HTTP_NOT_FOUND

    requested_path = os.path.join(static_folder_path, path)
    if path and os.path.exists(requested_path):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", HTTP_NOT_FOUND


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
