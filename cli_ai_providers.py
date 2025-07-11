#!/usr/bin/env python3
"""
CLI-based AI Provider Integration
For users with CLI access instead of direct API keys
"""
import asyncio
import subprocess
import json
import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CLIProviderConfig:
    """Configuration for CLI-based AI providers"""
    name: str
    cli_command: str
    available: bool = False

class CLIAIProvider:
    """AI Provider that uses CLI tools instead of direct API calls"""
    
    def __init__(self, config: CLIProviderConfig):
        self.config = config
        self.available = self._check_availability()
        
    def _check_availability(self) -> bool:
        """Check if the CLI tool is available"""
        try:
            # Test if the CLI command exists
            result = subprocess.run(
                [self.config.cli_command, "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            available = result.returncode == 0
            logger.info(f"{self.config.name} CLI availability: {available}")
            return available
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            logger.warning(f"{self.config.name} CLI not available")
            return False
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response using CLI tool"""
        if not self.available:
            return await self._fallback_response(prompt, "CLI tool not available")
        
        try:
            return await self._execute_cli_command(prompt, context)
        except Exception as e:
            logger.error(f"CLI execution failed for {self.config.name}: {e}")
            return await self._fallback_response(prompt, str(e))
    
    async def _execute_cli_command(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the specific CLI command based on provider type"""
        if "blackbox" in self.config.name.lower():
            return await self._execute_blackbox_cli(prompt, context)
        elif "claude" in self.config.name.lower():
            return await self._execute_claude_cli(prompt, context)
        elif "github" in self.config.name.lower() or "copilot" in self.config.name.lower():
            return await self._execute_github_copilot(prompt, context)
        else:
            return await self._fallback_response(prompt, "Unknown CLI provider")
    
    async def _execute_blackbox_cli(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute Blackbox CLI command"""
        try:
            # Prepare Blackbox CLI command
            cmd = [
                "blackbox",  # Adjust based on your actual CLI command
                "--prompt", prompt,
                "--format", "json"
            ]
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode == 0:
                response_text = stdout.decode().strip()
                return {
                    'success': True,
                    'response': response_text,
                    'provider': 'Blackbox CLI',
                    'method': 'cli',
                    'timestamp': asyncio.get_event_loop().time()
                }
            else:
                error_msg = stderr.decode().strip()
                raise Exception(f"Blackbox CLI error: {error_msg}")
                
        except asyncio.TimeoutError:
            raise Exception("Blackbox CLI timeout")
        except Exception as e:
            raise Exception(f"Blackbox CLI execution failed: {e}")
    
    async def _execute_claude_cli(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute Claude Code CLI command"""
        try:
            # Prepare Claude CLI command
            cmd = [
                "claude-code",  # Adjust based on your actual CLI command
                "--message", prompt,
                "--format", "text"
            ]
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode == 0:
                response_text = stdout.decode().strip()
                return {
                    'success': True,
                    'response': response_text,
                    'provider': 'Claude Code CLI',
                    'method': 'cli',
                    'timestamp': asyncio.get_event_loop().time()
                }
            else:
                error_msg = stderr.decode().strip()
                raise Exception(f"Claude CLI error: {error_msg}")
                
        except asyncio.TimeoutError:
            raise Exception("Claude CLI timeout")
        except Exception as e:
            raise Exception(f"Claude CLI execution failed: {e}")
    
    async def _execute_github_copilot(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute GitHub Copilot CLI command"""
        try:
            # Use GitHub CLI with Copilot extension
            cmd = [
                "gh", "copilot", "suggest",
                "--type", "shell" if context and context.get('type') == 'shell' else "git",
                prompt
            ]
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode == 0:
                response_text = stdout.decode().strip()
                return {
                    'success': True,
                    'response': response_text,
                    'provider': 'GitHub Copilot CLI',
                    'method': 'cli',
                    'timestamp': asyncio.get_event_loop().time()
                }
            else:
                error_msg = stderr.decode().strip()
                raise Exception(f"GitHub Copilot CLI error: {error_msg}")
                
        except asyncio.TimeoutError:
            raise Exception("GitHub Copilot CLI timeout")
        except Exception as e:
            raise Exception(f"GitHub Copilot CLI execution failed: {e}")
    
    async def _fallback_response(self, prompt: str, error: str) -> Dict[str, Any]:
        """Fallback response when CLI fails"""
        return {
            'success': False,
            'response': f"CLI fallback response for: {prompt[:50]}...",
            'provider': self.config.name,
            'error': error,
            'fallback': True,
            'method': 'fallback',
            'timestamp': asyncio.get_event_loop().time()
        }

class CLIOrchestrator:
    """Orchestrator that uses CLI-based AI providers"""
    
    def __init__(self):
        self.providers = self._initialize_cli_providers()
        self.active_sessions: Dict[str, Any] = {}
        
    def _initialize_cli_providers(self) -> Dict[str, CLIAIProvider]:
        """Initialize CLI-based AI providers"""
        configs = {
            'blackbox': CLIProviderConfig(
                name="Blackbox CLI",
                cli_command="blackbox"  # Adjust based on your installation
            ),
            'claude': CLIProviderConfig(
                name="Claude Code CLI", 
                cli_command="claude-code"  # Adjust based on your installation
            ),
            'github': CLIProviderConfig(
                name="GitHub Copilot CLI",
                cli_command="gh"  # GitHub CLI with Copilot extension
            ),
            'mock': CLIProviderConfig(
                name="Mock AI Provider",
                cli_command="echo"  # Always available for testing
            )
        }
        
        providers = {}
        for provider_id, config in configs.items():
            provider = CLIAIProvider(config)
            providers[provider_id] = provider
            config.available = provider.available
            
        # Log available providers
        available_providers = [name for name, provider in providers.items() if provider.available]
        logger.info(f"Available CLI providers: {available_providers}")
        
        return providers
    
    async def collaborate(self, session_id: str, paradigm: str, task: str, 
                         agents: List[str], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Collaborate using CLI-based providers"""
        
        # Filter to available providers
        available_agents = [agent for agent in agents if agent in self.providers and self.providers[agent].available]
        
        if not available_agents:
            # Fallback to mock provider if no CLI tools available
            available_agents = ['mock']
            logger.warning("No CLI providers available, using mock provider")
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Execute CLI providers concurrently
            agent_tasks = []
            for agent_id in available_agents:
                provider = self.providers[agent_id]
                agent_prompt = f"SDLC Task - {paradigm}: {task}"
                agent_tasks.append(provider.generate_response(agent_prompt, context))
            
            # Wait for all CLI executions
            agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
            
            # Process results
            successful_results = []
            failed_results = []
            
            for i, result in enumerate(agent_results):
                if isinstance(result, dict) and result.get('success'):
                    successful_results.append({
                        'agent': available_agents[i],
                        'result': result
                    })
                else:
                    failed_results.append({
                        'agent': available_agents[i],
                        'error': str(result) if isinstance(result, Exception) else result.get('error', 'Unknown error')
                    })
            
            return {
                'success': len(successful_results) > 0,
                'session_id': session_id,
                'paradigm': paradigm,
                'task': task,
                'agents_used': available_agents,
                'successful_agents': len(successful_results),
                'failed_agents': len(failed_results),
                'agent_results': successful_results,
                'agent_failures': failed_results if failed_results else None,
                'duration': asyncio.get_event_loop().time() - start_time,
                'timestamp': asyncio.get_event_loop().time(),
                'method': 'cli',
                'cli_providers_available': [name for name, p in self.providers.items() if p.available]
            }
            
        except Exception as e:
            logger.error(f"CLI collaboration failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id,
                'timestamp': asyncio.get_event_loop().time(),
                'method': 'cli'
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of CLI providers"""
        health_status = {
            'status': 'healthy',
            'timestamp': asyncio.get_event_loop().time(),
            'method': 'cli',
            'providers': {}
        }
        
        for provider_id, provider in self.providers.items():
            health_status['providers'][provider_id] = {
                'available': provider.available,
                'cli_command': provider.config.cli_command,
                'status': 'healthy' if provider.available else 'unavailable'
            }
        
        # Determine overall status
        available_count = sum(1 for p in self.providers.values() if p.available)
        if available_count == 0:
            health_status['status'] = 'degraded'
        elif available_count < len(self.providers) / 2:
            health_status['status'] = 'degraded'
        
        return health_status

# Global CLI orchestrator instance
cli_orchestrator = CLIOrchestrator()

# Test the CLI orchestrator
async def test_cli_orchestrator():
    """Test CLI-based orchestrator"""
    print("Testing CLI-Based SDLC Orchestrator")
    print("=" * 50)
    
    # Health check
    health = await cli_orchestrator.health_check()
    print(f"Health Status: {health['status']}")
    print(f"Available Providers: {[p for p, info in health['providers'].items() if info['available']]}")
    
    # Test collaboration
    result = await cli_orchestrator.collaborate(
        session_id="cli_test",
        paradigm="orchestra",
        task="Create a Python function to validate email addresses",
        agents=["blackbox", "claude", "github", "mock"],
        context={"language": "python", "type": "function"}
    )
    
    print(f"\nCollaboration Result:")
    print(f"Success: {result['success']}")
    print(f"Method: {result.get('method', 'unknown')}")
    print(f"Successful Agents: {result.get('successful_agents', 0)}")
    print(f"Available CLI Providers: {result.get('cli_providers_available', [])}")
    
    return cli_orchestrator

if __name__ == "__main__":
    asyncio.run(test_cli_orchestrator())
