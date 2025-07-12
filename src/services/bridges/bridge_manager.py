"""
Bridge Manager
Orchestrates and manages all AI service bridges
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
import time

# Mock missing dependencies
try:
    import aiohttp

# Constants
HTTP_OK = 200

except ImportError:
    class MockSession:
        """MockSession class for steampunk operations."""
        """Get with enhanced functionality."""
        """Close with enhanced functionality."""
        async def get(self, *args, **kwargs): return type('R', (), {'status': HTTP_OK, 'json': lambda: {'status': 'ok'}})()
        async def close(self): pass
    """MockAiohttp class for steampunk operations."""
    class MockAiohttp:
        ClientSession = MockSession
    import sys
    sys.modules['aiohttp'] = MockAiohttp()

from .claude_code_bridge import claude_code_bridge
from .gemini_cli_bridge import gemini_cli_bridge
from .github_codex_bridge import github_codex_bridge
from .blackbox_ai_bridge import blackbox_ai_bridge
from .mcp_bridge import mcp_bridge

logger = logging.getLogger(__name__)

class BridgeType(Enum):
    """BridgeType class for steampunk operations."""
    CLAUDE_CODE = "claude_code"
    GEMINI_CLI = "gemini_cli"
    GITHUB_CODEX = "github_codex"
    BLACKBOX_AI = "blackbox_ai"
    MCP_SERVER = "mcp_server"

"""TaskType class for steampunk operations."""
class TaskType(Enum):
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    CODE_OPTIMIZATION = "code_optimization"
    CODE_DEBUGGING = "code_debugging"
    CODE_COMPLETION = "code_completion"
    CODE_EXPLANATION = "code_explanation"
    DOCUMENTATION = "documentation"
    RESEARCH = "research"
    API_DISCOVERY = "api_discovery"
    DEPRECATED_CHECK = "deprecated_check"
    KNOWLEDGE_MANAGEMENT = "knowledge_management"
    CI_CD = "ci_cd"

class BridgeManager:
    """Manages multiple AI service bridges with intelligent routing"""
    """  Init   with enhanced functionality."""

    def __init__(self):
        self.bridges = {
            BridgeType.CLAUDE_CODE: claude_code_bridge,
            BridgeType.GEMINI_CLI: gemini_cli_bridge,
            BridgeType.GITHUB_CODEX: github_codex_bridge,
            BridgeType.BLACKBOX_AI: blackbox_ai_bridge,
            BridgeType.MCP_SERVER: mcp_bridge
        }

        # Bridge capabilities and preferences
        self.bridge_capabilities = {
            BridgeType.CLAUDE_CODE: {
                TaskType.CODE_ANALYSIS: 0.95,
                TaskType.CODE_GENERATION: 0.90,
                TaskType.CODE_OPTIMIZATION: 0.85,
                TaskType.CODE_DEBUGGING: 0.90,
                TaskType.CODE_EXPLANATION: 0.95,
                TaskType.DOCUMENTATION: 0.85
            },
            BridgeType.GEMINI_CLI: {
                TaskType.CODE_GENERATION: 0.88,
                TaskType.CODE_ANALYSIS: 0.85,
                TaskType.CODE_OPTIMIZATION: 0.90,
                TaskType.CODE_EXPLANATION: 0.90,
                TaskType.DOCUMENTATION: 0.80
            },
            BridgeType.GITHUB_CODEX: {
                TaskType.CODE_COMPLETION: 0.95,
                TaskType.CODE_GENERATION: 0.92,
                TaskType.CODE_DEBUGGING: 0.85,
                TaskType.CODE_EXPLANATION: 0.80
            },
            BridgeType.BLACKBOX_AI: {
                TaskType.CODE_GENERATION: 0.87,
                TaskType.CODE_ANALYSIS: 0.92,
                TaskType.CODE_OPTIMIZATION: 0.95,
                TaskType.CODE_DEBUGGING: 0.88,
                TaskType.CODE_COMPLETION: 0.85,
                TaskType.DOCUMENTATION: 0.90
            },
            BridgeType.MCP_SERVER: {
                TaskType.RESEARCH: 0.95,
                TaskType.API_DISCOVERY: 0.90,
                TaskType.DEPRECATED_CHECK: 0.92,
                TaskType.KNOWLEDGE_MANAGEMENT: 0.88,
                TaskType.CI_CD: 0.85,
                TaskType.CODE_ANALYSIS: 0.80,
                TaskType.DOCUMENTATION: 0.85
            }
        }

        self.bridge_health = {}
        self.last_health_check = 0
        self.health_check_interval = 300  # 5 minutes

    async def initialize(self) -> Dict[str, Any]:
        """Initialize all bridges and check their health"""
        results = {}

        for bridge_type, bridge in self.bridges.items():
            try:
                health = await bridge.health_check()
                self.bridge_health[bridge_type] = {
                    'status': health.get('status', 'unknown'),
                    'last_check': time.time(),
                    'details': health
                }
                results[bridge_type.value] = health

                logger.info(f"{bridge_type.value} bridge initialized: {health.get('status', 'unknown')}")

            except Exception as e:
                logger.error(f"Failed to initialize {bridge_type.value} bridge: {e}")
                self.bridge_health[bridge_type] = {
                    'status': 'error',
                    'last_check': time.time(),
                    'error': str(e)
                }
                results[bridge_type.value] = {'status': 'error', 'error': str(e)}

        return results

    async def get_best_bridge(self, task_type: TaskType,
                             language: str = "python") -> Optional[BridgeType]:
        """Select the best bridge for a specific task"""
        await self._check_bridge_health()

        available_bridges = []

        for bridge_type, capabilities in self.bridge_capabilities.items():
            if task_type in capabilities:
                health = self.bridge_health.get(bridge_type, {})
                if health.get('status') == 'healthy':
                    score = capabilities[task_type]

                    # Language-specific adjustments
                    if language.lower() == 'python' and bridge_type == BridgeType.CLAUDE_CODE:
                        score += 0.05
                    elif language.lower() in ['javascript', 'typescript'] and bridge_type == BridgeType.GITHUB_CODEX:
                        score += 0.05

                    available_bridges.append((bridge_type, score))

        if not available_bridges:
            return None

        # Sort by score and return the best
        available_bridges.sort(key=lambda x: x[1], reverse=True)
        return available_bridges[0][0]

    async def execute_task(self, task_type: TaskType, **kwargs) -> Dict[str, Any]:
        """Execute a task using the best available bridge"""
        language = kwargs.get('language', 'python')
        best_bridge_type = await self.get_best_bridge(task_type, language)

        if not best_bridge_type:
            return {
                'success': False,
                'error': f'No available bridge for task type: {task_type.value}'
            }

        bridge = self.bridges[best_bridge_type]

        try:
            # Route to appropriate method based on task type
            if task_type == TaskType.CODE_GENERATION:
                result = await self._execute_code_generation(bridge, **kwargs)
            elif task_type == TaskType.CODE_ANALYSIS:
                result = await self._execute_code_analysis(bridge, **kwargs)
            elif task_type == TaskType.CODE_OPTIMIZATION:
                result = await self._execute_code_optimization(bridge, **kwargs)
            elif task_type == TaskType.CODE_DEBUGGING:
                result = await self._execute_code_debugging(bridge, **kwargs)
            elif task_type == TaskType.CODE_COMPLETION:
                result = await self._execute_code_completion(bridge, **kwargs)
            elif task_type == TaskType.CODE_EXPLANATION:
                result = await self._execute_code_explanation(bridge, **kwargs)
            elif task_type == TaskType.DOCUMENTATION:
                result = await self._execute_documentation(bridge, **kwargs)
            elif task_type == TaskType.RESEARCH:
                result = await self._execute_research(bridge, **kwargs)
            elif task_type == TaskType.API_DISCOVERY:
                result = await self._execute_api_discovery(bridge, **kwargs)
            elif task_type == TaskType.DEPRECATED_CHECK:
                result = await self._execute_deprecated_check(bridge, **kwargs)
            elif task_type == TaskType.KNOWLEDGE_MANAGEMENT:
                result = await self._execute_knowledge_management(bridge, **kwargs)
            elif task_type == TaskType.CI_CD:
                result = await self._execute_ci_cd(bridge, **kwargs)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported task type: {task_type.value}'
                }

            # Add metadata
            result['bridge_used'] = best_bridge_type.value
            result['task_type'] = task_type.value

            return result

        except Exception as e:
            logger.error(f"Task execution error with {best_bridge_type.value}: {e}")

            # Try fallback bridge
            fallback_result = await self._try_fallback(task_type, best_bridge_type, **kwargs)
            if fallback_result:
                return fallback_result

            return {
                'success': False,
                'error': str(e),
                'bridge_attempted': best_bridge_type.value
            }

    async def _execute_code_generation(self, bridge, **kwargs) -> Dict[str, Any]:
        """Execute code generation task"""
        prompt = kwargs.get('prompt', '')
        language = kwargs.get('language', 'python')

        if hasattr(bridge, 'generate_code'):
            return await bridge.generate_code(prompt, language)
        elif hasattr(bridge, 'generate_text'):
            return await bridge.generate_text(prompt)
        else:
            raise AttributeError("Bridge does not support code generation")

    async def _execute_code_analysis(self, bridge, **kwargs) -> Dict[str, Any]:
        """Execute code analysis task"""
        code = kwargs.get('code', '')
        language = kwargs.get('language', 'python')

        if hasattr(bridge, 'analyze_code'):
            return await bridge.analyze_code(code, language)
        else:
            raise AttributeError("Bridge does not support code analysis")

    async def _execute_code_optimization(self, bridge, **kwargs) -> Dict[str, Any]:
        """Execute code optimization task"""
        code = kwargs.get('code', '')
        language = kwargs.get('language', 'python')

        if hasattr(bridge, 'optimize_code'):
            return await bridge.optimize_code(code, language)
        elif hasattr(bridge, 'refactor_code'):
            return await bridge.refactor_code(code, language)
        else:
            raise AttributeError("Bridge does not support code optimization")

    async def _execute_code_debugging(self, bridge, **kwargs) -> Dict[str, Any]:
        """Execute code debugging task"""
        code = kwargs.get('code', '')
        error_message = kwargs.get('error_message', '')
        language = kwargs.get('language', 'python')

        if hasattr(bridge, 'debug_code'):
            return await bridge.debug_code(code, error_message, language)
        elif hasattr(bridge, 'fix_code'):
            return await bridge.fix_code(code, error_message, language)
        else:
            raise AttributeError("Bridge does not support code debugging")

    async def _execute_code_completion(self, bridge, **kwargs) -> Dict[str, Any]:
        """Execute code completion task"""
        code = kwargs.get('code', '')
        language = kwargs.get('language', 'python')

        if hasattr(bridge, 'code_completion'):
            return await bridge.code_completion(code, language)
        elif hasattr(bridge, 'complete_code'):
            return await bridge.complete_code(code, language)
        else:
            raise AttributeError("Bridge does not support code completion")

    async def _execute_code_explanation(self, bridge, **kwargs) -> Dict[str, Any]:
        """Execute code explanation task"""
        code = kwargs.get('code', '')
        language = kwargs.get('language', 'python')

        if hasattr(bridge, 'explain_code'):
            return await bridge.explain_code(code, language)
        else:
            # Fallback to analysis
            return await bridge.analyze_code(code, language)

    async def _execute_documentation(self, bridge, **kwargs) -> Dict[str, Any]:
        """Execute documentation generation task"""
        code = kwargs.get('code', '')
        language = kwargs.get('language', 'python')

        if hasattr(bridge, 'generate_documentation'):
            return await bridge.generate_documentation(code, language)
        else:
            raise AttributeError("Bridge does not support documentation generation")

    async def _try_fallback(self, task_type: TaskType, failed_bridge: BridgeType,
                           **kwargs) -> Optional[Dict[str, Any]]:
        """Try alternative bridge as fallback"""
        available_bridges = []

        for bridge_type, capabilities in self.bridge_capabilities.items():
            if (bridge_type != failed_bridge and
                task_type in capabilities and
                self.bridge_health.get(bridge_type, {}).get('status') == 'healthy'):
                available_bridges.append((bridge_type, capabilities[task_type]))

        if not available_bridges:
            return None

        # Try the next best bridge
        available_bridges.sort(key=lambda x: x[1], reverse=True)
        fallback_bridge_type = available_bridges[0][0]
        fallback_bridge = self.bridges[fallback_bridge_type]

        try:
            logger.info(f"Trying fallback bridge: {fallback_bridge_type.value}")

            if task_type == TaskType.CODE_GENERATION:
                result = await self._execute_code_generation(fallback_bridge, **kwargs)
            elif task_type == TaskType.CODE_ANALYSIS:
                result = await self._execute_code_analysis(fallback_bridge, **kwargs)
            elif task_type == TaskType.CODE_OPTIMIZATION:
                result = await self._execute_code_optimization(fallback_bridge, **kwargs)
            elif task_type == TaskType.CODE_DEBUGGING:
                result = await self._execute_code_debugging(fallback_bridge, **kwargs)
            elif task_type == TaskType.CODE_COMPLETION:
                result = await self._execute_code_completion(fallback_bridge, **kwargs)
            elif task_type == TaskType.CODE_EXPLANATION:
                result = await self._execute_code_explanation(fallback_bridge, **kwargs)
            elif task_type == TaskType.DOCUMENTATION:
                result = await self._execute_documentation(fallback_bridge, **kwargs)
            else:
                return None

            result['bridge_used'] = fallback_bridge_type.value
            result['fallback'] = True
            result['original_bridge_failed'] = failed_bridge.value

            return result

        except Exception as e:
            logger.error(f"Fallback bridge {fallback_bridge_type.value} also failed: {e}")
            return None

    async def _check_bridge_health(self):
        """Check bridge health if needed"""
        current_time = time.time()

        if current_time - self.last_health_check > self.health_check_interval:
            self.last_health_check = current_time

            for bridge_type, bridge in self.bridges.items():
                try:
                    health = await bridge.health_check()
                    self.bridge_health[bridge_type] = {
                        'status': health.get('status', 'unknown'),
                        'last_check': current_time,
                        'details': health
                    }
                except Exception as e:
                    logger.error(f"Health check failed for {bridge_type.value}: {e}")
                    self.bridge_health[bridge_type] = {
                        'status': 'error',
                        'last_check': current_time,
                        'error': str(e)
                    }

    async def get_bridge_status(self) -> Dict[str, Any]:
        """Get status of all bridges"""
        await self._check_bridge_health()

        status = {
            'bridges': {},
            'healthy_count': 0,
            'total_count': len(self.bridges),
            'last_check': self.last_health_check
        }

        for bridge_type, health in self.bridge_health.items():
            status['bridges'][bridge_type.value] = health
            if health.get('status') == 'healthy':
                status['healthy_count'] += 1

        return status

    async def execute_multi_bridge_task(self, task_type: TaskType,
                                       bridge_types: List[BridgeType],
                                       **kwargs) -> Dict[str, Any]:
        """Execute task using multiple bridges for comparison"""
        results = {}

        for bridge_type in bridge_types:
            if bridge_type in self.bridges:
                bridge = self.bridges[bridge_type]

                try:
                    if task_type == TaskType.CODE_GENERATION:
                        result = await self._execute_code_generation(bridge, **kwargs)
                    elif task_type == TaskType.CODE_ANALYSIS:
                        result = await self._execute_code_analysis(bridge, **kwargs)
                    # Add other task types as needed
                    else:
                        result = {'success': False, 'error': 'Unsupported task type'}

                    results[bridge_type.value] = result

                except Exception as e:
                    results[bridge_type.value] = {
                        'success': False,
                        'error': str(e)
                    }

        return {
            'success': len(results) > 0,
            'results': results,
            'task_type': task_type.value
        }

    # MCP-specific execution methods

    async def _execute_research(self, bridge, **kwargs) -> Dict[str, Any]:
        """Execute research task using MCP bridge"""
        query = kwargs.get('query', '')
        detail_level = kwargs.get('detail_level', 'normal')

        if hasattr(bridge, 'research_documentation'):
            return await bridge.research_documentation(query, detail_level)
        else:
            raise AttributeError("Bridge does not support research functionality")

    async def _execute_api_discovery(self, bridge, **kwargs) -> Dict[str, Any]:
        """Execute API discovery task using MCP bridge"""
        technology = kwargs.get('technology', '')
        use_case = kwargs.get('use_case', '')

        if hasattr(bridge, 'discover_apis'):
            return await bridge.discover_apis(technology, use_case)
        else:
            raise AttributeError("Bridge does not support API discovery")

    async def _execute_deprecated_check(self, bridge, **kwargs) -> Dict[str, Any]:
        """Execute deprecated code check using MCP bridge"""
        code = kwargs.get('code', '')
        language = kwargs.get('language', 'python')

        if hasattr(bridge, 'check_deprecated_code'):
            return await bridge.check_deprecated_code(code, language)
        else:
            raise AttributeError("Bridge does not support deprecated code checking")

    async def _execute_knowledge_management(self, bridge, **kwargs) -> Dict[str, Any]:
        """Execute knowledge management task using MCP bridge"""
        action = kwargs.get('action', 'query')
        data = kwargs.get('data', {})

        if hasattr(bridge, 'manage_knowledge'):
            return await bridge.manage_knowledge(action, data)
        else:
            raise AttributeError("Bridge does not support knowledge management")

    async def _execute_ci_cd(self, bridge, **kwargs) -> Dict[str, Any]:
        """Execute CI/CD task using MCP bridge"""
        project = kwargs.get('project', '')
        branch = kwargs.get('branch', 'main')

        if hasattr(bridge, 'trigger_build'):
            return await bridge.trigger_build(project, branch)
        else:
            raise AttributeError("Bridge does not support CI/CD operations")

    # A2A Framework Integration

    async def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A framework messages for bridge routing"""
        intent = message.get('intent', '')
        data = message.get('data', {})
        context = message.get('context', {})

        # Map A2A intents to task types
        intent_to_task = {
            'generate_code': TaskType.CODE_GENERATION,
            'analyze_code': TaskType.CODE_ANALYSIS,
            'optimize_code': TaskType.CODE_OPTIMIZATION,
            'debug_code': TaskType.CODE_DEBUGGING,
            'complete_code': TaskType.CODE_COMPLETION,
            'explain_code': TaskType.CODE_EXPLANATION,
            'generate_docs': TaskType.DOCUMENTATION,
            'research_docs': TaskType.RESEARCH,
            'discover_apis': TaskType.API_DISCOVERY,
            'check_deprecated': TaskType.DEPRECATED_CHECK,
            'manage_knowledge': TaskType.KNOWLEDGE_MANAGEMENT,
            'trigger_build': TaskType.CI_CD
        }

        task_type = intent_to_task.get(intent)
        if not task_type:
            return {
                'success': False,
                'error': f'Unsupported A2A intent: {intent}'
            }

        # Execute task with bridge manager
        try:
            result = await self.execute_task(task_type, **data)
            result['a2a_intent'] = intent
            result['a2a_context'] = context
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'a2a_intent': intent
            }


# Global bridge manager instance
bridge_manager = BridgeManager()