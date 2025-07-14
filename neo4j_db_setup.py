"""
Neo4j Database Customization and Data Population Script

This script customizes the Neo4j database schema and populates it with initial data
for the Agent-to-Agent (A2A) communication pattern using the MCP server's Cypher tools.

Usage:
- Ensure the MCP server "mcp-neo4j-cypher" is running and accessible.
- Adjust MCP_SERVER_URL if needed.
- Run this script to set up constraints, indexes, and insert sample data.

"""

import json
import httpx

MCP_SERVER_URL = "http://localhost:8000/sse"  # Adjust if using SSE transport or other URL

def cypher_write_query(query: str, params: dict = None) -> dict:
    if params is None:
        params = {}

    payload = {
        "name": "write-neo4j-cypher",
        "arguments": {
            "query": query,
            "params": params
        }
    }

    with httpx.Client() as client:
        response = client.post(MCP_SERVER_URL, json=payload)
        response.raise_for_status()
        return response.json()

def setup_constraints():
    queries = [
        "CREATE CONSTRAINT IF NOT EXISTS ON (a:Agent) ASSERT a.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS ON (m:A2AMessage) ASSERT m.id IS UNIQUE",
    ]
    for q in queries:
        result = cypher_write_query(q)
        print(f"Constraint setup result: {result}")

def populate_sample_data():
    # Insert sample agents
    agents = [
        {"id": "orchestrator_core", "name": "Orchestrator Core"},
        {"id": "system_architect", "name": "System Architect"},
        {"id": "lead_developer", "name": "Lead Developer"},
    ]

    for agent in agents:
        query = """
        MERGE (a:Agent {id: $id})
        SET a.name = $name
        """
        result = cypher_write_query(query, agent)
        print(f"Inserted/updated agent {agent['id']}: {result}")

    # Insert a sample registration message
    import uuid
    from datetime import datetime

    message_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"

    query = """
    MERGE (msg:A2AMessage {id: $message_id})
    SET msg.thread_id = $message_id,
        msg.type = 'registration',
        msg.payload = $payload,
        msg.context = '{}',
        msg.timestamp = $timestamp
    MERGE (sender:Agent {id: $sender})
    MERGE (recipient:Agent {id: $recipient})
    MERGE (sender)-[:SENT]->(msg)
    MERGE (msg)-[:TO]->(recipient)
    """

    params = {
        "message_id": message_id,
        "sender": "system_architect",
        "recipient": "orchestrator_core",
        "payload": json.dumps({"capabilities": ["design", "review"], "model_id": "blackboxai/meta-llama/llama-3.3-70b-instruct:free"}),
        "timestamp": timestamp
    }

    result = cypher_write_query(query, params)
    print(f"Inserted sample registration message: {result}")

if __name__ == "__main__":
    print("Setting up Neo4j constraints...")
    setup_constraints()
    print("Populating sample data...")
    populate_sample_data()
    print("Neo4j database setup complete.")
