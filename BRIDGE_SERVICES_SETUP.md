# 🌉 Bridge Services Setup Guide

## Enhanced Step 5: AI Service Bridges Integration

Instead of traditional API keys, this platform now integrates with your premium AI services through bridge connections:

### 🔗 Bridge Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SDLC Agent Platform                     │
├─────────────────────────────────────────────────────────────┤
│                    Bridge Manager                          │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Claude Code   │   Gemini CLI    │   GitHub Codex  │ Blackbox.ai │
│     Bridge      │     Bridge      │     Bridge      │   Bridge   │
└─────────────────┴─────────────────┴─────────────────────────┘
         │                 │                 │                │
         ▼                 ▼                 ▼                ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐
│   Claude Code   │ │   Gemini CLI    │ │  GitHub Copilot │ │ Blackbox.ai  │
│   (Your Sub)    │ │     (npx)       │ │    (Service)    │ │  (Premium)   │
└─────────────────┘ └─────────────────┘ └─────────────────┘ └──────────────┘
```

## 🎯 Bridge Service Configurations

### 1. Claude Code Bridge
**Your existing Claude subscription with Claude Code included**

```bash
# No additional setup needed - uses your existing Claude Code CLI
# Bridge automatically detects: claude-code command
# Provides: Advanced code analysis, generation, refactoring, debugging
```

**Features:**
- ✅ Advanced code analysis with detailed feedback
- ✅ Intelligent code generation with explanations
- ✅ Sophisticated refactoring suggestions
- ✅ Interactive debugging assistance
- ✅ Multi-language support with context awareness

### 2. Gemini CLI Bridge
**Google Gemini CLI integration**

```bash
# Automatic installation via NPX
npm install -g @google-ai/generativelanguage

# Or use directly via NPX (handled by bridge)
npx gemini-cli --version
```

**Setup:**
```bash
# Set your Gemini API key (if needed)
export GEMINI_API_KEY="your-gemini-api-key"
```

**Features:**
- ✅ High-performance code generation
- ✅ Natural language to code conversion
- ✅ Code optimization recommendations
- ✅ Multi-modal analysis capabilities

### 3. GitHub Codex Bridge
**GitHub Copilot/Codex integration**

```bash
# Set up GitHub authentication
export GITHUB_TOKEN="your-github-personal-access-token"
export GITHUB_COPILOT_TOKEN="your-copilot-token" # if separate
```

**Features:**
- ✅ Real-time code completion
- ✅ Context-aware suggestions
- ✅ Function generation from descriptions
- ✅ Code explanation and documentation
- ✅ Integrated with GitHub ecosystem

### 4. Blackbox.ai Premium Bridge
**Blackbox.ai premium service integration**

```bash
# Set up Blackbox.ai credentials
export BLACKBOX_API_KEY="your-blackbox-api-key"
export BLACKBOX_PREMIUM_KEY="your-premium-key"
```

**Features:**
- ✅ Advanced code analysis with security scanning
- ✅ Performance optimization recommendations
- ✅ Comprehensive code documentation generation
- ✅ Multi-language debugging assistance
- ✅ Premium-level AI capabilities

## 🚀 Quick Bridge Setup

### Environment Variables Setup

Create a `.env` file in your project root:

```bash
# Claude Code - Uses your existing subscription
# No additional configuration needed

# Gemini CLI (optional, for enhanced features)
GEMINI_API_KEY=your-gemini-api-key

# GitHub Copilot/Codex
GITHUB_TOKEN=your-github-personal-access-token
GITHUB_COPILOT_TOKEN=your-copilot-token

# Blackbox.ai Premium
BLACKBOX_API_KEY=your-blackbox-api-key
BLACKBOX_PREMIUM_KEY=your-premium-key
```

### Kubernetes Secrets (Production)

```bash
# Create bridge secrets
kubectl create secret generic bridge-secrets \
  --from-literal=GEMINI_API_KEY=your-key \
  --from-literal=GITHUB_TOKEN=your-token \
  --from-literal=GITHUB_COPILOT_TOKEN=your-copilot-token \
  --from-literal=BLACKBOX_API_KEY=your-blackbox-key \
  --from-literal=BLACKBOX_PREMIUM_KEY=your-premium-key \
  --namespace sdlc-agent
```

## 🔧 Bridge Service API Endpoints

### Initialize Bridges
```http
POST /api/bridges/initialize
```

### Get Bridge Status
```http
GET /api/bridges/status
```

### Enhanced Code Generation
```http
POST /api/bridges/generate-code
Content-Type: application/json

{
  "prompt": "Create a REST API for user management",
  "language": "python",
  "paradigm": "orchestra"
}
```

### Advanced Code Analysis
```http
POST /api/bridges/analyze-code
Content-Type: application/json

{
  "code": "your code here",
  "language": "python"
}
```

### Code Optimization
```http
POST /api/bridges/optimize-code
Content-Type: application/json

{
  "code": "your code here",
  "language": "python"
}
```

### Intelligent Debugging
```http
POST /api/bridges/debug-code
Content-Type: application/json

{
  "code": "your code here",
  "error_message": "NameError: name 'x' is not defined",
  "language": "python"
}
```

## 🎨 Frontend Integration

The React frontend automatically detects and utilizes bridge services:

```typescript
// Enhanced code generation with bridge services
const generateCode = async (prompt: string, language: string) => {
  const response = await fetch('/api/bridges/generate-code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt,
      language,
      paradigm: 'orchestra' // Uses multiple bridges
    })
  });
  
  const result = await response.json();
  
  if (result.success && result.result.enhanced_by_bridges) {
    // Bridge-enhanced response with multiple AI perspectives
    console.log('Generated with bridge services:', result.result);
  }
};
```

## 🧪 Testing Bridge Services

### Local Testing
```bash
# Test bridge initialization
curl -X POST http://localhost:5000/api/bridges/initialize

# Test bridge status
curl http://localhost:5000/api/bridges/status

# Test code generation
curl -X POST http://localhost:5000/api/bridges/generate-code \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello world function", "language": "python"}'
```

### Health Monitoring
```bash
# Check individual bridge health
curl http://localhost:5000/api/bridges/health
```

## 🔥 Bridge Service Benefits

### Multi-AI Collaboration
- **Orchestra Mode**: Coordinated responses from multiple bridges
- **Best Bridge Selection**: Automatic routing to optimal service
- **Fallback Support**: Graceful degradation when services unavailable

### Enhanced Capabilities
- **Claude Code**: Your premium subscription's advanced features
- **Gemini CLI**: Google's latest AI capabilities
- **GitHub Codex**: GitHub's ecosystem integration
- **Blackbox.ai**: Premium analysis and optimization

### Production Ready
- **Health Monitoring**: Continuous service health checks
- **Rate Limiting**: Built-in request management
- **Error Handling**: Graceful error recovery
- **Async Processing**: Non-blocking operations

## 🛠️ Bridge Service Commands

### Manual Bridge Testing

```bash
# Test Claude Code bridge
curl -X POST http://localhost:5000/api/bridges/claude-code/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello(): print(\"world\")", "language": "python"}'

# Test Gemini CLI bridge
curl -X POST http://localhost:5000/api/bridges/gemini-cli/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "fibonacci function", "language": "python"}'

# Test GitHub Codex bridge
curl -X POST http://localhost:5000/api/bridges/github-codex/complete \
  -H "Content-Type: application/json" \
  -d '{"code": "def factorial(n):", "language": "python"}'

# Test Blackbox.ai bridge
curl -X POST http://localhost:5000/api/bridges/blackbox-ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "def divide(a, b): return a/b", "language": "python"}'
```

## 🎉 What You Get

### Unified AI Platform
- **4 Premium AI Services** integrated seamlessly
- **Intelligent Routing** to best service for each task
- **Multi-Bridge Collaboration** for complex tasks
- **Fallback Support** ensuring reliability

### Advanced Features
- **Real-time Code Completion** (GitHub Codex)
- **Advanced Analysis** (Claude Code + Blackbox.ai)
- **Optimization Recommendations** (All bridges)
- **Security Scanning** (Blackbox.ai Premium)
- **Multi-language Support** (All bridges)

### Enterprise Grade
- **Health Monitoring** for all bridges
- **Rate Limiting** and error handling
- **Kubernetes Ready** with secret management
- **Async Processing** for performance

---

**🌉 Your autonomous SDLC platform now bridges the gap between multiple premium AI services, creating a unified, powerful development experience!**