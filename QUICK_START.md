# 🚀 Quick Start Guide - Autonomous SDLC Agent Platform

## GitHub-Only Setup (Recommended)

### 1. Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Repository name: `autonomous-sdlc-agent`
3. Description: `Multi-agent autonomous SDLC platform with AI orchestration`
4. Set to Public (for free GitHub Container Registry)
5. Click "Create repository"

### 2. Push Code to GitHub

```bash
# Configure git (if not done already)
git config --global user.email "westonaaron675@gmail.com"
git config --global user.name "asshat1981ar"

# Add remote origin
git remote add origin https://github.com/asshat1981ar/autonomous-sdlc-agent.git

# Stage all files
git add .

# Commit changes
git commit -m "Initial commit: Autonomous SDLC Agent Platform

🤖 Multi-agent AI orchestration platform
🔄 5 collaboration paradigms (Orchestra, Mesh, Swarm, Weaver, Ecosystem)
🐳 Docker containerization ready
☸️ Kubernetes deployment with Helm
🏗️ GitHub Actions CI/CD pipeline
📊 Monitoring and observability

🚀 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
git push -u origin main
```

### 3. Automatic CI/CD Pipeline

Once pushed, GitHub Actions will automatically:

1. ✅ **Test** - Run Python and Node.js tests
2. 🔍 **Lint** - Check code quality
3. 🐳 **Build** - Create Docker images
4. 📦 **Push** - Upload to GitHub Container Registry
5. 🎉 **Ready** - Images available for deployment

### 4. Access Container Images

After successful build, your images will be available at:
- **Backend**: `ghcr.io/asshat1981ar/autonomous-sdlc-agent/backend:latest`
- **Frontend**: `ghcr.io/asshat1981ar/autonomous-sdlc-agent/frontend:latest`

### 5. Quick Local Test

```bash
# Run quick validation
./scripts/quick-test.sh

# Or test with Docker
docker run -p 5000:5000 ghcr.io/asshat1981ar/autonomous-sdlc-agent/backend:latest
docker run -p 80:80 ghcr.io/asshat1981ar/autonomous-sdlc-agent/frontend:latest
```

## 🎯 What You Get

### Multi-Agent AI Platform
- **5 Collaboration Paradigms**: Orchestra, Mesh, Swarm, Weaver, Ecosystem
- **AI Provider Support**: Gemini, Claude, OpenAI, Blackbox
- **Real-time Orchestration**: Dynamic agent coordination
- **Intelligent Recommendations**: AI-driven paradigm selection

### Production-Ready Infrastructure
- **Docker Containers**: Multi-stage optimized builds
- **Kubernetes Ready**: Helm charts included
- **CI/CD Pipeline**: Automated testing and deployment
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Security**: Non-root containers, security contexts

### Enterprise Features
- **Autoscaling**: Horizontal and vertical pod autoscaling
- **Health Checks**: Comprehensive monitoring endpoints
- **Secrets Management**: Kubernetes secrets integration
- **Multi-Environment**: Development, staging, production configs

## 🔧 Bridge Services Configuration

### Premium AI Service Integration

This platform now integrates with your premium AI subscriptions through bridge services:

```bash
# Claude Code Bridge - Uses your existing Claude subscription
# No additional setup needed!

# Gemini CLI Bridge (optional enhancement)
GEMINI_API_KEY=your-gemini-key

# GitHub Codex Bridge (uses your GitHub Copilot subscription)
GITHUB_TOKEN=your-github-personal-access-token
GITHUB_COPILOT_TOKEN=your-copilot-token

# Blackbox.ai Premium Bridge
BLACKBOX_API_KEY=your-blackbox-api-key
BLACKBOX_PREMIUM_KEY=your-premium-key
```

### Bridge Services Features

🌉 **Claude Code Bridge**: Your existing subscription's advanced features
🚀 **Gemini CLI Bridge**: Google's latest AI via NPX integration  
🐙 **GitHub Codex Bridge**: GitHub Copilot integration
⚫ **Blackbox.ai Bridge**: Premium analysis and optimization

### Optional Configuration

```bash
# Database (defaults to SQLite)
DATABASE_URL=sqlite:///app/database/app.db

# Security
SECRET_KEY=your-secret-key

# Logging
LOG_LEVEL=INFO
```

## 📊 Monitoring

### Health Check Endpoints

```bash
# Backend health
curl http://localhost:5000/api/health

# Frontend health
curl http://localhost/health

# Bridge services health
curl http://localhost:5000/api/bridges/health

# Bridge status
curl http://localhost:5000/api/bridges/status
```

### Enhanced Metrics

- **Application Performance**: Request latency, throughput
- **AI Collaboration**: Success rates, paradigm usage
- **Bridge Services**: Health, response times, success rates
- **Infrastructure**: CPU, memory, network usage
- **Business Metrics**: User sessions, project completions

## 🚀 Next Steps

1. **Create GitHub Repository** (Manual step)
2. **Push Code** (Commands above)
3. **Configure Bridge Services** (See BRIDGE_SERVICES_SETUP.md)
4. **Deploy to Kubernetes** (Optional - see DEPLOYMENT.md)
5. **Set Up Monitoring** (Prometheus + Grafana)

## 📞 Support

- **GitHub Issues**: [Report bugs](https://github.com/asshat1981ar/autonomous-sdlc-agent/issues)
- **Documentation**: [Full deployment guide](DEPLOYMENT.md)
- **Bridge Services**: [Setup guide](BRIDGE_SERVICES_SETUP.md)
- **Kubernetes Guide**: [Advanced deployment](DEPLOYMENT.md#kubernetes-deployment)

---

**🌉 Your autonomous SDLC platform with premium AI bridge services is ready to revolutionize software development!**