#!/bin/bash
# Setup script for free AI APIs

echo "🚀 Setting up Free AI APIs for A2A Framework"

# OpenAI Free Tier Setup
echo "📝 OpenAI API Setup:"
echo "1. Visit: https://platform.openai.com/api-keys"
echo "2. Create account (free \$5 credit)"
echo "3. Generate API key"
echo "4. Export: export OPENAI_API_KEY='sk-...'"
echo ""

# Anthropic Claude Free Tier Setup  
echo "🤖 Anthropic Claude API Setup:"
echo "1. Visit: https://console.anthropic.com/"
echo "2. Create account (free credits available)"
echo "3. Generate API key"
echo "4. Export: export ANTHROPIC_API_KEY='sk-ant-...'"
echo ""

# Google Gemini Free Tier Setup
echo "🔍 Google Gemini API Setup:"
echo "1. Visit: https://makersuite.google.com/app/apikey"
echo "2. Create Google account"
echo "3. Generate API key (60 requests/minute free)"
echo "4. Export: export GOOGLE_API_KEY='AI...'"
echo ""

# BlackBox AI (Already configured)
echo "⚡ BlackBox AI: Already configured with your API key!"
echo ""

echo "💡 After setting environment variables, restart the server:"
echo "python3 multi_ai_a2a_server.py"
echo ""

echo "🎯 Test all providers with:"
echo "curl -X POST http://localhost:5001/api/a2a/process -H 'Content-Type: application/json' -d '{\"message\": \"Create a Hello World app\"}'"