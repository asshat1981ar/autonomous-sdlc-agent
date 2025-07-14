#!/usr/bin/env bash
# Complete A2A Neo4j Setup Script
# This script sets up Neo4j, populates it with data, and verifies the installation

set -e

echo "🚀 A2A Neo4j Complete Setup Script"
echo "This will set up Neo4j Enterprise with APOC & GDS plugins and populate with A2A data"
echo ""

# Check if Docker is running
if ! docker info &>/dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"

# Create required directories
echo "📁 Creating required directories..."
mkdir -p data/neo4j data/redis logs/neo4j plugins import scripts

# Step 1: Start Neo4j
echo "🐳 Starting Neo4j container..."
if docker ps | grep -q neo4j-a2a; then
    echo "ℹ️  Neo4j container already running, stopping first..."
    docker-compose -f docker-compose-neo4j.yml down
fi

docker-compose -f docker-compose-neo4j.yml up -d

echo "⏳ Waiting for Neo4j to start (this may take 2-3 minutes)..."
sleep 30

# Wait for Neo4j to be ready
for i in {1..60}; do
    if docker exec neo4j-a2a cypher-shell -u neo4j -p password123 "RETURN 1" &>/dev/null; then
        echo "✅ Neo4j is ready!"
        break
    fi
    echo "Waiting for Neo4j to be ready... ($i/60)"
    sleep 5
done

# Check if Neo4j is ready
if ! docker exec neo4j-a2a cypher-shell -u neo4j -p password123 "RETURN 1" &>/dev/null; then
    echo "❌ Neo4j failed to start properly"
    echo "💡 Check logs with: docker logs neo4j-a2a"
    exit 1
fi

echo "✅ Neo4j is fully operational"

# Step 2: Download and install plugins (if needed)
echo "📦 Ensuring plugins are installed..."
docker exec neo4j-a2a sh -c '
    if [ ! -f /var/lib/neo4j/plugins/apoc.jar ]; then
        echo "Downloading APOC plugin..."
        wget -O /var/lib/neo4j/plugins/apoc.jar https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/5.18.1/apoc-5.18.1-core.jar
    fi
'

# Restart to ensure plugins are loaded
echo "🔄 Restarting Neo4j to ensure plugins are loaded..."
docker-compose -f docker-compose-neo4j.yml restart neo4j

echo "⏳ Waiting for Neo4j to restart..."
sleep 20

# Wait for restart
for i in {1..30}; do
    if docker exec neo4j-a2a cypher-shell -u neo4j -p password123 "RETURN 1" &>/dev/null; then
        echo "✅ Neo4j restarted successfully!"
        break
    fi
    echo "Waiting for restart... ($i/30)"
    sleep 3
done

# Step 3: Populate database
echo "📊 Populating database with A2A data..."
./populate_neo4j.sh

# Step 4: Verify installation
echo "🔍 Verifying installation..."
./verify_neo4j.sh

# Step 5: Generate quick start guide
echo "📋 Generating quick start guide..."
cat << 'EOF' > NEO4J_QUICK_START.md
# A2A Neo4j Quick Start Guide

## 🎯 Your Neo4j Database is Ready!

### Access Information
- **Neo4j Browser**: http://localhost:7474
- **Bolt Connection**: bolt://localhost:7687
- **Username**: neo4j
- **Password**: password123

### Quick Commands

#### Start Neo4j
```bash
docker-compose -f docker-compose-neo4j.yml up -d
```

#### Stop Neo4j
```bash
docker-compose -f docker-compose-neo4j.yml down
```

#### Verify Health
```bash
./verify_neo4j.sh
```

#### Access Cypher Shell
```bash
docker exec -it neo4j-a2a cypher-shell -u neo4j -p password123
```

### Sample Queries

#### View All Agents
```cypher
MATCH (a:AgentCard) 
RETURN a.name, a.capabilities, a.performance_score 
ORDER BY a.performance_score DESC;
```

#### View Recent Tasks
```cypher
MATCH (t:Task) 
RETURN t.taskId, t.intent, t.status, t.confidence 
ORDER BY t.startedAt DESC LIMIT 10;
```

#### Agent Performance Analysis
```cypher
MATCH (a:AgentCard)-[:RAN]->(t:Task)-[:MEASURES]->(m:PerformanceMetric)
WHERE m.type = 'confidence_score'
RETURN a.name, 
       count(t) as tasks_completed,
       ROUND(avg(m.value), 3) as avg_confidence
ORDER BY avg_confidence DESC;
```

#### Collaboration Network
```cypher
MATCH (a1:AgentCard)-[c:COLLABORATED_WITH]->(a2:AgentCard)
RETURN a1.name + ' → ' + a2.name as collaboration,
       c.effectiveness,
       c.interaction_type;
```

### Integration with A2A System

Your existing A2A system can now connect to Neo4j using:

```python
from a2a_neo4j_integration import A2ANeo4jIntegratedOrchestrator

orchestrator = A2ANeo4jIntegratedOrchestrator(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j", 
    neo4j_password="password123"
)

# Now all A2A operations will persist to Neo4j
result = await orchestrator.orchestrate_with_persistence(
    "Create a D&D character system",
    intent="mmorpg"
)
```

### Monitoring and Maintenance

- **Logs**: `docker logs neo4j-a2a`
- **Data Directory**: `./data/neo4j`
- **Backup**: Use Neo4j dump/restore commands
- **Performance**: Monitor via Neo4j Browser metrics

🎉 Your A2A system now has enterprise-grade graph database persistence!
EOF

echo ""
echo "==============================================="
echo "🎉 A2A NEO4J SETUP COMPLETE!"
echo "==============================================="
echo ""
echo "✅ Neo4j Enterprise is running with APOC & GDS plugins"
echo "✅ A2A schema and sample data populated"
echo "✅ System verified and ready for use"
echo ""
echo "🌐 Access Neo4j Browser: http://localhost:7474"
echo "🔐 Username: neo4j | Password: password123"
echo ""
echo "📖 Quick start guide created: NEO4J_QUICK_START.md"
echo ""
echo "🚀 Your A2A system now has persistent graph database storage!"
echo "==============================================="