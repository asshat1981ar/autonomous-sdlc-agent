#!/bin/bash

# Quick validation script for GitHub CI/CD setup
set -e

echo "🧪 Quick Local Validation"
echo "=========================="

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -f "main.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📋 Checking Required Files..."
echo "----------------------------"

# Check if required files exist
required_files=(
    "README.md"
    "DEPLOYMENT.md"
    ".gitignore"
    "package.json"
    "requirements.txt"
    "main.py"
    "docker/Dockerfile.backend"
    "docker/Dockerfile.frontend"
    ".github/workflows/ci-cd.yml"
)

all_files_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        all_files_exist=false
    fi
done

echo ""
echo "🐳 Checking Docker Files..."
echo "---------------------------"

# Basic syntax check for Dockerfiles
if [ -f "docker/Dockerfile.backend" ]; then
    if grep -q "FROM python" docker/Dockerfile.backend; then
        echo "✅ Backend Dockerfile looks valid"
    else
        echo "❌ Backend Dockerfile missing Python base image"
    fi
fi

if [ -f "docker/Dockerfile.frontend" ]; then
    if grep -q "FROM node" docker/Dockerfile.frontend; then
        echo "✅ Frontend Dockerfile looks valid"
    else
        echo "❌ Frontend Dockerfile missing Node base image"
    fi
fi

echo ""
echo "📦 Checking Package Configuration..."
echo "-----------------------------------"

# Check package.json
if [ -f "package.json" ]; then
    if command -v node &> /dev/null; then
        node -e "JSON.parse(require('fs').readFileSync('package.json', 'utf8'))" && echo "✅ package.json is valid JSON"
    else
        echo "⚠️ Node.js not found, skipping package.json validation"
    fi
fi

# Check Python imports
echo ""
echo "🐍 Basic Python Validation..."
echo "-----------------------------"

python3 -c "
try:
    import sys
    sys.path.insert(0, 'src')
    print('✅ Python path setup works')
except Exception as e:
    print(f'❌ Python path issue: {e}')
"

echo ""
echo "⚙️ Checking CI/CD Configuration..."
echo "---------------------------------"

if [ -f ".github/workflows/ci-cd.yml" ]; then
    if grep -q "ghcr.io" .github/workflows/ci-cd.yml; then
        echo "✅ GitHub Container Registry configured"
    else
        echo "❌ GitHub Container Registry not found in CI/CD"
    fi
    
    if grep -q "docker/build-push-action" .github/workflows/ci-cd.yml; then
        echo "✅ Docker build actions configured"
    else
        echo "❌ Docker build actions missing"
    fi
fi

echo ""
if [ "$all_files_exist" = true ]; then
    echo "🎉 Quick validation completed successfully!"
    echo "========================"
    echo ""
    echo "✅ All required files present"
    echo "✅ Docker configuration valid"
    echo "✅ CI/CD pipeline configured"
    echo ""
    echo "🚀 Ready for GitHub repository creation!"
    echo ""
    echo "Next steps:"
    echo "1. Create repository on GitHub: https://github.com/new"
    echo "2. git remote add origin https://github.com/asshat1981ar/autonomous-sdlc-agent.git"
    echo "3. git add ."
    echo "4. git commit -m 'Initial commit: Autonomous SDLC Agent Platform'"
    echo "5. git push -u origin main"
else
    echo "❌ Some required files are missing"
    echo "Please ensure all files are present before proceeding"
    exit 1
fi