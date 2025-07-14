#!/usr/bin/env python3
"""
A2A Neo4j Integration - Advanced Graph Database Persistence
Integrates Neo4j graph database with the A2A orchestration system
"""
import asyncio
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging
from neo4j import GraphDatabase, Session
import aiohttp
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentCardDTO:
    """Agent card data transfer object"""
    agentId: str
    name: str
    capabilities: List[str]
    version: str
    language: str
    jwtSub: str
    created_at: str
    performance_score: float = 0.95

@dataclass
class TaskDTO:
    """Task data transfer object"""
    taskId: str
    intent: str
    status: str
    startedAt: str
    payloadHash: str
    agentId: str
    description: str
    result: Optional[str] = None
    confidence: float = 0.0
    processing_time: float = 0.0

@dataclass
class PerformanceMetricDTO:
    """Performance metric data transfer object"""
    metricId: str
    type: str
    value: float
    unit: str
    timestamp: str
    taskId: str

class Neo4jA2ADriver:
    """Neo4j driver optimized for A2A operations"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password),
            max_connection_pool_size=100,
            connection_acquisition_timeout=60000,
            max_transaction_retry_time=30000
        )
        self._ensure_constraints()
    
    def _ensure_constraints(self):
        """Create necessary constraints and indexes"""
        with self.driver.session() as session:
            try:
                # Create constraints
                session.run("""
                CREATE CONSTRAINT agentcard_id IF NOT EXISTS
                FOR (a:AgentCard) REQUIRE a.agentId IS UNIQUE
                """)
                
                session.run("""
                CREATE CONSTRAINT task_id IF NOT EXISTS
                FOR (t:Task) REQUIRE t.taskId IS UNIQUE
                """)
                
                session.run("""
                CREATE CONSTRAINT metric_id IF NOT EXISTS
                FOR (m:PerformanceMetric) REQUIRE m.metricId IS UNIQUE
                """)
                
                # Create indexes for performance
                session.run("""
                CREATE INDEX task_intent_status IF NOT EXISTS
                FOR (t:Task) ON (t.intent, t.status)
                """)
                
                session.run("""
                CREATE INDEX agent_capabilities IF NOT EXISTS
                FOR (a:AgentCard) ON (a.capabilities)
                """)
                
                session.run("""
                CREATE INDEX metric_timestamp IF NOT EXISTS
                FOR (m:PerformanceMetric) ON (m.timestamp)
                """)
                
                logger.info("Neo4j constraints and indexes created successfully")
                
            except Exception as e:
                logger.warning(f"Constraint creation warning (may already exist): {e}")
    
    def close(self):
        """Close the driver connection"""
        self.driver.close()
    
    @asynccontextmanager
    async def session(self):
        """Async context manager for sessions"""
        session = self.driver.session()
        try:
            yield session
        finally:
            session.close()

class A2ANeo4jRepository:
    """Repository for A2A data operations with Neo4j"""
    
    def __init__(self, driver: Neo4jA2ADriver):
        self.driver = driver
    
    def create_agent_card(self, agent: AgentCardDTO) -> bool:
        """Create or update an agent card"""
        try:
            with self.driver.driver.session() as session:
                result = session.write_transaction(self._create_agent_tx, agent)
                logger.info(f"Agent card created/updated: {agent.agentId}")
                return True
        except Exception as e:
            logger.error(f"Failed to create agent card: {e}")
            return False
    
    def _create_agent_tx(self, tx, agent: AgentCardDTO):
        """Transaction for creating agent card"""
        query = """
        MERGE (a:AgentCard {agentId: $agentId})
        ON CREATE SET 
            a.name = $name,
            a.version = $version,
            a.language = $language,
            a.jwtSub = $jwtSub,
            a.capabilities = $capabilities,
            a.created_at = $created_at,
            a.performance_score = $performance_score
        ON MATCH SET 
            a.capabilities = $capabilities,
            a.performance_score = $performance_score,
            a.version = $version
        RETURN a
        """
        return tx.run(query, **asdict(agent))
    
    def create_task_with_metrics(self, task: TaskDTO, metrics: List[PerformanceMetricDTO]) -> bool:
        """Create task with associated performance metrics"""
        try:
            with self.driver.driver.session() as session:
                result = session.write_transaction(self._create_task_with_metrics_tx, task, metrics)
                logger.info(f"Task created with {len(metrics)} metrics: {task.taskId}")
                return True
        except Exception as e:
            logger.error(f"Failed to create task with metrics: {e}")
            return False
    
    def _create_task_with_metrics_tx(self, tx, task: TaskDTO, metrics: List[PerformanceMetricDTO]):
        """Transaction for creating task with metrics"""
        # Create/get agent
        agent_query = """
        MERGE (a:AgentCard {agentId: $agentId})
        RETURN a
        """
        tx.run(agent_query, agentId=task.agentId)
        
        # Create task
        task_query = """
        MATCH (a:AgentCard {agentId: $agentId})
        CREATE (t:Task {
            taskId: $taskId,
            intent: $intent,
            status: $status,
            startedAt: datetime($startedAt),
            payloadHash: $payloadHash,
            description: $description,
            result: $result,
            confidence: $confidence,
            processing_time: $processing_time
        })
        CREATE (a)-[:RAN {timestamp: datetime()}]->(t)
        RETURN t
        """
        task_dict = asdict(task)
        tx.run(task_query, **task_dict)
        
        # Create metrics
        if metrics:
            for metric in metrics:
                metric_query = """
                MATCH (t:Task {taskId: $taskId})
                CREATE (m:PerformanceMetric {
                    metricId: $metricId,
                    type: $type,
                    value: $value,
                    unit: $unit,
                    timestamp: datetime($timestamp)
                })
                CREATE (m)-[:MEASURES]->(t)
                """
                metric_dict = asdict(metric)
                tx.run(metric_query, **metric_dict)
    
    def find_agents_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """Find agents with specific capability"""
        try:
            with self.driver.driver.session() as session:
                result = session.read_transaction(self._find_agents_by_capability_tx, capability)
                return result
        except Exception as e:
            logger.error(f"Failed to find agents by capability: {e}")
            return []
    
    def _find_agents_by_capability_tx(self, tx, capability: str):
        """Transaction for finding agents by capability"""
        query = """
        MATCH (a:AgentCard)
        WHERE $capability IN a.capabilities
        RETURN a {.*} as agent
        ORDER BY a.performance_score DESC
        """
        result = tx.run(query, capability=capability)
        return [record["agent"] for record in result]
    
    def get_agent_performance_history(self, agent_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get agent performance history over specified days"""
        try:
            with self.driver.driver.session() as session:
                result = session.read_transaction(self._get_performance_history_tx, agent_id, days)
                return result
        except Exception as e:
            logger.error(f"Failed to get performance history: {e}")
            return []
    
    def _get_performance_history_tx(self, tx, agent_id: str, days: int):
        """Transaction for getting performance history"""
        query = """
        MATCH (a:AgentCard {agentId: $agent_id})-[:RAN]->(t:Task)<-[:MEASURES]-(m:PerformanceMetric)
        WHERE m.timestamp >= datetime() - duration({days: $days})
        RETURN {
            taskId: t.taskId,
            intent: t.intent,
            status: t.status,
            confidence: t.confidence,
            processing_time: t.processing_time,
            metric_type: m.type,
            metric_value: m.value,
            timestamp: toString(m.timestamp)
        } as performance_data
        ORDER BY m.timestamp DESC
        """
        result = tx.run(query, agent_id=agent_id, days=days)
        return [record["performance_data"] for record in result]
    
    def get_task_collaboration_network(self, task_id: str) -> Dict[str, Any]:
        """Get collaboration network for a specific task"""
        try:
            with self.driver.driver.session() as session:
                result = session.read_transaction(self._get_collaboration_network_tx, task_id)
                return result
        except Exception as e:
            logger.error(f"Failed to get collaboration network: {e}")
            return {}
    
    def _get_collaboration_network_tx(self, tx, task_id: str):
        """Transaction for getting collaboration network"""
        query = """
        MATCH (t:Task {taskId: $task_id})<-[:RAN]-(a:AgentCard)
        OPTIONAL MATCH (a)-[:RAN]->(related_task:Task)
        WHERE related_task.startedAt >= t.startedAt - duration({hours: 24})
        AND related_task.startedAt <= t.startedAt + duration({hours: 24})
        WITH a, t, collect(DISTINCT related_task) as related_tasks
        OPTIONAL MATCH (other_agent:AgentCard)-[:RAN]->(shared_task:Task)<-[:RAN]-(a)
        WHERE shared_task.startedAt >= t.startedAt - duration({days: 7})
        RETURN {
            primary_agent: a {.*},
            primary_task: t {.*},
            related_tasks: [rt IN related_tasks | rt {.*}],
            collaborating_agents: collect(DISTINCT other_agent {.*})
        } as network
        """
        result = tx.run(query, task_id=task_id)
        record = result.single()
        return record["network"] if record else {}
    
    def find_optimal_agent_for_task(self, task_intent: str, required_capabilities: List[str]) -> Optional[Dict[str, Any]]:
        """Find optimal agent for a given task based on capabilities and performance"""
        try:
            with self.driver.driver.session() as session:
                result = session.read_transaction(self._find_optimal_agent_tx, task_intent, required_capabilities)
                return result
        except Exception as e:
            logger.error(f"Failed to find optimal agent: {e}")
            return None
    
    def _find_optimal_agent_tx(self, tx, task_intent: str, required_capabilities: List[str]):
        """Transaction for finding optimal agent"""
        query = """
        MATCH (a:AgentCard)
        WHERE ALL(cap IN $required_capabilities WHERE cap IN a.capabilities)
        OPTIONAL MATCH (a)-[:RAN]->(recent_task:Task)
        WHERE recent_task.startedAt >= datetime() - duration({days: 30})
        AND recent_task.intent = $task_intent
        WITH a, 
             count(recent_task) as recent_task_count,
             avg(recent_task.confidence) as avg_confidence,
             avg(recent_task.processing_time) as avg_processing_time
        RETURN a {
            .*,
            recent_task_count: recent_task_count,
            avg_confidence: COALESCE(avg_confidence, 0.5),
            avg_processing_time: COALESCE(avg_processing_time, 0.0),
            optimization_score: a.performance_score * COALESCE(avg_confidence, 0.5) * (1.0 / (COALESCE(avg_processing_time, 1.0) + 1))
        } as agent
        ORDER BY agent.optimization_score DESC
        LIMIT 1
        """
        result = tx.run(query, task_intent=task_intent, required_capabilities=required_capabilities)
        record = result.single()
        return record["agent"] if record else None
    
    def get_system_analytics(self) -> Dict[str, Any]:
        """Get comprehensive system analytics"""
        try:
            with self.driver.driver.session() as session:
                result = session.read_transaction(self._get_system_analytics_tx)
                return result
        except Exception as e:
            logger.error(f"Failed to get system analytics: {e}")
            return {}
    
    def _get_system_analytics_tx(self, tx):
        """Transaction for getting system analytics"""
        query = """
        CALL {
            MATCH (a:AgentCard)
            RETURN count(a) as total_agents
        }
        CALL {
            MATCH (t:Task)
            RETURN count(t) as total_tasks
        }
        CALL {
            MATCH (t:Task)
            WHERE t.startedAt >= datetime() - duration({days: 7})
            RETURN count(t) as tasks_last_week
        }
        CALL {
            MATCH (t:Task)
            WHERE t.status = 'COMPLETED'
            RETURN avg(t.confidence) as avg_confidence
        }
        CALL {
            MATCH (t:Task)
            WHERE t.status = 'COMPLETED'
            RETURN avg(t.processing_time) as avg_processing_time
        }
        CALL {
            MATCH (a:AgentCard)-[:RAN]->(t:Task)
            WITH a, count(t) as task_count
            ORDER BY task_count DESC
            LIMIT 5
            RETURN collect({agent: a.name, task_count: task_count}) as top_agents
        }
        RETURN {
            total_agents: total_agents,
            total_tasks: total_tasks,
            tasks_last_week: tasks_last_week,
            avg_confidence: COALESCE(avg_confidence, 0.0),
            avg_processing_time: COALESCE(avg_processing_time, 0.0),
            top_agents: top_agents
        } as analytics
        """
        result = tx.run(query)
        record = result.single()
        return record["analytics"] if record else {}

class A2ANeo4jIntegratedOrchestrator:
    """A2A Orchestrator with Neo4j persistence integration"""
    
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.neo4j_driver = Neo4jA2ADriver(neo4j_uri, neo4j_user, neo4j_password)
        self.repository = A2ANeo4jRepository(self.neo4j_driver)
        self.agents = self._initialize_agents()
    
    def _initialize_agents(self) -> Dict[str, AgentCardDTO]:
        """Initialize and persist agent cards"""
        agents = {
            "planner": AgentCardDTO(
                agentId="planner-001",
                name="Project Planner",
                capabilities=["technical_planning", "architecture_design", "project_management"],
                version="1.0.0",
                language="python",
                jwtSub="planner-jwt",
                created_at=datetime.now(timezone.utc).isoformat(),
                performance_score=0.95
            ),
            "coder": AgentCardDTO(
                agentId="coder-001",
                name="Code Generator",
                capabilities=["full_stack_development", "api_design", "database_design"],
                version="1.0.0",
                language="python",
                jwtSub="coder-jwt",
                created_at=datetime.now(timezone.utc).isoformat(),
                performance_score=0.92
            ),
            "reviewer": AgentCardDTO(
                agentId="reviewer-001",
                name="Code Reviewer",
                capabilities=["code_quality", "security_analysis", "performance_optimization"],
                version="1.0.0",
                language="python",
                jwtSub="reviewer-jwt",
                created_at=datetime.now(timezone.utc).isoformat(),
                performance_score=0.96
            ),
            "tester": AgentCardDTO(
                agentId="tester-001",
                name="QA Engineer",
                capabilities=["automated_testing", "performance_testing", "security_testing"],
                version="1.0.0",
                language="python",
                jwtSub="tester-jwt",
                created_at=datetime.now(timezone.utc).isoformat(),
                performance_score=0.90
            ),
            "coordinator": AgentCardDTO(
                agentId="coordinator-001",
                name="Project Coordinator",
                capabilities=["team_coordination", "project_management", "quality_assurance"],
                version="1.0.0",
                language="python",
                jwtSub="coordinator-jwt",
                created_at=datetime.now(timezone.utc).isoformat(),
                performance_score=0.94
            )
        }
        
        # Persist agents to Neo4j
        for agent in agents.values():
            self.repository.create_agent_card(agent)
        
        return agents
    
    async def orchestrate_with_persistence(self, description: str, intent: str = "general") -> Dict[str, Any]:
        """Orchestrate task with full Neo4j persistence"""
        start_time = time.time()
        task_id = str(uuid.uuid4())
        
        logger.info(f"Starting Neo4j-integrated orchestration: {description}")
        
        # Find optimal agents for this task
        required_capabilities = self._determine_required_capabilities(intent)
        optimal_agents = []
        
        for capability in required_capabilities:
            agent = self.repository.find_optimal_agent_for_task(intent, [capability])
            if agent:
                optimal_agents.append(agent)
        
        if not optimal_agents:
            # Fallback to default agents
            optimal_agents = list(self.agents.values())
        
        # Create main task
        main_task = TaskDTO(
            taskId=task_id,
            intent=intent,
            status="IN_PROGRESS",
            startedAt=datetime.now(timezone.utc).isoformat(),
            payloadHash=str(hash(description)),
            agentId="coordinator-001",
            description=description,
            confidence=0.0,
            processing_time=0.0
        )
        
        # Process with each agent and collect results
        agent_results = []
        all_metrics = []
        
        for i, agent_data in enumerate(optimal_agents[:5]):  # Limit to 5 agents
            agent_id = agent_data.get('agentId', f"agent-{i}")
            
            # Simulate agent processing
            processing_start = time.time()
            
            # Create agent-specific task
            agent_task = TaskDTO(
                taskId=f"{task_id}-{agent_id}",
                intent=intent,
                status="COMPLETED",
                startedAt=datetime.now(timezone.utc).isoformat(),
                payloadHash=str(hash(f"{description}-{agent_id}")),
                agentId=agent_id,
                description=f"Agent {agent_id} processing: {description}",
                result=self._generate_agent_result(agent_id, description),
                confidence=0.85 + (i * 0.02),  # Vary confidence slightly
                processing_time=time.time() - processing_start
            )
            
            # Create performance metrics
            metrics = [
                PerformanceMetricDTO(
                    metricId=str(uuid.uuid4()),
                    type="response_time",
                    value=agent_task.processing_time,
                    unit="seconds",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    taskId=agent_task.taskId
                ),
                PerformanceMetricDTO(
                    metricId=str(uuid.uuid4()),
                    type="confidence_score",
                    value=agent_task.confidence,
                    unit="percentage",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    taskId=agent_task.taskId
                )
            ]
            
            # Persist to Neo4j
            self.repository.create_task_with_metrics(agent_task, metrics)
            
            agent_results.append({
                "agent_id": agent_id,
                "task_id": agent_task.taskId,
                "result": agent_task.result,
                "confidence": agent_task.confidence,
                "processing_time": agent_task.processing_time
            })
            all_metrics.extend(metrics)
        
        # Update main task
        total_processing_time = time.time() - start_time
        main_task.status = "COMPLETED"
        main_task.result = "Multi-agent orchestration completed successfully"
        main_task.confidence = sum(r["confidence"] for r in agent_results) / len(agent_results)
        main_task.processing_time = total_processing_time
        
        # Create final metrics for main task
        final_metrics = [
            PerformanceMetricDTO(
                metricId=str(uuid.uuid4()),
                type="total_processing_time",
                value=total_processing_time,
                unit="seconds",
                timestamp=datetime.now(timezone.utc).isoformat(),
                taskId=task_id
            ),
            PerformanceMetricDTO(
                metricId=str(uuid.uuid4()),
                type="overall_confidence",
                value=main_task.confidence,
                unit="percentage",
                timestamp=datetime.now(timezone.utc).isoformat(),
                taskId=task_id
            )
        ]
        
        # Persist main task
        self.repository.create_task_with_metrics(main_task, final_metrics)
        
        # Get collaboration network analysis
        collaboration_network = self.repository.get_task_collaboration_network(task_id)
        
        logger.info(f"Neo4j orchestration completed in {total_processing_time:.2f}s")
        
        return {
            "task_id": task_id,
            "description": description,
            "intent": intent,
            "status": "COMPLETED",
            "total_processing_time": total_processing_time,
            "overall_confidence": main_task.confidence,
            "agent_results": agent_results,
            "collaboration_network": collaboration_network,
            "metrics_count": len(all_metrics) + len(final_metrics),
            "neo4j_integration": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _determine_required_capabilities(self, intent: str) -> List[str]:
        """Determine required capabilities based on task intent"""
        capability_map = {
            "mmorpg": ["technical_planning", "full_stack_development", "code_quality", "automated_testing"],
            "web_app": ["api_design", "full_stack_development", "security_analysis"],
            "mobile_app": ["full_stack_development", "performance_optimization", "automated_testing"],
            "ai_integration": ["technical_planning", "api_design", "performance_optimization"],
            "general": ["technical_planning", "full_stack_development", "code_quality"]
        }
        return capability_map.get(intent, capability_map["general"])
    
    def _generate_agent_result(self, agent_id: str, description: str) -> str:
        """Generate contextual result based on agent role"""
        if "planner" in agent_id:
            return f"Technical planning completed for: {description}. Architecture designed with scalability considerations."
        elif "coder" in agent_id:
            return f"Implementation completed for: {description}. Code generated with best practices and error handling."
        elif "reviewer" in agent_id:
            return f"Code review completed for: {description}. Quality assessment passed with optimization recommendations."
        elif "tester" in agent_id:
            return f"Testing strategy developed for: {description}. Comprehensive test coverage planned."
        elif "coordinator" in agent_id:
            return f"Project coordination completed for: {description}. Team alignment and delivery timeline established."
        else:
            return f"Task processed successfully: {description}"
    
    def get_analytics_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard"""
        try:
            system_analytics = self.repository.get_system_analytics()
            
            # Get individual agent performance
            agent_performance = {}
            for agent_id in self.agents.keys():
                performance_history = self.repository.get_agent_performance_history(
                    f"{agent_id}-001", days=30
                )
                agent_performance[agent_id] = {
                    "recent_tasks": len(performance_history),
                    "avg_confidence": sum(p.get("confidence", 0) for p in performance_history) / len(performance_history) if performance_history else 0,
                    "avg_processing_time": sum(p.get("processing_time", 0) for p in performance_history) / len(performance_history) if performance_history else 0
                }
            
            return {
                "system_analytics": system_analytics,
                "agent_performance": agent_performance,
                "neo4j_status": "connected",
                "dashboard_generated_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to generate analytics dashboard: {e}")
            return {"error": str(e), "neo4j_status": "error"}
    
    def close(self):
        """Close Neo4j connections"""
        self.neo4j_driver.close()

# Example usage and testing
async def main():
    """Example usage of Neo4j integrated A2A orchestrator"""
    
    # Initialize with Neo4j connection
    orchestrator = A2ANeo4jIntegratedOrchestrator(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password"
    )
    
    try:
        # Test orchestration with persistence
        result = await orchestrator.orchestrate_with_persistence(
            description="Create a scalable D&D MMORPG with real-time combat and guild system",
            intent="mmorpg"
        )
        
        print("Orchestration Result:")
        print(json.dumps(result, indent=2))
        
        # Get analytics dashboard
        analytics = orchestrator.get_analytics_dashboard()
        print("\nAnalytics Dashboard:")
        print(json.dumps(analytics, indent=2))
        
        # Test agent discovery
        agents = orchestrator.repository.find_agents_by_capability("technical_planning")
        print(f"\nFound {len(agents)} agents with technical_planning capability")
        
    finally:
        orchestrator.close()

if __name__ == "__main__":
    asyncio.run(main())