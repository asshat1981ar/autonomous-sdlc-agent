#!/bin/bash

# GitHub Repository Setup Script
set -e

echo "🚀 GitHub Repository Setup for Autonomous SDLC Agent Platform"
echo "=============================================================="

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -f "main.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo ""
echo "📋 Pre-Push Validation"
echo "======================"

# Run quick validation
if [ -f "scripts/quick-test.sh" ]; then
    echo "Running quick validation..."
    ./scripts/quick-test.sh
else
    echo "⚠️ Quick test script not found, continuing..."
fi

echo ""
echo "🔍 Checking Git Configuration"
echo "============================="

# Check git configuration
if git config user.name && git config user.email; then
    echo "✅ Git user configuration:"
    echo "   Name: $(git config user.name)"
    echo "   Email: $(git config user.email)"
else
    echo "⚠️ Git user not configured. Setting up..."
    git config --global user.email "westonaaron675@gmail.com"
    git config --global user.name "asshat1981ar"
    echo "✅ Git user configured"
fi

echo ""
echo "🌐 Checking Remote Repository"
echo "============================="

# Check remote repository
if git remote get-url origin &>/dev/null; then
    echo "✅ Remote origin configured:"
    echo "   $(git remote get-url origin)"
else
    echo "⚠️ Adding remote repository..."
    git remote add origin https://github.com/asshat1981ar/autonomous-sdlc-agent.git
    echo "✅ Remote repository added"
fi

echo ""
echo "📦 Repository Status"
echo "==================="

# Show repository status
echo "Current branch: $(git branch --show-current)"
echo "Files ready for push:"
git ls-files | head -10
if [ $(git ls-files | wc -l) -gt 10 ]; then
    echo "... and $(($(git ls-files | wc -l) - 10)) more files"
fi

echo ""
echo "🎯 What happens next:"
echo "===================="
echo ""
echo "1. 📝 Create GitHub Repository:"
echo "   - Go to: https://github.com/new"
echo "   - Repository name: autonomous-sdlc-agent"
echo "   - Description: Multi-agent autonomous SDLC platform with AI orchestration"
echo "   - Set to PUBLIC (for free GitHub Container Registry)"
echo "   - ✅ Initialize with README: NO (we have our own)"
echo "   - ✅ Add .gitignore: NO (we have our own)"
echo "   - ✅ Choose a license: NO (or add later)"
echo "   - Click 'Create repository'"
echo ""
echo "2. 🚀 Push Code to GitHub:"
echo "   git push -u origin main"
echo ""
echo "3. ⚡ Automatic CI/CD Pipeline:"
echo "   - GitHub Actions will automatically start"
echo "   - Tests will run (Python + Node.js)"
echo "   - Docker images will be built and pushed to ghcr.io"
echo "   - Check: https://github.com/asshat1981ar/autonomous-sdlc-agent/actions"
echo ""
echo "4. 📦 Access Container Images:"
echo "   - Backend: ghcr.io/asshat1981ar/autonomous-sdlc-agent/backend:latest"
echo "   - Frontend: ghcr.io/asshat1981ar/autonomous-sdlc-agent/frontend:latest"
echo ""
echo "5. 🔧 Optional Configuration:"
echo "   - Add API keys to GitHub Secrets (Repository Settings > Secrets)"
echo "   - GEMINI_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY, BLACKBOX_API_KEY"
echo ""
echo "🎉 Your autonomous SDLC platform will be live and ready!"
echo ""
echo "Need help? Check:"
echo "- 📖 QUICK_START.md"
echo "- 🚀 DEPLOYMENT.md"
echo "- 📊 README.md"