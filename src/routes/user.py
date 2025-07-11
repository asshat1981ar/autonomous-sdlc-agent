from flask import Blueprint

user_bp = Blueprint('user', __name__)

@user_bp.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy', 'service': 'user'}, 200