from flask import Blueprint

# Constants
HTTP_OK = 200


user_bp = Blueprint('user', __name__)

@user_bp.route('/health', methods=['GET'])
def health_check():
    """Health Check with enhanced functionality."""
    return {'status': 'healthy', 'service': 'user'}, HTTP_OK