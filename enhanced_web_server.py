#!/usr/bin/env python3
"""
Enhanced web server with BlackBox AI integration and Vibe-Code support
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import mimetypes
import asyncio
import threading
import time
from urllib.parse import urlparse, parse_qs
import logging

# Import our enhanced orchestrator
from enhanced_ai_orchestrator import vibe_orchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedWebHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.loop = None
        super().__init__(*args, **kwargs)
    
    def _get_event_loop(self):
        """Get or create event loop for async operations"""
        if self.loop is None or self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        return self.loop
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Serve frontend files
        if path == '/' or path == '/index.html':
            self.serve_file('static/enhanced_index.html', 'text/html')
        elif path.startswith('/static/'):
            file_path = path[1:]  # Remove leading slash
            self.serve_file(file_path)
        
        # API endpoints
        elif path == '/api/health':
            self.send_json_response({
                "status": "healthy", 
                "service": "Enhanced SDLC Orchestrator",
                "features": ["BlackBox AI", "Multi-Agent", "Vibe-Code"],
                "timestamp": time.time()
            })
        
        elif path == '/api/models':
            # Get available models
            loop = self._get_event_loop()
            models_data = loop.run_until_complete(self._get_models())
            self.send_json_response(models_data)
        
        elif path == '/api/agents':
            self.send_json_response({
                "agents": [
                    {"id": "planner", "name": "Project Planner", "status": "active", "description": "Analyzes requirements and creates development plans"},
                    {"id": "coder", "name": "Code Generator", "status": "active", "description": "Implements solutions with high-quality code"},
                    {"id": "reviewer", "name": "Code Reviewer", "status": "active", "description": "Reviews code quality and suggests improvements"},
                    {"id": "speed_agent", "name": "Speed Agent", "status": "active", "description": "Provides rapid responses and real-time interaction"},
                    {"id": "specialist", "name": "Deep Specialist", "status": "active", "description": "Handles complex reasoning and analysis"}
                ]
            })
        
        elif path.startswith('/api/session/'):
            # Handle session status requests
            session_id = path.split('/')[-1]
            loop = self._get_event_loop()
            session_data = loop.run_until_complete(self._get_session_status(session_id))
            self.send_json_response(session_data)
        
        else:
            self.send_json_response({"error": "Not found"}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_json_response({"error": "Invalid JSON"}, 400)
            return
        
        if path == '/api/vibe/create':
            # Create new vibe session
            loop = self._get_event_loop()
            result = loop.run_until_complete(self._create_vibe_session(data))
            self.send_json_response(result)
        
        elif path == '/api/vibe/process':
            # Process vibe request
            loop = self._get_event_loop()
            result = loop.run_until_complete(self._process_vibe_request(data))
            self.send_json_response(result)
        
        elif path == '/api/agent/run':
            # Run specific agent
            loop = self._get_event_loop()
            result = loop.run_until_complete(self._run_specific_agent(data))
            self.send_json_response(result)
        
        else:
            self.send_json_response({"error": "Endpoint not found"}, 404)
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    async def _get_models(self):
        """Get available models"""
        try:
            return vibe_orchestrator.get_available_models()
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return {"error": str(e)}
    
    async def _create_vibe_session(self, data):
        """Create new vibe session"""
        try:
            project_description = data.get('description', '')
            agents = data.get('agents', None)
            
            session_id = await vibe_orchestrator.create_vibe_session(
                project_description, agents
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "message": "Vibe session created successfully"
            }
        except Exception as e:
            logger.error(f"Error creating vibe session: {e}")
            return {"success": False, "error": str(e)}
    
    async def _process_vibe_request(self, data):
        """Process vibe request"""
        try:
            session_id = data.get('session_id', '')
            user_input = data.get('input', '')
            
            if not session_id or not user_input:
                return {"success": False, "error": "Missing session_id or input"}
            
            result = await vibe_orchestrator.process_vibe_request(session_id, user_input)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Error processing vibe request: {e}")
            return {"success": False, "error": str(e)}
    
    async def _run_specific_agent(self, data):
        """Run specific agent"""
        try:
            agent_type = data.get('agent', '')
            prompt = data.get('prompt', '')
            session_id = data.get('session_id', '')
            
            if not agent_type or not prompt:
                return {"success": False, "error": "Missing agent or prompt"}
            
            result = await vibe_orchestrator._run_agent(agent_type, prompt, session_id)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_session_status(self, session_id):
        """Get session status"""
        try:
            return await vibe_orchestrator.get_session_status(session_id)
        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return {"error": str(e)}
    
    def serve_file(self, file_path, content_type=None):
        """Serve static files"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            if not content_type:
                content_type, _ = mimetypes.guess_type(file_path)
                content_type = content_type or 'application/octet-stream'
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_json_response({"error": "File not found"}, 404)
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

def run_server(host='0.0.0.0', port=5000):
    """Run the enhanced web server"""
    server = HTTPServer((host, port), EnhancedWebHandler)
    print("🚀 Enhanced SDLC Orchestrator running at:")
    print(f"   http://localhost:{port}")
    print(f"   http://127.0.0.1:{port}")
    print(f"   http://0.0.0.0:{port}")
    print("\n🎯 New Features:")
    print("   • BlackBox AI Integration with 15+ models")
    print("   • Multi-agent orchestration (Planner, Coder, Reviewer)")
    print("   • Vibe-Code natural language prototyping")
    print("   • A2A framework support")
    print("\n📡 API Endpoints:")
    print("   GET  /api/health - Service status")
    print("   GET  /api/models - Available AI models")
    print("   GET  /api/agents - Available agents")
    print("   POST /api/vibe/create - Create vibe session")
    print("   POST /api/vibe/process - Process vibe request")
    print("   POST /api/agent/run - Run specific agent")
    print("   GET  /api/session/{id} - Get session status")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server shutting down...")
        server.shutdown()

if __name__ == "__main__":
    run_server()