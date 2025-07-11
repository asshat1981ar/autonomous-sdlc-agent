"""
GitHub Codex Bridge Service
Integrates with GitHub Copilot/Codex for advanced code completion and generation
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
import os
from pathlib import Path
import base64

logger = logging.getLogger(__name__)

class GitHubCodexBridge:
    """Bridge service to GitHub Codex/Copilot"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.copilot_token = os.getenv('GITHUB_COPILOT_TOKEN', '')
        self.base_url = "https://api.github.com"
        self.copilot_url = "https://copilot-proxy.githubusercontent.com"
        
    async def authenticate_copilot(self) -> Dict[str, Any]:
        """Authenticate with GitHub Copilot"""
        try:
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'SDLC-Agent-Platform/1.0'
            }
            
            async with aiohttp.ClientSession() as session:
                # Check GitHub authentication
                async with session.get(
                    f"{self.base_url}/user",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        
                        # Try to get Copilot subscription status
                        async with session.get(
                            f"{self.base_url}/user/copilot_billing",
                            headers=headers
                        ) as billing_response:
                            if billing_response.status == 200:
                                billing_data = await billing_response.json()
                                return {
                                    'success': True,
                                    'authenticated': True,
                                    'user': user_data.get('login'),
                                    'copilot_enabled': True,
                                    'billing': billing_data
                                }
                            else:
                                return {
                                    'success': True,
                                    'authenticated': True,
                                    'user': user_data.get('login'),
                                    'copilot_enabled': False,
                                    'message': 'GitHub Copilot not enabled'
                                }
                    else:
                        return {
                            'success': False,
                            'error': f'GitHub authentication failed: {response.status}'
                        }
                        
        except Exception as e:
            logger.error(f"GitHub Copilot authentication error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def complete_code(self, code: str, language: str = "python",
                           cursor_position: int = None) -> Dict[str, Any]:
        """Get code completions using GitHub Copilot"""
        try:
            if cursor_position is None:
                cursor_position = len(code)
            
            # Prepare the completion request
            payload = {
                "prompt": code,
                "suffix": "",
                "max_tokens": 100,
                "temperature": 0.2,
                "top_p": 1,
                "n": 3,
                "stream": False,
                "logprobs": None,
                "stop": ["\n\n", "###"],
                "model": "copilot-codex",
                "language": language
            }
            
            headers = {
                'Authorization': f'Bearer {self.copilot_token or self.github_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'SDLC-Agent-Platform/1.0'
            }
            
            # Try GitHub Copilot API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.copilot_url}/v1/engines/copilot-codex/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        completions = []
                        
                        for choice in result.get('choices', []):
                            completions.append({
                                'text': choice.get('text', ''),
                                'score': choice.get('logprobs', {}).get('token_logprobs', [0])[0] if choice.get('logprobs') else 0.8,
                                'finish_reason': choice.get('finish_reason', 'unknown')
                            })
                        
                        return {
                            'success': True,
                            'completions': completions,
                            'language': language,
                            'model': 'github-copilot'
                        }
                    else:
                        # Fallback to local code completion
                        return await self._fallback_completion(code, language)
                        
        except Exception as e:
            logger.error(f"GitHub Copilot completion error: {e}")
            return await self._fallback_completion(code, language)
    
    async def generate_function(self, description: str, language: str = "python",
                               parameters: List[str] = None) -> Dict[str, Any]:
        """Generate a function using GitHub Codex"""
        try:
            # Create a prompt for function generation
            if parameters is None:
                parameters = []
            
            param_list = ", ".join(parameters) if parameters else ""
            
            prompt = f"""
# Generate a {language} function
# Description: {description}
# Parameters: {param_list}

def"""
            
            if language.lower() in ['javascript', 'typescript', 'js', 'ts']:
                prompt = f"""
// Generate a {language} function
// Description: {description}
// Parameters: {param_list}

function"""
            elif language.lower() in ['java']:
                prompt = f"""
// Generate a {language} function
// Description: {description}
// Parameters: {param_list}

public static"""
            
            result = await self.complete_code(prompt, language)
            
            if result['success'] and result['completions']:
                best_completion = max(result['completions'], key=lambda x: x['score'])
                
                return {
                    'success': True,
                    'function_code': prompt + best_completion['text'],
                    'description': description,
                    'language': language,
                    'parameters': parameters,
                    'confidence': best_completion['score']
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"GitHub Codex function generation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def explain_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Explain code using GitHub Codex"""
        try:
            # Create explanation prompt
            prompt = f"""
# Explain this {language} code:
{code}

# Explanation:
# This code"""
            
            result = await self.complete_code(prompt, language)
            
            if result['success'] and result['completions']:
                explanations = []
                
                for completion in result['completions']:
                    explanation_text = completion['text'].strip()
                    if explanation_text:
                        explanations.append({
                            'explanation': explanation_text,
                            'confidence': completion['score']
                        })
                
                return {
                    'success': True,
                    'explanations': explanations,
                    'code': code,
                    'language': language
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"GitHub Codex explanation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def fix_code(self, code: str, error_message: str,
                       language: str = "python") -> Dict[str, Any]:
        """Fix code using GitHub Codex"""
        try:
            prompt = f"""
# Fix this {language} code that has an error:
# Error: {error_message}

# Broken code:
{code}

# Fixed code:
"""
            
            result = await self.complete_code(prompt, language)
            
            if result['success'] and result['completions']:
                fixes = []
                
                for completion in result['completions']:
                    fixed_code = completion['text'].strip()
                    if fixed_code:
                        fixes.append({
                            'fixed_code': fixed_code,
                            'confidence': completion['score'],
                            'explanation': f"Fixed error: {error_message}"
                        })
                
                return {
                    'success': True,
                    'original_code': code,
                    'error_message': error_message,
                    'fixes': fixes,
                    'language': language
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"GitHub Codex code fix error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_tests(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Generate unit tests using GitHub Codex"""
        try:
            test_framework = {
                'python': 'pytest',
                'javascript': 'jest',
                'typescript': 'jest',
                'java': 'junit',
                'csharp': 'nunit'
            }.get(language.lower(), 'unittest')
            
            prompt = f"""
# Generate {test_framework} tests for this {language} code:
{code}

# Test code:
"""
            
            result = await self.complete_code(prompt, language)
            
            if result['success'] and result['completions']:
                test_suggestions = []
                
                for completion in result['completions']:
                    test_code = completion['text'].strip()
                    if test_code:
                        test_suggestions.append({
                            'test_code': test_code,
                            'framework': test_framework,
                            'confidence': completion['score']
                        })
                
                return {
                    'success': True,
                    'original_code': code,
                    'test_suggestions': test_suggestions,
                    'language': language,
                    'framework': test_framework
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"GitHub Codex test generation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _fallback_completion(self, code: str, language: str) -> Dict[str, Any]:
        """Fallback completion when GitHub Copilot is unavailable"""
        # Simple pattern-based completion
        lines = code.split('\n')
        last_line = lines[-1] if lines else ""
        
        suggestions = []
        
        # Python-specific completions
        if language.lower() == 'python':
            if last_line.strip().startswith('def '):
                suggestions.append(':\n    pass')
            elif last_line.strip().startswith('class '):
                suggestions.append(':\n    def __init__(self):\n        pass')
            elif last_line.strip().startswith('if '):
                suggestions.append(':\n    pass')
            elif last_line.strip().startswith('for '):
                suggestions.append(':\n    pass')
        
        # JavaScript/TypeScript completions
        elif language.lower() in ['javascript', 'typescript']:
            if last_line.strip().startswith('function '):
                suggestions.append(' {\n    \n}')
            elif last_line.strip().startswith('if '):
                suggestions.append(' {\n    \n}')
            elif last_line.strip().startswith('for '):
                suggestions.append(' {\n    \n}')
        
        return {
            'success': True,
            'completions': [
                {'text': suggestion, 'score': 0.5, 'finish_reason': 'fallback'}
                for suggestion in suggestions
            ],
            'language': language,
            'model': 'fallback-local'
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if GitHub Codex bridge is working"""
        try:
            auth_result = await self.authenticate_copilot()
            
            if auth_result['success']:
                return {
                    'status': 'healthy',
                    'authenticated': auth_result['authenticated'],
                    'copilot_enabled': auth_result.get('copilot_enabled', False),
                    'user': auth_result.get('user', 'unknown')
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': auth_result['error']
                }
                
        except Exception as e:
            return {
                'status': 'unavailable',
                'error': str(e)
            }


# Bridge service instance
github_codex_bridge = GitHubCodexBridge()