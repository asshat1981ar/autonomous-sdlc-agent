"""
Gemini CLI Bridge Service
Integrates with Google Gemini CLI for advanced AI capabilities
"""

import asyncio
import subprocess
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile
import os

# Constants
MILLISECONDS_PER_SECOND = 1000


logger = logging.getLogger(__name__)

class GeminiCliBridge:
    """Bridge service to Google Gemini CLI"""

    def __init__(self):
        """  Init   with enhanced functionality."""
        self.setup_complete = False
        self.temp_dir = tempfile.mkdtemp(prefix="gemini_bridge_")

    async def setup_gemini_cli(self) -> Dict[str, Any]:
        """Setup Gemini CLI if not already installed"""
        try:
            # Check if gemini CLI is available
            check_result = await self._run_command(['npx', 'gemini-cli', '--version'])

            if check_result['success']:
                self.setup_complete = True
                return {
                    'success': True,
                    'message': 'Gemini CLI already available',
                    'version': check_result['output']
                }

            # Install gemini CLI
            logger.info("Installing Gemini CLI...")
            install_result = await self._run_command([
                'npm', 'install', '-g', '@google-ai/generativelanguage'
            ])

            if install_result['success']:
                self.setup_complete = True
                return {
                    'success': True,
                    'message': 'Gemini CLI installed successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to install Gemini CLI: {install_result['error']}"
                }

        except Exception as e:
            logger.error(f"Gemini CLI setup error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def generate_text(self, prompt: str, model: str = "gemini-pro",
                           temperature: float = 0.7, max_tokens: int = MILLISECONDS_PER_SECOND) -> Dict[str, Any]:
        """Generate text using Gemini CLI"""
        try:
            if not self.setup_complete:
                setup_result = await self.setup_gemini_cli()
                if not setup_result['success']:
                    return setup_result

            # Create prompt file
            prompt_file = Path(self.temp_dir) / "prompt.txt"
            prompt_file.write_text(prompt)

            cmd = [
                'npx', 'gemini-cli',
                'generate',
                '--model', model,
                '--prompt-file', str(prompt_file),
                '--temperature', str(temperature),
                '--max-tokens', str(max_tokens),
                '--format', 'json'
            ]

            result = await self._run_command(cmd)

            if result['success']:
                try:
                    response = json.loads(result['output'])
                    return {
                        'success': True,
                        'text': response.get('text', ''),
                        'model': model,
                        'usage': response.get('usage', {}),
                        'safety_ratings': response.get('safety_ratings', [])
                    }
                except json.JSONDecodeError:
                    return {
                        'success': True,
                        'text': result['output'],
                        'model': model
                    }
            else:
                return {
                    'success': False,
                    'error': result['error']
                }

        except Exception as e:
            logger.error(f"Gemini text generation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def analyze_code(self, code: str, language: str = "python",
                          analysis_type: str = "quality") -> Dict[str, Any]:
        """Analyze code using Gemini CLI"""
        try:
            prompt = f"""
            Analyze this {language} code for {analysis_type}:

            ```{language}
            {code}
            ```

            Provide analysis in JSON format with:
            - quality_score (0-100)
            - issues: [{{type, severity, line, message}}]
            - suggestions: [{{type, description, example}}]
            - complexity: {{cyclomatic, cognitive, maintainability}}
            - security: [{{severity, issue, recommendation}}]
            """

            result = await self.generate_text(
                prompt=prompt,
                model="gemini-pro",
                temperature=0.3
            )

            if result['success']:
                try:
                    # Try to extract JSON from response
                    text = result['text']
                    if '```json' in text:
                        json_start = text.find('```json') + 7
                        json_end = text.find('```', json_start)
                        json_text = text[json_start:json_end].strip()
                    else:
                        json_text = text

                    analysis = json.loads(json_text)
                    return {
                        'success': True,
                        'analysis': analysis,
                        'language': language,
                        'analysis_type': analysis_type
                    }
                except json.JSONDecodeError:
                    return {
                        'success': True,
                        'raw_analysis': result['text'],
                        'language': language
                    }
            else:
                return result

        except Exception as e:
            logger.error(f"Gemini code analysis error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def generate_code(self, prompt: str, language: str = "python",
                           framework: str = "", style: str = "clean") -> Dict[str, Any]:
        """Generate code using Gemini CLI"""
        try:
            enhanced_prompt = f"""
            Generate {language} code for: {prompt}

            Requirements:
            - Language: {language}
            - Framework: {framework if framework else 'standard library'}
            - Style: {style}
            - Include comments and documentation
            - Follow best practices
            - Add error handling

            Provide response in JSON format:
            {{
                "code": "generated code here",
                "explanation": "explanation of the code",
                "usage": "how to use this code",
                "dependencies": ["list of dependencies"],
                "tests": "example tests"
            }}
            """

            result = await self.generate_text(
                prompt=enhanced_prompt,
                model="gemini-pro",
                temperature=0.5
            )

            if result['success']:
                try:
                    text = result['text']
                    if '```json' in text:
                        json_start = text.find('```json') + 7
                        json_end = text.find('```', json_start)
                        json_text = text[json_start:json_end].strip()
                    else:
                        json_text = text

                    code_result = json.loads(json_text)
                    return {
                        'success': True,
                        'code': code_result.get('code', ''),
                        'explanation': code_result.get('explanation', ''),
                        'usage': code_result.get('usage', ''),
                        'dependencies': code_result.get('dependencies', []),
                        'tests': code_result.get('tests', ''),
                        'language': language
                    }
                except json.JSONDecodeError:
                    # Fallback: try to extract code blocks
                    text = result['text']
                    if f'```{language}' in text:
                        code_start = text.find(f'```{language}') + len(f'```{language}')
                        code_end = text.find('```', code_start)
                        code = text[code_start:code_end].strip()
                        return {
                            'success': True,
                            'code': code,
                            'explanation': text,
                            'language': language
                        }
                    else:
                        return {
                            'success': True,
                            'code': text,
                            'language': language
                        }
            else:
                return result

        except Exception as e:
            logger.error(f"Gemini code generation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def optimize_code(self, code: str, language: str = "python",
                           optimization_type: str = "performance") -> Dict[str, Any]:
        """Optimize code using Gemini CLI"""
        try:
            prompt = f"""
            Optimize this {language} code for {optimization_type}:

            ```{language}
            {code}
            ```

            Provide optimized version with:
            - Improved performance
            - Better memory usage
            - Enhanced readability
            - Modern best practices

            Response format:
            {{
                "optimized_code": "optimized code here",
                "improvements": ["list of improvements made"],
                "performance_gains": "expected performance improvements",
                "explanation": "detailed explanation of changes"
            }}
            """

            result = await self.generate_text(
                prompt=prompt,
                model="gemini-pro",
                temperature=0.3
            )

            if result['success']:
                try:
                    text = result['text']
                    if '```json' in text:
                        json_start = text.find('```json') + 7
                        json_end = text.find('```', json_start)
                        json_text = text[json_start:json_end].strip()
                    else:
                        json_text = text

                    optimization = json.loads(json_text)
                    return {
                        'success': True,
                        'original_code': code,
                        'optimized_code': optimization.get('optimized_code', ''),
                        'improvements': optimization.get('improvements', []),
                        'performance_gains': optimization.get('performance_gains', ''),
                        'explanation': optimization.get('explanation', ''),
                        'optimization_type': optimization_type
                    }
                except json.JSONDecodeError:
                    return {
                        'success': True,
                        'raw_response': result['text'],
                        'original_code': code
                    }
            else:
                return result

        except Exception as e:
            logger.error(f"Gemini code optimization error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _run_command(self, cmd: List[str]) -> Dict[str, Any]:
        """Run command asynchronously"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return {
                    'success': True,
                    'output': stdout.decode().strip(),
                    'returncode': process.returncode
                }
            else:
                return {
                    'success': False,
                    'error': stderr.decode().strip(),
                    'returncode': process.returncode
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def health_check(self) -> Dict[str, Any]:
        """Check if Gemini CLI bridge is working"""
        try:
            result = await self._run_command(['npx', 'gemini-cli', '--help'])

            if result['success']:
                return {
                    'status': 'healthy',
                    'setup_complete': self.setup_complete,
                    'help_available': True
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': result['error'],
                    'setup_complete': self.setup_complete
                }

        except Exception as e:
            return {
                'status': 'unavailable',
                'error': str(e),
                'setup_complete': self.setup_complete
            }

    def __del__(self):
        """Cleanup temporary directory"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass


# Bridge service instance
gemini_cli_bridge = GeminiCliBridge()