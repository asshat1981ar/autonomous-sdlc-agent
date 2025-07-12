"""
AI-Driven Paradigm and Agent Recommendation Engine

This module implements an intelligent recommendation system that analyzes task descriptions
and suggests optimal collaboration paradigms and AI agent combinations.
"""

import re
import json
import asyncio
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TaskAnalysis:
    """Represents the analysis of a user's task description."""
    domain: str
    complexity: str
    intent: str
    keywords: List[str]
    confidence: float

@dataclass
class Recommendation:
    """Represents a paradigm and agent recommendation."""
    paradigm: str
    agents: List[str]
    confidence: float
    justification: str
    estimated_duration: str

class NLPAnalyzer:
    """Natural Language Processing analyzer for task descriptions."""

    def __init__(self):
        """  Init   with enhanced functionality."""
        # Domain keywords mapping
        self.domain_keywords = {
            'python': ['python', 'django', 'flask', 'pandas', 'numpy', 'fastapi', 'pytest'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'angular', 'express', 'npm'],
            'web': ['html', 'css', 'frontend', 'backend', 'api', 'rest', 'graphql', 'website'],
            'data': ['data', 'analysis', 'visualization', 'machine learning', 'ml', 'ai', 'dataset'],
            'mobile': ['mobile', 'android', 'ios', 'react native', 'flutter', 'app'],
            'devops': ['docker', 'kubernetes', 'ci/cd', 'deployment', 'aws', 'azure', 'gcp'],
            'security': ['security', 'authentication', 'authorization', 'encryption', 'vulnerability'],
            'database': ['database', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis']
        }

        # Intent keywords mapping
        self.intent_keywords = {
            'create': ['create', 'build', 'develop', 'implement', 'generate', 'make', 'design'],
            'debug': ['debug', 'fix', 'error', 'bug', 'issue', 'problem', 'troubleshoot'],
            'optimize': ['optimize', 'improve', 'performance', 'speed up', 'enhance', 'refactor'],
            'test': ['test', 'testing', 'unit test', 'integration test', 'validate', 'verify'],
            'document': ['document', 'documentation', 'readme', 'comment', 'explain', 'describe'],
            'review': ['review', 'analyze', 'audit', 'check', 'evaluate', 'assess']
        }

        # Complexity indicators
        self.complexity_indicators = {
            'simple': ['simple', 'basic', 'quick', 'small', 'minimal', 'easy'],
            'medium': ['medium', 'moderate', 'standard', 'typical', 'normal'],
            'complex': ['complex', 'advanced', 'large', 'enterprise', 'scalable', 'distributed', 'microservices']
        }

    def analyze_task(self, task_description: str) -> TaskAnalysis:
        """Analyze a task description and extract key information."""
        task_lower = task_description.lower()

        # Extract domain
        domain = self._extract_domain(task_lower)

        # Extract intent
        intent = self._extract_intent(task_lower)

        # Extract complexity
        complexity = self._extract_complexity(task_lower)

        # Extract keywords
        keywords = self._extract_keywords(task_lower)

        # Calculate confidence based on keyword matches
        confidence = self._calculate_confidence(task_lower, domain, intent, complexity)

        return TaskAnalysis(
            domain=domain,
            complexity=complexity,
            intent=intent,
            keywords=keywords,
            confidence=confidence
        )

    def _extract_domain(self, task_lower: str) -> str:
        """Extract the primary domain from task description."""
        domain_scores = {}

        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in task_lower)
            if score > 0:
                domain_scores[domain] = score

        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        return 'general'

    def _extract_intent(self, task_lower: str) -> str:
        """Extract the primary intent from task description."""
        intent_scores = {}

        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in task_lower)
            if score > 0:
                intent_scores[intent] = score

        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return 'create'  # Default intent

    def _extract_complexity(self, task_lower: str) -> str:
        """Extract complexity level from task description."""
        for complexity, indicators in self.complexity_indicators.items():
            if any(indicator in task_lower for indicator in indicators):
                return complexity

        # Heuristic: longer descriptions tend to be more complex
        word_count = len(task_lower.split())
        if word_count > 20:
            return 'complex'
        elif word_count > 10:
            return 'medium'
        return 'simple'

    def _extract_keywords(self, task_lower: str) -> List[str]:
        """Extract relevant keywords from task description."""
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\b\w+\b', task_lower)
        return [word for word in words if word not in stop_words and len(word) > 2]

    def _calculate_confidence(self, task_lower: str, domain: str, intent: str, complexity: str) -> float:
        """Calculate confidence score for the analysis."""
        confidence = 0.5  # Base confidence

        # Increase confidence based on keyword matches
        if domain != 'general':
            confidence += 0.2

        # Check for specific technical terms
        technical_terms = ['api', 'database', 'algorithm', 'framework', 'library', 'service']
        if any(term in task_lower for term in technical_terms):
            confidence += 0.2

        # Check for clear action words
        if intent in ['create', 'debug', 'optimize']:
            confidence += 0.1

        return min(confidence, 1.0)

class KnowledgeBase:
    """Knowledge base for paradigm and agent mappings."""

    """  Init   with enhanced functionality."""
    def __init__(self):
        self.paradigm_mappings = {
            # Task characteristics -> optimal paradigm
            ('create', 'complex', 'python'): 'orchestra',
            ('create', 'complex', 'javascript'): 'orchestra',
            ('create', 'medium', 'web'): 'mesh',
            ('debug', 'simple', 'general'): 'swarm',
            ('debug', 'complex', 'general'): 'orchestra',
            ('optimize', 'medium', 'general'): 'weaver',
            ('optimize', 'complex', 'general'): 'ecosystem',
            ('document', 'simple', 'general'): 'mesh',
            ('review', 'complex', 'general'): 'weaver',
            ('test', 'medium', 'general'): 'swarm'
        }

        self.agent_capabilities = {
            'gemini': {
                'strengths': ['creative problem-solving', 'multi-modal understanding', 'general reasoning'],
                'domains': ['general', 'python', 'javascript', 'web', 'data'],
                'complexity': ['simple', 'medium', 'complex']
            },
            'claude': {
                'strengths': ['code analysis', 'detailed reasoning', 'safety-focused responses'],
                'domains': ['general', 'python', 'javascript', 'security', 'review'],
                'complexity': ['medium', 'complex']
            },
            'openai': {
                'strengths': ['code generation', 'natural language', 'versatile problem-solving'],
                'domains': ['general', 'python', 'javascript', 'web', 'documentation'],
                'complexity': ['simple', 'medium', 'complex']
            },
            'blackbox': {
                'strengths': ['code-specific tasks', 'programming optimization', 'development tools'],
                'domains': ['python', 'javascript', 'web', 'debugging'],
                'complexity': ['simple', 'medium']
            }
        }

        self.paradigm_descriptions = {
            'orchestra': {
                'name': 'Multi-Agent CLI Orchestra',
                'best_for': 'Complex, multi-faceted tasks requiring structured coordination',
                'agent_count': 3
            },
            'mesh': {
                'name': 'Conversational Code Mesh',
                'best_for': 'Collaborative brainstorming and iterative development',
                'agent_count': 2
            },
            'swarm': {
                'name': 'Autonomous Code Swarm',
                'best_for': 'Parallel problem-solving and emergent solutions',
                'agent_count': 3
            },
            'weaver': {
                'name': 'Contextual Code Weaver',
                'best_for': 'Context-aware integration and business alignment',
                'agent_count': 2
            },
            'ecosystem': {
                'name': 'Emergent Code Ecosystem',
                'best_for': 'Adaptive, evolutionary problem-solving',
                'agent_count': 4
            }
        }

    def get_paradigm_recommendation(self, analysis: TaskAnalysis) -> str:
        """Get paradigm recommendation based on task analysis."""
        # Try exact match first
        key = (analysis.intent, analysis.complexity, analysis.domain)
        if key in self.paradigm_mappings:
            return self.paradigm_mappings[key]

        # Try partial matches
        for (intent, complexity, domain), paradigm in self.paradigm_mappings.items():
            if intent == analysis.intent and complexity == analysis.complexity:
                return paradigm
            elif intent == analysis.intent and domain == analysis.domain:
                return paradigm

        # Default recommendations based on complexity
        if analysis.complexity == 'complex':
            return 'orchestra'
        elif analysis.complexity == 'simple':
            return 'mesh'
        else:
            return 'weaver'

    def get_agent_recommendations(self, analysis: TaskAnalysis, paradigm: str) -> List[str]:
        """Get agent recommendations based on task analysis and paradigm."""
        target_count = self.paradigm_descriptions[paradigm]['agent_count']

        # Score agents based on suitability
        agent_scores = {}
        for agent, capabilities in self.agent_capabilities.items():
            score = 0

            # Domain match
            if analysis.domain in capabilities['domains'] or 'general' in capabilities['domains']:
                score += 3

            # Complexity match
            if analysis.complexity in capabilities['complexity']:
                score += 2

            # Intent-based scoring
            if analysis.intent == 'debug' and 'debugging' in capabilities['domains']:
                score += 2
            elif analysis.intent == 'review' and 'review' in capabilities['domains']:
                score += 2
            elif analysis.intent == 'create' and 'code generation' in capabilities['strengths']:
                score += 2

            agent_scores[agent] = score

        # Select top agents
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        recommended_agents = [agent for agent, score in sorted_agents[:target_count]]

        # Ensure we have at least 2 agents
        if len(recommended_agents) < 2:
            recommended_agents = ['gemini', 'claude']

        return recommended_agents

class RecommendationEngine:
    """Main recommendation engine that coordinates analysis and recommendations."""
    """  Init   with enhanced functionality."""

    def __init__(self):
        self.nlp_analyzer = NLPAnalyzer()
        self.knowledge_base = KnowledgeBase()
        self.performance_metrics = {}  # Store historical performance data

    async def get_recommendation(self, task_description: str, user_preferences: Optional[Dict] = None) -> Recommendation:
        """Get paradigm and agent recommendation for a task."""
        try:
            # Analyze the task
            analysis = self.nlp_analyzer.analyze_task(task_description)

            # Get paradigm recommendation
            paradigm = self.knowledge_base.get_paradigm_recommendation(analysis)

            # Get agent recommendations
            agents = self.knowledge_base.get_agent_recommendations(analysis, paradigm)

            # Apply user preferences if provided
            if user_preferences:
                paradigm, agents = self._apply_user_preferences(paradigm, agents, user_preferences)

            # Generate justification
            justification = self._generate_justification(analysis, paradigm, agents)

            # Estimate duration
            estimated_duration = self._estimate_duration(analysis, paradigm)

            # Calculate overall confidence
            confidence = self._calculate_recommendation_confidence(analysis, paradigm, agents)

            recommendation = Recommendation(
                paradigm=paradigm,
                agents=agents,
                confidence=confidence,
                justification=justification,
                estimated_duration=estimated_duration
            )

            logger.info(f"Generated recommendation for task: {task_description[:50]}...")
            return recommendation

        except Exception as e:
            logger.error(f"Error generating recommendation: {str(e)}")
            # Return default recommendation
            return Recommendation(
                paradigm='mesh',
                agents=['gemini', 'claude'],
                confidence=0.5,
                justification='Default recommendation due to analysis error',
                estimated_duration='5-10 minutes'
            )

    def _apply_user_preferences(self, paradigm: str, agents: List[str], preferences: Dict) -> Tuple[str, List[str]]:
        """Apply user preferences to modify recommendations."""
        # Preferred agents
        if 'preferred_agents' in preferences:
            preferred = preferences['preferred_agents']
            # Try to include preferred agents while maintaining paradigm requirements
            target_count = self.knowledge_base.paradigm_descriptions[paradigm]['agent_count']
            new_agents = []

            # Add preferred agents first
            for agent in preferred:
                if agent in self.knowledge_base.agent_capabilities and len(new_agents) < target_count:
                    new_agents.append(agent)

            # Fill remaining slots with original recommendations
            for agent in agents:
                if agent not in new_agents and len(new_agents) < target_count:
                    new_agents.append(agent)

            agents = new_agents

        # Preferred paradigm
        if 'preferred_paradigm' in preferences:
            preferred_paradigm = preferences['preferred_paradigm']
            if preferred_paradigm in self.knowledge_base.paradigm_descriptions:
                paradigm = preferred_paradigm
                # Adjust agents for new paradigm
                agents = self.knowledge_base.get_agent_recommendations(
                    self.nlp_analyzer.analyze_task(""), paradigm
                )[:self.knowledge_base.paradigm_descriptions[paradigm]['agent_count']]

        return paradigm, agents

    def _generate_justification(self, analysis: TaskAnalysis, paradigm: str, agents: List[str]) -> str:
        """Generate human-readable justification for the recommendation."""
        paradigm_info = self.knowledge_base.paradigm_descriptions[paradigm]

        justification = f"Recommended {paradigm_info['name']} because it's {paradigm_info['best_for']}. "

        if analysis.domain != 'general':
            justification += f"Detected {analysis.domain} domain with {analysis.complexity} complexity. "

        justification += f"Selected {', '.join(agents)} agents for their complementary strengths in "

        agent_strengths = []
        for agent in agents:
            strengths = self.knowledge_base.agent_capabilities[agent]['strengths']
            agent_strengths.extend(strengths[:1])  # Take first strength

        justification += f"{', '.join(agent_strengths)}."

        return justification

    def _estimate_duration(self, analysis: TaskAnalysis, paradigm: str) -> str:
        """Estimate task duration based on complexity and paradigm."""
        base_times = {
            'simple': 5,
            'medium': 15,
            'complex': 30
        }

        paradigm_multipliers = {
            'mesh': 1.0,
            'swarm': 1.2,
            'weaver': 1.3,
            'orchestra': 1.5,
            'ecosystem': 2.0
        }

        base_time = base_times.get(analysis.complexity, 15)
        multiplier = paradigm_multipliers.get(paradigm, 1.0)
        estimated_time = int(base_time * multiplier)

        return f"{estimated_time}-{estimated_time + 10} minutes"

    def _calculate_recommendation_confidence(self, analysis: TaskAnalysis, paradigm: str, agents: List[str]) -> float:
        """Calculate confidence in the recommendation."""
        confidence = analysis.confidence

        # Boost confidence if we have historical success data
        # (This would be implemented with actual performance tracking)

        # Reduce confidence for edge cases
        if analysis.domain == 'general' and analysis.complexity == 'complex':
            confidence *= 0.8

        return min(confidence, 1.0)

    def record_feedback(self, task_description: str, recommendation: Recommendation,
                       user_satisfaction: float, actual_outcome: Dict):
        """Record user feedback to improve future recommendations."""
        # This would store feedback in a database for machine learning
        feedback_record = {
            'timestamp': datetime.now().isoformat(),
            'task_description': task_description,
            'recommendation': recommendation.__dict__,
            'user_satisfaction': user_satisfaction,
            'actual_outcome': actual_outcome
        }

        logger.info(f"Recorded feedback: satisfaction={user_satisfaction}")
        # In a real implementation, this would update ML models

# Global instance
recommendation_engine = RecommendationEngine()

