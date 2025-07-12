"""
Bridge Services API Routes
Provides endpoints for enhanced AI bridge services
"""

from flask import Blueprint, request, jsonify
import logging
import asyncio
from typing import Dict, Any

# Import orchestrator with bridge capabilities
from src.services.ai_providers_simple import orchestrator

# Constants
HTTP_INTERNAL_ERROR = 500


logger = logging.getLogger(__name__)
bridges_bp = Blueprint('bridges', __name__)

def run_async_bridge(func):
    """Helper to run async functions in Flask bridge routes"""
    def bridge_wrapper(*args, **kwargs):
        """Bridge Wrapper with enhanced functionality."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()
    bridge_wrapper.__name__ = func.__name__
    return bridge_wrapper

@bridges_bp.route('/bridges/status', methods=['GET'])
@run_async_bridge
async def get_bridge_status():
    """Get status of all bridge services"""
    try:
        status = await orchestrator.get_bridge_status()
        return jsonify({
            'success': True,
            'bridge_status': status
        })
    except Exception as e:
        logger.error(f"Bridge status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), HTTP_INTERNAL_ERROR

@bridges_bp.route('/bridges/initialize', methods=['POST'])
@run_async_bridge
async def initialize_bridges():
    """Initialize bridge services"""
    try:
        result = await orchestrator.initialize_bridges()
        return jsonify({
            'success': result['success'],
            'message': 'Bridge services initialized',
            'details': result
        })
    except Exception as e:
        logger.error(f"Bridge initialization error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), HTTP_INTERNAL_ERROR

@bridges_bp.route('/bridges/generate-code', methods=['POST'])
@run_async_bridge
async def generate_code():
    """Generate code using bridge services"""
    try:
        data = request.get_json()

        prompt = data.get('prompt', '')
        language = data.get('language', 'python')
        paradigm = data.get('paradigm', 'orchestra')

        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt is required'
            }), 400

        result = await orchestrator.generate_code_with_bridges(
            prompt=prompt,
            language=language,
            paradigm=paradigm
        )

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logger.error(f"Code generation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), HTTP_INTERNAL_ERROR

@bridges_bp.route('/bridges/analyze-code', methods=['POST'])
@run_async_bridge
async def analyze_code():
    """Analyze code using bridge services"""
    try:
        data = request.get_json()

        code = data.get('code', '')
        language = data.get('language', 'python')

        if not code:
            return jsonify({
                'success': False,
                'error': 'Code is required'
            }), 400

        result = await orchestrator.analyze_code_with_bridges(
            code=code,
            language=language
        )

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logger.error(f"Code analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), HTTP_INTERNAL_ERROR

@bridges_bp.route('/bridges/optimize-code', methods=['POST'])
@run_async_bridge
async def optimize_code():
    """Optimize code using bridge services"""
    try:
        data = request.get_json()

        code = data.get('code', '')
        language = data.get('language', 'python')

        if not code:
            return jsonify({
                'success': False,
                'error': 'Code is required'
            }), 400

        result = await orchestrator.optimize_code_with_bridges(
            code=code,
            language=language
        )

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logger.error(f"Code optimization error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), HTTP_INTERNAL_ERROR

@bridges_bp.route('/bridges/debug-code', methods=['POST'])
@run_async_bridge
async def debug_code():
    """Debug code using bridge services"""
    try:
        data = request.get_json()

        code = data.get('code', '')
        error_message = data.get('error_message', '')
        language = data.get('language', 'python')

        if not code or not error_message:
            return jsonify({
                'success': False,
                'error': 'Code and error_message are required'
            }), 400

        result = await orchestrator.debug_code_with_bridges(
            code=code,
            error_message=error_message,
            language=language
        )

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logger.error(f"Code debugging error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), HTTP_INTERNAL_ERROR

@bridges_bp.route('/bridges/claude-code/analyze', methods=['POST'])
@run_async_bridge
async def claude_code_analyze():
    """Direct Claude Code bridge analysis"""
    try:
        from src.services.bridges.claude_code_bridge import claude_code_bridge

        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        context = data.get('context', '')

        result = await claude_code_bridge.analyze_code(code, language, context)

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logger.error(f"Claude Code analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), HTTP_INTERNAL_ERROR

@bridges_bp.route('/bridges/gemini-cli/generate', methods=['POST'])
@run_async_bridge
async def gemini_cli_generate():
    """Direct Gemini CLI bridge generation"""
    try:
        from src.services.bridges.gemini_cli_bridge import gemini_cli_bridge

        data = request.get_json()
        prompt = data.get('prompt', '')
        language = data.get('language', 'python')
        framework = data.get('framework', '')

        result = await gemini_cli_bridge.generate_code(prompt, language, framework)

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logger.error(f"Gemini CLI generation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), HTTP_INTERNAL_ERROR

@bridges_bp.route('/bridges/github-codex/complete', methods=['POST'])
@run_async_bridge
async def github_codex_complete():
    """Direct GitHub Codex bridge completion"""
    try:
        from src.services.bridges.github_codex_bridge import github_codex_bridge

        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')

        result = await github_codex_bridge.complete_code(code, language)

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logger.error(f"GitHub Codex completion error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), HTTP_INTERNAL_ERROR

@bridges_bp.route('/bridges/blackbox-ai/analyze', methods=['POST'])
@run_async_bridge
async def blackbox_ai_analyze():
    """Direct Blackbox.ai bridge analysis"""
    try:
        from src.services.bridges.blackbox_ai_bridge import blackbox_ai_bridge

        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        analysis_type = data.get('analysis_type', 'comprehensive')

        result = await blackbox_ai_bridge.analyze_code(code, language, analysis_type)

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logger.error(f"Blackbox.ai analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), HTTP_INTERNAL_ERROR

@bridges_bp.route('/bridges/health', methods=['GET'])
@run_async_bridge
async def bridges_health():
    """Health check for individual bridges"""
    try:
        health_results = {}

        # Check Claude Code bridge
        try:
            from src.services.bridges.claude_code_bridge import claude_code_bridge
            health_results['claude_code'] = await claude_code_bridge.health_check()
        except Exception as e:
            health_results['claude_code'] = {'status': 'error', 'error': str(e)}

        # Check Gemini CLI bridge
        try:
            from src.services.bridges.gemini_cli_bridge import gemini_cli_bridge
            health_results['gemini_cli'] = await gemini_cli_bridge.health_check()
        except Exception as e:
            health_results['gemini_cli'] = {'status': 'error', 'error': str(e)}

        # Check GitHub Codex bridge
        try:
            from src.services.bridges.github_codex_bridge import github_codex_bridge
            health_results['github_codex'] = await github_codex_bridge.health_check()
        except Exception as e:
            health_results['github_codex'] = {'status': 'error', 'error': str(e)}

        # Check Blackbox.ai bridge
        try:
            from src.services.bridges.blackbox_ai_bridge import blackbox_ai_bridge
            health_results['blackbox_ai'] = await blackbox_ai_bridge.health_check()
        except Exception as e:
            health_results['blackbox_ai'] = {'status': 'error', 'error': str(e)}

        # Count healthy bridges
        healthy_count = sum(1 for result in health_results.values()
                          if result.get('status') == 'healthy')

        return jsonify({
            'success': True,
            'bridges': health_results,
            'healthy_count': healthy_count,
            'total_count': len(health_results),
            'overall_status': 'healthy' if healthy_count > 0 else 'unhealthy'
        })

    except Exception as e:
        logger.error(f"Bridge health check error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), HTTP_INTERNAL_ERROR