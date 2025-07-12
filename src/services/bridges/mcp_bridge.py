"""
MCP Bridge
Integrates Model Context Protocol servers with the A2A framework
"""

import asyncio
import logging
import json
import subprocess
import os
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import sqlite3
from pathlib import Path

# Constants
MILLISECONDS_PER_SECOND = 1000


logger = logging.getLogger(__name__)

class MCPServerConfig:
    """Configuration for an MCP server"""
    def __init__(self, name: str, command: str, args: List[str] = None,
                 """  Init   with enhanced functionality."""
                 capabilities: List[str] = None, health_check_timeout: int = 30):
        self.name = name
        self.command = command
        self.args = args or []
        self.capabilities = capabilities or []
        self.health_check_timeout = health_check_timeout
        self.process = None
        self.status = 'inactive'
        self.last_health_check = 0


class MCPBridge:
    """Bridge for Model Context Protocol servers"""

    """  Init   with enhanced functionality."""
    def __init__(self):
        self.mock_mode = True  # Enable mock mode for testing
        self.servers = {}
        self.active_connections = {}
        self.message_id_counter = 0
        self.db_path = "mcp_bridge.db"
        self._init_database()
        self._discover_mcp_servers()

    def _init_database(self):
        """Initialize SQLite database for MCP bridge data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create tables for MCP server management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mcp_servers (
                    name TEXT PRIMARY KEY,
                    command TEXT NOT NULL,
                    args TEXT,
                    capabilities TEXT,
                    status TEXT,
                    last_health_check INTEGER,
                    created_at INTEGER
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mcp_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_name TEXT,
                    method TEXT,
                    params TEXT,
                    response TEXT,
                    status TEXT,
                    timestamp INTEGER,
                    duration_ms INTEGER
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mcp_capabilities (
                    server_name TEXT,
                    capability TEXT,
                    description TEXT,
                    PRIMARY KEY (server_name, capability)
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("MCP Bridge database initialized")

        except Exception as e:
            logger.error(f"Failed to initialize MCP bridge database: {e}")

    def _discover_mcp_servers(self):
        """Discover available MCP servers"""
        # Known MCP server configurations
        mcp_configs = [
            MCPServerConfig(
                name="perplexity",
                command="node",
                args=["/mnt/c/Users/posso/Downloads/1/perplexity-mcp/build/index.js"],
                capabilities=["research", "documentation", "api_discovery", "deprecated_code_check"]
            ),
            MCPServerConfig(
                name="notion",
                command="npx",
                args=["@notionhq/notion-mcp-server"],
                capabilities=["knowledge_management", "documentation", "project_tracking"]
            ),
            MCPServerConfig(
                name="eslint",
                command="npx",
                args=["@uplinq/mcp-eslint"],
                capabilities=["code_analysis", "linting", "style_checking"]
            ),
            MCPServerConfig(
                name="deepseek",
                command="npx",
                args=["deepseek-mcp-server"],
                capabilities=["code_generation", "ai_analysis", "code_completion"]
            ),
            MCPServerConfig(
                name="jenkins",
                command="npx",
                args=["@grec0/mcp-jenkins"],
                capabilities=["ci_cd", "build_automation", "deployment"]
            )
        ]

        for config in mcp_configs:
            self.servers[config.name] = config
            logger.info(f"Registered MCP server: {config.name}")

    async def health_check(self) -> Dict[str, Any]:
        """Check health of MCP bridge and all servers"""
        healthy_servers = 0
        total_servers = len(self.servers)
        server_statuses = {}

        for name, server_config in self.servers.items():
            try:
                status = await self._check_server_health(server_config)
                server_statuses[name] = status
                if status.get('status') == 'healthy':
                    healthy_servers += 1
            except Exception as e:
                server_statuses[name] = {
                    'status': 'error',
                    'error': str(e)
                }

        overall_status = 'healthy' if healthy_servers > 0 else 'degraded' if healthy_servers == 0 and total_servers > 0 else 'offline'

        return {
            'status': overall_status,
            'servers': server_statuses,
            'healthy_servers': healthy_servers,
            'total_servers': total_servers,
            'timestamp': time.time()
        }

    async def _check_server_health(self, server_config: MCPServerConfig) -> Dict[str, Any]:
        """Check health of a specific MCP server"""
        try:
            # Check if server command exists
            if not server_config.command:
                return {'status': 'error', 'error': 'No command specified'}

            # Try to start server if not running
            if server_config.status != 'active':
                await self._start_server(server_config)

            # Perform a simple capabilities check
            result = await self._send_mcp_request(
                server_config.name,
                'initialize',
                {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {},
                    'clientInfo': {
                        'name': 'A2A-MCP-Bridge',
                        'version': '1.0.0'
                    }
                }
            )

            if result.get('success'):
                server_config.status = 'healthy'
                server_config.last_health_check = time.time()
                return {
                    'status': 'healthy',
                    'capabilities': server_config.capabilities,
                    'last_check': server_config.last_health_check
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error')
                }

        except Exception as e:
            logger.error(f"Health check failed for MCP server {server_config.name}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    async def _start_server(self, server_config: MCPServerConfig):
        """Start an MCP server process"""
        try:
            cmd = [server_config.command] + server_config.args

            # Start the server process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            server_config.process = process
            server_config.status = 'active'

            logger.info(f"Started MCP server: {server_config.name}")

        except Exception as e:
            logger.error(f"Failed to start MCP server {server_config.name}: {e}")
            server_config.status = 'error'
            raise

    async def _send_mcp_request(self, server_name: str, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a request to an MCP server (full mock implementation)"""
        start_time = time.time()

        # Always return mock responses in test mode
        try:
            duration_ms = int((time.time() - start_time) * MILLISECONDS_PER_SECOND)

            # Mock responses based on method
            if method == 'initialize':
                response = {
                    'jsonrpc': '2.0',
                    'id': 1,
                    'result': {
                        'protocolVersion': '2024-11-05',
                        'capabilities': {'tools': []},
                        'serverInfo': {'name': server_name, 'version': '1.0.0'}
                    }
                }
            elif method == 'search_docs':
                response = {
                    'jsonrpc': '2.0',
                    'id': 1,
                    'result': {
                        'results': [
                            {
                                'title': f'Mock documentation for {params.get("query", "")}',
                                'content': 'Mock comprehensive documentation content with best practices',
                                'url': f'https://mock-docs.example.com/{params.get("query", "").replace(" ", "-")}',
                                'score': 0.95
                            }
                        ]
                    }
                }
            elif method == 'find_apis':
                response = {
                    'jsonrpc': '2.0',
                    'id': 1,
                    'result': {
                        'apis': [
                            {
                                'name': f'{params.get("technology", "")}-api',
                                'description': f'Mock API for {params.get("technology", "")}',
                                'rating': 4.5,
                                'documentation': 'excellent',
                                'github_stars': 10000
                            }
                        ]
                    }
                }
            else:
                response = {
                    'jsonrpc': '2.0',
                    'id': 1,
                    'result': f'Mock response for {method} with server {server_name}'
                }

            self._log_mcp_request(server_name, method, params, response, 'success', duration_ms)

            return {
                'success': True,
                'response': response,
                'duration_ms': duration_ms,
                'mock': True
            }

        except Exception as e:
            logger.error(f"Mock MCP request failed for {server_name}.{method}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    def _log_mcp_request(self, server_name: str, method: str, params: Any,
                        response: Any, status: str, duration_ms: int):
        """Log MCP request to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO mcp_requests
                (server_name, method, params, response, status, timestamp, duration_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                server_name,
                method,
                json.dumps(params) if params else None,
                json.dumps(response) if response else None,
                status,
                int(time.time()),
                duration_ms
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to log MCP request: {e}")

    # A2A Framework Integration Methods

    async def research_documentation(self, query: str, detail_level: str = "normal") -> Dict[str, Any]:
        """Research documentation using Perplexity MCP server"""
        return await self._send_mcp_request(
            'perplexity',
            'search_docs',
            {
                'query': query,
                'detail_level': detail_level,
                'context': 'development'
            }
        )

    async def discover_apis(self, technology: str, use_case: str = "") -> Dict[str, Any]:
        """Discover APIs for integration using Perplexity MCP server"""
        return await self._send_mcp_request(
            'perplexity',
            'find_apis',
            {
                'technology': technology,
                'use_case': use_case,
                'criteria': ['popularity', 'documentation_quality', 'active_development']
            }
        )

    async def check_deprecated_code(self, code: str, language: str) -> Dict[str, Any]:
        """Check for deprecated code patterns using Perplexity MCP server"""
        return await self._send_mcp_request(
            'perplexity',
            'check_deprecated',
            {
                'code': code,
                'language': language,
                'check_type': 'comprehensive'
            }
        )

    async def analyze_code_quality(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code quality using ESLint MCP server"""
        return await self._send_mcp_request(
            'eslint',
            'lint_code',
            {
                'code': code,
                'language': language,
                'rules': 'recommended'
            }
        )

    async def manage_knowledge(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage knowledge using Notion MCP server"""
        return await self._send_mcp_request(
            'notion',
            action,
            data
        )

    async def trigger_build(self, project: str, branch: str = "main") -> Dict[str, Any]:
        """Trigger CI/CD build using Jenkins MCP server"""
        return await self._send_mcp_request(
            'jenkins',
            'trigger_build',
            {
                'project': project,
                'branch': branch,
                'parameters': {}
            }
        )

    async def generate_code_ai(self, prompt: str, language: str) -> Dict[str, Any]:
        """Generate code using DeepSeek MCP server"""
        return await self._send_mcp_request(
            'deepseek',
            'generate_code',
            {
                'prompt': prompt,
                'language': language,
                'style': 'production'
            }
        )

    # A2A Message Handling

    async def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A framework messages for MCP servers"""
        intent = message.get('intent', '')
        data = message.get('data', {})
        context = message.get('context', {})

        try:
            if intent == 'research_documentation':
                return await self.research_documentation(
                    data.get('query', ''),
                    data.get('detail_level', 'normal')
                )

            elif intent == 'discover_apis':
                return await self.discover_apis(
                    data.get('technology', ''),
                    data.get('use_case', '')
                )

            elif intent == 'check_deprecated':
                return await self.check_deprecated_code(
                    data.get('code', ''),
                    data.get('language', 'python')
                )

            elif intent == 'analyze_quality':
                return await self.analyze_code_quality(
                    data.get('code', ''),
                    data.get('language', 'javascript')
                )

            elif intent == 'manage_knowledge':
                return await self.manage_knowledge(
                    data.get('action', 'query'),
                    data.get('payload', {})
                )

            elif intent == 'trigger_build':
                return await self.trigger_build(
                    data.get('project', ''),
                    data.get('branch', 'main')
                )

            elif intent == 'generate_code':
                return await self.generate_code_ai(
                    data.get('prompt', ''),
                    data.get('language', 'python')
                )

            else:
                return {
                    'success': False,
                    'error': f'Unsupported intent: {intent}'
                }

        except Exception as e:
            logger.error(f"A2A message handling error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_server_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all MCP servers"""
        capabilities = {}
        for name, server_config in self.servers.items():
            capabilities[name] = server_config.capabilities
        return capabilities

    async def shutdown(self):
        """Shutdown all MCP server processes"""
        for name, server_config in self.servers.items():
            if server_config.process:
                try:
                    server_config.process.terminate()
                    await server_config.process.wait()
                    logger.info(f"Shutdown MCP server: {name}")
                except Exception as e:
                    logger.error(f"Error shutting down MCP server {name}: {e}")

        logger.info("MCP Bridge shutdown complete")


# Global MCP bridge instance
mcp_bridge = MCPBridge()