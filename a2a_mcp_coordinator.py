#!/usr/bin/env python3
"""
A2A MCP Coordinator
Coordinates Agent-to-Agent communication with Model Context Protocol servers
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from src.services.bridges.bridge_manager import bridge_manager, TaskType
from refactored_orchestrator import enhanced_orchestrator

# Constants
MILLISECONDS_PER_SECOND = 1000


logger = logging.getLogger(__name__)

class AgentRole(Enum):
    """AgentRole class for steampunk operations."""
    RESEARCH_AGENT = "research_agent"
    CODE_ANALYZER = "code_analyzer"
    API_SCOUT = "api_scout"
    KNOWLEDGE_KEEPER = "knowledge_keeper"
    BUILD_MASTER = "build_master"
    QUALITY_INSPECTOR = "quality_inspector"

@dataclass
class A2AMessage:
    """Structured A2A message format"""
    id: str
    sender: str
    recipient: str
    intent: str
    data: Dict[str, Any]
    context: Dict[str, Any]
    timestamp: datetime
    priority: str = "normal"  # low, normal, high, urgent

class A2AMCPCoordinator:
    """Coordinates A2A communication with MCP servers"""

    """  Init   with enhanced functionality."""
    def __init__(self):
        self.agents = {}
        self.message_queue = asyncio.Queue()
        self.active_sessions = {}
        self.message_history = []
        self.performance_metrics = {}
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize specialized A2A agents for MCP coordination"""
        self.agents = {
            AgentRole.RESEARCH_AGENT: {
                'name': 'Research Agent',
                'description': 'Specializes in documentation research and knowledge discovery',
                'capabilities': ['research', 'documentation', 'analysis'],
                'mcp_servers': ['perplexity'],
                'status': 'active',
                'model': 'claude-3.5-sonnet'
            },
            AgentRole.CODE_ANALYZER: {
                'name': 'Code Analysis Agent',
                'description': 'Analyzes code quality, security, and best practices',
                'capabilities': ['code_analysis', 'security_audit', 'style_checking'],
                'mcp_servers': ['eslint', 'deepseek'],
                'status': 'active',
                'model': 'qwen-2.5-coder-32b'
            },
            AgentRole.API_SCOUT: {
                'name': 'API Discovery Agent',
                'description': 'Discovers and evaluates APIs for integration',
                'capabilities': ['api_discovery', 'integration_analysis', 'compatibility_check'],
                'mcp_servers': ['perplexity'],
                'status': 'active',
                'model': 'gemini-2.0-flash'
            },
            AgentRole.KNOWLEDGE_KEEPER: {
                'name': 'Knowledge Management Agent',
                'description': 'Manages project knowledge and documentation',
                'capabilities': ['knowledge_management', 'documentation', 'project_tracking'],
                'mcp_servers': ['notion'],
                'status': 'active',
                'model': 'llama-3.3-70b'
            },
            AgentRole.BUILD_MASTER: {
                'name': 'CI/CD Orchestration Agent',
                'description': 'Manages build pipelines and deployment processes',
                'capabilities': ['ci_cd', 'deployment', 'monitoring'],
                'mcp_servers': ['jenkins'],
                'status': 'active',
                'model': 'deepseek-r1-distill-70b'
            },
            AgentRole.QUALITY_INSPECTOR: {
                'name': 'Quality Assurance Agent',
                'description': 'Ensures code quality and detects deprecated patterns',
                'capabilities': ['quality_assurance', 'deprecated_check', 'testing'],
                'mcp_servers': ['eslint', 'perplexity'],
                'status': 'active',
                'model': 'glm-z1-32b'
            }
        }

        logger.info(f"Initialized {len(self.agents)} A2A agents for MCP coordination")

    async def create_message(self, sender: str, recipient: str, intent: str,
                           data: Dict[str, Any], context: Dict[str, Any] = None,
                           priority: str = "normal") -> A2AMessage:
        """Create a structured A2A message"""
        message = A2AMessage(
            id=f"a2a_{int(time.time() * MILLISECONDS_PER_SECOND)}_{len(self.message_history)}",
            sender=sender,
            recipient=recipient,
            intent=intent,
            data=data,
            context=context or {},
            timestamp=datetime.now(),
            priority=priority
        )

        await self.message_queue.put(message)
        self.message_history.append(message)

        logger.info(f"Created A2A message: {sender} -> {recipient} [{intent}]")
        return message

    async def route_message(self, message: A2AMessage) -> Dict[str, Any]:
        """Route A2A message to appropriate handler"""
        try:
            # Check if recipient is an MCP server task
            if message.recipient == "mcp_server":
                return await self._handle_mcp_request(message)

            # Check if recipient is a specialized agent
            elif message.recipient in [role.value for role in AgentRole]:
                return await self._handle_agent_request(message)

            # Check if recipient is the orchestrator
            elif message.recipient == "orchestrator":
                return await self._handle_orchestrator_request(message)

            else:
                return {
                    'success': False,
                    'error': f'Unknown recipient: {message.recipient}',
                    'message_id': message.id
                }

        except Exception as e:
            logger.error(f"Error routing A2A message {message.id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message_id': message.id
            }

    async def _handle_mcp_request(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle requests directed to MCP servers"""
        intent = message.intent
        data = message.data

        try:
            # Use bridge manager to handle MCP requests
            result = await bridge_manager.handle_a2a_message({
                'intent': intent,
                'data': data,
                'context': message.context
            })

            result['message_id'] = message.id
            result['sender'] = message.sender
            result['processing_time'] = time.time() - message.timestamp.timestamp()

            return result

        except Exception as e:
            logger.error(f"MCP request failed for message {message.id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message_id': message.id
            }

    async def _handle_agent_request(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle requests directed to specialized agents"""
        recipient_role = AgentRole(message.recipient)
        agent_config = self.agents[recipient_role]

        try:
            # Route to appropriate MCP server based on agent capabilities
            mcp_servers = agent_config['mcp_servers']
            intent = message.intent
            data = message.data

            # Enhanced agent-specific routing
            if recipient_role == AgentRole.RESEARCH_AGENT:
                return await self._handle_research_request(message, mcp_servers)
            elif recipient_role == AgentRole.CODE_ANALYZER:
                return await self._handle_code_analysis_request(message, mcp_servers)
            elif recipient_role == AgentRole.API_SCOUT:
                return await self._handle_api_discovery_request(message, mcp_servers)
            elif recipient_role == AgentRole.KNOWLEDGE_KEEPER:
                return await self._handle_knowledge_request(message, mcp_servers)
            elif recipient_role == AgentRole.BUILD_MASTER:
                return await self._handle_build_request(message, mcp_servers)
            elif recipient_role == AgentRole.QUALITY_INSPECTOR:
                return await self._handle_quality_request(message, mcp_servers)
            else:
                return {
                    'success': False,
                    'error': f'No handler for agent role: {recipient_role.value}',
                    'message_id': message.id
                }

        except Exception as e:
            logger.error(f"Agent request failed for {recipient_role.value}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message_id': message.id
            }

    async def _handle_orchestrator_request(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle requests directed to the orchestrator"""
        try:
            # Use the enhanced orchestrator for complex multi-agent tasks
            result = await enhanced_orchestrator.collaborate(
                session_id=message.id,
                paradigm=message.context.get('paradigm', 'mesh'),
                task=message.data.get('task', message.intent),
                agents=message.data.get('agents', ['claude', 'gemini']),
                context=message.context
            )

            result['message_id'] = message.id
            result['sender'] = message.sender

            return result

        except Exception as e:
            logger.error(f"Orchestrator request failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message_id': message.id
            }

    # Specialized request handlers

    async def _handle_research_request(self, message: A2AMessage, mcp_servers: List[str]) -> Dict[str, Any]:
        """Handle research-specific requests"""
        intent = message.intent
        data = message.data

        if intent == "research_documentation":
            return await bridge_manager.execute_task(
                TaskType.RESEARCH,
                query=data.get('query', ''),
                detail_level=data.get('detail_level', 'normal')
            )
        elif intent == "find_examples":
            return await bridge_manager.execute_task(
                TaskType.RESEARCH,
                query=f"examples of {data.get('technology', '')} {data.get('use_case', '')}",
                detail_level="detailed"
            )
        else:
            return {'success': False, 'error': f'Unsupported research intent: {intent}'}

    async def _handle_code_analysis_request(self, message: A2AMessage, mcp_servers: List[str]) -> Dict[str, Any]:
        """Handle code analysis requests"""
        intent = message.intent
        data = message.data

        if intent == "analyze_quality":
            return await bridge_manager.execute_task(
                TaskType.CODE_ANALYSIS,
                code=data.get('code', ''),
                language=data.get('language', 'python')
            )
        elif intent == "security_audit":
            # Use both code analysis and research for comprehensive audit
            analysis_result = await bridge_manager.execute_task(
                TaskType.CODE_ANALYSIS,
                code=data.get('code', ''),
                language=data.get('language', 'python')
            )

            security_research = await bridge_manager.execute_task(
                TaskType.RESEARCH,
                query=f"security vulnerabilities {data.get('language', 'python')} code patterns",
                detail_level="detailed"
            )

            return {
                'success': True,
                'analysis': analysis_result,
                'security_research': security_research,
                'message_id': message.id
            }
        else:
            return {'success': False, 'error': f'Unsupported analysis intent: {intent}'}

    async def _handle_api_discovery_request(self, message: A2AMessage, mcp_servers: List[str]) -> Dict[str, Any]:
        """Handle API discovery requests"""
        intent = message.intent
        data = message.data

        if intent == "discover_apis":
            return await bridge_manager.execute_task(
                TaskType.API_DISCOVERY,
                technology=data.get('technology', ''),
                use_case=data.get('use_case', '')
            )
        elif intent == "evaluate_api":
            return await bridge_manager.execute_task(
                TaskType.RESEARCH,
                query=f"API evaluation {data.get('api_name', '')} documentation quality performance",
                detail_level="detailed"
            )
        else:
            return {'success': False, 'error': f'Unsupported API discovery intent: {intent}'}

    async def _handle_knowledge_request(self, message: A2AMessage, mcp_servers: List[str]) -> Dict[str, Any]:
        """Handle knowledge management requests"""
        intent = message.intent
        data = message.data

        if intent == "store_knowledge":
            return await bridge_manager.execute_task(
                TaskType.KNOWLEDGE_MANAGEMENT,
                action="create",
                data=data
            )
        elif intent == "query_knowledge":
            return await bridge_manager.execute_task(
                TaskType.KNOWLEDGE_MANAGEMENT,
                action="query",
                data=data
            )
        else:
            return {'success': False, 'error': f'Unsupported knowledge intent: {intent}'}

    async def _handle_build_request(self, message: A2AMessage, mcp_servers: List[str]) -> Dict[str, Any]:
        """Handle CI/CD build requests"""
        intent = message.intent
        data = message.data

        if intent == "trigger_build":
            return await bridge_manager.execute_task(
                TaskType.CI_CD,
                project=data.get('project', ''),
                branch=data.get('branch', 'main')
            )
        elif intent == "check_build_status":
            # This would be handled by Jenkins MCP server
            return await bridge_manager.execute_task(
                TaskType.CI_CD,
                project=data.get('project', ''),
                action="status"
            )
        else:
            return {'success': False, 'error': f'Unsupported build intent: {intent}'}

    async def _handle_quality_request(self, message: A2AMessage, mcp_servers: List[str]) -> Dict[str, Any]:
        """Handle quality assurance requests"""
        intent = message.intent
        data = message.data

        if intent == "check_deprecated":
            return await bridge_manager.execute_task(
                TaskType.DEPRECATED_CHECK,
                code=data.get('code', ''),
                language=data.get('language', 'python')
            )
        elif intent == "quality_report":
            # Comprehensive quality check using multiple MCP servers
            code_analysis = await bridge_manager.execute_task(
                TaskType.CODE_ANALYSIS,
                code=data.get('code', ''),
                language=data.get('language', 'python')
            )

            deprecated_check = await bridge_manager.execute_task(
                TaskType.DEPRECATED_CHECK,
                code=data.get('code', ''),
                language=data.get('language', 'python')
            )

            return {
                'success': True,
                'code_analysis': code_analysis,
                'deprecated_check': deprecated_check,
                'message_id': message.id
            }
        else:
            return {'success': False, 'error': f'Unsupported quality intent: {intent}'}

    # Workflow orchestration methods

    async def orchestrate_development_workflow(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate a complete development workflow using A2A and MCP"""
        workflow_id = f"workflow_{int(time.time())}"
        results = {}

        try:
            # 1. Research phase
            research_msg = await self.create_message(
                sender="coordinator",
                recipient="research_agent",
                intent="research_documentation",
                data={
                    'query': f"{project_data.get('technology', '')} {project_data.get('project_type', '')} best practices",
                    'detail_level': 'detailed'
                },
                context={'workflow_id': workflow_id, 'phase': 'research'}
            )
            results['research'] = await self.route_message(research_msg)

            # 2. API discovery phase
            api_msg = await self.create_message(
                sender="coordinator",
                recipient="api_scout",
                intent="discover_apis",
                data={
                    'technology': project_data.get('technology', ''),
                    'use_case': project_data.get('use_case', '')
                },
                context={'workflow_id': workflow_id, 'phase': 'api_discovery'}
            )
            results['api_discovery'] = await self.route_message(api_msg)

            # 3. Code generation using orchestrator
            if project_data.get('generate_code'):
                code_msg = await self.create_message(
                    sender="coordinator",
                    recipient="orchestrator",
                    intent="generate_project",
                    data={
                        'task': f"Generate {project_data.get('project_type', '')} project using {project_data.get('technology', '')}",
                        'agents': ['claude', 'qwen', 'gemini'],
                        'requirements': project_data.get('requirements', [])
                    },
                    context={'workflow_id': workflow_id, 'phase': 'code_generation', 'paradigm': 'orchestra'}
                )
                results['code_generation'] = await self.route_message(code_msg)

            # 4. Quality assurance phase
            if results.get('code_generation', {}).get('success'):
                quality_msg = await self.create_message(
                    sender="coordinator",
                    recipient="quality_inspector",
                    intent="quality_report",
                    data={
                        'code': results['code_generation'].get('generated_code', ''),
                        'language': project_data.get('language', 'python')
                    },
                    context={'workflow_id': workflow_id, 'phase': 'quality_assurance'}
                )
                results['quality_assurance'] = await self.route_message(quality_msg)

            # 5. Knowledge storage phase
            knowledge_msg = await self.create_message(
                sender="coordinator",
                recipient="knowledge_keeper",
                intent="store_knowledge",
                data={
                    'title': f"Project: {project_data.get('name', 'Unnamed')}",
                    'content': {
                        'research': results.get('research'),
                        'apis': results.get('api_discovery'),
                        'quality': results.get('quality_assurance')
                    }
                },
                context={'workflow_id': workflow_id, 'phase': 'knowledge_storage'}
            )
            results['knowledge_storage'] = await self.route_message(knowledge_msg)

            return {
                'success': True,
                'workflow_id': workflow_id,
                'results': results,
                'phases_completed': len([r for r in results.values() if r.get('success')])
            }

        except Exception as e:
            logger.error(f"Workflow orchestration failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'workflow_id': workflow_id,
                'partial_results': results
            }

    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all A2A agents and MCP servers"""
        bridge_status = await bridge_manager.get_bridge_status()

        return {
            'agents': self.agents,
            'mcp_servers': bridge_status,
            'message_queue_size': self.message_queue.qsize(),
            'message_history_count': len(self.message_history),
            'active_sessions': len(self.active_sessions)
        }

    async def process_message_queue(self):
        """Process messages from the queue continuously"""
        while True:
            try:
                message = await self.message_queue.get()
                result = await self.route_message(message)
                logger.info(f"Processed message {message.id}: {result.get('success', False)}")
                self.message_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing message queue: {e}")
                await asyncio.sleep(1)


# Global A2A MCP coordinator instance
a2a_mcp_coordinator = A2AMCPCoordinator()

# Test function
async def test_a2a_mcp_integration():
    """Test A2A MCP integration"""
    logger.info("Testing A2A MCP Integration")
    logger.info("=" * 50)

    coordinator = a2a_mcp_coordinator

    # Test individual agent communication
    test_message = await coordinator.create_message(
        sender="test_client",
        recipient="research_agent",
        intent="research_documentation",
        data={
            'query': 'FastAPI best practices for production deployment',
            'detail_level': 'detailed'
        }
    )

    result = await coordinator.route_message(test_message)
    logger.info(f"Research result: {result.get('success', False)}")

    # Test workflow orchestration
    workflow_result = await coordinator.orchestrate_development_workflow({
        'name': 'Test API Project',
        'technology': 'FastAPI',
        'project_type': 'REST API',
        'use_case': 'user management system',
        'language': 'python',
        'generate_code': True,
        'requirements': ['authentication', 'database integration', 'API documentation']
    })

    logger.info(f"Workflow result: {workflow_result.get('success', False)}")
    logger.info(f"Phases completed: {workflow_result.get('phases_completed', 0)}")

    # Get system status
    status = await coordinator.get_agent_status()
    logger.info(f"Active agents: {len(status['agents'])}")
    logger.info(f"MCP servers: {status['mcp_servers']['healthy_count']}/{status['mcp_servers']['total_count']}")

if __name__ == "__main__":
    asyncio.run(test_a2a_mcp_integration())