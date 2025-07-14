#!/usr/bin/env python3
"""
Robust A2A Communication Framework with Consensus Mechanisms
"""
import json
import asyncio
import time
import uuid
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import aiohttp
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """A2A Message types"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    COLLABORATION_INVITE = "collaboration_invite"
    CONSENSUS_VOTE = "consensus_vote"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    HEARTBEAT = "heartbeat"
    DISCOVERY = "discovery"

class AgentRole(Enum):
    """Agent roles in the A2A network"""
    COORDINATOR = "coordinator"
    PLANNER = "planner"
    CODER = "coder"
    REVIEWER = "reviewer"
    TESTER = "tester"
    SPECIALIST = "specialist"

class ConsensusType(Enum):
    """Types of consensus mechanisms"""
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_CONSENSUS = "weighted_consensus"
    EXPERT_VALIDATION = "expert_validation"
    ITERATIVE_REFINEMENT = "iterative_refinement"

@dataclass
class A2AMessage:
    """A2A Communication message structure"""
    id: str
    type: MessageType
    sender_id: str
    receiver_id: Optional[str]
    timestamp: float
    payload: Dict[str, Any]
    context: Dict[str, Any]
    priority: int = 5  # 1-10, 10 being highest
    requires_response: bool = False
    expires_at: Optional[float] = None

@dataclass
class AgentCapability:
    """Agent capability definition"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    confidence: float  # 0-1
    latency_estimate: float  # seconds
    cost_estimate: float  # relative cost

@dataclass
class AgentProfile:
    """Complete agent profile for A2A network"""
    id: str
    name: str
    role: AgentRole
    model_id: str
    capabilities: List[AgentCapability]
    status: str
    last_seen: float
    performance_metrics: Dict[str, float]
    trust_score: float  # 0-1
    collaboration_history: Dict[str, Any]

class ConsensusEngine:
    """Handles consensus mechanisms between agents"""
    
    def __init__(self):
        self.active_consensus = {}
        self.consensus_history = []
        
    async def initiate_consensus(self, 
                               topic: str,
                               participants: List[str],
                               consensus_type: ConsensusType,
                               data: Dict[str, Any],
                               timeout: float = 30.0) -> str:
        """Initiate consensus process"""
        consensus_id = str(uuid.uuid4())
        
        self.active_consensus[consensus_id] = {
            "id": consensus_id,
            "topic": topic,
            "participants": participants,
            "type": consensus_type,
            "data": data,
            "votes": {},
            "started_at": time.time(),
            "timeout": timeout,
            "status": "pending"
        }
        
        logger.info(f"Initiated consensus {consensus_id} for topic: {topic}")
        return consensus_id
        
    async def submit_vote(self, 
                         consensus_id: str,
                         agent_id: str,
                         vote_data: Dict[str, Any],
                         confidence: float) -> bool:
        """Submit a vote for consensus"""
        if consensus_id not in self.active_consensus:
            return False
            
        consensus = self.active_consensus[consensus_id]
        if agent_id not in consensus["participants"]:
            return False
            
        consensus["votes"][agent_id] = {
            "data": vote_data,
            "confidence": confidence,
            "timestamp": time.time()
        }
        
        # Check if consensus is reached
        await self._check_consensus_completion(consensus_id)
        return True
        
    async def _check_consensus_completion(self, consensus_id: str):
        """Check if consensus is complete"""
        consensus = self.active_consensus[consensus_id]
        
        # Check timeout
        if time.time() - consensus["started_at"] > consensus["timeout"]:
            consensus["status"] = "timeout"
            await self._finalize_consensus(consensus_id)
            return
            
        # Check if all participants voted
        if len(consensus["votes"]) >= len(consensus["participants"]):
            consensus["status"] = "complete"
            await self._finalize_consensus(consensus_id)
            
    async def _finalize_consensus(self, consensus_id: str):
        """Finalize consensus and determine result"""
        consensus = self.active_consensus[consensus_id]
        
        if consensus["type"] == ConsensusType.MAJORITY_VOTE:
            result = await self._majority_vote_consensus(consensus)
        elif consensus["type"] == ConsensusType.WEIGHTED_CONSENSUS:
            result = await self._weighted_consensus(consensus)
        elif consensus["type"] == ConsensusType.EXPERT_VALIDATION:
            result = await self._expert_validation_consensus(consensus)
        else:
            result = await self._iterative_refinement_consensus(consensus)
            
        consensus["result"] = result
        consensus["finalized_at"] = time.time()
        
        # Move to history
        self.consensus_history.append(consensus)
        del self.active_consensus[consensus_id]
        
        logger.info(f"Consensus {consensus_id} finalized: {result}")
        
    async def _majority_vote_consensus(self, consensus: Dict) -> Dict[str, Any]:
        """Simple majority vote consensus"""
        votes = consensus["votes"]
        vote_counts = defaultdict(int)
        
        for vote_data in votes.values():
            # Extract main decision from vote
            decision = vote_data["data"].get("decision", "abstain")
            vote_counts[decision] += 1
            
        winner = max(vote_counts.items(), key=lambda x: x[1])
        return {
            "decision": winner[0],
            "vote_count": winner[1],
            "total_votes": len(votes),
            "confidence": sum(v["confidence"] for v in votes.values()) / len(votes)
        }
        
    async def _weighted_consensus(self, consensus: Dict) -> Dict[str, Any]:
        """Weighted consensus based on agent trust scores"""
        votes = consensus["votes"]
        weighted_decisions = defaultdict(float)
        total_weight = 0
        
        for agent_id, vote_data in votes.items():
            # In real implementation, get agent trust score
            weight = vote_data["confidence"]  # Use confidence as weight for now
            decision = vote_data["data"].get("decision", "abstain")
            
            weighted_decisions[decision] += weight
            total_weight += weight
            
        # Normalize weights
        for decision in weighted_decisions:
            weighted_decisions[decision] /= total_weight
            
        winner = max(weighted_decisions.items(), key=lambda x: x[1])
        return {
            "decision": winner[0],
            "weight": winner[1],
            "confidence": winner[1],
            "total_weight": total_weight
        }

class A2ACommunicationLayer:
    """Advanced A2A Communication Layer with robust protocols"""
    
    def __init__(self, agent_id: str, agent_profile: AgentProfile):
        self.agent_id = agent_id
        self.profile = agent_profile
        self.message_queue = asyncio.Queue()
        self.sent_messages = {}
        self.received_messages = {}
        self.active_collaborations = {}
        self.consensus_engine = ConsensusEngine()
        self.network_map = {}  # Other agents in network
        self.performance_tracker = {}
        
    async def send_message(self, message: A2AMessage) -> bool:
        """Send A2A message with delivery confirmation"""
        try:
            # Store message for tracking
            self.sent_messages[message.id] = {
                "message": message,
                "sent_at": time.time(),
                "status": "sent",
                "retries": 0
            }
            
            # Add to queue for processing
            await self.message_queue.put(message)
            
            logger.info(f"Agent {self.agent_id} sent message {message.id} to {message.receiver_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message {message.id}: {e}")
            return False
            
    async def receive_message(self, message: A2AMessage) -> Dict[str, Any]:
        """Receive and process A2A message"""
        try:
            # Store received message
            self.received_messages[message.id] = {
                "message": message,
                "received_at": time.time(),
                "processed": False
            }
            
            # Process based on message type
            if message.type == MessageType.TASK_REQUEST:
                response = await self._handle_task_request(message)
            elif message.type == MessageType.COLLABORATION_INVITE:
                response = await self._handle_collaboration_invite(message)
            elif message.type == MessageType.CONSENSUS_VOTE:
                response = await self._handle_consensus_vote(message)
            elif message.type == MessageType.DISCOVERY:
                response = await self._handle_discovery(message)
            else:
                response = await self._handle_generic_message(message)
                
            # Mark as processed
            self.received_messages[message.id]["processed"] = True
            
            # Send response if required
            if message.requires_response and response:
                await self._send_response(message, response)
                
            return response
            
        except Exception as e:
            logger.error(f"Failed to process message {message.id}: {e}")
            return {"error": str(e)}
            
    async def initiate_collaboration(self, 
                                   task: str,
                                   required_roles: List[AgentRole],
                                   context: Dict[str, Any]) -> str:
        """Initiate multi-agent collaboration"""
        collaboration_id = str(uuid.uuid4())
        
        # Find suitable agents for roles
        participants = await self._discover_agents_for_roles(required_roles)
        
        collaboration = {
            "id": collaboration_id,
            "task": task,
            "participants": participants,
            "context": context,
            "status": "initializing",
            "created_at": time.time(),
            "messages": [],
            "results": {}
        }
        
        self.active_collaborations[collaboration_id] = collaboration
        
        # Send collaboration invites
        for participant_id in participants:
            invite_message = A2AMessage(
                id=str(uuid.uuid4()),
                type=MessageType.COLLABORATION_INVITE,
                sender_id=self.agent_id,
                receiver_id=participant_id,
                timestamp=time.time(),
                payload={
                    "collaboration_id": collaboration_id,
                    "task": task,
                    "role_required": participants[participant_id]["role"],
                    "context": context
                },
                context={"collaboration": True},
                requires_response=True
            )
            
            await self.send_message(invite_message)
            
        logger.info(f"Initiated collaboration {collaboration_id} with {len(participants)} agents")
        return collaboration_id
        
    async def request_consensus(self,
                              topic: str,
                              data: Dict[str, Any],
                              consensus_type: ConsensusType = ConsensusType.MAJORITY_VOTE) -> str:
        """Request consensus from network agents"""
        
        # Get available agents
        available_agents = list(self.network_map.keys())
        
        # Initiate consensus
        consensus_id = await self.consensus_engine.initiate_consensus(
            topic=topic,
            participants=available_agents,
            consensus_type=consensus_type,
            data=data
        )
        
        # Send consensus vote requests
        for agent_id in available_agents:
            vote_request = A2AMessage(
                id=str(uuid.uuid4()),
                type=MessageType.CONSENSUS_VOTE,
                sender_id=self.agent_id,
                receiver_id=agent_id,
                timestamp=time.time(),
                payload={
                    "consensus_id": consensus_id,
                    "topic": topic,
                    "data": data,
                    "consensus_type": consensus_type.value
                },
                context={"consensus": True},
                requires_response=True
            )
            
            await self.send_message(vote_request)
            
        return consensus_id
        
    async def _handle_task_request(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle incoming task request"""
        task_data = message.payload
        
        # Check if agent can handle this task
        can_handle = await self._check_task_capability(task_data)
        
        if can_handle:
            # Process the task
            result = await self._execute_task(task_data)
            return {
                "status": "accepted",
                "result": result,
                "agent_id": self.agent_id,
                "processing_time": time.time() - message.timestamp
            }
        else:
            # Suggest alternative agents
            alternatives = await self._suggest_alternative_agents(task_data)
            return {
                "status": "declined",
                "reason": "Capability mismatch",
                "alternatives": alternatives
            }
            
    async def _handle_collaboration_invite(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle collaboration invitation"""
        invite_data = message.payload
        
        # Evaluate if agent should join
        should_join = await self._evaluate_collaboration_invite(invite_data)
        
        if should_join:
            collaboration_id = invite_data["collaboration_id"]
            return {
                "status": "accepted",
                "collaboration_id": collaboration_id,
                "capabilities": [asdict(cap) for cap in self.profile.capabilities],
                "estimated_contribution": await self._estimate_contribution(invite_data)
            }
        else:
            return {
                "status": "declined",
                "reason": "Resource constraints or role mismatch"
            }
            
    async def _handle_consensus_vote(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle consensus vote request"""
        consensus_data = message.payload
        
        # Generate vote based on agent's expertise
        vote = await self._generate_consensus_vote(consensus_data)
        
        # Submit vote to consensus engine
        await self.consensus_engine.submit_vote(
            consensus_data["consensus_id"],
            self.agent_id,
            vote["data"],
            vote["confidence"]
        )
        
        return {
            "status": "voted",
            "consensus_id": consensus_data["consensus_id"],
            "confidence": vote["confidence"]
        }
        
    async def _discover_agents_for_roles(self, required_roles: List[AgentRole]) -> Dict[str, Dict]:
        """Discover agents that can fulfill required roles"""
        participants = {}
        
        for role in required_roles:
            # Find best agent for this role
            best_agent = await self._find_best_agent_for_role(role)
            if best_agent:
                participants[best_agent["id"]] = {
                    "role": role,
                    "agent_profile": best_agent
                }
                
        return participants
        
    async def _find_best_agent_for_role(self, role: AgentRole) -> Optional[Dict]:
        """Find the best agent for a specific role"""
        candidates = []
        
        for agent_id, agent_info in self.network_map.items():
            if agent_info.get("role") == role:
                score = agent_info.get("trust_score", 0.5) * agent_info.get("availability", 1.0)
                candidates.append((score, agent_info))
                
        if candidates:
            return max(candidates, key=lambda x: x[0])[1]
        return None
        
    async def get_network_status(self) -> Dict[str, Any]:
        """Get comprehensive network status"""
        return {
            "agent_id": self.agent_id,
            "network_size": len(self.network_map),
            "active_collaborations": len(self.active_collaborations),
            "active_consensus": len(self.consensus_engine.active_consensus),
            "message_queue_size": self.message_queue.qsize(),
            "performance_metrics": self.performance_tracker,
            "last_updated": time.time()
        }

class AdaptiveA2AOrchestrator:
    """Adaptive A2A Orchestrator that manages multiple agents and consensus"""
    
    def __init__(self):
        self.agents = {}
        self.communication_layers = {}
        self.global_consensus_engine = ConsensusEngine()
        self.orchestration_history = []
        
    async def register_agent(self, agent_profile: AgentProfile) -> str:
        """Register new agent in the A2A network"""
        agent_id = agent_profile.id
        
        # Create communication layer for agent
        comm_layer = A2ACommunicationLayer(agent_id, agent_profile)
        
        self.agents[agent_id] = agent_profile
        self.communication_layers[agent_id] = comm_layer
        
        # Notify other agents of new agent
        await self._broadcast_agent_discovery(agent_profile)
        
        logger.info(f"Registered agent {agent_id} with role {agent_profile.role}")
        return agent_id
        
    async def orchestrate_task(self, 
                             task_description: str,
                             required_capabilities: List[str],
                             consensus_required: bool = True) -> Dict[str, Any]:
        """Orchestrate task execution across multiple agents"""
        
        orchestration_id = str(uuid.uuid4())
        
        # Phase 1: Task Analysis and Agent Selection
        suitable_agents = await self._select_agents_for_task(
            task_description, required_capabilities
        )
        
        if not suitable_agents:
            return {"error": "No suitable agents found for task"}
            
        # Phase 2: Initial Task Distribution
        task_assignments = await self._distribute_task(
            task_description, suitable_agents
        )
        
        # Phase 3: Parallel Execution
        results = await self._execute_parallel_tasks(task_assignments)
        
        # Phase 4: Consensus if required
        if consensus_required and len(results) > 1:
            consensus_result = await self._reach_consensus_on_results(
                task_description, results, suitable_agents
            )
            final_result = consensus_result
        else:
            final_result = await self._merge_results(results)
            
        # Phase 5: Store orchestration history
        orchestration_record = {
            "id": orchestration_id,
            "task": task_description,
            "agents_used": suitable_agents,
            "results": results,
            "final_result": final_result,
            "timestamp": time.time()
        }
        
        self.orchestration_history.append(orchestration_record)
        
        return {
            "orchestration_id": orchestration_id,
            "task": task_description,
            "agents_involved": len(suitable_agents),
            "execution_time": time.time() - orchestration_record["timestamp"],
            "result": final_result,
            "consensus_used": consensus_required
        }
        
    async def _reach_consensus_on_results(self,
                                        task: str,
                                        results: Dict[str, Any],
                                        agents: List[str]) -> Dict[str, Any]:
        """Reach consensus on task results"""
        
        consensus_id = await self.global_consensus_engine.initiate_consensus(
            topic=f"Task results: {task}",
            participants=agents,
            consensus_type=ConsensusType.WEIGHTED_CONSENSUS,
            data={"results": results, "task": task}
        )
        
        # Each agent votes on the best result
        for agent_id in agents:
            comm_layer = self.communication_layers[agent_id]
            
            # Agent evaluates all results and votes
            vote_data = await self._generate_result_vote(agent_id, results, task)
            
            await self.global_consensus_engine.submit_vote(
                consensus_id, agent_id, vote_data["data"], vote_data["confidence"]
            )
            
        # Wait for consensus completion
        max_wait = 30.0
        start_time = time.time()
        
        while consensus_id in self.global_consensus_engine.active_consensus:
            if time.time() - start_time > max_wait:
                break
            await asyncio.sleep(0.1)
            
        # Get consensus result
        for record in self.global_consensus_engine.consensus_history:
            if record["id"] == consensus_id:
                return record["result"]
                
        return {"error": "Consensus timeout"}

# Global orchestrator instance
adaptive_orchestrator = AdaptiveA2AOrchestrator()