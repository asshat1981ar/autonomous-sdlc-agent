"""
Claude Code Bridge Service
Integrates with Claude Code CLI for advanced code generation and analysis
"""

import asyncio
import subprocess
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile
import os

logger = logging.getLogger(__name__)

class ClaudeCodeBridge:
    """Bridge service to Claude Code CLI"""
    
    def __init__(self):
        self.claude_code_path = self._find_claude_code()
        self.temp_dir = tempfile.mkdtemp(prefix="claude_bridge_")
        
    def _find_claude_code(self) -> str:
        """Find Claude Code CLI installation"""
        try:
            # Try common installation paths
            result = subprocess.run(['which', 'claude-code'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
                
            # Try alternative paths
            for path in ['/usr/local/bin/claude-code', 
                        os.path.expanduser('~/.local/bin/claude-code'),
                        'claude-code']:
                if subprocess.run(['which', path], 
                                capture_output=True).returncode == 0:
                    return path
                    
        except Exception as e:
            logger.warning(f"Claude Code CLI not found: {e}")
            
        return 'claude-code'  # Fallback
    
    async def analyze_code(self, code: str, language: str = "python", 
                          context: str = "") -> Dict[str, Any]:
        """Analyze code using Claude Code"""
        try:
            # Create temporary file
            temp_file = Path(self.temp_dir) / f"code.{language}"
            temp_file.write_text(code)
            
            # Prepare Claude Code command
            cmd = [
                self.claude_code_path,
                'analyze',
                str(temp_file),
                '--format', 'json'
            ]
            
            if context:
                cmd.extend(['--context', context])
            
            # Execute Claude Code
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result = json.loads(stdout.decode())
                return {
                    'success': True,
                    'analysis': result,
                    'suggestions': result.get('suggestions', []),
                    'issues': result.get('issues', []),
                    'metrics': result.get('metrics', {})
                }
            else:
                logger.error(f"Claude Code analysis failed: {stderr.decode()}")
                return {
                    'success': False,
                    'error': stderr.decode(),
                    'fallback_analysis': self._basic_analysis(code, language)
                }
                
        except Exception as e:
            logger.error(f"Claude Code bridge error: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_analysis': self._basic_analysis(code, language)
            }
    
    async def generate_code(self, prompt: str, language: str = "python",
                           framework: str = "", style: str = "") -> Dict[str, Any]:
        """Generate code using Claude Code"""
        try:
            cmd = [
                self.claude_code_path,
                'generate',
                '--prompt', prompt,
                '--language', language,
                '--format', 'json'
            ]
            
            if framework:
                cmd.extend(['--framework', framework])
            if style:
                cmd.extend(['--style', style])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result = json.loads(stdout.decode())
                return {
                    'success': True,
                    'code': result.get('code', ''),
                    'explanation': result.get('explanation', ''),
                    'tests': result.get('tests', ''),
                    'documentation': result.get('documentation', '')
                }
            else:
                return {
                    'success': False,
                    'error': stderr.decode()
                }
                
        except Exception as e:
            logger.error(f"Claude Code generation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def refactor_code(self, code: str, language: str = "python",
                           refactor_type: str = "optimize") -> Dict[str, Any]:
        """Refactor code using Claude Code"""
        try:
            temp_file = Path(self.temp_dir) / f"refactor.{language}"
            temp_file.write_text(code)
            
            cmd = [
                self.claude_code_path,
                'refactor',
                str(temp_file),
                '--type', refactor_type,
                '--format', 'json'
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result = json.loads(stdout.decode())
                return {
                    'success': True,
                    'original_code': code,
                    'refactored_code': result.get('code', ''),
                    'changes': result.get('changes', []),
                    'improvements': result.get('improvements', [])
                }
            else:
                return {
                    'success': False,
                    'error': stderr.decode()
                }
                
        except Exception as e:
            logger.error(f"Claude Code refactor error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def debug_code(self, code: str, error_message: str,
                        language: str = "python") -> Dict[str, Any]:
        """Debug code using Claude Code"""
        try:
            temp_file = Path(self.temp_dir) / f"debug.{language}"
            temp_file.write_text(code)
            
            cmd = [
                self.claude_code_path,
                'debug',
                str(temp_file),
                '--error', error_message,
                '--format', 'json'
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result = json.loads(stdout.decode())
                return {
                    'success': True,
                    'diagnosis': result.get('diagnosis', ''),
                    'fixes': result.get('fixes', []),
                    'fixed_code': result.get('fixed_code', ''),
                    'explanation': result.get('explanation', '')
                }
            else:
                return {
                    'success': False,
                    'error': stderr.decode()
                }
                
        except Exception as e:
            logger.error(f"Claude Code debug error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _basic_analysis(self, code: str, language: str) -> Dict[str, Any]:
        """Fallback basic analysis when Claude Code is unavailable"""
        lines = code.split('\n')
        return {
            'lines_of_code': len(lines),
            'language': language,
            'functions': len([line for line in lines if 'def ' in line]),
            'classes': len([line for line in lines if 'class ' in line]),
            'comments': len([line for line in lines if line.strip().startswith('#')])
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if Claude Code bridge is working"""
        try:
            process = await asyncio.create_subprocess_exec(
                self.claude_code_path,
                '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                version = stdout.decode().strip()
                return {
                    'status': 'healthy',
                    'version': version,
                    'claude_code_path': self.claude_code_path
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': stderr.decode()
                }
                
        except Exception as e:
            return {
                'status': 'unavailable',
                'error': str(e)
            }
    
    def __del__(self):
        """Cleanup temporary directory"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass


# Bridge service instance
claude_code_bridge = ClaudeCodeBridge()