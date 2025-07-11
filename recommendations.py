"""
API routes for the AI-driven recommendation engine.
"""

from flask import Blueprint, request, jsonify
from src.services.recommendation_engine import recommendation_engine
import asyncio
import json
from datetime import datetime

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommend', methods=['POST'])
def get_recommendation():
    """Get paradigm and agent recommendation for a task."""
    try:
        data = request.get_json()
        task_description = data.get('task_description', '')
        user_preferences = data.get('user_preferences', {})
        
        if not task_description:
            return jsonify({
                'success': False,
                'error': 'Task description is required'
            }), 400
        
        # Get recommendation asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        recommendation = loop.run_until_complete(
            recommendation_engine.get_recommendation(task_description, user_preferences)
        )
        loop.close()
        
        return jsonify({
            'success': True,
            'recommendation': {
                'paradigm': recommendation.paradigm,
                'agents': recommendation.agents,
                'confidence': recommendation.confidence,
                'justification': recommendation.justification,
                'estimated_duration': recommendation.estimated_duration
            },
            'task_analysis': {
                'task_description': task_description,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@recommendations_bp.route('/feedback', methods=['POST'])
def record_feedback():
    """Record user feedback on a recommendation."""
    try:
        data = request.get_json()
        task_description = data.get('task_description', '')
        recommendation_data = data.get('recommendation', {})
        user_satisfaction = data.get('user_satisfaction', 0.5)
        actual_outcome = data.get('actual_outcome', {})
        
        # Convert recommendation data back to Recommendation object
        from src.services.recommendation_engine import Recommendation
        recommendation = Recommendation(
            paradigm=recommendation_data.get('paradigm', ''),
            agents=recommendation_data.get('agents', []),
            confidence=recommendation_data.get('confidence', 0.5),
            justification=recommendation_data.get('justification', ''),
            estimated_duration=recommendation_data.get('estimated_duration', '')
        )
        
        # Record feedback
        recommendation_engine.record_feedback(
            task_description, recommendation, user_satisfaction, actual_outcome
        )
        
        return jsonify({
            'success': True,
            'message': 'Feedback recorded successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@recommendations_bp.route('/analyze', methods=['POST'])
def analyze_task():
    """Analyze a task description without generating full recommendation."""
    try:
        data = request.get_json()
        task_description = data.get('task_description', '')
        
        if not task_description:
            return jsonify({
                'success': False,
                'error': 'Task description is required'
            }), 400
        
        # Analyze task
        analysis = recommendation_engine.nlp_analyzer.analyze_task(task_description)
        
        return jsonify({
            'success': True,
            'analysis': {
                'domain': analysis.domain,
                'complexity': analysis.complexity,
                'intent': analysis.intent,
                'keywords': analysis.keywords,
                'confidence': analysis.confidence
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@recommendations_bp.route('/paradigms', methods=['GET'])
def get_paradigm_info():
    """Get information about available paradigms."""
    try:
        paradigms = recommendation_engine.knowledge_base.paradigm_descriptions
        
        return jsonify({
            'success': True,
            'paradigms': paradigms
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@recommendations_bp.route('/agents', methods=['GET'])
def get_agent_info():
    """Get information about available agents."""
    try:
        agents = recommendation_engine.knowledge_base.agent_capabilities
        
        return jsonify({
            'success': True,
            'agents': agents
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@recommendations_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for recommendation service."""
    return jsonify({
        'status': 'healthy',
        'service': 'recommendation_engine',
        'timestamp': datetime.now().isoformat()
    })

