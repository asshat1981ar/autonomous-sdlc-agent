#!/usr/bin/env python3
"""
Simple Flask application runner for testing without dependencies
"""
import os
import sys

# Simple HTTP server as fallback
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
from threading import Thread
import time

def start_simple_server():
    """Start a simple HTTP server on port 3000 for frontend"""
    os.chdir('.')
    
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/index.html'
            return SimpleHTTPRequestHandler.do_GET(self)
    
    try:
        with socketserver.TCPServer(("", 3000), Handler) as httpd:
            print("🌐 Frontend server running at http://localhost:3000")
            httpd.serve_forever()
    except Exception as e:
        print(f"Frontend server error: {e}")

def start_backend():
    """Start a simple backend API server"""
    try:
        # Try to import Flask
        from flask import Flask, jsonify
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/api/health')
        def health():
            return jsonify({"status": "healthy", "service": "SDLC Orchestrator"})
        
        @app.route('/api/agents')
        def agents():
            return jsonify({
                "agents": [
                    {"id": "claude", "name": "Claude", "status": "active"},
                    {"id": "gemini", "name": "Gemini", "status": "active"},
                    {"id": "openai", "name": "OpenAI", "status": "active"}
                ]
            })
        
        print("🚀 Backend API running at http://localhost:5000")
        print("🌐 Also accessible at http://127.0.0.1:5000")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        
    except ImportError:
        # Fallback to simple HTTP server
        print("Flask not available, starting simple backend...")
        
        class APIHandler(SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/api/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(b'{"status": "healthy", "service": "SDLC Orchestrator"}')
                else:
                    self.send_response(404)
                    self.end_headers()
        
        with socketserver.TCPServer(("", 5000), APIHandler) as httpd:
            print("🚀 Simple backend running at http://localhost:5000")
            httpd.serve_forever()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='SDLC Orchestrator Simple Runner')
    parser.add_argument('--mode', choices=['api', 'frontend', 'both'], default='both',
                       help='Run mode: api (backend only), frontend (frontend only), both (default)')
    
    args = parser.parse_args()
    
    if args.mode == 'both':
        # Start frontend in background thread
        frontend_thread = Thread(target=start_simple_server, daemon=True)
        frontend_thread.start()
        time.sleep(1)  # Give frontend time to start
        
        # Start backend in main thread
        start_backend()
    elif args.mode == 'frontend':
        start_simple_server()
    else:
        start_backend()