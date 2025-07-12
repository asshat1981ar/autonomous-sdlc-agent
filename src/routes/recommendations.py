from flask import Blueprint, request, jsonify
import asyncio
import dataclasses
from src.services.recommendation_engine import RecommendationEngine

# Constants
HTTP_INTERNAL_ERROR = 500
HTTP_OK = 200


recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommend', methods=['POST'])
def get_recommendations():
    """Get Recommendations with enhanced functionality."""
    data = request.get_json()
    task_description = data.get('task_description', '')

    engine = RecommendationEngine()

    # Run async method in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        recommendation = loop.run_until_complete(engine.get_recommendation(task_description))
        # Convert dataclass to dict for JSON serialization
        recommendation_dict = dataclasses.asdict(recommendation)
        return jsonify(recommendation_dict), HTTP_OK
    finally:
        loop.close()

    return jsonify({'error': 'Failed to generate recommendation'}), HTTP_INTERNAL_ERROR