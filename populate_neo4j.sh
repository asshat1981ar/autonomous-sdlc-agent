#!/usr/bin/env bash
# A2A Neo4j Database Population Script
# Usage: ./populate_neo4j.sh [NEO4J_URI] [USER] [PASS]

set -e

NEO4J_URI=${1:-bolt://localhost:7687}
NEO4J_USER=${2:-neo4j}
NEO4J_PASS=${3:-password123}

echo "🚀 A2A Neo4j Database Population Script"
echo "URI: $NEO4J_URI"
echo "User: $NEO4J_USER"
echo ""

# Create directories for temporary files
mkdir -p scripts/cypher

# Function to execute Cypher commands
neo4j_shell() {
  docker exec -i neo4j-a2a cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASS" "$@"
}

# Wait for Neo4j to be ready
echo "⏳ Waiting for Neo4j to be ready..."
for i in {1..30}; do
  if docker exec neo4j-a2a cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASS" "RETURN 1" &>/dev/null; then
    echo "✅ Neo4j is ready!"
    break
  fi
  echo "Waiting... ($i/30)"
  sleep 2
done

# 1. Load schema and constraints
echo "📋 Creating schema and constraints..."
cat << 'CYPHER' > scripts/cypher/schema.cql
// A2A System Schema Creation

// === CONSTRAINTS ===
CREATE CONSTRAINT agentcard_id IF NOT EXISTS
FOR (a:AgentCard) REQUIRE a.agentId IS UNIQUE;

CREATE CONSTRAINT task_id IF NOT EXISTS
FOR (t:Task) REQUIRE t.taskId IS UNIQUE;

CREATE CONSTRAINT metric_id IF NOT EXISTS
FOR (m:PerformanceMetric) REQUIRE m.metricId IS UNIQUE;

CREATE CONSTRAINT knowledge_item_id IF NOT EXISTS
FOR (k:KnowledgeItem) REQUIRE k.itemId IS UNIQUE;

CREATE CONSTRAINT session_id IF NOT EXISTS
FOR (s:Session) REQUIRE s.sessionId IS UNIQUE;

// === INDEXES FOR PERFORMANCE ===
CREATE INDEX task_intent_status IF NOT EXISTS
FOR (t:Task) ON (t.intent, t.status);

CREATE INDEX agent_capabilities IF NOT EXISTS
FOR (a:AgentCard) ON (a.capabilities);

CREATE INDEX metric_timestamp IF NOT EXISTS
FOR (m:PerformanceMetric) ON (m.timestamp);

CREATE INDEX task_timestamp IF NOT EXISTS
FOR (t:Task) ON (t.startedAt);

CREATE INDEX knowledge_type IF NOT EXISTS
FOR (k:KnowledgeItem) ON (k.type);

CREATE INDEX session_timestamp IF NOT EXISTS
FOR (s:Session) ON (s.createdAt);

// === ADDITIONAL PERFORMANCE INDEXES ===
CREATE INDEX agent_performance_score IF NOT EXISTS
FOR (a:AgentCard) ON (a.performance_score);

CREATE INDEX task_confidence IF NOT EXISTS
FOR (t:Task) ON (t.confidence);

CREATE INDEX metric_value IF NOT EXISTS
FOR (m:PerformanceMetric) ON (m.value);

CYPHER

neo4j_shell < scripts/cypher/schema.cql
echo "✅ Schema and constraints created"

# 2. Load A2A agents
echo "🤖 Creating A2A agents..."
cat << 'CYPHER' > scripts/cypher/agents.cql
// A2A Specialized Agents

MERGE (planner:AgentCard {agentId: 'planner-001'})
SET planner += {
  name: 'Project Planner',
  capabilities: ['technical_planning', 'architecture_design', 'project_management', 'requirements_analysis'],
  version: '1.0.0',
  language: 'python',
  jwtSub: 'planner-jwt',
  created_at: datetime(),
  performance_score: 0.95,
  specialty: 'Technical Planning & Architecture',
  description: 'Specialized in creating comprehensive technical plans and system architectures'
};

MERGE (coder:AgentCard {agentId: 'coder-001'})
SET coder += {
  name: 'Code Generator',
  capabilities: ['full_stack_development', 'api_design', 'database_design', 'code_generation', 'algorithm_implementation'],
  version: '1.0.0',
  language: 'python',
  jwtSub: 'coder-jwt',
  created_at: datetime(),
  performance_score: 0.92,
  specialty: 'Full-Stack Development',
  description: 'Expert in generating production-ready code across multiple languages and frameworks'
};

MERGE (reviewer:AgentCard {agentId: 'reviewer-001'})
SET reviewer += {
  name: 'Code Reviewer',
  capabilities: ['code_quality', 'security_analysis', 'performance_optimization', 'best_practices', 'vulnerability_detection'],
  version: '1.0.0',
  language: 'python',
  jwtSub: 'reviewer-jwt',
  created_at: datetime(),
  performance_score: 0.96,
  specialty: 'Code Quality & Security',
  description: 'Focused on ensuring code quality, security, and performance optimization'
};

MERGE (tester:AgentCard {agentId: 'tester-001'})
SET tester += {
  name: 'QA Engineer',
  capabilities: ['automated_testing', 'performance_testing', 'security_testing', 'integration_testing', 'test_automation'],
  version: '1.0.0',
  language: 'python',
  jwtSub: 'tester-jwt',
  created_at: datetime(),
  performance_score: 0.90,
  specialty: 'Quality Assurance & Testing',
  description: 'Comprehensive testing strategies and automated quality assurance'
};

MERGE (coordinator:AgentCard {agentId: 'coordinator-001'})
SET coordinator += {
  name: 'Project Coordinator',
  capabilities: ['team_coordination', 'project_management', 'quality_assurance', 'workflow_optimization', 'resource_management'],
  version: '1.0.0',
  language: 'python',
  jwtSub: 'coordinator-jwt',
  created_at: datetime(),
  performance_score: 0.94,
  specialty: 'Project Management & Coordination',
  description: 'Orchestrates team collaboration and ensures project delivery excellence'
};

// Game Development Specialists
MERGE (gameDesigner:AgentCard {agentId: 'game-designer-001'})
SET gameDesigner += {
  name: 'Game Designer',
  capabilities: ['game_design', 'balance_analysis', 'mechanics_design', 'progression_systems', 'narrative_design'],
  version: '1.0.0',
  language: 'python',
  jwtSub: 'game-designer-jwt',
  created_at: datetime(),
  performance_score: 0.93,
  specialty: 'D&D MMORPG Game Design',
  description: 'Specialized in creating engaging game mechanics and balanced progression systems'
};

MERGE (backendDev:AgentCard {agentId: 'backend-dev-001'})
SET backendDev += {
  name: 'Backend Developer',
  capabilities: ['server_architecture', 'database_optimization', 'api_development', 'scalability_design', 'real_time_systems'],
  version: '1.0.0',
  language: 'python',
  jwtSub: 'backend-dev-jwt',
  created_at: datetime(),
  performance_score: 0.91,
  specialty: 'Scalable Backend Systems',
  description: 'Expert in building high-performance, scalable backend systems for MMORPGs'
};

CYPHER

neo4j_shell < scripts/cypher/agents.cql
echo "✅ A2A agents created"

# 3. Create sample tasks and workflows
echo "📋 Creating sample tasks and workflows..."
cat << 'CYPHER' > scripts/cypher/tasks.cql
// Sample A2A Tasks and Workflows

// MMORPG Development Session
MATCH (coordinator:AgentCard {agentId: 'coordinator-001'})
CREATE (session:Session {
  sessionId: 'mmorpg-session-001',
  type: 'mmorpg_development',
  description: 'D&D MMORPG Character System Development',
  createdAt: datetime(),
  status: 'COMPLETED'
})
CREATE (coordinator)-[:COORDINATED]->(session);

// Main MMORPG Task
MATCH (session:Session {sessionId: 'mmorpg-session-001'})
CREATE (mainTask:Task {
  taskId: 'task-mmorpg-001',
  intent: 'mmorpg_development',
  status: 'COMPLETED',
  startedAt: datetime() - duration({hours: 2}),
  finishedAt: datetime() - duration({hours: 1}),
  payloadHash: 'mmorpg-char-system-001',
  description: 'Create comprehensive D&D character system with classes, skills, and progression',
  result: 'Complete character system implementation with 12 classes, skill trees, and balanced progression',
  confidence: 0.94,
  processing_time: 3600.0,
  priority: 'high'
})
CREATE (session)-[:CONTAINS]->(mainTask);

// Planning Phase
MATCH (planner:AgentCard {agentId: 'planner-001'}), (mainTask:Task {taskId: 'task-mmorpg-001'})
CREATE (planningTask:Task {
  taskId: 'task-planning-001',
  intent: 'technical_planning',
  status: 'COMPLETED',
  startedAt: datetime() - duration({hours: 2}),
  finishedAt: datetime() - duration({minutes: 105}),
  payloadHash: 'planning-char-system-001',
  description: 'Design technical architecture for D&D character system',
  result: 'Comprehensive technical plan with database schema, API endpoints, and component architecture',
  confidence: 0.96,
  processing_time: 900.0,
  priority: 'high'
})
CREATE (planner)-[:RAN]->(planningTask)
CREATE (planningTask)-[:SUBTASK_OF]->(mainTask);

// Implementation Phase
MATCH (coder:AgentCard {agentId: 'coder-001'}), (mainTask:Task {taskId: 'task-mmorpg-001'})
CREATE (codingTask:Task {
  taskId: 'task-coding-001',
  intent: 'full_stack_development',
  status: 'COMPLETED',
  startedAt: datetime() - duration({minutes: 105}),
  finishedAt: datetime() - duration({minutes: 75}),
  payloadHash: 'coding-char-system-001',
  description: 'Implement D&D character system components',
  result: 'Complete implementation with character classes, skill system, and progression mechanics',
  confidence: 0.93,
  processing_time: 1800.0,
  priority: 'high'
})
CREATE (coder)-[:RAN]->(codingTask)
CREATE (codingTask)-[:SUBTASK_OF]->(mainTask);

// Review Phase
MATCH (reviewer:AgentCard {agentId: 'reviewer-001'}), (mainTask:Task {taskId: 'task-mmorpg-001'})
CREATE (reviewTask:Task {
  taskId: 'task-review-001',
  intent: 'code_quality',
  status: 'COMPLETED',
  startedAt: datetime() - duration({minutes: 75}),
  finishedAt: datetime() - duration({minutes: 45}),
  payloadHash: 'review-char-system-001',
  description: 'Review character system implementation for quality and security',
  result: 'Code review completed with optimization recommendations and security validation',
  confidence: 0.97,
  processing_time: 1800.0,
  priority: 'medium'
})
CREATE (reviewer)-[:RAN]->(reviewTask)
CREATE (reviewTask)-[:SUBTASK_OF]->(mainTask);

// Testing Phase
MATCH (tester:AgentCard {agentId: 'tester-001'}), (mainTask:Task {taskId: 'task-mmorpg-001'})
CREATE (testingTask:Task {
  taskId: 'task-testing-001',
  intent: 'automated_testing',
  status: 'COMPLETED',
  startedAt: datetime() - duration({minutes: 45}),
  finishedAt: datetime() - duration({minutes: 15}),
  payloadHash: 'testing-char-system-001',
  description: 'Create comprehensive test suite for character system',
  result: 'Complete test suite with unit tests, integration tests, and performance benchmarks',
  confidence: 0.91,
  processing_time: 1800.0,
  priority: 'medium'
})
CREATE (tester)-[:RAN]->(testingTask)
CREATE (testingTask)-[:SUBTASK_OF]->(mainTask);

CYPHER

neo4j_shell < scripts/cypher/tasks.cql
echo "✅ Sample tasks and workflows created"

# 4. Create performance metrics
echo "📊 Creating performance metrics..."
cat << 'CYPHER' > scripts/cypher/metrics.cql
// Performance Metrics for A2A Tasks

// Planning Task Metrics
MATCH (planningTask:Task {taskId: 'task-planning-001'})
CREATE (planningLatency:PerformanceMetric {
  metricId: 'metric-planning-latency-001',
  type: 'response_time',
  value: 0.89,
  unit: 'seconds',
  timestamp: datetime() - duration({hours: 2}),
  category: 'performance'
})
CREATE (planningLatency)-[:MEASURES]->(planningTask);

CREATE (planningConfidence:PerformanceMetric {
  metricId: 'metric-planning-confidence-001',
  type: 'confidence_score',
  value: 0.96,
  unit: 'percentage',
  timestamp: datetime() - duration({hours: 2}),
  category: 'quality'
})
CREATE (planningConfidence)-[:MEASURES]->(planningTask);

// Coding Task Metrics
MATCH (codingTask:Task {taskId: 'task-coding-001'})
CREATE (codingLatency:PerformanceMetric {
  metricId: 'metric-coding-latency-001',
  type: 'response_time',
  value: 1.45,
  unit: 'seconds',
  timestamp: datetime() - duration({minutes: 105}),
  category: 'performance'
})
CREATE (codingLatency)-[:MEASURES]->(codingTask);

CREATE (codingThroughput:PerformanceMetric {
  metricId: 'metric-coding-throughput-001',
  type: 'lines_of_code',
  value: 1250.0,
  unit: 'lines',
  timestamp: datetime() - duration({minutes: 105}),
  category: 'productivity'
})
CREATE (codingThroughput)-[:MEASURES]->(codingTask);

// Review Task Metrics
MATCH (reviewTask:Task {taskId: 'task-review-001'})
CREATE (reviewAccuracy:PerformanceMetric {
  metricId: 'metric-review-accuracy-001',
  type: 'issue_detection_rate',
  value: 0.94,
  unit: 'percentage',
  timestamp: datetime() - duration({minutes: 75}),
  category: 'quality'
})
CREATE (reviewAccuracy)-[:MEASURES]->(reviewTask);

CREATE (reviewCoverage:PerformanceMetric {
  metricId: 'metric-review-coverage-001',
  type: 'code_coverage',
  value: 0.97,
  unit: 'percentage',
  timestamp: datetime() - duration({minutes: 75}),
  category: 'quality'
})
CREATE (reviewCoverage)-[:MEASURES]->(reviewTask);

// Testing Task Metrics
MATCH (testingTask:Task {taskId: 'task-testing-001'})
CREATE (testCoverage:PerformanceMetric {
  metricId: 'metric-test-coverage-001',
  type: 'test_coverage',
  value: 0.89,
  unit: 'percentage',
  timestamp: datetime() - duration({minutes: 45}),
  category: 'quality'
})
CREATE (testCoverage)-[:MEASURES]->(testingTask);

CREATE (testPassRate:PerformanceMetric {
  metricId: 'metric-test-pass-rate-001',
  type: 'test_pass_rate',
  value: 0.98,
  unit: 'percentage',
  timestamp: datetime() - duration({minutes: 45}),
  category: 'quality'
})
CREATE (testPassRate)-[:MEASURES]->(testingTask);

CYPHER

neo4j_shell < scripts/cypher/metrics.cql
echo "✅ Performance metrics created"

# 5. Create knowledge items and relationships
echo "🧠 Creating knowledge items and relationships..."
cat << 'CYPHER' > scripts/cypher/knowledge.cql
// Knowledge Items and Learning Relationships

// Character System Knowledge
MATCH (mainTask:Task {taskId: 'task-mmorpg-001'})
CREATE (charSystemKnowledge:KnowledgeItem {
  itemId: 'knowledge-char-system-001',
  type: 'implementation_pattern',
  uri: 'internal://a2a/patterns/character-system',
  content: 'D&D Character System Implementation Pattern',
  tags: ['d&d', 'character-system', 'mmorpg', 'game-design'],
  createdAt: datetime() - duration({hours: 1}),
  confidence: 0.95,
  usage_count: 1,
  quality_score: 0.92
})
CREATE (charSystemKnowledge)-[:DERIVES_FROM]->(mainTask);

// API Design Knowledge
MATCH (codingTask:Task {taskId: 'task-coding-001'})
CREATE (apiKnowledge:KnowledgeItem {
  itemId: 'knowledge-api-design-001',
  type: 'api_pattern',
  uri: 'internal://a2a/patterns/restful-api',
  content: 'RESTful API Design Patterns for Game Systems',
  tags: ['api-design', 'rest', 'game-backend', 'scalability'],
  createdAt: datetime() - duration({minutes: 90}),
  confidence: 0.91,
  usage_count: 1,
  quality_score: 0.89
})
CREATE (apiKnowledge)-[:DERIVES_FROM]->(codingTask);

// Security Best Practices Knowledge
MATCH (reviewTask:Task {taskId: 'task-review-001'})
CREATE (securityKnowledge:KnowledgeItem {
  itemId: 'knowledge-security-001',
  type: 'security_pattern',
  uri: 'internal://a2a/patterns/game-security',
  content: 'Security Best Practices for MMORPG Systems',
  tags: ['security', 'authentication', 'authorization', 'game-security'],
  createdAt: datetime() - duration({minutes: 60}),
  confidence: 0.97,
  usage_count: 1,
  quality_score: 0.96
})
CREATE (securityKnowledge)-[:DERIVES_FROM]->(reviewTask);

// Testing Strategy Knowledge
MATCH (testingTask:Task {taskId: 'task-testing-001'})
CREATE (testingKnowledge:KnowledgeItem {
  itemId: 'knowledge-testing-001',
  type: 'testing_strategy',
  uri: 'internal://a2a/patterns/game-testing',
  content: 'Comprehensive Testing Strategies for Game Systems',
  tags: ['testing', 'automation', 'game-testing', 'quality-assurance'],
  createdAt: datetime() - duration({minutes: 30}),
  confidence: 0.88,
  usage_count: 1,
  quality_score: 0.90
})
CREATE (testingKnowledge)-[:DERIVES_FROM]->(testingTask);

// Agent Learning Relationships
MATCH (planner:AgentCard {agentId: 'planner-001'}), (charSystemKnowledge:KnowledgeItem {itemId: 'knowledge-char-system-001'})
CREATE (planner)-[:LEARNED]->(charSystemKnowledge);

MATCH (coder:AgentCard {agentId: 'coder-001'}), (apiKnowledge:KnowledgeItem {itemId: 'knowledge-api-design-001'})
CREATE (coder)-[:LEARNED]->(apiKnowledge);

MATCH (reviewer:AgentCard {agentId: 'reviewer-001'}), (securityKnowledge:KnowledgeItem {itemId: 'knowledge-security-001'})
CREATE (reviewer)-[:LEARNED]->(securityKnowledge);

MATCH (tester:AgentCard {agentId: 'tester-001'}), (testingKnowledge:KnowledgeItem {itemId: 'knowledge-testing-001'})
CREATE (tester)-[:LEARNED]->(testingKnowledge);

CYPHER

neo4j_shell < scripts/cypher/knowledge.cql
echo "✅ Knowledge items and relationships created"

# 6. Create collaboration networks
echo "🤝 Creating collaboration networks..."
cat << 'CYPHER' > scripts/cypher/collaboration.cql
// Agent Collaboration Networks

// Planning-Coding Collaboration
MATCH (planner:AgentCard {agentId: 'planner-001'}), (coder:AgentCard {agentId: 'coder-001'})
CREATE (planner)-[:COLLABORATED_WITH {
  session_id: 'mmorpg-session-001',
  interaction_type: 'handoff',
  timestamp: datetime() - duration({minutes: 105}),
  effectiveness: 0.94,
  feedback_score: 0.92
}]->(coder);

// Coding-Review Collaboration
MATCH (coder:AgentCard {agentId: 'coder-001'}), (reviewer:AgentCard {agentId: 'reviewer-001'})
CREATE (coder)-[:COLLABORATED_WITH {
  session_id: 'mmorpg-session-001',
  interaction_type: 'review_request',
  timestamp: datetime() - duration({minutes: 75}),
  effectiveness: 0.96,
  feedback_score: 0.95
}]->(reviewer);

// Review-Testing Collaboration
MATCH (reviewer:AgentCard {agentId: 'reviewer-001'}), (tester:AgentCard {agentId: 'tester-001'})
CREATE (reviewer)-[:COLLABORATED_WITH {
  session_id: 'mmorpg-session-001',
  interaction_type: 'quality_handoff',
  timestamp: datetime() - duration({minutes: 45}),
  effectiveness: 0.91,
  feedback_score: 0.89
}]->(tester);

// Coordinator Oversight
MATCH (coordinator:AgentCard {agentId: 'coordinator-001'}), (agent:AgentCard)
WHERE agent.agentId IN ['planner-001', 'coder-001', 'reviewer-001', 'tester-001']
CREATE (coordinator)-[:COORDINATED {
  session_id: 'mmorpg-session-001',
  oversight_type: 'project_management',
  timestamp: datetime() - duration({hours: 2}),
  effectiveness: 0.93
}]->(agent);

CYPHER

neo4j_shell < scripts/cypher/collaboration.cql
echo "✅ Collaboration networks created"

# 7. Cleanup temporary files
echo "🧹 Cleaning up temporary files..."
rm -rf scripts/cypher

# 8. Final verification
echo "🔍 Verifying database population..."
echo ""
echo "=== VERIFICATION QUERIES ==="

echo "📊 Agent Count:"
neo4j_shell "MATCH (a:AgentCard) RETURN count(a) AS agentCount;"

echo ""
echo "📋 Task Count:"
neo4j_shell "MATCH (t:Task) RETURN count(t) AS taskCount;"

echo ""
echo "📈 Metrics Count:"
neo4j_shell "MATCH (m:PerformanceMetric) RETURN count(m) AS metricCount;"

echo ""
echo "🧠 Knowledge Items Count:"
neo4j_shell "MATCH (k:KnowledgeItem) RETURN count(k) AS knowledgeCount;"

echo ""
echo "🤝 Collaboration Relationships:"
neo4j_shell "MATCH ()-[r:COLLABORATED_WITH]->() RETURN count(r) AS collaborationCount;"

echo ""
echo "=== SAMPLE DATA VERIFICATION ==="
echo "🎮 MMORPG Development Session:"
neo4j_shell "MATCH (s:Session {sessionId: 'mmorpg-session-001'})-[:CONTAINS]->(t:Task) RETURN s.description, count(t) AS taskCount;"

echo ""
echo "⚡ Agent Performance Scores:"
neo4j_shell "MATCH (a:AgentCard) RETURN a.name, a.performance_score ORDER BY a.performance_score DESC;"

echo ""
echo "🎯 Task Success Metrics:"
neo4j_shell "MATCH (t:Task)-[:MEASURES]-(m:PerformanceMetric {type: 'confidence_score'}) RETURN t.taskId, t.description, m.value AS confidence ORDER BY m.value DESC LIMIT 5;"

echo ""
echo "✅ A2A Neo4j Database Population Complete!"
echo ""
echo "🌐 Access Neo4j Browser at: http://localhost:7474"
echo "🔐 Username: neo4j"
echo "🔐 Password: password123"
echo ""
echo "🚀 Your A2A system is now ready with comprehensive graph database persistence!"