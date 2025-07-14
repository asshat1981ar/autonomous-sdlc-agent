# A2A Orchestrator API Reference

## Overview

Your A2A system provides three main API endpoints across different services. Here's the complete API reference for orchestrator access.

## Service Endpoints

### 1. Multi-AI A2A Framework (Port 5001)

**Base URL**: `http://localhost:5001`

#### Health Check
```bash
GET /api/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "Multi-AI A2A Framework",
  "providers": ["blackbox"],
  "agents": 5,
  "timestamp": 1752444682.6927016
}
```

#### Get Agents Status
```bash
GET /api/agents
```

**Response**:
```json
{
  "agents": [
    {
      "id": "planner",
      "name": "Project Planner", 
      "role": "planner",
      "provider": "blackbox",
      "model_id": "blackboxai/openai/gpt-4",
      "status": "active",
      "trust_score": 0.9,
      "last_active": 1752444746.675995
    }
    // ... other agents
  ]
}
```

#### Process A2A Task
```bash
POST /api/a2a/process
Content-Type: application/json

{
  "message": "Your task description here",
  "session_id": "optional_session_id"
}
```

**Response**:
```json
{
  "success": true,
  "session_id": "general_1752444720",
  "planning_response": "Detailed planning response...",
  "coding_response": "Complete code implementation...",
  "review_response": "Code review and analysis...",
  "consensus": {
    "consensus_reached": true,
    "confidence": 95.0,
    "agreement_level": "high",
    "participants": 3,
    "variance": 0.0
  },
  "timestamp": 1752444720.123
}
```

#### D&D MMORPG Specialized Orchestration
```bash
POST /api/dnd/orchestrate
Content-Type: application/json

{
  "message": "D&D MMORPG development task"
}
```

**Response**:
```json
{
  "session_id": "dnd_session_1752444720",
  "task": "Build D&D MMORPG...",
  "game_design": {
    "agent_id": "planner",
    "response": "Complete game design document..."
  },
  "implementation": {
    "agent_id": "coder", 
    "response": "Full code implementation..."
  },
  "balance_review": {
    "agent_id": "reviewer",
    "response": "Game balance analysis..."
  },
  "consensus": {
    "consensus_reached": true,
    "confidence": 95.0
  },
  "project_type": "dnd_mmorpg"
}
```

### 2. Official A2A Protocol (Port 5002)

**Base URL**: `http://localhost:5002`

#### Health Check
```bash
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "protocol": "A2A-1.0",
  "agents": 5,
  "timestamp": "2025-07-13T22:11:25.294173+00:00"
}
```

#### Agent Discovery
```bash
GET /agents
```

**Response**:
```json
{
  "agents": [
    {
      "name": "GameDesigner",
      "description": "Specialized in D&D MMORPG game design and balance",
      "version": "1.0.0",
      "capabilities": ["game_design", "balance_analysis", "mechanics_design", "progression_systems"],
      "endpoints": {
        "create_task": "/tasks",
        "get_task": "/tasks/{task_id}",
        "send_message": "/tasks/{task_id}/messages",
        "get_messages": "/tasks/{task_id}/messages"
      }
    }
    // ... other agents
  ]
}
```

#### Protocol Information
```bash
GET /
```

**Response**:
```json
{
  "protocol": "Agent-to-Agent (A2A) Protocol",
  "version": "1.0",
  "description": "Official A2A Protocol implementation for MMORPG development",
  "endpoints": {
    "GET /agents": "Discover available agents",
    "GET /health": "Service health check",
    "POST /collaborate": "Start agent collaboration", 
    "POST /mmorpg/develop": "MMORPG development orchestration"
  }
}
```

#### MMORPG Development Orchestration
```bash
POST /mmorpg/develop
Content-Type: application/json

{
  "project_description": "Your MMORPG project description"
}
```

**Response**:
```json
{
  "session_id": "uuid-session-id",
  "project_description": "Build D&D MMORPG...",
  "phases": {
    "game_design": {
      "task_id": "task-uuid",
      "agent": "game_designer",
      "response": "Comprehensive game design..."
    },
    "backend_architecture": {
      "task_id": "task-uuid", 
      "agent": "backend_dev",
      "response": "Backend architecture plan..."
    },
    "frontend_design": {
      "task_id": "task-uuid",
      "agent": "frontend_dev", 
      "response": "Frontend design plan..."
    },
    "qa_planning": {
      "task_id": "task-uuid",
      "agent": "qa_engineer",
      "response": "QA strategy..."
    },
    "devops_planning": {
      "task_id": "task-uuid",
      "agent": "devops",
      "response": "Deployment strategy..."
    }
  },
  "consensus": {
    "score": 95.0,
    "participants": 5,
    "successful_collaborations": 5,
    "protocol_compliance": true,
    "agreement_level": "high"
  },
  "protocol_version": "A2A-1.0"
}
```

### 3. IDE Interface (Port 5000)

**Base URL**: `http://localhost:5000`

#### Health Check
```bash
GET /api/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "Vibe-Code IDE Pro", 
  "features": ["A2A Framework", "Sandboxed Execution", "Multi-Agent Consensus"],
  "agents": 5,
  "timestamp": 1752446677.024842
}
```

#### Get Agents Status
```bash
GET /api/agents
```

#### Process A2A Task
```bash
POST /api/a2a/process
Content-Type: application/json

{
  "message": "Task description",
  "session_id": "optional"
}
```

#### Execute Code
```bash
POST /api/execute
Content-Type: application/json

{
  "code": "print('Hello, World!')"
}
```

**Response**:
```json
{
  "success": true,
  "output": "Hello, World!\n",
  "errors": null
}
```

#### Execute Terminal Command
```bash
POST /api/terminal
Content-Type: application/json

{
  "command": "ls -la"
}
```

**Response**:
```json
{
  "success": true,
  "output": "total 24\ndrwxr-xr-x...",
  "errors": null
}
```

#### Create Vibe Project
```bash
POST /api/vibe/create
Content-Type: application/json

{
  "name": "my_project",
  "type": "web_app",
  "description": "A simple web application"
}
```

**Response**:
```json
{
  "success": true,
  "project_name": "my_project",
  "project_type": "web_app",
  "session_id": "session_uuid",
  "structure": "Project structure plan...",
  "implementation": "Implementation code...",
  "review": "Code review...",
  "consensus": {
    "consensus_reached": true,
    "confidence": 95.0
  }
}
```

## Python SDK Usage Examples

### Basic A2A Orchestration

```python
import aiohttp
import asyncio

class A2AOrchestrator:
    def __init__(self):
        self.multi_ai_url = "http://localhost:5001"
        self.official_a2a_url = "http://localhost:5002"
        self.ide_url = "http://localhost:5000"
    
    async def process_task(self, task_description: str):
        """Process task using Multi-AI A2A Framework"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.multi_ai_url}/api/a2a/process",
                json={"message": task_description}
            ) as response:
                return await response.json()
    
    async def develop_mmorpg(self, project_description: str):
        """Develop MMORPG using Official A2A Protocol"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.official_a2a_url}/mmorpg/develop",
                json={"project_description": project_description}
            ) as response:
                return await response.json()
    
    async def create_project(self, name: str, project_type: str, description: str):
        """Create project using IDE interface"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.ide_url}/api/vibe/create",
                json={
                    "name": name,
                    "type": project_type, 
                    "description": description
                }
            ) as response:
                return await response.json()

# Usage
async def main():
    orchestrator = A2AOrchestrator()
    
    # Process general task
    result = await orchestrator.process_task("Create a Python calculator")
    print(f"Task completed with {result['consensus']['confidence']}% confidence")
    
    # Develop MMORPG
    mmorpg_result = await orchestrator.develop_mmorpg("D&D inspired MMORPG with classes")
    print(f"MMORPG development session: {mmorpg_result['session_id']}")
    
    # Create new project
    project_result = await orchestrator.create_project(
        "calculator_app", 
        "python", 
        "Scientific calculator with GUI"
    )
    print(f"Project created: {project_result['project_name']}")

# Run
asyncio.run(main())
```

### Advanced Cross-Service Orchestration

```python
class AdvancedA2AOrchestrator:
    async def comprehensive_development(self, project_description: str):
        """Use all A2A services for comprehensive development"""
        
        # Phase 1: Multi-AI analysis and planning
        multi_ai_result = await self.process_task(f"Analyze and plan: {project_description}")
        
        # Phase 2: Official A2A protocol development (if MMORPG)
        if "game" in project_description.lower() or "mmorpg" in project_description.lower():
            official_result = await self.develop_mmorpg(project_description)
        else:
            official_result = None
        
        # Phase 3: IDE project creation
        project_result = await self.create_project(
            "ai_generated_project",
            "full_stack",
            project_description
        )
        
        # Calculate combined consensus
        multi_ai_confidence = multi_ai_result.get("consensus", {}).get("confidence", 0)
        project_confidence = project_result.get("consensus", {}).get("confidence", 0)
        official_confidence = official_result.get("consensus", {}).get("score", 0) if official_result else 0
        
        combined_confidence = (multi_ai_confidence + project_confidence + official_confidence) / 3
        
        return {
            "project_description": project_description,
            "multi_ai_analysis": multi_ai_result,
            "official_a2a_development": official_result,
            "ide_project_creation": project_result,
            "combined_consensus": {
                "confidence": round(combined_confidence, 1),
                "services_used": 3 if official_result else 2,
                "agreement_level": "high" if combined_confidence > 80 else "medium"
            }
        }
```

## cURL Command Examples

### Quick Testing Commands

```bash
# Test Multi-AI A2A Framework
curl -X POST -H "Content-Type: application/json" \
  -d '{"message": "Create a REST API for user management"}' \
  http://localhost:5001/api/a2a/process

# Test Official A2A Protocol
curl -X POST -H "Content-Type: application/json" \
  -d '{"project_description": "Build a turn-based RPG game"}' \
  http://localhost:5002/mmorpg/develop

# Test IDE Interface
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "my_api", "type": "backend", "description": "User management API"}' \
  http://localhost:5000/api/vibe/create

# Check all service health
curl http://localhost:5001/api/health
curl http://localhost:5002/health  
curl http://localhost:5000/api/health
```

## Error Handling

All APIs return consistent error responses:

```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_TYPE",
  "timestamp": 1752444720.123
}
```

Common error codes:
- `INVALID_JSON`: Malformed JSON request
- `MISSING_PARAMETER`: Required parameter missing
- `API_TIMEOUT`: Request timeout
- `SERVICE_UNAVAILABLE`: Service temporarily unavailable
- `RATE_LIMITED`: Too many requests

## Rate Limits

- Multi-AI A2A Framework: 60 requests/minute
- Official A2A Protocol: 30 requests/minute  
- IDE Interface: 100 requests/minute

## Authentication

Currently, all services run without authentication for development. For production, implement JWT-based authentication:

```bash
# Example with authentication header
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{"message": "task"}' \
  http://localhost:5001/api/a2a/process
```

This API reference provides complete access to your A2A orchestrator system across all services.