#!/usr/bin/env python3
"""
Enhanced AI Orchestrator with BlackBox AI integration and extensive free models
Based on the comprehensive model analysis with A2A framework
"""
import os
import json
import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for AI models"""
    id: str
    name: str
    provider: str
    context_window: int
    strengths: List[str]
    optimal_for: List[str]
    speed_rating: str  # "fast", "medium", "slow"
    accuracy_rating: str  # "high", "medium", "low"

class EnhancedAIProvider:
    """Enhanced AI Provider with extensive model support"""
    
    # BlackBox AI API Configuration
    BLACKBOX_API_KEY = "sk-8K0xZsHMXRrGjhFewKm_Dg"
    BLACKBOX_BASE_URL = "https://api.blackbox.ai/v1"
    
    # Extensive model configurations based on analysis
    MODELS = {
        # DeepSeek Series - Ultra-large MoE models
        "deepseek-v3": ModelConfig(
            id="blackboxai/deepseek-v3-0324",
            name="DeepSeek V3",
            provider="blackbox",
            context_window=160000,
            strengths=["coding", "reasoning", "long_context"],
            optimal_for=["complex_algorithms", "architecture_design", "debugging"],
            speed_rating="slow",
            accuracy_rating="high"
        ),
        "deepseek-r1": ModelConfig(
            id="blackboxai/deepseek-r1-0528", 
            name="DeepSeek R1",
            provider="blackbox",
            context_window=160000,
            strengths=["reasoning", "math", "function_calling"],
            optimal_for=["step_by_step_analysis", "complex_logic", "formal_reasoning"],
            speed_rating="slow",
            accuracy_rating="high"
        ),
        "deepseek-r1-distill-70b": ModelConfig(
            id="blackboxai/deepseek-r1-distill-llama-70b",
            name="DeepSeek R1 Distill 70B",
            provider="blackbox",
            context_window=128000,
            strengths=["coding", "reasoning", "efficiency"],
            optimal_for=["code_review", "architecture_planning", "optimization"],
            speed_rating="medium",
            accuracy_rating="high"
        ),
        
        # Qwen Series - High-performing code models
        "qwen-coder-32b": ModelConfig(
            id="qwen/qwen2.5-coder-32b-instruct",
            name="Qwen 2.5 Coder 32B",
            provider="blackbox",
            context_window=32000,
            strengths=["code_generation", "code_fixing", "debugging"],
            optimal_for=["implementation", "bug_fixes", "code_optimization"],
            speed_rating="fast",
            accuracy_rating="high"
        ),
        "qwen-72b": ModelConfig(
            id="qwen/qwen2.5-72b-instruct",
            name="Qwen 2.5 72B",
            provider="blackbox",
            context_window=32000,
            strengths=["general_intelligence", "multilingual", "reasoning"],
            optimal_for=["complex_tasks", "planning", "analysis"],
            speed_rating="medium",
            accuracy_rating="high"
        ),
        "qwerky-72b": ModelConfig(
            id="featherless/qwerky-72b",
            name="Qwerky 72B (RWKV)",
            provider="blackbox",
            context_window=32000,
            strengths=["speed", "efficiency", "multilingual"],
            optimal_for=["rapid_prototyping", "quick_iterations", "real_time_responses"],
            speed_rating="fast",
            accuracy_rating="high"
        ),
        
        # Specialized Code Models
        "deepcoder-14b": ModelConfig(
            id="agentica/deepcoder-14b",
            name="DeepCoder 14B",
            provider="blackbox",
            context_window=96000,
            strengths=["code_accuracy", "competitive_programming", "algorithms"],
            optimal_for=["precise_coding", "algorithm_implementation", "code_challenges"],
            speed_rating="fast",
            accuracy_rating="high"
        ),
        
        # GLM Models - Enhanced reasoning
        "glm-z1-32b": ModelConfig(
            id="thudm/glm-z1-32b-0414",
            name="GLM Z1 32B",
            provider="blackbox",
            context_window=32000,
            strengths=["structured_reasoning", "formal_logic", "tool_calling"],
            optimal_for=["planning", "analysis", "formal_verification"],
            speed_rating="medium",
            accuracy_rating="high"
        ),
        
        # Meta Llama Models
        "llama-70b": ModelConfig(
            id="meta-llama/llama-3.3-70b-instruct",
            name="Llama 3.3 70B",
            provider="blackbox",
            context_window=131000,
            strengths=["instruction_following", "multilingual", "conversation"],
            optimal_for=["user_interaction", "documentation", "explanation"],
            speed_rating="medium",
            accuracy_rating="high"
        ),
        
        # Gemini Models - Fast and efficient
        "gemini-flash": ModelConfig(
            id="google/gemini-2.0-flash-thinking",
            name="Gemini 2.0 Flash",
            provider="blackbox",
            context_window=100000,
            strengths=["speed", "reasoning", "thinking_mode"],
            optimal_for=["rapid_analysis", "interactive_sessions", "real_time_help"],
            speed_rating="fast",
            accuracy_rating="high"
        ),
        
        # Mistral Models - Efficient specialists
        "mistral-24b": ModelConfig(
            id="mistralai/mistral-small-24b-instruct-2501",
            name="Mistral Small 24B",
            provider="blackbox",
            context_window=32000,
            strengths=["efficiency", "instruction_following", "balanced_performance"],
            optimal_for=["moderate_tasks", "quick_responses", "general_coding"],
            speed_rating="fast",
            accuracy_rating="medium"
        )
    }
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or self.BLACKBOX_API_KEY
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def generate_response(self, 
                              model_id: str, 
                              prompt: str, 
                              context: Optional[Dict] = None,
                              max_tokens: int = 2000,
                              temperature: float = 0.7) -> Dict[str, Any]:
        """Generate response from specified model"""
        try:
            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": "You are an expert AI coding assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            # Add context if provided
            if context:
                payload["messages"].insert(1, {
                    "role": "system", 
                    "content": f"Context: {json.dumps(context)}"
                })
            
            async with self.session.post(f"{self.BLACKBOX_BASE_URL}/chat/completions", 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "response": data["choices"][0]["message"]["content"],
                        "model": model_id,
                        "usage": data.get("usage", {}),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"API Error {response.status}: {error_text}",
                        "model": model_id,
                        "timestamp": datetime.now().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"Error generating response with {model_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "model": model_id,
                "timestamp": datetime.now().isoformat()
            }

class VibeCodeOrchestrator:
    """Enhanced orchestrator for Vibe-Code platform with specialized agents"""
    
    def __init__(self):
        self.provider = EnhancedAIProvider()
        self.active_sessions = {}
        self.agent_roles = {
            "planner": {
                "models": ["glm-z1-32b", "llama-70b", "deepseek-r1-distill-70b"],
                "description": "Project planning and architecture design"
            },
            "coder": {
                "models": ["qwen-coder-32b", "deepcoder-14b", "qwen-72b"],
                "description": "Code implementation and generation"
            },
            "reviewer": {
                "models": ["deepseek-r1-distill-70b", "gemini-flash", "glm-z1-32b"],
                "description": "Code review and quality assurance"
            },
            "speed_agent": {
                "models": ["qwerky-72b", "gemini-flash", "mistral-24b"],
                "description": "Fast responses and real-time interaction"
            },
            "specialist": {
                "models": ["deepseek-v3", "deepseek-r1"],
                "description": "Complex reasoning and deep analysis"
            }
        }
        
    async def create_vibe_session(self, project_description: str, agents: List[str] = None) -> str:
        """Create a new vibe-coding session"""
        session_id = f"vibe_{int(time.time())}"
        
        # Default agent selection based on task complexity
        if not agents:
            agents = ["planner", "coder", "reviewer", "speed_agent"]
            
        self.active_sessions[session_id] = {
            "description": project_description,
            "agents": agents,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "artifacts": {},
            "status": "active"
        }
        
        logger.info(f"Created vibe session {session_id} with agents: {agents}")
        return session_id
        
    async def process_vibe_request(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Process a natural language vibe request"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
            
        # Step 1: Planning Agent analyzes the request
        planning_result = await self._run_agent("planner", f"""
        Analyze this user request and create a development plan:
        
        Project Context: {session['description']}
        User Request: {user_input}
        
        Provide a structured plan with:
        1. Required modules/components
        2. Implementation approach
        3. Technology recommendations
        4. Task breakdown
        
        Respond in JSON format with clear sections.
        """, session_id)
        
        # Step 2: Coder Agent implements the solution
        coding_result = await self._run_agent("coder", f"""
        Implement the solution based on this plan:
        
        Plan: {planning_result.get('response', '')}
        User Request: {user_input}
        
        Generate working code with:
        - Complete implementation
        - Proper structure and organization
        - Comments and documentation
        - Error handling
        
        Format as markdown with code blocks.
        """, session_id)
        
        # Step 3: Reviewer Agent checks the implementation
        review_result = await self._run_agent("reviewer", f"""
        Review this implementation for quality and correctness:
        
        Original Request: {user_input}
        Plan: {planning_result.get('response', '')}
        Code: {coding_result.get('response', '')}
        
        Provide:
        - Code quality assessment
        - Potential issues or improvements
        - Test recommendations
        - Final approval or revision suggestions
        """, session_id)
        
        # Store artifacts
        session["artifacts"] = {
            "plan": planning_result.get('response', ''),
            "code": coding_result.get('response', ''),
            "review": review_result.get('response', ''),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "session_id": session_id,
            "plan": planning_result,
            "implementation": coding_result,
            "review": review_result,
            "status": "completed"
        }
        
    async def _run_agent(self, agent_type: str, prompt: str, session_id: str) -> Dict[str, Any]:
        """Run a specific agent with optimal model selection"""
        agent_config = self.agent_roles.get(agent_type)
        if not agent_config:
            return {"error": f"Unknown agent type: {agent_type}"}
            
        # Select best model for the agent based on current load and capabilities
        model_id = self._select_optimal_model(agent_type)
        
        async with self.provider as provider:
            result = await provider.generate_response(
                model_id=model_id,
                prompt=prompt,
                context={"agent_type": agent_type, "session_id": session_id}
            )
            
        # Log the interaction
        session = self.active_sessions.get(session_id, {})
        session.setdefault("messages", []).append({
            "agent": agent_type,
            "model": model_id,
            "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
            "response": result.get('response', '')[:200] + "..." if len(result.get('response', '')) > 200 else result.get('response', ''),
            "timestamp": datetime.now().isoformat(),
            "success": result.get('success', False)
        })
        
        return result
        
    def _select_optimal_model(self, agent_type: str) -> str:
        """Select optimal model based on agent type and current performance"""
        agent_config = self.agent_roles.get(agent_type, {})
        available_models = agent_config.get("models", ["qwen-coder-32b"])
        
        # For now, select the first available model
        # In production, this would consider load balancing, performance metrics, etc.
        return EnhancedAIProvider.MODELS[available_models[0]].id
        
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status and artifacts of a vibe session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
            
        return {
            "session_id": session_id,
            "status": session.get("status", "unknown"),
            "description": session.get("description", ""),
            "agents": session.get("agents", []),
            "created_at": session.get("created_at", ""),
            "message_count": len(session.get("messages", [])),
            "has_artifacts": bool(session.get("artifacts", {})),
            "artifacts": session.get("artifacts", {})
        }
        
    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models and their capabilities"""
        return {
            "models": {k: asdict(v) for k, v in EnhancedAIProvider.MODELS.items()},
            "agents": self.agent_roles,
            "total_models": len(EnhancedAIProvider.MODELS)
        }

# Global orchestrator instance
vibe_orchestrator = VibeCodeOrchestrator()