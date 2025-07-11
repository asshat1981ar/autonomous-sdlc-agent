# 🚀 Running the Autonomous SDLC Agent Platform

## 📋 Prerequisites

### Required Software
- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Node.js** (version 18+ for frontend development)
- **Python** (version 3.11+ for backend development)
- **Git** (for repository management)

### API Keys (Optional but Recommended)
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"  
export GEMINI_API_KEY="your-gemini-api-key"
export BLACKBOX_API_KEY="your-blackbox-api-key"
```

## 🎯 Quick Start (Recommended)

### 1. **Clone and Setup**
```bash
# Clone the repository
git clone https://github.com/asshat1981ar/autonomous-sdlc-agent.git
cd autonomous-sdlc-agent

# Make deployment script executable (Linux/Mac)
chmod +x deploy.sh
```

### 2. **Run with Deploy Script**
```bash
# Development environment with all services
./deploy.sh --environment development

# Or on Windows
bash deploy.sh --environment development
```

### 3. **Access the Platform**
- **Main Application**: http://localhost:5000
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090
- **Database Admin**: http://localhost:8080 (development only)
- **Redis Commander**: http://localhost:8081 (development only)

## 🐳 Docker Compose Methods

### **Method 1: Full Production Stack**
```bash
# Start all services (PostgreSQL, Redis, Nginx, Monitoring)
docker-compose up -d

# View logs
docker-compose logs -f sdlc-orchestrator

# Stop services
docker-compose down
```

### **Method 2: Development Mode**
```bash
# Development with hot reloading and debugging tools
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View all service status
docker-compose ps

# Follow logs for main application
docker-compose logs -f sdlc-orchestrator
```

### **Method 3: Minimal Setup (Backend Only)**
```bash
# Run just the main application for testing
docker build -t sdlc-orchestrator .
docker run -p 5000:5000 sdlc-orchestrator
```

## 🖥️ Local Development Setup

### **Backend Development**
```bash
# 1. Setup Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start development server
python main.py

# 4. Test the orchestrator
python test_orchestrator.py
python foundational_improvements.py
```

### **Frontend Development**
```bash
# 1. Install Node.js dependencies
npm install

# 2. Start development server (if using Vite)
npm run dev

# 3. Build for production
npm run build
```

## 🧪 Testing the Platform

### **Health Check**
```bash
# Check if application is running
curl http://localhost:5000/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-XX...",
  "components": {...}
}
```

### **Test Orchestrator Functionality**
```bash
# Run orchestrator tests
python test_orchestrator.py

# Run comprehensive test suite
python test_suite.py

# Test foundational improvements
python foundational_improvements.py
```

### **API Testing**
```bash
# Test collaboration endpoint
curl -X POST http://localhost:5000/api/demo \
  -H "Content-Type: application/json" \
  -d '{
    "paradigm": "orchestra",
    "task": "Create a simple web API",
    "agents": ["gemini", "claude"]
  }'

# Get available paradigms
curl http://localhost:5000/api/paradigms

# Get available agents
curl http://localhost:5000/api/agents
```

## 🔧 Configuration Options

### **Environment Variables**
```bash
# Application Configuration
export FLASK_ENV=development|production
export DATABASE_URL=postgresql://user:pass@host:port/db
export REDIS_URL=redis://host:port/db

# AI Provider APIs
export OPENAI_API_KEY=your-key
export ANTHROPIC_API_KEY=your-key
export GEMINI_API_KEY=your-key
export BLACKBOX_API_KEY=your-key

# Monitoring (Optional)
export PROMETHEUS_URL=http://localhost:9090
export GRAFANA_URL=http://localhost:3000
```

## 🚨 Troubleshooting

### **Common Issues**

#### **Port Already in Use**
```bash
# Check what's using port 5000
netstat -tulpn | grep 5000
# or on Windows
netstat -ano | findstr 5000

# Stop conflicting services or change port
docker-compose down
```

#### **Docker Build Issues**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache sdlc-orchestrator
```

#### **Database Connection Issues**
```bash
# Check database container
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### **Missing Dependencies**
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
npm install --force
```

### **Performance Issues**
```bash
# Check container resources
docker stats

# View detailed logs
docker-compose logs --tail=100 sdlc-orchestrator

# Monitor health endpoints
curl http://localhost:5000/api/health
```

## 📊 Monitoring and Logs

### **Application Logs**
```bash
# View real-time logs
docker-compose logs -f sdlc-orchestrator

# View specific service logs
docker-compose logs postgres
docker-compose logs redis
```

### **Performance Monitoring**
- **Grafana**: http://localhost:3000
  - Username: admin
  - Password: admin
  - Pre-configured dashboards for application metrics

- **Prometheus**: http://localhost:9090
  - Raw metrics and query interface
  - Application health and performance data

### **Database Management**
- **Adminer**: http://localhost:8080 (development only)
  - Server: postgres
  - Username: sdlc_user
  - Password: sdlc_pass
  - Database: sdlc_dev_db

## 🎛️ Advanced Usage

### **Custom Configuration**
```bash
# Use custom Docker Compose file
docker-compose -f custom-compose.yml up -d

# Override environment variables
FLASK_ENV=production docker-compose up -d

# Scale specific services
docker-compose up -d --scale sdlc-orchestrator=3
```

### **Production Deployment**
```bash
# Deploy to production with optimizations
./deploy.sh --environment production --push

# Use production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### **CI/CD Integration**
```bash
# Trigger automated deployment (if GitHub Actions configured)
git push origin main

# Manual deployment with tests
./deploy.sh --environment staging --no-frontend
```

## 🎯 Usage Examples

### **1. Basic Collaboration**
Access http://localhost:5000 and:
1. Enter a project idea: "Create a REST API for user management"
2. Select collaboration paradigm: "Multi-Agent Orchestra"
3. Choose AI agents: Gemini, Claude, OpenAI
4. Watch real-time collaboration between AI agents

### **2. API Usage**
```python
import requests

# Start collaboration
response = requests.post('http://localhost:5000/api/demo', json={
    'paradigm': 'mesh',
    'task': 'Design a database schema for e-commerce',
    'agents': ['gemini', 'claude']
})

print(response.json())
```

### **3. Health Monitoring**
```bash
# Comprehensive health check
curl http://localhost:5000/api/health | jq .

# Check specific components
curl http://localhost:5000/api/collaboration/health
```

## 🎉 Success Indicators

When everything is running correctly, you should see:

✅ **All containers healthy**: `docker-compose ps` shows "Up" status  
✅ **Application accessible**: http://localhost:5000 loads the interface  
✅ **Health check passes**: `/api/health` returns "healthy" status  
✅ **AI providers available**: Orchestrator can communicate with AI services  
✅ **Database connected**: PostgreSQL accepting connections  
✅ **Cache working**: Redis responding to ping  
✅ **Monitoring active**: Grafana and Prometheus collecting metrics  

## 🚀 Ready to Use!

Your autonomous SDLC agent platform is now running and ready to:
- Orchestrate multi-agent AI collaborations
- Manage software development lifecycles
- Provide real-time development assistance
- Scale based on demand
- Monitor performance and health

**Happy coding with your AI-powered development team! 🤖✨**
