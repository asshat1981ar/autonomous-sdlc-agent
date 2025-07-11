"""
Blackbox.ai Premium Bridge Service
Integrates with Blackbox.ai premium API for advanced code generation and analysis
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
import os
from urllib.parse import urlencode
import time

logger = logging.getLogger(__name__)

class BlackboxAiBridge:
    """Bridge service to Blackbox.ai Premium API"""
    
    def __init__(self):
        self.api_key = os.getenv('BLACKBOX_API_KEY', '')
        self.premium_key = os.getenv('BLACKBOX_PREMIUM_KEY', '')
        self.base_url = "https://api.blackbox.ai"
        self.session_id = None
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0
        
    async def _rate_limit(self):
        """Implement rate limiting for API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    async def authenticate(self) -> Dict[str, Any]:
        """Authenticate with Blackbox.ai Premium"""
        try:
            await self._rate_limit()
            
            payload = {
                'apiKey': self.premium_key or self.api_key,
                'action': 'authenticate'
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'SDLC-Agent-Platform/1.0'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/auth",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.session_id = result.get('sessionId')
                        
                        return {
                            'success': True,
                            'authenticated': True,
                            'premium': result.get('premium', False),
                            'session_id': self.session_id,
                            'features': result.get('features', [])
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f'Authentication failed: {response.status} - {error_text}'
                        }
                        
        except Exception as e:
            logger.error(f"Blackbox.ai authentication error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_code(self, prompt: str, language: str = "python",
                           mode: str = "code", complexity: str = "medium") -> Dict[str, Any]:
        """Generate code using Blackbox.ai Premium"""
        try:
            if not self.session_id:
                auth_result = await self.authenticate()
                if not auth_result['success']:
                    return auth_result
            
            await self._rate_limit()
            
            payload = {
                'prompt': prompt,
                'language': language,
                'mode': mode,  # 'code', 'explain', 'optimize', 'debug'
                'complexity': complexity,  # 'simple', 'medium', 'advanced'
                'includeComments': True,
                'includeTests': True,
                'sessionId': self.session_id
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.premium_key or self.api_key}',
                'User-Agent': 'SDLC-Agent-Platform/1.0'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/generate",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        return {
                            'success': True,
                            'code': result.get('code', ''),
                            'explanation': result.get('explanation', ''),
                            'tests': result.get('tests', ''),
                            'documentation': result.get('documentation', ''),
                            'complexity_score': result.get('complexityScore', 0),
                            'quality_score': result.get('qualityScore', 0),
                            'language': language,
                            'mode': mode
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f'Code generation failed: {response.status} - {error_text}'
                        }
                        
        except Exception as e:
            logger.error(f"Blackbox.ai code generation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_code(self, code: str, language: str = "python",
                          analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze code using Blackbox.ai Premium"""
        try:
            await self._rate_limit()
            
            payload = {
                'code': code,
                'language': language,
                'analysisType': analysis_type,  # 'comprehensive', 'security', 'performance', 'quality'
                'sessionId': self.session_id
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.premium_key or self.api_key}',
                'User-Agent': 'SDLC-Agent-Platform/1.0'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/analyze",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        return {
                            'success': True,
                            'analysis': {
                                'quality_score': result.get('qualityScore', 0),
                                'security_score': result.get('securityScore', 0),
                                'performance_score': result.get('performanceScore', 0),
                                'maintainability_score': result.get('maintainabilityScore', 0)
                            },
                            'issues': result.get('issues', []),
                            'suggestions': result.get('suggestions', []),
                            'vulnerabilities': result.get('vulnerabilities', []),
                            'optimizations': result.get('optimizations', []),
                            'complexity_analysis': result.get('complexityAnalysis', {}),
                            'language': language,
                            'analysis_type': analysis_type
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f'Code analysis failed: {response.status} - {error_text}'
                        }
                        
        except Exception as e:
            logger.error(f"Blackbox.ai code analysis error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def optimize_code(self, code: str, language: str = "python",
                           optimization_goals: List[str] = None) -> Dict[str, Any]:
        """Optimize code using Blackbox.ai Premium"""
        try:
            if optimization_goals is None:
                optimization_goals = ['performance', 'readability', 'memory']
            
            await self._rate_limit()
            
            payload = {
                'code': code,
                'language': language,
                'optimizationGoals': optimization_goals,
                'preserveFunctionality': True,
                'sessionId': self.session_id
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.premium_key or self.api_key}',
                'User-Agent': 'SDLC-Agent-Platform/1.0'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/optimize",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        return {
                            'success': True,
                            'original_code': code,
                            'optimized_code': result.get('optimizedCode', ''),
                            'improvements': result.get('improvements', []),
                            'performance_gain': result.get('performanceGain', '0%'),
                            'memory_reduction': result.get('memoryReduction', '0%'),
                            'complexity_reduction': result.get('complexityReduction', '0%'),
                            'optimization_report': result.get('optimizationReport', ''),
                            'language': language,
                            'goals': optimization_goals
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f'Code optimization failed: {response.status} - {error_text}'
                        }
                        
        except Exception as e:
            logger.error(f"Blackbox.ai code optimization error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def debug_code(self, code: str, error_message: str,
                        language: str = "python", context: str = "") -> Dict[str, Any]:
        """Debug code using Blackbox.ai Premium"""
        try:
            await self._rate_limit()
            
            payload = {
                'code': code,
                'errorMessage': error_message,
                'language': language,
                'context': context,
                'includeExplanation': True,
                'sessionId': self.session_id
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.premium_key or self.api_key}',
                'User-Agent': 'SDLC-Agent-Platform/1.0'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/debug",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        return {
                            'success': True,
                            'diagnosis': result.get('diagnosis', ''),
                            'root_cause': result.get('rootCause', ''),
                            'fixed_code': result.get('fixedCode', ''),
                            'fixes': result.get('fixes', []),
                            'explanation': result.get('explanation', ''),
                            'prevention_tips': result.get('preventionTips', []),
                            'confidence': result.get('confidence', 0),
                            'language': language
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f'Code debugging failed: {response.status} - {error_text}'
                        }
                        
        except Exception as e:
            logger.error(f"Blackbox.ai code debugging error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_documentation(self, code: str, language: str = "python",
                                   doc_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate documentation using Blackbox.ai Premium"""
        try:
            await self._rate_limit()
            
            payload = {
                'code': code,
                'language': language,
                'documentationType': doc_type,  # 'comprehensive', 'api', 'inline', 'readme'
                'includeExamples': True,
                'sessionId': self.session_id
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.premium_key or self.api_key}',
                'User-Agent': 'SDLC-Agent-Platform/1.0'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/document",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        return {
                            'success': True,
                            'documentation': result.get('documentation', ''),
                            'api_docs': result.get('apiDocs', ''),
                            'examples': result.get('examples', []),
                            'usage_guide': result.get('usageGuide', ''),
                            'inline_comments': result.get('inlineComments', ''),
                            'doc_type': doc_type,
                            'language': language
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f'Documentation generation failed: {response.status} - {error_text}'
                        }
                        
        except Exception as e:
            logger.error(f"Blackbox.ai documentation generation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def code_completion(self, partial_code: str, language: str = "python",
                             cursor_position: int = None) -> Dict[str, Any]:
        """Get intelligent code completion using Blackbox.ai Premium"""
        try:
            if cursor_position is None:
                cursor_position = len(partial_code)
            
            await self._rate_limit()
            
            payload = {
                'partialCode': partial_code,
                'language': language,
                'cursorPosition': cursor_position,
                'maxSuggestions': 5,
                'includeContext': True,
                'sessionId': self.session_id
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.premium_key or self.api_key}',
                'User-Agent': 'SDLC-Agent-Platform/1.0'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/complete",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        return {
                            'success': True,
                            'completions': result.get('completions', []),
                            'cursor_position': cursor_position,
                            'context_aware': result.get('contextAware', False),
                            'language': language
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f'Code completion failed: {response.status} - {error_text}'
                        }
                        
        except Exception as e:
            logger.error(f"Blackbox.ai code completion error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if Blackbox.ai bridge is working"""
        try:
            auth_result = await self.authenticate()
            
            if auth_result['success']:
                return {
                    'status': 'healthy',
                    'authenticated': auth_result['authenticated'],
                    'premium': auth_result.get('premium', False),
                    'features': auth_result.get('features', []),
                    'session_active': bool(self.session_id)
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
blackbox_ai_bridge = BlackboxAiBridge()