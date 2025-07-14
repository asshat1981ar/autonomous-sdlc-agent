"""
A2A Communication Pattern Implementation using Neo4j MCP Server Cypher Tools

This module provides functions to log A2A messages, agent registration, task assignment,
results, feedback, and errors into Neo4j using the MCP server's Cypher tools.

Requires:
- MCP server "mcp-neo4j-cypher" running and accessible
- Python 3.10+
- httpx for HTTP requests to MCP server (or use MCP SDK if available)

"""

import json
import uuid
import httpx
from datetime import datetime

MCP_SERVER_URL = "http://localhost:8000/sse"  # Adjust if using SSE transport or other URL

def generate_uuid() -> str:
    return str(uuid.uuid4())

def current_timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"

def cypher_write_query(query: str, params: dict = None) -> dict:
    """
    Execute a write Cypher query using the MCP server's write-neo4j-cypher tool.
    """
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

def cypher_read_query(query: str, params: dict = None) -> dict:
    """
    Execute a read Cypher query using the MCP server's read-neo4j-cypher tool.
    """
    if params is None:
        params = {}

    payload = {
        "name": "read-neo4j-cypher",
        "arguments": {
            "query": query,
            "params": params
        }
    }

    with httpx.Client() as client:
        response = client.post(MCP_SERVER_URL, json=payload)
        response.raise_for_status()
        return response.json()

def log_a2a_message(message_id: str, thread_id: str, sender: str, recipient: str,
                    msg_type: str, payload: dict, context: dict, timestamp: str):
    """
    Log an A2A message as a node and relationships in Neo4j.
    """
    query = """
    MERGE (msg:A2AMessage {id: $message_id})
    SET msg.thread_id = $thread_id,
        msg.type = $msg_type,
        msg.payload = $payload,
        msg.context = $context,
        msg.timestamp = $timestamp
    MERGE (sender:Agent {id: $sender})
    MERGE (recipient:Agent {id: $recipient})
    MERGE (sender)-[:SENT]->(msg)
    MERGE (msg)-[:TO]->(recipient)
    """
    params = {
        "message_id": message_id,
        "thread_id": thread_id,
        "sender": sender,
        "recipient": recipient,
        "msg_type": msg_type,
        "payload": json.dumps(payload),
        "context": json.dumps(context),
        "timestamp": timestamp
    }
    return cypher_write_query(query, params)

def register_agent(agent_id: str, capabilities: dict, model_id: str):
    """
    Register an agent node in Neo4j.
    """
    message_id = generate_uuid()
    timestamp = current_timestamp()
    payload = {
        "capabilities": capabilities,
        "model_id": model_id
    }
    context = {}
    return log_a2a_message(message_id, message_id, agent_id, "orchestrator_core",
                           "registration", payload, context, timestamp)

def assign_task(message_id: str, sender: str, recipient: str, task_type: str,
                prompt: str, context: dict):
    """
    Log a task assignment message.
    """
    timestamp = current_timestamp()
    payload = {
        "task_type": task_type,
        "prompt": prompt
    }
    thread_id = message_id  # Use message_id as thread_id for new tasks
    return log_a2a_message(message_id, thread_id, sender, recipient,
                           "task_assignment", payload, context, timestamp)

def task_result(message_id: str, sender: str, recipient: str, task_type: str,
                result: dict, context: dict):
    """
    Log a task result message.
    """
    timestamp = current_timestamp()
    payload = {
        "task_type": task_type,
        "result": result
    }
    thread_id = message_id
    return log_a2a_message(message_id, thread_id, sender, recipient,
                           "task_result", payload, context, timestamp)

def send_feedback(message_id: str, sender: str, recipient: str, feedback: dict, context: dict):
    """
    Log a feedback message.
    """
    timestamp = current_timestamp()
    payload = {
        "feedback": feedback
    }
    thread_id = message_id
    return log_a2a_message(message_id, thread_id, sender, recipient,
                           "feedback", payload, context, timestamp)

def send_error(message_id: str, sender: str, recipient: str, error_info: dict, context: dict):
    """
    Log an error message.
    """
    timestamp = current_timestamp()
    payload = {
        "error_info": error_info
    }
    thread_id = message_id
    return log_a2a_message(message_id, thread_id, sender, recipient,
                           "error", payload, context, timestamp)

# Additional functions for querying, agent lifecycle, orchestration can be added here.
