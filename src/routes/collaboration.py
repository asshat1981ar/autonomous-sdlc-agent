from flask import Blueprint, request, jsonify
from src.models.agent import db, Agent, Session, Task, Collaboration
from src.services.ai_providers_simple import orchestrator
import asyncio
import json
from datetime import datetime

# Constants
HTTP_INTERNAL_ERROR = 500


collaboration_bp = Blueprint('collaboration', __name__)

@collaboration_bp.route('/paradigms', methods=['GET'])
def get_paradigms():
    """Get available collaboration paradigms"""
    paradigms = [
        {
            'id': 'orchestra',
            'name': 'Multi-Agent CLI Orchestra',
            'description': 'Structured orchestration with specialized AI agents working in harmony',
            'features': ['Role-based assignment', 'Conductor coordination', 'Specialized expertise']
        },
        {
            'id': 'mesh',
            'name': 'Conversational Code Mesh',
            'description': 'Natural language conversations between humans and AI agents',
            'features': ['Natural dialogue', 'Context awareness', 'Collaborative brainstorming']
        },
        {
            'id': 'swarm',
            'name': 'Autonomous Code Swarm',
            'description': 'Self-organizing AI agents with emergent behaviors',
            'features': ['Autonomous operation', 'Emergent patterns', 'Distributed coordination']
        },
        {
            'id': 'weaver',
            'name': 'Contextual Code Weaver',
            'description': 'Context-aware integration of multiple dimensions',
            'features': ['Contextual analysis', 'Multi-dimensional integration', 'Business alignment']
        },
        {
            'id': 'ecosystem',
            'name': 'Emergent Code Ecosystem',
            'description': 'Living ecosystem where code and agents co-evolve',
            'features': ['Evolutionary adaptation', 'Ecosystem dynamics', 'Emergent solutions']
        }
    ]
    return jsonify(paradigms)

@collaboration_bp.route('/agents', methods=['GET'])
def get_agents():
    """Get available AI agents"""
    agents = [
        {
            'id': 'gemini',
            'name': 'Google Gemini',
            'type': 'gemini',
            'capabilities': ['Creative problem-solving', 'Multi-modal understanding', 'General reasoning'],
            'status': 'available'
        },
        {
            'id': 'claude',
            'name': 'Anthropic Claude',
            'type': 'claude',
            'capabilities': ['Code analysis', 'Detailed reasoning', 'Safety-focused responses'],
            'status': 'available'
        },
        {
            'id': 'openai',
            'name': 'OpenAI GPT',
            'type': 'openai',
            'capabilities': ['Code generation', 'Natural language', 'Versatile problem-solving'],
            'status': 'available'
        },
        {
            'id': 'blackbox',
            'name': 'Blackbox AI',
            'type': 'blackbox',
            'capabilities': ['Code-specific tasks', 'Programming optimization', 'Development tools'],
            'status': 'available'
        }
    ]
    return jsonify(agents)

@collaboration_bp.route('/sessions', methods=['POST'])
def create_session():
    """Create a new collaboration session"""
    try:
        data = request.get_json()
        name = data.get('name', 'Untitled Session')
        paradigm = data.get('paradigm', 'orchestra')
        selected_agents = data.get('agents', ['gemini', 'claude'])

        # Create session in database
        session = Session(name=name, paradigm=paradigm)
        db.session.add(session)
        db.session.commit()

        # Create session in orchestrator (simplified)
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        orchestrator.active_sessions[session_id] = {
            'paradigm': paradigm,
            'agents': selected_agents,
            'created_at': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'session': session.to_dict(),
            'orchestrator_session_id': session_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), HTTP_INTERNAL_ERROR

@collaboration_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """Get all collaboration sessions"""
    sessions = Session.query.order_by(Session.created_at.desc()).all()
    return jsonify([session.to_dict() for session in sessions])

@collaboration_bp.route('/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get specific session details"""
    session = Session.query.get_or_404(session_id)
    tasks = Task.query.filter_by(session_id=session_id).all()
    collaborations = Collaboration.query.filter_by(session_id=session_id).all()

    return jsonify({
        'session': session.to_dict(),
        'tasks': [task.to_dict() for task in tasks],
        'collaborations': [collab.to_dict() for collab in collaborations]
    })

@collaboration_bp.route('/collaborate', methods=['POST'])
def collaborate():
    """Execute collaboration based on paradigm"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        task_description = data.get('task', '')
        paradigm = data.get('paradigm', 'orchestra')

        if not task_description:
            return jsonify({'success': False, 'error': 'Task description is required'}), 400

        # Create task record
        task = Task(
            session_id=session_id,
            title=f"Collaborative Task - {paradigm.title()}",
            description=task_description,
            status='in_progress'
        )
        db.session.add(task)
        db.session.commit()

        # Execute collaboration
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        orchestrator_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result = loop.run_until_complete(
            orchestrator.collaborate(orchestrator_session_id, paradigm, task_description, data.get('agents', ['gemini', 'claude']))
        )
        loop.close()

        # Update task with results
        task.code_output = json.dumps(result, indent=2)
        task.status = 'completed'
        task.completed_at = datetime.utcnow()
        db.session.commit()

        # Record collaboration
        collaboration = Collaboration(
            session_id=session_id,
            agent_ids=json.dumps(data.get('agents', [])),
            interaction_type=paradigm,
            content=json.dumps(result, indent=2)
        )
        db.session.add(collaboration)
        db.session.commit()

        return jsonify({
            'success': True,
            'task_id': task.id,
            'result': result
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), HTTP_INTERNAL_ERROR

@collaboration_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get specific task details"""
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@collaboration_bp.route('/demo', methods=['POST'])
def demo_collaboration():
    """Demo endpoint for testing collaboration paradigms"""
    try:
        data = request.get_json()
        paradigm = data.get('paradigm', 'orchestra')
        task = data.get('task', 'Create a simple Python function')
        agents = data.get('agents', ['gemini', 'claude'])

        # Execute demo collaboration
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        session_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        result = loop.run_until_complete(
            orchestrator.collaborate(session_id, paradigm, task, agents)
        )
        loop.close()

        return jsonify({
            'success': True,
            'paradigm': paradigm,
            'task': task,
            'agents': agents,
            'result': result
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), HTTP_INTERNAL_ERROR

@collaboration_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'available_paradigms': 5,
        'available_agents': 4
    })

