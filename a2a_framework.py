#!/usr/bin/env python3
"""
Agent-to-Agent (A2A) Communication Framework
Enables direct communication and collaboration between AI agents
"""
import asyncio
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of A2A messages"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    PROPOSAL = "proposal"
    ACCEPTANCE = "acceptance"
    REJECTION = "rejection"
    DELEGATION = "delegation"
    COMPLETION = "completion"
    QUESTION = "question"
    ANSWER = "answer"
    COLLABORATION_INVITE = "collaboration_invite"
    KNOWLEDGE_SHARE = "knowledge_share"

class AgentRole(Enum):
    """Agent roles in A2A communication"""
    INITIATOR = "initiator"
    RESPONDER = "responder"
    MEDIATOR = "mediator"
    OBSERVER = "observer"
    COORDINATOR = "coordinator"

@dataclass
class A2AMessage:
    """Agent-to-Agent message structure"""
    id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: float
    conversation_id: str
    priority: int = 1  # 1=low, 5=high
    requires_response: bool = False
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AgentCapability:
    """Agent capability description"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    confidence: float
    specializations: List[str]

@dataclass
class CollaborationSession:
    """A2A collaboration session"""
    id: str
    participants: List[str]
    goal: str
    status: str
    created_at: float
    messages: List[A2AMessage]
    shared_context: Dict[str, Any]
    outcomes: List[Dict[str, Any]]

class A2AAgent:
    """Enhanced agent with A2A communication capabilities"""

    def __init__(self, agent_id: str, name: str, capabilities: List[AgentCapability]):
        """  Init   with enhanced functionality."""
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.active_conversations: Dict[str, CollaborationSession] = {}
        self.knowledge_base: Dict[str, Any] = {}
        self.peers: Dict[str, 'A2AAgent'] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False

        # Register default message handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default message handlers"""
        self.message_handlers[MessageType.REQUEST] = self._handle_request
        self.message_handlers[MessageType.RESPONSE] = self._handle_response
        self.message_handlers[MessageType.PROPOSAL] = self._handle_proposal
        self.message_handlers[MessageType.QUESTION] = self._handle_question
        self.message_handlers[MessageType.KNOWLEDGE_SHARE] = self._handle_knowledge_share
        self.message_handlers[MessageType.COLLABORATION_INVITE] = self._handle_collaboration_invite

    async def start(self):
        """Start the agent's message processing loop"""
        self.running = True
        asyncio.create_task(self._message_processing_loop())
        logger.info(f"Agent {self.name} started A2A communication")

    async def stop(self):
        """Stop the agent's message processing"""
        self.running = False
        logger.info(f"Agent {self.name} stopped A2A communication")

    async def _message_processing_loop(self):
        """Main message processing loop"""
        while self.running:
            try:
                # Process messages with timeout
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self._process_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Agent {self.name} message processing error: {e}")

    async def _process_message(self, message: A2AMessage):
        """Process incoming A2A message"""
        logger.info(f"Agent {self.name} processing {message.message_type.value} from {message.sender_id}")

        # Find appropriate handler
        handler = self.message_handlers.get(message.message_type)
        if handler:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Message handler error in {self.name}: {e}")
                # Send error response if required
                if message.requires_response:
                    await self._send_error_response(message, str(e))
        else:
            logger.warning(f"No handler for {message.message_type.value} in agent {self.name}")

    async def send_message(self, receiver_id: str, message_type: MessageType,
                          content: Dict[str, Any], requires_response: bool = False,
                          conversation_id: str = None) -> A2AMessage:
        """Send message to another agent"""

        message = A2AMessage(
            id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            timestamp=time.time(),
            conversation_id=conversation_id or str(uuid.uuid4()),
            requires_response=requires_response
        )

        # Send to peer agent
        if receiver_id in self.peers:
            await self.peers[receiver_id].receive_message(message)
            logger.info(f"Agent {self.name} sent {message_type.value} to {receiver_id}")
        else:
            logger.error(f"Agent {receiver_id} not found in peers of {self.name}")

        return message

    async def receive_message(self, message: A2AMessage):
        """Receive message from another agent"""
        await self.message_queue.put(message)

    async def request_capability(self, receiver_id: str, capability_name: str,
                               input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Request a specific capability from another agent"""

        request_content = {
            'capability': capability_name,
            'input_data': input_data,
            'requester_capabilities': [cap.name for cap in self.capabilities]
        }

        message = await self.send_message(
            receiver_id=receiver_id,
            message_type=MessageType.REQUEST,
            content=request_content,
            requires_response=True
        )

        # Wait for response (simplified - in production, use proper response tracking)
        await asyncio.sleep(1)  # Simulate processing time

        return {"status": "completed", "message_id": message.id}

    async def propose_collaboration(self, peer_ids: List[str], goal: str,
                                  shared_context: Dict[str, Any]) -> str:
        """Propose collaboration with multiple agents"""

        collaboration_id = str(uuid.uuid4())

        proposal_content = {
            'collaboration_id': collaboration_id,
            'goal': goal,
            'shared_context': shared_context,
            'proposed_participants': peer_ids,
            'initiator_capabilities': [cap.name for cap in self.capabilities]
        }

        # Send collaboration invites to all peers
        for peer_id in peer_ids:
            await self.send_message(
                receiver_id=peer_id,
                message_type=MessageType.COLLABORATION_INVITE,
                content=proposal_content,
                requires_response=True,
                conversation_id=collaboration_id
            )

        # Create collaboration session
        session = CollaborationSession(
            id=collaboration_id,
            participants=[self.agent_id] + peer_ids,
            goal=goal,
            status="proposed",
            created_at=time.time(),
            messages=[],
            shared_context=shared_context,
            outcomes=[]
        )

        self.active_conversations[collaboration_id] = session

        logger.info(f"Agent {self.name} proposed collaboration {collaboration_id}")
        return collaboration_id

    async def share_knowledge(self, receiver_id: str, knowledge_key: str,
                            knowledge_data: Any):
        """Share knowledge with another agent"""

        knowledge_content = {
            'knowledge_key': knowledge_key,
            'knowledge_data': knowledge_data,
            'source_agent': self.agent_id,
            'confidence': 0.8,  # Default confidence
            'timestamp': time.time()
        }

        await self.send_message(
            receiver_id=receiver_id,
            message_type=MessageType.KNOWLEDGE_SHARE,
            content=knowledge_content
        )

    async def negotiate_task_allocation(self, peer_ids: List[str],
                                      tasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Negotiate task allocation among agents"""

        # Analyze own capabilities for each task
        capability_matrix = {}
        for task in tasks:
            task_id = task['id']
            required_capabilities = task.get('required_capabilities', [])

            # Calculate compatibility score
            my_capabilities = [cap.name for cap in self.capabilities]
            compatibility = len(set(required_capabilities) & set(my_capabilities)) / max(len(required_capabilities), 1)

            capability_matrix[task_id] = {
                'compatibility': compatibility,
                'estimated_effort': task.get('complexity', 1),
                'can_handle': compatibility > 0.5
            }

        # Send negotiation proposals to peers
        negotiation_content = {
            'tasks': tasks,
            'my_capabilities': capability_matrix,
            'agent_id': self.agent_id
        }

        for peer_id in peer_ids:
            await self.send_message(
                receiver_id=peer_id,
                message_type=MessageType.PROPOSAL,
                content=negotiation_content,
                requires_response=True
            )

        # Simplified allocation (in production, implement proper negotiation)
        allocation = {self.agent_id: []}
        for task in tasks:
            if capability_matrix[task['id']]['can_handle']:
                allocation[self.agent_id].append(task['id'])

        return allocation

    # Message Handlers
    async def _handle_request(self, message: A2AMessage):
        """Handle capability request"""
        content = message.content
        capability_name = content.get('capability')
        input_data = content.get('input_data', {})

        # Check if we have the requested capability
        has_capability = any(cap.name == capability_name for cap in self.capabilities)

        if has_capability:
            # Simulate capability execution
            result = {
                'success': True,
                'result': f"Executed {capability_name} with data: {input_data}",
                'agent': self.name,
                'timestamp': time.time()
            }
        else:
            result = {
                'success': False,
                'error': f"Capability {capability_name} not available",
                'available_capabilities': [cap.name for cap in self.capabilities]
            }

        # Send response
        if message.requires_response:
            await self.send_message(
                receiver_id=message.sender_id,
                message_type=MessageType.RESPONSE,
                content=result,
                conversation_id=message.conversation_id
            )

    async def _handle_response(self, message: A2AMessage):
        """Handle response message"""
        logger.info(f"Agent {self.name} received response: {message.content.get('success', 'unknown')}")

    async def _handle_proposal(self, message: A2AMessage):
        """Handle negotiation proposal"""
        content = message.content
        tasks = content.get('tasks', [])

        # Analyze proposal and send acceptance/rejection
        response_type = MessageType.ACCEPTANCE if len(tasks) > 0 else MessageType.REJECTION

        response_content = {
            'proposal_id': message.id,
            'decision': response_type.value,
            'reasoning': f"Agent {self.name} can handle {len(tasks)} tasks"
        }

        await self.send_message(
            receiver_id=message.sender_id,
            message_type=response_type,
            content=response_content,
            conversation_id=message.conversation_id
        )

    async def _handle_question(self, message: A2AMessage):
        """Handle question from another agent"""
        content = message.content
        question = content.get('question', '')

        # Generate answer based on knowledge base or capabilities
        answer = f"Agent {self.name} response to: {question}"

        if message.requires_response:
            await self.send_message(
                receiver_id=message.sender_id,
                message_type=MessageType.ANSWER,
                content={'answer': answer, 'confidence': 0.7},
                conversation_id=message.conversation_id
            )

    async def _handle_knowledge_share(self, message: A2AMessage):
        """Handle knowledge sharing"""
        content = message.content
        knowledge_key = content.get('knowledge_key')
        knowledge_data = content.get('knowledge_data')

        # Store in knowledge base
        self.knowledge_base[knowledge_key] = {
            'data': knowledge_data,
            'source': content.get('source_agent'),
            'timestamp': content.get('timestamp'),
            'confidence': content.get('confidence', 0.5)
        }

        logger.info(f"Agent {self.name} received knowledge: {knowledge_key}")

    async def _handle_collaboration_invite(self, message: A2AMessage):
        """Handle collaboration invitation"""
        content = message.content
        collaboration_id = content.get('collaboration_id')
        goal = content.get('goal')

        # Decide whether to accept collaboration
        accept = True  # Simplified decision logic

        response_type = MessageType.ACCEPTANCE if accept else MessageType.REJECTION
        response_content = {
            'collaboration_id': collaboration_id,
            'decision': response_type.value,
            'my_capabilities': [cap.name for cap in self.capabilities]
        }

        await self.send_message(
            receiver_id=message.sender_id,
            message_type=response_type,
            content=response_content,
            conversation_id=collaboration_id
        )

        if accept:
            # Create local collaboration session
            session = CollaborationSession(
                id=collaboration_id,
                participants=content.get('proposed_participants', []),
                goal=goal,
                status="accepted",
                created_at=time.time(),
                messages=[],
                shared_context=content.get('shared_context', {}),
                outcomes=[]
            )
            self.active_conversations[collaboration_id] = session

    async def _send_error_response(self, original_message: A2AMessage, error: str):
        """Send error response"""
        await self.send_message(
            receiver_id=original_message.sender_id,
            message_type=MessageType.RESPONSE,
            content={'success': False, 'error': error},
            conversation_id=original_message.conversation_id
        )

    def get_status(self) -> Dict[str, Any]:
        """Get agent status for monitoring"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'running': self.running,
            'capabilities_count': len(self.capabilities),
            'active_conversations': len(self.active_conversations),
            'peers_connected': len(self.peers),
            'knowledge_items': len(self.knowledge_base),
            'message_queue_size': self.message_queue.qsize()
        }

class A2AOrchestrator:
    """Orchestrator for Agent-to-Agent communications"""

    """  Init   with enhanced functionality."""
    def __init__(self):
        self.agents: Dict[str, A2AAgent] = {}
        self.message_log: List[A2AMessage] = []
        self.collaboration_sessions: Dict[str, CollaborationSession] = {}
        self.running = False

    async def start(self):
        """Start the A2A orchestrator"""
        self.running = True

        # Start all agents
        for agent in self.agents.values():
            await agent.start()

        logger.info("A2A Orchestrator started")

    async def stop(self):
        """Stop the A2A orchestrator"""
        self.running = False

        # Stop all agents
        for agent in self.agents.values():
            await agent.stop()

        logger.info("A2A Orchestrator stopped")

    def register_agent(self, agent: A2AAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.agent_id] = agent

        # Connect agent to all existing agents
        for existing_agent in self.agents.values():
            if existing_agent.agent_id != agent.agent_id:
                agent.peers[existing_agent.agent_id] = existing_agent
                existing_agent.peers[agent.agent_id] = agent

        logger.info(f"Registered agent {agent.name} with {len(agent.peers)} peers")

    async def initiate_multi_agent_collaboration(self, goal: str, required_capabilities: List[str]) -> str:
        """Initiate collaboration between multiple agents"""

        # Find suitable agents based on capabilities
        suitable_agents = []
        for agent in self.agents.values():
            agent_capabilities = [cap.name for cap in agent.capabilities]
            if any(cap in agent_capabilities for cap in required_capabilities):
                suitable_agents.append(agent.agent_id)

        if len(suitable_agents) < 2:
            raise ValueError("Not enough suitable agents for collaboration")

        # Select coordinator (first suitable agent)
        coordinator_id = suitable_agents[0]
        participant_ids = suitable_agents[1:]

        # Start collaboration
        coordinator = self.agents[coordinator_id]
        collaboration_id = await coordinator.propose_collaboration(
            peer_ids=participant_ids,
            goal=goal,
            shared_context={'required_capabilities': required_capabilities}
        )

        return collaboration_id

    async def facilitate_knowledge_exchange(self, source_agent_id: str, target_agent_ids: List[str]):
        """Facilitate knowledge exchange between agents"""

        source_agent = self.agents.get(source_agent_id)
        if not source_agent:
            raise ValueError(f"Source agent {source_agent_id} not found")

        # Share knowledge from source to targets
        for target_id in target_agent_ids:
            for knowledge_key, knowledge_item in source_agent.knowledge_base.items():
                await source_agent.share_knowledge(
                    receiver_id=target_id,
                    knowledge_key=knowledge_key,
                    knowledge_data=knowledge_item['data']
                )

    def get_network_status(self) -> Dict[str, Any]:
        """Get overall network status"""
        total_messages = len(self.message_log)
        active_collaborations = len([s for s in self.collaboration_sessions.values() if s.status == 'active'])

        agent_statuses = {}
        for agent_id, agent in self.agents.items():
            agent_statuses[agent_id] = agent.get_status()

        return {
            'orchestrator_running': self.running,
            'total_agents': len(self.agents),
            'total_messages': total_messages,
            'active_collaborations': active_collaborations,
            'agent_statuses': agent_statuses,
            'timestamp': time.time()
        }

# Example usage and testing
async def demo_a2a_communication():
    """Demonstrate A2A communication"""
    logger.info("Agent-to-Agent Communication Demo")
    logger.info("=" * 50)

    # Create orchestrator
    orchestrator = A2AOrchestrator()

    # Create agents with different capabilities
    coding_capabilities = [
        AgentCapability("code_generation", "Generate code", ["requirements"], ["code"], 0.9, ["python", "javascript"]),
        AgentCapability("code_review", "Review code quality", ["code"], ["feedback"], 0.8, ["best_practices"])
    ]

    testing_capabilities = [
        AgentCapability("test_generation", "Generate test cases", ["code"], ["tests"], 0.85, ["unit_testing"]),
        AgentCapability("bug_detection", "Detect bugs", ["code"], ["issues"], 0.7, ["static_analysis"])
    ]

    design_capabilities = [
        AgentCapability("architecture_design", "Design system architecture", ["requirements"], ["design"], 0.9, ["microservices"]),
        AgentCapability("ui_design", "Design user interfaces", ["requirements"], ["mockups"], 0.8, ["web", "mobile"])
    ]

    # Create agents
    coder_agent = A2AAgent("coder_001", "CodeMaster", coding_capabilities)
    tester_agent = A2AAgent("tester_001", "TestGuardian", testing_capabilities)
    designer_agent = A2AAgent("designer_001", "ArchitectAI", design_capabilities)

    # Register agents
    orchestrator.register_agent(coder_agent)
    orchestrator.register_agent(tester_agent)
    orchestrator.register_agent(designer_agent)

    # Start orchestrator
    await orchestrator.start()

    logger.info(f"✅ Started A2A network with {len(orchestrator.agents)} agents")

    # Demo 1: Direct agent communication
    logger.info("\n🔗 Demo 1: Direct Agent Communication")
    await coder_agent.request_capability(
        receiver_id="tester_001",
        capability_name="test_generation",
        input_data={"code": "def hello(): return 'Hello World'"}
    )

    # Demo 2: Knowledge sharing
    logger.info("\n📚 Demo 2: Knowledge Sharing")
    await designer_agent.share_knowledge(
        receiver_id="coder_001",
        knowledge_key="best_practices",
        knowledge_data={"pattern": "singleton", "use_case": "database connections"}
    )

    # Demo 3: Multi-agent collaboration
    logger.info("\n🤝 Demo 3: Multi-Agent Collaboration")
    collaboration_id = await orchestrator.initiate_multi_agent_collaboration(
        goal="Build a web application with authentication",
        required_capabilities=["code_generation", "test_generation", "architecture_design"]
    )
    logger.info(f"Started collaboration: {collaboration_id}")

    # Demo 4: Knowledge exchange
    logger.info("\n🔄 Demo 4: Knowledge Exchange")
    await orchestrator.facilitate_knowledge_exchange(
        source_agent_id="designer_001",
        target_agent_ids=["coder_001", "tester_001"]
    )

    # Wait for message processing
    await asyncio.sleep(2)

    # Show network status
    logger.info("\n📊 Network Status:")
    status = orchestrator.get_network_status()
    for agent_id, agent_status in status['agent_statuses'].items():
        logger.info(f"  {agent_status['name']}: {agent_status['active_conversations']} active conversations")

    # Stop orchestrator
    await orchestrator.stop()
    logger.info("\n✅ A2A Communication Demo Complete")

if __name__ == "__main__":
    asyncio.run(demo_a2a_communication())
