#!/usr/bin/env python3
"""
Integrated SDLC Orchestrator with A2A Communication
Combines existing orchestrator with Agent-to-Agent capabilities
"""
import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import existing components
from a2a_framework import A2AAgent, A2AOrchestrator, AgentCapability, MessageType
from a2a_knowledge_system import SharedKnowledgeBase, KnowledgeAgent, KnowledgeType
from foundational_improvements import FoundationalOrchestrator

logger = logging.getLogger(__name__)

class EnhancedA2AAgent(A2AAgent, KnowledgeAgent):
    """Agent with both A2A communication and knowledge management"""

    def __init__(self, agent_id: str, name: str, capabilities: List[AgentCapability],
                 """  Init   with enhanced functionality."""
                 knowledge_base: SharedKnowledgeBase, ai_provider=None):
        # Initialize both parent classes
        A2AAgent.__init__(self, agent_id, name, capabilities)
        KnowledgeAgent.__init__(self, agent_id, knowledge_base)

        self.ai_provider = ai_provider
        self.specialization = self._determine_specialization()
        self.collaboration_history: List[Dict[str, Any]] = []

    def _determine_specialization(self) -> str:
        """Determine agent specialization based on capabilities"""
        capability_names = [cap.name for cap in self.capabilities]

        if any('code' in cap for cap in capability_names):
            return 'developer'
        elif any('test' in cap for cap in capability_names):
            return 'tester'
        elif any('design' in cap or 'architecture' in cap for cap in capability_names):
            return 'architect'
        elif any('review' in cap for cap in capability_names):
            return 'reviewer'
        else:
            return 'generalist'

    async def enhanced_generate_response(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response using AI provider with A2A context"""

        # Enrich prompt with relevant knowledge
        relevant_knowledge = await self.discover_knowledge(
            keywords=prompt.split()[:5],  # Use first 5 words as keywords
            knowledge_types=[KnowledgeType.BEST_PRACTICE, KnowledgeType.CODE_PATTERN],
            tags=[self.specialization]
        )

        enhanced_prompt = prompt
        if relevant_knowledge:
            knowledge_context = "\\n".join([
                f"Relevant knowledge: {item.title} - {item.description}"
                for item in relevant_knowledge[:3]
            ])
            enhanced_prompt = f"{prompt}\\n\\nContext from knowledge base:\\n{knowledge_context}"

        # Use AI provider if available
        if self.ai_provider:
            try:
                response = await self.ai_provider.generate_response(enhanced_prompt, context)

                # Learn from successful interactions
                if response.get('success'):
                    await self.learn_from_experience(
                        experience_title=f"Successful response to: {prompt[:50]}",
                        situation=f"Received request: {prompt}",
                        action=f"Generated response using {self.ai_provider.config.name}",
                        result="Successful response generated",
                        lesson="This approach worked well for this type of request",
                        tags=[self.specialization, 'successful_interaction']
                    )

                return response

            except Exception as e:
                logger.error(f"AI provider failed for {self.name}: {e}")

        # Fallback to knowledge-based response
        return await self._knowledge_based_response(prompt, context)

    async def _knowledge_based_response(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response based on knowledge base"""

        # Search for relevant solutions
        solutions = await self.discover_knowledge(
            keywords=prompt.split(),
            knowledge_types=[KnowledgeType.SOLUTION, KnowledgeType.TECHNIQUE],
            tags=[self.specialization]
        )

        if solutions:
            best_solution = solutions[0]  # Highest relevance

            response_content = {
                'suggestion': best_solution.description,
                'source': 'knowledge_base',
                'confidence': best_solution.confidence,
                'details': best_solution.content
            }
        else:
            response_content = {
                'suggestion': f"No specific knowledge found for: {prompt}",
                'source': 'fallback',
                'confidence': 0.3,
                'recommendation': 'Consider consulting with peer agents or adding this to knowledge base'
            }

        return {
            'success': True,
            'response': json.dumps(response_content),
            'provider': f"{self.name} Knowledge Base",
            'method': 'knowledge_based',
            'timestamp': time.time()
        }

    async def collaborate_on_task(self, task: Dict[str, Any], peer_ids: List[str]) -> Dict[str, Any]:
        """Collaborate with peer agents on a specific task"""

        task_id = task.get('id', str(time.time()))
        task_description = task.get('description', '')

        logger.info(f"Agent {self.name} starting collaboration on task: {task_description}")

        # Step 1: Analyze task and identify required capabilities
        required_capabilities = task.get('required_capabilities', [])
        my_relevant_capabilities = [
            cap.name for cap in self.capabilities
            if any(req in cap.name for req in required_capabilities)
        ]

        # Step 2: Discover relevant knowledge
        task_knowledge = await self.discover_knowledge(
            keywords=task_description.split(),
            knowledge_types=[KnowledgeType.SOLUTION, KnowledgeType.BEST_PRACTICE],
            tags=required_capabilities
        )

        # Step 3: Share knowledge with peers
        for peer_id in peer_ids:
            if task_knowledge:
                best_knowledge = task_knowledge[0]
                await self.send_message(
                    receiver_id=peer_id,
                    message_type=MessageType.KNOWLEDGE_SHARE,
                    content={
                        'task_id': task_id,
                        'knowledge_item': {
                            'title': best_knowledge.title,
                            'description': best_knowledge.description,
                            'content': best_knowledge.content
                        },
                        'my_capabilities': my_relevant_capabilities
                    }
                )

        # Step 4: Request collaboration
        collaboration_id = await self.propose_collaboration(
            peer_ids=peer_ids,
            goal=f"Complete task: {task_description}",
            shared_context={
                'task': task,
                'my_capabilities': my_relevant_capabilities,
                'available_knowledge': len(task_knowledge)
            }
        )

        # Step 5: Execute my part of the task
        my_contribution = await self._execute_task_part(task, my_relevant_capabilities)

        # Step 6: Record collaboration outcome
        collaboration_result = {
            'collaboration_id': collaboration_id,
            'task_id': task_id,
            'my_contribution': my_contribution,
            'peers_involved': peer_ids,
            'knowledge_used': len(task_knowledge),
            'timestamp': time.time()
        }

        self.collaboration_history.append(collaboration_result)

        # Step 7: Learn from this collaboration
        await self.learn_from_experience(
            experience_title=f"Collaboration on {task_description}",
            situation=f"Asked to collaborate on task with {len(peer_ids)} peers",
            action=f"Applied {len(my_relevant_capabilities)} capabilities and shared knowledge",
            result=f"Contributed: {my_contribution.get('status', 'unknown')}",
            lesson="Collaboration improved task outcome through knowledge sharing",
            tags=['collaboration', 'teamwork', self.specialization]
        )

        return collaboration_result

    async def _execute_task_part(self, task: Dict[str, Any], relevant_capabilities: List[str]) -> Dict[str, Any]:
        """Execute the agent's part of the task"""

        if not relevant_capabilities:
            return {
                'status': 'no_relevant_capabilities',
                'message': 'No relevant capabilities for this task'
            }

        # Simulate task execution based on capabilities
        primary_capability = relevant_capabilities[0]

        # Generate task-specific response
        task_prompt = f"Execute {primary_capability} for task: {task.get('description', '')}"
        response = await self.enhanced_generate_response(task_prompt, {'task': task})

        return {
            'status': 'completed',
            'capability_used': primary_capability,
            'response': response,
            'confidence': response.get('confidence', 0.7)
        }

class IntegratedSDLCOrchestrator:
    """Integrated SDLC Orchestrator with A2A communication"""

    """  Init   with enhanced functionality."""
    def __init__(self):
        self.foundational_orchestrator = FoundationalOrchestrator()
        self.a2a_orchestrator = A2AOrchestrator()
        self.knowledge_base = SharedKnowledgeBase()
        self.enhanced_agents: Dict[str, EnhancedA2AAgent] = {}
        self.active_collaborations: Dict[str, Dict[str, Any]] = {}

    async def initialize(self):
        """Initialize the integrated orchestrator"""

        await self.foundational_orchestrator.initialize()
        await self.a2a_orchestrator.start()

        # Create enhanced agents
        await self._create_enhanced_agents()

        logger.info("Integrated SDLC Orchestrator initialized")

    async def _create_enhanced_agents(self):
        """Create enhanced agents with A2A and knowledge capabilities"""

        # Developer Agent
        dev_capabilities = [
            AgentCapability("code_generation", "Generate code", ["requirements"], ["code"], 0.9, ["python", "javascript"]),
            AgentCapability("code_refactoring", "Refactor code", ["code"], ["improved_code"], 0.8, ["optimization"]),
            AgentCapability("api_design", "Design APIs", ["requirements"], ["api_spec"], 0.85, ["rest", "graphql"])
        ]

        dev_agent = EnhancedA2AAgent(
            "enhanced_dev_001",
            "Enhanced Developer",
            dev_capabilities,
            self.knowledge_base,
            self.foundational_orchestrator.ai_providers.get('openai')
        )

        # Testing Agent
        test_capabilities = [
            AgentCapability("test_generation", "Generate tests", ["code"], ["tests"], 0.9, ["unit", "integration"]),
            AgentCapability("test_automation", "Automate testing", ["tests"], ["test_suite"], 0.85, ["ci_cd"]),
            AgentCapability("bug_detection", "Detect bugs", ["code"], ["bug_report"], 0.8, ["static_analysis"])
        ]

        test_agent = EnhancedA2AAgent(
            "enhanced_test_001",
            "Enhanced Tester",
            test_capabilities,
            self.knowledge_base,
            self.foundational_orchestrator.ai_providers.get('anthropic')
        )

        # Architecture Agent
        arch_capabilities = [
            AgentCapability("system_design", "Design system architecture", ["requirements"], ["architecture"], 0.9, ["microservices"]),
            AgentCapability("performance_optimization", "Optimize performance", ["system"], ["optimizations"], 0.85, ["scalability"]),
            AgentCapability("security_review", "Review security", ["design"], ["security_assessment"], 0.8, ["security"])
        ]

        arch_agent = EnhancedA2AAgent(
            "enhanced_arch_001",
            "Enhanced Architect",
            arch_capabilities,
            self.knowledge_base,
            self.foundational_orchestrator.ai_providers.get('gemini')
        )

        # Register agents
        agents = [dev_agent, test_agent, arch_agent]
        for agent in agents:
            self.enhanced_agents[agent.agent_id] = agent
            self.a2a_orchestrator.register_agent(agent)
            await agent.start()

        logger.info(f"Created {len(agents)} enhanced agents")

    async def execute_complex_task(self, task_description: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complex task using A2A collaboration"""

        task = {
            'id': f"task_{int(time.time())}",
            'description': task_description,
            'requirements': requirements,
            'required_capabilities': self._analyze_required_capabilities(task_description, requirements)
        }

        logger.info(f"Executing complex task: {task_description}")

        # Step 1: Identify suitable agents
        suitable_agents = self._find_suitable_agents(task['required_capabilities'])

        if len(suitable_agents) < 2:
            # Fallback to single agent or foundational orchestrator
            return await self._fallback_execution(task)

        # Step 2: Initiate A2A collaboration
        coordinator_agent = suitable_agents[0]
        peer_agents = suitable_agents[1:]

        # Step 3: Execute collaborative task
        collaboration_results = []

        # Coordinator starts the collaboration
        coordinator_result = await coordinator_agent.collaborate_on_task(
            task=task,
            peer_ids=[agent.agent_id for agent in peer_agents]
        )
        collaboration_results.append(coordinator_result)

        # Wait for peer collaborations
        await asyncio.sleep(2)  # Allow time for A2A message processing

        # Step 4: Collect peer contributions
        for peer_agent in peer_agents:
            peer_result = await peer_agent.collaborate_on_task(
                task=task,
                peer_ids=[coordinator_agent.agent_id]
            )
            collaboration_results.append(peer_result)

        # Step 5: Synthesize results
        final_result = await self._synthesize_collaboration_results(task, collaboration_results)

        # Step 6: Record collaboration in knowledge base
        await self._record_collaboration_knowledge(task, collaboration_results, final_result)

        return final_result

    def _analyze_required_capabilities(self, task_description: str, requirements: Dict[str, Any]) -> List[str]:
        """Analyze task to determine required capabilities"""

        required_capabilities = []

        # Keyword-based analysis (simplified)
        if any(keyword in task_description.lower() for keyword in ['code', 'implement', 'develop']):
            required_capabilities.append('code_generation')

        if any(keyword in task_description.lower() for keyword in ['test', 'verify', 'validate']):
            required_capabilities.append('test_generation')

        if any(keyword in task_description.lower() for keyword in ['design', 'architecture', 'system']):
            required_capabilities.append('system_design')

        if any(keyword in task_description.lower() for keyword in ['review', 'analyze', 'audit']):
            required_capabilities.append('code_review')

        # Add capabilities from requirements
        if 'performance' in requirements:
            required_capabilities.append('performance_optimization')

        if 'security' in requirements:
            required_capabilities.append('security_review')

        return required_capabilities or ['code_generation']  # Default capability

    def _find_suitable_agents(self, required_capabilities: List[str]) -> List[EnhancedA2AAgent]:
        """Find agents suitable for the required capabilities"""

        suitable_agents = []

        for agent in self.enhanced_agents.values():
            agent_capabilities = [cap.name for cap in agent.capabilities]

            # Check if agent has any required capability
            if any(req_cap in agent_capabilities for req_cap in required_capabilities):
                suitable_agents.append(agent)

        # Sort by capability match count
        suitable_agents.sort(
            key=lambda agent: len(set([cap.name for cap in agent.capabilities]) & set(required_capabilities)),
            reverse=True
        )

        return suitable_agents

    async def _fallback_execution(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to foundational orchestrator"""

        logger.info("Falling back to foundational orchestrator")

        return await self.foundational_orchestrator.collaborate(
            session_id=task['id'],
            paradigm='orchestra',
            task=task['description'],
            agents=['openai', 'anthropic'],
            context=task.get('requirements', {})
        )

    async def _synthesize_collaboration_results(self, task: Dict[str, Any],
                                              collaboration_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize results from multiple agent collaborations"""

        successful_contributions = [
            result for result in collaboration_results
            if result.get('my_contribution', {}).get('status') == 'completed'
        ]

        # Combine contributions
        combined_output = {
            'task_id': task['id'],
            'task_description': task['description'],
            'collaboration_method': 'a2a_integrated',
            'total_agents': len(collaboration_results),
            'successful_contributions': len(successful_contributions),
            'contributions': [],
            'knowledge_items_used': 0,
            'synthesis': {},
            'success': len(successful_contributions) > 0,
            'timestamp': time.time()
        }

        for result in successful_contributions:
            contribution = result.get('my_contribution', {})
            combined_output['contributions'].append({
                'agent_id': result.get('collaboration_id', 'unknown'),
                'capability': contribution.get('capability_used'),
                'confidence': contribution.get('confidence', 0),
                'response': contribution.get('response', {})
            })

            combined_output['knowledge_items_used'] += result.get('knowledge_used', 0)

        # Create synthesis
        if successful_contributions:
            avg_confidence = sum(
                contrib.get('my_contribution', {}).get('confidence', 0)
                for contrib in successful_contributions
            ) / len(successful_contributions)

            combined_output['synthesis'] = {
                'quality': 'high' if avg_confidence > 0.8 else 'medium' if avg_confidence > 0.6 else 'low',
                'average_confidence': avg_confidence,
                'collaboration_effectiveness': len(successful_contributions) / len(collaboration_results),
                'knowledge_leverage': combined_output['knowledge_items_used'] > 0
            }

        return combined_output

    async def _record_collaboration_knowledge(self, task: Dict[str, Any],
                                            collaboration_results: List[Dict[str, Any]],
                                            final_result: Dict[str, Any]):
        """Record collaboration knowledge for future use"""

        # Record successful collaboration pattern
        if final_result.get('success') and len(collaboration_results) > 1:

            # Find a suitable agent to record the knowledge
            recorder_agent = list(self.enhanced_agents.values())[0]

            await recorder_agent.contribute_knowledge(
                title=f"Successful A2A Collaboration: {task['description'][:50]}",
                description=f"Multi-agent collaboration that successfully completed: {task['description']}",
                knowledge_type=KnowledgeType.WORKFLOW,
                content={
                    'task_type': task['description'],
                    'required_capabilities': task.get('required_capabilities', []),
                    'agents_involved': len(collaboration_results),
                    'success_rate': final_result['synthesis']['collaboration_effectiveness'],
                    'average_confidence': final_result['synthesis']['average_confidence'],
                    'pattern': 'a2a_collaboration'
                },
                tags=['collaboration', 'workflow', 'a2a', 'successful']
            )

    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status"""

        # Get foundational orchestrator health
        foundational_health = await self.foundational_orchestrator.health_check()

        # Get A2A network status
        a2a_status = self.a2a_orchestrator.get_network_status()

        # Get knowledge base stats
        knowledge_stats = self.knowledge_base.get_knowledge_stats()

        # Get enhanced agents status
        enhanced_agents_status = {}
        for agent_id, agent in self.enhanced_agents.items():
            enhanced_agents_status[agent_id] = {
                **agent.get_status(),
                'specialization': agent.specialization,
                'collaboration_history': len(agent.collaboration_history),
                'knowledge_contributions': len(agent.get_knowledge_contributions())
            }

        return {
            'integration_status': 'active',
            'foundational_orchestrator': foundational_health,
            'a2a_network': a2a_status,
            'knowledge_base': knowledge_stats,
            'enhanced_agents': enhanced_agents_status,
            'active_collaborations': len(self.active_collaborations),
            'timestamp': time.time()
        }

    async def close(self):
        """Close the integrated orchestrator"""

        # Stop enhanced agents
        for agent in self.enhanced_agents.values():
            await agent.stop()

        # Stop orchestrators
        await self.a2a_orchestrator.stop()
        await self.foundational_orchestrator.close()

        logger.info("Integrated SDLC Orchestrator closed")

# Example usage and testing
async def demo_integrated_orchestrator():
    """Demonstrate the integrated orchestrator"""
    logger.info("🚀 Integrated A2A SDLC Orchestrator Demo")
    logger.info("=" * 60)

    # Create and initialize orchestrator
    orchestrator = IntegratedSDLCOrchestrator()

    try:
        await orchestrator.initialize()
        logger.info("✅ Integrated orchestrator initialized")

        # Test 1: Complex task execution
        logger.info("\\n🔧 Test 1: Complex Task Execution")

        result = await orchestrator.execute_complex_task(
            task_description="Design and implement a secure user authentication system with testing",
            requirements={
                'security': 'high',
                'performance': 'medium',
                'testing': 'comprehensive',
                'language': 'python'
            }
        )

        logger.info(f"Task Result:")
        logger.info(f"  Success: {result['success']}")
        logger.info(f"  Agents involved: {result['total_agents']}")
        logger.info(f"  Successful contributions: {result['successful_contributions']}")
        logger.info(f"  Quality: {result['synthesis']['quality']}")
        logger.info(f"  Knowledge items used: {result['knowledge_items_used']}")

        # Test 2: Orchestrator status
        logger.info("\\n📊 Test 2: Orchestrator Status")

        status = await orchestrator.get_orchestrator_status()
        logger.info(f"Integration Status: {status['integration_status']}")
        logger.info(f"Enhanced Agents: {len(status['enhanced_agents'])}")
        logger.info(f"Knowledge Base Items: {status['knowledge_base']['total_items']}")
        logger.info(f"A2A Network Agents: {status['a2a_network']['total_agents']}")

        # Test 3: Agent specializations
        logger.info("\\n🎯 Test 3: Agent Specializations")
        for agent_id, agent_status in status['enhanced_agents'].items():
            print(f"  {agent_status['name']}: {agent_status['specialization']} "
                  f"({agent_status['capabilities_count']} capabilities)")

        logger.info("\\n✅ Integrated A2A SDLC Orchestrator Demo Complete!")

    finally:
        await orchestrator.close()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Run demo
    asyncio.run(demo_integrated_orchestrator())
