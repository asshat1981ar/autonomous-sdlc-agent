#!/bin/bash
# Setup script for CLI-based AI access

echo "🔧 Setting up CLI-based AI access for SDLC Orchestrator"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check and setup GitHub CLI with Copilot
echo "📋 Checking GitHub CLI and Copilot..."
if command_exists gh; then
    echo "✅ GitHub CLI found"
    
    # Check if Copilot extension is installed
    if gh extension list | grep -q copilot; then
        echo "✅ GitHub Copilot extension found"
    else
        echo "⚠️  Installing GitHub Copilot extension..."
        gh extension install github/gh-copilot
    fi
else
    echo "❌ GitHub CLI not found. Please install:"
    echo "   Windows: winget install --id GitHub.cli"
    echo "   Mac: brew install gh"
    echo "   Linux: https://cli.github.com/manual/installation"
fi

# Check for Claude CLI
echo "📋 Checking Claude CLI..."
if command_exists claude-code; then
    echo "✅ Claude Code CLI found"
elif command_exists claude; then
    echo "✅ Claude CLI found"
else
    echo "❌ Claude CLI not found. Please install:"
    echo "   Visit: https://claude.ai/cli"
    echo "   Or check your Claude subscription for CLI access"
fi

# Check for Blackbox CLI
echo "📋 Checking Blackbox CLI..."
if command_exists blackbox; then
    echo "✅ Blackbox CLI found"
else
    echo "❌ Blackbox CLI not found. Please install:"
    echo "   Visit: https://blackbox.ai/"
    echo "   Install CLI tools from your Blackbox account"
fi

# Create environment configuration
echo "📝 Creating CLI configuration..."
cat > .env.cli << EOF
# CLI-based AI Configuration
AI_MODE=cli
AI_FALLBACK_MODE=mock

# GitHub Configuration (for Copilot access)
# Set this if you have a GitHub token for API access
# GITHUB_TOKEN=your_github_token_here

# CLI Command Paths (adjust if needed)
BLACKBOX_CLI_COMMAND=blackbox
CLAUDE_CLI_COMMAND=claude-code
GITHUB_CLI_COMMAND=gh

# Timeout settings (seconds)
CLI_TIMEOUT=30
CLI_MAX_RETRIES=3
EOF

echo "✅ Created .env.cli configuration file"

# Update main.py to use CLI providers
echo "🔄 Updating main.py for CLI integration..."
cat > main_cli.py << 'EOF'
import os
import sys
# Load CLI environment
from dotenv import load_dotenv
load_dotenv('.env.cli')

# Import CLI orchestrator instead of regular one
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from cli_ai_providers import cli_orchestrator

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Load secret key from environment variable for security
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')

# Enable CORS for all routes
CORS(app)

@app.route('/api/health', methods=['GET'])
async def health_check():
    """Health check using CLI providers"""
    try:
        health = await cli_orchestrator.health_check()
        return jsonify(health)
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'method': 'cli'
        }), 500

@app.route('/api/demo', methods=['POST'])
async def demo_collaboration():
    """Demo collaboration using CLI providers"""
    try:
        from flask import request
        data = request.get_json()
        
        result = await cli_orchestrator.collaborate(
            session_id='demo',
            paradigm=data.get('paradigm', 'orchestra'),
            task=data.get('task', 'Create a simple function'),
            agents=data.get('agents', ['mock']),
            context=data.get('context', {})
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'method': 'cli'
        }), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if not static_folder_path:
        return "Static folder not configured", 404

    requested_path = os.path.join(static_folder_path, path)
    if path and os.path.exists(requested_path):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
EOF

echo "✅ Created main_cli.py for CLI-based operation"

# Create test script
echo "🧪 Creating test script..."
cat > test_cli_setup.py << 'EOF'
#!/usr/bin/env python3
import asyncio
import subprocess
import sys

async def test_cli_tools():
    """Test available CLI tools"""
    print("🧪 Testing CLI Tools")
    print("=" * 40)
    
    tools = [
        ("GitHub CLI", "gh --version"),
        ("GitHub Copilot", "gh copilot --help"),
        ("Claude CLI", "claude --version"),
        ("Claude Code CLI", "claude-code --version"),
        ("Blackbox CLI", "blackbox --version")
    ]
    
    results = {}
    
    for name, command in tools:
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print(f"✅ {name}: Available")
                results[name] = True
            else:
                print(f"❌ {name}: Error")
                results[name] = False
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"❌ {name}: Not found")
            results[name] = False
    
    print("\n📊 Summary:")
    available = sum(results.values())
    total = len(results)
    print(f"Available tools: {available}/{total}")
    
    if available > 0:
        print("✅ You can run the CLI-based orchestrator!")
    else:
        print("⚠️  No CLI tools found. Will use mock providers.")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_cli_tools())
EOF

chmod +x test_cli_setup.py

echo "✅ Created test_cli_setup.py"

# Create simple run script
echo "🚀 Creating simplified run script..."
cat > run_with_cli.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting SDLC Orchestrator with CLI-based AI"

# Load CLI environment
export $(cat .env.cli | xargs)

# Test CLI tools first
echo "🧪 Testing CLI tools..."
python test_cli_setup.py

echo ""
echo "🚀 Starting application..."
python main_cli.py
EOF

chmod +x run_with_cli.sh

echo ""
echo "🎉 CLI Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Install missing CLI tools (see messages above)"
echo "2. Test setup: python test_cli_setup.py"
echo "3. Run with CLI: ./run_with_cli.sh"
echo "   or: python main_cli.py"
echo ""
echo "🔧 Configuration files created:"
echo "   - .env.cli (environment settings)"
echo "   - main_cli.py (CLI-enabled main app)"
echo "   - test_cli_setup.py (test CLI tools)"
echo "   - run_with_cli.sh (simplified run script)"
